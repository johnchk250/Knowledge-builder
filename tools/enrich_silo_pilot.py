"""UEE-2 reviewed design enrichment. Default rehearses against an isolated DB.

Run from the audited v510 snapshot; --apply accepts the same source-scoped batches.
No direct canonical SQL writes. Descriptive component names are not field tags.
"""
import argparse, hashlib, json, sqlite3
import enrich_conveyor_tp1_pilot as core
from enrich_conveyor_tp1_pilot import ROOT, Store, stage, commit, validate

DOCS={'flow':'doc_4f2cd96c3b1e413ea4b5','house':'doc_17dab58f999c4939bbc7',
      'extract':'doc_ef73ffa11a1748979909','extract_ga':'doc_40baa8f059a0427f9567',
      'feeder':'doc_396739a89bde48f28f61','gate':'doc_9258f527621741938b79',
      'pipe':'doc_e87ceea2e93c40d7ad8b','dfds_control':'doc_294aacf286d246769e32',
      'de':'doc_84156b4bfaae4e6184fe','de_control':'doc_a786031791b9437d9479',
      'sump':'doc_0453a0a014424f1cae06'}
DOCS['dfds_pid']='doc_bca09d68af9b43e3b633'
core.DOCS.update(DOCS)
HOUSE='Coal Blending Silo House'
DE='Blending Silo EBB-1/EBB-2 Vent-Filter DE System'
DFDS='UEE-2 Local DFDS'
ACCESS='UEE-2 Maintenance access and lifting'
BASIS='Reviewed design document; not field/as-built verification. Component labels without original tags are descriptive.'

class Batch(core.Batch):
 def finish(self,out):
  body={'summary':self.name,'operations':self.ops,'intake_assessment':{
   'route':'mixed','purpose':'Coal blending silo visual assembly implementation: UEE-2 vessels, extractors, feeders, gates and local services.',
   'questions':['What is connected and owned here?','What is the source of this particular component, value or control condition?','Which source qualifications remain unresolved?'],
   'gaps':self.gaps+['Supplemental reviewed pages: '+', '.join(map(str,sorted(self.pages)))+'. All document evidence blocks were triaged as source inventory; only the listed pages support new claims. No exhaustive extraction is claimed.',BASIS],
   'reviewed_evidence_ids':[e['id'] for e in self.ev]}}
  report=validate(self.s,{'summary':self.name,'operations':self.ops},self.doc,self.version,visual_ids=self.visual)
  if report['errors']:raise ValueError(json.dumps(report['errors']))
  (out/(self.name+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  r=stage(self.s,self.doc,body,visual_ids=self.visual,analysis_dir=str(out),expected_version=self.version)
  accepted=commit(self.s,r['proposal_id'])
  rec={'name':self.name,'document_id':self.doc,'base_version':self.version,'result_version':self.s.version(),'operations':len(self.ops),'entities':sum(o['op']=='entity' for o in self.ops),'assertions':sum(o['op']=='assert' for o in self.ops),'pages':sorted(self.pages),'warnings':report['warnings'],'commit':accepted}
  with (out/'commits.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
  print(json.dumps({k:rec[k] for k in ['name','result_version','operations','entities','assertions']}),flush=True)
 def retire(self,aid,reason,page,region):
  self.ops.append({'op':'retire','assertion_id':aid,'reason':reason,**self.evidence(page,region)})

def part(b,parent,name,typ,page,r,role=None):
 label=parent+' '+name;b.entity(label,typ,page,r,parent,role);return label

def foundation(s,out):
 b=Batch(s,'flow','silo-boundaries','Coal flow 175001 Rev8, PDF p55; source design topology. '+BASIS)
 r=[.603,.565,.743,.719]
 b.a(HOUSE,'equipment_role','Store coal in two silos and regulate their extraction rates for blending before the crusher-house conveyors.',5,quote='Coal from EBB-1 and EBB-2 shall be extracted at required blending ratio')
 b.a(HOUSE,'location_description','UEE-2, between the EBA-6/EBA-16 incoming routes and EBA-17A/B to UEE-3 crusher house.',55,r)
 for i in (1,2):
  vessel=f'EBB-{i}';ex=f'EBE-CES-{i}';kf=f'KF-{i+2}';gate=f'FG-{i+12}'
  for name in [vessel,ex,kf,gate]:b.rel(name,'part_of',HOUSE,55,r)
  b.a(vessel,'equipment_role',f'Coal storage vessel feeding {ex}, then {kf}; paired with EBB-{3-i} for controlled blending.',55,r)
  b.a(kf,'equipment_role',f'Carry coal discharged by {ex} to {gate} for the selected EBA-17 conveyor.',55,r)
  b.a(gate,'equipment_role',f'Direct {kf} discharge to selected EBA-17A or EBA-17B.',55,r)
 b.retire('fact_058eba7a58634a37a5bc','Original legend identifies GK drinking water and PC service water; earlier hoist/ventilation interpretation was incorrect.',55,[.048,.715,.245,.76])
 b.a(HOUSE,'operating_requirement','Coal-flow service badges: GK drinking water, PC service water and HDD dry-fog dust suppression. Badges do not define installed piping routes.',55,[.048,.715,.245,.76])
 b.finish(out)

def extractors(s,out,i):
 ex=f'EBE-CES-{i}';v=f'EBB-{i}';kf=f'KF-{i+2}'
 b=Batch(s,'extract',f'{ex}-mechanism','Silo extractor philosophy 175115 Rev1 / L&T Rev2, approved 30-Apr-2019. RE-1/RE-2 design applied to the two corresponding CBSH extractors; vessel input data remains qualified. '+BASIS)
 tech=[.17,.333,.93,.827];construct=[.15,.476,.93,.827];lube=[.18,.133,.93,.25]
 # RE-1/2 are vendor design designations, not two additional installed extractors.
 ref=f'RE-{i}'
 for a in b.live:
  if a.get('canonical_subject')==b.ids[ref] and a['predicate'] in ('instance_of','part_of'):
   b.retire(a['id'],'Vendor RE designation retained as a design reference; do not project an additional installed extractor beside EBE-CES.',4,tech)
 b.entity(ref,'equipment_design_reference',4,tech)
 b.rel(ref,'design_detail_applies_to',ex,4,tech,origin='inferred',condition='Corresponding numbered CBSH vendor design; installed nameplate crosswalk not field verified')
 b.a(ref,'source_gap','RE-1/RE-2 designate the paired vendor extractor design. Model applicability to EBE-CES-1/2 is retained without asserting a verified nameplate alias or adding two physical machines.',4,tech)
 b.a(ex,'equipment_role','A rotating blade sweeps coal from around the pressure cone into a rotating tubular chute above the belt feeder. Two geared drives share one speed reference.',4,[.17,.20,.93,.316])
 for key,val,unit in [('rated_capacity',1250,'t/h'),('design_capacity',1375,'t/h'),('minimum_adjustable_capacity',250,'t/h'),('maximum_adjustable_capacity',1375,'t/h'),('minimum_blade_speed',2,'rpm'),('maximum_blade_speed',9,'rpm')]:b.a(ex,key,val,4,tech,unit)
 b.a(ex,'assembly_arrangement','Rotary flange-mounted beneath silo; continuous rotation. Vendor designates the pair RE-1 and RE-2.',4,tech)
 for ref in ['Coal Silo Extractors RE-1 and RE-2','CBSH Coal Silo Extraction System']:b.rel(ref,'design_detail_applies_to',ex,4,tech,condition='Paired CBSH extractor design reference; not a separate installed machine.',origin='inferred')
 cone=part(b,ex,'Pressure cone and support arms','pressure_relief_cone',5,construct,'Relieve the coal load above the reclaim platform; four radial arms support the cone on the silo wall.')
 b.a(cone,'quantity',4,5,construct,'arms',condition='Equispaced radial support arms, one providing internal access')
 b.a(cone,'maintenance_requirement','One support arm incorporates blade-maintenance access; source discusses access with filled silo. This records design access, not a work permit or isolation procedure.',5,construct)
 plat=part(b,ex,'Reclaim platform','reclaim_platform',5,construct,'Support the reclaiming zone and its central coal discharge opening.')
 blade=part(b,ex,'Rotating blade','extractor_blade',5,construct,'Sweep coal inward to the central opening; rotates with the tubular chute.')
 b.a(blade,'component_dimension',4400,4,tech,'mm',condition='Wheel diameter');b.a(blade,'quantity',1,4,tech,'blade',condition='Per extractor')
 b.a(blade,'component_material','Blade liner: Hardox 400 / JFE Everhard / QUARD 400 / ABREX 400 / XAR 400 / Dilidur 400 or equivalent; supplier selection not established.',4,tech)
 sleeve=part(b,ex,'Adjusting sleeve','mechanical_component',5,construct,'Adjust the depth of coal swept above the reclaim platform.')
 b.a(sleeve,'component_dimension',350,5,construct,'mm','Minimum height above platform');b.a(sleeve,'component_dimension',450,5,construct,'mm','Maximum height above platform')
 chute=part(b,ex,'Rotating tubular chute','chute',5,construct,'Carry swept coal through the rotating tube to the belt feeder below.')
 outlet=part(b,chute,'Conical outlet','chute',5,construct)
 bearing=part(b,ex,'Slew bearing and external gear','slew_bearing',5,construct,'Common geared rotating support driven by two pinions.')
 seal=part(b,ex,'Labyrinth seal','mechanical_component',6,lube,'Lubricated sealing arrangement listed with the slew bearing and pinion bearings.')
 for a,z in [(blade,chute),(chute,outlet),(outlet,kf)]:b.rel(a,'material_flow_to',z,5,construct,network='material')
 for z in [blade,chute]:b.rel(bearing,'mechanically_drives',z,5,construct,network='mechanical')
 l=part(b,ex,'Automatic lubrication','lubrication_system',6,lube,'Automatic centralized lubrication to slew raceway, drive pinion bearings and labyrinth seal; sequenced by an inbuilt controller.')
 b.a(l,'source_gap','Reviewed GA and philosophy identify the lubrication destinations but do not establish pump model, lubricant grade, dosage, cycle setting or a separate hydraulic dust-seal circuit.',6,lube)
 for z in [bearing,seal]:b.rel(l,'utility_supply_to',z,6,lube,network='utility',condition='Automatic lubrication; medium and dose not specified here')
 for d in (1,2):
  drive=part(b,ex,f'Drive assembly {d}','functional_assembly',5,construct,'One of two electromechanical drive trains acting on the same external slew gear; numbering is descriptive.')
  motor=part(b,drive,'Motor','electric_motor',4,tech)
  coupling=part(b,drive,'Coupling','coupling',4,tech)
  gear=part(b,drive,'Helical gearbox','gearbox',5,construct)
  pinion=part(b,drive,'Pinion and bearings','mechanical_component',5,construct)
  for key,val,u in [('motor_rated_power',55,'kW'),('motor_speed',1500,'rpm'),('motor_voltage',415,'V')]:b.a(motor,key,val,4,tech,u)
  b.a(motor,'operating_requirement','Motor voltage tolerance +/-10%; both motors run from a common VFD output bus.',4,tech)
  for a,z in [(motor,coupling),(coupling,gear),(gear,pinion),(pinion,bearing)]:b.rel(a,'mechanically_drives',z,5,construct,network='mechanical',condition='Electromechanical motor/coupling/gear drive to pinion and external slew gear')
  b.rel(l,'utility_supply_to',pinion,6,lube,network='utility',condition='Lubricates drive pinion bearings')
  b.a(drive,'source_gap','Gearbox ratio, coupling model, bearing part numbers and installed motor identification are not established by these reviewed pages.',5,construct)
 for key,val,u,c in [('vendor_hopper_capacity_input',1000,'t','Extractor input data; not independent vessel certification'),('vendor_hopper_top_diameter_input',15.5,'m','Extractor input data'),('vendor_hopper_bottom_diameter_input',4.5,'m','At reclaim platform; extractor input'),('vendor_hopper_height_input',16.97,'m','From T.O.T., as printed'),('material_bulk_density_design',.8,'t/m3','For volume calculation'),('material_bulk_density_design',1.1,'t/m3','For structural design and power calculation'),('design_temperature_limit',41,'degC','Maximum coal temperature input, not alarm/trip setting'),('maximum_moisture_input',24,'%','Coal design input')]:b.a(ex,key,val,5,[.17,.125,.925,.425],u,c)
 b.a(ex,'operating_requirement','Vendor operational note: two blade revolutions every 24 hours during shutdown/plant stoppage to avoid material consolidation.',6,[.19,.275,.94,.375])
 b.a(ex,'operating_requirement','Vendor note: maintain minimum coal bed height of 700 mm to avoid spillage during filling; no level-switch setting is established by this note.',6,[.19,.275,.94,.375])
 b.finish(out)

def extractor_controls(s,out,i):
 ex=f'EBE-CES-{i}';kf=f'KF-{i+2}'
 b=Batch(s,'extract',f'{ex}-controls','Extractor philosophy 175115 Rev1 / L&T Rev2 pp6–8; mode-specific documented design conditions. '+BASIS)
 r=[.17,.417,.94,.62];vfd=part(b,ex,'Common VFD','variable_frequency_drive',6,r,'One six-pulse VFD per extractor; common output bus feeds both motors with the same speed reference.')
 b.a(vfd,'quantity',1,6,r,'No.','Per extractor, two in the plant pair');b.a(vfd,'assembly_arrangement','Both motor branches connected to a common output bus; each motor has dedicated overload protection.',6,r)
 b.a(vfd,'location_description','Philosophy locates VFD panel in silo building; consult the separately recorded CBSH review reply concerning the MCC near DS Pump House-2.',6,r)
 for d in (1,2):
  motor=ex+f' Drive assembly {d} Motor';relay=part(b,vfd,f'Motor {d} overload relay','protection_device',6,r)
  b.rel(vfd,'electrical_supply_to',motor,6,r,network='electrical',condition='Common VFD output bus; individual overload relay per motor')
  b.rel(relay,'protects_equipment',motor,6,r)
  b.rel(relay,'control_signal_to',ex,6,r,network='control',condition='Motor overload not operated is a permissive in each mode')
 lcs=part(b,ex,'Local control station','local_control_panel',7,[.20,.13,.94,.23],'Operate the extractor locally or in maintenance mode; located near the extractor.')
 for parent in [vfd,lcs]:
  stop=part(b,parent,'Emergency stop','protection_device',7,[.24,.24,.93,.355]);b.rel(stop,'control_signal_to',ex,7,[.24,.24,.93,.355],network='control',condition='Emergency stop not activated required in remote, local and maintenance modes')
 for mode,p,rng,req,controls in [
  ('Remote',6,[.20,.667,.94,.864],f'{kf} running; remote selected; VFD and LCS emergency stops not activated; VFD healthy; motor overloads not operated.','Plant control supplies 4–20 mA speed reference; CCR monitors downstream belt-scale flow and adjusts reference.'),
  ('Local',7,[.20,.13,.94,.51],f'{kf} running; local selected; VFD and LCS emergency stops not activated; VFD healthy; motor overloads not operated; plant-control local-operation permissive.','LCS speed increase/decrease, forward start, emergency stop and speed display; feeder-running and plant-permissive indications.'),
  ('Maintenance',7,[.20,.529,.94,.807],'Maintenance selected; VFD and LCS emergency stops not activated; VFD healthy; motor overloads not operated.','LCS speed increase/decrease, forward AND reverse start, emergency stop and speed display. The listed maintenance permissives omit feeder-running and plant local-operation permission; this is a design mode description, not an instruction to bypass isolation.')]:
  b.a(ex,'start_permissive',req,p,rng,condition='Mode: '+mode)
  b.a(ex,'operator_controls',controls,p,rng,condition='Mode: '+mode)
 b.rel(kf,'control_signal_to',ex,6,[.20,.765,.94,.864],network='control',condition='Feeder running required in Remote and Local modes; maintenance mode has its own listed conditions')
 b.a(vfd,'control_interface','To CCR: VFD healthy, motor overload, emergency stop, remote/local selections (potential-free); current and speed (4–20 mA). From CCR: feeder-running and local permission (potential-free), remote speed reference (4–20 mA).',8,[.18,.132,.90,.523])
 b.a(ex,'source_discrepancy','Earlier review response broadly lists a reverse pushbutton for local operation; revised main text separates Local forward start from Maintenance forward/reverse. Keep mode-specific main-text conditions and confirm commissioned logic.',7,[.20,.13,.94,.807])
 b.finish(out)

def extractor_ga(s,out):
 b=Batch(s,'extract_ga','extractor-GA-and-access','Extractor GA 175116 drawing sheet1 plus review sheets2–3; indicative civil/electrical arrangements and client-confirmation dimensions retained. '+BASIS)
 for i in (1,2):
  ex=f'EBE-CES-{i}';r=[.46,.813,.718,.957]
  for name in ['Rotating blade','Rotating tubular chute','Reclaim platform']:
   b.a(ex+' '+name,'component_material','10 mm wear liner: Hardox 400 / JFE Everhard / QUARD 400 / ABREX 400 / XAR 400 / Dilidur 400 or equivalent.',1,r)
  b.a(ex+' Pressure cone and support arms','component_material','Pressure cone liner 10 mm SS409 or equivalent; structural material IS2062:2011 E250-BR.',1,r)
  b.a(ex+' Slew bearing and external gear','assembly_arrangement','Single-row ball bearing with external pinion engagement; GA detail D1 also shows a slew-gear guard.',1,[.721,.55,.874,.709])
  guard=part(b,ex+' Slew bearing and external gear','Gear guard','mechanical_component',1,[.72,.556,.862,.705])
  b.a(ex+' Rotating tubular chute','maintenance_requirement','Lower part of tubular chute is removable for access; GA detail D2 includes sealing in BTL scope.',1,[.858,.54,.959,.704])
  b.a(ex,'location_description',f'Below EBB-{i}; extractor support near EL+16.029 m, belt-feeder floor EL+12.000 m in extractor GA. Civil/electrical arrangement is indicative.',1,[.448,.23,.935,.526])
  b.a(ex,'source_gap','GA lists automatic lubrication for slew bearing and drives but gives no complete hydraulic dust-seal circuit requested in philosophy review. Treat that circuit and its settings as unresolved.',1,r)
  b.a(ex+' Common VFD','source_discrepancy','Extractor GA indicates a panel enclosure between silos near EL+17.500 m. CBSH review p7 instead states an air-conditioned MCC room near DS Pump House-2; installed panel location remains unverified.',1,[.604,.296,.713,.437])
 b.finish(out)

def house(s,out):
 b=Batch(s,'house','CBSH-vessels-place-and-access','CBSH GA 175040 Rev4 sheets1–6, November2019 issue, with p7 review replies. Elevations use local building datum: FFL +0.000 = RL+5.60 m. '+BASIS)
 for i in (1,2):
  v=f'EBB-{i}';ex=f'EBE-CES-{i}';kf=f'KF-{i+2}';gate=f'FG-{i+12}'
  b.a(v,'rated_capacity',1000,1,[.654,.17,.876,.225],'t','CBSH elevation capacity annotation, per silo; design value')
  b.a(v,'location_description','Inside UEE-2; silo centres 16 m apart. Roof/filling floor EL+34.500 m; cone/support access plans EL+21.900 and +17.500 m. Local building datum, not site RL.',1,[.181,.183,.509,.527])
  shell=part(b,v,'Shell and sloping liner','mechanical_component',6,[.176,.897,.43,.956],'Steel vessel shell and wear lining around the stored coal.')
  b.a(shell,'component_material','Shell and necessary stiffeners: 10 mm IS2062 or equivalent. Sloping-surface liner: 6 mm stainless steel SS316 or equivalent.',6,[.176,.897,.43,.956])
  inst=part(b,v,'Level and temperature instruments','functional_assembly',6,[.176,.886,.437,.917],'Design provision for level indication and silo temperature detection; installed tags and settings require confirmation.')
  for name,typ in [('Level indication','level_sensor'),('Temperature detector','temperature_sensor')]:
   dev=part(b,inst,name,typ,6,[.176,.886,.437,.917]);b.rel(dev,'monitors_equipment',v,6,[.176,.886,.437,.917])
   b.a(dev,'source_gap','GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.',6,[.176,.886,.437,.917])
  b.a(inst+' Level indication','assembly_arrangement','GA note: maximum and minimum position level indication; review p7 replies continuous level monitoring included. Instrument technology and detailed channel count remain unresolved.',6,[.176,.886,.437,.917])
  bypass=part(b,v,'Emergency bypass chute','chute',4,[.18,.153,.49,.34],'Emergency coal evacuation branch shown beside the extractor.')
  rod=part(b,bypass,'Rod gate','rod_gate',7,[.49,.31,.919,.44])
  b.a(bypass,'source_gap','Bypass chute and rod gate are documented; discharge endpoint and operating/isolation procedure are not established by these reviewed views.',4,[.18,.153,.49,.34])
  access=part(b,v,'Manholes and access openings','mechanical_component',1,[.646,.261,.904,.403])
  b.a(access,'location_description','Manhole access at silo side; pressure-cone internal access through support-arm opening shown on extractor GA.',1,[.646,.261,.904,.403])
  b.a(kf,'location_description','Belt feeder at floor EL+12.000 m TOC, pulley working point near +13.500 m; local CBSH datum.',5,[.059,.442,.604,.803])
  b.a(gate,'location_description','Below belt feeder, gate platform EL+6.200 m TOS; discharges to EBA-17A/B near ground floor.',5,[.059,.442,.604,.803])
  b.a(ex+' Common VFD','location_description','CBSH review reply: VFD panel in air-conditioned MCC room near DS Pump House-2.',7,[.487,.428,.941,.475])
  b.a(ex+' Common VFD','source_discrepancy','CBSH review reply differs from extractor GA/philosophy showing a silo-building panel. Retain both source locations; verify latest electrical GA and field installation.',7,[.487,.428,.941,.475])
 b.entity(ACCESS,'maintenance_access_assembly',6,[.053,.248,.325,.5],HOUSE,'Lifting, landing and access provisions for silo-house conveyors, extractors, feeders and gates.')
 for tag,cap,qty,elev,role in [('EH-1',10,1,42,'EBA-16A/B and 6A/B head/snub pulleys, drives and belt drums'),('EH-2',5,1,42,'Incoming conveyor head and snub pulleys'),('EH-3',3,1,16.3,'KF-3/4 head, tail and snub pulleys, drives and belt drums'),('MH-1',2,1,33.1,'EBA-16A/B take-up pulleys'),('MH-2',7.5,2,20.2,'EBA-16A/B counterweight frames'),('MH-3',2,1,33.1,'EBA-6A/B take-up pulleys'),('MH-4',10,1,15.2,'EBA-6A/B counterweight frames'),('MH-5',3,1,16.3,'KF-3/4 pulleys and take-up frame'),('MH-6',2,2,10.4,'FG-13/14 actuators'),('MH-7',2,1,5.2,'EBA-17A/B tail pulleys')]:
  hoist=b.entity('UEE-2 '+tag,'hoist',6,[.053,.248,.324,.398],ACCESS,role)
  b.a(hoist,'rated_capacity',cap,6,[.053,.248,.324,.398],'t','Per hoist in schedule, not a lifting procedure');b.a(hoist,'quantity',qty,6,[.053,.248,.324,.398],'No.','Schedule quantity for this designation')
  b.a(hoist,'location_description',f'Monorail bottom elevation +{elev:.3f} m (BOMR), local building datum.',6,[.053,.248,.324,.398])
 for i,tags in [(1,'H-5/H-6'),(2,'H-7/H-8')]:
  hook=b.entity('UEE-2 '+tags+' lifting hooks','mechanical_component',6,[.053,.418,.263,.50],ACCESS,f'Handle motors of extractor {i}.')
  b.a(hook,'rated_capacity',2.5,6,[.053,.418,.263,.50],'t','Per hook, source schedule');b.rel(hook,'serves_equipment',f'EBE-CES-{i}',6,[.053,.418,.263,.50])
 b.a(ACCESS,'maintenance_requirement','GA indicates removable guardrails at openings, guarded floor openings, hoist maintenance platforms and common motor/belt-drum landing areas.',6,[.174,.624,.449,.712])
 b.finish(out)

def feeder(s,out,k):
 tag=f'KF-{k}';b=Batch(s,'feeder',tag+'-physical-assembly','Feeder GA 175031 Rev1; actual drawing title specifies KF-3/4 at CBSH although imported filename says feeder1/2. GA table and dimension differences are preserved. '+BASIS)
 dr=[.811,.17,.98,.291];me=[.809,.29,.98,.70];prot=[.809,.677,.98,.708]
 d=part(b,tag,'Drive assembly','functional_assembly',1,dr,'Motor through delay-filled fluid coupling, bevel-helical gearbox and low-speed geared coupling to the head pulley; brake on drive train.')
 m=part(b,d,'Main motor','electric_motor',1,dr)
 for key,val,u in [('motor_rated_power',45,'kW'),('motor_speed',1470,'rpm'),('motor_voltage',3.3,'kV')]:b.a(m,key,val,1,dr,u)
 b.a(m,'assembly_arrangement','TEFC squirrel-cage induction motor, 3-phase 3-wire AC. Table labels 1470 rpm as speed (synch.).',1,dr)
 c=part(b,d,'Fluid coupling SDFC 370','coupling',1,dr);g=part(b,d,'Gearbox B3 225','gearbox',1,dr);low=part(b,d,'Low-speed geared coupling RG-08','coupling',1,dr);br=part(b,d,'Thruster brake','brake_assembly',1,dr)
 for entity,model in [(c,'SDFC 370 (Premium)'),(g,'B3 225'),(low,'RG-08 (GBM)'),(br,'EBTM 300/H (Electromach)')]:b.a(entity,'model_number',model,1,dr)
 b.a(g,'gear_ratio_nominal',34.7,1,dr);b.a(g,'assembly_arrangement','Bevel helical',1,dr)
 b.a(c,'assembly_arrangement','Delay-filled coupling with diameter 250 mm brake drum; no scoop actuator or external oil-cooler circuit is established by this GA.',1,dr)
 b.a(br,'source_discrepancy','GA coupling row gives brake drum diameter 250 mm while brake model row says EBTM 300/H; reconcile brake GA/drive schedule before selecting spares.',1,dr)
 mech=part(b,tag,'Belt and mechanical assemblies','functional_assembly',1,me)
 belt=part(b,mech,'Conveyor belt','conveyor_belt',1,[.809,.29,.98,.357]);b.a(belt,'belt_width',1600,1,[.809,.29,.98,.357],'mm');b.a(belt,'belt_length',18.124,1,[.809,.29,.98,.357],'m','GA endless length per feeder, not combined purchasing quantity')
 b.a(belt,'assembly_arrangement','NN-630/4, FR cover, top/bottom cover 5/2 mm.',1,[.809,.29,.98,.357])
 head=None
 for name,dia in [('Head pulley',630),('Snub pulley',500),('Tail pulley',500)]:
  pulley=part(b,mech,name,'pulley',1,[.809,.367,.98,.43]);b.a(pulley,'quantity',1,1,[.809,.367,.98,.43],'No.','Per feeder');b.a(pulley,'component_dimension',dia,1,[.809,.367,.98,.43],'mm','Diameter');b.a(pulley,'component_dimension',1800,1,[.809,.367,.98,.43],'mm','Face width');b.a(pulley,'component_dimension',2300,1,[.809,.367,.98,.43],'mm','Bearing centres')
  b.a(pulley,'assembly_arrangement','12 mm rubber lagging; head herringbone/diamond groove, snub and tail plain rubber.',1,[.809,.367,.98,.43])
  if name=='Head pulley':head=pulley
 for a,z in [(m,c),(c,g),(g,low),(low,head),(head,belt)]:b.rel(a,'mechanically_drives',z,1,dr if z!=belt else [.809,.29,.98,.43],network='mechanical')
 b.rel(br,'acts_on',c,1,dr,network='mechanical',condition='Drive brake drum shown with high-speed coupling')
 for name,q,desc in [('Impact idlers',13,'3-roll pick type, 20 degree trough, 159 mm tube, 190 mm outside diameter, 400 mm pitch'),('Carrying idlers',2,'3-roll pick type, 20 degree trough, 159 mm tube'),('Return idler',1,'10 degree trough, 159 mm tube'),('Deflector rollers',2,'219 mm diameter by 1800 mm face')]:
  n=part(b,mech,name,'idler_group',1,[.809,.419,.98,.574]);b.a(n,'quantity',q,1,[.809,.419,.98,.574],'No.','GA per feeder, sets/assemblies as listed, not individual rollers in an idler set');b.a(n,'assembly_arrangement',desc,1,[.809,.419,.98,.574])
 take=part(b,mech,'Screw take-up','take_up_assembly',1,[.809,.615,.98,.651]);b.a(take,'component_dimension',200,1,[.809,.615,.98,.651],'mm','Travel');b.a(take,'assembly_arrangement','Screw take-up with mark-up scale; no gravity counterweight listed.',1,[.809,.615,.98,.651])
 for name,role in [('Primary scraper','Spring loaded at discharge pulley'),('Secondary scraper','Spring loaded at discharge pulley'),('V-plough scraper','Internal scraper near tail pulley')]:
  z=part(b,mech,name,'belt_scraper',1,[.809,.65,.98,.682],role);b.a(z,'quantity',1,1,[.809,.65,.98,.682],'No.','Per feeder')
 skirt=part(b,mech,'Skirt and hood','mechanical_component',1,[.809,.575,.98,.614]);b.a(skirt,'assembly_arrangement','Table: 5.4 m skirt, 20 mm Hardox400 with 10 mm cover plate. Elevation separately marks skirt 6400 mm.',1,[.809,.575,.98,.614])
 protect=part(b,tag,'Belt protection devices','functional_assembly',1,prot)
 for name,typ,count,u,loc in [('PCS','pull_cord_switch_group',1,'pair','Both sides'),('BSS','belt_sway_switch_group',1,'pair','Both sides'),('ZSS','zero_speed_switch',1,'No.','On tail pulley')]:
  z=part(b,protect,name,typ,1,prot);b.a(z,'quantity',count,1,prot,u,'Per belt feeder');b.a(z,'location_description',loc,1,prot);b.rel(z,'protects_equipment',tag,1,prot)
  if u=='pair':b.a(z,'individual_device_count',2,1,prot,'devices','Derived: one pair = two individual devices',origin='inferred')
 b.a(tag,'source_discrepancy','GA table gives 8.000 m horizontal/profile length while its elevation dimensions pulley centres 8500 mm; prior power calculation uses 17 m horizontal length. Do not treat these as one reconciled length.',1,[.084,.032,.981,.171])
 b.a(tag,'source_discrepancy','GA specifies screw take-up, 210 degree wrap and skirt 5.4 m (elevation 6.4 m); prior calculation uses vertical-gravity take-up, 180 degree wrap and 14.5 m skirt. Calculation facts remain design-case records, not confirmed installed geometry.',1,[.809,.11,.98,.67])
 b.a(tag,'source_gap','Drive vendor part details, brake setting, lubricant grades and commissioned PCS/BSS/ZSS settings require their applicable vendor and field records.',1,dr)
 b.finish(out)

def gates(s,out):
 b=Batch(s,'gate','FG13-FG14-Type4-assemblies','Flap gate GA 175065 Rev2, sheet4 Type4 explicitly scheduled for KF-3/4 at UEE-2; do not copy another flap-gate type. '+BASIS)
 r=[.735,.493,.97,.706]
 for k in (13,14):
  tag=f'FG-{k}';b.a(tag,'assembly_arrangement','Type4 motorised flap gate, 50 degree travel with limit switches on both sides.',4,[.54,.227,.687,.383])
  cas=part(b,tag,'Casing and inspection doors','chute',4,r);flap=part(b,tag,'Flap and shaft','mechanical_component',4,r);arm=part(b,tag,'Lever arm','mechanical_component',4,r)
  b.a(cas,'component_material','20 mm Hardox400 chute casing; two hinged inspection doors, 350×450 mm openings.',4,r)
  b.a(flap,'component_material','Flap 20 mm Hardox400 with 10 mm IS2062 ribs; shaft EN8/C40, 150 square / diameter135 as dimensioned.',4,r)
  bearings=part(b,tag,'Plummer blocks and seals','mechanical_component',4,r);b.a(bearings,'quantity',2,4,r,'sets','Per gate');b.a(bearings,'model_number','SNA530; 22230CCK/W33 bearing; H3130 sleeve; 2 FRB 16.5/270 locating rings',4,r);b.a(bearings,'assembly_arrangement','Felt shaft seals; 12 mm IS2062 seal plate.',4,r)
  act=part(b,tag,'Linear actuator','electric_actuator',4,r,'Move gate through lever arm and shaft; travel and thrust dependent limits protect the mechanism.')
  b.a(act,'model_number','PREPEC P5 (Model B)',4,r);b.a(act,'component_dimension',650,4,r,'mm','Rated stroke, adjustable up to100 mm from each end');b.a(act,'actuator_speed',30,4,r,'mm/s');b.a(act,'rated_thrust_source',5600,4,r,'kg','Source prints thrust in kg; no silent force-unit conversion')
  motor=part(b,act,'Motor','electric_motor',4,r);b.a(motor,'motor_rated_power',7.5,4,r,'kW')
  wheel=part(b,act,'Removable handwheel','mechanical_component',4,r);b.a(wheel,'component_dimension',500,4,r,'mm','Diameter');b.a(wheel,'operating_requirement','Manual-operation attachment with electrical interlocking.',4,r)
  limit=part(b,act,'Travel and thrust limits','protection_device',4,r);b.rel(limit,'protects_equipment',act,4,r)
  for a,z in [(motor,act),(act,arm),(arm,flap)]:b.rel(a,'mechanically_drives',z,4,r,network='mechanical')
  b.a(act,'operating_requirement','15 operations per hour with 10 consecutive switchings at rated load and thrust, per vendor BOM.',4,r)
  b.a(tag,'source_gap','Commissioned travel/thrust settings and direction-to-destination field checks are not provided by this mechanical GA.',4,r)
 b.finish(out)

def dfds(s,out):
 b=Batch(s,'dfds_pid','UEE2-DFDS-applications','DFDS P&ID 175089 Rev1 sheet2, System2 and UEE-2 AP schedule. Operating nozzle column describes the design scenario, not present state. '+BASIS)
 area=[.418,.03,.607,.309];tab=[.60,.588,.776,.69]
 b.entity(DFDS,'dfds_system',2,area,HOUSE,'Ten local spray applications suppress dust at incoming conveyor discharges, belt-feeder discharges and EBA-17 receiving points.')
 b.rel('DFDS System-2','utility_supply_to',DFDS,2,[.416,.031,.976,.31],network='utility',condition='Air and water branches from shared System2 pump/compressor house; local subsystem only')
 b.a(DFDS,'scheduled_nozzle_count',60,2,tab,'nozzles','Sum of ten UEE-2 application totals: six groups of4 plus four groups of9',origin='inferred')
 for j,dest,zone,n in [(1,'EBA-16A','discharge',4),(2,'KF-3','discharge',4),(3,'EBA-17A','receiving',9),(4,'EBA-17B','receiving',9),(5,'EBA-16B','discharge',4),(6,'KF-4','discharge',4),(7,'EBA-17A','receiving',9),(8,'EBA-17B','receiving',9),(9,'EBA-6A','discharge',4),(10,'EBA-6B','discharge',4)]:
  ap=b.entity(f'UEE-2 AP-{j:02}','spray_application_point',2,tab,DFDS,f'Dust suppression at {dest} {zone}; application numbering belongs to DFDS System2.')
  b.a(ap,'scheduled_nozzle_count',n,2,tab,'nozzles','Application total in P&ID; not a live operating count')
  b.a(ap,'location_description',f'{dest} {zone} interface inside UEE-2.',2,tab)
  b.rel(ap,'sprays_at',dest,2,tab)
  for kind in ['FAS','PRU']:b.rel(f'UEE-2 {kind}-{j}','part_of',ap,2,area)
  b.rel(f'UEE-2 PRU-{j}','utility_supply_to',ap,2,area,network='utility',condition='Regulated air and water to spray headers')
  b.a(ap,'source_gap','Schedule total is established. Individual nozzle serial numbers, field condition and commissioned pressures remain unverified.',2,tab)
 b.a(DFDS,'source_discrepancy','P&ID shows LCP-02 above the EBA-16A / KF-3 branch and LCP-01 above the EBA-6 branch; philosophy pp21–23 labels AP01–04 LCP01 and AP05–08 LCP02. Preserve source-specific assignments; verify wiring before treating them as installed panel allocation.',2,area)
 b.finish(out)

def piping(s,out):
 b=Batch(s,'pipe','UEE2-DFDS-piping-and-water','UEE-2 piping layout 175298 Rev2, FIO16-Sep-2019. Layout routing and branch services; not commissioned settings. '+BASIS)
 for j,page,r,level in [(1,3,[.079,.501,.257,.765],34.5),(2,3,[.416,.518,.66,.788],12),(3,1,[.287,.711,.621,.909],0),(4,1,[.287,.711,.621,.909],0),(5,2,[.747,.345,.963,.574],34.5),(6,3,[.416,.518,.66,.788],12),(7,1,[.645,.711,.765,.909],0),(8,1,[.645,.711,.765,.909],0),(9,2,[.747,.078,.963,.338],34.5),(10,3,[.257,.51,.414,.777],34.5)]:
  ap=f'UEE-2 AP-{j:02}';fas=f'UEE-2 FAS-{j}';pru=f'UEE-2 PRU-{j}'
  b.a(ap,'location_description',f'Local spray branch shown at floor EL+{level:.3f} m in piping plans (local CBSH datum); exact mounting follows the referenced views.',page,r)
  headers=part(b,ap,'Air and water headers','spray_header',page,r,'Paired air/water header branches supplying atomising nozzles.')
  b.a(headers,'assembly_arrangement','20 NB air and15 NB water branch to the application; source drawings distinguish upstream larger mains.',page,r)
  b.rel(pru,'utility_supply_to',headers,page,r,network='utility')
  nozzles=part(b,headers,'Atomising nozzles','spray_nozzle_group',2,[.042,.404,.238,.485],'Air and water meet at the spray nozzles fixed around the hood/skirt interface.')
  b.rel(headers,'utility_supply_to',nozzles,2,[.042,.404,.238,.485],network='utility')
  for medium in ['Air','Water']:
   sol=part(b,fas,medium+' solenoid valve','solenoid_valve',page,r);reg=part(b,pru,medium+' regulating branch','pressure_regulating_unit',page,r)
   b.rel(sol,'utility_supply_to',reg,page,r,network='utility',condition=medium+' branch');b.rel(reg,'utility_supply_to',headers,page,r,network='utility',condition=medium+' branch')
 b.entity('UEE-2 Service and drinking water','water_distribution_system',2,[.679,.36,.73,.711],HOUSE,'Separate service-water washdown and potable-water taps supplied through the silo-house pipework.')
 water='UEE-2 Service and drinking water';tank=part(b,water,'Potable water tank','water_tank',3,[.042,.747,.276,.941])
 b.a(tank,'rated_capacity',300,3,[.042,.747,.276,.941],'L','PVC potable-water tank in piping layout');b.a(tank,'source_discrepancy','Piping layout specifies300 L; CBSH GA p2 labels250 L while its elevation p1 shows300 L. Confirm procurement/as-built capacity.',3,[.042,.747,.276,.941])
 b.a(water,'location_description','DFDS/SW/PW incoming from pump/compressor house labelled UGA-2; risers serve upper, feeder and ground floors; continuations to UEF-12 and UEE-3 are shown.',1,[.08,.116,.585,.654])
 b.a(water,'source_gap','Source UGA-2 denotes pump/compressor house. Existing model label UGA-2 Dozer Shed is a conflicting identity; no automatic merge or utility ownership under that shed is made.',1,[.462,.116,.586,.171])
 b.finish(out)

def dfds_controls(s,out):
 b=Batch(s,'dfds_control','UEE2-DFDS-local-controls','DFDS control philosophy175265 Rev2, FIO14-Jan-2019, PDFpp21–23. Listed conditions are not a synthesized PLC program. '+BASIS)
 for lcp in (1,2):b.entity(f'UEE-2 DFDS LCP-{lcp:02}','local_control_panel',21 if lcp==1 else 22,[.111,.133,.83,.798],DFDS,'Local selector and application controls; panel assignment is source-specific and conflicts with P&ID layout labels.')
 for j,page,r,lcp,condition in [(1,21,[.11,.183,.81,.331],1,'EBA-16A running with load from UBS01'),(2,21,[.11,.336,.81,.504],1,'Listed inputs: EBA-16A load UBS01; EBA-6B load UBS02; KF-3 running with load'),(3,21,[.11,.51,.81,.65],1,'FG-13 position and KF-3 running with load'),(4,22,[.11,.12,.81,.285],1,'FG-13 position and KF-3 running with load'),(5,22,[.11,.28,.81,.445],2,'EBA-16B running with load from UBS04'),(6,22,[.11,.446,.81,.627],2,'Listed inputs: EBA-16B load UBS04; EBA-6A load UBS03; KF-4 running with load'),(7,22,[.11,.633,.81,.79],2,'FG-14 position and KF-4 running with load'),(8,23,[.11,.128,.81,.28],2,'FG-14 position and KF-4 running with load'),(9,23,[.11,.28,.81,.442],1,'EBA-6A running with load from UBS03'),(10,23,[.11,.449,.81,.601],1,'EBA-6B running with load from UBS02')]:
  ap=f'UEE-2 AP-{j:02}';fas=f'UEE-2 FAS-{j}'
  b.a(ap,'start_permissive','AUTO selected; PS02 compressed-air pressure healthy; '+condition+'.',page,r,condition='Mode: Auto (philosophy)')
  b.a(ap,'operator_controls','MANUAL selector permits manual FAS energisation as listed by source; other field safeguards are not resolved here.',page,r,condition='Mode: Manual (philosophy)')
  b.rel(f'UEE-2 DFDS LCP-{lcp:02}','control_signal_to',fas,page,r,network='control',condition='Philosophy allocation; P&ID LCP branch labels require reconciliation')
  if j in (2,6):
   b.a(ap,'source_discrepancy','Source lists multiple upstream load signals with the feeder signal but supplies no Boolean grouping. Do not silently decide AND/OR or substitute feeder position for running-with-load.',page,r)
  if j in (2,3,4,6,7,8):
   # Correct all feeder-feedback summaries, including receiving-chute applications.
   for a in b.live:
    if a.get('canonical_subject')==b.ids[fas] and a['predicate']=='sequence_logic' and 'position' in str(a.get('value','')).lower():
     b.retire(a['id'],'Source says feeder running with Load, not position; Boolean grouping is not explicit.',page,r)
  if j in (3,4,7,8):b.a(ap,'source_gap','Source calls for gate position but does not specify FWD/REV in this application paragraph; retain destination from piping/P&ID and verify position contact.',page,r)
 for name in ['DFDSS-2 PS-02A','DFDSS-2 PS-02B']:
  b.rel(name,'associated_with',DFDS,21,[.11,.19,.81,.51],origin='inferred',condition='Existing local pressure instruments; philosophy names unsuffixed PS02, A/B-to-LCP assignment unresolved')
 b.finish(out)

def vent(s,out):
 b=Batch(s,'de','silo-vent-filter-assemblies','DE schematic175100 Rev1 sheet3, approved14-Dec-2018. Direct-mounted silo vent filters; do not instantiate generic RAV/hood items absent from this arrangement. '+BASIS)
 for i,r in [(1,[.403,.084,.528,.386]),(2,[.153,.084,.302,.386])]:
  v=f'EBB-{i}';vf=part(b,v,'Vent filter system','silo_vent_filter',3,r,'Direct-mounted pulse-cleaned vent filter with centrifugal fan and roof exhaust; no suction hood required.')
  b.rel(vf,'part_of',DE,3,r);b.rel(vf,'serves_equipment',v,3,r)
  filt=part(b,vf,'Filter body','bag_filter',3,r);fan=f'FAN-BS-{i}-001';timer=f'ST-BS-{i}-001';pv=f'PU-BS-{i}-001-005'
  for e in [fan,timer,pv,f'DPS-BS-{i}-001',f'PS-BS-{i}-001']:b.rel(e,'part_of',vf,3,r,condition='Existing tagged control identity retained; detailed tag support comes from DE philosophy')
  exhaust=part(b,vf,'Exhaust duct','ventilation_duct',3,r)
  b.rel(v,'utility_supply_to',filt,3,r,network='utility',condition='Silo vent air');b.rel(filt,'utility_supply_to',fan,3,r,network='utility',condition='Filtered air');b.rel(fan,'utility_supply_to',exhaust,3,r,network='utility',condition='Fan discharge to roof exhaust')
  b.a(fan,'fan_design_airflow',3450,3,[.714,.323,.942,.404],'m3/h');b.a(fan,'fan_static_pressure',250,3,[.714,.323,.942,.404],'mmWG');b.a(fan,'operating_temperature',50,3,[.714,.323,.942,.404],'degC','Schematic design temperature')
  motor=part(b,fan,'Motor','electric_motor',3,[.714,.323,.942,.404]);b.a(motor,'motor_rated_power',5.5,3,[.714,.323,.942,.404],'kW','Schematic stage; final motor selection requires fan GA');b.a(motor,'assembly_arrangement','2 pole, IP55 with canopy.',3,[.714,.323,.942,.404])
  b.rel(motor,'mechanically_drives',fan,3,[.714,.323,.942,.404],network='mechanical')
  b.a(pv,'quantity',5,3,[.743,.591,.838,.645],'valves','Five per silo; drawing total5+5=10')
  b.rel(pv,'utility_supply_to',filt,3,[.047,.739,.414,.928],network='utility',condition='Pulse-cleaning compressed air through filter manifold')
  b.a(vf,'source_gap','Generic accessories legend also lists RAV and ZSS, but the direct-mount silo arrangement does not show a hopper/RAV. No such local components are inferred from that legend.',3,[.636,.415,.942,.589])
 b.finish(out)

def vent_controls(s,out):
 b=Batch(s,'de_control','silo-vent-filter-controls-correction','DE control philosophy175280 Rev1 pp15–16, approved16-Oct-2019. Silo-specific section starts mid-page15; preceding bunker logic is excluded. '+BASIS)
 b.retire('fact_990232b7d7d1407fa0be','Silo-specific text describes continuous ventilation and air/timer/fan sequence; it does not establish selected filling-conveyor start as summarized previously.',15,[.13,.319,.939,.72])
 b.retire('fact_7ca97b40ef7948189cd9','Stopping associated silo operation is not the source condition; source describes fan-off cascade and power-failure reset.',16,[.13,.322,.943,.59])
 b.a(DE,'sequence_logic','Silo-specific description calls for continuous ventilation, AUTO sequence through local hardware logic and MANUAL test operation. Normal conveyor-dependent start/stop is not explicitly resolved; the power-restoration note separately mentions conveyor feedback.',15,[.13,.319,.939,.489])
 for i,page,r in [(1,15,[.145,.506,.943,.854]),(2,16,[.145,.134,.943,.59])]:
  vf=f'EBB-{i} Vent filter system';fan=f'FAN-BS-{i}-001';ps=f'PS-BS-{i}-001';st=f'ST-BS-{i}-001';dp=f'DPS-BS-{i}-001';pv=f'PU-BS-{i}-001-005'
  b.a(vf,'sequence_logic','AUTO: air pressure healthy enables sequential timer and pulsing; timer ON permissive enables fan; fan feedback enables DP check. Unhealthy DP within2–3 minutes stops the system.',page,r)
  b.a(vf,'operator_controls','AUTO is normal sequential operation. MANUAL is for checking auxiliary equipment.',15,[.145,.359,.943,.489])
  b.a(vf,'trip_condition','Fan stop removes DP-switch and timer/pulsing enable; timer-off removes pressure-switch enable. Power failure turns equipment off; reset before restart, with conveyor feedback mentioned in the restart note.',16,[.145,.325,.943,.591])
  for a,z,c in [(ps,st,'Air pressure healthy enables timer'),(st,pv,'Sequential timer operates pulse valves'),(st,fan,'Timer ON is fan-start permissive'),(fan,dp,'Fan start feedback enables DP health check'),(dp,fan,'DP unhealthy within2–3 min stops the system')]:b.rel(a,'control_signal_to',z,page,r,network='control',condition=c)
  b.a(vf,'source_discrepancy','Silo section inconsistently uses BU tags for fan/DP/timer in some steps and BS tags elsewhere. Existing BS identities retained with this qualification; no extra bunker-tagged devices created.',page,r)
  b.a(dp,'source_gap','DP set value and precise timer setting are not given here; source says unhealthy within2–3 min, not a single commissioned trip delay.',page,r)
 b.finish(out)

def sump(s,out):
 b=Batch(s,'sump','UEE2-sump-drainage','Sump/runoff P&ID175259 Rev3, sheet1, dated09-Sep-2019. '+BASIS)
 pair='UEE-2 Sump Pumps SP-7A/7B';r=[.838,.27,.967,.313]
 b.rel(pair,'part_of',HOUSE,1,[.271,.051,.425,.219]);b.a(pair,'assembly_arrangement','Two pumps, one working plus one standby, as scheduled for UEE-2.',1,r)
 b.a(pair,'location_description','Intermediate sump pit near UEE-2; pumping route shown to coal runoff/settling pond.',1,[.271,.051,.425,.219])
 for letter in ['A','B']:
  pump=part(b,pair,'SP-7'+letter,'sump_pump',1,r)
  for key,val,u in [('rated_flow',45,'m3/h'),('pump_head',40,'mWC'),('motor_rated_power',22,'kW')]:b.a(pump,key,val,1,r,u,'Schedule per pump')
  b.rel(pump,'utility_supply_to','CHP Coal Run-off Pond',1,[.265,.04,.82,.566],network='utility',condition='Drainage discharge route in P&ID, not potable/process water')
 b.a(pair,'sequence_logic','Sump level switches provide automatic ON/OFF through local controls; selector allows manual ON/OFF. Commissioned level thresholds and duty rotation are not stated here.',1,[.624,.894,.821,.926])
 b.finish(out)

def controls(s,out):
 b=Batch(s,'flow','silo-receiving-and-outlet-permissives','Control write-up179162 Rev04 pp40,45,48. Path-specific conditions retained; no FG14 direction conflict is silently resolved. '+BASIS)
 for i,conv in [(1,'EBA-16A'),(2,'EBA-16B')]:
  b.rel(f'EBB-{i} Level and temperature instruments Level indication','control_signal_to',conv,45,[.12,.821,.90,.902],network='control',condition=f'Silo-{i} high level NOT reached is receiving-conveyor start permissive; sensor channel/tag unresolved')
 for i,conv in [(2,'EBA-6A'),(1,'EBA-6B')]:
  b.rel(f'EBB-{i} Level and temperature instruments Level indication','control_signal_to',conv,40,[.12,.808,.90,.871],network='control',condition=f'Silo-{i} high level NOT reached is receiving-conveyor start permissive; EBA6 crossover retained')
 for k in (3,4):
  b.rel(f'KF-{k}','control_signal_to',f'EBE-CES-{k-2}',48,[.12,.715,.90,.808],network='control',condition='Path4 table: corresponding belt feeder running before extractor start')
  b.a(f'KF-{k}','source_discrepancy','General belt-feeder control says LT electrical healthy, while local KF3/4 GA lists3.3 kV motor supply. Preserve source-specific wording; confirm applicable switchgear before using an electrical designation.',29,quote='Electrical Condition : Same as LT drive. Refer section 5.0.2.')
  b.a(f'KF-{k}','start_permissive','General belt-feeder section: electrical healthy; local stop reset; PCS, BSS and chute-block switch not operated; succeeding conveyor running with applicable flap gate positioned to it. No auto ON/OFF condition is specified.',29,[.17,.45,.89,.69],condition='General feeder design logic; LT designation conflicts with local motor GA')
  for device,wording in [('PCS','Pull cord operated'),('BSS','Belt sway operated'),('ZSS','Zero-speed switch operated with source-stated on delay of 60 seconds')]:
   target=f'KF-{k} Belt protection devices {device}'
   b.a(target,'trip_condition',wording+' trips the belt feeder in the general feeder control section.',29,[.17,.70,.89,.846],condition='Documented design condition; commissioned setting not verified')
   b.rel(target,'control_signal_to',f'KF-{k}',29,[.17,.70,.89,.846],network='control',condition=wording)
 for tag in ['KF-4','FG-14']:
  b.a(tag,'source_discrepancy','Path2 p40: FG14 FWD→17A with17A running; Path3 p45: both FWD and REV text refer to17B; Path4 p48: FWD destination17A but running requirement17B. Physical branches to both conveyors are established; FWD/REV permissive assignment is unresolved.',48,[.12,.631,.90,.728])
 b.finish(out)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--output-name',default='rehearsal');args=parser.parse_args()
 plant=ROOT/'data/plant';base=ROOT/'output/silo-pilot';snap=json.loads((base/'snapshot.json').read_text(encoding='utf-8'))
 for doc in snap['documents']:
  if doc['id'] in DOCS.values() and hashlib.sha256((plant/'originals'/doc['sha256']).read_bytes()).hexdigest()!=doc['sha256']:raise RuntimeError('Original changed: '+doc['name'])
 ro=sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True)
 version=int(ro.execute("select value from meta where key='version'").fetchone()[0])
 if version!=510:raise RuntimeError(f'Expected v510, found{version}; reconcile instead of replaying.')
 out=base/('accepted' if args.apply else args.output_name);out.mkdir(parents=True,exist_ok=True)
 if (out/'commits.jsonl').exists():raise RuntimeError('Run log already exists. Inspect rather than replay.')
 backup=base/'backup-v510.sqlite3'
 if not backup.exists():
  with sqlite3.connect(backup) as dst:ro.backup(dst)
 if args.apply:s=Store(plant)
 else:
  with sqlite3.connect(out/'plant.sqlite3') as dst:ro.backup(dst)
  s=Store(out)
 ro.close();foundation(s,out)
 for i in (1,2):extractors(s,out,i);extractor_controls(s,out,i)
 extractor_ga(s,out);house(s,out)
 for k in (3,4):feeder(s,out,k)
 gates(s,out);dfds(s,out);piping(s,out);dfds_controls(s,out);vent(s,out);vent_controls(s,out);sump(s,out);controls(s,out)
 (out/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()

