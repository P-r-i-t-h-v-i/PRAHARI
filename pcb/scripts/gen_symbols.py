"""Write PRAHARI.kicad_sym: schematic symbols for the two modules KiCad lacks."""
import os

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# (number, name, x, y, angle, electrical type)
# Power on the top and bottom edges, signals on the sides: that is what lets a
# schematic hang a +3V3 bar above and a GND triangle below without the wire
# having to dog-leg around the signal labels.
XIAO_PINS = [
    ("1",  "D0/A0",    -12.7,  10.16,   0, "bidirectional"),
    ("2",  "D1/A1",    -12.7,   7.62,   0, "bidirectional"),
    ("3",  "D2/A2",    -12.7,   5.08,   0, "bidirectional"),
    ("4",  "D3/A3",    -12.7,   2.54,   0, "bidirectional"),
    ("5",  "D4/SDA",   -12.7,   0.0,    0, "bidirectional"),
    ("6",  "D5/SCL",   -12.7,  -2.54,   0, "bidirectional"),
    ("7",  "D6/TX",    -12.7,  -5.08,   0, "bidirectional"),
    ("8",  "D7/RX",     12.7,  10.16, 180, "bidirectional"),
    ("9",  "D8/SCK",    12.7,   7.62, 180, "bidirectional"),
    ("10", "D9/MISO",   12.7,   5.08, 180, "bidirectional"),
    ("11", "D10/MOSI",  12.7,   2.54, 180, "bidirectional"),
    ("12", "3V3",       -2.54, 15.24, 270, "power_out"),
    ("14", "5V",         2.54, 15.24, 270, "power_out"),
    ("13", "GND",        0.0, -15.24,  90, "power_in"),
]

RA02_PINS = [
    ("14", "RST",  -12.7,   7.62,   0, "input"),
    ("8",  "NSS",  -12.7,   2.54,   0, "input"),
    ("11", "SCK",  -12.7,   0.0,    0, "input"),
    ("10", "MOSI", -12.7,  -2.54,   0, "input"),
    ("9",  "MISO", -12.7,  -5.08,   0, "output"),
    ("15", "ANT",   12.7,  10.16, 180, "passive"),
    ("7",  "DIO0",  12.7,   5.08, 180, "output"),
    ("6",  "DIO1",  12.7,   2.54, 180, "output"),
    ("5",  "DIO2",  12.7,   0.0,  180, "output"),
    ("4",  "DIO3",  12.7,  -2.54, 180, "output"),
    ("3",  "DIO4",  12.7,  -5.08, 180, "output"),
    ("2",  "DIO5",  12.7,  -7.62, 180, "output"),
    ("13", "3V3",    0.0,  15.24, 270, "power_in"),
    ("1",  "GND",   -2.54, -15.24, 90, "power_in"),
    ("12", "GND",    0.0,  -15.24, 90, "power_in"),
    ("16", "GND",    2.54, -15.24, 90, "power_in"),
]


def pin(number, name, x, y, ang, etype, length=2.54):
    return f'''			(pin {etype} line
				(at {x} {y} {ang})
				(length {length})
				(name "{name}" (effects (font (size 1.27 1.27))))
				(number "{number}" (effects (font (size 1.27 1.27))))
			)
'''


def prop(name, value, x, y, hide=False, size=1.27):
    h = "\n					(hide yes)" if hide else ""
    return f'''		(property "{name}" "{value}"
			(at {x} {y} 0)
			(effects
				(font (size {size} {size})){h}
			)
		)
'''


def symbol(name, ref, value, footprint, datasheet, descr, pins, x0, y0, x1, y1):
    s = f'''	(symbol "{name}"
		(pin_names (offset 0.762))
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
'''
    s += prop("Reference", ref, x0, y1 + 5.08)
    s += prop("Value", value, x0, y1 + 2.54)
    s += prop("Footprint", footprint, 0, 0, hide=True)
    s += prop("Datasheet", datasheet, 0, 0, hide=True)
    s += prop("Description", descr, 0, 0, hide=True)
    s += f'''		(symbol "{name}_0_1"
			(rectangle
				(start {x0} {y1})
				(end {x1} {y0})
				(stroke (width 0.254) (type default))
				(fill (type background))
			)
		)
		(symbol "{name}_1_1"
'''
    for p in pins:
        s += pin(*p)
    s += "		)\n	)\n"
    return s


out = '''(kicad_symbol_lib
	(version 20241209)
	(generator "prahari_gen")
	(generator_version "10.0")
'''
out += symbol(
    "XIAO_nRF52840_Sense", "U", "XIAO nRF52840 Sense",
    "PRAHARI:XIAO_nRF52840_Sense",
    "https://wiki.seeedstudio.com/XIAO_BLE/",
    "Seeed XIAO nRF52840 Sense - Cortex-M4F, BLE, IMU, mic, LiPo charger",
    XIAO_PINS, -10.16, -12.7, 10.16, 12.7)
out += symbol(
    "Ai-Thinker_Ra-02", "U", "Ra-02 SX1278",
    "PRAHARI:Ai-Thinker_Ra-02",
    "https://docs.ai-thinker.com/en/lora",
    "Ai-Thinker Ra-02 SX1278 LoRa transceiver, 433 MHz, SPI",
    RA02_PINS, -10.16, -12.7, 10.16, 12.7)
out += ")\n"

open(os.path.join(PROJ, "PRAHARI.kicad_sym"), "w", encoding="utf-8").write(out)
print("wrote PRAHARI.kicad_sym (2 symbols)")
