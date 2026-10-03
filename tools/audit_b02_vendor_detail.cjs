/* Source-review expectations independent of the source-package builder. */
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const PE=require('../dist/plant-model.js'),S=require('../dist/plant-scene-model.js');
const model=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),p=PE.build(model);
const rawEntities=new Map(model.entities.map(e=>[e.id,e]));
const facts=(id,key)=>(p.outgoing.get(id)||[]).filter(a=>a.predicate===key);
const vals=(id,key)=>facts(id,key).map(a=>a.value);
const children=id=>(p.children.get(id)||[]).map(a=>p.entities.get(a.canonical_subject));
const select=(id,suffix)=>{const rows=children(id).filter(e=>e.label.endsWith(suffix));assert.equal(rows.length,1,suffix);return rows[0].id;};
const houses=['ent_bdf8e7e7f7f8485b80fe','ent_36135b45a07c4d03bf06'];
const pumps=[['ent_975edb9acc07451cbc62',0],['ent_8a35251f220d4c9287d2',0],['ent_afdfc43f0f1148d0b555',1],['ent_eca52aa5ec3d4d3fa153',1]];
const report={ok:true,version:model.version,pumps:[],receivers:[],filters:[],browser:'Recorded separately in browser-checks; static SVG checks do not replace browser journeys'};
for(const [id,index] of pumps){
  const motor=select(id,'Drive motor'),impellers=select(id,'Closed impeller group'),coupling=select(id,'Rigid coupling'),shaft=select(id,'Pump shaft');
  assert.deepEqual(vals(motor,'motor_rated_power'),[index?4:3]);
  assert.deepEqual(vals(motor,'motor_rated_speed').sort((a,b)=>a-b),index?[2863,2910]:[2867,2870]);
  assert.deepEqual(vals(impellers,'quantity'),[index?16:14]);
  assert.deepEqual(vals(coupling,'quantity'),[1]);
  assert.equal(facts(coupling,'quantity')[0].origin,'inferred');
  assert.deepEqual(vals(select(id,'Coupling guard group'),'quantity'),[2]);
  assert.deepEqual(vals(select(id,'Bearing sleeve group'),'quantity'),[2]);
  assert.deepEqual(vals(select(id,'Long spacer sleeve group'),'quantity'),[index?13:11]);
  if(model.version>=626){
    assert.deepEqual(vals(select(id,'Vent plug'),'quantity'),[1]);
    assert.deepEqual(vals(select(id,'Screwed plug group'),'quantity'),[2]);
    assert.deepEqual(vals(select(id,'Pump cover'),'quantity'),[1]);
    assert.deepEqual(vals(select(id,'Short spacer sleeve group'),'quantity'),[2]);
    assert.deepEqual(vals(select(id,'Shaft-end spacer sleeve'),'quantity'),[1]);
    assert.deepEqual(vals(select(id,'Seal-side spacer sleeve'),'quantity'),[1]);
    const rings=select(id,'O-ring group');
    assert.deepEqual(vals(rings,'quantity'),[],'No invented aggregate spare kit count');
    const row=vals(rings,'equipment_role')[0];
    for(const text of ['412.01 quantity2','412.02 quantity1','412.03 quantity'+(index?16:14),'412.04 quantity1'])assert.ok(row.includes(text),text);
    assert.deepEqual(vals(rings,'component_material'),['EPDM WRC (BOM412.01–412.04)']);
    assert.deepEqual(vals(select(id,'Seal-side spacer sleeve'),'component_material'),['1.4305 (BOM525.05)']);
    assert.equal(children(id).filter(e=>rawEntities.get(e.id)?.created_version===626).length,7);
  }
  for(const e of children(id)){
    assert.deepEqual(facts(e.id,'located_at').map(a=>a.canonical_object),[houses[index]]);
    assert.equal(facts(e.id,'part_of').length,1);
    assert.ok(!['pump','compressor','receiver'].includes(S.kind(p,e.id)),e.label);
    assert.ok((p.outgoing.get(e.id)||[]).every(a=>a.evidence?.length&&a.context?.basis),e.label);
    assert.ok((p.outgoing.get(e.id)||[]).every(a=>(a.evidence||[]).every(s=>s.region||s.quote)),e.label);
  }
  for(const [from,to] of [[motor,coupling],[coupling,shaft],[shaft,impellers]]){
    assert.ok(p.networks.some(a=>a.canonical_subject===from&&a.canonical_object===to&&a.predicate==='mechanically_drives'&&a.context.network==='mechanical'&&a.context.verification==='documented'));
  }
  assert.equal(S.kind(p,select(id,'Mechanical seal')),'seal');
  report.pumps.push({id,motor,impellers,motorPower:vals(motor,'motor_rated_power'),qualifiedMotorSpeeds:vals(motor,'motor_rated_speed'),impellerCount:vals(impellers,'quantity'),ownedComponents:children(id).length});
}
for(const [i,id] of ['ent_3651ef55706b4f46a164','ent_f3863d4082594e6d9556'].entries()){
  const nodes=p.assembly(id).filter(e=>rawEntities.get(e.id)?.created_version===624);
  assert.equal(nodes.length,4);
  assert.ok(nodes.some(e=>S.kind(p,e.id)==='sensor'));
  assert.equal(nodes.filter(e=>S.kind(p,e.id)==='valve').length,3);
  assert.ok(nodes.every(e=>facts(e.id,'located_at').some(a=>a.canonical_object===houses[i])));
  report.receivers.push({id,accessories:nodes.map(e=>e.id)});
}
for(const id of ['ent_24964c483cf14e2188d8','ent_d380e5eec9aa434f8c64']){
  const owned=p.assembly(id).filter(e=>rawEntities.get(e.id)?.created_version===623);
  assert.equal(owned.length,8);
  assert.ok(owned.some(e=>S.kind(p,e.id)==='valve'));
  assert.equal(owned.filter(e=>S.kind(p,e.id)==='mechanical-part').length,4);
  report.filters.push({id,components:owned.map(e=>e.id)});
}
assert.equal(model.conflicts.length,4);
const out=process.argv[3];fs.mkdirSync(out,{recursive:true});
for(const [id] of pumps){
  for(const narrow of [false,true]){
    const context=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,
      location:{hash:'#overview?equipment='+id},window:{matchMedia:()=>({matches:narrow})},
      esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;')});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),context);
    context.projection=p;
    const html=vm.runInContext('PlantScene.view(projection,{})',context);
    for(const e of children(id))assert.ok(html.includes('aria-label="Inspect '+e.label+'"'),e.label);
    fs.writeFileSync(out+'/'+id+(narrow?'-narrow':'-desktop')+'.html',html);
  }
}
fs.writeFileSync(out+'/result.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,version:model.version,pumps:report.pumps.length,receivers:report.receivers.length,filters:report.filters.length,svgViews:8}));
