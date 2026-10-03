"""Final reviewed B36 detail closure, after the main source intake at v588.

Uses the same guarded source-specific stage/commit path on rehearsal or canonical.
"""
import argparse,json,sys
from pathlib import Path
import enrich_b36 as b
from chp.store import Store

def details(s,out):
 x=b.batch(s,'bw','EAT3-4-physical-supports','175069 applicable1400mm10-14-4 p1 and60-12C p4; original views/notes inspected; supports are physical parts, no assumed commissioned calibration')
 for t,e in zip(b.TAGS,['EAT-3','EAT-4']):
  bridge=e+' Four-idler weighbridge';r=[.27,.10,.585,.55]
  idlers=b.child(x,bridge,'Weighing idlers','idler_group',1,r);x.a(idlers,'quantity',4,1,r,'sets',condition='W1 labels across four-idler10-14-4 bridge; conveyor GA independently gives4 machined weighing sets')
  rods=b.child(x,bridge,'Longitudinal check rods and scale frame','mechanical_component',1,r);x.rel(rods,'supports',e+' Four-idler weighbridge Load cells',1,r,condition='Weighbridge frame/check-rod arrangement; not a mechanical drive')
  test=e+' Calibration test-weight arrangement';b.child(x,test,'Weight supports and hangers','mechanical_component',1,[.26,.36,.64,.59])
  x.a(test,'assembly_arrangement','Test weights supported at the bridge arrangement shown in the applicable1400mm view. No installed test-weight mass, certified load or completed calibration is inferred.',1,[.26,.36,.64,.59])
  speed=e+' Speed sensor60-12C';tail=b.mech(t)+' Tail bend and take-up pulley group Tail pulley'
  x.rel(tail,'mechanically_drives',speed,4,[.055,.72,.52,.94],network='mechanical',condition='Sensor stub shaft driven by tail-pulley shaft; restraint arm/spring prevents sensor-body rotation')
  for name in ['Stub shaft','Restraint arm','Retaining spring','Mechanical stop and spring mount']:b.child(x,speed,name,'mechanical_component',4,[.12,.32,.52,.70])
  x.a(speed,'operating_range','Input shaft20–200 rpm, manufacturer design limit; distinct from ZSS threshold.',4,[.055,.72,.52,.94])
  x.a(bridge,'maintenance_requirement','Scale-zone idlers aligned to the installation notes; rigid bracing, alignment of+5 to-5 idlers and keeping load-cell cables unaltered are manufacturer requirements. No current alignment certificate is established.',1,[.054,.705,.57,.928])
 x.finish(out)
 b.DOCS['coasting']='doc_0ed3cc8247ed4484ac8f'
 x=b.batch(s,'coasting','18AB-brake-calculation-basis','Coasting/deceleration calculation175008 Rev2 tablep3, explicitEBA18AB column; design calculations rather than commissioned stopping/brake settings')
 for t in b.TAGS:
  br=b.brake(t);r=[.857,.047,.905,.289]
  x.a(br,'calculation_applied_brake_torque',160,3,r,'kgf-m',condition='Applied torque assumed in calculation; not a field adjustment')
  x.a(br,'source_discrepancy','Coasting table selects EBTM600/G and gives440 maximum torque and160 applied torque; drive schedule givesEBTF600/G and495 kg-m rated torque. Rated and assumed applied torque have different meanings; model/rating disagreement still needs final brake selection and field test record.',3,r)
 x.finish(out)
 x=b.batch(s,'ga','18AB-chute-and-location-details','175028 conveyor18AB GA6 chute plate/scraper/take-up rows; keep local TP placement separate from conveyor ownership')
 for t in b.TAGS:
  chute=t+' Discharge chute interface';r=[.78,.749,.975,.8]
  x.a(chute,'component_dimension',10,6,r,'mm',condition='Hardox400 chute plate, non-impact sides');x.a(chute,'component_dimension',20,6,r,'mm',condition='Hardox400 chute plate, impact sides')
  x.a(b.mech(t)+' Internal V-plough scraper','location_description','Near the tail pulley,1 per conveyor; separate from primary/secondary discharge scrapers.',6,[.78,.69,.975,.736])
 x.finish(out)
 x=b.batch(s,'calc','18AB-calculation-selection-reconciliation','175231 Rev3 pp113 calculation pulley input basis compared with later175062 Rev4 shaft/bearing selections; cannot establish final installed shaft by calculation input alone')
 for t in b.TAGS:
  x.a(b.mech(t),'source_discrepancy','Calculation p113 lists drive-bearing diameter280mm, non-drive tail/take-up/bend160mm and snub140mm. Later selection p4/5 uses different selected shaft diameters at bearings (drive260mm, take-up220mm, tail/snub180mm). Final shaft/BOM revision and bearing-fit record are needed; catalogue bearing model is design selection only.',113,b.FULL)
 x.finish(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--expected-version',type=int,default=588);a=p.parse_args();sys.stdout.reconfigure(encoding='utf-8')
 out=b.BASE/('accepted' if a.apply else 'rehearsal-final');s=Store(b.ROOT/'data/plant' if a.apply else out)
 assert s.version()==a.expected_version,(s.version(),a.expected_version)
 details(s,out);(out/'model.json').write_text(json.dumps(s.model(),ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':main()
