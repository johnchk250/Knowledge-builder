"""Read-only audit of the Yard 1 migration and its operational boundaries."""
import argparse, collections, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from chp.store import Store

def audit(model,baseline,evidence):
 entities={e['id']:e for e in model['entities'] if e['id']==e['canonical_id'] and not e.get('inactive')}
 bylabel={e['label']:e['id'] for e in entities.values()}
 facts=[a for a in model['assertions'] if not a.get('retirement') and not a.get('suppressed')]
 added=[a for a in facts if a['created_version']>baseline['version']]
 prior={a['id']:a for a in baseline['assertions']};current={a['id']:a for a in model['assertions']}
 assert all(current.get(k)==v for k,v in prior.items()),'Prior assertion changed or lost'
 ev={e['id']:e for e in evidence}
 for a in added:
  assert a['canonical_subject'] in entities
  assert not a.get('canonical_object') or a['canonical_object'] in entities
  assert a.get('evidence') and a.get('context',{}).get('basis')
  for ref in a['evidence']:
   assert ref['evidence_id'] in ev
   assert ref.get('quote') or ref.get('region')
   if ref.get('region'):
    x0,y0,x1,y1=ref['region'];assert 0<=x0<x1<=1 and 0<=y0<y1<=1
  if a['context'].get('network'):assert a['context']['network'] in ['material','mechanical','electrical','control','utility']
 children=collections.defaultdict(set)
 for a in facts:
  if a['predicate']=='part_of':children[a['canonical_object']].add(a['canonical_subject'])
 def descendants(label):
  root=bylabel[label];seen=set();pending=[(root,())]
  while pending:
   n,parents=pending.pop();assert n not in parents,'Containment cycle: '+entities[n]['label']
   if n in seen:continue
   seen.add(n);pending.extend((c,parents+(n,)) for c in children[n])
  return seen
 yard=descendants('Coal Yard 1');spds=descendants('Coal Yard 1 SPDS')
 labels={entities[n]['label'] for n in yard}
 assert all(tag in labels for tag in ['EAC-7','EAD-1','EAE-1','EAF-1','EBA-8','UEB-1','UAX-1','UAX-5'])
 assert all(tag not in labels for tag in ['EAC-9','EAD-2','EAF-2','EBA-10','SPDSP-1A','SPDSP-1B','CHP Coal Run-off Pond'])
 assert len([n for n in spds if entities[n]['label'].endswith(' Sprinkler')])==28
 assert len([n for n in spds if ' Sector ' in entities[n]['label'] and ' SV-' in entities[n]['label']])==28
 assert len([n for n in spds if ' Sector ' in entities[n]['label'] and ' SV-' not in entities[n]['label']])==14
 assert sum(x.endswith(' SP-8G') or x.endswith(' SP-8H') for x in labels)==2
 assert not any(x.endswith((' SP-8A',' SP-8B')) for x in labels)
 def own(label,key):return [a for a in facts if a['canonical_subject']==bylabel[label] and a['predicate']==key]
 def values(label,key):return [a['value'] for a in own(label,key)]
 for tag,pairs,devices,pcs,power in [('EAC-7',18,36,30,680),('EBA-8',17,34,31,270)]:
  assert pairs in values(tag+' Belt protection devices Belt-sway switches (BSS)','quantity')
  assert devices in values(tag+' Belt protection devices Belt-sway switches (BSS)','individual_device_count')
  pc=tag+' Belt protection devices Pull-cord switches (PCS)'
  assert pcs in values(pc,'quantity') and not values(pc,'individual_device_count')
  assert power in values(tag+' Drive assembly Main motor','motor_rated_power')
  assert own(pc,'source_gap')
 assert own('EBA-8 Drive assembly Scoop coupling','source_discrepancy')
 assert {'PST-530','500 PST'}<=set(values('EBA-8 Drive assembly Scoop coupling','model_number'))
 assert own('EAF-1','source_discrepancy')
 assert len([x for x in labels if x.startswith('EAD-1 Central grease lubrication') and x.endswith(' Pump unit')])==3
 assert 'EAD-1 Boom Belt Weigher' in labels and 'EAD-1 Boom conveyor Belt scale' not in labels,'Existing boom weigher identity must be reused'
 assert any('33' in str(a['value']) for a in own('Stockpile Sequential Controller SC-01','source_discrepancy'))
 for n in [1,28]:
  sprinkler=f'Coal Yard 1 SPDS Sprinkler risers AP-1 to AP-28 AP-{n} Sprinkler'
  assert 30 in values(sprinkler,'rated_flow')
  assert all(ev[a['evidence'][0]['evidence_id']]['page']==2 for a in own(sprinkler,'rated_flow'))
 return {'ok':True,'baseline_version':baseline['version'],'result_version':model['version'],
  'new_entities':len(entities)-len([e for e in baseline['entities'] if e['id']==e['canonical_id'] and not e.get('inactive')]),
  'new_assertions':len(added),'prior_assertions_preserved':len(prior),'yard_records_including_root':len(yard),
  'review_gaps_and_disagreements':sum(a['predicate'] in ['source_gap','source_discrepancy'] for a in added),
  'source_documents':len({ev[r['evidence_id']]['document_id'] for a in added for r in a['evidence']}),
  'source_pages':len({(ev[r['evidence_id']]['document_id'],ev[r['evidence_id']]['page']) for a in added for r in a['evidence']}),
  'checks':['Existing assertions unchanged','Every added claim has valid page/region provenance and basis','No containment cycles in Yard 1','Other yards excluded','Shared pumps/pond excluded from Yard 1 ownership','28 physical sprinklers, 28 solenoids and 14 sectors','SP-8G/H local runoff identities','BSS pair arithmetic and unresolved PCS units','Coupling model disagreement retained','Machine lubrication pumps and final sprinkler datasheet sources']}

def main():
 p=argparse.ArgumentParser();p.add_argument('--model');p.add_argument('--out');args=p.parse_args()
 snap=json.loads((ROOT/'output/yard1-pilot/snapshot.json').read_text(encoding='utf8'))
 if args.model:m=json.loads(Path(args.model).read_text(encoding='utf8'))
 else:
  with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
   db.row_factory=sqlite3.Row;db.execute('BEGIN');m=Store.__new__(Store).model(db=db)
 report=audit(m,snap['model'],snap['evidence']);print(json.dumps(report,indent=2))
 if args.out:Path(args.out).write_text(json.dumps(report,indent=2),encoding='utf8')

if __name__=='__main__':main()
