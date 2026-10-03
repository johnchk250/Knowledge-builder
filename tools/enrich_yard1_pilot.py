"""Coal Yard 1 source review: rehearse first; --apply uses reviewed ingestion.

Original PDFs remain immutable. Descriptive component labels are not field tags.
Project-family machine details retain design applicability, not as-built status.
"""
import argparse, hashlib, json, sqlite3, sys
from pathlib import Path
import enrich_conveyor_tp1_pilot as core
from enrich_conveyor_tp1_pilot import ROOT, Store, stage, commit, validate

DOCS = {
 'flow':'doc_4f2cd96c3b1e413ea4b5', 'c7':'doc_2664b59a573b467eb166', 'c8':'doc_75a88e7148014a83aefd',
 'stacker':'doc_78bebe6773984d59b013', 'reclaimer':'doc_498f70490d294542b8b0',
 'reclaimer_ga':'doc_3e81ea1c32df4215968d', 'hydraulic':'doc_9f1d51138e104d5a905e',
 'spds':'doc_777d1a06d4fa4e8ba231', 'spds_pid':'doc_5a36f2843d504d6e96de',
 'spds_control':'doc_e17edf6897d746fabe12', 'sprinkler':'doc_4b620e0e7bca45e3af10',
 'stacker_ds':'doc_0f52c77514a74773ae30', 'reclaimer_ds':'doc_a6a2fa82944f4d12b8aa',
 'reclaimer_lube':'doc_42554b5718fc423997b3', 'fire':'doc_4d488fd685284c408297',
 'runoff':'doc_0453a0a014424f1cae06', 'layout':'doc_7244e891263a4e6d8214',
 'scoop':'doc_7aa49cc0d1c34af7ac06', 'stacker_lube':'doc_b7d031cc33c54157ad86',
}
core.DOCS.update(DOCS)
YARD='Coal Yard 1'
SPDS='Coal Yard 1 SPDS'
SC='Stockpile Sequential Controller SC-01'
COMMON='Coal Stockpile Plain Water DS System DS-1'
FAMILY='Project-family design applied to the Yard 1 machine identified by coal-flow 175001 Rev8. Component names without plant tags are descriptive. Installed configuration and commissioned settings are not verified.'

class Batch(core.Batch):
 def finish(self,out):
  body={'summary':self.name,'operations':self.ops,'intake_assessment':{
   'route':'mixed','purpose':'Coal Yard 1 equipment-centered pilot: navigable assemblies, utility dependencies and fact-level sources.',
   'questions':['Which local assembly owns this fact?','How does it connect, operate and receive protection?','What is the exact source and applicability?'],
   'gaps':self.gaps+['Supplemental review of pages '+', '.join(map(str,sorted(self.pages)))+'. Other imported blocks remain inventory/context; this is not a new exhaustive review of every page.','Design and vendor records do not establish installed condition or commissioned settings.'],
   'reviewed_evidence_ids':[e['id'] for e in self.ev]}}
  report=validate(self.s,{'summary':self.name,'operations':self.ops},self.doc,self.version,visual_ids=self.visual)
  if report['errors']:raise ValueError(json.dumps(report['errors']))
  (out/(self.name+'.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  r=stage(self.s,self.doc,body,visual_ids=self.visual,analysis_dir=str(out),expected_version=self.version)
  accepted=commit(self.s,r['proposal_id'])
  record={'name':self.name,'document_id':self.doc,'base_version':self.version,'result_version':self.s.version(),'operations':len(self.ops),'entities':sum(o['op']=='entity' for o in self.ops),'assertions':sum(o['op']=='assert' for o in self.ops),'visual_ids':sorted(self.visual),'pages':sorted(self.pages),'warnings':report['warnings'],'commit':accepted}
  with (out/'commits.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
  print(json.dumps({k:record[k] for k in ['name','result_version','operations','entities','assertions']}),flush=True)

def component(b,parent,name,typ,p,r,role=None,props=()):
 label=parent+' '+name
 b.entity(label,typ,p,r,parent,role)
 for prop in props:
  key,val,*rest=prop;b.a(label,key,val,p,r,*rest)
 return label

def foundation(s,out):
 b=Batch(s,'flow','yard1-boundary-and-flow','Coal-flow diagram 175001 Rev8, control write-up PDF page 55. Yard 1 is a descriptive functional-area grouping of the EAE-1 branch, not a new field tag.')
 r=[.437,.47,.904,.563]
 b.entity(YARD,'functional_area',55,r,'Coal Stockpile Yard','Stack, store and reclaim coal through EAC-7, EAD-1, EAE-1, EAF-1 and EBA-8.')
 b.a(YARD,'location_description','EAE-1 / UEB-1 branch, between UEF-6 on the stacking side and UEF-11 on the reclaim side; adjacent UAX-1 and UAX-5.',55,r)
 for tag,role in [('EAC-7','Yard stacking conveyor feeding the travelling stacker.'),('EAD-1','Travelling stacker placing coal onto stockpile EAE-1.'),('EAE-1','Coal stockpile used for storage between stacking and reclaiming.'),('EAF-1','Portal reclaimer recovering EAE-1 coal onto EBA-8.'),('EBA-8','Reclaim conveyor carrying recovered coal to UEF-11.'),('UEB-1','Cover shed for stockpile EAE-1.'),('UAX-1','Drive house at the EAC-7 end.'),('UAX-5','Tail-pulley house at the EBA-8 end.')]:
  b.rel(tag,'part_of',YARD,55,r,condition='Membership in the descriptive EAE-1 yard functional area; existing equipment identity retained.',origin='inferred')
  b.a(tag,'equipment_role',role,55,r)
 for tag,target in [('EAC-7','EAD-1'),('EAD-1','EAE-1'),('EAE-1','EAF-1'),('EAF-1','EBA-8'),('EBA-8','UEF-11')]:b.rel(tag,'feeds_material_to',target,55,r,network='material',condition='Coal-flow diagram Yard 1 branch; no live route or current operating state implied.')
 b.rel(YARD,'associated_with','UEF-6',55,r,condition='Stacking-side boundary transfer point; not owned by Yard 1.')
 b.rel(YARD,'associated_with','UEF-11',55,r,condition='Reclaim-side boundary transfer point; not owned by Yard 1.')
 b.a(YARD,'source_gap','No live stock inventory, coal lot/age/temperature history, commissioned settings, field asset serial numbers or approved maintenance intervals are established by this drawing-based pilot.',55,r)
 b.finish(out)

def conveyor(s,out,tag,key):
 b=Batch(s,key,tag+'-yard-assembly','GA and load data for '+tag+', sheet 5 Rev2, approved November 2018. Source-stated design, not field verification.')
 r=[.777,.05,.96,.812];dr=[.777,.19,.96,.322];be=[.777,.321,.96,.388];pr=[.777,.758,.96,.794];is7=tag=='EAC-7'
 drive=component(b,tag,'Drive assembly','functional_assembly',5,dr,'Motor, scoop coupling, gearbox and geared coupling transmit power to the head pulley.')
 m=component(b,drive,'Main motor','electric_motor',5,dr,props=[('motor_rated_power',680 if is7 else 270,'kW'),('motor_voltage',3.3,'kV'),('motor_speed',1488,'rpm'),('manufacturer','BHEL')])
 c=component(b,drive,'Scoop coupling','coupling',5,dr,props=[('model_number','PST-660' if is7 else 'PST-530'),('manufacturer','PREMIUM')])
 g=component(b,drive,'Gearbox','gearbox',5,dr,props=[('model_number','B3-560' if is7 else 'B3-355'),('gear_ratio_nominal',20.9 if is7 else 23.2),('assembly_arrangement','Bevel helical')])
 l=component(b,drive,'Low-speed coupling','coupling',5,dr,props=[('model_number','RG-12' if is7 else 'RG-10'),('manufacturer','GBM')])
 br=component(b,drive,'Thruster brake','brake_assembly',5,dr,props=[('model_number','EBTM 500 DS/L' if is7 else 'EBTM 500'),('manufacturer','ELEKTROMAG')])
 head=component(b,tag,'Head pulley','mechanical_component',5,[.777,.386,.96,.415],props=[('component_dimension',1000 if is7 else 800,'mm','Diameter'),('component_dimension',2200 if is7 else 1600,'mm','Face width'),('component_dimension',12,'mm','Diamond-groove rubber lagging')])
 for fr,to in [(m,c),(c,g),(g,l),(l,head)]:b.rel(fr,'transmits_power_to',to,5,dr,network='mechanical')
 belt=component(b,tag,'Belt','conveyor_belt',5,be,props=[('belt_type','ST 1000 with REP protection' if is7 else 'N/N HD 1250/4'),('belt_width',2000 if is7 else 1400,'mm'),('belt_length',1850 if is7 else 1820,'m','Endless length'),('belt_cover_thickness',8 if is7 else 5,'mm','Top cover'),('belt_cover_thickness',6 if is7 else 2,'mm','Bottom cover'),('belt_cover_grade','FR')])
 take=component(b,tag,'Take-up assembly','take_up_assembly',5,[.777,.672,.96,.742],props=[('assembly_arrangement','Horizontal gravity take-up with mark-up scale'),('take_up_travel',3300 if is7 else 23000,'mm')])
 component(b,take,'Counterweight','mechanical_component',5,[.777,.710,.96,.741],props=[('design_mass',17000 if is7 else 21000,'kg','Design counterweight per conveyor')])
 component(b,take,'Rope and sheaves','mechanical_component',5,[.777,.685,.96,.722],props=[('component_dimension',32 if is7 else 24,'mm','6x37 rope diameter'),('component_dimension',700 if is7 else 550,'mm','Sheave diameter')])
 component(b,take,'Trolley and pulley','mechanical_component',5,[.12,.78,.39,.954])
 protection=component(b,tag,'Belt protection devices','functional_assembly',5,pr)
 bs=component(b,protection,'Belt-sway switches (BSS)','belt_sway_switch_group',5,pr,props=[('quantity',18 if is7 else 17,'pairs','Source explicitly prints pairs; both sides'),('device_spacing',50,'m','Both sides')])
 b.a(bs,'individual_device_count',36 if is7 else 34,5,pr,'devices',condition='Derived: source pair count multiplied by two.',origin='inferred')
 pc=component(b,protection,'Pull-cord switches (PCS)','pull_cord_switch_group',5,pr,props=[('quantity',30 if is7 else 31,None,'GA prints a number without a unit; both sides at 30 m spacing. Not asserted as an individual-device total.'),('device_spacing',30,'m','Both sides')])
 b.a(pc,'source_gap','PCS total needs reconciliation of both-side symbols, schedule and quantity unit. No multiplication into an installed switch count has been made.',5,pr)
 z=component(b,protection,'Zero-speed switch (ZSS)','speed_switch',5,pr,props=[('quantity',1,'device'),('location_description','On tail pulley')])
 for item in [bs,pc,z,br]:b.rel(item,'protects_equipment',tag,5,pr)
 idlers=component(b,tag,'Idlers','functional_assembly',5,[.777,.507,.96,.665])
 for name,n in [('Carrying',855 if is7 else 847),('Self-aligning carrying',62 if is7 else 61),('Return',255 if is7 else 260),('Self-aligning return',43 if is7 else 51),('Self-cleaning return',1),('Flat return',2)]:component(b,idlers,name,'idler_group',5,[.777,.507,.96,.665],props=[('quantity',n,'sets','GA quantity for this idler row; not individual roller count')])
 for name,role in [('External scrapers','Spring-loaded primary and secondary at discharge pulley'),('Internal scraper','V-plough near tail pulley')]:component(b,tag,name,'mechanical_component',5,[.777,.740,.96,.770],role)
 if not is7:component(b,tag,'Belt weigher','belt_weigher',5,[.777,.786,.96,.820],props=[('quantity',1,'unit'),('assembly_arrangement','Load-cell type for 1400 mm belt')])
 b.a(tag,'location_description','Between UEF-6 and UAX-1, alongside EAE-1' if is7 else 'Between UAX-5 and UEF-11, receiving from EAF-1',5,[.777,.103,.96,.193])
 b.a(tag,'source_gap','Field sensor loop IDs, brake setting and final equipment-specific control settings require confirmation. Coupling oil details are recorded separately from the vendor design, with model applicability qualifications.',5,r)
 b.finish(out)

def stacker(s,out):
 b=Batch(s,'stacker','EAD-1-machine-assembly','Basis of design 175249 Rev2, approved 27-Feb-2019. '+FAMILY)
 whole=[.155,.095,.916,.955];top=[.155,.095,.916,.518]
 b.a('EAD-1','design_applicability',FAMILY,2,top)
 b.a('EAD-1','rated_capacity',3400,3,[.155,.171,.916,.247],'t/h','Rated stacking, measured over four hours')
 b.a('EAD-1','design_capacity',3740,3,[.155,.171,.916,.247],'t/h')
 b.a('EAD-1','assembly_arrangement','Unidirectional travelling, slewing and luffing stacker; four machines in project-family design.',2,top)
 b.a('EAD-1','source_discrepancy','BOD calls handled material crushed coal; yard conveyor GA and plant flow identify the pre-crushing stockyard stream. Preserve the BOD wording, without changing the documented plant route.',2,top)
 for v,c in [(16,'Operating maximum'),(35,'Non-operating inside shed, clamped'),(73,'Non-operating outside shed, anchored; three-second gust at 10 m above ground')]:b.a('EAD-1','design_wind_velocity',v,2,[.155,.358,.916,.474],'m/s',c+'; structural design condition, not a wind trip setpoint')
 boom=component(b,'EAD-1','Boom conveyor','conveyor',2,[.155,.514,.916,.693],'Convey coal from the travelling tripper onto EAE-1.')
 drive=component(b,boom,'Drive group','functional_assembly',2,[.155,.514,.916,.693],props=[('quantity',2,'drive sets','Two per machine; BOD 2 x 4 project total')])
 component(b,drive,'Motors','electric_motor',2,[.155,.514,.916,.693],props=[('quantity',2,'motors'),('motor_rated_power',132,'kW','Each motor'),('motor_speed',1485,'rpm','Printed syn. speed')])
 component(b,drive,'Gearboxes','gearbox',2,[.155,.514,.916,.693],props=[('quantity',2,'gearboxes'),('gear_ratio_nominal',20),('assembly_arrangement','Three-stage bevel helical')])
 component(b,drive,'Fluid couplings','coupling',2,[.155,.514,.916,.693],props=[('quantity',2,'couplings'),('rated_power',132,'kW','Each, suitable for 1485 rpm motor')])
 component(b,drive,'Shrink-disc output couplings','coupling',2,[.155,.514,.916,.693])
 component(b,drive,'Thruster brakes','brake_assembly',2,[.155,.514,.916,.693],props=[('brake_drum_diameter',400,'mm')])
 slew=component(b,'EAD-1','Slew system','functional_assembly',2,[.155,.696,.916,.815],'Position the boom across the pile.',[('slew_range','0 to 100 degrees'),('slew_speed',.0758,'rpm')])
 component(b,slew,'Hydraulic motors','hydraulic_motor',2,[.155,.696,.916,.815],props=[('quantity',2,'units','Two per machine')])
 component(b,slew,'Ring bearing and pinions','mechanical_component',2,[.155,.696,.916,.815],props=[('assembly_arrangement','Three-row roller bearing, approximately 4000 mm track diameter; ring gear z=173, pinion z=18, module 25')])
 luff=component(b,'EAD-1','Luffing system','functional_assembly',2,[.155,.821,.916,.954],'Raise and lower boom.',[('operating_range','+14 to -8 degrees'),('luff_speed',3,'m/min','Maximum at boom head pulley centre')])
 hp=component(b,luff,'Hydraulic power pack','hydraulic_power_pack',2,[.155,.821,.916,.954])
 component(b,hp,'Motor','electric_motor',2,[.155,.821,.916,.954],props=[('motor_rated_power',22,'kW'),('motor_speed',1500,'rpm')])
 component(b,hp,'Pump and coupling','functional_assembly',2,[.155,.821,.916,.954])
 component(b,luff,'Cylinder','hydraulic_cylinder',2,[.155,.821,.916,.954],props=[('cylinder_bore',250,'mm'),('cylinder_stroke',2040,'mm'),('maximum_working_pressure',160,'bar'),('component_dimension',180,'mm','BOD calls this piston diameter; do not silently reinterpret as rod diameter')])
 tr=component(b,'EAD-1','Travel system','functional_assembly',3,[.155,.058,.916,.174],'Move the stacker along the yard conveyor.')
 component(b,tr,'Geared motors','electric_motor',3,[.155,.058,.916,.174],props=[('quantity',12,'drives','Per machine, BOD 12 x 4'),('motor_rated_power',5.5,'kW','Each'),('gear_ratio_nominal',141.93),('assembly_arrangement','VVVF control; four-stage bevel helical gear motor')])
 b.a(tr,'operating_speed',7,3,[.155,.058,.916,.174],'m/min','Operating');b.a(tr,'operating_speed',20,3,[.155,.058,.916,.174],'m/min','Shunting')
 component(b,tr,'Rails and wheels','mechanical_component',3,[.155,.155,.916,.267],props=[('rail_gauge',8400,'mm'),('rail_section','UIC60'),('maximum_wheel_load',27,'t')])
 component(b,'EAD-1','Operator cabin','plant_building',3,[.155,.27,.916,.307],props=[('assembly_arrangement','Dust proof and air conditioned; 2.4 x 1.9 x 2.4 m design dimensions')])
 component(b,boom,'Belt scale','belt_weigher',3,[.155,.312,.916,.36],'Load-cell type boom discharge weighing.')
 trip=component(b,'EAD-1','Travelling tripper','tripper',3,[.155,.36,.916,.515],'Take coal from the unidirectional yard conveyor to the boom.',[('belt_width',2000,'mm'),('horizontal_length',47878,'mm','Approximate'),('inclined_length',61480,'mm','Approximate belt length'),('pulley_diameter',800,'mm','Discharge pulley'),('trough_angle',35,'degrees')])
 b.rel(trip,'associated_with','EAC-7',3,[.155,.36,.916,.515],condition='Plain tripper for the unidirectional yard conveyor; Yard 1 assignment from flow identity.')
 b.a('EAD-1','source_gap','Machine PLC cause/effect, collision and travel-limit loops, storm-parking procedure and field tag assignment require separate verification. Structural wind limits are not automatic trip thresholds.',2,top)
 b.finish(out)

def reclaimer(s,out):
 b=Batch(s,'reclaimer_ga','EAF-1-machine-assembly','GA and TDS 175127 Rev2, approved 23-Nov-2018, explicitly lists EAF-1 through EAF-4. '+FAMILY)
 left=[.053,.042,.303,.445];centre=[.309,.04,.558,.977]
 b.a('EAF-1','design_applicability',FAMILY,3,left)
 for prop,v,u in [('rated_capacity',1250,'t/h'),('design_capacity',1375,'t/h'),('design_mass',417,'t'),('maximum_design_temperature',50,'degC')]:b.a('EAF-1',prop,v,3,[.053,.253,.303,.443],u,condition='GA design; mass approximate')
 b.a('EAE-1','maximum_dead_stock',5,3,[.053,.161,.303,.242],'%','GA design percentage, not measured current stock')
 for name,power,ratio,pitch,strength,centres,speed,blade,rg in [
  ('Main scraper boom',110,180,500,1500,37.145,.69,'2500 x 500 mm',[.309,.196,.558,.439]),
  ('Auxiliary scraper boom',30,160,400,500,14.8,.62,'1800 x 450 mm',[.309,.443,.558,.687])]:
  boom=component(b,'EAF-1',name,'functional_assembly',3,rg,'Scrape coal down toward the reclaim conveyor.')
  drive=component(b,boom,'Drive group','functional_assembly',3,rg)
  component(b,drive,'Motors','electric_motor',3,rg,props=[('quantity',2,'motors'),('motor_rated_power',power,'kW','Each motor'),('motor_speed',1500,'rpm'),('starting_method','VFD')])
  component(b,drive,'Gearboxes','gearbox',3,rg,props=[('quantity',2,'gearboxes'),('gear_ratio_nominal',ratio),('assembly_arrangement','Bevel helical hollow output shaft with shrink disc; one clockwise and one anticlockwise')])
  component(b,drive,'Input flexible couplings','coupling',3,rg)
  cr=[.053,.829,.303,.979] if power==110 else [.309,.04,.558,.187]
  chain=component(b,boom,'Scraper chain','mechanical_component',3,cr,props=[('assembly_arrangement','Roller bush chain'),('chain_pitch',pitch,'mm'),('breaking_strength',strength,'kN'),('sprocket_centres',centres,'m'),('chain_speed',speed,'m/s')])
  component(b,boom,'Scraper blades','mechanical_component',3,cr,props=[('assembly_arrangement',blade+' blades; spacing '+str(1000 if power==110 else 800)+' mm')])
  component(b,boom,'Hydraulic-assisted take-up','take_up_assembly',3,[.786,.04,.975,.117],props=[('take_up_stroke',500 if power==110 else 400,'mm')])
 ho=component(b,'EAF-1','Hoist system','functional_assembly',3,[.309,.694,.558,.971],'Raise and lower the scraper booms.')
 component(b,ho,'Motor','electric_motor',3,[.309,.694,.558,.971],props=[('motor_rated_power',45,'kW'),('motor_speed',1500,'rpm'),('starting_method','VFD')])
 component(b,ho,'Gearbox and connecting gear','gearbox',3,[.309,.694,.558,.971],props=[('gear_ratio_nominal',35.5,None,'Gearbox ratio'),('assembly_arrangement','Helical hollow output shaft with shrink disc; connecting gear ratio 5.294')])
 component(b,ho,'Input flexible coupling','coupling',3,[.309,.694,.558,.971],props=[('brake_drum_diameter',315,'mm')])
 component(b,ho,'Operating and safety thruster brakes','brake_assembly',3,[.309,.891,.558,.971],props=[('quantity',2,'brakes','One operating and one safety'),('brake_torque',292,'Nm','Source design value')])
 component(b,ho,'Winch rope and sheaves','mechanical_component',3,[.564,.82,.778,.893],props=[('winch_drum_diameter',1300,'mm'),('sheave_diameter',800,'mm'),('rope_diameter',28,'mm')])
 b.a(ho,'operating_speed',3,3,[.309,.694,.558,.971],'m/min');b.a(ho,'rope_speed',34,3,[.309,.694,.558,.971],'m/min')
 tr=component(b,'EAF-1','Travel system','functional_assembly',3,[.053,.448,.303,.82],'Advance the portal reclaimer along EAE-1.')
 component(b,tr,'Geared motors','electric_motor',3,[.053,.448,.303,.82],props=[('quantity',12,'drives','Eight fixed side plus four pendulum side'),('motor_rated_power',5.5,'kW','Each'),('starting_method','VFD'),('assembly_arrangement','Bevel helical hollow-output geared motor with inbuilt brake')])
 component(b,tr,'Rails and wheels','mechanical_component',3,[.053,.47,.303,.702],props=[('quantity',22,'wheels','Fourteen fixed side and eight pendulum side; twelve driven'),('rail_section','UIC60'),('rail_gauge',55.8,'m'),('wheel_diameter',630,'mm'),('travel_distance',714.75,'m')])
 b.a(tr,'operating_range','Reclaim travel 2 to 8 m/min; relocation 20 m/min maximum.',3,[.053,.448,.303,.483])
 component(b,tr,'Hydraulic rail clamps','rail_clamp',3,[.053,.678,.303,.714],props=[('quantity',2,'clamps'),('rated_capacity',10,'t','Per clamp, GA notation')])
 component(b,tr,'Manual rail clamps','rail_clamp',3,[.053,.678,.303,.714],props=[('quantity',2,'clamps','One on each side')])
 component(b,tr,'Spring buffers','mechanical_component',3,[.786,.355,.975,.431],props=[('quantity',8,'buffers','Four pendulum side and four fixed side'),('buffer_stroke',210,'mm','Approximate')])
 for name,kw in [('Power cable reel',7.5),('Control cable reel',3.7)]:component(b,'EAF-1',name,'cable_reel',3,[.564,.158,.778,.228],props=[('quantity',1,'unit'),('assembly_arrangement','Mono spiral; electromechanical drive'),('motor_rated_power',kw,'kW')])
 component(b,'EAF-1','Central grease lubrication','lubrication_system',3,[.564,.041,.778,.153],'Lubricate fixed/pendulum travel wheels, guide wheels and scraper-boom plummer blocks.')
 component(b,'EAF-1','Chain oil lubrication','lubrication_system',3,[.564,.041,.778,.153],'Lubricate main and auxiliary scraper chains.')
 b.a('EAF-1','source_gap','Safety-instrument GA 179103 is referenced here; exact travel/collision/hoist interlock loops and wind trip settings still need verification. Do not infer the installed settings from structural design limits.',3,[.786,.441,.975,.475])
 b.a('EAF-1','source_discrepancy','GA wind rows print 16 km/h operating and 73 km/h non-operating. Reclaimer BOD page 6 prints 16, 35 and 73 m/s. Units conflict; no authoritative trip or safe operating threshold is inferred.',3,[.053,.345,.303,.415])
 b.finish(out)
 b=Batch(s,'reclaimer','EAF-1-design-qualifications','Portal reclaimer BOD 47039270 Rev2, approved 23-Nov-2018. '+FAMILY)
 b.a('EAF-1','design_wind_velocity',16,6,[.15,.52,.90,.777],'m/s','Operating structural-design condition, not a commissioned trip setting')
 b.a('EAF-1','design_wind_velocity',35,6,[.15,.52,.90,.777],'m/s','Non-operating structural-design condition')
 b.a('EAF-1','design_wind_velocity',73,6,[.15,.52,.90,.777],'m/s','High-wind non-operating structural-design condition')
 b.a('EAF-1 Travel system','source_discrepancy','BOD travel row shows 2 m/min and a separate 5 m/min entry without a clear range; GA page 3 states operating 2 to 8 m/min. Retained as competing design information.',5,[.22,.552,.87,.64])
 b.a('EAF-1 Auxiliary scraper boom','source_discrepancy','BOD gives 500-650 t/h depending on boom inclination; GA page 3 gives 500-660 t/h. Final applicable rating remains to be reconciled.',6,[.22,.164,.90,.376])
 b.finish(out)

def hydraulic(s,out):
 b=Batch(s,'hydraulic','EAD-1-slew-hydraulics','Maha hydraulic circuit MH-3296-00 Rev1 and operation write-up MH-OP-233 Rev1; FIO 18-Feb-2019. '+FAMILY)
 sl='EAD-1 Slew system';r=[.05,.04,.96,.955]
 hp=component(b,sl,'Hydraulic power pack','hydraulic_power_pack',2,r,'Supply the two slew hydraulic motors and cooling circuit.')
 tank=component(b,hp,'Oil tank','oil_tank',2,[.065,.82,.56,.947],props=[('useful_volume',300,'L')])
 pump=component(b,hp,'Pump Q1','hydraulic_pump',2,[.15,.705,.292,.865],props=[('rated_flow',42,'L/min')])
 motor=component(b,hp,'Motor EM1','electric_motor',2,[.15,.705,.292,.865],props=[('motor_rated_power',22,'kW'),('motor_speed',1480,'rpm')])
 cool=component(b,hp,'Air oil cooler','oil_cooler',2,[.563,.622,.635,.817])
 component(b,cool,'Fan motor EM2','electric_motor',2,[.563,.622,.635,.817],props=[('motor_rated_power',.18,'kW')])
 for name,rg,grade in [('RF1 return filter',[.365,.792,.453,.861],10),('RF2 return filter',[.06,.792,.148,.861],10),('PF1 pressure filter',[.234,.66,.288,.74],5)]:component(b,hp,name,'oil_filter',2,rg,props=[('filtration_rating',grade,'micrometre')])
 for name,typ in [('FS1 oil level switch','level_switch'),('LS1 suction valve limit switch','limit_switch'),('TT1 temperature transmitter','temperature_transmitter'),('Proportional directional valve','hydraulic_valve'),('Drive control card','control_system')]:component(b,hp,name,typ,2,r)
 b.a(hp,'lubricant_grade','VG 100',2,[.669,.086,.932,.243]);b.a(hp,'nominal_pressure',230,2,[.669,.086,.932,.243],'bar','Approximate working pressure, slew drive')
 b.a(hp,'operating_temperature',55,2,[.669,.086,.932,.243],'degC','Source nominal operating temperature, not alarm/trip setting')
 b.a(hp,'oil_cleanliness_requirement','NAS level 6 to 7',2,[.669,.086,.932,.243])
 b.a(hp,'start_permissive','Oil above minimum level; suction ball valve open confirmed by LS1; no high oil temperature; air-oil-cooler motor running.',7,[.11,.648,.9,.757])
 b.a(hp+' FS1 oil level switch','trip_condition','Low oil level switches off the complete hydraulic system.',7,[.11,.489,.9,.595])
 b.a(hp+' TT1 temperature transmitter','operating_requirement','Two setpoints: one alarm and one complete-system trip. Numeric setpoints are not specified in this write-up.',7,[.11,.583,.9,.628])
 b.a(hp,'alarm_condition','Return or charge-line pressure filter clogging provides an alarm signal.',7,[.11,.831,.9,.867])
 b.a(hp,'sequence_logic','Forward energizes S1, S2 and S4; reverse energizes S1, S3 and S4. Speed command is through the proportional valve; source logic, not a control command.',7,[.11,.175,.9,.43])
 for fr,to in [(motor,pump),(pump,sl+' Hydraulic motors'),(hp+' FS1 oil level switch',hp),(hp+' LS1 suction valve limit switch',motor),(hp+' TT1 temperature transmitter',hp)]:b.rel(fr,'associated_with',to,2,r)
 b.a(sl+' Hydraulic motors','model_number','HMB20',2,[.402,.04,.604,.119]);b.a(sl+' Hydraulic motors','displacement',20,2,[.402,.04,.604,.119],'L/rev')
 b.finish(out)

def spds(s,out):
 b=Batch(s,'spds','yard1-spds-scope','SPDS design basis 175256 Rev2, approved 21-Jan-2019. Design quantities; shared pump motor rating explicitly provisional.')
 r=[.04,.20,.97,.78]
 b.entity(SPDS,'dust_suppression_system',3,r,YARD,'Suppress fugitive dust over EAE-1 with the yard ring header and automatic swivelling sprinklers.')
 b.rel(SPDS,'part_of',COMMON,3,r,condition='Local branch of the common four-stockpile system; shared pumps remain owned by the common system.')
 b.rel(SPDS,'serves','EAE-1',3,r,network='utility')
 for key,val,unit in [('quantity',28,'sprinklers'),('rated_flow',30,'m3/h per sprinkler'),('nominal_pressure',5,'kg/cm2'),('spray_radius',41,'m')]:b.a(SPDS,key,val,3,[.04,.39,.97,.578],unit,condition='Yard 1 sprinkler design; radius approximate')
 for key,val in [('stockpile_length',710),('stockpile_width',52),('max_stockpile_height',16)]:b.a('EAE-1',key,val,3,[.04,.39,.97,.455],'m','Stockpile design dimensions, not live pile survey')
 header=component(b,SPDS,'Ring header','utility_header',3,[.04,.26,.97,.365],'Receive shared DS water and feed the two sides of EAE-1.')
 b.rel(COMMON,'supplies_water_to',header,3,[.04,.26,.97,.365],network='utility',condition='From common pump-house header to individual stockpile ring header')
 for pump in ['SPDSP-1A','SPDSP-1B']:
  b.a(pump,'rated_flow',154,2,[.035,.26,.98,.478],'m3/h');b.a(pump,'pump_head',124,2,[.035,.26,.98,.478],'mwc')
  b.a(pump,'duty_arrangement','Two pumps: one working and one standby for the common system.',2,[.035,.26,.98,.478])
  b.rel(pump,'serves',SPDS,3,r,condition='Shared service for all four yards; not a Yard 1-owned pump.')
  motor=component(b,pump,'Motor design selection','electric_motor',2,[.035,.26,.98,.478],props=[('motor_rated_power',110,'kW','DBR selection; source says final motor kW subject to final vendor data')])
 b.a(SPDS,'operating_requirement','Maximum four sprinklers across two stockpiles simultaneously; two per stockpile. Shared water-demand basis includes 20 m3/h makeup for stacker/reclaimer machines.',3,[.04,.57,.97,.78])
 b.finish(out)
 b=Batch(s,'spds_control','yard1-spds-control','SPDS control philosophy, approved 26-May-2020. Source wording and tag discrepancies retained.')
 r=[.055,.078,.95,.463]
 b.rel(SC,'part_of',SPDS,3,r);b.a(SC,'equipment_role','Sequence Yard 1 sprinklers AP-1 through AP-28 in 14 pairs.',3,[.055,.482,.95,.909])
 b.a(SC,'kks_tag_as_printed','00EAE001QN201',3,[.055,.482,.95,.516])
 b.a(SC,'source_gap','Controller KKS is printed with 00EAE001; field/IO confirmation is needed before treating a normalized tag as an alias.',3,[.055,.482,.95,.516])
 b.a(SC,'control_timer_delay',120,3,r,'s','Per-sector operating time');b.a(SC,'control_timer_delay',20,3,r,'s','Inter-sector interval')
 b.a(SC,'sequence_logic','SC-01 and SC-02 operate stockpiles 1 and 2 together, sectors 1-14, then stop while SC-03 and SC-04 operate stockpiles 3 and 4. Local/remote and auto/manual selections are documented.',3,r)
 b.a(SC,'source_discrepancy','Source calls one cycle 33 minutes but its expression 2 min x 14 + 20 s x 13 equals 32 min 20 s. Timing remains source-qualified; no PLC adjustment inferred.',3,[.055,.298,.95,.411])
 b.a(SPDS,'operating_requirement','Manual mode permits individual solenoid selection; maximum four sprinklers across the system. Continuous controller power and local or DDCMIS ON command are required.',3,r)
 b.finish(out)
 for start,end in [(1,8),(9,14)]:
  b=Batch(s,'spds_control',f'yard1-SPDS-sectors-{start}-{end}','Yard 1 SC-01 sector pairing and valve KKS tags, SPDS control philosophy pp3-4; approved 26-May-2020.')
  for n in range(start,end+1):
   p=3 if n<=8 else 4;r=[.055,.54+(n-1)*.044,.96,.591+(n-1)*.044] if p==3 else [.055,.06+(n-9)*.039,.96,.104+(n-9)*.039]
   sector=component(b,SPDS,f'Sector {n:02}','functional_assembly',p,r,'Control grouping for one opposite-side sprinkler pair; not a separate physical machine.')
   b.rel(SC,'controls',sector,p,r,network='control')
   for sv,kks in [(n,199+2*n),(n+14,200+2*n)]:
    valve=component(b,sector,f'SV-{sv}','solenoid_valve',p,r,props=[('kks_tag',f'00EAE01SV{kks}')])
    b.a(valve,'equipment_role',f'Yard 1 solenoid valve in sector {n}; paired with SV-{sv+14 if sv<=14 else sv-14}.',p,r)
  b.finish(out)

def spds_physical(s,out):
 b=Batch(s,'spds_pid','yard1-SPDS-piping','P&ID 175255 Rev2; FIO 21-Jan-2019. Local 28-point scope and typical riser construction; page shows competing pump-head values.')
 r=[.036,.053,.66,.168];detail=[.354,.697,.55,.966]
 header=SPDS+' Ring header'
 b.a(header,'nominal_diameter',100,1,[.357,.76,.55,.965],'NB','Individual stockpile header')
 b.a(header,'assembly_arrangement','Two sides with 14 sprinklers each; 65 NB riser gate valve, solenoid valve and globe valve; 32 NB quick-release makeup connections.',1,[.04,.59,.81,.965])
 b.a(SPDS,'location_description','Around EAE-1: AP-1 to AP-14 on the upper side and AP-15 to AP-28 on the lower side of the P&ID. Drawing-side labels do not establish geographic north/south.',1,r)
 b.a(SPDS,'source_gap','AP and SV ranges/pairs are documented, but a unique AP-to-SV cross-reference and surveyed coordinates are not established here. APs and SVs remain separately navigable groups.',1,r)
 b.a(SPDS,'source_discrepancy','This P&ID schedule gives pump head 124 mwc while its major BOM gives 115 mwc. DBR gives 124 mwc; final pump selection must be reconciled.',1,[.348,.273,.96,.708])
 qrc=component(b,SPDS,'Machine makeup QRC connections','utility_header',1,[.158,.832,.265,.963],'Provide makeup water connections for machine onboard tanks.',[('nominal_diameter',32,'NB')])
 b.a(qrc,'device_spacing',30,1,[.548,.704,.81,.955],'m','P&ID note 9; no Yard 1 outlet count inferred')
 for machine in ['EAD-1','EAF-1']:b.rel(qrc,'serves',machine,1,[.548,.704,.81,.955],network='utility',condition='Makeup connection via hose; not a permanent direct machine-water pipe')
 group=component(b,SPDS,'Sprinkler risers AP-1 to AP-28','functional_assembly',1,r,'Local physical spray points; distinct from functional sector grouping.')
 b.finish(out)

def shared_controls(s,out):
 b=Batch(s,'spds_control','yard1-shared-SPDS-dependencies','SPDS control philosophy, approved 26-May-2020. Pump identities here are the explicit control-text identities, not an automatic merge with SPDSP-1A/B.')
 r=[.05,.06,.96,.574]
 level='Tank-2 SPDS Water Level Switch 00EGC06CL100';ps='SPDS Pressure Switch PS-01-SPDS1';dp='SPDS Duplex Filter DPS-01-SPDS1'
 for suffix,kks in [('A','00EGC06KP001'),('B','00EGC06KP002')]:
  pump=f'CHP Stockpile DS Pump SPDSP-2{suffix} (control-text identity)'
  b.rel(pump,'serves',SPDS,8,r,condition='Shared SPDS control reference. Document pump naming differs from SPDSP-1A/B in DBR; identity unresolved.')
  b.a(pump,'kks_tag',kks,8,r)
  b.a(pump,'start_permissive','Remote selection and MCC healthy for PLC/DCS operation; overload not operated, LS-03-H not operated (source defines level at/above H), emergency stop not pressed.',8,[.05,.137,.96,.371])
  b.a(pump,'source_discrepancy','Local-mode MCC wording is printed as "MCC no faulty signal not available at PLC"; polarity needs reconciliation. Pump label 2A/2B differs from DBR/P&ID 1A/1B. Do not treat these as four installed pumps.',8,r)
  b.a(pump,'trip_condition','LS-03-L operated; emergency stop; overload; required pressure not reached after 5 minutes from start; or duplex-filter choked DPS signal.',8,[.05,.386,.96,.574])
  for item in [level,ps,dp]:b.rel(item,'control_signal_to',pump,8,[.05,.386,.96,.574],network='control')
 b.a(ps,'control_timer_delay',5,8,[.05,.492,.96,.541],'min','Required pressure not reached following pump start -> trip')
 b.rel(level,'part_of','Common DS Tank-2 SPDS-1 Compartment',8,r)
 b.rel('Common DS Tank-2 SPDS-1 Compartment','serves',SPDS,8,r,condition='Shared tank compartment supplying the coal stockpile DS system.')
 inlet='Tank-2 Partition-2 Inlet Motorized Valve MGV-02'
 b.rel(inlet,'serves',SPDS,10,[.05,.276,.96,.474],condition='Shared tank makeup dependency; not owned by Yard 1.')
 b.a(inlet,'sequence_logic','Open/start when LS-03-HH is not operated (below HH); close when LS-03-HH operates (at or above HH). KKS 00EGC06AA001; level switch 00EGC06CL100.',10,[.05,.276,.96,.474])
 b.finish(out)

def machine_dust(s,out):
 b=Batch(s,'stacker_ds','EAD-1-onboard-dust-suppression','Chemtrols coal stacker plain-water DSS design/control Rev05, FIO 23-Jan-2021. Coal section only; limestone dry-fog section is excluded. '+FAMILY)
 r=[.18,.164,.94,.909];ds=component(b,'EAD-1','Onboard plain-water DSS','dust_suppression_system',21,r,'Suppress dust at tripper discharge, boom receipt and boom discharge.')
 b.a(ds,'location_description','Pump skid, tank and accessories on the stacker machine; dedicated headers near the three spray points.',21,[.18,.165,.94,.449])
 tank=component(b,ds,'Water tank','water_tank',22,[.23,.18,.92,.24],props=[('component_material','Stainless steel')])
 for name,typ in [('Level switch','level_switch'),('Float valve','float_valve')]:component(b,tank,name,typ,22,[.23,.18,.92,.24])
 pump=component(b,ds,'Pump set','pump',22,[.23,.3,.92,.497],props=[('duty_arrangement','One working and one standby; electric motor driven centrifugal pumps')])
 b.a(pump,'rated_flow',4.9,8,[.062,.166,.906,.659],'m3/h','Pump sizing selection after 20% margin; not verified nameplate capacity')
 component(b,pump,'Drive motors','electric_motor',21,[.18,.712,.94,.909])
 for name,typ in [('Duplex suction filter','water_filter'),('Filter differential-pressure switch','differential_pressure_switch'),('Discharge pressure switch','pressure_switch'),('Pressure relief valve','pressure_relief_valve'),('Isolation and non-return valves','functional_assembly'),('Hose reel','hose_reel')]:component(b,ds,name,typ,22,[.21,.11,.94,.61])
 for n,name,count,target in [(1,'Tripper discharge',6,'EAD-1 Travelling tripper'),(2,'Boom receipt',12,'EAD-1 Boom conveyor'),(3,'Boom discharge',16,'EAD-1 Boom conveyor')]:
  ap=component(b,ds,f'AP-{n} {name}','spray_application_point',8,[.062,.34,.906,.555])
  nz=component(b,ap,'Nozzle group','spray_nozzle',8,[.062,.34,.906,.555],props=[('quantity',count,'nozzles'),('rated_flow',120,'L/h per nozzle','Coal spray-chart W-LPH value')])
  b.rel(ap,'sprays_at',target,8,[.062,.34,.906,.555],network='utility',condition=name)
 b.a(pump,'start_permissive','Normal tank level and continuous water supply; tank outlet and suction valves open; suction flooded; filter differential pressure below 0.2 barg.',22,[.23,.737,.94,.893])
 b.a(pump,'trip_condition','Pressure must exceed the low-pressure switch setting within one minute of start or pump trips. Low discharge pressure in normal operation trips; tank level below low setpoint for more than three minutes trips.',23,[.23,.142,.94,.465])
 b.a(ds,'alarm_condition','Tank high, low and low-low level; pump discharge low pressure; filter choked; motor trip.',23,[.23,.331,.94,.401])
 b.a(ds,'source_discrepancy','Component list specifies duplex filter; alarm text says simplex filter choked. Preserve both; actual filter arrangement needs reconciliation.',23,[.23,.331,.94,.401])
 b.rel(SPDS+' Machine makeup QRC connections','serves',tank,22,[.23,.18,.92,.24],condition='Tank makeup from yard header is established by stockpile P&ID; final hose connection/field point unverified.',origin='inferred')
 b.finish(out)
 b=Batch(s,'reclaimer_ds','EAF-1-onboard-dust-suppression','F. Harley plain-water DS BOD 47039284 Rev1, approved 19-Aug-2019, four portal reclaimers. '+FAMILY)
 r=[.035,.22,.94,.855];ds=component(b,'EAF-1','Onboard plain-water DSS','dust_suppression_system',4,r,'Suppress dust at receipt onto the yard reclaim conveyor.')
 tank=component(b,ds,'Water tank','water_tank',4,[.035,.306,.94,.365],props=[('tank_capacity',2000,'L'),('component_material','Stainless steel'),('location_description','On mobile reclaimer platform; stated two hours storage')])
 pump=component(b,ds,'PRP-1A pump','pump',3,[.09,.224,.90,.384],props=[('rated_flow',1,'m3/h'),('pump_head',45,'mwc'),('duty_arrangement','One working, no standby, per reclaimer')])
 component(b,pump,'Motor design selection','electric_motor',3,[.09,.224,.90,.384],props=[('motor_rated_power',.55,'kW','Tentative BOD rating subject to final vendor selection'),('motor_speed',2900,'rpm')])
 reel=component(b,ds,'Manual hose reel','hose_reel',4,[.035,.481,.94,.603],props=[('hose_length',50,'m'),('nominal_diameter',32,'NB'),('assembly_arrangement','Flexible hose and QRC for filling onboard tank')])
 for name,typ in [('Local DSS panel','local_control_panel'),('Tank inlet solenoid valve','solenoid_valve'),('Tank level switch','level_switch'),('Discharge pressure switch','pressure_switch'),('Pressure relief and recirculation','functional_assembly'),('Spray solenoid box','solenoid_box')]:component(b,ds,name,typ,4,r)
 ap=component(b,ds,'AP-1 Yard conveyor receipt','spray_application_point',5,[.035,.27,.98,.43])
 component(b,ap,'Nozzle group','spray_nozzle',5,[.035,.241,.98,.433],props=[('quantity',6,'nozzles'),('rated_flow',2,'L/min per nozzle'),('nominal_pressure',3,'bar','Nozzle tip'),('assembly_arrangement','Full cone plain-water nozzles')])
 b.rel(ap,'sprays_at','EBA-8',5,[.035,.27,.98,.43],network='utility',condition='Receipt of yard conveyor from the Yard 1 portal reclaimer.')
 b.a(ds+' Tank inlet solenoid valve','sequence_logic','Normally open type; closes at high tank water level.',4,[.035,.481,.94,.604])
 b.a(pump,'trip_condition','Low tank water level automatically trips the pump to prevent dry running.',4,[.035,.481,.94,.604])
 b.a(ds+' Spray solenoid box','start_permissive','Respective reclaim conveyor running with load signal from PLC actuates the spray solenoid.',4,[.035,.667,.94,.707])
 b.a(ds,'source_discrepancy','Machine GA lists approximate DSS power 2.2 kW; this later BOD lists tentative 0.55 kW pump motor. A final vendor/nameplate check is required before assigning installed motor power.',3,[.09,.224,.90,.384])
 b.rel(SPDS+' Machine makeup QRC connections','serves',reel,4,[.035,.481,.94,.604],network='utility',condition='Temporary hose connection to header tap points for tank filling')
 b.finish(out)

def lubrication(s,out):
 b=Batch(s,'reclaimer_lube','EAF-1-lubrication-details','Lincoln lubrication specification, approved 16-Jul-2019. '+FAMILY)
 gr='EAF-1 Central grease lubrication';oil='EAF-1 Chain oil lubrication';r=[.11,.17,.91,.819]
 pump=component(b,gr,'Pump','lubrication_pump',4,r,props=[('model_number','ZPU 14G-50XB'),('rated_flow',14,'L/h','+/-10%'),('lubricant_grade','Grease up to NLGI-II'),('filtration_rating',280,'micrometre')])
 component(b,pump,'Reservoir','oil_tank',4,r,props=[('tank_capacity',50,'L')])
 component(b,pump,'Motor','electric_motor',4,r,props=[('motor_rated_power',.55,'kW'),('motor_voltage',415,'V AC'),('rated_rotational_speed',66,'rpm','Output speed'),('ingress_protection','IP55'),('manufacturer','Siemens')])
 component(b,gr,'Changeover valve','hydraulic_valve',4,r,props=[('model_number','DU1 GK'),('nominal_pressure',400,'bar')])
 component(b,gr,'Safety valve','pressure_relief_valve',4,r,props=[('pressure_setting',410,'bar','Vendor design setting, not confirmed commissioned value')])
 component(b,gr,'High and low level switch','level_switch',4,r)
 r=[.11,.17,.91,.83]
 pump=component(b,oil,'Pump','lubrication_pump',10,r,props=[('model_number','MFE5-BW30+299'),('rated_flow',.5,'L/min'),('operating_range','Service viscosity 20 to 1000 mm2/s'),('motor_voltage',240,'V AC')])
 component(b,pump,'Reservoir','oil_tank',10,r,props=[('tank_capacity',30,'L')])
 component(b,oil,'Metering distributor','mechanical_component',10,r,props=[('model_number','350'),('metering_quantity',.6,'cm3'),('maximum_working_pressure',80,'bar'),('operating_range','0 to 80 degC')])
 component(b,oil,'Projection nozzle group','lubrication_nozzle',10,r,props=[('model_number','AC-A'),('quantity',16,'nozzles','Four groups of four'),('metering_quantity',60,'mm3/stroke'),('lubricant_grade','Mineral or synthetic oil; no additives')])
 component(b,oil,'Low level switch','level_switch',10,r)
 b.a(gr,'source_discrepancy','Machine GA shows 0.37 kW lubrication motors; later Lincoln grease pump datasheet gives 0.55 kW. Source-specific values are retained pending final configuration confirmation.',4,[.11,.434,.91,.583])
 b.finish(out)

def spds_risers(s,out):
 group=SPDS+' Sprinkler risers AP-1 to AP-28';header=SPDS+' Ring header'
 r=[.036,.053,.66,.168];detail=[.354,.697,.55,.966]
 for start,end in [(1,14),(15,28)]:
  b=Batch(s,'spds_pid',f'yard1-SPDS-risers-{start}-{end}','P&ID 175255 Rev2; FIO 21-Jan-2019. Typical riser replicated only at its explicitly drawn AP-1 to AP-28 positions. Untagged valve labels are descriptive.')
  for n in range(start,end+1):
   riser=component(b,group,f'AP-{n}','spray_application_point',1,r,props=[('location_description',f'EAE-1 P&ID {"upper" if n<=14 else "lower"} side, position {n if n<=14 else n-14} of 14; not a geographic direction')])
   component(b,riser,'Sprinkler','sprinkler',1,detail)
   component(b,riser,'Isolation gate valve','gate_valve',1,detail,props=[('nominal_diameter',65,'NB')])
   component(b,riser,'Flow-adjusting globe valve','globe_valve',1,detail,props=[('nominal_diameter',65,'NB')])
   b.rel(header,'supplies_water_to',riser,1,r,network='utility')
  b.finish(out)
 b=Batch(s,'sprinkler','yard1-SPDS-sprinkler-details','ES-65PC stockpile sprinkler datasheet, approved 26-Jun-2019; 112 is the four-yard total. Local Yard 1 count is 28 per DBR/P&ID.')
 r=[.12,.13,.95,.806]
 for n in range(1,29):
  sp=group+f' AP-{n} Sprinkler'
  for key,val,u,cond in [('model_number','ES-65PC',None,None),('manufacturer','Eagle Engineering Industries',None,None),('rated_flow',30,'m3/h','At source tip pressure'),('nominal_pressure',5,'kg/cm2','Nozzle tip'),('spray_radius',41,'m','Spray length'),('nozzle_diameter',20,'mm',None),('assembly_arrangement','Automatic swivelling, 180-degree rotation; 2.5-inch BSP female connection',None,None)]:b.a(sp,key,val,2,r,u,cond)
 b.finish(out)

def scoop_auxiliaries(s,out):
 for tag,page,size,fanpower in [('EAC-7',4,'660 PST',.55),('EBA-8',1,'500 PST',.37)]:
  b=Batch(s,'scoop',tag+'-scoop-auxiliaries','Premium scoop coupling 175058 Rev3, approved 19-Feb-2019. Sheet explicitly lists '+tag+'. Vendor design applicability is retained separately from conveyor GA model selection.')
  c=tag+' Drive assembly Scoop coupling';r=[.65,.035,.988,.963]
  b.a(c,'model_number',size,page,r,'',condition='Vendor scoop-coupling GA explicitly lists this conveyor; retain separately from conveyor GA selection')
  if tag=='EBA-8':b.a(c,'source_discrepancy','Conveyor GA sheet 5 selects PST-530; vendor scoop GA sheet 1 explicitly assigns EBA-8 to 500 PST. The auxiliaries below describe that vendor selection. Final installed model and component applicability remain unresolved.',page,r)
  for key,v,u,cond in [('lubricant_fill_quantity',270,'L','Oil capacity; verify against final selected/installed coupling'),('lubricant_grade','ISO VG 46: MAK 46 / Enklo 46 / Servo System 46',None,'Source alternatives, not an inferred substitution recommendation'),('maximum_working_pressure',3,'kg/cm2','Oil circuit'),('design_temperature_limit',75,'degC','Maximum oil temperature at 50 degC ambient, full load'),('fusible_plug_temperature',145,'degC','+/-5 degC')]:b.a(c,key,v,page,r,u,cond)
  pump=component(b,c,'Oil circulation pump','oil_circulation_pump',page,r,'Circulate coupling oil through the cooling and filtration circuit.',[('quantity',1,'unit'),('assembly_arrangement','Gear pump with relief valve'),('rated_flow',150,'L/min'),('nominal_pressure',3,'kg/cm2')])
  component(b,pump,'Motor','electric_motor',page,r,props=[('motor_rated_power',2.2,'kW'),('motor_speed',1415,'rpm'),('motor_supply_frequency',50,'Hz'),('assembly_arrangement','Three-phase AC')])
  radiator=component(b,c,'Radiator','oil_cooler',page,r,'Reject heat from the coupling oil.',[('quantity',1,'unit')])
  component(b,radiator,'Fan motor','electric_motor',page,r,props=[('motor_rated_power',fanpower,'kW'),('motor_speed',1350,'rpm')])
  component(b,c,'Oil filter','oil_filter',page,r,props=[('quantity',1,'unit'),('assembly_arrangement','20 mesh SS304 strainer')])
  act=component(b,c,'Scoop actuator','electric_actuator',page,r,'Position the scoop tube: IN disengages and OUT engages the coupling.',[('ingress_protection','IP55'),('actuator_travel_time',4,'s','IN / disengage'),('actuator_travel_time',8,'s','OUT / engage')])
  component(b,act,'Dual-speed motor','electric_motor',page,r,props=[('motor_rated_power',.1,'kW','Low speed'),('motor_rated_power',.25,'kW','High speed'),('motor_speed',685,'rpm','Low speed'),('motor_speed',1380,'rpm','High speed'),('motor_voltage',415,'V'),('motor_supply_frequency',50,'Hz')])
  for name,typ,count in [('TS-1 / TS-2','temperature_switch',2),('DPS','differential_pressure_switch',1),('PS','pressure_switch',1),('FSO','flow_switch',1),('TGO','temperature_gauge',1),('PGO','pressure_gauge',1),('Sight glass','mechanical_component',1),('Junction box','junction_box',1)]:
   component(b,c,name,typ,page,r,props=[('quantity',count,'devices','Per vendor assembly; TS/PS etc. are drawing symbols, not verified field loop tags')])
  for child in [pump,radiator]:b.rel(child,'serves_equipment',c,page,r)
  b.a(c,'source_gap','Instrument drawing symbols do not establish plant loop IDs. Alarm/trip thresholds, controller wiring and actual oil fill require applicable final records.',page,r)
  b.finish(out)

def stacker_lubrication(s,out):
 b=Batch(s,'stacker_lube','EAD-1-central-lubrication','Centralized lubrication GA 175148 Rev1, FIO 22-Apr-2019. '+FAMILY)
 r=[.456,.33,.79,.58];group=component(b,'EAD-1','Central grease lubrication','lubrication_system',1,r,'Three independent lubrication pump systems serving the stacker mechanism groups.')
 b.a(group,'quantity',3,1,r,'pump units','One for slewing/boom pulley area, one for long-travel wheels, one for tripper wheels/pulleys')
 b.a(group,'lubricant_grade','Lithium grease: Mobilux EP2 or Shell Alvania EP (LF)2',1,r,'',condition='Source examples; final lubricant and service interval require the machine maintenance record')
 for name,targets in [('Slewing and boom pulleys',['EAD-1 Slew system','EAD-1 Boom conveyor']),('Long-travel wheels',['EAD-1 Travel system']),('Tripper wheels and pulleys',['EAD-1 Travelling tripper'])]:
  branch=component(b,group,name,'functional_assembly',1,r)
  pump=component(b,branch,'Pump unit','lubrication_pump',1,r,props=[('model_number','KSP8-65S'),('rated_flow',65,'mL/min'),('nominal_pressure',30,'MPa')])
  component(b,pump,'Reservoir','oil_tank',1,r,props=[('tank_capacity',20,'L')])
  component(b,pump,'Motor','electric_motor',1,r,props=[('motor_rated_power',.25,'kW')])
  for name2,typ in [('Distributor','mechanical_component'),('Safety valve','pressure_relief_valve'),('Filter','oil_filter'),('Pipelines and joints','functional_assembly'),('Control box','local_control_panel')]:component(b,branch,name2,typ,1,r)
  for target in targets:b.rel(branch,'serves_equipment',target,1,r)
 b.a(group,'source_gap','Drawing first-fill quantities do not establish routine regreasing quantity or interval. Pump labels are descriptive; installed tags and controller timings need verification.',1,r)
 b.finish(out)

def fire_protection(s,out):
 b=Batch(s,'fire','EAD-1-fire-detection-and-suppression','Minimax FDA/FM200 drawing 179063 Rev2, FIO 14-Nov-2019. '+FAMILY)
 r=[.023,.065,.965,.955]
 group=component(b,'EAD-1','Fire detection and clean-agent system','fire_protection_system',5,r,'Detect fire and release HFC227ea in the electrical house and operator cabin.')
 panel=component(b,group,'FMZ5000 panel','fire_alarm_panel',6,r,props=[('model_number','FMZ5000'),('quantity',1,'panel','Shared machine panel in merged BOM column')])
 house=component(b,'EAD-1','Electrical house','plant_building',2,r,props=[('assembly_arrangement','Fire drawing protected enclosure dimensions 10.5 x 3 x 2.7 m')])
 for zone,place,litres,charge,nozzles,detectors in [('Z101',house,80,50,2,2),('Z201','EAD-1 Operator cabin',22,11,1,1)]:
  z=component(b,group,zone+' Protected zone','functional_assembly',5,r)
  b.rel(z,'protects_equipment',place,5,r)
  bank=component(b,z,'Cylinder bank','fire_suppression_cylinder_group',6,r,props=[('quantity',2,'cylinders','Per-zone BOM quantity; active/standby allocation is not established'),('cylinder_volume',litres,'L','Each cylinder'),('agent_charge',charge,'kg','HFC227ea per cylinder'),('nominal_pressure',25,'bar')])
  component(b,z,'Discharge nozzles','fire_suppression_nozzle',6,r,props=[('quantity',nozzles,'nozzles'),('assembly_arrangement','DN25 Rp, 360 degrees, four bores')])
  component(b,z,'Smoke detectors','smoke_detector',6,r,props=[('quantity',detectors,'detectors'),('model_number','Apollo 58000-650')])
  component(b,z,'Heat detectors','heat_detector',6,r,props=[('quantity',detectors,'detectors'),('model_number','Apollo 58000-450')])
  component(b,z,'Electrical release devices','electric_actuator',6,r,props=[('quantity',2,'devices')])
  component(b,z,'Cylinder manual release devices','mechanical_component',6,r,props=[('quantity',2,'devices')])
  component(b,z,'Manifold and discharge pressure switch','functional_assembly',6,r,props=[('assembly_arrangement','One DN50 manifold and one pressure switch per zone')])
  b.rel(panel,'controls',z,5,r,network='control',condition='Design release circuit: 24 VDC, 30 s delay; manual/automatic selection and abort facilities shown. Not a commissioned setting or operating instruction.')
  b.a(z,'source_gap','BOM shows two cylinders per zone, while schematic charge notation states one cylinder. Do not infer duty/reserve allocation or discharge quantity without the final release cause-and-effect.',5,r)
 b.a('EAD-1 Operator cabin','source_discrepancy','Machine BOD cabin dimensions are 2.4 x 1.9 x 2.4 m; fire design uses 2.4 x 1.9 x 2.5 m. Protected-volume design and final enclosure dimensions require reconciliation.',5,r)
 b.a(group,'source_gap','Final release logic, commissioned delay, isolations and inspected cylinder status are not established. This machine system does not establish stockpile fire hydrant, monitor or coal-temperature coverage.',5,r)
 b.finish(out)

def runoff(s,out):
 b=Batch(s,'runoff','yard1-runoff-collection','Sump and runoff water P&ID 175259, Sept-2019 submission. Yard 1 / UEF-7 pit explicitly contains SP-8G and SP-8H; other SP-8 pairs are separate yard pits.')
 r=[.718,.523,.84,.643];group=component(b,YARD,'Runoff collection','drainage_system',1,r,'Collect stockpile runoff in the sump shared by CHP SP-1 and UEF-7, then discharge toward the common coal runoff/settling pond.')
 pit=component(b,group,'Stockpile 1 and UEF-7 sump','sump',1,r,props=[('assembly_arrangement','Shared pit 6.0 m long x 3.5 m wide x 2.2 m high'),('design_volume',46.2,'m3'),('location_description','P&ID CHP SP-1 / UEF-7 branch; exact field coordinates not established')])
 b.rel(pit,'associated_with','UEF-7',1,r,condition='Pit also receives UEF-7 drainage; functional Yard 1 grouping does not imply exclusive service')
 schedule=[.839,.308,.966,.35]
 for tag in ['SP-8G','SP-8H']:
  pump=component(b,pit,tag,'pump',1,r)
  b.a(pump,'equipment_tag',tag,1,r)
  for key,v,u in [('flow_capacity',45,'m3/h'),('pump_head',40,'m'),('motor_rated_power',22,'kW')]:b.a(pump,key,v,1,schedule,u,condition='SP-8A through SP-8H shared schedule; this local pit identifies G/H')
  b.a(pump,'nominal_diameter',100,1,r,'NB','Individual discharge line')
  b.rel(pump,'associated_with','CHP Stockpile Sump Pumps SP-8A to SP-8H',1,schedule,condition='Member of project schedule; do not count group and local units as additional physical pumps')
  b.rel(pump,'supplies_water_to','CHP Coal Run-off Pond',1,[.469,.518,.84,.969],network='utility',condition='Runoff disposal via common line and settling/collection arrangement')
 panel=component(b,pit,'Local control panel','local_control_panel',1,r)
 level=component(b,pit,'Level-switch controls','level_switch',1,r)
 b.rel(level,'control_signal_to',panel,1,r,network='control')
 b.a(group,'operating_requirement','Sump pumps use level-based automatic start/stop with local manual selection; project SP-8 schedule is four working plus four standby across four yards. Local duty assignment and installed switch levels require verification.',1,[.613,.78,.805,.958])
 b.rel('CHP Coal Run-off Pond','serves_equipment',group,1,[.469,.518,.84,.969],condition='Shared downstream collection/settling facility; not a Yard 1-owned asset')
 b.a(YARD,'source_gap','Stockpile fire-water coverage, coal-temperature/age monitoring, shed structural inspection details, rail alignment/anchoring records and approved maintenance intervals remain open. Absence from this pilot is not evidence that those systems are absent.',1,r)
 b.finish(out)

def conveyor_controls(s,out):
 b=Batch(s,'flow','yard1-conveyor-controls','CHP Control Write-up Rev04, approved on condition 06-Apr-2020. General HT conveyor requirements are recorded with Yard 1 path-specific requirements; this is source logic, not verified PLC code or commissioned settings.')
 for tag in ['EAC-7','EBA-8']:
  drive=tag+' Drive assembly';c=drive+' Scoop coupling';act=c+' Scoop actuator';pump=c+' Oil circulation pump';fan=c+' Radiator Fan motor';motor=drive+' Main motor';br=drive+' Thruster brake'
  b.a(tag,'sequence_logic','Radiator running feedback -> oil circulation pump -> main HT motor -> brake release -> scoop OUT engagement. Normal stop: scoop IN -> brake apply -> main motor off -> oil pump stop -> radiator stop.',26,[.16,.793,.897,.934])
  b.a(motor,'start_permissive','All winding temperatures <120 degC; DE/NDE bearing temperatures <70 degC; electrical healthy; local stop reset.',27,[.16,.216,.897,.510])
  b.a(motor,'trip_condition','Any winding temperature >130 degC; any DE/NDE bearing temperature >80 degC; electrical trip; or local stop operated.',27,[.16,.216,.897,.510])
  b.a(br,'operating_requirement','Brake released with the conveyor start sequence; applied when main motor is off or coupling disengaged. Electrical healthy required; electrical trip is a trip condition.',27,[.16,.519,.897,.674])
  b.a(pump,'start_permissive','Radiator ON, oil temperature normal, local stop reset and electrical healthy.',28,[.16,.209,.897,.525])
  b.a(pump,'trip_condition','Oil temperature high; main motor OFF after stated 300 s delay; oil flow unhealthy after 10 s; or electrical trip.',28,[.16,.209,.897,.525])
  b.a(pump,'control_timer_delay',30,28,[.16,.231,.897,.284],'s','Separate normal off-command stopping delay, adjustable; not the 300 s motor-OFF trip delay')
  b.a(act,'start_permissive','Own main motor ON, oil pump ON, brake released, electrical healthy, local stop reset, PCS/BSS healthy and source-listed chute/gate/downstream conditions; path-specific selection must also be satisfied.',28,[.16,.536,.897,.852])
  b.a(act,'source_discrepancy','General CBS permissive and trip wording both say not operated, leaving trip polarity unresolved. Succeeding-conveyor/scoop conditions also require application review; no executable Boolean logic is inferred.',28,[.16,.536,.897,.944])
  for child,p,rg,condition in [('Pull-cord switches (PCS)',28,[.16,.865,.897,.943],'PCS operated -> scoop IN/disengage'),('Belt-sway switches (BSS)',28,[.16,.865,.897,.943],'BSS operated -> scoop IN/disengage'),('Zero-speed switch (ZSS)',29,[.16,.205,.897,.449],'ZSS operated with source-stated 60 s on-delay -> scoop IN/disengage')]:
   sensor=tag+' Belt protection devices '+child
   b.a(sensor,'trip_condition',condition,p,rg);b.rel(sensor,'control_signal_to',act,p,rg,condition=condition,network='control')
  b.a(tag+' Belt protection devices Zero-speed switch (ZSS)','trip_threshold',85,9,[.145,.815,.898,.900],'% rated belt speed','General control requirement: below 85% of rated speed; actuator action/delay is recorded separately')
  for source,target,condition in [(fan,pump,'Radiator running is required for oil pump start'),(pump,act,'Oil pump ON is required for scoop engagement'),(br,act,'Brake released is required for scoop engagement'),(motor,act,'Own main motor ON is required for scoop engagement')]:b.rel(source,'control_signal_to',target,28,[.16,.209,.897,.852],network='control',condition=condition)
  b.a(c+' FSO','trip_condition','Oil flow unhealthy after 10 s is listed for both oil pump trip and scoop disengagement.',29,[.16,.389,.897,.448])
 b.a('EAC-7','start_permissive','Path 5 table: scoop actuator disengaged; pressure switch and flow switch at cooler inlet healthy.',51,[.125,.407,.883,.469])
 b.a('EAC-7 Drive assembly Scoop coupling Scoop actuator','start_permissive','Path 2 and Path 5 tables: EAD-1 stacker running AND EAC-7 main motor running; select EAC-7 with EAD-1.',43,[.125,.205,.883,.367])
 b.rel('EAD-1','control_signal_to','EAC-7 Drive assembly Scoop coupling Scoop actuator',43,[.125,.205,.883,.367],network='control',condition='Selected EAD-1 running AND EAC-7 main motor running for Yard 1 scoop engagement')
 cond='Path 3 reclaim: (FG-10 REV toward EBA-15A AND EBA-15A running) OR (FG-10 FWD toward EBA-15B AND EBA-15B running).'
 b.a('EBA-8','start_permissive',cond,46,[.125,.657,.883,.735])
 for item in ['FG-10','EBA-15A','EBA-15B']:b.rel(item,'control_signal_to','EBA-8',46,[.125,.657,.883,.735],network='control',condition=cond)
 b.finish(out)

def reconcile_weigher(s,out):
 b=Batch(s,'stacker','EAD-1-reuse-existing-boom-weigher','Stacker BOD 175249 Rev2 page 3 identifies the boom load-cell belt scale; the existing EAD-1 Boom Belt Weigher already represents this component. Reuse its canonical identity, retaining the new design facts.')
 b.rel('EAD-1 Boom Belt Weigher','part_of','EAD-1 Boom conveyor',3,[.155,.312,.916,.36])
 b.ops.append({'op':'merge','source':b.ids['EAD-1 Boom conveyor Belt scale'],'target':b.ids['EAD-1 Boom Belt Weigher'],'reason':'Same EAD-1 boom belt weighing component; preserve the pre-pilot identity and source-supported assembly placement.',**b.evidence(3,[.155,.312,.916,.36])})
 b.finish(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--expected-version',type=int,default=484);p.add_argument('--output-name',default='rehearsal');args=p.parse_args()
 sys.stdout.reconfigure(encoding='utf-8')
 plant=ROOT/'data/plant';base=ROOT/'output/yard1-pilot';base.mkdir(exist_ok=True,parents=True)
 snap=json.loads((base/'snapshot.json').read_text(encoding='utf-8'))
 for d in snap['documents']:
  if d['id'] in DOCS.values() and hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()!=d['sha256']:raise RuntimeError('Source hash mismatch '+d['name'])
 ro=sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True)
 version=int(ro.execute("select value from meta where key='version'").fetchone()[0])
 if version!=args.expected_version:raise RuntimeError(f'Expected {args.expected_version}, found {version}. Reconcile before running.')
 folder=base/('accepted' if args.apply else args.output_name);folder.mkdir(exist_ok=True,parents=True)
 if (folder/'commits.jsonl').exists():raise RuntimeError('Run log exists; inspect previous run rather than replaying blindly.')
 backup=base/f'backup-v{version}.sqlite3'
 if not backup.exists():
  with sqlite3.connect(backup) as dst:ro.backup(dst)
 if not args.apply:
  with sqlite3.connect(folder/'plant.sqlite3') as dst:ro.backup(dst)
  s=Store(folder)
 else:s=Store(plant)
 ro.close()
 foundation(s,folder)
 conveyor(s,folder,'EAC-7','c7');conveyor(s,folder,'EBA-8','c8')
 scoop_auxiliaries(s,folder)
 stacker(s,folder);reclaimer(s,folder);hydraulic(s,folder)
 spds(s,folder);spds_physical(s,folder);spds_risers(s,folder);shared_controls(s,folder)
 machine_dust(s,folder);lubrication(s,folder);stacker_lubrication(s,folder);fire_protection(s,folder);runoff(s,folder);conveyor_controls(s,folder)
 reconcile_weigher(s,folder)
 (folder/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
