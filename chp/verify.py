"""Read-only integrity inspection of a workspace or unpacked backup."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from .store import dumps


def verify(root):
    root=Path(root).resolve()
    errors=[]
    db=sqlite3.connect((root/'plant.sqlite3').as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        db.execute('BEGIN')
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok': errors.append('SQLite structural integrity check failed')
        if db.execute('PRAGMA foreign_key_check').fetchall(): errors.append('Broken foreign-key references')
        documents=list(db.execute('SELECT * FROM documents'))
        evidence=list(db.execute('SELECT * FROM evidence'))
        for d in documents:
            file=root/'originals'/d['sha256']
            if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=d['sha256']:
                errors.append('Missing or modified original: '+d['id'])
        renders=set()
        for e in evidence:
            metadata=json.loads(e['metadata'])
            digest=hashlib.sha256(dumps([e['text'],e['page'],e['locator'],e['image'],metadata]).encode()).hexdigest()
            if digest!=e['sha256']: errors.append('Modified evidence: '+e['id'])
            if e['image'] and e['image'] not in renders:
                file=root/'renders'/e['image'];renders.add(e['image'])
                if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=metadata['render_sha256']:
                    errors.append('Missing or modified page render: '+e['id'])
        if db.execute("SELECT name FROM sqlite_master WHERE name='mesh_assets'").fetchone():
            for mesh in db.execute('SELECT sha256 FROM mesh_assets'):
                file=root/'meshes'/mesh['sha256']
                if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=mesh['sha256']:
                    errors.append('Missing or modified OBJ original: '+mesh['sha256'])
        previous='0'*64
        versions=list(db.execute('SELECT * FROM versions ORDER BY version'))
        for n,v in enumerate(versions,1):
            digest=hashlib.sha256(dumps([v['version'],v['proposal_id'],v['created'],json.loads(v['patch']),previous]).encode()).hexdigest()
            if v['version']!=n or v['previous_hash']!=previous or v['hash']!=digest: errors.append('Version chain mismatch at '+str(v['version']))
            previous=v['hash']
        current=int(db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0])
        if current!=len(versions): errors.append('Current model version does not match version history')
        return {'ok':not errors,'documents':len(documents),'evidence_blocks':len(evidence),'versions':len(versions),'errors':errors}
    finally: db.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Verify CHP workspace originals, evidence, references and version hashes')
    parser.add_argument('--data',required=True,help='Workspace folder containing plant.sqlite3, originals and renders')
    args=parser.parse_args()
    try: result=verify(args.data)
    except (OSError,sqlite3.Error,ValueError) as exc: result={'ok':False,'errors':[str(exc)]}
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['ok'] else 1)
