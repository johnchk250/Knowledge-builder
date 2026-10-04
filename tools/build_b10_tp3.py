"""Reviewed TP3 major branches and DFDS consumer package, source scoped."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=['house', 'utilities'])
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--version', required=True, type=int)
    args = ap.parse_args()
    m = json.loads((ROOT / args.baseline).read_text(encoding='utf8'))
    assert m['version'] == args.version
    labels = {e['label']: e['canonical_id'] for e in m['entities']}
    house = labels['UEF-3']
    doc = 'doc_883418b36ea44369adbe' if args.scope == 'house' else 'doc_bca09d68af9b43e3b633'
    evs = json.loads((ROOT / f'output/plant-enrichment/B10/review/{doc}-evidence.json').read_text(encoding='utf8'))
    ev = next(e['id'] for e in evs if e['page'] == 1)
    ops, nodes = [], []
    region = [.05, .05, .80, .79] if args.scope == 'house' else [.71, .03, .96, .31]
    basis = '175035 TP3 GA Rev3 approved14-Dec-2018; design only.' if args.scope == 'house' else '175089 DFDS System1 P&ID Rev1 approved16-Oct-2018, p1; design utility path, not live valve state.'

    def proof(r):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev, quote='', region=r)])

    def fact(s, p, v, r=region, obj=False, net=None, condition=None):
        ctx = dict(kind='classification' if p == 'instance_of' else 'specification', basis=basis)
        if net:
            ctx.update(kind='connection', network=net, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'): v}, context=ctx, **proof(r)))

    def new(key, label, typ, owner, r=region):
        assert label not in labels
        id = 'tmp_b10_' + key
        nodes.append(id)
        ops.append(dict(op='entity', id=id, label=label, **proof(r)))
        fact(id, 'instance_of', typ, r)
        fact(id, 'part_of', owner, r, True)
        fact(id, 'located_at', house, r, True)
        return id

    if args.scope == 'house':
        for n, lane in [(1, 'A'), (2, 'B')]:
            fd, fg = labels[f'KB-FD-{n}'], labels[f'FG-{n}']
            drive = new(f'fd{n}_drive', f'KB-FD-{n} drive assembly', 'functional_assembly', fd)
            actuator = new(f'fg{n}_actuator', f'FG-{n} rotary actuator', 'gate_actuator', fg)
            fact(drive, 'mechanically_drives', fd, obj=True, net='mechanical', condition='Source-drawn flow-divider drive; vendor internal mechanism and rating deferred.')
            fact(actuator, 'mechanically_drives', fg, obj=True, net='mechanical', condition='Flap-gate rotary actuator shown and named in MH4 hoist schedule.')
            fact(labels[f'EAC-3{lane} flow-divider inlet chute'], 'material_flow_to', fd, obj=True, net='material', condition=f'Conveyor3{lane} discharge enters its own numbered divider{n}.')
            for key, label, dest, condition in [('yard', 'Yard4 discharge chute', labels['EAC-13'], 'Divider positioned for full or partial Yard4 diversion; shares EAC13 receiving belt.'), ('onward', 'onward discharge chute', fg, 'Divider positioned for full or remaining partial onward flow to its own selector gate.')]:
                chute = new(f'fd{n}_{key}', f'KB-FD-{n} {label}', 'chute_interface', fd)
                fact(fd, 'material_flow_to', chute, obj=True, net='material', condition=condition)
                fact(chute, 'material_flow_to', dest, obj=True, net='material', condition=condition)
            chute = new(f'fg{n}_out', f'FG-{n} selector outlet chute group', 'chute_interface', fg)
            fact(fg, 'material_flow_to', chute, obj=True, net='material', condition='Selected onward conveyor4 outlet; two alternatives, not simultaneous discharge.')
            for out in ['A', 'B']:
                fact(chute, 'material_flow_to', labels[f'EAC-4{out}'], obj=True, net='material', condition=f'FG{n} selects EAC4{out}; retains the documented selector alternative.')
        # Building-level coal edges bypass the actual gates; explicit branches above remain.
        active = [a for a in m['assertions'] if not a['retirement'] and not a['suppressed']]
        for a in active:
            if a['predicate'] == 'material_flow_to' and ((a['canonical_subject'] in [labels['EAC-3A'], labels['EAC-3B']] and a['canonical_object'] == house) or (a['canonical_subject'] == house and a['canonical_object'] in [labels['EAC-4A'], labels['EAC-4B']])):
                ops.append(dict(op='retire', assertion_id=a['id'], reason='175035 shows actual FD/FG branching. Aggregate building material edges bypass branch conditions; preserve exact equipment routes and locations.', **proof(region)))
        hoists = [('EH-1', 10, 'EAC3A/B head/snub pulleys and drive units'), ('EH-2', 5.5, 'EAC3A/B head/snub pulleys'), ('EH-3', 4, 'EAC4A/B and EAC13 tail pulleys'), ('MH-1', 3, 'EAC3A/B take-up pulley frames'), ('MH-2', 1, 'CSU belt feeder and flow divider'), ('MH-3', 15, 'EAC3A/B counterweight frames'), ('MH-4', 1, 'FG1/2 actuators')]
        for tag, rating, service in hoists:
            r = [.195, .865, .41, .982]
            id = new(tag.replace('-', '_'), f'UEF-3 {tag} maintenance hoist', 'electric_hoist' if tag.startswith('EH') else 'manual_hoist', house, r)
            fact(id, 'assembly_arrangement', f'{rating}t GA design capacity; services {service}. No current lifting certification inferred.', r)
        access = new('access', 'UEF-3 platforms stairs and maintenance access', 'maintenance_access_assembly', house)
        fact(access, 'equipment_role', 'GA shows access stairs, platforms, monorail routes, take-up mesh guards and lockable doors. Review replies confirm sampler moved away from belt transition and revised maintenance access; no field clearance certification.')
        potable = new('potable', 'UEF-3 potable-water tank and tap assembly', 'functional_assembly', house, [.19, .07, .27, .19])
        fact(potable, 'assembly_arrangement', '250L water tank with tap arrangement on main GA; existing common potable-water service to UEF3 retained.', [.19, .07, .27, .19])
        gaps = ['Original175035 pp1-2 visually reviewed; review/reply pp3-5 read. Principal hoist and branching views enlarged. Existing sampling equipment retained for B11. Exact FD/FG control conditions remain from175001; partial split is not two simultaneously selected FG outlets. Four aggregate route edges retired. Divider/actuator internals,hoist certification and structural/clearance detail deferred.']
    else:
        mains = [new('air_main', 'UEF-3 local DFDS air main', 'utility_header', house), new('water_main', 'UEF-3 local DFDS water main', 'utility_header', house)]
        source_names = ['DFDS-1 Common air main at receiver outlet', 'DFDS-1 Common water main at station outlet']
        for source, main, other in zip(source_names, mains, ['UEE-1 local DFDS air main', 'UEE-1 local DFDS water main']):
            fact(labels[source], 'utility_supply_to', main, [.32, .03, .96, .43], True, 'utility', 'System1 main through primary-screening distribution to TP3 local branch; intervening pipe fittings not decomposed.')
            fact(labels[source], 'utility_supply_to', labels[other], [.32, .03, .70, .43], True, 'utility', '175089 explicitly supplies UEE1 from System1/UGA1. Conflicting175287 Pump House2 label remains qualified; no System2 pipe is added.')
        targets = {13:'EAC-3A',14:'EAC-4A',15:'EAC-4B',16:'EAC-13',17:'EAC-3B',18:'EAC-4A',19:'EAC-4B',20:'EAC-13'}
        for tag, target in targets.items():
            fas = labels[f'UEF-3 FAS-{tag}']
            pru = new(f'pru{tag}', f'UEF-3 PRU-{tag}', 'pressure_regulating_unit', house)
            spray = new(f'ap{tag}', f'UEF-3 AP-{tag} spray-header group', 'spray_header', house)
            for main in mains:
                fact(main, 'utility_supply_to', fas, obj=True, net='utility', condition='Local paired air/water supplies to existing numbered FAS; existing automatic/manual control group retained.')
            fact(fas, 'utility_supply_to', pru, obj=True, net='utility', condition='Same-number FAS/PRU pairing explicitly shown by P&ID.')
            fact(pru, 'utility_supply_to', spray, obj=True, net='utility', condition='Same-number regulated application group; no numeric pressure setting inferred.')
            fact(spray, 'utility_supply_to', labels[target], obj=True, net='utility', condition=f'AP{tag} at {target} transfer; selected conveyor route and existing FAS conditions determine operation.')
        fact(house, 'assembly_arrangement', 'Eight local DFDS application groups AP13-20 supplied by System1. AP13/17 at3A/B discharge;14/18 at4A receipt;15/19 at4B receipt;16/20 at13 receipt from3A/B. No assertion that all operate simultaneously.')
        gaps = ['Bounded visual re-review of original175089p1 UEE1/TP3/main-distribution and application schedule. Full two-sheet inventory reconciled to prior B02/B03 accepted review; System2p2 is unchanged and not newly expanded. Previously accepted common station and other areas unchanged. Eighteen local maintainable utility groups only; PRU internals,per-nozzle decomposition and settings deferred. UEE1 common source links close its physical boundary using this explicit P&ID while retaining the conflicting local-layout label.']
    out = ROOT / f'output/plant-enrichment/B10/{args.scope}'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'accepted/commit-log.json').exists()
    (out / 'baseline-model.json').write_text(json.dumps(m), encoding='utf8')
    pkg = dict(document_id=doc, baseline_version=args.version, baseline_model=(out / 'baseline-model.json').relative_to(ROOT).as_posix(), expected_new_components=len(nodes), visual_ids=[ev], body=dict(summary=f'B10 Tier1 TP3 {args.scope}', operations=ops, intake_assessment=dict(route='mixed', purpose='TP3 major branching equipment and common-service connections', questions=['Which major transfer assemblies and local consumers apply at TP3?'], reviewed_evidence_ids=[e['id'] for e in evs], gaps=gaps)))
    (out / 'package.json').write_text(json.dumps(pkg, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(components=len(nodes), operations=len(ops))))


if __name__ == '__main__':
    main()
