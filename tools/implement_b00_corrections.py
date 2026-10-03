"""Reviewed B00 corrections from v593. Rehearse first; never replay on later state."""
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import commit, validate

BASE = ROOT / 'output/plant-enrichment/B00'
CONTROL = 'doc_4f2cd96c3b1e413ea4b5'
TPDOC = 'doc_71a0d8fc66304e93b9c1'
FLOW = 'ev_0b5f0558fa714697879e'
TP = 'ent_108b99f6c64844df8cf8'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def support(eid, region):
    return {'origin': 'explicit', 'confidence': .98,
            'evidence': [{'evidence_id': eid, 'quote': '', 'region': region}]}


def proposals(snapshot):
    model = snapshot['model']
    names = {e['id']: e['label'] for e in model['entities']}
    facts = {f['id']: f for f in model['assertions']}
    legend = support(FLOW, [.054, .869, .243, .903])
    ops = []
    for entity, alias, fact, number in [
        ('ent_bdf8e7e7f7f8485b80fe', 'alias_d5ee77e8e3e5448f8f5d', 'fact_e1b0efd359104d5cb86e', 1),
        ('ent_36135b45a07c4d03bf06', 'alias_1a1a66e8db7444fba662', 'fact_28a3204497c74a76ba73', 2)]:
        ops.extend([
            {'op': 'retract_alias', 'alias_id': alias, 'reason': 'Coal-flow legend row 33 identifies UGA as dust suppression pump house; row 35 identifies MM-BD as bull dozer.', **legend},
            {'op': 'alias', 'entity': entity, 'alias': f'UGA-{number} Dust Suppression Pump House', **legend},
            {'op': 'retire', 'assertion_id': fact, 'reason': 'Replace generic building classification with the explicit UGA pump-house class from the same source.', **legend},
            {'op': 'assert', 'subject': entity, 'predicate': 'instance_of', 'value': 'pump_house', 'context': {'kind': 'classification', 'basis': '175001 Rev8, PDF p55 legend row 33. DS Pump House identity reconciliation belongs to B01.'}, **legend}])
    # Each affected place and its badge block was independently inspected on p55.
    regions = {
        'UEF-1': [.26,.08,.32,.18], 'UEE-1': [.38,.06,.48,.18],
        'UEF-3': [.58,.12,.66,.24], 'UEF-4': [.655,.24,.758,.33],
        'UEF-5': [.758,.325,.825,.43], 'UEF-6': [.829,.415,.93,.526],
        'UEF-7': [.907,.593,.978,.718], 'UEF-8': [.104,.214,.147,.28],
        'UEF-9': [.172,.311,.215,.39], 'UEF-10': [.264,.405,.304,.474],
        'UEF-11': [.358,.496,.399,.57], 'UEF-12': [.398,.636,.449,.718],
        'UEE-3': [.563,.727,.718,.89],
        'Unit-1 Coal Bunker Bay': [.394,.776,.488,.877],
        'Unit-2 Coal Bunker Bay': [.286,.776,.391,.877]}
    bad = [f for f in facts.values() if not f['retirement'] and isinstance(f['value'], str)
           and ('GK hoist' in f['value'] or 'SAC vacuum-cleaning' in f['value'])]
    assert len(bad) == 15
    badge_ledger = []
    for f in bad:
        label = names[f['canonical_subject']]
        assert f['evidence'][0]['evidence_id'] == FLOW
        prov = support(FLOW, [.05,.715,.246,.89])
        prov['evidence'].append({'evidence_id': FLOW, 'quote': '', 'region': regions[label]})
        if label.startswith('Unit-'):
            value = 'Coal-flow diagram shows SAC ventilation at this bunker bay. SAC is not vacuum cleaning; PC means service water, not ventilation. The SAC badge alone does not establish installed equipment, ductwork or piping routes.'
        elif label == 'UEE-3':
            value = 'Coal-flow badges at the crusher house identify GK drinking water and PC service water; HDF dust extraction is shown separately. HDD means dry-fog dust suppression, but no HDD badge is shown at this house on this sheet. Badges alone do not establish installed piping routes.'
        else:
            value = 'Coal-flow service badges: GK drinking water, PC service water and HDD dry-fog dust suppression. Badges do not define installed piping routes.'
        ops.extend([
            {'op': 'retire', 'assertion_id': f['id'], 'reason': 'Reviewed original legend and this local badge block; previous hoist/ventilation/vacuum interpretation was incorrect.', **prov},
            {'op': 'assert', 'subject': f['canonical_subject'], 'predicate': f['predicate'], 'value': value,
             'context': {**f['context'], 'basis': 'Coal-flow drawing 175001 Rev8, control PDF p55. Legend and local place badges visually checked in B00; design provision only.'}, **prov}])
        badge_ledger.append({'entity': f['canonical_subject'], 'label': label, 'retired_assertion': f['id'], 'reviewed_region': regions[label], 'replacement': value})
    ops.append({'op': 'assert', 'subject': 'ent_56e7a3ed39ed44749525', 'predicate': 'operating_requirement',
                'value': 'UEF-2 is explicitly outside coal-handling scope and shown for reference on coal-flow drawing 175001 Rev8. Preserve its service-water/drinking-water source records as a reference boundary; they do not add another CHP main-route transfer point.',
                'context': {'kind': 'classification', 'basis': 'Control PDF p55 explicit scope note; retains existing UEF-2 identity and utility records.'},
                **support(FLOW, [.648,.897,.758,.956])})
    tp_prov = support('ev_d7d009e07565467e8938', [.82,.79,.985,.98])
    tp_ops = [
        {'op': 'retire', 'assertion_id': 'fact_a3ba0551dcad4930992d', 'reason': 'The immutable source catalog contains GA & MECH LOAD OF TP-1.pdf; p1 identifies drawing 175033 Rev6 and p2 its earlier Rev5 review. The negative-search conclusion is obsolete.', **tp_prov},
        {'op': 'assert', 'subject': TP, 'predicate': 'operating_requirement',
         'value': 'TP1 general arrangement and mechanical-load drawing is available: MAITREE-00-UEF-LH-175033-ISG Rev6, dated 01-Oct-2019, PDF p1; approval stamp 18-Oct-2019. PDF p2 reviews Rev5 and requests 1000 litres instead of 300 litres, with BHEL reply Revised. Detailed hoist, access, tank and arrangement follow-up belongs to B05.',
         'context': {'kind': 'specification', 'basis': 'GA & MECH LOAD OF TP-1.pdf pp1-2. Rev6 drawing and Rev5 review are kept distinct; design source availability is not installed/as-built verification.'},
         **{**tp_prov, 'evidence': tp_prov['evidence'] + [{'evidence_id': 'ev_469e294f8e5b40359f6f', 'quote': '', 'region': [.12,.175,.945,.477]}]}},
        {'op': 'assert', 'subject': TP, 'predicate': 'source_gap',
         'value': 'Finding TP1 GA 175033 resolves the earlier missing-drawing search only. Available GA arrangement, hoist schedule and tank/review details remain B05 work. Access certification, field condition and liner wear limits are not established by this GA.',
         'context': {'kind': 'specification', 'basis': 'B00 bounded review of available TP1 GA pp1-2; no inference of commissioning, maintenance condition or certified access.'},
         **{**tp_prov, 'origin': 'inferred'}}]
    result = []
    for did, title, operations, reviewed in [
        (CONTROL, 'B00: correct UGA identities, reviewed local service legends and UEF-2 scope', ops, [FLOW]),
        (TPDOC, 'B00: replace obsolete TP1 missing-GA claim with revision-qualified source availability', tp_ops, ['ev_d7d009e07565467e8938','ev_469e294f8e5b40359f6f'])]:
        inventory = [e for e in snapshot['evidence'] if e['document_id'] == did]
        result.append({'document_id': did, 'visual_ids': reviewed, 'body': {
            'summary': title, 'operations': operations, 'intake_assessment': {
                'route': 'mixed', 'purpose': title,
                'questions': ['What identity, service legend or source-availability correction is explicitly supported?'],
                'gaps': ['Document-wide block inventory inspected for source/page identity only. Semantic review is limited to the recorded visual IDs and regions; other pages are not re-extracted or declared fully reviewed.', 'Pump-house merges remain B01. Unloader applicability remains a separate B00 decision. TP1 detail remains B05.'],
                'reviewed_evidence_ids': [e['id'] for e in inventory]}}})
    return result, badge_ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snap = json.loads((BASE/'baseline.json').read_text(encoding='utf-8'))
    packages, badge_ledger = proposals(snap)
    out = BASE / ('accepted' if args.apply else 'rehearsal')
    out.mkdir(exist_ok=True)
    assert not (out/'result.json').exists(), 'Already completed: inspect checkpoint instead of replaying.'
    plant = ROOT/'data/plant'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as ro:
        ro.row_factory = sqlite3.Row
        ro.execute('BEGIN')
        before = Store.__new__(Store).model(db=ro)
        assert before == snap['model'] and before['version'] == 593, 'Live state changed: re-review, do not change the guard.'
        if not args.apply:
            backup = BASE/'backup-v593'
            backup.mkdir(exist_ok=True)
            for destination in [backup/'plant.sqlite3', out/'plant.sqlite3']:
                with sqlite3.connect(destination) as dst: ro.backup(dst)
            copied = []
            for d in snap['documents']:
                if d['id'] not in [CONTROL, TPDOC]: continue
                source = plant/'originals'/d['sha256']
                assert hashlib.sha256(source.read_bytes()).hexdigest() == d['sha256']
                paths = [Path('originals')/d['sha256']] + [Path('renders')/e['image'] for e in snap['evidence'] if e['document_id']==d['id'] and e['image']]
                for rel in set(paths):
                    dest=backup/rel;dest.parent.mkdir(exist_ok=True);shutil.copy2(plant/rel,dest);copied.append(str(rel))
            save(backup/'manifest.json', {'version':593, 'sqlite_backup':'plant.sqlite3', 'scope':'Consistent full canonical database plus immutable originals/renders for the two changed source packages. Other original source assets remain unchanged in data/plant.', 'copied_files':copied})
    if args.apply:
        rehearsal=json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))
        assert rehearsal['ok'] and rehearsal['version']==595
        assert packages==json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
    save(out/'packages.json',packages)
    save(BASE/'badge-review.json',badge_ledger)
    store=Store(plant if args.apply else out)
    results=[]
    for index, package in enumerate(packages):
        version=593+index
        body=package['body']
        report=validate(store,{k:body[k] for k in ['summary','operations']},package['document_id'],version,visual_ids=package['visual_ids'])
        assert not report['errors'], report
        pending=stage(store,package['document_id'],body,visual_ids=package['visual_ids'],analysis_dir=str(out),expected_version=version)
        accepted=commit(store,pending['proposal_id'])
        results.append({'proposal_id':pending['proposal_id'],'document_id':package['document_id'],'operations':len(body['operations']), 'warnings':report['warnings'], **accepted})
        save(out/'commit-log.json',results)
    after=store.model()
    old={f['id']:f for f in before['assertions']}; new={f['id']:f for f in after['assertions']}
    retired={o['assertion_id'] for p in packages for o in p['body']['operations'] if o['op']=='retire'}
    for fid,f in old.items():
        if fid in retired:
            assert new[fid]['retirement'] and {k:v for k,v in f.items() if k!='retirement'}=={k:v for k,v in new[fid].items() if k!='retirement'}
        else: assert f==new[fid],fid
    assert before['merges']==after['merges'] and len(before['entities'])==len(after['entities'])
    assert after['version']==595 and len(retired)==18
    assert len(new)-len(old)==20
    assert not any('GK hoist' in str(f['value']) or 'SAC vacuum-cleaning' in str(f['value']) for f in after['assertions'] if not f['retirement'])
    save(out/'model.json',after)
    save(out/'result.json',{'ok':True,'base_version':593,'version':595,'commits':results,'retired_assertions':sorted(retired),'new_assertions':[f for fid,f in new.items() if fid not in old], 'preserved_other_assertions':len(old)-len(retired),'entities_preserved':len(before['entities'])})
    print(json.dumps({'ok':True,'mode':'accepted' if args.apply else 'rehearsal','version':595,'commits':results,'retired':len(retired),'added':len(new)-len(old)}))


if __name__=='__main__':
    main()
