/* Read-only navigation projection. Browse groups are not new plant assertions.
   Grouping basis: coal flow 175001 Rev8, control write-up Rev04 pp4-8/55.
   Connections, hierarchy, values and applicability always come from accepted facts. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.PlantExplorerModel=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const stages=[
    {id:'unloading',title:'Jetty & unloading',short:'Unloading',number:'01',row:1,col:1,description:'Receive vessel coal and feed the two receiving streams.',tags:'Ship unloaders · EAC-1 / 2 · UEF-1 (TP-1)'},
    {id:'screening',title:'Primary screening',short:'Screening',number:'02',row:1,col:2,description:'Screen incoming coal; separate oversize rejects.',tags:'UEE-1 (PSH) · EBD-1–4 · EAC-3'},
    {id:'distribution',title:'Distribution & diversion',short:'Distribution',number:'03',row:1,col:3,description:'Direct coal onward to silos or divert it to the stockyard.',tags:'UEF-3–7 (TP-3–7) · EAC-4 / 5 · EBA-6'},
    {id:'stockyard',title:'Stockyard',short:'Stockyard',number:'04',row:2,col:3,description:'Stack, store and reclaim coal through four yard branches.',tags:'EAD · EAE · EAF · yard conveyors'},
    {id:'reclaim',title:'Reclaim transfer',short:'Reclaim transfer',number:'05',row:2,col:2,description:'Combine selected reclaim streams and deliver coal to the silos.',tags:'UEF-8–12 (TP-8–12) · EBA-15 / 16'},
    {id:'blending',title:'Blending silos',short:'Blending',number:'06',row:2,col:1,description:'Receive, store and extract coal into the crusher-feed streams.',tags:'UEE-2 (CBSH) · EBB-1 / 2 · extractors'},
    {id:'crushing',title:'Screening & crushing',short:'Crushing',number:'07',row:3,col:1,description:'Screen and crush coal, with documented bypass alternatives.',tags:'UEE-3 (CRH) · EBA-17 · EBC-1 / 2'},
    {id:'bunkerfeed',title:'Bunker-feed transfer',short:'Bunker feed',number:'08',row:3,col:2,description:'Transfer processed coal to either bunker conveyor.',tags:'EBA-18 · UEF-13 (TP-13) · EBA-19'},
    {id:'bunkers',title:'Unit bunkers',short:'Bunkers',number:'09',row:3,col:3,description:'Distribute coal to the selected unit and bunker position.',tags:'TT-1–4 · Unit 1 / 2 · bunkers A–F'}
  ];
  const pathStages={
    1:['unloading','screening','distribution','stockyard'],
    2:['unloading','screening','distribution','stockyard','blending','crushing','bunkerfeed','bunkers'],
    3:['stockyard','reclaim','blending','crushing','bunkerfeed','bunkers'],
    4:['blending','crushing','bunkerfeed','bunker'],
    5:['unloading','screening','distribution','stockyard','blending']
  };
  // Fix typo guard: ensure path 4 uses 'bunkers'
  pathStages[4]=['blending','crushing','bunkerfeed','bunkers'];
  const pathTitles={1:'Ship → stockyard',2:'Ship → bunkers + stacking',3:'Reclaim → bunkers',4:'Silos → bunkers',5:'Ship → silos + stacking'};
  const pretty=s=>String(s||'').replaceAll('_',' ');
  function reference(e,classes){return e.category==='document'||classes.some(c=>/calculation|control_requirement_scheme|engineering_standard|design_basis|equipment_design_reference|piping_specification/.test(c));}
  function stageForLabel(label){
    const n=String(label).toUpperCase().trim();
    // Exact identities / tag families only. An arbitrary substring in a document
    // title never establishes equipment placement or physical ownership.
    if(/^(COAL JETTY|COAL SHIP UNLOADER-[123]|EAC-[12][AB]|UEF-1|AT-[12]|QB-[12]|EAT-[12])$/.test(n))return 'unloading';
    if(/^(UEE-1|UEE-1 OVERSIZE REJECT BINS|EBD-[1-4]|EAC-3[AB]|KB-RG-[1-4]|KB-RPG-[1-4]|EAU-1(?: .*)?)$/.test(n)||n==='UEF-3 COAL SAMPLING SYSTEM')return 'screening';
    if(/^(UEF-[3-7]|EAC-[45][AB]|EBA-6[AB]|KB-FD-[1-8]|FG-[1-6]|FTR-[1-4]|CV-[12])$/.test(n))return 'distribution';
    if(/^(EAC-(7|9|11|13)|EBA-(8|10|12|14)|EA[DEF]-[1-4]|UEB-[1-4]|UAX-[1-8]|COAL STOCKPILE YARD)$/.test(n))return 'stockyard';
    if(/^(UEF-(8|9|10|11|12)|EBA-(15|16)[AB]|FG-(7|8|9|10|11|12)|AT-[34]|CV-[34])$/.test(n))return 'reclaim';
    if(/^(COAL BLENDING SILO HOUSE|UEE-2|EBB-[12]|EBE-CES-[12]|KF-[34]|FG-1[34])$/.test(n))return 'blending';
    if(/^(UEE-3|EBA-17[AB]|EBD-[56]|EBC-[12]|KF-[12]|FG-15[AB]?|FG-16|CV-[56])$/.test(n))return 'crushing';
    if(/^(UEF-13|EBA-1[89][AB]|FG-1[78]|EAT-[34]|QB-[34]|EAU-2(?: .*)?)$/.test(n)||n==='UEF-13 COAL SAMPLING SYSTEM'||n==='UEF-13 COAL SAMPLING SYSTEM (EAU-2)')return 'bunkerfeed';
    if(/^(TT-[1-4]|FG-(19|20|21|22)|UNIT-[12] COAL BUNKER BAY|BUNKER-[A-F] OF UNIT-[12])$/.test(n))return 'bunkers';
    return null;
  }
  function current(a,at){
    const c=a.context||{};
    const start=c.valid_from?Date.parse(c.valid_from):null,end=c.valid_to?Date.parse(c.valid_to):null;
    return (!c.valid_from||(Number.isFinite(start)&&start<=at))&&(!c.valid_to||(Number.isFinite(end)&&at<end));
  }
  function qualificationSeverity(a){
    const text=[a?.predicate,a?.value,a?.context?.condition,a?.context?.basis].filter(Boolean).join(' ').toLowerCase();
    if(/voltage|\bkv\b|415\s*v|6\.6\s*kv|motor.*power|\bkw\b|trip|interlock|permissive|brake|stopping\s*time|emergency|safety|protection|short.circuit|ip6[567]|explosion|hazardous|holdback/i.test(text))return 'high';
    if(/capacity|t\/h|tph|flow|m3\/h|head|pressure|\bbar\b|\bkpa\b|speed|m\/s|\brpm\b|diameter|width|length|elevation|travel|stroke|nozzle|quantity|count|ratio|pulley|idler|chute|gate/i.test(text))return 'medium';
    return 'low';
  }
  function isPrimaryEquipment(p,id){
    const e=p.entities.get(id);
    if(!e||p.refs.has(id)||e.category==='document')return false;
    if([e.label,...(e.aliases||[])].some(n=>stageForLabel(n)))return true;
    const classes=p.classes.get(id)||[];
    if(classes.some(c=>/belt_conveyor|belt_feeder|transfer_point|transfer_house|primary_screening_house|coal_blending_silo_house|crusher_house|plant_building|functional_area|ship_unloader|stacker_machine|portal_reclaimer|ring_granulator|vibrating_screen|coal_silo|silo_extractor|coal_bunker|tripper|coal_sampling_system|sampling_system|dust_extraction_system|dust_suppression_system|dfds_system|service_water_system|potable_water_system|feed_water_system|runoff_pond|pump_house|elevator|coal_analyser|belt_weigher|metal_detector|magnetic_separator/.test(c)))return true;
    const parents=(p.parents.get(id)||[]).filter(a=>p.entities.get(a.canonical_object)?.label!=='Maitree Coal Handling Plant');
    if(!parents.length&&(p.children.get(id)||[]).length>0)return true;
    return false;
  }

  /**
   * Derive comprehensive engineering aliases, plant codes, KKS/BHEL/ISG equivalents,
   * and a human-readable common name subtitle for each entity without mutating
   * committed database assertions.
   */
  function deriveOwnAliases(e,classes){
    const lbl=String(e.label||'').trim();
    const u=lbl.toUpperCase();
    const own=new Set(e.aliases||[]);
    let commonName='';
    const add=(...items)=>{for(const x of items)if(x)own.add(x);};

    // 1. Major Process Buildings (UEE-1 = PSH, UEE-2 = CBSH, UEE-3 = CRH)
    if(u==='UEE-1'||classes.includes('primary_screening_house')){
      commonName='Primary Screening House · PSH';
      add('Primary Screening House','Primary Screen House','Primary Screenhouse','PSH','UEE-1','UEE 1','UEE1','Screen House','Screening House','Stage-1 Screen House');
    }else if(u==='COAL BLENDING SILO HOUSE'||u==='UEE-2'||classes.includes('coal_blending_silo_house')){
      commonName='UEE-2 · CBSH · Silo House';
      add('UEE-2','UEE 2','UEE2','CBSH','Coal Blending Silo House','Blending Silo House','Blending Silo','Coal Silo House','Silo House','Silo Building','Silo');
    }else if(u==='UEE-3'||(classes.includes('crusher_house')&&!/RIHAND/i.test(u))){
      commonName='Crusher House · CRH';
      add('Crusher House','CRH','UEE-3','UEE 3','UEE3','Secondary Screening & Crushing House','Crushing House','Coal Crusher House','Secondary Screen House');
    }

    // 2. Transfer Points / Transfer Houses / Transfer Towers (UEF-1..13, TP-16..18)
    let m=/^UEF-(\d+)$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Transfer Point TP-${n} · Transfer House ${n}`;
      add(`TP-${n}`,`TP ${n}`,`TP${n}`,`TP-0${n}`,`Transfer Point ${n}`,`Transfer Point-${n}`,`Transfer Point TP-${n}`,`Transfer House ${n}`,`Transfer House-${n}`,`TH-${n}`,`TH ${n}`,`TH${n}`,`Transfer Tower ${n}`,`TTW-${n}`,`UEF ${n}`,`UEF${n}`,'transfer point','transfer house','transfer tower','TP','UEF','TH');
    }
    m=/^TP-(\d+)$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Transfer Point UEF-${n}`;
      add(`UEF-${n}`,`UEF ${n}`,`UEF${n}`,`TP ${n}`,`TP${n}`,`Transfer Point ${n}`,`Transfer Point-${n}`,`Transfer House ${n}`,`TH-${n}`,`TH ${n}`,`TH${n}`,'transfer point','transfer house','TP','UEF');
    }

    // 3. Belt Conveyors (EAC-1A..13, EBA-6A..19B, LS-EAC-1)
    m=/^(EAC|EBA)-(\d+[AB]?)$/.exec(u);
    if(m){
      const pref=m[1],num=m[2],numBase=num.replace(/[AB]$/,'');
      const altPref=pref==='EAC'?'EBA':'EAC';
      commonName=pref==='EBA'?`Belt Conveyor BCN-${num} · EAC-${num}`:`Belt Conveyor BCN-${num}`;
      add(
        `BCN-${num}`,`BCN ${num}`,`BCN${num}`,`BCN-${numBase}`,
        `BC-${num}`,`BC ${num}`,`BC${num}`,`BC-${numBase}`,
        `CONV-${num}`,`CONV ${num}`,`CONV${num}`,
        `${altPref}-${num}`,`${altPref} ${num}`,`${altPref}${num}`,
        `${pref} ${num}`,`${pref}${num}`,`${pref}-${numBase}`,
        `Belt Conveyor ${num}`,`Belt Conveyor-${num}`,`Conveyor ${num}`,`Conveyor-${num}`,`Belt ${num}`,`Coal Conveyor ${num}`,
        `Belt Conveyor ${numBase}`,`Conveyor ${numBase}`,
        'belt conveyor','conveyor belt','coal conveyor','conveyor','belt','EAC','EBA','BCN','BC'
      );
    }
    if(u==='LS-EAC-1'){
      commonName='Limestone Belt Conveyor · BCN-LS-1';
      add('Limestone Conveyor','Limestone Belt Conveyor','LHP Conveyor','BCN-LS-1','LS-BCN-1','LS EAC 1','LSEAC1','belt conveyor','conveyor');
    }

    // 4. Stockyard Drive Houses (UAX-1..4 = DH-1..4) & Tail Pulley Houses (UAX-5..8 = TPH-1..4)
    m=/^UAX-([1-4])$/.exec(u);
    if(m){
      const n=Number(m[1]),convNum=5+2*n;
      commonName=`Drive House DH-${n} (EAC-${convNum})`;
      add(`DH-${n}`,`DH ${n}`,`DH${n}`,`Drive House ${n}`,`Drive House-${n}`,`EAC-${convNum} Drive House`,`BCN-${convNum} Drive House`,`UAX ${n}`,`UAX${n}`,'drive house','DH','UAX');
    }
    m=/^UAX-([5-8])$/.exec(u);
    if(m){
      const uNum=Number(m[1]),tphNum=uNum-4,convNum=6+2*tphNum;
      commonName=`Tail Pulley House TPH-${tphNum} (EBA-${convNum})`;
      add(`TPH-${tphNum}`,`TPH ${tphNum}`,`TPH${tphNum}`,`Tail Pulley House ${tphNum}`,`Tail Pulley House-${tphNum}`,`Tail House ${tphNum}`,`EBA-${convNum} Tail House`,`EAC-${convNum} Tail House`,`UAX ${uNum}`,`UAX${uNum}`,'tail pulley house','tail house','TPH','UAX');
      if(uNum===5)add('DH-5','DH 5','DH5','Drive House 5');
    }

    // 5. Stockpile Sheds (UEB-1..4), Stockpiles (EAE-1..4), & Yards (Coal Yard 1..4)
    m=/^UEB-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Stockpile Cover Shed ${n}`;
      add(`Stockpile Shed ${n}`,`Cover Shed ${n}`,`Coal Shed ${n}`,`Storage Shed ${n}`,`Yard ${n} Shed`,`Shed ${n}`,`CS-${n}`,`UEB ${n}`,`UEB${n}`,'stockpile shed','cover shed','coal shed','UEB');
    }
    m=/^EAE-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Coal Stockpile ${n}`;
      add(`Coal Stockpile ${n}`,`Stockpile ${n}`,`Stockpile-${n}`,`Coal Pile ${n}`,`Pile ${n}`,`Yard ${n} Stockpile`,`EAE ${n}`,`EAE${n}`,'stockpile','coal pile','EAE');
    }
    m=/^COAL YARD ([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Stockyard Branch ${n} (EAE-${n})`;
      add(`Yard ${n}`,`Yard-${n}`,`Stockyard ${n}`,`Coal Stockyard ${n}`,`CY-${n}`,`EAE-${n}`,'stockyard','coal yard');
    }

    // 6. Stackers (EAD-1..4), Portal Reclaimers (EAF-1..4), & Ship Unloaders (Coal Ship Unloader-1..3)
    m=/^EAD-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Coal Stacker ${n} · STK-${n}`;
      add(`Stacker ${n}`,`Stacker-${n}`,`Coal Stacker ${n}`,`Coal Stacker-${n}`,`STK-${n}`,`STK ${n}`,`STK${n}`,`EAD ${n}`,`EAD${n}`,'stacker','coal stacker','EAD','STK');
    }
    m=/^EAF-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Portal Scraper Reclaimer ${n} · PSR-${n}`;
      add(`Reclaimer ${n}`,`Reclaimer-${n}`,`Portal Reclaimer ${n}`,`Portal Scraper Reclaimer ${n}`,`Scraper Reclaimer ${n}`,`PSR-${n}`,`PSR ${n}`,`PSR${n}`,`REC-${n}`,`PR-${n}`,`EAF ${n}`,`EAF${n}`,'reclaimer','portal reclaimer','scraper reclaimer','EAF','PSR');
    }
    m=/^COAL SHIP UNLOADER-([123])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`SUL-${n} · Grab Ship Unloader ${n}`;
      add(`SUL-${n}`,`SUL ${n}`,`SUL${n}`,`SU-${n}`,`SU ${n}`,`SU${n}`,`Ship Unloader ${n}`,`Ship Unloader-${n}`,`Unloader ${n}`,`Grab Unloader ${n}`,'ship unloader','unloader','SUL','SU');
    }

    // 7. Blending Silos (EBB-1..2), Silo Extractors (EBE-CES-1..2), & Belt Feeders (KF-1..4)
    m=/^EBB-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Coal Blending Silo ${n} (at UEE-2 / CBSH)`;
      add(`Coal Silo ${n}`,`Coal Silo-${n}`,`Blending Silo ${n}`,`Blending Silo-${n}`,`Silo ${n}`,`Silo-${n}`,`BS-${n}`,`CBSH Silo ${n}`,`UEE-2 Silo ${n}`,`EBB ${n}`,`EBB${n}`,'silo','coal silo','blending silo','EBB');
    }
    m=/^EBE-CES-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Rotary Silo Extractor RE-${n} (below EBB-${n})`;
      add(`RE-${n}`,`RE ${n}`,`RE${n}`,`CES-${n}`,`CES ${n}`,`CES${n}`,`Rotary Extractor ${n}`,`Silo Extractor ${n}`,`Coal Silo Extractor ${n}`,`Rotary Plow Extractor ${n}`,`Extractor ${n}`,`EBE-${n}`,`EBE ${n}`,'silo extractor','rotary extractor','RE','CES');
    }
    m=/^KF-([1-4])$/.exec(u);
    if(m){
      const n=Number(m[1]);
      commonName=n<=2?`Belt Feeder ${n} (at UEE-3 / CRH)`:`Belt Feeder ${n} (BF-${n-2} at UEE-2 / CBSH)`;
      add(`Belt Feeder ${n}`,`Belt Feeder-${n}`,`BF-${n}`,`BF ${n}`,`BF${n}`,`Feeder ${n}`,`KF ${n}`,`KF${n}`,'belt feeder','feeder','KF','BF');
      if(n<=2)add(`Crusher House Belt Feeder ${n}`,`CRH Belt Feeder ${n}`,`UEE-3 Belt Feeder ${n}`);
      else add(`CBSH Belt Feeder ${n-2}`,`Belt Feeder ${n-2} at CBSH`,`Silo Belt Feeder ${n}`,`UEE-2 Belt Feeder ${n}`);
    }

    // 8. Ring Granulator Crushers (EBC-1..2) & Screens (EBD-1..6)
    m=/^EBC-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Ring Granulator Crusher ${n} · CR-${n} (at UEE-3 / CRH)`;
      add(`Crusher ${n}`,`Crusher-${n}`,`Coal Crusher ${n}`,`Ring Granulator ${n}`,`Ring Granulator Crusher ${n}`,`Granulator ${n}`,`CR-${n}`,`CR ${n}`,`CR${n}`,`RGC-${n}`,`CRH Crusher ${n}`,`UEE-3 Crusher ${n}`,`EBC ${n}`,`EBC${n}`,'crusher','ring granulator','coal crusher','EBC','CR');
    }
    m=/^EBD-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Primary Grizzly Roller Screen ${n} (at UEE-1 / PSH)`;
      add(`Primary Screen ${n}`,`Roller Screen ${n}`,`Vibration Grizzly Screen ${n}`,`Vibrating Grizzly Screen ${n}`,`Grizzly Screen ${n}`,`Screen ${n}`,`PSH Screen ${n}`,`UEE-1 Screen ${n}`,`VGS-${n}`,`RS-${n}`,`EBD ${n}`,`EBD${n}`,'primary screen','roller screen','grizzly screen','screen','EBD');
    }
    m=/^EBD-([56])$/.exec(u);
    if(m){
      const n=Number(m[1]),sec=n-4;
      commonName=`Secondary Grizzly Screen ${sec} · EBD-${n} (at UEE-3 / CRH)`;
      add(`Secondary Screen ${sec}`,`Secondary Screen ${n}`,`Crusher Screen ${sec}`,`Vibrating Grizzly Feeder ${sec}`,`Grizzly Screen ${n}`,`Screen ${n}`,`CRH Screen ${sec}`,`UEE-3 Screen ${sec}`,`VGF-${sec}`,`EBD ${n}`,`EBD${n}`,'secondary screen','crusher screen','grizzly screen','screen','EBD');
    }

    // 9. Gates & Trippers (FG-1..22, KB-FD-1..8, KB-RG-1..4, KB-RPG-1..4, FTR-1..4, TT-1..4)
    m=/^FG-(\d+[AB]?)$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Two-Way Flap Diverter Gate ${n}`;
      add(`Flap Gate ${n}`,`Flap Gate-${n}`,`Diverter Gate ${n}`,`Two-Way Flap Gate ${n}`,`FG ${n}`,`FG${n}`,'flap gate','diverter gate','FG');
    }
    m=/^KB-FD-([1-8])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Flow Divider Gate FD-${n}`;
      add(`FD-${n}`,`FD ${n}`,`FD${n}`,`Flow Divider ${n}`,`Flow Divider-${n}`,`Flow Divider Gate ${n}`,`KB-FD ${n}`,`KBFD${n}`,'flow divider','diverter gate','FD','KB-FD');
    }
    m=/^KB-RG-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Manual Rod Gate RG-${n} (at UEE-1 / PSH)`;
      add(`RG-${n}`,`RG ${n}`,`RG${n}`,`Rod Gate ${n}`,`Rod Gate-${n}`,`Manual Rod Gate ${n}`,`PSH Rod Gate ${n}`,`KBRG${n}`,'rod gate','RG','KB-RG');
    }
    m=/^KB-RPG-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Rack & Pinion Bypass Gate RPG-${n} (at UEE-1 / PSH)`;
      add(`RPG-${n}`,`RPG ${n}`,`RPG${n}`,`Rack and Pinion Gate ${n}`,`R&P Gate ${n}`,`RP Gate ${n}`,`Pinion Gate ${n}`,`Bypass Gate ${n}`,`PSH Bypass Gate ${n}`,`KBRPG${n}`,'rack and pinion gate','bypass gate','RPG','KB-RPG');
    }
    m=/^FTR-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Fixed Tripper ${n}`;
      add(`Fixed Tripper ${n}`,`Fixed Tripper-${n}`,`FT-${n}`,`FT ${n}`,`FT${n}`,`FTR ${n}`,`FTR${n}`,'fixed tripper','tripper','FTR','FT');
    }
    m=/^TT-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Travelling Bunker Tripper ${n}`;
      add(`Travelling Tripper ${n}`,`Traveling Tripper ${n}`,`Bunker Tripper ${n}`,`Motorized Tripper ${n}`,`Tripper ${n}`,`TT ${n}`,`TT${n}`,'travelling tripper','bunker tripper','tripper','TT');
    }

    // 10. Samplers, Analyzers, Weighers, Metal Detectors, & Magnetic Separators
    if(u==='UEF-3 COAL SAMPLING SYSTEM'){
      commonName='EAU-1 · CSU-1 · TP-3 Coal Sampling System';
      add('EAU-1','EAU 1','EAU1','CSU-1','CSU 1','CSU1','Coal Sampling Unit 1','Coal Sampler 1','As-Received Coal Sampler','TP-3 Coal Sampling System','TP-3 Sampler','UEF-3 Sampler','coal sampler','sampling system','EAU','CSU');
    }
    if(u==='UEF-13 COAL SAMPLING SYSTEM'){
      commonName='EAU-2 · CSU-2 · TP-13 Coal Sampling System';
      add('EAU-2','EAU 2','EAU2','CSU-2','CSU 2','CSU2','Coal Sampling Unit 2','Coal Sampler 2','As-Fired Coal Sampler','Bunker Coal Sampler','TP-13 Coal Sampling System','TP-13 Sampler','UEF-13 Sampler','coal sampler','sampling system','EAU','CSU');
    }
    m=/^CV-([1-6])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Online Coal Analyzer ${n} · OCA-${n}`;
      add(`Coal Analyser ${n}`,`Coal Analyzer ${n}`,`Online Coal Analyzer ${n}`,`OCA-${n}`,`CA-${n}`,`CV ${n}`,`CV${n}`,'coal analyzer','coal analyser','CV','OCA');
    }
    m=/^EAT-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Belt Weigher Scale ${n} · BW-${n}`;
      add(`Belt Weigher ${n}`,`Belt Scale ${n}`,`Conveyor Weigher ${n}`,`Weigh Scale ${n}`,`BW-${n}`,`BWS-${n}`,`EAT ${n}`,`EAT${n}`,'belt weigher','belt scale','weigher','EAT','BW');
    }
    m=/^QB-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Metal Detector MD-${n}`;
      add(`MD-${n}`,`MD ${n}`,`MD${n}`,`Metal Detector ${n}`,`Tramp Metal Detector ${n}`,`QB ${n}`,`QB${n}`,'metal detector','QB','MD');
    }
    m=/^AT-([1-4])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Inline Magnetic Separator ILMS-${n}`;
      add(`ILMS-${n}`,`ILMS ${n}`,`ILMS${n}`,`Inline Magnetic Separator ${n}`,`Magnetic Separator ${n}`,`Cross Belt Magnetic Separator ${n}`,`Suspended Magnet ${n}`,`Electromagnet ${n}`,`MS-${n}`,`CBMS-${n}`,`AT ${n}`,`AT${n}`,'magnetic separator','inline magnetic separator','ILMS','AT');
    }
    m=/^ILMS-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Inline Magnetic Separator ${n} · AT-${n}`;
      add(`Inline Magnetic Separator ${n}`,`Magnetic Separator ${n}`,`Cross Belt Magnetic Separator ${n}`,`AT-${n}`,`ILMS ${n}`,`ILMS${n}`,'magnetic separator','ILMS');
    }

    // 11. Boiler Bunkers & Bunker Bays
    m=/^UNIT-([12]) COAL BUNKER BAY$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Unit-${n} Boiler Bunker House · BH-${n}`;
      add(`Bunker House ${n}`,`Bunker Bay ${n}`,`BH-${n}`,`BH ${n}`,`Unit ${n} Bunker House`,`Unit ${n} Bunker Bay`,`Boiler Bunker House ${n}`,`Mill Bunker Bay ${n}`,'bunker house','bunker bay','BH');
    }
    m=/^BUNKER-([A-F]) OF UNIT-([12])$/.exec(u);
    if(m){
      const let_=m[1],uNum=m[2];
      commonName=`Unit-${uNum} Mill Bunker ${uNum}${let_}`;
      add(`Bunker ${uNum}${let_}`,`Bunker-${uNum}${let_}`,`Bunker ${let_}`,`Unit ${uNum} Bunker ${let_}`,`Mill Bunker ${uNum}${let_}`,`Coal Bunker ${uNum}${let_}`,'coal bunker','mill bunker','bunker');
    }

    // 12. MCC Buildings, Pump Houses, Elevators, Dust & Water Systems
    m=/^CHP MCC-([1-4]) BUILDING$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`UBA-${n} · MCC-${n} Switchgear Building`;
      add(`UBA-${n}`,`UBA ${n}`,`UBA${n}`,`MCC-${n}`,`MCC ${n}`,`MCC${n}`,`MCC Building ${n}`,`MCC Room ${n}`,`Electrical Building ${n}`,'MCC building','MCC room','UBA','MCC');
    }
    m=/^DS PUMP HOUSE-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`UGA-${n} · Dust Suppression Pump House ${n}`;
      add(`UGA-${n}`,`UGA ${n}`,`UGA${n}`,`DSPH-${n}`,`DSPH ${n}`,`Dust Suppression Pump House ${n}`,`Pump House ${n}`,'pump house','UGA','DSPH');
    }
    m=/^DE-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Crusher House Dust Extraction Stream ${n} (at UEE-3 / CRH)`;
      add(`Dust Extraction System ${n}`,`DES-${n}`,`Bag Filter System ${n}`,`Crusher House DE-${n}`,`CRH DE-${n}`,`UEE-3 DE-${n}`,'dust extraction','bag filter','DE','DES');
    }
    m=/^DFDS SYSTEM-([12])$/.exec(u);
    if(m){
      const n=m[1];
      commonName=`Dry Fog Dust Suppression System ${n}`;
      add(`DFDS-${n}`,`DFDS ${n}`,`Dry Fog Dust Suppression ${n}`,`Dry Fog System ${n}`,'dry fog','dust suppression','DFDS');
    }
    if(u==='SNC-2'||u==='TRANSFER POINT TP-13 PASSENGER AND GOODS ELEVATOR'){
      commonName='TP-13 / UEF-13 Goods & Passenger Elevator (SNC-2)';
      add('SNC-2','SNC 2','SNC2','TP-13 Elevator','UEF-13 Elevator','Transfer Tower Elevator','Lift 2','Elevator 2','goods elevator','passenger elevator','lift');
    }
    if(u==='CRUSHER HOUSE PASSENGER AND GOODS ELEVATOR'){
      commonName='CRH / UEE-3 Goods & Passenger Elevator (SNC-1)';
      add('SNC-1','SNC 1','SNC1','CRH Elevator','UEE-3 Elevator','Crusher House Elevator','Crusher House Lift','Lift 1','Elevator 1');
    }

    // 13. Prefix-based alias expansion for sub-assemblies & child components
    const prefixRules=[
      [/\bUEF-(\d+)\b/i, (_,n)=>[`TP-${n}`,`TP ${n}`,`Transfer Point ${n}`,`Transfer House ${n}`,`TH-${n}`]],
      [/\bTP-(\d+)\b/i, (_,n)=>[`UEF-${n}`,`UEF ${n}`,`Transfer Point ${n}`]],
      [/\bUEE-1\b/i, ()=>['PSH','Primary Screening House','Primary Screen House']],
      [/\bUEE-2\b/i, ()=>['CBSH','Coal Blending Silo House','Silo House']],
      [/\bUEE-3\b/i, ()=>['CRH','Crusher House']],
      [/\bEAC-(\d+[AB]?)\b/i, (_,n)=>[`BCN-${n}`,`BC-${n}`,`Conveyor ${n}`,`Belt ${n}`]],
      [/\bEBA-(\d+[AB]?)\b/i, (_,n)=>[`BCN-${n}`,`BC-${n}`,`EAC-${n}`,`Conveyor ${n}`,`Belt ${n}`]],
      [/\bEAD-(\d+)\b/i, (_,n)=>[`Stacker ${n}`,`Coal Stacker ${n}`,`STK-${n}`]],
      [/\bEAE-(\d+)\b/i, (_,n)=>[`Stockpile ${n}`,`Coal Stockpile ${n}`]],
      [/\bEAF-(\d+)\b/i, (_,n)=>[`Reclaimer ${n}`,`Portal Reclaimer ${n}`,`PSR-${n}`]],
      [/\bSUL-(\d+)\b/i, (_,n)=>[`Coal Ship Unloader-${n}`,`Ship Unloader ${n}`,`SU-${n}`,`Unloader ${n}`]],
      [/\bEAU-1\b/i, ()=>['CSU-1','UEF-3 Coal Sampling System','TP-3 Sampler','Coal Sampler 1']],
      [/\bEAU-2\b/i, ()=>['CSU-2','UEF-13 Coal Sampling System','TP-13 Sampler','Coal Sampler 2']],
      [/\bEBB-([12])\b/i, (_,n)=>[`Coal Silo ${n}`,`Blending Silo ${n}`,`Silo ${n}`,'CBSH','UEE-2']],
      [/\bEBE-CES-([12])\b/i, (_,n)=>[`RE-${n}`,`Rotary Extractor ${n}`,`Silo Extractor ${n}`,'CBSH','UEE-2']],
      [/\bEBC-([12])\b/i, (_,n)=>[`Crusher ${n}`,`Ring Granulator ${n}`,`CR-${n}`,'CRH','UEE-3']],
      [/\bEBD-([1-4])\b/i, (_,n)=>[`Primary Screen ${n}`,`Roller Screen ${n}`,`Grizzly Screen ${n}`,'PSH','UEE-1']],
      [/\bEBD-([56])\b/i, (_,n)=>[`Secondary Screen ${Number(n)-4}`,`Crusher Screen ${n}`,'CRH','UEE-3']]
    ];
    for(const [rx,fn] of prefixRules){
      const match=rx.exec(lbl);
      if(match){
        for(const syn of fn(...match)){
          add(syn);
          if(lbl.toUpperCase()!==match[0].toUpperCase()){
            add(lbl.replace(rx,syn));
          }
        }
      }
    }

    // Class-based generic terms so searching "belt", "conveyor", "pulley", "PCS", "BSS", "ZSS" etc. always works
    if(classes.includes('belt_conveyor')||classes.includes('conveyor_belt')||classes.includes('conveyor_belting')){
      add('belt','conveyor','belt conveyor','conveyor belt','BCN','EAC');
    }
    if(classes.includes('pull_cord_switch')||/\bpull[- ]?cord\b/i.test(lbl))add('PCS','pull cord switch','emergency pull cord');
    if(classes.includes('belt_sway_switch')||/\bbelt[- ]?sway\b/i.test(lbl))add('BSS','belt sway switch','misalignment switch');
    if(classes.includes('zero_speed_switch')||/\bzero[- ]?speed\b/i.test(lbl))add('ZSS','zero speed switch','speed switch');

    return {ownAliases:[...own],commonName};
  }

  const SEARCH_SYNONYMS={
    sampler:['sampler','sampling','eau-1','eau-2','csu-1','csu-2'],
    sampling:['sampling','sampler','eau-1','eau-2','csu-1','csu-2'],
    csu:['csu','eau-1','eau-2','coal sampling'],
    eau:['eau','eau-1','eau-2','coal sampling'],
    unloader:['unloader','sul','ship unloader','su-1','su-2','su-3'],
    sul:['sul','ship unloader','unloader'],
    stacker:['stacker','ead','stk'],
    stk:['stk','ead','stacker'],
    reclaimer:['reclaimer','eaf','bridge scraper','portal reclaimer','psr'],
    psr:['psr','eaf','portal reclaimer','reclaimer'],
    crusher:['crusher','ebc','uee-3','crh','granulator','ring granulator'],
    crh:['crh','uee-3','crusher house','ebc-1','ebc-2'],
    psh:['psh','uee-1','primary screening house','primary screen house','ebd-1','ebd-2','ebd-3','ebd-4'],
    cbsh:['cbsh','uee-2','coal blending silo house','blending silo','ebb-1','ebb-2','ebe-ces-1','ebe-ces-2'],
    silo:['silo','ebb','uee-2','cbsh','blending'],
    bunker:['bunker','tt-1','tt-2','tt-3','tt-4','bh-1','bh-2'],
    screen:['screen','screenhouse','ebd','uee-1','psh'],
    screenhouse:['screenhouse','psh','uee-1','primary screening house'],
    extractor:['extractor','ebe-ces','re-1','re-2','rotary extractor','silo extractor'],
    tripper:['tripper','ftr','tt-1','tt-2','tt-3','tt-4'],
    weigher:['weigher','belt scale','eat-1','eat-2','eat-3','eat-4','bw-1','bw-2','bw-3','bw-4'],
    scale:['scale','belt scale','belt weigher','eat-1','eat-2','eat-3','eat-4'],
    detector:['detector','metal detector','qb-1','qb-2','qb-3','qb-4','md-1','md-2','md-3','md-4'],
    separator:['separator','magnetic','at-1','at-2','at-3','at-4','ilms-1','ilms-2'],
    ilms:['ilms','at-1','at-2','at-3','at-4','magnetic separator'],
    conveyor:['conveyor','belt_conveyor','eac','eba','bcn'],
    belt:['belt','belt_conveyor','conveyor_belt','eac','eba','bcn','belt_feeder'],
    bcn:['bcn','belt_conveyor','eac','eba','conveyor'],
    eac:['eac','belt_conveyor','eba','bcn'],
    eba:['eba','belt_conveyor','eac','bcn'],
    tp:['tp','transfer_point','uef'],
    uef:['uef','transfer_point','tp'],
    th:['th','transfer_point','uef','transfer house'],
    dh:['dh','uax-1','uax-2','uax-3','uax-4','uax-5','drive house'],
    tph:['tph','uax-5','uax-6','uax-7','uax-8','tail pulley house'],
    uax:['uax','drive house','tail pulley house','dh-1','dh-2','dh-3','dh-4','tph-1','tph-2','tph-3','tph-4'],
    ueb:['ueb','stockpile shed','cover shed','coal shed'],
    uba:['uba','mcc-1','mcc-2','mcc-3','mcc-4','mcc building'],
    uga:['uga','ds pump house','pump house','dsph'],
    cctv:['cctv','camera','video','monitoring'],
    camera:['camera','cctv','video','monitoring'],
    pcs:['pcs','pull cord','pull-cord'],
    bss:['bss','belt sway','belt-sway'],
    zss:['zss','zero speed','zero-speed'],
    elevator:['elevator','lift','snc-1','snc-2'],
    lift:['lift','elevator','snc-1','snc-2']
  };

  function normCompact(s){return String(s||'').toLowerCase().replace(/[^a-z0-9]/g,'');}
  function escapeRx(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}

  // Normalize query shorthands (e.g. "TP 5", "TP-5", "TP5" -> "uef-5"; "UEE 1" -> "uee-1"; "BCN 18A" -> "eba-18a")
  function normalizeUserQuery(rawQ){
    let q=String(rawQ||'').trim().toLowerCase();
    q=q
      .replace(/\b(?:tp|th|transfer\s*(?:point|house|tower))\s*[-#]?\s*0*([1-9]|1[0-5])\b/gi,'uef-$1')
      .replace(/\b(?:tp|th|transfer\s*(?:point|house|tower))\s*[-#]?\s*0*(1[678])\b/gi,'tp-$1')
      .replace(/\buef\s*[-#]?\s*0*(1[678])\b/gi,'tp-$1')
      .replace(/\buef\s*[-#]?\s*0*([1-9]|1[0-5])\b/gi,'uef-$1')
      .replace(/\buee\s*[-#]?\s*0*1\b/gi,'uee-1')
      .replace(/\b(?:primary\s+screen(?:ing)?\s+house|psh)\b/gi,'uee-1')
      .replace(/\buee\s*[-#]?\s*0*2\b/gi,'uee-2')
      .replace(/\b(?:coal\s+blending\s+silo\s+house|blending\s+silo\s+house|silo\s+house|cbsh)\b/gi,'uee-2')
      .replace(/\buee\s*[-#]?\s*0*3\b/gi,'uee-3')
      .replace(/\b(?:crusher\s+house|crushing\s+house|crh)\b/gi,'uee-3')
      .replace(/\b(?:dh|drive\s+house)\s*[-#]?\s*0*([1-4])\b/gi,'uax-$1')
      .replace(/\b(?:dh|drive\s+house)\s*[-#]?\s*0*5\b/gi,'uax-5')
      .replace(/\b(?:tph|tail\s*(?:pulley\s*)?house)\s*[-#]?\s*0*([1-4])\b/gi,(_,n)=>'uax-'+(Number(n)+4))
      .replace(/\b(?:bcn|bc|conv|conveyor|belt\s+conveyor)\s*[-#]?\s*0*(1[0-9]|[1-9])\s*([ab])?\b/gi,(_,n,l)=>`bcn-${n}${l||''}`)
      .replace(/\bbunker\s*[-#]?\s*([12])\s*([a-f])\b/gi,'bunker-$2 unit-$1')
      .replace(/\bbunker\s*[-#]?\s*[3-9]\s*([a-f])\b/gi,'bunker-$1')
      .replace(/\b(?:ship\s+)?unloader\s*[-#]?\s*0*([123])\b/gi,'sul-$1')
      .replace(/\b(?:sul|su)\s*[-#]?\s*0*([123])\b/gi,'sul-$1')
      .replace(/\b(?:stacker|stk)\s*[-#]?\s*0*([1-4])\b/gi,'ead-$1')
      .replace(/\b(?:reclaimer|portal\s+reclaimer|psr)\s*[-#]?\s*0*([1-4])\b/gi,'eaf-$1')
      .replace(/\b(?:stockpile|pile)\s*[-#]?\s*0*([1-4])\b/gi,'eae-$1')
      .replace(/\b(?:shed|cover\s+shed|stockpile\s+shed)\s*[-#]?\s*0*([1-4])\b/gi,'ueb-$1')
      .replace(/\b(?:silo|blending\s+silo|coal\s+silo)\s*[-#]?\s*0*([12])\b/gi,'ebb-$1')
      .replace(/\b(?:rotary\s+extractor|silo\s+extractor|re|ces)\s*[-#]?\s*0*([12])\b/gi,'ebe-ces-$1')
      .replace(/\b(?:crusher|ring\s+granulator|cr|rgc)\s*[-#]?\s*0*([12])\b/gi,'ebc-$1')
      .replace(/\b(?:belt\s+feeder|bf|kf)\s*[-#]?\s*0*([1-4])\b/gi,'kf-$1')
      .replace(/\b(?:flow\s+divider|fd)\s*[-#]?\s*0*([1-8])\b/gi,'kb-fd-$1')
      .replace(/\b(?:rod\s+gate|rg)\s*[-#]?\s*0*([1-4])\b/gi,'kb-rg-$1')
      .replace(/\b(?:rack\s*(?:and|&)\s*pinion\s*gate|r&p\s*gate|rp\s*gate|rpg)\s*[-#]?\s*0*([1-4])\b/gi,'kb-rpg-$1')
      .replace(/\b(?:flap\s+gate|fg)\s*[-#]?\s*0*(\d+[ab]?)\b/gi,'fg-$1')
      .replace(/\b(?:fixed\s+tripper|ftr|ft)\s*[-#]?\s*0*([1-4])\b/gi,'ftr-$1')
      .replace(/\b(?:travell?ing\s+tripper|bunker\s+tripper|tt)\s*[-#]?\s*0*([1-4])\b/gi,'tt-$1')
      .replace(/\b(?:belt\s+weigher|belt\s+scale|bw)\s*[-#]?\s*0*([1-4])\b/gi,'eat-$1')
      .replace(/\b(?:metal\s+detector|md|qb)\s*[-#]?\s*0*([1-4])\b/gi,'qb-$1')
      .replace(/\b(?:magnetic\s+separator|ilms)\s*[-#]?\s*0*([1-4])\b/gi,'at-$1')
      .replace(/\b(?:coal\s+analy[sz]er|oca)\s*[-#]?\s*0*([1-6])\b/gi,'cv-$1')
      .replace(/\b(?:coal\s+sampling\s+(?:unit|system)|csu|eau)\s*[-#]?\s*0*([12])\b/gi,'eau-$1')
      .replace(/\b(?:mcc\s+(?:building|room)|uba)\s*[-#]?\s*0*([1-4])\b/gi,'uba-$1')
      .replace(/\b(?:ds\s+pump\s+house|pump\s+house|uga|dsph)\s*[-#]?\s*0*([12])\b/gi,'uga-$1');
    return q;
  }

  function tokenMatchesHaystack(token,hayRaw,hayCompact){
    const t=token.toLowerCase();
    const tCompact=normCompact(t);
    if(!tCompact)return true;
    // If token starts with a digit (e.g. "5a", "2", "18a"), enforce non-digit boundary before it so "5a" does NOT match "15a"
    if(/^\d/.test(t)){
      const rx=new RegExp(`(?:^|[^0-9])${escapeRx(t)}(?![0-9])`,'i');
      if(rx.test(hayRaw))return true;
      const rxCompact=new RegExp(`(?:^|[a-z])${escapeRx(tCompact)}(?![0-9])`,'i');
      return rxCompact.test(hayCompact);
    }
    // Check tag-number tokens like "uef-5", "bcn-18a", "eac-5a", "uax-1" so "uef-1" does NOT match "uef-10" or "uef-13"
    const tagMatch=/^([a-z]+(?:-[a-z]+)*)-(\d+[a-z]?)$/.exec(t);
    if(tagMatch){
      const prefix=tagMatch[1],num=tagMatch[2];
      const tagRx=new RegExp(`(?:^|[^a-z0-9])${escapeRx(prefix)}[-_\\s]*0*${escapeRx(num)}(?![0-9a-z])`,'i');
      if(tagRx.test(hayRaw))return true;
      const compactRx=new RegExp(`(?:^|[^a-z0-9])${escapeRx(normCompact(prefix))}0*${escapeRx(num)}(?![0-9a-z])`,'i');
      return compactRx.test(hayCompact);
    }
    const syns=SEARCH_SYNONYMS[t]||[t];
    for(const syn of syns){
      if(hayRaw.includes(syn))return true;
      const sc=normCompact(syn);
      if(sc&&sc.length>=2&&hayCompact.includes(sc)){
        const m=/^([a-z]+)(\d+[a-z]?)$/.exec(sc);
        if(m){
          const tagRx=new RegExp(`(?:^|[^a-z0-9])${escapeRx(m[1])}[-_\\s]*0*${escapeRx(m[2])}(?![0-9a-z])`,'i');
          if(tagRx.test(hayRaw))return true;
        }else{
          return true;
        }
      }
    }
    return false;
  }

  function searchEntities(p,query){
    const rawQ=String(query||'').trim();
    if(!rawQ)return [];
    const qLower=rawQ.toLowerCase();
    const qCompact=normCompact(rawQ);
    const normQ=normalizeUserQuery(rawQ);
    const normQCompact=normCompact(normQ);
    const words=normQ.split(/\s+/).filter(Boolean);
    if(!words.length)return [];

    const scored=[];
    for(const e of p.entities.values()){
      const ownNames=[e.label,...(e.aliases||[]),...(p.searchAliases?.get(e.id)||[])];
      const locNames=p.locationAliases?.get(e.id)||[];
      const classes=(p.classes.get(e.id)||[]).flatMap(c=>[c,pretty(c)]);
      const ownHayRaw=[...ownNames,...classes].join(' ').toLowerCase();
      const ownHayCompact=ownNames.map(normCompact).join(' ');
      const fullHayRaw=[ownHayRaw,...locNames.map(s=>s.toLowerCase())].join(' ');
      const fullHayCompact=[ownHayCompact,...locNames.map(normCompact)].join(' ');

      const matchesOwn=words.every(w=>tokenMatchesHaystack(w,ownHayRaw,ownHayCompact));
      const matchesWithLoc=!matchesOwn&&words.every(w=>tokenMatchesHaystack(w,fullHayRaw,fullHayCompact));
      const directCompactMatch=qCompact.length>=2&&ownNames.some(n=>{
        const nc=normCompact(n);
        if(nc===qCompact||nc===normQCompact)return true;
        if((qCompact.length>=3&&nc.startsWith(qCompact)&&!/^\d/.test(nc.slice(qCompact.length)))||
           (normQCompact.length>=3&&nc.startsWith(normQCompact)&&!/^\d/.test(nc.slice(normQCompact.length))))return true;
        return n.toLowerCase().split(/[\s()/·,]+/).some(tok=>{
          const tc=normCompact(tok);
          return tc===qCompact||tc===normQCompact;
        });
      });

      if(!matchesOwn&&!matchesWithLoc&&!directCompactMatch)continue;

      const isRef=p.refs.has(e.id);
      const isPrimary=isPrimaryEquipment(p,e.id);
      const canonicalExact=[e.label,...(e.aliases||[])].some(n=>{
        const nl=n.toLowerCase(),nc=normCompact(n);
        return nl===qLower||nl===normQ||nc===qCompact||nc===normQCompact;
      });
      const aliasExact=!canonicalExact&&(p.searchAliases?.get(e.id)||[]).some(n=>{
        const nl=n.toLowerCase(),nc=normCompact(n);
        return nl===qLower||nl===normQ||nc===qCompact||nc===normQCompact;
      });
      const exactName=canonicalExact||aliasExact;
      const prefixName=ownNames.some(n=>{
        const nl=n.toLowerCase(),nc=normCompact(n);
        return nl.startsWith(qLower)||nl.startsWith(normQ)||
          (qCompact.length>=3&&nc.startsWith(qCompact)&&!/^\d/.test(nc.slice(qCompact.length)))||
          (normQCompact.length>=3&&nc.startsWith(normQCompact)&&!/^\d/.test(nc.slice(normQCompact.length)));
      });
      const wordTokenExact=ownNames.some(n=>n.toLowerCase().split(/[\s()/·,]+/).some(tok=>{
        const tc=normCompact(tok);
        return tok===qLower||tok===normQ||tc===qCompact||tc===normQCompact;
      }));

      let tier=isRef?4:(isPrimary?2:3);
      if(exactName&&!isRef)tier=1;
      let score=(5-tier)*1000;
      if(canonicalExact)score+=3500;
      else if(aliasExact)score+=2800;
      else if(matchesOwn&&wordTokenExact)score+=1100;
      else if(matchesOwn&&prefixName)score+=600;
      else if(matchesWithLoc)score-=350; // Location/building children appear right after the building itself!
      if(isPrimary)score+=400;
      if(p.memberships?.has(e.id))score+=220;
      if(!isRef)score+=150;
      if(!isPrimary)score-=Math.min(60,e.label.length);
      scored.push({entity:e,tier,isPrimary,isRef,score});
    }
    scored.sort((a,b)=>b.score-a.score||a.entity.label.localeCompare(b.entity.label,undefined,{numeric:true}));
    return scored.map(x=>x.entity);
  }

  function commonName(p,id){
    return p?.commonNames?.get(id)||'';
  }


  function enrichSubcomponentModel(model){
    return model;
  }

  function build(model,{at=Date.now()}={}){
    enrichSubcomponentModel(model);
    const entities=new Map((model.entities||[]).filter(e=>e.id===e.canonical_id&&!e.inactive).map(e=>[e.id,e]));
    const facts=(model.assertions||[]).filter(a=>!a.retirement&&!a.suppressed&&entities.has(a.canonical_subject)&&(!a.canonical_object||entities.has(a.canonical_object)));
    const outgoing=new Map(),incoming=new Map(),children=new Map(),parents=new Map(),classes=new Map(),memberships=new Map();
    const add=(map,key,value)=>{if(!map.has(key))map.set(key,[]);map.get(key).push(value);};
    for(const a of facts){
      add(outgoing,a.canonical_subject,a);if(a.canonical_object)add(incoming,a.canonical_object,a);
      if(a.predicate==='instance_of'&&!(classes.get(a.canonical_subject)||[]).includes(String(a.value)))add(classes,a.canonical_subject,String(a.value));
      if(a.predicate==='part_of'&&a.canonical_object&&current(a,at)){add(children,a.canonical_object,a);add(parents,a.canonical_subject,a);}
    }
    const refs=new Set([...entities.values()].filter(e=>reference(e,classes.get(e.id)||[])).map(e=>e.id));
    for(const e of entities.values()){
      if(refs.has(e.id))continue;
      const groups=new Set([e.label,...(e.aliases||[])].map(stageForLabel).filter(Boolean));
      if(groups.size)memberships.set(e.id,groups);
    }
    // A recorded location or part-of chain may place an item in a browse group.
    // This is not inheritance of specifications or a claim of installation.
    const directlyPlaced=new Set(memberships.keys());
    let changed=true;
    while(changed){
      changed=false;
      for(const a of facts){
        if(!['located_at','part_of'].includes(a.predicate)||!a.canonical_object||!current(a,at)||refs.has(a.canonical_subject)||directlyPlaced.has(a.canonical_subject))continue;
        const target=memberships.get(a.canonical_object);if(!target)continue;
        const own=memberships.get(a.canonical_subject)||new Set();
        for(const id of target)if(!own.has(id)){own.add(id);changed=true;}
        if(own.size)memberships.set(a.canonical_subject,own);
      }
    }

    // Build synthetic search aliases and common names for all entities, plus location/parent search propagation
    const searchAliases=new Map(),commonNames=new Map(),locationAliases=new Map();
    for(const e of entities.values()){
      const {ownAliases,commonName:cn}=deriveOwnAliases(e,classes.get(e.id)||[]);
      searchAliases.set(e.id,ownAliases);
      if(cn)commonNames.set(e.id,cn);
    }
    for(const e of entities.values()){
      if(refs.has(e.id))continue;
      const locSet=new Set();
      const locTargets=[
        ...(parents.get(e.id)||[]).map(a=>a.canonical_object),
        ...(outgoing.get(e.id)||[]).filter(a=>a.predicate==='located_at'&&a.canonical_object&&current(a,at)).map(a=>a.canonical_object)
      ];
      for(const tid of locTargets){
        const te=entities.get(tid);
        if(!te||te.label==='Maitree Coal Handling Plant')continue;
        locSet.add(te.label);
        for(const al of (searchAliases.get(tid)||[])){
          if(al.length<=36)locSet.add(al);
        }
      }
      if(locSet.size){
        locationAliases.set(e.id,[...locSet]);
        if(!commonNames.has(e.id)){
          const firstLoc=locTargets.map(tid=>entities.get(tid)?.label).find(l=>l&&l!=='Maitree Coal Handling Plant');
          if(firstLoc&&!e.label.startsWith(firstLoc)){
            const shortLoc=commonNames.get(locTargets[0])?.split(' · ')[0]||firstLoc;
            commonNames.set(e.id,`at ${firstLoc}${shortLoc!==firstLoc?' ('+shortLoc+')':''}`);
          }
        }
      }
    }

    const networks=facts.filter(a=>a.canonical_object&&a.context?.kind==='connection'&&a.context?.verification==='documented'&&a.origin!=='inferred'&&current(a,at));
    const material=networks.filter(a=>a.context.network==='material');
    const links=new Map();
    for(const a of material){
      const from=memberships.get(a.canonical_subject),to=memberships.get(a.canonical_object);
      // Ambiguous placements must not multiply one physical edge into fake routes.
      if(from?.size!==1||to?.size!==1)continue;
      const f=[...from][0],t=[...to][0];if(f===t)continue;
      const k=f+'>'+t;if(!links.has(k))links.set(k,{id:k,from:f,to:t,facts:[]});links.get(k).facts.push(a);
    }
    const paths=[];
    for(const e of entities.values()){
      const match=/^CHP Operating Path-([1-5])$/.exec(e.label);if(!match)continue;
      const own=outgoing.get(e.id)||[],summary=own.find(a=>a.predicate==='sequence_logic'&&typeof a.value==='string');
      if(summary)paths.push({id:match[1],entity:e,title:pathTitles[match[1]],summary,stages:pathStages[match[1]],facts:own.filter(a=>a.predicate!=='instance_of'&&a.predicate!=='part_of')});
    }
    const stageList=stages.map(s=>({...s,entities:[...entities.values()].filter(e=>memberships.get(e.id)?.has(s.id)).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}))}));
    const applicable=id=>(incoming.get(id)||[]).filter(a=>a.origin!=='inferred'&&current(a,at)&&['control_scheme_applies_to','applies_to_conveyor','calculation_applies_to','calculation_applies_to_equipment','sampling_applies_to_conveyor'].includes(a.predicate));
    const relatedFacts=id=>applicable(id).flatMap(link=>(outgoing.get(link.canonical_subject)||[]).filter(a=>!a.canonical_object&&a.predicate!=='instance_of').map(a=>({fact:a,via:link})));
    const sevOrder={high:0,medium:1,low:2};
    const qualifications=id=>[...(outgoing.get(id)||[]).map(fact=>({fact})),...relatedFacts(id)]
      .filter(({fact:a})=>/^source_(gap|discrepancy)$/.test(a.predicate)||/unresolved|conflict|reconcil|contradict|copy error|uncertain|discrepanc/i.test(String(a.value||'')+' '+(a.context?.condition||'')))
      .map(item=>({...item,severity:qualificationSeverity(item.fact)}))
      .sort((a,b)=>(sevOrder[a.severity]??2)-(sevOrder[b.severity]??2));
    // Only accepted, current containment edges expand an assembly. A shared
    // service or nearby machine must not donate its entire tree to this one.
    const assemblyCache=new Map();
    const assembly=id=>{
      if(!entities.has(id))return [];
      if(assemblyCache.has(id))return assemblyCache.get(id);
      const seen=new Set([id]),result=[],queue=[{id,depth:0,parent:null}];
      for(let i=0;i<queue.length;i++){
        const item=queue[i];result.push({...item,entity:entities.get(item.id),facts:outgoing.get(item.id)||[]});
        for(const edge of children.get(item.id)||[]){
          const child=edge.canonical_subject;if(seen.has(child))continue;
          seen.add(child);queue.push({id:child,depth:item.depth+1,parent:item.id});
        }
      }
      result._ids=seen;
      assemblyCache.set(id,result);
      return result;
    };
    const designCandidates=id=>[...entities.values()].filter(e=>e.id!==id&&!refs.has(e.id)&&!memberships.has(e.id)&&(classes.get(e.id)||[]).some(c=>(classes.get(id)||[]).includes(c))&&((children.get(e.id)||[]).length||(outgoing.get(e.id)||[]).length>10)).slice(0,6);
    const assemblyBoundary=id=>{
      const ids=new Set(assembly(id).map(item=>item.id));
      return facts.filter(a=>a.canonical_object&&current(a,at)&&
        (ids.has(a.canonical_subject)!==ids.has(a.canonical_object))&&
        (networks.includes(a)||['serves','serves_equipment','supplies_water_to','utility_supply_to','associated_with'].includes(a.predicate)));
    };
    return {version:model.version,entities,facts,outgoing,incoming,children,parents,classes,refs,memberships,searchAliases,commonNames,locationAliases,networks,material,links:[...links.values()],stages:stageList,paths:paths.sort((a,b)=>a.id-b.id),applicable,relatedFacts,qualifications,designCandidates,assembly,assemblyBoundary};
  }
  function factGroup(a){
    const p=a.predicate;
    if(/calculation|^case[12]_|^theoretical_/.test(p)||/calculation/i.test(a.context?.condition||''))return 'reference';
    if(/brake|holdback/.test(p)&&/type|model|torque|provided|quantity|diameter/.test(p))return 'mechanical';
    if(/alarm|trip|interlock|permissive|protect|emergency|brake|holdback|switch|safety|fault|setpoint|severity/.test(p))return 'protection';
    if(/^(operating_requirement|design_numeric_requirement|control_timer_delay)$/.test(p)){
      const wording=String(a.value||'')+' '+(a.context?.condition||'');
      if(/alarm|\btrip(?:s|ped)?\b|interlock|permissive|protect|emergency|fault|zero.speed|\b(?:PCS|BSS|CBS)\b|start (?:winding|bearing) temperature/i.test(wording))return 'protection';
      if(p==='design_numeric_requirement'&&!/delay|warning|duration|allowance|start.*window/i.test(wording))return 'limits';
      return 'operation';
    }
    if(/capacity|flow|speed|range|temperature|pressure|voltage|power|level|limit/.test(p)&&!/^calculation_|^case[12]_/.test(p))return 'limits';
    if(/operating|sequence|command|control_|duty|standby|timer|requirement/.test(p))return 'operation';
    if(/oil_grade|lubri|maintenance|bearing|coupling|belt_|pulley|shaft|gear|dimension|length|width|height|clearance|manufacturer|model|construction|arrangement|weight|mass|takeup|idler/.test(p))return 'mechanical';
    return 'reference';
  }

  /**
   * Adaptive Equipment Information Flow Builder.
   * Dynamically organizes an entity's scalar properties, parsed engineering notes,
   * child parts, and multi-network connections into categories tailored to that
   * specific equipment or component, while keeping the exact assertion (`fact`)
   * attached to every single value for 1-click source review (`data-action="fact-source"`).
   */
  const FLOW_CATEGORY_META={
    process:{id:'process',title:'Process Duty & Conveying Profile',icon:'⇄'},
    drive:{id:'drive',title:'Drive Train, Torque & Power Transmission',icon:'⚙'},
    mechanical:{id:'mechanical',title:'Mechanical Geometry, Rollers & Wear Parts',icon:'◈'},
    tensions:{id:'tensions',title:'Belt Tensions, Take-Up & Structural Loads',icon:'⊥'},
    fluid:{id:'fluid',title:'Water, Air, Dust & Lubrication Systems',icon:'💧'},
    electrical:{id:'electrical',title:'Electrical, Instrumentation & Protection Logic',icon:'⚡'},
    access:{id:'access',title:'Hoists, Access, Civil & Maintenance Provisions',icon:'🏗'},
    notes:{id:'notes',title:'Engineering Notes & Drawing Context',icon:'📋'}
  };

  function classifySpecRow(key,val,pred,entityClasses){
    const k=String(key||'').toLowerCase(),v=String(val||'').toLowerCase(),p=String(pred||'').toLowerCase(),t=k+' '+p;
    if(/belt_tension|t1|t2|t3|takeup|take-up|counterweight|hgtu|rope_diameter|minimum_breaking|sheave_diameter|wheel load|anchoring|clamping force|vz|fx|fy|wind speed/i.test(t))return 'tensions';
    if(/motor|gearbox|gear_ratio|coupling|scoop|fluid_coupling|brake|torque|thruster|drum_diameter|excitation|cardan|pinion|slew|drive_power|rated_power/i.test(t))return 'drive';
    if(/pulley|face_width|bearing|shaft|lagging|idler|trough|pitch|roll_diameter|belt_construction|carcass|cover_thickness|cover_grade|scraper|cleaner|plough|skirt|chute|liner|hardox|ss304|valley angle|flap|stroke|cylinder|blade|grab|trolley|boom/i.test(t))return 'mechanical';
    if(/flow|pressure|pump|head|nozzle|spray|compressor|fad|dryer|receiver|filter|bag|airlock|ralv|fan|damper|oil|grease|lube|lubrication|tank|sump|strainer|valve|pipe|header/i.test(t))return 'fluid';
    if(/switch|pcs|bss|zss|pull-cord|belt-sway|zero-speed|probe|sensor|radar|level|weigher|load_cell|detector|ip65|ip66|ip67|contact|cam|mcc|switchboard|sld|transformer|cable|reel|plc|interlock|trip|alarm|delay|timer|permissive|control|voltage|frequency|enclosure/i.test(t))return 'electrical';
    if(/hoist|crane|monorail|walkway|stair|manhole|elevation|floor|rail|hvac|pressurization|fire/i.test(t))return 'access';
    if(/capacity|tph|belt_width|belt_speed|belt_length|lift|material|density|lump|moisture|hgi|screen|aperture|sample|cutter|bunker|volume|storage|quantity|individual_device_count/i.test(t))return 'process';
    if(p==='document_note'&&k==='engineering note')return 'notes';
    if((entityClasses||[]).some(c=>/motor|gearbox|coupling|brake/.test(c)))return 'drive';
    if((entityClasses||[]).some(c=>/pulley|idler|scraper|conveyor_belt|mechanical_component/.test(c)))return 'mechanical';
    if((entityClasses||[]).some(c=>/pump|compressor|filter|fan|valve|tank|spray|dust/.test(c)))return 'fluid';
    if((entityClasses||[]).some(c=>/switch|sensor|weigher|detector|panel|switchboard|mcc/.test(c)))return 'electrical';
    return 'process';
  }

  function preferredCategoryOrder(entityClasses,entityLabel){
    const c=(entityClasses||[]).join(' ').toLowerCase()+' '+String(entityLabel||'').toLowerCase();
    if(/motor|gearbox|coupling|brake|drive/.test(c))return ['drive','mechanical','electrical','fluid','tensions','process','access','notes'];
    if(/pulley|idler|scraper|cleaner|take_up|take-up|counterweight|rope|belt and mechanical/.test(c))return ['mechanical','tensions','process','drive','electrical','fluid','access','notes'];
    if(/switch|sensor|weigher|detector|protection|panel|mcc|switchboard|cable_reel/.test(c))return ['electrical','process','mechanical','drive','tensions','fluid','access','notes'];
    if(/pump|compressor|dryer|filter|fan|airlock|spray|dfds|spds|water|lubrication|hydraulic/.test(c))return ['fluid','process','drive','mechanical','electrical','tensions','access','notes'];
    if(/hoist|bogie|rail_clamp|access/.test(c))return ['access','mechanical','drive','tensions','electrical','process','fluid','notes'];
    return ['process','drive','mechanical','tensions','fluid','electrical','access','notes'];
  }

  function formatScalarValue(a){
    if(a.value===null||a.value===undefined)return '';
    const v=typeof a.value==='boolean'?(a.value?'Yes':'No'):String(a.value);
    return a.unit?`${v} ${a.unit}`:v;
  }

  function childHeadline(p,childId){
    const own=p.outgoing.get(childId)||[];
    const priority=['rated_capacity','design_capacity','motor_rated_power','rated_power','coupling_power_rating','gear_ratio_nominal','brake_rated_torque','pulley_diameter','face_width','idler_roll_diameter','quantity','individual_device_count','scheduled_nozzle_count','takeup_travel','counterweight_mass','belt_width','belt_speed','belt_construction','model_number','manufacturer'];
    const bits=[];
    for(const pred of priority){
      const f=own.find(a=>a.predicate===pred&&a.value!==null&&a.value!==undefined);
      if(f){
        const txt=formatScalarValue(f);
        if(txt&&!bits.includes(txt))bits.push(pred==='gear_ratio_nominal'?`${txt}:1`:pred==='pulley_diameter'||pred==='idler_roll_diameter'?`Ø${txt}`:pred==='quantity'||pred==='individual_device_count'?`Qty ${txt}`:txt);
      }
      if(bits.length>=4)break;
    }
    if(!bits.length){
      const role=own.find(a=>['equipment_role','assembly_arrangement','purpose'].includes(a.predicate)&&typeof a.value==='string');
      if(role)return {summary:role.value.length>88?role.value.slice(0,86)+'…':role.value,fact:role};
      const note=own.find(a=>a.predicate==='document_note'&&typeof a.value==='string');
      if(note){
        const first=note.value.split(/;\s*/)[0]||'';
        return {summary:first.length>88?first.slice(0,86)+'…':first,fact:note};
      }
    }
    const firstFact=own.find(a=>priority.includes(a.predicate))||own[0];
    return {summary:bits.join(' · '),fact:firstFact};
  }

  function buildEquipmentFlow(p,id){
    const e=p.entities.get(id);
    if(!e)return null;
    const own=p.outgoing.get(id)||[];
    const entityClasses=p.classes.get(id)||[];
    const classFacts=own.filter(a=>a.predicate==='instance_of');
    const parentEdges=p.parents.get(id)||[];
    const locatedEdges=own.filter(a=>a.predicate==='located_at'&&a.canonical_object);
    const childEdges=p.children.get(id)||[];

    // 1. Operational Lead & Role Statements (with direct source citation)
    const narrativePreds=['equipment_role','purpose','equipment_description','function','assembly_arrangement','location_description','control_role'];
    const roleStatements=[];
    const seenRoleText=new Set();
    for(const pred of narrativePreds){
      for(const a of own.filter(x=>x.predicate===pred&&typeof x.value==='string')){
        const normTxt=a.value.trim();
        if(normTxt&&!seenRoleText.has(normTxt.toLowerCase())){
          seenRoleText.add(normTxt.toLowerCase());
          roleStatements.push({label:pretty(pred),text:normTxt,fact:a});
        }
      }
    }

    // 2. Parse scalar specifications + structured key:value segments from document_note
    const skipPreds=new Set(['instance_of','part_of','located_at','depicted_in','source_discrepancy','source_gap',...narrativePreds]);
    const rawRows=[];
    const revisionRows=[];

    for(const a of own){
      if(a.canonical_object||skipPreds.has(a.predicate))continue;
      if(a.predicate==='document_note'&&typeof a.value==='string'){
        const segments=a.value.split(/;\s*/).map(s=>s.trim()).filter(Boolean);
        for(const seg of segments){
          const colonIdx=seg.indexOf(':');
          if(colonIdx>0&&colonIdx<68){
            const key=seg.slice(0,colonIdx).trim();
            const val=seg.slice(colonIdx+1).trim();
            if(/^rev(?:ision)?\b/i.test(key)||/\brev\s*\d+\b/i.test(key)){
              revisionRows.push({key,value:val,condition:a.context?.condition,fact:a});
            }else{
              const cat=classifySpecRow(key,val,'document_note',entityClasses);
              rawRows.push({key,value:val,unit:'',condition:a.context?.condition,fact:a,category:cat,fromNote:true});
            }
          }else{
            rawRows.push({key:'Engineering Note',value:seg,unit:'',condition:a.context?.condition,fact:a,category:'notes',fromNote:true});
          }
        }
      }else if(a.value!==null&&a.value!==undefined){
        const key=pretty(a.predicate);
        const val=typeof a.value==='boolean'?(a.value?'Yes':'No'):String(a.value);
        const cat=classifySpecRow(key,val,a.predicate,entityClasses);
        rawRows.push({key,value:val,unit:a.unit||'',condition:a.context?.condition,fact:a,category:cat,predicate:a.predicate,fromNote:false});
      }
    }

    // Deduplicate identical key+value rows (preferring typed scalar predicates over parsed note strings)
    const dedupedRows=[];
    const seenRowKey=new Set();
    for(const r of rawRows){
      const sig=`${r.key.toLowerCase().replace(/[^a-z0-9]/g,'')}:${String(r.value).toLowerCase().replace(/\s+/g,'')}`;
      if(seenRowKey.has(sig))continue;
      seenRowKey.add(sig);
      dedupedRows.push(r);
    }

    // 3. Headline Key Metrics Ribbon (2 to 6 adaptive badges with 1-click source review)
    const metricPriority=['rated_capacity','design_capacity','coal_rated_capacity','belt_width','belt_speed','belt_length','motor_rated_power','drive_power_rating','rated_power','motor_voltage','power_supply_voltage','rated_voltage','motor_speed','motor_rated_speed','rated_rotational_speed','manufacturer','model_number','electrical_feeder_schedule','compartment_number','breaker_rating','cable_size','gear_ratio_nominal','coupling_power_rating','brake_rated_torque','pulley_diameter','face_width','bearing_center_distance','takeup_travel','counterweight_mass','idler_roll_diameter','idler_trough_angle','idler_spacing','quantity','individual_device_count','scheduled_nozzle_count','rated_flow','working_pressure','hydraulic_working_pressure'];
    const headlineMetrics=[];
    const usedMetricKeys=new Set();
    for(const pred of metricPriority){
      const matches=dedupedRows.filter(r=>r.predicate===pred);
      if(matches.length){
        const first=matches[0];
        const combinedVal=[...new Set(matches.map(m=>m.unit?`${m.value} ${m.unit}`:m.value))].join(' / ');
        headlineMetrics.push({label:first.key,value:combinedVal,condition:first.condition,fact:first.fact,allFacts:matches.map(m=>m.fact)});
        usedMetricKeys.add(pred);
        usedMetricKeys.add(first.key.toLowerCase());
      }
      if(headlineMetrics.length>=6)break;
    }
    if(headlineMetrics.length<4){
      for(const r of dedupedRows){
        const rKeyLower=r.key.toLowerCase();
        if(r.category!=='notes'&&r.value.length<=68&&!usedMetricKeys.has(r.predicate)&&!usedMetricKeys.has(rKeyLower)){
          const formattedVal=r.unit?`${r.value} ${r.unit}`:r.value;
          headlineMetrics.push({label:r.key,value:formattedVal,condition:r.condition,fact:r.fact,allFacts:[r.fact]});
          usedMetricKeys.add(r.predicate);
          usedMetricKeys.add(rKeyLower);
          if(headlineMetrics.length>=6)break;
        }
      }
    }

    // 4. Group Specification Rows into Adaptive Domain Sections
    const order=preferredCategoryOrder(entityClasses,e.label);
    const sections=[];
    for(const catId of order){
      const rows=dedupedRows.filter(r=>r.category===catId);
      if(rows.length){
        sections.push({
          ...FLOW_CATEGORY_META[catId],
          rows
        });
      }
    }

    // 5. Sub-Assembly & Component Anatomy Cards
    const seenChild=new Set();
    const childrenCards=[];
    for(const edge of childEdges){
      const cid=edge.canonical_subject;
      if(seenChild.has(cid)||!p.entities.has(cid)||p.refs.has(cid))continue;
      seenChild.add(cid);
      const ce=p.entities.get(cid);
      const subCount=new Set((p.children.get(cid)||[]).map(a=>a.canonical_subject)).size;
      const head=childHeadline(p,cid);
      childrenCards.push({
        id:cid,
        label:ce.label,
        classes:(p.classes.get(cid)||[]).map(pretty),
        subCount,
        summary:head.summary,
        summaryFact:head.fact,
        partEdge:edge
      });
    }
    childrenCards.sort((a,b)=>b.subCount-a.subCount||a.label.localeCompare(b.label,undefined,{numeric:true}));

    // 6. Multi-Network Process & Mechanical Wiring Groups
    const netMeta=[
      ['material','Coal & Material Flow'],
      ['mechanical','Mechanical Drive, Support & Tensioning'],
      ['utility','Water, Compressed Air & Lubrication'],
      ['electrical','Electrical Power Supply'],
      ['control','Control, Protection & Interlocks']
    ];
    const allEdges=p.networks.filter(a=>a.canonical_subject===id||a.canonical_object===id);
    const nonNetLinks=[...(p.incoming.get(id)||[]),...own].filter(a=>a.canonical_object&&!['instance_of','part_of','located_at'].includes(a.predicate)&&!allEdges.includes(a));
    const wiringGroups=[];
    for(const [netKey,netTitle] of netMeta){
      const edges=allEdges.filter(a=>a.context?.network===netKey);
      if(edges.length){
        wiringGroups.push({
          network:netKey,
          title:netTitle,
          incoming:edges.filter(a=>a.canonical_object===id),
          outgoing:edges.filter(a=>a.canonical_subject===id),
          all:edges
        });
      }
    }
    if(nonNetLinks.length){
      wiringGroups.push({
        network:'associated',
        title:'Service Coverage & Associated Equipment',
        incoming:nonNetLinks.filter(a=>a.canonical_object===id),
        outgoing:nonNetLinks.filter(a=>a.canonical_subject===id),
        all:nonNetLinks
      });
    }

    // 7. Discrepancies, Gaps & Applicable References
    const qualifications=p.qualifications(id);
    const applicableRefs=p.relatedFacts(id);

    // 8. Start Permissives, Trip Conditions & Interlocks Checklist
    const checklistCandidates=[
      ...own.filter(a=>!a.canonical_object&&a.predicate!=='instance_of').map(fact=>({fact,via:null})),
      ...applicableRefs
    ];
    const permissivesChecklist=[];
    const seenCheckSig=new Set();
    for(const {fact:a,via} of checklistCandidates){
      const pred=a.predicate;
      const valStr=formatScalarValue(a);
      const fullTxt=`${pred} ${valStr} ${a.context?.condition||''}`;
      let kind=null;
      if(/permissive|prior to start|before start|ready to start|healthy|zero.speed.*start/i.test(pred+' '+valStr)){
        kind='permissive';
      }else if(/trip|emergency_stop|fault|pull.cord|belt.sway|plugged.chute|chute.block|over.temp|high.temp|overload|\b(?:PCS|BSS|ZSS)\b/i.test(pred+' '+valStr)&&factGroup(a)==='protection'){
        kind='trip';
      }else if(['sequence_logic','interlock_requirement','control_timer_delay'].includes(pred)||(pred==='operating_requirement'&&/interlock|sequence|start|stop|delay/i.test(fullTxt))){
        kind='sequence';
      }
      if(!kind)continue;
      const sig=`${kind}:${valStr.toLowerCase().slice(0,120)}`;
      if(seenCheckSig.has(sig))continue;
      seenCheckSig.add(sig);
      permissivesChecklist.push({
        id:a.id,
        kind,
        badge:kind==='permissive'?'PERMISSIVE':kind==='trip'?'TRIP / PROTECT':'INTERLOCK',
        label:pretty(pred),
        text:valStr,
        condition:a.context?.condition||'',
        fact:a,
        via
      });
    }
    const kindRank={permissive:0,trip:1,sequence:2};
    permissivesChecklist.sort((a,b)=>(kindRank[a.kind]??9)-(kindRank[b.kind]??9));

    return {
      entity:e,
      commonName:commonName(p,id),
      searchAliases:p.searchAliases?.get(id)||[],
      entityClasses,
      classFacts,
      parentEdges,
      locatedEdges,
      roleStatements,
      headlineMetrics,
      sections,
      revisionRows,
      childrenCards,
      wiringGroups,
      qualifications,
      applicableRefs,
      permissivesChecklist
    };
  }

  // Lay out only recorded in-area edges. Condense cycles before ranking so a
  // recycle loop cannot hang navigation or imply an invented process sequence.
  function areaGraph(projection,area,root=null){
    const members=new Set(projection.stages.find(s=>s.id===area)?.entities.map(e=>e.id)||[]);
    if(root){const scope=new Set(projection.assembly(root).map(item=>item.id));for(const id of members)if(!scope.has(id))members.delete(id);}
    const grouped=new Map();
    for(const a of projection.material){
      if(!members.has(a.canonical_subject)||!members.has(a.canonical_object))continue;
      const key=a.canonical_subject+'>'+a.canonical_object;
      if(!grouped.has(key))grouped.set(key,{from:a.canonical_subject,to:a.canonical_object,facts:[]});
      grouped.get(key).facts.push(a);
    }
    const edges=[...grouped.values()],ids=[...new Set(edges.flatMap(e=>[e.from,e.to]))];
    const adj=new Map(ids.map(id=>[id,[]]));edges.forEach(e=>adj.get(e.from).push(e.to));
    let serial=0;const stack=[],onStack=new Set(),index=new Map(),low=new Map(),components=[];
    function visit(id){
      index.set(id,serial);low.set(id,serial++);stack.push(id);onStack.add(id);
      for(const next of adj.get(id)){
        if(!index.has(next)){visit(next);low.set(id,Math.min(low.get(id),low.get(next)));}
        else if(onStack.has(next))low.set(id,Math.min(low.get(id),index.get(next)));
      }
      if(low.get(id)===index.get(id)){
        const part=[];let next;do{next=stack.pop();onStack.delete(next);part.push(next);}while(next!==id);
        components.push(part);
      }
    }
    ids.forEach(id=>{if(!index.has(id))visit(id);});
    const componentOf=new Map();components.forEach((part,i)=>part.forEach(id=>componentOf.set(id,i)));
    const dag=components.map(()=>new Set()),degree=components.map(()=>0),rank=components.map(()=>0);
    edges.forEach(e=>{const a=componentOf.get(e.from),b=componentOf.get(e.to);if(a!==b&&!dag[a].has(b)){dag[a].add(b);degree[b]++;}});
    const queue=degree.map((v,i)=>v===0?i:null).filter(v=>v!==null);
    for(let i=0;i<queue.length;i++)for(const next of dag[queue[i]]){rank[next]=Math.max(rank[next],rank[queue[i]]+1);if(--degree[next]===0)queue.push(next);}
    const columns=[];
    for(const id of ids){const c=rank[componentOf.get(id)];(columns[c]??=[]).push(id);}
    const structure=id=>(projection.classes.get(id)||[]).includes('plant_building')?1:0;
    const compare=(a,b)=>structure(a)-structure(b)||projection.entities.get(a).label.localeCompare(projection.entities.get(b).label,undefined,{numeric:true});
    columns.forEach(col=>col.sort(compare));
    const positions=()=>new Map(columns.flatMap(col=>col.map((id,i)=>[id,i])));
    // Barycentric sweeps keep parallel A/B and yard branches visually adjacent.
    for(let sweep=0;sweep<3;sweep++)for(const direction of [1,-1]){
      const order=direction===1?columns:[...columns].reverse();const pos=positions();
      for(const col of order){const score=id=>{const peers=edges.filter(e=>direction===1?e.to===id:e.from===id).map(e=>direction===1?e.from:e.to).filter(peer=>structure(id)||!structure(peer)).map(peer=>pos.get(peer));return peers.length?peers.reduce((a,b)=>a+b,0)/peers.length:pos.get(id);};col.sort((a,b)=>structure(a)-structure(b)||score(a)-score(b)||compare(a,b));col.forEach((id,i)=>pos.set(id,i));}
    }
    let bypass=0;
    edges.forEach(e=>{if(rank[componentOf.get(e.to)]-rank[componentOf.get(e.from)]>1)e.bypassLane=bypass++;});
    const top=20+bypass*12;
    const nodes=columns.flatMap((col,c)=>col.map((id,r)=>({id,x:16+c*206,y:top+r*118,cycle:components[componentOf.get(id)].length>1||adj.get(id).includes(id)})));
    return {nodes,edges,width:Math.max(340,columns.length*206-30),height:Math.max(160,...columns.map(c=>c.length*118+top))};
  }
  return {build,stages,pathStages,pretty,stageForLabel,factGroup,current,areaGraph,buildEquipmentFlow,searchEntities,isPrimaryEquipment,qualificationSeverity,commonName,normalizeUserQuery};
});
