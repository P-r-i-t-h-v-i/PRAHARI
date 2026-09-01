"""PRAHARI countdown band - carrier board, single source of truth.

Board: 70 x 40 mm, 2-layer.  Every active part is an off-the-shelf module, per the
SIH deck ("four modules, nothing custom - all stocked on Robu.in today").

GPIO budget on the XIAO nRF52840 Sense is exactly 11 pins, and all 11 are used:

    D0  LORA_DIO1      D4  SDA          D8  SPI_SCK
    D1  LORA_DIO0      D5  SCL          D9  SPI_MISO
    D2  LORA_RST       D6  HAPTIC_PWM   D10 SPI_MOSI
    D3  LORA_NSS       D7  PPG_INT

Battery voltage needs no external divider: the XIAO reads VBAT internally on
P0.31, gated by P0.14 - neither pin is brought out to the 2x7 header.
"""

BOARD_W, BOARD_H = 70.0, 40.0
CORNER_R = 2.0
ORIGIN = (30.0, 40.0)          # board top-left on the drawing sheet

# ---------------------------------------------------------------- components
# ref: (footprint, value, x, y, rotation_deg, side, description)
#      x/y are board-relative mm, measured to the footprint origin.
COMPONENTS = {
    # --- modules -----------------------------------------------------------
    "U1":  ("PRAHARI:XIAO_nRF52840_Sense", "XIAO nRF52840 Sense",
            54.0, 12.5, 0, "F", "MCU: Cortex-M4F, BLE, on-board IMU + mic + LiPo charger"),
    "U2":  ("PRAHARI:Ai-Thinker_Ra-02", "Ra-02 SX1278",
            20.0, 13.5, 0, "F", "LoRa 433 MHz transceiver, band-to-band mesh"),
    "U3":  ("Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "ATECC608A-SSHDA",
            61.0, 29.0, 0, "F", "Secure element: key storage for the anonymised uplink"),

    # --- sensor breakouts (I2C), rot 90 so the pin rows run left-to-right ---
    "J1":  ("Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical", "MAX30100",
            5.0, 28.0, 90, "F", "Red/IR PPG - heart rate, IMU-gated"),
    "J2":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "MLX90614",
            24.5, 28.0, 90, "F", "IR thermopile - wrist skin temperature"),
    "J3":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "AHT20",
            36.0, 28.0, 90, "F", "Air temperature + RH - the WBGT inputs"),
    "J7":  ("Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "I2C EXP",
            47.5, 28.0, 90, "F", "Spare I2C: 3V3 / GND / SCL / SDA"),

    # --- power, actuator, antenna -----------------------------------------
    "J4":  ("Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "LiPo 3.7V",
            10.0, 33.0, 0, "F", "Battery in - feed to XIAO BAT pads via TP1/TP2"),
    "J5":  ("Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "HAPTIC",
            30.0, 33.0, 0, "F", "Vibration motor - hazard and strain patterns"),
    # 433 MHz antenna: two solder pads directly above the module's ANT pad.
    # A quarter-wave whip is 173 mm of wire; pin 2 is the counterpoise.  This
    # keeps the RF trace to 3.5 mm - an edge-launch SMA would need its pads on
    # the board outline, and a vertical SMA would push the trace past 10 mm.
    # For a proper antenna, use the Ra-02's own IPEX connector and leave J6 open.
    "J6":  ("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "ANT WHIP",
            15.0, 2.0, 90, "F", "433 MHz whip / counterpoise solder pads"),

    "Q1":  ("Package_TO_SOT_SMD:SOT-23", "2N7002", 37.0, 36.0, 0, "F", "Haptic low-side switch"),
    "D1":  ("Diode_SMD:D_SOD-123", "1N4148W", 42.0, 36.0, 0, "F", "Motor flyback clamp"),
    "D2":  ("LED_SMD:LED_0805_2012Metric", "GRN", 48.0, 36.0, 0, "F", "3V3 power LED"),

    # --- passives ----------------------------------------------------------
    "R1":  ("Resistor_SMD:R_0805_2012Metric", "4k7", 35.0, 12.0, 0, "B", "SDA pull-up"),
    "R2":  ("Resistor_SMD:R_0805_2012Metric", "4k7", 39.0, 12.0, 0, "B", "SCL pull-up"),
    "R3":  ("Resistor_SMD:R_0805_2012Metric", "1k",  52.0, 36.0, 0, "F", "LED series"),
    "R4":  ("Resistor_SMD:R_0805_2012Metric", "100R", 37.0, 33.0, 0, "F", "Gate series"),
    "R5":  ("Resistor_SMD:R_0805_2012Metric", "100k", 41.0, 33.0, 0, "F", "Gate pull-down"),

    "C1":  ("Capacitor_SMD:C_1206_3216Metric", "100uF", 31.0, 2.0, 0, "F", "LoRa TX bulk (120 mA burst)"),
    "C2":  ("Capacitor_SMD:C_0805_2012Metric", "10uF", 42.0, 12.0, 0, "F", "3V3 bulk at the XIAO"),
    "C3":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 25.0, 2.0, 0, "F", "Ra-02 decoupling"),
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

# ---------------------------------------------------------------------- nets
# net name -> [(ref, pad), ...]
NETS = {
    "GND": [
        ("U1", "13"),
        ("U2", "1"), ("U2", "12"), ("U2", "16"),
        ("U3", "4"),
        ("J1", "2"), ("J2", "2"), ("J3", "2"), ("J7", "2"),
        ("J4", "2"), ("J6", "2"),
        ("Q1", "2"), ("D2", "1"), ("R5", "2"),
        ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2"), ("C5", "2"), ("C6", "2"),
        ("TP2", "1"), ("TP6", "1"),
    ],
    "+3V3": [
        ("U1", "12"), ("U2", "13"), ("U3", "8"),
        ("J1", "1"), ("J2", "1"), ("J3", "1"), ("J7", "1"),
        ("R1", "1"), ("R2", "1"), ("R3", "1"),
        ("C1", "1"), ("C2", "1"), ("C3", "1"), ("C4", "1"), ("C5", "1"),
        ("TP5", "1"),
    ],
    "VBAT":       [("J4", "1"), ("J5", "1"), ("D1", "1"), ("C6", "1"), ("TP1", "1")],
    "VUSB":       [("U1", "14")],

    # I2C bus - MAX30100, MLX90614, AHT20, ATECC608A, expansion header
    "SDA":        [("U1", "5"), ("U3", "5"), ("J1", "4"), ("J2", "4"),
                   ("J3", "4"), ("J7", "4"), ("R1", "2"), ("TP3", "1")],
    "SCL":        [("U1", "6"), ("U3", "6"), ("J1", "3"), ("J2", "3"),
                   ("J3", "3"), ("J7", "3"), ("R2", "2"), ("TP4", "1")],
    "PPG_INT":    [("U1", "8"), ("J1", "5")],

    # SPI to the Ra-02
    "SPI_SCK":    [("U1", "9"),  ("U2", "11")],
    "SPI_MISO":   [("U1", "10"), ("U2", "9")],
    "SPI_MOSI":   [("U1", "11"), ("U2", "10")],
    "LORA_NSS":   [("U1", "4"),  ("U2", "8")],
    "LORA_RST":   [("U1", "3"),  ("U2", "14")],
    "LORA_DIO0":  [("U1", "2"),  ("U2", "7")],
    "LORA_DIO1":  [("U1", "1"),  ("U2", "6")],
    "ANT":        [("U2", "15"), ("J6", "1")],

    # haptic drive
    "HAPTIC_PWM": [("U1", "7"), ("R4", "1")],
    "HAPTIC_G":   [("R4", "2"), ("R5", "1"), ("Q1", "1")],
    "MOTOR_N":    [("Q1", "3"), ("D1", "2"), ("J5", "2")],

    "LED_A":      [("R3", "2"), ("D2", "2")],
}

# Ra-02 DIO2..DIO5 are unused; name them so DRC does not flag them as floating.
for i, pad in zip(range(2, 6), ["5", "4", "3", "2"]):
    NETS[f"LORA_DIO{i}"] = [("U2", pad)]
# KiCad auto-names the ATECC's NC pins; carry the same names on the board so
# schematic-to-board parity is clean without running "Update PCB from Schematic".
for _p in ("1", "2", "3", "7"):
    NETS[f"unconnected-(U3-NC-Pad{_p})"] = [("U3", _p)]
NETS["PPG_IRD"] = [("J1", "6")]
NETS["PPG_RD"] = [("J1", "7")]

# ------------------------------------------------------------- design rules
NETCLASS = {
    # name: (track_mm, clearance_mm, via_dia_mm, via_drill_mm, nets)
    "Default": (0.25, 0.20, 0.60, 0.30, None),
    "Power":   (0.60, 0.25, 0.80, 0.40, ["+3V3", "VBAT", "VUSB", "MOTOR_N"]),
    "RF":      (0.90, 0.35, 0.60, 0.30, ["ANT"]),
}
