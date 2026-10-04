"""Build source-reviewed Tier-1 primary screening packages; never replay acceptance."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOUSE = 'ent_92291cd617b04811bc28'
DOCS = {'screens': 'doc_b4cf0a76c954435aadd6', 'house': 'doc_8d973a7544ef4a488e98', 'utilities': 'doc_c0ce31dea65b4d4caef4'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--version', type=int, required=True)
    args = ap.parse_args()
    model = json.loads((ROOT / args.baseline).read_text(encoding='utf8'))
    model = model.get('model', model)
    assert model['version'] == args.version
    labels = {e['label']: e['canonical_id'] for e in model['entities']}
    active = [a for a in model['assertions'] if not a['retirement'] and not a['suppressed']]
    doc = DOCS[args.scope]
    evidence = json.loads((ROOT / f'output/plant-enrichment/B09/review/{doc}-evidence.json').read_text(encoding='utf8'))
    ev = {e['page']: e['id'] for e in evidence}
    ops, created, visual = [], [], set()
    basis = {'screens': '175064 primary grizzly screen GA and selection/calculation; approved21-Jan-2019. Four screens at PSH, not crusher-house screens.', 'house': '175034 primary screening house main GA Rev3; approved01-Oct-2019. Design arrangement, not installation certification.', 'utilities': '175287 UEE-1 DFDS/SW/PW piping layout Rev2, FIO12-Sep-2019. Information design, not field verification.'}[args.scope]

    def proof(page, region):
        visual.add(ev[page])
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[page], quote='', region=region)])

    def fact(s, p, value, page=1, region=None, obj=False, network=None, condition=None):
        region = region or [.04, .04, .98, .93]
        context = dict(kind='classification' if p == 'instance_of' else 'specification', basis=basis)
        if network:
            context.update(kind='connection', network=network, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'): value}, context=context, **proof(page, region)))

    def new(key, label, typ, owner, page=1, region=None):
        assert label not in labels, ('Already modeled', label)
        id = 'tmp_b09_' + key
        region = region or [.04, .04, .98, .93]
        created.append(id)
        ops.append(dict(op='entity', id=id, label=label, **proof(page, region)))
        fact(id, 'instance_of', typ, page, region)
        fact(id, 'part_of', owner, page, region, True)
        return id

    gaps = []
    if args.scope == 'screens':
        for n in range(1, 5):
            owner = labels[f'EBD-{n}']
            def part(key, name, typ='functional_assembly', region=None):
                return new(f'{n}_{key}', f'EBD-{n} {name}', typ, owner, region=region)
            body = part('body', 'screen body and grizzly deck')
            blind = part('blind', 'blind feed deck')
            motor = part('motor', 'screen drive motor', 'electric_motor', [.53, .06, .83, .31])
            belt = part('belt', 'belt and pulley transmission', region=[.53, .06, .83, .31])
            shafts = part('shafts', 'cardan drive-shaft group', region=[.53, .06, .83, .31])
            exciters = part('exciters', 'paired vibration exciters', 'vibration_exciter', [.53, .06, .83, .31])
            supports = part('supports', 'spring supports and amplitude limiters')
            cover = part('cover', 'dust-cover assembly')
            fact(owner, 'assembly_arrangement', 'Primary grizzly screen2700mm wide x7000mm nominal length; rated1700/design1870t/h. GA working range725-800rpm and100mm separation. Selection sheet overall length7090mm includes blind section and lip; not a second machine size.')
            fact(motor, 'assembly_arrangement', 'One55kW motor, selected1500rpm. Calculation uses1440rpm for shaft-torque basis; no actual operating speed or electrical feeder inferred.', 3, [.12, .48, .93, .87])
            fact(body, 'assembly_arrangement', 'Screen body with grizzly bar set; main schedule50mm thick grizzly bars.', 1, [.76, .535, .985, .74])
            fact(blind, 'assembly_arrangement', 'Blind deck plate20mm thick Tiscral or equivalent, upstream of the grizzly bars.', 1, [.76, .535, .985, .74])
            fact(exciters, 'assembly_arrangement', 'Two DF601V exciters per screen; connected by intermediate cardan shaft.', 1, [.76, .535, .985, .74])
            fact(supports, 'assembly_arrangement', 'Front/rear spring supports with supporting plates/structure and amplitude limiters, grouped as one maintainable assembly. Individual springs and fasteners deferred.', 1, [.76, .535, .985, .74])
            fact(cover, 'assembly_arrangement', 'One dust-cover set per screen, distinct from the local DFDS supply.', 1, [.76, .535, .985, .74])
            for a, b in [(motor, belt), (belt, shafts), (shafts, exciters), (exciters, body)]:
                fact(a, 'mechanically_drives', b, 1, [.53, .06, .83, .31], True, 'mechanical', 'GA drive train at assembly level; no exciter internal gearing inferred.')
        gaps = ['All4 original pages reviewed; enlarged GA drive and schedule used. Primary-screen design applies to EBD1-4 only. Existing operational permissives/trips retained. Exciter internals, spring/liner/fastener BOM, stroke/weight setting and torque reconciliation deferred to Pass B.']
    elif args.scope == 'house':
        lane_region = [.385, .06, .675, .49]
        for n in range(1, 5):
            screen = labels[f'EBD-{n}']
            for suffix, name, destination, condition in [('under', 'undersize discharge chute', labels['EAC-3A' if n < 3 else 'EAC-3B'], 'Screen undersize to its own conveyor3 lane; screen1/2 to3A,3/4 to3B.'), ('over', 'oversize reject chute', labels['UEE-1 Oversize Reject Bins'], 'Oversize rejection to the existing bin boundary, not onward conveyor flow.')]:
                chute = new(f'{n}_{suffix}', f'EBD-{n} {name}', 'chute_interface', screen, region=lane_region)
                fact(screen, 'material_flow_to', chute, 1, lane_region, True, 'material', condition)
                fact(chute, 'material_flow_to', destination, 1, lane_region, True, 'material', condition)
            gate = labels[f'KB-RPG-{n}']
            actuator = new(f'{n}_actuator', f'KB-RPG-{n} rotary actuator', 'gate_actuator', gate, 2, [.55, .80, .75, .98])
            fact(actuator, 'mechanically_drives', gate, 2, [.55, .80, .75, .98], True, 'mechanical', 'Motor-operated rack-and-pinion gate rotary actuator shown on house GA; no torque or motor rating inferred.')
            rod = labels[f'KB-RG-{n}']
            duplicate = [a for a in active if a['canonical_subject'] == rod and a['predicate'] == 'part_of' and a['canonical_object'] == labels['Maitree Coal Handling Plant']]
            assert len(duplicate) == 1
            ops.append(dict(op='retire', assertion_id=duplicate[0]['id'], reason='175034 shows this rod gate in UEE-1. Preserve existing UEE-1 owner and remove duplicate plant-level ownership only; identity and route unchanged.', **proof(1, lane_region)))
        schedule = [.31, .807, .473, .887]
        hoists = [('EH-1', 10, 'EAC-2A/2B drive units'), ('EH-2', 10, 'EBD-1/EBD-3 and their drives'), ('EH-3', 10, 'EBD-2/EBD-4 and their drives'), ('EH-4', 5.5, 'EAC-2A/2B head and snub pulleys'), ('MH-1', 3, 'EAC-2A/2B take-up pulleys'), ('MH-2', 10, 'counterweight frames'), ('MH-3', 2, 'EAC-3A/3B tail pulleys'), ('MH-4', 1, 'rack-and-pinion gate rotary actuators')]
        for tag, tonnes, service in hoists:
            hoist = new(tag.replace('-', '_'), f'UEE-1 {tag} maintenance hoist', 'electric_hoist' if tag.startswith('EH') else 'manual_hoist', HOUSE, 2, schedule)
            fact(hoist, 'assembly_arrangement', f'{tonnes}t design capacity; services {service}. Schedule in175034 governs this source claim; shared maintenance coverage is not a material-route connection.', 2, schedule)
        access = new('access', 'UEE-1 platforms stairs and maintenance access', 'maintenance_access_assembly', HOUSE)
        fact(access, 'equipment_role', 'Main GA shows stairs, platforms, handrails and equipment maintenance paths. Review requires minimum800mm handrail-to-motor-belt-guard clearance and entrance clear of oversize discharge. Dimensions do not certify present access condition.', 3, [.05, .13, .96, .94])
        gaps = ['Original175034 pp1-3 reviewed with enlarged lane/hoist/actuator views. Correct drawing number is175034 (old checkpoint typo175037). Existing rods/RPGs, reject-bin boundary and control routes reused. Gate internals, vendor actuator detail, hoist rails/certification and exact bin count deferred. Screen controls already retained from175001.']
    else:
        mains = [new('air', 'UEE-1 local DFDS air main', 'utility_header', HOUSE, 1, [.33, .14, .66, .48]), new('water', 'UEE-1 local DFDS water main', 'utility_header', HOUSE, 1, [.33, .14, .66, .48])]
        for main in mains:
            fact(main, 'source_discrepancy', 'Layout175287 labels incoming utilities FROM PUMP HOUSE-2 and continuation PIPE TO UEF-1. Existing175089 system assignment serves UEE-1 from DFDS System-1/UGA-1. Preserve that assignment; the layout alone does not prove a new connection to DFDS System-2 or reverse the accepted TP1 supply. Upstream routing label needs reconciliation.', 1, [.28, .14, .66, .81])
        # Existing tagged stations are reused, with explicit location and local ownership.
        tags = ['05', '09', '08', '07', '6', '6A', '10A', '10', '11', '12']
        for tag in tags:
            fas, pru = [labels[f'UEE-1 {kind}-{tag}'] for kind in ['FAS', 'PRU']]
            for station in [fas, pru]:
                if not any(a['canonical_subject'] == station and a['predicate'] == 'part_of' for a in active):
                    fact(station, 'part_of', HOUSE, 2, [.10, .10, .67, .72], True)
                fact(station, 'located_at', HOUSE, 2, [.10, .10, .67, .72], True)
            for main in mains:
                fact(main, 'utility_supply_to', fas, 2, [.10, .10, .67, .72], True, 'utility', 'Local DFDS air/water mains to existing filtration/solenoid stations; upstream house label remains source-qualified.')
        for n, tag in [(1, '6'), (2, '6A'), (3, '10'), (4, '10A')]:
            screen, pru = labels[f'EBD-{n}'], labels[f'UEE-1 PRU-{tag}']
            spray = new(f'{n}_spray', f'EBD-{n} DFDS spray-header group', 'spray_header', screen, 2, [.10, .33, .65, .54])
            fact(pru, 'utility_supply_to', spray, 2, [.10, .33, .65, .54], True, 'utility', 'Paired regulated air/water to the primary-screen spray application; no nozzle count or settings inferred.')
            fact(spray, 'utility_supply_to', screen, 2, [.10, .33, .65, .54], True, 'utility', 'Dust suppression at its numbered primary screen.')
            if n == 4:
                fact(pru, 'source_discrepancy', '175287p2 labels the EBD-4 station FAS-10A but PRU-8A; existing accepted corresponding station is PRU-10A. This local inconsistent label is preserved, not a new PRU or an identity merge.', 2, [.39, .39, .50, .54])
        for tag, lane in [('11', 'B'), ('12', 'B')]:
            fact(labels[f'UEE-1 PRU-{tag}'], 'utility_supply_to', labels[f'EAC-3{lane}'], 2, [.10, .56, .49, .73], True, 'utility', '175287 View2-2 labels both outlets ECA-3B; keep this source wording without silently changing one to3A. Existing PRU08-to3A and PRU07-to3B remain.')
        service = new('wash', 'UEE-1 service-water washdown points', 'functional_assembly', HOUSE, 2, [.10, .77, .165, .88])
        potable = new('potable', 'UEE-1 potable-water tank and tap assembly', 'functional_assembly', HOUSE, 2, [.47, .54, .67, .73])
        fact(labels['SW1 Common distribution header'], 'utility_supply_to', service, 2, [.10, .77, .165, .88], True, 'utility', 'Local washdown consuming existing accepted SW1-to-UEE1 supply; building branch upstream assignment retained from B03.')
        ops[-1]['origin'] = 'inferred'
        ops[-1]['context']['verification'] = 'unverified'
        fact(labels['PW Common distribution header'], 'utility_supply_to', potable, 2, [.17, .77, .235, .88], True, 'utility', 'Local potable tank/taps consuming existing accepted PW-to-UEE1 supply; no new upstream source inferred.')
        ops[-1]['origin'] = 'inferred'
        ops[-1]['context']['verification'] = 'unverified'
        fact(potable, 'assembly_arrangement', 'PVC potable-water tank and tap arrangement; capacity is not inferred from this layout.', 2, [.47, .54, .67, .73])
        gaps = ['Original175287 pp1-3 visually reviewed. Existing20 FAS/PRU units reused; major local mains,screen spray groups,washdown and potable assembly only. Common source service relationships and drainage from B01/B03/B04 retained. Layout incoming Pump House2 label conflicts with established DFDS1 assignment; no false cross-system pipe added. PRU8A/10A and paired3B outlet labels retained as qualified source wording. Internals,nozzle counts,piping BOM,settings and supply-label reconciliation are Pass B.']
    out = ROOT / f'output/plant-enrichment/B09/{args.scope}'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'accepted/commit-log.json').exists()
    (out / 'baseline-model.json').write_text(json.dumps(model), encoding='utf8')
    pkg = dict(document_id=doc, baseline_version=args.version, baseline_model=(out / 'baseline-model.json').relative_to(ROOT).as_posix(), expected_new_components=len(created), visual_ids=sorted(visual), body=dict(summary=f'B09 Tier1 primary screening {args.scope}', operations=ops, intake_assessment=dict(route='mixed', purpose='Major primary-screening equipment and service interfaces', questions=['Which major assemblies and routes are explicitly supported for UEE-1 and its four primary screens?'], reviewed_evidence_ids=[e['id'] for e in evidence], gaps=gaps)))
    (out / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(components=len(created), operations=len(ops))))


if __name__ == '__main__':
    main()
