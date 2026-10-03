"""Read-only HTTP checks for representative exact B36 evidence and immutable originals."""
import hashlib,io,json,sys,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]/'output/plant-enrichment/B36'
claims=json.loads((BASE/'claims.json').read_text(encoding='utf-8'))
sources=json.loads((BASE/'sources.json').read_text(encoding='utf-8'))
checks=[]
for subject,predicate in [('EBA-18A Drive assembly Main motor','motor_rated_power'),('EBA-18B Drive assembly Main motor','motor_rated_power'),('EBA-18A Drive assembly Scoop coupling PST-570 Oil circulation pump Motor','motor_rated_power'),('EBA-18A Drive assembly Scoop coupling PST-570 TS2','trip_threshold'),('EBA-18B Drive assembly Gearbox B3-500','gearbox_thermal_power_rating'),('EBA-18A Belt and mechanical assemblies Belt protection devices PCS','quantity'),('QB-3 Tandem probe','belt_speed'),('EAT-4 Four-idler weighbridge Load cells','quantity'),('FG-18 Shaft bearings and housings','assembly_arrangement'),('UEF-13 Local DFDS AP-13 Nozzle group','quantity'),('UEF-13 Sump Pumps SP-2A/2B SP-2A Motor','motor_rated_power')]:
 matches=[c for c in claims if c['subject_label']==subject and c['predicate']==predicate]
 if not matches:
  # Strictly identify the known protection group label variation in the accepted graph.
  matches=[c for c in claims if subject.endswith('devices PCS') and c['subject_label']=='EBA-18A Belt protection devices PCS' and c['predicate']==predicate]
 assert matches,(subject,predicate)
 c=matches[0];s=c['source_supports'][0]
 checks.append({'subject':c['subject_label'],'predicate':predicate,'url':s['readable_detail_url'],'kind':'detail'})
for did in ['doc_52e18b65d3b845fdb786','doc_9258f527621741938b79']:
 s=next(s for s in sources if s['document_id']==did)
 checks.append({'subject':s['name'],'url':'http://127.0.0.1:8775/api/original/'+did,'kind':'original','sha256':s['sha256']})
def test(c):
 assert c['url'],c
 with urllib.request.urlopen(c['url'],timeout=90) as r:data=r.read();status=r.status;media=r.headers.get('Content-Type','')
 result={**c,'status':status,'content_type':media,'bytes':len(data)}
 if c['kind']=='detail':
  im=Image.open(io.BytesIO(data));im.verify();result['dimensions']=Image.open(io.BytesIO(data)).size;assert media.startswith('image/png') and min(result['dimensions'])>100
 else:assert hashlib.sha256(data).hexdigest()==c['sha256']
 return result
with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(test,checks))
(BASE/'evidence-api-checks.json').write_text(json.dumps({'ok':True,'checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'ok':True,'exact_details':sum(c['kind']=='detail' for c in checks),'original_hashes':sum(c['kind']=='original' for c in checks)}))
