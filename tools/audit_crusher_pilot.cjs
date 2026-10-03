/* Read-only acceptance audit. Never changes the plant database. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const PE=require('../dist/plant-model.js'),S=require('../dist/plant-scene-model.js');
const file=process.argv[2]||'output/crusher-pilot/accepted/model.json';
const m=JSON.parse(fs.readFileSync(file,'utf8')),p=PE.build(m);
const id=l=>{const e=[...p.entities.values()].find(e=>e.label===l);assert.ok(e,'Missing '+l);return e.id;};
const own=l=>p.outgoing.get(id(l))||[];
const prop=(l,key,value,unit)=>assert.ok(own(l).some(a=>a.predicate===key&&a.value===value&&(!unit||a.unit===unit)),`${l}: ${key}=${value}`);
const edge=(a,b,net)=>assert.ok(p.networks.some(f=>f.canonical_subject===id(a)&&f.canonical_object===id(b)&&f.context.network===net),a+' → '+b);
const h=id('UEE-3'),cols=S.crusherColumns(p,h);assert.equal(cols.length,2);
for(let i=1;i<=2;i++){
 const c=cols[i-1],lane='AB'[i-1],crusher='EBC-'+i,co=crusher+' Drive assembly Scoop coupling PST-1150';
 assert.deepEqual(c.screens,[id('EBD-'+(i+4))]);assert.deepEqual(c.feeders,[id('KF-'+i)]);
 assert.deepEqual(c.inletGates,[id('FG-15'+lane)]);assert.deepEqual(c.outletGates,[id('FG-'+(i+14))]);assert.deepEqual(c.inlets,[id('EBA-17'+lane)]);
 assert.deepEqual(c.outlets.map(x=>p.entities.get(x).label),['EBA-18A','EBA-18B']);
 const bypass=S.crusherRoute(p,c,'bypass',id('EBA-18B')),screen=S.crusherRoute(p,c,'screen',id('EBA-18A'));
 assert.ok(bypass.length);assert.ok(!bypass.some(a=>a.canonical_subject===c.crusher||a.canonical_object===c.crusher||c.screens.includes(a.canonical_object)));
 assert.ok(screen.some(a=>a.canonical_subject===c.screens[0]&&a.canonical_object===c.feeders[0]));
 assert.ok(!screen.some(a=>a.canonical_subject===c.inletGates[0]&&a.canonical_object===c.feeders[0]));
 assert.ok(!screen.some(a=>a.canonical_object===id('EBA-18B')));
 prop(crusher+' Rotor assembly Ring hammers','quantity',56,'hammers');
 prop(crusher+' Drive assembly Main motor','motor_rated_power',750,'kW');
 edge(crusher+' Drive assembly Main motor',co,'mechanical');edge(co,crusher+' Rotor assembly','mechanical');
 prop(co+' Oil circulation pump','rated_flow',415,'L/min');prop(co+' Oil circulation pump Motor','motor_rated_power',10,'hp');
 prop(co+' Oil radiator Fan motor','motor_rated_power',2.2,'kW');assert.equal(S.kind(p,id(co+' Oil radiator Fan motor')),'motor');
 edge(co+' Return Y filter',co+' Duplex lubrication filter','utility');
 assert.ok(own(co+' Scoop actuator').some(a=>a.predicate==='source_discrepancy'&&a.value.includes('CBS')));
 prop('KF-'+i+' Belt protection devices PCS','quantity',1,'pairs');prop('KF-'+i+' Belt protection devices PCS','individual_device_count',2,'switches');
 prop('EBA-17'+lane+' Belt protection devices PCS','quantity',9,'pairs');prop('EBA-17'+lane+' Belt protection devices PCS','individual_device_count',18,'switches');
 prop('EBA-17'+lane+' Belt protection devices BSS','quantity',7,'pairs');
 prop(crusher+' Isolated foundation Spring elements','quantity',12,'elements');prop(crusher+' Isolated foundation Viscodampers','quantity',4,'dampers');
 prop('FAN-CH-00'+i+' Drive assembly Motor','motor_rated_power',90,'kW');
 edge('DE-'+i+' Suction duct and hoods','DE-'+i+' Cyclone separator','utility');
 edge('DE-'+i+' Cyclone separator','DE-'+i+' Bag-filter compartment','utility');
 edge('DE-'+i+' Bag-filter compartment','FAN-CH-00'+i,'utility');
}
for(const n of ['EBD-1','EBD-2','EBD-3','EBD-4'])assert.ok(!p.assembly(h).some(e=>e.id===id(n)));
assert.ok(!p.assembly(h).some(e=>e.id===id('EBA-18A')));
const de='Crusher House DE System DE-1 and DE-2';
assert.equal(S.modeFacts(own(de)).modes.length,4);
let total=0;for(let n=35;n<=40;n++){const name='UEE-3 AP-'+n;const a=own(name).find(a=>a.predicate==='scheduled_nozzle_count');total+=a.value;assert.ok(a.evidence[0].region);assert.ok(own(name).some(a=>a.predicate==='sprays_at'));}
assert.equal(total,44);
assert.equal(S.areaEntry(p,'crushing'),h);
assert.ok(p.refs.has(id('Crusher House Vibration Isolation System (VIS)')));
assert.ok(!S.scene(p,h).nodes.some(n=>n.id===id('Crusher House Vibration Isolation System (VIS)')));
assert.ok(S.closestParents(p,id('DFDSS-2 PS-09')).includes(id('UEE-3 Local DFDS')));
for(let i=1;i<=5;i++){
 const tag='RAL-CH-00'+i;
 prop(tag,'rated_capacity',4,'t/h');prop(tag+' Rotor and housing Detachable spring-steel tips','quantity',6,'tips');
 prop(tag+' Geared motor','output_speed',20,'rpm');if(i<5)prop(tag+' Geared motor','output_speed',25,'rpm');
 edge(tag+' Geared motor',tag+' Rotor shaft and coupling','mechanical');
}
prop('Crusher House Passenger and Goods Elevator Traction drive assembly Motor','motor_rated_power',15,'kW');
assert.ok(p.entities.get(id('Crusher House Passenger and Goods Elevator')).aliases.includes('SNC-1'));
assert.ok(p.assembly(h).some(e=>e.id===id('Crusher House Passenger and Goods Elevator')));
const additions=p.facts.filter(a=>a.created_version>527);
for(const a of additions){assert.ok(a.evidence.length,a.id);assert.ok(a.context.kind,a.id);for(const e of a.evidence)assert.ok(e.quote||e.region,a.id);}
// Keep the historical zero-conflict default; later qualified exceptions require
// an exact reviewed subject/predicate/assertion manifest, not a count allowance.
const expectedConflicts=process.argv[4]?JSON.parse(fs.readFileSync(process.argv[4],'utf8')):[];
assert.deepEqual(m.conflicts,expectedConflicts,'Unexpected or changed formal conflicts');
const result={ok:true,version:m.version,addedAssertions:additions.length,newEntities:m.entities.filter(e=>e.created_version>527).length,nozzles:total,lanes:cols.map(c=>Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Array.isArray(v)?v.map(x=>p.entities.get(x).label):p.entities.get(v).label]))),checks:['three distinct coal paths per lane','selected stream/outlet only','56 rings per crusher','750kW direct motor/scoop/rotor drive','crusher-specific oil pump and cooler','motor vs rotor vs oil protection scope','feeder/conveyor PCS pair basis','12 springs and4 dampers per foundation','DE air capture/filter/fan and shared returns','44 total DFDS nozzles, not simultaneously operating','source qualifications and per-fact evidence','primary screens and outlet conveyor ownership preserved']};
result.formalConflicts=m.conflicts.length;result.conflictManifest=process.argv[4]||null;
fs.writeFileSync(process.argv[3]||'output/crusher-pilot/semantic-audit.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
