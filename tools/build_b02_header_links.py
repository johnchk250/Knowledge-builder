"""B02 Pass-A last Tier-1 item: connect the common DFDS station outlet headers to the TP1 and TP13 (via UEE-3) local
header entities. Stage 'a' = source 175089 P&ID (baseline 628); stage 'b' = corroborating local TP1 plan 175286
(baseline 629). Build writes package.json + baseline-model.json; accept with tools/accept_b02_scoped.py."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from tools.implement_b00_corrections import save, support

BASE = ROOT / 'output/plant-enrichment/B02'
D175089 = 'doc_bca09d68af9b43e3b633'
D175286 = 'doc_7568f1550b254ee2a94a'

AIR1, WATER1 = 'ent_c870015a2dd64f3aa6fb', 'ent_932c068ee9a14dde93d9'      # DFDS-1 common outlet mains
AIR2, WATER2 = 'ent_744537b8c45f406e9fc1', 'ent_78bccd9a79e448cfaebd'      # DFDS-2 common outlet mains
TP1_AIR, TP1_WATER = 'ent_21a02d1f40f04686a18a', 'ent_3e6f0c75149b49cdbce2'
UEE3_LOCAL = 'ent_864774d050ca4a308f0e'                                    # existing -> UEF-13 inlet since v577
LIVE_EXPECT = {AIR1: 'DFDS-1 Common air main at receiver outlet', WATER1: 'DFDS-1 Common water main at station outlet',
               AIR2: 'DFDS-2 Common air main at receiver outlet', WATER2: 'DFDS-2 Common water main at station outlet',
               TP1_AIR: 'UEF-1 DFDS air main', TP1_WATER: 'UEF-1 DFDS water main',
               UEE3_LOCAL: 'UEE-3 Local DFDS Air and water connection'}

# Evidence IDs are page anchors inside the named document; regions are fractions of the original page.
EV = {(D175089, 1): 'ev_08ec0122d044468d8975', (D175089, 2): 'ev_d705803b38ce46ccb5fa',
      (D175286, 1): 'ev_17a7e1b7dfa84cd783cd', (D175286, 2): 'ev_05c0654378d14887b3ac',
      (D175286, 3): 'ev_ec67d44b73af4e96b64c'}
BASIS_P = ('Original 175089 Rev1 P&ID (BTL EPC/BHEL ISG, approved 14-Dec-2018, FIO), PDF p{p}: arrows, line sizes and '
           'reducer symbols visually traced on the enlarged original. Design arrangement, not live valve state, complete '
           'isolation or as-built verification. ')


def sup(doc, page, *regions):
    return {'origin': 'explicit', 'confidence': .96,
            'evidence': [{'evidence_id': EV[(doc, page)], 'quote': '', 'region': r} for r in regions]}


def conn(subject, obj, condition, basis, proof):
    return {'op': 'assert', 'subject': subject, 'predicate': 'utility_supply_to', 'object_entity': obj,
            'context': {'kind': 'connection', 'network': 'utility', 'verification': 'documented',
                        'condition': condition, 'basis': basis}, **proof}


def spec(subject, predicate, value, basis, proof):
    return {'op': 'assert', 'subject': subject, 'predicate': predicate, 'value': value,
            'context': {'kind': 'specification', 'basis': basis}, **proof}


def stage_a():
    ops = []
    s1 = sup(D175089, 1, [.23, .07, .40, .30])
    b1 = BASIS_P.format(p=1)
    ops.append(conn(AIR1, TP1_AIR,
                    'Air only. 80NB(A) common main rises to junction E, where a reducing branch (40NB(A)) runs to UEF-1 and '
                    'feeds the UEF-1 header (20NB(A) local branches). The 80NB(A) main also continues east toward UEE-1; that '
                    'continuation, its tees and any intermediate isolation are not modelled by this link.',
                    b1 + 'Junction E to UEF-1 local air header; air and water are separate lines, crossings are not cross-connections.', s1))
    ops.append(conn(WATER1, TP1_WATER,
                    'Water only. 32NB(W) common main rises to junction E, where a reducing branch (15NB(W)) runs to UEF-1 and '
                    'feeds the UEF-1 local water header. The 32NB(W) main also continues east toward UEE-1; that continuation '
                    'is not modelled by this link.',
                    b1 + 'Junction E to UEF-1 local water header; separate from the air line.', s1))
    s2a = [.595, .115, .66, .30]
    s2b = [.598, .27, .745, .56]
    p2 = sup(D175089, 2, s2a, s2b)
    b2 = BASIS_P.format(p=2)
    ops.append(conn(AIR2, UEE3_LOCAL,
                    'Air only. 100NB(A) common main leaves BV-03 to junction E and runs past the UEE-2 header (UEE-2 branches tee '
                    'off it; their upstream main is not modelled here). Near the south end of UEE-2 a branch reduces to 50NB(A) '
                    'and enters the UEE-3 loop; the 100NB(A) main also continues west toward UEF-12/11/10/9/8 (not modelled).',
                    b2 + 'Common main to UEE-3 local air main, which already continues to the UEF-13 inlet (v577).', p2))
    ops.append(conn(WATER2, UEE3_LOCAL,
                    'Water only. 32NB(W) common main runs to junction E and past the UEE-2 header; near the south end of UEE-2 a '
                    'branch reduces to 15NB(W) and enters the UEE-3 loop. The 32NB(W) main also continues west toward '
                    'UEF-12/11/10/9/8 (not modelled).',
                    b2 + 'Common main to UEE-3 local water main, which already continues to the UEF-13 inlet (v577).', p2))
    return D175089, 628, ops, [EV[(D175089, 1)], EV[(D175089, 2)]], {
        'summary': 'B02: connect DFDS-1/2 common air and water station mains to the TP1 local mains and, via UEE-3, to the TP13 inlet',
        'questions': ['Where do the common air/water outlet mains continue after the station boundary?',
                      'Which local header entities receive them, and with which size reductions?'],
        'gaps': ['Only the TP1 (UEF-1) and UEE-3 -> UEF-13 branches are connected; trunk continuations to UEE-1, UEE-2 and the UEF-2..12 headers are recorded in the depth queue.',
                 'No valve state, isolation boundary or pipe length is asserted; junction E is a drawing callout, not a component.']}


def stage_b():
    basis = ('Original 175286 Rev1 piping layout for DFDS, SW & PW at UEF-1 (FIO, 12-Sep-2019), {where}. Local plan corroborating '
             'the System-1 P&ID feeder; design drawing, not as-built verification. ')
    s1 = sup(D175286, 1, [.495, .455, .56, .60])
    s2 = sup(D175286, 2, [.705, .28, .75, .325])
    p1 = s1['evidence'] + s2['evidence']
    proof = {'origin': 'explicit', 'confidence': .96, 'evidence': p1}
    ops = [
        spec(TP1_AIR, 'assembly_arrangement',
             'Enters TP1 as a 40NB(A) feeder labelled "PIPE FROM UEE-1" in a bundle with separate 15NB(W) DFDS water, 125NB(SW) '
             'service-water and 32NB(PW) potable-water lines; inside the building it continues as 20NB(A) local branches to the '
             'FAS/PRU units. The label gives the route origin of the pipe bundle, not an equipment boundary at UEE-1.',
             basis.format(where='PDF pp1-2 plan and section callouts'), proof),
        spec(TP1_WATER, 'assembly_arrangement',
             'Enters TP1 as a 15NB(W) feeder labelled "PIPE FROM UEE-1" in a bundle with separate 40NB(A) DFDS air, 125NB(SW) '
             'service-water and 32NB(PW) potable-water lines; inside the building it continues as 15NB(W) local branches to the '
             'FAS/PRU units. SW/PW are other services and are not part of this DFDS water main.',
             basis.format(where='PDF pp1-2 plan and section callouts'), proof),
    ]
    return D175286, 629, ops, [EV[(D175286, 1)], EV[(D175286, 2)], EV[(D175286, 3)]], {
        'summary': 'B02: corroborate TP1 DFDS air/water feeder sizes and route origin from the local 175286 plan',
        'questions': ['Does the local TP1 plan agree with the System-1 P&ID feeder sizes and route origin?'],
        'gaps': ['175286 shows the bundle origin as UEE-1 route; the junction E tee on 175089 is not drawn here, so no second connection edge is asserted.']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['a', 'b'])
    args = ap.parse_args()
    doc, baseline, ops, visual, intake = stage_a() if args.stage == 'a' else stage_b()
    out = BASE / ('headers-175089' if args.stage == 'a' else 'headers-175286')
    plant = ROOT / 'data/plant'
    with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        model = Store.__new__(Store).model(db=db)
        docrow = db.execute('SELECT sha256 FROM documents WHERE id=?', (doc,)).fetchone()
        known = {r[0] for r in db.execute('SELECT id FROM evidence WHERE document_id=?', (doc,))}
    assert model['version'] == baseline, (model['version'], baseline)
    assert hashlib.sha256((plant / 'originals' / docrow['sha256']).read_bytes()).hexdigest() == docrow['sha256']
    assert set(visual) <= known and all(e['evidence_id'] in known for o in ops for e in o['evidence'])
    labels = {e['id']: e['label'] for e in model['entities']}
    for k, v in LIVE_EXPECT.items():
        assert labels[k] == v, (k, labels.get(k))
    live = {(a['canonical_subject'], a['canonical_object']) for a in model['assertions']
            if a['predicate'] == 'utility_supply_to' and not a.get('retirement')}
    for o in ops:
        if o['predicate'] == 'utility_supply_to':
            assert (o['subject'], o['object_entity']) not in live, 'edge already exists'
    save(out / 'baseline-model.json', model)
    save(out / 'package.json', {
        'document_id': doc, 'baseline_version': baseline,
        'baseline_model': str((out / 'baseline-model.json').relative_to(ROOT)).replace('\\', '/'),
        'expected_new_components': 0, 'visual_ids': visual,
        'body': {'summary': intake['summary'], 'operations': ops,
                 'intake_assessment': {'route': 'mixed', 'purpose': intake['summary'], 'questions': intake['questions'],
                                       'reviewed_evidence_ids': sorted(known), 'gaps': intake['gaps']}}})
    print(json.dumps({'stage': args.stage, 'baseline': baseline, 'assertions': len(ops), 'out': str(out)}))


if __name__ == '__main__':
    main()
