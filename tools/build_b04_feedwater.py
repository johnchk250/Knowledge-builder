"""Build the reviewed175257 main pond-to-SPDS return only."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/plant-enrichment/B04/feedwater-175257'
DOC='doc_d92dbaa70d964993bb86';EV='ev_6d108aae58914c47bf74'

def main():
 m=json.loads((ROOT/'output/plant-enrichment/B04/sump-175259/accepted/model.json').read_text(encoding='utf8'));assert m['version']==633
 ops=[];system='ent_93afe5d239a54e9a963b';pond='ent_5ac31846c95842f8955c';r=[.15,.415,.725,.655];station=[.15,.07,.375,.655]
 def proof(region):return dict(origin='explicit',confidence=.98,evidence=[dict(evidence_id=EV,quote='',region=region)])
 def fact(s,p,v,region,obj=False,condition=None):
  c=dict(kind='classification' if p=='instance_of' else 'specification',basis='175257 Rev5 original,31-Jul-2019,approved14-Oct-2019. Pond station and Tank2 compartment paths visually traced; design only.')
  if p=='utility_supply_to':c.update(kind='connection',network='utility',verification='documented',condition=condition)
  ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=c,**proof(region)))
 def edge(s,t,region,condition):fact(s,'utility_supply_to',t,region,True,condition)
 def new(key,name,typ,owner,place,region):
  id='tmp_b04_return_'+key;ops.append(dict(op='entity',id=id,label=name,**proof(region)));fact(id,'instance_of',typ,region);fact(id,'part_of',owner,region,True);fact(id,'located_at',place,region,True);return id
 chambers=[]
 for i in [1,2,3]:chambers.append(new('chamber'+str(i),f'CHP Runoff pond chamber {i}','water_tank',pond,pond,r))
 fact(pond,'assembly_arrangement','Three chambers drawn: first chamber receives working/standby drainage inlets; third chamber contains CRP-1A/B. Inter-chamber wall/overflow construction is not specified here.',r)
 header=new('header','CHP Runoff feed-water common discharge header','utility_header',system,pond,station)
 filt=new('filter','CHP Runoff feed-water DUP-01 duplex filter','duplex_filter',system,'ent_36135b45a07c4d03bf06',[.25,.075,.36,.19])
 panel=new('panel','CHP Runoff feed-water LCP-01 panel','local_control_panel',system,pond,station)
 edge(pond,chambers[2],r,'Third-chamber suction-water boundary within the common pond; this does not specify an inter-chamber pipe or operating selection.')
 for pump in ['ent_20058e93e1bf4391b323','ent_51d70207f7a446298408']:
  fact(pump,'located_at',chambers[2],r,True)
  edge(chambers[2],pump,r,'Submerged suction in third chamber. One-working/one-standby pump design; no current duty asserted.')
  edge(pump,header,station,'Non-return/isolation branch to common125NB discharge.')
 edge(header,filt,[.23,.075,.365,.43],'125NB pond makeup line to duplex filter at pump-house2.')
 edge(filt,'ent_4bacbfff7b384d368f55',[.31,.085,.66,.25],'Filtered125NB pond return through MGV-04; this line enters SPDS-1 only.')
 edge('ent_4bacbfff7b384d368f55','ent_36777dcc88b24427abb1',[.54,.115,.68,.36],'Runoff makeup enters SPDS-1 compartment, distinct from client makeup and potable compartment. Existing MGV KKS source disagreement remains qualified.')
 fact(panel,'equipment_role','Local pump starter/control panel receives the source-drawn pressure and level signals for CRP-1A/B. Numeric settings and detailed cable/feeder mapping deferred.',station)
 fact(filt,'assembly_arrangement','Common125NB duplex filter with DPS-01 across it. Main pump schedule67m3/h at58MWC is distinct from indicated65m3/h pond-return flow; existing qualified ratings retained.',[.25,.07,.54,.185])
 OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'accepted/commit-log.json').exists();(OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
 pkg=dict(document_id=DOC,baseline_version=633,baseline_model='output/plant-enrichment/B04/feedwater-175257/baseline-model.json',expected_new_components=6,visual_ids=[EV],body=dict(summary='B04 Tier1 three pond chambers, existing CRP pump branches, common discharge/filter/control and SPDS-only return',operations=ops,intake_assessment=dict(route='mixed',purpose='Trace runoff water reuse to the correct tank compartment',questions=['Where do CRP-1A/B draw from and where does their filtered return enter?'],reviewed_evidence_ids=[EV],gaps=['Original full P&ID visually reviewed including station,125NB return, three distinct tank compartments and schedule. Individual valves/level settings, pump internals and civil overflow construction are Pass B.','No runoff-to-potable edge. Preserve existing source-qualified MGV KKS discrepancy and pump ratings; grouped reference record is not another installed pump.'])))
 (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print(json.dumps({'components':6,'operations':len(ops)}))

if __name__=='__main__':main()
