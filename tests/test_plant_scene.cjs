const test=require('node:test');
const assert=require('node:assert/strict');
const PE=require('../dist/plant-model.js');
const S=require('../dist/plant-scene-model.js');
const e=(id,label=id)=>({id,canonical_id:id,label,category:'equipment',aliases:[]});
let n=0;
const f=(s,p,o,extra={})=>({id:'f'+(++n),canonical_subject:s,canonical_object:o,predicate:p,origin:'explicit',context:{kind:'classification'},evidence:[{evidence_id:'ev'+n}],...extra});
const net=(s,o,network='material',extra={})=>f(s,network==='mechanical'?'mechanically_drives':'material_flow_to',o,{context:{kind:'connection',network,verification:'documented'},...extra});
const project=(es,fs)=>PE.build({version:510,entities:es,assertions:fs});

test('location never converts a conveyor drive into transfer-point ownership',()=>{
  const p=project([e('tp','UEF-1'),e('belt','EAC-1A'),e('drive','EAC-1A Drive assembly'),e('motor','Motor')],[f('drive','part_of','belt'),f('motor','part_of','drive'),f('drive','located_at','tp'),f('motor','located_at','tp')]);
  const s=S.scene(p,'tp');assert.equal(s.nodes.find(n=>n.id==='drive').role,'located');assert.equal(s.nodes.some(n=>n.id==='motor'),false);assert.deepEqual(S.closestParents(p,'drive'),['belt']);
});
test('nearest parent removes distant duplicate memberships and keeps real alternatives',()=>{
  const p=project(['plant','yard','belt','drive','gear'].map(x=>e(x)),[f('yard','part_of','plant'),f('belt','part_of','yard'),f('drive','part_of','belt'),f('gear','part_of','drive'),f('gear','part_of','belt'),f('gear','part_of','plant')]);
  assert.deepEqual(S.closestParents(p,'gear'),['drive']);assert.deepEqual(S.breadcrumbs(p,'gear'),['plant','yard','belt','drive','gear']);assert.deepEqual(S.scene(p,'belt').nodes.filter(n=>n.role==='part').map(n=>n.id),['drive']);
});
test('shared supplies stay external; owned protective devices never become external',()=>{
  const p=project([e('belt','EAC-1A'),e('protect','Belt protection devices'),e('pcs','PCS'),e('water','Water system')],[f('protect','part_of','belt'),f('pcs','part_of','protect'),f('pcs','protects_equipment','belt'),f('water','serves_equipment','belt')]);
  const s=S.scene(p,'belt');assert.equal(s.nodes.find(n=>n.id==='water').role,'connected');assert.equal(s.nodes.find(n=>n.id==='pcs').role,'part');assert.ok(s.all.includes('pcs'));
});
test('drive scene reaches head pulley without changing its parentage',()=>{
  const p=project([e('drive','EAC-1A Drive assembly'),e('coupling','EAC-1A Low-speed geared coupling RG-10'),e('mechanical','Mechanical assembly'),e('pulley','Head pulley')],[f('coupling','part_of','drive'),f('pulley','part_of','mechanical'),net('coupling','pulley','mechanical')]);
  const s=S.scene(p,'drive');assert.equal(s.nodes.find(n=>n.id==='pulley').role,'connected');assert.equal(s.edges.length,1);assert.deepEqual(S.closestParents(p,'pulley'),['mechanical']);
});
test('pile without owned parts has connected machine and dust-control context',()=>{
  const p=project([e('pile','EAE-1'),e('stacker','EAD-1'),e('reclaimer','EAF-1'),e('spds','Yard SPDS'),e('shed','UEB-1')],[net('stacker','pile'),net('pile','reclaimer'),f('spds','serves_equipment','pile'),f('pile','covered_by','shed')]);
  const s=S.scene(p,'pile');assert.equal(s.kind,'pile');assert.equal(s.nodes.length,5);assert.equal(s.nodes.filter(n=>n.role==='part').length,0);
});
test('parallel connection evidence is retained, inferred and expired routes excluded',()=>{
  const p=project([e('a','EAC-1A'),e('b','UEF-1')],[net('a','b'),net('a','b'),net('a','b','material',{origin:'inferred'}),net('a','b','material',{context:{kind:'connection',network:'material',verification:'documented',valid_to:'2000-01-01'}})]);
  const s=S.scene(p,'a'),g=S.groupEdges(s.edges);assert.equal(g.length,1);assert.equal(g[0].facts.length,2);assert.equal(g[0].facts[0].evidence.length,1);
});
test('cyclic memberships do not hang navigation and missing identities stay missing',()=>{
  const p=project(['a','b'].map(x=>e(x)),[f('a','part_of','b'),f('b','part_of','a')]);assert.ok(S.breadcrumbs(p,'a').length<=2);assert.equal(S.scene(p,'unknown').kind,'missing');
});
test('rendering template classification does not inherit generic assembly facts',()=>{
  const p=project([e('installed','EAD-1'),e('generic','Coal Stacker Machine'),e('pump','Pump')],[f('installed','instance_of',null,{value:'stacker_machine'}),f('generic','instance_of',null,{value:'stacker_machine'}),f('pump','part_of','generic')]);assert.equal(S.scene(p,'installed').nodes.length,1);assert.equal(S.kind(p,'installed'),'stacker');
});

test('design references keep a reference symbol despite equipment names',()=>{
  const p=project([e('ref','DFDS Screw Compressors SC-1A/1B'),e('pump','Pump'),e('house','House')],[
    f('ref','instance_of',null,{value:'equipment_design_reference'}),
    f('pump','instance_of',null,{value:'pump'}),f('ref','design_detail_applies_to','pump'),
    f('ref','part_of','house'),f('pump','part_of','house')]);
  assert.equal(S.kind(p,'ref'),'reference');assert.equal(S.kind(p,'pump'),'pump');
  assert.equal(S.scene(p,'house').nodes.some(n=>n.id==='ref'),false);
  assert.equal(S.scene(p,'ref').nodes.find(n=>n.id==='ref').kind,'reference');
});
test('area entry retains a detailed functional yard beneath the aggregate stockyard',()=>{
  const p=project([e('root','Coal Stockpile Yard'),e('yard','Coal Yard 1'),e('belt','EAC-7')],[f('yard','instance_of',null,{value:'functional_area'}),f('yard','part_of','root'),f('belt','part_of','yard'),net('belt','root')]);
  // The production stage grouping can include both ancestor and detailed area.
  p.stages.find(s=>s.id==='stockyard').entities=[...p.entities.values()];
  assert.ok(S.scene(p,null,'stockyard').nodes.some(n=>n.id==='yard'&&n.kind==='yard'));
});

test('silo house exposes exact vessel inlets and both outlet alternatives without adopting external conveyors',()=>{
  const types={house:'coal_blending_silo_house',v1:'coal_silo',v2:'coal_silo',x1:'silo_extractor',x2:'silo_extractor',k1:'belt_feeder',k2:'belt_feeder',g1:'diverter_gate',g2:'diverter_gate','6A':'belt_conveyor','6B':'belt_conveyor','16A':'belt_conveyor','16B':'belt_conveyor'};
  const es=[...Object.keys(types),'17A','17B','reference'].map(x=>e(x));
  const fs=Object.entries(types).map(([id,type])=>f(id,'instance_of',null,{value:type}));
  for(const id of Object.keys(types).filter(x=>!['house','6A','6B','16A','16B'].includes(x)))fs.push(f(id,'part_of','house'));
  fs.push(f('reference','instance_of',null,{value:'equipment_design_reference'}),f('reference','part_of','house'));
  for(const[a,b]of [['6A','v2'],['6B','v1'],['16A','v1'],['16B','v2'],['v1','x1'],['v2','x2'],['x1','k1'],['x2','k2'],['k1','g1'],['k2','g2'],['g1','17A'],['g1','17B'],['g2','17A'],['g2','17B']])fs.push(net(a,b));
  fs.push(net('6A','v1','material',{origin:'inferred'}));
  const p=project(es,fs),s=S.scene(p,'house'),columns=S.siloColumns(p,'house');
  assert.deepEqual(columns[0],{vessel:'v1',extractors:['x1'],feeders:['k1'],gates:['g1'],inlets:['6B','16A']});
  assert.deepEqual(columns[1].inlets,['6A','16B']);assert.equal(s.edges.length,14);
  assert.equal(s.nodes.find(n=>n.id==='17A').role,'connected');assert.deepEqual(S.closestParents(p,'17A'),[]);
  assert.equal(s.nodes.some(n=>n.id==='reference'),false);
});

test('extractor drive children retain their own symbols and exact electrical endpoints',()=>{
  const types={x:'silo_extractor',drive:'functional_assembly',motor:'electric_motor',gear:'gearbox',vfd:'variable_frequency_drive',relay:'motor_overload_relay'};
  const p=project([e('x','EBE-CES-1'),e('drive','EBE-CES-1 Drive assembly 1'),e('motor','EBE-CES-1 Drive assembly 1 Motor'),e('gear','EBE-CES-1 Drive assembly 1 Helical gearbox'),e('vfd','Common VFD'),e('relay','Motor overload relay')],
    [...Object.entries(types).map(([id,type])=>f(id,'instance_of',null,{value:type})),f('drive','part_of','x'),f('motor','part_of','drive'),f('gear','part_of','drive'),f('vfd','part_of','x'),f('relay','part_of','vfd'),net('vfd','motor','electrical')]);
  assert.equal(S.kind(p,'motor'),'motor');assert.equal(S.kind(p,'gear'),'gearbox');assert.equal(S.kind(p,'relay'),'sensor');
  const s=S.scene(p,'x');assert.equal(s.kind,'extractor');assert.equal(s.nodes.find(n=>n.id==='motor').role,'detail');assert.equal(s.edges[0].canonical_object,'motor');
  assert.deepEqual(S.closestParents(p,'motor'),['drive']);
});

test('silo inlets follow chute interfaces without duplicating conveyors or crossing upstream gates',()=>{
  const types={house:'coal_blending_silo_house',v1:'coal_silo',v2:'coal_silo',a:'belt_conveyor',b:'belt_conveyor',gate:'diverter_gate',ca:'chute_interface',cb:'chute_interface',cycle:'chute_interface',unresolved:'chute_interface'};
  const fs=Object.entries(types).map(([id,type])=>f(id,'instance_of',null,{value:type}));
  fs.push(f('v1','part_of','house'),f('v2','part_of','house'),f('ca','part_of','a'),f('cb','part_of','b'));
  for(const [a,b] of [['gate','a'],['a','ca'],['ca','v2'],['a','v2'],['b','cb'],['cb','v1'],['cb','cycle'],['cycle','cb'],['unresolved','v1']])fs.push(net(a,b));
  const p=project(Object.keys(types).map(x=>e(x)),fs),cols=S.siloColumns(p,'house');
  assert.deepEqual(cols[0].inlets,['b']);
  assert.deepEqual(cols[1].inlets,['a']);
  assert.ok(S.scene(p,'a').nodes.some(n=>n.id==='ca'));
});

test('operating mode reference separates Remote, Local and Maintenance without borrowing permissives',()=>{
  const facts=['Remote','Local','Maintenance'].map(mode=>f('x','start_permissive',null,{value:mode+' conditions',context:{kind:'specification',condition:'Mode: '+mode}}));
  facts.push(f('x','rated_capacity',null,{value:1250}));
  const selected=S.modeFacts(facts,'Maintenance');assert.deepEqual(selected.facts.map(a=>a.value),['Maintenance conditions']);assert.equal(selected.general.length,1);
  assert.equal(S.modeFacts(facts,'Unknown').selected,'Remote');assert.equal(S.modeFacts(facts.slice(-1),'Local').facts.length,0);
});

test('crusher drive exposes the motor-coupling-rotor path without inventing a gearbox',()=>{
  const types={crusher:'ring_granulator',drive:'functional_assembly',motor:'electric_motor',coupling:'scoop_coupling',rotor:'crusher_rotor',fan:'electric_motor',gear:'gearbox'};
  const p=project([e('crusher','EBC-1'),e('drive','EBC-1 Drive assembly'),e('motor','Main motor'),e('coupling','PST coupling'),e('rotor','Rotor'),e('fan','Coupling Oil radiator Fan motor'),e('gear','Gearbox')],[...Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t})),f('drive','part_of','crusher'),f('motor','part_of','drive'),f('coupling','part_of','drive'),f('rotor','part_of','crusher'),net('motor','coupling','mechanical'),net('coupling','rotor','mechanical')]);
  assert.equal(S.driveSymbol(p,'drive'),'direct-drive');assert.equal(S.kind(p,'fan'),'motor');
  const scene=S.scene(p,'crusher');assert.equal(scene.nodes.find(n=>n.id==='motor').role,'detail');assert.equal(scene.edges.length,2);
  assert.equal(S.scene(p,'drive').nodes.find(n=>n.id==='rotor').role,'connected');assert.deepEqual(S.closestParents(p,'rotor'),['crusher']);
  p.children.get('drive').push(f('gear','part_of','drive'));assert.equal(S.driveSymbol(p,'drive'),'drive');
});

test('crusher route selection keeps bypass, undersize and oversize distinct and selects one outlet',()=>{
  const types={house:'crusher_house',a:'belt_conveyor',b:'belt_conveyor',ga:'diverter_gate',gb:'diverter_gate',sa:'vibrating_screen',sb:'vibrating_screen',ca:'ring_granulator',cb:'ring_granulator',ka:'belt_feeder',kb:'belt_feeder',oa:'diverter_gate',ob:'diverter_gate',x:'belt_conveyor',y:'belt_conveyor'};
  const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
  for(const id of ['ga','gb','sa','sb','ca','cb','ka','kb','oa','ob'])fs.push(f(id,'part_of','house'));
  for(const lane of ['a','b'])for(const [from,to]of [[lane,'g'+lane],['g'+lane,'s'+lane],['g'+lane,'k'+lane],['s'+lane,'c'+lane],['s'+lane,'k'+lane],['c'+lane,'k'+lane],['k'+lane,'o'+lane],['o'+lane,'x'],['o'+lane,'y']])fs.push(net(from,to));
  const p=project(Object.keys(types).map(x=>e(x)),fs),cols=S.crusherColumns(p,'house');assert.equal(cols.length,2);
  assert.deepEqual(S.crusherRoute(p,cols[0],'bypass','y').map(a=>[a.canonical_subject,a.canonical_object]),[['a','ga'],['ga','ka'],['ka','oa'],['oa','y']]);
  const screen=S.crusherRoute(p,cols[1],'screen','x');assert.equal(screen.length,7);assert.ok(screen.some(a=>a.canonical_subject==='sb'&&a.canonical_object==='kb'));
  assert.ok(!screen.some(a=>a.canonical_subject==='gb'&&a.canonical_object==='kb'));assert.ok(!screen.some(a=>a.canonical_object==='y'));assert.deepEqual(S.closestParents(p,'x'),[]);
});

test('area entry is scoped to this plant and does not select a foreign crusher house',()=>{
  const p=project([e('ours','UEE-3'),e('foreign','Rihand STPP stage-2 Crusher House')],[f('ours','instance_of',null,{value:'crusher_house'}),f('foreign','instance_of',null,{value:'crusher_house'})]);
  assert.equal(S.areaEntry(p,'crushing'),'ours');assert.equal(S.areaEntry(p,'unloading'),null);
});

test('transfer routes use located gates and one selected receiving conveyor without adopting the belts',()=>{
  const types={tp:'transfer_point',a:'belt_conveyor',b:'belt_conveyor',x:'belt_conveyor',y:'belt_conveyor',g1:'diverter_gate',g2:'diverter_gate',drive:'functional_assembly',shared:'dfds_system'};
  const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
  fs.push(f('g1','part_of','a'),f('g2','part_of','b'),f('g1','located_at','tp'),f('g2','located_at','tp'),f('drive','part_of','a'),f('drive','located_at','tp'),f('shared','serves_equipment','tp'));
  for(const [a,b]of [['a','g1'],['b','g2'],['g1','x'],['g1','y'],['g2','x'],['g2','y']])fs.push(net(a,b));
  const p=project(Object.keys(types).map(x=>e(x,x==='drive'?'EBA-18A Drive assembly':x)),fs),cols=S.transferColumns(p,'tp');
  assert.equal(cols.length,2);assert.deepEqual(S.transferRoute(p,cols[0],'y').map(a=>[a.canonical_subject,a.canonical_object]),[['a','g1'],['g1','y']]);
  assert.deepEqual(S.transferRoute(p,cols[1],'unknown'),[]);assert.deepEqual(S.closestParents(p,'drive'),['a']);assert.deepEqual(S.closestParents(p,'g1'),['a']);
  const scene=S.scene(p,'tp');assert.ok(scene.nodes.some(n=>n.id==='drive'&&n.role==='located'));assert.equal(scene.nodes.find(n=>n.id==='a').role,'connected');assert.ok(!p.assembly('tp').some(e=>e.id==='shared'));
});

test('transfer divider follows its own downstream selector and stops at receiving belts',()=>{
  const types={tp:'transfer_point',a:'belt_conveyor',b:'belt_conveyor',x:'belt_conveyor',y:'belt_conveyor',yard:'belt_conveyor',beyond:'belt_conveyor',d1:'diverter_gate',d2:'diverter_gate',g1:'diverter_gate',g2:'diverter_gate'};
  const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
  for(const id of ['d1','d2','g1','g2'])fs.push(f(id,'located_at','tp'));
  for(const [a,b]of [['a','d1'],['b','d2'],['d1','yard'],['d2','yard'],['d1','g1'],['d2','g2'],['g1','x'],['g1','y'],['g2','x'],['g2','y'],['x','beyond'],['g1','d1']])fs.push(net(a,b));
  const p=project(Object.keys(types).map(x=>e(x)),fs),cols=S.transferColumns(p,'tp');
  assert.equal(cols.length,2);assert.deepEqual(cols[0].outlets,['x','y','yard']);
  assert.deepEqual(S.transferRoute(p,cols[0],'x').map(a=>[a.canonical_subject,a.canonical_object]),[['a','d1'],['d1','g1'],['g1','x']]);
  assert.deepEqual(S.transferRoute(p,cols[0],'yard').map(a=>[a.canonical_subject,a.canonical_object]),[['a','d1'],['d1','yard']]);
});

test('measurement, oil valves and maintainable subparts retain physical symbols under long inherited labels',()=>{
  const types={q:'metal_detector',e:'belt_weigher',v:'isolation_valve',r:'pressure_regulator',m:'electric_motor',part:'mechanical_component',marker:'mechanical_component',pipe:'utility_header',stand:'functional_assembly'};
  const p=project([e('q','QB-3'),e('e','EAT-3'),e('v','EBA-18A Scoop coupling Oil isolation valve'),e('r','UEF-13 PRU-11 Air regulator'),e('m','Scoop coupling Oil circulation pump Motor'),e('part','Scoop coupling Fusible plug'),e('marker','QB-3 Sandbag marker'),e('pipe','Sump Pumps SP-2B Self-water lubrication line'),e('stand','Sump Pumps SP-2B Thrust stand')],Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t})));
  assert.deepEqual(Object.keys(types).map(id=>S.kind(p,id)),['detector','weigher','valve','valve','motor','mechanical-part','marker','pipe','bearing']);
});

test('tank inlet motorized valves remain valves while their separate motors remain motors',()=>{
  const p=project([e('tank','Tank-2 SPDS compartment'),e('valve','Tank-2 Inlet Motorized Valve MGV-02'),e('motor','MGV-02 Motor')],[f('tank','instance_of',null,{value:'water_tank'}),f('valve','instance_of',null,{value:'motorized_valve'}),f('motor','instance_of',null,{value:'electric_motor'}),f('valve','part_of','tank'),f('motor','part_of','valve')]);
  assert.equal(S.kind(p,'valve'),'valve');assert.equal(S.kind(p,'motor'),'motor');
  assert.ok(S.scene(p,'tank').nodes.some(n=>n.id==='valve'));assert.deepEqual(S.closestParents(p,'motor'),['valve']);
});

test('station valve types win over pump and compressor words in source branch labels',()=>{
  const types={gate:'gate_valve',globe:'globe_valve',ball:'ball_valve',check:'non_return_valve',relief:'pressure_relief_valve',pump:'pump',compressor:'air_compressor'};
  const p=project(Object.keys(types).map(id=>e(id,'DFDS-1 pump-A compressor branch '+id)),Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t})));
  assert.deepEqual(['gate','globe','ball','check','relief'].map(id=>S.kind(p,id)),Array(5).fill('valve'));
  assert.equal(S.kind(p,'pump'),'pump');
  assert.equal(S.kind(p,'compressor'),'compressor');
});

test('common compressed-air train retains compressor boundary symbols and system ownership',()=>{
  const p=project([e('system','DFDS System-1'),e('train','DFDS-1 Common compressed-air supply train'),e('valve','DFDS-1 BV-01 compressor-A discharge ball valve'),e('compressor','DFDSC-1A')],[f('system','instance_of',null,{value:'dfds_system'}),f('train','instance_of',null,{value:'functional_assembly'}),f('valve','instance_of',null,{value:'ball_valve'}),f('compressor','instance_of',null,{value:'air_compressor'}),f('train','part_of','system'),f('valve','part_of','train'),f('compressor','part_of','system'),net('compressor','valve','utility')]);
  const scene=S.scene(p,'train');
  assert.equal(scene.kind,'assembly');
  assert.equal(scene.nodes.find(n=>n.id==='compressor').kind,'compressor');
  assert.equal(scene.nodes.find(n=>n.id==='compressor').role,'connected');
  assert.deepEqual(S.closestParents(p,'compressor'),['system']);
  assert.equal(scene.edges.length,1);
});

test('common utility train shows existing external pumps and tank without changing their ownership',()=>{
  const types={system:'dfds_system',train:'functional_assembly',filter:'duplex_filter',valve:'gate_valve',pump:'pump',tank:'water_tank'};
  const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
  fs.push(f('train','part_of','system'),f('filter','part_of','train'),f('valve','part_of','train'),f('pump','part_of','system'),net('tank','filter','utility'),net('filter','valve','utility'),net('valve','pump','utility'));
  const p=project(Object.keys(types).map(id=>e(id,id==='train'?'DFDS-1 Common water supply train':id)),fs),scene=S.scene(p,'train');
  assert.ok(scene.nodes.some(n=>n.id==='pump'&&n.role==='connected'));
  assert.ok(scene.nodes.some(n=>n.id==='tank'&&n.role==='connected'));
  assert.equal(scene.edges.length,3);
  assert.ok(!p.assembly('train').some(e=>e.id==='pump'));
  assert.deepEqual(S.closestParents(p,'pump'),['system']);
});

test('spray service overview exposes exact descendant supply boundaries without adopting shared assets',()=>{
  const types={local:'dfds_system',ap:'spray_application_point',header:'utility_header',fas:'functional_assembly',source:'utility_header',belt:'belt_conveyor'};
  const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
  fs.push(f('ap','part_of','local'),f('header','part_of','ap'),f('fas','part_of','local'),net('source','fas','utility'),net('fas','header','utility'),f('ap','sprays_at','belt'));
  const p=project(Object.keys(types).map(id=>e(id)),fs),scene=S.scene(p,'local');
  assert.equal(scene.nodes.find(n=>n.id==='source').role,'connected');
  assert.ok(!p.assembly('local').some(e=>e.id==='source'));
  assert.ok(scene.edges.some(a=>a.canonical_subject==='source'&&a.canonical_object==='fas'));
  assert.deepEqual(S.closestParents(p,'header'),['ap']);
});

test('water system scenes expose their tank-pump-header-consumer route without adopting external assets',()=>{
  for(const type of ['service_water_system','potable_water_system','dust_suppression_system','feed_water_system']){
    const types={system:type,filter:'duplex_filter',header:'utility_header',pump:'pump',tank:'water_tank',consumer:'transfer_point'};
    const fs=Object.entries(types).map(([id,t])=>f(id,'instance_of',null,{value:t}));
    fs.push(f('filter','part_of','system'),f('header','part_of','system'),net('tank','filter','utility'),net('filter','pump','utility'),net('pump','header','utility'),net('header','consumer','utility'));
    const p=project(Object.keys(types).map(id=>e(id)),fs),scene=S.scene(p,'system');
    assert.equal(scene.edges.length,4,type);
    for(const id of ['tank','pump','consumer']){
      assert.equal(scene.nodes.find(n=>n.id===id)?.role,'connected',type+': '+id);
      assert.ok(!p.assembly('system').some(e=>e.id===id));
    }
  }
});

test('filter auxiliary groups retain their declared form despite inherited filter labels',()=>{
  const types={v:'valve_group',plug:'plug_group',cover:'filter_cover_group',support:'filter_support_group',basket:'filter_element_group'};
  const p=project(Object.keys(types).map(id=>e(id,'DFDS DUP-01 duplex filter '+id)),Object.entries(types).map(([id,type])=>f(id,'instance_of',null,{value:type})));
  assert.deepEqual(Object.keys(types).map(id=>S.kind(p,id)),['valve','mechanical-part','mechanical-part','mechanical-part','filter']);
});

test('pump seal and receiver drain keep their physical forms under parent labels',()=>{
  const p=project([e('seal','DFDSP-1A Mechanical seal'),e('drain','DFDS-1 Common air receiver drain')],
    [f('seal','instance_of',null,{value:'mechanical_component'}),f('drain','instance_of',null,{value:'drain_valve'})]);
  assert.equal(S.kind(p,'seal'),'seal');
  assert.equal(S.kind(p,'drain'),'valve');
});



test('stacker and portal reclaimer 3D models are built on demand with exact GA dimensions and kinematic articulation',()=>{
  const Y3D=require('../dist/plant-yard-3d.js');
  // Verify dist/plant-scene.js defines both window.PlantScene and window.PlantYard3D and executes full 2D -> 3D -> 2D bind/mount/unmount lifecycle
  const vm=require('node:vm'),fs=require('node:fs');
  const M=require('../dist/plant-model.js');
  const elMap=new Map();
  const mockGL=new Proxy({
    VERTEX_SHADER:35633,FRAGMENT_SHADER:35632,COMPILE_STATUS:35713,LINK_STATUS:35714,
    ARRAY_BUFFER:34962,STATIC_DRAW:35044,FLOAT:5126,DEPTH_TEST:2929,CULL_FACE:2884,
    POLYGON_OFFSET_FILL:32823,COLOR_BUFFER_BIT:16384,DEPTH_BUFFER_BIT:256,TRIANGLES:4,LINES:1,
    getShaderParameter:()=>true,getShaderInfoLog:()=>'',getProgramParameter:()=>true,getProgramInfoLog:()=>'',
    getExtension:()=>({loseContext:()=>{}})
  },{get:(t,k)=>(k in t?t[k]:()=>0)});
  const mkEl=id=>({
    id,dataset:{width:'1200',height:'720',initialHeight:'720'},style:{},
    classList:{toggle:()=>{},add:()=>{},remove:()=>{}},setAttribute:()=>{},getAttribute:()=>'',
    addEventListener:()=>{},removeEventListener:()=>{},
    getBoundingClientRect:()=>({left:0,top:0,width:1200,height:640}),
    querySelector:()=>null,querySelectorAll:()=>[],closest:()=>null,
    clientWidth:1200,clientHeight:640,width:1200,height:640,getContext:()=>mockGL,innerHTML:''
  });
  const rootEl=mkEl('ps-root');
  const doc={
    body:{classList:{toggle:()=>{}}},addEventListener:()=>{},removeEventListener:()=>{},
    querySelector:sel=>(sel==='.ps-root'?rootEl:null),querySelectorAll:()=>[],
    getElementById:id=>(elMap.has(id)?elMap.get(id):(elMap.set(id,mkEl(id)),elMap.get(id)))
  };
  const bctx={
    window:null,globalThis:null,location:{hash:'#overview'},document:doc,
    URLSearchParams,Date,Math,Number,String,Array,Object,Set,Map,RegExp,JSON,Float32Array,AbortController,
    CSS:{escape:s=>s},ResizeObserver:class{observe(){}disconnect(){}},
    requestAnimationFrame:()=>1,cancelAnimationFrame:()=>{},
    console,PlantExplorerModel:M,PlantSceneModel:S,esc:s=>String(s??'')
  };
  bctx.window=bctx;bctx.globalThis=bctx;
  bctx.window.matchMedia=()=>({matches:false});
  bctx.window.addEventListener=()=>{};bctx.window.removeEventListener=()=>{};
  vm.createContext(bctx);
  vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../dist/plant-scene.js'),'utf8'),bctx);
  assert.equal(typeof bctx.PlantScene,'object','dist/plant-scene.js must define window.PlantScene');
  assert.equal(typeof bctx.PlantScene.view,'function','window.PlantScene.view must be a function');
  assert.equal(typeof bctx.PlantYard3D,'object','dist/plant-scene.js must define window.PlantYard3D');
  assert.equal(typeof bctx.PlantYard3D.unmount,'function','window.PlantYard3D.unmount must be a function');
  assert.equal(typeof bctx.PlantYard3D.destroy3DHost,'function','window.PlantYard3D.destroy3DHost must be a function');
  assert.equal(Y3D.isMounted(),false,'3D engine must not mount during module load or 2D browsing');

  // 1. Stacker (EAD-1) 3D geometry & kinematic check
  const stEnts=[
    e('ead1','EAD-1'),e('trip','EAD-1 Travelling tripper'),e('boom','EAD-1 Boom conveyor'),
    e('weigh','EAD-1 Boom Belt Weigher'),e('bdrive','EAD-1 Boom conveyor Drive group'),
    e('luff','EAD-1 Luffing system'),e('lcyl','EAD-1 Luffing system Cylinder'),
    e('slew','EAD-1 Slew system'),e('sring','EAD-1 Slew system Ring bearing and pinions'),
    e('trav','EAD-1 Travel system'),e('twheel','EAD-1 Travel system Rails and wheels'),
    e('cabin','EAD-1 Operator cabin'),e('ehouse','EAD-1 Electrical house'),
    e('dss','EAD-1 Onboard plain-water DSS'),e('lube','EAD-1 Central grease lubrication'),
    e('eac7','EAC-7'),e('eae1','EAE-1')
  ];
  const stFacts=[
    f('ead1','instance_of',null,{value:'stacker_machine'}),
    f('trip','instance_of',null,{value:'tripper'}),f('trip','part_of','ead1'),
    f('boom','instance_of',null,{value:'conveyor'}),f('boom','part_of','ead1'),
    f('weigh','instance_of',null,{value:'belt_weigher'}),f('weigh','part_of','boom'),
    f('bdrive','instance_of',null,{value:'drive_unit'}),f('bdrive','part_of','boom'),
    f('luff','instance_of',null,{value:'functional_assembly'}),f('luff','part_of','ead1'),
    f('lcyl','instance_of',null,{value:'hydraulic_cylinder'}),f('lcyl','part_of','luff'),
    f('slew','instance_of',null,{value:'functional_assembly'}),f('slew','part_of','ead1'),
    f('sring','instance_of',null,{value:'bearing'}),f('sring','part_of','slew'),
    f('trav','instance_of',null,{value:'functional_assembly'}),f('trav','part_of','ead1'),
    f('twheel','instance_of',null,{value:'mechanical_component'}),f('twheel','part_of','trav'),
    f('cabin','instance_of',null,{value:'operator_cabin'}),f('cabin','part_of','ead1'),
    f('ehouse','instance_of',null,{value:'building'}),f('ehouse','part_of','ead1'),
    f('dss','instance_of',null,{value:'dust_suppression_system'}),f('dss','part_of','ead1'),
    f('lube','instance_of',null,{value:'lubrication_system'}),f('lube','part_of','ead1'),
    f('eac7','instance_of',null,{value:'belt_conveyor'}),
    f('eae1','instance_of',null,{value:'stockpile'}),
    net('eac7','ead1','material'),net('ead1','eae1','material')
  ];
  const pSt=project(stEnts,stFacts),scSt=S.scene(pSt,'ead1');
  const m0=Y3D.buildStackerScene3D(scSt,{slewDeg:0,luffDeg:-8,travelM:0});
  const m1=Y3D.buildStackerScene3D(scSt,{slewDeg:90,luffDeg:14,travelM:10});
  assert.ok(m0.items.length>=14,'Stacker 3D model must include all major mechanical, structural, electrical and utility subassemblies');
  assert.ok(m0.dimLines.some(d=>d.label.includes('8,400 mm')),'Stacker 3D model must include 8,400 mm rail gauge dimension');
  assert.ok(m0.dimLines.some(d=>d.label.includes('41,755 mm')),'Stacker 3D model must include 41,755 mm boom dimension');
  assert.ok(m0.dimLines.some(d=>d.label.includes('47,878 mm')),'Stacker 3D model must include 47,878 mm travelling tripper dimension');
  // Verify boom luff & slew kinematics actually move the 3D vertices
  const boom0=m0.items.find(i=>i.label.includes('Boom Conveyor Belt'));
  const boom1=m1.items.find(i=>i.label.includes('Boom Conveyor Belt'));
  assert.ok(boom1.bbox.hi[1]>boom0.bbox.hi[1]+9,'Luffing from -8 deg to +14 deg must raise the 41.755 m boom head elevation by >9 m');
  assert.ok(Math.abs(boom1.centre[2]-boom0.centre[2])>10,'Slewing from 0 deg to 90 deg must rotate the boom across the stockpile');

  // 2. Portal Reclaimer (EAF-1) 3D geometry & kinematic check
  const recEnts=[
    e('eaf1','EAF-1'),e('mboom','EAF-1 Main scraper boom'),e('mchain','EAF-1 Main scraper boom Scraper chain'),
    e('mblade','EAF-1 Main scraper boom Scraper blades'),e('mdrive','EAF-1 Main scraper boom Drive group'),
    e('aboom','EAF-1 Auxiliary scraper boom'),e('achain','EAF-1 Auxiliary scraper boom Scraper chain'),
    e('ablade','EAF-1 Auxiliary scraper boom Scraper blades'),e('adrive','EAF-1 Auxiliary scraper boom Drive group'),
    e('hoist','EAF-1 Hoist system'),e('hwinch','EAF-1 Hoist system Winch rope and sheaves'),
    e('rtrav','EAF-1 Travel system'),e('rwheel','EAF-1 Travel system Rails and wheels'),
    e('storm','EAF-1 Travel system Manual rail clamps'),e('preel','EAF-1 Power cable reel'),
    e('eba8','EBA-8'),e('eae1','EAE-1')
  ];
  const recFacts=[
    f('eaf1','instance_of',null,{value:'portal_reclaimer'}),
    f('mboom','instance_of',null,{value:'functional_assembly'}),f('mboom','part_of','eaf1'),
    f('mchain','instance_of',null,{value:'scraper_chain'}),f('mchain','part_of','mboom'),
    f('mblade','instance_of',null,{value:'mechanical_component'}),f('mblade','part_of','mboom'),
    f('mdrive','instance_of',null,{value:'drive_unit'}),f('mdrive','part_of','mboom'),
    f('aboom','instance_of',null,{value:'functional_assembly'}),f('aboom','part_of','eaf1'),
    f('achain','instance_of',null,{value:'scraper_chain'}),f('achain','part_of','aboom'),
    f('ablade','instance_of',null,{value:'mechanical_component'}),f('ablade','part_of','aboom'),
    f('adrive','instance_of',null,{value:'drive_unit'}),f('adrive','part_of','aboom'),
    f('hoist','instance_of',null,{value:'functional_assembly'}),f('hoist','part_of','eaf1'),
    f('hwinch','instance_of',null,{value:'hoist_winch'}),f('hwinch','part_of','hoist'),
    f('rtrav','instance_of',null,{value:'functional_assembly'}),f('rtrav','part_of','eaf1'),
    f('rwheel','instance_of',null,{value:'mechanical_component'}),f('rwheel','part_of','rtrav'),
    f('storm','instance_of',null,{value:'rail_clamp'}),f('storm','part_of','rtrav'),
    f('preel','instance_of',null,{value:'cable_reel'}),f('preel','part_of','eaf1'),
    f('eba8','instance_of',null,{value:'belt_conveyor'}),
    f('eae1','instance_of',null,{value:'stockpile'}),
    net('eae1','eaf1','material'),net('eaf1','eba8','material')
  ];
  const pRec=project(recEnts,recFacts),scRec=S.scene(pRec,'eaf1');
  const r0=Y3D.buildReclaimerScene3D(scRec,{mainBoomDeg:-24,auxBoomDeg:-22,travelM:0});
  const r1=Y3D.buildReclaimerScene3D(scRec,{mainBoomDeg:8,auxBoomDeg:10,travelM:12});
  assert.ok(r0.items.length>=14,'Portal reclaimer 3D model must include portal bridge, main/aux scraper booms, chains, blades, hoist winch, bogies and reels');
  assert.ok(r0.dimLines.some(d=>d.label.includes('55,800 mm')),'Portal reclaimer 3D model must include 55,800 mm rail span dimension');
  assert.ok(r0.dimLines.some(d=>d.label.includes('37,145 mm')),'Portal reclaimer 3D model must include 37,145 mm main boom sprocket centers');
  assert.ok(r0.dimLines.some(d=>d.label.includes('14,800 mm')),'Portal reclaimer 3D model must include 14,800 mm aux boom sprocket centers');
  const mb0=r0.items.find(i=>i.entity_id==='mboom');
  const mb1=r1.items.find(i=>i.entity_id==='mboom');
  assert.ok(mb1.bbox.lo[1]>mb0.bbox.lo[1]+8,'Hoisting main scraper boom from -24 deg to +8 deg must raise the boom tail elevation');
  // 3. Full PlantScene.view() + PlantScene.bind() 2D -> 3D -> 2D lifecycle check
  const helpers={fact:()=>'',entityLink:()=>'',docLink:()=>''};
  bctx.location.hash='#overview?equipment=eaf1';
  elMap.clear();
  assert.ok(bctx.PlantScene.view(pRec,helpers).includes('🧊 3D Model'),'2D reclaimer view must include 3D Model toggle');
  bctx.PlantScene.bind();
  assert.equal(bctx.PlantYard3D.isMounted(),false,'3D engine must stay unmounted in 2D view');

  bctx.location.hash='#overview?equipment=eaf1&view=3d';
  elMap.clear();
  assert.ok(bctx.PlantScene.view(pRec,helpers).includes('id="ps-yard3d-canvas"'),'3D reclaimer view must render WebGL canvas');
  bctx.PlantScene.bind();
  assert.equal(bctx.PlantYard3D.isMounted(),true,'3D engine must mount in 3D view');

  bctx.location.hash='#overview?equipment=eaf1';
  elMap.clear();
  bctx.PlantScene.view(pRec,helpers);
  bctx.PlantScene.bind();
  assert.equal(bctx.PlantYard3D.isMounted(),false,'3D engine must unmount cleanly when returning to 2D view');
});
