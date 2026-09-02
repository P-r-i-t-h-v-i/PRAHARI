# PRAHARI — carrier board, rev B

Prototype carrier PCB for **PRAHARI, The Countdown Band** (Point Break, SIH 2026, PS 26181).

**70 × 40 mm, 2 layer, 1.6 mm FR4.** Every active part is still an off-the-shelf
module on a 2.54 mm header. rev B upgrades the sensing, radio and power chain;
the board outline, mounting holes and connector positions are unchanged.

| | |
|---|---|
| Board | 70 × 40 mm, 2 mm corner radius, 4 × M2 mounting holes |
| Stackup | 2 layer, 1.6 mm, 1 oz, GND pour both sides |
| Parts | 38 footprints, 22 BOM line items |
| Routing | 345 tracks / 772 mm, 156 vias (23 routing + 133 ground stitching) |
| Widths | 0.25 mm signal, 0.6 mm power, 0.9 mm RF |
| Pads | 75 SMD, 39 plated through |
| Process | 0.25 mm track / 0.2 mm space / 0.3 mm drill — cheapest JLCPCB & PCBWay tier |
| DRC | **0 violations, 0 unconnected** — 8 cosmetic parity warnings |
| ERC | 202 warnings: 195 off-grid (pre-existing, see *Known warnings*) + 7 deliberate |

---

## What changed from rev A

| | rev A | rev B | Why |
|---|---|---|---|
| PPG | MAX30100 | **MAX30102** | Glass shield, ambient-light cancellation, and 3V3 bus levels — which retires rev A's "1.8 V pull-ups fighting R1/R2" warning entirely |
| Skin temp | MLX90614 (IR) | **MAX30208** (contact) | The thermopile had to see skin across an air gap that wrist curvature keeps changing. A contact digital sensor does not care: ±0.1 °C over I²C |
| Ambient | AHT20 | AHT20 | Unchanged — still the WBGT wet-bulb input |
| Radio | Ra-02 (SX1278) | **Ra-01SH (SX1262)** | 4.2 mA RX vs 11 mA, built-in DC-DC, +22 dBm. **Changes band — see below** |
| Display | 0.96" SSD1306 | **0.91" SSD1306** | Same driver and same 0x3C address, smaller panel, lower peak charge-pump current (<15 mA) |
| Battery | bare LiPo | **DW01A + FS8205A** | On-carrier over-charge / over-discharge / over-current protection |
| Actuator | 1027 ERM + 2N7002 | unchanged | Already correct in rev A |
| MCU | XIAO nRF52840 Sense | unchanged | Already correct in rev A; its BQ25101 is still the only charger |

### ⚠ The radio swap changes the band

The Ra-01SH is an SX1262 part covering **803–930 MHz**. It does *not* cover
433 MHz like the Ra-02 it replaces. Consequences:

- **The whip on J6 drops from 173 mm to 86 mm** (λ/4 at 868 MHz). On a wrist-worn
  band that is a real win — 173 mm of wire was always awkward.
- **In India, keep the radio inside the de-licensed 865–867 MHz sub-band.**
- The deck's "433 MHz mesh" line needs updating to 868 MHz.

If you must stay on 433 MHz, the drop-in is the **Ra-01S / Ra-01SC (SX1268,
410–525 MHz)** — same SPI interface, same BUSY pin, same footprint family. Only
`RA01SH_PINS` and the silkscreen would change. The other option you floated,
the EBYTE E22-400T22S, holds 433 MHz but is a **TTL-UART** module needing
M0/M1/AUX instead of SPI, so it is not a drop-in at all.

---

## What's on it

```
 ANT ▫▫ GND      C3  C1      PRAHARI rev B
 ┌──────────────┐              ┌──────────────────┐
 │  U2 Ra-01SH  │       C2     │ U1  XIAO         │ USB-C
 │  SX1262      │   TP BAT±    │ nRF52840 Sense   │
 │  868 MHz     │   TP 3V3 GND │                  │
 │ U4 C7 R6 U5  │   TP SDA SCL └──────────────────┘
 └──────────────┘
 ┌──────┐ ┌────┐ ┌────┐ ┌────┐            ┌──────┐
 │  J1  │ │ J2 │ │ J3 │ │ J7 │            │  U3  │
 │MAX301│ │MAX │ │AHT │ │OLED│            │ATECC │
 │  02  │ │30208││ 20 │ │0.91│            │ 608A │
 └──────┘ └────┘ └────┘ └────┘            └──────┘
  [J4 BAT]  [J5 MOTOR]  Q1 D1 D2 R3 R4 R5  C4 C5
```

| Ref | Part | Role |
|---|---|---|
| **U1** | Seeed XIAO nRF52840 Sense | MCU, BLE, IMU + mic, BQ25101 LiPo charger |
| **U2** | Ai-Thinker Ra-01SH (SX1262) | LoRa 868 MHz, band-to-band mesh |
| **U3** | ATECC608A-SSHDA (SOIC-8) | Secure element for the anonymised uplink |
| **U4** | DW01A (SOT-23-6) | Li-ion protection: 4.3 V over-charge, 2.4 V over-discharge |
| **U5** | FS8205A (SOT-23-6) | Dual common-drain N-MOSFET — the protection switch pair |
| **J1** | MAX30102 breakout, 1×7 | Red/IR PPG — heart rate, IMU-gated |
| **J2** | MAX30208 breakout, 1×4 | Contact skin temperature, ±0.1 °C |
| **J3** | AHT20 breakout, 1×4 | Air temperature + RH — the WBGT inputs |
| **J7** | 1×4 header | I²C port — 0.91" SSD1306 OLED, or spare |
| **J4** | JST-PH 2 | LiPo in (bare cell — protection is on-board) |
| **J5** | JST-PH 2 | 1027 ERM coin vibration motor |
| **J6** | 2 solder pads | 868 MHz whip + counterpoise |

## GPIO budget

Still exactly 11 GPIO, still all 11 used. The SX1262 has no DIO0 and adds a
**mandatory BUSY**, so D1 changes role and the budget balances unchanged:

| Pin | Net | | Pin | Net |
|---|---|---|---|---|
| D0 | LORA_DIO1 | | D6 | HAPTIC_PWM |
| D1 | **LORA_BUSY** *(was LORA_DIO0)* | | D7 | PPG_INT |
| D2 | LORA_RST | | D8 | SPI_SCK |
| D3 | LORA_NSS | | D9 | SPI_MISO |
| D4 | SDA | | D10 | SPI_MOSI |
| D5 | SCL | | | |

Battery voltage still needs no external divider — the XIAO reads VBAT internally
on P0.31, gated by P0.14, and neither pin reaches the 2×7 header.

A display still costs no GPIO: I²C is a bus, so the SSD1306 hangs off the same
D4/D5 pair as the sensors.

**A Sharp Memory LCD is not possible on this board.** It is an SPI part needing
its own chip-select plus EXTCOMIN, and there is no GPIO left. It only becomes
an option if you move the radio to a UART module and free up SPI.

## I²C bus

| Device | Address |
|---|---|
| AHT20 | 0x38 |
| SSD1306 OLED | 0x3C (0x3D if you move the SA0 jumper) |
| MAX30208 | 0x50 |
| MAX30102 | 0x57 |
| ATECC608A | 0x60 |

Five distinct addresses, no clash. R1/R2 (4k7, on the back) pull up SDA/SCL.
Most breakouts carry their own 4.7 k pull-ups too; with four or five modules
plugged in the bus has plenty, and you can leave R1/R2 unpopulated. Five modules
on flying leads also push bus capacitance toward the 400 pF Fast-mode ceiling —
if the bus is flaky, drop to 100 kHz.

---

## Battery protection (new in rev B)

Standard low-side PCM. The cell's **negative** leg runs through two series FETs
before it becomes system ground, which is why J4 pin 2 is no longer GND:

```
cell+ ──► J4.1 ──► VBAT ──► TP1 ──wire──► XIAO BAT+     (and DW01A VCC via R6)
cell- ──► J4.2 ──► BAT_NEG ──► U5 S1 ──[common drain]──► U5 S2 ──► GND
                                DW01A GND on BAT_NEG, CS on GND (pack-)
```

`BAT_NEG` is a separate net and is deliberately kept out of the ground pour.
`GND` on this board means *pack negative* — the drain side of the FET pair.

### Pin mappings used

| Part | Mapping | Source |
|---|---|---|
| DW01A | 1=OD 2=CS 3=OC 4=TD 5=VCC 6=GND | KiCad's curated `Battery_Management:DW01A` |
| FS8205A | 1=S1 2=G1 3=S2 4=G2 5=D2 6=D1 | KiCad's `Transistor_FET:Q_Dual_NMOS_S1G1S2G2D2D1` |

Note that several secondary web sources give the DW01A as
`1=OC 2=OD 3=CS 4=VSS 5=VDD 6=NC`. That cannot be right — a real DW01A has
*both* VCC and GND plus a TD test pin — so the KiCad mapping is what the board
and the schematic are both built against. Worth one datasheet glance anyway.

### This is redundant with a protected cell

Most 3.7 V 350 mAh wearable cells ship with a DW01A + 8205A PCM already welded
to the tab. Two protections in series is harmless — about 50 mΩ total — but it
is redundant. It is on the carrier because bare cells are rev B's stated
assumption. If you source protected packs, leave U4, U5, R6 and C7 unpopulated
and fit a wire link from J4.2 to the nearest GND pad.

### Charge rate

The 0.5C = 175 mA figure needs checking against the XIAO, not against this
board. The XIAO's on-module BQ25101 sets its charge current with an on-module
resistor and ships configured well below 175 mA. Getting 175 mA means changing
that resistor on the module — the carrier has no charger and cannot influence it.

---

## Before you order — four things to check

**1. Verify the Ra-01SH pad map. This is the biggest open risk on the board.**
The SX1262 *signal set* is certain (NSS, SCK, MOSI, MISO, BUSY, DIO1, NRESET,
VCC, GND, ANT). What is provisional is **which castellated pad each signal sits
on**. The map in `RA01SH_PINS` was chosen to put every signal on the same
physical pad the Ra-02 used, so the routing solution carries over and ANT stays
3.5 mm from J6 — but it is not confirmed against a primary mechanical drawing.
Print `out/gerbers/PRAHARI-F_Cu.gbr` at 1:1, seat a real module on it, and check
before you spend money. If it disagrees, correct that one dict and re-run
`gen_footprints.py` then `gen_pcb.py` — nothing else references pad numbers.

**2. Verify the DW01A OD/OC gate assignment.** `OD(1)` drives `G1` (the FET whose
source sits on B−) and `OC(3)` drives `G2`. That is the usual published
arrangement, but swapping them would make over-discharge protection block
charging instead of discharging. It is a two-line change in the `DW_OD`/`DW_OC`
nets in `design.py`.

**3. The mounting holes are still provisional.** Your `Part1.SLDPRT` /
`Part2.SLDPRT` are the newer proprietary SolidWorks format — not OLE2, not ZIP,
no embedded preview — so the enclosure geometry could not be read. The four M2
holes sit at a symmetric 3.5 mm corner inset. Export the enclosure as **STEP or
DXF** and they can be matched exactly.

**4. Re-price the BOM.** Three parts changed and two were added (U4, U5, R6, C7),
so the deck's ₹3,468 parts total and ₹347-per-worker figure are both stale.

---

---

## Risk register

Ranked by what it costs you if it is wrong. Everything marked *open* needs a
human with the physical part or the enclosure; everything else is closed.

| # | Risk | If wrong | State |
|---|---|---|---|
| 1 | **Ra-01SH pad/signal map** | Board is scrap — every SPI and control line lands on the wrong castellation | **Open.** Mitigated as far as it can be without the part: see below |
| 2 | **DW01A OD/OC gate assignment** | Protection blocks charging instead of discharging — the cell can over-discharge | **Open.** Pin *numbering* is confirmed; only which gate each drives is convention |
| 3 | Mounting holes | Board does not fit the enclosure | **Open.** Needs STEP or DXF — the `.SLDPRT` files cannot be read |
| 4 | Reverse cell insertion on J4 | Reverse voltage reaches the XIAO; the DW01A does **not** protect against this | **Open by design.** J4 is silk-marked `+ −`; check crimp order before first power-up |
| 5 | Protection cluster placement | GND pour stops reaching U4's CS pad — DRC catches it | **Closed.** Guarded by `check_design.py` |
| 6 | `BAT_NEG` track width | Overheating on the cell-negative leg | **Closed.** 0.25 mm / 1 oz ≈ 0.9 A vs ~200 mA peak — about 4× margin |
| 7 | Protection redundant with a protected cell | Nothing — two series FET pairs, ~50 mΩ | **Closed.** DNP path documented above |
| 8 | 195 off-grid ERC warnings hiding a real one | A genuine ERC error goes unnoticed | **Closed.** `check_design.py` triages ERC *by category* and fails on anything that is not off-grid or an isolated label |
| 9 | Stale rev A outputs being uploaded to a fab | Wrong board manufactured | **Closed.** Moved to `out/_revA_archive/`; everything in `out/` is regenerated from the current board |
| 10 | 0.5C = 175 mA charge rate | Slower charging than the deck claims | **Closed as not-our-problem.** It is set by a resistor on the XIAO module, not by this carrier |

### On risk 1 — what is and is not verified

Ai-Thinker publish the Ra-01SH only as image-based or CID-font PDFs, so the pad
table could not be read from a primary source. What *is* established:

- **Signal set — confirmed.** VCC, GND, SCK, MISO, MOSI, NSS, NRESET, BUSY, DIO1,
  ANT (plus optional TXEN/RXEN, which this design leaves unconnected).
  `BUSY` is mandatory on the SX1262 and is wired to D1.
- **Body and package — confirmed** from vendor product data: 17.0 × 16.0 × 3.2 mm,
  dual-row stamp-hole SMD, 16 castellated pads — *identical body to the Ra-02*,
  which is why reusing the rev A pad grid is sound.
- **Which pad carries which signal — NOT confirmed.** This is the open item.

Mitigations already in place:

1. The map lives in exactly one dict, `RA01SH_PINS` in `scripts/design.py`.
   Nothing else in the project references pad numbers — the footprint's pin names
   and the netlist are both derived from it, so they cannot disagree.
2. Every signal sits on the same physical pad the Ra-02 used, so a correction is
   a netlist change, not a re-layout, and ANT stays 3.5 mm from J6.
3. **`out/Ra-01SH-checksheet.svg`** is a 1:1 printable verification sheet.

```bash
python scripts/gen_checksheet.py     # writes out/Ra-01SH-checksheet.svg
```

Open it in a browser, print at **100% / "actual size"** (not "fit to page"),
check the 20 mm ruler on the sheet with a caliper, then seat a real Ra-01SH on
the outline and read off whether pad 8 really is NSS. If it disagrees, fix
`RA01SH_PINS` and re-run `gen_footprints.py` then `gen_pcb.py`.

---

## The guard script

`scripts/check_design.py` re-runs every invariant that was established by hand,
so none of them can regress silently:

```bash
python scripts/check_design.py           # design-level checks, fast
python scripts/check_design.py --full    # + DRC, ERC, and a netlist diff
```

It checks, among other things, that no pad is on two nets, that all 11 XIAO GPIO
are assigned and D1 carries `LORA_BUSY`, that all 16 radio pads are mapped, that
ANT is still on pad 15, that the protection chain is wired as a low-side PCM
pin-for-pin, that `BAT_NEG` is *not* on the Power netclass and *is* in the
router's priority list, and that the protection cluster has not drifted from the
placement that pours cleanly.

With `--full` it also asserts DRC 0/0/8, fails on any ERC category other than
off-grid and isolated labels, and diffs the schematic's own exported netlist
against `design.py` — which is what proves the circuit diagram and the board
still describe the same circuit. **Run it before generating any fab output.**

## Antenna — pick one, not both

The Ra-01SH's ANT pad and the IPEX/U.FL connector on the `-P` variant are the
same RF node.

- **J6 whip (default).** Solder **86 mm** of wire (λ/4 at 868 MHz) to the ANT pad
  and, ideally, another 86 mm to the GND pad as a counterpoise. The RF trace from
  the module to J6 is 3.5 mm of 0.9 mm track over solid ground.
- **IPEX pigtail (better).** Use the Ra-01SH-P, fit a U.FL-to-SMA pigtail, leave
  J6 empty. Zero RF trace.

Do not fit both — a second unterminated path is a stub on the antenna port.
No SMA on the carrier: an edge-launch SMA needs its pads on the board outline (a
real copper-to-edge violation), and a vertical SMA would push the RF trace past
10 mm. Two solder pads 3.5 mm away beat both.

---

## Build and verify

Everything is generated from `scripts/design.py` — components, placement and
netlist live in one file, and **both the schematic and the board are built from
it**, so they cannot drift apart.

```bash
KP="$LOCALAPPDATA/Programs/KiCad/10.0/bin/python.exe"
"$KP" scripts/gen_footprints.py   # XIAO + Ra-01SH (+ Ra-02, kept for rollback)
"$KP" scripts/gen_symbols.py      # XIAO, Ra-01SH, Ra-02, DW01A, FS8205A
"$KP" scripts/gen_project.py      # .kicad_pro, lib tables, design rules
"$KP" scripts/gen_sch.py          # schematic
"$KP" scripts/gen_pcb.py          # place, route, pour, stitch
python scripts/gen_checksheet.py  # 1:1 radio pad-map verification sheet
python scripts/check_design.py --full   # guard: invariants + DRC/ERC + netlist diff
```

**`gen_sch.py` is live again in rev B.** rev A had retired it to protect hand
edits made in eeschema, but a diff showed those edits had not changed the
circuit — same refs, wires, labels and net names — so the schematic is
generated from `design.py` once more. That is what keeps board/schematic parity
at 8 cosmetic warnings while the netlist changes underneath.

`scripts/router.py` is a small two-layer maze router (8-way A* on a 0.1 mm grid,
vias costed at 40 grid units so it prefers to stay on one layer) — KiCad ships
no scriptable autorouter.

To re-check:

```bash
CLI="$LOCALAPPDATA/Programs/KiCad/10.0/bin/kicad-cli.exe"
"$CLI" pcb drc --schematic-parity --severity-all --format json -o out/drc.json PRAHARI.kicad_pcb
"$CLI" sch erc --severity-error --severity-warning --format json -o out/erc.json PRAHARI.kicad_sch
```

Expected: DRC **0 violations, 0 unconnected, 8 parity warnings**; ERC **202
warnings** (195 off-grid + 7 isolated pin labels). Anything else is new.

To rebuild the manufacturing outputs — **use these exact flags.** The CLI
defaults differ from what this project ships and will silently change the file
format if you omit them:

```bash
# BOM - the default --fields drops Description and renames the columns
"$CLI" sch export bom -o out/BOM.csv \
  --fields "Reference,Value,Footprint,Description,QUANTITY" \
  --labels "Reference,Value,Footprint,Description,QUANTITY" \
  --group-by "Value,Footprint" PRAHARI.kicad_sch

# gerbers - without --no-protel-ext you get .gtl/.gbl instead of .gbr
"$CLI" pcb export gerbers -o out/gerbers/ --no-protel-ext \
  --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts" \
  PRAHARI.kicad_pcb

# drills - the flag is --excellon-separate-th, not --separate-files
"$CLI" pcb export drill -o out/gerbers/ --format excellon --excellon-separate-th \
  --generate-map --map-format gerberx2 PRAHARI.kicad_pcb

"$CLI" pcb export pos -o out/positions.csv --format csv --units mm --side both PRAHARI.kicad_pcb
"$CLI" pcb render -o out/top.png --side top --width 1600 --height 1000 --quality high --background opaque PRAHARI.kicad_pcb
```

The gerber zip must contain **14 files**, including `PRAHARI-PTH.drl` and
`PRAHARI-NPTH.drl`. A zip with no `.drl` files is unmanufacturable.

## Manufacturing files

Everything a fab needs is in `out/`:

| File | Use |
|---|---|
| `PRAHARI-gerbers.zip` | upload straight to JLCPCB / PCBWay — 14 files |
| `BOM.csv` | 22 line items, test points and mounting holes excluded |
| `positions.csv` | centroid file, both sides |
| `schematic.pdf` | full schematic |
| `PRAHARI.svg` | same schematic, opens in any browser |
| `netlist.net` | schematic netlist — diff it against `design.py` to prove parity |
| `top.png`, `bottom.png` | 3D renders |
| `drc.json`, `erc.json` | the check reports, regenerated after the last board save |
| `Ra-01SH-checksheet.svg` | **print at 1:1** and verify the radio pad map |
| `_revA_archive/` | superseded rev A renders and zips, kept out of the way |

Order settings: **2 layer, 70 × 40 mm, 1.6 mm, 1 oz, HASL or ENIG.** Nothing on
the board needs better than the default process.

## Assembly order

1. U3 (SOIC-8), U4 and U5 (SOT-23-6), then the 0805/1206 passives — smallest first.
2. Q1 (SOT-23), D1 (SOD-123), D2 (0805 LED).
3. R1, R2 on the **back** side.
4. Headers J1, J2, J3, J7, J6; connectors J4, J5.
5. U2 Ra-01SH — hand-solder the castellations, pin-1 dot at the top left.
6. U1 XIAO last, on a 2×7 header or reflowed onto the castellated lands.
7. Two wires: TP1 → XIAO BAT+, TP2 → XIAO BAT−.

Power up with no battery first and check 3V3 at TP5 before fitting the LiPo.
D2 draws ~1.3 mA continuously — leave it unpopulated for battery-life runs.

## Known warnings

**DRC — 8 schematic parity warnings, cosmetic.** `MOTOR_N`, `ANT` and `HAPTIC_G`
are drawn as bare wires with no net labels, so KiCad auto-names them
`Net-(D1-A)`, `Net-(J6-Pin_1)` and `Net-(Q1-G)` in the schematic while
`design.py` names them explicitly on the board. Same copper, different name. To
clear them, add a net label to each of those three wires.

**ERC — 195 `endpoint_off_grid`, pre-existing.** `gen_sch.py` emits symbol
placements and wire stubs at whole-millimetre offsets rather than snapping to the
1.27 mm connection grid. This is **not new in rev B** — running rev A's
`gen_sch.py` produces 174 of the same warnings. rev A's committed schematic
showed only 7 warnings because that file had been round-tripped through eeschema,
which snaps everything to grid on save. Connectivity is unaffected: DRC reports
0 unconnected and parity holds at 8. To clear them, open `PRAHARI.kicad_sch` in
eeschema and save — or snap `PLACE`, the `ACT` offsets and `WIRES` in
`gen_sch.py` to 1.27 mm multiples.

**ERC — 7 `isolated_pin_label`, all intentional.** `VUSB`, `LORA_DIO2`,
`LORA_DIO3`, `LORA_NC1`, `LORA_NC2`, `PPG_IRD`, `PPG_RD`. These are pins brought
out and named but not used, so the pads carry a meaningful net name if you want
to wire them later. `LORA_NC1`/`NC2` are the two pads the SX1278 used for
DIO4/DIO5 that the SX1262 does not populate.

**One unresolved reference designator.** `gen_pcb.py` reports
`24 placed clear, 1 unresolved` — one silkscreen ref in the crowded U4/C7/R6/U5
cluster could not be auto-placed without overlap. Cosmetic; nudge it in pcbnew if
it bothers you.

## A note on the protection cluster placement

The positions and rotations of U4, U5, R6 and C7 in `design.py` are
**load-bearing**. U4 pin 2 (CS) is the middle pad of a SOT-23-6 and both its
neighbours carry tracks off the part, so the ground pour can only reach CS
head-on. Nudging U4 or rotating it closes that wedge and DRC comes back with
`Missing connection: Zone [GND] on F.Cu ↔ Pad 2 [GND] of U4`. Crowding the pocket
further also breaks the F.Cu-to-B.Cu pour tie. This combination was found by
sweeping placements against DRC — if you move any of the four, re-run
`gen_pcb.py` and confirm `unconnected` is still 0.

`BAT_NEG` is also on the `Default` 0.25 mm netclass rather than `Power`, on
purpose: a 0.6 mm track physically cannot reach a SOT-23-6 pad through a 0.35 mm
inter-pad gap, and the router reported `FAILED: ['BAT_NEG->pad2']` while it was
in `Power`. 0.25 mm on 1 oz carries about 0.9 A against a 175 mA charge current.
It is also in the router's `priority` list, because sorting by span would
otherwise route it last, after the short local nets had boxed in those pads.

## Layout

```
PRAHARI-PCB/
├── PRAHARI.kicad_pro / .kicad_sch / .kicad_pcb / .kicad_sym
├── PRAHARI.pretty/          XIAO, Ra-01SH, Ra-02 footprints
├── fp-lib-table, sym-lib-table
├── scripts/                 design.py, router.py, gen_*.py
└── out/                     gerbers, BOM, positions, PDFs, renders, reports
```
