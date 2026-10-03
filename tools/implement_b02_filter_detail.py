"""One-time source-reviewed 32 NB DFDS duplex-filter detail from v622."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store
from chp.reviewed_ingestion import stage
from chp.patches import validate, commit
from tools.implement_b00_corrections import save, support

BASE = ROOT / 'output/plant-enrichment/B02/filter-detail'
DOC = 'doc_48b502990d1f45009641'
SCHEDULE = 'ev_efbbaa134f264013a170'
GA = 'ev_d87b2abca5f943baa149'
REFERENCE = 'ent_a7f4613ef85b4b5bbf72'
FILTERS = [
    (1, 'ent_24964c483cf14e2188d8', 'ent_bdf8e7e7f7f8485b80fe', 2.2),
    (2, 'ent_d380e5eec9aa434f8c64', 'ent_36135b45a07c4d03bf06', 1.9),
]


def package(model, evidence):
    ops = []
    basis = ('Vendor175266 cover Rev02 dated10-Jun-2020/FIO29-Jun-2020; '
             '32NB GA883C213592 Rev2, PDFp3, DFDS1/2 columns. '
             'Source design detail, not installed inspection or final pump duty; '
             'flow rows retain older2.2/1.9m3/h@6bar bases alongside accepted later pump duties.')

    def fact(subject, predicate, value, region, eid=GA, relation=False, unit=None, kind='specification', origin='explicit'):
        op = {'op': 'assert', 'subject': subject, 'predicate': predicate,
              'object_entity' if relation else 'value': value,
              'context': {'kind': kind, 'basis': basis}, **support(eid, region)}
        if unit: op['unit'] = unit
        op['origin'] = origin
        ops.append(op)

    def node(n, key, label, cls, owner, house, qty, region):
        temp = f'tmp_dfds{n}_filter_{key}'
        ops.append({'op': 'entity', 'id': temp, 'label': f'DFDS-{n} DUP-01 {label}', **support(GA, region)})
        fact(temp, 'instance_of', cls, region, kind='classification')
        fact(temp, 'part_of', owner, region, relation=True)
        fact(temp, 'located_at', house, region, relation=True, origin='inferred')
        fact(temp, 'quantity', qty, region, unit='Nos')
        return temp

    types = {o['key'] for o in model['ontology']}
    definitions = [
        ('filter_cover_group', 'entity_type', 'Removable filter cover-flange group from the applicable vendor BOM.', 'string'),
        ('filter_support_group', 'entity_type', 'Filter support-angle group; quantity and foundation loads are source design values.', 'string'),
        ('valve_group', 'entity_type', 'Source-counted valve group within one equipment assembly.', 'string'),
        ('plug_group', 'entity_type', 'Source-counted vent or drain threaded plugs/couplings; no invented operating valve.', 'string'),
        ('hydrostatic_test_pressure', 'property', 'Source-stated design hydrostatic test pressure; not proof of a completed test.', 'number'),
    ]
    for key, kind, definition, value_type in definitions:
        assert key not in types
        ops.append({'op': 'define', 'key': key, 'kind': kind, 'definition': definition,
                    'cardinality': 'many', 'value_type': value_type, **support(GA, [.45,.075,.98,.95])})

    old = next(a for a in model['assertions'] if a['canonical_subject'] == REFERENCE
               and a['predicate'] == 'instance_of' and not a['retirement'])
    ops.append({'op': 'retire', 'assertion_id': old['id'],
                'reason': 'The source contains eight separately scoped filter schedule rows and five size-specific GAs. Generic Utility Duplex Filters is a design reference, not a ninth installed physical filter.',
                **support(SCHEDULE, [.14,.125,.88,.64])})
    fact(REFERENCE, 'instance_of', 'equipment_design_reference', [.14,.125,.88,.64], SCHEDULE, kind='classification')
    fact(REFERENCE, 'design_applicability',
         'Source175266 inventories separate DFDS1/2, SW1/2, DW, CHP stockpile, LHP stockpile and feed-water filters. This generic record indexes the vendor design; it is not merged with either DFDS DUP01. Other-service applicability remains B03/B04.',
         [.14,.125,.88,.64], SCHEDULE)
    table = [.03,.66,.45,.93]
    bom = [.652,.345,.962,.75]
    for n, filt, house, flow in FILTERS:
        fact(REFERENCE, 'design_detail_applies_to', filt, [.25,.30,.88,.465], SCHEDULE, relation=True)
        fact(filt, 'design_applicability',
             f'Schedulep2 explicitly maps DFDS-{n},32NB,DUP01,quantity1 to P&ID175089-ISG2. GA p3 explicitly includes DFDS-{n} in its design-data column. Revision references differ from accepted175089 Rev1; vendor scope is applicable design, not evidence of field installation.',
             [.25,.30,.88,.465], SCHEDULE)
        fact(filt, 'model_number', 'Gujarat Otofil 2395D32 / GA883C213592 Rev2', [.652,.753,.977,.95])
        fact(filt, 'nominal_diameter', 32, table, unit='mm')
        fact(filt, 'quantity', 1, table, unit='Nos')
        fact(filt, 'rated_flow', flow, table, unit='m3/h')
        fact(filt, 'nominal_pressure', 6, table, unit='bar(g)')
        fact(filt, 'maximum_working_pressure', 10, table, unit='bar(g)')
        fact(filt, 'operating_temperature', 45, table, unit='degC')
        fact(filt, 'design_temperature_limit', 65, table, unit='degC')
        fact(filt, 'hydrostatic_test_pressure', 15, table, unit='bar(g)')
        fact(filt, 'filter_mesh', 100, table, unit='mesh')
        fact(filt, 'operating_requirement',
             'Clear/clarified water design; allowable clean/50%-clogged pressure-drop row is1.5/4MWC at maximum flow. This vendor allowance is not the existing DPS01 alarm/trip setting. Gross/net filtration area1735.5/398cm2 and printed ratio4.3:1 retained as reported.', table)
        fact(filt, 'maintenance_requirement',
             'GA provides removable covers/lifting handles, spring-supported elements and vent/drain threaded plugs. Inspection/testing is per approved QAP; no completed inspection, changeover procedure, cleaning interval or isolation completeness is established.', [.03,.075,.63,.66])
        element = node(n, 'baskets', 'Basket element group', 'filter_element_group', filt, house, 2, [.45,.305,.635,.545])
        fact(element, 'equipment_role', 'Two removable basket elements per duplex-filter assembly. BOM items14/15 form the mesh and perforated backing; source-group quantities are per whole filter.', bom)
        mesh = node(n, 'mesh', 'Basket wire-mesh group', 'filter_element_group', element, house, 2, [.652,.523,.962,.55])
        fact(mesh, 'component_material', 'SS304', [.652,.523,.962,.55])
        fact(mesh, 'filter_mesh', 100, [.652,.523,.962,.55], unit='mesh')
        fact(mesh, 'equipment_role', 'BOM item14:100mesh,43SWG stainless wire mesh,41%open. Mesh count is not a micron rating.', [.652,.523,.962,.55])
        backing = node(n, 'backing', 'Basket perforated backing-sheet group', 'filter_element_group', element, house, 2, [.652,.497,.962,.526])
        fact(backing, 'component_material', 'SS304', [.652,.497,.962,.526])
        fact(backing, 'equipment_role', 'BOM item15:18G perforated sheet,6.25mm holes,8mm triangular pitch,56% open; backing is separate from100-mesh filtration medium.', [.652,.497,.962,.526])
        valves = node(n, 'changeover', 'Three-way ball-valve changeover group', 'valve_group', filt, house, 2, [.652,.547,.962,.568])
        fact(valves, 'equipment_role', 'BOM item13:two reduced-bore three-way ball valves,cast iron,1-1/4inch NB,flanged150#. GA shows inlet and outlet selection. No mechanically linked simultaneous changeover or current selected basket is established.', [.03,.075,.45,.66])
        vents = node(n, 'vents', 'Vent N3 plug-and-coupling group', 'plug_group', filt, house, 2, [.652,.729,.962,.749])
        fact(vents, 'equipment_role', 'BOM item1:two SA105 half-inch NPT female vent couplings with plugs. Plugged vent openings, not automatic vent valves.', [.652,.729,.962,.749])
        drains = node(n, 'drains', 'Drain N4 plug-and-coupling group', 'plug_group', filt, house, 2, [.652,.566,.962,.586])
        fact(drains, 'equipment_role', 'BOM item12:two SA105 three-quarter-inch NPT female drain couplings with plugs. No drain destination or automatic drain established.', [.652,.566,.962,.586])
        covers = node(n, 'covers', 'Removable cover-flange group', 'filter_cover_group', filt, house, 2, [.652,.71,.962,.732])
        fact(covers, 'component_material', 'IS2062GrB,6inch NB blind raised-face150# flanges', [.652,.71,.962,.732])
        supports = node(n, 'supports', 'Leg-support angle group', 'filter_support_group', filt, house, 4, [.652,.601,.962,.623])
        fact(supports, 'component_material', 'IS2062GrB,L40x40x5mm', [.652,.601,.962,.623])
        fact(supports, 'equipment_role', 'Four leg-support angles in BOM; separate pedestal table states115kg total foundation load and57.5kg per leg support. Drawing describes two base support positions. Do not infer four times57.5kg; grouping discrepancy retained.', [.03,.075,.962,.66])

    return {'document_id': DOC, 'visual_ids': [SCHEDULE, GA], 'body': {
        'summary': 'B02: separately applicable DFDS1/2 32NB duplex-filter vendor internals and qualified design ratings',
        'operations': ops,
        'intake_assessment': {'route': 'mixed',
            'purpose': 'Map explicit vendor schedule to existing two DFDS filters and add maintainable groups without merging generic or other-service filters.',
            'questions': ['Which vendor GA applies to each DFDS DUP01?', 'Which basket/changeover/cover/vent/drain groups and design ratings are supported?'],
            'reviewed_evidence_ids': [e['id'] for e in evidence],
            'gaps': ['All seven original pages visually inventoried; pp2/3 enlarged and semantically reviewed. Other sizes on pp4-7 belong B03/B04 and are not applied to DFDS.',
                     'Vendor175089-ISG2 schedule versus accepted175089 Rev1 and older filter duty versus later pump duty remain qualified design bases.',
                     'No commissioned DPS setting, installed test certificate, cleaning interval or complete isolation procedure.',
                     'BOM four support angles versus two support positions and57.5kg per support remains explicit; no derived four-support load.']}}}


def verify(before, after, out):
    facts = {a['id']: a for a in after['assertions']}
    intended = next(a['id'] for a in before['assertions'] if a['canonical_subject'] == REFERENCE and a['predicate'] == 'instance_of' and not a['retirement'])
    for a in before['assertions']:
        if a['id'] == intended:
            assert {k:v for k,v in a.items() if k != 'retirement'} == {k:v for k,v in facts[a['id']].items() if k != 'retirement'}
            assert facts[a['id']]['retirement']
        else: assert a == facts[a['id']], a['id']
    aliases = {a['id']: a for a in after['aliases']}
    assert all(a == aliases[a['id']] for a in before['aliases'])
    assert before['merges'] == after['merges'] and before['conflicts'] == after['conflicts']
    nodes = [e for e in after['entities'] if e['created_version'] > 622]
    assert len(nodes) == 16
    for n, filt, house, flow in FILTERS:
        mine = [e['id'] for e in nodes if e['label'].startswith(f'DFDS-{n} ')]
        assert len(mine) == 8
        for entity in mine:
            own = [a for a in after['assertions'] if a['canonical_subject'] == entity and a['predicate'] == 'part_of' and not a['retirement']]
            assert len(own) == 1
            loc = [a for a in after['assertions'] if a['canonical_subject'] == entity and a['predicate'] == 'located_at' and not a['retirement']]
            assert len(loc) == 1 and loc[0]['canonical_object'] == house
    save(out/'result.json', {'ok': True, 'version': after['version'], 'new_components': 16,
                             'added_assertions': len(after['assertions'])-len(before['assertions']),
                             'intentional_retirement': intended, 'preserved_prior_assertions': len(before['assertions'])-1,
                             'prior_aliases_merges_conflicts_unchanged': True})


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--apply', action='store_true'); args = p.parse_args()
    plant = ROOT/'data/plant'; out = BASE/('accepted' if args.apply else 'rehearsal'); out.mkdir(parents=True, exist_ok=True)
    assert not (out/'commit-log.json').exists(), 'One-time package; inspect partial state rather than replay.'
    before = json.loads((ROOT/'output/plant-enrichment/B02/review/vendor/baseline-model-v622.json').read_text(encoding='utf8'))
    evidence = json.loads((ROOT/'output/plant-enrichment/B02/review/vendor'/f'{DOC}.json').read_text(encoding='utf8'))
    pkg = package(before, evidence)
    with sqlite3.connect((plant/'plant.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row; db.execute('BEGIN')
        live = Store.__new__(Store).model(db=db)
        assert live == before and live['version'] == 622
        assert not db.execute("SELECT id FROM proposals WHERE status='pending'").fetchall()
        if not args.apply:
            backup = BASE/'backup-v622'; backup.mkdir(exist_ok=True)
            for dest in [out/'plant.sqlite3', backup/'plant.sqlite3']:
                with sqlite3.connect(dest) as dst: db.backup(dst)
            sha = '830a7cf2c96c1a7e419efdb663926d962343efe37f3204328f90d55d039e2b7a'
            assert hashlib.sha256((plant/'originals'/sha).read_bytes()).hexdigest() == sha
            paths = {Path('originals')/sha}|{Path('renders')/e['image'] for e in evidence if e['image']}
            for rel in paths:
                dest = backup/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(plant/rel,dest)
            save(backup/'manifest.json', {'version':622,'scope':'Consistent complete SQLite database plus immutable original and all seven rendered pages for affected source.', 'files':sorted(str(p) for p in paths)})
    if args.apply:
        assert pkg == json.loads((BASE/'rehearsal/package.json').read_text(encoding='utf8'))
        assert json.loads((BASE/'rehearsal/result.json').read_text(encoding='utf8'))['ok']
    save(out/'package.json',pkg); store = Store(plant if args.apply else out)
    report = validate(store, {k:pkg['body'][k] for k in ['summary','operations']}, DOC, 622, visual_ids=pkg['visual_ids'])
    save(out/'validation.json',report); assert not report['errors'],report
    staged = stage(store,DOC,pkg['body'],visual_ids=pkg['visual_ids'],analysis_dir=str(out),expected_version=622)
    accepted = commit(store,staged['proposal_id']);save(out/'commit-log.json',[{'proposal_id':staged['proposal_id'],**accepted}])
    after = store.model();save(out/'model.json',after);verify(before,after,out)
    print(json.dumps({'proposal':staged['proposal_id'],'version':after['version'],'mode':out.name}))


if __name__ == '__main__': main()
