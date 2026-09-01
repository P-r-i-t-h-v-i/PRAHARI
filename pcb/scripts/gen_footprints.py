# Generates the two custom footprints PRAHARI needs that KiCad does not ship:
#   - Seeed XIAO nRF52840 Sense  (2x7, 2.54mm pitch, 15.24mm row spacing)
#   - Ai-Thinker Ra-02 SX1278    (2x8, 2.00mm pitch, 16.0mm row spacing, castellated)
import os, uuid

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
open(os.path.join(OUT, "XIAO_nRF52840_Sense.kicad_mod"), "w", encoding="utf-8").write(s)

# --------------------------------------------------------------------------
# 2. Ai-Thinker Ra-02 (SX1278)
#    Body 17.0 (X) x 16.0 (Y). 16 castellated pads, 2.0mm pitch, rows at y=+/-8.
#    Pads 1-8  = bottom row (y=+8), left -> right
#    Pads 9-16 = top row    (y=-8), right -> left   (counter-clockwise)
# --------------------------------------------------------------------------
RA02_NAMES = ["GND", "DIO5", "DIO4", "DIO3", "DIO2", "DIO1", "DIO0", "NSS",
              "MISO", "MOSI", "SCK", "GND", "3V3", "RST", "ANT", "GND"]

s = hdr("Ai-Thinker_Ra-02",
        "Ai-Thinker Ra-02 SX1278 433MHz LoRa module, 17x16mm, 16 castellated pads, "
        "2.0mm pitch. VERIFY pad row assignment against your physical module before ordering.",
        "ai-thinker ra-02 sx1278 lora 433mhz module", "smd")
s += txt("Reference", "U**", 0, -10.8, "F.SilkS")
s += txt("Value", "Ai-Thinker_Ra-02", 0, 9.5, "F.Fab")
s += txt("Datasheet", "https://docs.ai-thinker.com/en/lora", 0, 0, "F.Fab", 0.5)
s += txt("Description", "Ra-02 SX1278 LoRa 433MHz", 0, 0, "F.Fab", 0.5)

xs = [-7.0 + 2.0 * i for i in range(8)]
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
open(os.path.join(OUT, "Ai-Thinker_Ra-02.kicad_mod"), "w", encoding="utf-8").write(s)

print("wrote XIAO_nRF52840_Sense.kicad_mod and Ai-Thinker_Ra-02.kicad_mod")
