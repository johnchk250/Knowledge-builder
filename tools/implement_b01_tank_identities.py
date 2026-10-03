"""One-time reviewed B01 common tank identity and compartment package from v606."""
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

BASE = ROOT / 'output/plant-enrichment/B01/tank-identities'
TANK1 = 'ent_568564ff3bd948438f86'
TANK2 = 'ent_dbe58a4eb9a74ed6b0c4'
SPDS = 'ent_36777dcc88b24427abb1'
PW = 'ent_73ec6a7ce80147b0b5be'
SHARED = 'ent_1aceca34e2644238a03e'
REDIRECTS = {'ent_515124be3d6b456b9715': TANK1}
RETRACT_ALIAS = 'alias_a18690eeef784d2d984a'


def packages(snap):
    def fact(subject, predicate, value, eid, region, basis, relation=False):
        return {'op':'assert', 'subject':subject, 'predicate':predicate,
                'object_entity' if relation else 'value':value,
                'context':{'kind':'classification' if relation else 'specification','basis':basis},
                **support(eid,region)}
    def pkg(doc,title,ops,visual,scope):
        return {'doc':doc,'visual':visual,'body':{'summary':title,'operations':ops,
                'intake_assessment':{'route':'mixed','purpose':title,
                'questions':['Which common tank and partition does each existing identity represent?'],
                'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==doc],
                'gaps':[scope,'Design identity and attachment only; full piping/control detail remains B02/B03/B04. Available unread pages are not a missing-source finding.']}}}
    eid='ev_6d108aae58914c47bf74'
    reg1=[.24,.68,.535,.976];reg2=[.365,.049,.967,.406]
    ops=[{'op':'merge','source':next(iter(REDIRECTS)),'target':TANK1,
          'reason':'Original runoff P&ID175257 explicitly captions COMMON DS TANK-1 AT PUMP HOUSE-1, SWS-1+DFDS-1, 5.2x3.75x3m, gross58.5/effective50.7m3. Same House-1 RCC tank already represented by canonical target and matching accepted dimensions; source/house GA cross-checked. No new tank or cross-house merge.',
          **support(eid,reg1)},
         {'op':'alias','entity':TANK2,'alias':'DS Pump House-2 Common RCC Tank-2 (three compartments)',**support(eid,reg2)},
         {'op':'retract_alias','alias_id':RETRACT_ALIAS,
          'reason':'Old display label lists only SWP/LSDS/DFDS and misleadingly identifies the entire three-compartment parent as one service compartment. Source shows separate PWS-2, SPDS-1 and DFDS-2+LSDS-2+SWS-2 compartments under COMMON DS TANK-2. Retain canonical parent and children; use the corrected whole-tank alias.',**support(eid,reg2)}]
    roles=[(TANK1,reg1,'Common DS Tank-1 at Pump House-1 serves SWS-1 and DFDS-1. The separately imported Common Tank DS-1 record denotes this same tank; gross58.5m3 and effective50.7m3 are design volumes, not current contents.'),
           (TANK2,reg2,'Common DS Tank-2 is the parent RCC tank assembly at Pump House-2 with three separately identified service compartments: PWS-2; SPDS-1; DFDS-2 + LSDS-2 + SWS-2. Their water services and inlet controls remain distinct; the parent is not a single mixed supply compartment.'),
           (PW,[.431,.22,.594,.353],'Potable-water PWS-2 compartment of Common DS Tank-2 at House-2; gross21m3, effective15.6m3. Keep separate from stockpile DS and shared DFDS/LSDS/SWS water.'),
           (SPDS,[.594,.22,.758,.353],'Stockpile dust-suppression SPDS-1 compartment of Common DS Tank-2 at House-2; gross126m3, effective86.4m3. Drawing shows client makeup and coal-runoff feed inlets into this compartment.'),
           (SHARED,[.758,.22,.927,.353],'Shared DFDS-2 + LSDS-2 + SWS-2 compartment of Common DS Tank-2 at House-2; gross57.75m3, effective41.25m3. Distinct from SPDS and potable-water compartments.')]
    for subject,region,value in roles:
        ops.append(fact(subject,'equipment_role',value,eid,region,'Runoff feed-water P&ID175257, original approved14-Apr-2020 sheet; labelled tank boundaries.'))
    ops.append(fact(TANK2,'operating_requirement',
        'Runoff P&ID175257 labels the Tank-2 inlets MGV-02 for DFDS/LSDS/SWS (00EGC08AA001), MGV-03 for SPDS client makeup (00EGC06AA001), MGV-04 for SPDS runoff (00EGC05AA001), and MGV-05 for PWS (00EGC04AA001). Short MGV numbers are source-local; reconcile the control text before using them as unique plant identities.',
        eid,reg2,'Source-local labels and KKS read from diagram; no valve renumbering, merge or executable control action.'))
    result=[pkg('doc_d92dbaa70d964993bb86','B01: reconcile common Tank-1 and distinguish Tank-2 compartment boundaries',ops,[eid],
                'Single original sheet inventoried and visually inspected, including title/approval, tank1/2 boundaries, dimensions, inlet labels and ports. Dense pond/pump details remain B04.')]
    eid='ev_74ffe42a254144ba8a22';basis='SW/PW philosophy175319 Rev5 dated24-Apr-2020, approved26-May-2020, PDFp10; partition ownership inferred from named service and existing compartment identities.'
    bindings=[('ent_7b7aea7be6094a2fbf91',SHARED,[.05,.063,.965,.245]),
              ('ent_51c1a88aff9b4b24a4a7',SPDS,[.05,.267,.965,.448]),
              ('ent_c67d930239454e2fa46f',PW,[.05,.465,.965,.664])]
    ops=[]
    for valve,comp,reg in bindings:
        op=fact(valve,'part_of',comp,eid,reg,basis,True);op['origin']='inferred';ops.append(op)
    op=fact('ent_4bacbfff7b384d368f55', 'part_of',SPDS,'ev_45c0946dd3164964b682',[.054,.443,.92,.57],
            'PDFp9 runoff pump permissive explicitly locates motorized valve04 at Tank-2 Partition-2 inlet; retain printed KKS disagreement.',True)
    op['origin']='inferred';ops.append(op)
    for comp,reg,value in [
        (SHARED,[.05,.063,.965,.245],'Control text p10 calls the shared-service Partition-1 inlet MGV-01, KKS00EGC08AA001. Runoff P&ID175257 labels the same service/KKS MGV-02. Keep source-local numbering; do not infer another physical inlet valve from the short-number difference.'),
        (SPDS,[.05,.267,.965,.448],'Control text p10 calls SPDS Partition-2 client inlet MGV-02, KKS00EGC06AA001; runoff P&ID175257 uses MGV-03 for that service/KKS. Control p9 prints runoff MGV-04 as00EGC40AA001, while the P&ID prints00EGC05AA001. Preserve both source labels pending B03/B04 reconciliation.'),
        (PW,[.05,.465,.965,.664],'Control text p10 calls potable Partition-3 inlet MGV-03, KKS00EGC04AA001; runoff P&ID175257 labels that service/KKS MGV-05. Keep the potable compartment distinct and retain the source numbering disagreement.')]:
        op=fact(comp,'source_discrepancy',value,eid,reg,'Control paragraphs compared with original runoff P&ID; numbered partition is a service boundary, not a source-independent MGV tag.');op['origin']='inferred'
        if comp==SPDS:op['evidence'].append({'evidence_id':'ev_45c0946dd3164964b682','quote':'','region':[.054,.443,.92,.57]})
        ops.append(op)
    result.append(pkg('doc_e17edf6897d746fabe12','B01: bind existing inlet valves to their documented tank compartments',ops,[eid,'ev_45c0946dd3164964b682'],
                      'All28 evidence blocks inventoried. Original pp1-4,8-10 visually reviewed for revision, stockpile service and partition control. Appended drawing details and remaining controls remain B03/B04 work.'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snap = json.loads((ROOT/'output/plant-enrichment/B01/accepted-v606.json').read_text(encoding='utf-8'))
    pkgs = packages(snap)
    plant = ROOT/'data/plant'
    out = BASE/('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'result.json').exists(), 'Already complete; inspect checkpoint.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 606 and before == snap['model'], 'Live state changed; review again.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v606'
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
            save(backup/'manifest.json', {'version':606, 'copied_files':copied,
                 'scope':'Consistent full SQLite database and package originals/renders; unrelated sources remain immutable in data/plant.'})
    if args.apply:
        assert pkgs == json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json', pkgs)
    store = Store(plant if args.apply else out)
    logs = []
    for i, p in enumerate(pkgs):
        body = p['body']
        v = 606+i
        report = validate(store, {k:body[k] for k in ['summary','operations']}, p['doc'], v, visual_ids=p['visual'])
        assert not report['errors'], report
        staged = stage(store, p['doc'], body, visual_ids=p['visual'], analysis_dir=str(out), expected_version=v)
        result = commit(store, staged['proposal_id'])
        logs.append({'proposal_id':staged['proposal_id'], 'document_id':p['doc'], 'warnings':report['warnings'], **result})
        save(out/'commit-log.json', logs)
    after = store.model()
    save(out/'model.json', after)
    assert after['version'] == 608
    facts = {a['id']:a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a) == preserved(facts[a['id']]), a['id']
        for field in ['canonical_subject','canonical_object']:
            assert facts[a['id']][field] == REDIRECTS.get(a[field], a[field])
    assert len(before['entities']) == len(after['entities'])
    old_aliases = {a['id']:a for a in before['aliases']}
    for a in after['aliases']:
        if a['id'] in old_aliases and a['id'] != RETRACT_ALIAS:
            assert a == old_aliases[a['id']]
    assert next(a for a in after['aliases'] if a['id']==RETRACT_ALIAS)['retracted']
    assert len(after['aliases']) == len(before['aliases'])+1
    assert len(after['merges']) == len(before['merges'])+1
    assert before['conflicts'] == after['conflicts']
    added = [a for a in after['assertions'] if a['created_version'] > 606]
    assert len(added) == 13
    save(out/'result.json', {'ok':True, 'version':608, 'proposals':[x['proposal_id'] for x in logs],
         'redirects':REDIRECTS, 'added_claims':added, 'preserved_assertions':len(before['assertions'])})
    print(json.dumps({'ok':True, 'version':608, 'mode':out.name, 'proposals':[x['proposal_id'] for x in logs]}))


if __name__ == '__main__':
    main()
