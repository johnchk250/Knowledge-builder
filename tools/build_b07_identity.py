"""Reconcile numbered ship-unloader records from the numbered jetty layout."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/plant-enrichment/B07/identity-175158'

def main():
    m=json.loads((ROOT/'output/plant-enrichment/B06/accepted-v637.json').read_text(encoding='utf8'))['model'];assert m['version']==637
    pairs=[('ent_6ce9a6eadc884f239d2e','ent_1a57e15407c145a19284'),('ent_63f51ca2fe4d40508384','ent_f319b7a72a2e4c85a617'),('ent_f76d833417f8463d8647','ent_9b33c14cee7f4d749335')]
    evs=json.loads((ROOT/'output/plant-enrichment/B07/review/doc_ccdd8ca4dbaa45898d6c-evidence.json').read_text(encoding='utf8'))
    ops=[]
    for n,(old,target) in enumerate(pairs,1):
        ev='ev_7ae3cf3cf1914c71a2e8' if n==3 else 'ev_7cac7848f2b54f388772'
        proof=dict(origin='explicit',confidence=.98,evidence=[dict(evidence_id=ev,quote='',region=[.04,.05,.97,.97])])
        reason=f'175158 Rev3 jetty layout explicitly labels Ship Unloader (SUL-{n}) in the three-machine plan, and the matching section names Ship Unloader {n if n==3 else "1 & 2"}. Notes give SUL1/2 toEAC1A/1B; SUL3 toEAC1A/1B andLS-EAC1. This directly bridges numbered ship-unloader and SUL terminology within one source, beyond suffix matching. Numbered175002 location and GA175155 Type1/Type2 arrangement cross-checked; three machines, not six.'
        ops.append(dict(op='merge',source=old,target=target,reason=reason,**proof))
        for a in m['assertions']:
            if a['canonical_subject']==target and a['predicate']=='source_gap' and not a['retirement'] and 'B00 identity decision' in str(a['value']):
                ops.append(dict(op='retire',assertion_id=a['id'],reason='Available175158 original jetty plan and numbered sections now establish the identity mapping described here. Historical gap retained in retirement history.',**proof))
        ops.append(dict(op='assert',subject=target,predicate='equipment_role',value=f'Numbered Ship Unloader-{n} and vendor SUL-{n} are one jetty machine. '+('Coal discharge can feed EAC-1A or EAC-1B.' if n<3 else 'Dual coal/limestone machine; source shows EAC-1A/EAC-1B coal outlets and separate LS-EAC-1 limestone outlet; no coal-to-limestone crossover is inferred.'),context=dict(kind='specification',basis='175158 Rev3,27-Jul-2020; FIO14-Sep-2020. Plan labels and separate numbered sections; tentative positions are not as-built coordinates.'),**proof))
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'accepted/commit-log.json').exists();(OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id='doc_ccdd8ca4dbaa45898d6c',baseline_version=637,baseline_model='output/plant-enrichment/B07/identity-175158/baseline-model.json',expected_new_components=0,visual_ids=['ev_7cac7848f2b54f388772','ev_7ae3cf3cf1914c71a2e8'],body=dict(summary='B07 reconcile three numbered unloaders with SUL identities using explicit jetty plan/section naming',operations=ops,intake_assessment=dict(route='mixed',purpose='Remove duplicate identity candidates without losing vendor facts or topology',questions=['Does the jetty layout explicitly connect SUL terminology to numbered ship unloaders and their distinct outlets?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Original pp3-4 plan/sections visually reviewed, p5 shutdown configuration checked; pp1-2 review text read. Remaining shutdown/travel configuration sheets pp6-11 inventoried and deferred: no surveyed travel limit, parked position or installed operating state asserted.','175155 main GA pp8-12 and DBR175154 pp2-3 independently compared for type applicability. Existing shuttle Type2-caption discrepancy and DBR limestone-only versus GA dual-duty basis remain intact. Generic vendor family records are not extra installed machines and are not merged.'])))
    (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
