"""Source-reviewed Yard2 Tier1 local-service packages (B19 Pass A). Never replay acceptance."""
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
              'Yard 2 (Stockpile-2/EAE-2, SC-02) scope only; stockpile-1/3/4 values are retained '
              'as stated pairing context, not Yard 2 claims. Design/control arrangement; '
              'installed and commissioned state unverified.')
PID_BASIS = ('SPDS P&ID 175255 Rev2, FIO 21-Jan-2019. Yard 2 makeup-tapping scope '
             '(note 9, BOM item 19, typical QRC connection). Design arrangement; '
             'routing and installation unverified.')
STACKER_BASIS = ('Chemtrols coal stacker plain-water DSS design/control Rev05, FIO 23-Jan-2021. '
                 'Coal section only; limestone dry-fog section is excluded. Project-family design '
                 'applied to the Yard 2 machine identified by coal-flow 175001 Rev8. Component names '
                 'without plant tags are descriptive. Installed configuration and commissioned '
                 'settings are not verified.')
RECLAIMER_BASIS = ('F. Harley plain-water DS BOD 47039284 Rev1, approved 19-Aug-2019, four portal '
                   'reclaimers. Project-family design applied to the Yard 2 machine identified by '
                   'coal-flow 175001 Rev8. Component names without plant tags are descriptive. '
                   'Installed configuration and commissioned settings are not verified.')

SECTOR_MAP = ('Sectors 1-14 pair Yard2 opposite-side sprinklers under SC-02: '
              'S1 SV-29 (00EAE02SV201) + SV-43 (00EAE02SV202); S2 SV-30 (SV203) + SV-44 (SV204); '
              'S3 SV-31 (SV205) + SV-45 (SV206); S4 SV-32 (SV207) + SV-46 (SV208); '
              'S5 SV-33 (SV209) + SV-47 (SV210); S6 SV-34 (SV211) + SV-48 (SV212); '
              'S7 SV-35 (SV213) + SV-49 (SV214); S8 SV-36 (SV215) + SV-50 (SV216); '
              'S9 SV-37 (SV217) + SV-51 (SV218); S10 SV-38 (SV219) + SV-52 (SV220); '
              'S11 SV-39 (SV221) + SV-53 (SV222); S12 SV-40 (SV223) + SV-54 (SV224); '
              'S13 SV-41 (SV225) + SV-55 (SV226); S14 SV-42 (SV227) + SV-56 (SV228). '
              'Each sector runs with its two Yard1 counterparts (SV-1..28) as a 4-solenoid group: '
              '2 min on, 20 s changeover, 33 min full cycle; SC-01 and SC-02 start/stop together from DDCMIS.')


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
        tid = 'tmp_b19_' + args.scope.replace('-', '') + '_' + key
        ops.append(dict(op='entity', id=tid, label=label, **proof(eid, r)))
        fact(tid, 'instance_of', typ, eid, r)
        fact(tid, 'part_of', owner, eid, r, obj=True)
        nodes.append(tid)
        return tid

    if args.scope == 'philosophy':
        p2, p3, p4 = ev[2], ev[3], ev[4]
        yard2 = labels['Coal Yard 2']
        sc02 = labels['Stockpile Sequential Controller SC-02']
        spds = new('spds', 'Coal Yard 2 SPDS', 'dust_suppression_system', yard2, p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'equipment_role', 'Suppress fugitive dust over EAE-2 with the yard ring header and automatic swivelling sprinklers.', p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'quantity', 28, p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'assembly_arrangement', 'Two side headers with 14 sprinklers each (AP-29 to AP-56); swivelling part-circle sprinklers on vertical risers from the ring header; solenoid per riser with manual globe and gate isolation valves.', p2, [0.06, 0.10, 0.94, 0.30])
        fact(spds, 'operating_requirement', 'Maximum four sprinklers across stockpiles 1 and 2 simultaneously; two per stockpile, one per side, so the top surface is covered from both sides.', p2, [0.06, 0.20, 0.94, 0.30])
        fact(spds, 'operating_requirement', 'Auto sequential with local manual selection; sequential controller ON/OFF from DDCMIS with local push-button backup and AUTO/MANUAL selector.', p3, [0.06, 0.06, 0.94, 0.30])
        fact(spds, 'document_note', 'Stockpile water route: Pump House-2 (near UEF-7) SPDSP pumps draw common Tank-2 to the common header, then a ring header around each stockpile. Pump ratings and head values live in B01/B03 qualifications, not re-asserted here.', p2, [0.06, 0.10, 0.94, 0.20])
        sector = new('sectors', 'Coal Yard 2 SPDS sector control group', 'functional_assembly', spds, p3, [0.06, 0.45, 0.94, 0.95])
        fact(sector, 'equipment_role', 'SC-02 automatic-sequential / local-manual control grouping for Yard 2 opposite-side sprinkler pairs; not a separate physical machine.', p3, [0.06, 0.30, 0.94, 0.45])
        fact(sector, 'assembly_arrangement', SECTOR_MAP, p3, [0.06, 0.45, 0.94, 0.95])
        fact(sector, 'source_discrepancy', 'Sector-6 row prints SV-34 KKS as 00EAE0701EAE01SV211, breaking the 00EAE02SV2xx pattern of every other Yard 2 valve; retained as printed, read as SV211 pending vendor-tag check.', p3, [0.06, 0.60, 0.94, 0.70])
        fact(sector, 'source_discrepancy', 'Page 4 heads the SC-04 application list as Stockpile-2 although its KKS tags read 00EAE04 (stockpile 4); retained as printed. Yard 2 claims use only the SC-02/00EAE02 rows.', p4, [0.04, 0.04, 0.94, 0.14])
        fact(sc02, 'control_signal_to', sector, p3, [0.06, 0.30, 0.94, 0.45], obj=True, net='control', condition='Auto sequential programme or local manual selection per philosophy.')
        risers = new('risers', 'Coal Yard 2 SPDS Sprinkler risers AP-29 to AP-56', 'functional_assembly', spds, p3, [0.06, 0.40, 0.94, 0.50])
        fact(risers, 'equipment_role', 'Local physical spray points; distinct from functional sector grouping.', p3, [0.06, 0.40, 0.94, 0.50])
        fact(risers, 'assembly_arrangement', 'AP-29 to AP-56 (KKS 00EAE02QN201) on the two EAE-2 side headers; each riser carries a solenoid valve on the sequential controller plus a manual flow globe valve and an isolation gate valve.', p2, [0.06, 0.10, 0.94, 0.20])
        fact(risers, 'source_gap', 'AP and SV ranges and sector pairs are documented, but a unique AP-to-SV cross-reference and surveyed riser coordinates are not established.', p3, [0.06, 0.40, 0.94, 0.50])
        gaps = ['Philosophy pp1-18 fully read; pp2-4 carry Yard 2 scope. Valve/nozzle internals, commissioned timings, DDCMIS loop wiring and field coordinates deferred to depth queue. Pump ratings/heads remain B01/B03 qualifications. No Yard 1 sector/AP/SV values copied; every Yard 2 tag comes from the SC-02 rows.']
        summary = 'B19 Yard2 SPDS system, sector control and riser groups'
        purpose = 'Yard2 local SPDS identity, SC-02 sector/SV map and AP riser groups at Tier1 from the stockpile philosophy'
        questions = ['Which SC-02 sectors, SVs and APs serve EAE-2?', 'How is Yard2 sequential control grouped and timed?']
    elif args.scope == 'qrc':
        p1 = ev[1]
        spds = labels['Coal Yard 2 SPDS']
        ead2 = labels['EAD-2']
        eaf2 = labels['EAF-2']
        qrcm = new('qrc', 'Coal Yard 2 SPDS Machine makeup QRC connections', 'utility_header', spds, p1, [0.10, 0.60, 0.26, 0.74])
        fact(qrcm, 'equipment_role', 'Provide makeup water connections for machine onboard tanks.', p1, [0.44, 0.60, 0.74, 0.90])
        fact(qrcm, 'nominal_diameter', 32, p1, [0.66, 0.22, 0.98, 0.56], unit='mm')
        fact(qrcm, 'device_spacing', 30, p1, [0.44, 0.60, 0.74, 0.90], unit='m')
        fact(qrcm, 'assembly_arrangement', 'Quick-release couplings with isolation valves at 30 m intervals for makeup water for the stacker and reclaimer machines; 92 project QRC positions in the major BOM, per-yard share not stated.', p1, [0.44, 0.60, 0.74, 0.90])
        fact(qrcm, 'serves', ead2, p1, [0.44, 0.60, 0.74, 0.90], obj=True, net='utility', condition='Makeup-water tapping for the stacker onboard tank; hose connection method and routing detail deferred.')
        fact(qrcm, 'serves', eaf2, p1, [0.44, 0.60, 0.74, 0.90], obj=True, net='utility', condition='Makeup-water tapping for the reclaimer onboard tank; hose connection method and routing detail deferred.')
        gaps = ['SPDS P&ID p1 fully reviewed (strips, pump house, BOM, typicals, notes). Per-yard QRC count share, valve/nozzle internals and installed routing deferred to depth queue. No Yard1 QRC values copied; diameter/spacing come from this P&ID BOM/note.']
        summary = 'B19 Yard2 machine makeup QRC group and machine links'
        purpose = 'Yard2 onboard-tank refill boundary at Tier1 from the SPDS P&ID makeup note'
        questions = ['Where do EAD-2/EAF-2 onboard tanks get makeup water?']
    elif args.scope == 'stacker-dss':
        p21 = ev[21]
        ead2 = labels['EAD-2']
        dss = new('dss', 'EAD-2 Onboard plain-water DSS', 'dust_suppression_system', ead2, p21, [0.18, 0.16, 0.94, 0.91])
        fact(dss, 'equipment_role', 'Suppress dust at tripper discharge, boom receipt and boom discharge.', p21, [0.18, 0.30, 0.94, 0.55])
        fact(dss, 'location_description', 'Pump skid, tank and accessories on the stacker machine; dedicated headers near the three spray points.', p21, [0.18, 0.16, 0.94, 0.30])
        fact(dss, 'assembly_arrangement', 'Motor-driven pumps 1 working + 1 standby with suction duplex filter and differential-pressure switch, isolation/throttle valves, pressure switch/relief/gauge, globe valves, tangential circle-jet nozzles and water tank with level accessories; manual/remote via CZMC DCS/PLC with auto start from conveyor-drive contacts. Coal plain-water section only.', p21, [0.18, 0.55, 0.94, 0.91])
        fact(dss, 'source_gap', 'Duplex/simplex filter wording reconciliation, commissioned set points and installed skid serials need vendor/nameplate verification; deferred to depth.', p21, [0.18, 0.55, 0.94, 0.91])
        gaps = ['Stacker DS DBR coal plain-water control sections (pp20-23) reviewed; limestone dry-fog sections explicitly excluded from all claims. Pump/nozzle ratings, set points and installation detail deferred to depth queue. No Yard1 DSS values copied.']
        summary = 'B19 EAD-2 onboard plain-water DSS group'
        purpose = 'EAD-2 onboard dust suppression assembly at Tier1 from the coal-stacker DSS control philosophy'
        questions = ['What onboard dust suppression does EAD-2 carry and where does it spray?']
    else:
        p4 = ev[4]
        eaf2 = labels['EAF-2']
        qrcm = labels['Coal Yard 2 SPDS Machine makeup QRC connections']
        dss = new('dss', 'EAF-2 Onboard plain-water DSS', 'dust_suppression_system', eaf2, p4, [0.035, 0.22, 0.94, 0.855])
        fact(dss, 'equipment_role', 'Suppress fugitive coal dust during reclaim handling at the reclaimer application points.', p4, [0.035, 0.22, 0.94, 0.40])
        fact(dss, 'assembly_arrangement', '2000 L SS tank (2-hour storage) with level-switch PLC interlock, pumps 1 working + 0 standby on the mobile platform, DSS control panel, solenoid boxes with mist nozzles, 32NB x 50 m manual hose reel drum with QRC tank filling from header tap points, suction/discharge gauges with pressure switch and recirculation. Four-machine family design applied to EAF-2.', p4, [0.035, 0.22, 0.94, 0.70])
        fact(dss, 'source_discrepancy', 'Reclaimer GA prints approximate 2.2 kW DSS power (accepted B18 visual review, not re-cited here); this BOD builds its pump schedule around the PRP-1A tentative motor selection (accepted PRP-1A record). Final vendor/nameplate check required before assigning installed motor power.', p4, [0.035, 0.55, 0.94, 0.855])
        fact(qrcm, 'serves', dss, p4, [0.035, 0.40, 0.94, 0.60], obj=True, net='utility', condition='SS tank filling via hose reel from header tap points with QRC; detailed routing deferred.')
        gaps = ['Reclaimer DS DBR design-basis section (pp2-8) reviewed; calculation/BOM internals, commissioned set points and installation detail deferred to depth queue. No Yard1 DSS values copied.']
        summary = 'B19 EAF-2 onboard plain-water DSS group and QRC refill link'
        purpose = 'EAF-2 onboard dust suppression assembly and its header refill boundary at Tier1 from the reclaimer DSS design basis'
        questions = ['What onboard dust suppression does EAF-2 carry and how is its tank refilled?']
    out = ROOT / 'output/plant-enrichment/B19' / args.scope
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
    (out / 'package.json').write_text(json.dumps(pkg, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(scope=args.scope, components=len(nodes), operations=len(ops), baseline=model['version'])))

if __name__ == '__main__':
    main()
