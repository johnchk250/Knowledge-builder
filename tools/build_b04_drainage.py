"""Source-reviewed breadth drainage, including two explicit TP13 route corrections."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/plant-enrichment/B04/sump-175259'
DOC='doc_0453a0a014424f1cae06';EV='ev_cfe00ec0be184ce7a51e'

def main():
 m=json.loads((ROOT/'output/plant-enrichment/B03/model-v632.json').read_text(encoding='utf8'))
 assert m['version']==632
 E={e['id']:e for e in m['entities']};ops=[]
 def label(s):
  ids={e['canonical_id'] for e in E.values() if e['label']==s};assert len(ids)==1,s;return ids.pop()
 def proof(r):return dict(origin='explicit',confidence=.98,evidence=[dict(evidence_id=EV,quote='',region=r)])
 def fact(s,p,v,r,obj=False,condition=None):
  c=dict(kind='classification' if p=='instance_of' else 'specification',basis='175259 Rev4 original p1,09-Sep-2019; enlarged yard/local/intermediate branch crops visually traced. Design routing only. Page2 review requests5m3 to10m3 while p1 retains5m3 labels; no capacity promoted as resolved.')
  if p=='utility_supply_to':c.update(kind='connection',network='utility',verification='documented',condition=condition or 'Source-drawn drainage path; no present operating state asserted.')
  ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=c,**proof(r)))
 def edge(s,t,r,condition=None):fact(s,'utility_supply_to',t,r,True,condition)
 def new(key,name,typ,owner,place,r):
  id='tmp_b04_'+key.replace('-','_');ops.append(dict(op='entity',id=id,label=name,**proof(r)));fact(id,'instance_of',typ,r);fact(id,'part_of',owner,r,True)
  if place:fact(id,'located_at',place,r,True)
  return id
 def membership(id,place,r):
  for p in ['part_of','located_at']:
   if not any(a['canonical_subject']==id and a['predicate']==p and not a['retirement'] for a in m['assertions']):fact(id,p,place,r,True)
 pond='ent_5ac31846c95842f8955c'
 regions={'UEE-2':[.265,.04,.68,.27],'UEF-12':[.05,.205,.43,.45],'UEF-3':[.10,.70,.60,.94]}
 groups={'UEE-2':'ent_91ebdd9ff58546668756','UEF-12':'ent_75585a0864b74b46a8de','UEF-3':'ent_48ace7b370f04fc38adc'}
 pits={}
 for place,r in regions.items():
  pits[place]=new(place,'CHP Intermediate sump near '+place,'sump',groups[place],label(place),r)
  membership(groups[place],label(place),r);edge(label(place),pits[place],r,'Local gravity drainage into intermediate collection pit.');edge(pits[place],groups[place],r,'Suction from intermediate pit by existing scheduled pump pair.')
 edge(groups['UEF-3'],pond,[.40,.33,.845,.94],'125NB discharge to coal runoff pond working/standby chamber inlet selection.')
 edge(groups['UEF-12'],pits['UEE-2'],[.27,.065,.425,.43],'100NB discharge rises to the intermediate sump near UEE-2.')
 edge(groups['UEE-2'],pond,[.32,.04,.70,.44],'125NB discharge from SP-7A/B to coal runoff pond inlet selection.')
 for number,pair,r in [(8,'A/B',[.025,.315,.14,.43]),(9,'C/D',[.085,.275,.185,.38]),(10,'E/F',[.135,.25,.235,.335]),(11,'G/H',[.20,.20,.29,.305]),(0,'M/N',[.35,.75,.47,.87])]:
  place='UEE-1' if number==0 else f'UEF-{number}'
  local=new('local'+str(number),f'{place} Drainage sump and SP-1{pair} pump pair','functional_assembly',label(place),label(place),r)
  fact(local,'assembly_arrangement',f'Local collection sump, SP-1{pair} duty/standby pump pair, level switches and local panel shown as a grouped assembly. Fine internals and level settings deferred; capacity review discrepancy retained.',r)
  edge(label(place),local,r,'Peripheral/local gravity drainage into sump; pump pair transfers collected water.')
  edge(local,pits['UEF-3' if number==0 else 'UEF-12'],regions['UEF-3' if number==0 else 'UEF-12'],'65NB pumped branch to intermediate collector; pair assignment from original labels, not inferred alphabetically.')
 tp1='ent_67fbbe1cde554a03a148';edge(label('UEF-1'),'ent_be0bcbae381345dbbbba',regions['UEF-3'],'Local and jetty collection boundary; reuse existing intermediate sump identity.')
 edge(tp1,pits['UEF-3'],regions['UEF-3'],'100NB discharge from intermediate sump near UEF-1 to intermediate sump near UEF-3.')
 edge('ent_16d4fcf603644364a57b',pits['UEE-2'],[.32,.035,.59,.225],'65NB UEE-3 sump branch enters intermediate sump near UEE-2. Existing pond edge is an overall drainage destination, not a direct pipe.')
 for fid,pump in [('fact_a7cf934a2f5e4169afb1','ent_707d01d4e46f4956b99e'),('fact_b85fbf936f9345e8bd4d','ent_105b5e78f0ad4b7093ff')]:
  ops.append(dict(op='retire',assertion_id=fid,reason='Original175259 top65NB UEF-13 branch terminates at the intermediate sump explicitly labelled near UEE-2. Prior UEF-1 interpretation was wrong; replace with source-traced destination.',**proof([.32,.035,.68,.225])))
  edge(pump,pits['UEE-2'],[.32,.035,.68,.225],'UEF-13 SP-2A/B common65NB branch to intermediate sump near UEE-2, not UEF-1.')
 for yard,pair,tp,r in [(4,'A/B',4,[.40,.52,.51,.675]),(3,'C/D',5,[.50,.52,.615,.675]),(2,'E/F',6,[.605,.52,.72,.675])]:
  pile=label(f'EAE-{yard}');pit=new('yard'+str(yard),f'EAE-{yard} and UEF-{tp} runoff sump','sump',pile,pile,r)
  pumps=new('yardpumps'+str(yard),f'EAE-{yard} Runoff pump pair SP-8{pair}','functional_assembly',pit,pit,r)
  fact(pumps,'assembly_arrangement',f'Source-specific SP-8{pair} pump pair with local panel and level switches; one working/one standby design. Stockpile{yard} and UEF-{tp} share this collection pit.',r)
  edge(pile,pit,r,'Stockpile runoff gravity collection.');edge(label(f'UEF-{tp}'),pit,r,'Adjacent transfer-building drainage enters the same pit.');edge(pit,pumps,r,'Two pump suctions from the shared pit.');edge(pumps,pond,[.40,.315,.85,.68],'125NB pumped disposal to coal runoff pond inlet selection; separate yard branch.')
 fact(pond,'source_discrepancy','175259 original p1 Rev4 retains5m3 local-pit labels, while p2 Rev3 review/reply requests5m3 to10m3 and says Revised. Local final capacity is unresolved; the branch topology and pump assignments are independently readable.',[.03,.02,.98,.97])
 ops[-1]['evidence'].append(dict(evidence_id='ev_aa6e4a2bb49644ebb9ba',quote='revise the sump pit size - 5m3 to 10m3 as finalised in the DBR(Date: 24-Aug-19)'))
 OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'accepted/commit-log.json').exists()
 (OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
 evs=json.loads((ROOT/f'output/plant-enrichment/B04/review/{DOC}-evidence.json').read_text(encoding='utf8'))
 pkg=dict(document_id=DOC,baseline_version=632,baseline_model='output/plant-enrichment/B04/sump-175259/baseline-model.json',expected_new_components=14,visual_ids=[EV],body=dict(summary='B04 Tier1 drainage collectors, three remaining yard pump pairs and correction of two TP13 outlet destinations',operations=ops,intake_assessment=dict(route='mixed',purpose='Connect local sump pumps through the correct collectors to the common runoff pond',questions=['Which pit and pump pair handles each CHP location, and where does it discharge?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Original p1 full drawing and enlarged yard/top/bottom route crops reviewed; p2 review text inspected. Final local pit capacities remain discrepant; numerical capacities are not added.','Reuse Yard1 SP8G/H, existing TP1/silo/crusher/TP13 components and their qualified ratings. LHP/reference boundaries retained; no fabricated pump unit identities.','Pass B: individual pump internals, all valves/level settings and detailed civil routing; feedwater return is a separate175257 package.'])))
 (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print(json.dumps({'operations':len(ops),'components':14,'retired':2}))

if __name__=='__main__':main()

