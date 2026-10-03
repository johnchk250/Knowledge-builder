"""Prepare source-reviewed DFDS control links at the reconciled v626 baseline."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'output/plant-enrichment/B02'
DOC = 'doc_294aacf286d246769e32'


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf8')


def main():
    snapshot = json.loads((BASE/'resume-v626.json').read_text(encoding='utf8'))
    model = snapshot['model']
    assert model['version'] == 626
    doc = next(d for d in snapshot['documents'] if d['id'] == DOC)
    assert hashlib.sha256((ROOT/'data/plant/originals'/doc['sha256']).read_bytes()).hexdigest() == doc['sha256']
    evidence = {e['page']: e for e in snapshot['evidence'] if e['document_id'] == DOC}
    assert set(evidence) == set(range(1, 33))
    entities = {e['id']: e for e in model['entities']}
    live = [a for a in model['assertions'] if not a['retirement']]
    ops = []
    reconciliation = []

    def add(subject, predicate, value, page, region, condition='', relation=False, inferred=False, additional=None):
        assert entities[subject]['canonical_id'] == subject
        context = {'kind': 'connection' if relation else 'specification',
                   'basis': f'175265 / IS-4-DB-702-110-M226 Rev2, 01-Jan-2019, FIO14-Jan-2019; original PDFp{page}. Source-specific design requirement; not commissioned or executable logic.'}
        if condition:
            context['condition'] = condition
        if relation:
            context.update(network='control', verification='documented')
            assert entities[value]['canonical_id'] == value
            assert not any(a['canonical_subject'] == subject and a['predicate'] == predicate and a['canonical_object'] == value for a in live)
        supports = [{'evidence_id': evidence[page]['id'], 'region': region}]
        for p, r in additional or []:
            supports.append({'evidence_id': evidence[p]['id'], 'region': r})
        ops.append({'op': 'assert', 'subject': subject, 'predicate': predicate,
                    'object_entity' if relation else 'value': value, 'context': context,
                    'origin': 'inferred' if inferred else 'explicit', 'confidence': .97,
                    'evidence': supports})

    systems = [
        (1, 'ent_2024dfa4a4084a86b0b5', ['ent_975edb9acc07451cbc62', 'ent_8a35251f220d4c9287d2'],
         'ent_eca67be446b14e6f8706', 'ent_f29313786c2242e89aed', 'ent_568564ff3bd948438f86'),
        (2, 'ent_b2f48e8d116f484882a1', ['ent_afdfc43f0f1148d0b555', 'ent_eca52aa5ec3d4d3fa153'],
         'ent_52a0bd107b394410bd8b', 'ent_c3e2e10247594533af74', 'ent_dbe58a4eb9a74ed6b0c4'),
    ]
    for number, system, pumps, ps, dps, tank in systems:
        page = 4 if number == 1 else 20
        general, level = page-2, page-1
        for pump in pumps:
            existing = [a for a in live if a['canonical_subject'] == pump and a['predicate'] in ('pump_start_permissive', 'pump_trip_condition')]
            assert len(existing) == 9, (pump, len(existing))
            reconciliation.append({'pump': pump, 'label': entities[pump]['label'],
                                   'preserved_individual_conditions': [a['id'] for a in existing]})
            add(pump, 'sequence_logic',
                f'175265 start grouping: Local starter-panel manual command in Local mode OR client PLC/DCS command in Remote mode; start requires ALL three listed conditions: overload O/L NOT operated AND low-level switch LLS NOT operated (RCC Water Tank-{number} not LOW) AND emergency-stop pushbutton NOT pressed. This restates the existing individual conditions as one AND group; it does not add an automatic standby command.',
                page, [.115,.45,.92,.672], inferred=True)
            add(pump, 'sequence_logic',
                f'175265 trip grouping: ANY of RCC Water Tank-{number} LLS operated (LOW) OR emergency-stop pressed OR overload O/L operated OR station PS-01 activated (pump pressure BELOW its set pressure) OR duplex-filter choked signal from its differential-pressure switch is listed as a pump trip. Delay, latch, reset and numerical thresholds are not stated in this source.',
                page, [.115,.681,.92,.849], inferred=True)
            add(pump, 'operating_requirement',
                'Keep 175265 control conditions source-qualified. Separate accepted control write-up 179162 p30 supplies its own standby-start, minimum-level, delayed low-pressure trip and suction-DP annunciation requirements. Those values/actions are not inserted into the 175265 logic. Resolve the filter-trip versus annunciation difference and final delay/reset behaviour against approved cause-and-effect, PLC logic and commissioning records.',
                page, [.115,.45,.92,.849], inferred=True)
            add(ps, 'control_signal_to', pump, page, [.115,.681,.92,.849], relation=True,
                condition=f'DFDS-{number} PS-01 activated when pump pressure is BELOW its set pressure: source-listed trip of {entities[pump]["label"]}. Numerical threshold/delay/reset unstated in175265; preserve separate schedule High wording and later write-up delay without combining their bases.')
            add(dps, 'control_signal_to', pump, page, [.115,.681,.92,.849], relation=True,
                condition=f'DFDS-{number} duplex-filter choked signal from its differential-pressure switch: source-listed trip of {entities[pump]["label"]} in175265. DPS-01 identity reused from accepted same-system suction-filter monitoring; later179162 high-suction-DP annunciation remains a separate unresolved source basis. No numerical threshold/delay/reset inferred.')
        add(ps, 'control_role',
            f'175265 PDFp{page} names station PS-01 as the low-pump-pressure trip initiator for DFDSP-{number}A and DFDSP-{number}B. Reuse the existing DFDSS-{number} PS-01 identity; this is distinct from downstream building air-pressure permissive switches. No numeric threshold or commissioned setting is supplied by this source.',
            page, [.115,.681,.92,.849])
        add(ps, 'source_discrepancy',
            '175265 explicitly states pump pressure BELOW the set pressure. The separately accepted instrument schedule179162 p53 labels Severity High. Preserve the literal schedule label; it does not reverse this source-specific low-pressure action or establish a commissioned contact polarity. Approved loop/cause-and-effect and field setting are needed to reconcile the meanings.',
            page, [.115,.681,.92,.849], inferred=True)
        add(dps, 'control_role',
            f'175265 PDFp{page} explicitly makes the differential-pressure switch across the duplex filter a choked-filter pump-trip initiator. Existing DFDSS-{number} DPS-01 and its accepted same-system DUP-01 monitoring relationship are reused. No additional switch or duplicate filter is created.',
            page, [.115,.681,.92,.849])
        add(dps, 'source_discrepancy',
            '175265 lists duplex-filter choked DPS among pump TRIP conditions. Separately accepted179162 p30 describes high suction DP as ANNUNCIATION. Both source actions remain visible; neither overrides the other here. The accepted schedule setpoint/range disagreement is also retained. Resolve final action, threshold, delay and reset with approved cause-and-effect/PLC and commissioning records.',
            page, [.115,.681,.92,.849], inferred=True)
        add(system, 'source_discrepancy',
            f'Within175265, general PDFp{general} says pump operation is interlocked with the tank High Level Switch, while explicit pump-start PDFp{page} says LLS NOT operated (not LOW). The intervening PDFp{level} separately states H opens the inlet motorized gate valve, HH closes it, and L trips the operating DFDS pump. Preserve these distinct statements; do not convert H into a new pump-start threshold.',
            general, [.17,.84,.91,.93], inferred=True,
            additional=[(page,[.115,.45,.92,.672]),(level,[.17,.194,.92,.484] if number==1 else [.17,.213,.92,.51])])
        add(tank, 'operating_requirement',
            '175265 describes one displacer level switch with HH/H/L contacts: H opens the inlet motorized gate valve; HH closes it; L trips the operating DFDS pump. Existing tank claims are preserved. This source gives no KKS/LS/MGV tag mapping or numerical elevations; final mapping to the shared-service level switch, inlet valve and (Tank-2) compartment requires the separate SW/PW control and runoff P&ID reconciliation. Do not create another sensor or infer a tagged control edge from this untagged description.',
            level, [.17,.194,.92,.484] if number==1 else [.17,.213,.92,.51])

    out = BASE/'pump-controls'
    save(out/'baseline-model.json', model)
    save(out/'reconciliation.json', {'baseline':626, 'systems':systems, 'preserved_conditions':reconciliation,
        'independently_reviewed_originals':{'175265':[1,2,3,4,18,19,20,32], '179162':[30,53,54]},
        'note':'179162 comparisons use its separately accepted facts; every new support is from175265. No current/source-logic settings are consolidated.'})
    inventory = []
    deep = {1,2,3,4,18,19,20,32}
    used = {s['evidence_id'] for op in ops for s in op['evidence']}
    for p, ev in evidence.items():
        inventory.append({'evidence_id':ev['id'], 'page':p,
            'review':'original page visually reviewed' if p in deep else 'text heading/scope inventory only; local application logic not reviewed for this package',
            'disposition':'used' if ev['id'] in used else 'corroborating' if p in deep else 'deferred-with-reason',
            'reason':'Common pump/level control scope' if p in deep else 'Local FAS/conveyor/selector conditions belong to the exact downstream consumer package; not missing source.'})
    save(out/'source-review.json', {'document_id':DOC,'sha256':doc['sha256'],'drawing':'175265 Rev2 / M226',
        'title_status':'01-Jan-2019; FIO14-Jan-2019; review sheet32 addresses earlierRev1',
        'inventory':inventory})
    save(out/'package.json', {'document_id':DOC,'baseline_version':626,
        'baseline_model':'output/plant-enrichment/B02/pump-controls/baseline-model.json','expected_new_components':0,
        'visual_ids':[evidence[p]['id'] for p in sorted(deep)],
        'body':{'summary':'B02: connect existing DFDS pressure/duplex-filter signals to all four pumps with source-specific control grouping and unresolved action differences',
            'operations':ops,'intake_assessment':{'route':'mixed',
                'purpose':'Reuse accepted controls and sensor identities; add missing supported signal edges and explicit source-qualified grouping, preserving original individual claims.',
                'questions':['Which existing station instruments initiate the listed pump trips?','Which AND/OR groupings and source differences must remain visible?'],
                'reviewed_evidence_ids':[e['id'] for e in evidence.values()],
                'gaps':['Document-wide text heading/scope inventory is recorded separately; only original pp1-4,18-20,32 were deeply reviewed for this bounded package. Other local-application pages are explicitly deferred, not semantically accepted.',
                        '175265 contains no numerical pump-trip threshold, delay, latch or reset; later179162 source bases remain separately accepted, not imported into these claims.',
                        'Filter choked trip versus later suction-DP annunciation and PS schedule High versus low-pressure action remain unresolved; no source is silently preferred.',
                        'Tank2 compartment and LS/MGV KKS mapping requires separate SW/PW and runoff reconciliation; no duplicate sensor or unsupported tagged level edge.',
                        'Compressor detail, local header takeoffs and final180055 motor evidence remain outside this milestone.']}}})
    print(json.dumps({'baseline':626,'operations':len(ops),'control_edges':sum(o['context']['kind']=='connection' for o in ops),'new_components':0}))


if __name__ == '__main__':
    main()
