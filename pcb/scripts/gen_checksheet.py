"""Write out/Ra-01SH-checksheet.svg - a 1:1 printable verification sheet.

The Ra-01SH pad/signal assignment in design.RA01SH_PINS is the one unverified
thing on this board: Ai-Thinker publishes the module only as image-based or
CID-font PDFs, so the pad numbering could not be read from a primary source.

This sheet prints the land pattern at exactly 1:1 so you can seat a real module
on the paper and read off whether pad 8 really is NSS.  Print at 100% / "actual
size" - NOT "fit to page" - and check the 20 mm ruler with a caliper first.

    python scripts/gen_checksheet.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(PROJ, "out", "Ra-01SH-checksheet.svg")

# --- geometry, mirrored from gen_footprints.py -----------------------------
PITCH = 2.0
PAD_W, PAD_H = 2.0, 1.5      # 2.0 mm points outward from the module edge
COL_X = 8.0                  # the two pad columns, 16.0 mm apart
BODY_W, BODY_H = 16.0, 17.0  # 16 mm is the axis across the pad columns
YS = [-7.0 + PITCH * i for i in range(8)]

MARGIN = 22.0
W = BODY_W + 2 * MARGIN
H = BODY_H + 2 * MARGIN + 26.0    # extra room for the ruler + notes
CX, CY = W / 2.0, MARGIN + BODY_H / 2.0


def pad_name_by_number():
    by = {}
    for sig, pads in D.RA01SH_PINS.items():
        for p in ([pads] if isinstance(pads, str) else pads):
            by[int(p)] = sig
    return by


NAMES = pad_name_by_number()

# pad number -> (x, y) in local module coords.  Pads 1-8 run down the left
# edge, 9-16 back up the right edge (counter-clockwise), per KiCad's curated
# Ai-Thinker-Ra-01 land pattern.
POS = {}
for i, y in enumerate(YS):
    POS[i + 1] = (-COL_X, y)
for i, y in enumerate(reversed(YS)):
    POS[i + 9] = (COL_X, y)

p = []
a = p.append
a('<?xml version="1.0" encoding="UTF-8"?>')
a('<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" '
  'viewBox="0 0 %.2f %.2f">' % (W, H, W, H))
a('<style>'
  'text{font-family:DejaVu Sans,Arial,sans-serif}'
  '.pad{fill:#b8860b;stroke:#000;stroke-width:0.05}'
  '.body{fill:none;stroke:#000;stroke-width:0.15}'
  '.ctyd{fill:none;stroke:#888;stroke-width:0.05;stroke-dasharray:0.6 0.4}'
  '.num{font-size:1.0px;text-anchor:middle;fill:#000}'
  '.sig{font-size:0.95px;fill:#000}'
  '.ttl{font-size:2.2px;fill:#000}'
  '.sub{font-size:1.25px;fill:#000}'
  '.warn{font-size:1.35px;fill:#a00;font-weight:bold}'
  '.rule{stroke:#000;stroke-width:0.12}'
  '</style>')
a('<rect x="0" y="0" width="%.2f" height="%.2f" fill="#fff"/>' % (W, H))

# title
a('<text class="ttl" x="%.2f" y="7.5">Ra-01SH land pattern - PRINT AT 1:1</text>' % MARGIN)
a('<text class="sub" x="%.2f" y="11.5">PRAHARI rev B, U2. Seat a real module on '
  'this outline and confirm every signal name.</text>' % MARGIN)

# courtyard + body
a('<rect class="ctyd" x="%.3f" y="%.3f" width="%.3f" height="%.3f"/>'
  % (CX - 9.4, CY - 9.1, 18.8, 18.2))
a('<rect class="body" x="%.3f" y="%.3f" width="%.3f" height="%.3f"/>'
  % (CX - BODY_W / 2, CY - BODY_H / 2, BODY_W, BODY_H))

# pin-1 marker dot
a('<circle cx="%.3f" cy="%.3f" r="0.35" fill="#000"/>'
  % (CX - 9.4, CY - 7.0))

# pads + labels
for num in range(1, 17):
    lx, ly = POS[num]
    x = CX + lx
    y = CY + ly           # SVG y grows downward; module +y is the pad-1 row
    a('<rect class="pad" x="%.3f" y="%.3f" width="%.3f" height="%.3f"/>'
      % (x - PAD_W / 2, y - PAD_H / 2, PAD_W, PAD_H))
    a('<text class="num" x="%.3f" y="%.3f">%d</text>' % (x, y + 0.35, num))
    sig = NAMES.get(num, "?")
    if lx < 0:                                   # left column: label further left
        a('<text class="sig" x="%.3f" y="%.3f" text-anchor="end">%s</text>'
          % (x - 1.6, y + 0.35, sig))
    else:                                        # right column: label to the right
        a('<text class="sig" x="%.3f" y="%.3f">%s</text>'
          % (x + 1.6, y + 0.35, sig))

# 20 mm ruler for print-scale verification
ry = MARGIN + BODY_H + 16.0
a('<text class="sub" x="%.2f" y="%.2f">Scale check - this bar must measure '
  'exactly 20.0 mm:</text>' % (MARGIN, ry - 2.5))
a('<line class="rule" x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>'
  % (MARGIN, ry, MARGIN + 20.0, ry))
for i in range(21):
    t = 1.2 if i % 5 == 0 else 0.6
    a('<line class="rule" x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f"/>'
      % (MARGIN + i, ry, MARGIN + i, ry - t))
a('<text class="sub" x="%.2f" y="%.2f">0</text>' % (MARGIN - 0.5, ry + 3.0))
a('<text class="sub" x="%.2f" y="%.2f">20 mm</text>' % (MARGIN + 18.0, ry + 3.0))

a('<text class="warn" x="%.2f" y="%.2f">Pinout from KiCad curated '
  'Ai-Thinker-Ra-01; SX126x signal mapping still assumed. Verify.</text>'
  % (MARGIN, ry + 8.0))
a('<text class="sub" x="%.2f" y="%.2f">Body 17.0 x 16.0 mm, 16 castellated pads, '
  '2.0 mm pitch, pad 2.0 x 1.5 mm. Dot = pin 1 = ANT.</text>' % (MARGIN, ry + 11.5))
a('<text class="sub" x="%.2f" y="%.2f">If it disagrees: fix RA01SH_PINS in '
  'scripts/design.py, then re-run gen_footprints.py and gen_pcb.py.</text>'
  % (MARGIN, ry + 14.5))
a('</svg>')

open(OUT, "w", encoding="utf-8").write("\n".join(p))
print("wrote out/Ra-01SH-checksheet.svg  (%.1f x %.1f mm, print at 100%%)" % (W, H))
print("pad map under test:")
print("   " + ", ".join("%d=%s" % (n, NAMES.get(n, "?")) for n in range(1, 17)))
