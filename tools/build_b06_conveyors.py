"""Source-reviewed Tier 1 assemblies for conveyor 2, guarded at v635."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/plant-enrichment/B06/ga-175012'
DOC = 'doc_030c8f82fb674548a4dc'
EV = 'ev_e681c2f0a7c64430b4c4'


def main():
    m = json.loads((ROOT/'output/plant-enrichment/B05/model-v635.json').read_text(encoding='utf8'))
    assert m['version'] == 635
    ops = []
    schedule = [.78, .065, .96, .765]
    drive = [.27, .61, .56, .79]
    inlet = [.07, .09, .28, .46]

    def proof(region):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=EV, quote='', region=region)])

    def fact(s, p, v, region=schedule, obj=False, network=None, condition=None):
        ctx = dict(kind='classification' if p == 'instance_of' else 'specification', basis='175012 Rev2,29-Oct-2018; approved23-Nov-2018. Original GA/schedule, design applicability EAC-2A and EAC-2B; not an installed-condition inspection.')
        if network:
            ctx.update(kind='connection', network=network, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'):v}, context=ctx, **proof(region)))

    for lane, owner in [('A','ent_91dd763af7f4417ebaa6'), ('B','ent_f4dc6c5b38d14bceb5e5')]:
        def new(key, label, typ, region=schedule, place=None):
            id = 'tmp_b06_'+lane.lower()+'_'+key
            ops.append(dict(op='entity', id=id, label=f'EAC-2{lane} {label}', **proof(region)))
            fact(id,'instance_of',typ,region)
            fact(id,'part_of',owner,region,True)
            if place:
                fact(id,'located_at',place,region,True)
            return id
        head = 'ent_92291cd617b04811bc28'
        motor = new('motor','main drive motor','electric_motor',drive,head)
        fluid = new('fluid','scoop fluid coupling','fluid_coupling',drive,head)
        gear = new('gear','main gearbox','gearbox',drive,head)
        low = new('low','low-speed coupling','coupling',drive,head)
        brake = new('brake','service thruster brake','thruster_drum_brake',drive,head)
        pulley = new('head','head drive pulley','pulley',drive,head)
        belt = new('belt','conveyor belting','conveyor_belt')
        support = new('support','idler and belt-support assembly','functional_assembly')
        tails = new('tail_bends','tail and bend/snub pulley group','functional_assembly')
        takeup = new('takeup','vertical gravity take-up assembly','take_up_assembly')
        cleaners = new('cleaners','head and tail belt-cleaner group','functional_assembly')
        protection = new('protection','PCS BSS and ZSS protection group','functional_assembly')
        chute = new('head_chute','screening discharge chute','chute_interface',inlet,head)
        for s,p,v in [
            (motor,'assembly_arrangement','One BHEL TEFC squirrel-cage motor per conveyor:380kW HT,3.3kV; schedule speed1488rpm.'),
            (fluid,'equipment_model','PST530 scoop type fluid coupling'),
            (gear,'assembly_arrangement','Premium B3-450 bevel helical gearbox; ratio17:1.'),
            (low,'equipment_model','RG10 low-speed coupling'),
            (brake,'equipment_model','EBTM-500/DS/DG electro-hydraulic thruster brake'),
            (pulley,'assembly_arrangement','One drive pulley per conveyor:800mm diameter,2200mm face,2700mm bearing centres.'),
            (belt,'assembly_arrangement','NN1000/5,2000mm width,275m endless length; FR cover5mm top/2mm bottom.'),
            (support,'assembly_arrangement','Transition,impact,carrying,machined,non-magnetic,self-aligning,return and flat-return idler groups; gallery deck/seal plate and receiving skirt shown. Individual idler/BOM breakdown deferred.'),
            (tails,'assembly_arrangement','Schedule combines tail and bend/snub pulleys:630mm diameter,quantity4 per conveyor. This is a combined group, not four tail pulleys; take-up pulley is separately included in the gravity take-up assembly.'),
            (takeup,'assembly_arrangement','Vertical gravity take-up with mark-up scale;3700mm travel; one630mm take-up pulley; schedule design counterweight8100kg per conveyor. Rope/sheave selection remains source-qualified.'),
            (cleaners,'assembly_arrangement','One spring-loaded primary and one secondary scraper at discharge pulley; one internal V-plough near tail pulley, per conveyor.'),
            (protection,'assembly_arrangement','Per conveyor: BSS3 pairs on both sides at40m intervals; PCS4 pairs on both sides at30m spacing; ZSS1 on tail pulley. No numeric trip settings inferred.')]:
            fact(s,p,v)
        fact(takeup,'source_discrepancy','GA schedule gives20mm rope,185kN minimum breaking force and440mm sheave. Review p3 requests231kN minimum and questions20mm rope; p4 reply says sheave not required. Final rope/sheave selection is unresolved; do not treat drawing schedule as a reconciled final selection.')
        fact(chute,'source_discrepancy','View D-D labels KB-RG-3/4 and KB-RPG-3/4 on both sides although screens are EBD1/2 under2A and EBD3/4 under2B. Gate identities follow separately sourced175001 topology; this repeated GA callout is not proof of cross-lane flow.',inlet)
        for a,b in zip([motor,fluid,gear,low,pulley],[fluid,gear,low,pulley,belt]):
            fact(a,'mechanically_drives',b,drive,True,'mechanical','Source-drawn head drive train; design connection.')
        fact(owner,'feeds',chute,inlet,True,'material','Head discharge at UEE-1; gates retain their separate selected-path conditions.')
    evs=json.loads((ROOT/'output/plant-enrichment/B06/review/doc_030c8f82fb674548a4dc-evidence.json').read_text(encoding='utf8'))
    # Discrepancies cite their review pages as well as the displayed GA table.
    for op in ops:
        if op.get('predicate')=='source_discrepancy' and op['subject'].endswith('_takeup'):
            op['evidence'] += [dict(evidence_id=e['id'],quote='',region=[.1,.1,.97,.96]) for e in evs if e['page'] in [3,4]]
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'accepted/commit-log.json').exists()
    (OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=DOC,baseline_version=635,baseline_model='output/plant-enrichment/B06/ga-175012/baseline-model.json',expected_new_components=26,visual_ids=[e['id'] for e in evs if e['page'] <= 4],body=dict(summary='B06 Tier1 conveyor2A/B main drive, belt support, take-up, cleaners, protections and screening chute',operations=ops,intake_assessment=dict(route='mixed',purpose='Complete both conveyor2 main assemblies without vendor-internal expansion',questions=['What are the major assemblies and head-end screening interfaces of each conveyor2 lane?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Original GA pp1-2 visually reviewed with enlarged drive/schedule/screen views; review replies pp3-5 read. Existing root headline ratings, TP1 receiving chutes, QB1/2 and EAT1/2 retained; AT1/2 remain on conveyor1.','Rope/sheave discrepancy and duplicated gate callout explicitly qualified. Detailed settings, idler/BOM rows, internals and selection reconciliation deferred to Pass B. Screening gate outlet edges use the separate control topology source.'])))
    (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'components':26,'operations':len(ops)}))


if __name__=='__main__':
    main()
