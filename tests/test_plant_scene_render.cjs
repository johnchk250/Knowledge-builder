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

test('fixed tripper renders same-belt continuation without a recycle arc and keeps local services',()=>{
 const labels={tp:'UEF-4',a:'EAC-4A',b:'EAC-4B',t1:'FTR-1',t2:'FTR-2',g1:'KB-FD-3',g2:'KB-FD-4',yard:'EAC-11',water:'UEF-4 local water'};
 const entities=Object.entries(labels).map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));let n=0;const assertions=[];
 const add=(s,p,o,value,context={kind:'classification'})=>assertions.push({id:'ft'+(++n),canonical_subject:s,canonical_object:o,predicate:p,value,origin:'explicit',context,evidence:[{evidence_id:'ev'}]});
 for(const [id,t] of Object.entries({tp:'transfer_point',a:'belt_conveyor',b:'belt_conveyor',t1:'tripper',t2:'tripper',g1:'diverter_gate',g2:'diverter_gate',yard:'belt_conveyor',water:'utility_header'}))add(id,'instance_of',null,t);
 add('water','part_of','tp');
 for(const [belt,t,g] of [['a','t1','g1'],['b','t2','g2']]){
  add(t,'part_of',belt);add(t,'located_at','tp');add(g,'part_of','tp');add(g,'located_at','tp');
  for(const [a,b] of [[belt,t],[t,g],[g,belt],[g,'yard']])add(a,'material_flow_to',b,null,{kind:'connection',network:'material',verification:'documented',condition:b===belt?'Through-flow on same continuous belt':'Yard diversion'});
 }
 const projection=PE.build({version:652,entities,assertions});assert.equal(S.fixedTripperColumns(projection,'tp').length,2);
 for(const narrow of [false,true])for(const mode of ['through','yard']){
  const context=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash:'#overview?equipment=tp&fixedmode='+mode},window:{matchMedia:()=>({matches:narrow})},esc:s=>String(s)});
  vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),context);context.projection=projection;
  const html=vm.runInContext('PlantScene.view(projection,{})',context);
  for(const label of ['EAC-4A continues','EAC-4B continues','SAME CONTINUOUS BELT','UEF-4 local water','Fixed-tripper branch'])assert.ok(html.includes(label),label);
  assert.equal((html.match(/aria-label="Inspect EAC-11"/g)||[]).length,2);
  assert.ok(html.includes('ps-route-inactive'));
 }
});

test('conveyor scene renders 1D kinematic belt loop strip by default and switches to component matrix when spread=1',()=>{
  const entities=[
    ['conv','EAC-1A'],['inlet','Coal Ship Unloader-1'],['outlet','UEF-1'],
    ['weigh','EAC-1A Belt Weigher'],['motor','EAC-1A Drive Motor'],['cpl','EAC-1A Fluid Coupling'],
    ['gbx','EAC-1A Gearbox'],['pulley','EAC-1A Head Drive Pulley'],['tail','EAC-1A Tail Pulley'],
    ['tu','EAC-1A Gravity Take-Up'],['pcs','EAC-1A Pull Cord Switch']
  ].map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));
  let n=0;const assertions=[];
  const add=(s,p,o,value,context={kind:'classification'})=>assertions.push({id:'cv'+(++n),canonical_subject:s,canonical_object:o,predicate:p,value,origin:'explicit',context,evidence:[{evidence_id:'ev'}]});
  for(const [id,t] of Object.entries({
    conv:'belt_conveyor',inlet:'ship_unloader',outlet:'transfer_point',
    weigh:'belt_weigher',motor:'electric_motor',cpl:'fluid_coupling',
    gbx:'gearbox',pulley:'conveyor_pulley',tail:'conveyor_pulley',
    tu:'take_up_system',pcs:'pull_cord_switch'
  }))add(id,'instance_of',null,t);
  for(const id of ['weigh','motor','cpl','gbx','pulley','tail','tu','pcs'])add(id,'part_of','conv');
  add('inlet','material_flow_to','conv',null,{kind:'connection',network:'material',verification:'documented'});
  add('conv','material_flow_to','outlet',null,{kind:'connection',network:'material',verification:'documented'});
  add('motor','mechanically_drives','cpl',null,{kind:'connection',network:'mechanical',verification:'documented'});
  add('cpl','mechanically_drives','gbx',null,{kind:'connection',network:'mechanical',verification:'documented'});
  add('gbx','mechanically_drives','pulley',null,{kind:'connection',network:'mechanical',verification:'documented'});

  const projection=PE.build({version:1007,entities,assertions});
  const renderHash=hash=>{
    const ctx=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash},window:{matchMedia:()=>({matches:false})},esc:s=>String(s)});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),ctx);ctx.projection=projection;
    return vm.runInContext('PlantScene.view(projection,{})',ctx);
  };
  const stripHtml=renderHash('#overview?equipment=conv');
  assert.ok(stripHtml.includes('1D KINEMATIC CONVEYOR BELT LOOP'));
  assert.ok(stripHtml.includes('ps-belt-carry'));
  assert.ok(stripHtml.includes('ps-belt-return'));
  assert.ok(stripHtml.includes('⇄ 1D Belt Strip'));
  assert.ok(stripHtml.includes('ps-open-pill'));
  for(const {label} of entities)assert.ok(stripHtml.includes('aria-label="Inspect '+label+'"'),label);

  const matrixHtml=renderHash('#overview?equipment=conv&spread=1');
  assert.ok(matrixHtml.includes('CONVEYOR, DRIVE & MECHANICAL LOOP'));
  for(const {label} of entities)assert.ok(matrixHtml.includes('aria-label="Inspect '+label+'"'),label);
});

test('multi-floor building scenes render 2.5D isometric elevation decks and floor slicer pills',()=>{
  const html=render(false);
  assert.ok(html.includes('ps-iso-deck'));
  assert.ok(html.includes('ps-floor-slicer'));
  assert.ok(html.includes('◫ 2.5D Stack'));
  assert.ok(html.includes('▭ 2D Flat'));
});

test('plant overview route selection highlights active route stages and arrows and dims non-participating stages',()=>{
  const entities=[
    ['p3','CHP Operating Path-3'],['u','Coal Ship Unloader-1'],['sc','UEE-1'],['y','EAE-1'],['r','UEF-8'],['b','UEE-2'],['c','UEE-3'],['bf','UEF-13'],['bk','TT-1']
  ].map(([id,label])=>({id,label,canonical_id:id,aliases:[]}));
  let n=0;const assertions=[];
  const add=(s,p,o,value,context={kind:'classification'})=>assertions.push({id:'rt'+(++n),canonical_subject:s,canonical_object:o,predicate:p,value,origin:'explicit',context,evidence:[{evidence_id:'ev'}]});
  add('p3','sequence_logic',null,'Reclaiming to silo to bunker');
  for(const [a,b] of [['u','sc'],['y','r'],['r','b'],['b','c'],['c','bf'],['bf','bk']])add(a,'material_flow_to',b,null,{kind:'connection',network:'material',verification:'documented'});
  const projection=PE.build({version:1007,entities,assertions});
  const renderHash=hash=>{
    const ctx=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash},window:{matchMedia:()=>({matches:false})},esc:s=>String(s)});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),ctx);ctx.projection=projection;
    return vm.runInContext('PlantScene.view(projection,{})',ctx);
  };
  const wholeHtml=renderHash('#overview');
  assert.ok(!wholeHtml.includes('ps-active-route-banner'));
  assert.ok(!wholeHtml.includes('ps-route-stage-active'));

  const path3Html=renderHash('#overview?path=3');
  assert.ok(path3Html.includes('ps-active-route-banner'));
  assert.ok(path3Html.includes('Reclaiming to silo to bunker'));
  assert.ok(path3Html.includes('ps-route-stage-active'));
  assert.ok(path3Html.includes('ps-route-edge-active'));
  assert.ok(path3Html.includes('ps-dimmed'));
});

test('unloading area scene renders full multi-hop flow through UEF-1 and inspector renders checklist, severity badges and quick actions',()=>{
  const entities=[
    ['sul1','Coal Ship Unloader-1'],['c1a','EAC-1A'],['uef1','UEF-1'],['c2a','EAC-2A'],
    ['dc1','EAC-1A discharge chute at UEF-1'],['rc2','EAC-2A receiving chute at UEF-1']
  ].map(([id,label])=>({id,label,canonical_id:id,category:'equipment',aliases:[]}));
  let n=0;const assertions=[];
  const add=(s,p,o,value,context={kind:'classification'})=>assertions.push({id:'ua'+(++n),canonical_subject:s,canonical_object:o,predicate:p,value,origin:'explicit',context,evidence:[{evidence_id:'ev'}]});
  add('sul1','instance_of',null,'ship_unloader');
  add('c1a','instance_of',null,'belt_conveyor');
  add('uef1','instance_of',null,'transfer_point');
  add('c2a','instance_of',null,'belt_conveyor');
  add('dc1','instance_of',null,'chute_interface');
  add('rc2','instance_of',null,'chute_interface');
  add('dc1','part_of','c1a');add('dc1','located_at','uef1');
  add('rc2','part_of','c2a');add('rc2','located_at','uef1');
  add('sul1','material_flow_to','c1a',null,{kind:'connection',network:'material',verification:'documented'});
  add('c1a','material_flow_to','dc1',null,{kind:'connection',network:'material',verification:'documented'});
  add('dc1','material_flow_to','rc2',null,{kind:'connection',network:'material',verification:'documented'});
  add('rc2','material_flow_to','c2a',null,{kind:'connection',network:'material',verification:'documented'});
  add('c1a','start_permissive',null,'Downstream belt EAC-2A running');
  add('c1a','source_discrepancy',null,'Motor voltage 6.6 kV vs 415 V');

  const projection=PE.build({version:1007,entities,assertions});
  const renderHash=hash=>{
    const ctx=vm.createContext({PlantSceneModel:S,PlantExplorerModel:PE,URLSearchParams,location:{hash},window:{matchMedia:()=>({matches:false})},esc:s=>String(s??''),state:{events:[],evidence_index:[]}});
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'),'utf8'),ctx);ctx.projection=projection;
    return vm.runInContext('PlantScene.view(projection,{fact:a=>`<div>${a.value||a.predicate}</div>`})',ctx);
  };
  const areaHtml=renderHash('#overview?area=unloading');
  assert.ok(areaHtml.includes('Inspect Coal Ship Unloader-1 to EAC-1A connection'));
  assert.ok(areaHtml.includes('Inspect EAC-1A to EAC-1A discharge chute at UEF-1 connection'));
  assert.ok(areaHtml.includes('Inspect EAC-2A receiving chute at UEF-1 to EAC-2A connection'));

  const pickHtml=renderHash('#overview?equipment=c1a&pick=c1a');
  assert.ok(pickHtml.includes('Start Permissives & Trip Interlocks'));
  assert.ok(pickHtml.includes('data-action="plant-record"'));
  assert.ok(pickHtml.includes('data-action="scene-trace"'));
  assert.ok(pickHtml.includes('ps-sev-badge is-high'));
  assert.ok(pickHtml.includes('Wheel: Zoom 🔍'));
});

test('sub-component BOM enrichment and bespoke cutaway / P&ID schematics render distinct symbols and layouts for rotor, onboard DSS, and lubrication units',()=>{
  const raw = JSON.parse(fs.readFileSync('/tmp/raw_state.json','utf8'));
  const projection = PE.build(raw);
  const findId = lbl => [...projection.entities.values()].find(e => e.label === lbl)?.id;

  const renderEquip = lbl => {
    const id = findId(lbl);
    assert.ok(id, 'Entity found: ' + lbl);
    const ctx = vm.createContext({
      PlantSceneModel: S,
      PlantExplorerModel: PE,
      URLSearchParams,
      location: { hash: '#overview?equipment=' + encodeURIComponent(id) + '&pick=' + encodeURIComponent(id) },
      window: { matchMedia: () => ({ matches: false }) },
      esc: s => String(s ?? ''),
      state: { events: [], evidence_index: [] }
    });
    vm.runInContext(fs.readFileSync(require.resolve('../dist/plant-scene.js'), 'utf8'), ctx);
    ctx.projection = projection;
    return vm.runInContext('PlantScene.view(projection,{fact:a=>`<div>${a.value||a.predicate}</div>`})', ctx);
  };

  // 1. EBC-1 Rotor assembly longitudinal & radial cutaway schematic
  const rotorHtml = renderEquip('EBC-1 Rotor assembly');
  assert.ok(rotorHtml.includes('LONGITUDINAL ROTOR BARREL & Ø1600 MM RADIAL HAMMER SWING CUTAWAY'), 'Rotor cutaway header');
  assert.ok(rotorHtml.includes('RADIAL CUTAWAY · 592 RPM'), 'Radial cutaway callout');
  for (const part of ['Rotor shaft', 'End discs', 'Spacing discs', 'Suspension arms', 'Suspension bars', 'Ring hammers', 'Hammer replacement maintenance bar']) {
    assert.ok(rotorHtml.includes('aria-label="Inspect EBC-1 Rotor assembly ' + part + '"'), 'Rotor part hotspot: ' + part);
  }
  assert.ok(rotorHtml.includes('#ps-rotor-shaft') && rotorHtml.includes('#ps-rotor-disc') && rotorHtml.includes('#ps-suspension-bar') && rotorHtml.includes('#ps-ring-hammer'), 'Bespoke rotor symbols');

  // 2. SUL-2 onboard dust-suppression assembly 3-stage P&ID schematic
  const dssHtml = renderEquip('SUL-2 onboard dust-suppression assembly');
  assert.ok(dssHtml.includes('ONBOARD WATER-MIST P&ID HYDRAULIC FLOW & NOZZLE MANIFOLD SCHEMATIC'), 'Onboard DSS P&ID header');
  assert.ok(dssHtml.includes('STAGE 1 · WATER FILL & 10 m³ STORAGE'), 'DSS Stage 1');
  assert.ok(dssHtml.includes('STAGE 2 · STRAINER & 1W+1S BOOSTER SKID'), 'DSS Stage 2');
  assert.ok(dssHtml.includes('STAGE 3 · PRESSURIZED SPRAY HEADERS'), 'DSS Stage 3');
  assert.ok(dssHtml.includes('#ps-hose-reel') && dssHtml.includes('#ps-tank') && dssHtml.includes('#ps-filter') && dssHtml.includes('#ps-pump') && dssHtml.includes('#ps-spray'), 'DSS P&ID symbols');

  // 3. SUL-2 lubrication units Dual-Line & Progressive Lubrication schematic
  const lubeHtml = renderEquip('SUL-2 lubrication units');
  assert.ok(lubeHtml.includes('CENTRALIZED DUAL-LINE (LINE A / LINE B) & PROGRESSIVE METERING LUBRICATION SCHEMATIC'), 'Lubrication schematic header');
  assert.ok(lubeHtml.includes('DUAL-LINE HIGH-PRESSURE GREASE HEADERS (LINE A & LINE B · 400 BAR)'), 'Dual-line rails');
  assert.ok(lubeHtml.includes('#ps-grease-pump') && lubeHtml.includes('#ps-changeover-valve') && lubeHtml.includes('#ps-distributor-block'), 'Lubrication bespoke symbols');
});
