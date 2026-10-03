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
    {id:'unloading',title:'Jetty & unloading',short:'Unloading',number:'01',row:1,col:1,description:'Receive vessel coal and feed the two receiving streams.',tags:'Ship unloaders · EAC-1 / 2 · UEF-1'},
    {id:'screening',title:'Primary screening',short:'Screening',number:'02',row:1,col:2,description:'Screen incoming coal; separate oversize rejects.',tags:'UEE-1 · EBD-1–4 · EAC-3'},
    {id:'distribution',title:'Distribution & diversion',short:'Distribution',number:'03',row:1,col:3,description:'Direct coal onward to silos or divert it to the stockyard.',tags:'UEF-3–7 · EAC-4 / 5 · EBA-6'},
    {id:'stockyard',title:'Stockyard',short:'Stockyard',number:'04',row:2,col:3,description:'Stack, store and reclaim coal through four yard branches.',tags:'EAD · EAE · EAF · yard conveyors'},
    {id:'reclaim',title:'Reclaim transfer',short:'Reclaim transfer',number:'05',row:2,col:2,description:'Combine selected reclaim streams and deliver coal to the silos.',tags:'UEF-8–12 · EBA-15 / 16'},
    {id:'blending',title:'Blending silos',short:'Blending',number:'06',row:2,col:1,description:'Receive, store and extract coal into the crusher-feed streams.',tags:'UEE-2 · EBB-1 / 2 · extractors'},
    {id:'crushing',title:'Screening & crushing',short:'Crushing',number:'07',row:3,col:1,description:'Screen and crush coal, with documented bypass alternatives.',tags:'UEE-3 · EBA-17 · EBC-1 / 2'},
    {id:'bunkerfeed',title:'Bunker-feed transfer',short:'Bunker feed',number:'08',row:3,col:2,description:'Transfer processed coal to either bunker conveyor.',tags:'EBA-18 · UEF-13 · EBA-19'},
    {id:'bunkers',title:'Unit bunkers',short:'Bunkers',number:'09',row:3,col:3,description:'Distribute coal to the selected unit and bunker position.',tags:'TT-1–4 · Unit 1 / 2 · bunkers A–F'}
  ];
  const pathStages={
    1:['unloading','screening','distribution','stockyard'],
    2:['unloading','screening','distribution','stockyard','blending','crushing','bunkerfeed','bunkers'],
    3:['stockyard','reclaim','blending','crushing','bunkerfeed','bunkers'],
    4:['blending','crushing','bunkerfeed','bunkers'],
    5:['unloading','screening','distribution','stockyard','blending']
  };
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
    if(/^(UEF-13|EBA-1[89][AB]|FG-1[78]|EAT-[34]|QB-[34]|EAU-2(?: .*)?)$/.test(n)||n==='UEF-13 COAL SAMPLING SYSTEM')return 'bunkerfeed';
    if(/^(TT-[1-4]|FG-(19|20|21|22)|UNIT-[12] COAL BUNKER BAY|BUNKER-[A-F] OF UNIT-[12])$/.test(n))return 'bunkers';
    return null;
  }
  function current(a,at){
    const c=a.context||{};
    const start=c.valid_from?Date.parse(c.valid_from):null,end=c.valid_to?Date.parse(c.valid_to):null;
    return (!c.valid_from||(Number.isFinite(start)&&start<=at))&&(!c.valid_to||(Number.isFinite(end)&&at<end));
  }
  function build(model,{at=Date.now()}={}){
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
    const qualifications=id=>[...(outgoing.get(id)||[]).map(fact=>({fact})),...relatedFacts(id)].filter(({fact:a})=>/^source_(gap|discrepancy)$/.test(a.predicate)||/unresolved|conflict|reconcil|contradict|copy error|uncertain|discrepanc/i.test(String(a.value||'')+' '+(a.context?.condition||'')));
    // Only accepted, current containment edges expand an assembly. A shared
    // service or nearby machine must not donate its entire tree to this one.
    const assembly=id=>{
      if(!entities.has(id))return [];
      const seen=new Set([id]),result=[],queue=[{id,depth:0,parent:null}];
      for(let i=0;i<queue.length;i++){
        const item=queue[i];result.push({...item,entity:entities.get(item.id),facts:outgoing.get(item.id)||[]});
        for(const edge of children.get(item.id)||[]){
          const child=edge.canonical_subject;if(seen.has(child))continue;
          seen.add(child);queue.push({id:child,depth:item.depth+1,parent:item.id});
        }
      }
      return result;
    };
    const designCandidates=id=>[...entities.values()].filter(e=>e.id!==id&&!refs.has(e.id)&&!memberships.has(e.id)&&(classes.get(e.id)||[]).some(c=>(classes.get(id)||[]).includes(c))&&((children.get(e.id)||[]).length||(outgoing.get(e.id)||[]).length>10)).slice(0,6);
    const assemblyBoundary=id=>{
      const ids=new Set(assembly(id).map(item=>item.id));
      return facts.filter(a=>a.canonical_object&&current(a,at)&&
        (ids.has(a.canonical_subject)!==ids.has(a.canonical_object))&&
        (networks.includes(a)||['serves','serves_equipment','supplies_water_to','utility_supply_to','associated_with'].includes(a.predicate)));
    };
    return {version:model.version,entities,facts,outgoing,incoming,children,parents,classes,refs,memberships,networks,material,links:[...links.values()],stages:stageList,paths:paths.sort((a,b)=>a.id-b.id),applicable,relatedFacts,qualifications,designCandidates,assembly,assemblyBoundary};
  }
  function factGroup(a){
    const p=a.predicate;
    if(/calculation|^case[12]_|^theoretical_/.test(p)||/calculation/i.test(a.context?.condition||''))return 'reference';
    if(/brake|holdback/.test(p)&&/type|model|torque|provided|quantity|diameter/.test(p))return 'mechanical';
    if(/alarm|trip|interlock|permissive|protect|emergency|brake|holdback|switch|safety|fault|setpoint|severity/.test(p))return 'protection';
    // The source uses broad predicates for both start sequences and trips.
    // Use its retained wording to organize those cards, without changing them.
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
  return {build,stages,pathStages,pretty,stageForLabel,factGroup,current,areaGraph};
});
