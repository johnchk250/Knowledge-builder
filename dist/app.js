'use strict';

const $ = (s, r=document) => r.querySelector(s);

const esc = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const fmt = d => new Date(d).toLocaleString(undefined,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});

let token='', workspace='plant', state=null, settings=null, selectedProposal='', selectedEntity='', search='', conceptSearch='', historical=null, busy=false, lastSignature='';

let showDocumentRecords=false, docSearch='', docLimit=50, reviewSearch='', reviewLimit=30, historyLimit=40, entityLimit=60;

let providerDraft='',modelDraft='',effortDraft='',modelCatalog={},modelsLoading={};

let route=()=>location.hash.slice(1).split('?')[0]||'overview';

let toastTimer, serverMarker='', clientId='chp-'+(crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2));

async function poll(){const ws=workspace;const marker=JSON.stringify(await api('/api/revision'));if(ws!==workspace)return;if(marker!==serverMarker){serverMarker=marker;await refresh();}}

function toast(message,error=false){const el=$('#toast');el.textContent=message;el.className='show'+(error?' error':'');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.className='',error?11000:5000);}

async function api(path,body,options={}){

 const headers={'X-Workspace':workspace,...options.headers};

 if(body!==undefined){headers['X-CHP-Token']=token;if(!(body instanceof File)){headers['Content-Type']='application/json';body=JSON.stringify(body);}}

 const res=await fetch(path,{method:body===undefined?'GET':'POST',body,headers});

 if(!res.ok){let message='The local application could not complete this request.';try{message=(await res.json()).error||message;}catch{}throw new Error(message);}

 return options.blob?res.blob():res.json();

}

async function download(path,filename){const blob=await api(path,undefined,{blob:true});if(!blob.size)throw new Error('The download was empty. Check the source file in your local data folder.');const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}

function directDownload(path,filename){const url=new URL(path,location.origin);if(!url.searchParams.has('workspace'))url.searchParams.set('workspace',workspace);const a=document.createElement('a');a.href=url.href;a.download=filename;document.body.appendChild(a);a.click();a.remove();}

async function downloadOriginal(id){const path='/api/original/'+encodeURIComponent(id)+'?download=1&workspace='+encodeURIComponent(workspace);const res=await fetch(path,{method:'HEAD',headers:{'X-Workspace':workspace}});if(res.status!==200||!(Number(res.headers.get('Content-Length'))>0))throw new Error('The original file is not available in this local data folder.');directDownload(path,doc(id).name);}

function badge(text,color=''){return `<span class="badge ${color}">${esc(text)}</span>`;}

function btn(text,action,extra='',classes='secondary'){return `<button class="button ${classes}" data-action="${action}" ${extra}>${text}</button>`;}

function heading(title,sub,action=''){return `<div class="page-heading"><div><h1>${title}</h1><p>${sub}</p></div>${action}</div>`;}

function empty(title,sub,action=''){return `<div class="empty"><div class="upload-symbol">◇</div><h2>${title}</h2><p>${sub}</p>${action}</div>`;}

function doc(id){return state.documents.find(d=>d.id===id)||{name:'Source document',revision:'',authority:''};}

function label(id,model=historical||state.model){return model.entities.find(e=>e.id===id)?.label||id;}

function liveFacts(model=historical||state.model){return model.assertions.filter(a=>!a.retirement);}

function currentEntities(model=historical||state.model){return model.entities.filter(e=>e.canonical_id===e.id&&!e.inactive&&(showDocumentRecords||e.category!=='document'));}

function pending(){return state.proposals.filter(p=>p.status==='pending');}

function isRunning(){return state.runs.some(r=>['queued','running'].includes(r.status));}

function demoRibbon(){return workspace==='demo'?`<div class="demo-ribbon"><div><strong>Offline walkthrough · sample plant data</strong><p>Deterministic examples, no AI calls. Your plant workspace is separate.</p></div>${btn(state.model.version>=3?'Walkthrough complete':`Process sample ${state.model.version+1} of 3`,'demo-next',(state.model.version>=3||pending().length||isRunning())?'disabled':'','secondary small')}</div>`:'';}

function dropzone(){return `<div class="dropzone" id="dropzone"><div class="upload-symbol">↥</div><h3>Add the next piece of your plant</h3><p>Drop a document here, or browse your computer</p>${btn('＋ &nbsp; Add document','upload','','')}<input id="file-input" type="file" class="hidden" accept=".pdf,.txt,.md,.csv,.tsv,.xlsx,.png,.jpg,.jpeg"><div class="micro">PDF · text · spreadsheets · scanned images &nbsp; / &nbsp; up to 40 MB</div></div>`;}

function documentStatus(d){const p=state.proposals.find(p=>p.document_id===d.id&&p.status==='pending');const r=state.runs.find(r=>r.document_id===d.id);if(r&&['running','queued'].includes(r.status))return badge('Analyzing','blue');if(p)return badge(p.findings.errors.length?'Needs correction':'Ready for review',p.findings.errors.length?'red':'amber');if(state.proposals.some(p=>p.document_id===d.id&&p.status==='accepted'))return badge('In plant model','green');if(r&&['failed','interrupted'].includes(r.status))return badge('Analysis stopped','red');return badge('Ready to analyze');}

function documentRows(docs,compact=false){return docs.length?`<div class="table-wrap"><table><thead><tr><th>Source document</th><th>Status</th>${compact?'':'<th>Evidence</th>'}<th></th></tr></thead><tbody>${docs.map(d=>`<tr><td><div class="file-cell"><span class="document-icon">${esc(d.name.split('.').pop().toUpperCase().slice(0,4))}</span><div><strong class="wrap">${esc(d.name)}</strong><span class="sub">${esc(d.revision?'Rev '+d.revision+' · ':'')}${esc(d.authority)} · ${fmt(d.created)}</span></div></div></td><td>${documentStatus(d)}</td>${compact?'':`<td>${d.evidence_count} blocks<span class="sub">${(d.bytes/1024).toFixed(1)} KB</span></td>`}<td class="text-right">${btn('Open','document',`data-id="${d.id}"`,'ghost small')}</td></tr>`).join('')}</tbody></table></div>`:empty('No documents yet','Start with one equipment register, drawing, or technical note.');}

function overview(){const m=state.model;return heading('Build your plant’s knowledge','One document at a time. Every fact connected to its evidence.',btn('＋ &nbsp; Add document','upload','',''))+demoRibbon()+`<div class="stats"><div class="stat"><div class="stat-top">Source documents <span>▤</span></div><span class="stat-number">${state.documents.length}</span><small>Immutable original files</small></div><div class="stat"><div class="stat-top">Plant entities <span>◇</span></div><span class="stat-number">${currentEntities(state.model).length}</span><small>Equipment, systems & components</small></div><div class="stat"><div class="stat-top">Pending review <span>✓</span></div><span class="stat-number blue">${pending().length}</span><small>Proposed knowledge updates</small></div><div class="stat"><div class="stat-top">Open conflicts <span>≠</span></div><span class="stat-number amber">${m.conflicts.length}</span><small>Competing evidence retained</small></div></div><div class="grid-two"><div><section class="card"><div class="card-head"><h2>Bring in plant information</h2>${badge('Local ingestion','green')}</div><div class="card-body">${dropzone()}<div class="micro">Importing stays local. Analysis sends selected source content and relevant plant context to your configured API.</div></div></section><section class="card"><div class="card-head"><h2>Recent documents</h2><a class="button ghost small" href="#documents">View all →</a></div>${documentRows(state.documents.slice(0,4),true)}</section></div><div><section class="card"><div class="card-head"><h2>A model that can evolve</h2></div><div class="card-body"><div class="steps"><div class="step"><span class="step-number">1</span><div><h3>Preserve the source</h3><p>Keep the original file, extracted evidence, and page locations.</p></div></div><div class="step"><span class="step-number">2</span><div><h3>Compare with what is known</h3><p>Find related equipment, aliases, concepts, and existing claims.</p></div></div><div class="step"><span class="step-number">3</span><div><h3>Review a structured update</h3><p>Inspect discoveries, uncertain matches, conflicts, and model changes.</p></div></div><div class="step"><span class="step-number">4</span><div><h3>Grow the plant model</h3><p>Commit a new version. Earlier interpretations remain traceable.</p></div></div></div></div></section><section class="card"><div class="card-head"><h3>Latest activity</h3></div>${state.runs.length?state.runs.slice(0,3).map(r=>`<div class="activity-row">${['running','queued'].includes(r.status)?'<span class="spin"></span>':''}${esc(r.progress)}<small>${esc(doc(r.document_id).name)}</small>${r.error?`<small style="color:#b13037">${esc(r.error)}</small>`:''}</div>`).join(''):'<div class="card-body"><p class="muted" style="font-size:14px;margin:0">Your first document starts the history.</p></div>'}</section></div></div>`;}

function documents(){
  const filtered=state.documents.filter(d=>!docSearch||[d.name,d.revision||'',d.authority||''].join(' ').toLowerCase().includes(docSearch.toLowerCase()));
  const shown=filtered.slice(0,docLimit);
  return heading('Source documents','Original files and extracted evidence remain unchanged.',btn('＋ &nbsp; Add document','upload','',''))+demoRibbon()+
    `<div class="toolbar"><input id="doc-search" class="search" placeholder="Filter ${state.documents.length} source documents by filename, revision or authority…" value="${esc(docSearch)}"><span class="muted" style="font-size:13px">Showing ${shown.length} of ${filtered.length} documents</span></div>`+
    `<section class="card">${documentRows(shown)}${filtered.length>docLimit?`<div class="card-body"><button class="button secondary small" data-action="more-documents">Show more documents (${filtered.length-docLimit} remaining)</button></div>`:''}</section>`;
}

function opTitle(o,map){const name=id=>map[id]||label(id);switch(o.op){case'define':return `Define ${String(o.key??'unknown').replaceAll('_',' ')}`;case'entity':return `Add ${o.label}`;case'alias':return `${o.alias} → ${name(o.entity)}`;case'assert':return `${name(o.subject)} · ${String(o.predicate??'unknown').replaceAll('_',' ')} · ${o.object_entity?name(o.object_entity):JSON.stringify(o.value)}${o.unit?' '+o.unit:''}`;case'retire':return `Retire earlier assertion`;case'merge':return `Merge ${name(o.source)} into ${name(o.target)}`;case'source_note':return `Index source region: ${o.text}`;case'event':return `${name(o.equipment)} · ${o.event_type} · ${o.summary}`;case'qualify':return `Qualify ${o.assertion_id}`;case'invalidate_entity':case'restore_entity':case'unmerge':return `${o.op.replaceAll('_',' ')} · ${name(o.entity)}`;case'retract_alias':case'restore_alias':return `${o.op.replaceAll('_',' ')} · ${o.alias_id}`;default:return 'Invalid operation';}}

function operation(o,i,map){

 if(!o||typeof o!=='object')return `<div class="operation">Invalid operation ${i+1}</div>`;

 const kinds={define:'Concept',entity:'New entity',alias:'Alias',assert:'Fact',retire:'Retirement',merge:'Identity merge',event:'Operating record',source_note:'Source index',qualify:'Fact context',invalidate_entity:'Invalidate identity',restore_entity:'Restore identity',unmerge:'Reverse merge',retract_alias:'Retract alias',restore_alias:'Restore alias'};

 const descriptions={assert:'Source-supported plant claim',alias:'Link a source name to an existing identity',event:'Dated operator/source record; separate from equipment specifications',source_note:'Searchable source description; does not create a plant specification',qualify:'Replace complete operational context; preserve the original value and evidence'};

 let details='';

 if(o.context){const earlier=o.op==='qualify'&&state.proposals.find(p=>p.id===selectedProposal)?.status==='pending'?state.model.assertions.find(a=>a.id===o.assertion_id):null;details=`${earlier?`<h4>Before</h4><pre class="source-text">${esc(JSON.stringify(earlier.context||{},null,2))}</pre>`:''}<h4>${earlier?'After':'Operational context'}</h4><pre class="source-text">${esc(JSON.stringify(o.context,null,2))}</pre>`;}

 if(o.op==='event')details=`<p>Occurred: ${esc(o.occurred_at)} / ${esc(o.status||'recorded')}</p><p style="white-space:pre-wrap">${esc(o.details||'')}</p>${o.related_event?`<p>Related event: ${esc(o.related_event)}</p>`:''}${o.measurements?.length?`<pre class="source-text">${esc(JSON.stringify(o.measurements,null,2))}</pre>`:''}`;

 if(['invalidate_entity','restore_entity','unmerge'].includes(o.op)){const related=state.model.assertions.filter(a=>[a.subject,a.object_entity,a.canonical_subject,a.canonical_object].includes(o.entity));details=`<details><summary>Affected facts (${related.length})</summary>${related.map(a=>`<p>${esc(label(a.subject,state.model))} / ${esc(a.predicate)} / ${esc(a.object_entity?label(a.object_entity,state.model):JSON.stringify(a.value))}</p>`).join('')}</details>`;}

 if(['retract_alias','restore_alias'].includes(o.op)){const a=state.model.aliases.find(a=>a.id===o.alias_id);details=`<p>Alias: <strong>${esc(a?.alias||o.alias_id)}</strong> / current owner ${esc(label(a?.entity_id,state.model))}</p>`;}

 return `<div class="operation"><span class="op-icon">${['invalidate_entity','retire','unmerge'].includes(o.op)?'!':'+'}</span><div><h3>${esc(opTitle(o,map))}</h3><p>${esc(o.definition||o.reason||descriptions[o.op]||'Reviewed knowledge change')}</p>${details}<div class="op-meta">${badge(o.origin||'unknown',o.origin==='inferred'?'amber':'')}${badge(Number.isFinite(o.confidence)?Math.round(o.confidence*100)+'% extraction confidence':'Invalid confidence')}${Array.isArray(o.evidence)?o.evidence.map((s,j)=>`<button class="source-link" data-action="op-source" data-index="${i}" data-support="${j}">Evidence ${j+1}</button>`).join(''):''}${['retire','qualify'].includes(o.op)?`<button class="source-link" data-action="old-fact" data-id="${esc(o.assertion_id)}">View original claim</button>`:''}</div></div>${badge(kinds[o.op]||'Invalid',['retire','merge','invalidate_entity'].includes(o.op)?'amber':'blue')}</div>`;

}



async function ensureProposalLoaded(id){
 if(!id||!state?.proposals)return;
 const idx=state.proposals.findIndex(p=>p.id===id);
 if(idx===-1||!state.proposals[idx].trimmed)return;
 try{
  const full=await api('/api/proposal?id='+encodeURIComponent(id));
  state.proposals[idx]=full;
  render();
 }catch(e){toast(e.message,true);}
}

function review(){const list=state.proposals;const p=list.find(p=>p.id===selectedProposal)||pending()[0]||list[0];selectedProposal=p?.id||'';if(p?.trimmed)setTimeout(()=>ensureProposalLoaded(p.id),0);if(!p)return heading('Review changes','Compare proposed updates with their evidence before committing.')+demoRibbon()+`<section class="card">${empty('No proposals to review','Import a document and run analysis to discover new plant knowledge.',btn('Open documents','go-documents','',''))}</section>`;const run=state.runs.find(r=>r.id===p.run_id);const manifest=JSON.parse(run?.manifest||'{}');const guidance=manifest.understanding_revision;const stale=(p.base_version!==state.model.version||guidance!==state.understanding.revision||(manifest.provider!=='offline_fixture'&&manifest.intake_policy!==state.intake_policy))&&p.status==='pending';const map=Object.fromEntries((p.body.operations||[]).filter(o=>o?.op==='entity').map(o=>[o.id,o.label]));const error=p.findings.errors.length>0||stale;return heading('Review changes','Accept a complete, validated update as one new model version.')+demoRibbon()+`<div class="review-layout"><aside class="proposal-list"><div class="proposal-filter-box"><input id="proposal-search" type="search" placeholder="Filter ${list.length} proposals…" value="${esc(reviewSearch)}" aria-label="Filter proposals"></div>${(()=>{const pend=list.filter(x=>x.status==='pending'&&(!reviewSearch||doc(x.document_id).name.toLowerCase().includes(reviewSearch.toLowerCase())));const hist=list.filter(x=>x.status!=='pending'&&(!reviewSearch||doc(x.document_id).name.toLowerCase().includes(reviewSearch.toLowerCase())));const shown=[...pend,...hist.slice(0,reviewLimit)];if(p&&!shown.some(x=>x.id===p.id))shown.unshift(p);return shown.map(x=>`<button class="proposal-item ${x.id===p.id?'active':''}" data-action="select-proposal" data-id="${x.id}"><strong>${esc(doc(x.document_id).name)}</strong><small>${x.operation_count??x.body?.operations?.length??0} changes · ${fmt(x.created)}</small><small>${badge(x.status,x.status==='pending'?'amber':x.status==='accepted'?'green':'')}</small></button>`).join('')+(hist.length>reviewLimit?`<div style="padding:10px"><button class="button secondary small" style="width:100%" data-action="more-proposals">Show more (${hist.length-reviewLimit} older)</button></div>`:'');})()}</aside><section class="card"><div class="proposal-summary"><div class="inline-list">${badge('Based on version '+p.base_version)}${badge('Guidance revision '+(guidance??'legacy'))}${badge(doc(p.document_id).revision?'Source rev '+doc(p.document_id).revision:'No source revision')}${badge(p.status,p.status==='accepted'?'green':'blue')}</div><p>${esc(p.body.summary)}</p>${(state.intakes?.[p.run_id]||[]).map(a=>`<div class="notice"><strong>${esc(a.route)} intake</strong><p>${esc(a.purpose)}</p><p>Supports: ${esc(a.questions.join('; ')||'Source reference only')}</p><p>Gaps: ${esc(a.gaps.join('; ')||'None recorded; completeness is not certified')}</p><span class="micro">${a.reviewed_evidence_ids.length} evidence blocks reviewed</span></div>`).join('')}</div><div style="padding:20px 22px 0">${stale?'<div class="notice red"><strong>This proposal is stale.</strong> Reject it and re-analyze the source against the current plant model and project understanding.</div>':''}${p.findings.errors.length?`<div class="notice red"><strong>Validation blocked acceptance</strong><ul>${p.findings.errors.map(e=>`<li>${esc(e)}</li>`).join('')}</ul></div>`:''}${p.findings.warnings.length?`<details class="notice amber" open><summary>${p.findings.warnings.length} items need engineering review</summary><ul>${p.findings.warnings.map(w=>`<li>${esc(w)}</li>`).join('')}</ul></details>`:''}</div>${p.trimmed?'<div class="card-body"><span class="spin"></span> Loading historical proposal operations…</div>':(p.body.operations.map((o,i)=>operation(o,i,map)).join('')||'<div class="card-body">No new claims were proposed.</div>')}<div class="review-actions"><div>${btn('View original','original',`data-id="${p.document_id}"`,'secondary small')}${btn('Analysis record','run-audit',`data-id="${p.run_id}"`,'ghost small')}</div>${p.status==='pending'?`<div>${btn('Edit JSON','edit-proposal','','secondary small')}${btn('Reject','reject',`data-id="${p.id}"`,'danger small')}${btn('Accept update →','accept',`data-id="${p.id}" ${error?'disabled':''}`,'small')}</div>`:badge(p.status==='accepted'?'Committed to model':'Proposal retained in history',p.status==='accepted'?'green':'')}</div></section></div>`;}

function graph(model){const entities=currentEntities(model).filter(e=>!search||[e.label,...e.aliases].some(x=>x.toLowerCase().includes(search.toLowerCase()))).slice(0,18);if(!entities.length)return empty('No matching entities','Add and accept knowledge to see connected equipment here.');const pos={};const rows=Math.ceil(entities.length/3),height=Math.max(300,rows*110+60);entities.forEach((e,i)=>pos[e.id]={x:120+(i%3)*225,y:65+Math.floor(i/3)*110});const edges=liveFacts(model).filter(a=>a.canonical_object&&pos[a.canonical_subject]&&pos[a.canonical_object]);return `<svg viewBox="0 0 690 ${height}" style="height:${height}px" role="img" aria-label="Plant relationship graph. All relationships are also available in the entity details."><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#8198ba"/></marker></defs>${edges.map((a,i)=>{const p=pos[a.canonical_subject],q=pos[a.canonical_object];const same=p.y===q.y;const dy=same?28+(i%2)*13:0;return `<path d="M ${p.x} ${p.y+20} Q ${(p.x+q.x)/2} ${(p.y+q.y)/2+dy+55} ${q.x} ${q.y+24}" fill="none" stroke="#94a8c5" stroke-width="1.4" marker-end="url(#arrow)"/><text class="edge-label" x="${(p.x+q.x)/2}" y="${(p.y+q.y)/2+dy+40}" text-anchor="middle">${esc(a.predicate.replaceAll('_',' '))}</text>`;}).join('')}${entities.map(e=>{const p=pos[e.id];return `<g class="graph-node ${e.id===selectedEntity?'selected':''}" tabindex="0" role="button" aria-label="Inspect ${esc(e.label)}" data-action="select-entity" data-id="${e.id}"><rect x="${p.x-70}" y="${p.y-22}" width="140" height="44" rx="7"/><text x="${p.x}" y="${p.y+5}" text-anchor="middle">${esc(e.label.length>19?e.label.slice(0,18)+'…':e.label)}</text></g>`;}).join('')}</svg>`;}

function factRow(a,model){const other=a.canonical_object?label(a.canonical_object,model):JSON.stringify(a.value);const conflict=model.conflicts.some(c=>c.assertion_ids.includes(a.id));return `<div class="fact-row"><div class="fact-value"><span>${esc(a.predicate.replaceAll('_',' '))}</span><strong>${esc(other)} ${esc(a.unit||'')}</strong></div><div class="sub">${esc(a.context?.kind||'Legacy context pending')} · ${esc(a.context?.condition||'Condition unspecified')} · ${Math.round(a.confidence*100)}% confidence · ${esc(a.origin)} · version ${a.created_version}${a.retirement?' · retired in v'+a.retirement.version:''}</div>${conflict?badge('Conflicting values','amber'):''}<div>${Object.keys(a.context||{}).length?`<details><summary>Operational context</summary><pre class="source-text">${esc(JSON.stringify(a.context,null,2))}</pre></details>`:''}${(a.context_record?.provenance?.evidence||[]).map((s,j)=>btn('Context review source','context-source',`data-id="${a.id}" data-support="${j}"`,'ghost small')).join('')}${a.evidence.map((s,j)=>`<button class="source-link" data-action="fact-source" data-id="${a.id}" data-support="${j}">▤ View source ${a.evidence.length>1?j+1:''}</button>`).join(' ')}</div></div>`;}

function entityDetail(model){const e=model.entities.find(e=>e.id===selectedEntity);if(!e)return `<div class="empty"><h2>Inspect an entity</h2><p>Select an equipment tag to see its current claims and source evidence.</p></div>`;const facts=liveFacts(model).filter(a=>a.canonical_subject===e.id);const old=model.assertions.filter(a=>a.canonical_subject===e.id&&a.retirement);return `<div class="entity-detail"><h2>${esc(e.label)}</h2><p class="muted" style="font-size:13px">${esc(e.id)}</p><div class="inline-list">${[...new Set(e.aliases)].filter(a=>a!==e.label).map(a=>badge(a)).join('')}</div><div class="divider"></div>${historical||e.category==='document'?'':btn('Add operating record','new-event','','secondary small')}<br><button class="source-link" data-action="entity-source" data-id="${e.id}">▤ Identity evidence</button>${facts.map(a=>factRow(a,model)).join('')||'<p class="muted">No active assertions.</p>'}${historical?'':`<h3>Operating history</h3>${eventCards((state.events||[]).filter(x=>x.canonical_equipment===e.id).slice(0,30))}`}${old.length?`<details style="margin-top:20px"><summary>Earlier interpretations (${old.length})</summary>${old.map(a=>factRow(a,model)).join('')}</details>`:''}</div>`;}

function knowledge(){const model=historical||state.model;const p=(!historical&&typeof PlantExplorer!=='undefined'&&PlantExplorer.projection)?PlantExplorer.projection():PlantExplorerModel.build(model);const ents=search?PlantExplorerModel.searchEntities(p,search).filter(e=>showDocumentRecords||e.category!=='document'):currentEntities(model);return heading('Equipment & evidence','Equipment facts, documented relationships, operating history and corrections.',badge('Model version '+model.version,'blue'))+`${historical?`<div class="notice">Historical view · version ${historical.version}. ${btn('Return to current model','current-model','','ghost small')}</div>`:''}${model.conflicts.length?`<div class="notice amber"><strong>${model.conflicts.length} unresolved ${model.conflicts.length===1?'conflict':'conflicts'}.</strong> Both source claims remain active. <div class="inline-list" style="margin-top:8px">${model.conflicts.map(c=>btn(`${esc(label(c.subject,model))} · ${esc(c.predicate.replaceAll('_',' '))}`,'select-entity',`data-id="${c.subject}"`,'secondary small')).join('')}</div></div>`:''}<div class="toolbar"><input class="search" id="entity-search" placeholder="Search equipment tags or aliases…" aria-label="Search entities" value="${esc(search)}"><label><input id="include-records" type="checkbox" ${showDocumentRecords?'checked':''}> Include document records</label><span class="muted" style="font-size:13px">${ents.length} entities · ${liveFacts(model).length} active assertions</span></div>${!model.entities.length?`<section class="card">${empty('Your plant model starts here','Accept your first proposal to create the first equipment identities and claims.',btn('Review changes','go-review','',''))}</section>`:`<div class="entity-layout"><div><section class="card"><div class="card-head"><h2>Relationship map</h2><span class="muted" style="font-size:12px">Up to 18 matching entities</span></div><div class="graph-surface">${graph(model)}</div></section><section class="card"><div class="table-wrap"><table><thead><tr><th>Entity</th><th>Classification</th><th>Active claims</th></tr></thead><tbody>${ents.slice(0,entityLimit).map(e=>{const fs=liveFacts(model).filter(a=>a.canonical_subject===e.id);return `<tr><td><button class="entity-button" data-action="select-entity" data-id="${e.id}">${esc(e.label)}</button><span class="sub">${esc([...new Set(e.aliases)].filter(a=>a!==e.label).join(' · '))}</span></td><td>${fs.filter(a=>a.predicate==='instance_of').map(a=>esc(String(a.value).replaceAll('_',' '))).join(', ')||'Not classified'}</td><td>${fs.length}</td></tr>`;}).join('')}</tbody></table></div>${ents.length>entityLimit?`<div class="card-body"><button class="button secondary small" data-action="more-entities">Show more entities (${ents.length-entityLimit} remaining)</button></div>`:''}</section></div><section class="card">${entityDetail(model)}</section></div>`}`;}

function ontology(){const rows=state.model.ontology.filter(o=>(o.key+' '+o.definition).toLowerCase().includes(conceptSearch.toLowerCase()));return heading('Concepts','An extensible vocabulary grown through reviewed source evidence.',badge(state.model.ontology.length+' definitions'))+`<div class="toolbar"><input id="concept-search" class="search" aria-label="Search concepts" placeholder="Find a concept or property…" value="${esc(conceptSearch)}"></div><div class="notice">The structure for evidence and changes is fixed. Engineering types, properties, and relationships can grow with the documents. Existing definitions stay immutable; a changed meaning needs a new concept and an explicit migration proposal.</div><section class="card"><div class="table-wrap"><table><thead><tr><th>Concept</th><th>Kind</th><th>Values</th><th>Definition</th><th>Source</th></tr></thead><tbody>${rows.map(o=>`<tr><td><strong>${esc(o.key)}</strong><span class="sub">Added in v${o.created_version}</span></td><td>${badge(o.kind.replaceAll('_',' '))}</td><td>${esc(o.value_type)}<span class="sub">${o.cardinality==='one'?'One current value':'Multiple values'}</span></td><td>${esc(o.definition)}</td><td>${o.created_version?btn('Evidence','concept-source',`data-id="${o.key}"`,'ghost small'):badge('Bootstrap')}</td></tr>`).join('')}</tbody></table></div></section>`;}

function history(){
  const ordered=state.versions.slice().reverse();
  const shown=ordered.slice(0,historyLimit);
  return heading('Version history',`Each accepted proposal is one atomic, traceable model version (${ordered.length} committed versions).`,btn('Download full backup','backup','','secondary'))+
    `<section class="card">${shown.length?shown.map(v=>`<div class="timeline-item"><span class="version-box">v${v.version}</span><div class="timeline-content"><h3>${esc(v.summary)}</h3><p>${fmt(v.created)} · ${esc(doc(state.proposals.find(p=>p.id===v.proposal_id)?.document_id).name)}</p><div class="hash" style="margin-top:10px">${esc(v.hash)}</div></div>${btn('Inspect','history-model',`data-version="${v.version}"`,'secondary small')}</div>`).join('')+(ordered.length>historyLimit?`<div class="card-body"><button class="button secondary small" data-action="more-history">Show older versions (${ordered.length-historyLimit} remaining)</button></div>`:''):empty('No committed versions','Accept a proposal to create the first version. Source imports and rejected proposals do not alter the model.')}</section><div class="notice">Backups include the database, original files, and page renders. Restore into a separate workspace folder while the application is stopped; see README.md for the steps. JSON exports are for machine-readable analysis, not full restoration.</div>`;
}

function settingsView(){const s=settings;return heading('AI connection','Choose where reasoning happens. Plant storage remains on your computer.')+`<div class="settings-grid"><section class="card"><div class="card-head"><h2>Model provider</h2>${badge(s.has_key?'Key available':'Key needed',s.has_key?'green':'amber')}</div><form id="settings-form" class="card-body"><div class="form-row"><label for="provider">API protocol</label><select id="provider" name="provider">${[['openai','OpenAI-compatible'],['anthropic','Anthropic Messages'],['gemini','Google Gemini']].map(([v,l])=>`<option value="${v}" ${s.provider===v?'selected':''}>${l}</option>`).join('')}</select></div><div class="form-row"><label for="model">Model ID</label><input id="model" name="model" value="${esc(s.model)}" placeholder="Exact model ID from your provider" required><p>Use a model with image support when enabling drawing analysis.</p></div><div class="form-row"><label for="base_url">API base URL <span class="muted">(optional)</span></label><input id="base_url" name="base_url" value="${esc(s.base_url)}" placeholder="${esc(s.defaults[s.provider])}"><p>Leave blank for the provider default. Compatible gateways and local model servers can use a custom URL.</p></div><div class="form-row"><label for="api_key">Session API key</label><input id="api_key" name="api_key" type="password" autocomplete="off" placeholder="${s.has_key?'Leave blank to keep the available key':'Paste an API key'}"><p>Stored in application memory until shutdown. You can also configure an environment variable.</p></div><div class="form-row"><label class="checkbox-label"><input type="checkbox" name="vision" ${s.vision?'checked':''}><span>Include rendered pages for vision analysis<br><small class="muted">Sends page images alongside extracted text. Required for scans; recommended for drawings.</small></span></label></div><div class="form-row"><label class="checkbox-label"><input type="checkbox" name="clear_key"><span>Clear the session key when saving</span></label></div><button class="button" type="submit">Save connection</button><p class="micro">Saving does not contact the provider. The next document analysis makes the API calls.</p></form></section><div><section class="card"><div class="card-head"><h2>Data boundary</h2></div><div class="card-body"><div class="status-line"><span>Original documents</span>${badge('Local','green')}</div><div class="status-line"><span>Plant model & history</span>${badge('Local','green')}</div><div class="status-line"><span>Selected source evidence</span>${badge('Sent for analysis','blue')}</div><div class="status-line"><span>Relevant plant context</span>${badge('Sent for analysis','blue')}</div><p class="micro">Your API provider’s retention and billing policies apply to transmitted content. This application does not train or fine-tune the model.</p></div></section><section class="card"><div class="card-head"><h3>Review policy</h3></div><div class="card-body"><p style="font-size:14px;margin-bottom:0">All proposals require human acceptance in this first version. Validation checks structure, references, evidence, conflicts, and hierarchy consistency. It cannot establish that an engineering interpretation is correct.</p></div></section></div></div>`;}



const sessionBackend=p=>['codex_session','antigravity_session'].includes(p);

function sessionModelFields(provider,selected,effort){

 const catalog=modelCatalog[provider];

 if(!catalog)return `<div class="form-row"><label>Model</label><select id="model" name="model" required><option value="${esc(selected)}">Loading live model picker…</option></select><p>The list is read from the authenticated desktop CLI.</p></div>`;

 const chosen=catalog.find(m=>m.id===selected)||catalog.find(m=>m.default)||catalog[0];

 const efforts=chosen?.efforts?.length?chosen.efforts:['medium'];

 const activeEffort=efforts.includes(effort)?effort:(chosen?.default_effort||efforts[0]);

 return `<div class="form-row"><label for="model">Available model</label><div class="inline-list"><select id="model" name="model" required>${catalog.map(m=>`<option value="${esc(m.id)}" ${m.id===chosen?.id?'selected':''}>${esc(m.display_name)}</option>`).join('')}</select><button class="button ghost small" type="button" id="refresh-models">Refresh</button></div><p>${esc(chosen?.description||'Read from the signed-in account.')}</p></div><div class="form-row"><label for="effort">Reasoning effort</label><select id="effort" name="effort">${efforts.map(x=>`<option value="${x}" ${x===activeEffort?'selected':''}>${x}</option>`).join('')}</select></div>`;

}

async function loadSessionModels(provider,refresh=false){

 if(!sessionBackend(provider)||modelsLoading[provider]||(!refresh&&modelCatalog[provider]))return;

 modelsLoading[provider]=true;

 try{const result=await api('/api/models?provider='+encodeURIComponent(provider)+(refresh?'&refresh=1':''));modelCatalog[provider]=result.models;if(route()==='settings'&&(providerDraft||settings.provider)===provider)render();}

 catch(e){toast(e.message,true);}

 finally{modelsLoading[provider]=false;}

}

function settingsViewV2(){

 const s=settings,p=providerDraft||s.provider,isSession=sessionBackend(p),selected=modelDraft||(p===s.provider?s.model:''),effort=effortDraft||s.effort||'medium';

 const choices=[['openai','OpenAI-compatible API'],['anthropic','Anthropic Messages API'],['gemini','Google Gemini API'],['codex_session','Codex signed-in session'],['antigravity_session','Antigravity signed-in session']];

 const modelFields=isSession?sessionModelFields(p,selected,effort):`<div class="form-row"><label for="model">Model ID</label><input id="model" name="model" value="${esc(p===s.provider?s.model:'')}" placeholder="Exact model ID from your provider" required><p>Use a model with image support when enabling drawing analysis.</p></div><input type="hidden" name="effort" value="medium">`;

 const connectionFields=isSession?`<div class="notice green"><strong>Uses the authenticated local ${p==='codex_session'?'Codex':'Antigravity'} CLI.</strong> Credentials are managed by that application and are never read or copied by CHP Knowledge Builder.${p==='antigravity_session'?' Each analysis call runs in a disposable isolated project; only read-only access inside that request workspace is accepted.':''}</div>`:`<div class="form-row"><label for="base_url">API base URL <span class="muted">(optional)</span></label><input id="base_url" name="base_url" value="${esc(p===s.provider?s.base_url:'')}" placeholder="${esc(s.defaults[p]||'')}"><p>Leave blank for the provider default. HTTP is allowed only for local servers.</p></div><div class="form-row"><label for="api_key">Session API key</label><input id="api_key" name="api_key" type="password" autocomplete="off" placeholder="${s.has_key?'Leave blank to keep the available key':'Paste an API key'}"><p>Stored in application memory until shutdown.</p></div><div class="form-row"><label class="checkbox-label"><input type="checkbox" name="clear_key"><span>Clear the session key when saving</span></label></div>`;

 return heading('AI backends','Choose an API or reuse an authenticated desktop AI session. Plant storage remains on your computer.')+`<div class="settings-grid"><section class="card"><div class="card-head"><h2>AI backend</h2>${badge(isSession?'Authenticated session':s.has_key?'Key available':'Key needed',isSession||s.has_key?'green':'amber')}</div><form id="settings-form" class="card-body"><div class="form-row"><label for="provider">Backend</label><select id="provider" name="provider">${choices.map(([v,l,disabled])=>`<option value="${v}" ${p===v?'selected':''} ${disabled?'disabled':''}>${l}</option>`).join('')}</select></div><div id="model-controls">${modelFields}</div>${connectionFields}<div class="form-row"><label class="checkbox-label"><input type="checkbox" name="vision" ${s.vision?'checked':''}><span>Include rendered pages for vision analysis<br><small class="muted">Images are attached temporarily to the selected API request or authenticated CLI run.</small></span></label></div><button class="button" type="submit">Save connection</button><p class="micro">Saving validates the selected session model but does not analyze a document.</p></form></section><div><section class="card"><div class="card-head"><h2>Data boundary</h2></div><div class="card-body"><div class="status-line"><span>Original documents</span>${badge('Local','green')}</div><div class="status-line"><span>Plant model & history</span>${badge('Local','green')}</div><div class="status-line"><span>Selected source evidence</span>${badge('Sent for analysis','blue')}</div><div class="status-line"><span>Relevant plant context</span>${badge('Sent for analysis','blue')}</div><p class="micro">For session backends, content is sent through the vendor CLI under its signed-in account, usage limits and retention terms.</p></div></section><section class="card"><div class="card-head"><h3>Review policy</h3></div><div class="card-body"><p style="font-size:14px;margin-bottom:0">All proposals still require human acceptance. Changing the backend does not grant the model database or commit authority.</p></div></section></div></div>`;

}

function bindSessionSettings(){

 const form=$('#settings-form');if(!form)return;

 form.onsubmit=async e=>{e.preventDefault();const values=new FormData(form);try{settings=await api('/api/settings',{provider:values.get('provider'),model:values.get('model'),effort:values.get('effort')||'medium',base_url:values.get('base_url')||'',api_key:values.get('api_key')||'',vision:values.has('vision'),clear_key:values.has('clear_key')});providerDraft=modelDraft=effortDraft='';render();toast('Connection saved and backend selection validated.');}catch(err){toast(err.message,true);}};

 const provider=$('#provider');if(provider)provider.onchange=()=>{providerDraft=provider.value;modelDraft=effortDraft='';render();};

 const model=$('#model');if(model&&sessionBackend(provider?.value))model.onchange=()=>{modelDraft=model.value;effortDraft='';render();};

 const refresh=$('#refresh-models');if(refresh)refresh.onclick=()=>{modelCatalog[provider.value]=null;loadSessionModels(provider.value,true);render();};

}



let memoryRevision=0;

function memoryEditor(note={},suggestion=''){

 memoryRevision=state.understanding.revision;

 modal(suggestion?'Review an interpretation note':note.id?'Edit interpretation note':'Add interpretation note',`<p class="micro">Guidance helps interpretation; it cannot replace source evidence for plant facts. Hypotheses and questions remain uncertain.</p><div class="form-row"><label for="memory-kind">Kind</label><select id="memory-kind">${['convention','lesson','question','hypothesis'].map(k=>`<option ${k===(note.kind||'convention')?'selected':''}>${k}</option>`).join('')}</select></div><div class="form-row"><label for="memory-text">What should the AI keep in mind?</label><textarea id="memory-text" maxlength="1200" rows="5" style="width:100%">${esc(note.text||'')}</textarea></div><div class="form-row"><label for="memory-scope">Applies to (comma-separated tags or concepts)</label><input id="memory-scope" style="width:100%" value="${esc((note.scope||[]).join(', '))}" placeholder="Blank means every document"><p class="micro">Specific scopes are retrieved using source text, discovered mentions, and related entity labels. Matching notes are included whole; excessive guidance stops analysis instead of being silently cut off.</p></div><div class="notice amber">Saving creates a guidance revision. Pending plant proposals will need re-analysis; accept any reviewed plant update first.</div><div class="dialog-actions">${btn(suggestion?'Approve reviewed note':'Save note','memory-save',`data-note="${esc(note.id||'')}" data-suggestion="${esc(suggestion)}"`,'')}</div>`);

}

function understandingView(){

 const u=state.understanding,queued=u.suggestions.filter(s=>s.status==='pending');

 return heading('Project understanding','The purpose, interpretation guidance, and open questions supplied to the AI.',btn('＋ Add interpretation note','memory-add','',''))+

 `<div class="notice">Ready to use: the CHP project brief is preloaded from your requirements. Every analysis receives it, relevant reviewed notes, and a recap derived from the current model. Imported documents cannot directly rewrite this guidance.</div><div class="stats"><div class="stat"><div class="stat-top">Guidance revision</div><span class="stat-number">${u.revision}</span><small>Separate from plant model versions</small></div><div class="stat"><div class="stat-top">Reviewed notes</div><span class="stat-number">${u.notes.length}</span><small>Conventions, lessons & unknowns</small></div><div class="stat"><div class="stat-top">Suggested memories</div><span class="stat-number blue">${queued.length}</span><small>Inactive until separately approved</small></div><div class="stat"><div class="stat-top">Unresolved plant conflicts</div><span class="stat-number amber">${state.model.conflicts.length}</span><small>Derived from the current graph</small></div></div>

 <section class="card"><div class="card-head"><h2>Project purpose & interpretation approach</h2>${btn('Edit brief','memory-brief','','secondary small')}</div><div class="card-body"><details><summary>Read the instructions sent with every document</summary><div style="white-space:pre-wrap;font-size:15px;line-height:1.7;margin-top:18px">${esc(u.brief)}</div></details></div></section>

 <section class="card"><div class="card-head"><h2>Reviewed interpretation notes</h2>${badge(u.notes.length+' active')}</div>${u.notes.map(n=>`<div class="activity-row"><div class="inline-list">${badge(n.kind,['hypothesis','question'].includes(n.kind)?'amber':'blue')}${badge(n.scope.length?n.scope.join(', '):'All documents')}</div><p style="margin:12px 0">${esc(n.text)}</p><small>${esc(n.origin)}</small><div class="toolbar" style="margin:12px 0 0"><div>${btn('Edit','memory-edit',`data-id="${n.id}"`,'ghost small')} &nbsp; ${btn('Retire','memory-retire',`data-id="${n.id}"`,'ghost small')}</div><div>${(n.source?.evidence||[]).map((s,i)=>btn('Source '+(i+1),'memory-note-source',`data-id="${n.id}" data-support="${i}"`,'ghost small')).join(' ')}</div></div></div>`).join('')||empty('No additional conventions yet','The project brief already establishes the goal. Add plant-specific conventions as needed, or capture lessons while correcting proposals.')}</section>

 <section class="card"><div class="card-head"><h2>Memory suggestions for review</h2>${badge(queued.length+' pending','amber')}</div><div class="card-body"><p class="micro" style="margin:0">Accept the associated plant update before approving its memory suggestions. Guidance changes invalidate pending plant proposals. Rejecting a plant proposal does not approve or reject its separate memory suggestions.</p></div>${queued.map(s=>`<div class="activity-row"><div class="inline-list">${badge(s.body.kind||'Invalid suggestion')}${badge(s.author)}${badge('Not active','amber')}</div><p style="margin:12px 0">${esc(s.body.text||'Invalid suggestion')}</p><small>${esc(s.body.reason)}</small>${s.errors.length?`<div class="notice red">${s.errors.map(esc).join('; ')}</div>`:''}<div class="inline-list" style="margin-top:12px">${Array.isArray(s.body.evidence)?s.body.evidence.map((e,i)=>btn('Source '+(i+1),'memory-source',`data-id="${s.id}" data-support="${i}"`,'ghost small')).join(''):''}${s.proposal_id?btn('Plant proposal','open-proposal',`data-id="${s.proposal_id}"`,'secondary small'):''}${btn('Reject','memory-reject',`data-id="${s.id}"`,'secondary small')}${btn('Review & approve','memory-approve',`data-id="${s.id}" ${s.errors.length?'disabled':''}`,'small')}</div></div>`).join('')||'<div class="card-body muted">No pending memory suggestions.</div>'}</section>

 <section class="card"><div class="card-head"><h2>Understanding history</h2></div>${u.history.map(r=>`<div class="status-line" style="padding:16px 22px"><span>Revision ${r.revision} · ${esc(r.reason)}<small class="muted"> · ${fmt(r.created)}</small></span>${btn('Inspect','memory-history',`data-revision="${r.revision}"`,'ghost small')}</div>`).join('')}</section>`;

}



function render(){if(!state)return;const r=route();document.querySelectorAll('[data-nav]').forEach(a=>a.classList.toggle('active',a.dataset.nav===r||(r==='log'&&a.dataset.nav==='desk')));const more=$('#topbar-more');if(more&&['history','understanding','corrections','migration','ontology','knowledge','settings'].includes(r))more.classList.add('has-active');else if(more)more.classList.remove('has-active');for(const sel of ['#doc-count','#top-doc-count']){const el=$(sel);if(el)el.textContent=state.documents.length||'';}for(const sel of ['#review-count','#top-review-count']){const el=$(sel);if(el)el.textContent=pending().length||'';}$('#workspace-badge').textContent=workspace==='demo'?'Offline sample':'Your plant';$('#workspace-badge').className='badge '+(workspace==='demo'?'amber':'');$('#model-version').textContent='Version '+state.model.version;$('#switch-workspace').textContent=workspace==='demo'?'Return to your plant ↗':'Open offline walkthrough ↗';const views={overview:PlantExplorer.view,desk:operationsHome,sources:sourceSearchView,networks:networkView,log:logView,corrections:correctionsView,migration:migrationView,documents,review,knowledge,understanding:understandingView,ontology,history,settings:settingsViewV2};$('#main').innerHTML=(views[r]||PlantExplorer.view)();bindInputs();bindSessionSettings();bindOperations();PlantExplorer.bind();if(r==='settings'){const p=providerDraft||settings.provider;if(sessionBackend(p)&&!modelCatalog[p])setTimeout(()=>loadSessionModels(p),0);}}

async function refresh(force=false){const ws=workspace;const next=await api('/api/state');if(ws!==workspace)return;const sig=JSON.stringify([workspace,next.model.version,next.understanding?.revision,next.events?.length,next.documents.length,next.proposals.map(p=>[p.id,p.status,p.decision,p.operation_count??p.body?.operations?.length??0,p.findings?.errors?.length??0]),next.runs.map(r=>[r.id,r.status,r.progress])]);state=next;if(force||sig!==lastSignature){lastSignature=sig;render();}}

function modal(title,html){$('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;if(!$('#dialog').open)$('#dialog').showModal();}

function closeModal(){$('#dialog').close();}

async function source(support,assertion=null){
  const rows=await api('/api/evidence?id='+encodeURIComponent(support.evidence_id));
  if(!rows.length)throw new Error('Evidence not found');
  const e=rows[0],d=doc(e.document_id),region=support.region;
  let text=esc(e.text);if(support.quote)text=text.replace(esc(support.quote),'<mark>'+esc(support.quote)+'</mark>');
  const detail=region&&d.media_type==='application/pdf'?`<section class="source-detail"><h3>Cited drawing detail</h3><a href="/api/evidence-detail/${e.id}?workspace=${workspace}&region=${region.join(',')}" target="_blank" rel="noopener"><img src="/api/evidence-detail/${e.id}?workspace=${workspace}&region=${region.join(',')}" alt="Enlarged cited region from original PDF page ${e.page}"></a><p class="micro">Display strengthens faint ink. Open the image to zoom further, or the original PDF for unchanged source appearance. The highlighted full page below shows its location.</p></section>`:'';
  modal('Source evidence',`<div class="inline-list">${badge(d.name)}${badge(e.locator)}${badge(d.revision?'Rev '+d.revision:'Revision unspecified')}${badge("Catalog label: "+(d.authority||"Unclassified"))}</div>${assertion?.context?.basis?`<p class="source-basis"><strong>Basis of this claim:</strong> ${esc(assertion.context.basis)}</p>`:""}<div class="dialog-actions"><a class="button secondary" href="/api/original/${e.document_id}?workspace=${workspace}#page=${e.page||1}" target="_blank" rel="noopener">Open original - page ${e.page||1}</a>${btn('Download original','original',`data-id="${e.document_id}"`,'secondary')}</div>${support.quote?`<blockquote class="source-quote">${esc(support.quote)}</blockquote>`:''}${detail}${e.image?`<details ${detail?'':'open'}><summary>Full source page${region?' - cited region highlighted':''}</summary><div class="source-image"><img src="/api/render/${e.id}?workspace=${workspace}" alt="Original rendered source page">${region?`<div class="region" style="left:${region[0]*100}%;top:${region[1]*100}%;width:${(region[2]-region[0])*100}%;height:${(region[3]-region[1])*100}%"></div>`:''}</div></details>`:''}${text?`<details ${!e.image?'open':''}><summary>Extracted text</summary><pre class="source-text">${text}</pre></details>`:''}<p class="micro">Evidence ${esc(e.id)} - SHA-256 ${esc(e.sha256)}</p>`);
}
async function documentModal(id){const d=doc(id),ev=await api('/api/evidence?document='+id);const run=state.runs.find(r=>r.document_id===id);const p=state.proposals.find(p=>p.document_id===id&&p.status==='pending');let warnings=[];try{warnings=JSON.parse(d.warnings);}catch{}modal(d.name,`<div class="inline-list">${documentStatus(d)}${badge(d.revision?'Rev '+d.revision:'Revision unspecified')}${badge(d.authority)}</div><p class="micro">SHA-256 ${esc(d.sha256)}</p>${run?.error?`<div class="notice red">${esc(run.error)}</div>`:''}${run&&['queued','running'].includes(run.status)?`<div class="notice"><span class="spin"></span>${esc(run.progress)}</div>`:''}${warnings.length?`<details class="notice amber"><summary>Parsing notes (${warnings.length})</summary><ul>${warnings.map(w=>`<li>${esc(w)}</li>`).join('')}</ul></details>`:''}<h3>Extracted evidence</h3><div style="max-height:310px;overflow:auto">${ev.map(e=>`<div class="status-line"><span>${esc(e.locator)} <small class="muted">· ${e.text.length.toLocaleString()} characters${e.image?' · page image':''}</small></span>${btn('Inspect','evidence',`data-id="${e.id}"`,'ghost small')}</div>`).join('')}</div><div class="dialog-actions">${btn('Download original','original',`data-id="${d.id}"`,'secondary')}${p?btn('Review proposal','open-proposal',`data-id="${p.id}"`,''):btn('Analyze document →','prepare-analysis',`data-id="${d.id}" ${run&&['running','queued'].includes(run.status)?'disabled':''}`,'')}</div>`);}

async function uploadFile(file){if(!file)return;if(workspace==='demo'){toast('Add your own documents in the plant workspace. The demo accepts bundled samples only.',true);return;}if(file.size>40*1024*1024){toast('Maximum file size is 40 MB.',true);return;}modal('Import document',`<p><strong>${esc(file.name)}</strong> <span class="muted">· ${(file.size/1024).toFixed(1)} KB</span></p><div class="form-columns"><div class="form-row"><label for="import-revision">Source revision</label><input id="import-revision" maxlength="120" placeholder="e.g. B / 2024-06"></div><div class="form-row"><label for="import-authority">Source authority</label><select id="import-authority"><option>Unclassified</option><option>Approved as-built drawing</option><option>OEM manual / datasheet</option><option>Approved engineering record</option><option>Maintenance / inspection record</option><option>Personal technical note</option></select></div></div><p class="micro">These labels help assess evidence. A higher authority does not automatically overwrite a conflicting claim. Importing and parsing happen locally.</p><div class="dialog-actions"><button class="button" id="confirm-import">Import locally</button></div>`);$('#confirm-import').onclick=async()=>{const button=$('#confirm-import');button.disabled=true;button.textContent='Parsing locally…';try{const query=new URLSearchParams({name:file.name,revision:$('#import-revision').value,authority:$('#import-authority').value});const result=await api('/api/documents?'+query,file);closeModal();await refresh(true);toast(result.duplicate?'This exact source file is already registered.':'Document preserved and evidence extracted.');await documentModal(result.document.id);}catch(e){toast(e.message,true);button.disabled=false;button.textContent='Import locally';}};}

function bindInputs(){const records=$('#include-records');if(records)records.onchange=()=>{showDocumentRecords=records.checked;render();};const input=$('#file-input');if(input)input.onchange=()=>uploadFile(input.files[0]);const dz=$('#dropzone');if(dz){dz.ondragover=e=>{e.preventDefault();dz.classList.add('drag');};dz.ondragleave=()=>dz.classList.remove('drag');dz.ondrop=e=>{e.preventDefault();dz.classList.remove('drag');if(e.dataTransfer.files.length>1){toast('Add one document at a time.',true);return;}uploadFile(e.dataTransfer.files[0]);};}for(const [id,set] of [['entity-search',v=>{search=v;entityLimit=60;}],['concept-search',v=>conceptSearch=v],['doc-search',v=>{docSearch=v;docLimit=50;}],['proposal-search',v=>{reviewSearch=v;reviewLimit=30;}]]){const el=$('#'+id);if(el)el.oninput=()=>{const pos=el.selectionStart;set(el.value);render();const next=$('#'+id);next.focus();next.setSelectionRange(pos,pos);};}}

async function action(name,el){if(await PlantExplorer.action(name,el))return;if(await operationsAction(name,el))return;const id=el.dataset.id;switch(name){

 case'context-source':{const a=(historical||state.model).assertions.find(a=>a.id===id);await source(a.context_record.provenance.evidence[+el.dataset.support]);break;}

 case'spatial-knowledge':selectedEntity=id;historical=null;location.hash='overview?equipment='+encodeURIComponent(id)+'&view=records';render();break;

 case'memory-brief':memoryRevision=state.understanding.revision;modal('Project purpose and interpretation instructions',`<p class="micro">This brief accompanies every analysis. Editing it creates a new revision; pending proposals then require re-analysis.</p><textarea id="memory-brief" maxlength="6000" class="json-editor" style="font-family:inherit">${esc(state.understanding.brief)}</textarea><div class="dialog-actions">${btn('Save project brief','memory-save-brief','','')}</div>`);break;

 case'memory-save-brief':await api('/api/understanding/update',{action:'brief',brief:$('#memory-brief').value,expected_revision:memoryRevision});closeModal();await refresh(true);toast('Project brief saved for future analyses.');break;

 case'memory-add':memoryEditor();break;

 case'memory-edit':memoryEditor(state.understanding.notes.find(n=>n.id===id));break;

 case'memory-approve':memoryEditor(state.understanding.suggestions.find(n=>n.id===id).body,id);break;

 case'memory-save':{const note={kind:$('#memory-kind').value,text:$('#memory-text').value,scope:$('#memory-scope').value.split(',').map(s=>s.trim()).filter(Boolean)};if(el.dataset.suggestion)await api('/api/understanding/decide',{id:el.dataset.suggestion,decision:'approve',note,expected_revision:memoryRevision});else await api('/api/understanding/update',{action:'note',...note,id:el.dataset.note||null,expected_revision:memoryRevision});closeModal();await refresh(true);toast('Reviewed guidance saved. It will be supplied to relevant future analyses.');break;}

 case'memory-retire':await api('/api/understanding/update',{action:'retire',id,expected_revision:state.understanding.revision});await refresh(true);toast('Note retired; earlier guidance remains in history.');break;

 case'memory-reject':await api('/api/understanding/decide',{id,decision:'reject'});await refresh(true);break;

 case'memory-source':{const n=state.understanding.suggestions.find(s=>s.id===id);await source(n.body.evidence[+el.dataset.support]);break;}

 case'memory-note-source':{const n=state.understanding.notes.find(s=>s.id===id);await source(n.source.evidence[+el.dataset.support]);break;}

 case'memory-history':{const revision=await api('/api/understanding/history?revision='+el.dataset.revision);modal('Understanding revision '+revision.revision,`<p>${esc(revision.reason)}</p><pre class="source-text">${esc(revision.brief)}</pre><h3>Reviewed notes</h3><pre class="source-text">${esc(JSON.stringify(revision.notes,null,2))}</pre>`);break;}

 case'upload':if(workspace==='demo'){toast('Return to your plant to import real documents.',true);break;}if(!$('#file-input')){modal('Add a source document',dropzone());bindInputs();}$('#file-input').click();break;

 case'go-documents':location.hash='documents';break;

 case'go-review':location.hash='review';break;

 case'document':await documentModal(id);break;

 case'evidence':await source({evidence_id:id});break;

 case'original':await downloadOriginal(id);break;

 case'prepare-analysis':{if(workspace==='demo'){await api('/api/analyze',{document_id:id});closeModal();await refresh(true);break;}const p=await api('/api/transmission?document='+id);modal('Review the analysis boundary',`<h3>${esc(p.document.name)}</h3><div class="status-line"><span>Destination</span><strong>${esc(p.provider)} / ${esc(p.model||'Model not configured')}</strong></div><p class="hash">${esc(p.base_url)}</p><div class="status-line"><span>Evidence</span><span>${p.blocks} blocks · ${p.characters.toLocaleString()} characters</span></div><div class="status-line"><span>Page images</span><span>${p.vision?p.rendered_pages+' pages included':'Not included (vision disabled)'}</span></div><div class="notice" style="margin-top:20px">${esc(p.description)}</div><p class="micro">The model makes discovery and proposal calls for each block. Large documents can consume substantial API tokens. Nothing is committed until you review and accept.</p><div class="dialog-actions">${btn('AI connection','go-settings','','secondary')}${btn('Send for AI analysis','analyze',`data-id="${id}"`,'')}</div>`);break;}

 case'go-settings':closeModal();location.hash='settings';break;

 case'analyze':await api('/api/analyze',{document_id:id});closeModal();await refresh(true);toast('Analysis queued. You can continue using the application.');break;

 case'demo-next':await api('/api/demo/next',{});location.hash='review';await refresh(true);break;

 case'select-proposal':selectedProposal=id;render();break;
 case'more-documents':docLimit+=60;render();break;
 case'more-proposals':reviewLimit+=50;render();break;
 case'more-history':historyLimit+=60;render();break;
 case'more-entities':entityLimit+=80;render();break;

 case'open-proposal':selectedProposal=id;closeModal();location.hash='review';render();break;

 case'op-source':{const p=state.proposals.find(p=>p.id===selectedProposal);await source(p.body.operations[+el.dataset.index].evidence[+el.dataset.support]);break;}

 case'fact-source':{const a=(historical||state.model).assertions.find(a=>a.id===id)||state.model.assertions.find(a=>a.id===id);await source(a.evidence[+el.dataset.support],a);break;}

 case'entity-source':{const e=(historical||state.model).entities.find(e=>e.id===id);await source(e.provenance.evidence[0]);break;}

 case'concept-source':await source(state.model.ontology.find(o=>o.key===id).provenance.evidence[0]);break;

 case'old-fact':{const a=state.model.assertions.find(a=>a.id===id);if(!a)throw new Error('Earlier assertion not found');modal('Earlier interpretation',`<h3>${esc(label(a.canonical_subject))}</h3>${factRow(a,state.model)}`);break;}

 case'accept':{el.disabled=true;const result=await api('/api/proposals/accept',{id});await refresh(true);toast('Knowledge committed as version '+result.version+'. Earlier evidence is retained.');break;}

 case'reject':await api('/api/proposals/reject',{id});await refresh(true);toast('Proposal rejected. Source evidence and proposal history are retained.');break;

 case'edit-proposal':{const p=state.proposals.find(p=>p.id===selectedProposal);modal('Edit structured proposal',`<div class="notice">Edits are audited. The validator runs again before acceptance. Remove or correct dependent operations together.</div><textarea class="json-editor" id="patch-json" spellcheck="false" aria-label="Proposal JSON">${esc(JSON.stringify(p.body,null,2))}</textarea><div class="form-row" style="margin-top:20px"><label for="correction-lesson">What should the AI remember from this correction? (optional)</label><textarea id="correction-lesson" maxlength="1200" style="width:100%" placeholder="State a reusable lesson, rather than only the corrected fact."></textarea><p class="micro">Saved for separate review under Project understanding. Accept this plant update before approving the lesson.</p></div><div class="form-row"><label for="correction-scope">Lesson scope (comma-separated; blank applies to all documents)</label><input id="correction-scope" placeholder="e.g. BC-04, protection logic"></div><div id="edit-errors"></div><div class="dialog-actions">${btn('Validate and save','save-proposal',`data-id="${p.id}"`,'')}</div>`);break;}

 case'save-proposal':{let body;try{body=JSON.parse($('#patch-json').value);}catch{throw new Error('The edited proposal is not valid JSON.');}const text=$('#correction-lesson').value.trim();const lesson=text?{kind:'lesson',text,scope:$('#correction-scope').value.split(',').map(s=>s.trim()).filter(Boolean)}:null;const result=await api('/api/proposals/edit',{id,body,lesson});closeModal();await refresh(true);toast(result.errors.length?'Edits saved; validation still needs attention.':'Edits saved and validated.',!!result.errors.length);break;}

 case'run-audit':{const steps=await api('/api/run/'+id);modal('Analysis record',`<p class="micro">Discovery and proposal inputs and model outputs. Images are identified by their immutable render hashes. No API keys are included.</p>${steps.map(s=>`<details class="notice"><summary>${esc(s.stage)} · ${fmt(s.created)}</summary><h3 style="margin-top:18px">Request</h3><pre class="source-text">${esc(JSON.stringify(JSON.parse(s.request),null,2))}</pre><h3>Response</h3><pre class="source-text">${esc(JSON.stringify(JSON.parse(s.response),null,2))}</pre></details>`).join('')||'<p>No completed analysis steps.</p>'}`);break;}

 case'select-entity':selectedEntity=id;render();break;

 case'history-model':historical=await api('/api/model?version='+el.dataset.version);selectedEntity='';location.hash='knowledge';render();break;

 case'current-model':historical=null;selectedEntity='';render();break;

 case'backup':toast('Preparing a consistent workspace backup…');await download('/api/backup','chp-'+workspace+'-backup.zip');toast('Backup downloaded.');break;

 }}

 document.addEventListener('click',async e=>{const el=e.target.closest('[data-action]');if(!el||el.disabled)return;try{await action(el.dataset.action,el);}catch(err){toast(err.message,true);if(el.isConnected)el.disabled=false;}});

 document.addEventListener('keydown',e=>{const el=e.target.closest('g[data-action],path[data-action]');if(el&&['Enter',' '].includes(e.key)){e.preventDefault();el.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});

 $('#close-dialog').onclick=closeModal;

 $('#export').onclick=async()=>{try{await download('/api/export','chp-'+workspace+'-knowledge.json');}catch(e){toast(e.message,true);}};

 $('#switch-workspace').onclick=async()=>{if(busy)return;busy=true;try{workspace=workspace==='plant'?'demo':'plant';historical=null;sourceResults=null;networkResult=null;migrationResult=null;eventFilter='';selectedEntity='';selectedProposal='';search='';conceptSearch='';closeModal();location.hash='overview';await refresh(true);}catch(e){toast(e.message,true);}finally{busy=false;}};

 let lastMajorHashKey='';
window.addEventListener('hashchange',()=>{const more=$('#topbar-more');if(more)more.open=false;
  const savedY=window.scrollY;
  const qp=new URLSearchParams(location.hash.split('?')[1]||'');
  const majorKey=[route(),qp.get('area')||'',qp.get('equipment')||'',qp.get('view')||'',qp.get('scene')||''].join('|');
  const sameScene=majorKey===lastMajorHashKey;
  lastMajorHashKey=majorKey;
  render();
  if(sameScene)window.scrollTo({top:savedY,behavior:'instant'});
  else window.scrollTo(0,0);
});

 function closeClient(){if(!token)return;try{fetch('/api/client/close',{method:'POST',headers:{'X-CHP-Token':token,'Content-Type':'application/json'},body:JSON.stringify({client_id:clientId}),keepalive:true});}catch{}}

 window.addEventListener('pagehide',closeClient);

 async function startClientLease(){

  const res=await fetch('/api/client/lease',{method:'POST',headers:{'X-CHP-Token':token,'Content-Type':'application/json'},body:JSON.stringify({client_id:clientId})});

  if(!res.ok)throw new Error('Could not attach this window to the local server.');

  const reader=res.body?.getReader();if(!reader)return;

  (async()=>{try{while(!(await reader.read()).done){}}catch{}})();

 }

 async function init(){try{const boot=await api('/api/bootstrap');token=boot.token;settings=boot.settings;await startClientLease();await refresh(true);setInterval(()=>poll().catch(()=>{}),2000);}catch(err){$('#main').innerHTML=empty('The local server is not available','Start the application using start.bat or start.sh, then open http://127.0.0.1:8765.');toast(err.message,true);}}

 init();

