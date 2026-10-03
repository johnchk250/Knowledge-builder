"""Independent B04 routes and B05 pilot boundary checks against accepted v634."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 m=json.loads((ROOT/'output/plant-enrichment/B04/model-v634.json').read_text(encoding='utf8'))
 labels={e['label']:e['canonical_id'] for e in m['entities']}
 def reach(s,t,network='utility'):
  adj={}
  for a in m['assertions']:
   if not a['retirement'] and not a['suppressed'] and a.get('context',{}).get('network')==network:adj.setdefault(a['canonical_subject'],set()).add(a['canonical_object'])
  seen=set();q=[s]
  while q:
   x=q.pop()
   if x==t:return True
   if x not in seen:seen.add(x);q.extend(adj.get(x,[]))
  return False
 checks={};pond='ent_5ac31846c95842f8955c'
 for src in ['UEF-1','UEF-3','UEF-8','UEF-9','UEF-10','UEF-11','UEF-12','UEE-1','UEE-2','UEE-3 Drainage sump and pumps','EAE-2','EAE-3','EAE-4']:
  checks[src+' -> pond']=reach(labels[src],pond)
 for pump in ['ent_707d01d4e46f4956b99e','ent_105b5e78f0ad4b7093ff']:
  checks[pump+' -> UEE2 sump']=reach(pump,labels['CHP Intermediate sump near UEE-2'])
  checks[pump+' excludes UEF1 sump']=not reach(pump,'ent_be0bcbae381345dbbbba')
 checks['pond -> SPDS compartment']=reach(pond,'ent_36777dcc88b24427abb1')
 checks['pond excludes potable compartment']=not reach(pond,'ent_73ec6a7ce80147b0b5be')
 for src,dst,name in [('ent_081c34835a684544a6d0','ent_21a02d1f40f04686a18a','DFDS air to TP1'),('ent_975edb9acc07451cbc62','ent_3e6f0c75149b49cdbce2','DFDS water to TP1')]:checks[name]=reach(src,dst)
 assert all(checks.values()),checks
 out=ROOT/'output/plant-enrichment/B04/routes-v634.json';out.write_text(json.dumps(dict(ok=True,version=634,checks=checks),indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(ok=True,checks=len(checks))))

if __name__=='__main__':main()
