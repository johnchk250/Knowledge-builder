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
