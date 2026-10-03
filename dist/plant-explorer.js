/* UI for the read-only, evidence-backed plant explorer. */
'use strict';
const PlantExplorer=(()=>{
  let cachedModel,cachedProjection,cachedMinute,resizeObserver;
  const parameters=()=>new URLSearchParams(location.hash.split('?')[1]||'');
  const projection=()=>{
    const minute=Math.floor(Date.now()/60000);
    if(cachedModel!==state.model||cachedMinute!==minute){cachedModel=state.model;cachedMinute=minute;cachedProjection=PlantExplorerModel.build(state.model);}
    return cachedProjection;
  };
  const nice=PlantExplorerModel.pretty;
  const value=a=>a.canonical_object?projection().entities.get(a.canonical_object)?.label||a.canonical_object:typeof a.value==='string'?a.value:typeof a.value==='boolean'?(a.value?'Yes':'No'):JSON.stringify(a.value);
  const url=(changes={},reset=false)=>{const p=reset?new URLSearchParams():parameters();for(const[k,v]of Object.entries(changes)){if(v===null||v===undefined||v==='')p.delete(k);else p.set(k,v);}return '#overview'+(p.size?'?'+p.toString():'');};
  const entityLink=(id,text,cls='pe-entity-link')=>{
    const groups=projection().memberships.get(id),area=parameters().get('area');
    const destination=groups?.has(area)?area:groups?.size===1?[...groups][0]:null;
    return `<a class="${cls}" href="${esc(url({equipment:id,area:destination,tab:null,q:null,network:null,pick:null,edge:null,trail:null,scene:null,browse:null}))}">${esc(text||projection().entities.get(id)?.label||id)}</a>`;
  };
  const canRecord=id=>projection().entities.get(id)?.category==='equipment'&&!projection().refs.has(id);
  const cite=(a,label='Source')=>a.evidence?.length?`<button class="pe-source" data-action="fact-source" data-id="${esc(a.id)}" data-support="0">${esc(label)}</button>`:'';
  const unique=items=>[...new Set(items)];
  const emptyText=text=>`<p class="pe-empty">${esc(text)}</p>`;
  function sourceLabel(a){
    const index=state.evidence_index||[];const s=index.find(e=>e.id===a.evidence?.[0]?.evidence_id);
    return s?s.locator||'Page '+s.page:'View source';
  }
  function fact(a,via){
    const c=a.context||{},p=projection();
    const conflict=state.model.conflicts.some(x=>x.assertion_ids.includes(a.id));
    return `<article class="pe-fact"><div class="pe-fact-top"><span>${esc(nice(a.predicate))}</span>${cite(a,sourceLabel(a))}</div><div class="pe-fact-value">${a.canonical_object?entityLink(a.canonical_object):esc(value(a))}${a.unit?` <span class="pe-unit">${esc(a.unit)}</span>`:''}</div>${c.condition?`<p class="pe-condition">${esc(c.condition)}</p>`:''}${via?`<p class="pe-via">From ${entityLink(via.canonical_subject)} · ${cite(via,'Applicability source')}</p>`:''}${conflict?'<p class="pe-caution">Competing source values are retained.</p>':''}${!PlantExplorerModel.current(a,Date.now())?'<p class="pe-caution">Outside its recorded validity period.</p>':''}<details class="pe-context"><summary>Basis & evidence</summary><p>${esc(c.basis||'Source basis not specified in this record.')}</p>${c.valid_from||c.valid_to?`<p>Validity: ${esc(c.valid_from||'start unknown')} → ${esc(c.valid_to||'end unknown')}</p>`:''}<p>${esc(c.kind||'Unqualified')} · ${esc(a.origin||'source record')} · model v${a.created_version}</p><div class="pe-inline">${(a.evidence||[]).map((s,i)=>`<button class="pe-source" data-action="fact-source" data-id="${esc(a.id)}" data-support="${i}">Source ${i+1}</button>`).join('')}</div></details></article>`;
  }
  function evidenceIndex(){return new Map((state.evidence_index||[]).map(e=>[e.id,e]));}
  function sourceDocument(){
    return state.documents.find(d=>d.sha256==='c2230808a454b87e4b08648f2d6a45feab6785f24cff31545c34822c85723359');
  }
  function drawingButton(page,text){
    const d=sourceDocument(),e=(state.evidence_index||[]).find(e=>e.document_id===d?.id&&e.page===page);
    return e?`<button class="button secondary small" data-action="evidence" data-id="${esc(e.id)}">${esc(text)} ↗</button>`:'';
  }
  function pathPicker(p){
    const selected=parameters().get('path')||'';
    const path=p.paths.find(x=>x.id===selected);
    return `<section class="pe-paths" aria-label="Documented operating paths"><div class="pe-section-label">EXPLORE A COAL FLOW PATH</div><div class="pe-path-options"><a class="pe-path ${!path?'is-active':''}" href="${esc(url({path:null,area:null,equipment:null,tab:null}))}" ${!path?'aria-current="true"':''}>Whole plant</a>${p.paths.map(x=>`<a class="pe-path ${path?.id===x.id?'is-active':''}" href="${esc(url({path:x.id,area:null,equipment:null,tab:null}))}" ${path?.id===x.id?'aria-current="true"':''}><span>${x.id}</span>${esc(x.title)}</a>`).join('')}</div>${path?`<div class="pe-path-description"><strong>${esc(path.summary.value)}</strong> ${cite(path.summary,'Path source')}<details><summary>Path requirements & qualifications</summary>${path.facts.filter(a=>a.id!==path.summary.id).map(a=>fact(a)).join('')}</details></div>`:''}<p class="pe-help">${path?'Highlighted stages are a process guide. They do not select an A/B stream, gate position or live route.':'Select a process stage to find its equipment. Arrows represent documented coal-flow links between groups.'}</p></section>`;
  }
  function map(p){
    const selected=parameters().get('area'),path=p.paths.find(x=>x.id===parameters().get('path'));
    return `<div class="pe-flow-header"><div><h2>From vessel to bunker</h2><span class="pe-muted">Process schematic · not a geographical layout</span></div><div class="pe-inline"><a class="button secondary small" href="${url({focus:parameters().get('focus')?null:'map',area:null})}">${parameters().get('focus')?'Exit focus':'Expand overview'}</a>${drawingButton(55,'Flow drawing')}${drawingButton(56,'Plant layout')}</div></div><div class="pe-flow-map" id="pe-flow-map"><svg id="pe-flow-lines" role="group" aria-label="Coal-flow connections"></svg>${p.stages.map(s=>`<a href="${esc(url({area:s.id,equipment:null,tab:null,q:null}))}" class="pe-stage ${selected===s.id?'is-selected':''} ${path&&!path.stages.includes(s.id)?'is-muted':''}" data-stage="${s.id}" style="--stage-row:${s.row};--stage-col:${s.col}" ${selected===s.id?'aria-current="true"':''}><span class="pe-stage-top"><span class="pe-stage-number">${s.number}</span><span class="pe-stage-count">${s.entities.length} records</span></span><strong>${s.title}</strong><span class="pe-stage-description">${s.description}</span><span class="pe-stage-tags">${s.tags}</span><span class="pe-stage-open">Explore equipment <span aria-hidden="true">↗</span></span></a>`).join('')}</div><div class="pe-flow-footer"><span><i class="pe-legend-line"></i> Documented flow · conditional branches retained</span><details><summary>Browse connections as a list (${p.links.length})</summary><div class="pe-branch-list">${p.links.map(l=>`<button class="pe-link-row" data-action="plant-branch" data-id="${l.id}"><span>${p.stages.find(s=>s.id===l.from).short} → ${p.stages.find(s=>s.id===l.to).short}</span><span>${l.facts.length} source links ↗</span></button>`).join('')}</div></details></div>`;
  }
  function connection(a,id){
    const outgoing=a.canonical_subject===id,other=outgoing?a.canonical_object:a.canonical_subject;
    return `<article class="pe-connection"><div class="pe-inline"><span class="pe-direction">${outgoing?'TO →':'← FROM'}</span>${entityLink(other)}${cite(a,'Evidence')}</div><p>${esc(a.context?.condition||'No operating condition specified in the source record.')}</p>${a.context?.from_port||a.context?.to_port?`<span class="pe-muted">${esc(a.context.from_port||'Port unspecified')} → ${esc(a.context.to_port||'Port unspecified')}</span>`:''}</article>`;
  }
  function tree(id,ancestors=new Set(),depth=0){
    const p=projection(),e=p.entities.get(id);if(!e)return '';
    const children=unique((p.children.get(id)||[]).map(a=>a.canonical_subject));
    const className=(p.classes.get(id)||[]).map(nice).join(', ')||'Unclassified';
    if(ancestors.has(id)||depth>=7)return `<li>${entityLink(id)} <span class="pe-muted">Open to continue</span></li>`;
    const next=new Set(ancestors);next.add(id);
    return `<li>${children.length?`<details ${depth===0&&children.length<=3?'open':''}><summary>${entityLink(id)} <span class="pe-tree-count">${children.length}</span></summary><ul>${children.map(c=>tree(c,next,depth+1)).join('')}</ul></details>`:`${entityLink(id)} <span class="pe-tree-type">${esc(className)}</span>`}</li>`;
  }
  function areaMap(p,stage,root=null){
    const graph=PlantExplorerModel.areaGraph(p,stage.id,root);if(!graph.nodes.length)return '';
    const nodes=new Map(graph.nodes.map(n=>[n.id,n]));
    const bypassCount=graph.edges.filter(e=>e.bypassLane!==undefined).length;
    const lines=graph.edges.map(edge=>{
      const a=nodes.get(edge.from),b=nodes.get(edge.to),x=a.x+154,y=a.y+45,tx=b.x-5,ty=b.y+45;
      // Bypass links travel above the node rows, never through an intermediate
      // equipment box (which would incorrectly suggest an extra connection).
      const offset=12+(edge.bypassLane||0)*24/Math.max(1,bypassCount-1);
      const d=edge.bypassLane!==undefined?`M${x},${y} H${x+offset} V${8+edge.bypassLane*12} H${tx-offset} V${ty} H${tx}`:edge.from===edge.to?`M${x},${y} C${x+36},${y} ${x+36},${a.y+12} ${x+5},${a.y+12}`:b.x>a.x?`M${x},${y} C${x+30},${y} ${tx-30},${ty} ${tx},${ty}`:`M${x},${y} C${x+32},${y} ${x+32},${ty} ${b.x+159},${ty}`;
      const name=`${p.entities.get(edge.from).label} to ${p.entities.get(edge.to).label}`;
      return `<path class="pe-flow-line" aria-hidden="true" d="${d}" marker-end="url(#pe-local-arrow)"/><path class="pe-flow-hit" d="${d}" data-action="plant-flow-edge" data-id="${esc(edge.facts[0].id)}" tabindex="0" role="button" aria-label="Inspect ${esc(name)}"/>`;
    }).join('');
    return `<section class="pe-area-topology"><div class="pe-section-heading"><div><h3>Equipment flow</h3><p class="pe-help">Follow an arrow to inspect its conditions and evidence. Select equipment to open its details.</p></div><span class="pe-muted">${graph.nodes.length} connected records · ${graph.edges.length} links</span></div><div class="pe-area-scroll" tabindex="0" role="region" aria-label="${esc(stage.title)} equipment flow; scroll horizontally for more"><div class="pe-area-canvas" style="width:${graph.width}px;height:${graph.height}px"><svg width="${graph.width}" height="${graph.height}" role="group" aria-label="Documented equipment connections"><defs><marker id="pe-local-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#739591"/></marker></defs>${lines}</svg>${graph.nodes.map(n=>{
      const e=p.entities.get(n.id),type=(p.classes.get(n.id)||[]).map(nice).join(', ')||'Classification not recorded';
      return `<div class="pe-area-node" style="left:${n.x}px;top:${n.y}px">${entityLink(n.id)}<span>${esc(type)}</span>${n.cycle?'<small>Loop / return link</small>':''}</div>`;
    }).join('')}</div></div><p class="pe-help">In-area coal-flow connections. Scroll the diagram sideways if needed. Incoming and outgoing links are listed below.</p></section>`;
  }
  function areaEntries(p,stage){
    if(!stage)return '';
    const entries=stage.entities.filter(e=>(p.classes.get(e.id)||[]).includes('functional_area')&&(p.children.get(e.id)||[]).length);
    return entries.length?`<section class="pe-area-entries" aria-label="Explore functional areas"><h3>Explore an area in detail</h3><div class="pe-area-entry-grid">${entries.map(e=>{
      const role=(p.outgoing.get(e.id)||[]).find(a=>a.predicate==='equipment_role');
      return `<article>${entityLink(e.id,e.label,'pe-area-entry-title')}<p>${esc(role?.value||'Open equipment, local systems and shared dependencies.')}</p><span class="pe-muted">${unique((p.children.get(e.id)||[]).map(a=>a.canonical_subject)).length} main equipment & system entries</span><div class="pe-inline"><a href="${esc(url({equipment:e.id,tab:'structure',q:null}))}">Equipment tree →</a><a href="${esc(url({equipment:e.id,tab:'assembly',q:null}))}">Search assembly facts →</a></div></article>`;
    }).join('')}</div></section>`:'';
  }
  function directory(p){
    const area=parameters().get('area')||'',stage=p.stages.find(s=>s.id===area),limit=Math.max(40,Math.min(1000,Number(parameters().get('limit'))||40));
    let entities=stage?.entities||[...p.entities.values()].filter(e=>area==='references'?p.refs.has(e.id):!p.refs.has(e.id));
    if(area==='unplaced')entities=entities.filter(e=>!p.memberships.has(e.id));
    const ids=new Set(entities.map(e=>e.id));
    const roots=entities.filter(e=>!(p.parents.get(e.id)||[]).some(a=>ids.has(a.canonical_object))).sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
    const areaEdges=stage?p.material.filter(a=>ids.has(a.canonical_subject)||ids.has(a.canonical_object)):[];
    const title=stage?.title||({unplaced:'Other equipment & systems',references:'Engineering references'}[area])||'Equipment directory';
    return `<section id="pe-workspace" class="pe-workspace"><div class="pe-section-heading"><div><span class="pe-section-label">PLANT EXPLORER</span><h2>${esc(title)}</h2><p class="pe-muted">${stage?stage.description:'Search any equipment tag, name or alias, or browse the recorded component relationships.'}</p></div><div class="pe-inline">${stage?`<a class="button secondary small" href="${url({focus:parameters().get('focus')==='area'?null:'area'})}">${parameters().get('focus')==='area'?'Exit focus':'Expand area'}</a>`:''}<a class="button secondary small" href="${url({area:null,equipment:null,tab:null,q:null,focus:parameters().get('focus')?'map':null})}">Back to flow map ↑</a></div></div>${areaEntries(p,stage)}${stage?areaMap(p,stage):''}<div class="pe-directory-tools"><span>${entities.length} records · ${roots.length} root entries</span><div class="pe-inline"><a href="${url({area:'all',equipment:null,tab:null})}">All equipment</a><a href="${url({area:'unplaced',equipment:null,tab:null})}">Other systems</a><a href="${url({area:'references',equipment:null,tab:null})}">Engineering references</a></div></div>${stage?`<details class="pe-area-flow"><summary>Coal-flow links in this area (${areaEdges.length})</summary><p class="pe-help">Includes incoming, internal and outgoing branches; each retains its own source condition.</p>${areaEdges.map(a=>`<article class="pe-connection"><div class="pe-inline">${entityLink(a.canonical_subject)} → ${entityLink(a.canonical_object)} ${cite(a,'Evidence')}</div><p>${esc(a.context?.condition||'No condition specified.')}</p></article>`).join('')}</details>`:''}${entities.length?`<ul class="pe-tree pe-directory-tree">${roots.slice(0,limit).map(e=>tree(e.id)).join('')}</ul>${roots.length>limit?`<a class="button secondary" href="${url({limit:limit+60})}">Show more (${roots.length-limit} remaining)</a>`:''}`:emptyText('No equipment is placed in this group yet. Search the full directory for related records.')}<p class="pe-help">Browse groups organize the model. Expanders follow recorded “part of” relationships; shared items may appear in more than one branch.</p></section>`;
  }
  function searchResults(query){
    const p=projection(),words=query.toLowerCase().trim().split(/\s+/).filter(Boolean);if(!words.length)return '';
    const exact=e=>[e.label,...(e.aliases||[])].some(name=>name.toLowerCase()===query.toLowerCase().trim());
    const matches=[...p.entities.values()].filter(e=>words.every(w=>[e.label,...(e.aliases||[]),...(p.classes.get(e.id)||[])].join(' ').toLowerCase().includes(w))).sort((a,b)=>Number(exact(b))-Number(exact(a))||Number(p.refs.has(a.id))-Number(p.refs.has(b.id))||a.label.localeCompare(b.label,undefined,{numeric:true}));
    return `<div class="pe-search-heading" role="status">${matches.length} matches${matches.length>35?' · first 35 shown':''}</div>${matches.slice(0,35).map(e=>`<div class="pe-search-hit">${entityLink(e.id)}<span>${esc(p.refs.has(e.id)?'Engineering reference':(p.classes.get(e.id)||[]).map(nice).join(', ')||'Unclassified')}</span></div>`).join('')}${!matches.length?emptyText('No match. Try another tag or alias.'):''}`;
  }
  function searchBox(){const q=parameters().get('q')||'';return `<div class="pe-search"><label for="pe-search-input">Find equipment</label><div class="pe-search-input-row"><input type="search" id="pe-search-input" placeholder="Try EAC-1A, crusher, luffing pump…" value="${esc(q)}" autocomplete="off" aria-controls="pe-search-results"><a class="button secondary" href="${url({area:'all',equipment:null,tab:null,q:null})}">Browse all</a></div><div id="pe-search-results" class="pe-search-results" ${q?'':'hidden'}>${q?searchResults(q):''}</div></div>`;}
  function section(title,body,extra=''){return `<section class="pe-panel ${extra}"><h3>${esc(title)}</h3>${body}</section>`;}
  function childLinks(id){const p=projection(),ids=unique((p.children.get(id)||[]).map(a=>a.canonical_subject));return ids.length?`<ul class="pe-tree">${ids.map(i=>tree(i,new Set(),ids.length>3?1:0)).join('')}</ul>`:emptyText('No component hierarchy is recorded for this identity yet. This does not establish that it has no auxiliaries.');}
  function locationInfo(id){
    const p=projection(),facts=(p.outgoing.get(id)||[]).filter(a=>a.predicate==='located_at'||/^(location|equipment_location|functional_location|location_description)$/.test(a.predicate));
    const parents=unique((p.parents.get(id)||[]).map(a=>a.canonical_object));
    return facts.length?facts.map(a=>fact(a)).join(''):emptyText('Exact location is not recorded for this identity.')+(parents.length?`<p class="pe-help">Inspect its documented assembly for location context:</p><div class="pe-chip-list">${parents.map(parent=>entityLink(parent,null,'pe-chip')).join('')}</div>`:'');
  }
  function purpose(id){
    const p=projection(),own=p.outgoing.get(id)||[],facts=own.filter(a=>/^(purpose|function|description|equipment_description|operating_mode|control_role|equipment_role)$/.test(a.predicate));
    if(facts.length)return facts.map(a=>fact(a)).join('');
    const types=p.classes.get(id)||[],type=types[0],definition=state.model.ontology.find(o=>o.key===type)?.definition;
    const classification=own.find(a=>a.predicate==='instance_of');
    return `${type?`<p class="pe-purpose">${esc(nice(type))}</p>${definition?`<p>${esc(definition)}</p><p class="pe-help">Role described by the equipment classification.</p>`:''}${classification?cite(classification,'Classification source'):''}`:emptyText('Equipment purpose has not been classified yet.')}<p class="pe-help">Use its documented upstream and downstream links to inspect its role in the coal route.</p>`;
  }
  function summaryMetrics(id){
    const own=projection().outgoing.get(id)||[],keys=['rated_capacity','design_capacity','coal_rated_capacity','coal_design_capacity','quantity','individual_device_count','scheduled_nozzle_count','device_spacing','model_number','rated_flow','flow_capacity','belt_speed','drive_power_rating','motor_rated_power','hydraulic_working_pressure'];
    return keys.filter(k=>own.some(a=>a.predicate===k)).slice(0,4).map(k=>{const fs=own.filter(a=>a.predicate===k),values=unique(fs.map(a=>value(a)+' '+(a.unit||'')));return `<div class="pe-metric"><span>${esc(nice(k))}</span><strong>${esc(values.join(' / '))}</strong>${fs.map(a=>cite(a,sourceLabel(a))).join(' ')}${fs.some(a=>!PlantExplorerModel.current(a,Date.now()))?'<span class="pe-caution">Includes a value outside its recorded validity; inspect the source.</span>':''}${fs.some(a=>a.context?.condition)?`<span>${esc(unique(fs.map(a=>a.context?.condition).filter(Boolean)).join('; '))}</span>`:''}</div>`;}).join('');
  }
  function designReferences(id){
    const items=projection().designCandidates(id);
    return items.length?section('Related design dossiers',`<p class="pe-help">These records have the same equipment classification. Applicability to this particular unit has not been established; their specifications and components are not inherited.</p><div class="pe-chip-list">${items.map(e=>entityLink(e.id,null,'pe-chip')).join('')}</div>`):'';
  }
  function areaDossier(id){
    const p=projection();if(!(p.classes.get(id)||[]).includes('functional_area'))return '';
    const stage=p.stages.find(s=>p.memberships.get(id)?.has(s.id));
    return stage?areaMap(p,{...stage,title:p.entities.get(id).label},id):'';
  }
  function boundaryBody(id){
    const p=projection(),items=p.assemblyBoundary(id);
    if(!items.length)return '';
    return section('Services & boundary connections',`<p class="pe-help">Connections to this equipment and its components. Shared services remain separate assets. Each link retains its source and conditions.</p><details><summary>Inspect ${items.length} source-backed connections</summary>${items.map(a=>`<article class="pe-connection"><div class="pe-inline">${entityLink(a.canonical_subject)} <span>${esc(nice(a.predicate))}</span> ${entityLink(a.canonical_object)} ${cite(a,'Source')}</div>${a.context?.condition?`<p>${esc(a.context.condition)}</p>`:''}</article>`).join('')}</details>`);
  }
  function overviewBody(id){
    const p=projection(),own=p.outgoing.get(id)||[],coalEdges=p.material.filter(a=>a.canonical_subject===id||a.canonical_object===id),edges=coalEdges.length?coalEdges:p.networks.filter(a=>a.canonical_subject===id||a.canonical_object===id),metrics=summaryMetrics(id),children=unique((p.children.get(id)||[]).map(a=>a.canonical_subject)),applicable=p.applicable(id);
    return `${areaDossier(id)}${metrics?`<div class="pe-section-label">DOCUMENTED RATINGS & SPECIFICATIONS</div><div class="pe-metrics">${metrics}</div>`:''}<div class="pe-two-col">${section('What is it? What does it do?',purpose(id))}${section('Where is it?',locationInfo(id))}</div><div class="pe-two-col">${section('Components & auxiliaries',children.length?`<div class="pe-chip-list">${children.slice(0,10).map(i=>entityLink(i,null,'pe-chip')).join('')}</div><a class="pe-section-link" href="${url({tab:'structure'})}">Explore structure (${children.length}) →</a> <a class="pe-section-link" href="${url({tab:'assembly'})}">Find facts across this assembly →</a>`:childLinks(id))}${section(coalEdges.length?'Where does coal go?':'Connections & dependencies',edges.length?edges.slice(0,4).map(a=>connection(a,id)).join('')+`<a class="pe-section-link" href="${url({tab:'connections'})}">See all connections & branches →</a>`:(p.classes.get(id)||[]).includes('functional_area')?`<p class="pe-help">Follow the equipment flow above for the internal route. Shared supplies and incoming/outgoing connections are listed under Services & boundary connections below.</p>`:emptyText('No current documented directed connection is recorded for this identity.'))}</div>${applicable.length?section('Explicitly applicable engineering information',`<div class="pe-applicable-list">${applicable.map(a=>`<div>${entityLink(a.canonical_subject)}<span>${esc(nice(a.predicate))}</span>${cite(a,'Scope source')}</div>`).join('')}</div><p class="pe-help">These references explicitly name this identity. Similar equipment names alone do not establish applicability.</p>`):''}${boundaryBody(id)}${locatedBody(id)}${designReferences(id)}${own.some(a=>a.predicate==='document_note')?section('Equipment notes',own.filter(a=>a.predicate==='document_note').map(a=>fact(a)).join('')):''}`;
  }
  function structureBody(id){
    const p=projection(),parents=p.parents.get(id)||[],related=[...(p.outgoing.get(id)||[]),...(p.incoming.get(id)||[])].filter(a=>['serves','supplies_water_to','serves_equipment','covered_by','monitors_equipment','protects_equipment','sprays_at','associated_with','utility_supply_to'].includes(a.predicate));
    return `<div class="pe-two-col">${section('Assembly / system membership',parents.length?parents.map(a=>fact(a)).join(''):emptyText('No parent equipment or system is recorded.'))}${section('Location',locationInfo(id))}</div>${section('Subsystems, auxiliaries & components',childLinks(id))}${locatedBody(id)}${designReferences(id)}${section('Shared services & related equipment',related.length?related.map(a=>`<article class="pe-connection">${entityLink(a.canonical_subject)} <span>${esc(nice(a.predicate))}</span> ${entityLink(a.canonical_object)} ${cite(a,'Source')}</article>`).join(''):emptyText('No shared-service relationship is recorded for this identity.'))}`;
  }
  function locatedBody(id){
    const p=projection(),items=(p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at'&&PlantExplorerModel.current(a,Date.now()));
    const groups=new Map();for(const a of items){if(!groups.has(a.canonical_subject))groups.set(a.canonical_subject,[]);groups.get(a.canonical_subject).push(a);}
    return items.length?section('Equipment located here',`<p class="pe-help">Physical location links: equipment can belong to its conveyor or shared system and still be reached from this transfer point.</p><div class="pe-located">${[...groups].map(([key,facts])=>`<article>${entityLink(key)} ${facts.map((a,i)=>cite(a,'Location source'+(facts.length>1?' '+(i+1):''))).join(' ')}</article>`).join('')}</div>`):'';
  }
  function assemblyGroups(id,query=''){
    const p=projection(),q=query.trim().toLowerCase(),category=document.getElementById('pe-assembly-category')?.value||'all';
    const rows=p.assembly(id).map(item=>{
      const fs=item.facts.filter(a=>a.predicate!=='instance_of'&&a.predicate!=='part_of');
      const matches=fs.filter(a=>(category==='all'||(category==='gaps'?/^source_(gap|discrepancy)$/.test(a.predicate):PlantExplorerModel.factGroup(a)===category))&&(!q||[item.entity.label,nice(a.predicate),value(a),a.unit,a.context?.condition].join(' ').toLowerCase().includes(q)));
      return {...item,matches};
    }).filter(item=>item.matches.length);
    return `<p class="pe-help" role="status">${rows.reduce((n,item)=>n+item.matches.length,0)} facts across ${rows.length} equipment / component records</p>`+rows.map(item=>`<details class="pe-assembly-group" ${q||category!=='all'?'open':''}><summary>${esc(item.entity.label)} <span class="pe-tree-count">${item.matches.length} facts</span></summary><p>${entityLink(item.id,'Open component')} ${item.parent?`<span class="pe-muted"> · Part of </span>${entityLink(item.parent)}`:''}</p>${item.matches.map(a=>fact(a)).join('')}</details>`).join('')+(!rows.length?emptyText('No matching documented facts in this assembly.'):'');
  }
  function assemblyBody(id){
    return `<section class="pe-panel"><h3>Every component, with its own evidence</h3><p class="pe-help">Search this equipment and its component tree together. Open any source beside a value, or open a component for its connections and history.</p><div class="pe-assembly-tools"><label>Find a component or fact<input id="pe-assembly-search" type="search" placeholder="PCS, oil, torque, nozzle, 22 kW…" aria-controls="pe-assembly-results"></label><label>Information<select id="pe-assembly-category"><option value="all">All facts</option><option value="protection">Protections & interlocks</option><option value="limits">Ratings & ranges</option><option value="mechanical">Mechanical & maintenance</option><option value="operation">Operation</option><option value="gaps">Gaps & discrepancies</option></select></label></div><div id="pe-assembly-results">${assemblyGroups(id)}</div></section>`;
  }
  function connectionsBody(id){
    const p=projection(),all=p.networks.filter(a=>a.canonical_subject===id||a.canonical_object===id),network=parameters().get('network')||['material','utility','control','mechanical','electrical'].find(n=>all.some(a=>a.context.network===n))||'material',edges=all.filter(a=>a.context.network===network),ins=edges.filter(a=>a.canonical_object===id),outs=edges.filter(a=>a.canonical_subject===id);
    const raw=(p.outgoing.get(id)||[]).concat(p.incoming.get(id)||[]).filter(a=>a.context?.kind==='connection'&&!all.includes(a));
    return `<div class="pe-network-tabs">${['material','utility','control','mechanical','electrical'].map(n=>`<a class="pe-path ${n===network?'is-active':''}" href="${url({tab:'connections',network:n})}" ${n===network?'aria-current="true"':''}>${n==='material'?'Coal flow':nice(n)} <span>${all.filter(a=>a.context.network===n).length}</span></a>`).join('')}</div><p class="pe-help">Every branch below is a documented possibility. Conditions are shown per connection; this view does not combine them into a live route or isolation boundary.</p><div class="pe-local-flow"><section><h3>Upstream / supplying</h3>${ins.map(a=>connection(a,id)).join('')||emptyText('No documented incoming link in this network.')}</section><div class="pe-flow-focus"><span>${network==='material'?'COAL FLOW':'SELECTED EQUIPMENT'}</span><strong>${esc(p.entities.get(id).label)}</strong></div><section><h3>Downstream / next branches</h3>${outs.map(a=>connection(a,id)).join('')||emptyText('No documented outgoing link in this network.')}</section></div>${raw.length?`<details class="pe-panel"><summary>Other connection records (${raw.length})</summary><p class="pe-help">Not included above: outside recorded validity, unverified, or inferred.</p>${raw.map(a=>fact(a)).join('')}</details>`:''}`;
  }
  function relatedGroups(items){
    const groups=new Map();
    for(const item of items){const key=item.via.canonical_subject;if(!groups.has(key))groups.set(key,{via:item.via,facts:[]});groups.get(key).facts.push(item.fact);}
    return [...groups].map(([id,group])=>`<details class="pe-related"><summary>${esc(projection().entities.get(id).label)} · ${group.facts.length} requirements / values</summary><p class="pe-help">Explicitly linked to this equipment. ${cite(group.via,'Applicability source')} · ${entityLink(id,'Open reference')}</p>${unique(group.facts).map(a=>fact(a)).join('')}</details>`).join('');
  }
  function factsBody(id,mode){
    const p=projection(),own=(p.outgoing.get(id)||[]).filter(a=>!a.canonical_object&&a.predicate!=='instance_of'),related=p.relatedFacts(id),parents=(p.parents.get(id)||[]).filter(a=>p.entities.get(a.canonical_object)?.label!=='Maitree Coal Handling Plant');
    const groups=mode==='operation'?[['operation','How it operates'],['protection','Protection, permissives & interlocks'],['limits','Capacities, ranges & setpoints']]:[['mechanical','Structure, drive & maintenance information'],['reference','Other engineering information']];
    return `<p class="pe-help">Source-stated requirements and specifications. Design limits, calculations and instrument ranges retain their original basis; they are not live readings or automatically approved operating settings.</p>${parents.length?section('Related assembly information',`<p class="pe-help">System-level requirements may be recorded on the parent assembly. Open it to inspect its own operating and maintenance information.</p><div class="pe-chip-list">${unique(parents.map(a=>a.canonical_object)).map(parent=>entityLink(parent,null,'pe-chip')).join('')}</div>`):''}${groups.map(([key,title])=>{const fs=own.filter(a=>PlantExplorerModel.factGroup(a)===key),rs=related.filter(x=>PlantExplorerModel.factGroup(x.fact)===key);return section(title,fs.map(a=>fact(a)).join('')+(!fs.length?emptyText('No direct information recorded in this category.'):'' )+relatedGroups(rs));}).join('')}`;
  }
  function sourcesBody(id){
    const p=projection(),index=evidenceIndex(),items=[...(p.outgoing.get(id)||[]),...(p.incoming.get(id)||[]),...p.relatedFacts(id).map(x=>x.fact)],ids=unique(items.flatMap(a=>(a.evidence||[]).map(s=>s.evidence_id))),docs=new Map();
    for(const eid of ids){const row=index.get(eid),key=row?.document_id||'unknown';if(!docs.has(key))docs.set(key,[]);docs.get(key).push(row||{id:eid,locator:'Source evidence'});}
    const records=(state.events||[]).filter(e=>e.canonical_equipment===id);
    return section('Source documents & exact pages',[...docs].map(([key,rows])=>{const d=state.documents.find(d=>d.id===key);return `<article class="pe-document"><strong>${esc(d?.name||'Source evidence')}</strong><p>${esc(d?.revision||'Revision not specified')}</p><div class="pe-inline">${rows.sort((a,b)=>(a.page||0)-(b.page||0)).map(r=>`<button class="button secondary small" data-action="evidence" data-id="${esc(r.id)}">${esc(r.locator||'Page '+r.page)}</button>`).join('')}</div></article>`;}).join('')||emptyText('No cited source pages are recorded.'))+section('Operating & maintenance history',records.length?eventCards(records):emptyText('No observations, inspections or repairs have been recorded for this equipment yet.'))+(canRecord(id)?`<button class="button secondary" data-action="plant-record" data-id="${esc(id)}">Record an observation / maintenance event</button>`:'');
  }
  function equipment(p,id){
    const e=p.entities.get(id);if(!e)return section('Equipment unavailable','<p>This identity is not active in the current model.</p><a href="#overview">Return to plant overview</a>');
    const tab=parameters().get('tab')||'overview',stage=p.stages.find(s=>s.id===parameters().get('area')&&p.memberships.get(id)?.has(s.id))||p.stages.find(s=>p.memberships.get(id)?.has(s.id)),parents=p.parents.get(id)||[],qualified=p.qualifications(id);
    const tabs=[['overview','Overview'],['structure','Structure & auxiliaries'],['assembly','Assembly facts'],['connections','Connections'],['operation','Operation & protection'],['mechanical','Mechanical & maintenance'],['sources','Sources & history']];
    return `<section class="pe-equipment" id="pe-workspace"><nav class="pe-breadcrumbs" aria-label="Equipment breadcrumb"><a href="#overview">Plant overview</a><span>/</span>${stage?`<a href="${url({area:stage.id,equipment:null,tab:null})}">${stage.short}</a><span>/</span>`:''}${parents.filter(a=>p.entities.get(a.canonical_object)?.label!=='Maitree Coal Handling Plant').slice(0,2).map(a=>entityLink(a.canonical_object)+'<span>/</span>').join('')}<span>${esc(e.label)}</span></nav><div class="pe-equipment-heading"><div><span class="pe-section-label">${p.refs.has(id)?'ENGINEERING REFERENCE':'EQUIPMENT KNOWLEDGE'}</span><h2>${esc(e.label)}</h2><p>${esc((p.classes.get(id)||[]).map(nice).join(' · ')||'Classification not recorded')}</p>${unique(e.aliases||[]).filter(a=>a!==e.label).length?`<details class="pe-aliases"><summary>Other names & tags</summary>${esc(unique(e.aliases).filter(a=>a!==e.label).join(' · '))}</details>`:''}</div>${canRecord(id)?`<button class="button secondary small" data-action="plant-record" data-id="${esc(id)}">Add operating record</button>`:''}</div>${qualified.length?`<details class="pe-qualifications"><summary>${qualified.length} source qualification${qualified.length===1?'':'s'} to review</summary>${qualified.map(x=>fact(x.fact,x.via)).join('')}</details>`:''}<nav class="pe-detail-tabs" aria-label="Equipment information">${tabs.map(([key,title])=>`<a href="${url({tab:key})}" ${key===tab?'aria-current="page"':''}>${title}</a>`).join('')}</nav><div class="pe-detail-body">${tab==='structure'?structureBody(id):tab==='assembly'?assemblyBody(id):tab==='connections'?connectionsBody(id):tab==='operation'||tab==='mechanical'?factsBody(id,tab):tab==='sources'?sourcesBody(id):overviewBody(id)}</div><details class="pe-all-facts"><summary>All direct source claims (${(p.outgoing.get(id)||[]).length})</summary>${(p.outgoing.get(id)||[]).map(a=>fact(a)).join('')}</details></section>`;
  }
  function view(){
    const p=projection(),q=parameters(),id=q.get('equipment'),area=q.get('area');
    if(q.get('view')!=='records')return PlantScene.view(p,{fact});
    return `<div class="pe-root"><header class="pe-header"><div><div class="pe-eyebrow">MAITREE · COAL HANDLING PLANT</div><h1>Coal flow <span>overview</span></h1><p>Follow the route. Explore equipment, auxiliaries and operating information.</p></div><div class="pe-model-note"><span class="pe-model-dot"></span><div><strong>Documented plant model</strong><span>v${p.version} · Design knowledge, no live telemetry</span></div></div></header>${searchBox()}${id?`<a class="pe-back" href="${url({equipment:null,tab:null})}">← ${area?'Back to process group':'Back to coal-flow overview'}</a>${equipment(p,id)}`:`${pathPicker(p)}<section class="pe-map-panel">${map(p)}</section>${area?directory(p):`<div class="pe-bottom-links"><a href="${url({area:'unplaced'})}"><strong>Utilities & other equipment</strong><span>Find systems beyond the main coal route →</span></a><a href="#desk"><strong>Operations desk</strong><span>Observations, open issues and recent work →</span></a><a href="${url({area:'references'})}"><strong>Engineering references</strong><span>Control schemes and calculation records →</span></a></div>`}`}</div>`;
  }
  function drawLines(){
    const box=document.getElementById('pe-flow-map'),svg=document.getElementById('pe-flow-lines');if(!box||!svg)return;
    if(window.matchMedia('(max-width:760px)').matches){svg.innerHTML='';return;}
    const p=projection(),path=p.paths.find(x=>x.id===parameters().get('path')),bounds=box.getBoundingClientRect(),rects={};
    box.querySelectorAll('[data-stage]').forEach(el=>{const r=el.getBoundingClientRect();rects[el.dataset.stage]={x:r.left-bounds.left,y:r.top-bounds.top,w:r.width,h:r.height};});
    svg.setAttribute('viewBox',`0 0 ${box.clientWidth} ${box.clientHeight}`);
    svg.innerHTML=`<defs><marker id="pe-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="currentColor"/></marker></defs>`+p.links.map(l=>{
      const a=rects[l.from],b=rects[l.to];if(!a||!b)return '';
      let d;const sameRow=Math.abs(a.y-b.y)<10,sameCol=Math.abs(a.x-b.x)<10;
      if(sameRow){const right=b.x>a.x;d=`M${right?a.x+a.w:a.x},${a.y+a.h/2} H${right?b.x-5:b.x+b.w+5}`;}
      else if(sameCol){const down=b.y>a.y;d=`M${a.x+a.w/2},${down?a.y+a.h:a.y} V${down?b.y-5:b.y+b.h+5}`;}
      else{const down=b.y>a.y,sy=down?a.y+a.h:a.y,ey=down?b.y:b.y+b.h,my=(sy+ey)/2;d=`M${a.x+a.w/2},${sy} V${my} H${b.x+b.w/2} V${ey+(down?-5:5)}`;}
      const muted=path&&(!path.stages.includes(l.from)||!path.stages.includes(l.to));
      return `<path aria-hidden="true" class="pe-flow-line ${muted?'is-muted':''}" d="${d}" marker-end="url(#pe-arrow)"/><path class="pe-flow-hit" d="${d}" data-action="plant-branch" data-id="${l.id}" tabindex="0" role="button" aria-label="Inspect coal flow from ${esc(p.stages.find(s=>s.id===l.from).title)} to ${esc(p.stages.find(s=>s.id===l.to).title)}"/>`;
    }).join('');
  }
  function bind(){
    resizeObserver?.disconnect();
    PlantScene.bind();
    if(document.querySelector('.ps-root')){document.body.classList.remove('pe-focus-mode','pe-area-focus');return;}
    const focus=route()==='overview'&&!parameters().get('equipment'),areaFocus=focus&&parameters().get('focus')==='area'&&!!parameters().get('area');
    document.body.classList.toggle('pe-focus-mode',!!(areaFocus||focus&&parameters().get('focus')==='map'&&!parameters().get('area')));
    document.body.classList.toggle('pe-area-focus',!!areaFocus);
    const input=document.getElementById('pe-search-input');if(input)input.oninput=()=>{const el=document.getElementById('pe-search-results');el.hidden=!input.value.trim();el.innerHTML=searchResults(input.value);};
    const assemblySearch=document.getElementById('pe-assembly-search'),assemblyCategory=document.getElementById('pe-assembly-category');
    if(assemblySearch){const update=()=>{document.getElementById('pe-assembly-results').innerHTML=assemblyGroups(parameters().get('equipment'),assemblySearch.value);};assemblySearch.oninput=update;assemblyCategory.onchange=update;}
    const map=document.getElementById('pe-flow-map');if(map){resizeObserver=new ResizeObserver(drawLines);resizeObserver.observe(map);drawLines();}
    if(parameters().get('area')||parameters().get('equipment'))requestAnimationFrame(()=>document.getElementById('pe-workspace')?.scrollIntoView({block:'start'}));
  }
  async function action(name,el){
    if(await PlantScene.action(name,el))return true;
    if(name==='plant-record'){if(canRecord(el.dataset.id)){selectedEntity=el.dataset.id;eventEditor();}return true;}
    if(name==='plant-flow-edge'){
      const p=projection(),a=p.material.find(a=>a.id===el.dataset.id);if(!a)return true;
      const facts=p.material.filter(x=>x.canonical_subject===a.canonical_subject&&x.canonical_object===a.canonical_object);
      modal('Documented equipment connection',`<h3>${esc(p.entities.get(a.canonical_subject).label)} → ${esc(p.entities.get(a.canonical_object).label)}</h3>${facts.map(a=>fact(a)).join('')}`);
      document.querySelectorAll('#dialog-body a[href^="#overview"]').forEach(a=>a.addEventListener('click',closeModal,{once:true}));return true;
    }
    if(name==='plant-branch'){
      const p=projection(),l=p.links.find(x=>x.id===el.dataset.id);if(!l)return true;
      modal('Documented coal-flow branch',`<h3>${p.stages.find(s=>s.id===l.from).title} → ${p.stages.find(s=>s.id===l.to).title}</h3><p class="pe-help">Each item is a recorded link. Gate positions, flow splits and source qualifications are retained below.</p>${l.facts.map(a=>`<article class="pe-connection"><div class="pe-inline">${entityLink(a.canonical_subject)}<span>→</span>${entityLink(a.canonical_object)} ${cite(a,'Evidence')}</div><p>${esc(a.context?.condition||'No operating condition specified.')}</p></article>`).join('')}`);
      document.querySelectorAll('#dialog-body a[href^="#overview"]').forEach(a=>a.addEventListener('click',closeModal,{once:true}));return true;
    }
    return false;
  }
  return {view,bind,action};
})();
