"""B36 reviewed source-specific intake. Default is an isolated rehearsal.

Uses the established proposal builder, never replays earlier pilot functions.
All physical dimensions are source design facts; display coordinates are UI only.
"""
import argparse,hashlib,json,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
import enrich_conveyor_tp1_pilot as core
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate,commit
BASE=ROOT/'output/plant-enrichment/B36'
DOCS={**core.DOCS,'ga':'doc_52e18b65d3b845fdb786','tp':'doc_a9043e95d82c40f399ec','piping':'doc_800245b27bbd4afb900b','gate':'doc_9258f527621741938b79','md':'doc_41965812f7d842f3b1ef','md_manual':'doc_878e57f585f54e29b031','bw':'doc_558ade05e4644a008b81','bw_manual':'doc_3898269d389646c1829c','primary':'doc_6c1174cd1f294003a5e8','secondary':'doc_39a3930034b44154af6b','internal':'doc_ea7b9d057938417f822f','idler':'doc_e09ca845387544f8b9c2','switch':'doc_425fb77433564871b40e','calc':'doc_67a40e7649224ad08ae4'}
core.DOCS=DOCS
TAGS=['EBA-18A','EBA-18B'];TP='UEF-13'
FULL=[.015,.02,.985,.98]

class Batch(core.Batch):
 def finish(self,out,apply=True):
  body={'summary':self.name,'operations':self.ops,'intake_assessment':{'route':'mixed','purpose':'B36 detailed source-backed equipment, connections and maintainable auxiliaries; B37 excluded.','questions':['Which design applies independently to 18A and 18B?','What supports, drives, lubricates, measures and protects each part?','Which local/shared boundaries and conflicting records remain unresolved?'],'gaps':self.gaps+['Deep structured review uses pages '+', '.join(map(str,sorted(self.pages)))+'. All other document evidence blocks are inventory/context triage, not a claim of visual inspection or exhaustive extraction.','Design applicability only: field installation, commissioned settings and live state are not established.'],'reviewed_evidence_ids':[e['id'] for e in self.ev]}}
  report=validate(self.s,{'summary':self.name,'operations':self.ops},self.doc,self.version,visual_ids=self.visual)
  if report['errors']:raise ValueError(json.dumps(report['errors']))
  (out/(self.name+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  pending=stage(self.s,self.doc,body,visual_ids=self.visual,analysis_dir=str(out),expected_version=self.version)
  accepted=commit(self.s,pending['proposal_id'])
  record={'name':self.name,'document_id':self.doc,'base_version':self.version,'result_version':self.s.version(),'operations':len(self.ops),'pages':sorted(self.pages),'visual_ids':sorted(self.visual),'warnings':report['warnings'],'commit':accepted}
  with (out/'commits.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
  print(json.dumps({k:record[k] for k in ['name','result_version','operations']}),flush=True)

def batch(s,key,name,basis):return Batch(s,key,name,basis+' Source design, not field/as-built verification.')
def child(b,parent,name,typ,p,r,role=None):return b.entity(parent+' '+name,typ,p,r,parent,role)
def facts(b,node,p,r,rows):
 for key,value,unit,condition in rows:b.a(node,key,value,p,r,unit,condition)
def drive(t):return t+' Drive assembly'
def scoop(t):return drive(t)+' Scoop coupling PST-570'
def gear(t):return drive(t)+' Gearbox B3-500'
def motor(t):return drive(t)+' Main motor'
def brake(t):return drive(t)+' Thruster brake'
def low(t):return drive(t)+' Low-speed geared coupling RG-12'
def mech(t):return t+' Belt and mechanical assemblies'
def prot(t):return t+' Belt protection devices'

def ga(s,out,t):
 b=batch(s,'ga',t+'-GA','175028 Rev1 approved 14-Dec-2018; both conveyors are explicitly listed')
 r=[.785,.035,.967,.77];dr=[.785,.155,.967,.325];pu=[.785,.38,.967,.468];ir=[.785,.465,.967,.607];pr=[.785,.714,.967,.766]
 b.a(t,'equipment_role','Carry processed coal from crusher house UEE-3 to the elevated UEF-13 transfer, with FG-17/18 selecting a bunker conveyor.',1,FULL)
 D=b.entity(drive(t),'functional_assembly',6,dr,t)
 for node,typ,model in [(motor(t),'electric_motor',None),(scoop(t),'coupling','PST-570'),(gear(t),'gearbox','B3-500'),(low(t),'coupling','RG-12'),(brake(t),'brake_assembly','EBTF-600/G')]:
  b.entity(node,typ,6,dr,D)
  if model:b.a(node,'model_number',model,6,dr)
 facts(b,motor(t),6,dr,[('motor_rated_power',500,'kW',None),('motor_speed',1488,'rpm','GA row printed speed (synch.)'),('motor_voltage',3.3,'kV','±10%'),('motor_supply_frequency',50,'Hz','±5%')])
 b.a(gear(t),'gear_ratio_nominal',28.4,6,dr);b.a(scoop(t),'manufacturer','Premium',6,dr)
 b.rel(D,'located_at',TP,1,[.60,.15,.85,.55]);b.a(D,'location_description','Conveyor head-end drive at TP13; distinct A/B handing is shown.',1,[.60,.15,.85,.55])
 M=b.entity(mech(t),'functional_assembly',6,[.785,.325,.967,.714],t)
 belt=child(b,M,'Conveyor belt','conveyor_belt',6,[.785,.325,.967,.38])
 facts(b,belt,6,[.785,.325,.967,.38],[('belt_width',1400,'mm',None),('belt_length',954.271,'m','Endless length'),('belt_cover_thickness',5,'mm','Top cover'),('belt_cover_thickness',2,'mm','Bottom cover')]);b.a(belt,'assembly_arrangement','NN 2000/5; fire-resistant cover; 1400 mm belt width.',6,[.785,.325,.967,.38])
 for name,typ,qty,diam in [('Head pulley','pulley',1,1000),('Snub pulley','pulley',1,630),('Tail bend and take-up pulley group','functional_assembly',4,800),('Deflector pulley group','pulley',2,219)]:
  node=child(b,M,name,typ,6,pu);facts(b,node,6,pu,[('quantity',qty,'No.','Per conveyor; combined group where stated'),('component_dimension',diam,'mm','Pulley/deflector diameter'),('component_dimension',1600,'mm','Face width')])
  if name!='Deflector pulley group':b.a(node,'component_dimension',2100,6,pu,'mm',condition='Bearing centres')
 b.rel(gear(t),'mechanically_drives',low(t),1,[.60,.15,.85,.55],network='mechanical',condition='Conveyor head drive chain; low-speed coupling between reducer and pulley')
 b.rel(low(t),'mechanically_drives',M+' Head pulley',1,[.60,.15,.85,.55],network='mechanical',condition='Conveyor head-end layout')
 b.a(M+' Head pulley','assembly_arrangement','12 mm rubber lagging, herringbone/diamond groove.',6,pu)
 group=M+' Tail bend and take-up pulley group'
 tail=child(b,group,'Tail pulley','pulley',4,[.06,.1,.36,.57]);b.rel(tail,'located_at','UEE-3',4,[.06,.1,.36,.57])
 take=child(b,M,'Vertical gravity take-up','take_up_assembly',6,[.785,.652,.967,.716]);facts(b,take,6,[.785,.652,.967,.716],[('component_dimension',12100,'mm','Take-up travel; mark-up scale')])
 tp=child(b,group,'Take-up pulley','pulley',6,pu);b.rel(tp,'associated_with',take,6,[.785,.652,.967,.716])
 rope=child(b,take,'Wire rope','mechanical_component',6,[.785,.66,.967,.691]);facts(b,rope,6,[.785,.66,.967,.691],[('component_dimension',32,'mm','Rope diameter'),('minimum_breaking_force',474,'kN',None)]);b.a(rope,'assembly_arrangement','6 x 37, fibre core, grade 1570.',6,[.785,.66,.967,.691])
 cw=child(b,take,'Counterweight','mechanical_component',6,[.785,.691,.967,.716]);facts(b,cw,6,[.785,.691,.967,.716],[('counterweight_mass',14000,'kg','Design total per conveyor'),('quantity',800,'blocks','17.5 kg each')]);b.a(cw,'assembly_arrangement','Cast iron blocks 300 x 260 x 30 mm.',6,[.785,.691,.967,.716])
 for name,qty,arr in [('Transition idlers',4,'2 at 15° plus 2 at 25°'),('Impact idlers',12,'35° trough; 139.7 mm tube, 190 mm roller; 400 mm pitch'),('Carrying idlers',435,'35° trough; 159 mm roller; 1000 mm pitch; 2° forward tilt'),('Self-aligning carrying idlers',32,'15000 mm pitch'),('Return idlers',127,'10° trough; 159 mm roller; 3000 mm pitch'),('Self-aligning return idlers',27,'10° trough; 18000 mm pitch'),('Self-cleaning return idler',1,'Near discharge pulley'),('Nonmagnetic idlers',4,'At metal-detector zone, as GA per-conveyor row'),('Machined weighing idlers',4,'At belt-weigher zone')]:
  node=child(b,M,name,'idler_group',6,ir);b.a(node,'quantity',qty,6,ir,'sets',condition='Per conveyor, GA grouping');b.a(node,'assembly_arrangement',arr,6,ir)
 flat=child(b,M,'Flat return rollers','idler_group',6,ir);b.a(flat,'source_discrepancy','GA flat-return row states 4 but names EBA-6A/6B inside the 18A/B drawing. No per-18 count is inferred from this row; see dedicated idler schedule.',6,ir)
 skirt=child(b,M,'Skirt and deck','mechanical_component',6,[.785,.604,.967,.653]);facts(b,skirt,6,[.785,.604,.967,.653],[('component_dimension',18,'m','Total skirt length'),('component_dimension',20,'mm','Hardox 400 liner'),('component_dimension',10,'mm','Sides/top'),('component_dimension',3,'mm','Continuous deck plate')]);b.a(skirt,'source_discrepancy','Seal-plate thickness appears as 31.5 THK. Do not normalize to 3.15 mm or assert an installed 31.5 mm plate; fabrication revision needed.',6,[.785,.604,.967,.653])
 for name in ['Primary scraper','Secondary scraper','Internal V-plough scraper']:child(b,M,name,'belt_scraper',6,[.785,.696,.967,.729])
 P=b.entity(prot(t),'functional_assembly',6,pr,t)
 for name,typ,qty,unit,spacing in [('PCS','pull_cord_switch_group',16,'pairs',30),('BSS','belt_sway_switch_group',12,'pairs',40),('ZSS','zero_speed_switch',1,'No.',None)]:
  node=child(b,P,name,typ,6,pr);b.a(node,'quantity',qty,6,pr,unit,condition='Per conveyor; preserve original unit');b.rel(node,'protects_equipment',t,6,pr)
  if spacing:
   b.a(node,'device_spacing',spacing,6,pr,'m',condition='Both sides');b.a(node,'individual_device_count',2*qty,6,pr,'switches',condition=f'Derived: {qty} pairs x 2',origin='inferred')
  else:b.rel(node,'located_at',tail,6,pr)
  b.a(node,'source_gap','Individual switch addresses, cable tags and commissioned loop settings need field records.',6,pr)
 # Measurement membership follows physical GA location; control tag mapping is independently sourced later.
 b.finish(out)

def scoop_details(s,out,t):
 b=batch(s,'scoop',t+'-PST570','175058 sheet3 570 PST explicitly lists EBA-18A/B; sheet5 P&I and sheets12–17 control panel apply to 500/530/570/660 family; approved 19-Feb-2019')
 c=scoop(t);r=[.698,.057,.96,.571]
 pump=child(b,c,'Oil circulation pump','oil_circulation_pump',3,r);pm=child(b,pump,'Motor','electric_motor',3,r)
 radiator=child(b,c,'Oil radiator','hydraulic_oil_cooler',3,r);fan=child(b,radiator,'Fan motor','electric_motor',3,r)
 act=child(b,c,'Scoop actuator','electric_actuator',3,r);am=child(b,act,'Dual-speed motor','electric_motor',12,[.1,.3,.73,.68])
 sump=child(b,c,'Oil sump','oil_tank',5,[.13,.20,.71,.79]);su=child(b,c,'Suction strainer','oil_filter',5,[.13,.20,.71,.79]);fi=child(b,c,'Return Y filter','oil_filter',5,[.13,.20,.71,.79])
 valve=child(b,c,'Oil isolation valve','isolation_valve',5,[.13,.20,.71,.79]);fuse=child(b,c,'Fusible plug','mechanical_component',3,r)
 facts(b,pump,3,r,[('rated_flow',150,'L/min','Gear pump with relief valve'),('nominal_pressure',3,'kg/cm2','Pump design discharge')]);facts(b,pm,3,r,[('motor_rated_power',2.2,'kW','3 HP'),('rated_rotational_speed',1415,'rpm',None),('motor_supply_frequency',50,'Hz','3 phase')]);facts(b,fan,3,r,[('motor_rated_power',.55,'kW',None),('rated_rotational_speed',1350,'rpm',None)])
 facts(b,c,3,r,[('lubricant_fill_quantity',270,'L','Coupling oil capacity'),('design_temperature_limit',75,'degC','Maximum oil temperature at 50°C ambient/full load'),('design_absorbed_power',382,'kW','18A/B consumed-power design basis, not motor rating')]);b.a(c,'lubricant_grade','MAK 46 / ENKLO 46 / SERVO SYSTEM 46',3,r)
 b.a(su,'assembly_arrangement','SS304 suction screen 20 mesh.',5,[.72,.05,.965,.20]);b.a(fi,'assembly_arrangement','Return Y-filter 40 mesh; distinct from suction strainer.',5,[.72,.26,.965,.35])
 facts(b,fuse,3,r,[('fusible_plug_blowing_temperature',145,'degC','±5°C')]);facts(b,act,3,r,[('actuator_output_torque',15,'kg-m',None),('component_dimension',45,'deg','Output travel'),('actuator_travel_time',8,'s','Engagement, scoop OUT'),('actuator_travel_time',4,'s','Disengagement, scoop IN')]);b.a(act,'assembly_arrangement','Manual handwheel; 135 ohm/3 W potentiometer; two travel and two torque limits, 2NO+2NC.',3,r)
 facts(b,am,12,[.1,.3,.73,.68],[('motor_rated_power',.1,'kW','Forward, 685 rpm'),('motor_rated_power',.25,'kW','Reverse, 1380 rpm')]);b.a(am,'motor_voltage',415,3,r,'V');b.rel(am,'mechanically_drives',act,3,r,network='mechanical')
 for a,z in [(motor(t),c),(c,gear(t))]:b.rel(a,'mechanically_drives',z,3,[.03,.12,.69,.8],network='mechanical',condition='Conveyor 18 drive chain; input motor side, output gearbox side')
 b.rel(pm,'mechanically_drives',pump,3,r,network='mechanical');b.rel(fan,'mechanically_drives',radiator,3,r,network='mechanical',condition='Radiator fan drive')
 for a,z in [(sump,su),(su,valve),(valve,pump),(pump,radiator),(radiator,fi),(fi,c),(c,sump)]:b.rel(a,'oil_flow_to',z,5,[.13,.20,.71,.79],network='utility',condition='Common model-family P&I oil circulation, not a plant process-material route')
 for code,typ,location,alarm,trip,u,cond in [('FSO','flow_switch','Pump outlet',90,None,'L/min','Flow below; 570/660 row'),('TS1','temperature_switch','Coupling oil inlet',85,None,'degC','Oil above'),('TS2','temperature_switch','Coupling oil outlet',None,110,'degC','Oil above'),('PS','pressure_switch','Coupling oil inlet',.3,None,'bar','Pressure below'),('DPS','differential_pressure_switch','Across return Y-filter',.8,None,'bar','Differential pressure above')]:
  node=child(b,c,code,typ,5,[.72,.355,.968,.97]);b.a(node,'location_description',location,14,[.07,.50,.92,.73])
  if alarm is not None:b.a(node,'alarm_threshold',alarm,5,[.72,.355,.968,.97],u,condition=cond+'; vendor alarm column only')
  if trip is not None:b.a(node,'trip_threshold',trip,5,[.72,.355,.968,.97],u,condition=cond+'; vendor trip column, action target reconciled with control write-up')
  b.rel(node,'monitors_equipment',c,14,[.07,.50,.92,.73]);b.a(node,'control_terminal_description',{'TS1':'TP1-33/34; TP2-69/70','TS2':'TP1-35/36; TP2-71/72','PS':'TP1-37/38; TP2-73/74','DPS':'TP1-39/40; TP2-75/76','FSO':'TP1-41/42; TP2-77/78'}[code],14,[.07,.09,.94,.49],condition='Family panel schematic; field cable mapping not established')
 for name,typ in [('Oil level gauge','level_gauge'),('Oil temperature gauge','temperature_gauge'),('Oil pressure gauge','pressure_gauge')]:child(b,c,name,typ,5,[.13,.20,.71,.79])
 panel=child(b,c,'Control panel','local_control_panel',12,FULL)
 for z in [pm,fan,am]:b.rel(panel,'electrically_feeds',z,12,[.1,.09,.76,.70],network='electrical',condition='Family power circuit; terminals T11–13 pump, T14–16 radiator, T5–10 dual-speed actuator. Upstream plant feeder unverified.')
 b.a(c,'source_discrepancy','Pump GA flow is 150 L/min; P&I normal circulation row for 570/660 is 140 L/min. The 75°C design maximum, 85°C inlet alarm and >110°C outlet trip have different bases; they are not interchangeable settings.',5,[.72,.355,.968,.97])
 b.a(c,'source_gap','500 PST sectional BOM on sheet6 is not a 570-specific bearing/impeller selection. 570 internals and installed maintenance intervals need the matching vendor sectional/O&M record.',3,r)
 b.finish(out)

def drive_aux(s,out):
 b=batch(s,'gear','18AB-B3-500','175056 sheet10 B3-500 explicitly lists 18A/B, fan/holdback/oil pump, approved 14-Dec-2018')
 for t in TAGS:
  g=gear(t);r=[.67,.06,.97,.92]
  facts(b,g,10,r,[('gear_ratio_actual',29.2,None,'(+3%) as printed'),('gearbox_mechanical_power_rating',901,'kW',None),('gearbox_thermal_power_rating',633,'kW','50°C ambient'),('lubricant_fill_quantity',410,'L',None),('equipment_mass',3780,'kg','Without oil')]);b.a(g,'lubricant_grade','ISO VG 320',10,r);b.a(g,'lubrication_method','Splash and pump',10,r)
  for name,typ in [('Shaft-driven unidirectional oil pump','oil_circulation_pump'),('Cooling fan and cowl','fan'),('Sprag holdback','mechanical_component')]:child(b,g,name,typ,10,[.04,.03,.67,.87])
  b.rel(g,'mechanically_drives',g+' Shaft-driven unidirectional oil pump',10,[.04,.03,.67,.87],network='mechanical',condition='Shaft mounted; no separate electric pump motor shown')
  b.a(g,'shaft_handing_rotation','18B: handing 1A, anticlockwise output as drawn; 18A: handing 2, clockwise output referenced to opposite view.',10,r)
  b.a(g,'assembly_arrangement','Gearbox GA gives actual ratio 29.2 (+3%); conveyor GA gives nominal 28.4. Drive schedule independently distinguishes nominal and exact ratio; retain the different bases.',10,r)
  b.a(g,'source_gap','Gearbox internal gear/bearing selections and overhaul intervals are not resolved by the external GA. Two installed units plus one project spare is a supply total, not three per conveyor.',10,r)
 b.finish(out)
 b=batch(s,'geared','18AB-RG12','175059 sheet3 RG-12; 18A/B explicitly in schedule, approved 14-Dec-2018')
 for t in TAGS:
  c=low(t);r=[.04,.04,.97,.96];b.a(c,'lubricant_grade','Servogem II',3,r);b.a(c,'lubricant_fill_quantity',14,3,r,'kg',condition='Per coupling set')
  for name,typ,qty,mat in [('Hubs','mechanical_component',2,'EN8'),('Sleeves','mechanical_component',2,'BS1760 Grade A'),('O-ring seals','mechanical_component',2,'Synthetic rubber'),('Grease plugs','mechanical_component',2,'As BOM'),('End covers','mechanical_component',2,'Mild steel'),('Connecting bolts','mechanical_component',14,'As BOM')]:
   node=child(b,c,name,typ,3,r);b.a(node,'quantity',qty,3,r,'No.',condition='Per RG-12 coupling set');b.a(node,'component_material',mat,3,r)
  b.a(c,'source_gap','GA supplied in pilot-bore state; installed shaft bores, alignment and final coupling selection require installation records. Schedule totals cover several conveyors and spares.',3,r)
 b.finish(out)
 b=batch(s,'brake','18AB-brake','175061 sheet5, 500 kW/1488 rpm, 18A/B schedule printed EAC-18A/B; family applicability is qualified against conveyor18 GA')
 for t in TAGS:
  br=brake(t);r=[.70,.04,.98,.96];thr=child(b,br,'Electrohydraulic thruster','electrohydraulic_thruster',5,r);tm=child(b,thr,'Motor','electric_motor',5,r)
  facts(b,tm,5,r,[('motor_rated_power',.37,'kW',None),('motor_voltage',415,'V','Three phase'),('motor_supply_frequency',50,'Hz',None)]);facts(b,thr,5,r,[('component_dimension',75,'mm','Stroke'),('lubricant_fill_quantity',2.5,'L','Transformer oil IS335 EHV')]);b.a(thr,'model_number','ET3250/TL',5,r)
  for name,typ,qty,mat in [('Brake shoes','mechanical_component',2,'Cast iron'),('Brake liners','mechanical_component',2,'Non-asbestos, 10 mm'),('Main spring','mechanical_component',1,'BOM spring'),('Tie rod and adjusting nuts','mechanical_component',None,'BOM'),('Release limit switch','limit_switch',1,'Jai Balaji 45-18, 2NO+2NC')]:
   node=child(b,br,name,typ,5,[.04,.03,.70,.96]);b.a(node,'assembly_arrangement',mat,5,r)
   if qty:b.a(node,'quantity',qty,5,[.04,.03,.70,.96],'No.',condition='Per brake BOM')
  b.rel(tm,'mechanically_drives',thr,5,r,network='mechanical');b.rel(br,'acts_on',scoop(t),5,FULL,network='mechanical',condition='600 mm drive brake drum; qualified 18-family schedule')
  b.a(br,'source_discrepancy','Conveyor GA specifies EBTF-600/G. Brake sheet5 labels EBTM-600/G and EAC-18A/B, whereas canonical tags are EBA-18A/B. 600 mm and 500 kW/1488 rpm align; installed model/nameplate remains unresolved.',5,r)
 b.finish(out)

def bearings(s,out):
 b=batch(s,'bearing','18AB-pulley-bearings','175062 Rev4, approved 25-Feb-2019; mapping on p2/p3 aligns with the p4/p5 calculation columns, not adjacent conveyors')
 for t in TAGS:
  for node,model,page,r in [(mech(t)+' Head pulley','23156 CCK',4,[.65,.66,.703,.735]),(mech(t)+' Tail bend and take-up pulley group Take-up pulley','23148 CCK',5,[.65,.877,.704,.957]),(mech(t)+' Tail bend and take-up pulley group Tail pulley','23140 CCK',5,[.861,.877,.913,.957]),(mech(t)+' Snub pulley','23140 CCK',5,[.756,.877,.809,.957])]:
   be=child(b,node,'Bearings','bearing',page,r);b.a(be,'model_number',model,page,r,condition='Design calculation selected bearing; exact pulley type mapping on p2/3')
  lock=child(b,mech(t)+' Head pulley','Keyless locking assembly','mechanical_component',4,[.65,.352,.703,.411]);b.a(lock,'model_number','N7016.1, 280 x 355',4,[.65,.352,.703,.411]);b.a(lock,'source_gap','Do not use adjacent catalogue torque rows as the installed tightening procedure. Confirm exact supplied size/manual before maintenance.',4,[.65,.352,.703,.411])
 b.finish(out)

def scrapers(s,out):
 for key,name in [('primary','Primary scraper'),('secondary','Secondary scraper')]:
  b=batch(s,key,'18AB-'+key+'-scrapers','175079/175080 Rev3 sheet1, FIO 27-Oct-2020, explicit 18A and 18B quantity columns')
  for t in TAGS:
   node=mech(t)+' '+name;r=[.45,.58,.96,.76];b.a(node,'model_number','HOSCH B9S',1,r);b.a(node,'quantity',1,1,r,'assembly',condition='Per conveyor; drawing total 2 for 18A and 18B')
   blades=child(b,node,'Polyurethane blade blocks','mechanical_component',1,r);b.a(blades,'quantity',4,1,r,'blocks',condition='Per assembly');b.a(blades,'component_material','Polyurethane 90±5 Shore A',1,r);b.a(blades,'component_dimension',1200,1,[.49,.04,.89,.33],'mm',condition='Cleaning width')
   for n in ['Carrier tube','Left elastomount','Right elastomount','Adjusting spindles']:child(b,node,n,'mechanical_component',1,r)
   b.a(node,'equipment_mass',56,1,[.03,.55,.28,.74],'kg',condition='Assembly weight');b.a(node,'location_description','At conveyor head discharge pulley; mounting cut-outs/brackets shown in sheet1.',1,[.03,.04,.49,.42])
  b.finish(out)
 b=batch(s,'internal','18AB-internal-scrapers','175081 Rev1 approved 07-Jan-2019; IS-14 BOM explicitly includes EBA-18A/B. Later HOSCH internal/external package is limestone/gypsum scope and is excluded.')
 for t in TAGS:
  node=mech(t)+' Internal V-plough scraper';r=[.70,.35,.98,.69];b.a(node,'model_number','IS-14',1,r);b.a(node,'equipment_mass',46.97,1,r,'kg',condition='Per internal scraper assembly')
  blade=child(b,node,'Rubber blade','mechanical_component',1,r);b.a(blade,'component_material','Rubber 60–65 Shore A',1,r);b.a(blade,'component_dimension',25,1,r,'mm',condition='Blade thickness')
  for n in ['Steel V-plough','Blade clamp plates','Pivot/support frame']:child(b,node,n,'mechanical_component',1,r)
 b.finish(out)
 b=batch(s,'idler','18AB-idler-schedule','175060 Rev1 FIO 20-Feb-2019; 18A/B column is a pair schedule. All grouped source quantities stay distinct.')
 for t in TAGS:
  r=[.43,.70,.49,.95];b.a(mech(t)+' Carrying idlers','quantity',431,1,r,'sets',condition='Per conveyor derived from 431+431 in paired 18A/B schedule',origin='inferred');b.a(mech(t)+' Carrying idlers','source_discrepancy','Conveyor GA gives 435 carrying sets per conveyor; dedicated idler schedule gives 431+431 for 18A/B. Final installed quantity needs reconciliation.',1,r)
  b.a(mech(t)+' Flat return rollers','quantity',4,1,r,'rollers',condition='Per conveyor from 4+4 in dedicated 18A/B schedule',origin='inferred');b.a(mech(t)+' Nonmagnetic idlers','source_discrepancy','GA states 4 per conveyor, dedicated schedule gives 2+2 for the 18A/B pair. Preserve both; do not treat project pair total as a per-machine quantity.',1,r)
 b.finish(out)

def gates(s,out):
 b=batch(s,'gate','FG17-18-assemblies','175050 Rev2 sheet1 Type1 applicability schedule explicitly gives FG-17 at18A and FG-18 at18B in UEF-13')
 for t,fg in zip(TAGS,['FG-17','FG-18']):
  r=[.714,.24,.961,.716];b.rel(fg,'located_at',TP,1,r);b.rel(fg,'part_of',t,1,r);b.a(fg,'equipment_role','Select one receiving bunker conveyor from this conveyor discharge.',1,r)
  for n,typ,qty,mat in [('Casing','mechanical_component',1,'20 mm Hardox400'),('Flap','mechanical_component',1,'20 mm Hardox400'),('Flap shaft','mechanical_component',1,'EN8/C40; 135 mm round, 150 mm square'),('Inspection doors','maintenance_access',2,'350 x 450 mm'),('Felt shaft seals','mechanical_component',2,'Felt')]:
   node=child(b,fg,n,typ,1,r);b.a(node,'quantity',qty,1,r,'No.',condition='Per Type1 gate');b.a(node,'assembly_arrangement',mat,1,r)
  be=child(b,fg,'Shaft bearings and housings','bearing',1,r);b.a(be,'quantity',2,1,r,'sets');b.a(be,'assembly_arrangement','SNA530 plummer blocks; SKF22230CCK/W33 + H3130; 2 FRB6.5/270 locating rings.',1,r)
  act=child(b,fg,'Linear actuator','electric_actuator',1,r);am=child(b,act,'Motor','electric_motor',1,r);facts(b,am,1,r,[('motor_rated_power',7.5,'kW',None)])
  b.a(act,'model_number','Prepec P5 Model B',1,r);facts(b,act,1,r,[('actuator_thrust',5600,'kg','Source unit retained'),('component_dimension',650,'mm','Stroke; adjustable 100 mm each end'),('linear_speed',30,'mm/s',None)]);b.a(act,'assembly_arrangement','Trunnion mounting; removable 500 mm handwheel; travel and thrust limit switches; electrical handwheel interlock.',1,r)
  for n in ['Travel limit switches','Thrust limit switches','Handwheel electrical interlock']:child(b,act,n,'limit_switch',1,r)
  b.rel(am,'mechanically_drives',act,1,r,network='mechanical');b.rel(act,'mechanically_drives',fg+' Flap shaft',1,r,network='mechanical');b.rel(fg+' Flap shaft','mechanically_drives',fg+' Flap',1,r,network='mechanical');b.a(fg,'component_dimension',60,1,[.04,.04,.71,.83],'deg',condition='Flap angular travel')
 b.finish(out)

def measurements(s,out):
 b=batch(s,'md','QB3-4-assemblies','175070 Rev1 FIO 14-Nov-2019; p4 explicitly18A/B; p8 electronics SQTA; p2 marker; wiring pp11–14. Tag mapping preserved from control write-up.')
 for t,q in zip(TAGS,['QB-3','QB-4']):
  b.rel(q,'part_of',t,4,[.06,.5,.61,.68]);b.a(q,'equipment_role','Detect tramp metal on this belt and initiate corresponding conveyor stop; marker identifies removal point.',4,[.06,.5,.61,.68])
  probe=child(b,q,'Tandem probe','metal_detector_probe',4,FULL);b.a(probe,'manufacturer','Elektromag',4,FULL);facts(b,probe,4,[.06,.5,.61,.68],[('component_dimension',1400,'mm','Belt width'),('component_dimension',400,'mm','Aperture height'),('component_dimension',300,'mm','Maximum burden depth'),('belt_speed',2.6,'m/s','Detector GA design speed')]);b.a(probe,'detection_requirement','M30 mild-steel nut lying on the belt (p4); not a proven detection guarantee at every burial depth.',4,[.06,.5,.61,.68])
  b.a(q,'source_discrepancy','Detector GA design speed 2.6 m/s differs from conveyor18 GA 2.7 m/s. Compliance review also requests small ferrous/nonferrous pieces. Field sensitivity tests/final vendor approval are required.',4,[.06,.5,.61,.68])
  el=child(b,q,'Electronic unit SQTA','local_control_panel',8,FULL);b.a(el,'ingress_protection','IP65',8,[.42,.57,.72,.76]);b.a(el,'power_consumption',15,8,[.42,.57,.72,.76],'VA')
  for n,typ,p,r in [('Sandbag marker','mechanical_component',2,FULL),('Marker interlock switch','limit_switch',2,FULL),('Local start reset and indication panel','local_control_panel',11,FULL),('Hooter and metal lamp','alarm_device',11,FULL)]:child(b,q,n,typ,p,r)
  b.rel(probe,'control_signal_to',el,4,[.07,.08,.95,.50],network='control',condition='Probe cable to electronics');b.rel(el,'control_signal_to',q+' Sandbag marker',11,FULL,network='control',condition='Metal indication relay initiates marker drop')
  b.a(q,'source_discrepancy','DCS IO table p12 maps ON T25/26, fault T22/23/24 and metal T27/28; wiring p11 labels relays differently. No definitive field terminal mapping is inferred.',12,FULL)
  b.a(q,'source_gap','Support height is explicitly determined at site. Sensitivity, serial numbers, field cable lengths and final IP protection of hooter remain unresolved.',4,FULL)
 b.finish(out)
 b=batch(s,'md_manual','QB3-4-maintenance','MS08/85 SQ/SQTA manual version05.2010 applies by SQTA electronics identity; manufacturer guidance, not a commissioned interval or field procedure approval')
 for q in ['QB-3','QB-4']:
  b.a(q,'maintenance_requirement','Manufacturer function-control S2 test guidance: once every two to six weeks depending on operating conditions; repeat sensitivity/self-control review after conveyor repairs/modifications.',16,[.52,.05,.94,.23]);b.a(q,'operating_requirement','Manual distinguishes S5 Operation versus Test (relay does not respond in Test). S6 offers normally relaxed or normally activated metal relay, with different power-failure behavior; installed selection must be checked.',16,[.52,.23,.94,.70])
 b.finish(out)
 b=batch(s,'bw','EAT3-4-assemblies','175069 Rev1 FIO27-Feb-2019; p1 explicitly includes18A/B in 1400 mm 10-14-4 group; pp2–6 integrator/JB/speed/wiring')
 for t,e in zip(TAGS,['EAT-3','EAT-4']):
  b.rel(e,'part_of',t,1,FULL);b.a(e,'model_number','Thermo Ramsey 10-14-4',1,FULL);facts(b,e,1,FULL,[('rated_capacity',1375,'t/h','Design flow'),('belt_speed',2.7,'m/s',None),('measurement_accuracy',.25,'%','±0.25%; weigh range20–120%')])
  b.a(e,'equipment_role','Measure belt loading and speed, integrate coal flow and total tonnage; separate from belt protection zero-speed switch.',1,FULL)
  bridge=child(b,e,'Four-idler weighbridge','belt_weighbridge',1,FULL);cells=child(b,bridge,'Load cells','load_cell_group',5,[.05,.09,.40,.61]);b.a(cells,'quantity',4,5,[.05,.09,.40,.61],'cells',condition='LC1–LC4 in applicable field wiring')
  jb=child(b,e,'Load-cell summing junction box','junction_box',3,FULL);b.a(jb,'ingress_protection','IP65',3,[.05,.68,.54,.84]);integr=child(b,e,'Micro-Tech9101 integrator','local_control_panel',2,FULL);b.a(integr,'ingress_protection','IP66 / NEMA4X',2,[.56,.10,.90,.28])
  speed=child(b,e,'Speed sensor60-12C','speed_sensor',4,FULL);b.rel(speed,'located_at',mech(t)+' Tail bend and take-up pulley group Tail pulley',4,[.05,.71,.51,.90]);b.a(speed,'assembly_arrangement','Tail-pulley shaft driven; restraint arm and spring; do not mount rigidly.',4,[.05,.71,.51,.90])
  meter=child(b,e,'Local rate meter and totalizer','local_control_panel',6,FULL);test=child(b,e,'Calibration test-weight arrangement','mechanical_component',1,FULL)
  for a,z in [(cells,jb),(jb,integr),(speed,integr),(integr,meter)]:b.rel(a,'measurement_signal_to',z,5,FULL,network='control',condition='10-14-4 with9101 and60-12C field wiring')
  b.rel(integr,'control_signal_to','CHP Main Control Room DCS',5,[.43,.27,.77,.46],network='control',condition='Flow analog output J10; ON/totalizer pulse/fault digital contacts J7. Field loop IDs unresolved.')
  b.a(integr,'supply_requirement','100–240 VAC field-mount power input; 50–60 Hz. Circuit does not identify a particular plant feeder.',5,[.78,.08,.94,.25]);b.a(e,'maintenance_requirement','Vendor calibration note p7 requires empty running belt for zero and regular calibration according to system needs; weekly/monthly examples are not an installed interval.',7,None,quote='Belt Scale (Micro Tech ) shall be calibrated regularly')
  b.a(e,'source_gap','Drawing group totals of8 units cover several conveyor pairs, not8 per18 conveyor. Installed calibration results, load-cell serials and weighed-idler alignment require records.',1,FULL)
 b.finish(out)
 b=batch(s,'bw_manual','EAT3-4-maintenance','Included Thermo belt-scale manual REC3962 RevD, pp99–101; recommendation only, applied to project10-14-4 weighing family')
 for e in ['EAT-3','EAT-4']:
  b.a(e,'maintenance_requirement','Before calibration inspect wedged material/build-up, verify scale-zone alignment after conveyor work and weigh span on both sides; run the belt at least30 minutes before calibration.',100,None,quote='Routine inspection of the following points should be conducted')
  b.a(e,'maintenance_requirement','Manufacturer recommends zero checks every other day and weekly calibration checks initially, extending by observed accuracy. Weigh-idler grease once/twice yearly can change tare; zero calibration after greasing. This is vendor guidance, not the plant schedule.',101,None,quote='It is recommended that zero be checked every other day')
 b.finish(out)

def transfer(s,out):
 b=batch(s,'tp','TP13-place','175047 Rev3 approved18-Dec-2018; GA floors/layout, sampling/access detail expansion deferredB37')
 b.a(TP,'equipment_role','Elevated transfer of conveyor18A/B discharges through FG17/18 to conveyor19A or19B, with local utilities and drainage.',2,FULL)
 b.a(TP,'location_description','Conveyor18 head/drive level TOC+68.000m; conveyor19 tail level TOC+52.000m; datums follow GA.',2,FULL)
 for t,e,q,g in zip(TAGS,['EAT-3','EAT-4'],['QB-3','QB-4'],['FG-17','FG-18']):
  dis=child(b,t,'Discharge chute interface','chute_interface',2,FULL);b.rel(dis,'located_at',TP,2,FULL);b.rel(t,'associated_with',dis,2,FULL);b.rel(dis,'associated_with',g,2,FULL)
  b.a(e,'location_description','Belt-weigher zone on incoming conveyor18 gallery; not placed on TP13 floor merely because it serves this section.',2,FULL)
 b.a(TP,'source_gap','Existing sampling/elevator identities and sampling material branches are preserved. B37 must resolve SNC-2/elevator identity, sample return and access expansion separately.',2,FULL)
 b.finish(out)

def dfds(s,out):
 b=batch(s,'dfds','TP13-DFDS-network','175073 sheet2 DFDS System2 P&ID; local TP13 AP11–16 topology; same bare numbers in System1 are different namespaces')
 r=[.65,.30,.98,.63];local=child(b,TP,'Local DFDS','dfds_system',2,r);b.rel('DFDS System-2','serves_equipment',local,2,FULL)
 inlet=child(b,local,'Air and water inlet from UEE-3','utility_header',2,r);b.rel('DFDS System-2','utility_supply_to',inlet,2,FULL,network='utility',condition='Shared System2 supply passes through UEE-3; no ownership of shared pumps/compressors transferred to TP13')
 b.rel('UEE-3 Local DFDS Air and water connection','utility_supply_to',inlet,2,r,network='utility',condition='P&ID distribution continuation into TP13')
 ar=child(b,local,'Air receiver200L','air_receiver',2,r);b.a(ar,'rated_capacity',200,2,r,'L');b.rel(inlet,'utility_supply_to',ar,2,r,network='utility',condition='Air50NB branch; water bypasses receiver')
 panel=child(b,local,'LCP-03','local_control_panel',2,r);ps='DFDSS-2 PS-03';b.rel(ps,'part_of',local,2,r);b.rel(ps,'located_at',TP,2,r)
 for code,t in [('05','EBA-18A'),('06','EBA-18B')]:
  ub=child(b,local,'UBS-'+code+' on '+t,'under_belt_switch',2,r);b.rel(ub,'located_at',t,2,r);b.rel(ub,'control_signal_to',panel,2,r,network='control',condition='Running-with-load detection per P&ID')
 for n,t,count,role in [('11','EBA-18A',4,'Discharge18A'),('12','EBA-19A',9,'Receiving19A from18A branch in P&ID'),('13','EBA-19B',9,'Receiving19B from18A branch in P&ID'),('14','EBA-18B',4,'Discharge18B'),('15','EBA-19A',9,'Receiving19A from18B branch in P&ID'),('16','EBA-19B',9,'Receiving19B from18B branch in P&ID')]:
  fas='UEF-13 FAS-'+n;pru='UEF-13 PRU-'+n
  for node in [fas,pru]:b.rel(node,'part_of',local,2,r);b.rel(node,'located_at',TP,2,r)
  ap=child(b,local,'AP-'+n,'spray_application_point',2,r,role)
  no=child(b,ap,'Nozzle group','spray_nozzle_group',2,r);b.a(no,'quantity',count,2,r,'nozzles',condition='Per AP total/operating design count; not44 simultaneous')
  b.rel(ap,'sprays_at',t,2,r,condition='P&ID-design receiving/discharge branch; later piping labels have unresolved inconsistencies')
  b.rel(inlet,'utility_supply_to',fas,2,r,network='utility',condition='Separate air/water lines20NBair15NBwater');b.rel(fas,'utility_supply_to',pru,2,r,network='utility',condition='Air and water solenoids');b.rel(panel,'control_signal_to',fas,2,r,network='control',condition='Local control of FAS air/water solenoids')
  for medium in ['Air','Water']:
   hd=child(b,ap,medium+' header','spray_header',2,r);b.rel(pru,'utility_supply_to',hd,2,r,network='utility',condition=medium);b.rel(hd,'utility_supply_to',no,2,r,network='utility',condition=medium+' to atomizing nozzle group')
 b.a(local,'source_discrepancy','P&ID/operation philosophy maps12/13 to18A and15/16 to18B; piping view4-4 labels FAS12 to18B and FAS15 to18A. Piping view3-3 labels PRU13 destination19A although P&ID AP13 serves19B. These design associations are qualified, not installed routing confirmation.',2,r)
 b.finish(out)
 b=batch(s,'piping','TP13-water-and-layout','175300 Rev3 FIO18-Oct-2019, local piping plan/views; retain cross-reference contradictions')
 local=TP+' Local DFDS';r=[.54,.05,.78,.83]
 b.a(local+' Air receiver200L','rated_capacity',200,1,r,'L');b.a(local+' Air and water inlet from UEE-3','assembly_arrangement','50NB main air,15NB main water; FAS branches20NB air/15NB water.',1,r)
 water=child(b,TP,'Service and drinking water','functional_assembly',1,FULL)
 sw=child(b,water,'Service-water riser and hose points','utility_header',1,FULL);pw=child(b,water,'Drinking-water riser','utility_header',1,FULL);tank=child(b,water,'Roof potable-water tank','water_tank',1,FULL)
 b.a(tank,'rated_capacity',300,1,FULL,'L',condition='Roof tank');b.rel('CHP Potable Water System','utility_supply_to',pw,1,FULL,network='utility',condition='Drawing boundary to PW riser; pump-specific mapping not established');b.rel(pw,'utility_supply_to',tank,1,FULL,network='utility')
 b.rel('CHP Service Water System-2','serves_equipment',sw,1,FULL,condition='Shared service-water system identity retained; final individual feeder/isolation tags unverified');b.a(sw,'assembly_arrangement','32NB globe valve and quick-release hose tapping detail; source depicts local floor/ground hose points.',1,r)
 b.a(water,'source_gap','Shared potable-pump PWP-1/PWP-2 name disagreement is outside this local boundary. Source does not establish commissioned isolation/tag/feeder mapping.',1,FULL)
 b.a(local,'source_discrepancy','Piping drawing view4-4 prints upstream conveyor18 labels on FAS12/15 while plan and P&ID place them on receiving19A. View3-3 PRU13 has19A text at a19B level. Keep the exact drawing for reconciliation.',1,r)
 b.finish(out)
 b=batch(s,'fas','TP13-FAS-PRU-internals','175095 Rev1 FIO18-Feb-2019, project standard FAS and PRU assemblies; paired identities established by local P&ID')
 for n in map(str,range(11,17)):
  fas='UEF-13 FAS-'+n;pru='UEF-13 PRU-'+n
  for name,typ,arr in [('Air solenoid valve','solenoid_valve','20NB normally closed'),('Water solenoid valve','solenoid_valve','15NB normally closed'),('Air filter','air_filter','3/4 inch'),('Water Y-strainer','strainer','15NB')]:
   node=child(b,fas,name,typ,2,[.238,.783,.493,.956]);b.a(node,'assembly_arrangement',arr,2,[.238,.783,.493,.956]);b.a(node,'quantity',1,2,[.238,.783,.493,.956],'No.',condition='Per standard FAS')
  for name,arr in [('Air regulator','20NB, relieving SR13'),('Water regulator','15NB, non-relieving SR13')]:
   node=child(b,pru,name,'pressure_regulator',3,[.037,.745,.66,.95]);b.a(node,'assembly_arrangement',arr+'; Shavo Norgren; pressure gauge provided.',3,[.037,.745,.66,.95]);child(b,node,'Pressure gauge','pressure_gauge',3,[.037,.745,.66,.95])
 b.finish(out)
 b=batch(s,'header','TP13-spray-headers','175305 Rev0 standard4-outlet discharge p1 and9-outlet receipt p2 applied by AP nozzle counts')
 for n in map(str,range(11,17)):
  page=1 if n in ['11','14'] else 2
  for medium,nb in [('Air',20),('Water',15)]:
   node=TP+' Local DFDS AP-'+n+' '+medium+' header';r=[.02,.06,.86,.98];b.a(node,'component_dimension',410 if page==1 else 760,page,r,'mm',condition='Standard header length');b.a(node,'component_dimension',nb,page,r,'NB',condition=medium+' pipe');b.a(node,'component_material','ASTM A53 GradeB Schedule40',page,r)
 b.finish(out)
 b=batch(s,'nozzle','TP13-nozzle-design','175097 Rev1 sheet2 System2 nozzle specification; quantities remain on individual AP P&ID')
 for n in map(str,range(11,17)):
  node=TP+' Local DFDS AP-'+n+' Nozzle group';r=[.055,.226,.947,.528];facts(b,node,2,r,[('rated_flow',.15,'L/min','Water per nozzle'),('nominal_pressure',1,'bar','Water required'),('rated_flow',3.5,'CFM','Air per nozzle'),('nominal_pressure',5,'bar','Air required')]);b.a(node,'manufacturer','Lechler Germany',2,r);b.a(node,'component_material','SS316;1/4 inch BSPP female',2,r)
 b.finish(out)

def sump(s,out):
 b=batch(s,'sump_pid','TP13-drainage-network','175259 Rev3 P&ID; UEF13 sump SP2A/B65NB branch discharges into intermediate sump near UEF1, not directly to LHP pond')
 group='UEF-13 Sump Pumps SP-2A/2B';r=[.60,.07,.72,.23]
 b.rel(group,'part_of',TP,1,r);b.rel(group,'located_at',TP,1,r)
 pit=child(b,group,'Sump pit','water_tank',1,r);b.a(pit,'rated_capacity',5,1,r,'m3');b.a(pit,'assembly_arrangement','2.0L x1.5W x1.7H metres as printed.',1,r)
 inter=b.entity('CHP Intermediate sump near UEF-1','water_tank',1,[.15,.79,.36,.96]);b.a(inter,'rated_capacity',30,1,[.15,.79,.36,.96],'m3');b.rel(inter,'located_at','UEF-1',1,[.15,.79,.36,.96])
 b.rel(inter,'utility_supply_to','UEF-1 Sump Pumps SP-4A/4B',1,[.15,.79,.36,.96],network='utility',condition='Intermediate drainage collection sump; downstream pump group existing canonical identity')
 for n in ['2A','2B']:
  node=child(b,group,'SP-'+n,'pump',1,r);b.rel(pit,'water_flow_to',node,1,r,network='utility',condition='Bottom suction from UEF13 pit');b.rel(node,'water_flow_to',inter,1,FULL,network='utility',condition='Shared65NB discharge branch to intermediate collection sump; does not transfer ownership')
 b.a(group,'assembly_arrangement','One working plus one standby; selected status not live.',1,[.84,.37,.97,.57])
 b.a(pit,'source_discrepancy','P&ID UEF13 annotation still shows5 m3 and2.0 x1.5 x1.7 m; review p2 requests5 m3 ->10 m3 per DBR24-Aug-2019 and vendor replies Revised. The depicted pit and revision response disagree; final civil/as-built pit drawing needed.',2,None,quote='revise the sump pit size - 5m3 to 10m3')
 lcp=child(b,group,'Local control panel','local_control_panel',1,r);ls=child(b,pit,'Level switches','level_switch_group',1,r)
 b.rel(ls,'control_signal_to',lcp,1,r,network='control',condition='Local sump-level control; commissioned level settings unverified')
 for n in ['2A','2B']:b.rel(lcp,'control_signal_to',group+' SP-'+n,1,r,network='control',condition='Working/standby local pump control; duty selector not live')
 b.finish(out)
 b=batch(s,'sump','SP2AB-detailed-pumps','Flowmore SALE19094272-50 pp9–14 explicitly SP2A/B at UEF13; pp12–14 have suffix50, excluded similar suffix10 group')
 for n in ['2A','2B']:
  node=group+' SP-'+n;r=[.04,.15,.96,.94];b.a(node,'model_number','F5614H AWS(S.O)-40x25',9,r);b.a(node,'manufacturer','Flowmore Limited',9,r)
  facts(b,node,9,r,[('flow_capacity',10,'m3/h',None),('pump_head',54,'m',None),('rated_rotational_speed',2910,'rpm',None),('shutoff_head',59,'m','Design'),('pump_input_power',4.56,'kW','SG1.10'),('pump_efficiency',35.5,'%',None)]);b.a(node,'assembly_arrangement','Single-stage vertical sump pump; semi-open impeller; bottom suction/top discharge; counterclockwise looking from top; gland packing.',9,r)
  mot=child(b,node,'Motor','electric_motor',10,[.04,.33,.96,.71]);facts(b,mot,10,[.04,.33,.96,.71],[('motor_rated_power',7.5,'kW',None),('rated_rotational_speed',2910,'rpm',None),('motor_voltage',415,'V','Threephase±10%'),('motor_supply_frequency',50,'Hz','±5%')]);b.a(mot,'manufacturer','ABB',10,[.04,.33,.96,.71]);b.a(mot,'model_number','M2BAX132SB2',10,[.04,.33,.96,.71]);b.a(mot,'ingress_protection','IP55',10,[.04,.33,.96,.71]);b.a(mot,'insulation_class','F, temperature rise limited toB',10,[.04,.33,.96,.71])
  for name,typ,mat in [('Semi-open impeller','mechanical_component','2.5%NiCI350BHN'),('Volute casing','mechanical_component','2.5%NiCI350BHN'),('Suction strainer','strainer','GalvanizedMS'),('Gland packing','mechanical_component','Non-asbestos packing'),('Shaft and sleeves','mechanical_component','EN8 shaft; SS410 sleeves'),('Column rubber bushes','bearing','Cutless rubber'),('Flexible coupling','coupling','Lovejoy coupling'),('Self-water lubrication line','utility_header','Self-water lube branch')]:
   sub=child(b,node,name,typ,13,[.48,.06,.96,.72]);b.a(sub,'component_material',mat,13,[.48,.06,.96,.72])
  stand=child(b,node,'Thrust stand','functional_assembly',14,FULL)
  for name,typ,model,qty in [('Angular-contact bearing','bearing','7311',1),('Ball bearing','bearing','6011',1),('Non-reverse ratchet pins','mechanical_component','Case-hardenedCS',3),('Oil level indicator','level_gauge','Steel/glass',1),('Oil fill and drain plugs','mechanical_component','BOM',None)]:
   sub=child(b,stand,name,typ,14,[.5,.12,.96,.74]);b.a(sub,'model_number',model,14,[.5,.12,.96,.74]);
   if qty:b.a(sub,'quantity',qty,14,[.5,.12,.96,.74],'No.',condition='Per pump thrust stand')
  b.rel(mot,'mechanically_drives',node+' Flexible coupling',13,FULL,network='mechanical');b.rel(node+' Flexible coupling','mechanically_drives',node+' Shaft and sleeves',13,FULL,network='mechanical');b.rel(node+' Shaft and sleeves','mechanically_drives',node+' Semi-open impeller',13,FULL,network='mechanical');b.rel(node+' Self-water lubrication line','utility_supply_to',node+' Column rubber bushes',13,FULL,network='utility')
  b.a(node,'lubrication_method','Datasheet Grease/Oil; sectional self-water line lubricates column bushes, thrust stand has oil fill/level/drain. Distinct lubrication points.',9,r)
  b.a(node,'maximum_particle_size',15,10,[.04,.15,.96,.33],'mm');b.a(node,'operating_range','50–150% duty flow',10,[.04,.15,.96,.33]);b.a(node,'source_gap','Installed seal clearances, oil grade/fill, maintenance interval, local isolation and field loop tags need matching O&M/installation records.',14,FULL)
 b.finish(out)

def controls(s,out):
 # These pages were read as original extracted text. Exact quotes anchor evidence;
 # no image review IDs are claimed for text-only pages.
 b=batch(s,'control','18AB-component-control','Control write-up Rev04 approved on condition06-Apr-2020; requirements, not executable or commissioned logic')
 for t,q,e,g in zip(TAGS,['QB-3','QB-4'],['EAT-3','EAT-4'],['FG-17','FG-18']):
  c=scoop(t);act=c+' Scoop actuator';pump=c+' Oil circulation pump';fan=c+' Oil radiator Fan motor'
  b.rel(q,'monitors_equipment',t,17,None,quote='metal detector');b.rel(e,'monitors_equipment',t,18,None,quote='Belt weigher')
  b.a(q,'trip_condition','Metal detected: hooter and corresponding conveyor trip; restart only after local reset and marker restored.',17,None,quote='metal is detected');b.rel(q,'control_signal_to',act,29,None,quote='Metal is detected',network='control',condition='Metal detected causes corresponding scoop to disengage IN; path-table running permissive is separately recorded')
  b.a(q,'control_timer_delay',600,17,None,'s',condition='Detector off delay following corresponding conveyor stop',quote='600');b.a(e,'start_permissive','Electrical healthy; belt weigher runs before its corresponding conveyor.',18,None,quote='Belt weigher')
  b.a(t,'sequence_logic','Radiator feedback -> oil pump -> mainHT motor -> brake released -> scoop OUT; normal stop scoopIN -> brake -> main motor -> oil pump -> radiator.',26,None,quote='Radiator')
  b.a(motor(t),'start_permissive','All winding temperatures<120°C AND DE/NDE bearings<70°C AND electrical healthy AND local stop reset.',27,None,quote='120');b.a(motor(t),'trip_condition','Any winding>130°C OR bearing>80°C OR electrical trip OR local stop.',27,None,quote='130')
  b.a(pump,'start_permissive','Radiator ON AND oil temperature normal AND local stop reset AND electrical healthy.',28,None,quote='Radiator');b.a(pump,'trip_condition','Highoil temperature OR main conveyor motorOFF after300s OR oil flow unhealthy after10s OR electrical trip.',28,None,quote='300');b.a(pump,'control_timer_delay',30,28,None,'s',condition='Normal offcommand delay, adjustable; distinct from300s trip delay',quote='30')
  b.a(act,'start_permissive','Own oil pump ON AND own main motor ON AND both CBS not operated AND PCS not operated AND BSS not operated AND electrical healthy AND brake released AND succeeding conveyor main motor ON AND scoop engaged AND gate in position AND local stop reset. Other feeding gate can move only with its upstream stopped. Path-specific measurement logic is recorded separately.',28,None,quote='Scoop');b.a(act,'source_discrepancy','CBS permissive says both not operated; trip wording also says CBS not operated. Polarity remains unresolved. Vendor DPS gives alarm only; general control-write-up differential-pressure wording needs action-target reconciliation.',28,None,quote='CBS')
  for name,page,quote,condition in [('PCS',28,'PCS','PCS operated -> scoopIN'),('BSS',28,'BSS','BSS operated -> scoopIN'),('ZSS',29,'ZSS','ZSS operated after60s ondelay -> scoopIN')]:b.rel(prot(t)+' '+name,'control_signal_to',act,page,None,quote=quote,network='control',condition=condition)
  b.a(prot(t)+' ZSS','trip_threshold',85,9,None,'% rated belt speed',condition='General requirement speedbelow85%; separate60s actuator-delay source',quote='85');b.a(prot(t)+' ZSS','control_timer_delay',60,29,None,'s',condition='Source ondelay for scoopIN',quote='60')
  b.a(g,'start_permissive','Direction-specific MCC healthy AND travel-end limit reset AND torque limit reset AND local stop reset AND (feeding conveyor NOT ON OR bypass selected). FG17/18 are outside the stated FG19–22 bunker exception.',12,None,quote='Forward Travel')
  b.a(g,'source_discrepancy','Gate control text p12 gives approximately 2 min anti-jam reversal; p13 gives conveyor-off T1=10 s/return T2=5 s and feeding-conveyor-off T1=4 h/return T2=120 s. The modes and conflicting requirements are retained without a commissioned timer selection.',12,None,quote='flap gate')
  b.a(g,'sequence_logic','Conveyor-off anti-jam: after T1=10 s, (OFF duration AND reverse position) -> forward, OR (OFF duration AND forward position) -> reverse; return after T2=5 s. Feeding-conveyor-off periodic variant uses T1=4 h and T2=120 s. This does not resolve the p12 approximately 2 min requirement.',13,None,quote='Logic In Case of Conveyor Trip')
  b.a(g+' Linear actuator','trip_condition','Direction-specific MCC disturbed OR travel end limit operated OR torque limit operated OR local stop operated -> actuator drive trip.',13,None,quote='Forward Travel')
  b.a(act,'path_permissive_logic',f'{e} running AND {q} running AND (({g} REV AND EBA-19A running) OR ({g} FWD AND EBA-19B running)), in addition to general own-drive permissives.',39,None,quote='18A' if t.endswith('A') else '18B',condition='Path2/3/4 table; design requirement')
  for node,target,cond in [(fan,pump,'Radiator ON'),(pump,act,'Oil pump ON'),(brake(t),act,'Brake released'),(motor(t),act,'Own motor ON'),(e,act,'Corresponding weigher running')]:b.rel(node,'control_signal_to',target,28 if node!=e else 39,None,quote='Scoop' if node!=e else('18A' if t.endswith('A') else '18B'),network='control',condition=cond)
 # Reuse already accepted FG17/18 coal routes (REV19A/FWD19B), do not add aggregate bypass edges.
 b.a('UEF-13 Sump Pumps SP-2A/2B','operating_requirement','Automatic start/stop from sump-level switches via local panel; local manual available; either pump can be auto standby. Source low-level annunciation: minimum500 mm above sump bottom; high level:300 mm below top. These are requirements, not commissioned setpoints or current duty.',26,None,quote='Sump')
 b.finish(out)
 b=batch(s,'philosophy','TP13-DFDS-controls','DFDS operation philosophy Rev2 FIO14-Jan-2019 System2 pp23–25; compare localP&ID and piping, not System1 tagnamespace')
 for n in map(str,range(11,17)):
  page=23 if n=='11' else 25 if n=='16' else 24;fas='UEF-13 FAS-'+n;lane='EBA-18A' if int(n)<14 else 'EBA-18B';gate='FG-17' if int(n)<14 else 'FG-18'
  b.a(fas,'start_permissive',f'AUTO AND System2 PS03 airHEALTHY AND {lane} runningwithload'+(f' AND {gate} position signal' if n not in ['11','14'] else '')+'. MANUAL energization follows selector. Gate polarity is not specified here.',page,None,quote='FAS- '+n)
  b.a(fas,'source_gap','Commissioned selector/interlock wiring and final receiving branch are unresolved; do not execute this descriptive Boolean as field logic.',page,None,quote='FAS- '+n)
 b.finish(out)

def supplementary(s,out):
 b=batch(s,'drive','18AB-drive-schedule','175107 Rev2 FIO14-Dec-2018; EAC18A/18B column is independently matched to EBA18 GA through500kW/B3-500/PST570/RG12; tag-prefix discrepancy retained')
 r=[.873,.189,.932,.861]
 for t in TAGS:
  b.a(motor(t),'manufacturer','BHEL',2,r);b.a(motor(t),'motor_pole_count',4,2,r)
  b.a(gear(t),'gear_ratio_nominal',28.4,2,r);b.a(gear(t),'gear_ratio_actual',29.2,2,r,condition='Exact ratio, explicitly distinguished from nominal28.4')
  b.a(gear(t),'gearbox_thermal_power_rating',905,2,r,'kW',condition='Drive schedule; ambient basis not specified in table')
  b.a(gear(t),'source_discrepancy','Drive schedule thermal rating905 kW differs from gearbox GA633 kW at50°C. Nominal28.4 versus exact29.2 is a documented distinction, not itself a conflict. Verify thermal selection/ambient derating and installed nameplate.',2,r)
  b.a(brake(t),'brake_rated_torque',495,2,r,'kg-m',condition='Schedule design torque; not an installed adjustment or holding-test result')
  b.a(drive(t),'source_discrepancy','Drive schedule uses EAC18A/18B rather than EBA18A/18B; electrical tolerance ±6% and frequency+3%/-5% differ from conveyor GA±10% and±5%. Component sizes align; installed motor record needed.',2,r)
 b.finish(out)
 b=batch(s,'calc','18AB-calculation-bases','175231 Rev3 approved23-Nov-2018, pp112–121 explicit EBA18AB; calculation inputs/results kept separate from equipment GA and measured performance')
 for t in TAGS:
  b.a(t,'calculated_profile_length',472.184,112,[.027,.145,.969,.492],'m',condition='Calculation input; GA profile471.943 m')
  b.a(mech(t)+' Skirt and deck','source_discrepancy','Calculation input skirt length10 m differs from GA total18 m; confirm design revision and the skirting-length basis used in resistance calculation.',112,[.027,.145,.969,.492])
  b.a(mech(t)+' Deflector pulley group','source_discrepancy','Calculation inputs p113 give one deflector with243 mm external diameter; GA gives two219 mm deflector rollers. Quantity/revision and bare-versus-external-diameter basis require reconciliation.',113,FULL)
  b.a(t,'calculated_drive_power',368,121,[.027,.711,.969,.857],'kW',condition='Absorbed pulley power at design capacity; not500kW installed motor rating')
  b.a(motor(t),'calculated_required_power',470,121,[.027,.711,.969,.857],'kW',condition='Design factor applied; source separately selects500kW')
  b.a(t,'source_discrepancy','Calculation profile472.184 m differs from GA471.943 m; calculated motor-shaft power392 kW differs from coupling consumed-power basis382 kW. Keep source-qualified calculation/selection values.',121,[.027,.711,.969,.857])
 b.finish(out)
 b=batch(s,'switch','18AB-protection-design-details','178803 project PCS/BSS/ZSS supplier package; family design details apply to documented conveyor protection functions, not confirmation of installed addresses or panel assignment')
 for t in TAGS:
  pcs=prot(t)+' PCS';bs=prot(t)+' BSS';zs=prot(t)+' ZSS'
  b.a(pcs,'assembly_arrangement','Project addressable design SW-4030HAS122: IP66, bidirectional pull, manual hand reset,2NO+2NC, BW7011C sensor module. Per-device family detail; pair quantities remain on GA.',3,[.04,.61,.974,.956],condition='Supplier project family; installed device model/address unverified')
  b.a(bs,'assembly_arrangement','Project addressable design SW-4021HS122: IP66, self-reset, two cams10°/20° from normal,1NO+1NC per cam, prelubricated shaft ball bearings, BW7011C module. Cam angles are mechanical actuation, not field alarm/trip selection.',4,[.04,.30,.974,.956],condition='Supplier project family; installed cam/loop mapping unverified')
  b.a(zs,'assembly_arrangement','Project electronic-speed-switch design: IP65 monitoring unit and IP67 probe; nominal30 mm/effective18 mm sensing distance;12VDC probe. Separate from60-12C belt-weigher sensor.',2,[.04,.45,.95,.71],condition='Supplier project family; final installed model/speed setting unverified')
  b.a(prot(t),'source_gap','Supplier package pp5–25 contains group panels/auxiliary families without a verified18A/B panel or address schedule. Do not attach a specific panel number, individual switch address or cable tag without conveyor-specific wiring/commissioning records.',3,FULL)
 b.finish(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--expected-version',type=int,default=558);p.add_argument('--output-name',default='rehearsal');a=p.parse_args();sys.stdout.reconfigure(encoding='utf-8')
 snap=json.loads((BASE/'baseline.json').read_text(encoding='utf-8'));plant=ROOT/'data/plant'
 for d in snap['documents']:
  if d['id'] in DOCS.values():assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()==d['sha256'],d['name']
 ro=sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True);v=int(ro.execute("select value from meta where key='version'").fetchone()[0]);assert v==a.expected_version,(v,a.expected_version)
 backup=BASE/f'backup-v{v}.sqlite3'
 if not backup.exists():
  with sqlite3.connect(backup) as dst:ro.backup(dst)
 out=BASE/('accepted' if a.apply else a.output_name);out.mkdir(parents=True,exist_ok=True);assert not (out/'commits.jsonl').exists(),'Do not replay an existing intake'
 if a.apply:s=Store(plant)
 else:
  with sqlite3.connect(out/'plant.sqlite3') as dst:ro.backup(dst)
  s=Store(out)
 ro.close()
 for t in TAGS:ga(s,out,t)
 for t in TAGS:scoop_details(s,out,t)
 drive_aux(s,out);bearings(s,out);scrapers(s,out);gates(s,out);measurements(s,out);transfer(s,out);dfds(s,out);sump(s,out);controls(s,out);supplementary(s,out)
 (out/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()
