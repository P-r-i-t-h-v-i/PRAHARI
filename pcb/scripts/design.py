"""PRAHARI countdown band - carrier board rev B, single source of truth.

Board: 70 x 40 mm, 2-layer.  Every active part is an off-the-shelf module.

rev B upgrades the sensing, radio and power chain over rev A:
    PPG          MAX30100  -> MAX30102   (glass shield, ambient cancellation, 3V3)
    skin temp    MLX90614  -> MAX30208   (contact, +/-0.1 C, no optical drift)
    ambient      AHT20     -> AHT20      (unchanged - the WBGT wet-bulb input)
    radio        Ra-02     -> Ra-01SH    (SX1278 -> SX1262: 4.2 mA RX, DC-DC, +22 dBm)
    display      0.96in    -> 0.91in     (same SSD1306 driver, lower peak current)
    battery      bare LiPo -> DW01A + FS8205A protection on the carrier
    actuator     1027 ERM coin motor + 2N7002 low-side switch (unchanged)

BAND CHANGE.  The Ra-01SH is an SX1262 part covering 803-930 MHz - it does NOT
cover 433 MHz like the Ra-02 it replaces.  The quarter-wave whip on J6 therefore
drops from 173 mm to 86 mm, which is a great deal more wearable on a wrist.  In
India, keep the radio inside the de-licensed 865-867 MHz sub-band.

GPIO budget on the XIAO nRF52840 Sense is exactly 11 pins, and all 11 are used.
The SX1262 drops DIO0 and adds a mandatory BUSY, so D1 changes role but the
budget still balances exactly:

    D0  LORA_DIO1      D4  SDA          D8  SPI_SCK
    D1  LORA_BUSY      D5  SCL          D9  SPI_MISO
    D2  LORA_RST       D6  HAPTIC_PWM   D10 SPI_MOSI
    D3  LORA_NSS       D7  PPG_INT

Battery voltage needs no external divider: the XIAO reads VBAT internally on
P0.31, gated by P0.14 - neither pin is brought out to the 2x7 header.
"""

BOARD_W, BOARD_H = 70.0, 40.0
CORNER_R = 2.0
ORIGIN = (30.0, 40.0)          # board top-left on the drawing sheet

# ------------------------------------------------------- Ra-01SH pad mapping
# Sourced from KiCad's curated RF_Module library: the Ai-Thinker-Ra-01 and
# Ai-Thinker-Ra-02 symbols, which agree with each other on pads 2-16 and are
# corroborated by the shipped Ai-Thinker-Ra-01-LoRa land pattern (16 pads, 2.0 mm
# pitch, 8 per edge, 16 mm between edges, counter-clockwise numbering).
#
#     pad  1  ANT      (the Ra-02 has GND here instead - it uses its IPEX
#                       connector rather than a castellated antenna pad)
#     pad  2  GND        pad  9  GND        pad 16  GND
#     pad  3  VDD/VCC    pad 10  DIO4 -> TXEN on the SX126x
#     pad  4  NRESET     pad 11  DIO5 -> RXEN on the SX126x
#     pad  5  DIO0 -> BUSY on the SX126x
#     pad  6  DIO1       pad 12  SCK
#     pad  7  DIO2       pad 13  MISO
#     pad  8  DIO3       pad 14  MOSI
#                        pad 15  NSS
#
# This REPLACES the map rev A used, which was inferred from a counter-clockwise
# convention and was wrong on almost every pad - notably it put ANT on pad 15,
# which is really NSS.  rev A's gerbers would not have produced a working radio.
#
# REMAINING INFERENCE: the curated data is for the SX1278 Ra-01/Ra-02.  The
# Ra-01SH is the SX1262 part in the same 16-pad package, and the SX126x has no
# DIO0/DIO4/DIO5 - it has BUSY (mandatory), DIO1..DIO3, and optional TXEN/RXEN.
# Mapping BUSY onto the DIO0 pad and TXEN/RXEN onto the DIO4/DIO5 pads assumes
# Ai-Thinker kept the pad order across the family.  That is very likely - same
# package, same vendor, same pin count - but it is not proven, so the 1:1
# checksheet is still worth printing.  TXEN/RXEN are left unconnected, which the
# Ra-01S/SH reference wiring confirms is valid (the module switches internally).
RA01SH_PINS = {
    "ANT":    "1",
    "GND":    ["2", "9", "16"],
    "VCC":    "3",
    "NRESET": "4",
    "BUSY":   "5",
    "DIO1":   "6",
    "DIO2":   "7",
    "DIO3":   "8",
    "TXEN":   "10",
    "RXEN":   "11",
    "SCK":    "12",
    "MISO":   "13",
    "MOSI":   "14",
    "NSS":    "15",
}

# --------------------------------------------------------- DW01A / FS8205A
# DW01A, SOT-23-6:  1=OD  2=CS  3=OC  4=TD  5=VCC  6=GND
#   Over-charge 4.3 V (release 4.1 V), over-discharge 2.4 V (release 3.0 V).
#   Pin numbering taken from KiCad's curated Battery_Management:DW01A symbol.
#   NOTE: several secondary web sources instead give "1=OC 2=OD 3=CS 4=VSS
#   5=VDD 6=NC".  That variant cannot be right - a real DW01A has BOTH VCC and
#   GND plus a TD test pin - so the KiCad mapping is used here, and it is also
#   what the schematic symbol enforces, which keeps board/schematic parity.
#   Worth one datasheet glance before you fabricate.
#
# FS8205A, SOT-23-6, dual common-drain N-channel:
#   1=S1  2=G1  3=S2  4=G2  5=D2  6=D1  (5 and 6 internally tied).
#   Confirmed against KiCad's Transistor_FET:Q_Dual_NMOS_S1G1S2G2D2D1, whose
#   pin order is exactly the 8205A arrangement.
#
# *** VERIFY the OD/OC gate assignment. ***  OD(1) drives G1 - the FET whose
# source sits on B- - and OC(3) drives G2, on the P- side.  That is the usual
# published arrangement, but swapping the two would make over-discharge
# protection block charging instead of discharging.  It is a two-line change
# in the DW_OD / DW_OC nets below.
#
# Topology is the standard low-side PCM: the cell's NEGATIVE leg runs through
# the two FETs in series before it becomes system ground.  That is why J4 pin 2
# is no longer GND - it is BAT_NEG, and it must stay clear of the ground pour.
#     cell+ -> J4.1 -> VBAT (system +, and DW01A VCC via R6)
#     cell- -> J4.2 -> BAT_NEG -> FS8205A S1 -> [common drain] -> S2 -> GND
#     DW01A GND(6) on BAT_NEG (cell-), CS(2) on GND (pack-), gates G1/G2
#
# NOTE: most 3.7 V 350 mAh wearable cells already ship with a DW01A+8205A PCM
# on the tab.  This carrier protection is therefore redundant with a protected
# pack - harmless (two series FET pairs, ~50 mOhm total) but redundant.  It is
# here because bare cells are the design assumption for rev B.

# ---------------------------------------------------------------- components
# ref: (footprint, value, x, y, rotation_deg, side, description)
#      x/y are board-relative mm, measured to the footprint origin.
COMPONENTS = {
    # --- modules -----------------------------------------------------------
    "U1":  ("PRAHARI:XIAO_nRF52840_Sense", "XIAO nRF52840 Sense",
            54.0, 12.5, 0, "F", "MCU: Cortex-M4F, BLE, on-board IMU + mic + BQ25101 LiPo charger"),
    # y 13.5 -> 15.0: this land pattern is 17 mm tall in this orientation, so its
    # courtyard reached y = 4.4 and left no room for J6 above it.
    "U2":  ("PRAHARI:Ai-Thinker_Ra-01SH", "Ra-01SH SX1262",
            20.0, 16.5, 0, "F", "LoRa SX1262 868/915 MHz, band-to-band mesh, 4.2 mA RX"),
    "U3":  ("Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "ATECC608A-SSHDA",
            61.0, 29.0, 0, "F", "Secure element: key storage for the anonymised uplink"),

    # --- sensor breakouts (I2C), rot 90 so the pin rows run left-to-right ---
    # MAX30102 replaces the MAX30100: it adds a glass shield and ambient light
    # cancellation, and its breakouts run the bus at 3V3 - which retires rev A's
    # "1.8 V pull-ups fighting R1/R2" warning entirely.  Same 1x7 pin order.
    "J1":  ("Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical", "MAX30102",
            5.0, 28.0, 90, "F", "Red/IR PPG - heart rate, IMU-gated"),
    # MAX30208 replaces the MLX90614.  The IR thermopile had to see the skin
    # through an air gap that wrist curvature keeps changing; a contact digital
    # sensor does not care.  +/-0.1 C clinical accuracy, I2C 0x50.
    "J2":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "MAX30208",
            24.5, 28.0, 90, "F", "Contact skin temperature - +/-0.1 C clinical, I2C 0x50"),
    "J3":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "AHT20",
            36.0, 28.0, 90, "F", "Air temperature + RH - the WBGT inputs"),
    # Pin order is 3V3 / GND / SCL / SDA, pin 1 nearest J3.  The 0.91in SSD1306
    # OLED plugs in here; the common breakouts ship in two silk orders
    # (GND-VCC-SCL-SDA and VCC-GND-SCL-SDA), so wire it by label, not position.
    # 0.91in 128x32 replaces the 0.96in 128x64: same SSD1306 driver and same
    # 0x3C address, smaller panel, lower peak charge-pump current (<15 mA).
    #
    # NB: Value and Description must match the schematic's J7 fields, or DRC
    # --schematic-parity reports footprint_symbol_field_mismatch.  Both the
    # board and the schematic are generated from this file, so they cannot drift.
    "J7":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "OLED 0.91in",
            47.5, 28.0, 90, "F", "0.91in SSD1306 128x32 I2C OLED at 0x3C - countdown display"),

    # --- power, actuator, antenna -----------------------------------------
    "J4":  ("Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "LiPo 3.7V 350mAh",
            10.0, 33.0, 0, "F", "Bare cell in - protected by U4/U5, then to XIAO BAT pads via TP1/TP2"),
    "J5":  ("Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "HAPTIC",
            30.0, 33.0, 0, "F", "1027 ERM coin motor - hazard and strain patterns"),
    # 868 MHz antenna: two solder pads directly above the module's ANT pad.
    # A quarter-wave whip is 86 mm of wire; pin 2 is the counterpoise.  This
    # keeps the RF trace to 3.5 mm - an edge-launch SMA would need its pads on
    # the board outline, and a vertical SMA would push the trace past 10 mm.
    # For a proper antenna, use the Ra-01SH-P variant's own IPEX connector and
    # leave J6 open.  Do not fit both.  (Note the plain Ra-01SH brings ANT out on
    # pad 1; the -P variant fits IPEX instead, exactly as Ra-01 vs Ra-02 differ.)
    # Moved from (15, 2): ANT is pad 1 now, not pad 15, so the module's antenna
    # pad sits at board-relative (12, 6.5).  rot 0 (not 90) so the two header
    # pads run left-to-right - at rot 90 they run along +y, which would put the
    # GND counterpoise pin physically between the feed pin and the module's ANT
    # pad.  This gives a 4.5 mm RF run on 0.9 mm track over solid ground.
    "J6":  ("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "ANT WHIP",
            12.0, 5.0, 180, "F", "868 MHz whip (86 mm) / counterpoise solder pads"),

    "Q1":  ("Package_TO_SOT_SMD:SOT-23", "2N7002", 37.0, 36.0, 0, "F", "Haptic low-side switch"),
    "D1":  ("Diode_SMD:D_SOD-123", "1N4148W", 42.0, 36.0, 0, "F", "Motor flyback clamp"),
    "D2":  ("LED_SMD:LED_0805_2012Metric", "GRN", 48.0, 36.0, 0, "F", "3V3 power LED"),

    # --- battery protection (new in rev B) --------------------------------
    # On the BACK, beside J4.  It started on the front-left, but the corrected
    # radio pinout needs that pocket for the antenna feed and the VCC
    # decoupling.  The back was nearly empty (only R1/R2), and J4/J5 are
    # through-hole, so BAT_NEG reaches this side without an extra via.
    #
    # U4'S ORIENTATION IS LOAD-BEARING.  U4 pin 2 (CS) is the
    # middle pad of a SOT-23-6 and its neighbours (pin 1 OD, pin 3 OC) both carry
    # tracks off the part, so the GND pour can only reach CS head-on.  Nudging U4
    # left, or rotating it, closes that wedge and DRC comes back with
    #     Missing connection: Zone [GND] on F.Cu <-> Pad 2 [GND] of U4
    # Crowding the pocket further also breaks the F.Cu-to-B.Cu pour tie.  This
    # combination was found by sweeping placements against DRC; if you move any
    # of the four, re-run gen_pcb.py and check "unconnected" is still 0.
    "U4":  ("Package_TO_SOT_SMD:SOT-23-6", "DW01A", 18.0, 32.0, 0, "B",
            "Li-ion protection: 4.3 V over-charge, 2.4 V over-discharge, over-current"),
    "U5":  ("Package_TO_SOT_SMD:SOT-23-6", "FS8205A", 18.0, 37.0, 0, "B",
            "Dual common-drain N-MOSFET - the protection switch pair"),
    "R6":  ("Resistor_SMD:R_0805_2012Metric", "100R", 23.0, 32.0, 0, "B", "DW01A VDD series"),
    "C7":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 23.0, 35.5, 0, "B", "DW01A VDD decoupling"),

    # --- passives ----------------------------------------------------------
    # Moved from (35,12)/(39,12) in rev A.  At the old spot R1's SDA pad was
    # boxed in by LORA_NSS above and to its left, the +3V3 feed to R1.1 below,
    # and VBAT on the front - the router could not reach it (FAILED: SDA->pad6)
    # and the SDA pull-up was left floating.  Here both pads route cleanly and
    # the pull-ups sit right beside the sensor row they serve.
    "R1":  ("Resistor_SMD:R_0805_2012Metric", "4k7", 44.0, 24.0, 0, "B", "SDA pull-up"),
    "R2":  ("Resistor_SMD:R_0805_2012Metric", "4k7", 48.0, 24.0, 0, "B", "SCL pull-up"),
    "R3":  ("Resistor_SMD:R_0805_2012Metric", "1k",  52.0, 36.0, 0, "F", "LED series"),
    "R4":  ("Resistor_SMD:R_0805_2012Metric", "100R", 37.0, 33.0, 0, "F", "Gate series"),
    "R5":  ("Resistor_SMD:R_0805_2012Metric", "100k", 41.0, 33.0, 0, "F", "Gate pull-down"),

    # C1/C3 moved from (31, 2)/(25, 2) to the module's left edge.  VCC is pad 3 at
    # board-relative (12, 12) in the curated pinout; the old spots were chosen
    # for the wrong map and sat ~15 mm from the real VCC pad.  C3 sits closest
    # because a 100 nF must be nearest the pin; C1 is bulk and tolerates more.
    "C1":  ("Capacitor_SMD:C_1206_3216Metric", "100uF", 8.0, 9.0, 90, "F", "LoRa TX bulk (118 mA at +22 dBm)"),
    "C2":  ("Capacitor_SMD:C_0805_2012Metric", "10uF", 42.0, 12.0, 0, "F", "3V3 bulk at the XIAO"),
    "C3":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 8.0, 13.5, 90, "F", "Ra-01SH decoupling"),
    "C4":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 61.0, 34.0, 0, "F", "ATECC608A decoupling"),
    "C5":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 50.0, 33.0, 0, "F", "Sensor rail decoupling"),
    "C6":  ("Capacitor_SMD:C_0805_2012Metric", "10uF", 17.0, 36.0, 0, "F", "VBAT bulk"),

    # --- test points / mounting -------------------------------------------
    "TP1": ("TestPoint:TestPoint_Pad_D2.0mm", "BAT+", 33.0, 9.0, 0, "F", "Wire to XIAO BAT+ pad"),
    "TP2": ("TestPoint:TestPoint_Pad_D2.0mm", "BAT-", 39.0, 9.0, 0, "F", "Wire to XIAO BAT- pad"),
    "TP5": ("TestPoint:TestPoint_Pad_D2.0mm", "3V3",  33.0, 15.0, 0, "F", ""),
    "TP6": ("TestPoint:TestPoint_Pad_D2.0mm", "GND",  39.0, 15.0, 0, "F", ""),
    "TP3": ("TestPoint:TestPoint_Pad_D2.0mm", "SDA",  33.0, 21.0, 0, "F", ""),
    "TP4": ("TestPoint:TestPoint_Pad_D2.0mm", "SCL",  39.0, 21.0, 0, "F", ""),

    "MH1": ("MountingHole:MountingHole_2.2mm_M2", "M2", 3.5, 3.5, 0, "F", ""),
    "MH2": ("MountingHole:MountingHole_2.2mm_M2", "M2", 66.5, 3.5, 0, "F", ""),
    "MH3": ("MountingHole:MountingHole_2.2mm_M2", "M2", 3.5, 36.5, 0, "F", ""),
    "MH4": ("MountingHole:MountingHole_2.2mm_M2", "M2", 66.5, 36.5, 0, "F", ""),
}

_R = RA01SH_PINS   # shorthand for the netlist below

# ---------------------------------------------------------------------- nets
# net name -> [(ref, pad), ...]
NETS = {
    # System ground == pack negative (P-), i.e. the DRAIN side of the FET pair.
    # The cell's own negative leg is BAT_NEG and is deliberately NOT in here.
    "GND": [
        ("U1", "13"),
        *[("U2", _p) for _p in _R["GND"]],
        ("U3", "4"),
        ("J1", "2"), ("J2", "2"), ("J3", "2"), ("J7", "2"),
        ("J6", "2"),
        ("Q1", "2"), ("D2", "1"), ("R5", "2"),
        ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2"), ("C5", "2"), ("C6", "2"),
        ("TP2", "1"), ("TP6", "1"),
        ("U4", "2"),            # DW01A CS senses across the FETs, on pack-
        ("U5", "3"),            # FS8205A S2 -> system ground
    ],
    "+3V3": [
        ("U1", "12"), ("U2", _R["VCC"]), ("U3", "8"),
        ("J1", "1"), ("J2", "1"), ("J3", "1"), ("J7", "1"),
        ("R1", "1"), ("R2", "1"), ("R3", "1"),
        ("C1", "1"), ("C2", "1"), ("C3", "1"), ("C4", "1"), ("C5", "1"),
        ("TP5", "1"),
    ],

    # --- battery / protection chain ---------------------------------------
    # VBAT is the system battery rail (cell positive, shared with the pack +).
    "VBAT":       [("J4", "1"), ("J5", "1"), ("D1", "1"), ("C6", "1"),
                   ("TP1", "1"), ("R6", "1")],
    # The cell's negative leg, upstream of the protection FETs.  Must be kept
    # clear of the ground pour - it is only ground once it is through U5.
    "BAT_NEG":    [("J4", "2"), ("U4", "6"), ("U5", "1"), ("C7", "2")],
    "DW_VDD":     [("R6", "2"), ("U4", "5"), ("C7", "1")],
    "DW_OD":      [("U4", "1"), ("U5", "2")],     # over-discharge -> G1
    "DW_OC":      [("U4", "3"), ("U5", "4")],     # over-charge    -> G2
    "FET_MID":    [("U5", "5"), ("U5", "6")],     # common drain, internally tied
    "VUSB":       [("U1", "14")],

    # I2C bus - MAX30102 0x57, MAX30208 0x50, AHT20 0x38, ATECC608A 0x60,
    # and on J7 the SSD1306 OLED at 0x3C.  Five distinct addresses, no clash.
    # A display costs no GPIO: it shares D4/D5 with everything else on the bus.
    "SDA":        [("U1", "5"), ("U3", "5"), ("J1", "4"), ("J2", "4"),
                   ("J3", "4"), ("J7", "4"), ("R1", "2"), ("TP3", "1")],
    "SCL":        [("U1", "6"), ("U3", "6"), ("J1", "3"), ("J2", "3"),
                   ("J3", "3"), ("J7", "3"), ("R2", "2"), ("TP4", "1")],
    "PPG_INT":    [("U1", "8"), ("J1", "5")],

    # SPI to the Ra-01SH.  The SX1262 has no DIO0; BUSY is mandatory and takes
    # the D1 pin that LORA_DIO0 used to occupy, so the GPIO count is unchanged.
    "SPI_SCK":    [("U1", "9"),  ("U2", _R["SCK"])],
    "SPI_MISO":   [("U1", "10"), ("U2", _R["MISO"])],
    "SPI_MOSI":   [("U1", "11"), ("U2", _R["MOSI"])],
    "LORA_NSS":   [("U1", "4"),  ("U2", _R["NSS"])],
    "LORA_RST":   [("U1", "3"),  ("U2", _R["NRESET"])],
    "LORA_BUSY":  [("U1", "2"),  ("U2", _R["BUSY"])],
    "LORA_DIO1":  [("U1", "1"),  ("U2", _R["DIO1"])],
    "ANT":        [("U2", _R["ANT"]), ("J6", "1")],

    # haptic drive
    "HAPTIC_PWM": [("U1", "7"), ("R4", "1")],
    "HAPTIC_G":   [("R4", "2"), ("R5", "1"), ("Q1", "1")],
    "MOTOR_N":    [("Q1", "3"), ("D1", "2"), ("J5", "2")],

    "LED_A":      [("R3", "2"), ("D2", "2")],
}

# SX1262 DIO2/DIO3 are unused here (the on-module RF switch and TCXO control
# are internal); name them so DRC does not flag them as floating.
NETS["LORA_DIO2"] = [("U2", _R["DIO2"])]
NETS["LORA_DIO3"] = [("U2", _R["DIO3"])]
# The SX126x RF-switch enables.  The Ra-01SH switches internally, so these are
# brought out and named but not driven - same treatment as the unused DIOs.
NETS["LORA_TXEN"] = [("U2", _R["TXEN"])]
NETS["LORA_RXEN"] = [("U2", _R["RXEN"])]
# KiCad auto-names the ATECC's NC pins; carry the same names on the board so
# schematic-to-board parity is clean without running "Update PCB from Schematic".
for _p in ("1", "2", "3", "7"):
    NETS["unconnected-(U3-NC-Pad%s)" % _p] = [("U3", _p)]
NETS["PPG_IRD"] = [("J1", "6")]
NETS["PPG_RD"] = [("J1", "7")]
# DW01A pin 4 (TD) is a factory test pin.  Use the same "unconnected-(...)"
# convention as the ATECC's NC pads: gen_sch.py skips those and drops a
# no-connect marker, which keeps ERC quiet instead of hanging a dangling label
# on a pin that is meant to float.
NETS["unconnected-(U4-TD-Pad4)"] = [("U4", "4")]

# ------------------------------------------------------------- design rules
NETCLASS = {
    # name: (track_mm, clearance_mm, via_dia_mm, via_drill_mm, nets)
    "Default": (0.25, 0.20, 0.60, 0.30, None),
    # BAT_NEG and FET_MID deliberately stay on Default (0.25 mm), NOT Power.
    # They terminate on SOT-23-6 pads whose inter-pad gap is ~0.35 mm, so a
    # 0.60 mm Power track physically cannot reach them - the router reported
    # FAILED: ['BAT_NEG->pad2'] when they were in Power.  0.25 mm on 1 oz copper
    # carries roughly 0.9 A, against a 175 mA charge current and ~200 mA peak
    # discharge, so the thinner track still has about 5x margin.
    "Power":   (0.60, 0.25, 0.80, 0.40, ["+3V3", "VBAT", "VUSB", "MOTOR_N"]),
    "RF":      (0.90, 0.35, 0.60, 0.30, ["ANT"]),
}
