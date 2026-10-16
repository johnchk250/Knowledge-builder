"""Pass-1 Q4 close-out (DQ-B07-001 tentative leg), guarded at v730.

Applies the verified p8 follow-up return (top-model-result-p8.json): both Type-1
motor cells carry (Tentative); existing Tier-1 SUL-1 feeder/reel/dust records stand.
One source (doc_1518e219127b4b0eaa3a p8). Default rehearsal; --apply for live.
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-01-p8'
COPY = BASE / 'rehearsal-copy'
DOC = 'doc_1518e219127b4b0eaa3a'
SUL1 = 'ent_1a57e15407c145a19284'
EV8 = 'ev_a700ca88c76540e2ae1c'
BASIS = ('175155 Type-1 technical table p8 (sheet 1 of 5, GA74042951, REV 9, approved 14-Dec-2020). '
         'Design only.')


def ev(region):
    return dict(evidence_id=EV8, quote='', region=region)


def body():
    ops = [
        dict(op='assert', subject=SUL1, predicate='unloader_without_grab_weight', value=983, unit='t',
             context=dict(kind='specification', basis=BASIS + ' WEIGHTS (SUL-1 & SUL-2) box, per machine; '
                          'coal grab 17.5t cross-checked in table and box.'),
             origin='explicit', confidence=0.95,
             evidence=[ev([0.6481, 0.1786, 0.7750, 0.2051])]),
        dict(op='assert', subject=SUL1, predicate='coal_grab_self_weight', value=17.5, unit='t',
             context=dict(kind='specification', basis=BASIS + ' Grab-bucket self-weight row + weights box, '
                          'per machine Type 1.'),
             origin='explicit', confidence=0.95,
             evidence=[ev([0.6481, 0.1786, 0.7750, 0.2051])]),
        dict(op='source_note', origin='explicit', confidence=0.97,
             evidence=[ev([0.8931, 0.4306, 0.9769, 0.4377]), ev([0.7175, 0.1149, 0.8012, 0.1220]),
                       ev([0.8038, 0.4155, 0.9769, 0.4456]), ev([0.6281, 0.0999, 0.8012, 0.1299]),
                       ev([0.8038, 0.5799, 0.9769, 0.6180])],
             text=('Q4 verified by second independent read of p8: vibro-feeder cell "1 x 22 (Tentative)" kW and '
                   'cable-reeling-drum cell "1 x 7kW (Tentative)" both carry the tag; rows read 1700/1870 t/h VVVF '
                   'and Mono-spairal Type with VVVF/stall-torque drive ("spairal" spelling as drawn, not '
                   'normalised); dust Type plain-water spray 3bar jetty outlets/30m hose reel. This closes the '
                   'v720 tentative-gap: existing SUL-1 feeder/reel/dust records stand as written; no values '
                   'promoted beyond tentative. Cable-reel row sits in the untitled Contd block beside the Type-1 '
                   'table; Type-1 applicability retained as inference, flagged for a second source.')),
    ]
    return dict(summary='SUL-1 weights + p8 tentative-tag verification (175155 p8)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Close the SUL1 tentative-rating leg with p8 verification',
                    questions=['Do the Type-1 motor cells carry Tentative tags?'],
                    reviewed_evidence_ids=[EV8],
                    gaps=['p8 table + weights box read. Contd-block applicability inference flagged above.']))


def all_ids(doc):
    import sqlite3 as _sq
    with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
        return [r[0] for r in _db.execute('SELECT id FROM evidence WHERE document_id=? ORDER BY page, id', (doc,)).fetchall()]


def main():
    from chp.store import Store
    from chp.patches import validate, commit
    from chp.reviewed_ingestion import stage
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    plant = ROOT / 'data/plant'
    with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 730, before['version']
    out = BASE / ('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    pkg = body()
    pkg['intake_assessment']['reviewed_evidence_ids'] = all_ids(DOC)
    if args.apply:
        assert pkg == json.loads((BASE / 'rehearsal/package.json').read_text(encoding='utf8'))
        assert json.loads((BASE / 'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    else:
        if COPY.exists():
            shutil.rmtree(COPY)
        COPY.mkdir(parents=True)
        with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
            with sqlite3.connect(COPY / 'plant.sqlite3') as dst:
                db.backup(dst)
    (out / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf8')
    store = Store(plant if args.apply else COPY)
    assert store.version() == 730, store.version()
    report = validate(store, {k: pkg[k] for k in ('summary', 'operations')}, DOC, 730, visual_ids=[EV8])
    (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    assert not report['errors'], report
    staged = stage(store, DOC, pkg, visual_ids=[EV8], analysis_dir=str(out), expected_version=730)
    result = commit(store, staged['proposal_id'])
    (out / 'result.json').write_text(
        json.dumps({'ok': True, 'proposal_id': staged['proposal_id'], **result}, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'proposal': staged['proposal_id'], 'version': store.version()}))
    if args.apply:
        with sqlite3.connect(plant / 'plant.sqlite3') as db:
            db.row_factory = sqlite3.Row
            after = Store.__new__(Store).model(db=db)
        bf = {a['id']: {k: v for k, v in a.items() if k not in ('canonical_subject', 'canonical_object')} for a in before['assertions']}
        af = {a['id']: a for a in after['assertions']}
        assert not [k for k in bf if k not in af]
        assert not [k for k in bf if k in af and bf[k] != {kk: vv for kk, vv in af[k].items() if kk in bf[k]}]
        print(json.dumps({'applied': True, 'version': after['version']}))


if __name__ == '__main__':
    main()
