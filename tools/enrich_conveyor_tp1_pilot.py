"""Reviewed source-backed EAC-1A/1B + UEF-1 enrichment. No direct plant SQL writes.

Default: rehearse all proposals in an isolated SQLite copy. --apply accepts the
reviewed batches through chp.reviewed_ingestion.stage / chp.patches.commit.
Source page regions and scope notes were visually checked in this session.
"""
import argparse, hashlib, json, re, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import commit, validate

DOCS={
 'ga':'doc_603b4d9077e14d16b605','drive':'doc_957d8f8bd41c4e71be3c',
 'scoop':'doc_7aa49cc0d1c34af7ac06','brake':'doc_64825298f3d243368408',
 'gear':'doc_97e93732778e4618b52b','geared':'doc_62fdccede7154dc2b8b6',
 'layout':'doc_7568f1550b254ee2a94a','dfds':'doc_bca09d68af9b43e3b633',
 'philosophy':'doc_294aacf286d246769e32','fas':'doc_3cfdfb0f23c6429eb268',
 'header':'doc_9b7d3360a5e84ec2abc3','control':'doc_4f2cd96c3b1e413ea4b5',
 'bearing':'doc_41860f7c9ac2467bbdb4','sump':'doc_31b03f5030bc4db69d8d',
 'sump_pid':'doc_0453a0a014424f1cae06','nozzle':'doc_5537009e2cff4fad875e',
}
TYPES={
 'functional_assembly':'A source-supported equipment assembly or functional component collection; not an additional physical machine.',
 'conveyor_belt':'The continuous conveying belt identified in a conveyor design.',
 'belt_sway_switch_group':'The documented collection of belt-sway protection switches for one conveyor; individual installation tags may remain unknown.',
 'pull_cord_switch_group':'The documented collection of pull-cord protection switches for one conveyor; preserves pairs versus individual devices.',
 'temperature_switch':'Temperature-actuated switch with source-stated sensing location and function.',
 'flow_switch':'Flow-actuated switch with source-stated sensing location and function.',
 'idler_group':'Documented group of conveyor idlers of a particular function, without inventing individual roller tags.',
 'take_up_assembly':'Conveyor belt tensioning mechanism with its source-supported trolley, pulley, rope, sheave and counterweight.',
 'brake_assembly':'Documented brake assembly acting on a rotating drive.',
 'electrohydraulic_thruster':'Electrically powered hydraulic thruster used to release the source-stated spring-applied brake.',
 'mechanical_component':'Individually navigable mechanical component identified by the source; label is descriptive if no plant tag is supplied.',
 'oil_circulation_pump':'Pump circulating oil through a coupling and its cooler/filter circuit.',
 'oil_filter':'Filter or strainer identified in an equipment oil circuit.',
 'electric_actuator':'Electrically driven positioning actuator identified in an equipment design.',
 'spray_application_point':'Identified DFDS application zone serving a particular receiving or discharge interface.',
 'spray_header':'Air or water header supplying an identified DFDS nozzle group.',
 'under_belt_switch':'Under-belt load-detection switch used for the documented conveyor-running-with-load signal.',
 'local_control_panel':'Local control panel identified by the source and linked to its controlled equipment.',
 'chute_interface':'Source-identified receiving/discharge chute interface; not an invented fabrication tag or a claim of a separate fabricated chute.',
 'air_receiver':'Compressed-air receiver identified in a utility system.',
 'utility_header':'Identified utility distribution header or main; service type is recorded separately.',
}
DEFS={
 'equipment_role':('string','many','Source-supported purpose or role of this equipment or component.'),
 'location_description':('string','many','Source-stated physical position with datum/end/floor qualifications; not inferred coordinates.'),
 'source_gap':('string','many','Explicit unresolved evidence or applicability gap recorded during equipment review; not proof that equipment is absent.'),
 'source_discrepancy':('string','many','Source disagreement or ambiguous wording requiring reconciliation; no value is silently preferred.'),
 'individual_device_count':('number','one','Derived count of individual devices, kept distinct from the original pair/group quantity.'),
 'assembly_arrangement':('string','many','Source-supported mechanical, utility or device arrangement.'),
 'lubricant_grade':('string','many','Source-stated lubricant specification; not an inferred replacement recommendation.'),
 'lubricant_fill_quantity':('number','many','Source-stated lubricant quantity with the stated equipment and fill basis.'),
 'rated_flow':('number','many','Rated fluid flow at the source-stated condition and original unit.'),
 'nominal_pressure':('number','many','Source-stated nominal operating pressure, distinct from trip setting or instrument range.'),
 'maximum_working_pressure':('number','many','Source-stated maximum working pressure; pressure reference is retained if known.'),
 'alarm_threshold':('number','many','Source-stated alarm threshold; inequality, quantity and applicability remain in context.'),
 'trip_threshold':('number','many','Source-stated trip threshold; inequality, action and applicability remain in context.'),
 'operating_temperature':('number','many','Source-stated nominal/design operating temperature under a stated condition.'),
 'lubrication_method':('string','one','Source-stated method of lubricating this assembly.'),
 'shaft_handing_rotation':('string','one','Source-stated shaft handing and relative rotation, referenced to the drawing viewpoint.'),
 'gear_ratio_nominal':('number','one','Nominal gearbox reduction ratio, distinct from the exact actual design ratio.'),
 'gear_ratio_actual':('number','many','Actual design gear ratio as stated by a source; rounding differences retain their sources.'),
 'device_spacing':('number','many','Source-stated device spacing or interval; side and group scope remain explicit.'),
 'belt_cover_thickness':('number','many','Source-stated belt cover thickness with top/bottom side qualification.'),
 'component_dimension':('number','many','Source-stated component dimension; the dimension name and basis remain in context.'),
 'component_material':('string','many','Source-stated material for an identified component or surface.'),
 'motor_supply_frequency':('number','many','Source-stated motor power supply frequency; tolerance is recorded in context.'),
 'rated_capacity':('number','many','Source-stated equipment capacity at the stated rated/design condition.'),
 'design_temperature_limit':('number','many','Source-stated design temperature limit, not a commissioned alarm/trip setting.'),
}

class Batch:
 def __init__(self,store,key,name,basis):
  self.s=store;self.key=key;self.doc=DOCS[key];self.name=name;self.basis=basis;self.ops=[];self.visual=set();self.pages=set();self.gaps=[]
  self.m=store.model();self.version=self.m['version'];self.ont={o['key']:o for o in self.m['ontology']}
  self.ids={e['label']:e['id'] for e in self.m['entities'] if e['id']==e['canonical_id'] and not e.get('inactive')}
  self.ev=store.rows('SELECT * FROM evidence WHERE document_id=? ORDER BY page,id',(self.doc,))
  self.live=[a for a in self.m['assertions'] if not a.get('retirement') and not a.get('suppressed')]
 def evidence(self,page,region=None,quote=None):
  rows=[e for e in self.ev if e['page']==page]
  if quote:
   pattern=r'\s+'.join(re.escape(word) for word in quote.split())
   found=next(((e,re.search(pattern,e['text'])) for e in rows if re.search(pattern,e['text'])),None)
   e=found[0] if found else None
   if found:quote=found[1].group(0)
  else:e=next((e for e in rows if e['image']),None)
  if not e:raise ValueError((self.name,page,quote))
  ref={'evidence_id':e['id'],'quote':quote or ''}
  if region:ref['region']=region;self.visual.add(e['id'])
  self.pages.add(page)
  return {'origin':'explicit','confidence':.98,'evidence':[ref]}
 def define(self,key,kind,value_type,definition,prov,cardinality='many'):
  if key not in self.ont:
   op={'op':'define','key':key,'kind':kind,'value_type':value_type,'definition':definition,'cardinality':cardinality,**prov};self.ops.append(op);self.ont[key]=op
  elif self.ont[key]['kind']!=kind or self.ont[key]['value_type']!=value_type:raise ValueError(('Ontology mismatch',key))
 def prop(self,key,val,prov):
  typ='boolean' if isinstance(val,bool) else 'number' if isinstance(val,(int,float)) else 'string'
  spec=DEFS.get(key,(typ,'many','Source-stated '+key.replace('_',' ')+' for this equipment; units, conditions and applicability are preserved.'))
  self.define(key,'property',spec[0],spec[2],prov,spec[1])
 def entity(self,label,typ,page,region,parent=None,role=None):
  pr=self.evidence(page,region)
  if label not in self.ids:
   tid='tmp_pilot_'+str(len(self.ids));self.ids[label]=tid;self.ops.append({'op':'entity','id':tid,'label':label,**pr})
  self.define(typ,'entity_type','string',TYPES.get(typ,typ.replace('_',' ')+' explicitly identified by the source.'),pr)
  self.a(label,'instance_of',typ,page,region,kind='classification')
  if parent:self.rel(label,'part_of',parent,page,region)
  if role:self.a(label,'equipment_role',role,page,region)
  return label
 def a(self,label,key,val,page,region=None,unit=None,condition=None,kind='specification',origin='explicit',quote=None,basis=None):
  pr=self.evidence(page,region,quote);pr['origin']='inferred' if key in ('source_gap','source_discrepancy') else origin
  self.prop(key,val,pr)
  ctx={'kind':kind,'basis':basis or self.basis}
  if condition:ctx['condition']=condition
  op={'op':'assert','subject':self.ids[label],'predicate':key,'value':val,'context':ctx,**pr}
  if unit:op['unit']=unit
  self.append(op)
 def rel(self,label,key,target,page,region=None,condition=None,network=None,origin='explicit',quote=None):
  pr=self.evidence(page,region,quote);pr['origin']='inferred' if key in ('source_gap','source_discrepancy') else origin
  self.define(key,'relation','entity',{
   'protects_equipment':'Source-stated protection association; exact action is retained in the associated control facts, not inferred from monitoring.',
   'control_signal_to':'Subject device supplies a documented control signal/permissive to the receiving assembly; exact Boolean logic remains in context.',
   'sprays_at':'Subject spray application point or nozzle group suppresses dust at the identified receiving/discharge interface.',
   'design_detail_applies_to':'Documented design-detail applicability to the identified equipment; does not establish field/as-built verification.',
   'associated_with':'Source-supported association retained separately from ownership, material flow and control function.',
  }.get(key,key.replace('_',' ')+' relationship explicitly supported by the cited source.'),pr)
  ctx={'kind':'connection' if network else 'classification','basis':self.basis}
  if condition:ctx['condition']=condition
  if network:ctx.update(network=network,verification='documented' if origin=='explicit' else 'unverified')
  self.append({'op':'assert','subject':self.ids[label],'predicate':key,'object_entity':self.ids[target],'context':ctx,**pr})
 def append(self,op):
  # Avoid re-adding same claim from the same page. Independent source claims are retained.
  def same(a):
   return (a.get('canonical_subject',a.get('subject'))==op['subject'] and a['predicate']==op['predicate'] and a.get('value')==op.get('value') and a.get('canonical_object',a.get('object_entity'))==op.get('object_entity') and a.get('unit')==op.get('unit') and a.get('context',{}).get('condition')==op['context'].get('condition') and any(e['evidence_id'] in {z['evidence_id'] for z in op['evidence']} for e in a.get('evidence',[])))
  if not any(same(a) for a in self.live) and not any(same(a) for a in self.ops if a['op']=='assert'):self.ops.append(op)
 def finish(self,out,apply=True):
  body={'summary':self.name,'operations':self.ops,'intake_assessment':{'route':'mixed','purpose':'Equipment-centered supplemental review for EAC-1A, EAC-1B and UEF-1. Build navigable assemblies and fact-level source traceability.','questions':['What components and local auxiliaries are documented for this equipment?','Where is the exact source of each specification, quantity and relationship?','Which control or utility dependencies apply?'],'gaps':self.gaps+['Supplemental scope: newly structured claims come only from pages '+', '.join(map(str,sorted(self.pages)))+'. Other document blocks are retained as source inventory/context; this is not a fresh exhaustive extraction of every equipment in the document.','These are source-stated design records. Field tags, installed condition and commissioned settings are not established by this intake.'],'reviewed_evidence_ids':[e['id'] for e in self.ev]}}
  report=validate(self.s,{'summary':body['summary'],'operations':self.ops},self.doc,self.version,visual_ids=self.visual)
  if report['errors']:raise ValueError(json.dumps(report['errors']))
  path=out/(self.name+'.json');path.write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
  result=stage(self.s,self.doc,body,visual_ids=self.visual,analysis_dir=str(out),expected_version=self.version)
  accepted=commit(self.s,result['proposal_id'])
  record={'name':self.name,'document_id':self.doc,'base_version':self.version,'result_version':self.s.version(),'operations':len(self.ops),'entities':sum(o['op']=='entity' for o in self.ops),'assertions':sum(o['op']=='assert' for o in self.ops),'visual_ids':sorted(self.visual),'pages':sorted(self.pages),'warnings':report['warnings'],'commit':accepted}
  with (out/'commits.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
  print(json.dumps({k:record[k] for k in ['name','result_version','operations','entities','assertions']},ensure_ascii=True),flush=True)

GA_BASIS='Conveyor EAC-1A/B GA 175011 Rev2; approved 26-Nov-2018. Design drawing, not installed/as-built verification.'
SCOOP_BASIS='Conveyor scoop coupling 175058: 530 PST GA sheet 2 Rev3 and family P&I/control sheets. Applicability explicitly lists EAC-1A and EAC-1B. Approved 19-Feb-2019; design basis only.'

def ga(store,out,tag):
 b=Batch(store,'ga',tag+'-assembly',GA_BASIS)
 table=[.69,.035,.958,.768];drive=[.69,.168,.958,.324];beltr=[.69,.321,.958,.385];pulley=[.757,.39,.949,.455];protection=[.757,.686,.949,.718]
 D=tag+' Drive assembly';M=tag+' Main motor';C=tag+' Scoop coupling PST-530';G=tag+' Drive Gearbox B3 450';L=tag+' Low-speed geared coupling RG-10';B=tag+' Thruster brake';P=tag+' Head pulley'
 b.entity(D,'functional_assembly',4,drive,tag,'Transmit motor power through the scoop coupling, reduction gearbox and low-speed coupling to the belt drive.')
 for label,typ in [(M,'electric_motor'),(C,'coupling'),(G,'gearbox'),(L,'coupling'),(B,'brake_assembly')]:b.entity(label,typ,4,drive,D)
 b.a(M,'manufacturer','BHEL',4,drive);b.a(M,'motor_rated_power',315,4,drive,'kW');b.a(M,'motor_speed',1488,4,drive,'rpm',condition='GA motor speed row, printed as speed (synch.)')
 b.a(M,'motor_voltage',3.3,4,drive,'kV',condition='GA supply tolerance +/-10%');b.a(M,'motor_supply_frequency',50,4,drive,'Hz',condition='GA supply tolerance +/-5%');b.a(M,'assembly_arrangement','Squirrel cage',4,drive)
 for label,model in [(C,'PST-530'),(G,'B3-450'),(L,'RG 10'),(B,'EBTM-500/DS/DG')]:b.a(label,'model_number',model,4,drive)
 b.a(B,'component_dimension',500,4,drive,'mm',condition='Brake drum diameter');b.a(G,'gear_ratio_nominal',17.1,4,drive)
 mech=tag+' Belt and mechanical assemblies';b.entity(mech,'functional_assembly',4,[.69,.32,.958,.705],tag)
 belt=b.entity(tag+' Conveyor belt','conveyor_belt',4,beltr,mech)
 for key,v,u,c in [('belt_width',2000,'mm',None),('belt_length',820 if tag.endswith('A') else 825,'m','Endless belt length'),('belt_cover_thickness',5,'mm','Top cover; GA notation 5/2'),('belt_cover_thickness',2,'mm','Bottom cover; GA notation 5/2')]:b.a(belt,key,v,4,beltr,u,c)
 b.a(belt,'assembly_arrangement','N/N HD-1000/5; 2000 B/W; cover grade FR',4,beltr)
 b.entity(P,'pulley',4,pulley,mech);b.a(P,'quantity',1,4,pulley,'No.',condition='Per conveyor drive pulley')
 b.a(P,'component_dimension',800,4,pulley,'mm',condition='Drive pulley diameter');b.a(P,'component_dimension',2200,4,pulley,'mm',condition='Face width');b.a(P,'component_dimension',2700,4,pulley,'mm',condition='Bearing centre distance');b.a(P,'assembly_arrangement','12 mm diamond-groove rubber lagging',4,pulley)
 pg=b.entity(tag+' Tail bend and snub pulleys','functional_assembly',4,pulley,mech)
 b.a(pg,'quantity',6,4,pulley,'No.',condition='Combined tail and bend/snub pulley group per conveyor; not six of each type')
 b.a(pg,'component_dimension',630,4,pulley,'mm',condition='Pulley diameter');b.a(pg,'component_dimension',2200,4,pulley,'mm',condition='Face width');b.a(pg,'component_dimension',2700,4,pulley,'mm',condition='Bearing centre distance')
 tail=b.entity(tag+' Tail pulley','pulley',1,[.075,.215,.195,.395],pg)
 b.a(tail,'location_description','Tail end at the coal jetty; see plan/elevation for tail pulley to P-28.',1,[.075,.215,.195,.395])
 take=b.entity(tag+' Horizontal gravity take-up','take_up_assembly',4,[.69,.616,.958,.68],mech)
 b.a(take,'assembly_arrangement','Horizontal gravity take-up with mark-up scale',4,[.69,.616,.958,.655]);b.a(take,'component_dimension',10000,4,[.69,.616,.958,.655],'mm',condition='Take-up pulley travel')
 tp=b.entity(tag+' Take-up pulley','pulley',4,[.757,.429,.949,.455],take);b.a(tp,'quantity',1,4,[.757,.429,.949,.455],'No.');b.a(tp,'component_dimension',630,4,[.757,.429,.949,.455],'mm',condition='Pulley diameter')
 rope=b.entity(tag+' Take-up wire rope','mechanical_component',4,[.69,.639,.958,.66],take);b.a(rope,'component_dimension',24,4,[.69,.639,.958,.66],'mm',condition='Rope diameter');b.a(rope,'assembly_arrangement','6x37 construction, fibre core (CF), MGR-1570; minimum breaking force 267 kN as printed',4,[.69,.639,.958,.66])
 sheave=b.entity(tag+' Take-up sheave','mechanical_component',4,[.69,.639,.958,.66],take);b.a(sheave,'component_dimension',550,4,[.69,.639,.958,.66],'mm',condition='Sheave diameter');b.a(sheave,'component_material','Cast iron, IS-210 grade 25',4,[.69,.639,.958,.66])
 cw=b.entity(tag+' Take-up counterweight','mechanical_component',4,[.757,.645,.949,.670],take);b.a(cw,'counterweight_mass',17400,4,[.757,.645,.949,.670],'kg',condition='Design weight per conveyor, as printed');b.a(cw,'assembly_arrangement','Cast iron blocks 300 x 260 x 30 mm, 17.5 kg each, quantity 994 as printed.',4,[.757,.645,.949,.670]);b.a(cw,'source_discrepancy','Rounding discrepancy: 994 blocks x 17.5 kg = 17395 kg, while the drawing states a 17400 kg design weight. Preserve both bases.',4,[.757,.645,.949,.670],origin='inferred')
 for label,qty,arr,rg in [
  ('Carrying idlers',560 if tag.endswith('A') else 567,'3 equal rolls, 35-degree trough, 159 mm diameter; 600 mm spacing at loading and 1000 mm elsewhere as indicated; 2-degree forward tilt',[.757,.464,.949,.490]),
  ('Self-aligning carrying idlers',26,'1500 mm pitch, 2-degree forward tilt',[.757,.488,.949,.505]),
  ('Return idlers',101 if tag.endswith('A') else 102,'10-degree trough, 159 mm diameter, 3000 mm pitch',[.757,.530,.949,.552]),
  ('Self-aligning return idlers',22,'1800 mm pitch',[.757,.551,.949,.568]),
  ('Flat return rollers',5,'Single roller near tail end, head end and take-up',[.757,.565,.949,.584]),
  ('Self-cleaning return idler',1,'Return belt near discharge pulley',[.757,.512,.949,.533])]:
  item=b.entity(tag+' '+label,'idler_group',4,rg,mech);b.a(item,'quantity',qty,4,rg,'No.',condition='Per conveyor, GA group count');b.a(item,'assembly_arrangement',arr,4,rg)
 for label,arr in [('External scrapers','Spring-loaded primary and secondary at discharge pulley; GA quantity 1 per conveyor as a listed assembly.'),('Internal scraper','V-plough near tail pulley; GA quantity 1 per conveyor.')]:
  item=b.entity(tag+' '+label,'mechanical_component',4,[.757,.665,.949,.691],mech);b.a(item,'assembly_arrangement',arr,4,[.757,.665,.949,.691])
 prot=b.entity(tag+' Belt protection devices','functional_assembly',4,protection,tag)
 for label,typ,qty,unit,arr,space in [('Pull-cord switches (PCS)','pull_cord_switch_group',14,'pairs','Both sides of conveyor',30),('Belt-sway switches (BSS)','belt_sway_switch_group',11,'pairs','Both sides of conveyor',40),('Zero-speed switch (ZSS)','zero_speed_switch',1,'No.','On tail pulley',None)]:
  node=b.entity(tag+' '+label,typ,4,protection,prot)
  b.a(node,'quantity',qty,4,protection,unit,condition='Per conveyor; original GA unit preserved');b.a(node,'location_description',arr,4,protection)
  b.rel(node,'protects_equipment',tag,4,protection)
  if space:b.a(node,'device_spacing',space,4,protection,'m',condition='Both sides; design interval, individual switch coordinates not given');b.a(node,'individual_device_count',qty*2,4,protection,'switches',condition=f'Derived: {qty} pairs x 2 switches per pair',origin='inferred')
  else:b.rel(node,'located_at',tail,4,protection)
  b.a(node,'source_gap','Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.',4,protection)
 # Head drives are physically shown at the transfer building, not along the whole belt.
 b.rel(D,'located_at','UEF-1',3,[.63,.05,.90,.387]);b.a(D,'location_description','Head-end drive arrangement at UEF-1; EAC-1A and EAC-1B have distinct layouts shown in plan.',3,[.63,.05,.90,.387])
 b.a(tag,'equipment_role','Receive uncrushed coal along the jetty and convey it to UEF-1 for transfer to the next conveyor stage.',1,[.09,.724,.72,.922])
 b.a(tag,'source_gap','Individual PCS/BSS tags, commissioning settings and complete chute-block-switch locations are unresolved. Counts here are approved GA design quantities.',4,protection)
 b.finish(out)

def drive(store,out):
 b=Batch(store,'drive','drive-schedule','Drive schedule 175107 Rev2, 13-Dec-2018, FIO 14-Dec-2018; EAC-1A/1B column. Source-stated design only.')
 for tag in ['EAC-1A','EAC-1B']:
  m=tag+' Main motor';g=tag+' Drive Gearbox B3 450';c=tag+' Scoop coupling PST-530';l=tag+' Low-speed geared coupling RG-10';br=tag+' Thruster brake'
  for node,key,val,u,cond in [(m,'motor_rated_power',315,'kW',None),(m,'motor_voltage',3300,'V','Supply tolerance +/-6% in this schedule'),(m,'motor_supply_frequency',50,'Hz','Supply tolerance +3%, -5% in this schedule'),(g,'gear_ratio_nominal',17.1,None,None),(g,'gear_ratio_actual',17.8,None,'Schedule rounded exact ratio'),(g,'gearbox_mechanical_power_rating',909,'kW',None),(g,'gearbox_thermal_power_rating',712,'kW','Schedule does not state ambient; see gearbox GA'),(c,'coupling_power_rating',380,'kW','At 1500 rpm; coupling rating, not motor rating'),(l,'coupling_power_per_speed_rating',1150,'HP/100 RPM',None),(br,'brake_torque_rating',440,'kg-m','Schedule torque rating; not the current adjusted torque')]:b.a(node,key,val,2,[.055,.19,.292,.81],u,cond)
  b.a(m,'source_discrepancy','Supply-tolerance discrepancy: GA gives 3.3 kV +/-10%, 50 Hz +/-5%; drive schedule gives 3300 V +/-6%, 50 Hz +3%/-5%. Field/nameplate applicability unresolved.',2,[.055,.26,.292,.345])
 b.finish(out)

def scoop(store,out,tag):
 b=Batch(store,'scoop',tag+'-scoop-details',SCOOP_BASIS);c=tag+' Scoop coupling PST-530';g=tag+' Drive Gearbox B3 450';m=tag+' Main motor'
 r=[.64,.056,.959,.72];scope=[.811,.058,.959,.299]
 pump=b.entity(tag+' Scoop oil circulation pump','oil_circulation_pump',2,scope,c)
 pm=b.entity(tag+' Scoop oil pump motor','electric_motor',2,[.657,.219,.81,.297],pump)
 cool=b.entity(tag+' Scoop oil radiator','hydraulic_oil_cooler',2,scope,c)
 fan=b.entity(tag+' Scoop radiator motor','electric_motor',2,[.657,.296,.81,.32],cool)
 act=b.entity(tag+' Scoop actuator','electric_actuator',2,scope,c)
 filt=b.entity(tag+' Scoop oil filter','oil_filter',5,[.279,.583,.465,.79],c)
 strainer=b.entity(tag+' Scoop suction strainer','oil_filter',5,[.148,.483,.309,.735],c)
 sump=b.entity(tag+' Scoop oil sump','mechanical_component',5,[.207,.431,.406,.576],c)
 fuse=b.entity(tag+' Scoop fusible plug','mechanical_component',5,[.717,.32,.958,.352],c)
 for node,key,v,u,cond in [(pump,'rated_flow',150,'L/min','Gear pump with relief valve'),(pump,'nominal_pressure',3,'kg/cm2','Pump discharge design pressure'),(pm,'motor_rated_power',2.2,'kW',None),(pm,'rated_rotational_speed',1415,'rpm',None),(fan,'motor_rated_power',.37,'kW',None),(fan,'rated_rotational_speed',1350,'rpm',None),(c,'lubricant_fill_quantity',270,'L','Fluid coupling oil capacity'),(c,'maximum_working_pressure',3,'kg/cm2',None),(c,'design_temperature_limit',75,'degC','Maximum oil temperature at 50 degC ambient, full load'),(cool,'operating_temperature',75,'degC','Radiator oil inlet'),(cool,'operating_temperature',70,'degC','Radiator oil outlet'),(act,'actuator_travel_time',4,'s','SCOOP IN disengagement'),(act,'actuator_travel_time',8,'s','SCOOP OUT engagement')]:b.a(node,key,v,2,r,u,cond)
 b.a(c,'lubricant_grade','Bharat Petroleum MAK 46 / Hindustan Petroleum ENKLO 46 / Indian Oil SERVO SYSTEM 46',2,[.814,.64,.943,.712])
 b.a(filt,'assembly_arrangement','Y-type filter, 40 mesh in the P&I schedule.',5,[.72,.277,.958,.332]);b.a(strainer,'assembly_arrangement','Suction strainer, 20 mesh in the P&I schedule.',5,[.72,.085,.958,.179])
 b.a(c,'source_discrepancy','Filter nomenclature requires reconciliation: GA supply list calls a 20-mesh oil-filter screen; P&I distinguishes a 20-mesh suction strainer and 40-mesh Y-filter. Do not replace one with the other without identifying the component.',2,[.811,.131,.959,.189])
 for child,key,v,u,cond in [(fuse,'fusible_plug_blowing_temperature',145,'degC','Fusible plug blowing temperature, GA tolerance +/-5 degC'),(c,'coupling_power_rating',380,'kW','Maximum transmission capacity at 1450-1500 rpm'),(c,'design_slip',3,'%','Maximum slip at absorbed power at design capacity')]:b.a(child,key,v,2,r,u,cond)
 b.rel(m,'mechanically_drives',c,2,[.08,.175,.642,.742],network='mechanical',condition='Input is motor side in applicable GA')
 b.rel(c,'mechanically_drives',g,2,[.497,.493,.649,.742],network='mechanical',condition='Output is gearbox side in applicable GA')
 b.rel(pm,'mechanically_drives',pump,2,[.656,.229,.81,.301],network='mechanical')
 b.rel(fan,'associated_with',cool,2,[.656,.296,.81,.326])
 # Follow actual oil arrows on the reviewed P&I, including the return circuit.
 for a,z in [(sump,strainer),(strainer,pump),(pump,cool),(cool,filt),(filt,c)]:b.rel(a,'utility_supply_to',z,5,[.174,.425,.47,.794],network='utility',condition='Coupling oil circulation path; not an isolation boundary')
 instruments=[('TS1','temperature_switch','Oil inlet line of coupling'),('TS2','temperature_switch','Oil outlet line of coupling'),('PS','pressure_switch','Oil inlet line of coupling'),('DPS','differential_pressure_switch','Across coupling oil filter'),('FSO','flow_switch','Outlet line of oil circulating pump')]
 for token,typ,loc in instruments:
  node=b.entity(tag+' Scoop '+token,typ,14,[.099,.576,.645,.695],c)
  b.a(node,'location_description',loc,14,[.099,.576,.645,.695]);b.a(node,'quantity',1,2,scope,'No.');b.rel(node,'monitors_equipment',pump if token=='FSO' else filt if token=='DPS' else c,14,[.099,.576,.645,.695])
  b.a(node,'source_gap','Field calibration and commissioned setting are not established by the vendor design table.',5,[.687,.512,.88,.614])
 ranges={'TS1':(70,150,'degC','RT107'),'TS2':(70,150,'degC','RT107'),'PS':(.1,1.0,'kg/cm2','RT112'),'DPS':(.1,1.1,'kg/cm2','D4-24B')}
 for token,(lo,hi,u,model) in ranges.items():
  node=tag+' Scoop '+token;b.a(node,'instrument_range_lower',lo,5,[.722,.164,.957,.238],u);b.a(node,'instrument_range_upper',hi,5,[.722,.164,.957,.238],u);b.a(node,'model_number',model,5,[.722,.164,.957,.238])
 for token,key,v,u,condition in [('TS1','nominal_design_value',70,'degC','P&I nominal temperature'),('TS1','alarm_threshold',85,'degC','High oil-temperature alarm'),('TS2','nominal_design_value',70,'degC','P&I nominal temperature'),('TS2','trip_threshold',110,'degC','Trip when greater than 110; final trip target must be read with control philosophy'),('PS','nominal_pressure',.5,'bar','P&I normal value'),('PS','alarm_threshold',.3,'bar','Alarm below 0.3'),('DPS','nominal_pressure',.3,'bar','P&I nominal differential pressure'),('DPS','alarm_threshold',.8,'bar','Alarm above 0.8'),('FSO','rated_flow',140,'L/min','P&I normal oil flow, 500/530 PST column'),('FSO','alarm_threshold',90,'L/min','Alarm below 90; 500/530 PST column')]:b.a(tag+' Scoop '+token,key,v,5,[.687,.512,.88,.614],u,condition)
 for token,typ,loc in [('TGO','temperature_sensor','Coupling oil temperature gauge'),('PGO','pressure_gauge','Coupling oil pressure gauge'),('SFG','mechanical_component','Oil sight-flow glass'),('JB','junction_box','Coupling instrument junction box')]:
  node=b.entity(tag+' Scoop '+token,typ,2,scope,c);b.a(node,'equipment_role',loc,2,scope)
 b.a(act,'operating_requirement','SCOOP IN disengages the coupling; SCOOP OUT engages the coupling. Actuator has manual handwheel and electrical positioning.',2,r)
 b.a(c,'source_gap','Internal service procedures, overhaul tolerances, instrument calibration sheets and installed equipment serial numbers remain unresolved.',2,r)
 b.finish(out)

def gearbox(store,out):
 b=Batch(store,'gear','gearbox-details','Gearbox GA 175056 Rev1, applicable sheet 7, explicitly lists EAC-1A/1B; approved 14-Dec-2018. Design ratings and oil fill, not maintenance history.')
 for tag in ['EAC-1A','EAC-1B']:
  g=tag+' Drive Gearbox B3 450';r=[.686,.07,.951,.529]
  for key,v,u,cond in [('gear_ratio_actual',17.820,None,'Actual ratio on gearbox GA'),('gearbox_mechanical_power_rating',909,'kW','At 1500 rpm'),('gearbox_thermal_power_rating',712,'kW','At 1500 rpm, 20 degC ambient'),('gearbox_thermal_power_rating',498.4,'kW','At 1500 rpm, 50 degC ambient'),('lubricant_fill_quantity',205,'L','Approximate gearbox oil quantity'),('equipment_mass',2840,'kg','Approximate net gearbox weight')]:b.a(g,key,v,7,r,u,cond)
  b.a(g,'lubricant_grade','ISO VG-320',7,r);b.a(g,'lubrication_method','Splash',7,r);b.a(g,'shaft_handing_rotation','P2/CW' if tag.endswith('A') else 'P1A/ACW',7,[.687,.07,.951,.184],condition='As referenced to vendor shaft-handing diagram, not an independent plant viewpoint')
  for child,typ in [('Holdback','mechanical_component'),('Cooling fan','mechanical_component'),('Oil dipstick','mechanical_component'),('Oil breather','mechanical_component'),('Oil drain plug','mechanical_component'),('Inspection and oil filling cover','mechanical_component')]:b.entity(tag+' Gearbox '+child,typ,7,[.079,.081,.95,.688],g)
  b.a(tag+' Gearbox Holdback','assembly_arrangement','Centrifugally released sprag type',7,r)
  b.a(g,'design_temperature_limit',45,7,[.42,.621,.687,.717],'degC',condition='Maximum oil temperature RISE above 50 degC ambient, not absolute oil temperature')
 b.finish(out)

def geared(store,out):
 b=Batch(store,'geared','low-speed-coupling-details','Geared coupling 175059 Rev3, sheet 2, RG-10, EAC-1A/B row. Approved 06-Feb-2019; source design and lubricant requirements.')
 for tag in ['EAC-1A','EAC-1B']:
  c=tag+' Low-speed geared coupling RG-10';r=[.076,.057,.953,.718]
  b.a(c,'manufacturer','GBM Manufacturing (P) Ltd',2,[.416,.762,.672,.873]);b.a(c,'lubricant_grade','Indian Oil SERVOGEM-II grease',2,[.685,.593,.957,.69]);b.a(c,'lubricant_fill_quantity',8.5,2,[.685,.593,.957,.69],'kg',condition='Grease quantity per set')
  b.a(c,'component_dimension',200,2,[.103,.42,.507,.501],'mm',condition='Gearbox side finished bore, H7 tolerance per drawing');b.a(c,'component_dimension',210,2,[.103,.42,.507,.501],'mm',condition='Pulley side finished bore, H7 tolerance per drawing')
  for child,qty in [('Hubs',2),('Sleeves',2),('O-rings',2),('Grease plugs',2)]:
   node=b.entity(tag+' RG-10 '+child,'mechanical_component',2,[.063,.835,.408,.943],c);b.a(node,'quantity',qty,2,[.063,.835,.408,.943],'No.',condition='Per coupling set, not plant spare quantity')
  b.rel(tag+' Drive Gearbox B3 450','mechanically_drives',c,2,r,network='mechanical',condition='Gearbox side explicitly identified as drive side')
  b.rel(c,'mechanically_drives',tag+' Head pulley',2,r,network='mechanical',condition='Pulley side explicitly identified as driven side')
 b.finish(out)

def pulley_bearings(store,out):
 b=Batch(store,'bearing','conveyor-head-pulley-design','Pulley shaft/bearing calculation 175074, approved 25-Feb-2019. PDF p3 maps EAC-1A/B to 20DR1(SS); p4 continues that same column. Calculated selection, not an installed bearing/nameplate confirmation.')
 for tag in ['EAC-1A','EAC-1B']:
  head=tag+' Head pulley';rg=[.018,.650,.76,.740]
  bearings=b.entity(tag+' Head pulley bearings','mechanical_component',4,rg,head)
  b.a(bearings,'model_number','23148 CCK',4,rg,condition='Selected bearing in 20DR1(SS) calculation column; installed identity unresolved')
  b.a(bearings,'source_gap','Bearing selection is from calculation. Verify the installed bearing, adapter, housing, seals and clearance before using it for procurement or replacement.',4,rg)
  b.rel('20DR1(SS)','calculation_applies_to_equipment',head,3,[.018,.475,.76,.604])
  b.a(head,'component_material','EN-8 shaft in 20DR1(SS) calculation',3,[.018,.475,.76,.630],condition='Calculation basis')
  b.a(head,'component_dimension',220,4,[.018,.454,.76,.510],'mm',condition='Selected head-pulley shaft diameter at bearing in calculation')
  b.a(head,'component_dimension',240,4,[.018,.250,.76,.345],'mm',condition='Selected head-pulley shaft diameter at hub in calculation')
 # Every selection retains the page establishing applicability as well as the
 # continued table containing its value; neither page alone proves both.
 applicability=b.evidence(3,[.018,.475,.76,.604])['evidence'][0]
 for op in b.ops:
  if applicability not in op.get('evidence',[]):op['evidence'].append(applicability)
 b.finish(out)

def brakes(store,out):
 b=Batch(store,'brake','brake-details','Brake GA 175060 Rev2, sheet 3, EAC-1A/B row; approved 31-Jul-2019. Retain disagreements with conveyor GA and drive schedule.')
 for tag in ['EAC-1A','EAC-1B']:
  br=tag+' Thruster brake';r=[.042,.558,.4,.964]
  th=b.entity(tag+' Brake thruster','electrohydraulic_thruster',3,[.689,.137,.967,.191],br)
  b.a(th,'model_number','ET-3250/TL',3,r);b.a(th,'lubricant_grade','Transformer oil as per IS:335-1983, EHV grade',3,r);b.a(th,'lubricant_fill_quantity',2.5,3,r,'L',condition='Thruster oil quantity')
  b.a(th,'motor_rated_power',375,3,r,'W',condition='Brake technical specification power consumption');b.a(th,'component_dimension',75,3,r,'mm',condition='Thruster stroke')
  b.a(br,'brake_torque_rating',440,3,r,'kg-m',condition='Maximum braking torque in EAC-1A/B row');b.a(br,'required_braking_torque',344,3,r,'kg-m',condition='Required braking torque in brake GA EAC-1A/B row')
  b.a(br,'brake_release_time_min',2,3,r,'s');b.a(br,'brake_release_time_max',2.5,3,r,'s');b.a(br,'brake_application_time_min',1,3,r,'s');b.a(br,'brake_application_time_max',6,3,r,'s')
  for child,qty in [('Brake shoes',2),('Brake liners',2),('Main spring',1),('Shoe clearance bolts',2)]:
   node=b.entity(tag+' '+child,'mechanical_component',3,[.687,.061,.967,.414],br);b.a(node,'quantity',qty,3,[.687,.061,.967,.414],'No.')
  ls=b.entity(tag+' Brake position limit switch','limit_switch',3,[.686,.316,.966,.462],br)
  b.a(ls,'assembly_arrangement','Jai Balaji model 45-18, 2 NO + 2 NC; sheet 3 note calls the switch brake-engage.',3,[.686,.316,.966,.462]);b.rel(ls,'monitors_equipment',br,3,[.686,.316,.966,.462])
  b.a(br,'operating_requirement','Spring force applies the brake; the thruster releases it by overcoming spring pressure. Source requires energized shoe clearance sufficient for free drum rotation.',3,[.3,.716,.69,.846])
  b.a(tag+' Brake liners','component_dimension',10,3,[.3,.716,.69,.846],'mm',condition='Brake liner thickness');b.a(tag+' Brake liners','component_material','Non-asbestos lining, interwoven brass wire, countersunk aluminium rivets',3,[.686,.211,.967,.462]);b.a(tag+' Brake liners','design_temperature_limit',200,3,[.3,.716,.69,.846],'degC',condition='Source-stated lining withstand temperature')
  b.a(tag+' Main motor','motor_rated_power',350,3,[.059,.556,.398,.632],'kW',condition='Brake selection table motor entry; conflicts with conveyor/drive/gearbox 315 kW design')
  b.a(tag,'source_discrepancy','Unresolved motor-rating discrepancy: brake GA EAC-1A/B row states 350 kW / 1480 rpm, whereas conveyor GA, drive schedule and gearbox GA state 315 kW. No installed/nameplate value has been selected.',3,[.059,.556,.398,.632])
  b.a(br,'source_discrepancy','Brake-position contact meaning requires reconciliation: sheet 3 calls the limit switch brake-engage; the control write-up uses brake-released feedback. Do not infer contact polarity from the component name.',3,[.686,.316,.966,.462])
 b.finish(out)

def transfer(store,out):
 b=Batch(store,'dfds','UEF-1-DFDS-zones','DFDS System-1 P&ID 175089 Rev1, approved 14-Dec-2018. UEF-1 application schedule and explicit piping arrows; design, not live valve state.')
 group=b.entity('UEF-1 DFDS application equipment','functional_assembly',1,[.033,.025,.28,.202],'UEF-1')
 b.rel(group,'part_of','DFDS System-1',1,[.033,.025,.28,.202]);b.a(group,'equipment_role','Local dry-fog application equipment serving the two incoming discharge ends and the two receiving conveyor interfaces at UEF-1.',1,[.64,.578,.814,.63])
 b.a(group,'application_point_count',4,1,[.64,.578,.814,.63]);b.a(group,'scheduled_nozzle_count',26,1,[.64,.578,.814,.63],condition='Derived UEF-1 total: 4 + 9 + 4 + 9; not system total or live operating count',origin='inferred')
 b.a('UEF-1','equipment_role','Transfer coal from EAC-1A discharge to EAC-2A receiving and from EAC-1B discharge to EAC-2B receiving; local dry-fog zones treat each interface.',1,[.034,.022,.279,.203])
 zone_rows=[('01','EAC-1A','Discharge',4),('02','EAC-2A','Receiving',9),('03','EAC-1B','Discharge',4),('04','EAC-2B','Receiving',9)]
 for num,conv,kind,count in zone_rows:
  rg=[.64,.576,.814,.634];iface=conv+' '+kind.lower()+' chute at UEF-1';zone='UEF-1 AP-'+num
  b.entity(iface,'chute_interface',1,[.033,.025,.28,.202],conv)
  b.rel(iface,'located_at','UEF-1',1,[.033,.025,.28,.202]);b.a(iface,'equipment_role',kind+' chute/hood interface shown in DFDS design; descriptive location, not a fabricated chute tag.',1,rg)
  b.entity(zone,'spray_application_point',1,rg,group);b.a(zone,'equipment_role',kind+' dust-suppression application point for '+conv,1,rg);b.a(zone,'scheduled_nozzle_count',count,1,rg,'No.',condition='P&ID total nozzles at this application point');b.a(zone,'scheduled_operating_nozzle_count',count,1,rg,'No.',condition='P&ID design operating quantity, not a live indication')
  b.rel(zone,'sprays_at',iface,1,rg)
  for token,typ in [('FAS','dfds_fas_unit'),('PRU','pressure_regulating_unit')]:b.entity('UEF-1 '+token+'-'+num,typ,1,rg,zone)
  b.rel('UEF-1 FAS-'+num,'utility_supply_to','UEF-1 PRU-'+num,1,[.033,.025,.28,.202],network='utility',condition='Separate air 20 NB and water 15 NB lines')
  b.rel('UEF-1 PRU-'+num,'utility_supply_to',zone,1,[.033,.025,.28,.202],network='utility',condition='Supplies the identified application-point spray headers')
  nozzles=b.entity(zone+' Nozzle group','spray_nozzle',1,rg,zone);b.a(nozzles,'quantity',count,1,rg,'No.',condition='Group count; no invented individual nozzle tags');b.rel(nozzles,'sprays_at',iface,1,rg)
  b.a(zone,'source_gap','Individual nozzle identification, installed orientation and commissioning checks remain unresolved; this record preserves the design application-point quantity.',1,rg)
 for tag in ['EAC-1A','EAC-1B']:
  receiving='EAC-2'+tag[-1];dis=tag+' discharge chute at UEF-1';rec=receiving+' receiving chute at UEF-1';rg=[.033,.025,.28,.202]
  for s,t in [(tag,dis),(dis,rec),(rec,receiving)]:b.rel(s,'material_flow_to',t,1,rg,network='material',condition='A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred')
 b.entity('UEF-1 DFDS air main','utility_header',1,[.033,.025,.28,.202],group)
 b.entity('UEF-1 DFDS water main','utility_header',1,[.033,.025,.28,.202],group)
 for num,_,_,_ in zone_rows:
  for medium,nb in [('air',20),('water',15)]:b.rel('UEF-1 DFDS '+medium+' main','utility_supply_to','UEF-1 FAS-'+num,1,[.033,.025,.28,.202],network='utility',condition=f'{medium} service, {nb} NB local branch')
 b.a(group,'source_discrepancy','Pressure-switch tag discrepancy: the UEF-1 P&ID inset shows both PS-01 and PS-02 labels; the DFDS control philosophy uses PS-02 for all four UEF-1 FAS permissives. Do not merge the inset PS-01 with the pump-house PS-01.',1,[.033,.025,.28,.202])
 b.finish(out)

def transfer_layout(store,out):
 b=Batch(store,'layout','UEF-1-location-and-utilities','UEF-1 DFDS/SW/PW piping layout 175286 Rev2, FIO 12-Sep-2019. Floor elevations use the drawing datum; not surveyed coordinates.')
 for num,conv,end in [('01','EAC-1A','discharge'),('02','EAC-2A','receiving'),('03','EAC-1B','discharge'),('04','EAC-2B','receiving')]:
  zone='UEF-1 AP-'+num;iface=f'{conv} {end} chute at UEF-1'
  b.rel(iface,'located_at','UEF-1',2,[.09,.081,.761,.424])
  b.a(iface,'location_description',('Discharge hood at conveyor head end; equipment plan EL +5.500 m TOC and drive working level EL +7.000 m shown in UEF-1 sections.' if end=='discharge' else 'Receiving interface over EAC-2 belt; floor plan EL +0.000 m FFL, receiving conveyor support EL +1.000 m TOS shown in UEF-1 sections.'),1,[.086,.072,.657,.41])
  for token in ['FAS','PRU']:
   node='UEF-1 '+token+'-'+num;b.rel(node,'located_at','UEF-1',2,[.101,.614,.774,.834]);b.a(node,'location_description',f'View {int(num)}-{int(num)} shows {token}-{num} serving {conv}; see UEF-1 plan/section for physical placement.',2,[.101,.614,.774,.834])
 for label,typ,role in [('UEF-1 Potable-water tank','water_tank','Local potable-water storage shown in PW piping layout; separate from DFDS supply.'),('UEF-1 Service-water hose boxes','functional_assembly','Service-water hose facilities shown for local washing/housekeeping.')]:b.entity(label,typ,2,[.07,.036,.973,.449],'UEF-1',role)
 b.a('UEF-1 Potable-water tank','volume_capacity',300,2,[.248,.224,.318,.326],'L',condition='PVC water tank capacity as printed');b.a('UEF-1 Service-water hose boxes','quantity',2,2,[.764,.047,.966,.445],'No.',condition='UEF-1 bill of material hose-box quantity')
 b.a('UEF-1','location_description','At the jetty conveyor transfer from EAC-1A/B to EAC-2A/B. Drawing FFL EL +0.000 corresponds to RL +5.60 m (jetty area).',2,[.067,.295,.396,.418])
 b.a('UEF-1','source_gap','Dedicated UEF-1 structural/mechanical GA 175033 is referenced by the conveyor drawing but was not identified among the imported document titles. Do not infer civil loads, access certification, chute fabrication IDs or liner wear limits.',2,[.783,.898,.97,.956])
 b.a('UEF-1','operating_requirement','Piping review comments require routing that does not obstruct walking or maintenance of drive components and does not interfere with vacuum-cleaning ducting; replies state the drawing was revised.',3,quote='The pipelines should not be an hindrance for walking.')
 b.finish(out)

def dfds_control(store,out):
 b=Batch(store,'philosophy','UEF-1-DFDS-control','DFDS operation/control philosophy Rev2, FIO 14-Jan-2019, UEF-1 page 5. Source-stated Boolean requirements, not live signals.')
 group='UEF-1 DFDS application equipment';lcp=b.entity('UEF-1 DFDS LCP-01','local_control_panel',5,[.1,.12,.92,.90],group)
 ps='DFDSS-1 PS-02';b.rel(ps,'associated_with',group,5,[.1,.12,.92,.9])
 for tag,n,nums in [('EAC-1A','1',['01','02']),('EAC-1B','2',['03','04'])]:
  u=b.entity('DFDS-1 UBS-'+n,'under_belt_switch',5,[.1,.12,.92,.9],tag+' Belt protection devices')
  b.a(u,'equipment_role','Conveyor-running-with-load input for automatic dust-suppression activation; not a belt-stop protection by itself.',3,quote='Under Belt Switches (UBS) will be used for selected conveyors to get input signals of conveyors running on load.')
  b.rel(u,'monitors_equipment',tag,5,[.1,.12,.92,.9])
  for num in nums:
   fas='UEF-1 FAS-'+num;zone='UEF-1 AP-'+num
   b.rel(u,'control_signal_to',fas,5,[.1,.12,.92,.9],network='control',condition=f'AUTO: PS-02 healthy AND {tag} running with load via UBS-{n} AND selector AUTO; all conditions required')
   b.rel(ps,'control_signal_to',fas,5,[.1,.12,.92,.9],network='control',condition='Compressed-air pressure HEALTHY; AND loaded-conveyor input and AUTO selector')
   b.rel(lcp,'control_signal_to',fas,5,[.1,.12,.92,.9],network='control',condition='Application point controlled through LCP-01; manual selection is a distinct documented mode')
   b.a(zone,'sequence_logic',f'AUTO: PS-02 compressed-air pressure healthy AND {tag} running with load from UBS-{n} AND selector AUTO. MANUAL: selector MANUAL. Through LCP-01.',5,[.1,.12,.92,.9])
   for medium in ['Air','Water']:
    header=b.entity(zone+' '+medium+' header','spray_header',4,[.08,.178,.924,.427],zone)
    b.rel('UEF-1 PRU-'+num,'utility_supply_to',header,4,[.08,.178,.924,.427],network='utility',condition=medium+' header supplied through the application-point PRU')
    b.rel(header,'utility_supply_to',zone+' Nozzle group',4,[.08,.178,.924,.427],network='utility',condition=medium+' supply via flexible tubing to air-atomizing nozzles')
 b.a(group,'operating_requirement','Shared DFDS-1 water and air supplies come from DFDSP-1A/1B and DFDSC-1A/1B at Pump House-1 near the jetty, through FAS and PRU to nozzles.',2,[.085,.156,.92,.70])
 for label in ['DFDSP-1A','DFDSP-1B','DFDSC-1A','DFDSC-1B']:
  matches=[n for n in b.ids if n==label]
  if matches:b.rel(label,'serves_equipment',group,2,[.085,.156,.92,.70])
 b.finish(out)

def fas_details(store,out):
 b=Batch(store,'fas','UEF-1-FAS-PRU-details','Project FAS/PRU GA 175095 Rev1, FIO 18-Feb-2019. Standard assembly applied to the identified UEF-1 FAS/PRU family; component field tags remain unknown.')
 for num in ['01','02','03','04']:
  fas='UEF-1 FAS-'+num;pru='UEF-1 PRU-'+num
  b.a(fas,'equipment_role','Flow Activation Station: filters the air/water supplies and switches them using separate normally closed solenoid valves.',2,[.06,.07,.401,.56]);b.a(pru,'equipment_role','Pressure Regulating Unit: regulates air and water separately for the downstream spray headers.',3,[.033,.038,.402,.65])
  for label,typ,condition in [('Air solenoid valve','solenoid_valve','20 NB normally closed'),('Water solenoid valve','solenoid_valve','15 NB normally closed'),('Air filter','air_filter','3/4 inch air filter'),('Water Y-strainer','strainer','15 NB Y-strainer')]:
   c=b.entity(fas+' '+label,typ,2,[.238,.783,.493,.956],fas);b.a(c,'assembly_arrangement',condition,2,[.238,.783,.493,.956]);b.a(c,'quantity',1,2,[.238,.783,.493,.956],'No.',condition='Per standard FAS assembly')
  for label,nb,arr in [('Air regulator',20,'Relieving type SR-13'),('Water regulator',15,'Non-relieving type SR-13')]:
   c=b.entity(pru+' '+label,'pressure_regulator',3,[.037,.745,.367,.94],pru);b.a(c,'assembly_arrangement',arr+'; pressure gauge provided',3,[.037,.731,.661,.951]);b.a(c,'component_dimension',nb,3,[.037,.745,.367,.94],'NB',condition='Connection nominal bore');b.a(c,'manufacturer','Shavo Norgren',3,[.037,.745,.367,.94])
  for label,p,rg in [(fas,2,[.045,.768,.249,.943]),(pru,3,[.431,.724,.66,.95])]:
   b.a(label,'nominal_pressure',5,p,rg,'bar',condition='Air working pressure in standard assembly notes');b.a(label,'nominal_pressure',1,p,rg,'bar',condition='Water working pressure in standard assembly notes');b.a(label,'ingress_protection','IP55',p,rg)
   b.a(label,'source_gap','Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.',p,rg)
 b.finish(out)

def headers(store,out):
 b=Batch(store,'header','UEF-1-spray-header-details','Spray-header GA 175305 Rev0, FIO 27-May-2019. Four-outlet discharge header on p1, nine-outlet receipt header on p2; match to P&ID zone counts.')
 for num,count,page,length in [('01',4,1,410),('02',9,2,760),('03',4,1,410),('04',9,2,760)]:
  for medium,nb in [('Air',20),('Water',15)]:
   label='UEF-1 AP-'+num+' '+medium+' header';r=[.032,.061,.856,.511]
   b.a(label,'component_dimension',length,page,r,'mm',condition='Standard '+str(count)+'-spray header length');b.a(label,'component_dimension',nb,page,[.019,.7,.32,.984],'NB',condition=medium+' pipe nominal bore');b.a(label,'component_material','ASTM A53 Gr B Schedule 40 pipe',page,[.019,.7,.32,.984]);b.a(label,'assembly_arrangement','Pressure-gauge mounting socket provided; separate air/water lines.',page,[.326,.812,.553,.973])
 b.finish(out)

def nozzle_details(store,out):
 b=Batch(store,'nozzle','UEF-1-nozzle-design','DFDS nozzle schedule 175097 Rev1, FIO 15-Feb-2019. System-1 standard nozzle specification applied to the P&ID-identified UEF-1 nozzle groups; not measured consumption.')
 for n in ['01','02','03','04']:
  label='UEF-1 AP-'+n+' Nozzle group';r=[.055,.226,.947,.528]
  for key,v,u,cond in [('rated_flow',.15,'L/min','Water, per nozzle'),('nominal_pressure',1,'bar','Required water pressure'),('rated_flow',3.5,'CFM','Air, per nozzle'),('nominal_pressure',5,'bar','Required air pressure')]:b.a(label,key,v,2,r,u,cond)
  b.a(label,'manufacturer','Lechler Germany',2,r);b.a(label,'component_material','SS316 body; 1/4 inch BSPP female ends',2,r);b.a(label,'assembly_arrangement','Air-atomizing nozzle; quantities belong to the application-point P&ID, not the full-system schedule total.',2,r)
 b.finish(out)

def sump_details(store,out):
 b=Batch(store,'sump_pid','UEF-1-sump-system','Sump/runoff water P&ID 175259 Rev3 (Sept-2019). UEF-1 SP-4A/4B schedule; duties are source design only.')
 group='UEF-1 Sump Pumps SP-4A/4B';b.rel(group,'part_of','UEF-1',1,[.843,.154,.963,.195]);b.rel(group,'located_at','UEF-1',1,[.843,.154,.963,.195]);b.a(group,'equipment_role','Drain the UEF-1 intermediate sump; one working and one standby pump in the schedule.',1,[.843,.154,.963,.195])
 for n in ['4A','4B']:
  node=b.entity('SP-'+n,'pump',1,[.843,.154,.963,.195],group);b.a(node,'flow_capacity',30,1,[.843,.154,.963,.195],'m3/h');b.a(node,'pump_head',45,1,[.843,.154,.963,.195],'m');b.a(node,'motor_rated_power',22,1,[.843,.154,.963,.195],'kW',condition='Selected motor rating')
 b.a(group,'assembly_arrangement','1 working + 1 standby',1,[.843,.154,.963,.195]);b.a(group,'source_gap','Duty selection and installed pump condition are not live; local motor/level-switch cable tags and discharge isolation details need field/loop records.',1,[.176,.783,.331,.943])
 b.finish(out)
 b=Batch(store,'sump','UEF-1-sump-components','Flowmore sump-pump datasheet Rev1 dated 25-Oct-2019, FIO 18-Nov-2019, pp15-16; SP-4A/4B explicitly included. Location resolved with P&ID, not by list order.')
 for n in ['4A','4B']:
  node='SP-'+n;r=[.075,.18,.94,.9]
  b.a(node,'model_number','F-5414A AWS - 100 x 75',15,r);b.a(node,'manufacturer','Flowmore Limited',15,r);b.a(node,'assembly_arrangement','Vertical sump pump, single-stage, non-clog impeller, submerged bottom suction and top discharge; gland packing.',15,r);b.a(node,'lubrication_method','Grease',15,r)
  motor=b.entity(node+' Motor','electric_motor',15,r,node);b.a(motor,'motor_rated_power',22,15,r,'kW');b.a(motor,'rated_rotational_speed',1460,16,[.04,.39,.95,.69],'rpm',condition='Motor specification row 29')
  for child,typ in [('Flexible coupling','coupling'),('Non-clog impeller','mechanical_component'),('Gland packing','mechanical_component')]:b.entity(node+' '+child,typ,15,r,node)
  for key,v,u,c in [('manufacturer','ABB',None,None),('model_number','M2BAX 180MLB4',None,'Frame size'),('motor_voltage',415,'V','AC 3 phase +/-10%'),('motor_supply_frequency',50,'Hz','+/-5%'),('ingress_protection','IP55',None,None),('insulation_class','Class F, temperature rise limited to Class B',None,None)]:b.a(motor,key,v,16,[.04,.39,.95,.69],u,c)
  b.a(node,'operating_range','50% to 200% of duty flow',16,[.04,.28,.95,.39]);b.a(node,'maximum_particle_size',25,16,[.04,.28,.95,.39],'mm');b.a(node,'maximum_power_consumption',19,16,[.04,.28,.95,.39],'kW',condition='Entire operating range in vendor datasheet')
 b.finish(out)

def controls(store,out):
 b=Batch(store,'control','conveyor-component-controls','CHP Control Write-up Rev04 dated 26-Mar-2020, approved on condition 06-Apr-2020. Requirements for HT conveyor assemblies; exact inequalities/delays and unresolved wording preserved.')
 for tag in ['EAC-1A','EAC-1B']:
  motor=tag+' Main motor';act=tag+' Scoop actuator';pump=tag+' Scoop oil circulation pump';fan=tag+' Scoop radiator motor';br=tag+' Thruster brake';c=tag+' Scoop coupling PST-530'
  b.a(tag,'sequence_logic','Documented start sequence: radiator start feedback -> oil circulating pump -> main HT motor -> brake released -> scoop OUT engagement. Normal stop: scoop IN -> brake applied -> main motor off -> oil pump -> radiator.',26,[.16,.793,.897,.934])
  b.a(motor,'start_permissive','All winding temperatures <120 degC; DE/NDE bearing temperatures <70 degC; electrical healthy; local stop not pressed/reset.',27,[.16,.216,.897,.510]);b.a(motor,'trip_condition','Any winding temperature >130 degC; any DE/NDE bearing temperature >80 degC; electrical trip; or local stop operated.',27,[.16,.216,.897,.510])
  for key,v,cond in [('start_temperature_limit',120,'All winding temperatures must be below this value'),('start_temperature_limit',70,'DE and NDE bearing temperatures must be below this value'),('trip_threshold',130,'Any winding temperature above this value'),('trip_threshold',80,'Any DE/NDE bearing temperature above this value')]:b.a(motor,key,v,27,[.16,.216,.897,.510],'degC',cond)
  b.a(br,'operating_requirement','Brake is released with the conveyor start sequence; applied when main motor is off or fluid coupling disengaged. Electrical healthy is a permissive; electrical trip is a trip condition.',27,[.16,.519,.897,.674])
  b.a(fan,'start_permissive','Electrical healthy and local stop not pressed/reset.',27,[.16,.687,.897,.914]);b.a(fan,'trip_condition','Electrical trip or local stop pressed.',27,[.16,.687,.897,.914])
  b.a(pump,'start_permissive','Radiator motor ON AND oil temperature normal AND local stop not pressed/reset AND electrical healthy.',28,[.16,.209,.897,.525]);b.a(pump,'trip_condition','Oil temperature high; main conveyor motor OFF after stated 300 s delay; oil flow unhealthy after 10 s; or electrical trip.',28,[.16,.209,.897,.525])
  b.a(pump,'control_timer_delay',30,28,[.16,.231,.897,.284],'s',condition='Normal off-command oil-pump stopping delay, adjustable');b.a(pump,'control_timer_delay',300,28,[.16,.400,.897,.525],'s',condition='Separate source-listed main-motor-OFF oil-pump trip delay');b.a(pump,'control_timer_delay',10,28,[.16,.400,.897,.525],'s',condition='Oil-flow-switch not operated / oil flow unhealthy')
  b.a(act,'start_permissive','Oil pump ON; own main motor ON; both CBS not operated; PCS/BSS not operated; electrical healthy; brake released; succeeding conveyor motor ON; scoop/gate position and upstream-feeding conditions as listed; local stop reset.',28,[.16,.536,.897,.852])
  b.a(act,'source_discrepancy','CBS polarity unresolved: the permissive says both CBS are not operated, but the trip list also prints CBS not operated. Do not normalize this into executable logic. The succeeding-conveyor/scoop wording also requires application review.',28,[.16,.536,.897,.944])
  if tag.endswith('B'):b.a(act,'source_discrepancy','Path-table discrepancy: page 38 lists main motor for conveyor 1A running as the scoop-actuator permissive for 1B. General section requires the respective conveyor motor. This is retained as an unresolved source inconsistency.',38,[.125,.598,.882,.695])
  for typ,p,rg,condition in [('Pull-cord switches (PCS)',28,[.16,.865,.897,.943],'PCS operated -> scoop IN/disengage'),('Belt-sway switches (BSS)',28,[.16,.865,.897,.943],'BSS operated -> scoop IN/disengage'),('Zero-speed switch (ZSS)',29,[.16,.205,.897,.449],'ZSS operated with 60 s on-delay -> scoop IN/disengage')]:
   node=tag+' '+typ;b.rel(node,'control_signal_to',act,p,rg,network='control',condition=condition);b.a(node,'trip_condition',condition,p,rg)
  z=tag+' Zero-speed switch (ZSS)';b.a(z,'trip_threshold',85,9,[.145,.815,.898,.900],'% rated belt speed',condition='Belt speed below 85% of rated speed trips conveyor per general requirement; actuator action/delay stated separately');b.a(z,'control_timer_delay',60,29,[.16,.205,.897,.449],'s',condition='Source-stated ZSS on-delay in scoop-disengagement list')
  for node,condition,p,rg in [(fan,'Radiator running feedback required for oil-pump start',28,[.16,.209,.897,.525]),(pump,'Oil pump ON required for scoop engagement',28,[.16,.536,.897,.852]),(br,'Brake released feedback required for scoop engagement',28,[.16,.536,.897,.852]),(motor,'Own main motor ON required for scoop engagement',28,[.16,.536,.897,.852])]:b.rel(node,'control_signal_to',pump if node==fan else act,p,rg,network='control',condition=condition)
  b.a(tag+' Scoop PS','operating_requirement','Low pressure after filter produces an alarm contact; contacts wired to junction box / scoop control panel.',34,[.16,.491,.897,.550]);b.a(tag+' Scoop DPS','source_discrepancy','Control write-up calls for indication/alarm and says trip the motor without identifying which motor; vendor P&I table provides an alarm value only. Trip target remains unresolved.',34,[.16,.565,.897,.644])
  b.a(tag+' Scoop FSO','trip_condition','Oil flow unhealthy after 10 s appears in both oil-pump trip and scoop-disengagement lists; preserve the two source-stated actions.',29,[.16,.389,.897,.448])
  b.a(tag,'source_gap','CBS mounting/count, field loop IDs, path-specific magnetic-separator applicability, final relay logic and approved commissioned settings remain unresolved. Generic listed protections do not establish every installed sensor.',28,[.16,.536,.897,.944])
 b.a('UEF-1 Sump Pumps SP-4A/4B','operating_requirement','Sump pumps start/stop automatically from sump level switches through the local control panel; local manual start/stop is provided; either pump can be auto-standby.',26,[.16,.205,.897,.440])
 b.finish(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--expected-version',type=int,default=466);p.add_argument('--output-name',default='rehearsal-complete');args=p.parse_args()
 sys.stdout.reconfigure(encoding='utf-8')
 plant=ROOT/'data/plant';base=ROOT/'output/equipment-pilot';base.mkdir(exist_ok=True,parents=True)
 snap=json.loads((base/'snapshot.json').read_text(encoding='utf-8'))
 for d in snap['documents']:
  if d['id'] in DOCS.values():
   if hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()!=d['sha256']:raise RuntimeError('Source hash mismatch '+d['name'])
 ro=sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True)
 version=int(ro.execute("select value from meta where key='version'").fetchone()[0])
 if version!=args.expected_version:raise RuntimeError(f'Expected {args.expected_version}, found {version}. Reconcile before running.')
 folder=base/('accepted' if args.apply else args.output_name);folder.mkdir(exist_ok=True,parents=True)
 if (folder/'commits.jsonl').exists():raise RuntimeError('Run log exists; inspect previous run rather than replaying blindly.')
 backup=base/f'backup-v{version}.sqlite3'
 if not backup.exists():
  with sqlite3.connect(backup) as dst:ro.backup(dst)
 if not args.apply:
  target=folder/'plant.sqlite3'
  with sqlite3.connect(target) as dst:ro.backup(dst)
  s=Store(folder)
 else:s=Store(plant)
 ro.close()
 for tag in ['EAC-1A','EAC-1B']:ga(s,folder,tag)
 drive(s,folder)
 for tag in ['EAC-1A','EAC-1B']:scoop(s,folder,tag)
 gearbox(s,folder);geared(s,folder);pulley_bearings(s,folder);brakes(s,folder)
 transfer(s,folder);transfer_layout(s,folder);dfds_control(s,folder);fas_details(s,folder);headers(s,folder);nozzle_details(s,folder);sump_details(s,folder);controls(s,folder)
 (folder/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
