"""Source-reviewed Tier1 conveyor5, TP5/6 and their local utility packages."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    'conveyor': ('doc_b74a01e57a2b4792883c', '175015 Rev2 approved14-Dec-2018, conveyor5A/B GA'),
    'tp5': ('doc_6d28742056e94651be04', '175037 Rev3 approved18-Oct-2019, TP5 GA'),
    'tp6': ('doc_eadc432afcad400192d0', '175038 Rev3 approved18-Dec-2018, TP6 GA'),
    'utilities5': ('doc_e91d806d942243248e18', '175290 Rev2 FIO13-Sep-2019, TP5 utility layout'),
    'utilities6': ('doc_f9f96af6a25e47179881', '175291 Rev2 FIO16-Sep-2019, TP6 utility layout'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    ap.add_argument('--baseline', required=True)
    args = ap.parse_args()
    m = json.loads((ROOT / args.baseline).read_text(encoding='utf8'))
    labels = {e['label']: e['canonical_id'] for e in m['entities']}
    active = [a for a in m['assertions'] if not a['retirement'] and not a['suppressed']]
    doc, title = DOCS[args.scope]
    evs = json.loads((ROOT / f'output/plant-enrichment/B13/review/{doc}-evidence.json').read_text(encoding='utf8'))
    # Multiple extracted text blocks can share a page; every cited block is in visual_ids.
    ev = {e['page']: e['id'] for e in evs}
    ops, nodes = [], []
    house = labels['UEF-5' if args.scope.endswith('5') else 'UEF-6']
    region = [.04, .035, .97, .79]

    def proof(page=1, r=region):
        return dict(origin='explicit', confidence=.98, evidence=[dict(evidence_id=ev[page], quote='', region=r)])

    def fact(s, p, v, page=1, r=region, obj=False, net=None, condition=None):
        ctx = dict(kind='classification' if p == 'instance_of' else 'specification', basis=title + '; design evidence, not field verification.')
        if net:
            ctx.update(kind='connection', network=net, verification='documented', condition=condition)
        ops.append(dict(op='assert', subject=s, predicate=p, **{('object_entity' if obj else 'value'): v}, context=ctx, **proof(page, r)))

    def new(key, label, typ, owner, page=1, r=region, place=None):
        assert label not in labels, label
        id = 'tmp_b13_' + args.scope + '_' + key.replace('-', '_')
        ops.append(dict(op='entity', id=id, label=label, **proof(page, r)))
        fact(id, 'instance_of', typ, page, r)
        fact(id, 'part_of', owner, page, r, True)
        if place:
            fact(id, 'located_at', place, page, r, True)
        nodes.append(id)
        return id

    def retire(a, reason, page=1, r=region):
        ops.append(dict(op='retire', assertion_id=a['id'], reason=reason, **proof(page, r)))

    def local_owner(id):
        if not any(a['canonical_subject'] == id and a['predicate'] == 'part_of' and a['canonical_object'] == house for a in active):
            fact(id, 'part_of', house, obj=True)
        if not any(a['canonical_subject'] == id and a['predicate'] == 'located_at' and a['canonical_object'] == house for a in active):
            fact(id, 'located_at', house, obj=True)
        for a in active:
            if a['canonical_subject'] == id and a['predicate'] == 'part_of' and a['canonical_object'] == labels['Maitree Coal Handling Plant']:
                retire(a, 'Local GA proves transfer-house owner; plant containment remains through the house.')

    if args.scope == 'conveyor':
        schedule = [.80, .03, .983, .752]
        drive = [.42, .04, .80, .37]
        for n, lane in [(3, 'A'), (4, 'B')]:
            owner, ftr, head = labels['EAC-5' + lane], labels[f'FTR-{n}'], labels['UEF-7']
            specs = [
                ('motor', 'main drive motor', 'electric_motor', 'BHEL squirrel-cage380kW,1488rpm. Schedule says HT but also415V +/-10%; both source statements retained. Existing415V root value is design evidence, not a resolved installed supply.'),
                ('fluid', 'scoop fluid coupling', 'fluid_coupling', 'Premium PST-530 scoop coupling.'),
                ('gear', 'main gearbox', 'gearbox', 'Premium B3 450 bevel-helical gearbox17:1.'),
                ('low', 'low-speed coupling', 'coupling', 'GBM RG-10 geared coupling.'),
                ('brake', 'service thruster brake', 'thruster_drum_brake', 'Elektromag EBTM-500/DS/DG thruster brake.'),
                ('head', 'head drive pulley', 'pulley', 'One800mm diameter x2200mm face,2700mm bearing centres;12mm diamond-groove lagging.'),
                ('belt', 'conveyor belting', 'conveyor_belt', '2000mm N/N HD1000/5, FR5/2mm covers;405.500m endless length for each lane.'),
                ('idler', 'idler and belt-support assembly', 'functional_assembly', 'Transition,impact,carrying,self-aligning,self-cleaning and return idler groups, skirts and gallery deck/seal plates; detailed row quantities deferred.'),
                ('tail', 'tail bend and snub pulley group', 'functional_assembly', 'Eight630mm diameter x2200mm face,2700mm bearing-centre pulleys grouped as tail/bend/snub; excludes separately scheduled take-up and fixed-tripper pulleys.'),
                ('takeup', 'vertical gravity take-up assembly', 'take_up_assembly', 'VGTU atTP6,5300mm travel,one630mm pulley,11000kg cast-iron design counterweight; retained VGTU design despite review request for HGTU.'),
                ('cleaners', 'head tripper and tail cleaner group', 'functional_assembly', 'Primary/secondary cleaners at main and tripper discharge; two internal tail V-ploughs. Schedule says one primary/secondary each, reviewp5 requests two each and reply says revised. Quantity disagreement retained.'),
                ('protection', 'PCS BSS and ZSS protection group', 'functional_assembly', 'BSS5 pairs at40m intervals, PCS6 pairs at30m,one tail-pulley ZSS per conveyor. No numeric trip settings inferred.'),
                ('chute', 'head selector inlet chute', 'chute_interface', 'Main head atTP7 feeds own FG5/6; intermediate FTR3/4 atTP6 is part of the same continuous belt.'),
            ]
            ids = {}
            for key, name, typ, desc in specs:
                place = head if key in ['motor', 'fluid', 'gear', 'low', 'brake', 'head', 'chute'] else house if key == 'takeup' else None
                id = new(lane + key, 'EAC-5' + lane + ' ' + name, typ, owner, 3, drive if key in ['motor', 'fluid', 'gear', 'low', 'brake'] else schedule, place)
                fact(id, 'assembly_arrangement', desc, 3, schedule)
                if key == 'cleaners':
                    fact(id, 'document_note', 'Review requests two primary and two secondary cleaners; reply says drawing revised. Read together with the still-one-each schedule.', 5)
                ids[key] = id
            for a, b in zip(['motor', 'fluid', 'gear', 'low', 'head'], ['fluid', 'gear', 'low', 'head', 'belt']):
                fact(ids[a], 'mechanically_drives', ids[b], 3, drive, True, 'mechanical', 'Source-drawn main head drive train atTP7.')
            for src, dst in [(owner, ids['chute']), (ids['chute'], labels[f'FG-{n+2}'])]:
                fact(src, 'material_flow_to', dst, 2, [.83, .14, .963, .36], True, 'material', 'Main head discharge beyondTP6 to its own selector atTP7; existing downstream choice retained.')
            trip = new(lane + 'trip', f'FTR-{n} pulley hood and discharge assembly', 'functional_assembly', ftr, 3, schedule, house)
            fact(trip, 'assembly_arrangement', 'One800mm fixed-tripper discharge pulley and two219mm deflector rollers; same continuous conveyor belt, not a powered travelling machine.', 3, schedule)
            fact(ftr, 'located_at', house, 1, [.60, .10, .975, .43], True)
            fact(owner, 'document_note', 'GA3 motor row says HT and415V; unresolved source wording. GA2 plan caption says3A/B although title, tags and profile identify5A/B; no identity change.', 3, schedule)
            for a in active:
                if a['canonical_subject'] == ftr and a['predicate'] == 'part_of' and a['canonical_object'] == labels['Maitree Coal Handling Plant']:
                    retire(a, 'Keep existing own-conveyor FTR owner; remove redundant plant owner.')
                if a['canonical_subject'] == owner and a['predicate'] == 'material_flow_to' and a['canonical_object'] == head:
                    retire(a, 'Building aggregate bypasses FG5/6; exact own-selector route remains.', 2)
        gaps = ['All three GA sheets visually reviewed and review/repliespp4-6 read. Root headline ratings reused. HT/415V and cleaner quantity disagreements qualified. Vendor internals/settings deferred.']
    elif args.scope in ['tp5', 'tp6']:
        is5 = args.scope == 'tp5'
        number = 5 if is5 else 6
        for n, lane in ([(5, 'A'), (6, 'B')] if is5 else [(7, 'A'), (8, 'B')]):
            fd = labels[f'KB-FD-{n}']; local_owner(fd)
            drive = new(f'fd{n}', f'KB-FD-{n} geared actuator assembly', 'functional_assembly', fd, place=house)
            fact(drive, 'mechanically_drives', fd, 1 if is5 else 3, obj=True, net='mechanical', condition='Source-drawn local divider drive; internal parts and ratings deferred.')
            if is5:
                fg = labels[f'FG-{n-2}']; local_owner(fg)
                actuator = new(f'fg{n-2}', f'FG-{n-2} rotary actuator', 'gate_actuator', fg, place=house)
                fact(actuator, 'mechanically_drives', fg, obj=True, net='mechanical', condition='FG3/4 actuator named in MH3 hoist schedule.')
                branches = [('yard', 'Yard2 discharge chute', fd, labels['EAC-9'], 'Full or partial stacking to Yard2/EAC9.'), ('onward', 'onward selector inlet chute', fd, fg, 'Onward full or remaining divided stream to its own FG3/4.')]
            else:
                branches = [('in', 'fixed-tripper inlet chute', labels[f'FTR-{n-4}'], fd, 'Own-lane fixed-tripper discharge to divider.'), ('through', 'same-belt onward chute', fd, labels['EAC-5'+lane], 'Through-flow on the SAME continuous EAC5'+lane+' beyond the fixed tripper, not recirculation.'), ('yard', 'Yard1 discharge chute', fd, labels['EAC-7'], 'Full or partial stacking to Yard1/EAC7; any remainder stays on the same own EAC5 belt.')]
            for key, name, src, dst, condition in branches:
                chute = new(str(n)+key, f'KB-FD-{n} '+name, 'chute_interface', fd, place=house)
                fact(src, 'material_flow_to', chute, obj=True, net='material', condition=condition)
                fact(chute, 'material_flow_to', dst, obj=True, net='material', condition=condition)
            if is5:
                chute = new(f'fg{n-2}out', f'FG-{n-2} selector outlet chute group', 'chute_interface', fg, place=house)
                fact(fg, 'material_flow_to', chute, obj=True, net='material', condition='Selected outlet; alternatives are not simultaneous.')
                for out in ['A', 'B']:
                    fact(chute, 'material_flow_to', labels['EAC-5'+out], obj=True, net='material', condition=f'FG{n-2} selects EAC5{out}; retain the documented crossover option.')
        hoists = [('EH-1','10t','4A/B head/snub pulleys,drive units and belt drum'),('EH-2','5.5t','4A/B head/snub pulleys'),('EH-3','4t','5A/B and9 tail pulleys'),('MH-1','3t','4A/B take-up pulley frames'),('MH-2','1t','flow dividers'),('MH-3','1t','FG3/4 actuators'),('MH-4','16t','4A/B counterweight frames')] if is5 else [('EH-1','3.5t','5A/B tripper discharge pulleys'),('EH-2','3.5t','5A/B fixed-tripper bend pulleys'),('EH-3','4t','7 tail pulley'),('MH-1','3t','5A/B VGTU pulleys'),('MH-2','1t','flow dividers'),('MH-3','7.5t x2','counterweight frames')]
        hr = [.25, .81, .505, .95] if is5 else [.425, .875, .612, .982]
        for tag, rating, service in hoists:
            id = new(tag, f'UEF-{number} {tag} maintenance hoist', 'electric_hoist' if tag.startswith('EH') else 'manual_hoist', house, 1, hr, house)
            fact(id, 'assembly_arrangement', f'{rating} design capacity for {service}; no current lifting certification inferred.', 1, hr)
        access = new('access', f'UEF-{number} platforms stairs and maintenance access', 'maintenance_access_assembly', house, place=house)
        fact(access, 'assembly_arrangement', 'Stairs,platforms,hoist monorails,removable floor openings,mesh guards,lockable take-up doors and divider-access stools shown. Field clearances/certification not inferred.')
        tank = new('tank', f'UEF-{number} potable-water tank and tap assembly', 'functional_assembly', house, 1, [.06,.035,.56,.19], house)
        fact(tank, 'assembly_arrangement', '300L local potable tank perGA.' if is5 else 'GA labels250L. Later175291 layout includes both250L plan and300L elevation/tank detail; capacity remains unresolved, one assembly only.', 1, [.06,.035,.56,.19])
        drain = new('drain', f'UEF-{number} garland drain and downcomer group', 'functional_assembly', house, place=house)
        fact(drain, 'equipment_role', 'Local garland drain and downcomers. Existing shared runoff sump connection retained; detailed local pipe endpoint not invented.')
        for a in active:
            if a['canonical_subject'] == house and a['predicate'] == 'material_flow_to':
                retire(a, 'Aggregate building flow bypasses source-drawn FD/FG conditions; precise equipment branches remain.')
        if not is5:
            fact(house, 'document_note', 'Reviewp5 copies4A/B andEAC11 names intoTP6 discussion. PrincipalGA and existing topology prove5A/B andEAC7; no copied route asserted.', 5)
        gaps = ['Two GA sheets visually reviewed; all attached review/reply pages read. Main hoists,access,tank and drain only. Existing Yard1/2 conveyor identities and common runoff links reused. Detailed rail/clearance/vendor rows deferred.']
    else:
        number = 5 if args.scope == 'utilities5' else 6
        mains = []
        for fluid in ['air', 'water']:
            main = new(fluid, f'UEF-{number} local DFDS {fluid} main', 'utility_header', house, place=house); mains.append(main)
            fact(labels[f'UEF-{number-1} local DFDS {fluid} main'], 'utility_supply_to', main, obj=True, net='utility', condition=f'Continuation fromTP{number-1} toTP{number}; System1 upstream boundary retained.175291 labels UAF5/7 rather than UEF5/7,qualified by equipment/route context.' if number == 6 else '175290 shows DFDS continuation fromUEF4 throughUEF5 toUEF6; accepted System1 upstream boundary retained.')
        targets = {27:'EAC-4A',28:'EAC-5A',29:'EAC-5B',30:'EAC-9',31:'EAC-4B',32:'EAC-5A',33:'EAC-5B',34:'EAC-9'} if number == 5 else {35:'EAC-5B',36:'EAC-5B',37:'EAC-7',38:'EAC-5A',39:'EAC-5A',40:'EAC-7'}
        for n, target in targets.items():
            fas, pru = labels[f'UEF-{number} FAS-{n}'], labels[f'UEF-{number} PRU-{n}']
            local_owner(fas); local_owner(pru)
            for main in mains:
                fact(main, 'utility_supply_to', fas, 2, [.055,.05,.63,.58], True, 'utility', 'Paired air/water branch to existing numbered FAS; accepted FAS-to-PRU pair reused.')
            spray = new(f'spray{n}', f'UEF-{number} spray-header group downstream PRU-{n}', 'functional_assembly', house, 2, [.055,.05,.63,.58], house)
            fact(pru, 'utility_supply_to', spray, 2, [.055,.05,.63,.58], True, 'utility', 'Same-number regulated spray-header branch; no pressure setting inferred.')
            fact(spray, 'serves_equipment', labels[target], 2, [.055,.05,.63,.58], True, 'utility', 'Consumer label transcribed from this specific piping sheet, not inferred from numeric or alphabetical order.')
            role = 'Main discharge zone.' if number == 5 and n in [27,31] else 'Tripper discharge zone.' if number == 6 and n in [35,38] else 'Receiving zone; selected material route controls application.'
            fact(spray, 'equipment_role', role, 2, [.055,.05,.63,.58])
        wash = new('wash', f'UEF-{number} service-water hose and washdown group', 'functional_assembly', house, place=house)
        fact(wash, 'assembly_arrangement', 'Service-water hose boxes and tapping arrangement; existing common SW1 building supply retained. Local fittings and exact physical SW/PW branch extensions deferred.')
        fact(labels[f'UEF-{number} potable-water tank and tap assembly'], 'document_note', '175290 local tank detail300L agrees withGA.' if number == 5 else '175291 has300L elevation/detail and250L plan, whileGA175038 says250L. One local tank assembly; final capacity unresolved.')
        if number == 6:
            fact(house, 'document_note', '175291p2 explicitly maps35/36 to5B and38/39 to5A; retained even though numbering may suggest the opposite. UAF5/7 continuation labels qualified as source wording; other sheets sayUEF5/7.')
        gaps = ['Both piping sheets visually reviewed and reviewp3 read. FIO design status retained. Existing FAS/PRUs reused; spray application grouped by source-specific consumer. No new common station or Yard1 utility equipment. Nozzle/valve BOM,settings and local SW/PW branches deferred.']
    out = ROOT / 'output/plant-enrichment/B13' / args.scope
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'accepted/commit-log.json').exists()
    (out / 'baseline-model.json').write_text(json.dumps(m), encoding='utf8')
    pkg = dict(document_id=doc, baseline_version=m['version'], baseline_model=(out/'baseline-model.json').relative_to(ROOT).as_posix(), expected_new_components=len(nodes), visual_ids=[e['id'] for e in evs], body=dict(summary='B13 Tier1 '+args.scope+' major equipment and locations', operations=ops, intake_assessment=dict(route='mixed', purpose='Conveyor5 andTP5/6 breadth: shared identities, exact branches and local services', questions=['Which major assemblies and local route/service connections are supported?'], reviewed_evidence_ids=[e['id'] for e in evs], gaps=gaps)))
    (out / 'package.json').write_text(json.dumps(pkg, indent=2)+'\n', encoding='utf8')
    print(dict(scope=args.scope, components=len(nodes), operations=len(ops), baseline=m['version']))


if __name__ == '__main__':
    main()
