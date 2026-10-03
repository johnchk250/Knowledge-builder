"""One-time, source-reviewed B01 grouped-service reference corrections from v616."""
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

BASE = ROOT/'output/plant-enrichment/B01/remaining-references'
GENERIC = 'ent_a1afdfc250e5494191ab'
VENDOR = 'ent_8154e35849e345dfa3dc'
CRP = 'ent_7c28590069a04e8b8cb1'
FWS = 'ent_93afe5d239a54e9a963b'
SP8 = 'ent_000cb429e6b642f98f71'
SP5 = 'ent_a691834f6642469ebe57'
SPDS = 'ent_3ebb96607d1f4f3094f0'
RETIRED = {'fact_b2ac354edb434c628577', 'fact_38eba2de6455406c847e',
           'fact_76d9f1fda2804e669afc', 'fact_14467dbda81241ddada1', 'fact_6e43689d9e9a4fe1816f'}


def packages(snap):
    def fact(subject, predicate, value, eid, region, basis, relation=False, inferred=False):
        return {'op':'assert', 'subject':subject, 'predicate':predicate,
                'object_entity' if relation else 'value':value,
                'context':{'kind':'classification' if predicate == 'instance_of' else 'specification', 'basis':basis},
                **{**support(eid,region),'origin':'inferred' if inferred else 'explicit'}}
    def retire(fid,eid,region,reason):
        return {'op':'retire','assertion_id':fid,'reason':reason,**support(eid,region)}
    def pkg(doc,title,ops,visual,scope):
        return {'document_id':doc,'visual_ids':visual,'body':{'summary':title,'operations':ops,'intake_assessment':{
            'route':'mixed','purpose':title,'questions':['Does this record represent a numbered physical instance, a multi-pump source group or a shared owner?'],
            'reviewed_evidence_ids':[e['id'] for e in snap['evidence'] if e['document_id']==doc],
            'gaps':[scope,'Individual runoff pump assemblies/routes remain B04; detailed SW/PW/SPDS supply and local controls remain B03. No installed serial, field condition or final motor selection is asserted.']}}}
    eid='ev_ceaa51cb2cbc41a6bbf0';reg=[.08,.14,.92,.40]
    proof={**support(eid,reg),'origin':'inferred'}
    ops=[{'op':'merge','source':GENERIC,'target':VENDOR,'reason':
          'Both imported Flowmore records originate in the same175539 vendor package. Original p2 explicitly tags FWP/CRP-1A/1B and quantity2; p6 gives the identical5616AWS model/order/duty; p7-9 are drawings for that pair. Neither generic label identifies another installed individual pump. Reconcile the duplicate source records as one vendor design reference, retaining every original fact.',**proof},
         retire('fact_b2ac354edb434c628577',eid,reg,'The source explicitly covers quantity2 FWP/CRP-1A/1B; this generic vendor record is a design reference, not another physical pump.'),
         retire('fact_38eba2de6455406c847e',eid,reg,'The pond caption is design applicability of a two-pump source package, not placement proof of this extra generic physical instance. Replace physical location with design applicability.'),
         {'op':'alias','entity':VENDOR,'alias':'CRP-1A/B Flowmore pump vendor design reference',**support(eid,reg)},
         fact(VENDOR,'instance_of','equipment_design_reference',eid,reg,'Original175539 Rev2 vendor data p2 explicitly covers FWP/CRP1A/1B quantity2.'),
         fact(VENDOR,'design_applicability','Vendor175539 Rev2, FIO18-Oct-2019, describes TWO FWP/CRP-1A/1B pumps at the coal runoff/settling pond. Flowmore5616AWS(S.O)125x100, orderSALE-1909-4272-40, is a shared design, not an additional installed pump. Old generic labels redirect here. B04 must instantiate the numbered pair with its actual pit and destination.',eid,reg,'Original all9pages visually reviewed for title, tag/quantity, data, comments and drawing applicability.'),
         fact(VENDOR,'design_detail_applies_to',CRP,eid,reg,'p2 explicitly identifies the CRP1A/B pair.',True),
         fact(VENDOR,'design_detail_applies_to',FWS,eid,reg,'p2 explicitly identifies coal-runoff feed-water service; existing common FWS identity reused.',True),
         fact(VENDOR,'source_discrepancy','Vendor pp2/3/6/7 specify or recommend37kW, while DBR175258 p2/p7 selects22kW subject to final vendor data. Vendor p3 maximum input33kW explains a wider duty range. Preserve both design bases; no current motor selection established. Datasheet grease lubrication and drawing self-water lubrication concern different component scopes; detailed reconciliation remains B04.', 'ev_3ca1f22fb5b546109723',[.08,.12,.94,.62], 'Vendor175539 pp2-9 reviewed; this is vendor/source qualification, not a new numeric motor claim.')]
    result=[pkg('doc_9984d9b1045b47deb8b4','B01: reconcile duplicate runoff vendor records as one two-pump design reference',ops,[eid,'ev_3ca1f22fb5b546109723'],
                'All9original pages visually reviewed: p1 cover/revision/FIO, pp2-3 datasheets, pp4-5 comments, p6 curve, pp7-9 GA/cross-sections. Detailed BOM extraction remains B04, not missing evidence.')]
    eid='ev_389647e5bc9d46b3bd34';reg=[.10,.10,.94,.34]
    ops=[fact(CRP,'instance_of','equipment_design_reference',eid,reg,'Original175258 Rev4 p2 is a grouped CRP1A/B design schedule, not one additional pump.'),
         fact(CRP,'design_detail_applies_to',FWS,eid,reg,'Explicit feed-water system application in the pump schedule.',True),
         fact(CRP,'design_applicability','CRP-1A/1B source schedule covers2pumps(1working+1standby),67m3/h and58mwc minimum, with22kW design motor selected subject to final vendor data. This record represents the schedule for the pair; B04 owns individual CRP1A/B assemblies and verified pond-to-tank routing. The vendor reference is separate evidence for the same pair.',eid,reg,'DBR175258 Rev4 dated31-Jul-2019; original pp1/2 cover and schedule visually reviewed, p7 calculation text inspected.'),
         fact(FWS,'source_discrepancy','DBR175258 Rev4 p2/p7 selects22kW with an explicit final-vendor qualification. Do not promote this calculation selection over the vendor17553937kW recommendation or to an installed motor rating. Both source bases require final vendor/as-built reconciliation in B04.',eid,reg,'Exact DBR schedule footnote retained; no scalar conflict is manufactured on a generic pump.')]
    result.append(pkg('doc_393f3d13817b4fe2acaa','B01: distinguish the CRP pair schedule from an extra installed pump',ops,[eid],
                      'All7pages text inventoried for source identity; original pp1/2 visually reviewed. Calculations pp3-7 remain detailed B04 work; p7 final-vendor note inspected as text.'))
    eid='ev_cfe00ec0be184ce7a51e';reg=[.80,.025,.99,.58]
    ops=[]
    for target,fid,scope in [(SP8,'fact_76d9f1fda2804e669afc','SP-8A through8H, four working plus four standby at CHP stockpiles'),
                             (SP5,'fact_14467dbda81241ddada1','SP-5A/5B, one working plus one standby at LHP runoff pond')]:
        ops += [retire(fid,eid,reg,'The original schedule row covers '+scope+'; imported grouped record is not one additional physical pump.'),
                fact(target,'instance_of','equipment_design_reference',eid,reg,'Grouped source schedule; physical numbered instances remain separately owned local assets.'),
                fact(target,'design_applicability','Original175092 grouped schedule covers '+scope+'. Scheduled duties are source-group design bases; no individual field instance or sump assignment follows solely from alphabetical numbering. Existing Yard1 SP8G/H remain separate physical instances; other source-specific pit mappings belong to B04 and their yard batches.',eid,reg,'Original sump/runoff P&ID175092 p1 schedule and branch scope visually reviewed.')]
    for target in ['ent_de6adf5793e24e77a69f','ent_815e00d27ae34b5d928a']:
        ops.append(fact(SP8,'design_detail_applies_to',target,eid,reg,'SP8A-H schedule explicitly includes the already accepted Yard1 SP8G/H pumps; local pit assignment retained.',True))
    result.append(pkg('doc_0453a0a014424f1cae06','B01: separate CHP/LHP runoff schedule groups from local pump instances',ops,[eid],
                      'Both-page evidence inventory inspected; p1 schedule and four-stockpile branch region visually reviewed. Dense per-pit routing/control details remain B04. No new LHP/CHP physical pump created.'))
    eid='ev_8a07d747de0f49c4a692';reg=[.05,.29,.94,.54]
    ops=[retire('fact_6e43689d9e9a4fe1816f',eid,reg,'Original175319 p2 identifies one common station/header serving all four numbered stockpiles. Shared SPDS system already has plant ownership; retire the generic-yard containment that gives it a second owner. Retain the aggregate stockyard area and all its numbered stockpiles.'),
         fact(SPDS,'equipment_role','One common CHP stockpile-water supply serves all4numbered stockpiles EAE1-4. Pumps are in House2 nearUEF7, drawing from common RCCtank2 and feeding a common header, then a separate ringheader around each stockpile. Common station equipment retains one canonical service owner; local ringheaders/sectors remain yard assets. Generic Coal Stockpile Yard is the aggregate area, not a second pump-station owner.',eid,reg,'Original175319 p2 common supply paragraph; design source, not live route state.'),
         fact('ent_988efbb9fa7c4dfd89e2','documented_source_identity','Aggregate CHP stockyard area contains the four separately numbered EAE1-4 stockpiles. It is not a fifth stockpile and does not own a second common SPDS pump station. Existing numbered-stockpile containment and aggregate area identity are retained.',eid,reg,'Original175319 p2 names four stockpiles; preserves existing control-drawing area hierarchy.',inferred=True)]
    result.append(pkg('doc_e17edf6897d746fabe12','B01: give the common stockpile supply one owner while retaining the aggregate yard area',ops,[eid],
                      'Original p2 common supply/four-stockpile paragraph rechecked; previously reviewed p1/3/4/8/10/15/16 retained. Full document evidence inventory is page identity, not a claim of detailed review of remaining controls.'))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--verify-rehearsal',action='store_true');args=p.parse_args()
    snap=json.loads((ROOT/'output/plant-enrichment/B01/accepted-v616.json').read_text(encoding='utf8'))
    pkgs=packages(snap);plant=ROOT/'data/plant';out=BASE/('accepted' if args.apply else 'rehearsal');out.mkdir(parents=True,exist_ok=True)
    if args.verify_rehearsal:
        assert not args.apply
        assert pkgs==json.loads((out/'packages.json').read_text(encoding='utf8'))
        verify(snap['model'],json.loads((out/'model.json').read_text(encoding='utf8')),
               json.loads((out/'commit-log.json').read_text(encoding='utf8')),out)
        return
    assert not (out/'commit-log.json').exists(),'Already committed or partial; resume verification, never replay.'
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('BEGIN');before=Store.__new__(Store).model(db=db)
        assert before['version']==616 and before==snap['model'],'Live state changed; re-review required.'
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup=BASE/'backup-v616';backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3',backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst:db.backup(dst)
            copied=[]
            for d in snap['documents']:
                if d['id'] not in [x['document_id'] for x in pkgs]:continue
                assert hashlib.sha256((plant/'originals'/d['sha256']).read_bytes()).hexdigest()==d['sha256']
                paths={Path('originals')/d['sha256']}|{Path('renders')/e['image'] for e in snap['evidence'] if e['document_id']==d['id'] and e['image']}
                for rel in paths:
                    dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(plant/rel,dest);copied.append(str(rel))
            save(backup/'manifest.json',{'version':616,'copied_files':copied,'scope':'Consistent full SQLite backup plus immutable originals/renders for all four packages.'})
    if args.apply:
        assert pkgs==json.loads((BASE/'rehearsal/packages.json').read_text(encoding='utf8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    save(out/'packages.json',pkgs);store=Store(plant if args.apply else out);logs=[]
    for i,pkg in enumerate(pkgs):
        body=pkg['body'];v=616+i
        report=validate(store,{k:body[k] for k in ['summary','operations']},pkg['document_id'],v,visual_ids=pkg['visual_ids'])
        save(out/f'validation-v{v}.json',report);assert not report['errors'],report
        staged=stage(store,pkg['document_id'],body,visual_ids=pkg['visual_ids'],analysis_dir=str(out),expected_version=v)
        result=commit(store,staged['proposal_id']);logs.append({'proposal_id':staged['proposal_id'],'document_id':pkg['document_id'],**result});save(out/'commit-log.json',logs)
    after=store.model();save(out/'model.json',after)
    verify(before,after,logs,out)


def verify(before,after,logs,out):
    assert after['version']==620
    facts={a['id']:a for a in after['assertions']};redirects={GENERIC:VENDOR}
    for a in before['assertions']:
        old,new=preserved(a),preserved(facts[a['id']])
        if a['id'] in RETIRED:
            assert new['retirement'];old.pop('retirement');new.pop('retirement')
        assert old==new,a['id']
        for field in ['canonical_subject','canonical_object']:assert facts[a['id']][field]==redirects.get(a[field],a[field])
    aliases={a['id']:a for a in after['aliases']};assert all(a==aliases[a['id']] for a in before['aliases'])
    assert len(after['aliases'])==len(before['aliases'])+1 and len(after['entities'])==len(before['entities'])
    assert len(after['merges'])==len(before['merges'])+1 and before['conflicts']==after['conflicts']
    added=[a for a in after['assertions'] if a['created_version']>616];assert len(added)==17
    save(out/'result.json',{'ok':True,'version':620,'proposals':[x['proposal_id'] for x in logs],'redirects':redirects,
                           'retired_assertions':sorted(RETIRED),'added_claims':added,'preserved_assertions':len(before['assertions'])-len(RETIRED),
                           'checks':['one duplicate vendor source redirect','four groups classified as design references','five reviewed retirements',
                                     'all other assertion and alias payloads preserved','one SPDS plant owner','four conflicts unchanged','no new physical equipment']})
    print(json.dumps({'ok':True,'version':620,'mode':out.name,'proposals':[x['proposal_id'] for x in logs]}))


if __name__=='__main__':main()
