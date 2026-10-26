/* Visual projection only. Scene coordinates are illustrative, never plant facts. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.PlantSceneModel=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const unique=xs=>[...new Set(xs)];
  const label=(p,id)=>p.entities.get(id)?.label||'';
  function kind(p,id){
    const c=(p.classes.get(id)||[]).join(' ').toLowerCase(),n=label(p,id).toLowerCase(),t=c+' '+n;
    if(p.refs.has(id))return 'reference';
    // Specific physical types win over words inherited in a component's label.
    if(/^uee-1$/i.test(n)||/primary_screen_house/.test(c))return 'screenhouse';
    if(/crusher_house/.test(c))return 'crusher-house';
    if(/crusher_dust_extraction_stream/.test(c))return 'de-stream';
    if(/crusher_dust_extraction/.test(c)||/bunker house dust extraction/i.test(n))return 'de-house';
    if(/coal_sampling_system/.test(c)||/coal sampling system|^eau-[12]$/i.test(n))return 'sampler-system';
    if(/sampling_component/.test(c)){
      if(/rotary sample collector|collector/i.test(n))return 'collector';
      if(/hammer crusher|sample crusher/i.test(n))return 'crusher';
      if(/reversible belt feeder|belt feeder/i.test(n))return 'feeder';
      if(/screw conveyor/i.test(n))return 'screw-conveyor';
      if(/slide gate|gate/i.test(n))return 'gate';
      return 'sampler';
    }
    if(/primary sampler|secondary sampler|cutter hood/i.test(n))return 'sampler';
    if(/rotary sample collector/i.test(n))return 'collector';
    if(/screw_conveyor/.test(c)||/screw conveyor/i.test(n))return 'screw-conveyor';
    if(/ring_granulator/.test(c))return 'crusher';
    if(/^ebc-\d+ housing and access$/.test(n)||/dust-cover assembly$/i.test(n))return 'crusher-housing';
    if(/rotor bearings and seals$|plummer block bearings/i.test(n))return 'bearing';
    if(/protection and monitoring$/.test(n))return 'protection';
    if(/crusher_rotor/.test(c))return 'crusher-rotor';
    if(/crusher_cage/.test(c))return 'cage';
    if(/hydraulic_power_pack|hydraulic_system/.test(c))return 'hydraulic';
    if(/hydraulic_cylinder/.test(c)||/luffing system$/i.test(n))return 'cylinder';
    if(/vibration_isolation_system/.test(c)||/spring supports and amplitude limiters$/i.test(n))return 'foundation';
    if(/vibration_exciter/.test(c))return 'exciter';
    if(/cyclone_separator/.test(c))return 'cyclone';
    if(/dust_hopper/.test(c))return 'chute';
    if(/damper/.test(c))return 'damper';
    if(/dust_extraction_duct|dust_capture_hood/.test(c))return 'duct';
    if(/rotary_airlock_valve/.test(c)||/rotary airlock|ralv/i.test(n))return 'airlock';
    if(/air_dryer/.test(c)||/air dryer|refrigerated.*dryer/i.test(n))return 'dryer';
    if(/electric_motor/.test(c))return 'motor';
    if(/magnetic_separator/.test(c)||/^at-[1-4]$/i.test(n)||/electromagnet|magnet coil|copper coil|annealed iron core/i.test(n))return 'electromagnet';
    if(/metal_detector_probe/.test(c))return 'detector';
    if(/metal_detector/.test(c))return 'detector';
    if(/belt_weighbridge|belt_weigher/.test(c))return 'weigher';
    if(/onboard water tank/i.test(n))return 'tank';
    if(/changeover valve|du1-gks/i.test(n))return 'changeover-valve';
    if(/level_sensor/.test(c)||/radar level|level transmitter|level switch|tilt switch/i.test(n))return 'level-sensor';
    if(/load_cell/.test(c))return 'sensor';
    if(/scraper blades?\b/i.test(n)&&/boom/i.test(n))return 'blade';
    if(/belt_scraper/.test(c))return 'scraper';
    if(/air_receiver/.test(c))return 'receiver';
    if(/air_compressor/.test(c))return 'compressor';
    if(/functional_assembly/.test(c)&&/common compressed-air supply train$/.test(n))return 'assembly';
    if(/conveyor_belt|bunker_sealing_system/.test(c)||/sealing belt|sealing-strip/i.test(n))return 'belt';
    if(/(?:isolation|solenoid|motorized|gate|globe|ball|non_return|pressure_relief|drain)_valve|pressure_regulator|valve_group/.test(c))return 'valve';
    if(/plug_group|filter_cover_group|filter_support_group/.test(c))return 'mechanical-part';
    if(/(?:^| )strainer(?: |$)|air_filter/.test(c))return 'filter';
    if(/metal_detector_marker/.test(c))return 'marker';
    if(/utility_header|piping_line/.test(c))return 'pipe';
    if(/thrust stand$/.test(n)&&/functional_assembly/.test(c))return 'bearing';
    if(/counterweight_group/.test(c)||/counterweight$/i.test(n))return 'counterweight';
    if(/wire_rope/.test(c)||/wire rope and sheaves$/i.test(n))return 'takeup';
    if(/electrohydraulic_thruster/.test(c)||(/thruster/i.test(n)&&!/brake/i.test(n)))return 'thruster';
    if(/progressive.*distributor|metering distributor|\bvsg\b|\bssv\b|\bssvd\b|zone-[123].*lubrication circuit|lubrication system-(?:i|ii|iii|iv)\b/i.test(n))return 'distributor-block';
    if((/pump station|grease pump|\bzpu\b|\bmfe5\b|electric pump unit|manual hand-pump circuit/i.test(n))&&!/motor/i.test(c))return 'grease-pump';
    if(/hose reel/i.test(n))return 'hose-reel';
    if(/spray header/i.test(n))return 'spray';
    // Prevent parent assembly names (Slewing, Long-travel, Tripper, Trolley, Grab, Elevator, Hopper, Boom) from overriding child component kinds:
    if(/slewing_bearing/.test(c)||/slew ring/i.test(n))return 'slew';
    if(/lubrication_pump/.test(c)||/pump unit$/i.test(n))return 'grease-pump';
    if(/pump unit reservoir$/i.test(n))return 'tank';
    if(/central grease lubrication.*filter$/i.test(n))return 'filter';
    if(/central grease lubrication.*control box$/i.test(n))return 'panel';
    if(/central grease lubrication.*distributor$/i.test(n))return 'distributor-block';
    if(/central grease lubrication.*(?:slewing and boom pulleys|long-travel wheels|tripper wheels and pulleys)$/i.test(n))return 'lubrication';
    if(/central grease lubrication.*pipelines and joints$/i.test(n))return 'pipe';
    if(/holdback|backstop|sprag/i.test(n))return 'sprag-holdback';
    if(/rack_and_pinion_gate/.test(c)||/rack-and-pinion.*gate|sliding gate blade/i.test(n))return 'rack-pinion';
    if(/lump grizzly grid|grizzly plate/i.test(n))return 'screen-plate';
    if(/pressurization fans/i.test(n))return 'fan';
    if(/machinery house structural enclosure/i.test(n))return 'building';
    if(/holding & closing rope drums|twin luffing rope drums/i.test(n))return 'hoist';
    if(/gearbox/.test(c)||(/gearbox/i.test(n)&&!/lubrication/i.test(n)))return 'gearbox';
    if(/coupling/.test(c)&&!/plug_group/.test(c))return 'coupling';
    if(/brake_assembly|thruster_drum_brake/.test(c)||(/disc brake|drum brake|caliper brake|emergency brake/i.test(n)&&!/motor|hoist drive|winch|drums/i.test(n)))return 'brake';
    if(/(?:^| )pulley(?: |$)/.test(c)&&!/clamshell|grab|trolley/i.test(n))return 'pulley';
    if(/traction sheave|diverter pulley/i.test(n))return 'pulley';
    if(/automatic rescue device|control and rescue equipment/i.test(n))return 'panel';
    if(/infrared door|overload detection|overspeed governor|fireman switch/i.test(n))return 'sensor';
    if(/skirtboard sealing|transfer chute to boom/i.test(n))return 'chute';
    if(/machine mounted dust suppression/i.test(n))return 'spray-system';
    if(/scraper-chain lubrication|motorized central lubrication|lubrication_arrangement/i.test(t))return 'lubrication';
    if(/cylindrical shell and ss304m conical hopper/i.test(n))return 'bunker';
    if(/common ds tank-2.*compartment/i.test(n))return 'tank';
    if(/(?:^| )hoist(?: |$)|overhead_crane/.test(c))return 'hoist';
    if((/hoist_mechanism|electric_hoist|manual_hoist/.test(c)||/\b(hoist|winch)\b|hoist system$/i.test(n))&&!/gearbox|coupling|brake/i.test(n))return 'hoist';
    if(/long_travel_mechanism|wheel_bogie_system/.test(c)||/travel system$|travel drive and wheel|wheel bogie|long-travel/i.test(n))return 'bogie';
    if(/rail_clamp|storm_anchor/.test(c)||/rail clamp|storm anchor|tie-down/i.test(n))return 'rail-clamp';
    if(/cable_reel/.test(c)||/cable reel|festoon/i.test(n))return 'cable-reel';
    if(/slew_bearing/.test(c)||/slew system$|slewing|pinion and bearings$|ring bearing and pinions/i.test(n))return 'slew';
    if(/operator_cabin/.test(c)||/operator cabin|\bcabin\b/i.test(n)&&!/electrical cabinet/i.test(n))return 'cabin';
    if(/machinery_house/.test(c)||/electrical house|machinery house/i.test(n))return 'building';
    if(/electrical_switchboard|mcc_lineup|power_transformer/.test(c)||/\bmcc-\d|\bswitchboard\b|\bswitchgear\b|switch board|\b00bbt|\b00bft|\bsld\b|electrical cabinet/i.test(n))return 'switchboard';
    if(/elevator/.test(c)||/^snc-\d+\b|elevator/i.test(n))return 'elevator';
    if(/clamshell bucket|grab bucket|\bgrab\b/i.test(n))return 'grab';
    if(/trolley/i.test(n)&&!/hoist/i.test(c))return 'trolley';
    if(/scraper boom|boom conveyor|hinged boom|luffing boom/i.test(n)&&!/drive group|motor|gearbox|coupling|brake|blade|take-up|belt and pulley|weigher/i.test(n))return 'boom';
    if(/receiving hopper|surge hopper|hopper/i.test(n))return 'chute';
    if(/cardan|belt and pulley transmission|shrink-disc/i.test(n))return 'shaft-coupling';
    if(/blind feed deck|screen body and grizzly deck/i.test(n))return 'screen';
    if(/diverging|diverter flap blade/i.test(n))return 'gate';
    if(/skirt_sealing_system/.test(c)||/deck plate, seal plate and skirtboard/i.test(n))return 'chute';
    if(/magnetic_separator/.test(c)||/^at-[1-4]$/i.test(n)||/electromagnet|magnet coil|copper coil|annealed iron core/i.test(n))return 'electromagnet';
    if(/coal_analyzer/.test(c)||/^cv-[1-6]$/i.test(n)||/source-holder|radiation source|cf-252/i.test(n))return 'radiation-source';
    if(/detector and cradle/i.test(n))return 'sensor';
    if(/frame and shielding/i.test(n))return 'protection';
    if(/hood and access/i.test(n))return 'access';
    if(/idler_set/.test(c)||/carrying idlers|impact.*idlers|transition idlers|return idlers/i.test(n))return 'idler';
    if(/mechanical_component/.test(c)){
      if(/sandbag marker$/.test(n))return 'marker';
      if(/blade blocks$|rubber blade$|v-plough$|urethane blade|tungsten-carbide|cushion module/i.test(n))return 'scraper';
      if(/scraper blades?\b/i.test(n))return 'blade';
      if(/\bseal(?:s)?(?: group)?$|labyrinth seal|gland packing|o-ring|dust covers/i.test(n))return 'seal';
      if(/counterweight$|wire rope$|suspension ropes|travelling counterweight/i.test(n))return 'takeup';
      if(/rotor shaft|main shaft and sleeve|line shaft|shaft and sleeves|stub shaft/i.test(n))return 'rotor-shaft';
      if(/end discs|spacing discs|suspension arms/i.test(n))return 'rotor-disc';
      if(/suspension bars|hammer replacement maintenance bar/i.test(n))return 'suspension-bar';
      if(/ring hammers/i.test(n))return 'ring-hammer';
      if(/screen plates?|breaker plate|grizzly bars|grizzly plate|impact bars/i.test(n))return 'screen-plate';
      if(/cage frame/i.test(n))return 'cage';
      if(/upper frame|lower frame/i.test(n))return 'crusher-housing';
      if(/cage adjust|compression spring|toggle and eccentric|ratchet/i.test(n))return 'cage-adjuster';
      if(/wear liners|deflector liners|housing liners|hardox.*liner|ceramic.*liner|tivar.*liner|baffle plate|casing and inspection/i.test(n))return 'wear-liner';
      if(/tramp iron trap/i.test(n))return 'tramp-trap';
      if(/helical isolation springs|viscous dampers|viscodampers|snubber|elastomeric buffer|spring supports|front springs|rear springs|spring elements|amplitude limiters|steel shims|adhesive pads/i.test(n))return 'spring-isolator';
      if(/brake drum|brake shoes|brake liners|main spring|shoe clearance|tie rod and adjusting|disc caliper|torque spring|centrifugal overspeed brake|brake spring/i.test(n))return 'brake-shoe';
      if(/driving hub|driven hub|\bhubs$|gear hubs|\bsleeves$|toothed outer sleeve|impeller and runner|sdfc-370 impeller|gear teeth|pin-bush coupling|cardan shaft|v-belt and pulley|scoop tube and casing|gearing and oil sump|hollow output shaft|end covers|connecting bolts|coupling guard|spacer sleeve/i.test(n))return 'coupling-hub';
      if(/head pulley bearings/i.test(n))return 'bearing';
      if(/storm lock/i.test(n))return 'rail-clamp';
      if(/needle.*rod|support rollers and frame/i.test(n))return 'needle-rods';
      if(/rack.*pinion|handwheel and bevel|travelling gate carriage|slide plate/i.test(n))return 'rack-pinion';
      if(/search coil|under-belt transmitter|over-belt receiver/i.test(n))return 'search-coil';
      if(/holdback|backstop|sprag/i.test(n))return 'sprag-holdback';
      if(/impeller and suction volute|pump impeller|strainer and foot valve|pump shroud|pump cover|motor stool/i.test(n))return 'impeller';
      if(/passenger car|lift cage|landing doors|guide rails/i.test(n))return 'elevator-car';
      if(/weighbridge|weight supports and hangers/i.test(n))return 'weigher';
      if(/clean-air plenum/i.test(n))return 'duct';
      if(/manual release devices/i.test(n))return 'actuator';
      if(/restraint arm|retaining spring|mechanical stop/i.test(n))return 'sensor';
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
    if(/extractor_blade/.test(c)||/scraper chain and blades|scraper blades?\b/i.test(n))return 'blade';
    if(/reclaim_platform/.test(c))return 'platform';
    if(/variable_frequency_drive|local_control_panel/.test(c))return 'panel';
    if(/relay|switch|instrument|gauge|sensor|protection_device|limit_switch_group/.test(c))return 'sensor';
    if(/lubrication_system/.test(c))return 'lubrication';
    if(/silo_vent_filter/.test(c))return 'filter';
    if(/fan/.test(c))return 'fan';
    if(/diverter_gate|rod_gate|slide_gate/.test(c))return 'gate';
    if(/belt_feeder|vibrating_feeder/.test(c))return 'feeder';
    if(/maintenance_access/.test(c))return 'access';
    if(/ventilation_duct|hvac_system/.test(c))return 'duct';
    if(/dfds_system/.test(c)||/local dfds/i.test(n))return 'spray-system';
    if(/outlet flange|rod\/slide gate interface/i.test(n))return 'gate';
    if(/spray_application_point|spray_header/.test(c))return 'spray';
    if(/adjusting sleeve$/.test(n))return 'sleeve';
    if(/labyrinth seal$/.test(n))return 'seal';
    if(/shell and sloping liner$/.test(n))return 'silo';
    if(/manholes and access openings$/.test(n))return 'access';
    if(/level and temperature instruments$/.test(n))return 'level-sensor';
    if(/electrical|control|pulse_valve/.test(c))return 'panel';
    if(/functional_area/.test(c))return /yard|stockpile/.test(n)?'yard':'assembly';
    if(/drive (?:assembly|group)(?: \d+)?$|geared brake drive$/i.test(n))return 'drive';
    if(/shared cyclone hopper and dust return$/.test(n))return 'cyclone';
    if(/(?:belt protection(?: devices)?|protection and instrumentation)$/i.test(n))return 'protection';
    if(/(?:belt and mechanical|mechanical and structural)(?: assembl(?:y|ies))?$/i.test(n))return 'mechanical';
    if(/radiator|cooler/.test(t))return 'cooler';
    if(/motor/.test(t))return 'motor';
    if(/gearbox/.test(t))return 'gearbox';
    if(/coupling/.test(c)||/coupling (pst|rg)|scoop coupling|fluid coupling|flexible coupling/i.test(n))return 'coupling';
    if(/brake/.test(t))return 'brake';
    if(/pulley|rollers$/.test(t))return 'pulley';
    if(/idler|roller/.test(t))return 'idler';
    if(/scraper/.test(t)&&!/reclaimer/.test(c)&&!/take.up/i.test(n))return 'scraper';
    if(/take.up|hgtu/.test(t))return 'takeup';
    if(/pump/.test(t))return 'pump';
    if(/filter|strainer/.test(t))return 'filter';
    if(/nozzle|sprinkler|spray gun/.test(t))return 'spray';
    if(/valve/.test(t))return 'valve';
    if(/sensor|switch|instrument|protection_device/.test(c)||/\b(bss|pcs|zss)\b/.test(n))return 'sensor';
    if(/coal_bunker_bay/.test(c)||/coal bunker bay/i.test(n))return 'bunker-bay';
    if(/coal_bunker|tank_compartment|material_storage_bin/.test(c)||/^bunker-[a-f] of unit-[12]/i.test(n)||/conical hopper/i.test(n))return 'bunker';
    if(/tank|sump/.test(t))return 'tank';
    if(/dust|spds|dfds/.test(t))return 'water';
    if(/water_distribution/.test(c))return 'water';
    if(/chute/.test(t))return 'chute';
    if(/tripper/.test(c)||/^(tt|ftr)-\d+$/i.test(n)||/travelling tripper/i.test(n))return 'tripper';
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
    if(/fire_protection/.test(c)||/fire detection/i.test(n))return 'protection';
    if(/belt|idler|scraper|take.up/.test(t))return 'belt';
    return 'assembly';
  }
  function hasInAssembly(p,anc,desc){
    if(anc===desc)return false;
    const a=p.assembly(anc);
    return a._ids?a._ids.has(desc):a.slice(1).some(n=>n.id===desc);
  }
  function closestParents(p,id){
    const parents=unique((p.parents.get(id)||[]).map(a=>a.canonical_object));
    // Remove a distant ancestor when a more specific parent also owns the item.
    return parents.filter(candidate=>!parents.some(other=>other!==candidate&&hasInAssembly(p,candidate,other)));
  }
  function breadcrumbs(p,id){
    const chain=[],seen=new Set();let next=id;
    while(next&&!seen.has(next)&&chain.length<16){seen.add(next);chain.unshift(next);next=closestParents(p,next).sort((a,b)=>label(p,a).localeCompare(label(p,b)))[0];}
    return chain;
  }
  function roots(p,ids){
    const set=new Set(ids);
    return ids.filter(id=>!ids.some(other=>other!==id&&hasInAssembly(p,other,id)&&!hasInAssembly(p,id,other))).filter(id=>set.has(id));
  }
  function expandPhysicalParts(p,ids,maxDepth=2){
    const out=[];
    const visit=(cid,depth)=>{
      const cls=p.classes.get(cid)||[];
      const children=unique((p.children.get(cid)||[]).map(a=>a.canonical_subject)).filter(x=>!p.refs.has(x));
      const isContainer=cls.some(c=>['functional_assembly','take_up_assembly','hgtu_assembly'].includes(c))||['drive','mechanical','protection','assembly','takeup'].includes(kind(p,cid))||/HT Switch Board$|LT Switch Board$/i.test(label(p,cid));
      if(children.length&&isContainer&&depth<maxDepth){
        if(cls.some(c=>['take_up_assembly','hgtu_assembly'].includes(c))||/HT Switch Board$|LT Switch Board$/i.test(label(p,cid)))out.push(cid);
        children.forEach(gc=>visit(gc,depth+1));
      }else{
        out.push(cid);
      }
    };
    ids.forEach(cid=>visit(cid,0));
    return unique(out);
  }
  function expandYardMachineParts(p,ids){
    const out=[];
    const visit=(cid,depth)=>{
      const k=kind(p,cid),lbl=label(p,cid).toLowerCase();
      const children=unique((p.children.get(cid)||[]).map(a=>a.canonical_subject)).filter(x=>!p.refs.has(x));
      const isSkid=['water','lubrication','protection','hydraulic','cabin','building','cable-reel'].includes(k)||/hydraulic power pack|onboard.*dss|lubrication|fire detection/i.test(lbl);
      if(isSkid||!children.length||depth>=2){
        out.push(cid);
        return;
      }
      if(!/drive group$/i.test(lbl))out.push(cid);
      children.forEach(gc=>visit(gc,depth+1));
    };
    ids.forEach(cid=>visit(cid,0));
    return unique(out);
  }
  function scene(p,id,area){
    const current=a=>PlantCurrent(a);
    function PlantCurrent(a){const c=a.context||{},now=Date.now();return (!c.valid_from||Date.parse(c.valid_from)<=now)&&(!c.valid_to||Date.parse(c.valid_to)>now);}
    if(!id){
      const stage=p.stages.find(s=>s.id===area);if(!stage)return {kind:'plant',id:null,nodes:[],edges:[],title:'Maitree coal handling plant',description:'Follow coal from unloading to the boiler bunkers. Open a process area to explore its equipment.'};
      const members=stage.entities.filter(e=>!p.refs.has(e.id)).map(e=>e.id),set=new Set(members);
      const flow=unique(p.material.flatMap(a=>[a.canonical_subject,a.canonical_object]).filter(x=>set.has(x)));
      const entries=unique([...members.filter(x=>(p.classes.get(x)||[]).includes('functional_area')),...roots(p,members).filter(x=>(p.children.get(x)||[]).length||(p.incoming.get(x)||[]).some(a=>a.predicate==='located_at')||!flow.length)]);
      const ids=unique([...flow,...entries]);
      return {kind:'area',id:null,area:stage.id,title:stage.title,description:stage.description,nodes:ids.map(x=>node(x,'equipment')),edges:p.material.filter(a=>ids.includes(a.canonical_subject)&&ids.includes(a.canonical_object)),all:members};
    }
    if(!p.entities.has(id))return {kind:'missing',id,nodes:[],edges:[],title:'Equipment unavailable',description:'This equipment is not active in the current model.'};
    const k=kind(p,id);
    const rawDirectChildren=unique((p.children.get(id)||[]).map(a=>a.canonical_subject)).filter(x=>!p.refs.has(x));
    const selfLbl=label(p,id);
    const fdZoneMatch=/^(EAD-[1-4]) Fire detection and clean-agent system (Z[12]01) Protected zone/i.exec(selfLbl);
    const fdSysMatch=!fdZoneMatch&&/^(EAD-[1-4]) Fire detection and clean-agent system$/i.exec(selfLbl);
    const extraFdChildren=fdZoneMatch?[...p.entities.values()].filter(e=>e.id!==id&&e.label.startsWith(`${fdZoneMatch[1]} Fire detection`)&&e.label.includes(` ${fdZoneMatch[2]} `)).map(e=>e.id):fdSysMatch?[...p.entities.values()].filter(e=>e.id!==id&&e.label.startsWith(`${fdSysMatch[1]} Fire detection`)&&/Z[12]01 /.test(e.label)).map(e=>e.id):[];
    const directChildren=unique([...rawDirectChildren,...extraFdChildren]);
    const own=['conveyor','feeder'].includes(k)?expandPhysicalParts(p,directChildren,2):['stacker','reclaimer'].includes(k)?expandYardMachineParts(p,directChildren):['ship','mechanical','screenhouse','boom','switchboard'].includes(k)?expandPhysicalParts(p,directChildren,1):roots(p,directChildren);
    const assembly=new Set(p.assembly(id).map(n=>n.id));
    const situated=roots(p,unique((p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at'&&current(a)&&!assembly.has(a.canonical_subject)).map(a=>a.canonical_subject)));
    const detail=['extractor','crusher'].includes(k)?unique(own.filter(x=>kind(p,x)==='drive').flatMap(x=>(p.children.get(x)||[]).map(a=>a.canonical_subject))):[];
    const isHtBusSec=k==='switchboard'&&/#00BB([D-J])/i.test(selfLbl);
    const htBusCode=isHtBusSec?/#00BB([D-J])/i.exec(selfLbl)[0].toUpperCase():null;
    const parentSwb=k==='switchboard'&&(isHtBusSec||/Switchgear & Feeder Lineup|415 V Bus Sections|415 V Incomer|3\.3 kV Bus-Coupler/i.test(selfLbl))?closestParents(p,id).filter(pid=>/Switch Board$/i.test(label(p,pid))):[];
    const swbSiblings=parentSwb.flatMap(pid=>unique((p.children.get(pid)||[]).map(a=>a.canonical_subject)).filter(x=>x!==id&&!p.refs.has(x)));
    if(parentSwb.length){parentSwb.forEach(pid=>{if(!own.includes(pid))own.unshift(pid);});swbSiblings.forEach(sid=>{if(!own.includes(sid))own.push(sid);});}
    const visible=new Set([id,...own,...situated,...detail]);
    const netVisible=isHtBusSec?new Set([id]):k==='switchboard'?new Set([id,...own,...situated.filter(s=>kind(p,s)==='switchboard'),...detail]):visible;
    const extraBusLoads=isHtBusSec?parentSwb.flatMap(pid=>p.networks.filter(a=>a.context?.network==='electrical'&&(a.canonical_subject===pid||a.canonical_object===pid)).map(a=>a.canonical_subject===pid?a.canonical_object:a.canonical_subject).filter(lid=>lid!==id&&(p.outgoing.get(lid)||[]).some(fa=>fa.predicate==='compartment_number'&&String(fa.value).toUpperCase().includes(htBusCode)))):[];
    const allowedNets=k==='switchboard'?['electrical']:['mechanical','material','control','electrical'];
    const utilityTrain=['water','assembly'].includes(k)&&(p.classes.get(id)||[]).includes('functional_assembly')&&/common (?:water|compressed-air) supply train$/i.test(label(p,id));
    const waterSystem=(p.classes.get(id)||[]).some(c=>['service_water_system','potable_water_system','dust_suppression_system','feed_water_system'].includes(c));
    const boundary=['silo-house','crusher-house','transfer','screenhouse','sampler-system'].includes(k)?p.material.filter(a=>visible.has(a.canonical_subject)||visible.has(a.canonical_object)).flatMap(a=>[a.canonical_subject,a.canonical_object]):['de-house','de-stream','spray-system'].includes(k)||utilityTrain||waterSystem?p.networks.filter(a=>assembly.has(a.canonical_subject)!==assembly.has(a.canonical_object)).flatMap(a=>[a.canonical_subject,a.canonical_object]):[];
    const related=unique([...p.networks.filter(a=>(a.canonical_subject===id||a.canonical_object===id)||(allowedNets.includes(a.context?.network)&&(netVisible.has(a.canonical_subject)||netVisible.has(a.canonical_object)))).flatMap(a=>[a.canonical_subject,a.canonical_object]),...(p.incoming.get(id)||[]).filter(a=>current(a)&&['serves','serves_equipment','protects_equipment','sprays_at','covered_by'].includes(a.predicate)).map(a=>a.canonical_subject),...(p.outgoing.get(id)||[]).filter(a=>current(a)&&['covered_by','associated_with'].includes(a.predicate)).map(a=>a.canonical_object)]).filter(x=>x!==id&&!assembly.has(x)&&!situated.includes(x));
    const external=unique([...related,...extraBusLoads,...boundary]).filter(x=>!visible.has(x)&&!assembly.has(x)&&!p.refs.has(x));
    const nodes=[node(id,'self'),...own.map(x=>node(x,'part')),...situated.map(x=>node(x,'located')),...detail.map(x=>node(x,'detail')),...external.map(x=>node(x,'connected'))];
    const set=new Set(nodes.map(n=>n.id));
    const edges=p.networks.filter(a=>set.has(a.canonical_subject)&&set.has(a.canonical_object));
    const relationships=[];
    for(const uid of set){
      for(const a of (p.outgoing.get(uid)||[])){
        if(a.canonical_object&&set.has(a.canonical_object)&&['part_of','located_at','covered_by','serves_equipment','associated_with','monitors_equipment','protects_equipment'].includes(a.predicate)&&current(a))relationships.push(a);
      }
    }
    const role=(p.outgoing.get(id)||[]).find(a=>['equipment_role','purpose','equipment_description','function'].includes(a.predicate)&&typeof a.value==='string');
    return {kind:k,id,title:label(p,id),description:role?.value||((p.classes.get(id)||[]).join(' ').replaceAll('_',' ')),nodes,edges,relationships,all:unique([...assembly,...situated,...external])};
    function node(x,role){return {id:x,label:label(p,x),kind:kind(p,x),role};}
  }
  function groupEdges(edges){
    const map=new Map();for(const a of edges){const k=[a.canonical_subject,a.canonical_object,a.context?.network||a.predicate].join('|');if(!map.has(k))map.set(k,{from:a.canonical_subject,to:a.canonical_object,network:a.context?.network||a.predicate,facts:[]});map.get(k).facts.push(a);}return [...map.values()];
  }
  function siloColumns(p,id){
    const owned=new Set(p.assembly(id).map(n=>n.id));
    const vessels=roots(p,[...owned].filter(x=>(p.classes.get(x)||[]).includes('coal_silo'))).sort((a,b)=>label(p,a).localeCompare(label(p,b)));
    const next=(from,type)=>unique(p.material.filter(a=>a.canonical_subject===from&&owned.has(a.canonical_object)&&(p.classes.get(a.canonical_object)||[]).includes(type)).map(a=>a.canonical_object));
    const inletSources=(cid,seen=new Set())=>{
      if(seen.has(cid))return [];
      const cls=p.classes.get(cid)||[];
      if(cls.includes('conveyor_belt')){
        const parentConv=closestParents(p,cid).find(pid=>kind(p,pid)==='conveyor');
        if(parentConv)return [parentConv];
      }
      if(!cls.includes('chute_interface')&&!cls.includes('conveyor_belt'))return [cid];
      const upstream=p.material.filter(a=>a.canonical_object===cid).map(a=>a.canonical_subject);
      return upstream.length?upstream.flatMap(x=>inletSources(x,new Set([...seen,cid]))):[cid];
    };
    return vessels.map(vessel=>{const extractors=next(vessel,'silo_extractor'),feeders=extractors.flatMap(x=>next(x,'belt_feeder')),gates=feeders.flatMap(x=>next(x,'diverter_gate'));return {vessel,extractors,feeders,gates,inlets:unique(p.material.filter(a=>a.canonical_object===vessel&&!owned.has(a.canonical_subject)).flatMap(a=>inletSources(a.canonical_subject))).filter(x=>kind(p,x)==='conveyor')};});
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
    const owned=new Set(p.assembly(id).map(n=>n.id));
    const located=(p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at').map(a=>a.canonical_subject);
    const gates=unique([...located,...owned].filter(x=>kind(p,x)==='gate'));
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
    const located=new Set([...(p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at').map(a=>a.canonical_subject),...p.assembly(id).map(n=>n.id)]);
    return [...located].filter(x=>(p.classes.get(x)||[]).includes('tripper')||kind(p,x)==='tripper').sort((a,b)=>label(p,a).localeCompare(label(p,b))).flatMap(tripper=>{
      const inlet=p.material.find(a=>a.canonical_object===tripper&&kind(p,a.canonical_subject)==='conveyor')?.canonical_subject;
      const gate=p.material.find(a=>a.canonical_subject===tripper&&located.has(a.canonical_object)&&kind(p,a.canonical_object)==='gate')?.canonical_object;
      if(!inlet||!gate)return [];
      const edges=p.material.filter(a=>a.canonical_subject===inlet&&a.canonical_object===tripper||a.canonical_subject===tripper&&a.canonical_object===gate||a.canonical_subject===gate&&kind(p,a.canonical_object)==='conveyor');
      if(!edges.some(a=>a.canonical_subject===gate&&a.canonical_object===inlet))return [];
      return [{inlet,tripper,gate,edges,outlets:unique(edges.filter(a=>a.canonical_subject===gate&&kind(p,a.canonical_object)==='conveyor').map(a=>a.canonical_object))}];
    });
  }
  return {kind,closestParents,breadcrumbs,scene,groupEdges,siloColumns,modeFacts,crusherColumns,crusherRoute,driveSymbol,areaEntry,transferColumns,transferRoute,fixedTripperColumns};
});
