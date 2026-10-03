"""Build durable B36 ledgers from the fresh accepted export and review record.

Read-only with respect to canonical data. Does not infer field commissioning.
"""
import argparse,csv,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'output/plant-enrichment/B36'
TARGETS=['EBA-18A','EBA-18B','UEF-13','FG-17','FG-18','QB-3','QB-4','EAT-3','EAT-4']
VISUAL={
 'doc_52e18b65d3b845fdb786':[1,2,3,4,5,6], 'doc_a9043e95d82c40f399ec':[1,2,3],
 'doc_800245b27bbd4afb900b':[1], 'doc_7aa49cc0d1c34af7ac06':[1,3,4,5,6,7,8,9,10,12,14],
 'doc_97e93732778e4618b52b':[10], 'doc_64825298f3d243368408':[1,3,4,5],
 'doc_62fdccede7154dc2b8b6':[3], 'doc_957d8f8bd41c4e71be3c':[2],
 'doc_9258f527621741938b79':[1], 'doc_41965812f7d842f3b1ef':[1,2,3,4,8,11,12],
 'doc_878e57f585f54e29b031':[16], 'doc_558ade05e4644a008b81':[1,2,3,4,5,6],
 'doc_bca09d68af9b43e3b633':[2], 'doc_3cfdfb0f23c6429eb268':[2,3],
 'doc_9b7d3360a5e84ec2abc3':[1,2], 'doc_5537009e2cff4fad875e':[2],
 'doc_0453a0a014424f1cae06':[1], 'doc_31b03f5030bc4db69d8d':[6,7,8,12,13,14],
 'doc_41860f7c9ac2467bbdb4':[2,4,5], 'doc_67a40e7649224ad08ae4':[112,113,121],
 'doc_6c1174cd1f294003a5e8':[1], 'doc_39a3930034b44154af6b':[1],
 'doc_ea7b9d057938417f822f':[1], 'doc_aebc312211eb4a029866':[2],
 'doc_61ba41211c294877a80e':[2], 'doc_e09ca845387544f8b9c2':[1],
 'doc_425fb77433564871b40e':[2,3,4], 'doc_0ed3cc8247ed4484ac8f':[3],
 'doc_9ea3e0c55ca347ae96a2':[3], 'doc_40568f1cddaf46f08262':[1],
}
EXCLUDED={'doc_aebc312211eb4a029866':'Later external scraper package names limestone/gypsum conveyors, not18AB; no installed coal18 scraper inferred.', 'doc_61ba41211c294877a80e':'Later internal scraper package names limestone/gypsum conveyors. Earlier applicableIS14 coal18 drawing retained.', 'doc_a786031791b9437d9479':'DE philosophy p5 heading/body inconsistency: body describes crusher-house KF1/2 and existing18AB returns. Completed crusher interfaces preserved; no TP13 DE system inferred.', 'doc_40568f1cddaf46f08262':'Bunker DE layout p1 shows19AB/bunker-bay hoods; UEF13 is a key-plan reference. Downstream B38-B42 scope, no TP13 extraction assembly inferred.'}
def dump(name,data): (BASE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('--intake',default='accepted');a=p.parse_args();sys.stdout.reconfigure(encoding='utf-8')
 snap=json.loads((BASE/'baseline.json').read_text(encoding='utf-8'));m=json.loads(Path(a.model).read_text(encoding='utf-8'));old={x['id'] for x in snap['model']['assertions']};ev={e['id']:e for e in snap['evidence']};entities={e['id']:e for e in m['entities']};bylabel={e['label']:e['id'] for e in m['entities'] if e['canonical_id']==e['id'] and not e['inactive']};docs={d['id']:d for d in snap['documents']}
 added=[x for x in m['assertions'] if x['id'] not in old];commits=[json.loads(l) for l in (BASE/a.intake/'commits.jsonl').read_text(encoding='utf-8').splitlines()];allfacts=[x for x in m['assertions'] if not x['retirement'] and not x['suppressed']]
 def supports(f):
  return [{**e,'document_id':ev[e['evidence_id']]['document_id'],'page':ev[e['evidence_id']]['page'],'original_url':'http://127.0.0.1:8775/api/original/'+ev[e['evidence_id']]['document_id']+'#page='+str(ev[e['evidence_id']]['page']),'readable_detail_url':('http://127.0.0.1:8775/api/evidence-detail/'+e['evidence_id']+'?region='+','.join(map(str,e['region']))) if e.get('region') else None} for e in f['evidence']]
 claims=[{**f,'subject_label':entities[f['canonical_subject']]['label'],'object_label':entities.get(f['canonical_object'],{}).get('label'),'source_supports':supports(f)} for f in added];dump('claims.json',claims)
 relations=[f for f in claims if f.get('canonical_object')];dump('boundaries.json',{'scope':'B36 localB02/B04 boundary closure; global service batches remain open','relations':relations,'unresolved':['No commissioned plant electrical feeder/cable assignment for18AB or local measurement units. Vendor circuit feeds are distinct from upstream plant feeders.','Service-water32NB hose interface and potable300L roof tank are documented; individual sharedpump/tag discrepancy remains globalB02.','DFDS AP12/13/15/16 piping labels disagree with P&ID/philosophy; retained as design-qualified branches.','UEF13 sump pit5m3 depicted versus10m3 review; final civil drawing required.','Sampling return, SNC2/elevator and access detail expansion reservedB37.']})
 parents={};places={}
 for f in allfacts:
  if f['predicate']=='part_of':parents.setdefault(f['canonical_subject'],set()).add(f['canonical_object'])
  if f['predicate']=='located_at':places.setdefault(f['canonical_subject'],set()).add(f['canonical_object'])
 involved={f['canonical_subject'] for f in added}|{f['canonical_object'] for f in added if f['canonical_object']};oldids={e['id'] for e in snap['model']['entities']}
 dump('identities.json',[{'id':i,'label':entities[i]['label'],'aliases':entities[i]['aliases'],'decision':'reused canonical identity' if i in oldids else 'new source-backed descriptive component; no invented field tag','owner_ids':sorted(parents.get(i,[])),'place_ids':sorted(places.get(i,[])),'role':'shared boundary' if entities[i]['label'] in ['DFDS System-2','CHP Main Control Room DCS','CHP Potable Water System','CHP Service Water System-2','CHP Intermediate sump near UEF-1'] else 'equipment or maintainable subassembly','accepted_claim_ids':[f['id'] for f in added if f['canonical_subject']==i]} for i in sorted(involved)])
 sourceids={ev[e['evidence_id']]['document_id'] for f in added for e in f['evidence']};reviewids={p.name for p in (BASE/'review').iterdir() if p.is_dir()};sources=[]
 for did in sorted(sourceids|reviewids):
  if did not in docs:continue
  d=docs[did];cs=[c for c in commits if c['document_id']==did];fs=[f for f in added if any(ev[e['evidence_id']]['document_id']==did for e in f['evidence'])];used=set(e['evidence_id'] for f in fs for e in f['evidence']);regions=[]
  for f in fs:
   for e in f['evidence']:
    if e.get('region') and {'page':ev[e['evidence_id']]['page'],'region':e['region']} not in regions:regions.append({'page':ev[e['evidence_id']]['page'],'region':e['region']})
  folder=BASE/'review'/did;montage=(folder/'montage.png').exists();text=(folder/'text.txt').exists()
  sources.append({'document_id':did,'name':d['name'],'sha256':d['sha256'],'original_path':str(ROOT/'data/plant/originals'/d['sha256']),'disposition':'used' if did in sourceids else 'not-applicable' if did in EXCLUDED else 'corroborating','reason':EXCLUDED.get(did,'Profile p3 explicitly labels18AB betweenUEE3 andUEF13; Rev1 corroborates route, newer exact18 GA supplies scalars.' if did=='doc_9ea3e0c55ca347ae96a2' else 'Explicit selected equipment/family scope recorded in accepted claim basis; pages outside this scope are inventory/context only.'),'revision_status_applicability':sorted(set(f['context'].get('basis','') for f in fs)),'visually_inspected_full_or_dense_pages':VISUAL.get(did,[]),'visual_semantic_claim_regions':regions,'used_text_quote_pages':sorted(set(ev[e['evidence_id']]['page'] for f in fs for e in f['evidence'] if e.get('quote'))),'text_retrieval':text,'montage_triage':montage,'semantic_pages':sorted(set(ev[eid]['page'] for eid in used)),'evidence_inventory':[{'id':e['id'],'page':e['page'],'disposition':'semantic original region/quote reviewed' if e['id'] in used else 'inventory/context triage, no deep semantic review claimed'} for e in snap['evidence'] if e['document_id']==did],'limitations':'Catalogue/control pages without exact installed mapping do not prove model-specific installed selections; nonselected conveyor/sampling/access detail is outsideB36. Rendered files alone are not proof of visual review.'})
 dump('sources.json',sources)
 uncertainties=[f for f in claims if f['predicate'] in ['source_gap','source_discrepancy']];dump('uncertainties.json',uncertainties)
 dimensions=['identity','purpose/place','containment','material routes','mechanical drive','utilities','control/protection','ratings/maintenance','provenance','visual journey']
 def closure(root):
  result={root};change=True
  while change:
   before=len(result);result|={i for i,ps in parents.items() if ps&result};change=len(result)!=before
  return result
 patterns={'identity':{'instance_of'},'purpose/place':{'equipment_role','located_at','location_description'},'containment':{'part_of'},'material routes':{'material_flow_to','discharges_to'},'mechanical drive':{'mechanically_drives','assembly_arrangement'},'utilities':{'utility_supply_to','oil_flow_to','water_flow_to','supply_requirement','motor_voltage','power_consumption'},'control/protection':{'start_permissive','trip_condition','trip_threshold','alarm_threshold','control_signal_to'},'ratings/maintenance':{'quantity','motor_rated_power','rated_capacity','maintenance_requirement','component_dimension'},'provenance':set(),'visual journey':set()}
 with (BASE/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['target','dimension','status','accepted_claim_ids','investigation','remaining_evidence']);w.writeheader()
  for t in TARGETS:
   cl=closure(bylabel[t]);tf=[f for f in allfacts if f['canonical_subject'] in cl];gaps=[f for f in tf if f['predicate']=='source_gap'];dis=[f for f in tf if f['predicate']=='source_discrepancy']
   for dim in dimensions:
    selected=[x for x in tf if x['predicate'] in patterns[dim]];status='supported' if selected else 'missing-source'
    evidence_needed=''
    if not selected:evidence_needed='No exact relation/value found for this dimension after scope/source review; do not infer an installed connection.'
    if dim=='material routes' and t.startswith(('QB','EAT')):status='not applicable with evidence';selected=[x for x in tf if x['predicate']=='equipment_role']
    if dim=='mechanical drive' and t.startswith('QB'):
     status='not applicable with evidence';selected=[x for x in tf if x['predicate'] in ['equipment_role','control_signal_to']];evidence_needed='Tandem detection probe/electronics and relay-triggered sandbag marker, not a motor-driven measurement machine; no marker motor inferred.'
    if dim in ['ratings/maintenance','control/protection','utilities']:
     keywords={'ratings/maintenance':['diameter','rating','ratio','quantity','count','length','idler','plate','skirt','calibrat','sensitiv','brake','speed','clearance','interval'], 'control/protection':['logic','timer','mcc','terminal','relay','polarity','setpoint','field loop','interlock','selector','commission'], 'utilities':['feeder','supply','voltage','electrical','thermal','water','air','routing','piping','isolation','oil grade','fill']}[dim]
     relevant_dis=[x for x in dis if any(k in str(x['value']).lower() for k in keywords)];relevant_gaps=[x for x in gaps if any(k in str(x['value']).lower() for k in keywords)]
     selected+=relevant_dis+relevant_gaps
     if relevant_dis:status='contradictory'
     elif relevant_gaps:status='missing-source (design support retained)'
     evidence_needed='|'.join(x['value'] for x in relevant_dis+relevant_gaps)
     if dim=='utilities' and t.startswith(('QB','EAT','FG','EBA')):
      evidence_needed+='|Final plant feeder/starter/cable/commissioning schedule not identified; vendor input ratings do not establish electrical supply ownership.'
      if status=='supported':status='missing-source (local design support retained)'
    if dim=='provenance':selected=tf;status='supported'
    if dim=='visual journey':
     proof=BASE/'browser-journeys.json';verified=proof.exists() and json.loads(proof.read_text(encoding='utf-8')).get('version')==m['version'] and json.loads(proof.read_text(encoding='utf-8')).get('ok')
     status='supported: actual browser journey' if verified else 'pending actual browser journey';evidence_needed='See browser-journeys.json and verification.md for individual target, source/return and viewport checks.'
    w.writerow({'target':t,'dimension':dim,'status':status,'accepted_claim_ids':'|'.join(x['id'] for x in selected),'investigation':'Exact GA/model/BOM, applicable drive/auxiliary, localPID, controls/manual and adjacent accepted boundary reviewed; sources.json distinguishes original region/quote review from inventory triage.','remaining_evidence':evidence_needed or ('B37 sampling/elevator/access expansion excluded' if t=='UEF-13' else '')})
 print(json.dumps({'version':m['version'],'newClaims':len(claims),'identities':len(involved),'usedDocuments':len(sourceids),'sourceDispositions':len(sources),'qualifiedGaps':len(uncertainties),'coverageCells':len(TARGETS)*10}))
if __name__=='__main__':main()
