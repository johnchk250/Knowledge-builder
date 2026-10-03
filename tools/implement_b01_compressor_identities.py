"""One-time reviewed B01 compressor/group identity packages from v602."""
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

BASE = ROOT / 'output/plant-enrichment/B01/compressor-identities'
REDIRECTS = {'ent_6bd80fed0d2046c180f7': 'ent_081c34835a684544a6d0',
             'ent_9e56a4eb9d9246e8be73': 'ent_2fc625b1e93743ae9e7f'}
PUMPS = ['ent_975edb9acc07451cbc62', 'ent_8a35251f220d4c9287d2']


def packages(snap):
    def fact(subject, predicate, value, eid, region, basis, relation=False):
        return {'op': 'assert', 'subject': subject, 'predicate': predicate,
                'object_entity' if relation else 'value': value,
                'context': {'kind': 'classification' if predicate == 'instance_of' else 'specification',
                            'basis': basis}, **support(eid, region)}

    def group(group_id, ids, eid, region, description):
        basis = 'Source schedule/datasheet represents two separately tagged units. Historical aggregate facts remain retired.'
        ops = [fact(group_id, 'instance_of', 'equipment_design_reference', eid, region, basis),
               fact(group_id, 'design_applicability', description, eid, region, basis)]
        for target in ids:
            op = fact(group_id, 'design_detail_applies_to', target, eid, region, basis, True)
            op['origin'] = 'inferred'
            ops.append(op)
        return ops

    def package(doc, title, ops, visual, scope):
        return {'doc': doc, 'visual': visual, 'body': {'summary': title, 'operations': ops,
                'intake_assessment': {'route': 'mixed', 'purpose': title,
                'questions': ['Which numbered equipment identities and source-group applicability are established?'],
                'reviewed_evidence_ids': [e['id'] for e in snap['evidence'] if e['document_id'] == doc],
                'gaps': [scope, 'Inventory coverage is distinct from visual semantic review. '
                         'B02 owns detailed compressor assemblies/control; no field identity, final motor or commissioned setting is established.']}}}

    eid = 'ev_c8ee5ec77a4a44c7abe5'
    ops = group('ent_7f3828521dea4b288092', PUMPS, eid, [.15,.29,.94,.405],
                'DBR175090 Rev1 System-1 schedule names DFDSP-1A/1B, quantity 2 (1 working + 1 standby). '
                'This grouped source reference applies to the two canonical individual pumps; it is not a third pump.')
    ops += group('ent_691147aababe4752a7b0', list(REDIRECTS), eid, [.15,.415,.94,.655],
                 'DBR175090 Rev1 System-1 schedule names SC-1A/1B, quantity 2 (1 working + 1 standby), '
                 '815 CFM and tentative 132 kW/4-pole motors. This is the grouped design reference for '
                 'the two individual compressors, not an additional machine. The document-number alias is a source reference, not an equipment tag.')
    result = [package('doc_456cfee5f9824d68b651', 'B01: classify retired DFDS aggregate records as design references',
                      ops, [eid], 'All 21 evidence blocks inventoried. Original pp1-4,8,10,15-16 visually reviewed '
                      'for revision, numbered schedules, system applicability and annex context; other calculations remain B02.')]

    eid = 'ev_9c603ad0326b4f2d9605'
    ops = []
    for lane, (old, new) in zip('AB', REDIRECTS.items()):
        prov = support(eid, [.14,.13,.9,.80])
        prov['origin'] = 'inferred'
        ops.append({'op': 'merge', 'source': old, 'target': new,
                    'reason': f'DFDS philosophy175265 Rev2 p2 explicitly cross-references DBR M090 and P&ID M089, '
                    f'identifies System-1 at House-1 near jetty and names its sole two 1W+1S compressors DFDSC-1A/1B. '
                    f'Cross-checked original DBR175090 pp2/4 names that same numbered pair SC-1A/1B in the same '
                    f'System-1/house/consumer scope. Thus SC-1{lane} and DFDSC-1{lane} identify the same design unit. '
                    'This does not match stockpile sequential-controller SC tags or resolve vendor motor ratings.', **prov})
        ops.append(fact(new, 'design_applicability',
                        f'DFDSC-1{lane} in philosophy175265 Rev2 and SC-1{lane} in its explicitly referenced '
                        'DBR175090 are the same System-1 compressor at House-1 near jetty. The documents identify '
                        'one pair, 1 working + 1 standby, supplying air through a receiver to FAS/PRU. '
                        'SC here denotes a screw compressor; stockpile sequential-controller SC numbering is a separate namespace.',
                        eid, [.14,.23,.9,.80], 'Cross-document identity inference from explicit references, numbered system, location and pair count.'))
        ops[-1]['origin'] = 'inferred'
    result.append(package('doc_294aacf286d246769e32', 'B01: reconcile SC-1A/B and DFDSC-1A/B in their proven system namespace',
                          ops, [eid], 'All 32 page evidence blocks inventoried; original pp1-5 and18 visually reviewed. '
                          'DBR pp2/4/8/10 and P&ID house regions corroborate system scope; detailed local control pages remain B02/consuming batches.'))

    eid = 'ev_593f764437c7464fba4c'
    result.append(package('doc_b5188c19e5b942cfa976', 'B01: retain grouped KSB pump data as an applicable vendor design reference',
        group('ent_bb130947657e41158cab', PUMPS, eid, [.07,.165,.955,.456],
              'Vendor175093 Rev4 p2 is one datasheet for the DFDS-1A/1B pair, equivalent to canonical DFDSP-1A/1B '
              'as proven by House-1 GA175050. This KSB Movitec group is a vendor design reference, not a third installed pump. '
              'Earlier DBR and later vendor duty bases remain separately qualified.'), [eid],
        'All nine original vendor pages visually reviewed in the prior pump milestone. Reuses accepted house identity bridge; dense BOM remains B02.'))

    ops = []
    for system, eid, model, capacity, old_kw, page in [
        ('ent_2024dfa4a4084a86b0b5','ev_50320e99cdab406aaad5','ZT160',815,132,3),
        ('ent_b2f48e8d116f484882a1','ev_873387f6ada444c5a1ae','ZT132',680,110,10)]:
        op = fact(system, 'source_discrepancy',
                  f'Compressor vendor175103 Rev2 p{page} lists Atlas Copco {model}, quantity2, {capacity} CFM '
                  f'at 1bar/45C and a 160kW motor row; the earlier matching-capacity DBR schedule lists tentative {old_kw}kW. '
                  'Keep these source bases distinct. Vendor load7bar(g)/unload7.5bar(g) are design values. '
                  'The model designation does not establish motor kW. Review reply p36 refers final motor details '
                  'to separate electrical drawing180055-ISG0; vendor-sheet capacity correspondence does not prove installed A/B motor identity.',
                  eid, [.14,.067,.875,.53], 'System-level vendor/design comparison, inferred by scheduled capacity. '
                  'No individual compressor model or final motor rating assigned by this package.')
        op['origin'] = 'inferred'
        op['evidence'].append({'evidence_id':'ev_63a6a1e8665a440ab13a','quote':'','region':[.12,.31,.975,.446]})
        ops.append(op)
    result.append(package('doc_d91e9eef8a40479687cd', 'B01: preserve compressor vendor applicability and motor-rating uncertainty',
                          ops, ['ev_50320e99cdab406aaad5','ev_873387f6ada444c5a1ae','ev_63a6a1e8665a440ab13a'],
                          'All 36 pages and their evidence blocks inventoried; original pp1-3,10,35-36 visually reviewed. '
                          'GA, internal P&ID, electrical and controller detail remains available B02 work. Final motor reference180055 needs retrieval.'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snap = json.loads((ROOT/'output/plant-enrichment/B01/accepted-v602.json').read_text(encoding='utf-8'))
    pkgs = packages(snap)
    plant = ROOT/'data/plant'
    out = BASE/('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'result.json').exists(), 'Already complete; inspect checkpoint.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 602 and before == snap['model'], 'Live state changed; review again.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v602'
            backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3', backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:
                    db.backup(dst)
            copied = []
            for d in snap['documents']:
                if d['id'] not in [p['doc'] for p in pkgs]:
                    continue
                assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest() == d['sha256']
                for rel in set([Path('originals')/d['sha256']] + [Path('renders')/e['image'] for e in snap['evidence'] if e['document_id'] == d['id'] and e['image']]):
                    dest = backup/rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(plant/rel, dest)
                    copied.append(str(rel))
            save(backup/'manifest.json', {'version':602, 'copied_files':copied,
                 'scope':'Consistent full SQLite database and package originals/renders; unrelated sources remain immutable in data/plant.'})
    if args.apply:
        assert pkgs == json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json', pkgs)
    store = Store(plant if args.apply else out)
    logs = []
    for i, p in enumerate(pkgs):
        body = p['body']
        v = 602+i
        report = validate(store, {k:body[k] for k in ['summary','operations']}, p['doc'], v, visual_ids=p['visual'])
        assert not report['errors'], report
        staged = stage(store, p['doc'], body, visual_ids=p['visual'], analysis_dir=str(out), expected_version=v)
        result = commit(store, staged['proposal_id'])
        logs.append({'proposal_id':staged['proposal_id'], 'document_id':p['doc'], 'warnings':report['warnings'], **result})
        save(out/'commit-log.json', logs)
    after = store.model()
    save(out/'model.json', after)
    assert after['version'] == 606
    facts = {a['id']:a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a) == preserved(facts[a['id']]), a['id']
        for field in ['canonical_subject','canonical_object']:
            assert facts[a['id']][field] == REDIRECTS.get(a[field], a[field])
    assert before['aliases'] == after['aliases'] and len(before['entities']) == len(after['entities'])
    assert len(after['merges']) == len(before['merges'])+2
    assert before['conflicts'] == after['conflicts']
    added = [a for a in after['assertions'] if a['created_version'] > 602]
    assert len(added) == 16
    save(out/'result.json', {'ok':True, 'version':606, 'proposals':[x['proposal_id'] for x in logs],
         'redirects':REDIRECTS, 'added_claims':added, 'preserved_assertions':len(before['assertions'])})
    print(json.dumps({'ok':True, 'version':606, 'mode':out.name, 'proposals':[x['proposal_id'] for x in logs]}))


if __name__ == '__main__':
    main()
