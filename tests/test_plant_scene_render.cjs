const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const PE=require('../dist/plant-model.js');
const S=require('../dist/plant-scene-model.js');

// Exercise the actual SVG renderer: projection-only checks missed located chutes.
function render(narrow,stream=0){
  const labels={tp:'UEF-13',a:'EBA-18A',b:'EBA-18B',x:'EBA-19A',y:'EBA-19B',ga:'FG-17',gb:'FG-18',ca:'EBA-18A Discharge chute',cb:'EBA-18B Discharge chute',da:'EBA-18A Drive assembly',db:'EBA-18B Drive assembly',lift:'SNC-2'};
  const entities=Object.entries(labels).map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));
  let counter=0;const facts=[];
  const add=(s,p,o,extra={})=>facts.push({id:'f'+(++counter),canonical_subject:s,canonical_object:o,predicate:p,origin:'explicit',context:{kind:'classification'},evidence:[{evidence_id:'ev'}],...extra});
  for(const [id,type] of Object.entries({tp:'transfer_point',a:'belt_conveyor',b:'belt_conveyor',x:'belt_conveyor',y:'belt_conveyor',ga:'diverter_gate',gb:'diverter_gate',ca:'chute_interface',cb:'chute_interface',da:'functional_assembly',db:'functional_assembly',lift:'elevator'}))add(id,'instance_of',null,{value:type});
  for(const lane of ['a','b']){
    for(const prefix of ['g','c','d']){add(prefix+lane,'part_of',lane);add(prefix+lane,'located_at','tp');}
    for(const [from,to]of [[lane,'g'+lane],['g'+lane,'x'],['g'+lane,'y']])add(from,'material_flow_to',to,{context:{kind:'connection',network:'material',verification:'documented',condition:'selected branch'}});
  }
  add('lift','located_at','tp');
  add('tp','location_description',null,{value:'Head TOC +68.000 m; tail TOC +52.000 m; GA datum.'});
  const projection=PE.build({version:593,entities,assertions:facts});
  const context=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,
    location:{hash:'#overview?equipment=tp&transferstream='+stream},
    window:{matchMedia:()=>({matches:narrow})},esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;')});
  vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),context);
  context.projection=projection;
  return vm.runInContext('PlantScene.view(projection,{})',context);
}

test('transfer SVG exposes both conveyor-owned chutes, remaining located equipment and source-backed location',()=>{
  const html=render(false);
  for(const label of ['EBA-18A Discharge chute','EBA-18B Discharge chute','SNC-2'])assert.ok(html.includes('aria-label="Inspect '+label+'"'),label);
  assert.ok(html.includes('Head TOC +68.000 m; tail TOC +52.000 m; GA datum.'));
  assert.ok(html.includes('Location source ↗'));
});

test('narrow transfer SVG switches chute and drive together with the selected lane',()=>{
  for(const [index,lane,other] of [[0,'A','B'],[1,'B','A']]){
    const html=render(true,index);
    for(const part of ['Discharge chute','Drive assembly']){
      assert.ok(html.includes('aria-label="Inspect EBA-18'+lane+' '+part+'"'));
      assert.ok(!html.includes('aria-label="Inspect EBA-18'+other+' '+part+'"'));
    }
    assert.ok(html.includes('aria-label="Inspect SNC-2"'));
  }
});

test('stockpile SVG retains owned sump and ring header alongside external machines',()=>{
  const entities=[['pile','EAE-2'],['sump','Yard2 runoff sump'],['ring','Yard2 ring header'],['stacker','EAD-2']].map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));
  let n=0;const assertions=[];
  const add=(s,p,o,extra={})=>assertions.push({id:'p'+(++n),canonical_subject:s,canonical_object:o,predicate:p,origin:'explicit',context:{kind:'classification'},evidence:[{evidence_id:'ev'}],...extra});
  for(const [id,type] of Object.entries({pile:'coal_stockpile',sump:'sump',ring:'utility_header',stacker:'stacker'}))add(id,'instance_of',null,{value:type});
  add('sump','part_of','pile');add('ring','part_of','pile');
  add('stacker','material_flow_to','pile',{context:{kind:'connection',network:'material',verification:'documented'}});
  const projection=PE.build({version:634,entities,assertions});
  for(const narrow of [false,true]){
    const context=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash:'#overview?equipment=pile'},window:{matchMedia:()=>({matches:narrow})},esc:s=>String(s)});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),context);context.projection=projection;
    const html=vm.runInContext('PlantScene.view(projection,{})',context);
    for(const name of ['Yard2 runoff sump','Yard2 ring header','EAD-2'])assert.ok(html.includes('aria-label="Inspect '+name+'"'),name);
  }
});

test('primary screens use an assembly view while accepted secondary screens retain their layout',()=>{
  for(const [label,body,secondary] of [['EBD-1','screen body and grizzly deck',false],['EBD-5','Screen body and deck',true]]){
    const entities=[['screen',label],['body',label+' '+body],['motor',label+' screen drive motor'],['chute',label+' undersize discharge chute']].map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));
    const assertions=[];let n=0;
    const add=(s,p,o,value)=>assertions.push({id:'s'+(++n),canonical_subject:s,canonical_object:o,predicate:p,value,origin:'explicit',context:{kind:'classification'},evidence:[{evidence_id:'ev'}]});
    for(const [id,type] of Object.entries({screen:'vibrating_screen',body:'functional_assembly',motor:'electric_motor',chute:'chute_interface'}))add(id,'instance_of',null,type);
    for(const id of ['body','motor','chute'])add(id,'part_of','screen');
    const projection=PE.build({version:644,entities,assertions});
    const context=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash:'#overview?equipment=screen'},window:{matchMedia:()=>({matches:false})},esc:s=>String(s)});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),context);context.projection=projection;
    const html=vm.runInContext('PlantScene.view(projection,{})',context);
    assert.equal(html.includes('SECONDARY GRIZZLY'),secondary);
    for(const e of entities.slice(1))assert.ok(html.includes('aria-label="Inspect '+e.label+'"'),e.label);
  }
});
