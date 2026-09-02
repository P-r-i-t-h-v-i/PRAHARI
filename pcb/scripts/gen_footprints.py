# Generates the custom footprints PRAHARI needs that KiCad does not ship:
#   - Seeed XIAO nRF52840 Sense  (2x7, 2.54mm pitch, 15.24mm row spacing)
#   - Ai-Thinker Ra-01SH SX1262  (2x8, 2.00mm pitch, 16.0mm row spacing, castellated)
#   - Ai-Thinker Ra-02 SX1278    (rev A radio, kept for rollback)
import os, sys, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

OUT = os.path.join(os.path.dirname(__file__), "..", "PRAHARI.pretty")
U = lambda: str(uuid.uuid4())


def hdr(name, descr, tags, attr):
    return f'''(footprint "{name}"
  (version 20241229) (generator "prahari_gen") (generator_version "10.0")
  (layer "F.Cu")
  (descr "{descr}")
  (tags "{tags}")
  (attr {attr})
'''


def txt(kind, text, x, y, layer, size=1.0, thick=0.15):
    return f'''  (property "{kind}" "{text}" (at {x} {y} 0) (layer "{layer}") (uuid "{U()}")
    (effects (font (size {size} {size}) (thickness {thick})))
  )
'''


def fp_text(kind, text, x, y, layer, size=1.0):
    return f'''  (fp_text {kind} "{text}" (at {x} {y} 0) (layer "{layer}") (uuid "{U()}")
    (effects (font (size {size} {size}) (thickness 0.15)))
  )
'''


def line(x1, y1, x2, y2, layer, w=0.12):
    return (f'  (fp_line (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{U()}"))\n')


def rect(x1, y1, x2, y2, layer, w=0.12):
    return (f'  (fp_rect (start {x1} {y1}) (end {x2} {y2}) '
            f'(stroke (width {w}) (type solid)) (fill none) (layer "{layer}") (uuid "{U()}"))\n')


def circle(cx, cy, r, layer, w=0.12, fill="none"):
    return (f'  (fp_circle (center {cx} {cy}) (end {cx + r} {cy}) '
            f'(stroke (width {w}) (type solid)) (fill {fill}) (layer "{layer}") (uuid "{U()}"))\n')


def pad_tht(num, x, y, sx, sy, drill, pin_name=""):
    # Oval through-hole pad: takes a 2.54mm header pin, and the elongated land
    # also catches the module's castellated edge if it is reflowed instead.
    return f'''  (pad "{num}" thru_hole oval (at {x} {y}) (size {sx} {sy}) (drill {drill})
    (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{U()}"))
'''


def pad_smd(num, x, y, sx, sy):
    return f'''  (pad "{num}" smd rect (at {x} {y}) (size {sx} {sy})
    (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{U()}"))
'''


def write(name, s):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)


# --------------------------------------------------------------------------
# 1. Seeed XIAO nRF52840 Sense
#    Local orientation: USB-C faces -Y (up). Body 17.5 (X) x 21.0 (Y).
#    Pads 1-7  = left column  (D0..D6),  top -> bottom
#    Pads 8-14 = right column (D7..5V),  bottom -> top   (counter-clockwise)
# --------------------------------------------------------------------------
XIAO_NAMES = ["D0/A0", "D1/A1", "D2/A2", "D3/A3", "D4/SDA", "D5/SCL", "D6/TX",
              "D7/RX", "D8/SCK", "D9/MISO", "D10/MOSI", "3V3", "GND", "5V"]

s = hdr("XIAO_nRF52840_Sense",
        "Seeed Studio XIAO nRF52840 Sense - 2x7 2.54mm THT/castellated land pattern. "
        "USB-C at -Y. Battery pads are on the module underside: bring VBAT in on the "
        "TP_BAT test points, not through this footprint.",
        "seeed xiao nrf52840 sense module", "through_hole")
s += txt("Reference", "U**", 0, 11.8, "F.SilkS")
s += txt("Value", "XIAO_nRF52840_Sense", 0, 13.2, "F.Fab")
s += txt("Datasheet", "https://wiki.seeedstudio.com/XIAO_BLE/", 0, 0, "F.Fab", 0.5)
s += txt("Description", "Seeed XIAO nRF52840 Sense", 0, 0, "F.Fab", 0.5)

ys = [-7.62 + 2.54 * i for i in range(7)]
for i, y in enumerate(ys):                      # left column, pins 1..7
    s += pad_tht(i + 1, -7.62, y, 2.6, 1.7, 1.0)
for i, y in enumerate(reversed(ys)):            # right column, pins 8..14
    s += pad_tht(i + 8, 7.62, y, 2.6, 1.7, 1.0)

# courtyard + body
s += rect(-8.75, -10.5, 8.75, 10.5, "F.Fab")
s += rect(-9.0, -10.75, 9.0, 10.75, "F.CrtYd", 0.05)
# silkscreen: sides only, keep clear of pads
s += line(-8.75, -10.5, 8.75, -10.5, "F.SilkS")
s += line(-8.75, 10.5, 8.75, 10.5, "F.SilkS")
s += line(-8.75, -10.5, -8.75, -9.2, "F.SilkS")
s += line(-8.75, 10.5, -8.75, 9.2, "F.SilkS")
s += line(8.75, -10.5, 8.75, -9.2, "F.SilkS")
s += line(8.75, 10.5, 8.75, 9.2, "F.SilkS")
# USB-C end marker + pin-1 dot
s += line(-4.0, -10.5, -4.0, -9.6, "F.SilkS")
s += line(4.0, -10.5, 4.0, -9.6, "F.SilkS")
s += fp_text("user", "USB-C", 0, -9.0, "F.SilkS", 0.8)
s += circle(-9.6, -7.62, 0.25, "F.SilkS", 0.12, "solid")
for i, n in enumerate(XIAO_NAMES[:7]):
    s += fp_text("user", n, -7.62, ys[i], "F.Fab", 0.5)
for i, n in enumerate(XIAO_NAMES[7:]):
    s += fp_text("user", n, 7.62, list(reversed(ys))[i], "F.Fab", 0.5)
s += ")\n"
write("XIAO_nRF52840_Sense.kicad_mod", s)


# --------------------------------------------------------------------------
# 2. Ai-Thinker Ra-01SH (SX1262)  -- rev B radio
#
#    Land pattern mirrors KiCad's curated RF_Module:Ai-Thinker-Ra-01-LoRa:
#      16 castellated pads, 2.0 mm pitch, 8 per edge, edges 16.0 mm apart,
#      pad 2.0 (outward) x 1.5 mm, counter-clockwise numbering.
#      Pads 1-8  = LEFT edge  (x = -8), top -> bottom
#      Pads 9-16 = RIGHT edge (x = +8), bottom -> top
#    Body 16.0 (X) x 17.0 (Y) - vendor gives 17.0 x 16.0 x 3.2 mm, and in this
#    orientation the 16 mm axis is the one across the two pad rows.
#
#    Signal names come from design.RA01SH_PINS, which is itself taken from
#    KiCad's curated Ai-Thinker-Ra-01/Ra-02 symbols - so the silkscreen, the
#    fab layer and the netlist cannot disagree.
# --------------------------------------------------------------------------
def ra01sh_names():
    """Invert design.RA01SH_PINS into a pad-ordered name list, pads 1..16."""
    by_pad = {}
    for sig, pads in D.RA01SH_PINS.items():
        for q in ([pads] if isinstance(pads, str) else pads):
            by_pad[int(q)] = sig
    return [by_pad.get(i, "?") for i in range(1, 17)]


RA01SH_NAMES = ra01sh_names()
RA_YS = [-7.0 + 2.0 * i for i in range(8)]

s = hdr("Ai-Thinker_Ra-01SH",
        "Ai-Thinker Ra-01SH SX1262 803-930MHz LoRa module, 17x16x3.2mm, 16 castellated "
        "pads, 2.0mm pitch. Land pattern and pin numbering follow KiCad's curated "
        "RF_Module Ai-Thinker-Ra-01. ANT is pad 1. Verify against your module before ordering.",
        "ai-thinker ra-01sh sx1262 lora 868mhz 915mhz module", "smd")
s += txt("Reference", "U**", 0, -11.5, "F.SilkS")
s += txt("Value", "Ai-Thinker_Ra-01SH", 0, 10.5, "F.Fab")
s += txt("Datasheet", "https://docs.ai-thinker.com/en/Ra-01SH", 0, 0, "F.Fab", 0.5)
s += txt("Description", "Ra-01SH SX1262 LoRa 868/915MHz", 0, 0, "F.Fab", 0.5)

for i, y in enumerate(RA_YS):                   # left edge, pads 1..8
    s += pad_smd(i + 1, -8.0, y, 2.0, 1.5)
for i, y in enumerate(reversed(RA_YS)):         # right edge, pads 9..16
    s += pad_smd(i + 9, 8.0, y, 2.0, 1.5)

s += rect(-8.0, -8.5, 8.0, 8.5, "F.Fab")
s += rect(-9.4, -9.1, 9.4, 9.1, "F.CrtYd", 0.05)
# silkscreen along the two pad-free edges only
s += line(-8.0, -8.5, 8.0, -8.5, "F.SilkS")
s += line(-8.0, 8.5, 8.0, 8.5, "F.SilkS")
# pin-1 dot, outboard of pad 1
s += circle(-9.4, -7.0, 0.3, "F.SilkS", 0.12, "solid")
s += fp_text("user", "Ra-01SH", 0, -1.0, "F.SilkS", 1.0)
s += fp_text("user", "SX1262 868MHz", 0, 0.8, "F.SilkS", 0.8)
s += fp_text("user", "ANT=1", 0, 2.6, "F.SilkS", 0.8)
for i, n in enumerate(RA01SH_NAMES[:8]):
    s += fp_text("user", n, -5.6, RA_YS[i], "F.Fab", 0.5)
for i, n in enumerate(RA01SH_NAMES[8:]):
    s += fp_text("user", n, 5.6, list(reversed(RA_YS))[i], "F.Fab", 0.5)
s += ")\n"
write("Ai-Thinker_Ra-01SH.kicad_mod", s)


# --------------------------------------------------------------------------
# 3. Ai-Thinker Ra-02 (SX1278)  -- rev A radio, kept so rev A can be rebuilt
#    Body 17.0 (X) x 16.0 (Y). 16 castellated pads, 2.0mm pitch, rows y=+/-8.
# --------------------------------------------------------------------------
# rev A's inferred map, kept verbatim only so rev A can be rebuilt byte-for-byte.
# It is WRONG - KiCad's curated Ai-Thinker-Ra-02 gives 1=GND 2=GND 3=VDD 4=NRESET
# 5=DIO0 6=DIO1 7=DIO2 8=DIO3 9=GND 10=DIO4 11=DIO5 12=SCK 13=MISO 14=MOSI
# 15=NSS 16=GND, and no castellated ANT at all (the Ra-02 uses its IPEX).
RA02_NAMES = ["GND", "DIO5", "DIO4", "DIO3", "DIO2", "DIO1", "DIO0", "NSS",
              "MISO", "MOSI", "SCK", "GND", "3V3", "RST", "ANT", "GND"]
xs = [-7.0 + 2.0 * i for i in range(8)]

s = hdr("Ai-Thinker_Ra-02",
        "Ai-Thinker Ra-02 SX1278 433MHz LoRa module, 17x16mm, 16 castellated pads, "
        "2.0mm pitch. SUPERSEDED by Ai-Thinker_Ra-01SH in rev B - kept for rollback. "
        "VERIFY pad row assignment against your physical module before ordering.",
        "ai-thinker ra-02 sx1278 lora 433mhz module", "smd")
s += txt("Reference", "U**", 0, -10.8, "F.SilkS")
s += txt("Value", "Ai-Thinker_Ra-02", 0, 9.5, "F.Fab")
s += txt("Datasheet", "https://docs.ai-thinker.com/en/lora", 0, 0, "F.Fab", 0.5)
s += txt("Description", "Ra-02 SX1278 LoRa 433MHz", 0, 0, "F.Fab", 0.5)

for i, x in enumerate(xs):                      # bottom row, pins 1..8
    s += pad_smd(i + 1, x, 8.0, 1.2, 2.4)
for i, x in enumerate(reversed(xs)):            # top row, pins 9..16
    s += pad_smd(i + 9, x, -8.0, 1.2, 2.4)

s += rect(-8.5, -8.0, 8.5, 8.0, "F.Fab")
s += rect(-8.9, -9.6, 8.9, 9.6, "F.CrtYd", 0.05)
s += line(-8.5, -6.4, -8.5, 6.4, "F.SilkS")
s += line(8.5, -6.4, 8.5, 6.4, "F.SilkS")
s += circle(-8.9, 9.0, 0.25, "F.SilkS", 0.12, "solid")
s += fp_text("user", "Ra-02", 0, 0, "F.SilkS", 1.0)
s += fp_text("user", "433MHz", 0, 1.6, "F.SilkS", 0.8)
for i, n in enumerate(RA02_NAMES[:8]):
    s += fp_text("user", n, xs[i], 6.6, "F.Fab", 0.4)
for i, n in enumerate(RA02_NAMES[8:]):
    s += fp_text("user", n, list(reversed(xs))[i], -6.6, "F.Fab", 0.4)
s += ")\n"
write("Ai-Thinker_Ra-02.kicad_mod", s)

print("wrote XIAO_nRF52840_Sense, Ai-Thinker_Ra-01SH and Ai-Thinker_Ra-02 .kicad_mod")
print("Ra-01SH pad names:", ", ".join(
    "%d=%s" % (i + 1, n) for i, n in enumerate(RA01SH_NAMES)))
