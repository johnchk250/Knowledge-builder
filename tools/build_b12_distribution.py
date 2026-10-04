"""Reviewed conveyor4/TP4 Tier1 packages, one original per proposal."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('scope',choices=['conveyor','house','utilities'])
    ap.add_argument('--baseline',required=True)
    args=ap.parse_args()
    m=json.loads((ROOT/args.baseline).read_text(encoding='utf8'))
    labels={e['label']:e['canonical_id'] for e in m['entities']}
    scope=args.scope
    doc={'conveyor':'doc_a02d56b879734b5db189','house':'doc_9bd6e66e9fbb43468184','utilities':'doc_492c079544304e2da177'}[scope]
    evs=json.loads((ROOT/f'output/plant-enrichment/B12/review/{doc}-evidence.json').read_text(encoding='utf8'))
    ev={e['page']:e['id'] for e in evs}
    basis={'conveyor':'175014 Rev4 approved16-Oct-2019, conveyor4A/B GA; design only.','house':'175036 Rev3 approved18-Dec-2018,TP4 GA; design only.','utilities':'175289 Rev2 FIO13-Sep-2019,TP4 DFDS/SW/PW layout; information design,not field-verified.'}[scope]
    house=labels['UEF-4'];ops=[];nodes=[]
    active=[a for a in m['assertions'] if not a['retirement'] and not a['suppressed']]

    def proof(page,region):
        return dict(origin='explicit',confidence=.98,evidence=[dict(evidence_id=ev[page],quote='',region=region)])

    def fact(s,p,v,page=1,region=None,obj=False,net=None,condition=None):
        region=region or [.035,.035,.97,.80]
        ctx=dict(kind='classification' if p=='instance_of' else 'specification',basis=basis)
        if net:ctx.update(kind='connection',network=net,verification='documented',condition=condition)
        ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=ctx,**proof(page,region)))

    def new(key,label,typ,owner,page=1,region=None,place=None):
        assert label not in labels
        id='tmp_b12_'+key.replace('-','_');region=region or [.035,.035,.97,.80]
        ops.append(dict(op='entity',id=id,label=label,**proof(page,region)))
        fact(id,'instance_of',typ,page,region);fact(id,'part_of',owner,page,region,True)
        if place:fact(id,'located_at',place,page,region,True)
        nodes.append(id);return id

    def retire(a,reason,page=1,region=None):
        ops.append(dict(op='retire',assertion_id=a['id'],reason=reason,**proof(page,region or [.035,.035,.97,.80])))

    if scope=='conveyor':
        schedule=[.035,.02,.278,.97];drive=[.42,.65,.59,.78]
        for n,lane in enumerate(['A','B'],1):
            owner=labels['EAC-4'+lane];head=labels['UEF-5'];ftr=labels['FTR-'+str(n)]
            specs=[('motor','main drive motor','electric_motor','BHEL squirrel-cage motor500kW,1488rpm,415V perGA schedule; voltage is not a power-feeder connection.'),('fluid','scoop fluid coupling','fluid_coupling','Premium PST-570 scoop coupling.'),('gear','main gearbox','gearbox','Premium B3 450 bevel-helical gearbox,17.1:1.'),('low','low-speed coupling','coupling','GBM RG-12 geared coupling.'),('brake','service thruster brake','thruster_drum_brake','GA EBTF-600/G Elektromag thruster brake; existing design-calculation EBTM-600/G wording retained,not silently reconciled.'),('head','head drive pulley','pulley','One800mm diameter x2200mm face,2700mm bearing centres,12mm diamond-groove lagging.'),('belt','conveyor belting','conveyor_belt',f'2000mm N/N HD1250/4,FR5mm top/2mm bottom; endless length{382.350 if lane=="A" else 388.300:.3f}m.'),('idler','idler and belt-support assembly','functional_assembly','Transition,impact,carrying,self-aligning,self-cleaning and return idler groups; gallery deck/seal plates and skirts. Individual idler rows deferred.'),('tail','tail bend and snub pulley group','functional_assembly','Schedule groups five630mm diameter x2200mm face pulleys per conveyor as tail/bend/snub; separate take-up and fixed-tripper pulleys are not included in this count.'),('takeup','vertical gravity take-up assembly','take_up_assembly','5000mm travel with mark-up scale; one630mm take-up pulley;10000kg design counterweight per conveyor.'),('cleaners','head tripper and tail cleaner group','functional_assembly','Two primary and two secondary scrapers per conveyor,at main/tripper discharge pulleys; two internal V-ploughs near tail. No duplicated cleaner sets under tripper.'),('protection','PCS BSS and ZSS protection group','functional_assembly','BSS4 pairs at40m intervals; PCS6 pairs at30m spacing; one tail-pulley ZSS per conveyor. Numeric settings deferred.'),('chute','head flow-divider inlet chute','chute_interface','Head discharge atTP5 to its own FD5/6; intermediate fixed-tripper branch remains atTP4.')]
            ids={}
            for key,name,typ,desc in specs:
                place=head if key in ['motor','fluid','gear','low','brake','head','takeup','chute'] else None
                region=drive if key in ['motor','fluid','gear','low','brake'] else schedule
                id=new(lane+key,'EAC-4'+lane+' '+name,typ,owner,4,region,place)
                fact(id,'assembly_arrangement',desc,4,schedule);ids[key]=id
            for a,b in zip(['motor','fluid','gear','low','head'],['fluid','gear','low','head','belt']):fact(ids[a],'mechanically_drives',ids[b],4,drive,True,'mechanical','Source-drawn main head drive train atTP5.')
            fact(owner,'material_flow_to',ids['chute'],2,[.57,.10,.79,.39],True,'material','Main head discharge beyondTP4 on the same continuous belt.')
            fact(ids['chute'],'material_flow_to',labels['KB-FD-'+str(n+4)],2,[.57,.10,.79,.39],True,'material','Conveyor4'+lane+' to its own FD'+str(n+4)+' atTP5; preserve existing downstream conditions.')
            trip=new(lane+'tripper','FTR-'+str(n)+' pulley hood and discharge assembly','functional_assembly',ftr,4,schedule,house)
            fact(trip,'assembly_arrangement','One800mm fixed-tripper discharge pulley and two219mm deflector rollers per conveyor; tripper pulley/hood redirects the same belt atTP4. This is not a second conveyor or a powered travelling tripper.',4,schedule)
            fact(ftr,'located_at',house,1,[.60,.14,.98,.42],True)
            for a in active:
                if a['canonical_subject']==ftr and a['predicate']=='part_of' and a['canonical_object']==labels['Maitree Coal Handling Plant']:retire(a,'Retain existing own-conveyor owner; GA proves FTR1/2 belong to their respective continuous EAC4 belt.',1)
                if a['canonical_subject']==owner and a['predicate']=='material_flow_to' and a['canonical_object']==head:retire(a,'Aggregate building route bypasses actual FD5/6; exact own-divider route retained and source-drawn chute added.',2)
        gaps=['All4 GA sheets and reviewp5 read. Headline root ratings already accepted and retained. Main drive/takeup atTP5; fixed tripper atTP4.','Drive/BOM internals,settings and EBTF/EBTM source wording deferred. No head stream mixed with other lane.']
    elif scope=='house':
        for n,lane in [(3,'A'),(4,'B')]:
            fd=labels['KB-FD-'+str(n)];ftr=labels['FTR-'+str(n-2)];owner=labels['EAC-4'+lane]
            fact(fd,'part_of',house,1,obj=True)
            for a in active:
                if a['canonical_subject']==fd and a['predicate']=='part_of' and a['canonical_object']==labels['Maitree Coal Handling Plant']:retire(a,'TP4 GA identifies FD3/4 as local divider assemblies; plant containment is viaTP4.')
            drive=new('fd'+str(n),'KB-FD-'+str(n)+' geared actuator assembly','functional_assembly',fd,3,[.70,.83,.965,.94],house)
            fact(drive,'mechanically_drives',fd,3,[.70,.83,.965,.94],True,'mechanical','Review reply identifies gear motor as maintainable divider drive; no power rating inferred.')
            for key,name,src,dst,condition in [('in','fixed-tripper inlet chute',ftr,fd,'Own-lane tripper discharge to its divider.'),('through','same-belt onward chute',fd,owner,'Through-flow beyond fixed tripper on the SAME continuous EAC4'+lane+'; not recirculation or a separate belt. Existing control REV through/FWD stacking qualification retained.'),('yard','Yard3 discharge chute',fd,labels['EAC-11'],'Full or partial stacking to Yard3/EAC11; divided remainder continues on same own EAC4 belt.')]:
                id=new(str(n)+key,'KB-FD-'+str(n)+' '+name,'chute_interface',fd,1,[.06,.13,.59,.46],house)
                fact(src,'material_flow_to',id,1,[.06,.13,.59,.46],True,'material',condition);fact(id,'material_flow_to',dst,1,[.06,.13,.59,.46],True,'material',condition)
        for tag,rating,service in [('EH-1',3.5,'EAC4A/B fixed-tripper discharge pulleys'),('EH-2',3.5,'EAC4A/B fixed-tripper bend pulleys'),('EH-3',4,'EAC11 tail pulley'),('MH-1',1,'flow dividers')]:
            id=new(tag,'UEF-4 '+tag+' maintenance hoist','manual_hoist' if tag.startswith('MH') else 'electric_hoist',house,1,[.285,.89,.553,.976],house)
            fact(id,'assembly_arrangement',f'{rating}t schedule design capacity for {service}; no lifting certification inferred. EH2 planp2 says2.5t versus schedulep1=3.5t; retained discrepancy.',1,[.285,.89,.553,.976])
        id=new('access','UEF-4 platforms stairs and maintenance access','maintenance_access_assembly',house,1,place=house)
        fact(id,'assembly_arrangement','Platforms,stairs,hoist maintenance platforms,removable floor openings and divider-access stool shown; design arrangement,not certified clearance.')
        tank=new('tank','UEF-4 potable-water tank and tap assembly','functional_assembly',house,1,[.045,.075,.155,.18],house)
        fact(tank,'assembly_arrangement','GA175036 shows250L potable tank; later piping175289 shows300L. Same local tank assembly; final capacity unresolved.',1,[.045,.075,.155,.18])
        drain=new('drain','UEF-4 garland drain and downcomer group','functional_assembly',house,1,[.045,.81,.278,.895],house)
        fact(drain,'equipment_role','GA calls for garland drain around building and downcomers. Existing EAE4/UEF4 common runoff sump identity retained; local pipe endpoint not asserted without source tracing.',1,[.045,.81,.278,.895])
        gaps=['Principal TP4 GA pp1-2 and repliespp3-5 reviewed. Four local hoists,access,tank and drain group atTier1.','EH2 schedule3.5t versus plan2.5t and tank250L versus later300L retained; deeper rails/civil/clearance review deferred. Existing runoff sump boundary not duplicated.']
    else:
        mains=[]
        for fluid in ['air','water']:
            main=new(fluid,'UEF-4 local DFDS '+fluid+' main','utility_header',house,1,[.05,.05,.62,.47],house);mains.append(main)
            fact(labels['UEF-3 local DFDS '+fluid+' main'],'utility_supply_to',main,1,[.05,.05,.62,.47],True,'utility','Layout explicitly routes DFDS fromUEF3 throughUEF4; common System1 already reachesUEF3. No System2 crossover.')
        for n,target in [(21,'EAC-4A'),(22,'EAC-4A'),(23,'EAC-11'),(24,'EAC-4B'),(25,'EAC-4B'),(26,'EAC-11')]:
            fas=labels[f'UEF-4 FAS-{n}'];pru=labels[f'UEF-4 PRU-{n}']
            for id in [fas,pru]:fact(id,'part_of',house,2,obj=True);fact(id,'located_at',house,2,obj=True)
            for main in mains:fact(main,'utility_supply_to',fas,2,[.05,.04,.52,.57],True,'utility','Local paired air/water branch to existing numberedFAS; FAS-to-PRU route reused.')
            group=new('spray'+str(n),f'UEF-4 spray-header group downstream PRU-{n}','functional_assembly',house,1,[.05,.05,.87,.79],house)
            fact(pru,'utility_supply_to',group,2,[.05,.04,.52,.57],True,'utility','Exact same-number PRU feeds layout spray-header group.')
            fact(group,'serves_equipment',labels[target],2,[.05,.04,.52,.57],True,'utility','Layout consumer '+target+'; no simultaneous-all-sprays operation inferred.')
            fact(group,'equipment_role','Tripper discharge spray zone.' if n in [21,24] else 'Same-belt receiving spray zone.' if n in [22,25] else 'Yard3/EAC11 receiving spray zone.',1,[.05,.05,.87,.79])
        wash=new('wash','UEF-4 service-water hose and washdown group','functional_assembly',house,2,[.08,.64,.17,.755],house)
        fact(wash,'assembly_arrangement','Service-water tapping arrangement and hose boxes; layout shows supply fromUEF3 and continuation toUEF5. Existing SW1 common supply atUEF4 retained.',2,[.08,.64,.17,.755])
        fact(labels['UEF-4 potable-water tank and tap assembly'],'document_note','Later175289 FIO layout labels300L and PVC tank detail,versus175036 GA250L. Potable supply drawn fromUEF5 towardUEF3; existing commonPW connection retained,not a second tank.',1,[.06,.06,.77,.47])
        fact(house,'document_note','175289 local utility layout is FIO13-Sep-2019. Six FAS/PRU pairs reused; common DFDS source remainsSystem1 viaUEF3. Local SW/PW branches not individually promoted to physical edges beyond the existing building supply.',1)
        gaps=['All3 piping pages reviewed. Existing12 FAS/PRU records receive local ownership/location; no duplicates. Six grouped application zones; nozzle/valve BOM remains depth.','SW/PW at common building boundary retained; exact local pipe branches and tank capacity discrepancy deferred. LayoutFIO qualification retained.']
    out=ROOT/'output/plant-enrichment/B12'/scope;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'accepted/commit-log.json').exists()
    (out/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=doc,baseline_version=m['version'],baseline_model=str((out/'baseline-model.json').relative_to(ROOT)),expected_new_components=len(nodes),visual_ids=[e['id'] for e in evs],body=dict(summary='B12 Tier1 '+scope+' major equipment and locations',operations=ops,intake_assessment=dict(route='mixed',purpose='Conveyor4/TP4 breadth with same-belt continuation and source-specific services',questions=['What major assemblies and routes belong to conveyor4 and TP4?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=gaps)))
    (out/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print(dict(scope=scope,components=len(nodes),operations=len(ops),baseline=m['version']))


if __name__=='__main__':main()
