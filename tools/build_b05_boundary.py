"""Retire aggregate-building topology that creates false TP1 crossovers."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/plant-enrichment/B05/boundary-175033'

def main():
 m=json.loads((ROOT/'output/plant-enrichment/B04/model-v634.json').read_text(encoding='utf8'));assert m['version']==634
 proof=dict(origin='explicit',confidence=.99,evidence=[dict(evidence_id='ev_d7d009e07565467e8938',quote='',region=[.33,.03,.79,.255])])
 ids=['fact_124562f56d764560bebe','fact_776415bdc56546ffaa3e','fact_2603f4cc0765482f9d0a','fact_fff27dc6f3654329ab2f']
 ops=[dict(op='retire',assertion_id=id,reason='175033 Rev6 original views C-C/D-D show separate1B-to2B and1A-to2A chutes. Routing through aggregate UEF1 creates unsupported cross-stream reachability. Accepted direct lane and individual chute edges remain; building membership/location remains.',**proof) for id in ids]
 ops.append(dict(op='assert',subject='ent_108b99f6c64844df8cf8',predicate='assembly_arrangement',value='Separate EAC-1A to EAC-2A and EAC-1B to EAC-2B transfer chutes at UEF-1. The building is a location for both lanes, not a common mixing node or crossover selector.',context=dict(kind='specification',basis='175033 Rev6 original p1 views C-C/D-D,01-Oct-2019; approved18-Oct-2019. Enlarged display contrast used for faint lines; immutable source unchanged.'),**proof))
 OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'accepted/commit-log.json').exists();(OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
 pkg=dict(document_id='doc_71a0d8fc66304e93b9c1',baseline_version=634,baseline_model='output/plant-enrichment/B05/boundary-175033/baseline-model.json',expected_new_components=0,visual_ids=['ev_d7d009e07565467e8938'],body=dict(summary='B05 boundary recheck: remove four aggregate TP1 flow edges that falsely cross-connect A/B lanes',operations=ops,intake_assessment=dict(route='mixed',purpose='Preserve exact TP1 lane topology alongside completed water/drainage boundaries',questions=['Does TP1 connect1A to2A and1B to2B without a crossover?'],reviewed_evidence_ids=['ev_d7d009e07565467e8938','ev_469e294f8e5b40359f6f'],gaps=['Original p1 full drawing and enlarged C-C/D-D reviewed. P2 prior review/tank-capacity dispute is retained from B00; no new detail extraction. Hoist/access/tank follow-ups stay DQ-B05-001.','No new asset or pilot migration replay. All lane/chute connections, membership, ratings and source qualifications retained.'])))
 (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print('Prepared four retirements and one boundary qualification')

if __name__=='__main__':main()
