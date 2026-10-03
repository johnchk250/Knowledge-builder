"""One-time reviewed B01 SPDS identity packages from v608."""
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

BASE = ROOT / 'output/plant-enrichment/B01/spds-identities'
PUMPS = ['ent_8018190d7c0b4b098fa7', 'ent_35093c21b4754c8695d3']
CONTROL = ['ent_5cf1b973d1714524bebb', 'ent_2f054f02b4c448b7b292']
VENDOR = ['ent_e0d8986c60c64a439ac0', 'ent_ad45a2d5b7054749b6ca']
REDIRECTS = dict(zip(CONTROL+VENDOR, PUMPS+PUMPS))


def packages(snap):
    def fact(subject, predicate, value, eid, region, basis, relation=False):
        return {'op':'assert','subject':subject,'predicate':predicate,
                'object_entity' if relation else 'value':value,
                'context':{'kind':'classification' if predicate=='instance_of' else 'specification','basis':basis},
                **support(eid,region)}
    def pkg(doc,title,ops,visual,scope):
        return {'doc':doc,'visual':visual,'body':{'summary':title,'operations':ops,
                'intake_assessment':{'route':'mixed','purpose':title,
                'questions':['Which stockpile pump names denote the same two design units and which are grouped source records?'],
                'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==doc],
                'gaps':[scope,'Evidence inventory is distinct from semantic visual review. B03 owns detailed pump/drive and SPDS header/control extraction; this package does not establish installed configuration or commissioned settings.']}}}
    eid='ev_0ed8d22358b747368ad7'; house=[.70,.025,.99,.28]; schedule=[.35,.57,.64,.715]
    ops=[]
    for lane,old,new in zip('AB',CONTROL,PUMPS):
        prov=support(eid,house);prov['origin']='inferred'
        prov['evidence'].append({'evidence_id':eid,'quote':'','region':schedule})
        reason=f'Philosophy175319 Rev5 PDFp16 appends stockpile P&ID175255 Rev2: its House2 diagram labels SPDSP-2{lane} with KKS00EGC06KP00{1 if lane=="A" else 2}, while the SAME sheet schedule names the sole SPDSP-1A/1B pair, quantity2(1W+1S),154m3/h124mwc. Cross-checked p8 control names/KKS and standalone175255 original. These are inconsistent names for one pair in one service, not four pumps; preserve literal source disagreement.'
        ops.append({'op':'merge','source':old,'target':new,'reason':reason,**prov})
        op=fact(new,'documented_source_identity',f'SPDSP-1{lane} (same-sheet schedule and earlier DBR/P&ID) and SPDSP-2{lane} (philosophy175319 p8 and p16 KKS-labelled diagram) are reconciled as one stockpile DS design unit. The p16 diagram and schedule retain different numbers despite representing the same two-pump duty/standby group. Earlier intake statements that equivalence was not yet asserted remain historical provenance; this reviewed identity decision supplies the missing reconciliation.',eid,house,'Identity inference from same-sheet diagram/schedule and exact KKS; not suffix or capacity matching alone.')
        op['origin']='inferred';op['evidence'].append({'evidence_id':eid,'quote':'','region':schedule});ops.append(op)
        ops.append(fact(new,'located_at','ent_36135b45a07c4d03bf06',eid,house,'P&ID explicitly encloses this numbered pump in PUMP HOUSE-2 (UGA-2); existing system ownership retained.',True))
    result=[pkg('doc_e17edf6897d746fabe12','B01: reconcile SPDSP1/2 names using the same-sheet pump schedule and KKS diagram',ops,[eid],
                'All28 evidence blocks inventoried. Original pp1-4,8-10 plus p16 house, schedule and title regions visually reviewed. Other controls and appended drawings remain available B03/B04 work.')]
    eid='ev_41d5812e05f34b2f9b70';reg=[.84,.59,.989,.795];ops=[]
    for lane,old,new in zip('AB',VENDOR,PUMPS):
        prov=support(eid,reg);prov['origin']='inferred'
        ops.append({'op':'merge','source':old,'target':new,'reason':f'House2 GA175051 reference table identifies stockpile DS SPDSP2A/2B against P&ID175255 and its corresponding pump row SDSP2A/2B against vendor175261, each2(1W+1S). Original vendor175261 Item4 pp17/19 names PWDSSP2A/2B,2 pumps,154m3/h124m, distinct from separate SWP/PWP/LSDSP items. This explicit house/service/reference bridge identifies PWDSSP2{lane} with canonical SPDSP1{lane} via the accepted same-sheet SPDSP1/2 reconciliation. SDSP abbreviation remains source-local; not a capacity-only match.',**prov})
        op=fact(new,'documented_source_identity',f'Vendor PWDSSP-2{lane} (175261 Item4) is the House2 stockpile pump also called SPDSP-2{lane} in the house/P&ID references and SPDSP-1{lane} in the schedule. GA175051 links the stockpile service to175255 and the pump row printed SDSP2A/2B to175261. Separate potable, service-water and limestone pump rows/items prevent cross-service substitution. This is a reviewed cross-document design-identity inference; original tags and duty facts remain inspectable.',eid,reg,'GA175051 explicit document references cross-checked with original175261 cover,Item4GA/datasheet and175319p16.');op['origin']='inferred';ops.append(op)
    result.append(pkg('doc_d0cb76dd3ab3478295db','B01: reconcile the vendor stockpile pump pair through House2 explicit source references',ops,[eid],
                      'Both original GA pages previously visually reviewed; p1 reference table rechecked for all service/pump rows. Vendor175261 pp1,2,17,19-21,27 corroborate scope; not new motor/BOM acceptance.'))
    def group(g,eid,region,description):
        ops=[fact(g,'instance_of','equipment_design_reference',eid,region,'Two-unit source group; retired aggregate facts stay retired.'),fact(g,'design_applicability',description,eid,region,'Source grouping applies to reconciled canonical individual units.')]
        for target in PUMPS:
            op=fact(g,'design_detail_applies_to',target,eid,region,'Applicability inferred using accepted house/P&ID/vendor identity bridge.',True);op['origin']='inferred';ops.append(op)
        return ops
    eid='ev_f96d2da5efe14366a974'
    result.append(pkg('doc_777d1a06d4fa4e8ba231','B01: retain stockpile DBR pump group as a design reference',group('ent_7932374f88714f7d82a9',eid,[.13,.14,.94,.49],
        'DBR175256 Rev2 names SPDSP-1A/1B,quantity2(1W+1S),154m3/h124mwc and tentative110kW motors. This grouped design reference applies to the two canonical pumps, not a third machine; later source-name qualifications remain attached to those individual records.'),[eid],
        'All8 pages inventoried as text; original p2 schedule visually reviewed. Remaining DBR calculations/annex details remain B03 available work.'))
    eid='ev_2580114fe289404dbdd7'
    result.append(pkg('doc_32c803b2331849b098d8','B01: retain Flowmore stockpile pump group as a vendor design reference',group('ent_ab84df3adf75499e876d',eid,[.04,.065,.964,.887],
        'Vendor175261 Rev2 Item4 datasheet (internal Rev1 dated13-May-2019;approved24-Jun-2019) covers two Flowmore PWDSSP-2A/2B pumps. The group applies to canonical SPDSP-1A/B via the reviewed House2 reference bridge. Rated duty154m3/h124m and shutoff head134m are distinct; no third pump or final installed configuration is asserted.'),[eid],
        'All27 PDFpages inventoried. Original pp1,2,17,19,20,21,27 visually reviewed for revision,Item4identity,duty and review scope. Remaining vendor assembly detail is B03 available work.'))
    return result


def verify_result(before, after, logs, out):
    assert after['version'] == 612
    facts = {a['id']:a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a) == preserved(facts[a['id']]), a['id']
        for field in ['canonical_subject','canonical_object']:
            assert facts[a['id']][field] == REDIRECTS.get(a[field], a[field])
    assert before['aliases'] == after['aliases'] and len(before['entities']) == len(after['entities'])
    assert len(after['merges']) == len(before['merges'])+4
    expected = json.loads((BASE.parent/'expected-conflicts-v612.json').read_text(encoding='utf8'))
    assert after['conflicts'] == expected, after['conflicts']
    added = [a for a in after['assertions'] if a['created_version'] > 608]
    assert len(added) == 14
    save(out/'result.json', {'ok':True, 'version':612, 'proposals':[x['proposal_id'] for x in logs],
         'redirects':REDIRECTS, 'added_claims':added, 'preserved_assertions':len(before['assertions'])})
    print(json.dumps({'ok':True, 'version':612, 'mode':out.name, 'proposals':[x['proposal_id'] for x in logs]}))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify-rehearsal', action='store_true')
    args = parser.parse_args()
    snap = json.loads((ROOT/'output/plant-enrichment/B01/accepted-v608.json').read_text(encoding='utf-8'))
    pkgs = packages(snap)
    plant = ROOT/'data/plant'
    out = BASE/('accepted' if args.apply else 'rehearsal')
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'result.json').exists(), 'Already complete; inspect checkpoint.'
    if args.verify_rehearsal:
        assert not args.apply
        assert pkgs == json.loads((out/'packages.json').read_text(encoding='utf8'))
        verify_result(snap['model'], json.loads((out/'model.json').read_text(encoding='utf8')), json.loads((out/'commit-log.json').read_text(encoding='utf8')), out)
        return
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        assert before['version'] == 608 and before == snap['model'], 'Live state changed; review again.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v608'
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
            save(backup/'manifest.json', {'version':608, 'copied_files':copied,
                 'scope':'Consistent full SQLite database and package originals/renders; unrelated sources remain immutable in data/plant.'})
    if args.apply:
        assert pkgs == json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json', pkgs)
    store = Store(plant if args.apply else out)
    logs = []
    for i, p in enumerate(pkgs):
        body = p['body']
        v = 608+i
        report = validate(store, {k:body[k] for k in ['summary','operations']}, p['doc'], v, visual_ids=p['visual'])
        assert not report['errors'], report
        staged = stage(store, p['doc'], body, visual_ids=p['visual'], analysis_dir=str(out), expected_version=v)
        result = commit(store, staged['proposal_id'])
        logs.append({'proposal_id':staged['proposal_id'], 'document_id':p['doc'], 'warnings':report['warnings'], **result})
        save(out/'commit-log.json', logs)
    after = store.model()
    save(out/'model.json', after)
    verify_result(before, after, logs, out)


if __name__ == '__main__':
    main()
