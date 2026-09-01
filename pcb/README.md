# PRAHARI — carrier board, rev A

Prototype carrier PCB for **PRAHARI, The Countdown Band** (Point Break, SIH 2026, PS 26181).

**70 × 40 mm, 2 layer, 1.6 mm FR4.** Every active part is an off-the-shelf module
on a 2.54 mm header, matching the deck's *"four modules, nothing custom — all
stocked on Robu.in today"*.

| | |
|---|---|
| Board | 70 × 40 mm, 2 mm corner radius, 4 × M2 mounting holes |
| Stackup | 2 layer, 1.6 mm, 1 oz, GND pour both sides, 178 stitching vias |
| Routing | 308 tracks / 733 mm, 0.25 mm signal, 0.5 mm power, 0.9 mm RF |
| Pads | 59 SMD, 39 plated through |
| Process | 0.25 mm track / 0.2 mm space / 0.3 mm drill — cheapest JLCPCB & PCBWay tier |
| DRC | **0 violations, 0 unconnected, 0 schematic-parity issues** |
| ERC | 7 warnings, all deliberate (see *Known warnings*) |

---

## What's on it

```
 ANT ▫▫ GND      C3  C1      PRAHARI rev A
 ┌──────────────┐              ┌──────────────────┐
 │  U2  Ra-02   │       C2     │ U1  XIAO         │ USB-C
 │  SX1278      │   TP BAT±    │ nRF52840 Sense   │
 │  433 MHz     │   TP 3V3 GND │                  │
 └──────────────┘   TP SDA SCL └──────────────────┘
 ┌──────┐ ┌────┐ ┌────┐ ┌────┐            ┌──────┐
 │  J1  │ │ J2 │ │ J3 │ │ J7 │            │  U3  │
 │MAX301│ │MLX │ │AHT │ │I2C │            │ATECC │
 └──────┘ └────┘ └────┘ └────┘            └──────┘
  [J4 BAT]  [J5 MOTOR]  Q1 D1 D2 R3 R4 R5  C4 C5
```

| Ref | Part | Role |
|---|---|---|
| **U1** | Seeed XIAO nRF52840 Sense | MCU, BLE, IMU + mic, LiPo charger |
| **U2** | Ai-Thinker Ra-02 (SX1278) | LoRa 433 MHz, band-to-band mesh |
| **U3** | ATECC608A-SSHDA (SOIC-8) | secure element for the anonymised uplink |
| **J1** | MAX30100 breakout, 1×7 | red/IR PPG — heart rate |
| **J2** | MLX90614 breakout, 1×4 | IR thermopile — wrist skin temperature |
| **J3** | AHT20 breakout, 1×4 | air temperature + RH — the WBGT inputs |
| **J7** | 1×4 header | spare I2C |
| **J4** | JST-PH 2 | LiPo in |
| **J5** | JST-PH 2 | vibration motor |
| **J6** | 2 solder pads | 433 MHz whip + counterpoise |

## GPIO budget

The XIAO brings out exactly 11 GPIO. All 11 are used, none spare:

| Pin | Net | | Pin | Net |
|---|---|---|---|---|
| D0 | LORA_DIO1 | | D6 | HAPTIC_PWM |
| D1 | LORA_DIO0 | | D7 | PPG_INT |
| D2 | LORA_RST | | D8 | SPI_SCK |
| D3 | LORA_NSS | | D9 | SPI_MISO |
| D4 | SDA | | D10 | SPI_MOSI |
| D5 | SCL | | | |

Battery voltage needs no external divider — the XIAO reads VBAT internally on
P0.31, gated by P0.14, and neither pin reaches the 2×7 header.

## Power

You chose the XIAO's built-in BQ25101 rather than a second charger, so the
carrier has **no charging circuit**. The battery path is:

```
J4 (JST-PH) ──► TP1 (BAT+) ──wire──► XIAO BAT+ pad  (module underside)
             ──► TP2 (BAT–) ──wire──► XIAO BAT– pad
```

The XIAO's battery pads are on its underside and do not come out on the 2×7
header, so those two short wires are unavoidable with a header-mounted module.
TP1/TP2 put them 3 mm from the module instead of across the board.

The 3V3 rail is sourced by the XIAO's regulator. Worst case is a LoRa transmit
burst at +20 dBm — about 120 mA for a few tens of ms — which is why C1 is 100 µF
right at the Ra-02's 3V3 pad, with C3 (100 nF) beside it.

---

## Before you order — three things to check

**1. Verify the Ra-02 land pattern.** This is the one measurement I could not
confirm against a primary mechanical drawing. The module is 17 × 16 mm with 16
castellated pads on a 2.0 mm pitch, and the pin *order* (1 = GND, 2 = DIO5, …
15 = ANT, 16 = GND) is well documented — but which pins sit in which of the two
rows I inferred from the standard counter-clockwise convention. Put a real Ra-02
on a printout of `out/gerbers/PRAHARI-F_Cu.gbr` at 1:1 before you spend money,
or drop a vendor footprint into `PRAHARI.pretty/` to replace mine.

**2. The GY-MAX30100 breakout has 1.8 V pull-ups.** The common red MAX30100
board pulls SDA/SCL to its internal 1.8 V rail. This carrier pulls the same bus
to 3V3 through R1/R2 (4k7, on the back). Two rails fighting over one bus is a
bad idea, so pick one:

- use a MAX30100 board that has been modded to pull up to 3V3 (the usual fix —
  lift the two pull-ups and jumper them to VIN), **or**
- leave R1 and R2 unpopulated and let the module's 1.8 V pull-ups drive the bus.

Leaving both populated as shipped will bias the bus and can upset the other
three I2C devices. **MAX30122 or MAX30102 boards do not have this problem** and
drop straight in.

**3. The mounting holes are provisional.** Your `Part1.SLDPRT` / `Part2.SLDPRT`
are the newer proprietary SolidWorks format — not OLE2, not ZIP, and with no
embedded preview — so I could not read the enclosure geometry. The four M2 holes
sit at a symmetric 3.5 mm corner inset. Export the enclosure as **STEP or DXF**
and I will match them exactly.

---

## Antenna — pick one, not both

The Ra-02's ANT pad and its on-board IPEX/U.FL connector are the same RF node.

- **J6 whip (default).** Solder 173 mm of wire (λ/4 at 433 MHz) to the ANT pad
  and, ideally, another 173 mm to the GND pad as a counterpoise. The RF trace
  from the module to J6 is 3.5 mm of 0.9 mm track over solid ground.
- **IPEX pigtail (better).** Fit a U.FL-to-SMA pigtail on the module and leave J6
  empty. Zero RF trace.

Do not fit both — a second unterminated path is a stub on the antenna port.

I deliberately did not put an SMA on the carrier. An edge-launch SMA needs its
pads on the board outline (a real copper-to-edge violation, not a false one),
and a vertical SMA does not fit next to the module without pushing the RF trace
past 10 mm. Two solder pads 3.5 mm away beat both.

---

## Build and verify

Everything is generated from `scripts/design.py` — components, placement and
netlist live in one file, and both the schematic and the board are built from
it, so they cannot drift apart.

```bash
KP="$LOCALAPPDATA/Programs/KiCad/10.0/bin/python.exe"
"$KP" scripts/gen_footprints.py   # XIAO + Ra-02 land patterns
"$KP" scripts/gen_symbols.py      # XIAO + Ra-02 schematic symbols
"$KP" scripts/gen_project.py      # .kicad_pro, lib tables, design rules
"$KP" scripts/gen_pcb.py          # place, route, pour, stitch
"$KP" scripts/gen_sch.py          # schematic
```

`scripts/router.py` is a small two-layer maze router (8-way A* on a 0.1 mm grid,
vias costed at 40 grid units so it prefers to stay on one layer) — KiCad ships
no scriptable autorouter.

To re-check:

```bash
CLI="$LOCALAPPDATA/Programs/KiCad/10.0/bin/kicad-cli.exe"
"$CLI" pcb drc --schematic-parity --severity-all --format json -o out/drc.json PRAHARI.kicad_pcb
"$CLI" sch erc --severity-error --severity-warning --format json -o out/erc.json PRAHARI.kicad_sch
```

## Manufacturing files

Everything a fab needs is in `out/`:

| File | Use |
|---|---|
| `PRAHARI-gerbers.zip` | upload straight to JLCPCB / PCBWay |
| `BOM.csv` | 20 line items, test points and mounting holes excluded |
| `positions.csv` | centroid file, both sides |
| `schematic.pdf` | full schematic |
| `top.png`, `bottom.png` | 3D renders |
| `drc.json`, `erc.json` | the clean check reports |

Order settings: **2 layer, 70 × 40 mm, 1.6 mm, 1 oz, HASL or ENIG.** Nothing on
the board needs better than the default process.

## Assembly order

1. U3 (SOIC-8) and the 0805/1206 passives — smallest first, hot air or iron.
2. Q1 (SOT-23), D1 (SOD-123), D2 (0805 LED).
3. R1, R2 on the **back** side.
4. Headers J1, J2, J3, J7, J6; connectors J4, J5.
5. U2 Ra-02 — hand-solder the castellations, pin-1 dot at the top left.
6. U1 XIAO last, on a 2×7 header or reflowed onto the castellated lands.
7. Two wires: TP1 → XIAO BAT+, TP2 → XIAO BAT–.

Power up with no battery first and check 3V3 at TP5 before fitting the LiPo.
D2 draws ~1.3 mA continuously — leave it unpopulated for battery-life runs.

## Known warnings

Seven ERC `isolated_pin_label` warnings, all intentional: `VUSB`,
`LORA_DIO2`–`LORA_DIO5`, `PPG_IRD`, `PPG_RD`. These are pins that are brought
out and named but not used, so the pads carry a meaningful net name if you want
to wire them later. They are named rather than left floating on purpose.

## Layout

```
PRAHARI-PCB/
├── PRAHARI.kicad_pro / .kicad_sch / .kicad_pcb / .kicad_sym
├── PRAHARI.pretty/          XIAO + Ra-02 footprints
├── fp-lib-table, sym-lib-table
├── scripts/                 design.py, router.py, gen_*.py
└── out/                     gerbers, BOM, positions, PDFs, renders, reports
```
