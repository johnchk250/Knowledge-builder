"""Pass-1 SUL3 Type-2 drive rows (DQ-B08-001 remainder), guarded at v729.

One source (doc_1518e219127b4b0eaa3a p10, read locally in full-page render).
Default: isolated rehearsal; --apply performs guarded live acceptance.
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-01-sul3'
COPY = BASE / 'rehearsal-copy'
DOC = 'doc_1518e219127b4b0eaa3a'
SUL3 = 'ent_9b33c14cee7f4d749335'
EV10 = 'ev_76b6c09bdcdf42e490ec'


def body():
    val = ('SUL-3 Type-2 drive rows as printed on the p10 technical table (REV 9, approved 14-Dec-2020). Grab '
           'hoisting/closing: full-grab 110m/min, lower/empty 150m/min, motors 2x630kW, VVVF control. Power supply '
           '3.3kV 3ph 50Hz AC. Diesel generator set for emergency slow-speed operation of specified functions. Site '
           'wind: operation 16m/s, positioning 18m/s, out of operation 73m/s; ambient 45C; seismic 0.12g Zone 1 '
           'BNBC-2012. Unloader without grab 983t; coal grab 17.5t consistent in table and weights box. Matches DBR '
           'duty/wind basis; T9-L4-M8-class mechanisms per DBR (not re-asserted here). Traverse/boom-hoist/long-'
           'travel/shuttle motor kW cells are not legibly transcribed from this render; not asserted.')
    ops = [dict(op='assert', subject=SUL3, predicate='assembly_arrangement', value=val,
                context=dict(kind='specification', basis='175155 Type-2 SUL-3 technical table p10, REV 9; design '
                             'only, not field verification.'),
                origin='explicit', confidence=0.9,
                evidence=[dict(evidence_id=EV10, quote='', region=[0.80, 0.10, 0.99, 0.68])]),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=[dict(evidence_id=EV10, quote='', region=[0.80, 0.10, 0.99, 0.68])],
                text=('SUL-3 traverse/boom/long-travel/shuttle motor kW cells need a legible table crop; limestone '
                      'grab weight stays with the Q3 gap (175161 grab GA).'))]
    return dict(summary='SUL-3 Type-2 hold/close drive, power, wind/site rows (175155 p10)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record SUL-3 drive rows readable on the Type-2 table',
                    questions=['What hold/close drive and site basis does the SUL-3 table state?'],
                    reviewed_evidence_ids=[EV10],
                    gaps=['p10 table visually reviewed in full-page render. Small motor-kW cells illegible; gap above.']))


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
        assert before['version'] == 729, before['version']
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
    assert store.version() == 729, store.version()
    visual = [EV10]
    report = validate(store, {k: pkg[k] for k in ('summary', 'operations')}, DOC, 729, visual_ids=visual)
    (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    assert not report['errors'], report
    staged = stage(store, DOC, pkg, visual_ids=visual, analysis_dir=str(out), expected_version=729)
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
