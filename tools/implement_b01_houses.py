"""One-time reviewed B01 house reconciliation from v598; isolated rehearsal first."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate, commit
from tools.implement_b00_corrections import save, support

BASE = ROOT / 'output/plant-enrichment/B01/houses'
DOC = 'doc_bca09d68af9b43e3b633'
HOUSES = [
    ('ent_da33b533a40c4cabbe39', 'ent_bdf8e7e7f7f8485b80fe',
     'ev_08ec0122d044468d8975', [.04, .21, .365, .469], '175050'),
    ('ent_120872c17d724862bee6', 'ent_36135b45a07c4d03bf06',
     'ev_d705803b38ce46ccb5fa', [.628, .035, .975, .32], '175051'),
]


def build(snap):
    ids = {e['label']: e['id'] for e in snap['model']['entities']
           if e['id'] == e['canonical_id']}
    ops = []
    for n, (old, house, eid, region, ga) in enumerate(HOUSES, 1):
        provenance = support(eid, region)
        ops.append({'op': 'merge', 'source': old, 'target': house,
                    'reason': f'DFDS P&ID 175089 Rev1 sheet {n} explicitly labels '
                    f'Pump cum Compressor House-{n} (UGA-{n}) and references '
                    f'DS Pump House-{n} GA {ga}. Original matching GA title, '
                    'numbered equipment and key plan visually cross-checked. '
                    'Same physical house; retain tagged UGA identity and redirect '
                    'all DS-house facts/aliases without changing component ownership.',
                    **provenance})
        ops.append({'op': 'assert', 'subject': house, 'predicate': 'equipment_role',
                    'value': f'Common pump and compressor house for DFDS System-{n}; '
                    f'P&ID 175089 Rev1 explicitly identifies UGA-{n} and references '
                    f'DS Pump House-{n} GA {ga}. Common service production is '
                    'distinct from the local application equipment at consuming areas.',
                    'context': {'kind': 'specification', 'basis':
                                f'DFDS P&ID PDF p{n}, Rev1, approval stamp 14-Dec-2018. '
                                'Design identity/location, not field/as-built confirmation.'},
                    **provenance})
        for prefix in ['DFDSP', 'DFDSC']:
            for lane in ['A', 'B']:
                ops.append({'op': 'assert', 'subject': ids[f'{prefix}-{n}{lane}'],
                            'predicate': 'located_at', 'object_entity': house,
                            'context': {'kind': 'specification', 'basis':
                                        f'P&ID sheet {n}: equipment inside explicitly '
                                        f'labelled UGA-{n} house boundary. Existing '
                                        'DFDS system ownership is retained.'},
                            **provenance})
    return {'summary': 'B01: reconcile proven UGA/DS house identities and locate common DFDS equipment',
            'operations': ops, 'intake_assessment': {
                'route': 'mixed', 'purpose': 'Source-proven shared house identity and physical placement',
                'questions': ['Which numbered DS house is the same physical UGA house?',
                              'Which existing DFDS pumps/compressors are shown inside each house?'],
                'reviewed_evidence_ids': [e['id'] for e in snap['evidence'] if e['document_id'] == DOC],
                'gaps': ['Both original P&ID pages visually reviewed for title/revision, house identity, '
                         'referenced GA numbers and equipment tags. All 13 evidence blocks inventoried. '
                         'Dense application/BOM/logic detail is not re-extracted by this package; B02 owns it.',
                         'Grouped versus individual DFDS/DFDSP/SC naming and other common assets remain '
                         'B01 work; no additional identity merge is inferred from a prefix or suffix.']}}


def preserved(a):
    return {k: v for k, v in a.items() if k not in ['canonical_subject', 'canonical_object']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snap = json.loads((ROOT / 'output/plant-enrichment/B00/accepted-snapshot.json').read_text(encoding='utf-8'))
    body = build(snap)
    plant = ROOT / 'data/plant'
    out = BASE / ('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'result.json').exists(), 'Already completed; inspect checkpoint.'
    with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 598, 'Changed model requires new source/state review.'
        assert before == snap['model'], 'Snapshot differs from current model.'
        if not args.apply:
            backup = BASE / 'backup-v598'
            backup.mkdir(exist_ok=True)
            for dest in [out / 'plant.sqlite3', backup / 'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:
                    db.backup(dst)
            copied = []
            for d in snap['documents']:
                if d['id'] not in [DOC, 'doc_af4f437e54f143af9f62', 'doc_d0cb76dd3ab3478295db']:
                    continue
                assert hashlib.sha256((plant / 'originals' / d['sha256']).read_bytes()).hexdigest() == d['sha256']
                paths = [Path('originals') / d['sha256']] + [Path('renders') / e['image'] for e in snap['evidence']
                         if e['document_id'] == d['id'] and e['image']]
                for rel in set(paths):
                    dest = backup / rel
                    dest.parent.mkdir(exist_ok=True)
                    shutil.copy2(plant / rel, dest)
                    copied.append(str(rel))
            save(backup / 'manifest.json', {'version': 598, 'copied_files': copied,
                 'scope': 'Consistent full SQLite database plus reviewed originals/renders; other source assets unchanged in data/plant.'})
    if args.apply:
        assert body == json.loads((BASE / 'rehearsal/package.json').read_text(encoding='utf-8'))
        assert json.loads((BASE / 'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out / 'package.json', body)
    store = Store(plant if args.apply else out)
    visual = [h[2] for h in HOUSES]
    report = validate(store, {k: body[k] for k in ['summary', 'operations']}, DOC, 598, visual_ids=visual)
    save(out / 'validation.json', report)
    assert not report['errors'], report
    staged = stage(store, DOC, body, visual_ids=visual, analysis_dir=str(out), expected_version=598)
    result = commit(store, staged['proposal_id'])
    save(out / 'commit.json', {'proposal_id': staged['proposal_id'], **result})
    after = store.model()
    save(out / 'model.json', after)
    assert after['version'] == 599
    facts = {a['id']: a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a) == preserved(facts[a['id']]), a['id']
    redirects = {old: target for old, target, *_ in HOUSES}
    for a in before['assertions']:
        for field in ['canonical_subject', 'canonical_object']:
            assert facts[a['id']][field] == redirects.get(a[field], a[field]), (a['id'], field)
    assert len(after['entities']) == len(before['entities'])
    assert after['aliases'] == before['aliases']
    entities = {e['id']: e for e in after['entities']}
    for old, target in redirects.items():
        assert entities[old]['canonical_id'] == target
        assert entities[target]['canonical_id'] == target
    added = [a for a in after['assertions'] if a['created_version'] == 599]
    assert len(added) == 10
    assert len([a for a in added if a['predicate'] == 'located_at']) == 8
    assert len(after['merges']) == len(before['merges']) + 2
    save(out / 'result.json', {'ok': True, 'version': 599, 'proposal_id': staged['proposal_id'],
         'preserved_assertions': len(before['assertions']), 'redirects': redirects,
         'added_claims': added, 'checks': ['all assertion content preserved', 'only two intended canonical redirects',
         'all alias history retained', 'no entity creation', 'eight documented equipment locations']})
    print(json.dumps({'ok': True, 'version': 599, 'proposal_id': staged['proposal_id'], 'mode': out.name}))


if __name__ == '__main__':
    main()
