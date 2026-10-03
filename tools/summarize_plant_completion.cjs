/* Current read-only graph inventory, separate from the frozen v510 discovery index.
 * Counts diagnose gaps; acceptance comes from checkpoints and original-source review.
 */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const PE=require('../dist/plant-model.js');
const source=process.argv[2];assert.ok(source,'Pass a fresh snapshot JSON');
const snap=JSON.parse(fs.readFileSync(source,'utf8')),p=PE.build(snap.model);
const base='docs/plant-handoff',out=path.join(base,'current');fs.mkdirSync(out,{recursive:true});
const targets=JSON.parse(fs.readFileSync(path.join(base,'inventory/targets.json'),'utf8'));
const batches=JSON.parse(fs.readFileSync(path.join(base,'batches.json'),'utf8')).batches;
const batchmap=new Map(batches.map(b=>[b.id,b]));
const phases=[['phase-1',0,5],['phase-2',6,14],['phase-3',15,29],['phase-4',37,42],['phase-5',43,46]];
const phase=id=>phases.find(([,start,end])=>Number(id.slice(1))>=start&&Number(id.slice(1))<=end)?.[0]||'accepted-reuse';
const rootChecks=new Map();
function stats(id){
 if(rootChecks.has(id))return rootChecks.get(id);
 const e=p.entities.get(id);if(!e)return {present:false};
 const owned=new Set(p.assembly(id).map(e=>e.id)),facts=p.facts.filter(a=>owned.has(a.canonical_subject));
 const own=p.outgoing.get(id)||[],children=new Set((p.children.get(id)||[]).map(a=>a.canonical_subject));
 const result={present:true,canonical_id:id,current_label:e.label,own_fact_count:own.length,direct_children:children.size,assembly_records:owned.size,
   located_records:[...new Set((p.incoming.get(id)||[]).filter(a=>a.predicate==='located_at').map(a=>a.canonical_subject))],
   network_assertions:Object.fromEntries(['material','mechanical','utility','electrical','control'].map(net=>[net,p.networks.filter(a=>a.context.network===net&&owned.has(a.canonical_subject)).length])),
   qualifications:facts.filter(a=>['source_gap','source_discrepancy'].includes(a.predicate)).map(a=>a.id),
   evidence_documents:[...new Set(facts.flatMap(a=>a.evidence||[]).map(r=>evidence.get(r.evidence_id)?.document_id).filter(Boolean))]};
 rootChecks.set(id,result);return result;
}
const evidence=new Map(snap.evidence.map(e=>[e.id,e]));
const acceptedStatuses=new Set(['complete','complete_with_gaps','implemented_with_source_qualifications']);
const rows=targets.map(t=>{
 const batch=batchmap.get(t.implementation_batch),accepted=acceptedStatuses.has(batch.status);
 const entity=snap.model.entities.find(e=>e.id===t.id),currentId=entity?.canonical_id||t.id;
 return {id:t.id,label:t.label,family:t.family,primary_batch:batch.id,phase:phase(batch.id),batch_status:batch.status,
  disposition:accepted?'accepted batch: reuse and recheck qualifications':'remaining batch: inspect existing detail before adding',
  prior_pilot: ['EAC-1A','EAC-1B','UEF-1'].includes(t.label)?'EQUIPMENT_PILOT_REPORT.md':/^(Coal Yard 1|EAC-7|EBA-8|EAD-1|EAF-1|EAE-1|UEB-1|UAX-1|UAX-5)$/.test(t.label)?'COAL_YARD_1_PILOT_REPORT.md':null,
  card:'../targets/'+t.card,...stats(currentId)};
});
const queue=[...p.entities.values()].filter(e=>!p.refs.has(e.id)&&!p.memberships.has(e.id)).map(e=>({id:e.id,label:e.label,classes:p.classes.get(e.id)||[],own_fact_count:(p.outgoing.get(e.id)||[]).length,disposition:'pending source review: unplaced does not mean physical asset missing',owner_batch:'B45',related_target_batches:rows.filter(t=>t.canonical_id===e.id).map(t=>t.primary_batch)}));
const accepted=batches.filter(b=>acceptedStatuses.has(b.status)),remaining=batches.filter(b=>!acceptedStatuses.has(b.status));
const families={conveyors:rows.filter(t=>/^(EAC-(?:[1-5][AB]|7|9|11|13)|EBA-(?:[6]|15|16|17|18|19)[AB]|EBA-(?:8|10|12|14))$/.test(t.label)),transfer_points:rows.filter(t=>/^UEF-(?:1|[3-9]|1[0-3])$/.test(t.label))};
assert.equal(families.conveyors.length,30);assert.equal(families.transfer_points.length,12);
const reviewDate=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Dhaka',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const followups=rows.filter(t=>acceptedStatuses.has(t.batch_status)&&t.present&&t.direct_children===0).map(t=>({id:t.canonical_id,label:t.label,accepted_batch:t.primary_batch,own_fact_count:t.own_fact_count,direct_children:t.direct_children,followup_batch:'B45',disposition:'Review original sources and accepted scope; count alone does not prove missing parts.'}));
const summary={review_date:reviewDate,version:snap.model.version,snapshot:source,scope:'Current graph inventory and recorded acceptance; not a full original-document re-audit or completion score.',entity_records:snap.model.entities.length,active_canonical_entities:p.entities.size,active_facts:p.facts.length,documents:snap.documents.length,evidence_blocks:snap.evidence.length,targets:rows.length,batches:batches.length,accepted_batches:accepted.map(b=>b.id),remaining_batches:remaining.map(b=>b.id),unplaced_nonreference_records:queue.length,network_assertions:Object.fromEntries(['material','mechanical','utility','electrical','control'].map(net=>[net,p.networks.filter(a=>a.context.network===net).length])),phase_batch_counts:Object.fromEntries(phases.map(([id])=>[id,remaining.filter(b=>phase(b.id)===id).length]))};
for(const [name,data]of [['summary.json',summary],['target-status.json',rows],['record-review-queue.json',queue],['main-equipment-status.json',families],['accepted-followups.json',followups]])fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2)+'\n');
const md=['# Current plant detail inventory','','Reviewed '+reviewDate+' at model v'+summary.version+'. This inventory reconciles all '+rows.length+' named targets against the live graph and '+batches.length+' batch definitions. Counts describe model records, not equipment quantities or completion percentages.','','Acceptance remains source- and scope-dependent. '+accepted.length+' batch checkpoints are accepted with qualifications; '+remaining.length+' batches remain, including follow-ups to earlier pilots. See [the five-phase plan](../FIVE_PHASE_PLAN.md).','','## Main conveyors','','| Conveyor | Owned records | Current work disposition | Batch / phase |','|---|---:|---|---|',...families.conveyors.map(t=>`| ${t.label} | ${t.assembly_records??0} | ${acceptedStatuses.has(t.batch_status)?'Accepted with qualifications; reuse':t.prior_pilot?'Existing pilot; targeted follow-up':'Detailed work remains; reuse current facts'} | ${t.primary_batch} / ${t.phase} |`),'','## Transfer points','','| Place | Owned records | Located records | Disposition | Batch / phase |','|---|---:|---:|---|---|',...families.transfer_points.map(t=>`| ${t.label} | ${t.assembly_records??0} | ${t.located_records?.length??0} | ${t.label==='UEF-1'?'Existing pilot; GA/place correction and extension':t.label==='UEF-13'?'B36 accepted; B37 sampling/access remains':'Detailed local assemblies remain'} | ${t.primary_batch} / ${t.phase} |`),'','## Review limits and additional queues','',`- Accepted-package targets without owned children: ${followups.map(t=>t.label).join(', ')}. See accepted-followups.json; B45 must review available detail and scope before closure.`,`- ${queue.length} non-reference canonical records are outside the current process-area projection; some are legitimate shared services or design/identity candidates. Every row is recorded in record-review-queue.json for source-based disposition, not automatic placement.`,`- Current documented electrical-network assertions: ${summary.network_assertions.electrical}; the old v510 statement of zero electrical edges is historical. Plant-wide SLD/feeder closure remains B43.`,'- target-status.json records every target, including reference boundaries and planned yard area identities. No missing target is silently created.','- Existing pilot source gaps, unwritten source dispositions and unresolved identities remain work even when a root has many assertions.','- B37 sampling/access, shared utilities B01–B04 and final integration B43–B46 have scope beyond named target-card roots; batch coverage is not inferred from target-card counts.',''];
fs.writeFileSync(path.join(out,'CURRENT_STATUS.md'),md.join('\n'));console.log(JSON.stringify(summary,null,2));
