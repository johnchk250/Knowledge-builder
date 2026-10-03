"""Reviewed, one-time B01 potable-water identity reconciliation from v615."""
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
from tools.implement_b01_houses import preserved

BASE = ROOT / 'output/plant-enrichment/B01/potable-identities'
DOC = 'doc_e17edf6897d746fabe12'
PAIRS = [
    ('ent_059b58691a3e4b45b4b3', 'ent_a408ea3a3ca04f2899b6', 'A', '00EGC04KP001'),
    ('ent_5acb954d9e3f49a08c70', 'ent_6380321730824a9a8be8', 'B', '00EGC04KP002'),
]
HOUSE = 'ent_36135b45a07c4d03bf06'
DIAGRAM = 'ev_a179ac4ae9454cedb364'
CONTROL = 'ev_ed7fcab701e04f15ba5b'


def package(snap):
    diagram = support(DIAGRAM, [.54, .505, .79, .70])
    control = support(CONTROL, [.05, .23, .94, .82])
    proof = {**diagram, 'origin': 'inferred',
             'evidence': diagram['evidence'] + control['evidence']}
    ops = []
    for old, target, lane, kks in PAIRS:
        ops.append({'op': 'merge', 'source': old, 'target': target,
                    'reason': f'PDF p15 labels PWP-1{lane} inside Pump House-2 with KKS {kks}; '
                    f'p7 names PWP-2{lane} with the SAME KKS and Tank-2 level/pressure/filter namespace. '
                    'These are two source names for the same design pump, not two separate stations. '
                    'Retain schedule ratings and control wording together; no installed/as-built tag choice.', **proof})
        ops.append({'op': 'alias', 'entity': target,
                    'alias': f'Potable Water Pump PWP-1{lane} / PWP-2{lane} ({kks})', **proof})
        for predicate, value, prov in [
            ('documented_source_identity', f'Potable-water design pump {kks}: '
             f'PWP-1{lane} on the p15 diagram/schedule and PWP-2{lane} in p7 control text. '
             'The matching individual KKS, Pump House-2 and Tank-2 PWS namespace establish source identity. '
             'Canonical record reuses the existing control-text pump and retains all schedule/control facts.', proof),
            ('source_discrepancy', 'Philosophy175319 Rev5 p7 refers to potable P&ID175091 Rev3 sheet5, '
             'while the potable drawing reproduced at PDFp15 is printed sheet4of5 and calls the pair '
             'PWP-1A/1B rather than PWP-2A/2B. Individual KKS00EGC04KP001/002 match. '
             'Short-name/sheet discrepancies are retained; B03 must check final tag schedule and source-specific controls. '
             'A source design identity does not establish a current field name or commissioned logic.', proof),
        ]:
            ops.append({'op': 'assert', 'subject': target, 'predicate': predicate, 'value': value,
                        'context': {'kind': 'specification', 'basis':
                                    'Original175319 Rev5, 24-Apr-2020, approved26-May-2020; '
                                    'p7 control text versus p15 appended175091 Rev3 (28-Mar-2019).'}, **prov})
        ops.append({'op': 'assert', 'subject': target, 'predicate': 'located_at', 'object_entity': HOUSE,
                    'context': {'kind': 'specification', 'basis':
                                'PDFp15 explicitly labels Pump House-2 around the potable pair. '
                                'Existing house membership retained; design placement.'}, **diagram})
    return {'summary': 'B01: reconcile PWP-1A/B schedule and PWP-2A/B control identities through matching KKS',
            'operations': ops, 'intake_assessment': {
                'route': 'mixed', 'purpose': 'Eliminate duplicate potable design pumps while retaining differing source names',
                'questions': ['Do the schedule and control text identify the same individual KKS pump?',
                              'Which common house contains the pair?'],
                'reviewed_evidence_ids': [e['id'] for e in snap['evidence'] if e['document_id'] == DOC],
                'gaps': ['Document-wide evidence inventory reviewed for source/page identity. '
                         'Semantic review in this milestone is original p7 text and p15 house, pump KKS, '
                         'schedule and title/revision regions, with p1 cover and earlier B01 source reviews. '
                         'Remaining detailed SW/PW controls and piping remain B03; no claim of whole-document extraction.',
                         'Catalog/house/vendor references inspected for potable identity; the explicit same-sheet '
                         'individual KKS bridge resolves the design duplicates. Final field tag and commissioned logic remain unverified.']}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    snap = json.loads((ROOT/'output/plant-enrichment/B01/baseline-v615-continuation.json').read_text(encoding='utf8'))
    body = package(snap)
    plant = ROOT/'data/plant'
    out = BASE/('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'commit.json').exists(), 'Already committed; resume verification, never replay.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 615 and before == snap['model'], 'Live state changed; re-review required.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v615'
            backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3', backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:
                    db.backup(dst)
            d = next(d for d in snap['documents'] if d['id'] == DOC)
            assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest() == d['sha256']
            copied = []
            paths = {Path('originals')/d['sha256']} | {Path('renders')/e['image'] for e in snap['evidence']
                                                          if e['document_id'] == DOC and e['image']}
            for rel in paths:
                dest = backup/rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(plant/rel, dest)
                copied.append(str(rel))
            save(backup/'manifest.json', {'version': 615, 'copied_files': copied,
                                         'scope': 'Consistent complete SQLite backup and immutable package originals/renders.'})
    if args.apply:
        assert body == json.loads((BASE/'rehearsal/package.json').read_text(encoding='utf8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    save(out/'package.json', body)
    store = Store(plant if args.apply else out)
    visual = [DIAGRAM, CONTROL]
    report = validate(store, {k: body[k] for k in ['summary', 'operations']}, DOC, 615, visual_ids=visual)
    save(out/'validation.json', report)
    assert not report['errors'], report
    staged = stage(store, DOC, body, visual_ids=visual, analysis_dir=str(out), expected_version=615)
    result = commit(store, staged['proposal_id'])
    save(out/'commit.json', {'proposal_id': staged['proposal_id'], **result})
    after = store.model()
    save(out/'model.json', after)
    assert after['version'] == 616
    redirects = {a: b for a, b, *_ in PAIRS}
    facts = {a['id']: a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a) == preserved(facts[a['id']]), a['id']
        for field in ['canonical_subject', 'canonical_object']:
            assert facts[a['id']][field] == redirects.get(a[field], a[field]), (a['id'], field)
    aliases = {a['id']: a for a in after['aliases']}
    assert all(a == aliases[a['id']] for a in before['aliases'])
    assert len(after['aliases']) == len(before['aliases'])+2
    assert before['conflicts'] == after['conflicts']
    assert len(after['entities']) == len(before['entities'])
    assert len(after['merges']) == len(before['merges'])+2
    added = [a for a in after['assertions'] if a['created_version'] == 616]
    assert len(added) == 6
    save(out/'result.json', {'ok': True, 'version': 616, 'proposal_id': staged['proposal_id'],
                             'redirects': redirects, 'added_claims': added,
                             'preserved_assertions': len(before['assertions']),
                             'checks': ['all original assertion payloads and aliases preserved',
                                        'two intended KKS-proven redirects', 'no new pump records', 'four conflicts unchanged']})
    print(json.dumps({'ok': True, 'version': 616, 'mode': out.name, 'proposal_id': staged['proposal_id']}))


if __name__ == '__main__':
    main()
