"""Complete conveyor2 discharge branches using the reviewed175001 topology."""
import json
import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/plant-enrichment/B06/routes-175001'
DOC='doc_4f2cd96c3b1e413ea4b5'
EV='ev_0b5f0558fa714697879e'

def main():
    m=json.loads((ROOT/'output/plant-enrichment/B06/ga-175012/accepted/model.json').read_text(encoding='utf8'));assert m['version']==636
    ids={e['label']:e['id'] for e in m['entities']}
    proof=dict(origin='explicit',confidence=.99,evidence=[dict(evidence_id=EV,quote='',region=[.31,.06,.50,.18])])
    ops=[]
    for lane, gates in [('A',[1,2]),('B',[3,4])]:
        for n in gates:
            ops.append(dict(op='assert',subject=ids[f'EAC-2{lane} screening discharge chute'],predicate='material_flow_to',object_entity=ids[f'KB-RG-{n}'],context=dict(kind='connection',network='material',verification='documented',basis='Attached175001Rev8 coal-flow drawing,p55; original lane split visually traced.',condition=f'Selected primary-screen branch via KB-RG-{n}/KB-RPG-{n} to EBD-{n}; design route, not current operating selection.'),**proof))
    for id in ['fact_b6abaaf2ed93451bb3f7','fact_aaaa198ecc9d4b7e825d','fact_551f69a5732d442c9559','fact_dcf7107d47574f3fb948']:
        ops.append(dict(op='retire',assertion_id=id,reason='175001p55 shows separate2A through screens1/2 to3A and2B through screens3/4 to3B. Aggregate-building material routing creates false cross-lane reachability; exact existing gate/screen routes and building location remain.',**proof))
    with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as c:
        evs=[r[0] for r in c.execute('select id from evidence where document_id=?',(DOC,))]
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'accepted/commit-log.json').exists()
    (OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=DOC,baseline_version=636,baseline_model='output/plant-enrichment/B06/routes-175001/baseline-model.json',expected_new_components=0,visual_ids=[EV],body=dict(summary='B06 screening chute-to-gate paths and removal of false aggregate-building crossovers',operations=ops,intake_assessment=dict(route='mixed',purpose='Keep exact A/B screening routes and reuse existing gates/screens',questions=['Which screen inlet gates belong to each conveyor2 discharge?'],reviewed_evidence_ids=evs,gaps=['Document previously reviewed in B00/B01 and accepted route work; this bounded review revisits originalp55 only. Other plant-wide control pages retain prior claims and are assigned to their consuming batches, with detailed controls deferred to Pass B.','GA175012 repeated gate callouts are qualified separately.175001 unequivocally maps2A toRG1/2 and2B toRG3/4. Four existing aggregate building edges retired to remove false crossovers; all exact gate/RPG/screen/undersize/reject edges preserved.'])))
    (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print('Prepared4 chute outlets and4 explicit aggregate-edge retirements')

if __name__=='__main__':main()
