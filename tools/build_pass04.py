"""Pass-4 packages (DQ-B17-001, DQ-B17-002, DQ-B18-001, DQ-B18-002, DQ-B19-001,
DQ-B19-002, DQ-B19-003, DQ-B19-004).

Locally extracted by four parallel readers (OCR text + full-page vision + zoom
crops) with per-source conflict lists, before any top-model trip, per
PASS_B_TWO_TIER_WORKFLOW.md complete-pass rule. Prior Tier-1 work already
covers headline ratings, family assembly notes and Tier-1 routes; these 16
one-source proposals add only the missing depth legs (drive vendor ratings,
brake reconciliation, pulley calc inputs, idler row BOMs, protection vendor
settings, machine family detail, DSS pump/nozzle/tank/setpoints, fire package
record, explicit gaps with deciding records). Chained v754 -> v770. Default:
isolated rehearsal in pass-04/rehearsal-copy; --apply performs guarded live
acceptance after the top-model return is folded in (proofread + 4 conflict Qs).
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-04'
COPY = BASE / 'rehearsal-copy'
DOC_C9D = 'doc_957d8f8bd41c4e71be3c'
DOC_C9S = 'doc_60a920124be746f680ed'
DOC_C9P = 'doc_41860f7c9ac2467bbdb4'
DOC_C9G = 'doc_cd640b41256b4b288744'
DOC_C10G = 'doc_229dddc0f5ab4d77bbf0'
DOC_PCS = 'doc_425fb77433564871b40e'
DOC_STKB = 'doc_78bebe6773984d59b013'
DOC_STKG = 'doc_d69ffd4c7c2241018323'
DOC_RECG = 'doc_3e81ea1c32df4215968d'
DOC_RECB = 'doc_498f70490d294542b8b0'
DOC_DSSS = 'doc_0f52c77514a74773ae30'
DOC_DSSR = 'doc_a6a2fa82944f4d12b8aa'
DOC_DSSP = 'doc_0eeb339e58a24707a475'
DOC_FIRE = 'doc_4d488fd685284c408297'
DOC_QRCP = 'doc_5a36f2843d504d6e96de'
DOC_PHIL = 'doc_e17edf6897d746fabe12'

BASIS_C9D = ('Drive schedule IS-3-SC-702-101-M107 Rev R2 24-11-2018 (customer doc Maitree-00-EAC-PA-175107-ISG-2); '
             'status block FOR APPROVAL, sheet stamped FIO FOR INFORMATION ONLY 14-Dec-2018. FIO non-approved '
             'schedule data only; group columns headed EAC 7/9/11/13 and EAC 8/10/12/14 as printed. Registry records rev 1 '
             'vs printed Rev R2 24-11-18.')
BASIS_C9S = ('Selection of drive components, brakes and belts IS-1-GA-702-101-M052 Rev 2 (customer doc '
             'Maitree-00-EAC-PA-175052-ISG); status block FOR APPROVAL, sheet stamped APPROVED 23-Nov-2018. '
             'Design selection only; required-vs-selected reconciliation as printed. Registry records rev 1 vs printed Rev 2.')
BASIS_C9P = ('Bearing selection & shell/diaphragm thickness calculation for conveyor pulleys, Rev 04 20-Dec-18 '
             '(BHEL/BTL); evidence stamp APPROVED 25-Feb-2019. Pulley input rows EAC 7/9/11/13 + EBA 8/10/12/14 only; '
             'bearing/shaft selections on later pages remain unopened. Registry filed blank revision vs printed Rev 04.')
BASIS_C9G = ('GA and load data belt conveyor-9, dwg IS-1-GA-702-101-M019 Rev 2 (customer dwg Maitree-00-KF-LH-175019-ISG-2); '
             'status block FOR APPROVAL, sheet stamped APPROVED 26-Nov-2018; Fichtner comments Trans 054935 15.10.18. Design only. '
             'Registry filed blank revision vs printed Rev 2.')
BASIS_C10G = ('GA and load data belt conveyor-10, dwg IS-1-GA-702-101-M020 Rev 2 (customer dwg Maitree-00-KF-LH-175020-ISG-2); '
              'status block FOR APPROVAL, sheet stamped APPROVED 26-Nov-2018; Fichtner comments 11.10.18. Design only. '
              'Registry filed blank revision vs printed Rev 2.')
BASIS_PCS = ('PCS BSS ZSS & belt-watch panel datasheet IS-4-GA-702-101-E804 REV 3 (customer doc 178803-ISG); status block '
             'FOR APPROVAL, sheet stamped APPROVED 18-Sep-2019 (registry filed rev 1). Vendor GA sheets for Jayashree '
             'electronic speed switch, pull-cord and belt-sway switches as printed; per-conveyor GCP allocation sheets remain unopened.')
BASIS_STKB = ('Basis of design for coal stacker 175249 Rev 2, vendor Hunan Changzhong, approved 27-Feb-2019. Project-family '
              'design for four stackers; applied to Yard 2 EAD-2 identified by coal-flow 175001 Rev 8. Component names without '
              'plant tags are descriptive. Installed configuration and commissioned settings are not verified.')
BASIS_STKG = ('GA & TDS of stacker 175126 Rev 2 (customer doc Maitree-00-EAF-DA-175126-ISG-1, prints EAF and -1 suffix as observed), approved 26-Nov-2018 with '
              'BIFPCL/BHEL compliance replies. Project-family design applied to Yard 2 EAD-2 as above. GA drawing sheets are '
              'image-only; reply text governs. Registry filed blank revision vs printed Rev 2.')
BASIS_RECG = ('GA & TDS of portal type scraper reclaimer 175127 Rev 2 (vendor dwg 47039267), approved 23-Nov-2018 with '
              'TENOVA compliance replies 09-11-2018. Project-family design for EAF-1..4 applied to Yard 2 EAF-2 identified by '
              'coal-flow 175001 Rev 8. Descriptive names; installed/commissioned state not verified. Approval stamp date string '
              "prints malformed '23-Nov-2019-11-2018' (read as 23-Nov-2018). Registry filed blank revision vs printed Rev 2.")
BASIS_RECB = ('Basis of design for portal reclaimer 175119 Rev 2 (vendor 47039270, TENOVA POC-705), approved 23-Nov-2018. '
              'Project-family structural/load design for four reclaimers applied to Yard 2 EAF-2 as above. Structural pressures '
              'are not trip settings. Internal system revision block prints rev 0 vs document Rev 2.')
BASIS_DSSS = ('Chemtrols coal stacker plain-water DSS design/control Rev 05, FIO 23-Jan-2021 (customer doc '
              'MAITREE-00-EAF-DB-175244-ISG). Coal section only; limestone dry-fog section excluded. Project-family design '
              'applied to Yard 2 EAD-2. Installed configuration and commissioned settings not verified. Registry records rev 1 '
              'and Approved authority vs sheet BHEL Rev 0 / Chemtrols Rev 05 FIO (critical mismatch).')
BASIS_DSSR = ('F. Harley plain-water DS BOD 47039284 Rev 2, approved 19-Aug-2019 (customer doc MAITREE-00-EAF-DB-175150-ISG-2), '
              'four portal reclaimers. Project-family design applied to Yard 2 EAF-2. Pump schedule ratings tentative, subject to '
              'final vendor selection. Installed state not verified. Registry records rev 1 vs printed Rev 2.')
BASIS_DSSP = ('P&ID of machine-mounted DS for portal reclaimer, vendor drg 3778-02-T-01 Rev 2 (customer doc '
              'MAITREE-00-EAF-MB-175151-ISG-2), FIO 19-Aug-2019. Typical arrangement; pipe routing tentative. Installed state not verified. '
              'Registry records rev 1 vs printed Rev 2.')
BASIS_FIRE = ('Datasheet/BOM for FDA system of stacker, drg IS-3-GA-702-108-E1104 REV 02 (KKS MAITREE-00-EAD-DA-179063-ISG, '
              'registry filed rev 1), vendor Hunan Changzhong; status FOR INFORMATION, stamped FIO 14-Nov-2019. Vendor '
               'supply/design proposal only; no erection, PLC I/O, commissioning or handover record in file. Stacker scope only. '
               'Sheet revision-history rows 1-6 blank.')
BASIS_QRCP = ('P&ID for plain-water DS for stockpile 175255 Rev 2, FIO 21-Jan-2019 (BOM item 19, note 9, typical QRC '
               'connection). Design arrangement; routing and installation unverified. Enclosed TCS references Rev 1 FIO-R vs sheet Rev 2. '
               'Registry filed blank revision.')
BASIS_PHIL = ('Operation & control philosophy for CHP stockpile DS + SW/PW pumping 175319 Rev 5, approved 26-May-2020. '
               'Yard 2 (Stockpile-2/EAE-2, SC-02) scope only; stockpile-1/3/4 values retained as stated pairing context. '
               'Design/control arrangement; installed and commissioned state unverified. Piping layout 175301 (FIO 16-Oct-2019) cited '
               'alongside. Registry filed blank revision vs printed Rev 5.')


def ev(eid, region):
    _evmap()
    full = _EV_MAP.get(eid[:12], eid)
    return dict(evidence_id=full, quote='', region=region)


FULL = [0.03, 0.05, 0.97, 0.97]

_ENT_CACHE = {}

_EV_MAP = {}


def _evmap():
    if not _EV_MAP:
        import sqlite3 as _sq
        with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
            for (i,) in _db.execute('SELECT id FROM evidence'):
                _EV_MAP.setdefault(i[:12], i)


def ent(label):
    if label not in _ENT_CACHE:
        import sqlite3 as _sq
        with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
            row = _db.execute('SELECT id FROM entities WHERE label=?', (label,)).fetchone()
        assert row, label
        _ENT_CACHE[label] = row[0]
    return _ENT_CACHE[label]


def note(subject, value, basis, eids, conf=0.95):
    return dict(op='assert', subject=subject, predicate='document_note', value=value,
                context=dict(kind='specification', basis=basis),
                origin='explicit', confidence=conf,
                evidence=[ev(e, FULL) for e in eids])


def gap(subject, value, basis, eids, conf=0.9):
    return dict(op='assert', subject=subject, predicate='source_gap', value=value,
                context=dict(kind='specification', basis=basis),
                origin='explicit', confidence=conf,
                evidence=[ev(e, FULL) for e in eids])


def disc(subject, value, basis, eids, conf=0.9):
    return dict(op='assert', subject=subject, predicate='source_discrepancy', value=value,
                context=dict(kind='specification', basis=basis),
                origin='explicit', confidence=conf,
                evidence=[ev(e, FULL) for e in eids])


def pkg_c9d():
    sched9 = ('Drive schedule EAC 7/9/11/13 group as printed (applies to EAC-9 with EAC-7/11/13; FIO data): motor SQ cage '
              'induction 680 kW, 4-pole, 3300V +/-6%, 50 Hz +3%/-5%, BHEL; gearbox bevel-helical B3-560, nominal ratio 20.9, '
              'exact 22.8, mechanical 1903 kW, thermal 1165 kW, fan-cooled YES, holdback YES, make PREMIUM; H.S. scoop '
              "coupling PST-660 (M107 prints 'PST - 660' with spaces), 975 kW at 1500 RPM, make row prints PREMLUM (sic); L.S. geared coupling RG-13, 2793 HP/100 RPM, torque "
              "19998 kg-m, max bore 330/min 140, make GBM; brake AC electro-hydraulic thruster, 951 kg-m, size EBTM-500-DS/I "
              "(M107 prints 'EBTM-500 - DS/I' with spaces), "
              'drum 500.0, brake make row prints ELEKCTROMAG (sic, KC; GA-9/GA-10 print ELEKTROMAG). Schedule prints RG-13 while GA-9 prints RG-12; both readings preserved, '
              'top-model Q1 retain_disagreement (deciding record: approved GBM geared-coupling GA with per-conveyor tag allocation or EAC-9 as-built nameplate).')
    sched10 = ('Drive schedule EAC 8/10/12/14 group as printed (column header reads EAC though EBA-10 is the machine; FIO '
               'data): motor SQ cage induction 270 kW, 1488 RPM synchronous, 3.3 kV; gearbox bevel-helical B3-355, nominal '
               '23.2, exact 23.5, mechanical 385 kW, thermal 424 kW, fan YES, holdback YES, make PREMIUM; H.S. scoop coupling '
               "PST-500 (M107 prints 'PST - 500' with spaces), 275 kW at 1500 RPM (make row prints PREMLUM, sic); L.S. geared RG-10, 1150 HP/100 RPM, make GBM; brake AC "
               "electro-hydraulic thruster, 290 kg-m, size EBTM-500/F (M107 prints 'EBTM-500 / F' with spaces), drum 500.0; brake make row prints ELEKCTROMAG (sic, KC). Schedule prints PST-500 while GA-10 "
               'prints PST-530; both readings preserved, top-model Q2 retain_disagreement (deciding record: approved Premium scoop-coupling GA with per-conveyor tag allocation or EBA-10 as-built nameplate).')
    ops = [note(ent('EAC-9'), sched9, BASIS_C9D + ' EAC-9 group ratings.', ['ev_fac9fa4f3', 'ev_520f37b37']),
           note(ent('EBA-10'), sched10, BASIS_C9D + ' EBA-10 group ratings.', ['ev_fac9fa4f3', 'ev_520f37b37']),
           note(ent('EAC-9 low-speed coupling'),
                 'Schedule L.S. row EAC 7/9/11/13 prints geared coupling RG-13 (2793 HP/100 RPM, GBM); GA-9 schedule block '
                 'prints RG-12 (GBM). Both preserved; top-model Q1 retain_disagreement, deciding record as above.', BASIS_C9D, ['ev_fac9fa4f3']),
           note(ent('EBA-10 scoop fluid coupling'),
                 'Schedule H.S. row EAC 8/10/12/14 prints scoop coupling PST-500 (275 kW at 1500 RPM, PREMIUM); GA-10 '
                 'schedule block prints PST-530 (PREMIUM). Both preserved; top-model Q2 retain_disagreement, deciding record as above.', BASIS_C9D, ['ev_fac9fa4f3'])]
    return dict(summary='Yard conveyor drive schedule vendor ratings, EAC-9/EBA-10 groups (M107 FIO)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record schedule vendor ratings with GA conflicts preserved',
                    questions=['Which schedule ratings apply to EAC-9/EBA-10?'],
                    reviewed_evidence_ids=[], gaps=['Vendor GA sheets for PST/RG/EBTM models (deciding records for retain_disagreement PD-Q1/PD-Q2).']))


def pkg_c9s():
    brk9 = ('Brake reconciliation EAC 7/9/11/13 group (APPROVED selection): required braking torque 668.3 kg-m; selected '
            'EBTM-500-DS/I, 951.0 kg-m, drum 500.0 (selected exceeds required). Coupling selection same group: H.S. '
            'PST-660 (rating 975 kW at 1500 RPM, drum 500.0), L.S. RG-13 (2793.00 HP/100 RPM, torque 19998 kg-m). Belt '
            'check same group: ST1000, F.S. 6.7, cover FR 8/6, RMBT 149.26 kN/m vs 142.934 required, drive pulley 1000 / '
            'non-drive 800 / snub 630, belt 14.00 mm, 51.60 kg/m; T1S 64244.00 lb / 285866.53 N. Cross-document spreads preserved '
            '(not resolved): required braking torque M052 668.3 kg-m vs live M008 1.73 kgf-m; belt mass M052 51.60 kg/m vs M008 31.93 kg/m.')
    brk10 = ('Brake reconciliation EBA 8/10/12/14 group (APPROVED selection): required 265.4 kg-m; selected EBTM-500/F, '
             '290.0 kg-m, drum 500.0 (selected exceeds required). Coupling selection same group: H.S. PST-500 (275 kW), '
             'L.S. RG-10 (1150 HP/100 RPM, torque 8289 kg-m, max bore 240/min 110). Belt check same group: N/N HD 1250/4, '
             'cover FR 5/2, RMBT 125.00 kN/m vs 104.457 required, T1 27293 lb / 121445.66 N, T1S 32865 lb / 146239.39 N, '
             'BW 1400, mass 37.40 kg/m. Cross-document spreads preserved (not resolved): required braking torque M052 265.4 kg-m '
             'vs live M008 231.15 kgf-m; belt mass M052 37.40 kg/m vs M008 15.98 kg/m.')
    ops = [note(ent('EAC-9 service thruster brake'), brk9, BASIS_C9S + ' EAC-9 brake/coupling/belt selection.',
                ['ev_e4150068d', 'ev_61eac3afa', 'ev_a67e3da13']),
           note(ent('EBA-10 service thruster brake'), brk10, BASIS_C9S + ' EBA-10 brake/coupling/belt selection.',
                ['ev_e4150068d', 'ev_61eac3afa', 'ev_a67e3da13'])]
    return dict(summary='Brake/coupling/belt selection reconciliation, EAC-9/EBA-10 groups (M052 APPROVED)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record required-vs-selected brake reconciliation',
                    questions=['Do selected brakes/couplings/belts cover requirements?'],
                    reviewed_evidence_ids=[], gaps=['None for selection; GA-vs-schedule model letters adjudicated retain_disagreement (Q1/Q2).']))


def pkg_c9p():
    pul9 = ('Pulley calculation inputs EAC 7/9/11/13 family (APPROVED): head pulley 20DR3, 1000 dia / 2200 face / 2700 '
            'bearing CRS; family row HEAD T1s 65143 lb / 289842 N, resultant 437465.81 N; tail 22152 lb / 98572 N; '
            'take-up 19550 lb / 86994 N; bend and snub rows as tabled. Starting-tension 3-way spread preserved: GA-9 284.610 kN '
            'vs M052 285866.53 N (64244.00 lb) vs pulley calc 289842 N (65143 lb). Dimensions agree with GA-9 table (1000/2200/2700 '
            'head, 800/2200/2700 tail/take-up/bend, 630 snub, 219 deflector/hold-down). Bearing/shaft selections on later '
            'calculation pages remain unopened.')
    pul10 = ('Pulley calculation inputs EBA 8/10/12/14 family (APPROVED): head pulley family row HEAD T1s 32865 lb / '
             '146243 N, resultant 221498.05 N; tail 12261 lb / 54559 N; snub 9945.23 lb / 44254 N. Starting-tension 3-way spread '
             'preserved: GA-10 146.191 kN vs M052 146239.39 N (32865 lb) vs pulley calc 146243 N (32865 lb). Dimensions agree with '
             'GA-10 table (800/1600/2100 head, 630/1600/2100 tail/take-up, 219 deflector/hold-down). Bearing/shaft '
             'selections on later pages remain unopened.')
    ops = [note(ent('EAC-9 head drive pulley'), pul9, BASIS_C9P + ' EAC-9 pulley inputs.',
                ['ev_0b0c5aa34', 'ev_2f9d8d8a6', 'ev_786de325a']),
           note(ent('EBA-10 head drive pulley'), pul10, BASIS_C9P + ' EBA-10 pulley inputs.',
                ['ev_0b0c5aa34', 'ev_2f9d8d8a6', 'ev_786de325a'])]
    return dict(summary='Pulley calculation T1s inputs and dimension confirmation (pulley calc APPROVED)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record pulley calc inputs vs GA tables',
                    questions=['Do calc inputs match GA pulley tables?'],
                    reviewed_evidence_ids=[], gaps=['Bearing/shaft/shell pages unopened; T1S three-way spread recorded above.']))


def pkg_c9g9():
    idlers = ('Idler row-level BOM EAC-9 as printed on GA-9 schedule (verified against sheet render): transition 3 equal-roll '
              '5/10/15/25/30deg trough dia-159mm tube (2deg tilt), QTY 5deg=2, 10deg=2, 15deg=2, 20deg=1, 25deg=3, 30deg=2 nos; '
              'impact/transition 3 equal-roll 15/20deg trough dia-139.7mm tube 190.0 O/D (2deg tilt), QTY 15deg=3 and 20deg=3 nos; '
              'impact 3 equal-roll 35deg trough dia-139.7mm tube 190.0 O/D at 400mm pitch, QTY 6 nos; carrying 3 equal-roll '
              '35deg trough dia-159mm tube at 1000/1000mm pitch with 2deg forward tilt, QTY 855 nos; self-aligning carrying '
              '10deg trough dia-159mm tube at 15000mm pitch, QTY 62 nos; self-cleaning return on return belt near discharge '
              'pulley, QTY 1 no; return 10deg trough dia-159mm tube at 3000mm pitch, QTY 255 nos; S.A. return 10deg trough '
              'dia-159mm tube at 18000mm pitch, QTY 43 nos; flat single roller near tail end, QTY 2 nos. Endless 1850m.')
    takeup = ('Take-up detail EAC-9 as printed: head-end HGTU at UAX-2; trolley travel 3300 MM (delta-2 revision); rope 32 DIA '
              '6x37 construction CF grade 1570, minimum breaking force 474 kN, sheave dia 700 mm CI Gr-25; cast-iron design '
              'counterweight 17000 kg per conveyor (300x260x30 = 17.5 kg each, QTY 972 nos). Take-up/HGTU tower steel, '
              'platform and sheave arrangement drawn on sheet 4 mid/bottom views; member sizes not transcribed (gap).')
    civil = ('Chute/skirt/foundation EAC-9 as printed: skirt 15 MTRS 20 THK Hardox 400 with top cover 10 THK Hardox 400 per '
             'conveyor; deck 3.15 THK continuous (delta-2); seal row dash (no seal); chute plate 10 MM Hardox 400 non-impact '
             'sides, 20 MM impact sides. Foundation load per base plate: dead 0.5/0.75 kN, live 0.65/0.65 kN; horizontal '
             'shear and belt-pull rows dash (explicitly no load); material density 1.1 t/cum; loads exclude impact/dynamic '
             'factor. Sheet-1 notes 18-19 refer head/tail short-post loads out to UAX-1 175049 and UEE-6 175038 drawings; '
             'LOCATION BETWEEN UEF-5 TO UAX-2.')
    ops = [note(ent('EAC-9 idler and belt-support assembly'), idlers, BASIS_C9G + ' EAC-9 idler rows.',
                ['ev_c30eea00d']),
           note(ent('EAC-9 conveyor belting'),
                "GA-9 belt row prints 'ST 1000 WITH REP PROTECTION (sic, REP for RIP), 2000MM BW' (triangle-1 row).",
                BASIS_C9G + ' EAC-9 belt verbatim.', ['ev_c30eea00d']),
           note(ent('EAC-9 horizontal gravity take-up assembly'), takeup, BASIS_C9G + ' EAC-9 take-up.',
                ['ev_c30eea00d']),
           note(ent('EAC-9'), civil, BASIS_C9G + ' EAC-9 chute/skirt/foundation.',
                ['ev_c30eea00d', 'ev_b80029a5d']),
           gap(ent('EAC-9'),
               'Head-frame, tail-frame short-post loads and HGTU-tower/gallery member sizes: GA-9 notes 18-19 refer out to '
               'UAX-1 (175049-ISG-0) and UEE-6 (175038-ISG-0) GA & mechanical-load drawings. Deciding records: those two '
               'referenced drawings plus fabrication steel. Not field-verified.',
               BASIS_C9G + ' Referred-out civil detail.', ['ev_b80029a5d'])]
    return dict(summary='Conveyor-9 depth: idler rows, take-up, chute/skirt/foundation, referred-out frames (GA-9)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record GA-9 depth rows and civil gaps',
                    questions=['Which idler/takeup/foundation rows are printed?'],
                    reviewed_evidence_ids=[], gaps=['UAX-1/UEE-6 referenced drawings; tower/gallery steel.']))


def pkg_c9g10():
    idlers = ('Idler row-level BOM EBA-10 as printed on GA-10 schedule (verified against sheet render): transition 3 '
              'equal-roll 15deg/25deg trough dia-159mm tube QTY 2+2 nos; carrying 3 equal-roll 35deg trough dia-159mm tube at '
              '1000/1000mm pitch with 2deg forward tilt QTY 847 nos; self-aligning carrying 10deg trough dia-159mm tube at '
              '15000mm pitch QTY 61 nos; self-cleaning return on return belt near discharge pulley QTY 1 no; return 10deg '
              'trough dia-159mm tube at 3000mm pitch QTY 260 nos; S.A. return 10deg trough dia-159mm tube at 18000mm pitch '
              'QTY 51 nos; flat single roller near tail end QTY 2 nos. C/C horizontal 903.345m; profile 903.755m; lift 8.3m; '
              'endless 1820m.')
    takeup = ('Take-up detail EBA-10 as printed: tail-end HGTU at UAX-6; trolley travel 23000 MM as printed (not '
              'normalised); rope 24 DIA 6x37 CF grade 1570, minimum braking force 267 kN, sheave dia 550 mm CI Gr-25 '
              '(delta-2); cast-iron design counterweight 21000 kg per conveyor (300x260x30 = 17.5 kg each, QTY 1200 nos).')
    civil = ('Chute/skirt/foundation EBA-10 as printed: skirt row dash (explicitly none, vs 15 MTRS on EAC-9); deck 3.15 THK '
             'continuous (delta-2); seal 31.5 THK seal plate continuous for conveyor, gallery and elevated walkway (delta-2, '
             'as printed, likely 3.15 typo, preserved verbatim); chute plate 10 MM non-impact / 20 MM impact Hardox 400. '
             'Hold-down roller 219 DIA x 2200 FACE WIDTH QTY 1 NO per conveyor (delta-2) on 1400 MM BW while all other '
             'EBA-10 pulleys are 1600 face, preserved verbatim. Sheet-1 note 18 refers head/chute loads out to UEE-11 '
             '175044-ISG-0 drawing; UEE-11 is a copied sheet-1 template note whereas GA-10 places EBA-10 between UAX-6 and UEF-10.')
    ops = [note(ent('EBA-10 idler and belt-support assembly'), idlers, BASIS_C10G + ' EBA-10 idler rows.',
                ['ev_519e13410']),
           note(ent('EBA-10 horizontal gravity take-up assembly'), takeup, BASIS_C10G + ' EBA-10 take-up.',
                ['ev_519e13410']),
           note(ent('EBA-10'), civil, BASIS_C10G + ' EBA-10 chute/skirt/foundation.',
                ['ev_519e13410', 'ev_dc8750229']),
           gap(ent('EBA-10'),
               'Head-frame, chute and gallery-steel member loads: GA-10 note 18 refers out to UEE-11 (175044-ISG-0) GA & '
               'mechanical-load drawing. Deciding records: that referenced drawing plus fabrication steel. Not field-verified.',
               BASIS_C10G + ' Referred-out civil detail.', ['ev_dc8750229'])]
    return dict(summary='Conveyor-10 depth: idler rows, take-up, chute/skirt/foundation, referred-out frames (GA-10)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record GA-10 depth rows and civil gaps',
                    questions=['Which idler/takeup/foundation rows are printed?'],
                    reviewed_evidence_ids=[], gaps=['UEE-11 referenced drawing; gallery steel.']))


def pkg_c9x():
    zss = ('Zero-speed protection vendor package (conveyor PCS/BSS/ZSS datasheet, APPROVED): electronic speed switch '
           'Jayashree RME211-NTD-CA-11-B60-ER; monitoring unit cast aluminium IP65 with acrylic window; supply 110V and '
           '240V AC +/-10%, 50 Hz +/-5%; output contacts 1 NO + 1 NC, 10 A resistive at 240V AC; time-setting knob NTD '
           '(VIEW-X); probe M60x1.5P x 65L nickel-plated brass tube, 12V DC, IP67, sensing distance 30 mm +/-10% nominal / '
           '18 mm +/-10% effective, 18 mm +/-10% sensing gap. Terminal diagram 10V/240VAC (sic as printed, vs 110V and 240V AC supply row) + RBG from probe.')
    pcs = ('Pull-cord protection vendor package (same datasheet): pull-cord switch addressable type Jayashree SW-4030HAS122; '
           'die-cast aluminium enclosure IP66; actuation 1-0 bidirectional by pull rope, manual reset with red indication; '
           'normal-action limit switch, contact combination 2 NO + 2 NC; rating 5 A resistive at 240V AC; sensor module '
           'BW-7011C; modules connect to group control panel through a pair of wires with display on the panel.')
    bss = ('Belt-sway protection vendor package (same datasheet): belt-sway switch addressable type Jayashree SW-4021HS122; '
           'die-cast aluminium IP66; self-reset action; plastic roller with stainless sleeve; two cams: CAM-1 10deg from '
           'normal, CAM-2 20deg from normal; contact combination 2 NO + 2 NC (1 NO + 1 NC per cam); rating 5 A resistive at '
           '240V AC 50 Hz; sensor module BW-7011C; GCP pair-of-wires connection with display. Per-conveyor GCP allocation '
           'sheets (pp7-25) remain unopened; actuation thresholds above are vendor type ratings, not commissioned set points.')
    ops = [note(ent('EAC-9 PCS BSS and ZSS protection group'), zss + ' ' + pcs + ' ' + bss,
                BASIS_PCS + ' Conveyor protection vendor settings (EAC-9 lane).',
                ['ev_9237e2425c', 'ev_287fcaafaf', 'ev_b7bbf13275']),
           note(ent('EBA-10 PCS BSS and ZSS protection group'), zss + ' ' + pcs + ' ' + bss,
                BASIS_PCS + ' Conveyor protection vendor settings (EBA-10 lane).',
                ['ev_9237e2425c', 'ev_287fcaafaf', 'ev_b7bbf13275'])]
    return dict(summary='Conveyor protection vendor settings: ZSS/PCS/BSS models, contacts, thresholds (178803)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record protection vendor numeric settings',
                    questions=['Which switch models, contacts and actuation values apply?'],
                    reviewed_evidence_ids=[], gaps=['Per-conveyor GCP allocation sheets pp7-25; commissioned set points.']))


def pkg_stkb():
    detail = ('Stacker family detail beyond Tier-1 (BOD 175249, applies to EAD-2 as family design): design wind 16 m/s '
              'operating, 35 m/s clamped inside shed, 73 m/s anchored three-second gust; travel/slew drives suitable for '
              '150 starts/hr with continuous reversals; self-lubricating bearing minimum life 25 years at 10 hrs/day; '
              'seismic loads per Bangladesh National Building Code-2012 Part 6 Chapter 2.4; walkway 800 mm clear, '
              'maintenance 1.5 m, interference 1.0 m, headroom 2100 mm; stacking chute 20 mm Hardox 400 three sides / '
              '10 mm non-sliding; deflection limits L/180, L/360, H/300. Per-unit commissioned values not verified.')
    ops = [note(ent('EAD-2'), detail, BASIS_STKB + ' Stacker family detail.',
                ['ev_fa22bd9e0', 'ev_1e528a219', 'ev_9a6d95aa8', 'ev_50fb6dbde']),
           gap(ent('EAD-2'),
               'Vendor drive internals below assembly (motor frames/bearings, gearbox tooth/bearing/seal rows, coupling '
               'elements, brake shoe/spring/thruster models), protection numeric pickups/delays, PLC/collision/travel-limit/'
               'storm-parking logic, commissioned speeds/pressures and per-unit serials: BOD/GA assert family design only. '
               'Deciding records (in corpus, unopened): boom drive assembly 42pp, brakes 17pp, fluid couplings 7pp, long '
               'travel 8pp, slewing 3pp, gearboxes 173pp, hydraulic powerpack/cylinder 18pp + P&I 101pp, luffing cylinder 1p, '
               'power calc 61pp, storm anchor 4pp, boom conveyor 3pp, tripper 4pp, QAP fluid 8pp + gearbox 11pp, wind calc '
               '17pp, central lube and storm/chain docs. Machine lube (central grease, chain oil) with Yard-2 applicability '
               'likewise unverified. Not field-verified.',
               BASIS_STKB + ' Vendor internals and settings deferred by name.', ['ev_fa22bd9e0'])]
    return dict(summary='Stacker family detail + vendor internals gap, EAD-2 (BOD 175249)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record stacker family detail, defer vendor internals by name',
                    questions=['Which family design values apply to EAD-2?'],
                    reviewed_evidence_ids=[], gaps=['Vendor drive/lube/PLC docs listed above; commissioned values.']))


def pkg_stkg():
    replies = ('Stacker GA compliance replies (175126, apply to EAD-2 as family design): boom belt speed instruction 3.6 m/s '
               '(BHEL to revise); carrying idler spacing not more than 1000 mm, return idlers 3000 mm, tripper idlers max '
               '1 m (revised); operator cabin forward of boom discharge with zoom camera top of cab above and below boom '
               '(views J/K-K); slew plan clear space 1000 mm, counterweight lowest clearance not less than 2100 mm, return '
               'idler 200 mm from walkway overhaulable; storm reply: wind above 20 m/s travel to boom anchoring position, '
               'hurricane warning drive in advance, single-side boom anchor claimed no problem with other side affecting '
               'reclaimer travel; luffing stacking chute omitted for head weight, pile shape by belt-speed calculation. '
               'Per-unit alignment not verified.')
    ops = [note(ent('EAD-2'), replies, BASIS_STKG + ' Stacker GA replies.',
                ['ev_1c33b8a55', 'ev_341916ae4'])]
    return dict(summary='Stacker GA compliance replies, EAD-2 family (GA 175126)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record GA reply detail',
                    questions=['Which GA replies refine the stacker design?'],
                    reviewed_evidence_ids=[], gaps=['Per-unit alignment; GA drawing sheets image-only.']))


def pkg_recg():
    mech = ('Reclaimer family mechanical detail beyond Tier-1 (GA 175127, applies to EAF-2): take-up hydraulic assisted, '
            'stroke main 500 mm / aux 400 mm; drive sprocket main dia 1618 mm 10 teeth / aux dia 1294 mm 10 teeth, disc hub '
            'E350BR, teeth segmented 42CrMo4; blade E350BR with Hardox 400 lip/tooth; yard-conveyor idlers dia 159 mm ERW and '
            'dia 190 mm with rubber ring, 35deg trough, spacing 400 as printed, deep-groove ball bearing size 25 mm (6205), '
            'shell 4.5 mm, roller EN9/C45, bush 16MnCr5, MOC main E350BR / secondary E250BR and E250A.')
    travel = ('Reclaimer family travel detail (same GA): hydraulic rail clamp 2 nos x 10 ton + manual one on each side; '
              'spring buffers 8 nos (4 pendulum + 4 fixed), stroke approx 210 mm; long-travel VVVF drives per BOD; storm-lock '
              'pin elevations in views C-C/B-B; cable guide 800 mm from rail centre with 300 mm clear gap; power lift ahead '
              'of guide roller and control lift behind. Clamp pressures and buffer test values not stated.')
    reels = ('Reclaimer family reel/lube detail (same GA): power cable reel 1 unit mono-spiral electromechanical 7.5 kW, VFD '
             'speed 150-1500 rpm with inbuilt brake; control cable reel 1 unit mono-spiral 3.7 kW; automatic grease '
             'centralized 1 no (fixed/pendulum travel wheels, guide wheels, scraper boom plummer blocks) with grease motor '
             '1x0.37 kW 1500 rpm squirrel; automatic oil for chains (main and aux) with oil motor 1x0.37 kW. Feeder/starter/'
             'VFD tag mapping and commissioned lube rates not stated.')
    mass = ('Reclaimer family mass/liner note (same GA): total weight approx 417 T; drag-trough liner 12 mm Hardox 400 '
            'minimum 300 BHN; skirt/discharge 12 mm Hardox 400; maximum dead stock 5%; gearbox and brake factor of safety '
            'minimum 1.5; brake torque 37 Nm / torque 292 Nm as tabled (placement ambiguous in extraction). Onboard DSS '
            'boundary approx 6 nozzles at 2 LPM with 2.2 kW (BOD pump schedule governs: PRP-1A 0.55 kW tentative).')
    ops = [note(ent('EAF-2 Main scraper boom'), mech, BASIS_RECG + ' Scraper chain detail.',
                ['ev_5fbf5a22f', 'ev_81c9bb85a', 'ev_811408f24']),
           note(ent('EAF-2 Travel system'), travel, BASIS_RECG + ' Clamp/buffer detail.',
                ['ev_5fbf5a22f', 'ev_c3efbcbae', 'ev_c1bfd9ca0']),
           note(ent('EAF-2 Power cable reel'), reels, BASIS_RECG + ' Reel/lube detail.',
                ['ev_5fbf5a22f', 'ev_82e6475ce']),
           note(ent('EAF-2'), mass, BASIS_RECG + ' Mass/liner note.',
                ['ev_5fbf5a22f', 'ev_0a5f6ad13'])]
    return dict(summary='Reclaimer family mechanical detail: chain/takeup, clamp/buffer, reels/lube, mass (GA 175127)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record reclaimer family detail below Tier-1 assemblies',
                    questions=['Which chain/takeup/clamp/reel/lube values apply as family design?'],
                    reviewed_evidence_ids=[], gaps=['Per-unit serials/settings; feeder/VFD tags; lube rates.']))


def pkg_recb():
    loads = ('Reclaimer family structural/load design (BOD 175119, applies to EAF-2): wind operating 16 m/s 0.16 kN/m2, '
             'non-operating 35.00 m/s 0.77, high wind 73 m/s 3.3 (detailed 76.6/333.1 kg/m2); rail gauge 55.800 m, '
             'rail-to-yard-conveyor 58.000 m, 22 wheels total (A1 6 + A2 8 fixed, B1 4 + B2 4 pendulum) with 12 drives at '
             '5.5 kW vs GA 14 wheels/8 driven (both readings preserved); load groups ML 554 kg/m at 1375 t/h, INC 10%, '
             'drag/return/linear combinations as tabled; chain tensions main T1 262.3/T2 32.9/T3 10.1/T4 10.1 kN, aux '
             '107.7/31.4/2.8/2.8 kN; crane/buffer/earthquake factors as tabled. Structural pressures are not trip settings.')
    speed = ('Reclaimer family speed/capacity notes (same BOD vs GA, both preserved): travel 2 m/min reclaiming and 5 m/min '
             'relocation with 20 m/min max vs GA 2-8 m/min operating + relocation 20 max (stability note retains 2 and 5); '
             'aux capacity 500-650 t/h depending on boom inclination vs GA 500-660 TPH; GA wind rows print 16 km/h operating '
             'and 73 km/h non-operating vs BOD m/s (unit conflict already recorded on EAF-2). No commissioned speed or trip '
             'inferred.')
    ops = [note(ent('EAF-2'), loads, BASIS_RECB + ' Structural/load design.',
                ['ev_0500740f2', 'ev_93916ae52', 'ev_0baf282cd', 'ev_27ceb574a', 'ev_1839b77df']),
           note(ent('EAF-2'), speed, BASIS_RECB + ' Speed/capacity notes.',
                ['ev_93916ae52', 'ev_4606e4906']),
           gap(ent('EAF-2'),
               'Vendor drive internals below assembly (reducer bearing lists, brake selections, coupling models), protection '
               'numeric settings, cable-reel feeder/starter/VFD mapping, safety-instrument 179103 loops, wind-trip '
               'reconciliation, lube/DSS/fire commissioned settings and per-unit serials: GA/BOD assert family design only. '
               'Deciding records (in corpus, unopened): long travel 12pp, brakes 3pp, couplings 10pp, gearboxes 5pp, rail '
               'clamps 2pp, storm anchor 1p, main/aux hoisting 4pp, boom hoist drive 1p, drive selection 5pp, central lube '
               '13pp, wind calc 13pp, stability 36pp, blade/scraper 175129, philosophy 179109, safety-instrument 179103 '
               'sheets, cable-reel/VFD schedule, PLC/collision manual. Machine lube (central grease, chain oil) with Yard-2 '
               'applicability likewise unverified. Not field-verified.',
               BASIS_RECB + ' Vendor internals and settings deferred by name.', ['ev_77476eda2'])]
    return dict(summary='Reclaimer family loads + vendor internals gap, EAF-2 (BOD 175119)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record reclaimer load design, defer vendor internals by name',
                    questions=['Which load/wind/geometry values apply as family design?'],
                    reviewed_evidence_ids=[], gaps=['Vendor drive/lube/PLC/safety docs listed above; commissioned values.']))


def pkg_dsss():
    design = ('Stacker onboard DSS coal design (DBR M206, EAD-2 family): 34 nozzles installed and operating simultaneously, '
              '2 LPM each at 5 bar inlet (5 kg/cm2); 3 header sets; pumps 1 working + 1 standby for one coal stacker (8 nos '
              'for 4 machines), pump duty 4.9 m3/hr at 85 m, tentative motor 3 kW at 2900 rpm; pipe velocity 1.8 m/s below '
              '50NB, 2.4 m/s at/above 50NB, SS304 pipe/fittings; maximum elevation 15 m; motor starter cum local control '
              'panel by CZMC scope.')
    skid = ('Stacker onboard DSS skid/tank (same DBR): pump skid with drive motor, suction duplex filter with differential-'
            'pressure indicating switch, isolation/throttling/non-return valves, pressure switch, relief valve, gauges, '
            'differential gauge; tangential circle-jet nozzles; dedicated SS water tank with level switch, float valve and '
            'isolation valves, 1-hour storage 10 m3 SS304 tank; hose reel and water pipelines from skid to nozzles. Control '
            'voltage 230V AC (item 19). Duplex-filter wording vs simplex-choked alarm line both preserved verbatim; '
            'reconciliation already gapped on this entity.')
    sets = ('Stacker onboard DSS design set points (same DBR, not commissioned): DP across filter below 0.2 bar g; pump '
            'continues if discharge pressure exceeds pressure-switch low set point within one minute of starting, else trip; '
            'trip on low discharge pressure during normal operation and on tank level below low set point for more than 3 '
            'minutes; alarms for tank high/low/low-low, pump discharge low, simplex filter choked (verbatim) and motor trip; '
            'relief recirculates to tank; manual/remote through CZMC DCS/PLC. Skid serials and commissioned values pending.')
    ops = [note(ent('EAD-2 Onboard plain-water DSS'), design, BASIS_DSSS + ' Nozzle/pump design.',
                ['ev_0c406e885d', 'ev_49e2079cc', 'ev_612ebbfc6']),
           note(ent('EAD-2 Onboard plain-water DSS'), skid, BASIS_DSSS + ' Skid/tank/voltage.',
                ['ev_b166e6fc8', 'ev_ab5013416']),
           note(ent('EAD-2 Onboard plain-water DSS'), sets, BASIS_DSSS + ' Design set points.',
                ['ev_ab5013416', 'ev_c2d3e8b34'])]
    return dict(summary='Stacker onboard DSS pump/nozzle/tank/setpoints, EAD-2 family (DBR M206)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record onboard DSS internals',
                    questions=['Which pump/nozzle/tank/setpoint values apply?'],
                    reviewed_evidence_ids=[], gaps=['Commissioned set points; skid serials; duplex/simplex (gapped).']))


def pkg_dssr():
    sched = ('Reclaimer onboard DSS pump schedule (BOD M150, EAF-2 family): PRP-1A 1.0 m3/hr, 45 mwc minimum, 1 no (1W+0S) '
             'per reclaimer; motor 0.55 kW at 2900 rpm, tentative subject to final vendor selection; vertical multistage '
             'centrifugal pump. Water calc: 6 nozzles at 2 LPM tip 3 bar = 12.00 lpm = 0.72 m3/hr +10% = 0.79, selected 1.00 '
             'm3/hr; head total 40.15 mWC +10% = 44.2, selected 45 mWC minimum; motor table 41% efficiency, 0.30 kW shaft '
             '+20% = 0.359, selected 0.55 kW at 2900 rpm.')
    arr = ('Reclaimer onboard DSS arrangement (same BOD): pumps 1 working + 0 standby draw from 2000 L SS tank on the mobile '
           'reclaimer platform (2 hours storage) to mist-type nozzles through solenoid boxes; onboard manual hose-reeling '
           'drum with 32NB x 50 m flexible hose and quick-release coupling for tank filling from 32NB tap points with QRC; '
           'normally-open inlet solenoid valve; level switch for interlocking/monitoring from CHP PLC (close on high, '
           'interlock against dry running on low); recirculation line with globe valve and pressure-relief valve; compound '
           'gauge at suction, pressure gauge at discharge with pressure switch. Control voltage 230V AC per this BOD.')
    volt = ('Control-voltage wording conflict (preserved, not resolved): this BOD prints 230V AC control voltage with '
            'solenoid coil 230V AC; the reclaimer DSS P&ID (175151) note 3 prints SOLENOID VALVE COIL VOLTAGE SHALL BE 240V '
            'AC. Stacker DSS design item 19 likewise prints 230V AC. No commissioned voltage asserted.')
    ops = [note(ent('EAF-2 Onboard plain-water DSS'), sched, BASIS_DSSR + ' Pump schedule/calc.',
                ['ev_854e1a0a9', 'ev_af622048f', 'ev_43c24e201', 'ev_15d5906ce']),
           note(ent('EAF-2 Onboard plain-water DSS'), arr, BASIS_DSSR + ' Arrangement/tank-fill.',
                ['ev_4d8973112']),
           disc(ent('EAF-2 Onboard plain-water DSS'), volt, BASIS_DSSR + ' Voltage wording.',
                ['ev_29437cbfb'])]
    return dict(summary='Reclaimer onboard DSS pump/tank/voltage, EAF-2 family (BOD M150)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record onboard DSS internals with voltage conflict',
                    questions=['Which pump/tank/voltage values apply?'],
                    reviewed_evidence_ids=[], gaps=['Commissioned set points; skid serials; P&ID 240V leg in dss-p.']))


def pkg_dssp():
    chart = ('Reclaimer DSS application-point chart (P&ID 175151, EAF-2 family): AP-1 conveyor receipt 1400BW 1375TPH, '
             '6/6 nozzles operating, 2 LPM at 3 bar each, 12 LPM total, 20NB line, solenoid box SB20-PRM1; pump schedule '
             '1 no (1W) 1.0 Cu.m/hr at 45 M.WG, vertical centrifugal multistage, motor 0.55 kW 2-pole tentative; manual hose '
             'reel drum with 32NB 50 m hose and 32NB quick-release coupler; SS tank 2 CUM; piping screwed stainless steel, '
             'routing tentative.')
    logic = ('Reclaimer DSS control logic (same P&ID, not commissioned): 1 no (1W) centrifugal pump PRP-1 with low-level '
             'switch against dry running; tank inlet solenoid normally-open type closes on high level (HL); 2/2 normally-'
             'closed solenoid valves with WATER PRESSURE HEALTHY and PORTAL MACHINE MAIN CHAIN CONVEYOR ON permissives; '
             'note 3 prints SOLENOID VALVE COIL VOLTAGE SHALL BE 240V AC (vs BOD 230V AC, both preserved); control 230V AC '
             '1-phase and 3-phase 415V AC +/-5% 50 Hz supply as printed.')
    ops = [note(ent('EAF-2 Onboard plain-water DSS'), chart, BASIS_DSSP + ' Application chart.',
                ['ev_f1631ced7', 'ev_206382b3c']),
           note(ent('EAF-2 Onboard plain-water DSS'), logic, BASIS_DSSP + ' Control logic/voltage.',
                ['ev_f3574496f', 'ev_1e846943b'])]
    return dict(summary='Reclaimer DSS application chart and control logic (P&ID 175151 FIO)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record P&ID application/control detail',
                    questions=['Which application points, logic and voltages are drawn?'],
                    reviewed_evidence_ids=[], gaps=['Installed routing; commissioned logic.']))


def pkg_firs():
    scope = ('Stacker fire detection/suppression package record (FIO vendor supply/design only): datasheet + BOM for FDA '
             'system of stacker, Hunan Changzhong, KKS MAITREE-00-EAD-DA-179063-ISG (EAD family prefix, no numbered unit); '
             "cover index row 3 prints 'SCHERMATIC' (sic); customer block prints 'BANGALADESH' (sic); "
             'status FOR INFORMATION, FIO 14-Nov-2019. No erection, cable-routing, PLC I/O, commissioning, cylinder-serial, '
             'pressure-test or handover record in this 50-page file. No page names EAD-2, EAF-2, reclaimer or a numbered '
             'yard; top-model Q4 confirmed Option b: package stays on the B44 boundary below as an unverified 00-EAD FIO '
             'family proposal, both numbered machines gapped.')
    equip = ('Package equipment types (same file, catalogue/project mix, per-machine counts NOT asserted): extinguishing '
             'cylinders 22L at 25 bar with 11 kg HFC-227ea and 80L at 25 bar with 50 kg HFC-227ea (Minimax MX200; BOM '
             'quantity columns garbled, DesignManager shows 1x80L 49.5 kg + 1x22L 11 kg for the two unnamed enclosures); '
             'Apollo Discovery photo-electric smoke detector 58000-650 and heat detector 58000-450; intelligent sounder '
             '55000-001, visual indicator 55000-009, sounder-visual 55000-005; fire control panel FMZ5000 (up to 4 loops x '
             '126 detectors, 16 control groups, 32 relays); 24V electrical + manual release devices (actuation present '
             'minimum 5 s); DN25 360deg 4-bore nozzles; DN50 manifold/check valve; Sch80 pipe; DMX95 buttons; hand/auto '
             'switch; HZFQ-1 gas-release indicator.')
    calc = ('Package design calculations (same file, unnamed enclosures only): Elecrical_Room / 1 (sic, missing first t in all 4 '
            "occurrences) 10.5x3x2.7 m (85.05 m3, 7.3% "
            'concentration, 48.7 kg, 2x889041 DN25 nozzles at 10.107 bar, 10.0 s) and Driver Room 2.4x1.9x2.5 m (11.4 m3, '
            '6.6 kg, 1x889037 at 14.247 bar, 9.9 s), NFPA 2001 10 s discharge; driver-room height 2.5 m vs live EAD-2 cabin '
            '2.4x1.9x2.4 m (0.1 m mismatch, not equated); pp8-37 Minimax/Apollo/FMZ catalogues and pp44-50 FM/UL listings are '
            'manufacturer-generic, never per-machine existence; From-E-house/To-Operator-Cabin indicates intent, not a '
            'verified interface.')
    ops = [note(ent('Stacker Onboard Fire Detection & Extinguishant System Boundary'), scope,
                BASIS_FIRE + ' Package scope/status.', ['ev_acc765dd2']),
           note(ent('Stacker Onboard Fire Detection & Extinguishant System Boundary'), equip,
                BASIS_FIRE + ' Equipment types.', ['ev_17968e861', 'ev_547fdcee9f', 'ev_ebf82b27d']),
           note(ent('Stacker Onboard Fire Detection & Extinguishant System Boundary'), calc,
                BASIS_FIRE + ' Enclosure calculations.', ['ev_2e8661318', 'ev_642b24ab8', 'ev_d2ceb31e0',
                                                         'ev_2e3cacbdd', 'ev_52ee06e97', 'ev_9c7e7cb0d']),
           gap(ent('EAD-2'),
               'Onboard fire protection per numbered machine: FDA package IS-3-GA-702-108-E1104 REV 02 is an unverified FIO '
               '00-EAD family proposal recorded on ent_1920bc6fa56ce0fde581 (Driver-Room 2.5 m vs live cabin 2.4 m height '
               'mismatch, no numbered unit named, no PLC I/O or commissioning record). Deciding records: approved E1104 '
               'revision, EAD-2 E-house/cabin nameplates or photos showing FMZ5000/Apollo/MX200 fitment, loop drawings, PLC '
               'I/O schedule, commissioning and enclosure-integrity certs. Not field-verified.',
               BASIS_FIRE + ' EAD-2 fire gap.', ['ev_acc765dd2']),
           gap(ent('EAF-2'),
               'Onboard fire detection/suppression for the portal scraper reclaimer: no reclaimer-titled fire document in '
               'sources.json, SOURCE_CATALOG.md or the documents table (22 reclaimer docs are DS/lube/mech/painting only); '
               'the 50-page FDA file is stacker-titled throughout. Deciding records: reclaimer-titled fire datasheet/BOM, '
               'EAF-2 E-house/cabin nameplates or photos showing FMZ5000/Apollo/MX200 fitment, loop drawings, commissioning '
               'and enclosure-integrity certs.',
               BASIS_FIRE + ' Reclaimer fire gap.', ['ev_acc765dd2'])]
    return dict(summary='Stacker FDA package record + reclaimer fire gap (FDA E1104 FIO)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record fire package without binding to numbered machines',
                    questions=['What does the FDA package cover, and what is missing for EAF-2?'],
                    reviewed_evidence_ids=[], gaps=['EAD-2 gap recorded (Q4 confirmed Option b); EAF-2 fire source absent.']))


def pkg_qrcg():
    ops = [gap(ent('Coal Yard 2 SPDS Machine makeup QRC connections'),
               'Per-yard share of the 92 BOM QRC positions and installed routing/hose-connection detail for the EAD-2/EAF-2 '
               'tanks: P&ID BOM item 19 states 92 NOS project-total with note 9 quick-release couplings at 30 m intervals '
               'for stacker/reclaimer makeup; no per-yard split is stated and no as-built routing is in the file. Reclaimer '
               'tank fill is 32NB x 50 m hose + QRC (BOD/P&ID); stacker tank fill is manual hose reel + float valve '
               'description only. Deciding records: as-built QRC routing, per-yard position split, hose-connection '
               'nameplates. Not field-verified.',
               BASIS_QRCP + ' QRC share/routing gap.', ['ev_ac1d949bf', 'ev_ddc8fa0a7'])]
    return dict(summary='QRC per-yard share and installed routing gap (P&ID 175255)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record QRC count-share/routing gap',
                    questions=['What share/routing of the 92 QRCs serves Yard 2?'],
                    reviewed_evidence_ids=[], gaps=['As-built routing; per-yard split.']))


def pkg_apsvg():
    ops = [gap(ent('Coal Yard 2 SPDS sector control group'),
               'Unique AP-29..56 to SV-29..56 cross-reference and surveyed riser coordinates: philosophy sector tables give '
               'the AP range and the S1-S14 SV pairs (with SV-34 KKS garble and SC-04 heading typo preserved) but no '
               'AP-to-SV row mapping; piping layout gives typical riser/QRC/sprinkler details with pipe-support notes but no '
               'AP/SV numbers or survey coordinates. Deciding records: riser/pedestal survey with CL/coordinate table, '
               'per-riser valve/nozzle tag schedule linking each AP to its SV, globe/gate tags and sprinkler make/model. '
               'Not field-verified.',
               BASIS_PHIL + ' AP-SV/coordinate gap.', ['ev_98b4d1715', 'ev_de83121d8'])]
    return dict(summary='AP-SV cross-reference and riser coordinate gap (philosophy 175319)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record AP-SV/coordinate gap',
                    questions=['Is there a unique AP-SV table or surveyed coordinates?'],
                    reviewed_evidence_ids=[], gaps=['Surveyed CL/coordinate table; per-riser tag schedule.']))


PACKAGES = [(DOC_C9D, pkg_c9d, 'c9d', 755), (DOC_C9S, pkg_c9s, 'c9s', 756),
            (DOC_C9P, pkg_c9p, 'c9p', 757), (DOC_C9G, pkg_c9g9, 'c9g9', 758),
            (DOC_C10G, pkg_c9g10, 'c9g10', 759), (DOC_PCS, pkg_c9x, 'c9x', 760),
            (DOC_STKB, pkg_stkb, 'stkb', 761), (DOC_STKG, pkg_stkg, 'stkg', 762),
            (DOC_RECG, pkg_recg, 'recg', 763), (DOC_RECB, pkg_recb, 'recb', 764),
            (DOC_DSSS, pkg_dsss, 'dsss', 765), (DOC_DSSR, pkg_dssr, 'dssr', 766),
            (DOC_DSSP, pkg_dssp, 'dssp', 767), (DOC_FIRE, pkg_firs, 'firs', 768),
            (DOC_QRCP, pkg_qrcg, 'qrcg', 769), (DOC_PHIL, pkg_apsvg, 'apsvg', 770)]


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
        assert base_version == 754, base_version
    running = base_version if not args.apply else 754
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
        assert not missing and (changed or len(af) > len(bf)), (missing, changed, len(af) - len(bf))
        print(json.dumps({'applied': True, 'version': after['version'], 'new_assertions': len(af) - len(bf)}))


if __name__ == '__main__':
    main()
