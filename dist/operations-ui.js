'use strict';
let sourceQuery='', sourceResults=null, networkResult=null, migrationResult=null, eventFilter='', showAllNetworkPaths=false;
const networkNames=['material','mechanical','electrical','control','utility'];

function getOpsProjection(){
  return (typeof PlantExplorer!=='undefined'&&PlantExplorer.projection)?PlantExplorer.projection():PlantExplorerModel.build(state.model);
}

function defaultEquipmentId(){
  if(selectedEntity&&state.model.entities.some(e=>e.id===selectedEntity&&e.canonical_id===e.id&&!e.inactive&&e.category!=='document'))return selectedEntity;
  const p=getOpsProjection();
  const pref=['Coal Ship Unloader-1','EAC-1A','UEF-1','UEE-1','EAC-3A','UEE-2','UEE-3','EBC-1','EBA-18A'];
  for(const lbl of pref){
    const found=[...p.entities.values()].find(e=>e.label===lbl);
    if(found)return found.id;
  }
  return [...p.entities.values()].find(e=>e.category!=='document')?.id||'';
}

function equipmentOptions(selected='',filterQuery=''){
  const p=getOpsProjection();
  const active=[...p.entities.values()].filter(e=>e.canonical_id===e.id&&!e.inactive&&e.category!=='document'&&!p.refs.has(e.id));
  const targetId=selected||defaultEquipmentId();
  const q=String(filterQuery||'').trim();
  const fmtOpt=e=>{
    const cn=PlantExplorerModel.commonName(p,e.id);
    return cn&&!cn.startsWith('at ')?`${e.label} (${cn})`:e.label;
  };
  if(q){
    const matches=PlantExplorerModel.searchEntities(p,q).filter(e=>e.category!=='document'&&!p.refs.has(e.id)).slice(0,160);
    const chosenId=matches.some(e=>e.id===targetId)?targetId:(matches[0]?.id||'');
    if(!matches.length)return `<option value="">No matching equipment for "${esc(q)}"</option>`;
    return matches.map(e=>{
      const tier=PlantExplorerModel.isPrimaryEquipment(p,e.id)?'★ ':'';
      return `<option value="${esc(e.id)}" ${e.id===chosenId?'selected':''}>${esc(tier+fmtOpt(e))}</option>`;
    }).join('');
  }
  const primary=[],subAssy=[];
  for(const e of active){
    if(PlantExplorerModel.isPrimaryEquipment(p,e.id))primary.push(e);
    else if(!/^\d{2}[A-Z]{2}\d*:/.test(e.label))subAssy.push(e);
  }
  primary.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
  subAssy.sort((a,b)=>a.label.localeCompare(b.label,undefined,{numeric:true}));
  const selEntity=targetId?p.entities.get(targetId):null;
  const selectedOpt=selEntity&&selEntity.category!=='document'?`<optgroup label="Selected Equipment"><option value="${esc(selEntity.id)}" selected>${esc(fmtOpt(selEntity))}</option></optgroup>`:'';
  return `${selectedOpt}<optgroup label="Primary Plant Equipment (${primary.length})">${primary.filter(e=>e.id!==targetId).map(e=>`<option value="${esc(e.id)}">${esc(fmtOpt(e))}</option>`).join('')}</optgroup><optgroup label="Sub-Assemblies & Major Components (${Math.min(subAssy.length,400)} shown · type above to search all ${active.length})">${subAssy.filter(e=>e.id!==targetId).slice(0,400).map(e=>`<option value="${esc(e.id)}">${esc(e.label)}</option>`).join('')}</optgroup>`;
}

function equipmentPicker(selectId,selected='',required=false){
  const targetId=selected||defaultEquipmentId();
  return `<div class="ops-picker-wrap"><input type="search" class="ops-equip-filter" data-target="${esc(selectId)}" placeholder="Filter by tag or alias (e.g. TP-5, PSH, CBSH, CRH, BCN-5A, eac5a)…" aria-label="Filter equipment list" autocomplete="off"><select id="${esc(selectId)}" ${required?'required':''}>${equipmentOptions(targetId,'')}</select></div>`;
}

function opsLink(text,hash){return `<a class="button secondary" href="#${hash}">${esc(text)}</a>`;}

function eventCards(items){return items.map(e=>`<article class="activity-row"><div class="inline-list">${badge(e.event_type,'blue')}${badge(e.current_status,e.current_status==='open'?'amber':'')}<button class="entity-button" data-action="equipment-page" data-id="${e.canonical_equipment}">${esc(label(e.canonical_equipment,state.model))}</button></div><h3>${esc(e.summary)}</h3><div class="sub">Occurred ${esc(fmt(e.occurred_at))} · recorded ${esc(fmt(e.recorded_at))}</div><p style="white-space:pre-wrap">${esc(e.details)}</p>${(e.measurements||[]).map(r=>`<p><strong>${esc(r.quantity)}: ${esc(r.value)} ${esc(r.unit)}</strong> ${esc(r.condition||'Condition unspecified')} ${esc(r.instrument||'')}</p>`).join('')}${e.related_event?`<div class="sub">Linked event: ${esc(e.related_event)}</div>`:''}<div class="inline-list">${(e.provenance.evidence||[]).map(s=>btn('Source','evidence',`data-id="${esc(s.evidence_id)}"`,'ghost small')).join('')}${btn('Add follow-up','event-followup',`data-id="${e.id}"`,'secondary small')}</div><span class="sub">${esc(e.id)}</span></article>`).join('')||'<div class="card-body muted">No records in this view yet.</div>';}

function operationsHome(){const allRecords=state.events||[],filtered=allRecords.filter(e=>!eventFilter||[e.summary,e.details,label(e.canonical_equipment,state.model),...(getOpsProjection().searchAliases?.get(e.canonical_equipment)||[])].join(' ').toLowerCase().includes(eventFilter.toLowerCase())),open=filtered.filter(e=>e.current_status==='open');return heading('Operations desk & shift log','Find source evidence, trace documented multi-hop connections, and record shift observations or breakdowns.',btn('＋ Record shift / breakdown','new-event','',''))+`<div class="stats"><div class="stat"><div class="stat-top">Equipment identities</div><span class="stat-number">${state.model.entities.filter(e=>e.canonical_id===e.id&&!e.inactive&&e.category!=='document').length}</span><small>Reviewed plant model</small></div><div class="stat"><div class="stat-top">Open issues</div><span class="stat-number amber">${allRecords.filter(e=>e.current_status==='open').length}</span><small>Reported issues & follow-ups</small></div><div class="stat"><div class="stat-top">Operational records</div><span class="stat-number">${allRecords.length}</span><small>Observations, actions & outcomes</small></div><div class="stat"><div class="stat-top">Source documents</div><span class="stat-number">${state.documents.length}</span><small>Originals & evidence retained</small></div></div><div class="ops-questions"><a href="#overview"><strong>Explore plant schematic & equipment</strong><span>Navigate the 2.5D buildings, 1D conveyor loops & dossiers.</span></a><a href="#sources"><strong>Where is the applicable source?</strong><span>Search extracted text, drawing titles, revisions & page crops.</span></a><a href="#networks"><strong>What connects to this equipment?</strong><span>Trace documented coal, drive, utility, power & control paths.</span></a></div><div class="toolbar" style="margin:18px 0"><form id="event-filter-form" class="inline-list" style="flex:1"><input id="event-filter" class="search" aria-label="Search operating history" value="${esc(eventFilter)}" placeholder="Filter shift log by equipment tag, symptom or repair…"><button class="button secondary small">Filter log</button>${eventFilter?btn('Clear','clear-event-filter','','ghost small'):''}</form><div class="inline-list">${opsLink('Correct model facts','corrections')}${btn('Audit data coverage','load-migration','','secondary small')}${btn('＋ Import document','upload','','secondary small')}${workspace==='demo'?btn('Next walkthrough sample','demo-next','','secondary small'):''}</div></div><div class="ops-columns"><section class="card"><div class="card-head"><h2>Open issues & actions (${open.length})</h2></div>${eventCards(open.slice(0,12))}</section><section class="card"><div class="card-head"><h2>Operating history (${filtered.length})</h2></div>${eventCards(filtered.slice(0,12))}</section></div>`;}

function sourceSearchView(){return heading('Find source evidence','Search original text, names, revisions and page locators.')+`<form id="source-search-form" class="toolbar"><input id="source-query" aria-label="Search source evidence" class="search" value="${esc(sourceQuery)}" placeholder="Equipment tag, component or phrase" required maxlength="300"><button class="button">Search sources</button></form><p class="micro">All entered words must match. This searches extracted text; unreadable image text is not automatically indexed. Open the original drawing to inspect it.</p>${sourceResults?`<p>${sourceResults.total} matching evidence blocks${sourceResults.total>40?' · showing first 40':''}</p><section class="card">${sourceResults.results.map(s=>`<article class="activity-row"><h3>${esc(s.name)}</h3><div class="inline-list">${badge(s.revision||'Revision unknown')}${badge(s.authority)}</div><p class="sub">${esc(s.locator)} · page/sheet ${s.page}</p><p style="white-space:pre-wrap">${esc(s.snippet||'Image evidence; inspect page')}</p>${btn('Open evidence',s.support?'indexed-source':'evidence',`data-id="${s.id}" data-note="${s.index_note_id||''}"`,'secondary small')} ${btn('Open document','document',`data-id="${s.document_id}"`,'ghost small')}</article>`).join('')||'<div class="card-body">No exact matches. Try an alias or document name.</div>'}</section>`:''}`;}

function networkView(){
  const eqId=networkResult?.equipment||defaultEquipmentId();
  const dir=networkResult?.direction||'downstream';
  const followAll=networkResult?Boolean(networkResult.follow_all):true;
  const availConds=networkResult?.available_conditions||[];
  const visiblePaths=networkResult?(showAllNetworkPaths?networkResult.paths:networkResult.paths.slice(0,30)):[];
  return heading('Trace equipment connections','Multi-hop tracing across documented coal, mechanical, electrical, utility, and control networks.')+
    `<form id="network-form" class="card card-body"><div class="ops-form-grid"><label>Equipment${equipmentPicker('network-equipment',eqId)}</label><label>Network<select id="network-kind">${networkNames.map(n=>`<option ${networkResult?.network===n?'selected':''}>${n}</option>`).join('')}</select></label><label>Direction<select id="network-direction"><option value="downstream" ${dir==='downstream'?'selected':''}>Downstream / supplied →</option><option value="upstream" ${dir==='upstream'?'selected':''}>← Upstream / supplying</option></select></label><label>Condition filter (optional substring or exact)<input id="network-condition" value="${esc(networkResult?.condition||'')}" placeholder="Blank = all branches, or e.g. Bunker-A, bypass…"></label></div><label class="checkbox-label" style="margin-top:12px"><input type="checkbox" id="network-follow-all" ${followAll?'checked':''}><span><strong>Follow all documented route branches</strong> — traverse conditional gates, diverters, and chutes and display each step’s operating condition inline</span></label><div class="inline-list" style="margin-top:14px"><button class="button">Trace documented connections</button>${eqId?`<a class="button secondary small" href="#overview?equipment=${encodeURIComponent(eqId)}">Open ${esc(label(eqId,state.model))} schematic ↗</a>`:''}</div></form>`+
    (availConds.length?`<div class="card card-body" style="margin-bottom:14px"><div class="sub" style="margin-bottom:8px"><strong>Documented branch conditions encountered (${availConds.length})</strong> — click a condition to filter paths:</div><div class="inline-list" style="flex-wrap:wrap;gap:6px"><button type="button" class="button ${!networkResult?.condition?'':'secondary'} small" data-action="network-cond-chip" data-cond="">All branches (${networkResult.paths.length})</button>${availConds.slice(0,18).map(c=>`<button type="button" class="button ${networkResult?.condition===c?'':'secondary'} small" data-action="network-cond-chip" data-cond="${esc(c)}">${esc(c.length>48?c.slice(0,46)+'…':c)}</button>`).join('')}</div></div>`:'')+
    `<div class="notice">Possible documented connections only. Unverified links remain boundaries. This view does not establish live route state, complete coverage or isolation safety.</div>`+
    (networkResult?`<section class="card"><div class="card-head"><h2>${networkResult.paths.length} reachable items from ${esc(label(networkResult.equipment,state.model))}</h2><div class="inline-list">${badge(networkResult.follow_all?'All documented branches':'Strict condition mode',networkResult.follow_all?'green':'amber')}${badge(networkResult.edges.length+' edges traversed','blue')}</div></div>${visiblePaths.map(p=>`<article class="activity-row"><div class="inline-list"><strong><a href="#overview?equipment=${encodeURIComponent(p.equipment)}">${esc(p.label)}</a></strong>${badge(p.steps.length+' hop'+(p.steps.length===1?'':'s'))}</div><p>${esc([label(networkResult.equipment,state.model),...p.steps.map(s=>label(s.to,state.model))].join(' → '))}</p>${p.steps.map(s=>`<div class="sub" style="margin-top:4px">${esc(label(s.from,state.model))} → <strong>${esc(label(s.to,state.model))}</strong> · ${esc(s.predicate.replaceAll('_',' '))}${s.context?.from_port||s.context?.to_port?` (${esc(s.context.from_port||'port')} → ${esc(s.context.to_port||'port')})`:''} ${s.context?.condition?badge(s.context.condition,'amber'):''} ${btn('Connection evidence','fact-source',`data-id="${s.assertion_id}" data-support="0"`,'ghost small')}</div>`).join('')}</article>`).join('')||'<div class="card-body">No documented paths found for this filter. Try enabling “Follow all documented route branches” or clearing the condition filter.</div>'}${networkResult.paths.length>30?`<div class="card-body"><button type="button" class="button secondary small" data-action="toggle-network-paths">${showAllNetworkPaths?'Show first 30 reachable items':`Show all ${networkResult.paths.length} reachable items`}</button></div>`:''}<details class="card-body"><summary><strong>All traversed connections (${networkResult.edges.length}) & unresolved boundaries (${networkResult.excluded.length})</strong></summary><h3>All traversed connections (${networkResult.edges.length})</h3>${networkResult.edges.slice(0,80).map(a=>`<p>${esc(label(a.canonical_subject,state.model))} → ${esc(label(a.canonical_object,state.model))} ${a.context?.condition?badge(a.context.condition,'amber'):''} ${btn('Evidence','fact-source',`data-id="${a.id}" data-support="0"`,'ghost small')}</p>`).join('')}<h3>Unresolved boundaries (${networkResult.excluded.length})</h3>${networkResult.excluded.slice(0,60).map(x=>`<p>${esc(label(x.at,state.model))}: ${esc(x.reason)} ${esc(x.context?.condition||'')}</p>`).join('')||'<p class="muted">No excluded links encountered. Missing undocumented links remain unknown.</p>'}</details></section>`:'');
}

function logView(){const records=(state.events||[]).filter(e=>!eventFilter||[e.summary,e.details,label(e.canonical_equipment,state.model),...(getOpsProjection().searchAliases?.get(e.canonical_equipment)||[])].join(' ').toLowerCase().includes(eventFilter.toLowerCase()));return heading('Operating history','Observations, breakdowns, actions, outcomes and lessons.',btn('Add record','new-event','',''))+`<form id="event-filter-form" class="toolbar"><input id="event-filter" class="search" aria-label="Search operating history" value="${esc(eventFilter)}" placeholder="Equipment, symptom or repair"><button class="button secondary">Find previous cases</button></form><section class="card">${eventCards(records)}</section>`;}

function bindEquipmentPickers(root=document){
  root.querySelectorAll('.ops-equip-filter').forEach(inp=>{
    if(inp._bound)return;
    inp._bound=true;
    inp.addEventListener('input',()=>{
      const sel=document.getElementById(inp.dataset.target);
      if(!sel)return;
      const prev=sel.value;
      sel.innerHTML=equipmentOptions(prev,inp.value);
      sel.dispatchEvent(new Event('change',{bubbles:true}));
    });
  });
}

function eventEditor(related=null){const equipment=related?.canonical_equipment||defaultEquipmentId();const local=new Date(Date.now()-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16);modal(related?'Record a follow-up':'Record shift / breakdown',`<form id="event-form"><div class="ops-form-grid"><label>Equipment${equipmentPicker('event-equipment',equipment,true)}</label><label>Record type<select id="event-type">${['observation','reading','breakdown','inspection','repair','replacement','action','outcome','lesson','correction'].map(t=>`<option ${t===(related?'outcome':'observation')?'selected':''}>${t}</option>`).join('')}</select></label><label>Occurred at (this computer’s local time)<input type="datetime-local" id="event-time" value="${local}" required></label><label>Status<select id="event-status"><option value="recorded">Recorded</option><option value="open">Open issue / action</option><option value="closed">Closed / resolved</option><option value="hypothesis">Hypothesis</option></select></label></div><label>Summary<input id="event-summary" maxlength="2000" required></label><label>Observations, readings with units, condition, action and outcome<textarea id="event-details" rows="6" maxlength="12000" required></textarea></label><details><summary>Add a structured reading (optional)</summary><div class="ops-form-grid"><label>Quantity<input id="reading-quantity" placeholder="bearing temperature"></label><label>Value<input id="reading-value" type="number" step="any"></label><label>Unit<input id="reading-unit" placeholder="degC"></label><label>Operating condition<input id="reading-condition"></label><label>Instrument<input id="reading-instrument"></label></div></details><label>Operator name<input id="event-author" maxlength="120" required></label>${related?`<p>Follow-up to ${esc(related.summary)} (${esc(related.id)}). Closing this follow-up updates that record’s displayed status.</p>`:''}<input type="hidden" id="event-related" value="${esc(related?.id||'')}"><p class="micro">Saving records your submitted observation with its time and source. It does not change equipment specifications. Lessons start as hypotheses.</p><div class="dialog-actions"><button class="button">Save operating record</button></div></form>`);bindEquipmentPickers(document.getElementById('dialog'));$('#event-form').onsubmit=async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{const type=$('#event-type').value;await api('/api/events',{expected_version:state.model.version,author:$('#event-author').value,reason:$('#event-details').value,event:{op:'event',equipment:$('#event-equipment').value,event_type:type,occurred_at:new Date($('#event-time').value).toISOString(),summary:$('#event-summary').value,details:$('#event-details').value,status:type==='lesson'?'hypothesis':$('#event-status').value,related_event:$('#event-related').value,measurements:$('#reading-quantity').value?[{quantity:$('#reading-quantity').value,value:$('#reading-value').value===''?null:Number($('#reading-value').value),unit:$('#reading-unit').value,...($('#reading-condition').value?{condition:$('#reading-condition').value}:{}),...($('#reading-instrument').value?{instrument:$('#reading-instrument').value}:{})}]:[]}});closeModal();await refresh(true);toast('Operating record saved with source and timestamp.');}catch(err){toast(err.message,true);button.disabled=false;}};}

function correctionsView(){return heading('Correct the working model','Stage corrections, inspect their scope, then accept them in Review changes.')+`<div class="notice">Extraction corrections and real plant changes are different. Invalidate only a proven false identity. Record a real replacement in operating history and update its supported equipment facts separately.</div><section class="card card-body"><form id="correction-form"><div class="ops-form-grid"><label>Equipment${equipmentPicker('correction-equipment',defaultEquipmentId())}</label><label>Correction<select id="correction-kind"><option value="qualify">Qualify a fact / network connection</option><option value="retire">Retire an incorrect fact</option><option value="retract_alias">Retract an incorrect alias</option><option value="invalidate_entity">Invalidate a false entity</option><option value="advanced">Advanced batch / restore / unmerge</option></select></label></div><div id="correction-targets"></div><label>Evidence reviewed and correction reason<textarea id="correction-reason" rows="3" required maxlength="12000" placeholder="Identify the drawing/record, what was wrong, and what it supports."></textarea></label><label>Reviewer name<input id="correction-author" maxlength="120" required></label><button class="button" style="margin-top:16px">Preview correction in review queue</button></form></section><p class="micro">Qualifying a fact replaces its full context. Existing values, citations and earlier versions remain intact. For corrected values, stage retire + assert in Advanced batch. Reverse a mistaken merge before staging a split.</p>`;}

function correctionTargets(){const eid=$('#correction-equipment').value,kind=$('#correction-kind').value, facts=liveFacts(state.model).filter(a=>a.canonical_subject===eid);let body='';if(['qualify','retire'].includes(kind)){body=`<label>Active fact<select id="correction-fact">${facts.map(a=>`<option value="${a.id}">${esc(a.predicate+' = '+(a.canonical_object?label(a.canonical_object,state.model):JSON.stringify(a.value))+' '+(a.unit||''))}</option>`).join('')}</select></label>`;if(kind==='qualify')body+='<label>Complete operational context (JSON)<textarea id="correction-context" rows="9" class="json-editor"></textarea></label><p class="micro">For a verified directed connection: kind connection, network material/mechanical/electrical/control/utility, verification documented, optional from_port/to_port and condition. Do not guess dates or direction.</p>';}if(kind==='retract_alias')body=`<label>Alias<select id="correction-alias">${state.model.aliases.filter(a=>!a.retracted&&state.model.entities.find(e=>e.id===a.entity_id)?.canonical_id===eid).map(a=>`<option value="${a.id}">${esc(a.alias)} · ${esc(a.id)}</option>`).join('')}</select></label>`;if(kind==='invalidate_entity')body=`<p>This will hide ${esc(label(eid,state.model))}, its aliases and ${liveFacts(state.model).filter(a=>a.canonical_subject===eid||a.canonical_object===eid).length} connected facts from the working view. History remains available.</p>`;if(kind==='advanced')body=`<label>Operations JSON (provenance is attached from your submitted source note)<textarea id="correction-operations" rows="10" class="json-editor">[]</textarea></label><details><summary>Inactive and merged identities / retracted aliases</summary><pre class="source-text">${esc(JSON.stringify({entities:state.model.entities.filter(e=>e.inactive||e.canonical_id!==e.id).map(e=>({id:e.id,label:e.label,inactive:e.inactive,canonical_id:e.canonical_id})),aliases:state.model.aliases.filter(a=>a.retracted).map(a=>({alias_id:a.id,alias:a.alias,entity:a.entity_id}))},null,2))}</pre></details>`;$('#correction-targets').innerHTML=body;if(kind==='qualify'){const update=()=>{$('#correction-context').value=JSON.stringify(facts.find(a=>a.id===$('#correction-fact').value)?.context||{},null,2);};$('#correction-fact').onchange=update;update();}}

function migrationView(){if(!migrationResult)return heading('Existing-data review','Build a review list without altering committed facts.',btn('Inspect existing data','load-migration','',''));const m=migrationResult;return heading('Existing-data review',`Plant version ${m.version}. These are review candidates, not proven errors.`,btn('Refresh review list','load-migration','','secondary'))+`<div class="stats">${[['Facts needing context',m.missing_context.length],['Relations needing network review',m.network_review.length],['Quantities needing unit review',m.unsupported_units.length],['Entities without active facts',m.entities_without_active_facts.length]].map(([t,n])=>`<div class="stat"><div class="stat-top">${esc(t)}</div><span class="stat-number">${n}</span></div>`).join('')}</div><div class="inline-list">${opsLink('Stage corrections','corrections')}${btn('Download complete review list','migration-export','','secondary')}</div><p>Start with one operating route. Check identity and aliases, then quantities and conditions, then document connection direction. Unknown dates stay unknown. Preserve useful facts and all originals.</p>${[['Network review',m.network_review],['Missing context',m.missing_context],['Unit review',m.unsupported_units]].map(([title,items])=>`<section class="card"><div class="card-head"><h2>${title}</h2><span>Showing first 40 of ${items.length}</span></div>${items.slice(0,40).map(a=>`<div class="activity-row"><strong>${esc(a.equipment)}</strong> · ${esc(a.predicate)} · ${esc(a.unit||'')}<div class="sub">${esc(a.assertion_id)}</div>${btn('Inspect source','fact-source',`data-id="${a.assertion_id}" data-support="0"`,'ghost small')}</div>`).join('')}</section>`).join('')}<section class="card card-body"><h2>Entities without active facts</h2><p>${esc(m.entities_without_active_facts.map(e=>e.label).join(', ')||'None')}</p><p class="micro">An empty identity is not automatically an error. Verify before invalidating.</p></section>`;}

async function runNetworkTrace(params){
  showAllNetworkPaths=false;
  networkResult=await api('/api/network?'+new URLSearchParams(params));
  render();
}

function bindOperations(){
  bindEquipmentPickers(document);
  const s=$('#source-search-form');
  if(s)s.onsubmit=async e=>{e.preventDefault();sourceQuery=$('#source-query').value;try{sourceResults=await api('/api/search?q='+encodeURIComponent(sourceQuery));render();}catch(err){toast(err.message,true);}};
  const n=$('#network-form');
  if(n)n.onsubmit=async e=>{
    e.preventDefault();
    try{
      await runNetworkTrace({
        equipment:$('#network-equipment').value,
        network:$('#network-kind').value,
        direction:$('#network-direction').value,
        condition:$('#network-condition').value,
        follow_all:$('#network-follow-all')?.checked?'1':'0'
      });
    }catch(err){toast(err.message,true);}
  };
  const f=$('#event-filter-form');
  if(f)f.onsubmit=e=>{e.preventDefault();eventFilter=$('#event-filter').value;render();};
  const c=$('#correction-form');
  if(c){correctionTargets();$('#correction-equipment').onchange=correctionTargets;$('#correction-kind').onchange=correctionTargets;c.onsubmit=async e=>{e.preventDefault();const button=e.submitter;button.disabled=true;try{const kind=$('#correction-kind').value,reason=$('#correction-reason').value;let ops;if(kind==='advanced')ops=JSON.parse($('#correction-operations').value);else{const op={op:kind,reason};if(kind==='qualify'||kind==='retire')op.assertion_id=$('#correction-fact').value;if(kind==='qualify')op.context=JSON.parse($('#correction-context').value);if(kind==='retract_alias')op.alias_id=$('#correction-alias').value;if(kind==='invalidate_entity')op.entity=$('#correction-equipment').value;ops=[op];}const r=await api('/api/corrections',{expected_version:state.model.version,author:$('#correction-author').value,reason,operations:ops});await refresh();selectedProposal=r.proposal_id;location.hash='review';render();toast('Correction staged. Inspect the source and operations before accepting.');}catch(err){toast(err.message,true);button.disabled=false;}};}
}

async function operationsAction(name,el){
  const id=el.dataset.id;
  if(name==='indexed-source'){const r=sourceResults.results.find(s=>s.index_note_id===el.dataset.note&&s.id===id);await source(r.support);return true;}
  if(name==='clear-event-filter'){eventFilter='';render();return true;}
  if(name==='new-event'){eventEditor();return true;}
  if(name==='event-followup'){eventEditor(state.events.find(e=>e.id===id));return true;}
  if(name==='equipment-page'){selectedEntity=id;historical=null;location.hash='overview?equipment='+encodeURIComponent(id);render();return true;}
  if(name==='load-migration'){migrationResult=await api('/api/migration');location.hash='migration';render();return true;}
  if(name==='migration-export'){await download('/api/migration','chp-existing-data-review.json');return true;}
  if(name==='toggle-network-paths'){showAllNetworkPaths=!showAllNetworkPaths;render();return true;}
  if(name==='network-cond-chip'){
    const cond=el.dataset.cond||'';
    await runNetworkTrace({
      equipment:networkResult?.equipment||$('#network-equipment')?.value||defaultEquipmentId(),
      network:networkResult?.network||$('#network-kind')?.value||'material',
      direction:networkResult?.direction||$('#network-direction')?.value||'downstream',
      condition:cond,
      follow_all:'1'
    });
    return true;
  }
  if(name==='scene-trace'){
    selectedEntity=id;
    location.hash='networks';
    await runNetworkTrace({
      equipment:id,
      network:'material',
      direction:'downstream',
      condition:'',
      follow_all:'1'
    });
    return true;
  }
  return false;
}
