"""Source-reviewed Tier 1 assemblies for conveyor 3, guarded at v644."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/plant-enrichment/B10/ga-175013'
DOC = 'doc_3eab668d697f4e4598c8'
EV = 'ev_a2fbfdaf239949dc99e5'


def main():
    m = json.loads((ROOT/'output/plant-enrichment/B09/utilities/accepted/model.json').read_text(encoding='utf8'))
    assert m['version'] == 644
    ops = []
    schedule = [.795, .047, .96, .70]
    drive = [.49, .58, .65, .67]
    inlet = [.36, .43, .52, .75]

    def proof(region):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=EV, quote='', region=region)])

    def fact(s, p, v, region=schedule, obj=False, network=None, condition=None):
        ctx = dict(kind='classification' if p == 'instance_of' else 'specification', basis='175013 Rev3,29-Oct-2018; approved26-Nov-2018. Original GA/schedule, design applicability EAC-3A and EAC-3B; not an installed-condition inspection.')
        if network:
            ctx.update(kind='connection', network=network, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'):v}, context=ctx, **proof(region)))

    for lane, owner in [('A','ent_9f1ca0f604de4bdda3a5'), ('B','ent_fb331701a6c04437842b')]:
        def new(key, label, typ, region=schedule, place=None):
            id = 'tmp_b10_'+lane.lower()+'_'+key
            ops.append(dict(op='entity', id=id, label=f'EAC-3{lane} {label}', **proof(region)))
            fact(id,'instance_of',typ,region)
            fact(id,'part_of',owner,region,True)
            if place:
                fact(id,'located_at',place,region,True)
            return id
        head = 'ent_d8d8763a4bc2400882b9'
        motor = new('motor','main drive motor','electric_motor',drive,head)
        fluid = new('fluid','scoop fluid coupling','fluid_coupling',drive,head)
        gear = new('gear','main gearbox','gearbox',drive,head)
        low = new('low','low-speed coupling','coupling',drive,head)
        brake = new('brake','service thruster brake','thruster_drum_brake',drive,head)
        pulley = new('head','head drive pulley','pulley',inlet,head)
        belt = new('belt','conveyor belting','conveyor_belt')
        support = new('support','idler and belt-support assembly','functional_assembly')
        tails = new('tail_bends','tail and bend/snub pulley group','functional_assembly')
        takeup = new('takeup','vertical gravity take-up assembly','take_up_assembly')
        cleaners = new('cleaners','head and tail belt-cleaner group','functional_assembly')
        protection = new('protection','PCS BSS and ZSS protection group','functional_assembly')
        chute = new('head_chute','flow-divider inlet chute','chute_interface',inlet,head)
        for s,p,v in [
            (motor,'assembly_arrangement','One BHEL squirrel-cage motor per conveyor:380kW HT,3.3kV; schedule speed1488rpm.'),
            (fluid,'equipment_model','PST570 scoop type fluid coupling'),
            (gear,'assembly_arrangement','Premium B3-450 bevel helical gearbox; ratio17:1.'),
            (low,'equipment_model','RG10 low-speed coupling'),
            (brake,'equipment_model','EBTM-500/DS/DG electro-hydraulic thruster brake'),
            (pulley,'assembly_arrangement','One drive pulley per conveyor:800mm diameter,2200mm face,2700mm bearing centres.'),
            (belt,'assembly_arrangement',f'NN1000/5,2000mm width; endless length{327.35 if lane == chr(65) else 333.35}m; FR cover5mm top/2mm bottom.'),
            (support,'assembly_arrangement','Transition,impact,carrying,self-aligning,self-cleaning return,return and flat-return idler groups; gallery deck/seal plate and receiving skirt shown. Individual idler/BOM breakdown deferred.'),
            (tails,'assembly_arrangement','One tail pulley plus three bend/snub pulleys; all630mm diameter x2200mm face. Schedule tail plus take-up count2 is split between this group and the gravity take-up assembly, not two tails.'),
            (takeup,'assembly_arrangement','Vertical gravity take-up with mark-up scale;4600mm travel; one630mm take-up pulley; schedule design counterweight11000kg per conveyor.'),
            (cleaners,'assembly_arrangement','One spring-loaded primary and one secondary scraper at discharge pulley; one internal V-plough near tail pulley, per conveyor.'),
            (protection,'assembly_arrangement','Per conveyor: BSS4 pairs on both sides at40m intervals; PCS5 pairs on both sides at30m spacing; ZSS1 on tail pulley. No numeric trip settings inferred.')]:
            fact(s,p,v)
        for a,b in zip([motor,fluid,gear,low,pulley],[fluid,gear,low,pulley,belt]):
            fact(a,'mechanically_drives',b,[.35,.43,.65,.75],True,'mechanical','Source-drawn head drive train; design connection.')
        fact(owner,'feeds',chute,inlet,True,'material','Head discharge at UEF-3 to its own flow divider; existing selected branch conditions retained.')
    evs=json.loads((ROOT/'output/plant-enrichment/B10/review/doc_3eab668d697f4e4598c8-evidence.json').read_text(encoding='utf8'))
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'accepted/commit-log.json').exists()
    (OUT/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=DOC,baseline_version=644,baseline_model='output/plant-enrichment/B10/ga-175013/baseline-model.json',expected_new_components=26,visual_ids=[e['id'] for e in evs if e['page'] <= 4],body=dict(summary='B10 Tier1 conveyor3A/B main drive, belt support, take-up, cleaners, protections and flow-divider inlet chute',operations=ops,intake_assessment=dict(route='mixed',purpose='Complete both conveyor3 main assemblies without vendor-internal expansion',questions=['What are the major assemblies and flow-divider inlet interfaces of each conveyor3 lane?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Original GA pp1-2 visually reviewed with enlarged drive/schedule views. Existing root headline ratings and UEE1 screen discharge chutes retained.','Detailed settings,idler/BOM rows,internals and tension calculations deferred to Pass B. Existing FD1/2 outlet branches remain separately source-qualified.'])))
    (OUT/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'components':26,'operations':len(ops)}))


if __name__=='__main__':
    main()
