/* Read-only semantic checks over the accepted pilot export; no DB writes. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const PE=require('../dist/plant-model.js'),S=require('../dist/plant-scene-model.js');
const input=process.argv[2]||'output/silo-pilot/accepted/model.json';
const m=JSON.parse(fs.readFileSync(input,'utf8')),p=PE.build(m);
const id=label=>{const e=[...p.entities.values()].find(e=>e.label===label);assert.ok(e,label);return e.id;};
const own=label=>p.outgoing.get(id(label))||[];
const property=(label,key,value,unit)=>own(label).find(a=>a.predicate===key&&a.value===value&&(!unit||a.unit===unit));
const house=id('Coal Blending Silo House'),columns=S.siloColumns(p,house);
assert.equal(columns.length,2);
assert.deepEqual(columns.map(c=>c.inlets.map(x=>p.entities.get(x).label).sort()),[['EBA-16A','EBA-6B'],['EBA-16B','EBA-6A']]);
for(let i=1;i<=2;i++){
  const ex='EBE-CES-'+i,col=columns[i-1];
  assert.deepEqual(col.extractors,[id(ex)]);assert.deepEqual(col.feeders,[id('KF-'+(i+2))]);assert.deepEqual(col.gates,[id('FG-'+(i+12))]);
  assert.ok(property(ex,'rated_capacity',1250,'t/h'));assert.ok(property(ex,'design_capacity',1375,'t/h'));
  const modes=S.modeFacts(own(ex),'Maintenance');assert.deepEqual(modes.modes,['Remote','Local','Maintenance']);assert.equal(modes.facts.length,2);
  for(let d=1;d<=2;d++){
    const motor=ex+' Drive assembly '+d+' Motor';assert.ok(property(motor,'motor_rated_power',55,'kW'));
    assert.ok(p.networks.some(a=>a.canonical_subject===id(ex+' Common VFD')&&a.canonical_object===id(motor)&&a.context.network==='electrical'));
  }
  assert.ok(p.refs.has(id('RE-'+i)));assert.equal(S.scene(p,house).nodes.some(n=>n.id===id('RE-'+i)),false);
  assert.deepEqual([...new Set(p.material.filter(a=>a.canonical_subject===id('FG-'+(i+12))).map(a=>p.entities.get(a.canonical_object).label))].sort(),['EBA-17A','EBA-17B']);
  const k='KF-'+(i+2);assert.ok(property(k+' Drive assembly Main motor','motor_rated_power',45,'kW'));
  assert.ok(property(k+' Belt protection devices PCS','quantity',1,'pair'));assert.ok(property(k+' Belt protection devices PCS','individual_device_count',2,'devices'));
  assert.ok(property(k+' Belt protection devices ZSS','quantity',1,'No.'));
}
let nozzles=0;
for(let j=1;j<=10;j++){
  const ap='UEE-2 AP-'+String(j).padStart(2,'0');const q=own(ap).find(a=>a.predicate==='scheduled_nozzle_count');assert.ok(q);nozzles+=q.value;
  assert.ok(own(ap).some(a=>a.predicate==='sprays_at'));
  const old=own('UEE-2 FAS-'+j).filter(a=>a.predicate==='sequence_logic');assert.ok(old.every(a=>!/KF-[34] position signal/.test(a.value)));
}
assert.equal(nozzles,60);assert.ok(property('UEE-2 Local DFDS','scheduled_nozzle_count',60,'nozzles'));
const added=p.facts.filter(a=>a.created_version>510&&a.created_version<=527);
for(const a of added){assert.ok(a.evidence.length,a.id);assert.ok(a.context.kind,a.id);for(const e of a.evidence)assert.ok(e.quote||e.region,e.evidence_id);}
// Later source reconciliation may intentionally retain conflicts outside this pilot.
// An explicit manifest must match every subject, predicate and supporting assertion;
// without it the historical zero-conflict requirement remains unchanged.
const expectedConflicts=process.argv[4]?JSON.parse(fs.readFileSync(process.argv[4],'utf8')):[];
assert.deepEqual(m.conflicts,expectedConflicts,'Unexpected or changed formal conflicts');
const result={ok:true,version:m.version,addedAssertions:added.length,newEntities:m.entities.filter(e=>e.created_version>510&&e.created_version<=527).length,columns:columns.map(c=>Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Array.isArray(v)?v.map(x=>p.entities.get(x).label):p.entities.get(v).label]))),nozzles,formalConflicts:m.conflicts.length,checks:['four exact inlets','two physical extractors','two 55-kW motors per extractor on common VFD','mode separation','both outlet alternatives','per-feeder protection counts','ten DFDS applications','retired incorrect feeder position summaries','per-claim evidence and context']};
result.conflictManifest=process.argv[4]||null;
fs.writeFileSync(process.argv[3]||'output/silo-pilot/semantic-audit.json',JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
