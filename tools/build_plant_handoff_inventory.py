"""Build planning indexes from a read-only snapshot, using the application's projection.

Generated files are observations and retrieval candidates, never canonical patches.
Authoritative engineering decisions remain in the authored handoff and original sources.
"""
import argparse
import collections
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/plant-handoff'

PACKAGES = {
    'P00': 'Identity, scope and topology reconciliation',
    'P01': 'Shared dust suppression, water, air and drainage',
    'P02': 'Jetty, ship unloaders, EAC-1/2 and UEF-1',
    'P03': 'Primary screening, EAC-3 and UEF-3',
    'P04': 'Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6',
    'P05': 'Coal Yard 1: preserve and close pilot gaps',
    'P06': 'Coal Yard 2', 'P07': 'Coal Yard 3', 'P08': 'Coal Yard 4',
    'P09': 'Reclaim transfer: UEF-8/9/10/11/12 and EBA-15/16',
    'P10': 'Blending silos and extraction',
    'P11': 'Crusher house and EBA-17',
    'P12': 'EBA-18, UEF-13 and sampling',
    'P13': 'EBA-19 and travelling trippers',
    'P14': 'Unit 1/2 bunkers and bunker dust extraction',
    'P15': 'Power, controls, fire, access and remaining shared infrastructure',
}

# These assign review work. They do not assert engineering identity, ownership or location.
def label_owner(label):
    if re.match(r'^(UEF-2|TP-(16|17|18))$', label): return 'P00'
    m = re.match(r'^(EAC|EBA)-(\d+)([AB]?)(?:\s|$)', label)
    if m:
        n = int(m[2])
        if n in [7, 8, 9, 10, 11, 12, 13, 14]: return f'P{5+(n-7)//2:02}'
        return {1:'P02',2:'P02',3:'P03',4:'P04',5:'P04',6:'P04',15:'P09',16:'P09',17:'P11',18:'P12',19:'P13'}.get(n)
    m = re.match(r'^(?:Coal Yard |EA[DEF]-|UEB-)([1-4])(?:\s|$)', label)
    if m: return f'P{4+int(m[1]):02}'
    m = re.match(r'^UAX-([1-8])(?:\s|$)', label)
    if m: return f'P{5+(int(m[1])-1)%4:02}'
    m = re.match(r'^UEF-(\d+)(?:\s|$)', label)
    if m: return {1:'P02',3:'P03',4:'P04',5:'P04',6:'P04',7:'P04',8:'P09',9:'P09',10:'P09',11:'P09',12:'P09',13:'P12'}.get(int(m[1]),'P00')
    if re.match(r'^(Coal Ship Unloader-[123]|SUL-[123])(?:\s|$)', label): return 'P02'
    if re.match(r'^(UEE-1|EBD-[1-4]|KB-R(?:P)?G-[1-4])(?:\s|$)', label): return 'P03'
    if re.match(r'^(UEE-3|EBD-[56]|EBC-[12]|KF-[12])(?:\s|$)', label): return 'P11'
    if re.match(r'^(Coal Blending Silo House|UEE-2|EBB-[12]|EBE-CES-[12]|KF-[34])(?:\s|$)', label): return 'P10'
    if re.match(r'^TT-[1-4](?:\s|$)', label): return 'P13'
    if re.match(r'^(Unit-[12] Coal Bunker Bay|Bunker-[A-F] of Unit-[12])$', label): return 'P14'
    m = re.match(r'^FG-(\d+)([AB]?)(?:\s|$)', label)
    if m:
        n=int(m[1]);return 'P03' if n<=2 else 'P04' if n<=6 else 'P09' if n<=12 else 'P10' if n<=14 else 'P11' if n<=16 else 'P12' if n<=18 else 'P13'
    m = re.match(r'^KB-FD-([1-8])$', label)
    if m:return 'P03' if int(m[1])<=2 else 'P04'
    if re.match(r'^(FTR-[1-4]|CV-[12])$',label):return 'P04'
    if re.match(r'^CV-[34]$',label):return 'P09'
    if re.match(r'^CV-[56]$',label):return 'P11'
    if re.match(r'^(AT-[12]|QB-[12]|EAT-[12])$',label):return 'P02'
    if re.match(r'^AT-[34]$',label):return 'P09'
    if re.match(r'^(QB-[34]|EAT-[34])$',label):return 'P12'
    if re.match(r'^EAU-1',label):return 'P03'
    if re.match(r'^EAU-2',label):return 'P12'
    return None

SOURCE_GROUPS = {
    'topology': r'^Control Write up|^COAL FLOW DIAGRAM|^LAYOUT OF COAL HANDLING|^CONV\. PROFILE|^General layout of Jetty',
    'conveyor': r'DRIVE SCHEDULE|^GA OF (GEAR BOX|GEARED COUPLING|BRAKE FOR CHP|SCOOP TYPE FLUID|TRACTION TYPE|IDLERS FOR CHP)|^BRG SELECTION|^SELECTION OF DRIVE COMPONENTS, BRAKES|^TECHNICAL DATA SHEET - CONVEYOR BELTING|^PCS BSS|^COASTING|^POWER & BELT TENSION CALC. FOR (ALL COAL|CONVEYORS)|SCRAPPER|SKIRT|^TYPICAL GA OF CHUTE',
    'transfer': r'FLAP GATE|FLOW DIVIDER|RACK & PINION|ROD GATE|HOIST SCHEDULE|^G.A. OF (ELECTRICAL|MANUAL)|^TYPICAL GA OF CHUTE',
    'screening': r'GRIZZLY|PSH|ROD GATE|RACK & PINION',
    'feeder': r'BELT FEEDER|DRIVE SCHEDULE|TRACTION TYPE FLUID|INTERNAL SCRAPPER',
    'dfds': r'DFDS|SUMP PUMP & STOCK|Data Sheet of Sump Pump|^GA-CATALOGUE & DATA SHEET OF SOLENOID',
    'yard': r'STOCKPILE|Stockpile|PLAIN WATER|SUMP PUMP & STOCK|Data Sheet of Sump Pump|^GA & MECH LOAD DATA OF (DH|TPH)|^GA & LOAD DATA OF DRIVE HOUSE',
    'stacker': r'Stacker|STACKER|Luffing Cylinder|^Fire detection',
    'reclaimer': r'Reclaimer|RECLAIMER|^Boom hoist drive',
    'silo': r'SILO|BLENDING|CBSH|BELT FEEDER|^DATASHEET OF BELT FOR BELT FEEDER',
    'crusher': r'CRUSHER|CRH|GRIZZLY|BELT FEEDER|OF DE SYSTEM|DE SYSTEM AT CRH|DUST EXRACTION',
    'tripper': r'TRIPPER|BUNKER SEALING|^DATASHEET OF BELT FOR BELT FEEDER',
    'bunker': r'Bunker|BUNKER|OF DE SYSTEM|DUST EXRACTION',
    'sampling': r'SAMPLING|SAMPLER',
    'measurement': r'WEIGHER|ANALY[SZ]ER|MAGNETIC SEPARATOR|METAL DETECTOR',
    'unloader': r'[Ss]hip [Uu]nloader|\(SUL\)|^Auxillary trolley|^Main trolley|^Trolley travel|^Holding closing|^GA of (Boom arrangement|Belt conveyor|Coupling|Machinary|Main Chute|Operator Cabin|H.O.T|Elevator-TENOVA)',
    'services': r'DFDS|SYSTEMS|SYSTEM|PUMP|PUMPS|VALVE|VENTILATION|AIR CONDITIONING|MCC|SLD|HOIST|ELEVATOR|Hooter|VULCANIZING|VACUUM|Dozer|LOADERS|Loaders',
}

def family(label):
    if re.fullmatch(r'(EAC|EBA)-\d+[AB]?',label):return 'conveyor'
    if re.fullmatch(r'UEF-\d+|TP-\d+',label):return 'transfer'
    if re.match(r'^Coal Yard',label):return 'yard'
    if re.fullmatch(r'EAD-[1-4]',label):return 'stacker'
    if re.fullmatch(r'EAF-[1-4]',label):return 'reclaimer'
    if re.match(r'^(EBB-|EBE-CES-|Coal Blending)',label):return 'silo'
    if re.match(r'^(UEE-3|EBC-)',label):return 'crusher'
    if re.match(r'^EBD-',label):return 'screen'
    if re.match(r'^KF-',label):return 'feeder'
    if re.match(r'^TT-',label):return 'tripper'
    if re.match(r'^(Bunker-|Unit-)',label):return 'bunker'
    if re.match(r'^(SUL-|Coal Ship)',label):return 'unloader'
    if re.match(r'^EAU-',label):return 'sampling'
    if re.match(r'^(EAT|AT|QB|CV)-',label):return 'measurement'
    return 'transfer' if re.match(r'^(FG|KB-|FTR)',label) else 'area'


def implementation_batch(target):
    """Primary target owner; later integration/service batches still review boundaries."""
    label, package = target['label'], target['review_package']
    if package == 'P00': return 'B00'
    if package == 'P02':
        if re.match(r'^(SUL-|Coal Ship Unloader-)', label):
            return 'B07' if label.endswith('-1') else 'B08'
        return 'B06' if re.match(r'^(EAC-2|QB-[12]|EAT-[12])', label) else 'B05'
    if package == 'P03':
        if label.startswith('EAU-'): return 'B11'
        return 'B10' if re.match(r'^(EAC-3|UEF-3|KB-FD-|FG-)', label) else 'B09'
    if package == 'P04':
        if re.match(r'^(EBA-6|UEF-7|CV-|FG-[56])', label): return 'B14'
        return 'B12' if re.match(r'^(EAC-4|UEF-4|FTR-[12]|KB-FD-[34])', label) else 'B13'
    if package == 'P05': return 'B15' if re.match(r'^EA[DF]-1$',label) else 'B16'
    if package in ['P06','P07','P08']:
        start={'P06':17,'P07':20,'P08':23}[package]
        return f'B{start+1 if re.match(r"^EA[DF]-",label) else start:02}'
    if package == 'P09':
        if re.match(r'^(UEF-[89]|FG-[78])$',label):return 'B26'
        if re.match(r'^(UEF-1[01]|FG-(9|10))$',label):return 'B27'
        return 'B29' if re.match(r'^(EBA-16|CV-)',label) else 'B28'
    if package == 'P10':return 'B30' if label=='Coal Blending Silo House' or label.startswith('EBB-') else 'B31'
    if package == 'P11':
        if label.startswith('EBC-'):return 'B33'
        return 'B32' if label=='UEE-3' or label.startswith('EBD-') or label in ['FG-15A','FG-15B'] else 'B34'
    if package == 'P12':return 'B37' if label.startswith('EAU-') else 'B36'
    if package == 'P13':
        if label in ['TT-1','TT-3','FG-19','FG-21']:return 'B39'
        if label in ['TT-2','TT-4','FG-20','FG-22']:return 'B40'
        return 'B38'
    if package == 'P14':return 'B41'
    raise ValueError(f'No batch assignment for target {label} in {package}')

def compact_pages(pages):
    pages=sorted(set(pages)); groups=[]
    for page in pages:
        if groups and page==groups[-1][-1]+1:groups[-1].append(page)
        else:groups.append([page])
    return ', '.join(str(g[0]) if len(g)==1 else f'{g[0]}–{g[-1]}' for g in groups)

def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--node',default=shutil.which('node'))
    args=parser.parse_args()
    if not args.node:parser.error('Node is needed for the same projection used by the application')
    snap=json.loads(Path(args.snapshot).read_text(encoding='utf8'));model=snap['model']
    js="""const fs=require('fs'),p=require('./dist/plant-model.js'),s=JSON.parse(fs.readFileSync(process.argv[1],'utf8')),m=p.build(s.model,{at:Date.parse(s.captured_at)});
    console.log(JSON.stringify({networks:m.networks.map(a=>a.id),entities:[...m.entities.values()].map(e=>({id:e.id,label:e.label,aliases:e.aliases,reference:m.refs.has(e.id),classes:m.classes.get(e.id)||[],stages:[...(m.memberships.get(e.id)||[])],children:(m.children.get(e.id)||[]).map(a=>a.canonical_subject),parents:(m.parents.get(e.id)||[]).map(a=>a.canonical_object),assembly:m.assembly(e.id).map(x=>x.id),applicable:m.applicable(e.id).map(a=>a.id)}))}));"""
    projection=json.loads(subprocess.run([args.node,'-e',js,str(Path(args.snapshot).resolve())],cwd=ROOT,check=True,capture_output=True,encoding='utf8').stdout)
    entities={e['id']:e for e in projection['entities']};labels={e['label']:e for e in entities.values()}
    facts=[a for a in model['assertions'] if not a.get('retirement') and not a.get('suppressed')]
    assertions={a['id']:a for a in facts};evs={e['id']:e for e in snap['evidence']};docs={d['id']:d for d in snap['documents']}
    outgoing=collections.defaultdict(list)
    for a in facts:outgoing[a['canonical_subject']].append(a)
    doc_pages=collections.defaultdict(lambda:collections.defaultdict(list))
    for e in evs.values():doc_pages[e['document_id']][e['page']].append(e['id'])
    def source_refs(items):
        use=collections.defaultdict(set)
        for a in items:
            for r in a['evidence']:
                e=evs.get(r['evidence_id'])
                if e:use[e['document_id']].add(e['page'])
        return [{'document_id':k,'pages':sorted(v)} for k,v in sorted(use.items(),key=lambda x:docs[x[0]]['name'])]
    def work_owner(e):
        direct=label_owner(e['label'])
        if direct:return direct,'tag/name retrieval rule; not an engineering assertion'
        # Prefer nearest recorded parent. Do not let membership in the plant root assign a family.
        seen={e['id']};queue=list(e['parents'])
        while queue:
            layer=queue;queue=[];owners=set()
            for parent in layer:
                if parent in seen:continue
                seen.add(parent);p=entities[parent];owner=label_owner(p['label'])
                if owner:owners.add(owner)
                queue.extend(p['parents'])
            if len(owners)==1:return next(iter(owners)),'review routing via recorded parent; review containment evidence'
            if len(owners)>1:return 'P00','multiple package parents; boundary review required'
        words=e['label'].lower()
        if 'rihand' in words or 'tanjung' in words:return 'P00','other-project reference: applicability exclusion review'
        for pattern,owner in [(r'unloader|\bsul\b|trolley|grab hold','P02'),(r'bunker','P14'),(r'tripper','P13'),(r'crusher|grizzly feeder','P11'),(r'silo|extractor','P10'),(r'stacker|reclaimer|scraper boom','P05'),(r'dfds|spds|stockpile.*(valve|water)|run.off|sump|\bcrp|\bsc-|ds pump|water system|sprinkler','P01'),(r'mcc|dcs|ventilation|fire|hoist|elevator|loader|dozer|vacuum|vulcaniz','P15'),(r'conveyor|idler|pulley|gearbox|coupling|scraper|brake','P00')]:
            if re.search(pattern,words):return owner,'family/name retrieval candidate; installed applicability unreviewed'
        return 'P00','unresolved record; explicit disposition required'
    for e in entities.values():
        e['review_package'],e['routing_basis']=work_owner(e)
        e['own_fact_count']=len(outgoing[e['id']]);e['assembly_record_count']=len(e['assembly'])
        e['current_source_pages']=source_refs(outgoing[e['id']])
        e['review_status']='reference_review' if e['reference'] else 'not_reviewed_by_this_plan'
    out=OUT/'inventory';cards=OUT/'targets';out.mkdir(parents=True,exist_ok=True);cards.mkdir(exist_ok=True)
    source_catalog=[]
    for d in snap['documents']:
        source_catalog.append({**{k:d[k] for k in ['id','name','sha256','media_type','revision','authority']},
            'original':f'data/plant/originals/{d["sha256"]}',
            'groups':[key for key,rx in SOURCE_GROUPS.items() if re.search(rx,d['name'],re.I)],
            'pages':dict(sorted(doc_pages[d['id']].items())),
            'review_status':'inventory_only_unless_review_log_specifies_pages',
            'authority_note':'Imported metadata is not proof of as-built or field acceptance; inspect each title block/review sheet.'})
    write_json(out/'sources.json',source_catalog)
    write_json(out/'entities.json',list(entities.values()))
    networks=[a for a in facts if a['id'] in set(projection['networks'])]
    write_json(out/'connections.json',[{**{k:a.get(k) for k in ['id','canonical_subject','predicate','canonical_object','context','origin','evidence']},'from_label':entities[a['canonical_subject']]['label'],'to_label':entities[a['canonical_object']]['label']} for a in networks])
    quals=[a for a in facts if a['predicate'] in ['source_gap','source_discrepancy']]
    write_json(out/'existing-qualifications.json',quals)
    with (out/'record-review-queue.csv').open('w',newline='',encoding='utf-8-sig') as file:
        fields=['id','label','reference','review_package','routing_basis','review_status','own_fact_count','assembly_record_count','stages']
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for e in sorted(entities.values(),key=lambda e:(e['review_package'],e['label'])):writer.writerow({**e,'stages':';'.join(e['stages'])})

    target_rx=r'^(?:(?:EAC|EBA)-\d+[AB]?|UEF-\d+|TP-(?:16|17|18)|UEE-[13]|Coal Blending Silo House|EA[DEF]-[1-4]|UEB-[1-4]|UAX-[1-8]|EBD-[1-6]|EBC-[12]|EBB-[12]|EBE-CES-[12]|KF-[1-4]|TT-[1-4]|FG-\d+[AB]?|KB-(?:FD|RG|RPG)-\d+|FTR-[1-4]|(?:AT|QB|EAT)-[1-4]|CV-[1-6]|EAU-[12]|Unit-[12] Coal Bunker Bay|Bunker-[A-F] of Unit-[12]|Coal Ship Unloader-[123]|SUL-[123]|Coal Yard [1-4])$'
    targets=[dict(e,family=family(e['label']),planned=False) for e in entities.values() if re.fullmatch(target_rx,e['label'])]
    for n in [2,3,4]:targets.append({'id':None,'label':f'Coal Yard {n}','family':'yard','review_package':f'P{4+n:02}','planned':True,'assembly':[],'assembly_record_count':0,'own_fact_count':0,'parents':[],'children':[],'aliases':[],'applicable':[],'current_source_pages':[]})
    for t in targets:
        t['implementation_batch']=implementation_batch(t)
        t['card']=re.sub(r'[^a-z0-9]+','-',t['label'].lower()).strip('-')+'.md'
        eid=t['id'];scope=set(t['assembly'])
        own=outgoing[eid] if eid else []
        scoped=[a for a in facts if a['canonical_subject'] in scope]
        related=[assertions[x] for x in t['applicable']]
        related_subjects={a['canonical_subject'] for a in related}
        t['applicable_reference_entities']=sorted(related_subjects)
        t['assembly_source_pages']=source_refs(scoped)
        t['applicable_source_pages']=source_refs([a for a in facts if a['canonical_subject'] in related_subjects])
        t['qualification_ids']=[a['id'] for a in quals if a['canonical_subject'] in scope|related_subjects]
        family_groups={'conveyor':['conveyor','measurement'],'transfer':['transfer','dfds'],'yard':['yard','stacker','reclaimer'],'stacker':['stacker'],'reclaimer':['reclaimer'],'silo':['silo','dfds'],'crusher':['crusher'],'screen':['screening','crusher'] if t['label'] in ['EBD-5','EBD-6'] else ['screening'],'feeder':['feeder'],'tripper':['tripper'],'bunker':['bunker'],'unloader':['unloader'],'sampling':['sampling'],'measurement':['measurement'],'area':['screening','dfds'] if t['label']=='UEE-1' else ['transfer']}.get(t['family'],[])
        t['source_groups']=family_groups
        dedicated=[]
        m=re.fullmatch(r'(EAC|EBA)-(\d+)[AB]?',t['label'])
        if m:
            n=int(m[2]);rx=rf'^GA & LOAD DATA OF BELT CONVEYOR-{n}(?!\d)'
            dedicated=[d['id'] for d in source_catalog if re.search(rx,d['name'],re.I)]
        m=re.fullmatch(r'UEF-(\d+)',t['label'])
        if m:
            n=int(m[1]);dedicated=[d['id'] for d in source_catalog if re.search(rf'^GA & MECH LOAD OF TP-{n}(?!\d)|^Piping Layout.*UEF-?{n}(?!\d)',d['name'],re.I)]
        t['dedicated_source_candidates']=dedicated
        boundary=[a for a in networks if (a['canonical_subject'] in scope)!=(a['canonical_object'] in scope)]
        t['boundary_connection_ids']=[a['id'] for a in boundary]
        t['located_records']=[a['canonical_subject'] for a in facts if a['predicate']=='located_at' and a.get('canonical_object')==eid] if eid else []
        scene_scope=set(scope)
        for located in t['located_records']:scene_scope.update(entities[located]['assembly'])
        scene_connections=[a for a in networks if a['canonical_subject'] in scene_scope or a['canonical_object'] in scene_scope]
        t['scene_connection_ids']=[a['id'] for a in scene_connections]
        t['review_dimensions']={key:'pilot_recheck' if t['label'] in ['EAC-1A','EAC-1B','UEF-1','Coal Yard 1'] else 'requires_source_review' for key in ['identity','purpose_location','containment','material_routes','drive_mechanical','utilities','control_protection','ratings_maintenance','provenance','visual_journey']}
        lines=[f'# {t["label"]}', '',f'Planning card at model v{model["version"]}. Package **{t["review_package"]}** — {PACKAGES[t["review_package"]]}. Primary implementation batch **{t["implementation_batch"]}**; later service/integration batches also review its boundaries.', '',
            f'Read [section plan](../SECTION_PLANS.md#{t["review_package"].lower()}) and [family contract](../ASSEMBLY_CONTRACTS.md#{t["family"]}) before editing. This card inventories accepted records; it does not certify their correctness or completeness.', '',
            f'- Canonical ID: `{eid}`.' if eid else '- **Planned functional-area entry; no canonical ID yet.** Establish membership from the source and create through reviewed ingestion.',
            f'- Existing containment closure: {t["assembly_record_count"]} record(s) including root; {t["own_fact_count"]} assertions on root. These are model records, not a count of physical devices.',
            '- Aliases: '+(', '.join(t['aliases']) or 'none'),
            '- Existing parents: '+(', '.join(entities[x]['label'] for x in t['parents']) or 'none'),
            '- Direct components: '+(', '.join(entities[x]['label'] for x in dict.fromkeys(t['children'])) or 'none recorded'),
            '- Located equipment: '+(', '.join(entities[x]['label'] for x in dict.fromkeys(t['located_records'])) or 'none recorded'),
            '', '## Source work', '', 'Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:', '']
        for did in dedicated:
            d=docs[did];lines.append(f'- `{did}` — {d["name"]}; available PDF pp. {compact_pages(doc_pages[did])}. Retrieval candidate, not reviewed applicability.')
        if not dedicated:lines.append('- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.')
        lines.extend(['',f'Common source groups: **{", ".join(family_groups)}** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).', '', 'Existing assembly citations (claims still require original-source review):',''])
        for use in t['assembly_source_pages']:
            d=docs[use['document_id']];lines.append(f'- `{d["id"]}` — {d["name"]}, PDF pp. {compact_pages(use["pages"])}.')
        if not t['assembly_source_pages']:lines.append('- None.')
        lines.extend(['','Existing explicitly applicable reference identities: '+(', '.join(f'{entities[x]["label"]} (`{x}`)' for x in sorted(related_subjects)) or 'none')+'.', '', '## Existing material interfaces', '', 'These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.', '', '| From | To | Source condition | Assertion |','|---|---|---|---|'])
        for a in scene_connections:
            if a['context'].get('network')!='material':continue
            condition=str(a['context'].get('condition','')).replace('|','/').replace('\n',' ')
            lines.append(f'| {entities[a["canonical_subject"]]["label"]} | {entities[a["canonical_object"]]["label"]} | {condition or "No condition recorded; review source"} | `{a["id"]}` |')
        if not any(a['context'].get('network')=='material' for a in scene_connections):
            lines.append('| No documented material connection in this scope | — | Review the section interface plan; this is not proof that no route exists | — |')
        lines.extend(['','All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.', '', '## Required closure', '',
            '- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.',
            '- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.',
            '- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.',
            '- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.',
            '- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.', '', 'Recorded gaps/disagreements in this assembly or applicable references:', ''])
        for fid in t['qualification_ids']:
            a=assertions[fid];lines.append(f'- `{fid}` ({entities[a["canonical_subject"]]["label"]}): {a["value"]}')
        if not t['qualification_ids']:lines.append('- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.')
        (cards/t['card']).write_text('\n'.join(lines)+'\n',encoding='utf8')
    targets.sort(key=lambda t:(t['review_package'],t['label']))
    write_json(out/'targets.json',targets)
    grouped_targets=collections.defaultdict(list)
    for t in targets:grouped_targets[t['implementation_batch']].append({'label':t['label'],'id':t['id'],'card':t['card']})
    write_json(out/'batch-targets.json',dict(sorted(grouped_targets.items())))
    with (out/'coverage.csv').open('w',newline='',encoding='utf-8-sig') as file:
        writer=csv.writer(file);writer.writerow(['package','batch','target','canonical_id','family','records_including_root',*targets[0]['review_dimensions']])
        for t in targets:writer.writerow([t['review_package'],t['implementation_batch'],t['label'],t['id'] or 'planned',t['family'],t['assembly_record_count'],*t['review_dimensions'].values()])
    index=['# Target index','',f'Baseline v{model["version"]}. {len(targets)} named work targets; these include planned yard-area entries and scope-boundary review targets. Individual cards are generated observations, not engineering completion certificates. Each target has one primary batch owner; later service/integration work still applies.','','| Package / batch | Target | Canonical ID | Containment records |','|---|---|---|---|']
    for t in targets:index.append(f'| {t["review_package"]} / {t["implementation_batch"]} | [{t["label"]}](targets/{t["card"]}) | `{t["id"] or "planned"}` | {t["assembly_record_count"]} |')
    (OUT/'TARGET_INDEX.md').write_text('\n'.join(index)+'\n',encoding='utf8')
    catalog=['# Source catalog','', 'Titles/groups are retrieval aids. Available PDF page numbers are one-based; evidence blocks may be crops or multiple text representations of the same page. Imported authority/revision metadata never overrides the original title block. See [review log](REVIEW_LOG.md) for what was actually examined in this design pass.','','Exact document hashes, original paths and all page-to-evidence mappings: [sources.json](inventory/sources.json).','']
    for group in SOURCE_GROUPS:
        catalog.extend([f'## {group}','', '| Document ID | Filename | Available pages |','|---|---|---|'])
        for d in source_catalog:
            if group in d['groups']:catalog.append(f'| `{d["id"]}` | {d["name"]} | {compact_pages(int(x) for x in d["pages"])} |')
        catalog.append('')
    catalog.extend(['## Dedicated conveyor and building GAs','', '| Document ID | Filename | Available pages |','|---|---|---|'])
    for d in source_catalog:
        if re.search(r'GA & (LOAD DATA OF BELT CONVEYOR|MECH LOAD OF|MECH LOAD DATA OF)',d['name'],re.I):catalog.append(f'| `{d["id"]}` | {d["name"]} | {compact_pages(int(x) for x in d["pages"])} |')
    (OUT/'SOURCE_CATALOG.md').write_text('\n'.join(catalog)+'\n',encoding='utf8')
    nonrefs=[e for e in entities.values() if not e['reference']]
    invalid_refs=[(a['id'],r['evidence_id']) for a in facts for r in a['evidence'] if r['evidence_id'] not in evs]
    report={'version':model['version'],'captured_at':snap['captured_at'],'documents':len(docs),'evidence_blocks':len(evs),'canonical_records':len(entities),'nonreference_records':len(nonrefs),'unplaced_nonreference_records':sum(not e['stages'] for e in nonrefs),'unplaced_local_name_records':sum(not e['stages'] and e['label'].startswith(('UEF','UEE','EAC','EBA')) for e in nonrefs),'nonreference_records_without_own_assertions':sum(not outgoing[e['id']] for e in nonrefs),'active_assertions':len(facts),'network_assertions':len(networks),'network_counts':dict(collections.Counter(a['context'].get('network') for a in networks)),'targets':len(targets),'conveyor_targets':sum(t['family']=='conveyor' for t in targets),'in_scope_uef_targets':sum(bool(re.fullmatch(r'UEF-(1|[3-9]|1[0-3])',t['label'])) for t in targets),'explicit_gap_discrepancy_assertions':len(quals),'review_package_counts':dict(collections.Counter(e['review_package'] for e in nonrefs)),'missing_evidence_references':invalid_refs,'sqlite_integrity':snap['integrity'],'foreign_key_errors':snap['foreign_key_errors']}
    write_json(out/'audit.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
