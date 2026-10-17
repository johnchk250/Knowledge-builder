"""Pass-5 local packages (DQ-B20-001/-002, DQ-B21-001/-002, DQ-B22-001..004).

Batched Pass-5 run per PASS_B_TWO_TIER_WORKFLOW.md, modified for this run so the
local tier applies only 100%-confidence work: CERTAIN printed rows become
document_note operations, ABSENT legs become source_gap operations naming the
deciding records. Everything UNCERTAIN (conflicts, illegible digits, unit
clashes, AP/SV mapping wording, filter wording, redesign questions) is deferred
to the Pass-5 top-model review zip. One documentary source per proposal.

Note text is compiled mechanically from the four reviewed findings files under
output/plant-enrichment/pass-05/mine/ (agent-A..D.json) so every asserted row
stays traceable to its evidence id, page region and crop. Chained v770 -> v789.
Default: isolated rehearsal in pass-05/rehearsal-copy; --apply performs guarded
live acceptance after the top-model return is folded in.
"""
import argparse
import json
import re
import shutil
import sqlite3
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-05'
MINE = BASE / 'mine'
COPY = BASE / 'rehearsal-copy'

DOC_A11 = 'doc_9d6657d14f3a4c829469'
DOC_A12 = 'doc_0adf08e6189847b88503'
DOC_STKB = 'doc_78bebe6773984d59b013'
DOC_STKG = 'doc_d69ffd4c7c2241018323'
DOC_RECG = 'doc_3e81ea1c32df4215968d'
DOC_RECB = 'doc_498f70490d294542b8b0'
DOC_FIRE = 'doc_4d488fd685284c408297'
DOC_DSSS = 'doc_0f52c77514a74773ae30'
DOC_DSPK = 'doc_5759a520616e4b588dce'
DOC_DSSR = 'doc_a6a2fa82944f4d12b8aa'
DOC_PUMP = 'doc_9db2601634034197a910'
DOC_FHPID = 'doc_0eeb339e58a24707a475'
DOC_LUBS = 'doc_b7d031cc33c54157ad86'
DOC_LUBR = 'doc_42554b5718fc423997b3'
DOC_PHIL = 'doc_e17edf6897d746fabe12'
DOC_PLAY = 'doc_7244e891263a4e6d8214'
DOC_QRC = 'doc_5a36f2843d504d6e96de'
DOC_DBR3 = 'doc_777d1a06d4fa4e8ba231'
DOC_TRIP = 'doc_2c2568dc7b9e4e509cd6'

ENT_EAC11 = 'ent_067d1133cfb64687acfb'
ENT_EBA12 = 'ent_e0cd946e46264ec89bdc'
ENT_EAC11_MOTOR = 'ent_002127907d8552b73e55'
ENT_EAC11_GEAR = 'ent_bfc48c0fa78afcd604a9'
ENT_EAC11_SCOOP = 'ent_e60a08ba16a36937e930'
ENT_EAC11_LSC = 'ent_f00d5cefed5379babae2'
ENT_EAC11_BRAKE = 'ent_00a38ed2b50c856b6f9d'
ENT_EAC11_BELT = 'ent_02adde69972659d5e7c6'
ENT_EAC11_PULLEY = 'ent_31e5ed043025801300ca'
ENT_EAC11_TAILP = 'ent_471b735e01ae1235bbb5'
ENT_EAC11_IDLER = 'ent_c0679be848713c08efbc'
ENT_EAC11_HGTU = 'ent_ec9c02b33cbae59843c8'
ENT_EAC11_CLEAN = 'ent_9970039e29380aa2a1cc'
ENT_EAC11_PROT = 'ent_529371344280f737371d'
ENT_EBA12_MOTOR = 'ent_7eefc99c6e951e4f661c'
ENT_EBA12_GEAR = 'ent_d68b5fd318ac7664614d'
ENT_EBA12_SCOOP = 'ent_d00bda32856ce8fd5213'
ENT_EBA12_LSC = 'ent_c514ff57be8f18d6c4b6'
ENT_EBA12_BRAKE = 'ent_ee12363c0d70998b21c3'
ENT_EBA12_BELT = 'ent_d4a1dd8e672fd8b59c20'
ENT_EBA12_PULLEY = 'ent_714244ee81e4ef82399d'
ENT_EBA12_TAILP = 'ent_8f56a25d59909591890a'
ENT_EBA12_IDLER = 'ent_0867fb2bdea71ef03f84'
ENT_EBA12_HGTU = 'ent_16ad2236af889e994cac'
ENT_EBA12_CLEAN = 'ent_4a86dbeea6107321bdf5'
ENT_EBA12_PROT = 'ent_1aaa1a99624d03a63162'
ENT_EBA12_CHUTE = 'ent_91d9e54561ca570ca794'

A_MAP_11 = [
    ('cleaner', ENT_EAC11_CLEAN), ('scraper', ENT_EAC11_CLEAN),
    ('protection', ENT_EAC11_PROT),
    ('tension', ENT_EAC11_BELT), ('belt', ENT_EAC11_BELT),
    ('idler', ENT_EAC11_IDLER), ('roller', ENT_EAC11_IDLER), ('deflector', ENT_EAC11_IDLER),
    ('pulley set', ENT_EAC11_PULLEY),
    ('drive motor', ENT_EAC11_MOTOR), ('motor', ENT_EAC11_MOTOR),
    ('main gearbox', ENT_EAC11_GEAR), ('gearbox', ENT_EAC11_GEAR),
    ('high-speed coupling', ENT_EAC11_SCOOP), ('low-speed coupling', ENT_EAC11_LSC),
    ('thruster brake', ENT_EAC11_BRAKE),
    ('take-up', ENT_EAC11_HGTU),
    ('tcs', ENT_EAC11), ('hgtu', ENT_EAC11_HGTU),
    ('foundation', ENT_EAC11), ('revision', ENT_EAC11),
    ('skirt', ENT_EAC11), ('deck', ENT_EAC11), ('chute', ENT_EAC11), ('seal plate', ENT_EAC11),
]
A_MAP_12 = [
    ('cleaner', ENT_EBA12_CLEAN), ('scraper', ENT_EBA12_CLEAN),
    ('protection', ENT_EBA12_PROT),
    ('weigher', 'ent_b8434b359bf7b44dfcfd'),
    ('tension', ENT_EBA12_BELT), ('belt', ENT_EBA12_BELT),
    ('chute', ENT_EBA12_CHUTE), ('skirt', ENT_EBA12_CHUTE), ('deck', ENT_EBA12_CHUTE),
    ('idler', ENT_EBA12_IDLER), ('roller', ENT_EBA12_IDLER), ('deflector', ENT_EBA12_IDLER),
    ('pulley set', ENT_EBA12_PULLEY),
    ('drive motor', ENT_EBA12_MOTOR), ('motor', ENT_EBA12_MOTOR),
    ('main gearbox', ENT_EBA12_GEAR), ('gearbox', ENT_EBA12_GEAR),
    ('high-speed coupling', ENT_EBA12_SCOOP), ('low-speed coupling', ENT_EBA12_LSC),
    ('thruster brake', ENT_EBA12_BRAKE),
    ('take-up', ENT_EBA12_HGTU),
    ('tcs', ENT_EBA12), ('hgtu', ENT_EBA12_HGTU),
    ('foundation', ENT_EBA12), ('revision', ENT_EBA12), ('head frame', ENT_EBA12),
]

BASIS_A11 = ('GA & load data of belt conveyor-11 (EAC-11), BHEL/TCS Yard-3 drawing 175021, 6 sheets '
             '(p1 key plan/notes/referred drawings, p2 key elevation/support details, p3-p4 GAs, p5 characteristics/load/'
             'foundation/HGTU tables, p6 TCS). Depth mining for DQ-B20-001/-002: drive and data-sheet rows, idler/take-up/'
             'civil tables. CERTAIN printed values asserted; absent legs recorded as source_gap; digit-uncertain rows '
             '(pulley BRG CRS, transition angle-set key, PCS pair-unit, notes-18/19 tags) adjudicated in the Pass-5 '
             'top-model review (Q1/Q2: pulley rows keep 2700 BRG .CRS. as governing reading; Notes 18/19 re-read as '
             'UAX-3/UEE-6, prior UAX1/UEF6 note retired). Not field-verified.')
BASIS_A12 = ('GA & load data of belt conveyor-12 (EBA-12), BHEL/TCS Yard-3 drawing 175022, 7 sheets '
             '(p1 key plan + notes, p2 profile, p3-p4 profile/stockpile + portal-reclaimer sheets, p5 characteristics/load/'
             'HGTU tables, p6-p7 TCS). Depth mining for DQ-B20-001/-002. CERTAIN printed values asserted; absent legs as '
             'source_gap; uncertain rows (seal plate 31.5 THK, hold-down 2200 face on 1400 belt, weigher accuracy, HGTU '
             'load-table reading) adjudicated in the Pass-5 top-model review (Q1/Q2 confirmations; weigher (+)25% vs '
             'live 0.25% retained as disagreement). Not field-verified.')
BASIS_STKB = ('Basis of design for coal stacker machine, BHEL IS-4-DB-702-108-M21x (175249) Rev 2, approved '
              '27-Feb-2019; project-family design for four stackers applied to Yard-3 EAD-3. Depth mining DQ-B21-001: '
              'drive internals, motions, wind/starts, tripper, cabin, weigher. Design basis only; commissioned state '
              'unverified. Uncertain rows (slew motor kW vs GA, tie-down both-ends deviation) adjudicated in the Pass-5 '
              'top-model review (Q3/Q4: 22 kW BOD vs 15 kW GA slew power retained as disagreement; tie-down both-ends '
              'deviation retained open).')
BASIS_STKG = ('GA & TDS of stacker machine 175126 Rev 2 (family, four machines), with BIFPCL/BHEL compliance replies; '
              'applied to Yard-3 EAD-3. Depth mining DQ-B21-001: GA TDS motion/drive rows, travel bogie fitments, '
              'protection devices, control mode, storm logic, tripper/cabin rows. GA sheets are image-based; reply text '
              'and TDS rows govern. Uncertain rows (slew angle glyph, boom belt speed 3.5 vs 3.6, moisture 25 vs 24, '
              'stacking digits, tie-down) adjudicated in the Pass-5 top-model review (Q3-Q5: slew range 0~100 deg '
              'confirmed; 3.5 vs 3.6 m/s and 25 vs 24% retained as disagreements; stacking 3400/3740 t/h confirmed).')
BASIS_RECG = ('GA & TDS of portal type scraper reclaimer 175127 Rev 2 (vendor 47039267, TENOVA), approved '
              '23-Nov-2018 with compliance replies pp4-6; project-family design for EAF-1..4 applied to Yard-3 EAF-3. '
              'Depth mining DQ-B21-002: scraper chain/blade rows, take-up and drives, hoist, travel/clamp/buffer, cable '
              'reels, DSS/lube/electrical rows, safety-instrument references. Uncertain rows (aux capacity 660 vs 650, '
              'wind units, hoist gearbox wording, travel speeds band, buffer end-distance digits) adjudicated in the '
              'Pass-5 top-model review (Q6-Q8: aux 660 vs 650 and hoist gearbox wording retained; wind km/h proven a '
              'unit typo with 16/35/73 m/s governing; travel band 2-8 vs 2/5 m/min retained; wheel count corrected to '
              '22 total / 12 driven). Not field-verified.')
BASIS_RECB = ('Basis of design for portal reclaimer 175119 Rev 2 (vendor 47039270, TENOVA POC-705), approved '
              '23-Nov-2018; structural/load and travel-drive design for four reclaimers applied to Yard-3 EAF-3. Depth '
              'mining DQ-B21-002: chain tension design values, rail clamp, buffer effect local check, locking load case. '
              'Structural pressures are not trip settings. Design only; commissioned state unverified.')
BASIS_FIRE3 = ('Datasheet/BOM for FDA system of stacker, drg IS-3-GA-702-108-E1104 REV 02 (vendor Hunan Changzhong; '
               'stacker KKS prefix 00-EAD, no numbered unit), status FOR INFORMATION, FIO 14-Nov-2019. Yard-3 depth: '
               'package identity, protected zones Z101/Z201, NFPA 72 coverage rule, BOM items 1-21. Design-stage vendor '
               'package only; installation/commissioning records absent (source_gap). Not field-verified.')
BASIS_DSSS3 = ('Chemtrols coal stacker plain-water DSS design/control Rev 05, FIO 23-Jan-2021 (DBR M206, doc 175244 '
               'family); coal section only, limestone dry-fog section excluded. Yard-3 depth: 34-nozzle design, AP1-AP5 '
               'distribution, Chemtrols component details. Duplex suction filter confirmed by the Pass-5 top-model '
               'review (Q9: DBR p21/p26 alarm "Duplex filter" plus DF-101/DPS-101 tag); pp23/29 simplex wording '
               'retained for dry-fog/copied alarm-table scope only. Design values only.')
BASIS_DSPK3 = ('P&ID of machine mounted DS system for stacker machine (123-page equipment list/technical specification '
               'package). Yard-3 depth: field-instrument and equipment rows PS-101, DPS-101, tank displacer level switch, '
               'pumps P101/P102, duplex filter DF-101, spray nozzles, hose reel. Design datasheet values only; serials '
               'and commissioned set points absent (source_gap).')
BASIS_DSSR3 = ('F.Harley plain-water DS BOD 47039284 Rev 2 for the portal reclaimer (vendor BOD Rev 2 / customer '
               'MAITREE-00-EAF-DB-175150-ISG-2 issue), approved 19-Aug-2019; applied to Yard-3 EAF-3. Yard-3 depth: '
               'pump schedule PRP-1A, tank/hose arrangement, suction head-loss calculation. Pump motor rating '
               'tentative subject to final vendor selection. Design only.')
BASIS_PUMP3 = ('Datasheet & cross section of pumps for DS system for portal type scraper reclaimer (Grundfos CRN 1-8 '
               'A-FGJ-A-V-HQQV, qty 4), dated 25.09.19; applied to Yard-3 EAF-3. Vendor datasheet values; TAG NO '
               '(as per SLD) field blank and no serial/FAT data (source_gap).')
BASIS_FHPID3 = ('P&ID of machine mounted DS system for portal type scraper reclaimer, vendor F.Harley drg '
                '3778-02-T-01 (title block of sheet 1 prints Rev 1, 21.5.19, sheet 1 of 2 - vendor sheet revision, '
                'distinct from the customer MAITREE-00-EAF-MB-175151-ISG-2 issue), TCS replies to 19-Aug-2019. Yard-3 '
                'depth: pump schedule, TCS outcomes/interlocks, yard-QRC tank-fill configuration. Typical arrangement; '
                'routing tentative.')
BASIS_LUBS3 = ('GA, TDS & P&ID of motorized central lubrication system for stacker machine; p4 KSP8-S pump TDS table, '
               'p11 compliance report (3 x KSP8-65S and mounting locations). Yard-3 depth for EAD-3 central lubrication. '
               'Vendor supply/design only; commissioned lube rates unverified.')
BASIS_LUBR3 = ('GA, TDS & P&ID of motorized central lubrication system for portal type scraper reclaimer; Lincoln '
               'dual-line lubrication system specification and 90-point lubrication schedule. Yard-3 depth for EAF-3 '
               'central lubrication. Vendor supply/design only.')
BASIS_PHIL3 = ('Operation & control philosophy for CHP stockpile DS system and SW/PW pumping system 175319 Rev 5, '
               'approved 26-May-2020, stamped FOR INFORMATION ONLY. Yard-3 depth: stockpile ring headers/sector '
               'control (SC-03/SC-04), AP-57..112 range rows. Design/control arrangement; AP-to-SV unique mapping '
               'absent (source_gap). Printed-tag row adjudicated in the Pass-5 top-model review (Q10: front-page '
               'Stockpile-2 tag retained with conflict note; Sectors 1-14 = 14 per stockpile).')
BASIS_PLAY3 = ('Piping layout for CHP stockpile DS system 175301 (Maitree-00-GAC-BR-175301-ISG-0 Rev 1, FIO '
               '16-Oct-2019). Yard-3 depth: TCS / pedestal-coordinate and routing comments. Surveyed coordinates and '
               'as-built routing absent (source_gap).')
BASIS_QRC3 = ('P&ID for plain-water DS system for stockpile 175255 Rev 2 (BHEL IS-1-PI-702-110-M216 Rev 2, FOR '
              'APPROVAL, FIO 21-Jan-2019). Yard-3 depth: BOM item 19 (92 QRC nos), notes 9/10 (30 m QRC spacing), '
              'pump schedule rows. Drawing-level stockpile-area totals; per-yard split absent (source_gap).')
BASIS_DBR3 = ('Design basis report for plain water DS system for stockpile for CHP (175256 family), TCS page with '
              'water-requirement / QRC-spacing replies. Yard-3 depth: machine water requirement 5 m3/hr per stacker and '
              'reclaimer. Design reply only.')
BASIS_TRIP3 = ('GA of tripper for stacker machine, compliance report / TCS sheet used to establish the EAF-3 fire '
               'protection source gap (reply describes stacker cab/electric-house provisions only; no reclaimer fire '
               'design package exists in the corpus). Source gap recorded; not field-verified.')

ENT_EAD3 = 'ent_74fe7db2cb3745e98849'
ENT_EAD3_SLEW = 'ent_1db781bc3c03b3431785'
ENT_EAD3_LUFF = 'ent_0ed79bbd1d47c09c8a02'
ENT_EAD3_BOOM = 'ent_a3e75bf14bff5bb4f39a'
ENT_EAD3_DSS = 'ent_a6f5f71cc6ad583a2e47'
ENT_EBA12_WEIGHER = 'ent_b8434b359bf7b44dfcfd'
ENT_EBA12_SEAL = 'ent_91d9e54561ca570ca794'
ENT_EAF3_AUX = 'ent_466456eb982706673d28'
ENT_EAF3_HOIST = 'ent_38612752f2fea740d98e'
ENT_EAF3_TRAVEL = 'ent_fdb13f81c7a9bed69285'
ENT_EAF3_RISERS = 'ent_4a0b95f13eeabb7c7583'

# Top-model Pass-5 review (returned 2026-10-17) fold-in: proofread corrections to
# compiled finding rows, text corrections on composed operations, retain/confirm
# notes for the previously deferred rows, and two evidence-backed retirements.
FINDING_FIXES = [
    (DOC_A11, 'impact_transition_idlers', [('Ø159 mm tube, 190.0 c/c', 'Ø139.7 mm TUBE DIA, 190.0 O/D'),
                                           ('190.0 c/c and tilt quoted as printed', '190.0 O/D and tilt quoted as printed')]),
    (DOC_A11, 'impact_idlers', [('Ø159 mm tube, 190.0 c/c', 'Ø139.7 mm TUBE DIA, 190.0 O/D')]),
    (DOC_A11, 'belt_tensions', [('98.557', '98.537')]),
    (DOC_A11, 'revision_table', [('Rev 1: 05.10.18', 'Rev 1: 05.08.18')]),
    (DOC_A12, 'take_up_assembly', [('min braking force 287 kN', 'min braking force 267 kN')]),
]

OP_FIXES = [
    (DOC_A11, 'of conveyor-7 (175021) and conveyor-8 (175022); the marked',
     'of belt conveyor-7 and conveyor-8 (referenced in the OE comments); the marked'),
    (DOC_RECG, 'GEAR BOX transmission ratio 35.5:1, connecting gear ratio 5.294;',
     "GEAR BOX transmission ratio 35.5:1, connecting gear ratio 5.294; GEAR BOX TYPE 'HELICAL HOLLOW "
     "OUTPUT SHAFT WITH SHRINK DISC' (BOD 175119 Rev 2 prints 'Bevel helical hollow output shaft with "
     "shrink disc' - both wordings retained);"),
    (DOC_DSSS, ' (Chemtrols DBR Annexure-1A; superseded in part by later Grundfos/F.Harley reclaimer values)',
     ' (Chemtrols DBR Annexure-1A)'),
    (DOC_DBR3, '(Machine requirement 5 m3/hr exceeds onboard pump capacity 5 m3/hr (EAD-3) - consistent 1:1 fill/use basis)',
     '(Machine requirement 5 m3/hr equals onboard pump capacity 5 m3/hr (EAD-3 Grundfos CR 5-16 = 5 m3/hr; '
     'DBR Annexure-1A = 4.90 m3/hr))'),
    (DOC_PHIL, '(Sector tables on p4 list Yard-3 as Sectors 1-12 spanning SC-03 and SC-04)',
     '(Sector tables on p4 list Yard-3 as Sectors 1-12 spanning SC-03 and SC-04; p5 continues with Sectors '
     '13-14 - 14 sectors total = 28 sprinklers per stockpile)'),
    (DOC_TRIP, 'on the stocker,', 'on the stocker (sic, for stacker),'),
]

FOLDIN = {
    DOC_A11: [
        dict(ent=ENT_EAC11_PULLEY, cites=['pulley_bearing_centres_digit_conflict'], confidence=0.9, value=(
            "Pulley bearing-centre rows on GA-11 p5 (rev-2 deltas) retain_disagreement (top-model Q1, "
            "DQ-B20-001-e): all five pulley schedule rows print '2700 BRG .CRS.' at 8x zoom (drive 1000 DIA x "
            "2200 FACE; tail 800; take-up 800; snub 630; bend 800), matching live fact_6c69b1b78ce04581b260, "
            "while the GA plan/head-detail dimension string reads ~2700/2730 and earlier low-resolution passes "
            "suggested 2300 (glyphs 2300/2700/2730 at render limit). '2700 BRG .CRS.' kept as the governing "
            "reading with the render-limit qualification; open: pulley bearing-centre calculation / vector CAD "
            "not in corpus.")),
        dict(ent=ENT_EAC11_IDLER, cites=['transition_idler_quantities'], confidence=0.9, value=(
            "EAC-11 transition idler row on GA-11 p5 (revision triangle 2 + black revision arrow) prints "
            "verbatim: '3 EQ. ROLL 5°,10°,15°,25°&30°TROUGH Ø159mm TUBE DIA.(2° TILT) | QTY.:-5°=2NOS.,"
            "10°=2NOS.,15°=2NOS., 20°=1NO, 25°=3NOS. & 30°=2NOS.' - the header list prints 5 angles (20° "
            "omitted, 30° not 35°) while the quantity key in the same cell runs 6 angles; the mismatch is "
            "explicitly printed (top-model Q1 confirmed, per-angle count digits at render limit). Immediately "
            "below: impact-transition row prints '3 EQ. ROLL 15°,20° TROUGH Ø139.7mm TUBE DIA, 190.0 O/D "
            "(2° TILT) | QTY.:-15°=3NOS. & 20°=3NOS.' and impact row '3 EQ. ROLL 35° TROUGH Ø139.7mm TUBE "
            "DIA, 190.0 O/D @ 400mm PITCH: | QTY.=6 NOS.'")),
        dict(ent=ENT_EAC11_PROT, cites=['pcs_pair_unit'], confidence=0.9, value=(
            "Pull-cord switch (PCS) quantities print as bare numbers without a pair/device unit: EAC-11 "
            "'BOTH SIDES @ 30M SPACING: QTY. - 30' and EBA-12 '31', while BSS prints '18 PAIRS' / '17 PAIRS' "
            "(top-model Q1 confirmed verbatim; do not normalize to 30/31 NOS. or PAIRS; whether the count "
            "means switches or pairs is unresolved).")),
        dict(ent=ENT_EAC11_HGTU, cites=['hgtu_frame_loads'], confidence=0.9, value=(
            "EAC-11 tail-pulley-with-HGTU frame load table transcribed (top-model Q2 confirmed; header 'LOAD "
            "DATA OF TAIL PULLEY WITH HGTU FRAME [IN KN]' although EAC-11's HGTU is at head-end UAX-3). Rows "
            "COLUMN MARKED | DL Hx/V/Hz | OL (trolley movement) Hx/V/Hz: T1 0.93/2.20/0.36 | "
            "2.416/11.288[or 11.268]/1.28[edge]; T2 4.48[or 4.46]/3.37/-0.24 | 12.765[or 12.785]/18.361/"
            "-1.13x; T3 4.48[or 4.46]/3.37/0.24 | 13.639/19.748/0.84x. 6/8 digits and trailing thousandths "
            "at raster/crop limit; columns right of OL Hz outside crop (open question Q2).")),
        dict(ent=ENT_EAC11, cites=['notes_support_tags'], confidence=0.9, value=(
            "GA-11 sheet-1 Notes 18/19 corrected transcription (top-model Q2): Note 18 'FOR HEAD PULLEY "
            "FRAME, SHORT POST LOAD DETAILS | REFER GA & MECHANICAL LOAD OF UAX-3_DRG. NO.: "
            "MAITREE-00-UEF-LH-175049-ISG-0'; Note 19 '... UEE-6_DRG. NO.: MAITREE-00-UEF-LH-175038-ISG-0'. "
            "Note 18 matches head house UAX-3; Note 19 'UEE-6' is a copied template tag on a conveyor whose "
            "tail is UEF-4 (UEF-4 to UAX-3 govern the endpoints). Supersedes fact_a1eaba854236c25c8aab "
            "(retired; 'UAX1/UEF6' wording).")),
    ],
    DOC_A12: [
        dict(ent=ENT_EBA12_IDLER, cites=['hold_down_face_width'], confidence=0.9, value=(
            "EBA-12 hold-down roller row prints '219 DIA x 2200 FACE WIDTH [triangle 2] | QTY. 1 NO./CONV.' "
            "verbatim while the drive/tail/take-up pulleys and deflector roller are 1600 FACE on this 1400 mm "
            "belt (top-model Q1 confirmed): 2200 matches the 2000-mm-belt EAC-9/EAC-11 template and is "
            "anomalous for 1400 BW; retained verbatim, not normalized to 1600 (open: roller schedule / "
            "gallery structural 175003 disposition).")),
        dict(ent=ENT_EBA12_SEAL, cites=['seal_plate_thickness'], confidence=0.9, value=(
            "EBA-12 seal plate row prints '31.5 THK. SEAL PLATE CONTINUOUS FOR CONV., GALLERY AND ALSO AT "
            "ELEVATED WALKWAY [triangle 2]' with the decimal clearly between '1' and '5' (top-model Q1 "
            "confirmed; same shifted-decimal style as peer GA-10); deck plate row above prints '3.15 THK. "
            "CONTINUOUS [triangle 2]' and Sheet-1 Note 8 requires min 3.0 mm seal plate - '31.5' retained "
            "verbatim as a print anomaly for 3.15 mm.")),
        dict(ent=ENT_EBA12_WEIGHER, cites=['belt_weigher_accuracy'], confidence=0.9, value=(
            "EBA-12 belt weigher cell prints 'LOAD CELL TYPE BELT WEIGHER ACCURACY (±)25% AT 20 TO 120% FOR "
            "1400 B/W QTY 1 NO.' verbatim - no decimal before '25%' (top-model Q1 retain_disagreement; peer "
            "GA-10 prints (±)2%); live fact_8b9219aae01042a4aff1 '±0.25%' stands as an unverified "
            "missing-decimal interpretation pending the belt-weigher GA/PG test procedure; neither reading "
            "dropped.")),
        dict(ent=ENT_EBA12_HGTU, cites=['hgtu_frame_loads'], confidence=0.9, value=(
            "EBA-12 tail-pulley-with-HGTU frame load table transcribed (top-model Q2 confirmed; footer: (-) "
            "= uplift, loads exclude impact/dynamic factor). T1-T6 | DL Hx/V/Hz | DL (trolley movement) | "
            "LL(Belt Snap) | Col4 Hx: T1 0.01/-0.83/0.1 | 0.033/-0.265/8.122[or 0.122] | 1.131/31.978/35.55 "
            "| -0.53; T2 0.23/2.04/0.05[or 8.05] | 0.84[or 0.81]/9.724[or 5.724]/0.157 | 0.649/-18.381[or "
            "-18.351]/-2.307 | 0.154; T3 1.05/3/-0.01 | 3.949/15.385/-0.074 | -3.909/-16.325/1.735 | 0.82; "
            "T4 1.05/3/0.01[or 8.01] | 4.227/16.531/0.644 | 0.82/5.385[or 5.365]/0.985 | -3.909; T5 "
            "0.23/2.04/-0.05 | 0.375/4.683/-0.12 | 0.154/13.731/0.389 | 0.649; T6 0.01/-0.83/-0.1 | "
            "0.02/-0.273/-0.189 | -0.53/-14.388/20.068[or 20.088] | 1.131. DL symmetric T1/T6, T2/T5, T3/T4; "
            "LL Hx vs Col4 Hx reversed order. Bracketed digits at render limit.")),
    ],
    DOC_STKG: [
        dict(ent=ENT_EAD3_SLEW, cites=['slew_drive_motor_power_conflict'], confidence=0.9, value=(
            "EAD-3 slew drive motor power retain_disagreement (top-model Q3, DQ-B21-001): GA & TDS 175126 "
            "Rev 2 (21.11.2018) prints 'Power of motor | , kW | 15' under Slewing mechanism (hydraulic "
            "motor, 0.0758 r/min, 0° ~100°); Stacker BOD 175249 Rev 2 (approved 27-Feb-2019) prints slew "
            "driving motor '22 kW, 1500 rpm syn.' (qty 2x4 nos.; 0.7284 x 18/173 = 0.0758 rpm matches GA). "
            "Neither dropped - hydraulic-motor shaft rating vs HPU pump-motor rating vs revision delta "
            "unresolved.")),
        dict(ent=ENT_EAD3_SLEW, cites=['slew_angle_ga_print'], confidence=0.9, value=(
            "EAD-3 slewing range 0° to 100° governs (top-model Q3 confirmed): GA TDS 175126 Rev 2 prints "
            "'0° ~100°' with a single range-separator stroke (not '~-100°'), matching live "
            "fact_c989cd61e4715f2863e3 and BOD 175249 Rev 2 'Slew Range (0~100°)'.")),
        dict(ent=ENT_EAD3_LUFF, cites=['luff_ga_tds_row_labels'], confidence=0.9, value=(
            "EAD-3 luffing TDS rows verbatim (top-model Q3 confirmed): 'Luffing gear | , Degree | Hydraulic "
            "Cylinder' (unit-cell typo), 'loft angle | , Degree | +14°', 'rotation angle | , Degree | -8°', "
            "'power of motor | , kW | 22'; 'loft angle +14°' = upward luffing limit, 'rotation angle -8°' = "
            "downward limit (BOD 175249 Rev 2 '+14° ~ -8°', 22 kW HPU); crop q3_b12 clipped below the "
            "slewing block (recrop optional).")),
        dict(ent=ENT_EAD3, cites=['tie_down_both_ends_deviation'], confidence=0.9, value=(
            "EAD-3 tie-down / storm-lock deviation retained open (top-model Q4 retain_disagreement, "
            "DQ-B21-001): TCS Item 14 (175126 Rev 2 p4) - FTS B4-28 requires machine tie-down / storm lock "
            "at BOTH ends of track for wind > 73 m/s ('not one side as furnished'); vendor reply - one-side "
            "boom anchor suffices (travel to anchor at wind > 20 m/s or hurricane warning; other side may "
            "affect reclaimer travel). Also Item 13: FTS requires a stacking chute at boom conveyor "
            "discharge; vendor declines (boom head weight). No post-Rev-2 concession or Rev 3+ GA in "
            "corpus.")),
        dict(ent=ENT_EAD3_BOOM, cites=['boom_belt_speed_conflict'], confidence=0.9, value=(
            "EAD-3 boom conveyor belt speed retain_disagreement (top-model Q5): GA TDS 175126 Rev 2 p1 "
            "prints '3.5' m/s inside a delta-2 box; TCS Item 6 requires 3.6 m/s and the vendor reply reads "
            "'Revised.' (Rev-2 cell still prints 3.5). The travelling tripper row stays separate at 3.5 m/s "
            "(ent_02089e0e7e2094360aac, matching EAC-11) - never merged with the boom row.")),
        dict(ent=ENT_EAD3, cites=['water_rate_moisture_conflict'], confidence=0.9, value=(
            "EAD-3 design coal moisture retain_disagreement (top-model Q5): GA TDS 175126 Rev 2 p1 prints "
            "handled-material 'water rate .% | max 25%'; Stacker BOD 175249 Rev 2 item 3.4 prints 'Moisture "
            "content = Max. 24%' (matching the 7-24% range on EAC-11/EBA-12, live fact_fee48d437a2645ed8e64 "
            "/ fact_33ff644d9227434b8787). Both values preserved with provenance; no silent "
            "normalization.")),
        dict(ent=ENT_EAD3, cites=['design_stacking_ga_print'], confidence=0.9, value=(
            "EAD-3 stacking throughput confirmed (top-model Q5): GA TDS 175126 Rev 2 p1 prints Rated "
            "Stacking 3400 t/h and Design Stacking 3740 t/h (first-digit glyph comparison ruled out "
            "5240/5740), matching BOD 175249 Rev 2 (110% of rated) and live fact_92e8d9c822728c919993 / "
            "fact_c75aa1e9d8ee891ea75c.")),
    ],
    DOC_STKB: [
        dict(ent=ENT_EAD3_SLEW, cites=['slew_drive_motor_bod', 'slew_range_bod', 'slew_output_speed'],
             confidence=0.9, value=(
            "EAD-3 slew system BOD record with GA cross-reference (top-model Q3): BOD drives table prints "
            "slew driving motor '22 kW, 1500 rpm syn.' (qty 2x4) and 'Slew Range (0~100°)' with output speed "
            "0.7284 rpm (x 18/173 = 0.0758 r/min = GA slew speed); GA & TDS 175126 Rev 2 instead prints "
            "'Power of motor 15 kW' - both readings retained (retain_disagreement).")),
    ],
    DOC_RECG: [
        dict(ent=ENT_EAF3_AUX, cites=['aux_boom_reclaim_capacity'], confidence=0.9, value=(
            "EAF-3 auxiliary boom reclaim capacity retain_disagreement (top-model Q6, DQ-B21-002): GA & TDS "
            "175127 Rev 2 p3 prints 'CAPACITY (AUXILIARY BOOM) [triangle 2] | 500-660 TPH' (660 inside "
            "revision cloud 2) vs BOD 175119 Rev 2 '500-650 t/h' (depending on boom inclination) - same "
            "23-Nov-2018 approval cycle, so both preserved; live fact_58a944cdee7a508149ad expanded to cite "
            "the 500-650 BOD figure alongside 500-660 TPH.")),
        dict(ent=ENT_EAF3_TRAVEL, cites=['buffer_support_end_distance'], confidence=0.9, value=(
            "EAF-3 Rail-B layout callouts at render limit (top-model Q7 retain_disagreement): top '752480 "
            "[or 732480] RAIL B LENGTH' (clipped), middle '729350 [or 727350] BUFFER SUPPORT END DISTANCE "
            "FOR PORTAL RECLAIMER (RAIL B SIDE)' (earlier 713356 candidate refuted), lower '727000 [or "
            "727300]'; left-end offsets 1770 / 350 / 2200 / 500; strip depicts EAE-4/EAF-4 context (EBA-12 "
            "GA layout), vs TDS 'TRAVEL DISTANCE: 714.750 m' and 710000 mm stockpile - not normalized.")),
        dict(ent=ENT_EAF3_HOIST, cites=['hoist_gearbox_type'], confidence=0.9, value=(
            "EAF-3 hoist gearbox type retain_disagreement (top-model Q7): GA & TDS 175127 Rev 2 p3 'GEAR BOX "
            "TYPE | HELICAL HOLLOW OUTPUT SHAFT WITH SHRINK DISC' (transmission ratio 35.5:1, FoS min 1.5 "
            "cloud 2) vs BOD 175119 Rev 2 'Bevel helical hollow output shaft with shrink disc'; both "
            "retained (the auxiliary-boom chain-drive table on the same sheet prints 'BEVEL HELICAL'"
            ").")),
        dict(ent='ent_cede7b76cd274533933c', cites=['wind_design_speeds'], confidence=0.9, value=(
            "EAF-3 wind design values resolved as a proven unit typo (top-model Q8): GA & TDS 175127 Rev 2 "
            "p3 prints 'MAXIMUM WIND VELOCITY (OPERATION) 16 km/h' and 'EXTREME WIND VELOCITY (NON "
            "OPERATION) 73 km/h'; q = 0.5 rho v^2 gives 0.16 / 3.33 kN/m2 at 16 / 73 m/s, matching BOD "
            "175119 Rev 2 and live fact_ba02e2bfc2428f12e884; governing 16 m/s operating, 35 m/s "
            "non-operating, 73 m/s extreme; no automatic anemometer trip setpoints inferred.")),
        dict(ent=ENT_EAF3_TRAVEL, cites=['travel_speeds'], confidence=0.9, value=(
            "EAF-3 travel speeds retain_disagreement (top-model Q8): GA TDS 175127 Rev 2 p3 prints 'TRAVEL "
            "SPEED [triangle 2] | OPERATING 2 TO 8 m/min - RELOCATION 20 m/min Max.' (8 in rev cloud 2; VFD "
            "150-1500 rpm) vs BOD 175119 Rev 2 discrete reclaiming 2 / 5 m/min and relocation 20 m/min "
            "(0.33 m/s buffer calc) - both preserved. Wheel counts corrected: the crop prints NO OF WHEELS "
            "14 (fixed side) + 8 (pendulum side) = 22 total and NO OF DRIVEN WHEELS 8 + 4 = 12 driven; "
            "fact_2022c45e62c6c4ab7648 read only the fixed-side column ('14 total, 8 driven') and is "
            "retired; 22 wheels / 12 driven per BOD 175119 and the lubr3 90-point schedule.")),
    ],
    DOC_RECB: [
        dict(ent=ENT_EAF3_TRAVEL, cites=['rail_clamp_bod', 'buffer_effect_analysis'], confidence=0.9, value=(
            "EAF-3 travel system BOD record (top-model Q8 cross-ref): 'Total No. of Wheels on Machine 22' "
            "with hydraulic rail clamps 2 nos. + manual 2 nos. + buffers 8 nos.; max travel speed 0.33 m/s "
            "(= 20 m/min relocation) used in the buffer-effect local check; reclaiming design speeds 2 / 5 "
            "m/min per BOD 1.2 vs GA TDS 'OPERATING 2 TO 8 m/min' band - both retained (see recg3 "
            "travel-speed note).")),
    ],
    DOC_DSSS: [
        dict(ent=ENT_EAD3_DSS, cites=['suction_filter_duplex_vs_simplex_wording'], confidence=0.9, value=(
            "Stacker plain-water DSS suction filter (top-model Q9 confirmed): DBR p21 lists 'Suction Duplex "
            "filter with Diff. Pressure Indicating Switch' and p26 alarm 'Duplex filter' choked; "
            "corroborated by P&ID/datasheet tag DF-101 duplex filter (250 microns, 150# B16.5, 1 1/2 inch "
            "line, 4 butterfly diversion valves) with DPS-101 (0.2 bar). pp23/29 'simplex filter choked' "
            "retained with explicit dry-fog / copied alarm-table scope only.")),
    ],
    DOC_PHIL: [
        dict(ent=ENT_EAF3_RISERS, cites=['ap_range_engineer_stockpile_mapping'], confidence=0.9, value=(
            "Yard-3 AP range mapping confirmed verbatim-with-conflict (top-model Q10): p4 prints "
            "'Application Points :- AP-57 to AP-84 in Stockpile-3(Controlled by SC-03) KKS tag "
            "no.-00EAE03QN201 and AP-85 to AP-112 in Stockpile-2(Controlled by SC-04) KKS tag "
            "no.-00EAE04QN201' under heading 'STOCKPILE NO - 3 & 4'; printed 'Stockpile-2' retained as-is "
            "with conflict note (heading, SC-04, KKS 00EAE04QN201 and SV..201-228 identify EAE-4). Sectors: "
            "p4 prints Sectors 1-12, p5 continues Sectors 13-14 (14 sectors = 28 sprinklers per stockpile); "
            "minor '(Sector r-12)' typo retained.")),
    ],
    DOC_FIRE: [
        dict(ent=ENT_EAD3, cites=['fire_package_identity_and_scope'], confidence=0.9, value=(
            "EAD-3 fire package identity note (top-model proofread item 5): IS-3-GA-702-108-E1104 REV 02 "
            "(FIO 14-Nov-2019) is the same unapproved FIO 00-EAD family submittal reviewed for Yard-2 B44; "
            "verbatim anomalies preserved across its review: cover index 'SCHERMATIC' (sic), MX "
            "DesignManager 'Elecrical_Room / 1' (sic), 1x80L [49.5 kg] + 1x22L [11 kg] MX calculation vs "
            "2x80L + 2x22L BOM/schematic cylinder counts, MX Driver-Room height 2.5 m vs approved cabin "
            "2.4 m; no numbered unit named; no installation/commissioning records (source_gap stands).")),
    ],
}

RETIRES = {
    DOC_A11: [
        ('fact_a1eaba854236c25c8aab',
         "Corrected by clear crop re-read (top-model Pass-5 Q2): GA-11 sheet-1 Notes 18/19 print UAX-3 "
         "(drg MAITREE-00-UEF-LH-175049-ISG-0) and UEE-6 (drg MAITREE-00-UEF-LH-175038-ISG-0); the prior "
         "'UAX1/UEF6' transcription was a low-resolution misread. Governing endpoints UEF-4 to UAX-3 "
         "retained.", ['notes_support_tags']),
    ],
    DOC_RECG: [
        ('fact_2022c45e62c6c4ab7648',
         "Crop re-read (top-model Pass-5 Q8): GA TDS prints 14 (fixed side) + 8 (pendulum side) = 22 wheels "
         "total and 8 + 4 = 12 driven wheels; the original value read only the Fixed Side column. "
         "Corroborated by BOD 175119 (22 wheels) and the lubr3 90-point lubrication schedule.",
         ['travel_speeds']),
    ],
}

FULL = [0.03, 0.05, 0.97, 0.97]

_FINDINGS = None
_BY_DOC = None


def findings_for(doc):
    global _FINDINGS, _BY_DOC
    if _FINDINGS is None:
        _FINDINGS = []
        _BY_DOC = {}
        for letter in ('A', 'B', 'C', 'D'):
            data = json.loads((MINE / ('agent-%s.json' % letter)).read_text(encoding='utf-8'))
            for f in data['findings']:
                f['_agent'] = letter
                f['_doc'] = (f.get('support') or {}).get('doc')
                _FINDINGS.append(f)
                _BY_DOC.setdefault(f['_doc'], []).append(f)
        _apply_finding_fixes()
    return _BY_DOC.get(doc, [])


def _apply_finding_fixes():
    for doc, pred, pairs in FINDING_FIXES:
        cands = [f for f in _BY_DOC.get(doc, []) if f.get('predicate') == pred]
        assert cands, (doc, pred)
        for old, new in pairs:
            hits = 0
            for f in cands:
                for key in ('value', 'unit', 'conditions'):
                    text = f.get(key) or ''
                    if old in text:
                        hits += text.count(old)
                        f[key] = text.replace(old, new)
            assert hits >= 1, (doc, pred, old[:60], hits)


_ENT_RE = re.compile(r'ent_[0-9a-f]{16,24}', re.I)
_ENT_IDS = set()


def _ent_ids():
    if not _ENT_IDS:
        with sqlite3.connect(ROOT / 'data/plant/plant.sqlite3') as db:
            for (i,) in db.execute('SELECT id FROM entities'):
                _ENT_IDS.add(i)
    return _ENT_IDS


def resolve(hint, default, mapping=None):
    m = _ENT_RE.search(hint or '')
    if m:
        eid = m.group(0).lower()
        assert eid in _ent_ids(), eid
        return eid
    hl = (hint or '').lower()
    for key, eid in (mapping or []):
        if key in hl:
            return eid
    return default


def _sentence(f):
    v = (f.get('value') or '').strip()
    u = (f.get('unit') or '').strip()
    if u and u.lower() not in v.lower() and u.lower() not in ('n/a', 'none'):
        v = '%s %s' % (v, u)
    cond = (f.get('conditions') or '').strip()
    if cond:
        v = '%s (%s)' % (v, cond)
    return '%s: %s' % ((f.get('predicate') or '').replace('_', ' '), v)


def _evidence(f):
    sup = f.get('support') or {}
    eid = sup.get('evidence_id')
    if not eid:
        return None
    reg = sup.get('region') or FULL
    return dict(evidence_id=eid, quote='', region=list(reg))


def _cite_evidence(doc, cites, pred_index):
    evs = []
    seen = set()
    for cite in cites:
        f = pred_index.get(cite)
        assert f, (doc, cite)
        e = _evidence(f)
        assert e, (doc, cite)
        if e['evidence_id'] not in seen:
            seen.add(e['evidence_id'])
            evs.append(e)
    return evs


def _fold_ops(doc):
    pred_index = {}
    for f in findings_for(doc):
        pred_index.setdefault(f.get('predicate'), f)
    ops = []
    for spec in FOLDIN.get(doc, []):
        ops.append(dict(op='assert', subject=spec['ent'], predicate='document_note', value=spec['value'],
                        context=dict(kind='specification', basis=BASIS_LOOKUP[doc]),
                        origin='explicit', confidence=spec.get('confidence', 0.9),
                        evidence=_cite_evidence(doc, spec['cites'], pred_index)))
    for (fid, reason, cites) in RETIRES.get(doc, []):
        ops.append(dict(op='retire', assertion_id=fid, reason=reason,
                        origin='explicit', confidence=0.95,
                        evidence=_cite_evidence(doc, cites, pred_index)))
    return ops


def ops_for_doc(doc, default_ent, mapping=None, per_op=6, extra_gaps=None):
    grouped = OrderedDict()
    gaps = OrderedDict()
    for f in findings_for(doc):
        cls = f.get('classification')
        if cls not in ('CERTAIN', 'ABSENT'):
            continue
        ent_id = resolve(f.get('subject_hint'), default_ent, mapping)
        assert ent_id in _ent_ids(), (doc, ent_id)
        if cls == 'CERTAIN':
            grouped.setdefault(ent_id, []).append(f)
        else:
            gaps.setdefault(ent_id, []).append(f)
    ops = []
    for ent_id, fs in grouped.items():
        for i in range(0, len(fs), per_op):
            chunk = fs[i:i + per_op]
            evs = [e for e in (_evidence(x) for x in chunk) if e]
            seen = set()
            dedup = []
            for e in evs:
                if e['evidence_id'] not in seen:
                    seen.add(e['evidence_id'])
                    dedup.append(e)
            ops.append(dict(op='assert', subject=ent_id, predicate='document_note',
                            value='; '.join(_sentence(x) for x in chunk),
                            context=dict(kind='specification', basis=BASIS_LOOKUP[doc]),
                            origin='explicit', confidence=0.95, evidence=dedup))
    for ent_id, fs in gaps.items():
        for f in fs:
            ev = _evidence(f)
            val = (f.get('value') or '').strip()
            val = re.sub(r'^ABSENT( from corpus)?;\s*', 'Absent from corpus: ', val)
            cond = (f.get('conditions') or '').strip()
            if cond:
                val += ' ' + cond
            ops.append(dict(op='assert', subject=ent_id, predicate='source_gap',
                            value=val,
                            context=dict(kind='specification', basis=BASIS_LOOKUP[doc]),
                            origin='explicit', confidence=0.9, evidence=[ev] if ev else []))
    for (ent_id, text, cite_findings) in (extra_gaps or []):
        evs = []
        seen = set()
        for f in cite_findings:
            e = _evidence(f)
            if e and e['evidence_id'] not in seen:
                seen.add(e['evidence_id'])
                evs.append(e)
        ops.append(dict(op='assert', subject=ent_id, predicate='source_gap', value=text,
                        context=dict(kind='specification', basis=BASIS_LOOKUP[doc]),
                        origin='explicit', confidence=0.9, evidence=evs[:4]))
    return ops


BASIS_LOOKUP = {}


def gap_entry(text, deciding, doc, ent_id, n=2):
    return (ent_id, '%s Deciding records: %s' % (text, deciding), none_findings(doc, n))


def none_findings(doc, n):
    return findings_for(doc)[:n]


def agaps(letter, indexes):
    data = json.loads((MINE / ('agent-%s.json' % letter)).read_text(encoding='utf-8'))
    gs = data['evidence_gaps']
    return [(gs[i]['gap'], gs[i]['deciding_record']) for i in indexes]


def pkg_a11():
    g = agaps('A', [0, 1, 2, 4, 5, 6])
    extra = [gap_entry(t, d, DOC_A11, ENT_EAC11) for t, d in g]
    return dict(ops=ops_for_doc(DOC_A11, ENT_EAC11, A_MAP_11, extra_gaps=extra),
                summary='Conveyor EAC-11 depth rows: drive/data-sheet, idlers, take-up, civil tables + vendor-internals gaps',
                purpose='Record GA-11 depth rows and absent vendor internals',
                questions=['Which EAC-11 drive/idler/take-up/civil rows are printed?'])


def pkg_a12():
    g = agaps('A', [0, 1, 2, 3])
    extra = [gap_entry(t, d, DOC_A12, ENT_EBA12) for t, d in g]
    return dict(ops=ops_for_doc(DOC_A12, ENT_EBA12, A_MAP_12, extra_gaps=extra),
                summary='Conveyor EBA-12 depth rows: drive/data-sheet, idlers, take-up, civil tables + weigher/vendor gaps',
                purpose='Record GA-12 depth rows and absent vendor internals',
                questions=['Which EBA-12 drive/idler/take-up/civil rows are printed?'])


def pkg_stkb():
    g = agaps('B', [0, 3])
    extra = [gap_entry(t, d, DOC_STKB, 'ent_74fe7db2cb3745e98849') for t, d in g]
    return dict(ops=ops_for_doc(DOC_STKB, 'ent_74fe7db2cb3745e98849', extra_gaps=extra),
                summary='Stacker EAD-3 family depth from BOD: drives, motions, wind/starts, weigher + settings gaps',
                purpose='Record stacker BOD depth rows and absent settings',
                questions=['Which stacker drive/motion design values apply to EAD-3?'])


def pkg_stkg():
    return dict(ops=ops_for_doc(DOC_STKG, 'ent_74fe7db2cb3745e98849'),
                summary='Stacker EAD-3 GA/TDS depth: TDS rows, travel bogie fitments, protection devices, storm logic',
                purpose='Record stacker GA depth rows',
                questions=['Which GA TDS fitments and protections are printed?'])


def pkg_recg():
    g = agaps('C', [0, 1])
    extra = [gap_entry(t, d, DOC_RECG, 'ent_cede7b76cd274533933c') for t, d in g]
    return dict(ops=ops_for_doc(DOC_RECG, 'ent_cede7b76cd274533933c', extra_gaps=extra),
                summary='Reclaimer EAF-3 GA/TDS depth: scraper chain, drives, hoist, travel, reels, DSS/lube rows + gaps',
                purpose='Record reclaimer GA depth rows and absent vendor data',
                questions=['Which reclaimer chain/hoist/travel rows are printed?'])


def pkg_recb():
    return dict(ops=ops_for_doc(DOC_RECB, 'ent_cede7b76cd274533933c'),
                summary='Reclaimer EAF-3 BOD depth: chain tensions, rail clamp, buffer local check, locking load case',
                purpose='Record reclaimer BOD design rows',
                questions=['Which reclaimer structural/load design rows apply?'])


def pkg_fire():
    return dict(ops=ops_for_doc(DOC_FIRE, 'ent_74fe7db2cb3745e98849'),
                summary='Stacker FDA package depth: identity, zones Z101/Z201, NFPA 72 rule, BOM items 1-21',
                purpose='Record fire package rows for the EAD-3 family',
                questions=['What does the FDA package define per zone and BOM item?'])


def pkg_dsss():
    return dict(ops=ops_for_doc(DOC_DSSS, 'ent_a6f5f71cc6ad583a2e47'),
                summary='Stacker onboard DSS depth: 34-nozzle design, AP distribution, Chemtrols component details',
                purpose='Record onboard DSS design rows',
                questions=['Which nozzle/AP/component rows are printed?'])


def pkg_dspk():
    return dict(ops=ops_for_doc(DOC_DSPK, 'ent_a6f5f71cc6ad583a2e47'),
                summary='Stacker DSS equipment/technical-spec rows: PS-101, DPS-101, level switch, P101/P102, DF-101, nozzles, hose reel',
                purpose='Record DSS package instrument/equipment rows',
                questions=['Which instrument/equipment datasheet values are printed?'])


def pkg_dssr():
    return dict(ops=ops_for_doc(DOC_DSSR, 'ent_3352a2725b882230502a'),
                summary='Reclaimer onboard DSS depth: PRP-1A schedule, tank/hose arrangement, suction head-loss calc',
                purpose='Record reclaimer DSS design rows',
                questions=['Which pump/tank/head-loss rows are printed?'])


def pkg_pump():
    return dict(ops=ops_for_doc(DOC_PUMP, 'ent_3352a2725b882230502a'),
                summary='Reclaimer DSS pump vendor datasheet rows (Grundfos CRN 1-8) + serial gap',
                purpose='Record pump vendor datasheet values',
                questions=['Which vendor pump values are printed?'])


def pkg_fhpid():
    return dict(ops=ops_for_doc(DOC_FHPID, 'ent_3352a2725b882230502a'),
                summary='Reclaimer DSS P&ID 3778-02-T-01 depth: pump schedule, TCS outcomes, yard-QRC tank-fill',
                purpose='Record FH P&ID rows',
                questions=['Which schedule/interlock/tank-fill rows are drawn?'])


def pkg_lubs():
    return dict(ops=ops_for_doc(DOC_LUBS, 'ent_74fe7db2cb3745e98849'),
                summary='Stacker central lubrication depth: KSP8-S TDS values and KSP8-65S mounting compliance',
                purpose='Record stacker lube pump rows',
                questions=['Which lube pump models/locations are stated?'])


def pkg_lubr():
    return dict(ops=ops_for_doc(DOC_LUBR, 'ent_cede7b76cd274533933c'),
                summary='Reclaimer central lubrication depth: Lincoln dual-line spec and 90-point schedule',
                purpose='Record reclaimer lube rows',
                questions=['Which lubrication spec/point rows are printed?'])


def pkg_phil():
    return dict(ops=ops_for_doc(DOC_PHIL, 'ent_53b88ca7215673aab2e0'),
                summary='Yard-3 DS philosophy depth: ring header/sector scheme and AP-57..112 rows + AP-SV gap',
                purpose='Record Yard-3 sprinkler scheme rows',
                questions=['Which stockpile ring/sector rows are printed for SC-03/SC-04?'])


def pkg_play():
    return dict(ops=ops_for_doc(DOC_PLAY, 'ent_4a0b95f13eeabb7c7583'),
                summary='Yard-3 piping layout TCS: riser/pedestal coordinate and routing gaps',
                purpose='Record Yard-3 layout gaps',
                questions=['What does the layout TCS state about coordinates/routing?'])


def pkg_qrc():
    return dict(ops=ops_for_doc(DOC_QRC, 'ent_1979c505f4b6b490828a'),
                summary='Yard-3 QRC P&ID depth: BOM item 19, notes 9/10 spacing, pump schedule + per-yard split gap',
                purpose='Record QRC drawing rows',
                questions=['Which QRC count/spacing rows are printed?'])


def pkg_dbr():
    return dict(ops=ops_for_doc(DOC_DBR3, 'ent_1979c505f4b6b490828a'),
                summary='Yard-3 machine water requirement reply: 5 m3/hr per stacker and reclaimer',
                purpose='Record stockpile DBR water-requirement reply',
                questions=['What water rate does the DBR reply state per machine?'])


def pkg_trip():
    return dict(ops=ops_for_doc(DOC_TRIP, 'ent_cede7b76cd274533933c'),
                summary='EAF-3 fire protection source gap evidenced from tripper GA compliance reply',
                purpose='Record reclaimer fire gap with its evidence',
                questions=['Is there any reclaimer fire design package in the corpus?'])


BUILDERS = {
    DOC_A11: (pkg_a11, 'a11', 771), DOC_A12: (pkg_a12, 'a12', 772),
    DOC_STKB: (pkg_stkb, 'stkb3', 773), DOC_STKG: (pkg_stkg, 'stkg3', 774),
    DOC_RECG: (pkg_recg, 'recg3', 775), DOC_RECB: (pkg_recb, 'recb3', 776),
    DOC_FIRE: (pkg_fire, 'fir3', 777), DOC_DSSS: (pkg_dsss, 'dsss3', 778),
    DOC_DSPK: (pkg_dspk, 'dspk3', 779), DOC_DSSR: (pkg_dssr, 'dssr3', 780),
    DOC_PUMP: (pkg_pump, 'pump3', 781), DOC_FHPID: (pkg_fhpid, 'fhpid3', 782),
    DOC_LUBS: (pkg_lubs, 'lubs3', 783), DOC_LUBR: (pkg_lubr, 'lubr3', 784),
    DOC_PHIL: (pkg_phil, 'phil3', 785), DOC_PLAY: (pkg_play, 'play3', 786),
    DOC_QRC: (pkg_qrc, 'qrc3', 787), DOC_DBR3: (pkg_dbr, 'dbr3', 788),
    DOC_TRIP: (pkg_trip, 'trip3', 789),
}

PACKAGES = [(doc, BUILDERS[doc][0], BUILDERS[doc][1], BUILDERS[doc][2]) for doc in BUILDERS]

BASIS_LOOKUP.update({
    DOC_A11: BASIS_A11, DOC_A12: BASIS_A12, DOC_STKB: BASIS_STKB, DOC_STKG: BASIS_STKG,
    DOC_RECG: BASIS_RECG, DOC_RECB: BASIS_RECB, DOC_FIRE: BASIS_FIRE3, DOC_DSSS: BASIS_DSSS3,
    DOC_DSPK: BASIS_DSPK3, DOC_DSSR: BASIS_DSSR3, DOC_PUMP: BASIS_PUMP3, DOC_FHPID: BASIS_FHPID3,
    DOC_LUBS: BASIS_LUBS3, DOC_LUBR: BASIS_LUBR3, DOC_PHIL: BASIS_PHIL3, DOC_PLAY: BASIS_PLAY3,
    DOC_QRC: BASIS_QRC3, DOC_DBR3: BASIS_DBR3, DOC_TRIP: BASIS_TRIP3,
})


def all_ids(doc):
    import sqlite3 as _sq
    with _sq.connect(ROOT / 'data/plant/plant.sqlite3') as _db:
        return [r[0] for r in _db.execute('SELECT id FROM evidence WHERE document_id=? ORDER BY page, id', (doc,)).fetchall()]


def build_package(doc, builder):
    body = builder()
    ops = body.pop('ops')
    for (fdoc, old, new) in OP_FIXES:
        if fdoc != doc:
            continue
        hits = 0
        for op in ops:
            text = op.get('value') or ''
            if old in text:
                hits += text.count(old)
                op['value'] = text.replace(old, new)
        assert hits >= 1, (doc, old[:60], hits)
    ops.extend(_fold_ops(doc))
    return dict(summary=body['summary'], operations=ops,
                intake_assessment=dict(route='mixed', purpose=body['purpose'],
                                       questions=body['questions'], reviewed_evidence_ids=[], gaps=[]))


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
        assert base_version == 770, base_version
    running = base_version if not args.apply else 770
    for doc, builder, tag, ver in PACKAGES:
        if args.apply:
            assert running == ver - 1, (tag, running, ver)
        out = BASE / ('accepted-%s' % tag if args.apply else 'rehearsal-%s' % tag)
        out.mkdir(parents=True, exist_ok=True)
        body = build_package(doc, builder)
        body['intake_assessment']['reviewed_evidence_ids'] = all_ids(doc)
        if args.apply:
            assert body == json.loads((BASE / ('rehearsal-%s/package.json' % tag)).read_text(encoding='utf8'))
            assert json.loads((BASE / ('rehearsal-%s/result.json' % tag)).read_text(encoding='utf8'))['ok']
        (out / 'package.json').write_text(json.dumps(body, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
        store = Store(plant if args.apply else COPY)
        if not args.apply:
            running = store.version()
        assert store.version() == running, (doc, store.version(), running)
        visual = list({e['evidence_id'] for op in body['operations'] for e in op.get('evidence', [])})
        report = validate(store, {k: body[k] for k in ('summary', 'operations')}, doc, running, visual_ids=visual)
        (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
        assert not report['errors'], (tag, report['errors'])
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
