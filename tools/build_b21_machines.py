"""Source-reviewed Yard3 Tier1 machine packages (B21 Pass A). Never replay acceptance."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store

DOCS = {'stacker': 'doc_78bebe6773984d59b013',
        'reclaimer': 'doc_3e81ea1c32df4215968d'}

STACKER_BASIS = ('Basis of design 175249 Rev2 approved 27-Feb-2019. Project-family design for four stackers; '
                 'applied to Yard 3 EAD-3 identified by coal-flow 175001 Rev8. Component names without plant tags are descriptive. '
                 'Installed configuration and commissioned settings are not verified.')
RECLAIMER_BASIS = ('GA 175127 Rev2 approved 23-Nov-2018. Project-family portal scraper design for EAF-1,2,3,4 (four machines); '
                   'applied to Yard 3 EAF-3 identified by coal-flow 175001 Rev8. Component names without plant tags are descriptive. '
                   'Installed configuration and commissioned settings are not verified.')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    ap.add_argument('--baseline-model-out', default=None)
    args = ap.parse_args()
    store = Store(ROOT / 'data/plant')
    model = store.model()
    print("live version", model['version'])
    labels = {e['label']: e['canonical_id'] for e in model['entities'] if not e.get('inactive')}
    doc = DOCS[args.scope]
    evs = store.rows('SELECT id,page FROM evidence WHERE document_id=? ORDER BY page', (doc,))
    ev = {}
    for e in evs:
        ev.setdefault(e['page'], e['id'])
    # map page->first evidence id; for p3 multi-block reclaimer use first block
    ev_by_page = ev
    all_ids = [e['id'] for e in evs]
    # visual ids: all with images
    vis = [r['id'] for r in store.rows('SELECT id FROM evidence WHERE document_id=? AND image IS NOT NULL', (doc,))]
    ops, nodes = [], []
    def proof(eid, r):
        return dict(origin='explicit', confidence=0.98, evidence=[dict(evidence_id=eid, quote='', region=r)])
    def fact(s, p, v, eid, r, obj=False, unit=None, kind='specification', basis=None, net=None, condition=None):
        ctx = dict(kind='classification' if p in ('instance_of', 'part_of') else kind, basis=basis or (STACKER_BASIS if args.scope == 'stacker' else RECLAIMER_BASIS))
        if net:
            ctx.update(kind='connection', network=net, verification='documented', condition=condition)
        o = dict(op='assert', subject=s, predicate=p, context=ctx, **proof(eid, r))
        if obj:
            o['object_entity'] = v
        else:
            o['value'] = v
        if unit is not None:
            o['unit'] = unit
        ops.append(o)
    def new(key, label, typ, owner, eid, r):
        assert label not in labels, label
        tid = 'tmp_b21_' + args.scope + '_' + key
        ops.append(dict(op='entity', id=tid, label=label, **proof(eid, r)))
        fact(tid, 'instance_of', typ, eid, r)
        fact(tid, 'part_of', owner, eid, r, obj=True)
        nodes.append(tid)
        return tid

    if args.scope == 'stacker':
        ead3 = labels['EAD-3']
        p1 = ev_by_page[1]; p2 = ev_by_page[2]; p3 = ev_by_page[3]
        # EAD-3 level Tier1 facts
        basis = STACKER_BASIS
        fact(ead3, 'design_applicability', 'Project-family stacker design for four machines applied to Yard 3 EAD-3 identified by coal-flow 175001 Rev8. Descriptive names; installed/commissioned state not verified.', p2, [0.15, 0.15, 0.92, 0.30])
        fact(ead3, 'assembly_arrangement', 'Unidirectional travelling, slewing and luffing stacker; one of four project-family machines.', p2, [0.15, 0.15, 0.92, 0.30])
        fact(ead3, 'rated_capacity', 3400, p3, [0.15, 0.35, 0.92, 0.50], unit='t/h')
        fact(ead3, 'design_capacity', 3740, p3, [0.15, 0.35, 0.92, 0.50], unit='t/h')
        fact(ead3, 'source_discrepancy', 'BOD material clause says crushed coal; yard conveyor GA and plant flow identify the pre-crushing stockyard stream. BOD wording preserved without changing the documented plant route.', p2, [0.15, 0.28, 0.92, 0.42])
        fact(ead3, 'rail_gauge', 8400, p3, [0.15, 0.28, 0.92, 0.35], unit='mm')
        # assemblies
        trav = new('travel', 'EAD-3 Travel system', 'functional_assembly', ead3, p3, [0.15, 0.15, 0.92, 0.30])
        fact(trav, 'equipment_role', 'Travel EAD-3 along the yard rails.', p3, [0.15, 0.15, 0.92, 0.30])
        fact(trav, 'assembly_arrangement', 'Electromechanical VVVF travel, 12 drives per machine in family design: 5.5 kW 1500 rpm synchronous motor per drive, 4-stage bevel-helical gear motor 141.93:1; operating 7 m/min, shunting 20 m/min. Per-unit motor serials and commissioned speeds not verified.', p3, [0.15, 0.15, 0.92, 0.30])
        slew = new('slew', 'EAD-3 Slew system', 'functional_assembly', ead3, p2, [0.15, 0.68, 0.92, 0.85])
        fact(slew, 'equipment_role', 'Slew the boom across the pile.', p2, [0.15, 0.68, 0.92, 0.85])
        fact(slew, 'assembly_arrangement', 'Hydraulic slew in family design: 22 kW 1500 rpm hydraulic drive motors (2 per machine), 0.7284 rpm output, slew gear z173 m25, pinion z18 m25, 3-row roller track dia ~4000 mm. Per-unit settings not verified.', p2, [0.15, 0.68, 0.92, 0.85])
        fact(slew, 'slew_range', '0 to 100 degrees', p2, [0.15, 0.68, 0.92, 0.85])
        fact(slew, 'slew_speed', 0.0758, p2, [0.15, 0.68, 0.92, 0.85], unit='rpm')
        luff = new('luff', 'EAD-3 Luffing system', 'functional_assembly', ead3, p2, [0.15, 0.84, 0.92, 0.97])
        fact(luff, 'equipment_role', 'Luff the boom head between stacking heights.', p2, [0.15, 0.84, 0.92, 0.97])
        fact(luff, 'assembly_arrangement', 'Hydraulic luffing in family design: hydraulic powerpack (22 kW 1500 rpm motor, coupling and pumps), cylinder bore 250 mm piston 180 mm stroke 2040 mm max 160 bar; luff range +14 to -8 degrees, head speed <=3 m/min. Per-unit pressure/setting not verified.', p2, [0.15, 0.84, 0.92, 0.97])
        boom = new('boom', 'EAD-3 Boom conveyor', 'conveyor', ead3, p2, [0.15, 0.50, 0.92, 0.68])
        fact(boom, 'equipment_role', 'Convey coal from the travelling tripper onto EAE-3 stockpile.', p2, [0.15, 0.50, 0.92, 0.68])
        fact(boom, 'assembly_arrangement', 'Boom conveyor drive in family design (2 per machine): RDOL electromechanical 2x132 kW 1485 rpm synchronous motors, 3-stage bevel-helical 20:1, fluid coupling, shrink disc, electro-hydraulic thruster brake drum dia 400 mm. Per-unit coupling/brake selection not verified.', p2, [0.15, 0.50, 0.92, 0.68])
        trip = new('tripper', 'EAD-3 Travelling tripper', 'tripper', ead3, p3, [0.15, 0.55, 0.92, 0.80])
        fact(trip, 'equipment_role', 'Receive EAC-11 coal and feed the boom conveyor.', p3, [0.15, 0.55, 0.92, 0.80])
        fact(trip, 'assembly_arrangement', 'Plain tripper for unidirectional yard conveyor in family design: horizontal ~47878 mm, inclined belt ~61480 mm, 2000 mm width, 35 deg trough, 100000 mm radius, 800 mm discharge pulley. Per-unit alignment not verified.', p3, [0.15, 0.55, 0.92, 0.80])
        cab = new('cabin', 'EAD-3 Operator cabin', 'operator_cabin', ead3, p3, [0.15, 0.35, 0.92, 0.55])
        fact(cab, 'equipment_role', 'Dust-proof air-conditioned operator cabin 2.4 m x 1.9 m x 2.4 m in family design.', p3, [0.15, 0.35, 0.92, 0.55])
        weigh = labels.get('EAD-3 Boom Belt Weigher')
        assert weigh, 'Expected existing EAD-3 weigher to reuse'
        fact(weigh, 'equipment_role', 'Load-cell belt scale on the boom conveyor discharge in family design.', p3, [0.15, 0.40, 0.92, 0.60])
        gaps = ['Stacker BOD pp1-6 fully read. Vendor motor/gearbox/brake internals, protection/setting tables, PLC/collision/travel-limit logic, storm-parking procedure, lube/DSS/fire/electrical-house detail and commissioned settings deferred to depth queue / B22. No Yard1 motor/lube counts copied; all drive notes are family-design assembly notes with per-unit verification outstanding.']
        summary = 'B21 Yard3 EAD-3 Tier1 stacker assemblies'
        purpose = 'Yard3 stacker EAD-3 motion assemblies at Tier1 from unit-specific family BOD against B15 applicability matrix'
        questions = ['Which travel/slew/luff/boom/tripper/cabin/weigher assemblies are supported for EAD-3?', 'What headline stacking ratings apply as family design?']
    else:
        eaf3 = labels['EAF-3']
        # need evidence ids per page; p3 has multiple blocks, use first p3 block id for all p3 claims
        p3ids = [e['id'] for e in evs if e['page'] == 3]
        p3 = p3ids[0]
        p1 = ev_by_page[1]
        basis = RECLAIMER_BASIS
        fact(eaf3, 'design_applicability', 'Project-family portal scraper design for EAF-1,2,3,4 (four machines) applied to Yard 3 EAF-3 identified by coal-flow 175001 Rev8. Descriptive names; installed/commissioned state not verified.', p3, [0.05, 0.05, 0.95, 0.25])
        fact(eaf3, 'rated_capacity', 1250, p3, [0.05, 0.10, 0.95, 0.25], unit='t/h')
        fact(eaf3, 'design_capacity', 1375, p3, [0.05, 0.10, 0.95, 0.25], unit='t/h')
        fact(eaf3, 'design_mass', 417, p3, [0.05, 0.10, 0.95, 0.25], unit='t')
        fact(eaf3, 'source_discrepancy', 'GA p3 wind rows print 16 km/h operating and 73 km/h non-operating; reclaimer BOD prints 16, 35 and 73 m/s. Units conflict; no trip or safe-operating threshold inferred.', p3, [0.05, 0.10, 0.95, 0.25])
        fact(eaf3, 'source_gap', 'Safety-instrument GA 179103 referenced on GA p3; travel/collision/hoist interlock loops and wind trip settings need verification. Structural limits are not automatic trips.', p3, [0.05, 0.70, 0.95, 0.90])
        main = new('main', 'EAF-3 Main scraper boom', 'functional_assembly', eaf3, p3, [0.05, 0.25, 0.50, 0.55])
        fact(main, 'equipment_role', 'Scrape coal down toward the reclaim conveyor (main boom).', p3, [0.05, 0.25, 0.50, 0.55])
        fact(main, 'assembly_arrangement', 'Main scraper chain in family design: 500 mm roller-bush chain, 1500 kN breaking, 37.145 m sprocket centres, 2500x500 mm blades at 1000 mm spacing, 0.69 m/s nominal; 2x110 kW 1500 rpm VFD squirrel-cage drives, 180:1 bevel-helical hollow-shaft, flexible coupling, shrink disc. Per-unit drive selection not verified; chain/brake internals deferred.', p3, [0.05, 0.25, 0.50, 0.55])
        aux = new('aux', 'EAF-3 Auxiliary scraper boom', 'functional_assembly', eaf3, p3, [0.50, 0.25, 0.95, 0.55])
        fact(aux, 'equipment_role', 'Scrape coal down toward the reclaim conveyor (auxiliary boom).', p3, [0.50, 0.25, 0.95, 0.55])
        fact(aux, 'assembly_arrangement', 'Aux scraper chain in family design: 400 mm roller-bush chain, 500 kN breaking, 14.8 m centres, 1800x450 mm blades at 800 mm spacing, 0.62 m/s nominal; 2x30 kW 1500 rpm VFD, 160:1 bevel-helical hollow-shaft, flexible coupling, shrink disc. Capacity 500-660 TPH per boom inclination note; final rating reconciliation deferred.', p3, [0.50, 0.25, 0.95, 0.55])
        hoist = new('hoist', 'EAF-3 Hoist system', 'functional_assembly', eaf3, p3, [0.05, 0.50, 0.95, 0.70])
        fact(hoist, 'equipment_role', 'Raise and lower the scraper booms.', p3, [0.05, 0.50, 0.95, 0.70])
        fact(hoist, 'assembly_arrangement', 'Hoist in family design: 1x45 kW 1500 rpm VFD squirrel-cage foot-mounted motor, 35.5:1 helical hollow-shaft with 5.294 connecting gear, flexible coupling with 315 dia brake drum, 2 thruster brakes (1 operating + 1 safety), 1300 mm winch drum, 800 mm sheaves, 28 mm rope. Per-unit brake/settings not verified.', p3, [0.05, 0.50, 0.95, 0.70])
        fact(hoist, 'operating_speed', 3, p3, [0.05, 0.50, 0.95, 0.70], unit='m/min')
        fact(hoist, 'rope_speed', 34, p3, [0.05, 0.50, 0.95, 0.70], unit='m/min')
        trav = new('travel', 'EAF-3 Travel system', 'functional_assembly', eaf3, p3, [0.05, 0.15, 0.95, 0.35])
        fact(trav, 'equipment_role', 'Travel EAF-3 along the 714.750 m yard rails.', p3, [0.05, 0.15, 0.95, 0.35])
        fact(trav, 'assembly_arrangement', 'Long travel in family design: 55.8 m span, UIC60 rail, 630 mm wheels (14 total, 8 driven), operating 2-8 m/min relocation 20 m/min max, 27 t max wheel load, 2x10 t hydraulic rail clamps plus manual clamps each side, 8 spring buffers. Per-unit clamp/buffer selection not verified.', p3, [0.05, 0.15, 0.95, 0.35])
        fact(trav, 'rail_span', 55.8, p3, [0.05, 0.15, 0.95, 0.35], unit='m')
        preel = new('powerreel', 'EAF-3 Power cable reel', 'cable_reel', eaf3, p3, [0.05, 0.55, 0.50, 0.70])
        fact(preel, 'equipment_role', 'Mono-spiral power cable reel for travel supply in family design.', p3, [0.05, 0.55, 0.50, 0.70])
        fact(preel, 'assembly_arrangement', 'Power reel 1 unit mono-spiral, electromechanical 7.5 kW drive with inbuilt brake in family design. Feeder/starter/VFD mapping is B43.', p3, [0.05, 0.55, 0.50, 0.70])
        creel = new('controlreel', 'EAF-3 Control cable reel', 'cable_reel', eaf3, p3, [0.50, 0.55, 0.95, 0.70])
        fact(creel, 'equipment_role', 'Mono-spiral control cable reel in family design.', p3, [0.50, 0.55, 0.95, 0.70])
        fact(creel, 'assembly_arrangement', 'Control reel 1 unit mono-spiral, electromechanical 3.7 kW drive in family design. Control logic is depth.', p3, [0.50, 0.55, 0.95, 0.70])
        gaps = ['Reclaimer GA pp1-6 fully read (p3 spec table plus review replies pp4-6). Vendor drive/brake internals, protection numeric settings, chain/blade take-up detail, lube/DSS/fire, safety-instrument loops and commissioned settings deferred to depth queue / B22. No Yard1 lube/DSS counts copied; all notes are family-design assembly notes with per-unit verification outstanding.']
        summary = 'B21 Yard3 EAF-3 Tier1 reclaimer assemblies'
        purpose = 'Yard3 reclaimer EAF-3 motion assemblies at Tier1 from unit-specific family GA against B15 applicability matrix'
        questions = ['Which main/aux boom, hoist, travel and cable-reel assemblies are supported for EAF-3?', 'What headline reclaim ratings apply as family design?']

    out = ROOT / 'output/plant-enrichment/B21' / args.scope
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'accepted/commit-log.json').exists()
    assert not (out / 'rehearsal/commit-log.json').exists(), 'Clear prior rehearsal before rebuild'
    baseline_path = out / 'baseline-model.json'
    baseline_path.write_text(json.dumps(model), encoding='utf8')
    pkg = dict(document_id=doc, baseline_version=model['version'],
               baseline_model=(out / 'baseline-model.json').relative_to(ROOT).as_posix(),
               expected_new_components=len(nodes),
               visual_ids=sorted(vis),
               body=dict(summary=summary, operations=ops,
                         intake_assessment=dict(route='mixed', purpose=purpose, questions=questions, gaps=gaps, reviewed_evidence_ids=sorted(all_ids))))
    (out / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(scope=args.scope, components=len(nodes), operations=len(ops), baseline=model['version'])))

if __name__ == '__main__':
    main()
