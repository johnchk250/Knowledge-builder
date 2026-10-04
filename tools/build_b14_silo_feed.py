"""Reviewed Tier1 conveyor6/TP7/analyser packages; no historical replay."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    'conveyor': ('doc_c91eac5d4c104264801f', '175016 Rev1 approved23-Nov-2018 conveyor6 GA'),
    'house': ('doc_f6e89f3b3d3b40eb8d80', '175039 Rev6 approved18-Oct-2019 TP7 GA'),
    'utilities': ('doc_d157f03e84e84c068b06', '175292 Rev2 FIO16-Sep-2019 TP7 utilities'),
    'analysers': ('doc_740734a151bd4c00b655', '175330 Rev0 FIO18-Oct-2019 analyser belt/stringer GA'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    ap.add_argument('--baseline', required=True)
    args = ap.parse_args()
    m = json.loads((ROOT/args.baseline).read_text(encoding='utf8'))
    labels = {e['label']: e['canonical_id'] for e in m['entities']}
    active = [a for a in m['assertions'] if not a['retirement'] and not a['suppressed']]
    doc, basis = DOCS[args.scope]
    evs = json.loads((ROOT/f'output/plant-enrichment/B14/review/{doc}-evidence.json').read_text(encoding='utf8'))
    ev = {e['page']: e['id'] for e in evs}
    ops, nodes = [], []
    house = labels['UEF-7']; silo = labels['Coal Blending Silo House']
    region = [.04,.035,.965,.80]

    def proof(page=1, r=region):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[page],quote='',region=r)])

    def fact(s,p,v,page=1,r=region,obj=False,net=None,condition=None):
        ctx = dict(kind='classification' if p=='instance_of' else 'specification',basis=basis+'; design evidence,not field/as-built verification.')
        if net: ctx.update(kind='connection',network=net,verification='documented',condition=condition)
        ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=ctx,**proof(page,r)))

    def new(key,label,typ,owner,page=1,r=region,place=None):
        assert label not in labels,label
        id='tmp_b14_'+args.scope+'_'+key.replace('-','_')
        ops.append(dict(op='entity',id=id,label=label,**proof(page,r)))
        fact(id,'instance_of',typ,page,r);fact(id,'part_of',owner,page,r,True)
        if place: fact(id,'located_at',place,page,r,True)
        nodes.append(id);return id

    def retire(a,reason,page=1,r=region):
        ops.append(dict(op='retire',assertion_id=a['id'],reason=reason,**proof(page,r)))

    def local_owner(id):
        for predicate in ['part_of','located_at']:
            if not any(a['canonical_subject']==id and a['predicate']==predicate and a['canonical_object']==house for a in active): fact(id,predicate,house,obj=True)
        for a in active:
            if a['canonical_subject']==id and a['predicate']=='part_of' and a['canonical_object']==labels['Maitree Coal Handling Plant']:retire(a,'Local GA identifies TP7 owner; plant membership retained throughTP7.')

    if args.scope=='conveyor':
        schedule=[.756,.052,.945,.785];drive=[.265,.305,.746,.835];head=[.06,.13,.347,.625]
        for lane in ['A','B']:
            owner=labels['EBA-6'+lane]
            specs=[
                ('motor','main drive motor','electric_motor','BHEL squirrel-cage315kW,1488rpm,3.3kV three-phase supply; voltage alone is not a feeder connection.'),
                ('fluid','scoop fluid coupling','fluid_coupling','Premium PST-530 scoop coupling.'),
                ('gear','main gearbox','gearbox','Premium B3 400 bevel-helical gearbox23.2:1.'),
                ('low','low-speed coupling','coupling','GBM RG-10 geared coupling.'),
                ('brake','service thruster brake','thruster_drum_brake','Elektromag EBTM500/F thruster brake; numeric settings deferred.'),
                ('head','head drive pulley','pulley','One800mm diameter x1600mm face,2100mm bearing centres,12mm diamond-groove lagging.'),
                ('belt','conveyor belting','conveyor_belt',f'1400mm N/N HD1250/4,FR5/2mm covers; endless length {772.672 if lane=="A" else 758.677}m.'),
                ('idlers','idler and belt-support assembly','functional_assembly','Transition,impact,carrying,self-aligning,self-cleaning and return idler groups,skirt and continuous deck/seal plates. Lane-specific detailed row counts deferred.'),
                ('tail','tail and bend snub pulley group','functional_assembly','One tail plus three bend/snub pulleys,all630mm diameter x1600mm face. Schedule tail plus take-up quantity2 splits one each; two219mm deflector rollers.'),
                ('takeup','vertical gravity take-up assembly','take_up_assembly','VGTU atUEE2/silo-house head end,10100mm travel,one630mm take-up pulley and8000kg cast-iron design counterweight; guards,partition and shock-absorber support shown.'),
                ('cleaners','head and tail belt-cleaner group','functional_assembly','One primary polyurethane and one secondary tungsten-carbide cleaner at head,one internal tail V-plough. Reviewp8 and revised schedule agree on these materials.'),
                ('protection','PCS BSS and ZSS protection group','functional_assembly',f'BSS {9 if lane=="A" else 8} pairs at50m intervals; PCS {14 if lane=="A" else 13} pairs at30m;one tail ZSS. Preserve A/B difference; settings deferred.'),
                ('chute','silo inlet discharge chute','chute_interface','Own head discharge into '+('EBB2' if lane=='A' else 'EBB1')+'; preserve accepted opposite-number silo crossover.'),
            ]
            ids={}
            for key,name,typ,desc in specs:
                id=new(lane+key,'EBA-6'+lane+' '+name,typ,owner,4,schedule)
                fact(id,'assembly_arrangement',desc,4,schedule)
                if key in ['motor','fluid','gear','low','brake','head','takeup','chute']:fact(id,'located_at',silo,1,head,True)
                ids[key]=id
            for a,b in zip(['motor','fluid','gear','low','head'],['fluid','gear','low','head','belt']):fact(ids[a],'mechanically_drives',ids[b],3,drive,True,'mechanical','Main head drive train atUEE2.')
            for src,dst in [(owner,ids['chute']),(ids['chute'],labels['EBB-2' if lane=='A' else 'EBB-1'])]:fact(src,'material_flow_to',dst,1,head,True,'material','Conveyor6'+lane+' discharges to its documented opposite-number silo; accepted high-level permissive retained.')
            for a in active:
                if a['canonical_subject']==owner and a['predicate']=='material_flow_to' and a['canonical_object']==silo:retire(a,'Aggregate building edge bypasses the exact silo inlet;6A-toEBB2 and6B-toEBB1 remain.',1,head)
        gaps=['All four GA sheets visually reviewed and attached reviewpp5-8 read. Headline ratings reused. No duplicate silo/hoists/tanks. Vendor BOM,settings and detailed gallery drainage remain PassB.']
    elif args.scope=='house':
        for n in [5,6]:
            fg=labels[f'FG-{n}'];local_owner(fg)
            actuator=new(f'fg{n}',f'FG-{n} rotary actuator','gate_actuator',fg,place=house)
            fact(actuator,'mechanically_drives',fg,obj=True,net='mechanical',condition='Actuator named by local MH1 hoist schedule.')
            chute=new(f'out{n}',f'FG-{n} selector outlet chute group','chute_interface',fg,place=house)
            fact(fg,'material_flow_to',chute,obj=True,net='material',condition='Selected6A or6B outlet; alternatives,not simultaneous.')
            for lane in ['A','B']:fact(chute,'material_flow_to',labels['EBA-6'+lane],obj=True,net='material',condition=f'FG{n} selected EBA6{lane}; existing directional-control qualifications remain.')
        for tag,rating,service in [('EH-1','10t','5A/B head/snub pulleys and drive units'),('EH-2','2.5t','6A/B tail pulleys'),('MH-1','1t','FG5/6 actuators')]:
            r=[.05,.91,.22,.965];id=new(tag,'UEF-7 '+tag+' maintenance hoist','manual_hoist' if tag.startswith('MH') else 'electric_hoist',house,1,r,house)
            fact(id,'assembly_arrangement',rating+' design capacity for '+service+'; no field lifting certification inferred.',1,r)
        access=new('access','UEF-7 platforms stairs and maintenance access','maintenance_access_assembly',house,place=house)
        fact(access,'assembly_arrangement','GA access stairs,removable floor openings,tail-pulley mesh guards,tank ladder and monorails. Review asks2000mm clear walkway,reply1700mm; existing design qualification retained.',2)
        tank=new('tank','UEF-7 potable-water tank and tap assembly','functional_assembly',house,1,[.08,.06,.47,.20],house)
        fact(tank,'assembly_arrangement','300L tank per revisedGA; reviewp2 confirms revision from250L. No installed-condition inspection inferred.',1,[.08,.06,.47,.20])
        drain=new('drain','UEF-7 garland drain and downcomer group','functional_assembly',house,place=house)
        fact(drain,'equipment_role','Local downcomers/debris chute and building garland drain shown. No untraced downstream pipe endpoint invented.')
        for a in active:
            if a['canonical_subject']==house and a['predicate']=='material_flow_to':retire(a,'Use explicit FG5/6 branches; aggregate building route bypasses selection conditions.')
        gaps=['Principal GApp1 and reviewp2 read. Gate alternatives and local hoists/access/tank/drain atTier1; detailed rail/civil work deferred.']
    elif args.scope=='utilities':
        mains=[]
        for fluid in ['air','water']:
            id=new(fluid,'UEF-7 local DFDS '+fluid+' main','utility_header',house,place=house);mains.append(id)
            fact(labels['UEF-6 local DFDS '+fluid+' main'],'utility_supply_to',id,obj=True,net='utility',condition='TP6 continuation; layout writes UAF6 while conveyor/GAs establishUEF6. Existing common System1 upstream source retained.')
        for n,target in {41:'EAC-5A',42:'EBA-6A',43:'EBA-6B',44:'EAC-5B',45:'EBA-6A',46:'EBA-6B'}.items():
            fas=labels[f'UEF-7 FAS-{n}'];pru=labels[f'UEF-7 PRU-{n}'];local_owner(fas);local_owner(pru)
            r=[.055,.045,.475,.94]
            for main in mains:fact(main,'utility_supply_to',fas,2,r,True,'utility','Paired air/water feed to existing FAS; existing same-number PRU route retained.')
            spray=new(f'spray{n}',f'UEF-7 spray-header group downstream PRU-{n}','functional_assembly',house,2,r,house)
            fact(pru,'utility_supply_to',spray,2,r,True,'utility','Same-number PRU application group; no pressure setting inferred.')
            fact(spray,'serves_equipment',labels[target],2,r,True,'utility','5A/B discharge or6A/B receipt; piping calls outgoing EAC6,canonical route/GAs identify EBA6. No duplicate EAC6 created.')
            fact(spray,'equipment_role','Head discharge zone.' if n in [41,44] else 'Receiving spray zone for selected6A/B outlet.',2,r)
        wash=new('wash','UEF-7 service-water hose and washdown group','functional_assembly',house,place=house)
        fact(wash,'assembly_arrangement','Hose box and washdown tapping. Drawing shows local SW/PW fromPH2 plus UAF6/TP16/17 continuations; existing common building supplies retained without inventing local physical branch assignments.')
        fact(labels['UEF-7 potable-water tank and tap assembly'],'document_note','Piping175292 tank/detail300L agrees with revisedGA175039.',1,[.35,.05,.90,.75])
        gaps=['Both piping sheets visually reviewed and reviewp3 read. FIO status,UAF6 andEAC6 labels qualified. TwelveFAS/PRUs reused;6 application groups only. Valve/nozzle BOM,settings and exact local SW/PW branches deferred.']
    else:
        r=[.565,.055,.945,.50]
        for ref in ['Coal Analyser Assembly - 1400mm Belt','RTI Cross-Belt Prompt Gamma Neutron Activation Coal Analyser']:
            id=labels[ref]
            for a in active:
                if a['canonical_subject']==id and a['predicate']=='instance_of' and a['value']=='coal_analyser':retire(a,'Generic assembly/vendor record is a design reference,not an additional physical analyser. Existing numbered units remain distinct.',1,r)
            fact(id,'instance_of','equipment_design_reference',1,r)
            fact(id,'document_note','RTI1400mm analyser design applies to6A/B,16A/B and17A/B. Generic record is not another installed unit or a serial-number identity merge.',1,[.08,.79,.945,.94])
        for n,lane in [(1,'A'),(2,'B')]:
            owner=labels[f'CV-{n}'];conv=labels['EBA-6'+lane]
            # Existing topology namesCV1/2; GA establishes host-specific design applicability.
            fact(labels['Coal Analyser Assembly - 1400mm Belt'],'design_detail_applies_to',owner,1,[.08,.79,.945,.94],True)
            fact(owner,'part_of',conv,1,[.08,.79,.945,.94],True)
            for a in active:
                if a['canonical_subject']==owner and a['predicate']=='part_of' and a['canonical_object']==labels['Maitree Coal Handling Plant']:retire(a,'Use accepted host conveyor as physical assembly owner; GA explicitly applies to6A/B.')
            for key,name,desc in [('frame','frame and shielding assembly','Frame,HDPE side/top shields and existing site-specific stringer interface; fasteners not individually decomposed.'),('detector','detector and cradle assembly','Single detector cradle assembly below belt,shown in sectionBB; calibration and electronics internals deferred.'),('cabinet','electrical cabinet assembly','Local cabinet and mounting frame; existing CV-toDCS interface retained without invented power/wiring.'),('hood','hood and access assembly','Hinged hood with gas-strut/prop support and solar shield; no operational servicing instruction inferred.'),('holder','source-holder assembly','Source-holder assembly identified byBOM23; no isotope,activity or loaded-source status asserted from this mechanical drawing.')]:
                id=new(str(n)+key,f'CV-{n} '+name,'functional_assembly',owner,1,r,conv)
                fact(id,'assembly_arrangement',desc,1,r)
            fact(owner,'document_note','175330FIO design explicitly covers1400mm6A/B; accepted CV1-on6A/CV2-on6B mapping reused. These are measuring assemblies,not material-flow destinations.',1,[.08,.79,.945,.94])
        gaps=['All five analyser GA sheets visually reviewed. Existing CV1/2 topology retained; two generic records classified as design references,not merged. Data/catalogue175331 and QAP found and deferred for internal electronics,calibration and performance; no new claims based on unread catalogue pages. Other conveyor analysers remain separate future batches.']
    out=ROOT/'output/plant-enrichment/B14'/args.scope;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'accepted/commit-log.json').exists()
    (out/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=doc,baseline_version=m['version'],baseline_model=(out/'baseline-model.json').relative_to(ROOT).as_posix(),expected_new_components=len(nodes),visual_ids=[e['id'] for e in evs],body=dict(summary='B14 Tier1 '+args.scope,operations=ops,intake_assessment=dict(route='mixed',purpose='Major conveyor6/TP7/analyser assemblies and exact silo crossover',questions=['What major assemblies and exact transfer interfaces are source-supported?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=gaps)))
    (out/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print(dict(scope=args.scope,components=len(nodes),operations=len(ops),baseline=m['version']))


if __name__=='__main__':main()
