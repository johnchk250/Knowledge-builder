"""Rehearse and accept a saved, source-reviewed B02 package with exact baseline guard."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate, commit
from tools.implement_b00_corrections import save


def verify(before,after,pkg,out):
    facts={a['id']:a for a in after['assertions']}
    retired={o['assertion_id'] for o in pkg['body']['operations'] if o['op']=='retire'}
    for a in before['assertions']:
        actual=facts[a['id']]
        if a['id'] in retired:
            assert a['retirement'] is None and actual['retirement'] is not None
            assert {k:v for k,v in a.items() if k!='retirement'}=={k:v for k,v in actual.items() if k!='retirement'}
        else:
            assert a==actual
    aliases={a['id']:a for a in after['aliases']}
    assert all(a==aliases[a['id']] for a in before['aliases'])
    assert before['conflicts']==after['conflicts'] and before['merges']==after['merges']
    nodes=[e for e in after['entities'] if e['created_version']>before['version']]
    assert len(nodes)==pkg['expected_new_components']
    for e in nodes:
        owners=[a for a in after['assertions'] if a['canonical_subject']==e['id'] and a['predicate']=='part_of' and not a['retirement']]
        assert len(owners)==1,(e['label'],owners)
    save(out/'result.json',{'ok':True,'version':after['version'],'new_components':len(nodes),
                          'added_assertions':len(after['assertions'])-len(before['assertions']),
                          'all_prior_assertions_preserved':len(before['assertions'])-len(retired),
                          'explicitly_retired_assertions':sorted(retired),
                          'all_prior_aliases_merges_conflicts_preserved':True})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package');p.add_argument('--apply',action='store_true');args=p.parse_args()
    path=Path(args.package).resolve();pkg=json.loads(path.read_text(encoding='utf8'));base=path.parent
    baseline=pkg['baseline_version'];before=json.loads((ROOT/pkg['baseline_model']).read_text(encoding='utf8'))
    assert before['version']==baseline
    plant=ROOT/'data/plant';out=base/('accepted' if args.apply else 'rehearsal');out.mkdir(exist_ok=True)
    assert not (out/'commit-log.json').exists(),'Inspect partial acceptance; never replay a committed package.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN')
        assert Store.__new__(Store).model(db=db)==before,'Live baseline changed: source/state re-review required.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup=base/f'backup-v{baseline}';backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3',backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:db.backup(dst)
            doc=dict(db.execute('SELECT * FROM documents WHERE id=?',(pkg['document_id'],)).fetchone())
            assert hashlib.sha256((plant/'originals'/doc['sha256']).read_bytes()).hexdigest()==doc['sha256']
            paths={Path('originals')/doc['sha256']}|{Path('renders')/row[0] for row in db.execute('SELECT image FROM evidence WHERE document_id=? AND image IS NOT NULL',(pkg['document_id'],))}
            for rel in paths:
                dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(plant/rel,dest)
            save(backup/'manifest.json',{'version':baseline,'scope':'Consistent full database plus immutable original/all rendered pages for this source package.','files':sorted(str(p) for p in paths)})
    if args.apply:
        assert pkg==json.loads((base/'rehearsal/package.json').read_text(encoding='utf8'))
        assert json.loads((base/'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    save(out/'package.json',pkg);store=Store(plant if args.apply else out)
    body=pkg['body'];report=validate(store,{k:body[k] for k in ['summary','operations']},pkg['document_id'],baseline,visual_ids=pkg['visual_ids'])
    save(out/'validation.json',report);assert not report['errors'],report
    staged=stage(store,pkg['document_id'],body,visual_ids=pkg['visual_ids'],expected_version=baseline,analysis_dir=str(out))
    accepted=commit(store,staged['proposal_id']);save(out/'commit-log.json',[{'proposal_id':staged['proposal_id'],**accepted}])
    after=store.model();save(out/'model.json',after);verify(before,after,pkg,out)
    print(json.dumps({'proposal':staged['proposal_id'],'version':after['version'],'mode':out.name}))


if __name__=='__main__':main()
