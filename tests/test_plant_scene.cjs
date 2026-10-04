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
  const s=S.scene(p,'belt');assert.equal(s.nodes.find(n=>n.id==='water').role,'connected');assert.equal(s.nodes.some(n=>n.id==='pcs'),false);assert.ok(s.all.includes('pcs'));
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
  const types={house:'coal_blending_silo_house',v1:'coal_silo',v2:'coal_silo',x1:'silo_extractor',x2:'silo_extractor',k1:'belt_feeder',k2:'belt_feeder',g1:'diverter_gate',g2:'diverter_gate'};
  const es=[...Object.keys(types),'6A','6B','16A','16B','17A','17B','reference'].map(x=>e(x));
  const fs=Object.entries(types).map(([id,type])=>f(id,'instance_of',null,{value:type}));
  for(const id of Object.keys(types).filter(x=>x!=='house'))fs.push(f(id,'part_of','house'));
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


