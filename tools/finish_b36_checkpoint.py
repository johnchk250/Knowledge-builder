"""Record completion after canonical and actual-browser verification; read-only DB."""
import json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/plant-enrichment/B36'
def read(p):return json.loads((BASE/p).read_text(encoding='utf-8'))
def dump(p,x):(BASE/p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 sys.stdout.reconfigure(encoding='utf-8')
 audit=read('accepted/semantic-audit.json');assert audit['ok'] and audit['version']==592
 for p in ['accepted/crusher-regression.json','accepted/silo-regression.json','integrity.json','rehearsal-comparison.json','evidence-api-checks.json','browser-journeys.json']:assert read(p)['ok'],p
 assert read('browser-journeys.json')['version']==592
 commits=[json.loads(l) for l in (BASE/'accepted/commits.jsonl').read_text(encoding='utf-8').splitlines()];assert len(commits)==34 and commits[-1]['result_version']==592
 with sqlite3.connect((ROOT/'data/plant/plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
  versions={v:{'proposal_id':pid,'hash':h} for v,pid,h in db.execute('select version,proposal_id,hash from versions where version>558 order by version')}
 assert len(versions)==34
 proposals=[{'source_name':c['name'],'document_id':c['document_id'],'base_version':c['base_version'],'version':c['result_version'],**versions[c['result_version']],'proposal_file':'accepted/'+c['name']+'.json'} for c in commits]
 progress={'batch_id':'B36','status':'complete_with_gaps','baseline_version':558,'current_version':592,'accepted_proposals':proposals,'target_status':{t:'implemented; source-qualified gaps in coverage.csv' for t in ['EBA-18A','EBA-18B','UEF-13','FG-17','FG-18','QB-3','QB-4','EAT-3','EAT-4']},'source_dispositions_file':'sources.json','identity_ledger_file':'identities.json','boundary_ledger_file':'boundaries.json','claim_ledger_file':'claims.json','coverage_file':'coverage.csv','open_findings_file':'uncertainties.json','verification':['accepted/semantic-audit.json','accepted/crusher-regression.json','accepted/silo-regression.json','integrity.json','rehearsal-comparison.json','evidence-api-checks.json','test-results.json','browser-journeys.json','verification.md'],'next_action':'B37 separately: read sampler GA doc_98b9805fdd334190a93f, TP13 GA doc_a9043e95d82c40f399ec pp1/3 and controls pp22-23/53-55; reconcile EAU-2/sampling/elevator/SNC-2 identities and sample/bias/reject returns before expanding access.'}
 dump('progress.json',progress)
 table='\n'.join('| '+str(p['version'])+' | '+p['source_name']+' | '+p['proposal_id']+' |' for p in proposals)
 checkpoint="""# B36 continuation checkpoint

Status: **complete_with_gaps**. Accepted 1 October 2026, **v558 → v592**. Supported scope is implemented in the canonical database and visual explorer. This does not establish field commissioning. B37 remains separate and not_started.

## Scope and durable state

EBA-18A/B, UEF-13, FG-17/18, QB-3/4, EAT-3/4; model-specific drives, oil auxiliaries, belt/pulley/bearing/take-up/scrapers/protection, measurements, gates, local DFDS/water/drainage and relevant shared B02/B04 boundaries.

Consistent baseline `baseline.json` / `backup-v558.sqlite3`; fresh canonical `final-snapshot.json` / `accepted/model.json`. Source-specific accepted proposal bodies and version hashes are in `accepted/commits.jsonl`; proposal IDs are below and in `progress.json`. `rehearsal-final/` is proven semantically equivalent by `rehearsal-comparison.json`. Earlier `rehearsal/` failed control quote validation and is investigation history only. **Do not replay guarded enrichment scripts against v592.**

362 new descriptive component identities and 1,756 assertions are individually recorded in `identities.json` / `claims.json`; all 14,098 baseline assertions and 2,326 identities are unchanged. Reused canonical identities include 18A/B, TP13, both gates/weighers/detectors, SP2 group, FAS/PRU11–16, PS03, DFDSSystem2, DCS and shared water systems. Incoming conveyor drives remain conveyor-owned and TP-located; common supplies remain external. Crusher interfaces and existing sampling assertions are preserved.

## Review and uncertainty

`sources.json` lists 34 dispositions/29 used documents, hashes, revisions, applicability, visually inspected pages, exact semantic regions/quote pages and inventory-only triage. Render existence is not claimed as visual review. `boundaries.json` resolves local supply/consumer paths without closing global B02/B04. `coverage.csv` resolves 90 target/dimension cells with source support or specific remaining evidence. `uncertainties.json` retains 67 added qualifications.

Nominal 28.4/exact 29.2 is resolved as two ratio definitions. 633kW@50°C versus 905kW thermal selection, EBTM/EBTF rating, 160kgf-m calculation brake setting, idler/nonmagnetic counts, shaft and profile/skirt/deflector inputs, seal-plate text, detector speed/IO/sensitivity, CBS polarity/gate timer modes, TP13FAS/PRU destination labels and 5 versus 10m3 sump revision remain qualified. Installed feeder/loop/address/calibration/maintenance/isolation records are not available in the reviewed selection. Resolution evidence is attached to each affected claim.

## Verification

Final semantic/preservation audits, crusher and silo regression audits, all-original/evidence/version-chain integrity, 11 high-resolution detail endpoints plus 2 original hashes, 36 Node tests and scene syntax pass. Python discovery executed 73 passing tests but has one unrelated import error for missing `triple_model_session`; full Python discovery is not claimed clean. Actual v592 browser journeys/screenshots and G1–G8 results are in `browser-journeys.json` / `verification.md`.

## Accepted proposals

| Version | Source package | Proposal ID |
|---|---|---|
"""+table+"""

## Next concrete action

Start B37 separately. Inspect sampling GA `doc_98b9805fdd334190a93f`; TP13GA175047 `doc_a9043e95d82c40f399ec` pp1/3; controls pp22–23 and53–55. Reconcile EAU-2/sampling and generic TP13elevator versus SNC-2 identities before creating anything. Trace primary sampler, feeder/reverse bias, small sample crusher, secondary sampler, collector, reject conveyor and open/closed slide-gate returns to19A/B. Preserve B36 main coal and local shared-service boundaries. Hoists/elevator/access expansion belongs to this separate run.
"""
 (BASE/'checkpoint.md').write_text(checkpoint,encoding='utf-8')
 p=ROOT/'docs/plant-handoff/batches.json';d=json.loads(p.read_text(encoding='utf-8'))
 d['progress_note']+=' B36 accepted at v592 on 2026-10-01 with documented source gaps; B37 remains separate. Relevant B02/B04 local boundaries resolved, global batches remain open.'
 b=next(b for b in d['batches'] if b['id']=='B36');b.update(status='complete_with_gaps',accepted_version=592,completed_date='2026-10-01',report='B36_CONVEYOR18_TP13_REPORT.md',dependency_resolution='Relevant B02 water/drainage and B04 DFDS local boundaries resolved/qualified in B36/boundaries.json; global B02/B04 remain unfinished. B37 sampling/access excluded.')
 assert next(b for b in d['batches'] if b['id']=='B37')['status']=='not_started'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 p=ROOT/'docs/plant-handoff/CONTINUATION_GUIDE.md';s=p.read_text(encoding='utf-8').replace('live database at **v558**','live database at **v592**')
 row='| Crusher house, 17A/B, screens, crushers, feeders and local services | B32–B35, v527 → v558 | [Crusher pilot](../../CRUSHER_HOUSE_PILOT_REPORT.md) |'
 s=s.replace(row,row+'\n| Conveyor18A/B and TP13 drives, measurements, gates and local services | B36, v558 → v592 | [B36 report](../../B36_CONVEYOR18_TP13_REPORT.md) |')
 s=s.replace('checkpoints exist for B30–B35','checkpoints exist for B30–B36').replace('B30/B31 and B32–B35 must not be recreated from old target cards.','B30/B31, B32–B35 and B36 must not be recreated from old target cards.')
 s=s.replace('the candidate is **B36: EBA-18A/B and UEF-13**, followed separately by B37 sampling/access. Inspect its outstanding B02/B04 service dependencies and the completed crusher interfaces first.','B36 is accepted at v592. The next separately scoped candidate is **B37: sampling2 and TP13 access**. Read the B36 report/checkpoint and preserve its qualified B02/B04 service boundaries and completed crusher interfaces.')
 p.write_text(s,encoding='utf-8')
 p=ROOT/'docs/plant-handoff/READY_TO_PASTE_PROMPT.md';s=p.read_text(encoding='utf-8').replace('Target: B36 — EBA-18A/B and UEF-13; leave B37 sampling/access for a separate run.','Target: B37 — sampling2 and TP13 access; preserve accepted B36 conveyor/service interfaces.').replace('v558 was the latest verified state','v592 was the latest verified state').replace('crusher-house B32-B35 pilots.','crusher-house B32-B35 and conveyor18/TP13 B36 implementations.');p.write_text(s,encoding='utf-8')
 p=ROOT/'PLANT_MODEL_IMPLEMENTATION_HANDOFF.md';s=p.read_text(encoding='utf-8').replace('live database was checked at v558.','live database was checked at v592.')
 point='The next agent should **extend the existing visual model one connected section at a time**'
 s=s.replace(point,'**B36 checkpoint, 1 October 2026:** EBA-18A/B, UEF-13, FG17/18, QB3/4, EAT3/4 and local dust/water/drainage are implemented with explicit source gaps at **v592**. Read [the B36 report](B36_CONVEYOR18_TP13_REPORT.md) and `output/plant-enrichment/B36/checkpoint.md`. All v558 crusher and sampling assertions are preserved. Relevant B02/B04 boundaries are locally resolved/qualified; global services remain open. B37 sampling/access remains a separate run.\n\n'+point)
 p.write_text(s,encoding='utf-8')
 p=ROOT/'B36_CONVEYOR18_TP13_REPORT.md';s=p.read_text(encoding='utf-8').replace('Status: **complete_with_gaps**, subject to the recorded final verification gates.','Status: **complete_with_gaps**; final verification gates are recorded.');p.write_text(s,encoding='utf-8')
 print(json.dumps({'batch':'B36','status':'complete_with_gaps','version':592,'proposals':len(proposals)}))
if __name__=='__main__':main()
