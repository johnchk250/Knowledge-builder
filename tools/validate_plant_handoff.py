"""Read-only checks of the handoff's coverage, references and baseline preservation."""
import argparse
import collections
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/plant-handoff'
    out = base / 'inventory/handoff-validation.json'
    read = lambda name: json.loads((base / name).read_text(encoding='utf8'))
    snap = json.loads(Path(args.snapshot).read_text(encoding='utf8'))
    targets, sources = read('inventory/targets.json'), read('inventory/sources.json')
    entities = {e['id']: e for e in read('inventory/entities.json')}
    assertions = {a['id']: a for a in snap['model']['assertions']}
    evidence = {e['id']: e for e in snap['evidence']}
    documents = {d['id']: d for d in snap['documents']}
    batches = read('batches.json')['batches']
    batchmap = {b['id']: b for b in batches}
    errors = []
    check = lambda ok, message: errors.append(message) if not ok else None

    check(len(entities) == len(read('inventory/entities.json')), 'Duplicate entity in inventory')
    check(len(batchmap) == len(batches), 'Duplicate batch ID')
    seen = set()
    for batch in batches:
        check(set(batch['depends_on']) <= seen, f'{batch["id"]}: missing/forward/cyclic dependency')
        seen.add(batch['id'])
    names = {t['label'] for t in targets}
    check(len(names) == len(targets), 'Duplicate named target')
    expected_belts = {f'EAC-{n}{lane}' for n in range(1,6) for lane in 'AB'}
    expected_belts |= {f'EAC-{n}' for n in [7,9,11,13]}
    expected_belts |= {f'EBA-{n}{lane}' for n in [6,15,16,17,18,19] for lane in 'AB'}
    expected_belts |= {f'EBA-{n}' for n in [8,10,12,14]}
    expected_tps = {f'UEF-{n}' for n in [1,*range(3,14)]}
    expected = expected_belts | expected_tps | {'UEE-1','Coal Blending Silo House','UEE-3'}
    expected |= {f'Coal Yard {n}' for n in range(1,5)}
    expected |= {f'{tag}-{n}' for tag in ['EAD','EAE','EAF','UEB','TT'] for n in range(1,5)}
    expected |= {f'UAX-{n}' for n in range(1,9)}
    expected |= {f'EBD-{n}' for n in range(1,7)}
    expected |= {f'{tag}-{n}' for tag in ['EBB','EBC','EBE-CES'] for n in [1,2]}
    expected |= {f'KF-{n}' for n in range(1,5)}
    expected |= {f'Bunker-{letter} of Unit-{unit}' for unit in [1,2] for letter in 'ABCDEF'}
    expected |= {f'Unit-{unit} Coal Bunker Bay' for unit in [1,2]}
    expected |= {f'Coal Ship Unloader-{n}' for n in [1,2,3]}
    expected |= {'UEF-2','TP-16','TP-17','TP-18'}
    check(expected <= names, f'Missing plant targets: {sorted(expected-names)}')
    batch_targets = read('inventory/batch-targets.json')
    assigned = [t['label'] for rows in batch_targets.values() for t in rows]
    check(collections.Counter(assigned) == collections.Counter(t['label'] for t in targets), 'Batch-target map does not assign every target exactly once')
    for target in targets:
        eid = target['id']
        check(target['implementation_batch'] in batchmap, f'{target["label"]}: unknown batch')
        if target['implementation_batch'] in batchmap:
            check(batchmap[target['implementation_batch']]['section'] == target['review_package'], f'{target["label"]}: batch/package mismatch')
        check((base/'targets'/target['card']).exists(), f'Missing card: {target["label"]}')
        check(target['planned'] or eid in entities, f'Missing entity: {target["label"]}')
        for node in target['assembly']:
            check(node in entities, f'{target["label"]}: dangling assembly node {node}')
        for key in ['assembly_source_pages','applicable_source_pages']:
            for ref in target[key]:
                pages={e['page'] for e in evidence.values() if e['document_id']==ref['document_id']}
                check(set(ref['pages'])<=pages,f'{target["label"]}: bad source pages')
        for fid in target['qualification_ids']+target['boundary_connection_ids']+target['scene_connection_ids']+target['applicable']:
            check(fid in assertions,f'{target["label"]}: missing assertion {fid}')
        check(len(target['review_dimensions'])==10,f'{target["label"]}: incomplete coverage dimensions')
    with (base/'inventory/coverage.csv').open(encoding='utf-8-sig',newline='') as file:
        coverage=list(csv.DictReader(file))
    check({r['target'] for r in coverage}==names, 'Coverage matrix does not cover all targets')
    with (base/'inventory/record-review-queue.csv').open(encoding='utf-8-sig',newline='') as file:
        queue=list(csv.DictReader(file))
    check({r['id'] for r in queue}==set(entities),'Review queue omits baseline records')
    for source in sources:
        check(source['id'] in documents, f'Unknown document {source["id"]}')
        check((ROOT/source['original']).is_file(),f'Missing original {source["id"]}')
        check(source['sha256']==documents[source['id']]['sha256'],f'Changed source hash {source["id"]}')
        for page, ids in source['pages'].items():
            for eid in ids:
                check(eid in evidence and evidence[eid]['document_id']==source['id'] and evidence[eid]['page']==int(page),f'Incorrect page/evidence mapping {source["id"]} {eid}')
    large_supports=set();active_fact_count=0;support_count=0
    for fact in assertions.values():
        if fact.get('retirement') or fact.get('suppressed'):continue
        active_fact_count+=1
        check(bool(fact.get('context',{}).get('kind')),f'Missing context.kind: {fact["id"]}')
        for ref in fact['evidence']:
            support_count+=1;eid=ref['evidence_id']
            check(eid in evidence,f'Missing source support {eid}')
            if eid not in evidence:continue
            if ref.get('quote'):check(ref['quote'] in evidence[eid]['text'],f'Quote mismatch: {fact["id"]}')
            region=ref.get('region')
            if region:
                valid=len(region)==4 and 0<=region[0]<region[2]<=1 and 0<=region[1]<region[3]<=1
                check(valid,f'Invalid region: {fact["id"]}')
                if valid and (region[2]-region[0])*(region[3]-region[1])>=.9:large_supports.add(fact['id'])
    # All current containment edges as projected by the application; broad multi-parent
    # memberships are not errors. Only actual directed cycles are reported.
    cycles=[];state={};trail=[]
    def visit(node):
        if state.get(node)==2:return
        if state.get(node)==1:
            cycles.append(trail[trail.index(node):]+[node]);return
        state[node]=1;trail.append(node)
        for child in entities[node]['children']:visit(child)
        trail.pop();state[node]=2
    for node in entities:visit(node)
    check(not cycles,'Existing current containment cycles require explicit findings disposition')
    # Validate only this handoff's links, not unrelated historical README artifacts.
    markdown=list(base.rglob('*.md'))+[ROOT/'PLANT_MODEL_IMPLEMENTATION_HANDOFF.md']
    idsets={'doc':set(documents),'ev':set(evidence),'ent':set(entities),'fact':set(assertions)}
    link_count=0;reference_count=0
    def anchors(path):
        headings=re.findall(r'^#+\s+(.+)$',path.read_text(encoding='utf8'),re.M)
        return {re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
    for path in markdown:
        body=path.read_text(encoding='utf8')
        for prefix, ident in re.findall(r'\b(doc|ev|ent|fact)_([0-9a-f]{20})\b',body):
            reference_count+=1
            check(prefix+'_'+ident in idsets[prefix],f'{path.name}: unknown {prefix}_{ident}')
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',body):
            if '://' in link or link.startswith('mailto:'):continue
            file,_,fragment=unquote(link).partition('#')
            dest=(path.parent/file).resolve() if file else path
            link_count+=1
            check(dest.exists() or dest==out,f'{path.name}: missing link {link}')
            if fragment and dest.exists() and dest.suffix=='.md':
                check(fragment in anchors(dest),f'{path.name}: missing anchor {link}')
    with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        live=Store.__new__(Store).model(db=db)
        live_docs=[dict(row) for row in db.execute('SELECT * FROM documents ORDER BY name')]
        live_ev=[dict(row) for row in db.execute('SELECT * FROM evidence ORDER BY document_id,page,id')]
    same_model=live==snap['model'];same_docs=live_docs==snap['documents'];same_evidence=live_ev==snap['evidence']
    check(same_model,'Live model changed since snapshot: reconcile authored handoff before claiming unchanged baseline')
    check(same_docs and same_evidence,'Document/evidence inventory changed since snapshot')
    report={'ok':not errors,'baseline_version':snap['model']['version'],'live_version':live['version'],
        'target_cards':len(targets),'main_conveyors_covered':len(expected_belts),'in_scope_tps_covered':len(expected_tps),
        'batches':len(batches),'all_targets_have_one_primary_batch':len(assigned)==len(targets),
        'canonical_records_queued':len(queue),'sources_resolve':len(sources),'markdown_links_checked':link_count,
        'explicit_identifiers_checked':reference_count,'current_containment_cycles':cycles,
        'active_assertions_checked':active_fact_count,'source_supports_checked':support_count,
        'assertions_with_pagewide_support':len(large_supports),
        'canonical_model_unchanged':same_model,'documents_unchanged':same_docs,'evidence_unchanged':same_evidence,
        'errors':errors,'limitation':'Structural consistency and preservation only; source semantics require the prescribed engineering review.'}
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
