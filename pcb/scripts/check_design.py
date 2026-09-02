"""Regression guard for PRAHARI rev B.

Every invariant in here was established by hand once and is easy to break by
accident later - a nudged footprint, a netclass edit, a renamed net.  Run this
after any change to scripts/ or before generating manufacturing outputs:

    python scripts/check_design.py            # design-level checks only
    python scripts/check_design.py --full     # also run DRC/ERC + netlist diff

Exit code is non-zero if anything fails.
"""
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LOCAL = os.environ.get("LOCALAPPDATA", "")
CLI = os.path.join(LOCAL, "Programs", "KiCad", "10.0", "bin", "kicad-cli.exe")

fails = []
notes = []


def check(ok, label, detail=""):
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", label,
                           "" if ok else "  -- " + detail))
    if not ok:
        fails.append(label)


def owner_map():
    own = {}
    for net, members in D.NETS.items():
        for ref, pad in members:
            own.setdefault((ref, pad), []).append(net)
    return own


print("=== design-level checks ===")
own = owner_map()

# 1. no pad on two nets, no net referencing a missing component
dupes = {k: v for k, v in own.items() if len(v) > 1}
check(not dupes, "no pad appears on two nets", str(dupes)[:200])
orphans = [(n, r, p) for n, ms in D.NETS.items() for r, p in ms
           if r not in D.COMPONENTS]
check(not orphans, "every net member references a real component", str(orphans)[:200])

# 2. the XIAO's GPIO budget: 11 signals + 3V3 + GND + VUSB = 14 pads, no more
u1 = {int(p) for (r, p) in own if r == "U1"}
check(u1 == set(range(1, 15)), "XIAO U1 uses exactly pads 1-14",
      "got %s" % sorted(u1))
gpio = {p for p in u1 if p <= 11}
check(len(gpio) == 11, "all 11 XIAO GPIO assigned", "got %d" % len(gpio))
check(own.get(("U1", "2")) == ["LORA_BUSY"],
      "D1 carries LORA_BUSY (SX1262 has no DIO0)",
      str(own.get(("U1", "2"))))

# 3. the radio: all 16 pads assigned exactly once, ANT on the pad that keeps
#    the 3.5 mm run to J6
u2 = sorted(int(p) for (r, p) in own if r == "U2")
check(u2 == list(range(1, 17)), "Ra-01SH U2 has all 16 pads assigned",
      "got %s" % u2)
check(D.RA01SH_PINS["ANT"] == "1",
      "ANT is on pad 1 (KiCad curated Ai-Thinker pinout, not the rev A guess)",
      D.RA01SH_PINS["ANT"])
check(D.RA01SH_PINS["VCC"] == "3" and D.RA01SH_PINS["NSS"] == "15"
      and D.RA01SH_PINS["SCK"] == "12" and D.RA01SH_PINS["NRESET"] == "4",
      "radio pad map matches KiCad's curated Ai-Thinker Ra-01/Ra-02 pinout")

# 4. battery protection topology - low-side PCM, DW01A pin numbering per
#    KiCad's curated Battery_Management:DW01A symbol
want = {
    ("J4", "1"): "VBAT",      ("J4", "2"): "BAT_NEG",
    ("U4", "1"): "DW_OD",     ("U4", "2"): "GND",
    ("U4", "3"): "DW_OC",     ("U4", "5"): "DW_VDD",
    ("U4", "6"): "BAT_NEG",
    ("U5", "1"): "BAT_NEG",   ("U5", "2"): "DW_OD",
    ("U5", "3"): "GND",       ("U5", "4"): "DW_OC",
    ("U5", "5"): "FET_MID",   ("U5", "6"): "FET_MID",
    ("R6", "1"): "VBAT",      ("R6", "2"): "DW_VDD",
    ("C7", "1"): "DW_VDD",    ("C7", "2"): "BAT_NEG",
}
wrong = {k: (own.get(k), v) for k, v in want.items()
         if own.get(k, [None])[0] != v}
check(not wrong, "protection chain wired as a low-side PCM", str(wrong)[:300])
check(own.get(("U4", "4"), [""])[0].startswith("unconnected-"),
      "DW01A TD (pin 4) is a no-connect, not a dangling label",
      str(own.get(("U4", "4"))))

# 5. netclasses: BAT_NEG must NOT be on Power - a 0.60 mm track cannot reach a
#    SOT-23-6 pad through a ~0.35 mm inter-pad gap
power_nets = D.NETCLASS["Power"][4] or []
check("BAT_NEG" not in power_nets,
      "BAT_NEG is not on the Power netclass (0.6 mm cannot reach SOT-23-6)")
check("FET_MID" not in power_nets, "FET_MID is not on the Power netclass")
check("ANT" in (D.NETCLASS["RF"][4] or []), "ANT is on the RF netclass")

# 6. the router must route BAT_NEG early or it gets boxed in
gp = io.open(os.path.join(PROJ, "scripts", "gen_pcb.py"), encoding="utf-8").read()
m = re.search(r'^priority = (\[[^\]]*\])', gp, re.M)
check(bool(m) and "BAT_NEG" in m.group(1),
      "gen_pcb.py routes BAT_NEG in the priority list",
      m.group(1) if m else "priority list not found")

# 7. protection placement is load-bearing - warn if it moved from the swept,
#    DRC-clean combination
EXPECT = {"U4": (18.0, 32.0, 0), "U5": (18.0, 37.0, 0),
          "R6": (23.0, 32.0, 0), "C7": (23.0, 35.5, 0)}
moved = {r: (D.COMPONENTS[r][2], D.COMPONENTS[r][3], D.COMPONENTS[r][4])
         for r, e in EXPECT.items()
         if (D.COMPONENTS[r][2], D.COMPONENTS[r][3], D.COMPONENTS[r][4]) != e}
if moved:
    notes.append("protection cluster moved from the DRC-clean sweep result: %s "
                 "- re-check DRC unconnected==0" % moved)
    print("  [WARN] protection placement differs from the swept combination: %s"
          % moved)
else:
    print("  [PASS] protection placement matches the DRC-clean swept combination")

# 8. board outline unchanged
check((D.BOARD_W, D.BOARD_H) == (70.0, 40.0), "board is still 70 x 40 mm")

if "--full" not in sys.argv:
    print("\n%d design check(s) failed. Re-run with --full for DRC/ERC."
          % len(fails) if fails else "\nall design checks passed. "
          "Re-run with --full for DRC/ERC + netlist diff.")
    raise SystemExit(1 if fails else 0)

# --------------------------------------------------------------- full checks
print("\n=== DRC / ERC ===")
if not os.path.isfile(CLI):
    print("  [SKIP] kicad-cli not found at %s" % CLI)
else:
    subprocess.run([CLI, "pcb", "drc", "--schematic-parity", "--severity-all",
                    "--format", "json", "-o", "out/drc.json", "PRAHARI.kicad_pcb"],
                   cwd=PROJ, capture_output=True, text=True)
    d = json.load(io.open(os.path.join(PROJ, "out", "drc.json"), encoding="utf-8"))
    check(len(d["violations"]) == 0, "DRC violations == 0",
          str([v.get("description") for v in d["violations"]])[:300])
    check(len(d["unconnected_items"]) == 0, "DRC unconnected == 0",
          str([v.get("description") for v in d["unconnected_items"]])[:300])
    check(len(d["schematic_parity"]) == 8,
          "DRC parity == 8 (the known cosmetic auto-named nets)",
          "got %d" % len(d["schematic_parity"]))

    subprocess.run([CLI, "sch", "erc", "--severity-error", "--severity-warning",
                    "--format", "json", "-o", "out/erc.json", "PRAHARI.kicad_sch"],
                   cwd=PROJ, capture_output=True, text=True)
    e = json.load(io.open(os.path.join(PROJ, "out", "erc.json"), encoding="utf-8"))
    kinds = {}
    for sh in e["sheets"]:
        for v in sh["violations"]:
            kinds[v.get("type")] = kinds.get(v.get("type"), 0) + 1
    real = {k: n for k, n in kinds.items()
            if k not in ("endpoint_off_grid", "isolated_pin_label")}
    check(not real, "no ERC errors beyond off-grid + isolated labels", str(real))
    print("        ERC breakdown: %s" % kinds)

    # netlist diff: does the SCHEMATIC agree with design.py?
    print("\n=== schematic netlist vs design.py ===")
    subprocess.run([CLI, "sch", "export", "netlist", "-o", "out/netlist.net",
                    "--format", "kicadsexpr", "PRAHARI.kicad_sch"],
                   cwd=PROJ, capture_output=True, text=True)
    t = io.open(os.path.join(PROJ, "out", "netlist.net"), encoding="utf-8").read()
    body = t[t.find("(nets"):]
    sch, i = {}, 0
    while True:
        i = body.find("(net\n", i)
        if i < 0:
            break
        depth, j = 0, i
        while j < len(body):
            if body[j] == "(":
                depth += 1
            elif body[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = body[i:j + 1]
        nm = re.search(r'\(name "([^"]+)"\)', blk)
        sch[(nm.group(1).lstrip("/") if nm else "?")] = set(
            re.findall(r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', blk))
        i = j + 1
    des = {n: set(v) for n, v in D.NETS.items()
           if not n.startswith("unconnected-")}
    # KiCad auto-names these three because they are drawn as bare wires
    AUTO = {"ANT", "HAPTIC_G", "MOTOR_N"}
    mismatch = {n: (sorted(des[n] - sch[n]), sorted(sch[n] - des[n]))
                for n in set(des) & set(sch) if des[n] != sch[n]}
    check(not mismatch, "no net membership mismatches", str(mismatch)[:400])
    missing = sorted(set(des) - set(sch) - AUTO)
    check(not missing, "every design.py net appears in the schematic",
          str(missing))

print()
if fails:
    print("FAILED: %d check(s) -> %s" % (len(fails), ", ".join(fails)))
else:
    print("all checks passed.")
for n in notes:
    print("note: %s" % n)
raise SystemExit(1 if fails else 0)
