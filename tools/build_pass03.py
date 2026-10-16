"""Pass-3 packages (DQ-B12-001, DQ-B12-002, DQ-B13-001, DQ-B13-002, DQ-B14-001, DQ-B14-002, DQ-B14-003).

Locally extracted by four parallel readers (OCR text + full-page vision + zoom
crops) with per-source conflict lists, before any top-model trip, per
PASS_B_TWO_TIER_WORKFLOW.md complete-pass rule. Prior accepted work already
covers Tier-1 basics plus several depth legs (hoist capacities, protection
counts, tank conflicts, TCS resolutions); these 15 one-source proposals add
only the missing depth legs. Chained v739 -> v754. Default: isolated rehearsal
in pass-03/rehearsal-copy; --apply performs guarded live acceptance after the
top-model return is folded in (proofread + 5 conflict questions).
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-03'
COPY = BASE / 'rehearsal-copy'
DOC_C4 = 'doc_a02d56b879734b5db189'
DOC_T4 = 'doc_9bd6e66e9fbb43468184'
DOC_U4 = 'doc_492c079544304e2da177'
DOC_C5 = 'doc_b74a01e57a2b4792883c'
DOC_T5 = 'doc_6d28742056e94651be04'
DOC_U5 = 'doc_e91d806d942243248e18'
DOC_C6 = 'doc_c91eac5d4c104264801f'
DOC_T6 = 'doc_eadc432afcad400192d0'
DOC_U6 = 'doc_f9f96af6a25e47179881'
DOC_T7 = 'doc_f6e89f3b3d3b40eb8d80'
DOC_U7 = 'doc_d157f03e84e84c068b06'
DOC_CTL = 'doc_4f2cd96c3b1e413ea4b5'
DOC_CVA = 'doc_740734a151bd4c00b655'
DOC_CVC = 'doc_b5c8e30f4e3d475b8cf2'
DOC_CVQ = 'doc_c29985298e9c4a338bbb'

BASIS_C4 = ('GA and load data belt conveyor-4A/B, dwg IS-1-GA-702-101-M014 Rev 4 (customer '
            'dwg Maitree-00-KF-LH-175025-ISG-4); status block FOR APPROVAL, sheet stamped APPROVED '
            '16-Oct-2019; TCS Rev A AOC 24-May-19. Design only.')
BASIS_T4 = ('GA and mech load UEF-4 (filed as TP-4), dwg IS-1-GA-702-104-M036 Rev 3 (customer dwg '
            'Maitree-00-UEF-LH-175036-ISG-3); status block FOR APPROVAL, sheet stamped APPROVED '
            '18-Dec-2018; TCS Rev 2 with BHEL replies. Design only.')
BASIS_U4 = ('Piping layout DFDS/SW/PW UEF-4, dwg IS-1-PI-702-110-M289 Rev 2 (customer dwg '
            'Maitree-00-GAC-BR-175289-ISG-2); status block FOR INFORMATION (sic), sheet stamped FIO '
            '13-Sep-2019; TCS FIO-R 08-Jul-19. FIO non-approved layout data only.')
BASIS_C5 = ('GA and load data belt conveyor-5A/B, dwg IS-1-GA-702-101-M015 Rev 2 (customer dwg '
            'Maitree-00-KF-LH-175015-ISG-2); status block FOR APPROVAL, sheet stamped APPROVED '
            '14-Dec-2018; TCS comments 23-Oct-18 with BHEL replies. Design only.')
BASIS_T5 = ('GA and mech load UEF-5 (filed as TP-5), dwg IS-1-GA-702-104-M037 Rev 3 (customer dwg '
            'Maitree-00-UEF-LH-175037-ISG-3); status block FOR APPROVAL, sheets stamped APPROVED, '
            'TCS AOC 18-Oct-2019. Design only.')
BASIS_U5 = ('Piping layout DFDS/SW/PW UEF-5, dwg IS-1-PI-702-110-M290 Rev 2 (customer dwg '
            'Maitree-00-GAC-BR-175290-ISG-2); status block FOR INFORMATION, sheet stamped FIO '
            '13-Sep-2019; TCS FIO-R. FIO non-approved layout data only.')
BASIS_C6 = ('GA and load data belt conveyor-6A/B, dwg IS-1-GA-702-101-M016 Rev 1 (customer dwg '
            'Maitree-00-KF-LH-175016-ISG-1); status block FOR APPROVAL, sheet stamped APPROVED '
            '23-Nov-2018; TCS 09-Oct-18 with BHEL replies. Design only.')
BASIS_T6 = ('GA and mech load UEF-6 (filed as TP-6), dwg IS-1-GA-702-104-M038 Rev 3 (customer dwg '
            'Maitree-00-UEF-LH-175038-ISG-3); status block FOR APPROVAL, sheet stamped APPROVED '
            '18-Dec-2018; TCS with BHEL replies. Design only.')
BASIS_U6 = ('Piping layout DFDS/SW/PW UEF-6, dwg IS-1-PI-702-110-M291 Rev 2 (customer dwg '
            'Maitree-00-GAC-BR-175291-ISG-2); status block FOR INFORMATION, sheet stamped FIO '
            '16-Sep-2019; TCS FIO-R. FIO non-approved layout data only.')
BASIS_T7 = ('GA and mech load data UEF-7 (filed as TP-7), dwg IS-1-GA-702-104-M039 Rev 6 (customer '
            'dwg MAITREE-00-UEF-LH-175039-ISG-6); status block FOR APPROVAL, sheet stamped APPROVED '
            '18-Oct-2019; TCS A AOC 30-Nov-18 with BHEL replies. Design only.')
BASIS_U7 = ('Piping layout DFDS/SW/PW UEF-7, dwg IS-1-PI-702-110-M292 Rev 2 (customer dwg '
            'Maitree-00-GAC-BR-175292-ISG-2); status block FOR INFORMATION, sheet stamped FIO '
            '16-Sep-2019; TCS FIO-R. FIO non-approved layout data only.')
BASIS_CTL = ('Control write-up IS-4-CW-702-101-E914 Rev04 26.03.2020 (BIFPCL doc MAITREE-00-EBY-DB-179162-ISG), '
             'AOC 06-Apr-2020 subject to necessary corrections; AOC conditions sheet not in corpus. Design only.')
BASIS_CVA = ('Coal analyser belt and stringer assembly, dwg IS-3-GA-702-111-M330 REV 0 (customer dwg '
             'Maitree-00-QP-DA-175330-ISG); status block FOR APPROVAL, sheets stamped FIO 18-Oct-2019. '
             'Design only; holder wording only, no isotope/activity/status inferred.')
BASIS_CVC = ('Coal analyser data sheet and technical catalogue, BHEL doc IS-3-GA-702-111-M331 REV 1 '
             '(customer doc MAITREE-00-QP-DA-175331-ISG, second submission 30/10/2019); FIO 26-Nov-2019. '
             'Vendor catalogue data only; explicit source quotes kept verbatim, nothing inferred about CV-1/CV-2 loading.')
BASIS_CVQ = ('QAP of coal analyser (CAT-I item), BHEL doc IS-3-QP-702-111-M334 REV 2 cover (Maitree QAP body '
             'REV 1, 27/09/2019, doc MAITREE-00-QP-QA-175334-ISG); FIO 13-Dec-2019. Enclosed NTPC MQP Rev 02 '
             'recorded as prior-approval reference only, not Maitree acceptance.')


def ev(eid, region):
    return dict(evidence_id=eid, quote='', region=region)


FULL = [0.03, 0.05, 0.97, 0.97]

_ENT_CACHE = {}


def ent(label):
    if label not in _ENT_CACHE:
        import sqlite3 as _sq
        with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
            row = _db.execute('SELECT id FROM entities WHERE label=?', (label,)).fetchone()
        assert row, label
        _ENT_CACHE[label] = row[0]
    return _ENT_CACHE[label]


def pkg_c4d():
    drive = ('Conveyor-4 drive-train make/model detail (approved 16-Oct-2019, both lanes EAC-4A/4B): motor '
             'SQ. CAGE, BHEL, 500kW, 1488rpm synchronous, 415V +/-10%, 50Hz +/-5%, MODEL/FRAME SIZE - (dash); '
             'gearbox BEVEL HELICAL, PREMIUM, MODEL B3 450, RATIO 17.1:1; H.S. coupling SCOOP COUPLING/PREMIUM '
             'PST-570; L.S. coupling GEARED/GBM RG-12; brake THRUSTER, ELECKTROMAG (verbatim spelling) MODEL '
             'EBTF-600/G. Drive arrangement V3-V3 left-to-right: GEAR BOX - CL GEAR BOX OUT PUT SHAFT - BRAKE - '
             'SCOOP COUPLING - CL MOTOR - MOTOR (brake sits between gearbox output shaft and scoop coupling).')
    sup_drive = [ev('ev_9904aaf9a4b64f8c8e40', FULL)]
    tripper = ('Fixed-tripper discharge arrangement (both lanes): FIXED TRIPPER PULLEY 800 dia x 2200 face x 2700 '
               'bearing CRS, 12mm diamond-groove rubber lagging, 1 no per conveyor; FTR-1/2 heads with KB-FD-3/4 '
               'chutes discharging below to EAC-11 (elevation UEF-4 head region); horizontal C/C tail pulley to '
               'tripper discharge pulley 86650 for EAC-4A/4B; tripper bend pulley to head pulley 84000 for EAC-4A '
               'and 87000 for EAC-4B.')
    key = ('Protection key diagram (both lanes): LEGENDS PCS = PULL CORD SWITCH, BSS = BELT SWY SWITCH (verbatim); '
           'plotted tags PCS-1..PCS-6, BSS-1..BSS-4, ZERO SPEED SWITCH at tail pulley, TRIPPER DISCHARGE PULLEY '
           'EAC 4A/4B. Counts: belt sway both sides at 40m intervals 4 pairs per conveyor; pull cord both sides '
           'at 30m spacing 6 pairs per conveyor; zero speed on tail pulley 1 no per conveyor (recorded on '
           'protection groups; numeric trip settings in control proposal).')
    sup_key = [ev('ev_c4f5db366e974e8ab215', FULL)]
    idlers_a = ('Idler schedule EAC-4A: carrying 3 equal-roll 35deg trough dia-159mm tube at 1000/1000mm pitch '
                'with 2deg forward tilt, QTY 169 nos; return sets QTY 49 nos. C/C horizontal 170.650m; profile '
                '189.785m; endless 382.350m.')
    idlers_b = ('Idler schedule EAC-4B: carrying same spec, QTY 172 nos; return sets QTY 49 nos. C/C horizontal '
                '173.650m; profile 192.785m; endless 388.300m.')
    context = ('Conveyor-4 duty context (both lanes): material UN-CRUSHED COAL, lump (-)100mm, density 800 kg/cu.m '
               'volumetric / 1100 kg/cu.m weight, moisture 7-24%, location BETWEEN COAL UEF-3 TO UEF-5, belt 2000mm '
               'N/N HD 1250/4 covers 5/2 FR, lift1 11.300m lift2 12.268m, design 3740 / rated 3400 TPH, 3 feed '
               'points per conveyor, wrap 210deg, speed 3.50 m/s, tensions T1 176.9 / T2 66.1 / T3 66.9 / '
               'Tup 62.4 / T1s 218.6 kN.')
    ops = []
    for subj, tag, idlers in [('EAC-4A', '4A', idlers_a), ('EAC-4B', '4B', idlers_b)]:
        ops.append(dict(op='assert', subject=ent(subj), predicate='assembly_arrangement', value=drive,
                        context=dict(kind='specification', basis=BASIS_C4 + ' EAC-%s drive makes.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_drive))
        ops.append(dict(op='assert', subject=ent(subj), predicate='assembly_arrangement', value=tripper,
                        context=dict(kind='specification', basis=BASIS_C4 + ' EAC-%s tripper.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_drive + sup_key))
        ops.append(dict(op='assert', subject=ent(subj), predicate='operating_requirement', value=key,
                        context=dict(kind='specification', basis=BASIS_C4 + ' EAC-%s switch layout.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_key))
        ops.append(dict(op='assert', subject=ent(subj + ' idler and belt-support assembly'), predicate='assembly_arrangement',
                        value=idlers, context=dict(kind='specification', basis=BASIS_C4 + ' EAC-%s idler counts.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_drive))
        ops.append(dict(op='assert', subject=ent(subj), predicate='document_note', value=context,
                        context=dict(kind='specification', basis=BASIS_C4 + ' EAC-%s duty.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_drive))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_drive,
                    text=('Brake model split preserved: GA nameplate row reads EBTF-600/G (installed thruster brake) '
                          'while the accepted Rev-03 power/belt-tension calculation entity records selected brake '
                          'model EBTM-600/G; different roles, both retained. The string EBTM appears nowhere in this '
                          'GA or in the control write-up.')))
    return dict(summary='EAC-4A/4B drive makes, tripper/divider arrangement, switch layout, per-lane idlers, duty context (conv-4 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record conveyor-4 drive/tripper/protection depth legs',
                    questions=['What drive makes, tripper arrangement and per-lane idler counts apply to EAC-4A/4B?'],
                    reviewed_evidence_ids=[], gaps=['Numeric protection trip settings (control proposal).']))


def pkg_t4d():
    sup_sched = [ev('ev_67caa6afe1c04fd2a1e2', [0.10, 0.64, 0.62, 1.0])]
    hoist = ('Hoist schedule UEF-4: EH-1 3.5T lift 20.5m B.O.M.R. EL+21.700M for EAC-4A/B fixed-tripper discharge '
             'pulleys; EH-2 3.5T/9.5m/EL+10.300M for 4A/4B fixed-tripper bend pulleys (schedule; plan view draws '
             'EH-2 2.5T, retained discrepancy); EH-3 4T/3.5m/EL+4.600M for EAC-11 tail pulley; MH-1 1T/2.0m/EL+14.100M '
             'for flow divider. Hooks: 1.5T cap, 4 nos, below EL+11.100M in hoisting area. Monorails EH-1 3.5T @ '
             '+21.700M, EH-2 3.5T @ +10.300M, EH-3 4T @ +4.600M, MH-1 1T @ divider.')
    drain = ('Drainage and water provisions UEF-4 (GA, no piped drainage routed): note 10 GARLAND DRAIN TO BE '
             'PROVIDED AROUND THE BUILDING; 400 SQ openings for downcomer with TYP mounting arrangement (curb '
             'angle 50x50x6); 300x1000 opening for water system pipes; service tag 4A/B WS1 on foundation plan. '
             'TCS: drain layout will be shown in separate drawing. Downcomer note on conveyor sheet (runoff to '
             'floor-washing drain) is cut off at sheet edge, endpoint not confirmed.')
    tcs = ('TP-4 TCS close-out (approved 18-Dec-2018): flow divider revised as discussed in DRM Nov-18 against '
           'comment that divide between conv 4AB and stacker conveyor was unclear; MH-1 monorail routed so only '
           'the diverter gear motor needs ground handling (only gear motor of diverter gate requires maintenance); '
           'BHEL to provide potable water tank inside TP drive floor with tapping at all operating floors, noted '
           'and incorporated (origin of the 250L GA tank).')
    notes = ('UEF-4 civil notes (all tentative, refer separate drawing): dimensions in mm, levels in meters; FFL '
             'RL+5.60M = plant EL 0.0M, ground RL+5.0M; cable openings tentative; safety handrail at openings; toe '
             'guard on grating; chequered step at 10deg+ slopes; 100mm kerb at floor openings; hood 6mm MS; impact '
             'chute 20mm Hardox 400, non-impact 10mm Hardox 400. Foundation load-per-base-plate table read; footnote: '
             '(-) vertical = uplift, live load at 1.1 T/cu.m material density.')
    ops = [dict(op='assert', subject=ent('UEF-4'), predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_T4 + ' Handling schedule.'),
                origin='explicit', confidence=0.95, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-4'), predicate='assembly_arrangement', value=drain,
                context=dict(kind='specification', basis=BASIS_T4 + ' Drainage provisions.'),
                origin='explicit', confidence=0.9, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-4'), predicate='document_note', value=tcs,
                context=dict(kind='specification', basis=BASIS_T4 + ' TCS close-out.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_38e01cb2ab574a128ddc', FULL), ev('ev_bf2f39fccbea4d79965f', FULL)]),
           dict(op='assert', subject=ent('UEF-4'), predicate='document_note', value=notes,
                context=dict(kind='specification', basis=BASIS_T4 + ' Civil notes and loads.'),
                origin='explicit', confidence=0.9, evidence=sup_sched),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_sched,
                text=('TP-4 filename versus UEF-4 drawing: file filed as GA & MECH LOAD OF TP-4, title block reads '
                      'GA & MECHANICAL LOAD OF UEF-4, dwg M036; legs attach to UEF-4. EH-2 plan/schedule 2.5T vs '
                      '3.5T retained. 250L GA tank versus 300L piping PW tank is the top-model tank question.'))]
    return dict(summary='UEF-4 hoist schedule, drainage provisions, TCS close-out, civil notes (TP-4 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record TP-4 handling/structural/access detail',
                    questions=['What hoist, drainage and TCS outcomes apply at UEF-4?'],
                    reviewed_evidence_ids=[], gaps=['Tank deciding record (top-model Q1); piped drain drawing.']))


def pkg_u4p():
    sup_p1 = [ev('ev_02591356954f49e0b549', FULL)]
    sup_p2 = [ev('ev_087be85148584a33b66d', FULL)]
    headers = ('UEF-4 header routing and continuation (FIO layout Rev 2): air/water 65NB(A)/32NB(W), potable 40NB(PW), '
               'service 100NB(SW) entering with EAC-4A/B gallery; left trunk DFDS,SW FROM UEF-3 and PW TO UEF-3; '
               'right trunk DFDS,SW TO UEF-5 and PW FROM UEF-5; 50NB(SW) take-off TO UAX-7 with EAC-11 spray header. '
               'Application branches: FAS-24/PRU-24 to EAC-4B and FAS-21/PRU-21 to EAC-4A (view 1-1); FAS-25/PRU-25 to '
               'EAC-4B and FAS-22/PRU-22 to EAC-4A (view 2-2); FAS-26/PRU-26 to EAC-11 (view 3-3); FAS-23/PRU-23 to '
               'EAC-11 (view 4-4). Drops 15NB(W)/20NB(A); FFL drain drops to EAC-4B/EAC-4A.')
    bom = ('UEF-4 piping BOM service groups (Rev 2): DFDS air 65/32/20NB pipe, elbows, tees, reducers, sockets, '
           'unions and U-clamps; DFDS water 32/20/15NB pipe, elbows, reducers, tees, unions and clamps; service '
           'water 100/50/32NB pipe and elbows, 2 hose boxes, 4 QRC with accessories; potable galvanized 40/25/20NB '
           'pipe, elbows and tees with U-clamps; 44 nos nozzle B 1/4, 4 nos 4-spray headers, 8 nos 9-spray headers, '
           '220m PU tube 8 OD, 4 nos BIB tap 25NB; MS angles L75/65/50 and plates. Pipe supports PS-1 7 nos, PS-3 '
           '4 nos, PS-5 7 nos, PS-7 3 nos (50NB SW, 65NB air, 32NB water).')
    tank = ('UEF-4 300L PW tank detail (piping sheet): PVC TANK ARRANGEMENT, CAPACITY 300 LTR FOR PW SYSTEM, on '
            'ISA 65x65x6 / 50x50x6 stand; FLOAT VALVE, VENT, 20NB OVER FLOW LINE, 25NB GLOBE VALVE, 25NB GATE VALVE '
            'NORMALLY OPEN, 20NB GATE VALVE NORMALLY CLOSE. Plan shows 100 SQ opening PW discharge and 100 DIA PVC '
            'pipe sleeve on floor. All SW and PW tap points 1200mm from finish floor. Versus GA 250L tank: top-model '
            'tank question decides one tank or two.')
    notes = ('UEF-4 piping notes: dimensions mm, levels meters; support spacing may change at erection; pipes '
             'supported every 3m max from existing structure; minor routing changes to suit site; pipes/fittings/valves '
             'per technical specification. Status FIO 13-Sep-2019. TCS FIO-R: FFL piping hinders man movement, pipe '
             'routed taking roof support, drawing revised accordingly; align with UEF-1 comments.')
    ops = [dict(op='assert', subject=ent('UEF-4'), predicate='utility_header_routing', value=headers,
                context=dict(kind='specification', basis=BASIS_U4 + ' Headers and branches.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-4'), predicate='utility_bom_summary', value=bom,
                context=dict(kind='specification', basis=BASIS_U4 + ' Piping and nozzle BOM.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='assert', subject=ent('UEF-4 potable-water tank and tap assembly'), predicate='assembly_arrangement',
                value=tank, context=dict(kind='specification', basis=BASIS_U4 + ' PW tank detail.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-4'), predicate='utility_tap_height_above_ffl', value=1200,
                context=dict(kind='specification', basis=BASIS_U4 + ' Tap height.'),
                origin='explicit', confidence=0.95, evidence=sup_p2, unit='mm'),
           dict(op='assert', subject=ent('UEF-4'), predicate='utility_support_schedule',
                value='PS-1: quantity 7; PS-3: quantity 4; PS-5: quantity 7; PS-7: quantity 3 (50NB SW, 65NB air, 32NB water).',
                context=dict(kind='specification', basis=BASIS_U4 + ' Pipe supports.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_p1 + sup_p2, text=notes)]
    return dict(summary='UEF-4 piping headers, BOM, PW tank valves, supports, tap height (UEF-4 piping)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record UEF-4 DFDS/SW/PW installation scope',
                    questions=['How is DFDS/SW/PW laid out and supported at UEF-4?'],
                    reviewed_evidence_ids=[], gaps=['Tank deciding record (top-model Q1).']))


def pkg_c5d():
    drive = ('Conveyor-5 drive-train make/model detail (approved 14-Dec-2018, both lanes EAC-5A/5B): motor SQ. CAGE, '
             'BHEL, RATING 380 KW HT, SPEED 1488rpm synchronous, SUPPLY 415V +/-10% 50Hz +/-5% (HT rating row versus '
             '415V LT supply row preserved as internal conflict, top-model Q3), MODEL/FRAME SIZE - (dash); gearbox '
             'BEVEL HELICAL, PREMIUM, MODEL B3 450, RATIO 17:1; H.S. coupling SCOOP COUPLING/PREMIUM PST-530; L.S. '
             'coupling GEARED/GBM RG-10; brake THRUSTER, ELECKTROMAG (verbatim) MODEL EBTM-500/DS/DG. Drive arrangement '
             'V1-V1/V2-V3 line: CL MOTOR - CL GEAR BOX OUT PUT SHAFT with scoop coupling and brake in line. Base-plate '
             'MKD EAC-5A/B SS-6 to SS-32 and SS-41 to SS-71. Chute plates 10mm Hardox 400 non-impact, 20mm impact, '
             'both lanes. Head-frame hooks HOOK-H1/H2 CAP-3.5T at UEF-6 end.')
    sup_drive = [ev('ev_ea9eece376a7425a9c8c', FULL)]
    tcs = ('Conveyor-5 TCS close-out threads (replies incorporated, approved 14-Dec-2018): flow divider in UEF-4 and '
           'UEF-5 revised per DRM; tension values revised per approved power and tension calculation; counterweight '
           'total plus cast-iron excluding frame indicated (629 blocks x 17.5kg); rope revised to dia-24 6x37 FMC '
           'grade 1570 minimum breaking 267kN against TCS-required 221kN per BS2573; access ladder added; take-up '
           'pulley-to-belt distance and take-up arrangement revised (BHEL asked for HGTU, final stays VERTICAL GRAVITY '
           'TAKE UP WITH MARK-UP SCALE, retained disagreement); coal-water downcomer at Tr-5a rerouted to independent '
           'coal run-off pond drain, not road drain; tripper bend pulley elevated for 35deg CI kink in UEF-6 tower; '
           'roller path at TP-7 discharge follows belt profile; external scraper count still reads QTY 1 NO EACH '
           '(primary + secondary) against TCS 2nos, retained disagreement (top-model Q4).')
    ops = [dict(op='assert', subject=ent('EAC-5A'), predicate='assembly_arrangement', value=drive,
                context=dict(kind='specification', basis=BASIS_C5 + ' EAC-5A drive makes.'),
                origin='explicit', confidence=0.95, evidence=sup_drive),
           dict(op='assert', subject=ent('EAC-5B'), predicate='assembly_arrangement', value=drive,
                context=dict(kind='specification', basis=BASIS_C5 + ' EAC-5B drive makes.'),
                origin='explicit', confidence=0.95, evidence=sup_drive),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=sup_drive + [ev('ev_27948e80b7e146f6810c', FULL)], text=tcs),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_drive,
                text=('HT versus 415V motor wording, EAC-5A/5B: RATING row 380 KW HT against SUPPLY row 415V; control '
                      'write-up HT-motor interlock supports HT classification. Top-model Q3 decides presentation; both '
                      'rows recorded verbatim, neither normalised.'))]
    return dict(summary='EAC-5A/5B drive makes, chute MOC, head hooks, TCS close-out, HT conflict (conv-5 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record conveyor-5 drive/TCS depth legs',
                    questions=['What drive makes, chute detail and TCS outcomes apply to EAC-5A/5B?'],
                    reviewed_evidence_ids=[], gaps=['HT deciding record (top-model Q3); cleaner count (top-model Q4).']))


def pkg_t5d():
    sup_sched = [ev('ev_6a88c5904c5d4b2b8b65', [0.10, 0.64, 0.62, 1.0])]
    hoist = ('Hoist schedule UEF-5: EH-1 10T lift 23m B.O.M.R. EL+24.500M for EAC-4A/4B head and snub pulleys + drive '
             'units 6 + belt drum; EH-2 5.5T/6m/EL+24.500M for 4A/4B head and snub pulleys; EH-3 4T/9m/EL+9.200M for '
             'EAC-5A/5B and EAC-9 tail pulleys (only hoist naming EAC-5A/5B); MH-1 3T/16m/EL+17.400M for 4A/4B take-up '
             'pulley frames; MH-2 1T/3m/EL+17.100M for flow divider; MH-3 1T/3m/EL+13.300M for flap-gate KB-FG-3/4 '
             'actuators; MH-4 16T/8m/EL+9.200M for 4A/4B counterweight frames. Hook schedule H-1&2 3T for EAC-4A/B '
             'bend pulleys. Monorails EH-1 10T @ +24.500M, MH-4 16T @ +9.200M; movable stool and 6000 maintenance '
             'platform at hoists.')
    drain = ('Drainage and civil UEF-5: note 10 GARLAND DRAIN TO BE PROVIDED AROUND THE BUILDING; note 9 150mm KERB '
             'WALL ALL AROUND FLOOR OPENING; DOWNCOMER with TYP mounting arrangement; DEBRIS CHUTE min 6mm thk; ramp, '
             'sandpit, wall, VGTU 1750 plinths at EL-0.600M FCL. TCS: coal water led to coal run-off pond via '
             'independent drain, not road drain (cross-ref conv-5 TCS). Equipment labels KB-FG-3, KB-FG-4, KB-FD-6, '
             'EAC-9, EAC-5B in views; section L-L 1350 skirt I/S, 4000 CRS, walkways 800/1100.')
    notes = ('UEF-5 drawing notes 1-8 + refs + legends: FFL RL+5.60M = plant EL 0.0M, ground RL+5.0M; cable openings '
             'tentative; civil/structural tentative, refer separate drawing; openings are clear; handrail at openings; '
             'toe guard on grating; chequered step at 10deg+ slopes. Ref drgs: plot plan, CHP layout 175002, coal flow '
             '175001, gallery cross-section 175003, conv profile 175004, flap-gate GA 175065, flow-divider GA 175066. '
             'Legends TOC/TOS/EL/RL/FFL/FGL/BOMR/BOSP/opng/TP/HP/SP/WP/EH/MH/CJB/SCP/LCS/LCP as printed.')
    ops = [dict(op='assert', subject=ent('UEF-5'), predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_T5 + ' Handling schedule.'),
                origin='explicit', confidence=0.95, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-5'), predicate='assembly_arrangement', value=drain,
                context=dict(kind='specification', basis=BASIS_T5 + ' Drainage and civil.'),
                origin='explicit', confidence=0.9, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-5'), predicate='document_note', value=notes,
                context=dict(kind='specification', basis=BASIS_T5 + ' Notes, refs, legends.'),
                origin='explicit', confidence=0.9, evidence=sup_sched),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_sched,
                text=('TP-5 filename versus UEF-5 drawing: file filed as GA & MECH LOAD OF TP-5, title block reads GA '
                      '& MECHANICAL LOAD OF UEF-5, dwg M037; TCS header also says TP-5; legs attach to UEF-5. Water '
                      'tank 300L on GA agrees with piping (no 250L string in these sheets). TCS: MH-4 capacity 16T '
                      'with monorail routing revised; scoop handwheel and brake thrustor toward radiator side; '
                      'take-up platform provided at 3.5m level in line with UEF-3.'))]
    return dict(summary='UEF-5 hoist schedule, drainage/civil, notes/refs, TCS threads (TP-5 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record TP-5 handling/structural/access detail',
                    questions=['What hoist, drainage and TCS outcomes apply at UEF-5?'],
                    reviewed_evidence_ids=[], gaps=['Foundation numeric cells (illegible at scan).']))


def pkg_u5p():
    sup_p1 = [ev('ev_04994662328d45aab6df', FULL)]
    sup_p2 = [ev('ev_39b94bf4dc3c4ede804d', FULL)]
    route = ('UEF-5 header routing and continuation (FIO layout Rev 2): left box DFDS,SW TO UEF-4 and PW TO UEF-4 '
             '(65NB air, 32NB water, 40NB PW, 100NB SW); key plan north box headers to EAC-5A/5B/4A/4B/EAC-9; TO UAX-6 '
             'at EAC-9 zone; TO CONV. EAC-9 (view 3-3). Application branches: FAS-31/PRU-31 to EAC-4B and FAS-27/PRU-27 '
             'to EAC-4A (view 1-1); FAS-34/PRU-34 + FAS-30/PRU-30 to EAC-9 (view 3-3); FAS-33/PRU-33 + FAS-29/PRU-29 to '
             'EAC-5B and FAS-32/PRU-32 + FAS-28/PRU-28 to EAC-5A (view 2-2). Tapping details: typical service-water and '
             'drinking-water tapping with FLOW CONTROL UNIT and PRESSURE REGULATING UNIT; hose-box arrangement; header '
             'fixing details at discharge and receipt ends.')
    bom = ('UEF-5 piping BOM (Rev 2): DFDS air 65NB 87m, 32NB 40m, 20NB 189m with elbows, tees, reducers, unions, '
           'sockets and U-clamps; DFDS water 32NB 73m, 20NB 40m, 15NB 189m with elbows, reducers, tees, unions and '
           'clamps; service water 100NB 73m, 50NB 28m, 32NB 10m with 2 hose boxes and 4 QRC with accessories; '
           'potable galvanized 40NB 73m, 25NB 38m, 20NB 6m; 62 nos nozzle B 1/4, 4 nos 4-spray headers, 12 nos '
           '9-spray headers, 310m PU tube 8 OD, 4 nos BIB tap 25NB; MS angles and plates. PVC tank detail CAPACITY '
           '300 LTR FOR PW SYSTEM with float valve, vent, globe/gate valves, overflow 20NB.')
    ops = [dict(op='assert', subject=ent('UEF-5'), predicate='utility_header_routing', value=route,
                context=dict(kind='specification', basis=BASIS_U5 + ' Headers, branches, tappings.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-5'), predicate='utility_bom_summary', value=bom,
                context=dict(kind='specification', basis=BASIS_U5 + ' Piping and nozzle BOM.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_p1,
                text=('UEF-5 piping TCS: refer TP-4 comments and revise accordingly; align with UEF-1 piping '
                      '175286 comments in similar lines. No monorail/hoist geometry on piping sheets; hoist legs '
                      'only from TP-5 GA. 250L string absent from these sheets.'))]
    return dict(summary='UEF-5 piping headers, branches, BOM, tank detail (UEF-5 piping)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record UEF-5 DFDS/SW/PW installation scope',
                    questions=['How is DFDS/SW/PW laid out and supplied at UEF-5?'],
                    reviewed_evidence_ids=[], gaps=['Hoist rails (GA proposal); foundation cells.']))


def pkg_c6d():
    sup_char = [ev('ev_e1911d1d4a2c4843a67e', FULL)]
    idlers_a = ('Idler schedule EBA-6A: transition 3 equal-roll 15/25deg dia-159mm, 2+2 nos per conveyor; impact 3 '
                'equal-roll 35deg dia-139.7mm 190.0 OD at 400mm pitch, 12 nos; carrying 3 equal-roll 35deg dia-159mm '
                'at 1000/1000mm pitch 2deg forward tilt, 354 nos; SA carrying at 15000mm pitch 2deg tilt, 25 nos; '
                'self-cleaning return near tail pulley 1 no; return 10deg trough dia-159mm at 3000mm pitch, 105 nos; '
                'SA return at 18000mm pitch, 21 nos; flat return roller near tail/head/take-up 3 nos.')
    idlers_b = ('Idler schedule EBA-6B: same specs; carrying 339 nos; SA carrying 24 nos; return 101 nos; SA return '
                '20 nos; transition/impact/self-cleaning/flat counts common (2+2/12/1/3). Lane differences preserved, '
                'never merged.')
    pulleys = ('Pulleys (both lanes): drive 800 dia x 1600 face x 2100 bearing CRS, 12mm diamond-groove lagging, 1 no '
               'per conveyor; bend/snub 630 dia x 1600 face x 2100 CRS lagged, 3 nos per conveyor; tail and take-up '
               '630 dia x 1600 face x 2100 CRS lagged, 2 nos per conveyor; deflector roller 219 dia x 1600 face, '
               'lagged, 2 nos per conveyor.')
    skirt = ('Skirt/deck/seal/chute (both lanes): skirt 10m length 20thk Hardox 400 with top cover plate 10thk per '
             'conveyor; deck plate 3.15mm continuous with leak-proof weld; seal plate 3.15mm throughout gallery with '
             'leak-proof weld; chute plate 10mm Hardox 400 non-impact, 20mm impact. Cleaners: polyurethane primary '
             'and TUNSTENCARBITE (verbatim) secondary, 1 each per conveyor at discharge; V-plough internal near tail '
             '1 no per conveyor (material agreement already recorded; spelling preserved).')
    vgtu = ('VGTU tower 6A/B: take-up travel 10100 (recorded); tower levels EL+34.300M TOS down to EL+0.000M FFL '
            '(RL+5.60) with monorail EL+33.100M/15.200M BOMR; 3mm metal partition plates through travel zones; shock '
            'absorbers; impact beam with IMPACT LOAD 1.5 T/BUFFER; rope CRS 1070, pipe CRS 2500; sand pit 7600; guard '
            '600 wide; 200 dia openings. Take-up counterweight cast-iron blocks design 8000kg per conveyor, 457 '
            'blocks of 17.5kg.')
    gallery = ('Gallery and civil (both lanes): bays 24600 gallery module with short-post spacing (43x3000, 7x3000, '
               '9x3000, 22x3000, 14x6000, 17501/17182 modules); stringer/post CRS 1730/1856; base plates for short '
               'post at gallery and house with M20/M24 foundation bolts; tail frame with guard, internal scraper, '
               'deflector roller; min 8m clearance at road crossing; crossover with chequered platform and ladder at '
               'max 100m; downcomer at each four-leg trestle to drain floor-washing water; 6mm fillet welds, 22 dia '
               'holes UON; starred dims tentative.')
    context = ('Conveyor-6 duty context: material UN-CRUSHED COAL lump (-)20mm, density 800/1100, moisture 7-24%, '
               'location BETWEEN COAL UEF-7 TO UEE-2, belt 1400mm N/N HD 1250/4 covers 5/2 FR, C/C 379.600m 6A / '
               '363.600m 6B, profile 382.648m 6A / 368.648m 6B, endless 772.672m 6A / 758.677m 6B, lift 34.820m tail '
               'to head, design 1375 / rated 1250 TPH, 2 feed points, wrap 210deg, speed 2.70 m/s, tensions T1 131.3 / '
               'T2 47.8 / T3 49.3 / Tup 50.7 / T1s 158.1 kN. Motor SQ. CAGE BHEL 315kW 1488rpm 3.3kV 3-phase, frame -; '
               'gearbox BEVEL HELICAL PREAMIMUM (verbatim) B3 400 ratio 23.2:1; scoop PST-530; geared GBM RG-10; '
               'brake THRUSTER ELECKTROMAG EBTM-500/F. Drive plan D1-D1/C-C with head/snub/deflector at EL+36.000M WP.')
    tcs = ('Conveyor-6 TCS threads (replies incorporated, Rev 1 approved 23-Nov-2018): take-up/counterweight guides '
           'strong pipe/box section against belt snap; momentum-arrest/shock arrangement at all take-up towers; '
           'take-up headroom revised; gallery profile at convex zone max 1400mm; coal slurry guided to downcomers '
           'each trestle into 2 cu.m RCC tank with 2 decanting taps, decanted water to nearest drain (recorded); SARI '
           'within 10m of tail/head; material trajectory checked; drive location revised; belt loading 80% basis '
           'disputed against TCS ask to revise speed (2.70 retained); shaft power and take-up tension not tabulated '
           '(recorded gap); seal plate full gallery length; belt standard IS:1891 to be shown on belt datasheet; short '
           'support max 1.5m at feed point; fire escape ladders every 100m at four-leg trestles (recorded); walkway '
           'extension so belt top max 1.2m from walkway (recorded); first ground portal at UEF-7; scraper MOC agreement '
           'polyurethane primary / tungsten secondary (recorded); transition spacing max 700mm; drive updated per '
           'approved selection; take-up travel/platforms per blending-silo observations.')
    ops = []
    for subj, tag, idlers in [('EBA-6A', '6A', idlers_a), ('EBA-6B', '6B', idlers_b)]:
        ops.append(dict(op='assert', subject=ent(subj + ' idler and belt-support assembly'), predicate='assembly_arrangement',
                        value=idlers, context=dict(kind='specification', basis=BASIS_C6 + ' EBA-%s idlers.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_char))
        ops.append(dict(op='assert', subject=ent(subj), predicate='assembly_arrangement', value=pulleys,
                        context=dict(kind='specification', basis=BASIS_C6 + ' EBA-%s pulleys.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_char))
        ops.append(dict(op='assert', subject=ent(subj), predicate='assembly_arrangement', value=skirt,
                        context=dict(kind='specification', basis=BASIS_C6 + ' EBA-%s skirt/seal/chute.' % tag),
                        origin='explicit', confidence=0.9, evidence=sup_char))
        ops.append(dict(op='assert', subject=ent(subj), predicate='document_note', value=context,
                        context=dict(kind='specification', basis=BASIS_C6 + ' EBA-%s duty and drive.' % tag),
                        origin='explicit', confidence=0.95, evidence=sup_char))
    ops.append(dict(op='assert', subject=ent('EBA-6A'), predicate='assembly_arrangement', value=vgtu,
                    context=dict(kind='specification', basis=BASIS_C6 + ' VGTU tower (shared 6A/B).'),
                    origin='explicit', confidence=0.9,
                    evidence=[ev('ev_208d9be2da864c2faa24', FULL)]))
    ops.append(dict(op='assert', subject=ent('EBA-6A'), predicate='assembly_arrangement', value=gallery,
                    context=dict(kind='specification', basis=BASIS_C6 + ' Gallery and civil (shared 6A/B).'),
                    origin='explicit', confidence=0.9, evidence=sup_char))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9,
                    evidence=sup_char + [ev('ev_3195df5cb4c04e45b496', FULL)], text=tcs))
    return dict(summary='EBA-6A/6B per-lane idlers, pulleys, skirt/seal, VGTU tower, gallery, TCS threads (conv-6 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record conveyor-6 internals and gallery detail',
                    questions=['What per-lane idler, pulley, take-up and gallery details apply to EBA-6A/6B?'],
                    reviewed_evidence_ids=[], gaps=['Shaft power; belt datasheet; belt/tension reconciliation vs Rev-03 calc.']))


def pkg_t6d():
    sup_sched = [ev('ev_063e2b5227aa4152a2cf', [0.10, 0.64, 0.62, 1.0])]
    hoist = ('Hoist schedule UEF-6: EH-1 3.5T lift 20.5m B.O.M.R. +21.700M for EAC-5A/B discharge pulley; EH-2 3.5T/9.5m/'
             '+10.300M for 5A/B fixed-tripper bend pulleys; EH-3 4T/3.5m/+4.600M for EAC-7 tail pulley; MH-1 3T/14.40m/'
             '+14.400M for 5A/B VGTU take-up pulley; MH-2 1T/2.0m/+14.100M for flow divider; MH-3 7.5x2T/10.30m/+10.300M '
             'for counterweight frames (additional monorail with hoist provided for counterweight). Hook schedule '
             'H-1&2 3.5T for EAC-5A/B bend pulleys. Monorails EH-1/EH-2 @ +21.700/+10.300M, MH-1 3T @ +14.400M and '
             'MH-1 7.5x2T @ +10.300M, MH-2 1T @ divider.')
    loads = ('UEF-6 foundation loads per base plate (footing) in kN, selected groups: 5A/B HF-1 dead 7.32 / live 0.00 / '
             'start-Hx 90.42 / normal-Hx 60.28 / start-Vy -66.16 / normal-Vy -44.11; HF-2 31.86/14.50/89.91/59.94/'
             '61.44/40.96; HF-3 18.92/0.00/-82.03/-54.68/82.03/54.68; DF-1 (21 nos) 14.60/0.00/81.26/54.18/81.26/54.18; '
             'DF-2 10.36/0.00/74.55/49.70/79.88/53.26; SS-1 20.40/0.00/77.84/51.89/-140.24/-93.49; CS-1 19.24/8.99/'
             '27.96/18.64/-126.39/-84.26; 7 TF-1 11.73/1.82/93.26/62.17/-91.93/-61.29; 7 TF-2 26.31/16.31/99.87/66.58/'
             '113.95/75.96. Footnote: (-) vertical = uplift; live load at 1.1 T/cu.m density. Full table on sheet 2.')
    civil = ('UEF-6 civil (all tentative, refer separate drawing): FFL RL+5.60M = plant EL 0.0M, ground RL+5.0M; cable '
             'openings tentative; handrail at openings; toe guard on grating; chequered step at 10deg+; 100mm kerb at '
             'floor openings; hood 6mm MS; impact chute 20mm Hardox 400, non-impact 10mm. Provisions: DOWN COMER with '
             '400 SQ openings; DEBRIS CHUTE min 6mm; 300x1000 water-pipe opening; 500x500 and 250x250 cable openings; '
             'removable chequered-plate openings; gate 900 SQ; ramp, wall, 800 wall. TCS: 10T-plus take-up/counterweight '
             'handling revised to VGTU+HGTU-compatible arrangement with platforms every 3m in travel area; MH-1 '
             'monorail/hoist arrangement revised for headroom; MH-3 counterweight-at-travel issue revised.')
    tcs = ('UEF-6 TCS threads (replies incorporated, approved 18-Dec-2018): monorail/hoist shifted clear of CW-hoist '
           'fouling; 4m take-up space inadequate, additional counterweight monorail+hoist provided; platform at final '
           'CW position; MH-1 routed for divider component ground handling (only diverter gear motor needs '
           'maintenance); load data revised per power/tension observations; chute side-plate angles and clear headroom '
           'with 1m walkway at EL 6.0M indicated; tail-pulley transition idler spacing/type/qty revised; 1m clear '
           'between the two flow dividers; inspection-door platform with movable stool above 1.5m (recorded); >80% '
           'flow to downstream 4A/B with 1m straight vertical chute above divider, conveyor inclination 12 to ~13/13.5 '
           'deg between TP-5 and TP-6, divider and chute profile changed; downcomers inside building, EL6.0 downcomer '
           'hindering tail-pulley maintenance path (2634 dim to downcomer), drain in separate drawing; hooks/chain '
           'pulley blocks as TP-4 for grid-1 bend pulleys; belt guard as TP-4; bend-pulley roof kept at gallery level; '
           'roof platform approach extended; 250L GA tank stands against DBR 300Ltr potable requirement, reply revises '
           'capacity and height as shown in piping layout (top-model tank question).')
    ops = [dict(op='assert', subject=ent('UEF-6'), predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_T6 + ' Handling schedule.'),
                origin='explicit', confidence=0.95, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-6'), predicate='assembly_arrangement', value=loads,
                context=dict(kind='specification', basis=BASIS_T6 + ' Foundation loads.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_5e7503fca28b4d809936', [0.0, 0.55, 1.0, 1.0])]),
           dict(op='assert', subject=ent('UEF-6'), predicate='assembly_arrangement', value=civil,
                context=dict(kind='specification', basis=BASIS_T6 + ' Civil and provisions.'),
                origin='explicit', confidence=0.9, evidence=sup_sched),
           dict(op='assert', subject=ent('UEF-6'), predicate='document_note', value=tcs,
                context=dict(kind='specification', basis=BASIS_T6 + ' TCS close-out.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_9feba11dba0d4769870e', FULL), ev('ev_006d5c5abf0a460d869e', FULL)]),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_sched,
                text=('TP-6 filename versus UEF-6 drawing: file filed as GA & MECH LOAD OF TP-6, title block reads GA '
                      '& MECHANICAL LOAD OF UEF-6, dwg M038 (both sheets); TCS header also says TP-6; legs attach to '
                      'UEF-6, no TP-6 entity created.'))]
    return dict(summary='UEF-6 hoist schedule, foundation loads, civil, TCS close-out (TP-6 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record TP-6 handling/structural/access detail',
                    questions=['What hoist, foundation and TCS outcomes apply at UEF-6?'],
                    reviewed_evidence_ids=[], gaps=['Tank deciding record (top-model Q1).']))


def pkg_u6p():
    sup_p1 = [ev('ev_03dbce3bff0446739e4d', FULL)]
    sup_p2 = [ev('ev_126cf8728aa54401bd59', FULL)]
    mapping = ('UEF-6 DFDS application branches (FIO layout Rev 2): view 1-1 FAS-35/PRU-35 to EAC-5B and FAS-38/PRU-38 '
               'to EAC-5A; view 2-2 FAS-36/PRU-36 to EAC-5B and FAS-39/PRU-39 to EAC-5A; view 3-3 FAS-37/PRU-37 to '
               'EAC-7; view 4-4 FAS-40/PRU-40 to EAC-7. Terminal drops 15NB water / 20NB air; FFL legs. Pipe supports '
               'PS-1 8 nos, PS-2 6 nos, PS-3 4 nos, PS-4 6 nos, PS-5 6 nos, PS-6 8 nos. Header fixing details at '
               'discharge and receipt ends; service-water and drinking-water tapping details with flow control and '
               'pressure regulating units.')
    headers = ('UEF-6 header labels as printed: FROM UAF-5 / TO UAF-5 / FROM UAF-7 / TO UAF-7 / TO UAX-5 on the UEF-6 '
               'equipment sheet (mains pass-through plausible but unproven; recorded as copied-label suspicion, not as '
               'UEF-6 supply). EAC-5A/B, EAC-7 conveyor labels; 300x1000 water-pipe opening; 1200 SQ debris-chute '
               'opening; common landing-area load 3.5T typical.')
    bom = ('UEF-6 piping BOM excerpts (Rev 2): DFDS air 50NB 49m / 20NB 134m with elbows; DFDS water 25NB 49m / 15NB '
           '134m; service water 100NB 49m; potable galvanized 50NB 49m; 44 nos nozzle B 1/4, 4 nos 4-spray headers, '
           '8 nos 9-spray headers, 220m PU tube 8 OD. Notes: dimensions mm, levels meters; support spacing changeable '
           'at erection; pipes supported every 3m max; SW/PW taps 1200mm above FFL. TCS FIO-R: refer UEF-4 comments '
           '(06-Jul-19) and UEF-1 175286 comments (03-Jul-19), drawing revised accordingly.')
    ops = [dict(op='assert', subject=ent('UEF-6'), predicate='assembly_arrangement', value=mapping,
                context=dict(kind='specification', basis=BASIS_U6 + ' Application branches and supports.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='assert', subject=ent('UEF-6'), predicate='utility_header_routing', value=headers,
                context=dict(kind='specification', basis=BASIS_U6 + ' Header labels with suspicion.'),
                origin='explicit', confidence=0.85, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-6'), predicate='utility_bom_summary', value=bom,
                context=dict(kind='specification', basis=BASIS_U6 + ' BOM excerpts and notes.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='source_note', origin='explicit', confidence=0.85, evidence=sup_p1 + sup_p2,
                text=('UEF-6 piping suspicions preserved: UAF-5/UAF-7/UAX-5 mains labels on a UEF-6 sheet (UEF-7 piping '
                      'correctly references UAF-6 on UEF-7 sheets, so a UEF-6 sheet referencing UAF-6 would be expected '
                      'if local); both piping sheets read SHEET 1 OF 2 for dwg M291 (possible drafting duplication, '
                      'needs 300 dpi confirm before sheet linking); EAQ-5A glyph ambiguous Q/C at 150 dpi, not modeled '
                      'as EAC without confirm.'))]
    return dict(summary='UEF-6 piping branches, headers with UAF suspicion, BOM, sheet conflict (UEF-6 piping)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record UEF-6 DFDS/SW/PW installation scope',
                    questions=['How is DFDS/SW/PW laid out at UEF-6 and what labels are suspect?'],
                    reviewed_evidence_ids=[], gaps=['UAF label resolution; sheet-number confirm.']))


def pkg_t7d():
    sup_p1 = [ev('ev_8e345f4e65fa4e3e9deb', FULL)]
    hoist = ('Hoist schedule UEF-7: EH-1 10T lift 14.0m B.O.M.R. +15.000M for EAC-5A/B head and snub pulleys + drive '
             'units; EH-2 2.5T/6.0m/+7.100M for EBA-6A/6B tail pulleys (tower-scoped tag: same EH-2 tag carries '
             'different rating/location at UEF-6, never merged); MH-1 1T/6.0m/+7.100M for flap-gate KB-FG-5/6 actuator. '
             'Monorails EH-1 10T @ +15.000M, EH-2 2.5T @ +7.100M, MH-1 1T @ +7.100M. Equipment labels: TRANSITION '
             'DIST 3500, 1000 WP at discharge, head pulley, 10thk rubber sealing for cutout, movable stool, '
             'inspection door, KB-FG-5, KB-FG-6, CBS, 950 I/S, debris chute, downcomer, mesh guard all round tail '
             'pulley.')
    loads = ('UEF-7 foundation loads per base plate (footing) in kN, selected groups: 5A/B HF-1 dead 5.76 / live 0.04 / '
             'start-Hx 27.08 / normal-Hx 23.65 / start-Vy -17.95 / normal-Vy -15.80; HF-2 36.47/13.95/37.22/31.39/'
             '-58.03/-50.33; HF-3 13.18/7.13/53.26/46.40/75.63/67.19; 6A/B TF-1 7.16/0.87/30.75/29.09/-25.45/-24.07; '
             '6A/B TF-2 14.26/7.55/32.18/30.44/29.30/27.71. Footnote: (-) vertical = uplift; live load at 1.1 T/cu.m '
             'density. Full table on sheet.')
    civil = ('UEF-7 civil notes (Rev 6, approved 18-Oct-2019): paving all round TP per civil specification; 150mm kerb '
             'at drive and other floors with handrail to 1.1m all round (recorded); floor openings removable handrail '
             'with chequered plate; grating toe guard; chequered step at 10deg+ slopes; garland drain around building '
             '(recorded); cable openings tentative; civil/structural tentative; openings clear; hood 6mm MS; impact '
             'chute 20mm Hardox 400, non-impact 10mm; FFL RL+5.60M = plant EL 0.0M, ground RL+5.0M.')
    tcs = ('UEF-7 TCS threads (A AOC 30-Nov-18, Rev 6): debris-chute fixing detail provided; column kept (950mm clear '
           'between conveyor structure and 250mm I-column face, no maintenance fouling); drive blow-up view shown with '
           'dims per latest equipment GA; downcomer relocated to corner where possible; safety mesh all round tail '
           'pulley (recorded); 1200 entry revised; short-post fixing/load shown (SS-1, loads in table); walkway 1700mm '
           'clear retained against 2000mm ask, constrained by tail-pulley handling from monorail fixed at EL7.1m '
           '(recorded with qualification); opening 1400x1500 ok as per layout against 950x1200 chute; paving per '
           'civil spec; dimensions final; floor openings with removable handrail/chequered plate; load data and drive '
           'per approved revised tension/motor rating (recorded); DBR potable 300Ltr against GA 250L, reply revises '
           'capacity and height as piping layout (recorded 300L); ladder 6B-LA1 kept (600x250 I-column gives clear '
           'space, no relocation).')
    ops = [dict(op='assert', subject=ent('UEF-7'), predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_T7 + ' Handling schedule.'),
                origin='explicit', confidence=0.95, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-7'), predicate='assembly_arrangement', value=loads,
                context=dict(kind='specification', basis=BASIS_T7 + ' Foundation loads.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-7'), predicate='document_note', value=civil,
                context=dict(kind='specification', basis=BASIS_T7 + ' Civil notes.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=ent('UEF-7'), predicate='document_note', value=tcs,
                context=dict(kind='specification', basis=BASIS_T7 + ' TCS close-out.'),
                origin='explicit', confidence=0.9, evidence=[ev('ev_bbfb4a3fe8d84ee39a5b', FULL)]),
           dict(op='source_note', origin='explicit', confidence=0.85, evidence=sup_p1,
                text=('UEF-7 copied-label suspicions preserved: SCP-EAC-5B and LCS-EAC-5B tags in the EL+8.500M plan '
                      '(EAC-5A/B as upstream feed into UEF-7 is plausible, kept as suspicion only); EH-2 tag reused '
                      'with different rating/location at UEF-6 (3.5T tripper bend) versus UEF-7 (2.5T tail) and MH-1 '
                      'likewise; tags are tower-scoped, never merged across towers. TP-7 filename versus UEF-7 drawing '
                      '(M039) same pattern as TP-4/5/6; legs attach to UEF-7.'))]
    return dict(summary='UEF-7 hoist schedule, foundation loads, civil, TCS close-out, label suspicions (TP-7 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record TP-7 handling/structural/access detail',
                    questions=['What hoist, foundation and TCS outcomes apply at UEF-7?'],
                    reviewed_evidence_ids=[], gaps=['E/N grid transcription (illegible at scan).']))


def pkg_u7p():
    sup_p1 = [ev('ev_01ef79d9d67a429992de', FULL)]
    sup_p2 = [ev('ev_35d6d3b0e48f4ff3b01c', FULL)]
    mapping = ('UEF-7 DFDS application branches (FIO layout Rev 2): view 1-1 FAS-44/PRU-44 to EAC-5B; view 2-2 '
               'FAS-41/PRU-41 to EAC-5A; view 3-3 FAS-46/PRU-46 and FAS-43/PRU-43 to EAC-6B; view 4-4 FAS-42/PRU-42 '
               'and FAS-45/PRU-45 to EAC-6A. Terminal drops 20NB air / 15NB water; FFL legs. Pipe supports PS-1 8 '
               'nos, PS-2 8 nos, PS-3 10 nos, PS-2a 5 nos, PS-4 7 nos, PS-5 6 nos; header fixing details at discharge '
               'and receipt ends.')
    route = ('UEF-7 header continuation: 32NB air / 20NB water / 65NB service FROM UAF-6, 50NB potable TO UAF-6; '
             'FROM PH-2 80NB service + 50NB potable; TO TP-16/17 80NB service + 32NB potable; EBA-6A/B tail-pulley '
             'zone with PRU-44/FAS-44, FAS-41/PRU-41, FAS-42,45/PRU-42,45, FAS-43,46/PRU-43,46; PVC tank arrangement '
             'for PW system; 100 DIA PVC floor sleeves; 300x1000 water-pipe opening; 1200 SQ debris-chute opening; '
             '800x600 cable opening. E/N grid values legible only in crops, full grid table not transcribed.')
    tcs = ('UEF-7 piping TCS (FIO-R): FFL routing hinders man movement and TP aesthetics, pipes rerouted to roof and '
           'dropped along conveyor on short-post support to discharge end, FAS/PRU locations revised accordingly, '
           'drawing revised; check utility pipes against vacuum-cleaning ducting; align with UEF-1 175286 comments. '
           'Both piping sheets read SHEET 2 OF 2 for dwg M292 (possible drafting duplication, needs 300 dpi confirm '
           'before sheet linking).')
    ops = [dict(op='assert', subject=ent('UEF-7'), predicate='assembly_arrangement', value=mapping,
                context=dict(kind='specification', basis=BASIS_U7 + ' Application branches and supports.'),
                origin='explicit', confidence=0.9, evidence=sup_p2),
           dict(op='assert', subject=ent('UEF-7'), predicate='utility_header_routing', value=route,
                context=dict(kind='specification', basis=BASIS_U7 + ' Header continuation.'),
                origin='explicit', confidence=0.85, evidence=sup_p1),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=sup_p1 + sup_p2 + [ev('ev_6dc0c6740c3244c3bb0a', FULL)], text=tcs)]
    return dict(summary='UEF-7 piping branches, continuation, TCS routing, sheet conflict (UEF-7 piping)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record UEF-7 DFDS/SW/PW installation scope',
                    questions=['How is DFDS/SW/PW laid out at UEF-7 and what was revised?'],
                    reviewed_evidence_ids=[], gaps=['E/N grid table; sheet-number confirm.']))


def pkg_ctd():
    sup_p5 = [ev('ev_142e4eee958d4c258029', FULL)]
    sup_logic = [ev('ev_305043d142fb468a867c', FULL)]
    sup_motor = [ev('ev_44b8d0d2437244a08020', FULL), ev('ev_a4478424942b446d891b', FULL)]
    sup_p36 = [ev('ev_336d0e49a9a44ee2bc1c', FULL), ev('ev_7798d437a4a448008814', FULL)]
    sup_p40 = [ev('ev_26fd82b75e334640a24c', FULL), ev('ev_67600e5f061d43c2b40a', FULL),
               ev('ev_262c5ad5db194ca88d7d', FULL)]
    divider = ('Fixed-tripper and flow-divider scheme (system description p5, UEF-4/UEF-5): through fixed tripper '
               'FTR-1, EAC-4A feeds coal either to EAC-4A (belt continuation) or to stacker-yard conveyor EAC-11 '
               'through flow divider KB-FD-3; through FTR-2, EAC-4B feeds coal either to EAC-4A through flow divider '
               'KB-FD-3 or to EAC-11 (control names only KB-FD-3 for both legs against GA KB-FD-3 + KB-FD-4, '
               'top-model Q2). Flow dividers positionable throughout length with AI 4-20mA position to DCS; stop '
               'command at site-adjustable position; permissives and trips same as flap gate.')
    divider5 = ('UEF-5 divider scheme (system description p5): EAC-4A feeds EAC-5A/5B through flap gate KB-FG-3 or '
                'EAC-9 through divider KB-FD-5; EAC-4B feeds EAC-5A/5B through KB-FG-4 or EAC-9 through KB-FD-6. '
                'UEF-6: through FTR-3, EAC-5A feeds EAC-5A (continuation) through KB-FD-7 or EAC-7; through FTR-4, '
                'EAC-5B feeds EAC-5B through KB-FD-8 or EAC-7. UEF-7: EAC-5A/5B feed EBA-6A or EBA-6B by flap gate '
                'KB-FG-5 or KB-FG-6. No selector inlet-chute string in this write-up (sole SELECTOR hit is '
                'coal-sampling selector switches, p19); EAC-5 selector wording kept as terminology gap.')
    brake = ('Conveyor brake and scoop scheme (general, each conveyor incl. EAC-4A/4B/5A/5B): brake auto-releases on '
             'main-conveyor command and auto-applies on motor off or fluid-coupling disengaged. Main-motor permissives: '
             'winding <120degC, DE/NDE bearing <70degC, electrical healthy, local stop reset; trips at winding >130, '
             'bearing >80, electrical trip, local stop. Scoop OUT needs oil pump ON, main motor ON, CBS clear, PCS/BSS '
             'clear, brake released, succeeding conveyor running, flap gate in position; scoop IN (with 60s ZSS delay, '
             'oil-flow 10s delay) plus belt-feeder trips on CBS/PCS/BSS/ZSS/succeeding-conveyor-off. Zero-speed trips '
             'below 85% rated speed. HT motors run on at no load by disengaging fluid coupling on process-interlock '
             'failure, tripping only on motor fault (O/L, high winding temp); coasting time, thrustor brake, actuator '
             'and chute sized against downstream spillage on next start.')
    path4 = ('EAC-4A path clauses verbatim (Flow Path-1 p36-37, repeated Path-2 p41-42): FD-5 FWD toward EAC-5A/5B '
             'through FG-3 REV needs EAC-5A running; FG-3 FWD needs EAC-5B; FD-5 REV toward EAC-9 needs EAC-9; FD-5 '
             'intermediate needs 5A/5B/9; FD-3 REV toward EAC-4A needs 5A/5B/9; FD-3 FWD toward EAC-11 needs EAC-11; '
             'FD-3 intermediate needs 4A/11. Scoop actuator for EAC-4A needs EAC-4A main motor running. EAC-4B mirrors '
             'with FD-6/FG-4/FD-4. Internal control conflict: p37 row 12 FD-1 FWD toward 4A/4B through FG-1 FWD needs '
             'EAC-4B running versus p42 row 38 same leg through FG-1 REV; both kept verbatim (top-model Q5 scope).')
    path5 = ('EAC-5A path clauses verbatim (Path-1 p36: FD-7 FWD toward EAC-7 needs EAC-7; Path-2 p40-41: FG-5 FWD '
             'toward EBA-6A needs EBA-6A or EAC-7 running, FD-7 toward 5A or EAC-7 or intermediate, FG-5 REV toward '
             'EBA-6B needs EBA-6B or EAC-7; Path-5 p49 repeats). EAC-5B mirrors with FG-6/FD-8 toward EBA-6A/6B/EAC-7. '
             'Scoop actuator for EAC-5A needs EAC-5A main motor; EAC-5B sheet rows as printed reference EAC-5A main '
             'motor (p36 row 7, p41 row 33, p49 row 9) against the correct 5A-for-5A pattern, preserved as copy error.')
    ops = [dict(op='assert', subject=ent('UEF-4'), predicate='operating_requirement', value=divider,
                context=dict(kind='specification', basis=BASIS_CTL + ' FTR/divider scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_p5),
           dict(op='assert', subject=ent('UEF-5'), predicate='operating_requirement', value=divider5,
                context=dict(kind='specification', basis=BASIS_CTL + ' UEF-5/6/7 divider scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_p5),
           dict(op='assert', subject=ent('EAC-4A'), predicate='operating_requirement', value=brake,
                context=dict(kind='specification', basis=BASIS_CTL + ' Brake/scoop scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_motor),
           dict(op='assert', subject=ent('EAC-4B'), predicate='operating_requirement', value=brake,
                context=dict(kind='specification', basis=BASIS_CTL + ' Brake/scoop scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_motor),
           dict(op='assert', subject=ent('EAC-5A'), predicate='operating_requirement', value=brake,
                context=dict(kind='specification', basis=BASIS_CTL + ' Brake/scoop/HT scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_motor + sup_logic),
           dict(op='assert', subject=ent('EAC-5B'), predicate='operating_requirement', value=brake,
                context=dict(kind='specification', basis=BASIS_CTL + ' Brake/scoop/HT scheme.'),
                origin='explicit', confidence=0.9, evidence=sup_motor + sup_logic),
           dict(op='assert', subject=ent('EAC-4A'), predicate='operating_requirement', value=path4,
                context=dict(kind='specification', basis=BASIS_CTL + ' Path clauses with conflict.'),
                origin='explicit', confidence=0.9, evidence=sup_p36),
           dict(op='assert', subject=ent('EAC-5A'), predicate='operating_requirement', value=path5,
                context=dict(kind='specification', basis=BASIS_CTL + ' Path clauses with copy error.'),
                origin='explicit', confidence=0.9, evidence=sup_p36 + sup_p40),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_p5,
                text=('EAC-4B destination wording (control p5) preserved as garbled: EAC-4B feeds coal either to '
                      'EAC-4A through flow divider KB-FD-3 or to EAC-11 (no KB-FD-4, and 4B-to-4A via divider against '
                      'GA chute arrangement discharging each lane divider to EAC-11). Top-model Q2/Q5 scope.'))]
    return dict(summary='FTR/divider schemes, brake/scoop/HT logic, EAC-4/5 path clauses with conflicts (control)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record conveyor-4/5 control depth legs',
                    questions=['What FTR/divider, brake/scoop and path logic applies to EAC-4A/4B/5A/5B?'],
                    reviewed_evidence_ids=[], gaps=['FD naming (top-model Q2); EAC-4B wording (top-model Q5).']))


def pkg_cva():
    sup_p1 = [ev('ev_8fd900ac9f264afbb8a9', FULL)]
    parts = ('AllScan analyser parts table, belt and stringer assembly M330 (shared CV-1/CV-2, documents do not '
             'differentiate): eye bolt M12 x2; hex bolt M12x40 x24; plain nut M12 x26; washer M12 x50; RTI ALLS MEC '
             'detector cradle single-detector-5 x1; electrical cabinet assembly x1; cabinet standoffs x4; frame '
             'assembly x1; gas struts x2 + pivot x1; hood prop bar x1; solar shield x1; HDPE side shields back/cabinet '
             'x1 each + window splits L/R x1 each; source cradle sides L/R x1 each; top shields cabinet/rear x1 each; '
             'hood assembly x1; cabinet mounting frame x1; source holder assembly x1 (holder wording only); existing '
             'site-specific stringer assembly x1. Applies to 1400mm belt (EBA-6A/6B, 16A/16B, 17A/17B).')
    dims = ('Analyser frame geometry (shared): belt width 1400, inside-to-inside 1670, CSR 1730, outside-to-outside '
            '1800, 35deg trough; section B-B: stringer top to detector top 35mm, to central roller 275mm, detector '
            'top to laden-belt underside min 10mm max 20mm, stringer top to laden-belt underside 255mm (2x sag); '
            'ballooned details A (1:10) and B (1:5); hood shown raised on gas struts with source-cradle box exposed '
            'and side detector doors open, and closed with double doors shut. Ref docs M331 datasheet, M330/M077 GA.')
    ops = [dict(op='assert', subject=ent('Coal Analyser Assembly - 1400mm Belt'), predicate='assembly_arrangement',
                value=parts, context=dict(kind='specification', basis=BASIS_CVA + ' Parts table.'),
                origin='explicit', confidence=0.95, evidence=sup_p1),
           dict(op='assert', subject=ent('Coal Analyser Assembly - 1400mm Belt'), predicate='assembly_arrangement',
                value=dims, context=dict(kind='specification', basis=BASIS_CVA + ' Frame geometry.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_1d164954875049d0b884', FULL), ev('ev_da4279fbded34c5a97c7', FULL),
                          ev('ev_5c069c94cde74674b896', FULL), ev('ev_d845c8f81f5e4c2481d8', FULL)]),
           dict(op='assert', subject=ent('CV-1 detector and cradle assembly'), predicate='assembly_arrangement',
                value=('Detector and cradle (shared design): RTI ALLS MEC single-detector-5 cradle; stringer top to '
                       'detector top 35mm; detector top to laden-belt underside 10-20mm. No detector electronics, '
                       'isotope or activity stated in this assembly file.'),
                context=dict(kind='specification', basis=BASIS_CVA + ' Detector detail.'),
                origin='explicit', confidence=0.9, evidence=[ev('ev_1d164954875049d0b884', FULL)]),
           dict(op='assert', subject=ent('CV-1 electrical cabinet assembly'), predicate='assembly_arrangement',
                value=('Electrical cabinet (shared design): cabinet assembly on 4 standoffs with slotted mounting '
                       'frame beside analyser frame; no wiring, power ratings or IO stated in this file.'),
                context=dict(kind='specification', basis=BASIS_CVA + ' Cabinet detail.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='source_note', origin='explicit', confidence=0.95, evidence=sup_p1,
                text=('Assembly M330 title-block REV 0 (registry filed as Rev 1); 5 sheets; FIO 18-Oct-2019. None of '
                      'the three analyser documents differentiate CV-1 versus CV-2: all legs attach to shared RTI '
                      'records and CV-1 subassemblies as representative; CV-2 records keep existing geometry.'))]
    return dict(summary='Analyser belt/stringer parts, geometry, refs (analyser assembly)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record analyser mechanical assembly detail',
                    questions=['What parts and geometry define the 1400mm AllScan assembly?'],
                    reviewed_evidence_ids=[], gaps=['CV-1 vs CV-2 differentiation (absent in corpus).']))


def pkg_cvc():
    ana = ent('RTI AllScan PGNAA Coal Analyser')
    cap = ('AllScan capability (shared, Rev 1 datasheet): Real Time Instruments (Australia) Pty Ltd online coal '
           'analysers measuring real-time as-fired coal quality by neutron-isotope activation (PGNAA); minimum ash, '
           'moisture, sulphur and GCV plus Si/Fe/Al/K/Ca/Mg; AERB type-test approval for Indian industry. Suitable '
           'for steel-chord belting (verbatim), FR chloride belts, belt speed 2.2-3.5 m/s, lump (-)100mm (revised '
           'TDS per TCS: RTI confirms suitability at (-)100mm before crusher house; supersedes (-)20mm occasionally '
           '(-)50mm submission), 35deg trough, tilt horizontal-16deg, strong/weak vibration, belt width 1000-2200mm '
           'and bed 200-450mm (datasheet range; Specs table separately 750-2400mm, both kept). One neutron dosimeter '
           'per TCS confirmed for Maitree radiation measurement.')
    meas = ('Elements and ranges (shared): up to 78 elements; Ash >0.5-100%, Moisture >0.5-100%, GCV >90 Kcl/Kg '
            '(verbatim, no upper limit), SiO2 >0.3-100%, Al2O3 >0.35-100%, Fe2O3 >0.35-100%, total Sulphur >0.05-100%; '
            'total moisture from hydrogen spectra (no separate microwave meter needed); free-moisture Moist Scan '
            'optional; dynamic sampling aligns analyser to laboratory. Accuracy table per ASTM D 6543 as printed: GCV '
            '30%-45% +/-1.5%, Moisture 0%-20% +/-1.0%, Ash 2500kcal-5000kcal +/-100 Kcal/Kg; value-column alignment '
            'appears swapped between GCV and Ash rows, recorded without correction (proofread item).')
    elec = ('Electronics and enclosure (shared): NaI detector + PMT + MCA in neutron-absorbing casing under belt with '
            'heater pads and temperature sensor; 316 stainless enclosure IP65 (table/text) versus IP66 (Specs table, '
            'both kept); HMI touch screen with cover for set-up/calibration, relocatable to walkway or control room; '
            '6 cable glands (power 110/230VAC, plant/analyser comms, source-drive contacts, detector heater/MCA '
            'power, detector data, modem antenna); ModBus RS485 + 3G standard, PLC/Ethernet/serial/4-20mA optional; '
            '2400W 120/240VAC 1-phase at analyser control station; on-board diagnostics with email fault reports; no '
            'belt-weigher input needed. Weight 1200-1500kg typical (Features cites approx 1500kg and 1.2t vs 3t, all '
            'kept). Aperture variable per material flow; customer prevents large rocks striking analyser.')
    cal = ('Calibration (shared): 5-day installation/commissioning (day 2 zero calibration, day 3 standard '
           'verification, day 4 contingency, day 5 plant running); accuracy verified by calibration standards, no '
           'labour-intensive sampling; stateless machine re-runs standards/dynamic data, archives spectra, refines '
           'calibration continually. No site-specific CV-1/CV-2 constants stated.')
    src = ('Source holder (shared, explicit quotes only): parts-table Neutron Source Holder houses radioactive isotope '
           'Cf-252; 20ug Cf-252, 2.6-year half-life, topped up 10ug at 2.5 and 5 years, disposal at 7.5 years; source '
           'normally supplied separate to analyser but holder is a registered storage/transport vessel so source can '
           'be pre-loaded; holder above belt on cradle under hood, neutron-absorbing fire-retardant, disc cavity, '
           'electro-mechanical 180deg spring-window drive with manual override, ON/OFF indication, padlockable OFF; '
           'fail-safe auto source drive with isolation point; exposure typically below 5uSv/h outside, average '
           '1.3uSv/hr at catwalk; walkway off-switch even with conveyor running. No loaded-source status at CV-1/CV-2 '
           'asserted beyond these quotes. Californium test source for 17.7 spectrum check (Cf252 remark) versus '
           'Thorium test source in enclosed NTPC MQP 9.7 (reference only).')
    ops = [dict(op='assert', subject=ana, predicate='assembly_arrangement', value=cap,
                context=dict(kind='specification', basis=BASIS_CVC + ' Capability.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_f77f11ed07504dacbe2c', FULL), ev('ev_43b3e787aa7c4dea95ae', FULL),
                          ev('ev_ecf290b20569428c8aa7', FULL)]),
           dict(op='assert', subject=ana, predicate='assembly_arrangement', value=meas,
                context=dict(kind='specification', basis=BASIS_CVC + ' Elements and ranges.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_239777d454eb4cc8bb33', FULL), ev('ev_795583c8a8df460ea740', FULL)]),
           dict(op='assert', subject=ana, predicate='assembly_arrangement', value=elec,
                context=dict(kind='specification', basis=BASIS_CVC + ' Electronics and enclosure.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_7b8a31c9bb4b46738e3d', FULL), ev('ev_b51d70b05b374478a36d', FULL),
                          ev('ev_8f65262a70ca49c9b74a', FULL), ev('ev_215fcc4253a2433796aa', FULL)]),
           dict(op='assert', subject=ana, predicate='assembly_arrangement', value=cal,
                context=dict(kind='specification', basis=BASIS_CVC + ' Calibration.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_1a37f2501a28456a9a50', FULL), ev('ev_935d5cb38bab4fb39a58', FULL)]),
           dict(op='assert', subject=ana, predicate='assembly_arrangement', value=src,
                context=dict(kind='specification', basis=BASIS_CVC + ' Source holder, quotes only.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_8f65262a70ca49c9b74a', FULL), ev('ev_795583c8a8df460ea740', FULL),
                          ev('ev_2f0834e65d1e4de1b9db', FULL)]),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=[ev('ev_f77f11ed07504dacbe2c', FULL)],
                text=('Datasheet revision: cover REV 1 second submission 30/10/2019 (registry filed Rev 0); 19 PDF '
                      'pages (cover + TCS + 12 RTI sheets + 5 brochure pages). Brochure pages carry vendor pagination '
                      'EP-0004 R2016-09. BOM of Online Coal Analyser ALL SCAN MODEL rows 01-16 with 2 radiation signs '
                      '(verbatim Radiations Sign) recorded in electronics value.'))]
    return dict(summary='Analyser capability, elements, electronics, calibration, source quotes (datasheet/catalogue)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record analyser catalogue/electronics/calibration',
                    questions=['What catalogue, electronic and calibration data define the AllScan?'],
                    reviewed_evidence_ids=[], gaps=['Site constants; loaded status (never infer).']))


def pkg_cvq():
    ana = ent('RTI AllScan PGNAA Coal Analyser')
    stages = ('Maitree QAP MAITREE-00-QP-QA-175334-ISG REV 1 27/09/2019 (CAT-I, BHEL ISG, contract IS-I-15-2004): stages '
              'I raw materials and bought-out items (borated polyethylene physical/dimensional 70/50%, stainless side '
              'panels 70/50%, cross braces and source-holder cradle 100%, detector housing cradle 70%, source-holder '
              'poly sheet/cutting, detector housing poly shell/sleeve/cover), II assembly/in-progress (cabinet 316 '
              'SS type/seal 50% + cutouts 100%, component selection 70%, mounting frame 50%, source/detector/heater '
              'cables 100% length, rotor free movement 100%, detector insulation/wiring 70/100%), III final '
              'inspection/functionality (DIN rail, wiring vs schematic, cable continuity/heat-shrink, shutter-drive '
              'on/off rotation W, detector cover screws W, terminations/labels/power-up LEDs W, 100% functional '
              'system checks W), IV (as printed V) final inspection of completed analysers and documents, Annexure-I '
              'makes (Mackay Aluminium, Blakey Engineering, Real Time Instruments, Bridgeport MCA). Legend '
              'P/V/W/TC/IR with M/C/B witness columns. References M077/M330/M331.')
    wit = ('Key witness/verification rows (shared): side-panel dimensional/location V/V; cross-brace/cradle and '
           'detector-cradle dims V/V; source-drive cable length V/V; detector data/heater cable V/V; rotor free '
           'movement V; detector wiring per AS 3000 V/V; shutter-drive on/off rotation W/W; detector cover screws '
           'W/W; cable labels V/V; power-up LEDs W/W; 100% functional system checks W/W; MCA reset relay W/W; '
           'processor comms W/W; heater sensor/heater/control W/W; 17.7 valid spectrum with Californium test source '
           '(detector in test analyser with Cf252 source) W/W; I/O simulation W/W; spectrum alignment and lock-on 98% '
           'conformity W/W. Heater wattage via mega circuit, temp sensor in 17.4.')
    ref = ('Prior-approval reference enclosed in the file (not Maitree acceptance): NTPC MQP QP 1901 REV 02 '
           '01/02/2018 for online coal analyser-RTI, APP CAT-I released 09-02-18 with minor comments (NTPC letter '
           'G K Haldar). MQP differs: radiation survey at manufacturer spec/Indian Radiation Authority with Rad '
           'Survey Report; 9.7 spectrum check with Thorium test source (against Maitree 17.7 Californium); static '
           'calibration check 100% W. TCS replies: BOI made by RTI Australia with endorsement done; radiation-level '
           'check around fully functional analyser deferred (Californium sources ship direct to site, commissioning '
           'report carries the site survey); statutory Bangladesh clearances to be enclosed.')
    ops = [dict(op='assert', subject=ana, predicate='document_note', value=stages,
                context=dict(kind='specification', basis=BASIS_CVQ + ' QAP stages.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_2e619de331934fde813d', FULL), ev('ev_6bc1d714527049cc9c91', FULL),
                          ev('ev_1c492a44a2264064acf4', FULL)]),
           dict(op='assert', subject=ana, predicate='document_note', value=wit,
                context=dict(kind='specification', basis=BASIS_CVQ + ' Witness rows.'),
                origin='explicit', confidence=0.9,
                evidence=[ev('ev_1c492a44a2264064acf4', FULL), ev('ev_4bca5bab860f44c7b436', FULL)]),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=[ev('ev_0c3c273fb07d46d6b6c9', FULL), ev('ev_dbe2b915e23745d9a313', FULL),
                          ev('ev_9a6e794e51d5466c8611', FULL)], text=ref),
           dict(op='source_note', origin='explicit', confidence=0.9,
                evidence=[ev('ev_503df8d2831f4ef3b7ad', FULL)],
                text=('QAP file revision stack: cover REV 2 (10/12/2019 revised per customer comments) over Maitree '
                      'QAP body REV 1 over enclosed NTPC MQP REV 02 (2018); 17 PDF pages (cover + 5 QAP + TCS + NTPC '
                      'letter + MQP title/comments + 7 MQP). QAP body skips numeral IV (I, II, III, V as printed).'))]
    return dict(summary='Analyser QAP stages, witness rows, NTPC reference, TCS (analyser QAP)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record analyser QAP and acceptance scope',
                    questions=['What QAP stages, witnesses and references govern the analysers?'],
                    reviewed_evidence_ids=[], gaps=['Statutory clearances; site radiation survey.']))


PACKAGES = [(DOC_C4, pkg_c4d, 'c4d', 740), (DOC_T4, pkg_t4d, 't4d', 741),
            (DOC_U4, pkg_u4p, 'u4p', 742), (DOC_C5, pkg_c5d, 'c5d', 743),
            (DOC_T5, pkg_t5d, 't5d', 744), (DOC_U5, pkg_u5p, 'u5p', 745),
            (DOC_C6, pkg_c6d, 'c6d', 746), (DOC_T6, pkg_t6d, 't6d', 747),
            (DOC_U6, pkg_u6p, 'u6p', 748), (DOC_T7, pkg_t7d, 't7d', 749),
            (DOC_U7, pkg_u7p, 'u7p', 750), (DOC_CTL, pkg_ctd, 'ctd', 751),
            (DOC_CVA, pkg_cva, 'cva', 752), (DOC_CVC, pkg_cvc, 'cvc', 753),
            (DOC_CVQ, pkg_cvq, 'cvq', 754)]


def all_ids(doc):
    import sqlite3 as _sq
    with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
        return [r[0] for r in _db.execute('SELECT id FROM evidence WHERE document_id=? ORDER BY page, id', (doc,)).fetchall()]


def main():
    from chp.store import Store
    from chp.patches import validate, commit
    from chp.reviewed_ingestion import stage
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    plant = ROOT / 'data/plant'
    with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN')
        before = Store.__new__(Store).model(db=db)
        base_version = before['version']
    if not args.apply:
        if COPY.exists():
            shutil.rmtree(COPY)
        COPY.mkdir(parents=True)
        with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
            with sqlite3.connect(COPY / 'plant.sqlite3') as dst:
                db.backup(dst)
    else:
        assert base_version == 739, base_version
    running = base_version if not args.apply else 739
    for doc, builder, tag, ver in PACKAGES:
        if args.apply:
            assert running == ver - 1, (tag, running, ver)
        out = BASE / ('accepted-%s' % tag if args.apply else 'rehearsal-%s' % tag)
        out.mkdir(parents=True, exist_ok=True)
        body = builder()
        body['intake_assessment']['reviewed_evidence_ids'] = all_ids(doc)
        if args.apply:
            assert body == json.loads((BASE / ('rehearsal-%s/package.json' % tag)).read_text(encoding='utf8'))
            assert json.loads((BASE / ('rehearsal-%s/result.json' % tag)).read_text(encoding='utf8'))['ok']
        (out / 'package.json').write_text(json.dumps(body, indent=2) + '\n', encoding='utf8')
        store = Store(plant if args.apply else COPY)
        if not args.apply:
            running = store.version()
        assert store.version() == running, (doc, store.version(), running)
        visual = list({e['evidence_id'] for op in body['operations'] for e in op.get('evidence', [])})
        report = validate(store, {k: body[k] for k in ('summary', 'operations')}, doc, running, visual_ids=visual)
        (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
        assert not report['errors'], (tag, report)
        staged = stage(store, doc, body, visual_ids=visual, analysis_dir=str(out), expected_version=running)
        result = commit(store, staged['proposal_id'])
        (out / 'result.json').write_text(
            json.dumps({'ok': True, 'proposal_id': staged['proposal_id'], **result}, indent=2) + '\n', encoding='utf8')
        running = store.version()
        print(json.dumps({'doc': doc[:12], 'proposal': staged['proposal_id'], 'version': running}))
    if args.apply:
        with sqlite3.connect(plant / 'plant.sqlite3') as db:
            db.row_factory = sqlite3.Row
            after = Store.__new__(Store).model(db=db)
        bf = {a['id']: {k: v for k, v in a.items() if k not in ('canonical_subject', 'canonical_object')} for a in before['assertions']}
        af = {a['id']: a for a in after['assertions']}
        missing = [k for k in bf if k not in af]
        changed = [k for k in bf if k in af and bf[k] != {kk: vv for kk, vv in af[k].items() if kk in bf[k]}]
        assert not missing and not changed, (missing, changed)
        print(json.dumps({'applied': True, 'version': after['version'], 'new_assertions': len(af) - len(bf)}))


if __name__ == '__main__':
    main()
