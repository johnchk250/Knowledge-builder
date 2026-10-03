"""One-time, source-reviewed TP13 legend correction at v592; rehearse by default."""
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import commit, validate

BASE = ROOT / 'output/plant-enrichment/B36-corrections'
DOC = 'doc_4f2cd96c3b1e413ea4b5'
EVIDENCE = 'ev_0b5f0558fa714697879e'
OLD = 'fact_85501cdfd0614f6187db'
TP = 'ent_1d5055a3fcb74ba6a593'
VALUE = 'Coal-flow service badges: GK drinking water, PC service water and HDD dry-fog dust suppression. Badges do not define installed piping routes.'


def check_change(before, after):
    assert after['version'] == before['version'] + 1 == 593
    assert before['entities'] == after['entities']
    old = {f['id']: f for f in before['assertions']}
    new = {f['id']: f for f in after['assertions']}
    for fid, fact in old.items():
        if fid == OLD:
            assert fact['retirement'] is None and new[fid]['retirement']
            assert {k:v for k,v in fact.items() if k != 'retirement'} == {k:v for k,v in new[fid].items() if k != 'retirement'}
        else:
            assert fact == new[fid], fid
    added = [f for fid, f in new.items() if fid not in old]
    assert len(added) == 1 and added[0]['value'] == VALUE
    assert added[0]['canonical_subject'] == TP
    return added[0]['id']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    BASE.mkdir(parents=True, exist_ok=True)
    plant = ROOT / 'data/plant'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as ro:
        ro.row_factory = sqlite3.Row
        ro.execute('BEGIN')
        before = Store.__new__(Store).model(db=ro)
        assert before['version'] == 592, 'Re-review current state; this is not a replayable migration.'
        source = dict(ro.execute('SELECT * FROM documents WHERE id=?', (DOC,)).fetchone())
        inventory = [dict(r) for r in ro.execute('SELECT id,page,locator FROM evidence WHERE document_id=? ORDER BY page,id', (DOC,))]
        assert hashlib.sha256((plant/'originals'/source['sha256']).read_bytes()).hexdigest() == source['sha256']
        assert any(f['id'] == OLD and f['retirement'] is None and f['canonical_subject'] == TP for f in before['assertions'])
        out = BASE / ('accepted' if args.apply else 'rehearsal')
        out.mkdir(exist_ok=True)
        assert not (out/'result.json').exists(), 'Already completed; inspect result instead of replaying.'
        if not (BASE/'backup-v592.sqlite3').exists():
            with sqlite3.connect(BASE/'backup-v592.sqlite3') as dst:
                ro.backup(dst)
        if not args.apply:
            with sqlite3.connect(out/'plant.sqlite3') as dst:
                ro.backup(dst)
    provenance = {'origin':'explicit', 'confidence':.98,
                  'evidence':[{'evidence_id':EVIDENCE, 'quote':'', 'region':[.048,.715,.245,.76]}]}
    body = {'summary':'Correct TP13 GK/PC service legend interpretation', 'operations':[
        {'op':'retire','assertion_id':OLD,'reason':'Original coal-flow legend identifies GK drinking water and PC service water, not hoist and ventilation.',**provenance},
        {'op':'assert','subject':TP,'predicate':'operating_requirement','value':VALUE,
         'context':{'kind':'specification','basis':'Coal flow diagram 175001 Rev8, control write-up PDF p55; original legend rows PC/GK/HDD visually reviewed. Corrects interpretation, not plant configuration.'},**provenance}],
        'intake_assessment':{'route':'mixed','purpose':'Correct one TP13 service-badge interpretation; preserve all other accepted records.',
            'questions':['What do GK, PC and HDD mean in the source legend?'],
            'gaps':['Only PDF p55 legend is semantically re-reviewed here. Other blocks were inspected as the document/page inventory; this is not a new full-document extraction. Badges alone do not establish piping, hoists or ventilation.'],
            'reviewed_evidence_ids':[e['id'] for e in inventory]}}
    if args.apply:
        rehearsal = json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf-8'))
        assert rehearsal['ok'] and rehearsal['base_version'] == 592
        assert body == json.loads((BASE/'rehearsal/proposal.json').read_text(encoding='utf-8'))
    store = Store(plant if args.apply else out)
    report = validate(store, {k:body[k] for k in ['summary','operations']}, DOC, 592, visual_ids=[EVIDENCE])
    assert not report['errors'], report
    (out/'proposal.json').write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/'source-inventory.json').write_text(json.dumps({'document_id':DOC,'sha256':source['sha256'],'blocks':inventory,'semantic_review':[{'evidence_id':EVIDENCE,'page':55,'region':[.048,.715,.245,.76]}]},indent=2),encoding='utf-8')
    pending = stage(store,DOC,body,visual_ids=[EVIDENCE],analysis_dir=str(out),expected_version=592)
    accepted = commit(store,pending['proposal_id'])
    after = store.model()
    added_id = check_change(before,after)
    (out/'model.json').write_text(json.dumps(after,ensure_ascii=False),encoding='utf-8')
    result = {'ok':True,'base_version':592,'version':593,'proposal_id':pending['proposal_id'],'retired_assertion':OLD,'replacement_assertion':added_id,'warnings':report['warnings'],'commit':accepted,'unchanged_entities':len(before['entities']),'other_assertions_preserved':len(before['assertions'])-1}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
