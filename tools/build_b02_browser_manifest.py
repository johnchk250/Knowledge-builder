"""Export claim expectations for actual UI journeys from an accepted snapshot."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/plant-enrichment/B02'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('model');p.add_argument('--since',type=int,required=True)
    p.add_argument('--out',required=True);args=p.parse_args()
    model=json.loads(Path(args.model).read_text(encoding='utf8'))
    if 'model' in model:model=model['model']
    snapshot=json.loads((BASE/'resume-v625.json').read_text(encoding='utf8'))
    evidence={e['id']:e for e in snapshot['evidence']}
    entities={e['id']:e for e in model['entities']}
    facts={}
    owners={}
    for a in model['assertions']:
        if a['retirement']:continue
        if a['predicate']=='part_of':owners[a['canonical_subject']]=a['canonical_object']
        if a['created_version']<args.since:continue
        facts.setdefault(a['canonical_subject'],[]).append(a)
    parts=[];roots=[]
    for id,claims in facts.items():
        e=entities[id];new=e['created_version']>=args.since
        descriptor={'id':id,'label':e['label'],'scene':owners[id] if new else id,
                    'version':e['created_version'],'facts':[]}
        for a in claims:
            s=a['evidence'][0]
            ev=evidence[s['evidence_id']]
            descriptor['facts'].append({'id':a['id'],'predicate':a['predicate'],
                'value':a['value'],'unit':a['unit'],'document':ev['document_id'],
                'page':ev['page'],'evidence':s['evidence_id']})
        (parts if new else roots).append(descriptor)
    Path(args.out).write_text(json.dumps({'version':model['version'],'parts':parts,
        'roots':roots},indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'parts':len(parts),'roots':len(roots),'claims':sum(len(x['facts']) for x in parts+roots)}))


if __name__=='__main__':main()
