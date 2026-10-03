/* Verify source-specific control semantics and actual scene projection. */
const fs=require('node:fs'),assert=require('node:assert/strict');
const P=require('../dist/plant-model.js'),S=require('../dist/plant-scene-model.js');
let model=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));model=model.model||model;
const p=P.build(model),facts=model.assertions.filter(a=>!a.retirement);
const rows=id=>facts.filter(a=>a.canonical_subject===id);
const label=id=>p.entities.get(id)?.label;
const find=name=>{const matches=[...p.entities.values()].filter(e=>e.label===name);assert.equal(matches.length,1,name);return matches[0].id;};
const report={ok:true,version:model.version,pumps:[],instrumentDisagreements:[],limitations:['Source175265 design only; tagged level/inlet mapping unresolved.','No commissioned settings or approved merged cause-and-effect claimed.']};
for(const number of [1,2]){
 const page=number===1?4:20;
 const ps=find(`DFDSS-${number} PS-01`),dps=find(`DFDSS-${number} DPS-01`);
 for(const lane of ['A','B']){
  const id=find(`DFDSP-${number}${lane}`),own=rows(id);
  const previous=own.filter(a=>['pump_start_permissive','pump_trip_condition'].includes(a.predicate));
  assert.equal(previous.length,9,'Original individual conditions retained');
  const grouped=own.filter(a=>a.created_version===627&&a.predicate==='sequence_logic');
  assert.equal(grouped.length,2);
  const start=grouped.find(a=>a.value.includes('start grouping')).value;
  for(const clause of ['Local mode OR','ALL three','O/L NOT operated AND','LLS NOT operated','AND emergency-stop','NOT pressed'])assert.ok(start.includes(clause),clause);
  const trip=grouped.find(a=>a.value.includes('trip grouping')).value;
  for(const clause of ['ANY of','LLS operated','OR emergency-stop','OR overload','OR station PS-01','BELOW','OR duplex-filter choked','Delay, latch, reset and numerical thresholds are not stated'])assert.ok(trip.includes(clause),clause);
  const incoming=p.networks.filter(a=>a.canonical_object===id&&a.created_version===627);
  assert.deepEqual(incoming.map(a=>a.canonical_subject).sort(),[ps,dps].sort(),'Correct same-system inputs only');
  for(const a of incoming){assert.equal(a.context.network,'control');assert.equal(a.context.verification,'documented');assert.ok(a.context.condition.includes(label(id)));assert.ok(a.context.basis.includes(`PDFp${page}`));}
  const scene=S.scene(p,id);
  assert.ok(scene.nodes.some(n=>n.id===ps),'PS drawn as connected node');
  assert.ok(scene.nodes.some(n=>n.id===dps),'DPS drawn as connected node');
  report.pumps.push({id,label:label(id),preservedConditions:previous.length,incomingSignals:incoming.map(a=>a.id)});
 }
 for(const sensor of [ps,dps]){
  const disagreement=rows(sensor).filter(a=>a.created_version===627&&a.predicate==='source_discrepancy');assert.equal(disagreement.length,1);
  assert.ok(disagreement[0].value.includes(sensor===ps?'High':'ANNUNCIATION'));
  assert.ok(rows(sensor).some(a=>a.predicate==='instrument_schedule_setpoint'),'Existing qualified schedule retained');
  report.instrumentDisagreements.push({id:sensor,assertion:disagreement[0].id});
 }
}
const added=facts.filter(a=>a.created_version===627);
assert.ok(added.every(a=>!['trip_threshold','control_timer_delay','instrument_schedule_setpoint'].includes(a.predicate)),'Do not turn other-source settings into175265 settings');
assert.ok(!model.entities.some(e=>e.created_version===627),'No duplicate sensors or pumps');
report.addedAssertions=added.length;
console.log(JSON.stringify(report,null,2));
