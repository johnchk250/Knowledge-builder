"""Reviewed UEE-3 enrichment. Rehearse first; apply only from inspected v527.
No direct canonical SQL writes. Source-scoped versioned proposals retain evidence.
"""
import argparse,hashlib,json,sqlite3
import enrich_conveyor_tp1_pilot as core
from enrich_conveyor_tp1_pilot import ROOT,Store,stage,commit,validate
BASE=ROOT/'output/crusher-pilot'
SOURCE=json.loads((BASE/'source-map.json').read_text(encoding='utf-8'))
DOCS={k:v['id'] for k,v in SOURCE.items()}
core.DOCS.update(DOCS)
HOUSE='UEE-3';DE='Crusher House DE System DE-1 and DE-2'
BASIS='Reviewed Maitree design source; not field/as-built verification. Untagged component labels are descriptive.'

class Batch(core.Batch):
 def finish(self,out):
  body={'summary':self.name,'operations':self.ops,'intake_assessment':{'route':'mixed','purpose':'Crusher-house visual equipment assemblies, coal paths and local services with individual evidence.', 'questions':['What parts make up this equipment?','Which material, drive, control and utility connections apply?','Where is each value supported and what remains unresolved?'],'gaps':self.gaps+[BASIS,'Supplemental claims use reviewed pages '+','.join(map(str,sorted(self.pages)))+'. Other evidence blocks triaged as inventory, not exhaustively re-extracted.'],'reviewed_evidence_ids':[e['id'] for e in self.ev]}}
  report=validate(self.s,{'summary':self.name,'operations':self.ops},self.doc,self.version,visual_ids=self.visual)
  if report['errors']:raise ValueError((self.name,report['errors']))
  (out/(self.name+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  staged=stage(self.s,self.doc,body,visual_ids=self.visual,analysis_dir=str(out),expected_version=self.version)
  accepted=commit(self.s,staged['proposal_id'])
  rec={'name':self.name,'document_id':self.doc,'base_version':self.version,'result_version':self.s.version(),'operations':len(self.ops),'entities':sum(o['op']=='entity' for o in self.ops),'assertions':sum(o['op']=='assert' for o in self.ops),'pages':sorted(self.pages),'warnings':report['warnings'],'commit':accepted}
  with (out/'commits.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
  print(json.dumps({k:rec[k] for k in ['name','result_version','entities','assertions']}),flush=True)
 def retire(self,id,reason,page,r):self.ops.append({'op':'retire','assertion_id':id,'reason':reason,**self.evidence(page,r)})

def part(b,parent,name,typ,page,r,role=None):
 label=parent+' '+name;b.entity(label,typ,page,r,parent,role);return label
def vals(b,label,items,page,r,condition=None):
 for key,val,unit in items:b.a(label,key,val,page,r,unit,condition)
def support(b,page,r):
 """Attach the next page of a multi-page statement, preserving fact-level evidence."""
 b.ops[-1]['evidence'].extend(b.evidence(page,r)['evidence'])

def foundation(s,out):
 b=Batch(s,'flow','crusher-boundaries','Control179162 Rev04 / flow175001 Rev8 p55; '+BASIS)
 r=[.56,.72,.77,.89]
 b.entity(HOUSE,'crusher_house',55,r,role='Screen incoming coal, crush the oversize, and collect screened, crushed or directly bypassed coal for the bunker-feed conveyors.')
 b.a(HOUSE,'location_description','Between the EBA-17A/B inlets from UEE-2 and the EBA-18A/B outlets towards UEF-13.',55,r)
 for i,lane in [(1,'A'),(2,'B')]:
  for tag in [f'EBC-{i}',f'EBD-{i+4}',f'KF-{i}',f'FG-15{lane}',f'FG-{i+14}']:
   b.rel(tag,'part_of',HOUSE,55,r)
  b.a(f'EBC-{i}','equipment_role',f'Ring granulator crushes the oversize from EBD-{i+4} and discharges to KF-{i}.',55,r)
  b.a(f'EBD-{i+4}','equipment_role',f'Separate incoming coal: oversize to EBC-{i}, undersize directly to KF-{i}.',55,r)
  b.a(f'KF-{i}','equipment_role',f'Collect direct-bypass, screen-undersize and crushed coal at three feed points; discharge through FG-{i+14} to the selected EBA-18 conveyor.',55,r)
  b.a(f'FG-15{lane}','equipment_role',f'Select EBD-{i+4} screening or direct bypass to KF-{i}; distinct from downstream selector FG-{i+14}.',55,r)
  b.a(f'FG-{i+14}','equipment_role',f'Select EBA-18A or EBA-18B for KF-{i} discharge.',55,r)
  b.a(f'EBD-{i+4}','source_discrepancy','Control narrative p5 calls the crusher-house pair EBD-1/2, but flow p55 identifies EBD-5/6; primary EBD-1–4 are different assets. No identity merge or alias is established.',5,quote='Vibrating Grizzly Screen EBD-1 in Crusher House')
  b.rel(f'EBA-17{lane}','located_at',HOUSE,55,r,condition='Discharge/head end; conveyor spans UEE-2 to UEE-3')
  for a,z,cond in [(f'EBA-17{lane}',f'FG-15{lane}','Incoming coal'),(f'FG-15{lane}',f'EBD-{i+4}','Screening route'),(f'FG-15{lane}',f'KF-{i}','Direct bypass selected'),(f'EBD-{i+4}',f'EBC-{i}','Screen oversize'),(f'EBD-{i+4}',f'KF-{i}','Screen undersize'),(f'EBC-{i}',f'KF-{i}','Crushed product'),(f'KF-{i}',f'FG-{i+14}','Feeder discharge'),(f'FG-{i+14}','EBA-18A','Outlet A selected'),(f'FG-{i+14}','EBA-18B','Outlet B selected')]:b.rel(a,'feeds',z,55,r,network='material',condition=cond)
  for g in [f'FG-15{lane}',f'FG-{i+14}']:b.entity(g,'diverter_gate',55,r)
 b.finish(out)

def crusher(s,out,i):
 c=f'EBC-{i}';b=Batch(s,'crusher',f'{c}-mechanical','Ring granulator GA175111 Rev3, vendorCS.1.1-12483 RevC, approved28-Mar-2019. Two-machine design (1LH+1RH); exact numbered handing remains unverified. '+BASIS)
 tech=[.575,.657,.747,.951];bom=[.777,.175,.948,.625];section=[.28,.046,.776,.591]
 vals(b,c,[('rated_capacity',1250,'t/h'),('design_capacity',1375,'t/h'),('rotor_speed',575,'rpm'),('maximum_feed_size',100,'mm')],1,tech)
 b.a(c,'product_size_requirement','98% passing 20 mm, as specified in GA.',1,tech)
 b.a(c,'equipment_model','L&T 1019U ring granulator',1,tech)
 b.a(c,'source_gap','Two machines are one LH and one RH; reviewed machine GA alone does not map handedness to EBC-1 versus EBC-2. Shaft/bearing selection remains design data.',1,tech)
 b.rel('Maitree CHP Ring Granulator','design_detail_applies_to',c,1,tech,condition='Common Maitree two-machine design, not a third installed granulator')
 body=part(b,c,'Housing and access','functional_assembly',1,section,'Enclose the crushing zone, with opening sections and access doors for maintenance.')
 for name,typ in [('Upper frame','mechanical_component'),('Lower frame','mechanical_component'),('Hopper and top cover','chute'),('Inspection door','maintenance_access'),('Cage access door','maintenance_access'),('Tramp iron trap box','mechanical_component'),('Deflector liners','mechanical_component'),('Housing liners','mechanical_component')]:part(b,body,name,typ,1,bom)
 b.a(body+' Housing liners','component_material','Mn steel, minimum 20 mm thick.',1,bom);b.a(body+' Deflector liners','component_material','Mn steel, minimum 20 mm thick.',1,bom)
 rotor=part(b,c,'Rotor assembly','crusher_rotor',1,section,'Rotor shaft and end discs carry suspension bars and toothed ring hammers.')
 for name in ['Rotor shaft','End discs','Suspension bars','Spacing discs','Ring hammers']:part(b,rotor,name,'mechanical_component',1,bom)
 vals(b,rotor+' Ring hammers',[('quantity',56,'hammers'),('component_mass',39.5,'kg')],1,tech,'Per crusher; approximate mass per ring')
 b.a(rotor+' Ring hammers','assembly_arrangement','Four rows at 90 degrees; 14 hammers per row. Mn steel, nominal size 140 x 330/220 mm.',1,tech)
 b.a(rotor+' Suspension bars','quantity',4,1,tech,'bars','Derived from four rows with one suspension bar per row',origin='inferred')
 b.a(rotor,'maintenance_requirement','Heaviest complete rotor with bearing housing is approximately 12 t; GA provides a maintenance bar and rotor locking holes. Replacement procedure refers to the vendor manual.',1,[.058,.499,.746,.918])
 cage=part(b,c,'Screen cage and adjustment','crusher_cage',1,bom,'Upper/lower screen plates and cage frame form the final crushing zone; external mechanism adjusts cage clearance.')
 for name in ['Cage frame','Upper screen plate','Lower screen plate','Breaker screen plates','Cage adjusting mechanism']:part(b,cage,name,'mechanical_component',1,bom)
 b.a(cage,'maintenance_requirement','GA states cage adjustment is made with granulator empty or running without crushing material; locking and detailed adjustment refer to the manual. This is a design note, not an isolation authorization.',1,[.07,.651,.302,.813])
 bearings=part(b,c,'Rotor bearings and seals','functional_assembly',1,tech,'Drive-end and non-drive-end split plummer blocks support the rotor shaft.')
 for end in ['Drive-end','Non-drive-end']:
  br=part(b,bearings,end+' bearing','bearing',1,tech)
  b.a(br,'equipment_model','SKF 22240 CCK3/W33 + H3140 or FAG equivalent; spherical roller bearing.',1,tech)
  b.a(br,'lubrication_method','Manual grease gun',1,tech)
  b.a(br,'lubricant_grade','Lithon EP2 / Servogem EP2',1,[.315,.91,.374,.95])
  part(b,br,'Labyrinth seal','mechanical_component',1,tech)
 b.a(bearings,'lubricant_fill_quantity',10,1,[.315,.91,.374,.95],'kg','Drawing note does not resolve whether total or per bearing; not a replenishment interval')
 hydraulic=part(b,c,'Hydraulic opening system','hydraulic_system',1,bom,'Hydraulic cylinders and power pack open the crusher housing for access.')
 cylinders=part(b,hydraulic,'Opening cylinders','hydraulic_cylinder',1,bom);b.a(cylinders,'quantity',2,1,bom,'cylinders')
 pack=part(b,hydraulic,'Power pack','hydraulic_power_pack',1,bom);b.rel(pack,'utility_supply_to',cylinders,1,section,network='utility',condition='Hydraulic opening function; detailed circuit not provided on GA')
 b.a(pack,'source_gap','Hydraulic motor rating, pump duty, oil grade/volume, valve circuit and commissioned pressure are not established by the reviewed crusher GA.',1,section)
 drive=part(b,c,'Drive assembly','functional_assembly',1,tech,'Motor transmits torque through the crusher-specific scoop coupling to the rotor; no reducer is shown in this direct drive.')
 motor=part(b,drive,'Main motor','electric_motor',1,tech)
 vals(b,motor,[('motor_rated_power',750,'kW'),('motor_speed',600,'rpm')],1,tech,'GA selection, distinct from rotor speed')
 coupling=part(b,drive,'Scoop coupling PST-1150','coupling',1,tech)
 b.rel(motor,'mechanically_drives',coupling,1,[.42,.667,.573,.842],network='mechanical',condition='GA key plan motor/coupling/crusher drive')
 b.rel(coupling,'mechanically_drives',rotor,1,[.42,.667,.573,.842],network='mechanical')
 protect=part(b,c,'Protection and monitoring','functional_assembly',1,[.191,.815,.374,.949])
 for typ,name in [('vibration_sensor','Rotor bearing vibration monitors'),('temperature_sensor','Rotor bearing RTDs')]:part(b,protect,name,typ,1,[.191,.815,.374,.949])
 v=protect+' Rotor bearing vibration monitors';t=protect+' Rotor bearing RTDs'
 vals(b,v,[('alarm_threshold',7.1,'mm/s'),('trip_threshold',11.2,'mm/s')],1,[.191,.82,.255,.863],'GA rotor-bearing vibration level; commissioned setting and delay not verified')
 b.a(v,'operating_range','Normal 4.5–5.0 mm/s in GA.',1,[.191,.82,.255,.863])
 vals(b,t,[('alarm_threshold',80,'degC'),('trip_threshold',90,'degC')],1,[.254,.824,.312,.855],'GA bearing detector values; control write-up has different limits')
 b.a(t,'source_discrepancy','GA bearing alarm/trip80/90 degC differs from crusher control p16/17 rotor-bearing scoop permission <=70 and disengagement >80 degC. Motor bearing limits are separate. Do not choose a commissioned setting from these documents.',1,[.191,.815,.374,.949])
 for d in [v,t]:b.rel(d,'protects_equipment',c,1,[.191,.815,.374,.949])
 b.finish(out)

def scoop(s,out,i):
 c=f'EBC-{i}';co=c+' Drive assembly Scoop coupling PST-1150'
 b=Batch(s,'scoop',f'{c}-scoop-oil','Crusher scoop175113 package, main GA footer175058 Rev1, PremiumC/1924/D1/D2; approved19-Feb-2019. 1150PST applies to ring granulator750kW600rpm. '+BASIS)
 ga=[.323,.072,.444,.304];notes=[.788,.308,.943,.553];pid=[.156,.086,.555,.68];schedule=[.67,.051,.959,.454]
 b.a(co,'equipment_model','Premium 1150 PST',1,[.833,.056,.959,.097])
 b.a(co,'lubricant_grade','HP ENKLO46 / BP MAK46 / Indian Oil Servo System46, as listed alternatives.',1,ga)
 vals(b,co,[('lubricant_fill_quantity',950,'L'),('maximum_working_pressure',3,'kg/cm2'),('design_temperature_limit',75,'degC')],1,notes,'Oil capacity and maximum oil temperature at50degC ambient/full load; not trip settings')
 oil=part(b,co,'Oil sump','oil_tank',2,pid)
 pump=part(b,co,'Oil circulation pump','oil_circulation_pump',1,ga)
 b.a(pump,'equipment_model','RDRN300S gear pump with relief valve',1,ga);vals(b,pump,[('rated_flow',415,'L/min'),('nominal_pressure',3,'kg/cm2')],1,ga)
 pm=part(b,pump,'Motor','electric_motor',1,ga);vals(b,pm,[('motor_rated_power',10,'hp'),('motor_speed',1450,'rpm')],1,ga);b.rel(pm,'mechanically_drives',pump,1,ga,network='mechanical')
 cooler=part(b,co,'Oil radiator','oil_cooler',1,[.492,.404,.699,.853]);cm=part(b,cooler,'Fan motor','electric_motor',1,ga)
 vals(b,cm,[('motor_rated_power',2.2,'kW'),('motor_speed',1000,'rpm')],1,ga);b.rel(cm,'mechanically_drives',cooler,1,ga,network='mechanical',condition='Air-cooling fan')
 ss=part(b,co,'Suction strainer','oil_filter',2,pid);fil=part(b,co,'Return Y filter','oil_filter',2,pid);duplex=part(b,co,'Duplex lubrication filter','oil_filter',2,pid)
 b.a(fil,'filter_mesh',20,2,schedule,'mesh');b.a(ss,'component_dimension',3,2,schedule,'inch','Suction strainer connection')
 for a,z in [(oil,ss),(ss,pump),(pump,cooler),(cooler,fil),(fil,oil),(fil,duplex),(duplex,co)]:b.rel(a,'utility_supply_to',z,2,pid,network='utility',condition='Oil path shown by P&I arrows; duplex branch supplies coupling lubrication')
 act=part(b,co,'Scoop actuator','electric_actuator',1,[.697,.062,.832,.174]);am=part(b,act,'Motor','electric_motor',12,[.058,.112,.94,.902])
 b.a(act,'assembly_arrangement','Dual-speed rotary actuator,15kgm output; travel and torque switches; manual handwheel.',12,[.058,.112,.94,.902])
 b.a(am,'motor_rated_power',.25,12,[.058,.112,.94,.902],'kW','High-speed1380rpm; low-speed685rpm is0.1kW')
 b.a(am,'source_discrepancy','GA detailed box and actuator datasheet give0.1/0.25kW; a separate GA notes line says0.37kW. Speed labels for8/4second engagement also differ from datasheet685/1380rpm. Final actuator selection/timing needs reconciliation.',1,notes)
 b.rel(am,'mechanically_drives',act,12,[.058,.112,.94,.902],network='mechanical');b.rel(act,'control_signal_to',co,2,pid,network='control',condition='Positions scoop tube; feedback/limits retained in local panel')
 panel=part(b,co,'Local control panel','local_control_panel',1,[.834,.233,.955,.258])
 for name,typ,loc in [('TS1 inlet oil temperature','temperature_switch','Inlet oil temperature'),('TS2 outlet oil temperature','temperature_switch','Outlet oil temperature'),('PS oil pressure','pressure_switch','Oil lubrication pressure'),('DPS filter differential pressure','pressure_switch','Across duplex filter'),('FSO oil flow','flow_switch','Pump/cooler circulation line'),('Oil level gauge','level_gauge','Sump level'),('Oil temperature gauge','temperature_gauge','Local oil indication'),('Oil pressure gauge','pressure_gauge','Local oil pressure'),('Fusible plug','protection_device','Coupling thermal protection')]:
  d=part(b,co,name,typ,2,pid,loc);b.rel(d,'protects_equipment',co,2,pid)
 tab=[.13,.707,.368,.831]
 for name,key,val,u,condition in [('TS1 inlet oil temperature','alarm_threshold',85,'degC','P&I alarm >85'),('TS2 outlet oil temperature','trip_threshold',110,'degC','P&I trip >110; action target not identified in table'),('PS oil pressure','alarm_threshold',.3,'kg/cm2','P&I alarm <0.3'),('DPS filter differential pressure','alarm_threshold',.8,'kg/cm2','P&I alarm >0.8'),('FSO oil flow','alarm_threshold',300,'L/min','P&I alarm <300')]:b.a(co+' '+name,key,val,2,tab,u,condition)
 b.a(co+' Fusible plug','design_temperature_limit',145,2,schedule,'degC','Nominal melting point; GA tolerance+/-5degC')
 b.a(co,'source_discrepancy','P&I TS1/TS2 alarm/trip>85/>110degC coexists with GA maximum operating oil75degC and review request to restrict maximum75degC. These are different reported limits, not verified commissioned settings. P&I nominal flow405L/min differs from GA pump415L/min.',2,tab)
 b.a(co,'source_gap','Local terminal/relay drawings are retained in source sheets5–11; field cable/MCC assignment and commissioned cause/effect are not established by the GA/P&I.',2,schedule)
 b.finish(out)

def screen(s,out,i):
 tag=f'EBD-{i+4}';b=Batch(s,'screen',f'{tag}-grizzly','Secondary vibro-grizzly175112 Rev2 GA plus calculation/review; approval21-Jan-2019, review contains later01-Mar reply. CRH-specific two-machine design. '+BASIS)
 bom=[.756,.538,.984,.731];tech=[.84,.337,.983,.522];ga=[.045,.044,.717,.406]
 vals(b,tag,[('rated_capacity',1250,'t/h'),('design_capacity',1375,'t/h'),('separation_size',20,'mm'),('minimum_operating_speed',725,'rpm'),('maximum_operating_speed',800,'rpm')],1,tech)
 b.a(tag,'source_discrepancy','GA design capacity1375t/h; selection/calculation headings state1370t/h. Preserve the difference pending reconciliation.',2,[.09,.134,.942,.93])
 b.a(tag,'location_description','Secondary screen at crusher house floor EL+24.000m (TOC), per GA.',1,[.418,.319,.709,.409])
 body=part(b,tag,'Screen body and deck','functional_assembly',1,bom,'Blind feed deck followed by grizzly plates; dust covers enclose the screening zone.')
 for name in ['Blind feed deck','Grizzly plate assembly','Dust covers']:part(b,body,name,'mechanical_component',1,bom)
 vals(b,body+' Grizzly plate assembly',[('component_dimension',12,'mm')],1,bom,'Plate thickness; TISCRAL/equivalent in GA')
 b.a(body+' Blind feed deck','component_dimension',16,1,bom,'mm','Thickness');b.a(body+' Blind feed deck','component_dimension',1.5,2,[.36,.626,.91,.812],'m','Feed-end blind-deck length in selection')
 drive=part(b,tag,'Vibrating drive assembly','functional_assembly',1,ga,'Motor and Cardan shaft drive paired exciters; intermediate Cardan shaft links the exciters.')
 motor=part(b,drive,'Motor','electric_motor',1,bom);vals(b,motor,[('motor_rated_power',37,'kW'),('motor_speed',1500,'rpm')],1,bom,'Selected motor; calculation also uses1440rpm for torque')
 shaft=part(b,drive,'Cardan shaft','mechanical_component',1,bom);inter=part(b,drive,'Intermediate Cardan shaft','mechanical_component',1,bom)
 exc=[]
 for j in (1,2):
  x=part(b,drive,f'Exciter {j}','vibration_exciter',1,bom);b.a(x,'equipment_model','DF501V',1,bom);exc.append(x)
 for a,z in [(motor,shaft),(shaft,exc[0]),(exc[0],inter),(inter,exc[1]),(exc[0],body),(exc[1],body)]:b.rel(a,'mechanically_drives',z,1,ga,network='mechanical',condition='GA motor/Cardan/exciter arrangement; descriptive exciter numbering')
 part(b,drive,'Cardan shaft guard','mechanical_component',1,bom)
 support=part(b,tag,'Springs and supports','functional_assembly',1,bom)
 for name,qty in [('Front springs',8),('Rear springs',10),('Amplitude limiters',8)]:
  x=part(b,support,name,'mechanical_component',1,bom);b.a(x,'quantity',qty,1,bom,'sets' if name=='Amplitude limiters' else 'springs','Per screen BOM')
 b.a(support,'source_gap','Spring supports isolate mechanical vibration; no separate vibration trip instrument is established by this GA. Exciter bearing/lubricant details need applicable vendor maintenance data.',1,bom)
 b.a(tag,'operating_requirement','Review reply: feed-rate adjustment40–100% by changing unbalance weights of DF exciters; secondary operating stroke12mm. Adjustment procedure and isolation need vendor maintenance instructions.',4,quote='The feed rate can be adjusted in the range of')
 b.finish(out)

def belt_machine(s,out,i,feeder=False):
 tag=f'KF-{i}' if feeder else f'EBA-17{"AB"[i-1]}'
 key='feeder' if feeder else 'conveyor';page=1 if feeder else 4
 r=[.794,.028,.976,.735] if feeder else [.785,.045,.966,.755]
 b=Batch(s,key,tag+'-assemblies',('KF1/2 GA175030 Rev1' if feeder else 'EBA17A/B GA175027 Rev2')+'; local drive/protection schedules; '+BASIS)
 drive=part(b,tag,'Drive assembly','functional_assembly',page,r,'Motor, fluid coupling, reducer and low-speed coupling transmit torque to the head pulley; thruster brake acts on the drive.')
 mech=part(b,tag,'Belt and mechanical assembly','functional_assembly',page,r)
 motor=part(b,drive,'Main motor','electric_motor',page,r)
 vals(b,motor,[('motor_rated_power',45 if feeder else 270,'kW'),('motor_speed',1480 if feeder else 1488,'rpm'),('motor_voltage',3300,'V')],page,r)
 co=part(b,drive,'Fluid coupling SDFC-370' if feeder else 'Scoop coupling PST-500','coupling',page,r)
 b.a(co,'equipment_model','SDFC-370 delay-filled fluid coupling' if feeder else 'PST-500 scoop coupling',page,r)
 gearbox=part(b,drive,'Gearbox','gearbox',page,r);b.a(gearbox,'equipment_model','Bevel-helical B3-225' if feeder else 'Bevel-helical B3-355',page,r)
 b.a(gearbox,'gear_ratio_nominal',34.7 if feeder else 23.2,page,r)
 low=part(b,drive,'Low-speed geared coupling','coupling',page,r);b.a(low,'equipment_model','RG08' if feeder else 'RG10',page,r)
 head=part(b,mech,'Head pulley','pulley',page,r);b.a(head,'component_dimension',630 if feeder else 800,page,r,'mm','Diameter')
 for a,z in [(motor,co),(co,gearbox),(gearbox,low),(low,head)]:b.rel(a,'mechanically_drives',z,page,r,network='mechanical',condition='Scheduled drive train; GA arrangement')
 brake=part(b,drive,'Thruster brake','brake_assembly',page,r);b.a(brake,'equipment_model','Electromach EBTM-300/H' if feeder else 'Electromach EBTM-500/F',page,r)
 b.a(brake,'component_dimension',250 if feeder else 500,page,r,'mm','Scheduled brake-drum diameter; model number is a separate field')
 b.rel(brake,'brakes',co,page,r,network='mechanical',condition='High-speed drive brake drum')
 b.a(brake,'source_gap','Local GA establishes a thruster brake. Exact thruster model, fluid grade/fill and brake-release switch field tag require the applicable vendor detail; do not copy another conveyor size.',page,r)
 belt=part(b,mech,'Conveyor belt','conveyor_belt',page,r)
 b.a(belt,'equipment_model','NN630/4 FR' if feeder else 'NN1000/4 FR',page,r)
 vals(b,belt,[('belt_width',1600 if feeder else 1400,'mm'),('belt_speed',1.5 if feeder else 2.7,'m/s'),('belt_endless_length',36.124 if feeder else (510 if i==1 else 500),'m')],page,r)
 b.a(belt,'belt_cover_thickness',5,page,r,'mm','Top');b.a(belt,'belt_cover_thickness',2,page,r,'mm','Bottom');b.rel(head,'mechanically_drives',belt,page,r,network='mechanical')
 for name,diam,qty in ([('Tail pulley',500,1),('Snub pulley',500,1),('Deflector rollers',219,2)] if feeder else [('Tail and take-up pulleys',630,2),('Snub and bend pulleys',630,3),('Deflector rollers',219,2)]):
  x=part(b,mech,name,'pulley',page,r);b.a(x,'quantity',qty,page,r,'devices','Per conveyor/feeder schedule group, not individually tagged');b.a(x,'component_dimension',diam,page,r,'mm','Diameter')
 idlers=part(b,mech,'Idlers','functional_assembly',page,r)
 for name,num in ([('Impact idlers',29),('Carrying idlers',4),('Return idlers',4)] if feeder else [('Impact idlers',12),('Carrying idlers',226 if i==1 else 223),('Return idlers',66 if i==1 else 65),('Self-aligning carrying idlers',17),('Self-aligning return idlers',15),('Transition idlers',4),('Self-cleaning return idler',1),('Flat return rollers',3)]):
  x=part(b,idlers,name,'idler_group',page,r);b.a(x,'quantity',num,page,r,'sets','Per belt; transition total is2+2 for15/25degree sets')
 take=part(b,mech,'Take-up assembly','take_up_assembly',page,r);b.a(take,'assembly_arrangement','Screw take-up,500mm travel.' if feeder else 'Vertical gravity take-up,7000mm travel;24mm6x37CF grade1570 rope,267kN minimum breaking force.',page,r)
 if not feeder:
  cw=part(b,take,'Counterweight','mechanical_component',page,r);b.a(cw,'component_mass',7000,page,r,'kg','Design mass,400 blocks of17.5kg');part(b,take,'Rope and reeving','mechanical_component',page,r)
 for name in ['Primary external scraper','Secondary external scraper','Internal V-plough scraper']:part(b,mech,name,'belt_scraper',page,r)
 skirt=part(b,mech,'Skirt and deck plates','mechanical_component',page,r);b.a(skirt,'assembly_arrangement',('14.4m skirt;20mmHardox400 sides,10mm top;3mm continuous deck.' if feeder else '7.25m skirt;20mmHardox400 sides,10mm top;3.15mm deck/seal.'),page,r)
 prot=part(b,tag,'Belt protection devices','functional_assembly',page,r)
 for name,typ,num,spacing in [('BSS','belt_sway_switch_group',1 if feeder else 7,40),('PCS','pull_cord_switch_group',1 if feeder else 9,30),('ZSS','zero_speed_switch',1,None)]:
  x=part(b,prot,name,typ,page,r);b.a(x,'quantity',num,page,r,'device' if name=='ZSS' else 'pairs','Per belt; ZSS at tail pulley')
  if name!='ZSS':
   b.a(x,'individual_device_count',num*2,page,r,'switches','Derived as two switches per documented pair',origin='inferred')
   if not feeder:b.a(x,'device_spacing',spacing,page,r,'m','Each side')
  b.rel(x,'protects_equipment',tag,page,r)
 if not feeder:b.a(co,'source_gap','EBA17 GA specifies PST-500. A detailed applicability check is still needed before attaching oil-pump, cooler, filter or actuator ratings from conveyor coupling family sheets. Crusher PST-1150 values do not apply.',page,r)
 b.finish(out)

def controls(s,out):
 b=Batch(s,'flow','crusher-control-dependencies','Control179162 Rev04, pp15–17 and29; design conditions, not verified commissioned settings. '+BASIS)
 for i in (1,2):
  c=f'EBC-{i}';co=c+' Drive assembly Scoop coupling PST-1150';motor=c+' Drive assembly Main motor';rad=co+' Oil radiator Fan motor';pump=co+' Oil circulation pump';act=co+' Scoop actuator';prot=c+' Protection and monitoring'
  b.a(c,'sequence_logic','Start command: radiator, oil circulation pump on radiator feedback, main motor, then scoop OUT/engaged. Stop: scoop IN/disengaged, pump, radiator, main motor. Separate motor permissive paragraph allows independent motor start; do not flatten sequence and permissives into one Boolean rule.',15,[.11,.18,.91,.4])
  b.a(motor,'start_permissive','All winding temperatures <120degC; DE/NDE motor bearings <70degC; scoop IN/disengaged; electrical healthy; local stop reset; hydraulic door closed.',15,[.16,.408,.91,.541])
  b.a(motor,'trip_condition','Any winding temperature >130degC; motor bearing >80degC; electrical trip; local stop operated. These are motor limits, not rotor-bearing limits.',15,[.16,.548,.91,.64])
  b.a(rad,'start_permissive','Electrical healthy and scoop fault not operated.',15,[.16,.797,.91,.865]);b.a(rad,'trip_condition','Electrical trip or scoop fault.',15,[.16,.876,.91,.943])
  b.a(pump,'start_permissive','Radiator ON, oil temperature normal, scoop fault not operated, electrical healthy.',16,[.11,.15,.92,.38])
  b.a(pump,'trip_condition','Oil-temperature switch high; electrical trip; radiator not ON; oil-flow switch unhealthy with10s delay; main crusher motor OFF with300s delay.',16,[.11,.34,.92,.51])
  b.a(pump,'source_discrepancy','Start/stop description says30s adjustable stop delay; trip list says300s after main motor OFF. Retain both clauses; final cause/effect and timer settings need reconciliation.',16,[.11,.16,.92,.51])
  b.a(act,'start_permissive','Scoop OUT/engaged requires radiator and oil pump ON; main motor ON; oil temperature/pressure/differential normal; both CBS not operated; process/electrical healthy; local stop reset; hydraulic door closed; crusher rotor-bearing temperature <=70degC.',16,[.11,.49,.92,.831])
  b.a(act,'trip_condition','Scoop IN/disengaged for ZSS with60s on delay; radiator, oil pump, main motor or corresponding KF OFF; electrical trip; vibration trip; hydraulic door open; crusher-bearing temperature >80degC. CBS clause on preceding page is contradictory and remains unresolved.',17,[.13,.157,.93,.306])
  b.a(act,'source_discrepancy','Engage permissive requires both CBS NOT operated, while disengage clause says ANY CBS NOT operated. Likely wording error is not corrected into an executable rule; reconcile with approved logic and field verification.',16,[.11,.642,.92,.893])
  part(b,prot,'Zero-speed switch','zero_speed_switch',17,[.13,.157,.93,.306])
  for name,typ in [('Hydraulic door closed switch','limit_switch'),('Chute block switches','chute_block_switch_group')]:part(b,prot,name,typ,16,[.11,.642,.92,.893])
  b.a(prot+' Chute block switches','quantity',2,16,[.11,.642,.92,.78],'switches','Control says both; exact field locations/tags unresolved')
  b.a(prot+' Zero-speed switch','trip_condition','Crusher ZSS operated with60s on delay disengages scoop per p17; no numerical speed threshold is stated here.',17,[.13,.157,.93,.306])
  for a,z,cond,page,r in [(rad,pump,'Radiator start feedback / ON permissive',16,[.11,.16,.92,.51]),(pump,act,'Oil pump ON',16,[.11,.49,.92,.831]),(motor,act,'Main motor ON',16,[.11,.49,.92,.831]),(f'KF-{i}',act,'Corresponding feeder OFF disengages scoop',17,[.13,.157,.93,.306]),(prot+' Hydraulic door closed switch',motor,'Hydraulic door closed permits motor start',15,[.16,.408,.91,.541]),(prot+' Zero-speed switch',act,'ZSS operated with60s delay disengages scoop',17,[.13,.157,.93,.306])]:b.rel(a,'control_signal_to',z,page,r,network='control',condition=cond)
  k=f'KF-{i}';b.a(k,'start_permissive','General feeder: electrical healthy; local stop reset; PCS/BSS/CBS not operated; succeeding conveyor running and outlet flap gate directed to it.',29,[.17,.45,.89,.69])
  b.a(k,'source_discrepancy','General feeder section calls drive LT; KF1/2 GA specifies3.3kV motor. Retain source-specific wording and verify switchgear designation.',29,quote='Electrical Condition : Same as LT drive. Refer section 5.0.2.')
  for d,cond in [('PCS','Pull cord operated'),('BSS','Belt sway operated'),('ZSS','Zero speed operated with60s on delay')]:b.a(k+' Belt protection devices '+d,'trip_condition',cond+' trips feeder in general control section.',29,[.17,.70,.89,.846])
 b.finish(out)

def house(s,out):
 b=Batch(s,'house','crusher-house-levels-and-access','UEE3 GA175046 Rev5; physical arrangement/TOC levels and service schedules. '+BASIS)
 r=[.04,.08,.76,.94]
 for i,lane in [(1,'A'),(2,'B')]:
  for tag,desc in [(f'EBA-17{lane}','Head/discharge on EL+34.200m TOC; tail is at UEE-2.'),(f'EBD-{i+4}','Secondary screening at EL+24.000m TOC.'),(f'EBC-{i}','Crusher/motor/coupling on the isolated support at the EL+18.000m TOC floor.'),(f'KF-{i}','Feeder at EL+10.900m TOC floor; top belt EL+12.400m.')]:b.a(tag,'location_description',desc,1,r)
 access=part(b,HOUSE,'Maintenance access and lifting','functional_assembly',6,[.055,.225,.515,.438],'Floor access, monorails and hoists serve the pulley, screen and crusher maintenance zones.')
 lifts=part(b,access,'Monorails and hoists','maintenance_access',6,[.055,.225,.515,.438])
 for tag,cap,lift,role in [('EH-1',10,39,'EBA17AB head/snub, drive and belt drum'),('EH-2',3.5,6,'EBA17AB head/snub and drive'),('EH-3',12.5,35,'EBC-2 and screen drive (schedule says EBD-1)'),('EH-4',12.5,35,'EBC-1 and screen drive (schedule says EBD-2)'),('EH-5',2,14,'KF1/2 pulleys and drives'),('EH-6',2.5,6,'EBA18AB tail pulleys'),('MH-1',1,9,'Gate actuators; schedule says FG15A and FG16A'),('MH-2',1,9,'FG15/16 actuators'),('MH-3',2.5,32.5,'EBA17AB take-up pulleys'),('MH-4',10,12.5,'EBA17AB counterweight frames'),('MH-5',1,6,'SNC-1 elevator motor')]:
  x=part(b,lifts,tag,'electric_hoist' if tag.startswith('EH') else 'manual_hoist',6,[.055,.225,.515,.438],role);b.a(x,'rated_capacity',cap,6,[.055,.225,.515,.438],'t','Hoist schedule; not current lifting certification');b.a(x,'lifting_height',lift,6,[.055,.225,.515,.438],'m','Scheduled lift')
 b.a(lifts,'source_discrepancy','House hoist schedule names EBD1/2 and FG16A; flow diagram establishes secondary EBD5/6 and bypass FG15A/B. Capacities retained with exact schedule scope; ambiguous hoist-to-screen/gate assignments are not silently corrected.',6,[.055,.225,.515,.438])
 b.rel('Crusher House Passenger and Goods Elevator','part_of',access,1,r)
 b.a(access,'maintenance_requirement','Use level-specific hoist schedule and maintenance openings; lifting capacities are not interchangeable. Full lifting plan and current certification are outside this model.',6,[.055,.225,.515,.438])
 for g in ['FG-15A','FG-15B']:b.a(g,'source_gap','Bypass gate added on flow Rev8 and house GA; reviewed older generic flap-gate175065 sheets do not schedule FG15A/B. Do not borrow FG15/16 actuator ratings.',1,r)
 b.finish(out)

def vis(s,out):
 b=Batch(s,'isolation','crusher-isolated-foundations','GERB GA175114 foundation for1019U; two identical sets. '+BASIS)
 for i in (1,2):
  c=f'EBC-{i}';v=part(b,c,'Isolated foundation','vibration_isolation_system',1,[.026,.04,.95,.96],'Common motor/coupling/crusher foundation supported on springs and viscodampers.')
  sp=part(b,v,'Spring elements','mechanical_component',1,[.84,.033,.974,.235]);b.a(sp,'quantity',12,1,[.84,.033,.974,.235],'elements','Per foundation');b.a(sp,'equipment_model','GP-8-771',1,[.84,.033,.974,.235])
  dm=part(b,v,'Viscodampers','mechanical_component',1,[.69,.19,.845,.24]);b.a(dm,'quantity',4,1,[.69,.19,.845,.24],'dampers','Per foundation');b.a(dm,'equipment_model','V5RM',1,[.69,.19,.845,.24])
  for name in ['Steel shims','Adhesive pads']:part(b,v,name,'mechanical_component',1,[.842,.235,.977,.431])
  b.rel('Crusher House Vibration Isolation System (VIS)','design_detail_applies_to',v,1,[.026,.04,.95,.96])
  b.a(v,'maintenance_requirement','GERB notes dimensions require final machine drawing/site verification and refer to GERB construction manual; this is mechanical isolation, separate from vibration trip instrumentation.',1,[.842,.235,.977,.65])
 b.finish(out)

def gates(s,out):
 b=Batch(s,'gate','crusher-outlet-gates','Flap-gate GA175065 Rev2 sheet5, type5 schedule for KF1/2. '+BASIS)
 r=[.53,.236,.97,.618]
 for g in ['FG-15','FG-16']:
  for name,typ in [('Casing and flap','mechanical_component'),('Shaft and plummer blocks','bearing'),('Lever arm','mechanical_component'),('Linear actuator','electric_actuator'),('Travel and thrust limit switches','limit_switch_group'),('Inspection doors','maintenance_access')]:part(b,g,name,typ,5,r)
  b.a(g,'operating_range','56degree gate travel, motorized linear electromechanical actuator with travel and thrust-dependent limits.',5,r)
  b.a(g+' Casing and flap','component_material','20mm Hardox400; flap has10mm rib plate.',5,r)
  b.a(g+' Linear actuator','equipment_model','Prefec P5 Model B',5,r);b.a(g+' Linear actuator','motor_rated_power',7.5,5,r,'kW');b.a(g+' Linear actuator','component_dimension',650,5,r,'mm','Stroke, adjustable up to100mm from each end');b.a(g+' Linear actuator','actuator_thrust',5600,5,r,'kgf','GA states5600kg thrust; interpreted as force unit',origin='inferred')
  b.rel(g+' Linear actuator','mechanically_drives',g+' Lever arm',5,[.048,.035,.483,.597],network='mechanical');b.rel(g+' Lever arm','mechanically_drives',g+' Casing and flap',5,[.048,.035,.483,.597],network='mechanical')
  b.a(g,'source_discrepancy','Type5 schedule location column repeats KF-1 for FG-16, while marking/casing code identifies KF-2 and process drawing connects KF-2 to FG-16. Preserve distinct gate identities.',5,r)
 b.finish(out)

def extraction(s,out):
 b=Batch(s,'de','crusher-dust-extraction-layout','DE schematic175100 Rev1 sheet1; two streams with common dust return and selectable crossover. '+BASIS)
 r=[.052,.05,.664,.575]
 b.entity(DE,'crusher_dust_extraction',1,r,HOUSE,'Capture dust at conveyor discharge, screen enclosure and feeder receiving points; separate dust through cyclones and filters and return it to a selected EBA-18 belt.')
 common=part(b,DE,'Shared cyclone hopper and dust return','functional_assembly',1,r)
 hopper=part(b,common,'Cyclone dust hopper','dust_hopper',1,r);b.a(hopper,'storage_capacity',.8,1,r,'m3','Common cyclone collection hopper, drawing value')
 for n in [5]:b.rel(f'RAL-CH-{n:03}','part_of',hopper,1,r)
 for n in [1,2]:b.rel(f'FGD-CH-{n:03}','part_of',common,1,r)
 air=part(b,DE,'Compressed-air connection','utility_header',1,[.357,.461,.631,.77],'Shared compressed-air supply to pulse-jet filters; compressor house is outside UEE-3.')
 for i in (1,2):
  stream=f'DE-{i}';b.entity(stream,'crusher_dust_extraction_stream',1,r,DE)
  b.a(stream,'equipment_role',f'Dust extraction stream{i}: four capture points, cyclone, bag-filter compartment and ID fan.',1,r)
  duct=part(b,stream,'Suction duct and hoods','dust_extraction_duct',1,r)
  for j,(name,target) in enumerate([(f'EBA-17{"AB"[i-1]} discharge',f'EBA-17{"AB"[i-1]}'),(f'EBD-{i+4} enclosure',f'EBD-{i+4}'),('Screen undersize receiving',f'KF-{i}'),('Crusher product receiving',f'KF-{i}')],1):
   hood=part(b,duct,f'H{j} {name}','dust_capture_hood',1,r);b.rel(hood,'serves_equipment',target,1,r,condition='Dust suction interface, not ownership of the process machine');b.rel(hood,'utility_supply_to',duct,1,r,network='utility',condition='Dust-laden air extraction')
  cyc=part(b,stream,'Cyclone separator','cyclone_separator',1,r)
  filt=part(b,stream,'Bag-filter compartment','bag_filter',1,r)
  b.rel(f'FAN-CH-{i:03}','part_of',stream,1,r)
  for a,z,cond in [(duct,cyc,'Dust-laden air'),(cyc,filt,'Pre-separated air'),(filt,f'FAN-CH-{i:03}','Filtered air'),(cyc,hopper,'Collected cyclone dust')]:b.rel(a,'utility_supply_to',z,1,r,network='utility',condition=cond)
  for n in [2*i-1,2*i]:
   hp=part(b,filt,f'Hopper {n}','dust_hopper',1,r)
   for pre in ['RAL','LV','ZSS']:b.rel(f'{pre}-CH-{n:03}','part_of',hp,1,r)
   b.rel(filt,'utility_supply_to',hp,1,r,network='utility',condition='Separated dust');b.rel(hp,'utility_supply_to',f'RAL-CH-{n:03}',1,r,network='utility',condition='Dust discharge');b.rel(f'RAL-CH-{n:03}','utility_supply_to','FGD-CH-002',1,r,network='utility',condition='Collected bag-filter dust return')
  pulse='PU-CH-001-020' if i==1 else 'PU-CH-021-040'
  for tag in [pulse,f'ST-CH-{i:03}',f'PS-CH-{i:03}',f'DPS-CH-{i:03}']:b.rel(tag,'part_of',filt,1,r)
  b.rel(air,'utility_supply_to',pulse,1,r,network='utility',condition='Pulse-cleaning compressed air')
  for n in [i,i+2]:b.rel(f'MD-CH-{n:03}','part_of',stream,1,r)
  b.a(filt,'rated_flow',35900,1,r,'m3/h','Per stream');b.a(pulse,'quantity',20,1,[.677,.047,.97,.433],'valves','Per stream schematic schedule')
 for n in [5]:
  for pre in ['LV','ZSS']:b.rel(f'{pre}-CH-{n:03}','part_of',hopper,1,r)
 b.rel(hopper,'utility_supply_to','RAL-CH-005',1,r,network='utility',condition='Common cyclone dust');b.rel('RAL-CH-005','utility_supply_to','FGD-CH-001',1,r,network='utility',condition='Cyclone dust return')
 for gate in ['FGD-CH-001','FGD-CH-002']:
  for dest in ['EBA-18A','EBA-18B']:b.rel(gate,'utility_supply_to',dest,1,r,network='utility',condition='Selected outlet for recovered dust; not simultaneous flow')
 cross=part(b,DE,'Crossover dampers','functional_assembly',1,r)
 for n in [5,6]:b.rel(f'MD-CH-{n:03}','part_of',cross,1,r)
 b.a(cross,'operating_requirement','MD5/6 closed in normal separate-stream operation; crossover opens only for documented single-stream interchange mode. Routes/positions are available in control details.',1,r)
 b.a(DE,'source_discrepancy','Schematic upper schedule lists5 motorized dampers, while tagged layout/lower schedule and philosophy identify MD-CH-001 through006. Six identities retained without silently editing either source.',1,[.677,.047,.97,.69])
 b.a(air,'source_gap','Schematic connects to compressor house. Shared compressor/dryer data remain plant utility references; dedicated UEE-3 compressor assets are not established.',1,[.357,.461,.631,.77])
 b.finish(out)

def extraction_controls(s,out):
 b=Batch(s,'de_control','crusher-dust-extraction-controls','DE philosophy175280 Rev1 approved16-Oct-2019; normal and two single-stream interchange cases retained separately. '+BASIS)
 for mode,k,fan,pg,rg in [('Normal stream 1',1,1,5,[.14,.467,.94,.85]),('Normal stream 2',2,2,7,[.14,.12,.95,.89]),('Interchange 1',1,2,9,[.14,.12,.95,.91]),('Interchange 2',2,1,11,[.14,.12,.95,.60])]:
  cond='Mode: '+mode
  cross='MD5/6 open; inactive stream inlet/isolation dampers closed' if 'Interchange' in mode else 'MD5/6 closed'
  b.a(DE,'sequence_logic',f'KF-{k} running selects fan{fan} circuit; pressure healthy enables pulsing; running EBA18 feedback directs both dust-return gates; RALs start,1–2min later fan starts; volume damper opens in thirds with motor health checks, then isolation damper and DP check. {cross}.',pg,rg,condition=cond)
  support(b,6 if pg==5 else 8 if pg==7 else 10 if pg==11 else 9,[.14,.12,.95,.91])
  b.rel(f'KF-{k}','control_signal_to',f'FAN-CH-{fan:03}',pg,rg,network='control',condition=cond+'; feeder-running dependency through sequenced local logic, not a direct start wire')
  b.a(DE,'trip_condition','High level in any of five dust hoppers stops the fan/system; DP unhealthy within2–3min stops DE. Feed stop stops selected fan; RALs continue2–3min before stop. Confirm timer set values and copied tags in approved logic.',6 if fan==1 and k==1 else 11 if k==2 and fan==1 else 8 if k==2 else 10,[.14,.12,.95,.91],condition=cond)
 for i in (1,2):
  filt=f'DE-{i} Bag-filter compartment'
  for tag in [f'ST-CH-{i:03}',f'PS-CH-{i:03}',f'DPS-CH-{i:03}']:b.a(tag,'equipment_role',('Sequential pulse controller' if tag.startswith('ST') else 'Pulse-air pressure permissive' if tag.startswith('PS') else 'Filter differential-pressure health check'),3,[.13,.24,.93,.92])
  b.rel(f'PS-CH-{i:03}','control_signal_to',f'ST-CH-{i:03}',5 if i==1 else 7,[.14,.12,.95,.91],network='control',condition='Pressure healthy permits pulsing')
  b.rel(f'DPS-CH-{i:03}','control_signal_to',f'FAN-CH-{i:03}',6 if i==1 else 8,[.14,.12,.95,.91],network='control',condition='DP health check in active mode; commissioned differential setpoint unresolved')
 for n in range(1,6):
  b.rel(f'ZSS-CH-{n:03}','protects_equipment',f'RAL-CH-{n:03}',3,[.13,.24,.93,.92]);b.a(f'LV-CH-{n:03}','trip_condition','High hopper level stops active fan/DE system; threshold not quantified in philosophy.',6,[.14,.12,.95,.91])
 b.a(DE,'source_discrepancy','Philosophy contains copied tags: p6 stop clause says RAL003 where stream1 starts001/002/005; stream2 timer clause mentions PS001; interchange2 stop clause lists001/003/005 where start list is001/002/005. Preserve mode intent and unresolved exact logic; do not execute copied sequences as commissioning instructions.',11,[.14,.12,.95,.91])
 b.a('LCP-1','operator_controls','AUTO normal operation, MANUAL test, interchange modes1/2 for one process stream at a time. Power restoration requires reset before restart; local stop is available.',5,[.14,.26,.95,.565])
 b.finish(out)

def filter_fan(s,out):
 b=Batch(s,'filter','crusher-filter-maintenance','Bag-filter GA175101 Rev4 sheet4; combined twin-compartment crusher-house assembly. '+BASIS)
 r=[.694,.03,.977,.662]
 for i in (1,2):
  f=f'DE-{i} Bag-filter compartment'
  for name,typ in [('Bags and cages','filter_element_group'),('Clean-air plenum','mechanical_component'),('Pulse-air manifold and blast pipes','utility_header'),('Explosion vents','protection_device'),('Inspection doors and access','maintenance_access')]:part(b,f,name,typ,4,r)
  b.a(f+' Bags and cages','component_material','Fire-retardant bags with antistatic treatment;160mm diameter x3660mm length; galvanized cages150mm x3650mm.',4,r)
  b.a(f+' Bags and cages','source_discrepancy','Combined GA says480 bags each compartment and480 in assembly BOM; model2x20x12 and two35900m3/h streams leave count basis ambiguous. Do not infer240 or480 per DE stream without reconciliation.',4,r)
  b.a(f,'operating_range','GA compressed air4–6kg/cm2g; maximum operating temperature60degC; pressure drop150mmWC design value. These are design conditions, not commissioned alarms.',4,r)
  b.a(f,'maintenance_requirement','Bag removal drawing: remove cage with venturi then bags from above; GA shows3500mm headroom over filter. Detailed isolation and cleaning instructions need vendor O&M.',4,[.04,.04,.73,.23])
  for n in [2*i-1,2*i]:
   mo=part(b,f'RAL-CH-{n:03}','Geared motor','electric_motor',4,r);vals(b,mo,[('motor_rated_power',.55,'kW'),('output_speed',25,'rpm'),('motor_voltage',415,'V')],4,r,'GA RAL drive schedule');b.rel(mo,'mechanically_drives',f'RAL-CH-{n:03}',4,r,network='mechanical')
 b.finish(out)
 b=Batch(s,'fan','crusher-id-fan-drive','Fan GA175102 Rev1, vendorF-14011 dated19-Sep-2019; FIO16-Oct-2019; applies to crusher-house DE1/2. '+BASIS)
 r=[.658,.102,.967,.704]
 for i in (1,2):
  f=f'FAN-CH-{i:03}';b.a(f,'equipment_model','CB Doctor MB125 II R0',2,r)
  vals(b,f,[('rated_flow',39500,'m3/h'),('static_pressure',500,'mmWC'),('fan_speed',1354,'rpm')],2,r,'GA duty at50degC')
  drive=part(b,f,'Drive assembly','functional_assembly',2,r)
  mo=part(b,drive,'Motor','electric_motor',2,r);b.a(mo,'motor_rated_power',90,2,r,'kW','4pole frame280SM, GA selection; not installed verification')
  belts=part(b,drive,'V-belts and pulleys','mechanical_component',2,r);rot=part(b,f,'Impeller and shaft','mechanical_component',2,r)
  for a,z in [(mo,belts),(belts,rot)]:b.rel(a,'mechanically_drives',z,2,r,network='mechanical')
  br=part(b,f,'Shaft bearings','bearing',2,r);b.a(br,'equipment_model','Two SKF22217EK bearings in SNH517TL housings.',2,r)
  for name in ['Inspection door','Belt guard','Flexible inlet and outlet connections','Base vibration isolators']:part(b,f,name,'maintenance_access' if name=='Inspection door' else 'mechanical_component',2,r)
  b.a(f,'source_discrepancy','Schematic175100 lists110kW tentative pending GA; this later FIO fan GA selects90kW. Also GA says fan quantity01 despite system1&2 applicability. Retain two process fan identities established by schematic and philosophy; procurement/installed count and motor nameplate remain to verify.',2,[.026,.101,.971,.965])
 b.finish(out)

SPRAY='UEE-3 Local DFDS'
def dfds(s,out):
 b=Batch(s,'dfds','crusher-local-dfds','DFDS175089 Rev1 sheet2, System2; scoped tags distinct from same numbers in System1. '+BASIS)
 r=[.602,.32,.738,.56];table=[.601,.91,.785,.972]
 b.entity(SPRAY,'dfds_system',2,r,HOUSE,'Dry-fog suppression at KF1/2 discharge and their selected receiving points on EBA18A/B.')
 panel=part(b,SPRAY,'LCP-09','local_control_panel',2,r)
 for name,typ in [('PS-09 air pressure switch','pressure_switch'),('UBS-13 on EBA-17A','under_belt_switch'),('UBS-14 on EBA-17B','under_belt_switch')]:part(b,SPRAY,name,typ,2,r)
 head=part(b,SPRAY,'Air and water connection','utility_header',2,r);b.a(head,'assembly_arrangement','System2 main at UEE-3:50NB air,15NB water; each PRU feeds20NB air/15NB water nozzle branches.',2,r)
 for ap,target,role,num in [(35,'KF-1','Discharge',4),(36,'EBA-18A','Receiving from KF-1',9),(37,'EBA-18B','Receiving from KF-1',9),(38,'KF-2','Discharge',4),(39,'EBA-18A','Receiving from KF-2',9),(40,'EBA-18B','Receiving from KF-2',9)]:
  a=f'UEE-3 AP-{ap}';b.entity(a,'spray_application_point',2,table,SPRAY,role+' chute at '+target)
  b.a(a,'scheduled_nozzle_count',num,2,table,'nozzles','Total installed in schedule, not current active count')
  b.rel(a,'sprays_at',target,2,r,condition=role+' interface')
  fas=f'UEE-3 FAS-{ap}';pru=f'UEE-3 PRU-{ap}'
  for tag in [fas,pru]:b.rel(tag,'part_of',a,2,r)
  nozzles=part(b,a,'Atomizing nozzles','spray_nozzle_group',2,r);b.a(nozzles,'quantity',num,2,table,'nozzles','Per application point')
  for x,z in [(head,fas),(fas,pru),(pru,nozzles)]:b.rel(x,'utility_supply_to',z,2,r,network='utility',condition='Separate air and water services through FAS/PRU')
  b.rel(panel,'control_signal_to',fas,2,r,network='control',condition='Local DFDS System2 control')
 b.a(SPRAY,'source_discrepancy','Application schedule misprints UEF-3 (Crusher House); sheet schematic, local panel and piping identify UEE-3. Identical AP/FAS/PRU numbers also occur in DFDS System1; identities are scoped to UEE-3/System2.',2,table)
 b.a(SPRAY,'operating_requirement','Schedule operating column depicts one route case:AP35/36 and38/40 operating;AP37/39 zero. These are route alternatives, not proof that receiving nozzles are absent or live status.',2,table)
 b.finish(out)
 b=Batch(s,'dfds_control','crusher-dfds-permissives','DFDS philosophy175106 Rev0 FIO14-Jan-2019 pp29–31; applicability includes direct bypass ambiguity. '+BASIS)
 for ap,lane,g,page in [(35,'A',None,29),(36,'A','FG-15',30),(37,'A','FG-15',30),(38,'B',None,30),(39,'B','FG-16',30),(40,'B','FG-16',31)]:
  a=f'UEE-3 AP-{ap}';b.a(a,'start_permissive',f'AUTO selected,PS09 compressed air healthy and EBA-17{lane} running with load viaUBS{13 if lane=="A" else 14}'+(f'; {g} position signal required.' if g else '.'),page,[.09,.06,.93,.88])
  b.a(a,'operator_controls','MANUAL selection energizes the local FAS according to philosophy; commissioned permissive bypass behavior is not established.',page,[.09,.06,.93,.88])
 b.a(SPRAY,'source_gap','Philosophy uses EBA17 running-with-load for KF discharge sprays rather than KF feedback, and does not explicitly resolve residual feeder discharge after EBA17 stops or screening/direct-bypass cases. Verify final logic; no automatic substitution is made.',30,[.09,.06,.93,.88])
 b.finish(out)

def utilities(s,out):
 b=Batch(s,'pipe','crusher-service-water','Piping175299 Rev2 FIO16-Sep-2019, UEE3 services routed from UEE2 towards UEF13. '+BASIS)
 r=[.063,.095,.754,.732]
 water=part(b,HOUSE,'Service and drinking water','functional_assembly',1,r,'Separate service-water, potable-water and DFDS services descend through the house.')
 for name,typ in [('Service-water riser and hose boxes','utility_header'),('Drinking-water riser','utility_header'),('Roof water tank','water_tank')]:part(b,water,name,typ,1,r)
 b.a(water+' Roof water tank','storage_capacity',300,1,[.076,.145,.286,.272],'L','Water-tank drawing label; supply category must be checked against final plumbing')
 b.a(water,'assembly_arrangement','Incoming labelled100NB service water and40NB potable water with50NB air/15NB DFDS water; service routes continue through house.',1,r)
 b.a(SPRAY+' Air and water connection','location_description','DFDS services enter from UEE2 and route down to KF and EBA18 spray interfaces; pipe FIO drawing shows connections to UEF13.',1,r)
 b.finish(out)

def common_air(s,out):
 b=Batch(s,'de_design','crusher-shared-extraction-air','DE design basis175099 Rev2, p8; plant service connection, not additional local compressors. '+BASIS)
 supply='CHP DE compressed-air supply'
 b.entity(supply,'compressed_air_system',8,[.115,.708,.936,.794],'Maitree Coal Handling Plant','Shared instrument-grade compressed air for DE pulse cleaning; compressor, dryer and receiver are in the pump-house room near UEF-7.')
 b.a(supply,'location_description','DBR identifies CHP pump house UGA-2 near UEF-7. UGA-2 tag usage elsewhere in corpus differs; this does not merge it with a dozer shed.',8,[.115,.708,.936,.794])
 b.a(supply,'nominal_pressure',5,8,[.115,.708,.936,.794],'kg/cm2','Source range5–6; not an alarm setpoint')
 b.rel(supply,'utility_supply_to',DE+' Compressed-air connection',8,[.115,.708,.936,.794],network='utility',condition='DE shared pulse-cleaning air distribution')
 b.a(supply,'source_discrepancy','DBR p7 specifies heatless desiccant dryer; the corpus also contains a DE refrigeration-dryer GA. Final applicable package, tags and air quality need reconciliation before decomposing this shared utility into installed identities.',7,quote='Desiccant Type (Heat less)')
 b.finish(out)
 b=Batch(s,'sump','crusher-drainage','Sump P&ID175259 Rev3 dated09-Sep-2019. '+BASIS)
 r=[.487,.032,.594,.164]
 sump=part(b,HOUSE,'Drainage sump and pumps','sump_pump_system',1,r,'Local cover drains collect in the UEE3 sump; pumps discharge towards coal runoff collection.')
 b.a(sump,'storage_capacity',5,1,r,'m3','Local2.00x1.50x1.70m pit label; design volume')
 b.a(sump,'assembly_arrangement','Location schedule: one working plus one standby pump at crusher house. Exact SP1 letter suffixes are not resolved on the reviewed location view.',1,[.837,.372,.968,.56])
 for name in ['Duty pump position','Standby pump position']:part(b,sump,name,'sump_pump',1,r)
 part(b,sump,'Level switch and local panel','local_control_panel',1,r)
 b.rel(sump,'utility_supply_to','CHP Coal Run-off Pond',1,[.47,.031,.831,.548],network='utility',condition='Drainage system path; intermediate collection piping retained in full P&ID')
 b.a(sump,'sequence_logic','Level-switch automatic ON/OFF with local manual selector; level setpoints and exact pump duty assignment require final controls.',1,[.624,.894,.821,.926])
 b.finish(out)

def reconcile(s,out):
 b=Batch(s,'isolation','crusher-foundation-reference-scope','GERB175114 common two-set foundation drawing; preserve reference history separately from the two installed-position assemblies. '+BASIS)
 ref='Crusher House Vibration Isolation System (VIS)';r=[.026,.04,.977,.97]
 b.entity(ref,'equipment_design_reference',1,r)
 for a in b.live:
  if a['canonical_subject']==b.ids[ref] and a['predicate']=='part_of' and a['canonical_object']==b.ids[HOUSE]:
   b.retire(a['id'],'Common design for two crusher foundations; per-crusher foundation assemblies now carry the physical membership. This is not a third foundation.',1,r)
 b.a(ref,'equipment_role','Common GERB foundation design applicable to the two EBC crusher foundations; not an additional installed foundation.',1,r)
 b.finish(out)
 b=Batch(s,'dfds','crusher-dfds-instrument-identity','System2 UEE3 inset explicitly labels one PS09 pressure switch; reconcile descriptive duplicate with existing scoped instrument. '+BASIS)
 r=[.602,.32,.738,.56]
 b.ops.append({'op':'merge','source':b.ids[SPRAY+' PS-09 air pressure switch'],'target':b.ids['DFDSS-2 PS-09'],'reason':'Same System2 UEE3 PS09 pressure switch. Keep the pre-existing instrument identity and its schedule facts; descriptive local record was a duplicate.',**b.evidence(2,r)})
 b.rel(SPRAY,'part_of','DFDS System-2',2,r,condition='Local UEE3 branch of the shared DFDS System2; house membership is functional location context')
 for lane,n in [('A',13),('B',14)]:
  b.rel(SPRAY+f' UBS-{n} on EBA-17{lane}','located_at',f'EBA-17{lane}',2,r)
  b.rel(SPRAY+f' UBS-{n} on EBA-17{lane}','control_signal_to',SPRAY+' LCP-09',2,r,network='control',condition='Conveyor running-with-load detection')
 b.rel('DFDSS-2 PS-09','control_signal_to',SPRAY+' LCP-09',2,r,network='control',condition='Compressed-air pressure status')
 b.finish(out)

def control_citations(s,out):
 b=Batch(s,'flow','crusher-control-source-regions','Source readability review of control179162 pp16–17; facts unchanged, focused citations corrected. '+BASIS)
 changes={
  (.11,.18,.91,.4):(15,[.17,.233,.94,.539]),
  (.11,.15,.92,.38):(16,[.17,.307,.94,.407]),
  (.11,.34,.92,.51):(16,[.17,.414,.94,.554]),
  (.11,.16,.92,.51):(16,[.17,.246,.94,.554]),
  (.11,.49,.92,.831):(16,[.17,.641,.94,.87]),
  (.13,.157,.93,.306):(17,[.17,.204,.94,.342]),
  (.11,.642,.92,.893):(16,[.17,.774,.94,.946]),
  (.11,.642,.92,.78):(16,[.17,.774,.94,.797]),
 }
 for a in b.live:
  if 'Control179162 Rev04, pp15' not in a.get('context',{}).get('basis',''):continue
  region=tuple(a['evidence'][0].get('region',[]))
  if region not in changes:continue
  page,r=changes[region]
  b.retire(a['id'],'Corrected focused evidence region to include the complete supporting control clause; engineering claim retained unchanged.',page,r)
  op={'op':'assert','subject':a['canonical_subject'],'predicate':a['predicate'],'context':a['context'],**b.evidence(page,r)}
  op['origin']=a['origin']
  if a.get('canonical_object'):op['object_entity']=a['canonical_object']
  else:op['value']=a['value']
  if a.get('unit'):op['unit']=a['unit']
  b.ops.append(op)
 b.finish(out)

def access_and_airlocks(s,out):
 b=Batch(s,'elevator','crusher-elevator-assembly','Elevator175075 Rev2 GA p1, Beacon SNC1, FIO; landing levels are FFL/TOS, distinct from house TOC. '+BASIS)
 e='Crusher House Passenger and Goods Elevator';r=[.764,.291,.957,.731];parts=[.057,.086,.624,.883];safety=[.633,.211,.758,.386]
 b.ops.append({'op':'alias','entity':b.ids[e],'alias':'SNC-1',**b.evidence(1,r)})
 b.a(e,'equipment_role','SNC-1 passenger-cum-goods electric traction lift serves six crusher-house landings with machinery above the shaft.',1,r)
 vals(b,e,[('rated_capacity',1100,'kg'),('rated_speed',1,'m/s'),('travel_height',34,'m')],1,r,'GA design, not current lifting certification')
 b.a(e,'location_description','UEE3 landings:0.0,7.1,10.7,17.8,23.8,34.0m; GA uses FFL/TOS. House structural TOC values differ by slab/finish datum; do not treat these as conflicting elevations.',1,r)
 drive=part(b,e,'Traction drive assembly','functional_assembly',1,r)
 motor=part(b,drive,'Motor','electric_motor',1,r);vals(b,motor,[('motor_rated_power',15,'kW'),('motor_rated_speed',1440,'rpm'),('motor_voltage',415,'V')],1,r)
 gear=part(b,drive,'Reduction gearbox','gearbox',1,r);b.a(gear,'gear_ratio_nominal',50,1,r,None,'GA gear ratio1/50, U-800')
 sheave=part(b,drive,'Traction sheave','pulley',1,r);b.a(sheave,'component_dimension',660,1,r,'mm','Diameter; five13mm grooves')
 for a,z in [(motor,gear),(gear,sheave)]:b.rel(a,'mechanically_drives',z,1,r,network='mechanical')
 ropes=part(b,e,'Suspension ropes','mechanical_component',1,r);b.a(ropes,'quantity',5,1,r,'ropes');b.a(ropes,'component_dimension',13,1,r,'mm','Main-rope diameter')
 for name,typ in [('Car and automatic doors','functional_assembly'),('Counterweight and guides','mechanical_component'),('Diverter pulley','pulley'),('Governor rope','mechanical_component')]:part(b,e,name,typ,1,parts)
 b.a(e+' Governor rope','component_dimension',8,1,r,'mm','One governor rope')
 b.a(e+' Diverter pulley','component_dimension',450,1,r,'mm','Diameter, one pulley')
 panel=part(b,e,'Control and rescue equipment','local_control_panel',1,r)
 b.a(panel,'equipment_model','ARKEL microprocessor ACV3F control, selective automatic with/without attendant.',1,r)
 for name,typ in [('Automatic rescue device','electrical_component'),('Infrared door protection','sensor'),('Overload detection','sensor'),('Phase failure and reversal protection','protection_relay'),('Emergency alarm and lighting','electrical_component'),('Fireman switch at ground floor','control_switch'),('Intercom','electrical_component')]:part(b,panel,name,typ,1,safety)
 b.a(e,'source_gap','GA lists protective features but does not establish present inspection status, emergency procedures, brake/safety-gear settings or a verified isolation plan. Detailed vendor and commissioned maintenance records remain required.',1,safety)
 b.finish(out)
 b=Batch(s,'airlock','crusher-rotary-airlock-assemblies','RAL175086 Rev1 FIO31-Jul-2019 p1 and review p2: five crusher-house positions; common design applicability, not new RAL identities. '+BASIS)
 spec=[.711,.454,.963,.628];bom=[.344,.652,.619,.892];layout=[.077,.115,.581,.409]
 for i in range(1,6):
  tag=f'RAL-CH-{i:03}';b.a(tag,'rated_capacity',4,1,[.353,.918,.582,.944],'t/h','Common RAL design; crusher-house quantity5 explicitly scheduled')
  b.a(tag,'design_temperature_limit',50,1,spec,'degC');b.a(tag,'operating_requirement','Continuous dust discharge; rotary airlock is not100% leakproof. This is not a positive isolation device.',1,[.344,.52,.965,.63])
  rotor=part(b,tag,'Rotor and housing','mechanical_component',1,bom)
  tip=part(b,rotor,'Detachable spring-steel tips','mechanical_component',1,bom);b.a(tip,'quantity',6,1,bom,'tips');b.a(tip,'component_dimension',.4,1,[.842,.068,.958,.18],'mm','Maximum radial rotor/housing clearance shown in tip detail')
  shaft=part(b,tag,'Rotor shaft and coupling','mechanical_component',1,bom);b.a(shaft,'component_material','EN8 shaft; coupling type not specified.',1,bom)
  bearing=part(b,tag,'Plummer blocks and bearings','bearing',1,bom);b.a(bearing,'quantity',2,1,bom,'bearings');b.a(bearing,'equipment_model','1207K bearing',1,bom)
  part(b,tag,'Stuffing boxes and seals','mechanical_component',1,bom)
  motor=part(b,tag,'Geared motor','electric_motor',1,layout);vals(b,motor,[('motor_rated_power',.55,'kW'),('output_speed',20,'rpm'),('motor_voltage',415,'V')],1,layout,'Common RAL GA175086 Rev1')
  b.rel(motor,'mechanically_drives',shaft,1,layout,network='mechanical');b.rel(shaft,'mechanically_drives',rotor,1,layout,network='mechanical')
  b.a(tag,'source_discrepancy','RAL GA gives20rpm; bag-filter GA lists25rpm for filter RAL drives. GA calls MS fabricated casing/rotor, while review requests wear-resistant lining and vendor reply asks acceptance of MS. Retain the source distinction and verify installed design.',2,[.08,.15,.93,.9])
 b.finish(out)

def airlock_citations(s,out):
 b=Batch(s,'airlock','crusher-airlock-comparison-support','Attach RAL GA and review reply; bag-filter speed remains separately sourced on each applicable geared motor. '+BASIS)
 for a in b.live:
  if a['predicate']!='source_discrepancy' or not str(a.get('value','')).startswith('RAL GA gives20rpm'):continue
  b.retire(a['id'],'Focus this qualification on the RAL GA and reviewer/vendor correspondence. Compare separately sourced output-speed facts on the geared motor.',2,[.08,.15,.93,.9])
  evidence=b.evidence(2,[.08,.15,.93,.9]);evidence['origin']='inferred';evidence['evidence']+=b.evidence(1,[.711,.454,.963,.628])['evidence']
  value='RAL GA states20rpm; compare the separately sourced bag-filter output-speed facts on the applicable geared motors. Review requests wear-resistant lining while vendor reply asks acceptance of MS fabricated casing/rotor. Final installed speed and material remain to verify.'
  b.ops.append({'op':'assert','subject':a['canonical_subject'],'predicate':a['predicate'],'value':value,'context':a['context'],**evidence})
 b.finish(out)

def gauge_scope(s,out):
 b=Batch(s,'scoop','crusher-local-gauge-scope','Crusher scoop P&I distinguishes local indication gauges from protective switches. '+BASIS)
 for i in (1,2):
  co=f'EBC-{i} Drive assembly Scoop coupling PST-1150'
  for name in ['Oil level gauge','Oil temperature gauge','Oil pressure gauge']:
   d=co+' '+name
   for a in b.live:
    if a['canonical_subject']==b.ids[d] and a['predicate']=='protects_equipment':b.retire(a['id'],'Local gauge indicates a condition; P&I does not establish an automatic protective action from this gauge.',2,[.156,.086,.555,.68])
   b.rel(d,'monitors_equipment',co,2,[.156,.086,.555,.68],condition='Local indication only; no automatic trip implied')
 b.finish(out)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--output-name',default='rehearsal');args=parser.parse_args()
 plant=ROOT/'data/plant';ro=sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True)
 version=int(ro.execute("select value from meta where key='version'").fetchone()[0])
 if version!=527:raise RuntimeError(f'Expected reviewedv527, found{version}; reconcile, never replay.')
 for doc in SOURCE.values():
  if hashlib.sha256((plant/'originals'/doc['sha256']).read_bytes()).hexdigest()!=doc['sha256']:raise RuntimeError('Changed original '+doc['name'])
 out=BASE/('accepted' if args.apply else args.output_name);out.mkdir(parents=True,exist_ok=True)
 if (out/'commits.jsonl').exists():raise RuntimeError('Existing run; inspect instead of replaying.')
 backup=BASE/'backup-v527.sqlite3'
 if not backup.exists():
  with sqlite3.connect(backup) as dst:ro.backup(dst)
 if args.apply:s=Store(plant)
 else:
  with sqlite3.connect(out/'plant.sqlite3') as dst:ro.backup(dst)
  s=Store(out)
 ro.close();foundation(s,out)
 for i in (1,2):crusher(s,out,i);scoop(s,out,i);screen(s,out,i)
 for i in (1,2):belt_machine(s,out,i,True);belt_machine(s,out,i)
 controls(s,out);house(s,out);vis(s,out);gates(s,out)
 extraction(s,out);extraction_controls(s,out);filter_fan(s,out);dfds(s,out);utilities(s,out);common_air(s,out);reconcile(s,out);control_citations(s,out);access_and_airlocks(s,out);airlock_citations(s,out);gauge_scope(s,out)
 (out/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
