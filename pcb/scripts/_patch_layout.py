"""Re-layout the left region for the corrected Ra-01SH pinout.

With the curated pinout, the module's left edge (top -> bottom) is
ANT(1) GND(2) VCC(3) NRESET(4) BUSY(5) DIO1(6) DIO2(7) DIO3(8) and the right
edge carries the SPI group, which faces the XIAO.  Two consequences:

  * J6 belongs top-left, feeding ANT on pad 1.
  * C1/C3 must sit beside VCC on pad 3 - they were placed for the old (wrong)
    map that had 3V3 on pad 13, leaving them ~15 mm from the real VCC pad.
    A 118 mA TX burst through 15 mm of track is exactly what bulk decoupling
    is supposed to prevent.

To free the left edge for the antenna and the decoupling, the battery
protection moves to the BACK, near J4.  J4/J5 are through-hole, so BAT_NEG
reaches the back layer without an extra via, and the back was almost empty.

Delete this file after running.
"""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def patch(fn, repl):
    p = os.path.join(HERE, fn)
    s = io.open(p, encoding="utf-8").read()
    miss = [i for i, (a, _) in enumerate(repl) if a not in s]
    if miss:
        sys.stderr.write("PATCH FAILED %s anchors %s\n" % (fn, miss))
        for i in miss:
            sys.stderr.write("--- %d ---\n%r\n" % (i, repl[i][0]))
        raise SystemExit(1)
    for a, b in repl:
        s = s.replace(a, b, 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("patched", fn)


patch("design.py", [
    # --- radio drops 1.5 mm to open a channel above it for J6 ---------------
    ('''    "U2":  ("PRAHARI:Ai-Thinker_Ra-01SH", "Ra-01SH SX1262",
            20.0, 13.5, 0, "F", "LoRa SX1262 868/915 MHz, band-to-band mesh, 4.2 mA RX"),''',
     '''    # y 13.5 -> 15.0: the land pattern is 17 mm tall in this orientation, so its
    # courtyard reached y = 4.4 and left no room for J6 above it.
    "U2":  ("PRAHARI:Ai-Thinker_Ra-01SH", "Ra-01SH SX1262",
            20.0, 15.0, 0, "F", "LoRa SX1262 868/915 MHz, band-to-band mesh, 4.2 mA RX"),'''),
    # --- J6 straight above ANT (pad 1 at board-relative (12, 8.0)) ----------
    ('''    "J6":  ("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "ANT WHIP",
            14.0, 2.5, 0, "F", "868 MHz whip (86 mm) / counterpoise solder pads"),''',
     '''    "J6":  ("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "ANT WHIP",
            12.0, 3.0, 0, "F", "868 MHz whip (86 mm) / counterpoise solder pads"),'''),
    # --- decoupling beside VCC on pad 3, board-relative (12, 12) ------------
    ('''    "C1":  ("Capacitor_SMD:C_1206_3216Metric", "100uF", 31.0, 2.0, 0, "F", "LoRa TX bulk (118 mA at +22 dBm)"),''',
     '''    # C1/C3 moved from (31, 2)/(25, 2) to the module's left edge.  VCC is pad 3
    # at board-relative (12, 12) in the curated pinout; the old spots were
    # chosen for the wrong map and sat ~15 mm away.  C3 is the closer of the two
    # because a 100 nF has to be nearest the pin; C1 is bulk and tolerates more.
    "C1":  ("Capacitor_SMD:C_1206_3216Metric", "100uF", 8.0, 8.0, 90, "F", "LoRa TX bulk (118 mA at +22 dBm)"),'''),
    ('''    "C3":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 25.0, 2.0, 0, "F", "Ra-01SH decoupling"),''',
     '''    "C3":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 8.0, 12.0, 90, "F", "Ra-01SH decoupling"),'''),
    # --- protection cluster moves to the back, beside J4 --------------------
    ('''    # --- battery protection (new in rev B) --------------------------------
    # Sits in the free left-edge pocket, above J4 so the cell-negative leg is
    # short.  Clear of the Ra-01SH courtyard, which starts at x = 12.
    #
    # THESE FOUR POSITIONS AND ROTATIONS ARE LOAD-BEARING.  U4 pin 2 (CS) is the
    # middle pad of a SOT-23-6 and its neighbours (pin 1 OD, pin 3 OC) both carry
    # tracks off the part, so the GND pour can only reach CS head-on.  Nudging U4
    # left, or rotating it, closes that wedge and DRC comes back with
    #     Missing connection: Zone [GND] on F.Cu <-> Pad 2 [GND] of U4
    # Crowding the pocket further also breaks the F.Cu-to-B.Cu pour tie.  This
    # combination was found by sweeping placements against DRC; if you move any
    # of the four, re-run gen_pcb.py and check "unconnected" is still 0.
    "U4":  ("Package_TO_SOT_SMD:SOT-23-6", "DW01A", 6.5, 12.0, 0, "F",
            "Li-ion protection: 4.3 V over-charge, 2.4 V over-discharge, over-current"),
    "U5":  ("Package_TO_SOT_SMD:SOT-23-6", "FS8205A", 5.5, 19.0, 90, "F",
            "Dual common-drain N-MOSFET - the protection switch pair"),
    "R6":  ("Resistor_SMD:R_0805_2012Metric", "100R", 9.0, 15.5, 90, "F", "DW01A VDD series"),
    "C7":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 9.5, 15.5, 0, "F", "DW01A VDD decoupling"),''',
     '''    # --- battery protection (new in rev B) --------------------------------
    # On the BACK, beside J4.  It started on the front-left, but the corrected
    # radio pinout needs that pocket for the antenna feed and the VCC
    # decoupling.  The back was nearly empty (only R1/R2), and J4/J5 are
    # through-hole, so BAT_NEG reaches this side without an extra via.
    #
    # U4's ORIENTATION IS LOAD-BEARING.  Pin 2 (CS) is the middle pad of a
    # SOT-23-6 and its neighbours (pin 1 OD, pin 3 OC) both carry tracks off the
    # part, so the ground pour can only reach CS head-on.  If you move or rotate
    # U4, re-run gen_pcb.py and confirm DRC "unconnected" is still 0 - the
    # failure mode is
    #     Missing connection: Zone [GND] <-> Pad 2 [GND] of U4
    "U4":  ("Package_TO_SOT_SMD:SOT-23-6", "DW01A", 18.0, 31.0, 0, "B",
            "Li-ion protection: 4.3 V over-charge, 2.4 V over-discharge, over-current"),
    "U5":  ("Package_TO_SOT_SMD:SOT-23-6", "FS8205A", 18.0, 36.0, 0, "B",
            "Dual common-drain N-MOSFET - the protection switch pair"),
    "R6":  ("Resistor_SMD:R_0805_2012Metric", "100R", 23.0, 31.0, 0, "B", "DW01A VDD series"),
    "C7":  ("Capacitor_SMD:C_0805_2012Metric", "100nF", 23.0, 34.0, 0, "B", "DW01A VDD decoupling"),'''),
])

patch("gen_pcb.py", [
    ('silk("ANT", 10.2, 2.5, 0.8)\nsilk("GND", 20.6, 2.5, 0.8)',
     'silk("ANT", 8.6, 3.0, 0.8)\nsilk("GND", 17.8, 3.0, 0.8)'),
])

patch("check_design.py", [
    ('''EXPECT = {"U4": (6.5, 12.0, 0), "U5": (5.5, 19.0, 90),
          "R6": (9.0, 15.5, 90), "C7": (2.0, 15.5, 90)}''',
     '''EXPECT = {"U4": (18.0, 31.0, 0), "U5": (18.0, 36.0, 0),
          "R6": (23.0, 31.0, 0), "C7": (23.0, 34.0, 0)}'''),
])
