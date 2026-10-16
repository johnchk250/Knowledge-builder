"""Source-reviewed Yard3 Tier1 local-service packages (B22 Pass A). Never replay acceptance."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store

DOCS = {'philosophy': 'doc_e17edf6897d746fabe12',
        'qrc': 'doc_5a36f2843d504d6e96de',
        'stacker-dss': 'doc_0f52c77514a74773ae30',
        'reclaimer-dss': 'doc_a6a2fa82944f4d12b8aa'}

PHIL_BASIS = ('Stockpile DS/SP operation philosophy 175319 Rev5, approved 26-May-2020. '
              'Yard 3 (Stockpile-3/EAE-3, SC-03) scope only; stockpile-1/2/4 values are retained '
              'as stated pairing context, not Yard 3 claims. Design/control arrangement; '
              'installed and commissioned state unverified.')
PID_BASIS = ('SPDS P&ID 175255 Rev2, FIO 21-Jan-2019. Yard 3 makeup-tapping scope '
             '(note 9, BOM item 19, typical QRC connection). Design arrangement; '
             'routing and installation unverified.')
STACKER_BASIS = ('Chemtrols coal stacker plain-water DSS design/control Rev05, FIO 23-Jan-2021. '
                 'Coal section only; limestone dry-fog section is excluded. Project-family design '
                 'applied to the Yard 3 machine identified by coal-flow 175001 Rev8. Component names '
                 'without plant tags are descriptive. Installed configuration and commissioned '
                 'settings are not verified.')
RECLAIMER_BASIS = ('F. Harley plain-water DS BOD 47039284 Rev1, approved 19-Aug-2019, four portal '
                   'reclaimers. Project-family design applied to the Yard 3 machine identified by '
                   'coal-flow 175001 Rev8. Component names without plant tags are descriptive. '
                   'Installed configuration and commissioned settings are not verified.')

SECTOR_MAP = ('Sectors 1-14 pair Yard3 opposite-side sprinklers under SC-03: '
              'S1 SV-57 (00EAE03SV201) + SV-71 (00EAE03SV202); S2 SV-58 (SV203) + SV-72 (SV204); '
              'S3 SV-59 (SV205) + SV-73 (SV206); S4 SV-60 (SV207) + SV-74 (SV208); '
              'S5 SV-61 (SV209) + SV-75 (SV210); S6 SV-62 (SV211) + SV-76 (SV212); '
              'S7 SV-63 (SV213) + SV-77 (SV214); S8 SV-64 (SV215) + SV-78 (SV216); '
              'S9 SV-65 (SV217) + SV-79 (SV218); S10 SV-66 (SV219) + SV-80 (SV220); '
              'S11 SV-67 (SV221) + SV-81 (SV222); S12 SV-68 (SV223) + SV-82 (SV224); '
              'S13 SV-69 (SV225) + SV-83 (SV226); S14 SV-70 (SV227) + SV-84 (SV228). '
              'Each sector runs with its two Yard4 counterparts (SV-85..112) as a 4-solenoid group: '
              '2 min on, 20 s changeover, 33 min full cycle; SC-03 and SC-04 start/stop together from DDCMIS after SC-01/SC-02.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scope', choices=DOCS)
    args = ap.parse_args()
    store = Store(ROOT / 'data/plant')
    model = store.model()
    print('live version', model['version'])
    labels = {e['label']: e['canonical_id'] for e in model['entities'] if not e.get('inactive')}
    doc = DOCS[args.scope]
    evs = store.rows('SELECT id,page FROM evidence WHERE document_id=? ORDER BY page', (doc,))
    ev = {}
    for e in evs:
        ev.setdefault(e['page'], e['id'])
    all_ids = [e['id'] for e in evs]
    vis = [r['id'] for r in store.rows('SELECT id FROM evidence WHERE document_id=? AND image IS NOT NULL', (doc,))]
    ops, nodes = [], []

    def proof(eid, r):
        return dict(origin='explicit', confidence=0.98, evidence=[dict(evidence_id=eid, quote='', region=r)])

    def fact(s, p, v, eid, r, obj=False, unit=None, kind='specification', basis=None, net=None, condition=None):
        ctx = dict(kind='classification' if p in ('instance_of', 'part_of') else kind,
                   basis=basis or {'philosophy': PHIL_BASIS, 'qrc': PID_BASIS,
                                   'stacker-dss': STACKER_BASIS, 'reclaimer-dss': RECLAIMER_BASIS}[args.scope])
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
        tid = 'tmp_b22_' + args.scope.replace('-', '') + '_' + key
        ops.append(dict(op='entity', id=tid, label=label, **proof(eid, r)))
        fact(tid, 'instance_of', typ, eid, r)
        fact(tid, 'part_of', owner, eid, r, obj=True)
        nodes.append(tid)
        return tid

    if args.scope == 'philosophy':
        p2, p3, p4, p5 = ev[2], ev[3], ev[4], ev[5]
        yard3 = labels['Coal Yard 3']
        sc03 = labels['Stockpile Sequential Controller SC-03']
        spds = new('spds', 'Coal Yard 3 SPDS', 'dust_suppression_system', yard3, p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'equipment_role', 'Suppress fugitive dust over EAE-3 with the yard ring header and automatic swivelling sprinklers.', p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'quantity', 28, p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'assembly_arrangement', 'Two side headers with 14 sprinklers each (AP-57 to AP-84); swivelling part-circle sprinklers on vertical risers from the ring header; solenoid per riser with manual globe and gate isolation valves.', p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'operating_requirement', 'Maximum four sprinklers across stockpiles 3 and 4 simultaneously; two per stockpile, one per side, so the top surface is covered from both sides.', p3, [0.06, 0.20, 0.94, 0.36])
        fact(spds, 'operating_requirement', 'Auto sequential with local manual selection; sequential controller ON/OFF from DDCMIS with local push-button backup and AUTO/MANUAL selector.', p3, [0.06, 0.06, 0.94, 0.30])
        fact(spds, 'document_note', 'Stockpile water route: Pump House-2 (near UEF-7) SPDSP pumps draw common Tank-2 to the common header, then a ring header around each stockpile. Pump ratings and head values live in B01/B03 qualifications, not re-asserted here.', p2, [0.06, 0.10, 0.94, 0.20])
        sector = new('sectors', 'Coal Yard 3 SPDS sector control group', 'functional_assembly', spds, p4, [0.06, 0.35, 0.94, 0.95])
        fact(sector, 'equipment_role', 'SC-03 automatic-sequential / local-manual control grouping for Yard 3 opposite-side sprinkler pairs; not a separate physical machine.', p4, [0.06, 0.35, 0.94, 0.50])
        fact(sector, 'assembly_arrangement', SECTOR_MAP, p4, [0.06, 0.35, 0.94, 0.95])
        fact(sector, 'source_discrepancy', 'Page 4 application-point line prints the paired SC-04 range as Stockpile-2 although its KKS tags read 00EAE04 (stockpile 4); retained as printed. Yard 3 claims use only the SC-03/00EAE03 rows (AP-57..84 and SV-57..84).', p4, [0.04, 0.30, 0.94, 0.40])
        fact(sector, 'document_note', 'SC-03 Sector-1 to Sector-12 rows appear on page 4 and Sector-13 to Sector-14 rows continue at the top of page 5; all 28 Yard 3 valves print 00EAE03SV201..228 cleanly.', p5, [0.04, 0.04, 0.94, 0.20])
        fact(sc03, 'control_signal_to', sector, p4, [0.06, 0.30, 0.94, 0.45], obj=True, net='control', condition='Auto sequential programme or local manual selection per philosophy.')
        risers = new('risers', 'Coal Yard 3 SPDS Sprinkler risers AP-57 to AP-84', 'functional_assembly', spds, p4, [0.06, 0.30, 0.94, 0.40])
        fact(risers, 'equipment_role', 'Local physical spray points; distinct from functional sector grouping.', p4, [0.06, 0.30, 0.94, 0.40])
        fact(risers, 'assembly_arrangement', 'AP-57 to AP-84 (KKS 00EAE03QN201) on the two EAE-3 side headers; each riser carries a solenoid valve on the sequential controller plus a manual flow globe valve and an isolation gate valve.', p4, [0.06, 0.30, 0.94, 0.40])
        fact(risers, 'source_gap', 'AP and SV ranges and sector pairs are documented, but a unique AP-to-SV cross-reference and surveyed riser coordinates are not established.', p4, [0.06, 0.30, 0.94, 0.40])
        gaps = ['Philosophy pp1-18 fully read; pp2-5 carry Yard 3 scope. Valve/nozzle internals, commissioned timings, DDCMIS loop wiring and field coordinates deferred to depth queue. Pump ratings/heads remain B01/B03 qualifications. No Yard 1/2 sector/AP/SV values copied; every Yard 3 tag comes from the SC-03 rows.']
        summary = 'B22 Yard3 SPDS system, sector control and riser groups'
        purpose = 'Yard3 local SPDS identity, SC-03 sector/SV map and AP riser groups at Tier1 from the stockpile philosophy'
        questions = ['Which SC-03 sectors, SVs and APs serve EAE-3?', 'How is Yard3 sequential control grouped and timed?']
    elif args.scope == 'qrc':
        p1 = ev[1]
        spds = labels['Coal Yard 3 SPDS']
        ead3 = labels['EAD-3']
        eaf3 = labels['EAF-3']
        qrcm = new('qrc', 'Coal Yard 3 SPDS Machine makeup QRC connections', 'utility_header', spds, p1, [0.10, 0.60, 0.26, 0.74])
        fact(qrcm, 'equipment_role', 'Provide makeup water connections for machine onboard tanks.', p1, [0.44, 0.60, 0.74, 0.90])
        fact(qrcm, 'nominal_diameter', 32, p1, [0.66, 0.22, 0.98, 0.56], unit='mm')
        fact(qrcm, 'device_spacing', 30, p1, [0.44, 0.60, 0.74, 0.90], unit='m')
        fact(qrcm, 'assembly_arrangement', 'Quick-release couplings with isolation valves at 30 m intervals for makeup water for the stacker and reclaimer machines; 92 project QRC positions in the major BOM, per-yard share not stated.', p1, [0.44, 0.60, 0.74, 0.90])
        fact(qrcm, 'serves', ead3, p1, [0.44, 0.60, 0.74, 0.90], obj=True, net='utility', condition='Makeup-water tapping for the stacker onboard tank; hose connection method and routing detail deferred.')
        fact(qrcm, 'serves', eaf3, p1, [0.44, 0.60, 0.74, 0.90], obj=True, net='utility', condition='Makeup-water tapping for the reclaimer onboard tank; hose connection method and routing detail deferred.')
        gaps = ['SPDS P&ID p1 fully reviewed (strips, pump house, BOM, typicals, notes). Per-yard QRC count share, valve/nozzle internals and installed routing deferred to depth queue. No Yard1/2 QRC values copied; diameter/spacing come from this P&ID BOM/note.']
        summary = 'B22 Yard3 machine makeup QRC group and machine links'
        purpose = 'Yard3 onboard-tank refill boundary at Tier1 from the SPDS P&ID makeup note'
        questions = ['Where do EAD-3/EAF-3 onboard tanks get makeup water?']
    elif args.scope == 'stacker-dss':
        p21 = ev[21]
        ead3 = labels['EAD-3']
        dss = new('dss', 'EAD-3 Onboard plain-water DSS', 'dust_suppression_system', ead3, p21, [0.18, 0.16, 0.94, 0.91])
        fact(dss, 'equipment_role', 'Suppress dust at tripper discharge, boom receipt and boom discharge.', p21, [0.18, 0.30, 0.94, 0.55])
        fact(dss, 'location_description', 'Pump skid, tank and accessories on the stacker machine; dedicated headers near the three spray points.', p21, [0.18, 0.16, 0.94, 0.30])
        fact(dss, 'assembly_arrangement', 'Motor-driven pumps 1 working + 1 standby with suction duplex filter and differential-pressure switch, isolation/throttle valves, pressure switch/relief/gauge, globe valves, tangential circle-jet nozzles and water tank with level accessories; manual/remote via CZMC DCS/PLC with auto start from conveyor-drive contacts. Coal plain-water section only.', p21, [0.18, 0.55, 0.94, 0.91])
        fact(dss, 'source_gap', 'Duplex/simplex filter wording reconciliation, commissioned set points and installed skid serials need vendor/nameplate verification; deferred to depth.', p21, [0.18, 0.55, 0.94, 0.91])
        gaps = ['Stacker DS DBR coal plain-water control sections (pp20-23) reviewed; limestone dry-fog sections explicitly excluded from all claims. Pump/nozzle ratings, set points and installation detail deferred to depth queue. No Yard1/2 DSS values copied.']
        summary = 'B22 EAD-3 onboard plain-water DSS group'
        purpose = 'EAD-3 onboard dust suppression assembly at Tier1 from the coal-stacker DSS control philosophy'
        questions = ['What onboard dust suppression does EAD-3 carry and where does it spray?']
    else:
        p4 = ev[4]
        eaf3 = labels['EAF-3']
        qrcm = labels['Coal Yard 3 SPDS Machine makeup QRC connections']
        dss = new('dss', 'EAF-3 Onboard plain-water DSS', 'dust_suppression_system', eaf3, p4, [0.035, 0.22, 0.94, 0.855])
        fact(dss, 'equipment_role', 'Suppress fugitive coal dust during reclaim handling at the reclaimer application points.', p4, [0.035, 0.22, 0.94, 0.40])
        fact(dss, 'assembly_arrangement', '2000 L SS tank (2-hour storage) with level-switch PLC interlock, pumps 1 working + 0 standby on the mobile platform, DSS control panel, solenoid boxes with mist nozzles, 32NB x 50 m manual hose reel drum with QRC tank filling from header tap points, suction/discharge gauges with pressure switch and recirculation. Four-machine family design applied to EAF-3.', p4, [0.035, 0.22, 0.94, 0.70])
        fact(dss, 'source_discrepancy', 'Reclaimer GA prints approximate 2.2 kW DSS power (accepted B21 visual review, not re-cited here); this BOD builds its pump schedule around the PRP-1A tentative motor selection (accepted PRP-1A record). Final vendor/nameplate check required before assigning installed motor power.', p4, [0.035, 0.55, 0.94, 0.855])
        fact(qrcm, 'serves', dss, p4, [0.035, 0.40, 0.94, 0.60], obj=True, net='utility', condition='SS tank filling via hose reel from header tap points with QRC; detailed routing deferred.')
        gaps = ['Reclaimer DS DBR design-basis section (pp2-8) reviewed; calculation/BOM internals, commissioned set points and installation detail deferred to depth queue. No Yard1/2 DSS values copied.']
        summary = 'B22 EAF-3 onboard plain-water DSS group and QRC refill link'
        purpose = 'EAF-3 onboard dust suppression assembly and its header refill boundary at Tier1 from the reclaimer DSS design basis'
        questions = ['What onboard dust suppression does EAF-3 carry and how is its tank refilled?']
    out = ROOT / 'output/plant-enrichment/B22' / args.scope
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'accepted/commit-log.json').exists()
    assert not (out / 'rehearsal/commit-log.json').exists(), 'Clear prior rehearsal before rebuild'
    (out / 'baseline-model.json').write_text(json.dumps(model), encoding='utf8')
    pkg = dict(document_id=doc, baseline_version=model['version'],
               baseline_model=(out / 'baseline-model.json').relative_to(ROOT).as_posix(),
               expected_new_components=len(nodes),
               visual_ids=sorted(vis),
               body=dict(summary=summary, operations=ops,
                         intake_assessment=dict(route='mixed', purpose=purpose, questions=questions, gaps=gaps, reviewed_evidence_ids=sorted(all_ids))))
    (out / 'package.json').write_text(json.dumps(pkg, indent=2) + '
', encoding='utf8')
    print(json.dumps(dict(scope=args.scope, components=len(nodes), operations=len(ops), baseline=model['version'])))

if __name__ == '__main__':
    main()
