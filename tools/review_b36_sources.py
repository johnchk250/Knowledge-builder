"""Read-only source retrieval/rendering for B36; no model writes."""
import argparse, json, re, hashlib, sys
from pathlib import Path
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/plant-enrichment/B36'
s=json.loads((BASE/'baseline.json').read_text(encoding='utf-8'))
docs={d['id']:d for d in s['documents']}
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('doc');p.add_argument('--pages',default='');p.add_argument('--crop',default='');p.add_argument('--scale',type=float,default=1.4);p.add_argument('--text',action='store_true');p.add_argument('--montage',action='store_true');a=p.parse_args()
 d=docs.get(a.doc) or next(d for d in docs.values() if a.doc.casefold() in d['name'].casefold())
 path=ROOT/'data/plant/originals'/d['sha256'];assert hashlib.sha256(path.read_bytes()).hexdigest()==d['sha256']
 pdf=fitz.open(path);out=BASE/'review'/d['id'];out.mkdir(parents=True,exist_ok=True)
 text='\n'.join(f'\n--- PDF PAGE {i+1} ---\n'+pg.get_text() for i,pg in enumerate(pdf));(out/'text.txt').write_text(text,encoding='utf-8')
 print(d['id'],d['name'],'pages',len(pdf))
 pages=[int(x) for x in a.pages.split(',') if x] or list(range(1,len(pdf)+1))
 if a.montage:
  from PIL import Image,ImageDraw
  canvas=Image.new('RGB',(1400,430*((len(pages)+2)//3)),'white');draw=ImageDraw.Draw(canvas)
  for i,n in enumerate(pages):
   pix=pdf[n-1].get_pixmap(matrix=fitz.Matrix(.6,.6));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((450,395));x=(i%3)*465;y=(i//3)*430;canvas.paste(im,(x,y+25));draw.text((x,y),'Page '+str(n),fill='black')
  canvas.save(out/'montage.png');print(out/'montage.png');return
 for n in pages:
  pg=pdf[n-1]
  if a.text:print(f'PAGE {n}\n'+pg.get_text());continue
  r=pg.rect
  if a.crop:
   x0,y0,x1,y1=map(float,a.crop.split(','));r=fitz.Rect(r.width*x0,r.height*y0,r.width*x1,r.height*y1)
  file=out/(f'p{n}'+('-'+a.crop.replace(',','_') if a.crop else '')+'.png');pg.get_pixmap(matrix=fitz.Matrix(a.scale,a.scale),clip=r).save(file);print(file)
if __name__=='__main__':main()
