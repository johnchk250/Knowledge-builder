"""Apply the Passes 6-10 top-model delta to the canonical plant model.

The delta follows DELTA_FORMAT.md in the handover zip: one proposal per source
document, operations in the chp.patches format, evidence supports either
{"evidence_id","quote"} (exact substring of the immutable extracted text) or a
page/region form the tool resolves first:

    {"document": "...", "page": 3, "quote": "..."}          -> resolved by text
    {"document": "...", "page": 3, "region": [l,t,r,b]}     -> visual support

All operations are validated with chp.patches.validate and staged through
chp.reviewed_ingestion.stage, one proposal per document, chained on top of the
current live version. Modes:

    --check      validate only (no database change, no copy)
    --rehearse   apply the whole delta onto a throwaway copy of the live DB
    --apply      guarded live acceptance; requires a matching --rehearse first

Whitespace-tolerant quote repair is applied when the delta quote differs from
the stored text only by line wrapping/spacing; every repair is reported.
"""
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chp.patches import validate, commit
from chp.reviewed_ingestion import stage
from chp.store import Store


def find_quote(text, quote):
    if not quote:
        return None
    if quote in text:
        return quote
    pattern = re.sub(r'\s+', r'\\s+', re.escape(quote.strip()))
    if not pattern.strip():
        return None
    match = re.search(pattern, text)
    return match.group(0) if match else None


def load_delta(path):
    raw = Path(path).read_text(encoding='utf-8')
    delta = json.loads(raw)
    if delta.get('schema_version') != 1 or not isinstance(delta.get('proposals'), list):
        raise ValueError('Unsupported delta file: expected schema_version 1 and a proposals array')
    return delta, hashlib.sha256(raw.encode('utf-8')).hexdigest()


def doc_evidence(store, doc):
    return {e['id']: e for e in store.rows('SELECT * FROM evidence WHERE document_id=?', (doc,))}


def body_size(proposal):
    return len(json.dumps({'summary': proposal.get('summary', ''), 'operations': proposal.get('operations') or []}))


def resolve_supports(store, proposal, repairs, problems):
    doc = proposal['document']
    ev = doc_evidence(store, doc)
    if not ev:
        problems.append('%s: document has no evidence blocks in the canonical DB' % doc)
    visual = set()
    for i, op in enumerate(proposal['operations']):
        supports = op.get('evidence')
        if not isinstance(supports, list):
            continue
        kept = []
        for j, support in enumerate(supports):
            label = 'op %d.%d' % (i + 1, j + 1)
            if not isinstance(support, dict):
                problems.append('%s: evidence support is not an object' % label)
                continue
            eid = support.get('evidence_id')
            quote = support.get('quote', '') or ''
            region = support.get('region')
            page = support.get('page')
            if not eid and page is not None:
                page_evs = [e for e in ev.values() if str(e['page']) == str(page)]
                if quote:
                    for e in page_evs:
                        fixed = find_quote(e['text'] or '', quote)
                        if fixed:
                            eid, quote = e['id'], fixed
                            break
                    if not eid:
                        problems.append('%s: quote not found on page %s of %s' % (label, page, doc))
                        continue
                elif region is not None:
                    imgs = [e for e in page_evs if e['image']]
                    if not imgs:
                        problems.append('%s: no rendered page image for page %s of %s' % (label, page, doc))
                        continue
                    eid = imgs[0]['id']
                else:
                    problems.append('%s: page reference needs quote or region' % label)
                    continue
            if not eid or eid not in ev:
                problems.append('%s: evidence %s does not belong to %s' % (label, eid, doc))
                continue
            block = ev[eid]
            if quote:
                fixed = find_quote(block['text'] or '', quote)
                if not fixed:
                    problems.append('%s: quote not found in %s (evidence %s, page %s)' % (label, doc, eid, block['page']))
                    continue
                if fixed != quote:
                    repairs.append({'document': doc, 'op': i + 1, 'evidence_id': eid, 'from': quote, 'to': fixed})
                quote = fixed
            if not quote and region is None:
                problems.append('%s: support needs an exact quote or a visual region' % label)
                continue
            if region is not None:
                if not block['image']:
                    problems.append('%s: region support needs a rendered page image (evidence %s)' % (label, eid))
                    continue
                visual.add(eid)
            clean = {'evidence_id': eid, 'quote': quote}
            if region is not None:
                clean['region'] = region
            kept.append(clean)
        op['evidence'] = kept
    return sorted(visual)


def build_body(proposal, evidence_ids):
    ops = proposal['operations']
    route = proposal.get('route')
    if not route:
        route = 'reference' if ops and all(o.get('op') == 'source_note' for o in ops) else 'mixed'
    depth = ', '.join(proposal.get('depth_ids') or []) or 'the depth item'
    questions = proposal.get('questions') or []
    if ops and not questions:
        questions = ['What does this source establish for %s?' % depth]
    assessment = {'route': route,
                  'purpose': proposal.get('purpose') or proposal['summary'],
                  'questions': questions,
                  'gaps': proposal.get('gaps') or [],
                  'reviewed_evidence_ids': sorted(evidence_ids)}
    return {'summary': proposal['summary'], 'operations': ops, 'intake_assessment': assessment}


def copy_live(live_dir, target_dir):
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)
    with sqlite3.connect('file:%s?mode=ro' % (live_dir / 'plant.sqlite3').as_posix(), uri=True) as src:
        with sqlite3.connect(target_dir / 'plant.sqlite3') as dst:
            src.backup(dst)


def process(delta, store, out_dir, commit_changes):
    """Walk the delta in order; validate everything and optionally stage+commit."""
    base = delta['base_version']
    if store.version() != base:
        raise ValueError('Delta base_version %s does not match model version %s'
                         % (base, store.version()))
    repairs, problems, entries = [], [], []
    running = base
    for index, proposal in enumerate(delta['proposals']):
        doc = proposal.get('document')
        ops = proposal.get('operations') or []
        if not doc or not isinstance(ops, list):
            raise ValueError('Proposal %d is missing document/operations' % (index + 1))
        if not ops:
            entries.append({'index': index, 'document': doc, 'skipped': 'no operations'})
            continue
        if len(ops) > 500 or body_size(proposal) > 500000:
            raise ValueError('Proposal %d exceeds the 500-operation / 500 KB limit; split it' % (index + 1))
        before = len(problems)
        visual = resolve_supports(store, proposal, repairs, problems)
        if len(problems) > before:
            entries.append({'index': index, 'document': doc, 'errors': ['support resolution failed']})
            continue
        evidence_ids = [e['id'] for e in store.rows('SELECT id FROM evidence WHERE document_id=?', (doc,))]
        body = build_body(proposal, evidence_ids)
        report = validate(store, {k: body[k] for k in ('summary', 'operations')}, doc, running, visual_ids=visual)
        if commit_changes or report['errors']:
            pkg_dir = out_dir / ('%02d-%s' % (index + 1, doc[4:16]))
            pkg_dir.mkdir(parents=True, exist_ok=True)
            (pkg_dir / 'package.json').write_text(
                json.dumps(body, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            (pkg_dir / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        if report['errors']:
            problems.extend(['proposal %d (%s): %s' % (index + 1, doc, e) for e in report['errors']])
            entries.append({'index': index, 'document': doc, 'errors': report['errors']})
            continue
        entry = {'index': index, 'document': doc, 'pass': proposal.get('pass_id'),
                 'ops': len(ops), 'warnings': report['warnings']}
        if commit_changes:
            staged = stage(store, doc, body, visual_ids=visual, analysis_dir=str(pkg_dir), expected_version=running)
            result = commit(store, staged['proposal_id'])
            running = result['version']
            entry.update(proposal_id=staged['proposal_id'], version=running)
            (pkg_dir / 'result.json').write_text(json.dumps(entry, indent=2) + '\n', encoding='utf-8')
            print(json.dumps({'document': doc[:12], 'pass': proposal.get('pass_id'),
                              'proposal': staged['proposal_id'], 'version': running, 'ops': len(ops)}))
        entries.append(entry)
    return entries, repairs, problems, running


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('delta', help='path to the returned delta JSON')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='validate only (default)')
    mode.add_argument('--rehearse', action='store_true', help='apply on a copy of the live DB')
    mode.add_argument('--apply', action='store_true', help='guarded live acceptance (needs --rehearse first)')
    parser.add_argument('--workdir', default=str(ROOT / 'output/plant-enrichment/pass06-10-delta'),
                        help='rehearsal/report directory (default output/plant-enrichment/pass06-10-delta)')
    args = parser.parse_args()

    delta, digest = load_delta(args.delta)
    live = ROOT / 'data/plant'
    workdir = Path(args.workdir)

    if args.apply:
        summary_file = workdir / 'rehearsal-summary.json'
        if not summary_file.exists():
            raise SystemExit('No rehearsal found at %s; run --rehearse first' % summary_file)
        summary = json.loads(summary_file.read_text(encoding='utf-8'))
        if summary['delta_sha256'] != digest:
            raise SystemExit('Delta file changed since rehearsal; re-run --rehearse')
        store = Store(live)
        out_dir = workdir / 'apply'
        out_dir.mkdir(parents=True, exist_ok=True)
        entries, repairs, problems, running = process(delta, store, out_dir, commit_changes=True)
        if problems:
            raise SystemExit('Apply stopped with problems:\n' + '\n'.join(problems))
        rehearsed_chain = [e.get('version') for e in summary['entries'] if e.get('version')]
        applied_chain = [e.get('version') for e in entries if e.get('version')]
        if applied_chain != rehearsed_chain:
            raise SystemExit('Applied chain %s does not match the rehearsal chain %s'
                             % (applied_chain, rehearsed_chain))
        result = {'applied': True, 'delta_sha256': digest, 'base_version': delta['base_version'],
                  'final_version': running, 'entries': entries, 'repairs': repairs, 'problems': problems}
    elif args.rehearse:
        target = workdir / 'rehearsal'
        copy_live(live, target)
        entries, repairs, problems, running = process(delta, Store(target), target, commit_changes=True)
        summary = {'delta_sha256': digest, 'base_version': delta['base_version'],
                   'final_version': running, 'entries': entries, 'repairs': repairs}
        (workdir / 'rehearsal-summary.json').write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        result = {'ok': not problems, 'rehearsed': True, **{k: summary[k] for k in ('base_version', 'final_version')},
                  'entries': entries, 'repairs': repairs, 'problems': problems}
    else:
        out_dir = workdir / 'check'
        out_dir.mkdir(parents=True, exist_ok=True)
        entries, repairs, problems, running = process(delta, Store(live), out_dir, commit_changes=False)
        result = {'ok': not problems, 'check': True, 'base_version': delta['base_version'],
                  'live_version': running, 'entries': entries, 'repairs': repairs, 'problems': problems}

    (workdir / 'last-run.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': not result.get('problems'),
                      'final_version': result.get('final_version', result.get('live_version')),
                      'proposals': len([e for e in result['entries'] if e.get('version') or e.get('errors') is not None or e.get('ops')]),
                      'repairs': len(result.get('repairs') or []),
                      'problems': len(result.get('problems') or [])}))
    if result.get('problems'):
        for problem in result['problems']:
            print('PROBLEM: ' + problem)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
