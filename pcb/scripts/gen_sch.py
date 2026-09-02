"""Build PRAHARI.kicad_sch — a block-structured A3 schematic.

Five titled functional blocks, real power symbols, direct wires inside a block
where the geometry allows, and net labels only where a signal crosses a block
boundary.  The netlist still comes from design.py — the same file that builds
the board — so the two cannot drift apart.
"""
import os, re, sys, uuid, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SYMDIR = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "KiCad", "10.0",
                      "share", "kicad", "symbols")
U = lambda: str(uuid.uuid4())
ROOT = "7a1f0c62-4d8b-4e19-9c33-0e1a2b3c4d5e"   # nil UUIDs are rejected

SYMBOL = {
    "U1": "PRAHARI:XIAO_nRF52840_Sense",
    "U2": "PRAHARI:Ai-Thinker_Ra-01SH",
    # Re-drawn single-unit in PRAHARI.kicad_sym, keeping KiCad's pin numbering:
    # DW01A 1=OD 2=CS 3=OC 4=TD 5=VCC 6=GND, and the FET pair
    # 1=S1 2=G1 3=S2 4=G2 5=D2 6=D1 - exactly the 8205A arrangement.
    # KiCad's own Q_Dual_NMOS_S1G1S2G2D2D1 is a two-unit symbol, and this
    # generator places a single unit per reference.
    "U4": "PRAHARI:DW01A",
    "U5": "PRAHARI:FS8205A",
    "U3": "Security:ATECC608A-SSHDA",
    "J1": "Connector_Generic:Conn_01x07",
    "J2": "Connector_Generic:Conn_01x04",
    "J3": "Connector_Generic:Conn_01x04",
    "J7": "Connector_Generic:Conn_01x04",
    "J4": "Connector_Generic:Conn_01x02",
    "J5": "Connector_Generic:Conn_01x02",
    "J6": "Connector_Generic:Conn_01x02",
    "Q1": "Transistor_FET:Q_NMOS_GSD",   # 2N7002 is derived; use its base symbol
    "D1": "Device:D",
    "D2": "Device:LED",
}
for r in ("R1", "R2", "R3", "R4", "R5", "R6"):
    SYMBOL[r] = "Device:R"
for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7"):
    SYMBOL[c] = "Device:C"
for t in ("TP1", "TP2", "TP3", "TP4", "TP5", "TP6"):
    SYMBOL[t] = "Connector:TestPoint"
for m in ("MH1", "MH2", "MH3", "MH4"):
    SYMBOL[m] = "Mechanical:MountingHole"

DATASHEET = {
    "U1": "https://wiki.seeedstudio.com/XIAO_BLE/",
    "U2": "https://docs.ai-thinker.com/en/Ra-01SH",
}

PADNET = {}
for net, conns in D.NETS.items():
    for ref, pad in conns:
        PADNET[(ref, pad)] = net

# --------------------------------------------------------------------- sheet
PAPER = "A3"
BLOCKS = [
    ("MCU  +  SECURE ELEMENT",   16, 20, 214, 118),
    ("LoRa  868 MHz  (SX1262)", 220, 20, 404, 118),
    ("SENSORS  -  I2C BUS",      16, 128, 404, 204),
    ("POWER  +  BATTERY PROTECTION", 16, 212, 170, 284),
    ("HAPTIC DRIVE",            176, 212, 300, 284),
    ("MECHANICAL",              306, 212, 404, 284),
]

PLACE = {
    "U1": (75, 62),   "C2": (120, 60),  "U3": (168, 62),  "C4": (200, 60),
    "U2": (285, 62),  "J6": (330, 51.84), "C1": (360, 60), "C3": (378, 60),
    "J1": (78, 160),  "J2": (160, 158), "J3": (238, 158), "J7": (316, 158),
    "R1": (350, 152), "R2": (366, 152), "C5": (386, 152),
    "TP3": (350, 172), "TP4": (366, 172),
    "J4": (52, 232),  "C6": (75, 240),  "TP1": (100, 230), "TP2": (118, 230),
    "TP5": (136, 230), "TP6": (154, 230), "R3": (40, 262), "D2": (80, 268),
    # battery protection, in the free lower-right corner of the POWER block
    "U4": (115, 262), "U5": (150, 262), "R6": (100, 248), "C7": (100, 272),
    "R4": (200, 232), "Q1": (215, 248), "R5": (200, 258),
    "D1": (250, 226), "J5": (280, 233.46),
    "MH1": (330, 235), "MH2": (360, 235), "MH3": (330, 258), "MH4": (360, 258),
}

# (ref, pin) -> ("pwr", h, v) | ("lbl", stub, angle) | ("wire",)
# h runs along the pin direction, v perpendicular, to reach the power symbol.
ACT = {}


def pwr(ref, pin, h, v):
    ACT[(ref, pin)] = ("pwr", h, v)


def lbl(ref, pin, stub=2.54, ang=None):
    ACT[(ref, pin)] = ("lbl", stub, ang)


def wired(*pairs):
    for ref, pin in pairs:
        ACT[(ref, pin)] = ("wire",)


# --- block A: MCU + secure element
pwr("U1", "12", 0, -5.08); pwr("U1", "13", 0, 5.08)
lbl("U1", "14", 2.54, 90)                       # VUSB, straight up
pwr("C2", "1", 0, -5.08); pwr("C2", "2", 0, 5.08)
pwr("U3", "8", 0, -5.08); pwr("U3", "4", 0, 5.08)
pwr("C4", "1", 0, -5.08); pwr("C4", "2", 0, 5.08)

# --- block B: LoRa
# VCC is pad 3 and the grounds are 2/9/16 in the curated Ai-Thinker pinout.
pwr("U2", "3", 0, -5.08)
pwr("U2", "2", 0, 10.16); pwr("U2", "9", 0, 5.08); pwr("U2", "16", 0, 10.16)
pwr("J6", "2", 8.0, 7.62)
pwr("C1", "1", 0, -5.08); pwr("C1", "2", 0, 5.08)
pwr("C3", "1", 0, -5.08); pwr("C3", "2", 0, 5.08)
wired(("U2", "1"), ("J6", "1"))                 # ANT (pad 1) direct run

# --- block C: sensors.  The 3V3 and GND runs travel past the signal labels
# before turning, so no vertical ever crosses label text.
for ref, up, dn in (("J1", 8.0, 22.0), ("J2", 11.0, 19.0),
                    ("J3", 11.0, 19.0), ("J7", 11.0, 19.0)):
    pwr(ref, "1", 22.0, -up)
    pwr(ref, "2", 26.0, dn)
pwr("R1", "1", 0, -5.08); lbl("R1", "2", 3.81, 270)
pwr("R2", "1", 0, -5.08); lbl("R2", "2", 3.81, 270)
pwr("C5", "1", 0, -5.08); pwr("C5", "2", 0, 5.08)
lbl("TP3", "1", 5.08, 270); lbl("TP4", "1", 5.08, 270)

# --- block D: power
lbl("J4", "1", 2.54, 180)
# J4 pin 2 used to be GND.  In rev B it is BAT_NEG - the cell's negative leg
# upstream of the protection FETs - so it gets a net label, not a ground bar.
# Everything else in the protection block falls through to the default action:
# GND pins (U4 CS, U5 S2) get power symbols, all other pins get labels.
lbl("J4", "2", 2.54, 180)
lbl("C6", "1", 5.08, 90); pwr("C6", "2", 0, 5.08)
lbl("TP1", "1", 6.0, 270)
pwr("TP2", "1", 0, 6.0)
lbl("TP5", "1", 6.0, 270)
pwr("TP6", "1", 0, 6.0)
pwr("R3", "1", 0, -5.08); lbl("R3", "2", 3.81, 270)
pwr("D2", "1", 10.0, 8.0); lbl("D2", "2", 2.54, 0)

# --- block E: haptic drive, wired as an actual circuit
lbl("R4", "1", 4.0, 90)
wired(("R4", "2"), ("R5", "1"), ("Q1", "1"), ("Q1", "3"),
      ("D1", "2"), ("J5", "2"))
pwr("R5", "2", 0, 5.08)
pwr("Q1", "2", 0, 8.92)
lbl("D1", "1", 6.0, 90)
lbl("J5", "1", 2.54, 180)

# Explicit polylines: each starts and ends exactly on a pin or on another wire.
WIRES = [
    [(297.7, 51.84), (324.92, 51.84)],                       # U2 ANT -> J6
    [(200, 235.81), (200, 248), (209.92, 248)],              # R4 -> Q1 gate
    [(200, 254.19), (200, 248)],                             # R5 -> gate node
    [(217.54, 242.92), (217.54, 236), (274.92, 236)],        # Q1 drain -> J5
    [(253.81, 226), (253.81, 236)],                          # D1 anode -> rail
]

# --------------------------------------------------------------- lib parsing
def lib_text(libname):
    path = (os.path.join(PROJ, "PRAHARI.kicad_sym") if libname == "PRAHARI"
            else os.path.join(SYMDIR, libname + ".kicad_sym"))
    return open(path, encoding="utf-8").read()


def block(text, name):
    tag = '(symbol "%s"' % name
    i = text.index(tag)
    depth, j, instr = 0, i, False
    while j < len(text):
        ch = text[j]
        if ch == '"' and text[j - 1] != "\\":
            instr = not instr
        elif not instr:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return text[i:j + 1]
        j += 1
    raise ValueError(name)


PIN_RE = re.compile(
    r'\(pin\s+(\w+)\s+\w+\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+([\d.]+)\)\s*'
    r'\(length\s+([\d.]+)\).*?\(number\s+"([^"]+)"', re.S)
cache = {}


def get_symbol(libid):
    if libid in cache:
        return cache[libid]
    lib, name = libid.split(":")
    text = lib_text(lib)
    blk = block(text, name)
    if re.search(r'\(extends\s+"[^"]+"\)', blk):
        raise SystemExit(f"{libid} is a derived symbol; use its base instead")
    pins = {m.group(6): (float(m.group(2)), float(m.group(3)),
                         float(m.group(4)), float(m.group(5)))
            for m in PIN_RE.finditer(blk)}
    blk = blk.replace('(symbol "%s"' % name, '(symbol "%s"' % libid, 1)
    cache[libid] = (blk, pins)
    return cache[libid]


# ------------------------------------------------------------------ emitting
body, used, wires = [], {}, []
LANG = {(-1, 0): 180, (1, 0): 0, (0, -1): 90, (0, 1): 270}


def place_symbol(ref, libid, sx, sy, val, fpid, descr, ds, in_bom, pins,
                 show=True):
    pu = "".join('\t\t(pin "%s" (uuid "%s"))\n' % (n, U()) for n in sorted(pins))
    hide = "" if show else "\n\t\t\t(hide yes)"
    body.append(f'''	(symbol
		(lib_id "{libid}")
		(at {sx} {sy} 0)
		(unit 1)
		(exclude_from_sim no) (in_bom {in_bom}) (on_board yes) (dnp no)
		(uuid "{U()}")
		(property "Reference" "{ref}" (at {sx - 2.54} {sy - 19.05} 0){hide}
			(effects (font (size 1.27 1.27)) (justify left)))
		(property "Value" "{val}" (at {sx - 2.54} {sy - 16.51} 0){hide}
			(effects (font (size 1.27 1.27)) (justify left)))
		(property "Footprint" "{fpid}" (at {sx} {sy} 0)
			(hide yes)
			(effects (font (size 1.27 1.27))))
		(property "Datasheet" "{ds}" (at {sx} {sy} 0)
			(hide yes)
			(effects (font (size 1.27 1.27))))
		(property "Description" "{descr}" (at {sx} {sy} 0)
			(hide yes)
			(effects (font (size 1.27 1.27))))
{pu}		(instances
			(project "PRAHARI"
				(path "/{ROOT}" (reference "{ref}") (unit 1))
			)
		)
	)
''')


def add_wire(pts):
    for a, b in zip(pts, pts[1:]):
        if a != b:
            wires.append([a, b])


def add_label(net, x, y, ang):
    just = "right" if ang == 180 else "left"
    body.append(f'''	(global_label "{net}"
		(shape bidirectional)
		(at {x} {y} {ang})
		(fields_autoplaced yes)
		(effects (font (size 1.27 1.27)) (justify {just}))
		(uuid "{U()}")
		(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} {y} 0)
			(hide yes)
			(effects (font (size 1.27 1.27)) (justify {just})))
	)
''')


PWRSYM = {"GND": "power:GND", "+3V3": "power:+3V3"}
pwr_n = 0

for ref in PLACE:
    libid = SYMBOL[ref]
    blk, pins = get_symbol(libid)
    used[libid] = blk
    sx, sy = PLACE[ref]
    fpid, val, descr = (D.COMPONENTS[ref][0], D.COMPONENTS[ref][1],
                        D.COMPONENTS[ref][6])
    in_bom = "no" if ref.startswith(("TP", "MH")) else "yes"
    place_symbol(ref, libid, sx, sy, val, fpid, descr,
                 DATASHEET.get(ref, ""), in_bom, pins)

    for num, (px, py, ang, ln) in sorted(pins.items()):
        net = PADNET.get((ref, num))
        if net and net.startswith("unconnected-"):
            net = None
        ex, ey = sx + px, sy - py
        dx = -math.cos(math.radians(ang))
        dy = math.sin(math.radians(ang))
        idx = (int(round(dx)), int(round(dy)))
        if not net:
            body.append('\t(no_connect (at %s %s) (uuid "%s"))\n' % (ex, ey, U()))
            continue

        act = ACT.get((ref, num))
        if act is None:
            act = (("pwr", 5.08, 7.62 if net == "GND" else -7.62)
                   if net in PWRSYM else ("lbl", 2.54, None))
        # A "pwr" action only makes sense for a net that has a power symbol.
        # If a net gets renamed out of PWRSYM (as GND -> BAT_NEG did on J4.2),
        # fall back to a label rather than dying with a KeyError.
        if act[0] == "pwr" and net not in PWRSYM:
            act = ("lbl", 2.54, None)

        if act[0] == "wire":
            continue
        if act[0] == "lbl":
            stub, la = act[1], act[2]
            wx, wy = ex + dx * stub, ey + dy * stub
            add_wire([(ex, ey), (wx, wy)])
            add_label(net, wx, wy, la if la is not None else LANG[idx])
            continue

        h, v = act[1], act[2]
        if idx[0]:                                   # horizontal pin
            mx = ex + dx * h
            px2, py2 = mx, ey + v
            add_wire([(ex, ey), (mx, ey), (px2, py2)])
        else:                                        # vertical pin
            px2, py2 = ex, ey + (v if v else dy * 5.08)
            add_wire([(ex, ey), (px2, py2)])
        pwr_n += 1
        plib = PWRSYM[net]
        pblk, ppins = get_symbol(plib)
        used[plib] = pblk
        place_symbol("#PWR%02d" % pwr_n, plib, px2, py2, net, "", "", "",
                     "no", ppins, show=False)

# GND needs a driver: every GND pin in the stock libraries is a power input.
pblk, ppins = get_symbol("power:PWR_FLAG")
used["power:PWR_FLAG"] = pblk
place_symbol("#FLG01", "power:PWR_FLAG", 140, 258, "PWR_FLAG", "", "", "",
             "no", ppins, show=False)
add_wire([(140, 258), (140, 264)])
pwr_n += 1
gblk, gpins = get_symbol("power:GND")
used["power:GND"] = gblk
place_symbol("#PWR%02d" % pwr_n, "power:GND", 140, 264, "GND", "", "", "",
             "no", gpins, show=False)

for pts in WIRES:
    add_wire(pts)

# ------------------------------------------------------------- junctions
def on_seg(p, a, b):
    if p == a or p == b:
        return False
    cross = ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
    if abs(cross) > 1e-6:
        return False
    return (min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and
            min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6)


ends = {}
for a, b in wires:
    ends[tuple(a)] = ends.get(tuple(a), 0) + 1
    ends[tuple(b)] = ends.get(tuple(b), 0) + 1
junctions = {p for p, n in ends.items() if n >= 3}
for p in ends:
    if any(on_seg(p, tuple(a), tuple(b)) for a, b in wires):
        junctions.add(p)

for a, b in wires:
    body.append(f'''	(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]}))
		(stroke (width 0) (type default)) (uuid "{U()}"))
''')
for x, y in sorted(junctions):
    body.append(f'	(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))\n')

# ---------------------------------------------------------------- block art
for title, x0, y0, x1, y1 in BLOCKS:
    body.append(f'''	(rectangle (start {x0} {y0}) (end {x1} {y1})
		(stroke (width 0.254) (type dash)) (fill (type none)) (uuid "{U()}"))
''')
    body.append(f'''	(text "{title}" (at {x0 + 3} {y0 + 5} 0)
		(effects (font (size 2.0 2.0) (thickness 0.4)) (justify left)) (uuid "{U()}"))
''')

sch = f'''(kicad_sch
	(version 20250610)
	(generator "prahari_gen")
	(generator_version "10.0")
	(uuid "{ROOT}")
	(paper "{PAPER}")
	(title_block
		(title "PRAHARI - The Countdown Band, carrier board")
		(date "2026-09-02")
		(rev "B")
		(company "Point Break - SIH 2026 - PS 26181")
		(comment 1 "Generated from scripts/design.py - the same netlist builds the PCB")
		(comment 2 "All 11 XIAO GPIO used: D0-D3 LoRa, D4/D5 I2C, D6 haptic, D7 PPG, D8-D10 SPI")
		(comment 3 "rev B: MAX30102, MAX30208, Ra-01SH SX1262 868MHz, 0.91in OLED, DW01A+FS8205A")
	)
	(lib_symbols
{"".join(used.values())}
	)
{"".join(body)}
	(sheet_instances
		(path "/" (page "1"))
	)
	(embedded_fonts no)
)
'''
open(os.path.join(PROJ, "PRAHARI.kicad_sch"), "w", encoding="utf-8").write(sch)
print(f"wrote PRAHARI.kicad_sch: {len(PLACE)} parts, {pwr_n} power symbols, "
      f"{len(wires)} wires, {len(junctions)} junctions, {len(used)} lib symbols")
