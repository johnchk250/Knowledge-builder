"""Accept reviewed B00 applicability/boundary qualifications at v595; rehearse first."""
import argparse
import json
import sqlite3
import shutil
import hashlib
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate,commit
from tools.implement_b00_corrections import save,support

BASE=ROOT/'output/plant-enrichment/B00/boundary-decisions'


def build(snap):
    model=snap['model']
    ids={e['label']:e['id'] for e in model['entities'] if e['id']==e['canonical_id']}
    packages=[]
    def package(doc,title,ops,visual,gaps):
        packages.append({'document_id':doc,'visual_ids':visual,'body':{'summary':title,'operations':ops,'intake_assessment':{
            'route':'mixed','purpose':title,'questions':['Which numbered-machine applicability or external route boundary is actually established by this source?'],
            'gaps':gaps,'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==doc]}}})
    def fact(label,predicate,value,eid,region,origin='explicit'):
        return {'op':'assert','subject':ids[label],'predicate':predicate,'value':value,
                'context':{'kind':'specification','basis':'B00 bounded identity/scope review. Retain original source qualification; no identity merge or extra physical equipment is implied.'},
                **{**support(eid,region),'origin':origin}}
    ops=[]
    for i in [1,2,3]:
        text=(f'DBR 175154 Rev2, dated 30-Jun-2020, identifies SUL-{i} as '+
              ('one of two Type 1 rail-mounted grab unloaders in the coal design column.' if i<3 else 'the single Type 2 rail-mounted grab unloader in the limestone design column. This DBR column does not rule out the separately documented coal capability of its reversible shuttle.'))
        ops.append(fact(f'SUL-{i}','operating_requirement',text,'ev_33262138211444af8553',[.095,.17,.93,.25]))
        ops.append(fact(f'Coal Ship Unloader-{i}','source_gap',f'B00 identity decision: retain this numbered layout identity separately from SUL-{i} until a numbered layout/vendor cross-reference proves the mapping. DBR 175154 distinguishes two Type 1 units (SUL-1/2) and one Type 2 unit (SUL-3); matching suffix alone is insufficient. B07/B08 own the available Type1/Type2 GA and jetty-layout cross-check. These records are identity candidates, not evidence of six installed unloaders.','ev_33262138211444af8553',[.095,.17,.93,.25],'inferred'))
    package('doc_cd1aae66b455491b8883','B00: qualify unloader type applicability and prevent unproven numbered merges',ops,
            ['ev_1459550ecc534b969c5a','ev_33262138211444af8553','ev_9cf7a4b7dc0d4a58aca9'],
            ['All three DBR pages reviewed. Numbered layout/vendor identity mapping is explicitly deferred to B07/B08; full GA/cycle-time detail remains available work, not missing evidence.'])
    ops=[]
    for i in [1,2]:
        op=fact(f'SUL-{i}','source_discrepancy','Shuttle GA 019676_03.PDF (title block 47043041 Rev4, FIO 18-Mar-2021) p2 identifies SUL-1/2 as Type 1, while p5 caption reads SUL 1 & SUL 2 (TYPE-2). Preserve this internal source wording conflict; do not change the numbered machine type or clone Type 2 equipment from the p5 caption.','ev_39538c76849144e884cf',[.744,.028,.978,.123])
        op['evidence'].append({'evidence_id':'ev_40d63b4a6e5844758dc1','quote':'','region':[.279,.921,.53,.949]})
        ops.append(op)
    op=fact('SUL-3','operating_requirement','Shuttle GA p1 identifies the Type 2 shuttle for coal and limestone; p2 assigns SUL-3 to Type 2 and shows reversible conveyor operation. The p4 SUL-3 arrangement depicts separate LSEAC-1 and EAC-1A/B discharge positions. This is mode-dependent design capability, not simultaneous coal/limestone operation.','ev_915199438a3149249e76',[.06,.034,.713,.285])
    op['evidence'] += [{'evidence_id':'ev_39538c76849144e884cf','quote':'','region':[.744,.028,.978,.165]},{'evidence_id':'ev_d6a634645e064a74884e','quote':'','region':[.07,.5,.715,.949]}]
    ops.append(op)
    package('doc_0d848e40b9394c72810b','B00: preserve the unloader Type1/Type2 source conflict and dual-material boundary',ops,
            ['ev_915199438a3149249e76','ev_39538c76849144e884cf','ev_4df831cfa0a84550ac1e','ev_d6a634645e064a74884e','ev_40d63b4a6e5844758dc1','ev_bfe377d522974174b9e7'],
            ['All six sheets visually inspected for identity and applicability. Dense drive/BOM/maintenance values are not re-extracted here; B07/B08 must review readable detail crops before enrichment.'])
    ops=[]
    for label,eid,region,desc in [
        ('UEF-2','ev_60765a8823b543efadc1',[.785,.039,.969,.434],'The UEF-2 key plan shows LSPC-1A/B and its local SW/PW arrangement'),
        ('TP-18','ev_73ef3663613a425dba08',[.694,.036,.97,.221],'The TP-18 key plan shows GPC-2A/B and LSPC-1A/B'),
        ('TP-17','ev_49cf115f16da4002ab16',[.701,.037,.969,.224],'The TP-17 key plan shows LSEAC-2'),
        ('TP-16','ev_d2f9b563d60f41e6a2c3',[.793,.035,.972,.34],'The TP-16 key plan shows GPC-1A/B and LSPC-1A/B')]:
        ops.append(fact(label,'operating_requirement',desc+'. These are source-specific limestone/gypsum-side reference interfaces in SW/DW layout 175338 Rev1 (FIO 27-Dec-2019), not additional EAC/EBA coal-route transfer points. Retain the existing utility BOM; common water integration is B03 and does not extend CHP coal-flow scope.',eid,region,'inferred'))
    package('doc_411067c712284bc5a957','B00: retain UEF-2 and TP16-18 as source-qualified utility reference boundaries',ops,
            ['ev_60765a8823b543efadc1','ev_73ef3663613a425dba08','ev_49cf115f16da4002ab16','ev_d2f9b563d60f41e6a2c3','ev_fd0b979811fa426db500'],
            ['All five sheets reviewed for project/title, key plans, service identification and review status. BOM quantities remain the existing claims; no new piping edge or field coordinate is inferred. Shared main/header continuation belongs to B03.'])
    return packages


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    snap=json.loads((ROOT/'output/plant-enrichment/B00/baseline.json').read_text(encoding='utf-8'))
    packages=build(snap);plant=ROOT/'data/plant';out=BASE/('accepted' if args.apply else 'rehearsal');out.mkdir(parents=True,exist_ok=True)
    assert not (out/'result.json').exists(),'Already completed; inspect checkpoint.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN');before=Store.__new__(Store).model(db=db)
        assert before['version']==595,'Changed live model requires new source/state review.'
        if not args.apply:
            save(BASE/'baseline-model.json',before)
            backup=BASE/'backup-v595';backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3',backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:db.backup(dst)
            copied=[]
            for d in snap['documents']:
                if d['id'] not in [p['document_id'] for p in packages]:continue
                assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()==d['sha256']
                paths=[Path('originals')/d['sha256']]+[Path('renders')/e['image'] for e in snap['evidence'] if e['document_id']==d['id'] and e['image']]
                for rel in set(paths):
                    dest=backup/rel;dest.parent.mkdir(exist_ok=True);shutil.copy2(plant/rel,dest);copied.append(str(rel))
            save(backup/'manifest.json',{'version':595,'scope':'Consistent SQLite database plus affected immutable originals/renders; all other source assets unchanged in data/plant.','copied_files':copied})
    if args.apply:
        assert before==json.loads((BASE/'baseline-model.json').read_text(encoding='utf-8'))
        assert packages==json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json',packages);store=Store(plant if args.apply else out);results=[]
    for i,p in enumerate(packages):
        b=p['body'];v=595+i
        report=validate(store,{k:b[k] for k in ['summary','operations']},p['document_id'],v,visual_ids=p['visual_ids']);assert not report['errors'],report
        staged=stage(store,p['document_id'],b,visual_ids=p['visual_ids'],analysis_dir=str(out),expected_version=v)
        result=commit(store,staged['proposal_id']);results.append({'proposal_id':staged['proposal_id'],'document_id':p['document_id'],'warnings':report['warnings'],**result});save(out/'commit-log.json',results)
    after=store.model();old={a['id']:a for a in before['assertions']};new={a['id']:a for a in after['assertions']}
    assert all(new[k]==v for k,v in old.items())
    assert before['entities']==after['entities'] and before['aliases']==after['aliases'] and before['merges']==after['merges']
    assert after['version']==598 and len(new)-len(old)==13
    save(out/'model.json',after);save(out/'result.json',{'ok':True,'base_version':595,'version':598,'commits':results,'new_assertions':[v for k,v in new.items() if k not in old], 'all_prior_assertions_preserved':len(old)})
    print(json.dumps({'ok':True,'mode':'accepted' if args.apply else 'rehearsal','version':598,'added':13,'commits':results}))


if __name__=='__main__':main()
