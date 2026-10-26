const test=require('node:test');
const assert=require('node:assert/strict');
const PE=require('../dist/plant-model.js');
const now=Date.parse('2026-09-18T12:00:00Z');
const entity=(id,label,extra={})=>({id,canonical_id:id,label,aliases:[label],category:'equipment',...extra});
let counter=0;
const fact=(s,p,o=null,extra={})=>({id:'f'+(++counter),canonical_subject:s,canonical_object:o,predicate:p,value:null,origin:'explicit',context:{kind:'classification'},evidence:[],...extra});
const edge=(s,o,extra={})=>fact(s,'material_flow_to',o,{context:{kind:'connection',network:'material',verification:'documented'},...extra});
const model=(entities,assertions)=>({version:466,entities,assertions});

test('merged source classifications display once while retaining both evidence claims',()=>{
  const es=[entity('pump','DFDSP-1A'),entity('vendor','DFDS-1A',{canonical_id:'pump'})];
  const fs=[fact('pump','instance_of',null,{subject:'pump',value:'pump',evidence:[{evidence_id:'design'}]}),fact('pump','instance_of',null,{subject:'vendor',value:'pump',evidence:[{evidence_id:'vendor-sheet'}]})];
  const p=PE.build(model(es,fs),{at:now});
  assert.deepEqual(p.classes.get('pump'),['pump']);
  assert.equal(p.entities.size,1);assert.deepEqual(p.outgoing.get('pump'),fs);
});

test('assembly search follows containment once and excludes shared services and expired membership',()=>{
  const es=['belt','drive','coupling','pump','supply','other','old'].map(id=>entity(id,id));
  const fs=[fact('drive','part_of','belt'),fact('coupling','part_of','drive'),fact('pump','part_of','coupling'),fact('pump','part_of','drive'),fact('drive','part_of','pump'),fact('supply','serves_equipment','belt'),fact('other','located_at','belt'),fact('old','part_of','belt',{context:{valid_to:'2020-01-01'}}),fact('pump','rated_flow',null,{value:150,unit:'L/min',evidence:[{evidence_id:'source'}]})];
  const p=PE.build(model(es,fs),{at:now}),rows=p.assembly('belt');
  assert.deepEqual(rows.map(x=>x.id),['belt','drive','coupling','pump']);
  assert.equal(rows.find(x=>x.id==='pump').facts.find(a=>a.predicate==='rated_flow').evidence[0].evidence_id,'source');
  assert.deepEqual(p.assembly('missing'),[]);
});

test('explicit gaps remain visible even without a keyword in their prose',()=>{
  const p=PE.build(model([entity('belt','EAC-1A')],[fact('belt','source_gap',null,{value:'Field calibration sheet needed.'})]),{at:now});
  assert.equal(p.qualifications('belt').length,1);
});

test('overview links come only from directed documented material assertions',()=>{
  const es=[entity('u','EAC-1A'),entity('s','EAC-3A'),entity('d','EAC-4A')];
  const fs=[edge('u','s'),fact('s','part_of','d'),fact('d','electrical_feed_to','s'),edge('s','d',{context:{kind:'connection',network:'control',verification:'documented'}})];
  const p=PE.build(model(es,fs),{at:now});
  assert.deepEqual(p.links.map(x=>x.id),['unloading>screening']);
  assert.equal(p.material.length,1);
});
test('retired, suppressed, inactive, inferred, unverified and out-of-time links are absent',()=>{
  const es=[entity('a','EAC-4A'),entity('b','EAC-7'),entity('dead','EAC-9',{inactive:true})];
  const fs=[edge('a','b',{retirement:{version:4}}),edge('a','b',{suppressed:true}),edge('a','dead'),edge('a','b',{origin:'inferred'}),edge('a','b',{context:{kind:'connection',network:'material',verification:'unverified'}}),edge('a','b',{context:{kind:'connection',network:'material',verification:'documented',valid_to:'2026-09-18T12:00:00Z'}}),edge('a','b',{context:{kind:'connection',network:'material',verification:'documented',valid_from:'2027-01-01T00:00:00Z'}})];
  const p=PE.build(model(es,fs),{at:now});assert.equal(p.material.length,0);assert.equal(p.links.length,0);
});
test('conditions remain attached to alternatives; no automatic stream choice',()=>{
  const es=[entity('g','FG-5'),entity('a','EBA-6A'),entity('b','EBA-6B')];
  const fs=['Gate FWD','Gate REV'].map((condition,i)=>edge('g',i?'b':'a',{context:{kind:'connection',network:'material',verification:'documented',condition}}));
  const p=PE.build(model(es,fs),{at:now});assert.deepEqual(p.material.map(a=>a.context.condition),['Gate FWD','Gate REV']);
});
test('silo crossover direction is preserved exactly',()=>{
  const es=[entity('6a','EBA-6A'),entity('6b','EBA-6B'),entity('s1','EBB-1'),entity('s2','EBB-2')];
  const p=PE.build(model(es,[edge('6a','s2'),edge('6b','s1')]),{at:now});
  assert.deepEqual(p.links[0].facts.map(a=>[a.canonical_subject,a.canonical_object]),[['6a','s2'],['6b','s1']]);
});
test('trippers keep their chosen browse group despite conveyor parentage',()=>{
  const es=[entity('belt','EBA-19A'),entity('tripper','TT-1'),entity('gate','FG-19')];
  const p=PE.build(model(es,[fact('tripper','part_of','belt'),fact('gate','part_of','tripper'),edge('belt','tripper')]),{at:now});
  assert.deepEqual([...p.memberships.get('tripper')],['bunkers']);assert.equal(p.links[0].id,'bunkerfeed>bunkers');
  assert.equal(p.parents.get('tripper')[0].canonical_object,'belt');
});
test('hierarchy handles multi-parent and cyclic input without inventing ownership',()=>{
  const es=[entity('a','EAC-4A'),entity('b','EBB-1'),entity('shared','shared component'),entity('child','child')];
  const fs=[fact('shared','part_of','a'),fact('shared','part_of','b'),fact('child','part_of','shared'),fact('shared','part_of','child')];
  const p=PE.build(model(es,fs),{at:now});
  assert.equal(p.parents.get('shared').length,3);assert.deepEqual([...p.memberships.get('child')].sort(),['blending','distribution']);
});
test('generic design dossiers remain separate from installed identities',()=>{
  const es=[entity('unit','EAD-1'),entity('generic','Coal Stacker Machine'),entity('pump','Luffing pump')];
  const fs=[fact('unit','instance_of',null,{value:'stacker_machine'}),fact('generic','instance_of',null,{value:'stacker_machine'}),fact('pump','part_of','generic'),fact('generic','rated_capacity',null,{value:1700,unit:'t/h'})];
  const p=PE.build(model(es,fs),{at:now});
  assert.deepEqual(p.designCandidates('unit').map(e=>e.id),['generic']);assert.equal(p.children.has('unit'),false);assert.equal(p.relatedFacts('unit').length,0);
});
test('only explicit applicability brings reference facts into an equipment page',()=>{
  const es=[entity('belt','EAC-1A'),entity('scheme','Conveyor control scheme'),entity('other','Other control scheme')];
  const fs=[fact('scheme','control_scheme_applies_to','belt'),fact('scheme','interlock_condition',null,{value:'downstream running'}),fact('other','interlock_condition',null,{value:'must not be inherited'})];
  const p=PE.build(model(es,fs),{at:now});assert.deepEqual(p.relatedFacts('belt').map(x=>x.fact.value),['downstream running']);
  assert.equal(p.relatedFacts('belt')[0].via.predicate,'control_scheme_applies_to');
});
test('document titles and future/limestone identities are not placed by substring',()=>{
  assert.equal(PE.stageForLabel('Drawing for EAC-1A'),null);assert.equal(PE.stageForLabel('LS-EAC-1'),null);assert.equal(PE.stageForLabel('UEF-2'),null);
  const p=PE.build(model([entity('d','EAC-1A',{category:'document'})],[]),{at:now});assert.equal(p.memberships.size,0);
});
test('paths require a recorded identity and summary; empty demo remains usable',()=>{
  const es=[entity('p','CHP Operating Path-3'),entity('q','CHP Operating Path-4')];
  const p=PE.build(model(es,[fact('p','sequence_logic',null,{value:'Reclaiming to silo to bunker'})]),{at:now});
  assert.deepEqual(p.paths.map(x=>x.id),['3']);assert.deepEqual(PE.build(model([],[]),{at:now}).paths,[]);
});
test('grouping distinguishes protection and operating ranges',()=>{
  assert.equal(PE.factGroup({predicate:'pump_start_permissive'}),'protection');assert.equal(PE.factGroup({predicate:'instrument_range_lower'}),'limits');assert.equal(PE.factGroup({predicate:'sequence_logic'}),'operation');
  assert.equal(PE.factGroup({predicate:'design_numeric_requirement',value:130,context:{condition:'Motor trip winding temperature above threshold'}}),'protection');
  assert.equal(PE.factGroup({predicate:'operating_requirement',value:'Start radiator then oil pump.'}),'operation');
  assert.equal(PE.factGroup({predicate:'design_numeric_requirement',value:1,context:{condition:'Pre-start warning duration; adjustable'}}),'operation');
  assert.equal(PE.factGroup({predicate:'power_calculation_required_motor_power'}),'reference');
  assert.equal(PE.factGroup({predicate:'selected_brake_model_design'}),'mechanical');
});
test('expired or inferred applicability does not inherit requirements or place components',()=>{
  const es=[entity('a','EAC-1A'),entity('scheme','Scheme'),entity('component','Pump')];
  const expired={kind:'relationship',valid_to:'2020-01-01T00:00:00Z'};
  const fs=[fact('scheme','control_scheme_applies_to','a',{origin:'inferred'}),fact('scheme','calculation_applies_to','a',{context:expired}),fact('scheme','operating_requirement',null,{value:'Never inherited'}),fact('component','part_of','a',{context:expired})];
  const p=PE.build(model(es,fs),{at:now});assert.equal(p.relatedFacts('a').length,0);assert.equal(p.memberships.has('component'),false);assert.equal(p.children.has('a'),false);assert.equal(p.facts.length,4);
});
test('area graph preserves parallel conditions and only places recorded internal endpoints',()=>{
  const es=[entity('a','EAC-7'),entity('b','EAD-1'),entity('c','EAE-1'),entity('external','EAC-4A'),entity('unconnected','EAD-2')];
  const fs=[edge('a','b'),edge('a','b',{context:{kind:'connection',network:'material',verification:'documented',condition:'Alternative source'}}),edge('b','c'),edge('external','a')];
  const graph=PE.areaGraph(PE.build(model(es,fs),{at:now}),'stockyard');
  assert.equal(graph.edges.length,2);assert.equal(graph.edges[0].facts.length,2);
  assert.deepEqual(new Set(graph.nodes.map(n=>n.id)),new Set(['a','b','c']));
  const byId=new Map(graph.nodes.map(n=>[n.id,n]));assert.ok(byId.get('a').x<byId.get('b').x&&byId.get('b').x<byId.get('c').x);
});
test('area graph keeps recycle loops and disconnected branches without overlapping nodes',()=>{
  const es=[entity('a','EAC-7'),entity('b','EAD-1'),entity('c','EAE-1'),entity('d','EAC-9'),entity('e','EAD-2')];
  const graph=PE.areaGraph(PE.build(model(es,[edge('a','b'),edge('b','a'),edge('b','c'),edge('d','e')]),{at:now}),'stockyard');
  assert.equal(graph.edges.length,4);assert.equal(graph.nodes.filter(n=>n.cycle).length,2);
  assert.equal(new Set(graph.nodes.map(n=>`${n.x},${n.y}`)).size,5);
  assert.deepEqual(PE.areaGraph(PE.build(model([],[])),'stockyard').nodes,[]);
});
test('yard machine lanes stay aligned alongside older transfer-building records',()=>{
  const es=[entity('u','UAX-5'),entity('v','UAX-1')],fs=[fact('u','instance_of',null,{value:'plant_building'}),fact('v','instance_of',null,{value:'plant_building'})];
  for(let n=1;n<=4;n++){
    const labels=[`EAC-${5+2*n}`,`EAD-${n}`,`EAE-${n}`,`EAF-${n}`,`EBA-${6+2*n}`];
    labels.forEach((label,i)=>es.push(entity(`${n}-${i}`,label)));
    for(let i=0;i<4;i++)fs.push(edge(`${n}-${i}`,`${n}-${i+1}`));
  }
  fs.push(edge('u','1-4'),edge('1-0','v'));
  const graph=PE.areaGraph(PE.build(model(es,fs),{at:now}),'stockyard');
  for(let n=1;n<=4;n++)assert.equal(new Set(graph.nodes.filter(x=>x.id.startsWith(n+'-')).map(x=>x.y)).size,1);
  assert.ok(graph.edges.find(e=>e.from==='u').bypassLane!==undefined);
});

test('yard overview scopes the flow to its assembly while keeping shared services reachable',()=>{
  const es=[entity('site','Coal Stockpile Yard'),entity('yard','Coal Yard 1'),entity('c7','EAC-7'),entity('stacker','EAD-1'),entity('c9','EAC-9'),entity('other','EAD-2'),entity('spds','Local SPDS'),entity('pump','Shared pump'),entity('old','Expired supply')];
  const fs=[fact('yard','part_of','site'),fact('c7','part_of','yard'),fact('stacker','part_of','yard'),fact('spds','part_of','yard'),edge('c7','stacker'),edge('c9','other'),fact('pump','serves','spds'),fact('old','serves','spds',{context:{valid_to:'2020-01-01'}}),fact('spds','serves','stacker')];
  const p=PE.build(model(es,fs),{at:now});
  assert.deepEqual(new Set(PE.areaGraph(p,'stockyard','yard').nodes.map(n=>n.id)),new Set(['c7','stacker']));
  assert.deepEqual(p.assemblyBoundary('yard').map(a=>a.canonical_subject),['pump']);
  assert.equal(p.assembly('yard').some(x=>x.id==='pump'),false);
});

test('smart search normalizes hyphens, enforces numeric token boundaries, expands synonyms and ranks primary equipment first',()=>{
  const es=[
    entity('c5','EAC-5A'),
    entity('c15','EBA-15A'),
    entity('part','EAC-5A Bend pulley'),
    entity('ref','EAC-5A Power and Belt-Tension Calculation'),
    entity('samp','UEF-3 Coal Sampling System'),
    entity('sul2','Coal Ship Unloader-2'),
    entity('stk1','EAD-1'),
    entity('bk1c','Bunker-C of Unit-1')
  ];
  const fs=[
    fact('c5','instance_of',null,{value:'belt_conveyor'}),
    fact('c15','instance_of',null,{value:'belt_conveyor'}),
    fact('part','part_of','c5'),
    fact('ref','instance_of',null,{value:'calculation'}),
    fact('samp','instance_of',null,{value:'sampling_system'}),
    fact('sul2','instance_of',null,{value:'ship_unloader'}),
    fact('stk1','instance_of',null,{value:'stacker_machine'}),
    fact('bk1c','instance_of',null,{value:'coal_bunker'})
  ];
  const p=PE.build(model(es,fs),{at:now});
  assert.equal(PE.searchEntities(p,'eac5a')[0].id,'c5');
  const fiveA=PE.searchEntities(p,'5A conveyor').map(e=>e.id);
  assert.ok(fiveA.includes('c5'));
  assert.ok(!fiveA.includes('c15'));
  assert.equal(PE.searchEntities(p,'coal sampler')[0].id,'samp');
  assert.equal(PE.searchEntities(p,'ship unloader 2')[0].id,'sul2');
  assert.equal(PE.searchEntities(p,'stacker 1')[0].id,'stk1');
  assert.equal(PE.searchEntities(p,'bunker 3c')[0].id,'bk1c');
});

test('equipment flow builds start permissives checklist and triages qualification severity',()=>{
  const es=[entity('c1','EAC-1A')];
  const fs=[
    fact('c1','instance_of',null,{value:'belt_conveyor'}),
    fact('c1','start_permissive',null,{value:'Downstream conveyor running and zero-speed switch healthy'}),
    fact('c1','trip_condition',null,{value:'Pull-cord switch or belt-sway switch stage-2 actuated'}),
    fact('c1','source_discrepancy',null,{value:'Weight listed as 120 kg on GA vs 125 kg on schedule'}),
    fact('c1','source_discrepancy',null,{value:'Motor voltage 6.6 kV vs 415 V in feeder schedule'})
  ];
  const p=PE.build(model(es,fs),{at:now});
  const flow=PE.buildEquipmentFlow(p,'c1');
  assert.equal(flow.permissivesChecklist.length,2);
  assert.equal(flow.permissivesChecklist[0].kind,'permissive');
  assert.equal(flow.permissivesChecklist[1].kind,'trip');
  assert.equal(flow.qualifications.length,2);
  assert.equal(flow.qualifications[0].severity,'high');
  assert.equal(flow.qualifications[1].severity,'low');
});

test('plant-wide aliases map TP/UEF, PSH/UEE-1, CBSH/UEE-2, CRH/UEE-3, BCN/EAC/EBA, DH/TPH/UAX and include located systems',()=>{
  const es=[
    entity('uef5','UEF-5'),
    entity('fg3','FG-3'),
    entity('uee1','UEE-1'),
    entity('ebd1','EBD-1'),
    entity('uee2','Coal Blending Silo House',{aliases:['Coal Blending Silo House','UEE-2','CBSH']}),
    entity('ebb1','EBB-1'),
    entity('re1','EBE-CES-1'),
    entity('uee3','UEE-3'),
    entity('ebc1','EBC-1'),
    entity('c1a','EAC-1A'),
    entity('c18a','EBA-18A'),
    entity('uax1','UAX-1'),
    entity('uax5','UAX-5')
  ];
  const fs=[
    fact('uef5','instance_of',null,{value:'transfer_point'}),
    fact('fg3','instance_of',null,{value:'diverter_gate'}),
    fact('fg3','located_at','uef5'),
    fact('uee1','instance_of',null,{value:'primary_screening_house'}),
    fact('ebd1','instance_of',null,{value:'vibrating_screen'}),
    fact('ebd1','part_of','uee1'),
    fact('uee2','instance_of',null,{value:'coal_blending_silo_house'}),
    fact('ebb1','instance_of',null,{value:'coal_silo'}),
    fact('ebb1','part_of','uee2'),
    fact('re1','instance_of',null,{value:'silo_extractor'}),
    fact('re1','part_of','uee2'),
    fact('uee3','instance_of',null,{value:'crusher_house'}),
    fact('ebc1','instance_of',null,{value:'ring_granulator'}),
    fact('ebc1','part_of','uee3'),
    fact('c1a','instance_of',null,{value:'belt_conveyor'}),
    fact('c18a','instance_of',null,{value:'belt_conveyor'}),
    fact('uax1','instance_of',null,{value:'plant_building'}),
    fact('uax5','instance_of',null,{value:'plant_building'})
  ];
  const p=PE.build(model(es,fs),{at:now});

  for(const q of ['TP 5','TP5','TP-5','TH-5','transfer point 5']){
    const res=PE.searchEntities(p,q).map(e=>e.id);
    assert.equal(res[0],'uef5',q+' top match should be uef5');
    assert.ok(res.includes('fg3'),q+' should also surface located gate fg3');
  }
  for(const q of ['PSH','Primary Screening House','UEE 1','UEE-1']){
    const res=PE.searchEntities(p,q).map(e=>e.id);
    assert.equal(res[0],'uee1',q+' top match should be uee1');
    assert.ok(res.includes('ebd1'),q+' should also surface screen ebd1');
  }
  for(const q of ['CBSH','Coal Blending Silo House','Silo House','UEE 2','UEE-2']){
    const res=PE.searchEntities(p,q).map(e=>e.id);
    assert.equal(res[0],'uee2',q+' top match should be uee2');
    assert.ok(res.includes('ebb1'),q+' should also surface silo ebb1');
  }
  for(const q of ['CRH','Crusher House','UEE 3','UEE-3']){
    const res=PE.searchEntities(p,q).map(e=>e.id);
    assert.equal(res[0],'uee3',q+' top match should be uee3');
    assert.ok(res.includes('ebc1'),q+' should also surface crusher ebc1');
  }
  for(const q of ['BCN-18A','BCN 18A','BC 18A','EAC-18A','EAC 18A','conveyor 18a','belt 18a']){
    assert.equal(PE.searchEntities(p,q)[0]?.id,'c18a',q);
  }
  for(const q of ['BCN','EAC','belt','conveyor']){
    const res=PE.searchEntities(p,q).map(e=>e.id);
    assert.ok(res.includes('c1a')&&res.includes('c18a'),q);
  }
  assert.equal(PE.searchEntities(p,'DH-1')[0]?.id,'uax1');
  assert.equal(PE.searchEntities(p,'TPH-1')[0]?.id,'uax5');
  assert.equal(PE.searchEntities(p,'RE-1')[0]?.id,'re1');
});
