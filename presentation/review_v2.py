from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw
import json
root=Path(__file__).resolve().parent
out=root/'previews_v2';out.mkdir(exist_ok=True)
doc=fitz.open(root/'PRAHARI_SIH2026_v2.pdf')
sheet=Image.new('RGB',(1440,1275),'#D9DFDC');draw=ImageDraw.Draw(sheet)
issues=[]
for i,page in enumerate(doc):
    path=out/f'slide-{i+1:02d}.png';page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(path)
    im=Image.open(path);im.thumbnail((700,394));x=10+(i%2)*720;y=10+(i//2)*425
    sheet.paste(im,(x,y));draw.text((x,y+399),f'{i+1:02d} / PRAHARI · v2',fill='#152C3B')
    for word in page.get_text('words'):
        if word[0]<0 or word[1]<0 or word[2]>page.rect.width+.5 or word[3]>page.rect.height+.5:issues.append((i+1,word))
sheet.save(root/'PRAHARI_v2_overview.jpg',quality=92)
report={'pages':len(doc),'outside_page_text':issues,'words_per_slide':[len(p.get_text().split()) for p in doc]}
(root/'v2_pdf_check.json').write_text(json.dumps(report,indent=2));print(report)
assert len(doc)==6 and not issues
