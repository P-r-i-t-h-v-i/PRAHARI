from pathlib import Path
from PIL import Image,ImageDraw
import fitz,json

root=Path(__file__).resolve().parent
preview=root/'previews';preview.mkdir(exist_ok=True)
doc=fitz.open(root/'PRAHARI_SIH2026.pdf')
sheet=Image.new('RGB',(1440,1275),'#D9DFDC')
d=ImageDraw.Draw(sheet)
issues=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    path=preview/f'slide-{i+1:02d}.png';pix.save(path)
    im=Image.open(path);im.thumbnail((700,394))
    x=10+(i%2)*720;y=10+(i//2)*425
    sheet.paste(im,(x,y));d.text((x,y+398),f'{i+1:02d} / PRAHARI',fill='#152C3B')
    for word in page.get_text('words'):
        if word[0]<0 or word[1]<0 or word[2]>page.rect.width+.5 or word[3]>page.rect.height+.5:issues.append([i+1,word])
sheet.save(root/'PRAHARI_slide_overview.jpg',quality=92)
report={'pdf_pages':len(doc),'pdf_bytes':(root/'PRAHARI_SIH2026.pdf').stat().st_size,'pptx_bytes':(root/'PRAHARI_SIH2026.pptx').stat().st_size,'outside_page_text':issues,'page_text':[page.get_text() for page in doc]}
(root/'pdf_review.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='page_text'},indent=2))
assert len(doc)==6 and not issues
