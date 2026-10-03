"""One-time reviewed B01 ownership corrections from v612."""
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

BASE = ROOT / 'output/plant-enrichment/B01/ownership'
GENERIC='ent_a66da2f42a3e427c8ee4'
SYSTEM1='ent_2024dfa4a4084a86b0b5'
SYSTEM2='ent_b2f48e8d116f484882a1'
NOZZLES='ent_7c06eb18a11849759eb4'
BOX='ent_99172a925e66459d8f7e'
REDIRECTS={GENERIC:SYSTEM1}
RETIRED={'fact_985d99248a9c4f65b028','fact_f1f2f9445fe04ca2a5d1','fact_05f39f07b9fe40488d77'}
RETRACT_ALIAS='alias_757ea71f8742404eb595'


def packages(snap):
    def fact(subject,predicate,value,eid,region,basis,relation=False):
        return {'op':'assert','subject':subject,'predicate':predicate,'object_entity' if relation else 'value':value,
                'context':{'kind':'classification' if predicate=='instance_of' else 'specification','basis':basis},**support(eid,region)}
    def retire(fid,eid,reg,reason):return {'op':'retire','assertion_id':fid,'reason':reason,**support(eid,reg)}
    def pkg(doc,title,ops,visual,scope):
        return {'doc':doc,'visual':visual,'body':{'summary':title,'operations':ops,'intake_assessment':{'route':'mixed','purpose':title,
          'questions':['Does the source describe a shared physical owner, an individual asset or an applicable source group?'],
          'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==doc],
          'gaps':[scope,'Detailed source equipment remains B02/B03; this identity correction does not assign installed serials, site settings or new physical units.']}}}
    eid='ev_66c26911855146e5a66a';reg=[.05,.11,.95,.54]
    ops=[retire(fid,eid,reg,'Original175097 p2 schedules nozzle groups for BOTH System1 and2. This imported source-level record is not a single physical spray nozzle owned by the TH/PSH System1 record.') for fid in ['fact_985d99248a9c4f65b028','fact_f1f2f9445fe04ca2a5d1']]
    ops += [fact(NOZZLES,'instance_of','equipment_design_reference',eid,reg,'Original grouped nozzle schedule, not an extra installed nozzle.'),
            fact(NOZZLES,'design_applicability','Nozzle design175097 Rev3, FIO15-Feb-2019, covers both DFDS System1 and2. Schedule counts346 and280 are source-system totals, not a local application count or simultaneously operating population. p3 Lechler nozzle design and p4 vendor droplet test apply at their stated test conditions; no site commissioning result is established.',eid,reg,'Original pp1-4 visually reviewed; source group applicability distinct from local installed applications.')]
    for target in [SYSTEM1,SYSTEM2]:ops.append(fact(NOZZLES,'design_detail_applies_to',target,eid,reg,'Schedule explicitly separates DFDS1/2 source totals.',True))
    result=[pkg('doc_5537009e2cff4fad875e','B01: distinguish the common nozzle design reference from physical nozzle instances',ops,[eid],
                'All4 original pages visually reviewed for cover revision/status, two-system schedule, nozzle design and vendor test scope; detailed application mapping remains B02/local batches.')]
    eid='ev_b11a00f2ef7041d99fd7';reg=[.025,.575,.98,.975]
    ops=[retire('fact_05f39f07b9fe40488d77',eid,reg,'Original PDFp3 says SOLENOID BOX FOR CHP STOCKPILE, references stockpile P&ID175255, and gives total12 boxes. PDFp2 is LHPstockpile. Cover/filename does not prove DFDSSystem1 ownership; remove the incorrect link while retaining the source record.'),
         {'op':'alias','entity':BOX,'alias':'Stockpile water solenoid-box design reference (CHP/LHP)',**support(eid,reg)},
         {'op':'retract_alias','alias_id':RETRACT_ALIAS,'reason':'Imported DFDS label came from catalog title; original sheets identify CHP/LHP stockpile water. Retain historical alias provenance and replace current display with correct source scope.',**support(eid,reg)},
         fact(BOX,'instance_of','equipment_design_reference',eid,reg,'Source contains generic CHP/LHP box drawings, not one unique installed box.'),
         fact(BOX,'design_applicability','Drawing175098 cover and sheet revision markings differ: cover large caption ISG3, title blockRev2 approved1-Aug-2019. PDFp3 is CHPstockpile(sheet2); PDFp2 is LHPstockpile(sheet3). CHP sheet specifies total12 boxes for stockpile, not12 peryard. The imported DFDS name and ownership are corrected; no local box instance is created.',eid,reg,'Original all3pages reviewed; use PDF page plus printed sheet/caption to disambiguate.'),
         fact(BOX,'design_detail_applies_to','ent_3ebb96607d1f4f3094f0',eid,reg,'CHPstockpile caption and explicit P&ID175255 reference identify the stockpile-water service.',True),
         fact(BOX,'source_discrepancy','PDFp2 LHPstockpile front/plan and BOM say32NB while the covered front view says65NB; PDFp3 CHPstockpile says65NB. Do not transfer LHPdimensions/valve sizes to CHP or treat the cover filename as DFDS applicability. B03 owns detailed box acceptance and sheet-specific qualifications.', 'ev_b50dcfc220cc4c8c8e30',[.05,.055,.78,.65],'Original LHPsheet views compared; source-specific discrepancy retained.')]
    result.append(pkg('doc_d9051ae5caff486e9dbf','B01: correct stockpile solenoid-box source scope and remove false DFDS ownership',ops,[eid,'ev_b50dcfc220cc4c8c8e30'],
                      'All3original PDFpages visually reviewed; PDFp2=printedSheet3LHP and PDFp3=printedSheet2CHP. Existing approval stamp retained; no final installed box mapping asserted.'))
    eid='ev_049473eb524d41f78646';reg=[.10,.045,.87,.39];prov=support(eid,reg);prov['origin']='inferred'
    ops=[{'op':'merge','source':GENERIC,'target':SYSTEM1,'reason':'DBR175090 p2 created the TH/PSH system from the DFDSP1A/B and SC1A/B schedule; p4 explicitly names DFDS SYSTEM1, House1 near jetty and UEF1/UEE1/UEF3-7 scope. These same four canonical machines already belong to System1. Broad nozzle/incorrect solenoid source-group attachments have now been separately corrected. The remaining generic TH/PSH record is the same System1 design identity, not a third common supply.',**prov},
         fact(SYSTEM1,'documented_source_identity','The historical Dry Fog Dust Suppression System - TH and PSH record denotes DFDS System1 in DBR175090 pp2/4: its DFDSP1A/B and SC1A/B pair supplies transfer houses and primary screen house from House1 near jetty. Generic nozzle design spans both systems; stockpile-water solenoid-box drawings are separate design references and are not owned physical DFDSSystem1 assets.',eid,reg,'Identity inferred from explicit DBR title, numbered equipment, house and named consumers; no merge with System2.')]
    ops[-1]['origin']='inferred'
    result.append(pkg('doc_456cfee5f9824d68b651','B01: reconcile the historical TH/PSH owner with DFDS System1',ops,[eid],
                      'All21evidence blocks inventoried; original pp1-4,8,10,15-16 reviewed previously, pp2/4/8/10 rechecked for identity and distinct system scopes. Remaining calculations B02.'))
    return result


def verify_result(before,after,logs,out):
    assert after['version']==615
    facts={a['id']:a for a in after['assertions']}
    for a in before['assertions']:
        new=facts[a['id']]
        old_payload=preserved(a);new_payload=preserved(new)
        if a['id'] in RETIRED:
            assert new['retirement'];old_payload.pop('retirement');new_payload.pop('retirement')
        assert old_payload==new_payload,a['id']
        for field in ['canonical_subject','canonical_object']:assert new[field]==REDIRECTS.get(a[field],a[field])
    new_aliases={a['id']:a for a in after['aliases']}
    for a in before['aliases']:
        if a['id']!=RETRACT_ALIAS:assert a==new_aliases[a['id']]
    assert next(a for a in after['aliases'] if a['id']==RETRACT_ALIAS)['retracted']
    assert len(after['aliases'])==len(before['aliases'])+1
    assert len(before['entities'])==len(after['entities']) and len(after['merges'])==len(before['merges'])+1
    assert before['conflicts']==after['conflicts']
    added=[a for a in after['assertions'] if a['created_version']>612];assert len(added)==9
    save(out/'result.json',dict(ok=True,version=615,proposals=[x['proposal_id'] for x in logs],redirects=REDIRECTS,retired_assertions=sorted(RETIRED),added_claims=added,preserved_assertions=len(before['assertions'])-len(RETIRED)))
    print(json.dumps(dict(ok=True,version=615,mode=out.name,proposals=[x['proposal_id'] for x in logs])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify-rehearsal', action='store_true')
    args = parser.parse_args()
    snap = json.loads((ROOT/'output/plant-enrichment/B01/accepted-v612.json').read_text(encoding='utf-8'))
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
        assert before['version'] == 612 and before == snap['model'], 'Live state changed; review again.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v612'
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
            save(backup/'manifest.json', {'version':612, 'copied_files':copied,
                 'scope':'Consistent full SQLite database and package originals/renders; unrelated sources remain immutable in data/plant.'})
    if args.apply:
        assert pkgs == json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json', pkgs)
    store = Store(plant if args.apply else out)
    logs = []
    for i, p in enumerate(pkgs):
        body = p['body']
        v = 612+i
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
