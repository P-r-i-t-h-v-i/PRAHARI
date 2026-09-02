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

# Ra-01SH (SX1262).  Pad numbers mirror design.RA01SH_PINS, which deliberately
# keeps every signal on the same physical pad the rev A Ra-02 used.  The SX1262
# has no DIO0 and adds a mandatory BUSY; pads 2 and 3 (the SX1278's DIO5/DIO4)
# are unpopulated on this part.
RA01SH_PINS = [
    ("4",  "NRESET", -12.7,   7.62,   0, "input"),
    ("15", "NSS",    -12.7,   2.54,   0, "input"),
    ("12", "SCK",    -12.7,   0.0,    0, "input"),
    ("14", "MOSI",   -12.7,  -2.54,   0, "input"),
    ("13", "MISO",   -12.7,  -5.08,   0, "output"),
    ("1",  "ANT",     12.7,  10.16, 180, "passive"),
    ("5",  "BUSY",    12.7,   5.08, 180, "output"),
    ("6",  "DIO1",    12.7,   2.54, 180, "output"),
    ("7",  "DIO2",    12.7,   0.0,  180, "output"),
    ("8",  "DIO3",    12.7,  -2.54, 180, "output"),
    ("10", "TXEN",    12.7,  -5.08, 180, "passive"),
    ("11", "RXEN",    12.7,  -7.62, 180, "passive"),
    ("3",  "VCC",      0.0,  15.24, 270, "power_in"),
    ("2",  "GND",    -2.54, -15.24, 90, "power_in"),
    ("9",  "GND",      0.0, -15.24, 90, "power_in"),
    ("16", "GND",      2.54, -15.24, 90, "power_in"),
]

# --- battery protection, rev B ------------------------------------------------
# Pin numbers and names are taken from KiCad's own curated symbols
# (Battery_Management:DW01A and Transistor_FET:Q_Dual_NMOS_S1G1S2G2D2D1) so the
# cross-check against the datasheet is preserved.  They are re-drawn here as
# SINGLE-unit symbols because gen_sch.py places one unit per reference, and
# KiCad's dual-FET symbol is split across units A and B.
#
# Electrical types are chosen to be ERC-clean for this circuit: VCC and GND on
# the DW01A are passive rather than power_in, because on this board they sit on
# DW_VDD and BAT_NEG - ordinary local nets with no power-symbol driver.
DW01A_PINS = [
    ("1", "OD",  -10.16,  5.08,   0, "output"),
    ("2", "CS",  -10.16,  0.0,    0, "passive"),
    ("3", "OC",  -10.16, -5.08,   0, "output"),
    ("5", "VCC",  10.16,  5.08, 180, "passive"),
    ("6", "GND",  10.16,  0.0,  180, "passive"),
    ("4", "TD",   10.16, -5.08, 180, "passive"),
]

FS8205A_PINS = [
    ("1", "S1", -10.16,  5.08,   0, "passive"),
    ("2", "G1", -10.16,  0.0,    0, "input"),
    ("3", "S2", -10.16, -5.08,   0, "passive"),
    ("6", "D1",  10.16,  5.08, 180, "passive"),
    ("5", "D2",  10.16,  0.0,  180, "passive"),
    ("4", "G2",  10.16, -5.08, 180, "input"),
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
    "Ai-Thinker_Ra-01SH", "U", "Ra-01SH SX1262",
    "PRAHARI:Ai-Thinker_Ra-01SH",
    "https://docs.ai-thinker.com/en/Ra-01SH",
    "Ai-Thinker Ra-01SH SX1262 LoRa transceiver, 868/915 MHz, SPI",
    RA01SH_PINS, -10.16, -12.7, 10.16, 12.7)
out += symbol(
    "Ai-Thinker_Ra-02", "U", "Ra-02 SX1278",
    "PRAHARI:Ai-Thinker_Ra-02",
    "https://docs.ai-thinker.com/en/lora",
    "Ai-Thinker Ra-02 SX1278 LoRa transceiver, 433 MHz, SPI",
    RA02_PINS, -10.16, -12.7, 10.16, 12.7)
out += symbol(
    "DW01A", "U", "DW01A",
    "Package_TO_SOT_SMD:SOT-23-6",
    "https://components101.com/ics/dw01a-battery-protection-ic",
    "Single-cell Li-ion protection: 4.3 V over-charge, 2.4 V over-discharge",
    DW01A_PINS, -7.62, -7.62, 7.62, 7.62)
out += symbol(
    "FS8205A", "U", "FS8205A",
    "Package_TO_SOT_SMD:SOT-23-6",
    "",
    "Dual common-drain N-channel MOSFET - battery protection switch pair",
    FS8205A_PINS, -7.62, -7.62, 7.62, 7.62)
out += ")\n"

open(os.path.join(PROJ, "PRAHARI.kicad_sym"), "w", encoding="utf-8").write(out)
print("wrote PRAHARI.kicad_sym (5 symbols)")
