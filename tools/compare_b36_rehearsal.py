"""Read-only comparison of final acceptance with the independently audited rehearsal."""
import collections,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'output/plant-enrichment/B36'
def semantic(folder):
 m=json.loads((BASE/folder/'model.json').read_text(encoding='utf-8'))
 es={e['id']:e['label'] for e in m['entities']}
 facts=[]
 for a in m['assertions']:
  if a['created_version']<=558:continue
  f={k:a.get(k) for k in ['predicate','value','unit','origin','confidence','context','evidence','retirement','suppressed']}
  f['subject']=es[a['canonical_subject']];f['object']=es.get(a['canonical_object'])
  facts.append(json.dumps(f,sort_keys=True,ensure_ascii=False))
 return m['version'],collections.Counter(facts),collections.Counter(e['label'] for e in m['entities'] if e['created_version']>558)
a,af,ae=semantic('accepted');r,rf,re=semantic('rehearsal-final')
assert a==r==592,(a,r)
assert af==rf,{'accepted_only':list((af-rf).items())[:3],'rehearsal_only':list((rf-af).items())[:3]}
assert ae==re
result={'ok':True,'version':a,'assertion_semantics_equal':sum(af.values()),'new_entity_labels_equal':sum(ae.values()),'comparison':'Canonical IDs/timestamps vary on newly created identities; exact subject/object labels, predicate, value, unit, origin/confidence/context, support and retirement semantics compared as multisets.'}
(BASE/'rehearsal-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
