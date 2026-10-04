/* Visual projection only. Scene coordinates are illustrative, never plant facts. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PlantSceneModel=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const unique=xs=>[...new Set(xs)];
  const label=(p,id)=>p.entities.get(id)?.label||'';
  function kind(p,id){
    const c=(p.classes.get(id)||[]).join(' ').toLowerCase(),n=label(p,id).toLowerCase(),t=c+' '+n;
    if(p.refs.has(id))return 'reference';
    // Specific physical types win over words inherited in a component's label.
    if(/crusher_house/.test(c))return 'crusher-house';
    if(/crusher_dust_extraction_stream/.test(c))return 'de-stream';
    if(/crusher_dust_extraction/.test(c))return 'de-house';
    if(/ring_granulator/.test(c))return 'crusher';
    if(/^ebc-\d+ housing and access$/.test(n))return 'crusher-housing';
    if(/rotor bearings and seals$/.test(n))return 'bearing';
    if(/protection and monitoring$/.test(n))return 'protection';
    if(/crusher_rotor/.test(c))return 'crusher-rotor';
    if(/crusher_cage/.test(c))return 'cage';
    if(/hydraulic_power_pack|hydraulic_system/.test(c))return 'hydraulic';
    if(/hydraulic_cylinder/.test(c))return 'cylinder';
    if(/vibration_isolation_system/.test(c))return 'foundation';
    if(/vibration_exciter/.test(c))return 'exciter';
    if(/cyclone_separator/.test(c))return 'cyclone';
    if(/dust_hopper/.test(c))return 'chute';
    if(/damper/.test(c))return 'damper';
    if(/dust_extraction_duct|dust_capture_hood/.test(c))return 'duct';
    if(/electric_motor/.test(c))return 'motor';
    if(/metal_detector_probe/.test(c))return 'detector';
    if(/metal_detector/.test(c))return 'detector';
    if(/belt_weighbridge|belt_weigher/.test(c))return 'weigher';
    if(/load_cell/.test(c))return 'sensor';
    if(/belt_scraper/.test(c))return 'scraper';
    if(/air_receiver/.test(c))return 'receiver';
    if(/air_compressor/.test(c))return 'compressor';
    if(/functional_assembly/.test(c)&&/common compressed-air supply train$/.test(n))return 'assembly';
    if(/conveyor_belt/.test(c))return 'belt';
    if(/(?:isolation|solenoid|motorized|gate|globe|ball|non_return|pressure_relief|drain)_valve|pressure_regulator|valve_group/.test(c))return 'valve';
    if(/plug_group|filter_cover_group|filter_support_group/.test(c))return 'mechanical-part';
    if(/(?:^| )strainer(?: |$)|air_filter/.test(c))return 'filter';
    if(/metal_detector_marker/.test(c))return 'marker';
    if(/utility_header/.test(c))return 'pipe';
    if(/thrust stand$/.test(n)&&/functional_assembly/.test(c))return 'bearing';
    if(/mechanical_component/.test(c)){
      if(/sandbag marker$/.test(n))return 'marker';
      if(/blade blocks$|rubber blade$|v-plough$/.test(n))return 'scraper';
      if(/\bseal(?:s)?(?: group)?$/.test(n))return 'seal';
      if(/counterweight$|wire rope$/.test(n))return 'takeup';
      return 'mechanical-part';
    }
    if(/gearbox/.test(c))return 'gearbox';
    if(/oil_circulation_pump|sump_pump$/.test(c))return 'pump';
    if(/oil_cooler/.test(c))return 'cooler';
    if(/oil_filter|filter_element_group|bag_filter/.test(c))return 'filter';
    if(/oil_tank|water_tank/.test(c))return 'tank';
    if(/electric_actuator/.test(c))return 'actuator';
    if(/(?:^| )bearing(?: |$)/.test(c))return 'bearing';
    if(/coal_blending_silo_house/.test(c))return 'silo-house';
    if(/silo_extractor/.test(c))return 'extractor';
    if(/pressure_relief_cone/.test(c))return 'cone';
    if(/extractor_blade/.test(c))return 'blade';
    if(/reclaim_platform/.test(c))return 'platform';
    if(/slew_bearing/.test(c)||/pinion and bearings$/.test(n))return 'bearing';
    if(/variable_frequency_drive|local_control_panel/.test(c))return 'panel';
    if(/relay|switch|instrument|gauge|sensor|protection_device/.test(c))return 'sensor';
    if(/lubrication_system/.test(c))return 'lubrication';
    if(/silo_vent_filter/.test(c))return 'filter';
    if(/fan/.test(c))return 'fan';
    if(/diverter_gate|rod_gate/.test(c))return 'gate';
    if(/belt_feeder/.test(c))return 'feeder';
    if(/maintenance_access/.test(c))return 'access';
    if(/ventilation_duct/.test(c))return 'duct';
    if(/dfds_system/.test(c))return 'spray-system';
    if(/spray_application_point/.test(c))return 'spray';
    if(/adjusting sleeve$/.test(n))return 'sleeve';
    if(/labyrinth seal$/.test(n))return 'seal';
    if(/shell and sloping liner$/.test(n))return 'silo';
    if(/manholes and access openings$/.test(n))return 'access';
    if(/level and temperature instruments$/.test(n))return 'sensor';
    if(/electrical|control|pulse_valve/.test(c))return 'panel';
    if(/functional_area/.test(c))return /yard|stockpile/.test(n)?'yard':'assembly';
    if(/drive assembly(?: \d+)?$/.test(n))return 'drive';
    if(/shared cyclone hopper and dust return$/.test(n))return 'cyclone';
    if(/belt protection/.test(n))return 'protection';
    if(/belt and mechanical/.test(n))return 'mechanical';
    if(/radiator|cooler/.test(t))return 'cooler';
    if(/motor/.test(t))return 'motor';
    if(/gearbox/.test(t))return 'gearbox';
    if(/coupling/.test(c)||/coupling (pst|rg)|scoop coupling/.test(n))return 'coupling';
    if(/brake/.test(t))return 'brake';
    if(/pulley/.test(t))return 'pulley';
    if(/idler|roller/.test(t))return 'idler';
    if(/scraper/.test(t)&&!/reclaimer/.test(c))return 'scraper';
    if(/take.up|counterweight/.test(t))return 'takeup';
    if(/pump/.test(t))return 'pump';
    if(/filter|strainer/.test(t))return 'filter';
    if(/nozzle|sprinkler|spray gun/.test(t))return 'spray';
    if(/valve/.test(t))return 'valve';
    if(/sensor|switch|instrument|protection_device/.test(c)||/\b(bss|pcs|zss)\b/.test(n))return 'sensor';
    if(/tank|sump/.test(t))return 'tank';
    if(/dust|spds|dfds/.test(t))return 'water';
    if(/water_distribution/.test(c))return 'water';
    if(/chute/.test(t))return 'chute';
    if(/transfer_point|transfer_house/.test(c)||/^uef-\d+$/.test(n))return 'transfer';
    if(/reclaimer/.test(c)||/^eaf-\d+$/.test(n))return 'reclaimer';
    if(/stacker/.test(c)||/^ead-\d+$/.test(n))return 'stacker';
    if(/stockpile/.test(c)||/^eae-\d+$/.test(n))return 'pile';
    if(/shed/.test(t)||/^ueb-\d+$/.test(n))return 'shed';
    if(/silo|bunker/.test(c))return 'silo';
    if(/crusher/.test(c))return 'crusher';
    if(/screen/.test(c))return 'screen';
    if(/unloader/.test(c))return 'ship';
    if(/conveyor_belt/.test(c)||/conveyor belt$/.test(n))return 'belt';
    if(/belt_conveyor|conveyor/.test(c)||/^(eac|eba)-\d+[ab]?$/.test(n))return 'conveyor';
    if(/house|building/.test(c)||/^uax-\d+$/.test(n))return 'building';
    if(/belt|idler|scraper|take.up/.test(t))return 'belt';
    return 'assembly';
  }
  function closestParents(p,id){
    const parents=unique((p.parents.get(id)||[]).map(a=>a.canonical_object));
    // Remove a distant ancestor when a more specific parent also owns the item.
    return parents.filter(candidate=>!parents.some(other=>other!==candidate&&p.assembly(candidate).some(n=>n.id===other)));
  }
  function breadcrumbs(p,id){
    const chain=[],seen=new Set();let next=id;
    while(next&&!seen.has(next)&&chain.length<16){seen.add(next);chain.unshift(next);next=closestParents(p,next).sort((a,b)=>label(p,a).localeCompare(label(p,b)))[0];}
    return chain;
  }
  function roots(p,ids){
    const set=new Set(ids);
    return ids.filter(id=>!ids.some(other=>other!==id&&p.assembly(other).slice(1).some(n=>n.id===id)&&!p.assembly(id).slice(1).some(n=>n.id===other))).filter(id=>set.has(id));
  }
  function scene(p,id,area){
    const current=a=>PlantCurrent(a);
    // p.children / p.networks already enforce accepted current relationships.
    function PlantCurrent(a){const c=a.context||{},now=Date.now();return (!c.valid_from||Date.parse(c.valid_from)<=now)&&(!c.valid_to||Date.parse(c.valid_to)>now);}
    if(!id){
      const stage=p.stages.find(s=>s.id===area);if(!stage)return {kind:'plant',id:null,nodes:[],edges:[],title:'Maitree coal handling plant',description:'Follow coal from unloading to the boiler bunkers. Open a process area to explore its equipment.'};
      const members=stage.entities.filter(e=>!p.refs.has(e.id)).map(e=>e.id),set=new Set(members);
      const flow=unique(p.material.flatMap(a=>[a.canonical_subject,a.canonical_object]).filter(x=>set.has(x)));
      const entries=unique([...members.filter(x=>(p.classes.get(x)||[]).includes('functional_area')),...roots(p,members).filter(x=>(p.children.get(x)||[]).length||!flow.length)]);
      const ids=unique([...flow,...entries]);
      return {kind:'area',id:null,area:stage.id,title:stage.title,description:stage.description,nodes:ids.map(x=>node(x,'equipment')),edges:p.material.filter(a=>ids.includes(a.canonical_subject)&&ids.includes(a.canonical_object)),all:members};
    }
    if(!p.entities.has(id))return {kind:'missing',id,nodes:[],edges:[],title:'Equipment unavailable',description:'This equipment is not active in the current model.'};
    const own=roots(p,unique((p.children.get(id)||[]).map(a=>a.canonical_subject)).filter(x=>!p.refs.has(x)));
    const assembly=new Set(p.assembly(id).map(n=>n.id));
    const situated=roots(p,unique((p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at'&&current(a)&&!assembly.has(a.canonical_subject)).map(a=>a.canonical_subject)));
    const detail=['extractor','crusher'].includes(kind(p,id))?unique(own.filter(x=>kind(p,x)==='drive').flatMap(x=>(p.children.get(x)||[]).map(a=>a.canonical_subject))):[];
    const visible=new Set([id,...own,...situated,...detail]);
    const utilityTrain=['water','assembly'].includes(kind(p,id))&&(p.classes.get(id)||[]).includes('functional_assembly')&&/common (?:water|compressed-air) supply train$/i.test(label(p,id));
    const waterSystem=(p.classes.get(id)||[]).some(c=>['service_water_system','potable_water_system','dust_suppression_system','feed_water_system'].includes(c));
    const boundary=['silo-house','crusher-house','transfer'].includes(kind(p,id))?p.material.filter(a=>visible.has(a.canonical_subject)||visible.has(a.canonical_object)).flatMap(a=>[a.canonical_subject,a.canonical_object]):['de-house','de-stream','spray-system'].includes(kind(p,id))||utilityTrain||waterSystem?p.networks.filter(a=>assembly.has(a.canonical_subject)!==assembly.has(a.canonical_object)).flatMap(a=>[a.canonical_subject,a.canonical_object]):[];
    const related=unique([...p.networks.filter(a=>(a.canonical_subject===id||a.canonical_object===id)||(a.context.network==='mechanical'&&(visible.has(a.canonical_subject)||visible.has(a.canonical_object)))).flatMap(a=>[a.canonical_subject,a.canonical_object]),...(p.incoming.get(id)||[]).filter(a=>current(a)&&['serves','serves_equipment','protects_equipment','sprays_at','covered_by'].includes(a.predicate)).map(a=>a.canonical_subject),...(p.outgoing.get(id)||[]).filter(a=>current(a)&&['covered_by','associated_with'].includes(a.predicate)).map(a=>a.canonical_object)]).filter(x=>x!==id&&!assembly.has(x)&&!situated.includes(x));
    const external=unique([...related,...boundary]).filter(x=>!visible.has(x)&&!assembly.has(x)&&!p.refs.has(x));
    const nodes=[node(id,'self'),...own.map(x=>node(x,'part')),...situated.map(x=>node(x,'located')),...detail.map(x=>node(x,'detail')),...external.map(x=>node(x,'connected'))];
    const set=new Set(nodes.map(n=>n.id));
    const edges=p.networks.filter(a=>set.has(a.canonical_subject)&&set.has(a.canonical_object));
    const relationships=p.facts.filter(a=>current(a)&&set.has(a.canonical_subject)&&set.has(a.canonical_object)&&['part_of','located_at','covered_by','serves_equipment','associated_with','monitors_equipment','protects_equipment'].includes(a.predicate));
    const role=(p.outgoing.get(id)||[]).find(a=>['equipment_role','purpose','equipment_description','function'].includes(a.predicate)&&typeof a.value==='string');
    return {kind:kind(p,id),id,title:label(p,id),description:role?.value||((p.classes.get(id)||[]).join(' ').replaceAll('_',' ')),nodes,edges,relationships,all:unique([...assembly,...situated,...external])};
    function node(x,role){return {id:x,label:label(p,x),kind:kind(p,x),role};}
  }
  function groupEdges(edges){
    const map=new Map();for(const a of edges){const k=[a.canonical_subject,a.canonical_object,a.context?.network||a.predicate].join('|');if(!map.has(k))map.set(k,{from:a.canonical_subject,to:a.canonical_object,network:a.context?.network||a.predicate,facts:[]});map.get(k).facts.push(a);}return [...map.values()];
  }
  function siloColumns(p,id){
    const owned=new Set(p.assembly(id).map(n=>n.id));
    const vessels=[...owned].filter(x=>(p.classes.get(x)||[]).includes('coal_silo')).sort((a,b)=>label(p,a).localeCompare(label(p,b)));
    const next=(from,type)=>unique(p.material.filter(a=>a.canonical_subject===from&&owned.has(a.canonical_object)&&(p.classes.get(a.canonical_object)||[]).includes(type)).map(a=>a.canonical_object));
    // A detailed discharge chute is an interface of its incoming stream, not
    // another conveyor. Follow only chute links; stop at the first equipment.
    const inletSources=(id,seen=new Set())=>{
      if(seen.has(id))return [];
      if(!(p.classes.get(id)||[]).includes('chute_interface'))return [id];
      const upstream=p.material.filter(a=>a.canonical_object===id).map(a=>a.canonical_subject);
      return upstream.length?upstream.flatMap(x=>inletSources(x,new Set([...seen,id]))):[id];
    };
    return vessels.map(vessel=>{const extractors=next(vessel,'silo_extractor'),feeders=extractors.flatMap(x=>next(x,'belt_feeder')),gates=feeders.flatMap(x=>next(x,'diverter_gate'));return {vessel,extractors,feeders,gates,inlets:unique(p.material.filter(a=>a.canonical_object===vessel&&!owned.has(a.canonical_subject)).flatMap(a=>inletSources(a.canonical_subject)))};});
  }
  function modeFacts(facts,requested){
    const mode=a=>/^Mode: ([^(;]+)/i.exec(a.context?.condition||'')?.[1].trim();
    const modes=unique(facts.map(mode).filter(Boolean)),selected=modes.includes(requested)?requested:modes[0];
    return {modes,selected,facts:selected?facts.filter(a=>mode(a)===selected):[],general:facts.filter(a=>!mode(a))};
  }
  function crusherColumns(p,id){
    const owned=new Set(p.assembly(id).map(n=>n.id));
    const is=(id,k)=>kind(p,id)===k;
    const next=(id,k)=>unique(p.material.filter(a=>a.canonical_subject===id&&is(a.canonical_object,k)).map(a=>a.canonical_object));
    const prev=(id,k)=>unique(p.material.filter(a=>a.canonical_object===id&&is(a.canonical_subject,k)).map(a=>a.canonical_subject));
    return [...owned].filter(x=>is(x,'crusher')).sort((a,b)=>label(p,a).localeCompare(label(p,b))).map(crusher=>{
      const screens=prev(crusher,'screen').filter(x=>owned.has(x)),feeders=next(crusher,'feeder').filter(x=>owned.has(x));
      const inletGates=unique(screens.flatMap(x=>prev(x,'gate'))).filter(x=>owned.has(x));
      const outletGates=unique(feeders.flatMap(x=>next(x,'gate'))).filter(x=>owned.has(x));
      return {crusher,screens,feeders,inletGates,outletGates,inlets:unique(inletGates.flatMap(x=>prev(x,'conveyor'))),outlets:unique(outletGates.flatMap(x=>next(x,'conveyor'))).sort((a,b)=>label(p,a).localeCompare(label(p,b)))};
    });
  }
  function crusherRoute(p,column,route='screen',outlet){
    if(!column)return [];
    const pairs=new Set(),add=(as,bs)=>as.forEach(a=>bs.forEach(b=>pairs.add(a+'>'+b)));
    add(column.inlets,column.inletGates);
    if(route==='bypass')add(column.inletGates,column.feeders);
    else{add(column.inletGates,column.screens);add(column.screens,[column.crusher]);add(column.screens,column.feeders);add([column.crusher],column.feeders);}
    add(column.feeders,column.outletGates);add(column.outletGates,[outlet].filter(x=>column.outlets.includes(x)));
    return p.material.filter(a=>pairs.has(a.canonical_subject+'>'+a.canonical_object));
  }
  function driveSymbol(p,id){
    const types=unique((p.children.get(id)||[]).map(a=>kind(p,a.canonical_subject)));
    if(types.includes('gearbox'))return 'drive';
    if(types.includes('motor')&&types.includes('coupling'))return 'direct-drive';
    return 'motor';
  }
  function areaEntry(p,area){
    const type={blending:'coal_blending_silo_house',crushing:'crusher_house',bunkerfeed:'transfer_point'}[area];
    if(!type)return null;
    const houses=(p.stages.find(s=>s.id===area)?.entities||[]).filter(e=>!p.refs.has(e.id)&&((p.classes.get(e.id)||[]).includes(type)||area==='bunkerfeed'&&kind(p,e.id)==='transfer'));
    return houses.length===1?houses[0].id:null;
  }
  function transferColumns(p,id){
    const gates=unique((p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at'&&kind(p,a.canonical_subject)==='gate').map(a=>a.canonical_subject));
    return gates.sort((a,b)=>label(p,a).localeCompare(label(p,b))).map(gate=>{
      const paths=[];
      const walk=(from,path,seen)=>p.material.filter(a=>a.canonical_subject===from).forEach(a=>{
        const to=a.canonical_object;
        if(kind(p,to)==='conveyor')paths.push({outlet:to,edges:[...path,a]});
        else if(gates.includes(to)&&!seen.has(to))walk(to,[...path,a],new Set([...seen,to]));
      });
      walk(gate,[],new Set([gate]));
      return {gate,paths,gates:unique([gate,...paths.flatMap(x=>x.edges.map(a=>a.canonical_subject))]),
        inlets:unique(p.material.filter(a=>a.canonical_object===gate&&kind(p,a.canonical_subject)==='conveyor').map(a=>a.canonical_subject)),
        outlets:unique(paths.map(x=>x.outlet)).sort((a,b)=>label(p,a).localeCompare(label(p,b)))};
    }).filter(c=>c.inlets.length&&c.outlets.length);
  }
  function transferRoute(p,column,outlet){
    if(!column||!column.outlets.includes(outlet))return [];
    const route=new Set(column.paths.filter(x=>x.outlet===outlet).flatMap(x=>x.edges));
    return p.material.filter(a=>column.inlets.includes(a.canonical_subject)&&a.canonical_object===column.gate||route.has(a));
  }
  function fixedTripperColumns(p,id){
    const located=new Set((p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at').map(a=>a.canonical_subject));
    return [...located].filter(x=>(p.classes.get(x)||[]).includes('tripper')).sort((a,b)=>label(p,a).localeCompare(label(p,b))).flatMap(tripper=>{
      const inlet=p.material.find(a=>a.canonical_object===tripper&&kind(p,a.canonical_subject)==='conveyor')?.canonical_subject;
      const gate=p.material.find(a=>a.canonical_subject===tripper&&located.has(a.canonical_object)&&kind(p,a.canonical_object)==='gate')?.canonical_object;
      if(!inlet||!gate)return [];
      const edges=p.material.filter(a=>a.canonical_subject===inlet&&a.canonical_object===tripper||a.canonical_subject===tripper&&a.canonical_object===gate||a.canonical_subject===gate&&kind(p,a.canonical_object)==='conveyor');
      if(!edges.some(a=>a.canonical_subject===gate&&a.canonical_object===inlet))return [];
      return [{inlet,tripper,gate,edges,outlets:unique(edges.filter(a=>a.canonical_subject===gate).map(a=>a.canonical_object))}];
    });
  }
  return {kind,closestParents,breadcrumbs,scene,groupEdges,siloColumns,modeFacts,crusherColumns,crusherRoute,driveSymbol,areaEntry,transferColumns,transferRoute,fixedTripperColumns};
});
