"""Reviewed B01 DFDS pump identity/revision packages, guarded from v599."""
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

BASE = ROOT / 'output/plant-enrichment/B01/pump-identities'
REDIRECTS = {'ent_5cbc1adfdd174936bbaf': 'ent_975edb9acc07451cbc62',
             'ent_5f410f0406c74631a0d1': 'ent_8a35251f220d4c9287d2'}


def packages(snap):
    def fact(subject, predicate, value, eid, region, basis):
        return {'op': 'assert', 'subject': subject, 'predicate': predicate, 'value': value,
                'context': {'kind': 'specification', 'basis': basis}, **support(eid, region)}
    def package(doc, title, ops, visual, scope):
        return {'doc': doc, 'visual': visual, 'body': {'summary': title, 'operations': ops,
                'intake_assessment': {'route': 'mixed', 'purpose': title,
                'questions': ['Which individual pump identity and revision basis does the source establish?'],
                'reviewed_evidence_ids': [e['id'] for e in snap['evidence'] if e['document_id'] == doc],
                'gaps': [scope, 'Field/as-built identity and commissioned duty are not established. '
                         'B02 owns detailed pump assemblies; grouped placeholders remain B01 review.']}}}
    eid = 'ev_0949a3ac5f0240069c4c'
    region = [.30, .83, .425, .95]
    ops = []
    for lane, (old, new) in zip('AB', REDIRECTS.items()):
        ops.append({'op': 'merge', 'source': old, 'target': new,
                    'reason': f'House-1 GA175050 Rev5 reference table calls the DFDS system pumps '
                    f'DFDSP-1A/1B against P&ID175089 and the same two duty/standby pumps '
                    f'DFDS-1A/1B against vendor GA175093. Plan locates DFDSP-1A/B in UGA1. '
                    f'Vendor175093 pp1-5 and P&ID175089 p1 cross-checked. Lane {lane} '
                    'identity is the same; retain earlier design and later vendor values with qualifications.',
                    **{**support(eid, region), 'origin': 'inferred', 'confidence': .96}})
        ops.append(fact(new, 'operating_requirement',
                    f'House-1 GA175050 Rev5 identifies the DFDS pump pair as DFDSP-1A/1B '
                    f'in the system/P&ID reference and DFDS-1A/1B in the pump/vendor reference. '
                    f'DFDS-1{lane} and DFDSP-1{lane} name the same numbered design pump; '
                    'different source revisions do not establish additional installed pumps.',
                    eid, region, 'Reference table and pump-house arrangement cross-checked. '
                    'Identity reconciliation does not resolve differences in rated duty or pump orientation.'))
    result = [package('doc_af4f437e54f143af9f62', 'B01: reconcile DFDS-1A/B with DFDSP-1A/B from the house reference table',
                      ops, [eid], 'Single original GA sheet reviewed for title/revision, key plan, '
                      'pump tags and reference table; all six blocks inventoried. Dense civil/load data remains separate work.')]
    ops = []
    for n, ids, e, reg, text in [
        (1, list(REDIRECTS.values()), 'ev_593f764437c7464fba4c', [.07,.165,.955,.456],
         'DFDS-1A/1B: KSB Movitec VCF6/14B vertical multistage, nominal 4.0 m3/h, 120 m head, recommended motor 3.0 kW'),
        (2, ['ent_afdfc43f0f1148d0b555','ent_eca52aa5ec3d4d3fa153'], 'ev_e2ec44123b7b4ad8a762', [.07,.174,.95,.464],
         'DFDS-2A/2B: KSB Movitec VCF6/16B vertical multistage, nominal 5.0 m3/h, 130 m head, recommended motor 4.0 kW')]:
        for pump in ids:
            op = fact(pump, 'source_discrepancy',
                      f'Vendor pump package 175093 Rev4, approved 30-Dec-2019, PDF p{2 if n==1 else 6} '
                      f'datasheet Rev02 dated 25-Sep-2019 states {text}. '
                      'The cover records Higher Capacity Pump Considered at Rev3 (04-Nov-2019). '
                      f'Retain the earlier DFDSP-{n}A/B design basis ('+
                      ('2.2 m3/h, 70 mwc' if n==1 else '1.9 m3/h, 120 mwc')+
                      ') separately. This is design/vendor revision context, not proof of field duty or extra installed pumps.',
                      e,reg,'All nine vendor sheets inspected for unit applicability, dates and revision context. '
                      'Performance curves distinguish requested duty from calculated curve output; neither is measured site operation.')
            op['evidence'].append({'evidence_id':'ev_a5cde5658f1f4d90a14f','quote':'','region':[.087,.19,.934,.3]})
            ops.append(op)
    result.append(package('doc_b5188c19e5b942cfa976', 'B01: preserve earlier design and later vendor pump duty bases',
                          ops, ['ev_a5cde5658f1f4d90a14f','ev_593f764437c7464fba4c','ev_e2ec44123b7b4ad8a762'],
                          'All nine original pages visually reviewed. Datasheets, curve requested/calculated '
                          'values, GA and 14/16-stage sections kept distinct. Detailed BOM/drive data is available B02 work.'))
    result.append(package('doc_d0cb76dd3ab3478295db', 'B01: retain mixed-number House-2 pump reference discrepancy',
        [fact('ent_36135b45a07c4d03bf06','source_discrepancy',
              'House-2 GA175051 Rev5 p1 reference table has DFDS SYSTEM DFDSP-2A/2B, '
              'but its pump/vendor row reads DFDS-2A/1B against drawing175093. '
              'The local arrangement labels DFDSP-2A and DFDSP-2B. Preserve the mixed-number '
              'reference-row discrepancy; it does not authorize moving or merging System-1 pump B into House-2.',
              'ev_41d5812e05f34b2f9b70',[.84,.59,.989,.795],
              'Original p1 reference table compared with the same sheet arrangement and p2. '
              'No inferred cross-house equipment duplication or reassignment.')],
        ['ev_41d5812e05f34b2f9b70'], 'Both house GA sheets visually reviewed for identity/arrangement; '
        'remaining civil/load and other system details retain their owning batch scope.'))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    snap=json.loads((ROOT/'output/plant-enrichment/B01/accepted-snapshot.json').read_text(encoding='utf-8'))
    pkgs=packages(snap);plant=ROOT/'data/plant';out=BASE/('accepted' if args.apply else 'rehearsal');out.mkdir(parents=True,exist_ok=True)
    assert not (out/'result.json').exists(),'Already complete; inspect checkpoint.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN');before=Store.__new__(Store).model(db=db)
        assert before['version']==599 and before==snap['model'],'Live model changed; review again.'
        if not args.apply:
            backup=BASE/'backup-v599';backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3',backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:db.backup(dst)
            copied=[]
            for d in snap['documents']:
                if d['id'] not in [p['doc'] for p in pkgs]:continue
                assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()==d['sha256']
                for rel in set([Path('originals')/d['sha256']]+[Path('renders')/e['image'] for e in snap['evidence'] if e['document_id']==d['id'] and e['image']]):
                    dest=backup/rel;dest.parent.mkdir(exist_ok=True);shutil.copy2(plant/rel,dest);copied.append(str(rel))
            save(backup/'manifest.json',{'version':599,'copied_files':copied,'scope':'Full consistent SQLite database plus reviewed originals/renders; other source assets unchanged in data/plant.'})
    if args.apply:
        assert pkgs==json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf-8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))['ok']
    save(out/'packages.json',pkgs);store=Store(plant if args.apply else out);logs=[]
    for i,p in enumerate(pkgs):
        body=p['body'];v=599+i
        report=validate(store,{k:body[k] for k in ['summary','operations']},p['doc'],v,visual_ids=p['visual']);assert not report['errors'],report
        staged=stage(store,p['doc'],body,visual_ids=p['visual'],analysis_dir=str(out),expected_version=v)
        result=commit(store,staged['proposal_id']);logs.append({'proposal_id':staged['proposal_id'],'document_id':p['doc'],'warnings':report['warnings'],**result});save(out/'commit-log.json',logs)
    after=store.model();save(out/'model.json',after);assert after['version']==602
    facts={a['id']:a for a in after['assertions']}
    for a in before['assertions']:
        assert preserved(a)==preserved(facts[a['id']]),a['id']
        for field in ['canonical_subject','canonical_object']:assert facts[a['id']][field]==REDIRECTS.get(a[field],a[field])
    assert before['aliases']==after['aliases'] and len(before['entities'])==len(after['entities'])
    assert len(after['merges'])==len(before['merges'])+2
    added=[a for a in after['assertions'] if a['created_version']>599];assert len(added)==7
    save(out/'result.json',{'ok':True,'version':602,'proposals':[x['proposal_id'] for x in logs],'redirects':REDIRECTS,'added_claims':added,'preserved_assertions':len(before['assertions'])})
    print(json.dumps({'ok':True,'version':602,'mode':out.name,'proposals':[x['proposal_id'] for x in logs]}))


if __name__=='__main__':main()
