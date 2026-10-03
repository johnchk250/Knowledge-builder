"""Build the source-reviewed 175255 Pass-A backbone at v630; accept via accept_b02_scoped.py."""
import json
import hashlib
import sqlite3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from chp.store import Store

OUT=ROOT/'output/plant-enrichment/B03/spds-175255'
DOC='doc_5a36f2843d504d6e96de'
EV='ev_ac1d949bfd3440969c6a'
SYS='ent_3ebb96607d1f4f3094f0'
HOUSE='ent_36135b45a07c4d03bf06'
TANK='ent_dbe58a4eb9a74ed6b0c4'
PUMPS=['ent_8018190d7c0b4b098fa7','ent_35093c21b4754c8695d3']
PILES=['ent_18d771b5863a4f2685cd','ent_e1181f45e78e462cbc07','ent_b74d44c57a034fe885c0']
RING1='ent_947a6fba09134b2ba7fe'
BASIS='175255 Rev2 P&ID original p1, FIO 21-Jan-2019; design arrangement only. Source schedule says154m3/h,124MWC; major BOM says115MWC. Existing source-qualified pump identities and ratings retained. '
ops=[]
def proof(region,page=1):
 return {'origin':'explicit','confidence':.97,'evidence':[{'evidence_id':EV if page==1 else 'ev_ddc8fa0a723b4658832d','quote':'','region':region}]}
def fact(s,p,v,r,obj=False,unit=None,kind='specification',network=None,condition=None):
 a={'op':'assert','subject':s,'predicate':p,('object_entity' if obj else 'value'):v,'context':{'kind':kind,'basis':BASIS},**proof(r)}
 if unit:a['unit']=unit
 if network:a['context'].update(network=network,verification='documented')
 if condition:a['context']['condition']=condition
 ops.append(a)
def edge(s,t,r,condition=None):fact(s,'utility_supply_to',t,r,True,kind='connection',network='utility',condition=condition)
def entity(key,label,typ,owner,r,located=None):
 id='tmp_b03_'+key
 ops.append({'op':'entity','id':id,'label':label,**proof(r)})
 fact(id,'instance_of',typ,r,kind='classification');fact(id,'part_of',owner,r,True)
 if located:fact(id,'located_at',located,r,True)
 return id
station=[.715,.025,.98,.275]
header=[.615,.025,.75,.58]
filt=entity('filter','SPDS Common DUP-01 duplex suction filter','duplex_filter',SYS,station,HOUSE)
suction=entity('suction','SPDS Common filtered suction header','utility_header',SYS,station,HOUSE)
discharge=entity('discharge','SPDS Common pump discharge header','utility_header',SYS,station,HOUSE)
main=entity('main','SPDS Common distribution header','utility_header',SYS,header)
panel=entity('panel','SPDS Local pump starter panel','local_control_panel',SYS,station,HOUSE)
recirc=entity('recirc','SPDS Pressure-relief and recirculation assembly','functional_assembly',SYS,station,HOUSE)
fact(recirc,'assembly_arrangement','100NB recirculation to common RCC water tank through GAV-06 and PRV-01 with GLV-02 bypass. No relief setting or live valve position established.',station)
edge(TANK,filt,station,'Stockpile-water takeoff through GAV-01, 200NB. Compartment allocation retained from the separately reviewed common tank GA; this sheet depicts the common tank outline.')
edge(filt,suction,station)
for i,p in enumerate(PUMPS):
 branch='A' if i==0 else 'B';gavin='02' if i==0 else '04';gavout='03' if i==0 else '05';nrv='01' if i==0 else '02'
 edge(suction,p,station,f'200NB suction through GAV-{gavin}; branch {branch} of one-working/one-standby design. No present duty selection asserted.')
 edge(p,discharge,station,f'200NB discharge through NRV-{nrv} and GAV-{gavout}; pump branch {branch}.')
 motor=['ent_16467383a69040fd8ab4','ent_8108d0924c334f5b817f'][i]
 fact(motor,'mechanically_drives',p,station,True,kind='connection',network='mechanical')
edge(discharge,main,station,'200NB common distribution outlet via GLV-01 at drawing point C; separate from pressure-relief return.')
edge(discharge,recirc,station,'100NB pressure-relief/recirculation branch; no claim of continuous or simultaneous flow.')
edge(recirc,TANK,station,'100NB return to source tank.')
fact(filt,'nominal_diameter',200,station,unit='NB')
fact(suction,'nominal_diameter',200,station,unit='NB')
fact(main,'assembly_arrangement','Common 200NB header supplies four independent stockpile ring headers. The drawing shows a150NB continuation below stockpile3 and100NB at stockpile4; ring distribution uses100NB. These are source bores, not a surveyed pipe route.',header)
fact(SYS,'source_discrepancy','175255 p1 water-pump schedule gives154m3/h and124MWC for SPDSP-1A/1B; major BOM item1 gives154m3/h and115MWC. Preserve both source bases; no head selected as definitive.',[.34,.27,.978,.705])
fact(SYS,'assembly_arrangement','Four stockpiles have28 sprinkler points each (14 per side),112 total; maximum4 operate at a time,2 per stockpile in2 selected stockpiles. AP labels identify physical spray points; SC/SV sector mapping is a separate control-source claim and is not inferred from suffixes.',[.345,.59,.815,.972])
edge(main,RING1,[.045,.025,.75,.185],'Supply to stockpile EAE-1 ring through100NB local sides; reuse accepted Yard1 header.')
for n,pile in enumerate(PILES,2):
 y0={2:.185,3:.32,4:.45}[n];r=[.025,y0,.665,y0+.13]
 ring=entity('ring'+str(n),f'EAE-{n} SPDS ring header','utility_header',pile,r,pile)
 edge(main,ring,[.60,.025,.75,.58],f'Stockpile EAE-{n} branch; common main continues to other stockpiles as drawn. No simultaneous operation implied.')
 fact(ring,'nominal_diameter',100,r,unit='NB')
 fact(ring,'assembly_arrangement',f'Two side headers supply28 physical sprinkler application points AP-{(n-1)*28+1} to AP-{n*28}. Riser gate/solenoid/globe valve arrangement65NB;32NB QRC at30m intervals is a separate machine makeup branch. Individual AP-to-SV mapping deferred.',r)
 fact(ring,'sprinkler_count',28,r,unit='No.')
 edge(ring,pile,r,'Water spray application through the grouped sprinkler risers. Application boundary, not a pipe ending inside the coal pile.')
fact('ent_74097576de5241a89a9a','monitors_equipment',filt,station,True)
fact('ent_1915a78bf4f545c0beb5','monitors_equipment',discharge,station,True)
fact(panel,'equipment_role','Local starter panel receives the source-drawn PS-01 and DPS-01 signals and connects to both pump motors. Existing detailed protection claims remain source-qualified; no numeric setting or feeder mapping added.',station)
# The review sheet qualifies pipe routing, not the functional branch direction.
a={'op':'assert','subject':main,'predicate':'source_gap','value':'175255 p2 review requests routing via transfer towers with stockpile subheaders and identifies overground/buried routing as unresolved in this sheet; vendor promises a separate layout. This topology does not certify physical pipe routing.','context':{'kind':'specification','basis':'175255 original p2 review/replies, FIO21-Jan-2019'},**proof([.11,.25,.97,.85],2)};ops.append(a)

def main_build():
 with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
  db.row_factory=sqlite3.Row;db.execute('BEGIN');m=Store.__new__(Store).model(db=db)
  assert m['version']==630
  assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
  doc=dict(db.execute('SELECT * FROM documents WHERE id=?',(DOC,)).fetchone())
  evs=[r[0] for r in db.execute('SELECT id FROM evidence WHERE document_id=?',(DOC,))]
 assert hashlib.sha256((ROOT/'data/plant/originals'/doc['sha256']).read_bytes()).hexdigest()==doc['sha256']
 labels={e['label'] for e in m['entities']}
 assert all(o['label'] not in labels for o in ops if o['op']=='entity')
 OUT.mkdir(parents=True,exist_ok=True)
 def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
 save('baseline-model.json',m)
 save('package.json',{'document_id':DOC,'baseline_version':630,'baseline_model':'output/plant-enrichment/B03/spds-175255/baseline-model.json','expected_new_components':9,'visual_ids':evs,'body':{'summary':'B03 Tier1 SPDS common filter, pumps, distribution and four stockpile branches; retain head/routing qualifications','operations':ops,'intake_assessment':{'route':'mixed','purpose':'Trace the common stockpile water supply to all four physical yard boundaries','questions':['How do the common tank and duty/standby pumps feed the four stockpile headers?'],'reviewed_evidence_ids':evs,'gaps':['Both original pages reviewed; p1 station/header/schedule/notes examined with enlarged crops; p2 review/replies inspected. Finer valve tags, pump internals and all AP-to-SV control mappings remain depth work.','SW/PW supplies are separate B03 work. P&ID175091 has references but no standalone source located in current inventory.']}}})
 print(json.dumps({'operations':len(ops),'components':9,'baseline':630}))
if __name__=='__main__':main_build()
