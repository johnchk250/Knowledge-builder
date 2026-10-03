"""Read-only Yard-1 inventory, source text retrieval and original PDF rendering."""
import json, re, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')
from chp.store import Store
OUT=ROOT/'output/yard1-pilot';OUT.mkdir(parents=True,exist_ok=True)

def snapshot():
    with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN')
        s=Store.__new__(Store)
        data={'model':s.model(db=db),'documents':[dict(x) for x in db.execute('select * from documents')],
              'evidence':[dict(x) for x in db.execute('select * from evidence order by document_id,page,id')]}
        (OUT/'snapshot.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    return data

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'inventory'
    data=snapshot() if mode=='inventory' else json.loads((OUT/'snapshot.json').read_text(encoding='utf-8'))
    docs={d['id']:d for d in data['documents']};ents={e['id']:e for e in data['model']['entities']}
    if mode=='inventory':
        print('MODEL',data['model']['version'])
        for d in docs.values():
            if re.search(r'yard|stack|reclaim|spds|sprink|travel|bucket|luff|slew|belt conveyor.?[- ]?(7|8)|runoff|fire|hydrant',d['name'],re.I):
                print('DOC',d['id'],d['name'],len({e['page'] for e in data['evidence'] if e['document_id']==d['id']}))
        print('ENTITIES')
        for e in ents.values():
            if e['id']==e['canonical_id'] and re.search(r'yard|stack|reclaim|spds|sprink|^EA[DEF]-1$|^EAC-7$|^EBA-8$|^UE[BF]-[167]$|^UAX-[15]$',e['label'],re.I):
                print(e['id'],e['label'])
    elif mode=='facts':
        pattern=re.compile(sys.argv[2],re.I)
        ids={e['id'] for e in ents.values() if e['id']==e['canonical_id'] and pattern.search(e['label'])}
        for a in data['model']['assertions']:
            if not a.get('retirement') and not a.get('suppressed') and (a['canonical_subject'] in ids or a.get('canonical_object') in ids):
                print(json.dumps({'id':a['id'],'s':ents[a['canonical_subject']]['label'],'p':a['predicate'],'v':ents[a['canonical_object']]['label'] if a.get('canonical_object') else a['value'],'unit':a['unit'],'ctx':a['context'],'ev':a['evidence']},ensure_ascii=False))
    elif mode=='text':
        pattern=re.compile(sys.argv[2],re.I);page_filter={int(p) for p in sys.argv[3].split(',')} if len(sys.argv)>3 else None
        for d in docs.values():
            if not pattern.search(d['name']+' '+d['id']):continue
            print('DOCUMENT',d['id'],d['name'],d['sha256'])
            for e in data['evidence']:
                if e['document_id']==d['id'] and (page_filter is None or e['page'] in page_filter):
                    print('PAGE',e['page'],e['id'],e['image'],'\n',e['text'])
    elif mode=='search':
        pattern=re.compile(sys.argv[2],re.I)
        for e in data['evidence']:
            matches=list(pattern.finditer(e['text']))
            if matches:
                print(docs[e['document_id']]['name'],e['document_id'],'PAGE',e['page'],e['id'])
                for m in matches[:3]:print(re.sub(r'\s+',' ',e['text'][max(0,m.start()-100):m.end()+220]))
    elif mode=='render':
        import fitz
        d=docs[sys.argv[2]];pages=[int(p) for p in sys.argv[3].split(',')]
        with fitz.open(ROOT/'data/plant/originals'/d['sha256']) as pdf:
            for n in pages:
                p=pdf[n-1];region=[float(v) for v in sys.argv[4].split(',')] if len(sys.argv)>4 else [0,0,1,1]
                clip=fitz.Rect(region[0]*p.rect.width,region[1]*p.rect.height,region[2]*p.rect.width,region[3]*p.rect.height)
                scale=min(8,1800/max(clip.width,clip.height));f=OUT/f'{d["id"]}-p{n}-{"crop" if len(sys.argv)>4 else "page"}.png'
                p.get_pixmap(matrix=fitz.Matrix(scale,scale),clip=clip).save(f);print(f)

if __name__=='__main__':main()
