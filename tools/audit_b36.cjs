/* Independent output audit against B36 reviewed source expectations and v558 preservation. */
const fs=require('node:fs'),assert=require('node:assert/strict'),path=require('node:path');
const PE=require('../dist/plant-model.js'),S=require('../dist/plant-scene-model.js');
const file=process.argv[2],out=process.argv[3]||path.dirname(file);
assert.ok(file,'Provide a fresh model export');
const m=JSON.parse(fs.readFileSync(file,'utf8')),baseline=JSON.parse(fs.readFileSync('output/plant-enrichment/B36/baseline.json','utf8')),p=PE.build(m);
const id=l=>{const es=[...p.entities.values()].filter(e=>e.label===l);assert.equal(es.length,1,l+' canonical identity');return es[0].id;};
const own=l=>p.outgoing.get(id(l))||[];
const prop=(l,k,v,u)=>{const a=own(l).find(a=>a.predicate===k&&a.value===v&&(!u||a.unit===u));assert.ok(a,`${l}: ${k}=${v} ${u||''}`);return a;};
const edge=(a,b,n)=>assert.ok(p.networks.some(f=>f.canonical_subject===id(a)&&f.canonical_object===id(b)&&f.context.network===n),`${a} -> ${b} [${n}]`);
for(const t of ['EBA-18A','EBA-18B']){
 const d=t+' Drive assembly',c=d+' Scoop coupling PST-570',me=t+' Belt and mechanical assemblies',pr=t+' Belt protection devices';
 prop(d+' Main motor','motor_rated_power',500,'kW');prop(me+' Conveyor belt','belt_width',1400,'mm');
 prop(c+' Oil circulation pump Motor','motor_rated_power',2.2,'kW');prop(c+' Oil radiator Fan motor','motor_rated_power',.55,'kW');
 prop(c+' Oil circulation pump','rated_flow',150,'L/min');prop(c,'lubricant_fill_quantity',270,'L');
 prop(c+' TS1','alarm_threshold',85,'degC');assert.ok(!own(c+' TS1').some(a=>a.predicate==='trip_threshold'));
 prop(c+' TS2','trip_threshold',110,'degC');prop(c+' DPS','alarm_threshold',.8,'bar');
 prop(d+' Gearbox B3-500','gear_ratio_nominal',28.4);prop(d+' Gearbox B3-500','gear_ratio_actual',29.2);
 prop(d+' Gearbox B3-500','gearbox_thermal_power_rating',633,'kW');prop(d+' Gearbox B3-500','gearbox_thermal_power_rating',905,'kW');
 edge(d+' Main motor',c,'mechanical');edge(c,d+' Gearbox B3-500','mechanical');edge(d+' Gearbox B3-500',d+' Low-speed geared coupling RG-12','mechanical');edge(d+' Low-speed geared coupling RG-12',me+' Head pulley','mechanical');
 edge(c+' Oil sump',c+' Suction strainer','utility');edge(c+' Oil circulation pump',c+' Oil radiator','utility');edge(c+' Oil radiator',c+' Return Y filter','utility');
 for(const [type,pairs]of [['PCS',16],['BSS',12]]){prop(pr+' '+type,'quantity',pairs,'pairs');assert.equal(prop(pr+' '+type,'individual_device_count',pairs*2,'switches').origin,'inferred');edge(pr+' '+type,c+' Scoop actuator','control');}
 prop(me+' Carrying idlers','quantity',435,'sets');prop(me+' Carrying idlers','quantity',431,'sets');prop(me+' Flat return rollers','quantity',4,'rollers');
 prop(me+' Head pulley Bearings','model_number','23156 CCK');prop(me+' Tail bend and take-up pulley group Take-up pulley Bearings','model_number','23148 CCK');prop(me+' Tail bend and take-up pulley group Tail pulley Bearings','model_number','23140 CCK');
 assert.ok(!own(me+' Deflector pulley group').some(a=>a.predicate==='component_dimension'&&a.context.condition==='Bearing centres'));
 assert.ok(S.closestParents(p,id(d)).includes(id(t)));assert.ok(!S.closestParents(p,id(d)).includes(id('UEF-13')));
}
for(const [t,fg,q,e]of [['EBA-18A','FG-17','QB-3','EAT-3'],['EBA-18B','FG-18','QB-4','EAT-4']]){
 prop(fg+' Linear actuator Motor','motor_rated_power',7.5,'kW');prop(fg+' Shaft bearings and housings','quantity',2,'sets');
 prop(q+' Tandem probe','component_dimension',1400,'mm');prop(q+' Tandem probe','belt_speed',2.6,'m/s');
 prop(e,'rated_capacity',1375,'t/h');prop(e+' Four-idler weighbridge Load cells','quantity',4,'cells');
 edge(e+' Load-cell summing junction box',e+' Micro-Tech9101 integrator','control');edge(e+' Micro-Tech9101 integrator','CHP Main Control Room DCS','control');
 assert.ok(S.closestParents(p,id(fg)).includes(id(t)));assert.equal(S.kind(p,id(q)),'detector');assert.equal(S.kind(p,id(e)),'weigher');
}
const cols=S.transferColumns(p,id('UEF-13'));assert.equal(cols.length,2);
assert.deepEqual(cols.map(c=>c.inlets.map(x=>p.entities.get(x).label)),[['EBA-18A'],['EBA-18B']]);
for(const c of cols){assert.deepEqual(c.outlets.map(x=>p.entities.get(x).label),['EBA-19A','EBA-19B']);for(const o of c.outlets){const edges=S.transferRoute(p,c,o);assert.ok(edges.length>=2);assert.equal(new Set(edges.filter(a=>a.canonical_subject===c.gate).map(a=>a.canonical_object)).size,1);assert.ok(edges.filter(a=>a.canonical_subject===c.gate).every(a=>a.context.condition));}}
const local='UEF-13 Local DFDS',counts=[4,9,9,4,9,9],dest=['EBA-18A','EBA-19A','EBA-19B','EBA-18B','EBA-19A','EBA-19B'];
let nozzleTotal=0;
for(let n=11;n<=16;n++){
 const ap=local+' AP-'+n,ng=ap+' Nozzle group';nozzleTotal+=prop(ng,'quantity',counts[n-11],'nozzles').value;
 prop(ng,'rated_flow',.15,'L/min');assert.ok(own(ap).some(a=>a.predicate==='sprays_at'&&a.canonical_object===id(dest[n-11])));
 edge('UEF-13 FAS-'+n,'UEF-13 PRU-'+n,'utility');prop('UEF-13 FAS-'+n+' Air solenoid valve','quantity',1,'No.');
}
assert.equal(nozzleTotal,44);edge('UEE-3 Local DFDS Air and water connection',local+' Air and water inlet from UEE-3','utility');
assert.ok(!p.assembly(id('UEF-13')).some(e=>e.id===id('DFDS System-2')));
assert.ok(S.closestParents(p,id('DFDSS-2 PS-03')).includes(id(local)));
const pumps='UEF-13 Sump Pumps SP-2A/2B';
for(const n of ['2A','2B']){
 const pump=pumps+' SP-'+n;prop(pump,'flow_capacity',10,'m3/h');prop(pump,'pump_head',54,'m');prop(pump+' Motor','motor_rated_power',7.5,'kW');
 prop(pump+' Thrust stand Angular-contact bearing','model_number','7311');prop(pump+' Thrust stand Ball bearing','model_number','6011');
 edge(pump,'CHP Intermediate sump near UEF-1','utility');assert.ok(!own(pump+' Motor').some(a=>a.predicate==='motor_rated_power'&&a.value===22));
}
assert.ok(own(pumps+' Sump pit').some(a=>a.predicate==='source_discrepancy'&&/10 m3/.test(a.value)));
const baseFacts=new Map(baseline.model.assertions.map(a=>[a.id,a])),finalFacts=new Map(m.assertions.map(a=>[a.id,a]));
const correctedLegend='fact_85501cdfd0614f6187db';
for(const [fid,a]of baseFacts){
 const current=finalFacts.get(fid);
 if(fid===correctedLegend&&m.version>=593){
  // Reviewed v593 correction, not a blanket exemption from preservation.
  assert.equal(current.retirement?.version,593);
  assert.deepEqual({...current,retirement:null},a);
  const provenance=JSON.parse(current.retirement.provenance);
  assert.equal(provenance.evidence[0].evidence_id,'ev_0b5f0558fa714697879e');
  assert.ok(own('UEF-13').some(f=>f.predicate==='operating_requirement'&&f.created_version===593&&f.value==='Coal-flow service badges: GK drinking water, PC service water and HDD dry-fog dust suppression. Badges do not define installed piping routes.'));
 }else assert.deepEqual(current,a,'Preserve baseline assertion '+fid);
}
for(const e of baseline.model.entities)assert.deepEqual(m.entities.find(x=>x.id===e.id),e,'Preserve baseline identity '+e.label);
const added=m.assertions.filter(a=>!baseFacts.has(a.id)),evidence=new Map(baseline.evidence.map(e=>[e.id,e]));
for(const a of added){assert.ok(a.evidence.length,a.id);assert.ok(a.context?.basis,a.id);for(const e of a.evidence){assert.ok(evidence.has(e.evidence_id),e.evidence_id);assert.ok(e.quote||e.region,a.id);if(e.region){assert.equal(e.region.length,4);assert.ok(e.region.every(x=>x>=0&&x<=1));}}}
const newEntities=m.entities.filter(e=>e.created_version>558),roots=['EBA-18A','EBA-18B','UEF-13','CHP Intermediate sump near UEF-1'].map(id),reachable=new Set(roots);
for(const r of roots)for(const e of p.assembly(r))reachable.add(e.id);
for(const e of newEntities)assert.ok(reachable.has(e.id),'Orphan '+e.label);
function parentsCycle(id,trail=new Set()){assert.ok(!trail.has(id),'New containment cycle '+id);const next=new Set(trail);next.add(id);for(const a of p.parents.get(id)||[])parentsCycle(a.canonical_object,next);}
for(const e of newEntities)parentsCycle(e.id);
const result={ok:true,version:m.version,baselineVersion:558,preservedAssertions:baseFacts.size,preservedEntities:baseline.model.entities.length,addedAssertions:added.length,newEntities:newEntities.length,nozzleDesignTotal:44,sourceDocuments:new Set(added.flatMap(a=>a.evidence.map(e=>evidence.get(e.evidence_id).document_id))).size,checks:['each conveyor verified independently','exact drive topology and auxiliary motors','original pairs and separate derived counts','nominal/exact ratio distinction and thermal qualification','measurement signal topology','four exclusive gate outlet selections','shared service ownership and UEE3 continuation','SP2-specific motors/thrust bearings and downstream collection','baseline assertion/identity preservation including all crusher and B37 records','exact evidence and context on every addition','component reachability and no new ownership cycle']};
if(m.version>=593){result.preservedAssertions--;result.reviewedRetirements=[correctedLegend];result.checks.push('v593 source-reviewed service legend correction retains historical fact');}
fs.writeFileSync(path.join(out,'semantic-audit.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
