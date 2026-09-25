#!/usr/bin/env python3
"""Build the PRAHARI project PDF: the idea, plus real PCB renders from pcb/out/."""

import csv
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

OUT = "/home/per/Downloads/PRAHARI_Project_Report.pdf"
PCB = "/home/per/PRAHARI/pcb/out"
DEJAVU = "/usr/share/fonts/truetype/dejavu"

pdfmetrics.registerFont(TTFont("DV", f"{DEJAVU}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", f"{DEJAVU}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", f"{DEJAVU}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-M", f"{DEJAVU}/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I")

NAVY = colors.HexColor("#1a3a6b")
ORANGE = colors.HexColor("#d9541e")
TEAL = colors.HexColor("#0f766e")
GREY = colors.HexColor("#555555")
LIGHT = colors.HexColor("#f2f5f9")
RULE = colors.HexColor("#c9d4e4")

ss = getSampleStyleSheet()


def S(name, **kw):
    base = dict(fontName="DV", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1a1a1a"))
    base.update(kw)
    return ParagraphStyle(name, parent=ss["Normal"], **base)


st_title = S("t", fontName="DV-B", fontSize=26, leading=30, textColor=NAVY, alignment=TA_CENTER)
st_sub = S("s", fontName="DV-I", fontSize=11.5, leading=16, textColor=ORANGE, alignment=TA_CENTER)
st_h1 = S("h1", fontName="DV-B", fontSize=15, leading=19, textColor=NAVY, spaceBefore=4, spaceAfter=7)
st_h2 = S("h2", fontName="DV-B", fontSize=11, leading=15, textColor=TEAL, spaceBefore=8, spaceAfter=4)
st_body = S("b", alignment=TA_JUSTIFY, spaceAfter=5)
st_bullet = S("bu", leftIndent=11, bulletIndent=2, spaceAfter=3.5)
st_cap = S("cap", fontSize=8.2, leading=11, textColor=GREY, alignment=TA_CENTER, spaceBefore=4)
st_small = S("sm", fontSize=8.2, leading=11.5, textColor=GREY)
st_cell = S("c", fontSize=7.8, leading=10)
st_cellb = S("cb", fontName="DV-B", fontSize=7.8, leading=10, textColor=colors.white)

ID_LINE = "Point Break"


def bullets(items, style=st_bullet):
    return [Paragraph(t, style, bulletText="▪") for t in items]


def rule(color=RULE, w=0.9, space=5):
    t = Table([[""]], colWidths=[168 * mm], rowHeights=[0.1])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), w, color),
                           ("TOPPADDING", (0, 0), (-1, -1), space),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), space)]))
    return t


def fit_image(path, max_w, max_h):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    scale = min(max_w / iw, max_h / ih)
    return Image(path, iw * scale, ih * scale)


LAND = landscape(A4)


def _chrome(canvas, doc, pw, ph):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, ph - 15 * mm, pw, 15 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("DV-B", 10)
    canvas.drawString(20 * mm, ph - 10 * mm, "PRAHARI — The Countdown Band")
    canvas.setFont("DV", 8)
    canvas.drawRightString(pw - 20 * mm, ph - 10 * mm, ID_LINE)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.7)
    canvas.line(20 * mm, 14 * mm, pw - 20 * mm, 14 * mm)
    canvas.setFillColor(GREY)
    canvas.setFont("DV", 7.8)
    canvas.drawString(20 * mm, 10 * mm, "Wearable multi-hazard early-warning band")
    canvas.drawRightString(pw - 20 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def header_footer(canvas, doc):
    _chrome(canvas, doc, A4[0], A4[1])


def header_footer_land(canvas, doc):
    _chrome(canvas, doc, LAND[0], LAND[1])


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                      topMargin=22 * mm, bottomMargin=18 * mm,
                      title="PRAHARI — The Countdown Band",
                      author="Point Break — SIH 2026")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")

LM, RM, TM, BM = 15 * mm, 15 * mm, 20 * mm, 16 * mm
land_frame = Frame(LM, BM, LAND[0] - LM - RM, LAND[1] - TM - BM, id="land")

doc.addPageTemplates([
    PageTemplate(id="all", frames=[frame], onPage=header_footer, pagesize=A4),
    PageTemplate(id="land", frames=[land_frame], onPage=header_footer_land, pagesize=LAND),
])
LAND_W = LAND[0] - LM - RM
LAND_H = LAND[1] - TM - BM

E = []
W = doc.width

# ---------------------------------------------------------------- page 1
E.append(Spacer(1, 6 * mm))
E.append(Paragraph("PRAHARI", st_title))
E.append(Paragraph("The Countdown Band", S("t2", fontName="DV-B", fontSize=15, leading=19,
                                           textColor=ORANGE, alignment=TA_CENTER)))
E.append(Spacer(1, 3 * mm))
E.append(Paragraph("Warns before the emergency — the flood, cyclone or heatwave coming at you, and "
                   "the heat strain building inside you — and reaches workers no tower reaches.", st_sub))
E.append(Spacer(1, 5 * mm))

meta = Table([
    [Paragraph("<b>Team Name</b>", st_cell), Paragraph("Point Break", st_cell),
     Paragraph("<b>Theme</b>", st_cell), Paragraph("MedTech / BioTech / HealthTech", st_cell)],
], colWidths=[W * 0.18, W * 0.24, W * 0.14, W * 0.44])
meta.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
]))
E.append(meta)
E.append(Spacer(1, 6 * mm))

E.append(Paragraph("The Idea", st_h1))
E.append(Paragraph(
    "PRAHARI is a wrist band that gives a person two warnings nobody gives them today: the "
    "<b>disaster coming at them from outside</b>, and the <b>heat strain building inside their own body</b> — "
    "and it delivers both <b>without needing a phone, a tower, or the internet</b>.", st_body))
E.append(Paragraph(
    "Official hazard alerts (flood, cyclone, heatwave, lightning) are pulled from the NDMA SACHET CAP "
    "public feed by any one phone that still has signal, then <b>hop band-to-band over LoRa radio</b> — so "
    "the warning reaches workers standing kilometres past the last working tower. At the same time the "
    "band watches the wearer's own body: heart rate, skin temperature and the surrounding air, fused "
    "on-chip into an estimate of core temperature, and it counts down <b>the minutes left before that "
    "person crosses their heat-collapse threshold</b>. No literacy and no smartphone are required — the "
    "output is a vibration on the wrist and a falling number.", st_body))
E.append(Spacer(1, 2 * mm))

E.append(Paragraph("The problem we are answering", st_h2))
E.extend(bullets([
    "<b>The warning never arrives.</b> Only 1 in 3 flood-exposed Indians has any early warning at all.",
    "<b>The network dies first.</b> Kerala 2018 — the towers ran out of diesel exactly when the alert mattered.",
    "<b>The body warns too late.</b> Collapse is usually the first symptom anyone actually notices.",
    "<b>Nobody is watching at night.</b> Warm nights rise faster than hot days, and the body never gets to cool down.",
]))

E.append(Paragraph("What makes it different", st_h2))
E.extend(bullets([
    "<b>Warns before, not after</b> — the hazard outside and the strain inside, both ahead of the event.",
    "<b>Works when the tower doesn't</b> — the alert hops band to band over LoRa, roughly 2 km per hop.",
    "<b>Official alerts, not guesses</b> — sourced from the NDMA SACHET CAP feed, not from a model's opinion.",
    "<b>₹3,468 of parts</b> — against ₹28,000 for the nearest commercial core-temperature sensor.",
    "<b>One band protects a whole gang</b> — a collapse detected on one wrist alerts the colleagues around it.",
]))

E.append(Spacer(1, 3 * mm))
E.append(rule())
E.append(Paragraph(
    "This report documents the idea and the <b>hardware actually built for it</b>: a custom 2-layer PCB "
    "(rev B, 70 × 40 mm), its schematic, bill of materials and current bring-up status.", st_small))

E.append(PageBreak())

# ---------------------------------------------------------------- page 2
E.append(Paragraph("How It Works", st_h1))
E.append(Paragraph("Three stages, all of them on the wrist. Nothing has to be transmitted for a "
                   "decision to be made.", st_body))
E.append(Spacer(1, 3 * mm))

stage_data = [[
    Paragraph("<b>1 · SENSE ON THE BODY</b>", st_cellb),
    Paragraph("<b>2 · DECIDE ON THE CHIP</b>", st_cellb),
    Paragraph("<b>3 · WARN WITHOUT A NETWORK</b>", st_cellb),
], [
    Paragraph("<b>XIAO nRF52840 Sense</b> — Cortex-M4F, IMU and mic already on board<br/><br/>"
              "<b>MAX30102 red/IR PPG</b> — heart rate, gated on the IMU when motion is high<br/><br/>"
              "<b>MAX30208</b> — contact skin temperature, ±0.1 °C clinical grade<br/><br/>"
              "<b>AHT20</b> — air temperature and humidity, the WBGT inputs", st_cell),
    Paragraph("<b>TensorFlow Lite Micro</b> — ~1 ms inference, ~18 ms with feature extraction<br/><br/>"
              "<b>ECTemp Kalman + WBGT + Strain Index</b> — fused every second<br/><br/>"
              "<b>Welford + CUSUM</b> — learns this specific wearer, on-device<br/><br/>"
              "<b>Forecast to threshold</b> — gated on a signal-quality index", st_cell),
    Paragraph("<b>Haptic warning</b> — one vibration pattern for hazard, another for your own strain<br/><br/>"
              "<b>Ra-01SH (SX1262) LoRa</b> — band to band, no tower needed<br/><br/>"
              "<b>NDMA SACHET CAP relay</b> — flood, cyclone and lightning warnings flood the mesh<br/><br/>"
              "<b>AES + ATECC608A</b> — only anonymised counts ever leave the band", st_cell),
]]
stage = Table(stage_data, colWidths=[W / 3.0] * 3)
stage.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, 0), NAVY), ("BACKGROUND", (1, 0), (1, 0), TEAL),
    ("BACKGROUND", (2, 0), (2, 0), ORANGE),
    ("BACKGROUND", (0, 1), (-1, 1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
]))
E.append(stage)
E.append(Spacer(1, 6 * mm))

E.append(Paragraph("The alert path", st_h2))
chain = Table([[
    Paragraph("<b>IMD · CWC · NDMA</b><br/><font size=7>issue the alert</font>", st_cell),
    Paragraph("→", S("a", fontSize=13, alignment=TA_CENTER, textColor=ORANGE)),
    Paragraph("<b>SACHET CAP</b><br/><font size=7>any phone with signal</font>", st_cell),
    Paragraph("→", S("a", fontSize=13, alignment=TA_CENTER, textColor=ORANGE)),
    Paragraph("<b>LoRa hop</b><br/><font size=7>band to band, ~2 km</font>", st_cell),
    Paragraph("→", S("a", fontSize=13, alignment=TA_CENTER, textColor=ORANGE)),
    Paragraph("<b>Your wrist</b><br/><font size=7>buzzes — no phone</font>", st_cell),
]], colWidths=[W * 0.20, W * 0.05, W * 0.20, W * 0.05, W * 0.20, W * 0.05, W * 0.25])
chain.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fdf1ec")),
    ("BOX", (0, 0), (-1, -1), 0.8, ORANGE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
E.append(chain)
E.append(Paragraph("Hazards covered: Flood · Cyclone · Heatwave · Tsunami · Lightning · Forest fire · Avalanche",
                   st_cap))
E.append(Spacer(1, 5 * mm))

E.append(Paragraph("Cost against the commercial alternative", st_h2))
cmp_rows = [["Parameter", "Commercial (greenTEG CORE 2)", "PRAHARI"],
            ["Device cost", "₹28,000+", "₹3,468"],
            ["Works with no network", "No", "Yes"],
            ["Warns before impact", "No", "Yes"],
            ["Output", "Lagging °C", "Minutes left"],
            ["Mesh rescue alert", "None", "~2 km"],
            ["Disaster alerts", "None", "All CAP hazards"]]
cmp_t = Table([[Paragraph(f"<b>{c}</b>" if i == 0 else c, st_cellb if i == 0 else st_cell)
                for c in row] for i, row in enumerate(cmp_rows)],
              colWidths=[W * 0.32, W * 0.36, W * 0.32])
cmp_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
    ("TEXTCOLOR", (2, 1), (2, -1), TEAL),
    ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
]))
E.append(cmp_t)
E.append(Paragraph("Parts costing: XIAO nRF52840 Sense ₹2,299 + MLX90614 ₹699 + SX1278 Ra-02 ₹329 + "
                   "MAX30100 ₹85 + AHT20 ₹56 — Robu.in, Aug 2026.", st_cap))

E.append(PageBreak())

# ---------------------------------------------------------------- page 3 — PCB
E.append(Paragraph("The Board We Built", st_h1))
E.append(Paragraph(
    "A custom 2-layer PCB, <b>70 × 40 mm</b>, carrying the XIAO nRF52840 Sense as a module, the Ra-01SH "
    "LoRa radio, the ATECC608A secure element, a complete single-cell LiPo protection stage (DW01A + "
    "FS8205A), a haptic driver, and headers that break out every sensor onto one shared I²C bus.", st_body))
E.append(Spacer(1, 3 * mm))

E.append(fit_image(f"{PCB}/top.png", W, 92 * mm))
E.append(Paragraph("<b>Figure 1 — PCB rev B, top side (3-D render).</b> U1 XIAO nRF52840 Sense · "
                   "U2 Ra-01SH SX1262 LoRa · U3 ATECC608A secure element · J1 MAX30102 PPG · "
                   "J2 MAX30208 skin temp · J3 AHT20 · J7 SSD1306 OLED · J4 LiPo · J5 haptic motor · "
                   "J6 antenna whip.", st_cap))

E.append(NextPageTemplate("land"))
E.append(PageBreak())

# ---------------------------------------------------------------- page 4 — schematic (landscape)
E.append(Paragraph("Schematic — PRAHARI rev B", st_h1))
E.append(Paragraph("Power and protection, the MCU module, the LoRa radio front end, the shared I²C "
                   "sensor bus, the secure element and the haptic driver. Rendered from the KiCad "
                   "project at full resolution — zoom in to read component values.", st_body))
E.append(Spacer(1, 2 * mm))
for _c in ("schematic_clean_hires.png", "schematic_revB_hires.png", "schematic_hires.png", "schematic_full.png"):
    sch = f"{PCB}/{_c}"
    if os.path.exists(sch):
        break
E.append(fit_image(sch, LAND_W, LAND_H - 34 * mm))
E.append(Paragraph("<b>Figure 3 — Complete schematic sheet, PRAHARI rev B.</b>", st_cap))

E.append(NextPageTemplate("all"))
E.append(PageBreak())

# ---------------------------------------------------------------- page 5 — BOM
E.append(Paragraph("Bill of Materials", st_h1))
E.append(Paragraph("Every part on the rev B board, as exported from the KiCad project.", st_body))
E.append(Spacer(1, 2 * mm))

with open(f"{PCB}/BOM.csv") as fh:
    rows = list(csv.reader(fh))
data = rows[1:]

bom_rows = [[Paragraph(f"<b>{h}</b>", st_cellb) for h in ["Ref", "Value", "Description", "Qty"]]]
for r in data:
    bom_rows.append([Paragraph(r[0], st_cell), Paragraph(r[1], st_cell),
                     Paragraph(r[3], st_cell), Paragraph(r[4], st_cell)])
bom = Table(bom_rows, colWidths=[W * 0.11, W * 0.22, W * 0.60, W * 0.07], repeatRows=1)
bom.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (3, 0), (3, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
]))
E.append(bom)
E.append(Spacer(1, 5 * mm))

E.append(Paragraph("Pin map — everything on one XIAO", st_h2))
pin_rows = [["XIAO pin", "Goes to", "Bus / role"],
            ["3V3", "All module VCC / VIN", "Shared 3.3 V rail (not 5 V tolerant)"],
            ["GND", "All module GND", "Common star ground — keeps PPG noise down"],
            ["D0", "MAX30102 INT", "Optional interrupt"],
            ["D1", "LoRa DIO0", "TX/RX done interrupt"],
            ["D2", "LoRa RESET", "Radio reset"],
            ["D3", "LoRa NSS (CS)", "SPI chip select"],
            ["D4", "SDA — MAX30102, MAX30208, AHT20, OLED", "Shared I²C data"],
            ["D5", "SCL — MAX30102, MAX30208, AHT20, OLED", "Shared I²C clock"],
            ["D8 / D9 / D10", "LoRa SCK / MISO / MOSI", "SPI to the radio"]]
pin_t = Table([[Paragraph(f"<b>{c}</b>", st_cellb) if i == 0 else Paragraph(c, st_cell)
                for c in row] for i, row in enumerate(pin_rows)],
              colWidths=[W * 0.17, W * 0.45, W * 0.38])
pin_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.4, RULE),
    ("FONTNAME", (0, 1), (0, -1), "DV-M"),
    ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
E.append(pin_t)

E.append(PageBreak())

# ---------------------------------------------------------------- page 6 — status
E.append(Paragraph("Build Status & Verification", st_h1))
E.append(Paragraph("What is already proven on real hardware, and what is still open.", st_body))
E.append(Spacer(1, 2 * mm))

E.append(Paragraph("Verified working on hardware", st_h2))
E.extend(bullets([
    "<b>Heart rate sensing</b> — live finger test: IR rose from ~400 (no finger) to ~96,000, average "
    "BPM stabilised at 78.",
    "<b>SSD1306 OLED countdown display</b> — flashed and verified; combined sketch shows live BPM on the OLED.",
    "<b>I²C bus and device discovery</b> — scanner and raw register probe both bring up the bus cleanly.",
    "<b>Sensor identification</b> — the breakout sold as \"MAX30100\" actually reports PART_ID 0x15 "
    "(MAX30102/MAX30105), a common mislabelling; firmware was switched to the SparkFun MAX3010x library "
    "and confirmed working.",
    "<b>PCB rev B integrity</b> — all 38 footprints verified pad-for-pad against schematic, netlist and "
    "the KiCad 10 libraries; ERC clean.",
]))

E.append(Spacer(1, 3 * mm))
E.append(Paragraph("Impact, in the numbers that justify it", st_h2))
imp = Table([[
    Paragraph("<b><font size=15 color='#d9541e'>30.4 cr</font></b><br/><font size=7.5>informal workers "
              "on e-Shram<br/>Ministry of Labour, Dec 2024</font>", st_cell),
    Paragraph("<b><font size=15 color='#d9541e'>1 in 3</font></b><br/><font size=7.5>flood-exposed Indians "
              "have<br/>any early warning — CEEW</font>", st_cell),
    Paragraph("<b><font size=15 color='#0f766e'>0%</font></b><br/><font size=7.5>heat-stroke mortality when "
              "cooling<br/>starts in time — Medicina 2020</font>", st_cell),
    Paragraph("<b><font size=15 color='#1a3a6b'>₹6.5 lakh cr</font></b><br/><font size=7.5>lost in wages to "
              "heat yearly<br/>1.99% of GDP — IIED</font>", st_cell),
]], colWidths=[W / 4.0] * 4)
imp.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
    ("BOX", (0, 0), (-1, -1), 0.8, RULE), ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
E.append(imp)

E.append(Spacer(1, 4 * mm))
E.append(Paragraph(
    "Repository: <font face='DV-M' size=8>github.com/P-r-i-t-h-v-i/PRAHARI</font> — firmware, KiCad "
    "project, gerbers and BOM. Generated 2026-09-03 from the rev B project files.", st_small))

E.append(PageBreak())

# ---------------------------------------------------------------- page 7 — prototype evolution
E.append(Paragraph("From Prototype to Integrated Board", st_h1))
E.append(Paragraph(
    "The original PRAHARI prototype was a breadboard-level assembly built around a XIAO nRF52840 Sense "
    "microcontroller, wired individually to a MAX30102 photoplethysmography sensor, an AHT20 air "
    "temperature and humidity sensor, and an SX1278 LoRa radio module. Each component was validated in "
    "isolation through dedicated firmware test sketches before any attempt was made to combine them.", st_body))
E.append(Paragraph(
    "Building on that foundation, we have now designed and fabricated a custom two-layer printed circuit "
    "board, revision B, measuring 70 × 40 mm, that integrates every sensor, the LoRa radio, an ATECC608A "
    "secure element for on-device encryption, a complete single-cell lithium-polymer protection and "
    "charging stage, and a haptic feedback driver onto one shared bus. This replaces the loose wiring of "
    "the breadboard prototype with a single compact, wearable-grade board.", st_body))

E.append(Paragraph("Why This Update Is an Improvement", st_h2))
E.append(Paragraph(
    "This update moves PRAHARI from a proof-of-concept sensor stack to an integrated, security-hardened "
    "wearable device. Consolidating every component onto a single board removes the loose connections and "
    "electrical noise that commonly affect breadboard prototypes and interfere with the accuracy of the "
    "heart-rate signal. The addition of the ATECC608A secure element ensures that only encrypted, "
    "anonymised data leaves the band over the LoRa mesh, a safeguard the original prototype did not "
    "include.", st_body))
E.append(Paragraph(
    "The design also remains substantially more affordable than the nearest commercial alternative. The "
    "complete PRAHARI bill of materials costs approximately ₹3,468, compared with roughly ₹28,000 for a "
    "comparable commercial core-temperature monitor such as the greenTEG CORE 2. It also provides hazard "
    "warnings and mesh connectivity that no commercial device in that price range currently offers.", st_body))

E.append(Paragraph("Testing Insight and Next Steps", st_h2))
E.append(Paragraph(
    "During hardware bring-up, the most significant and unexpected finding was that the heart-rate sensor "
    "breakout, sold and labelled as a MAX30100, actually reported a part identifier corresponding to the "
    "MAX30102/MAX30105 family. This mislabelling would have gone unnoticed without direct register-level "
    "probing of the sensor. The firmware was accordingly switched to the correct sensor library and "
    "verified end to end: the infrared reading rose from approximately 400 with no finger present to "
    "approximately 96,000 with a finger placed on the sensor, and the average heart rate stabilised at 78 "
    "beats per minute.", st_body))
E.append(Paragraph(
    "The immediate next steps are to resolve the remaining physical layout issues found during design "
    "rule checking, in particular a courtyard collision near the LoRa antenna connector and a "
    "radio-frequency clearance requirement, complete assembly of the revision B board, and carry out field "
    "testing of the LoRa mesh relay and the heat-strain forecasting algorithm on real users. Completing "
    "these steps is what will take PRAHARI from a verified hardware prototype to a device ready for real "
    "users.", st_body))

doc.build(E)
print(f"Written: {OUT}")
