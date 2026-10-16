"""Pass-1 two-tier depth packages (DQ-B06-001, DQ-B07-001, DQ-B08-001), guarded at v718.

Builds two source-scoped proposal packages from the accepted top-model return
(output/plant-enrichment/pass-01-jetty/top-model-result.json), which was
independently verified against all seven crops before staging:
  A: doc_030c8f82fb674548a4dc (175012 conveyor-2 GA + TCS) — Q1 not_resolvable.
  B: doc_1518e219127b4b0eaa3a (175155 unloader GA) — Q2 rejected/corrected, Q3.
Default is isolated rehearsal; --apply performs the guarded live acceptance.
"""
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BASE = ROOT / 'output/plant-enrichment/pass-01-jetty'
BACKUP = BASE / 'backup-v718'
PKG_A = BASE / 'prop-030c'
PKG_B = BASE / 'prop-1518'
DOC_A = 'doc_030c8f82fb674548a4dc'
DOC_B = 'doc_1518e219127b4b0eaa3a'
BASE_VERSION = 718

EV_A = {'p2': 'ev_e681c2f0a7c64430b4c4', 'p3': 'ev_1d4877df9d48480786bb',
        'p4': 'ev_53c4d65595a340b5901a'}
EV_B = {'p9': 'ev_ec07cf044f9249c0a710', 'p10': 'ev_76b6c09bdcdf42e490ec',
        'p11': 'ev_10ccd8905bb545f2995c', 'p12': 'ev_5f3558b82149437aa676'}


def ev(eid, region):
    return dict(evidence_id=eid, quote='', region=region)


BASIS_A = ('175012 GA & LOAD DATA OF BELT CONVEYOR-2A/B, Rev 2 29.10.18, '
           'IS-1-GA-702-101-M012, STATUS FOR APPROVAL; TCS comments 24.10.2018 on Rev 1, '
           'approval stamp 23-Nov-2018 (non-absolving). Pass-1 two-tier review v718; '
           'design source only, not field/as-built.')
BASIS_B = ('175155 GA OF SHIP UNLOADER TYPE 1 & TYPE 2 (GA74042951), package approved '
           '14-Dec-2020; Type1 pp8-9, Type2 pp10-11, rope arrangement p12. Pass-1 two-tier '
           'review v718; design source only, not field/as-built.')


def all_evidence_ids(doc):
    import sqlite3 as _sq
    with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
        return [r[0] for r in _db.execute(
            'SELECT id FROM evidence WHERE document_id=? ORDER BY page, id', (doc,)).fetchall()]


def pkg_a():
    ops = []
    disc = ('Pass-1 two-tier verdict not_resolvable for take-up rope/sheave final selection. '
            'Alternatives: (A) Rev-2 GA schedule FOR APPROVAL: 20 dia rope 6x36 fabric core GR-1570, '
            'MBF 185kN, sheave dia 440mm CI GR-24, take-up travel 3700mm; (B) TCS Rev-1 comment '
            '24.10.2018: minimum 231kN per BS2573 FOS, 20mm inadequate, BHEL reply "We have revised BOM" '
            'with no value; (C) reviewer comment and BHEL reply both state sheave not required/not '
            'applicable, while the Rev-2 schedule still prints a 440mm sheave. The existing '
            'takeup_rope_specification fact reads as-printed only, not a final selection. '
            'Deciding record, in order: later approved GA revision (Rev 3+) of IS-1-GA-702-101-M012; '
            'BHEL take-up rope calculation with acceptance; the revised BOM from the TCS reply. '
            'Transmittal FICH/MSTPP/TRM/055933 (24.10.18) link to the TCS comments not established.')
    sup = [ev(EV_A['p2'], [0.855, 0.6645, 0.955, 0.6815]),
           ev(EV_A['p2'], [0.789, 0.6515, 0.956, 0.6825]),
           ev(EV_A['p2'], [0.812, 0.803, 0.958, 0.955]),
           ev(EV_A['p3'], [0.289, 0.768, 0.775, 0.893]),
           ev(EV_A['p3'], [0.78, 0.768, 0.957, 0.893]),
           ev(EV_A['p3'], [0.008, 0.005, 0.155, 0.07]),
           ev(EV_A['p4'], [0.289, 0.093, 0.775, 0.165]),
           ev(EV_A['p4'], [0.78, 0.093, 0.957, 0.165])]
    for subj, lane in [('ent_91dd763af7f4417ebaa6', 'EAC-2A'), ('ent_f4dc6c5b38d14bceb5e5', 'EAC-2B')]:
        ops.append(dict(op='assert', subject=subj, predicate='source_discrepancy', value=disc,
                        context=dict(kind='specification', basis=BASIS_A + ' Applicability: %s only; '
                                     'GA sheet is combined EAC-2A/2B with no lane-specific rope/sheave '
                                     'difference; do not copy to any other conveyor.' % lane),
                        origin='explicit', confidence=0.9, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9,
                    evidence=[ev(EV_A['p2'], [0.812, 0.803, 0.958, 0.955]),
                              ev(EV_A['p3'], [0.289, 0.768, 0.775, 0.893])],
                    text=('Pass-1 Q1 closed as not_resolvable (DQ-B06-001 selection part). Open need: '
                          'later approved GA revision / rope calculation / revised BOM as above. '
                          'No final rope/sheave selection asserted for either lane.')))
    return dict(summary='Pass-1 Q1: EAC-2A/2B take-up rope/sheave final-selection not_resolvable with deciding record (doc_030c8f82fb674548a4dc)',
                operations=ops,
                intake_assessment=dict(
                    route='mixed',
                    purpose='Record the Pass-1 rope/sheave conflict resolution without inventing a final selection',
                    questions=['Which rope/sheave selection can be asserted as final for EAC-2A/2B?'],
                    reviewed_evidence_ids=all_evidence_ids(DOC_A),
                    gaps=['GA schedule p2, TCS comment p3 and BHEL reply p4 regions above examined at Pass-1; '
                          'GA pp1-2 and TCS pp3-5 reviewed across Tier-1 (B06) and Pass-1. '
                          'Drive internals, numeric protection settings '
                          'and idler/BOM rows live in vendor/calculation sources, not this GA; not re-extracted here.']))


def pkg_b():
    ops = []
    vis = ('Visibly supported at label/existence level only (Type 1, SUL-1 & SUL-2 jointly per sheet '
           'title; not copied to SUL-3). p9: hydraulic buffer at long-travel rail end (Over Buffer dim '
           '28760); storm tie-down stowage pin and storm tie-down hydraulic rail clamp; power and fiber '
           'optic reel (existence only); vibro-feeder platform (Section F-F); shuttle travel 4000; '
           '"Plain Water Dust Suppression System" label in Section E-E (scope undecided). p12 (shared '
           'Type1+Type2 sheet): rope-arrangement schematic only — grab hoisting (holding/closing '
           'ropes+drums, main/roller-girder/auxiliary-trolley sheaves), boom luffing (pylon-head/equaliser '
           'sheaves, equaliser arrangement, luffing drum), trolley traverse (boom-end water/land sheaves, '
           'traverse drum, compensating rope take-up sheave). A hydraulic buffer is a mechanical end-stop, '
           'not an anti-collision system. p9 title block reads REV 8 while its revision table lists rev 9 '
           '(05.10.20); p10-p12 read REV 9 — sheet revision consistency to confirm from the original.')
    ops.append(dict(op='assert', subject='ent_1a57e15407c145a19284', predicate='assembly_arrangement',
                    value=vis,
                    context=dict(kind='specification', basis=BASIS_B + ' Type-1 SUL-1&SUL-2 joint '
                                 'applicability; p12 items support type-level rope-system arrangement, not a '
                                 'SUL1-specific rating. 600mm LT / 400mm trolley buffer and 1x210kN clamp values '
                                 'on p10 are SUL-3 only.'),
                    origin='explicit', confidence=0.85,
                    evidence=[ev(EV_B['p9'], [0.664, 0.57, 0.708, 0.579]),
                              ev(EV_B['p9'], [0.767, 0.585, 0.838, 0.592]),
                              ev(EV_B['p9'], [0.774, 0.623, 0.806, 0.648]),
                              ev(EV_B['p9'], [0.84, 0.623, 0.87, 0.655]),
                              ev(EV_B['p9'], [0.694, 0.478, 0.743, 0.497]),
                              ev(EV_B['p9'], [0.189, 0.225, 0.253, 0.232]),
                              ev(EV_B['p9'], [0.52, 0.7, 0.58, 0.742]),
                              ev(EV_B['p12'], [0.157, 0.75, 0.302, 0.762]),
                              ev(EV_B['p12'], [0.728, 0.319, 0.793, 0.328]),
                              ev(EV_B['p12'], [0.864, 0.236, 0.94, 0.258]),
                              ev(EV_B['p12'], [0.44, 0.209, 0.499, 0.314])]))
    ops.append(dict(op='assert', subject='ent_1a57e15407c145a19284', predicate='source_gap',
                    value=('SUL1 tentative feeder/cable-reel ratings REJECTED on supplied crops: p9 is sheet 2 '
                           'of 5 (sections/View A) with no technical-data table, so no rating or Tentative tag '
                           'is visible for SUL1/SUL2. The 1700/1870t/h 1x22kW VVVF and 1x7kW figures appear only '
                           'on the Type-2 SUL-3 table (p10), where only the cable reeling drum is tagged '
                           'Tentative (type "Mono spairal"); the SUL-3 vibro-feeder row is untagged. Nothing '
                           'copied from Type 2 to Type 1. Need: Type-1 sheet 1 of 5 technical-data table page '
                           '(p8 of this document) showing the SUL-1/SUL-2 vibro-feeder and cable-reel rows.'),
                    context=dict(kind='specification', basis=BASIS_B + ' SUL1 (Type 1) only.'),
                    origin='explicit', confidence=0.9,
                    evidence=[ev(EV_B['p9'], [0.565, 0.938, 0.665, 0.97]),
                              ev(EV_B['p9'], [0.62, 0.903, 0.99, 0.93]),
                              ev(EV_B['p10'], [0.806, 0.4175, 0.986, 0.4475]),
                              ev(EV_B['p10'], [0.717, 0.1155, 0.784, 0.1217])]))
    ops.append(dict(op='assert', subject='ent_9b33c14cee7f4d749335', predicate='source_discrepancy',
                    value=('SUL-3 dust suppression scope NOT RESOLVABLE, readings preserved unmerged. (A) p10 '
                           'Type-2 table: Type Dry fog, water min 3bar, jetty outlets every 30m by manual hose '
                           'reel. (B) p11 Section E-E label: "Plain Water Dust Suppression System" (8500 pulley '
                           'centres beneath). DSS NOZZLES labels assert existence only. Whether these are '
                           'different sub-systems is unstated and not inferred; the same plain-water label on '
                           'the Type-1 E-E weakens but does not remove reading B. Deciding record: SUL-3 DSS '
                           'datasheet/P&ID/equipment list, or MAITREE-00-BR-DA-175169-ISG-TENOVA bulk transfer '
                           'arrangement.'),
                    context=dict(kind='specification', basis=BASIS_B + ' SUL-3 / Type 2 only; do not copy to '
                                 'SUL-1/SUL-2.'),
                    origin='explicit', confidence=0.9,
                    evidence=[ev(EV_B['p10'], [0.806, 0.5845, 0.986, 0.6185]),
                              ev(EV_B['p11'], [0.505, 0.782, 0.575, 0.808]),
                              ev(EV_B['p11'], [0.5026, 0.5257, 0.5465, 0.5346]),
                              ev(EV_B['p9'], [0.506, 0.782, 0.575, 0.808])]))
    ops.append(dict(op='assert', subject='ent_9b33c14cee7f4d749335', predicate='source_discrepancy',
                    value=('SUL-3 limestone grab weight NOT RESOLVABLE: 15.1t (technical-data table, Grab bucket '
                           'self weight, Limestone column) vs 15t (WEIGHTS (SUL-3) box, "Lime Stone Grab"). Coal '
                           'grab consistent at 17.5t both places; unloader without grab 983t; limestone capacity '
                           '13m3 (coal 33m3). p11 grab details carry dimensions only. 15t may be a rounding of '
                           '15.1t but no source says so. Deciding record: MAITREE-00-EAA-DA-175161-ISG-TENOVA GA '
                           'of grab with technical data for coal and lime.'),
                    context=dict(kind='specification', basis=BASIS_B + ' SUL-3 limestone grab only.'),
                    origin='explicit', confidence=0.92,
                    evidence=[ev(EV_B['p10'], [0.94, 0.1615, 0.986, 0.1672]),
                              ev(EV_B['p10'], [0.64, 0.2045, 0.776, 0.2135]),
                              ev(EV_B['p10'], [0.64, 0.1895, 0.776, 0.2045]),
                              ev(EV_B['p11'], [0.2, 0.82, 0.31, 0.955])]))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9,
                    evidence=[ev(EV_B['p9'], [0.62, 0.903, 0.99, 0.93])],
                    text=('Pass-1 Q2/Q3 needs register (DQ-B07-001/DQ-B08-001): (1) Type-1 sheet 1-of-5 '
                          'technical-data page for SUL1/SUL2 tentative ratings; (2) SUL-3 DSS record or '
                          '175169 bulk transfer arrangement; (3) 175161 grab GA for limestone weight. '
                          'Deferred until supplied: anti-collision/limit/overload/brake internals, rope dia/MBF, '
                          'buffer/clamp capacities for Type 1, numeric protection settings, PLC logic, vendor '
                          'drivetrain internals. p9 sheet revision inconsistency recorded (title REV 8 vs '
                          'rev-9 table row 05.10.20).')))
    return dict(summary='Pass-1 Q2/Q3: SUL1 visible provisions, SUL1 tentative-rating gap, SUL3 dust and grab-weight discrepancies (doc_1518e219127b4b0eaa3a)',
                operations=ops,
                intake_assessment=dict(
                    route='mixed',
                    purpose='Record Pass-1 unloader resolutions without copying Type-2 values onto Type-1 machines',
                    questions=['What tentative ratings and protections are supported for SUL1?',
                               'Dry-fog vs plain-water and 15 vs 15.1t grab for SUL3?'],
                    reviewed_evidence_ids=all_evidence_ids(DOC_B),
                    gaps=['Type-1 pp8-9, Type-2 pp10-11 and rope p12 regions above examined at Pass-1; '
                          'Tier-1 reviewed pp1-7 (B07). '
                          'Cycle-calculation pp13-29 stay qualified design facts, not re-extracted. '
                          'Vendor brake/limit/anti-collision internals live outside this GA; deferred with needs.']))


PACKAGES = [(PKG_A, DOC_A, pkg_a, [EV_A['p2'], EV_A['p3'], EV_A['p4']]),
            (PKG_B, DOC_B, pkg_b, [EV_B['p9'], EV_B['p10'], EV_B['p11'], EV_B['p12']])]


def main():
    from chp.store import Store
    from chp.patches import validate
    from chp.reviewed_ingestion import stage
    from chp.patches import commit
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    plant = ROOT / 'data/plant'
    with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == BASE_VERSION, 'Live model moved; refresh review.'
    if not args.apply:
        BACKUP.mkdir(parents=True, exist_ok=True)
        if not (BACKUP / 'plant.sqlite3').exists():
            with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
                with sqlite3.connect(BACKUP / 'plant.sqlite3') as dst:
                    db.backup(dst)
    results = []
    running = BASE_VERSION
    for pkgdir, doc, builder, visual in PACKAGES:
        out = pkgdir / ('accepted' if args.apply else 'rehearsal')
        out.mkdir(parents=True, exist_ok=True)
        body = builder()
        if args.apply:
            assert body == json.loads((pkgdir / 'rehearsal/package.json').read_text(encoding='utf8'))
            assert json.loads((pkgdir / 'rehearsal/result.json').read_text(encoding='utf8'))['ok']
        (out / 'package.json').write_text(json.dumps(body, indent=2) + '\n', encoding='utf8')
        store = Store(plant if args.apply else BACKUP)
        assert store.version() == running, (store.version(), running)
        report = validate(store, {k: body[k] for k in ('summary', 'operations')}, doc, running,
                          visual_ids=visual)
        (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
        assert not report['errors'], report
        staged = stage(store, doc, body, visual_ids=visual, analysis_dir=str(out),
                       expected_version=running)
        result = commit(store, staged['proposal_id'])
        (out / 'result.json').write_text(
            json.dumps({'ok': True, 'proposal_id': staged['proposal_id'], **result}, indent=2) + '\n',
            encoding='utf8')
        running = store.version()
        results.append((doc, staged['proposal_id'], result))
        print(json.dumps({'doc': doc, 'proposal': staged['proposal_id'], 'ok': True,
                          'version': running}))
    if args.apply:
        with sqlite3.connect(plant / 'plant.sqlite3') as db:
            db.row_factory = sqlite3.Row
            after = Store.__new__(Store).model(db=db)
        before_facts = {a['id']: {k: v for k, v in a.items() if k not in ('canonical_subject', 'canonical_object')}
                        for a in before['assertions']}
        after_facts = {a['id']: a for a in after['assertions']}
        for aid, old in before_facts.items():
            assert old == {k: v for k, v in after_facts[aid].items() if k in old}, aid
        print(json.dumps({'applied': True, 'version': after['version']}))


if __name__ == '__main__':
    main()
