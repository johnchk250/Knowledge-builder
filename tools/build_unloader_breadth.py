"""Build reviewed175155 major assemblies, explicitly scoped to numbered machines."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC='doc_1518e219127b4b0eaa3a'
OWNERS={1:'ent_1a57e15407c145a19284',2:'ent_f319b7a72a2e4c85a617',3:'ent_9b33c14cee7f4d749335'}
SHUTTLES={1:'ent_b4857f81859e46e98a72',2:'ent_9a86610c5f134c8eb32e',3:'ent_63115d1381984790826e'}
JETTY='ent_9b2045acf7044ad9b229'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--units',nargs='+',type=int,required=True);ap.add_argument('--baseline',required=True);ap.add_argument('--version',type=int,required=True);ap.add_argument('--batch',required=True);args=ap.parse_args()
    m=json.loads((ROOT/args.baseline).read_text(encoding='utf8'));m=m.get('model',m);assert m['version']==args.version
    out=ROOT/f'output/plant-enrichment/{args.batch}/ga-175155';ops=[];visual=set();created=[]
    labels={e['label']:e['canonical_id'] for e in m['entities']}
    def proof(ev,region):
        visual.add(ev);return dict(origin='explicit',confidence=.98,evidence=[dict(evidence_id=ev,quote='',region=region)])
    def fact(s,p,v,ev,region,obj=False,network=None,condition=None):
        ctx=dict(kind='classification' if p=='instance_of' else 'specification',basis='175155 GA74042951,Type1 pp8-9 / Type2 pp10-11,rope arrangement p12; source-specific revisions retained; package approved14-Dec-2020. Design only.')
        if network:ctx.update(kind='connection',network=network,verification='documented',condition=condition)
        ops.append(dict(op='assert',subject=s,predicate=p,**{('object_entity' if obj else 'value'):v},context=ctx,**proof(ev,region)))
    def new(id,label,typ,owner,ev,region):
        assert label not in labels,('Already modeled',label)
        created.append(id);ops.append(dict(op='entity',id=id,label=label,**proof(ev,region)));fact(id,'instance_of',typ,ev,region);fact(id,'part_of',owner,ev,region,True);return id
    water=labels.get('Coal Jetty water-supply outlets')
    if not water:
        water=new('tmp_jetty_water','Coal Jetty water-supply outlets','utility_header',JETTY,'ev_a700ca88c76540e2ae1c',[.80,.53,.98,.67])
        fact(water,'equipment_role','Jetty water outlets at30m intervals supply unloader dust suppression via manual hose reel; GA minimum3bar at supply boundary. This does not identify an upstream tank/pump or establish current pressure.','ev_a700ca88c76540e2ae1c',[.80,.53,.98,.67])
    for n in args.units:
        owner=OWNERS[n];shuttle=SHUTTLES[n]
        ev='ev_a700ca88c76540e2ae1c' if n<3 else 'ev_76b6c09bdcdf42e490ec'
        plan='ev_ec07cf044f9249c0a710' if n<3 else 'ev_10ccd8905bb545f2995c'
        sch=[.79,.03,.982,.69];whole=[.05,.03,.79,.89]
        def part(key,label,typ='functional_assembly',e=ev,r=whole):
            return new(f'tmp_sul{n}_{key}',f'SUL-{n} {label}',typ,owner,e,r)
        grab=part('grab','coal grab assembly')
        hold=part('hold','grab holding and closing drive assembly','hoist_mechanism')
        trolley=part('trolleys','main and auxiliary trolley assembly','trolley')
        traverse=part('traverse','trolley traverse drive assembly')
        boom=part('boom','luffing boom and latch assembly')
        hoist=part('hoist','boom hoist drive assembly','hoist_mechanism')
        travel=part('travel','long-travel drive and bogie assembly')
        anchor=part('anchor','rail-clamp buffer and storm-anchor group',e=plan,r=[.72,.54,.95,.68])
        hopper=part('hopper','receiving hopper grizzly and regulating gate')
        feeder=part('feeder','vibro-feeder assembly','vibrating_feeder')
        belt_drive=part('belt_drive','shuttle belt-drive assembly')
        shuttle_travel=part('shuttle_travel','shuttle travel-drive assembly')
        cable=part('cable','power and fibre-optic cable reel','cable_reel',plan,[.73,.43,.83,.58])
        cabin=part('cabin','operator cabin','operator_cabin')
        house=part('house','machinery house','machinery_house')
        electric=part('electrical','electrical house and transformer assembly')
        lift=part('lift','passenger lift','elevator')
        maintenance=part('maintenance','maintenance EOT and monorail hoist group')
        lube=part('lube','lubrication units','lubrication_system',plan,[.40,.04,.68,.84])
        dust=part('dust','onboard dust-suppression assembly','dust_suppression_system')
        safety=part('safety','anemometer and lightning-protection group')
        dg=part('dg','emergency diesel-generator assembly',e=plan,r=[.45,.56,.60,.76])
        data=[(grab,'Coal grab33m3,17.5t self weight; machine lifting capacity44t. These are design ratings, not present load.'),
              (hold,'Holding/closing motor group2x630kW,VVVF;110m/min full-grab hoist/close and150m/min empty lower/open. Separate holding and closing drums/ropes shown on p12.'),
              (traverse,'Trolley traverse drive1x210kW,VVVF;190m/min design traverse speed.'),
              (hoist,'Boom hoist drive1x75kW,VVVF;7min total lifting/lowering time. Rope drum/sheave reeving shown on p12.'),
              (travel,'Long travel20x7.5kW,VVVF,25m/min;20 seaside and20 landside wheels,10 driven on each side;630mm wheel diameter.'),
              (anchor,'Hydraulic rail clamps,hydraulic buffers,storm tie-downs and stowage pins shown. GA rail-clamp rating210kN per rail. No manual-clamp installation or current storm state inferred.'),
              (hopper,'85m3 hopper;68t load-cell limit;200x200mm clear grizzly mesh;manual rack-and-pinion discharge regulation.'),
              (feeder,'Vibro-feeder rated1700/design1870t/h;1x22kW VVVF, explicitly tentative in Type1 schedule.' if n<3 else 'Vibro-feeder rated1700/design1870t/h;1x22kW VVVF in Type2 schedule.'),
              (belt_drive,'Shuttle conveyor belt drive1x30kW,DOL.' if n<3 else 'Shuttle conveyor belt drive1x30kW,RDOL.'),
              (shuttle_travel,'Shuttle travel drive1x2.2kW,VVVF;10m/min.'),
              (cable,'Power and fibre-optic reel;mono-spiral cable-reeling drum with1x7kW motor,TENTATIVE in GA;VVVF/stall-torque motor. Feeder circuit not established here.'),
              (lift,'Rack-and-pinion passenger lift400kg,4 stops,25m/min,1x9.2kW VVVF.'),
              (maintenance,'Machinery-house maintenance EOT10t and hopper/feeder monorail maintenance2t grouped at assembly level; no extra physical hoist counts inferred.'),
              (dust,'Plain-water spray;jetty outlets every30m via manual hose reel,minimum3bar. Drawn pickups at hopper/feeder/shuttle and receiving belts.' if n<3 else 'Type2 schedule says dry fog while p11 section E-E labels Plain Water Dust Suppression System. Source disagreement retained; do not infer a common DFDS compressed-air connection.'),
              (dg,'Emergency slow-speed operation of specified functions,one at a time; no generator kVA is established by this GA.')]
        for s,v in data:
            region=[.62,.03,.80,.14] if s==cable else whole if s==maintenance else sch
            fact(s,'assembly_arrangement',v,ev,region)
            if s==anchor:
                ops[-1]['evidence'].append(dict(evidence_id=plan,quote='',region=[.72,.54,.95,.68]))
        fact(safety,'assembly_arrangement','Anemometer and lightning arrestor shown on main GA. Settings and control actions deferred.',ev,whole)
        fact(owner,'source_discrepancy','Control write-up describes a belt feeder; later175155 GA explicitly depicts a vibro-feeder. The modeled feeder follows this GA design; both source statements remain available.',ev,sch)
        if n==3:
            lime=part('lime_grab','limestone grab assembly')
            fact(lime,'assembly_arrangement','Separate limestone grab13m3;Type2 table self weight15.1t versus weight block15t. Coal grab remains separate. Type2 GA supports both coal1700t/h and limestone1000t/h; DBR limestone column is not exclusive coal-operation prohibition.',ev,sch)
            fact(dust,'source_discrepancy','Type2 schedule p10 calls dust suppression dry fog; p11 section E-E calls it plain-water suppression. Water supply is explicit; air supply and final nozzle mechanism require the unloader P&ID.',ev,sch)
        for a,b in [(hold,grab),(traverse,trolley),(hoist,boom),(belt_drive,shuttle),(shuttle_travel,shuttle)]:fact(a,'mechanically_drives',b,ev,whole,True,'mechanical','Documented motion/drive assembly relationship; no internal vendor mechanism inferred.')
        for a,b in [(grab,hopper),(hopper,feeder),(feeder,shuttle)]:fact(a,'material_flow_to',b,ev,whole,True,'material','Coal unloading design path from grab through hopper and vibro-feeder to shuttle.')
        for lane,b in [('A','ent_141f73b0a4ef460b9830'),('B','ent_8e0a39fb6e844f8a90d6')]:fact(shuttle,'material_flow_to',b,ev,whole,True,'material',f'Shuttle positioned for coal discharge to EAC-1{lane}; alternative outlets, not simultaneous routing.')
        fact(water,'utility_supply_to',dust,ev,sch,True,'utility','Jetty water outlet through manual hose reel; source minimum3bar, not measured pressure.')
        for a in [hopper,feeder,shuttle]:fact(dust,'utility_supply_to',a,ev,whole,True,'utility','Source-drawn dust-suppression pickup at coal transfer boundary; no nozzle count or operating state asserted.')
        fact(owner,'assembly_arrangement',f'Vendor SUL-{n} major assemblies use its own Type{1 if n<3 else 2} GA. Existing shuttle reused; generic vendor-family records are references and are not adopted as extra installed components.',ev,whole)
    evs=json.loads((ROOT/'output/plant-enrichment/B07/review/doc_1518e219127b4b0eaa3a-evidence.json').read_text(encoding='utf8'))
    out.mkdir(parents=True,exist_ok=True);assert not (out/'accepted/commit-log.json').exists();(out/'baseline-model.json').write_text(json.dumps(m),encoding='utf8')
    pkg=dict(document_id=DOC,baseline_version=args.version,baseline_model=str((out/'baseline-model.json').relative_to(ROOT)).replace('\\','/'),expected_new_components=len(created),visual_ids=sorted(visual),body=dict(summary=f'{args.batch} Tier1 major motion and coal-transfer assemblies for SUL units{args.units}',operations=ops,intake_assessment=dict(route='mixed',purpose='Visible per-unit major unloader assemblies and selected jetty-belt outlets',questions=['Which motion,coal-transfer and service assemblies apply to the numbered machine type?'],reviewed_evidence_ids=[e['id'] for e in evs],gaps=['Source inventory reconciles29PDF pages/31evidence blocks. Principal GA pp8-12 visually reviewed and Type1/Type2 schedule enlarged;pp1-7 review text inspected for relevant assembly qualifications. Cycle-calculation pp13-29 retain existing design-case facts and are not expanded in Pass A.','Existing root ratings and shuttles reused. Vendor drivetrain internals,rope details,protection thresholds,electrical feeders and detailed lube/DSS circuits are Pass B. Jetty water upstream source is not established by this GA. Type2 dust wording discrepancy and Type1 tentative feeder/reel ratings remain explicit.'])))
    (out/'package.json').write_text(json.dumps(pkg,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(components=len(created),operations=len(ops))))

if __name__=='__main__':main()
