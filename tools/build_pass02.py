"""Pass-2 packages (DQ-B09-001, DQ-B09-002, DQ-B10-001, DQ-B10-002, DQ-B11-001).

Locally reviewed (OCR text + full-page vision + zoom crops) before any top-model
trip, per PASS_B_TWO_TIER_WORKFLOW.md complete-pass rule. Eight one-source
proposals, chained v731 -> v739. Default: isolated rehearsal in
pass-02/rehearsal-copy; --apply performs guarded live acceptance after the
top-model return is folded in (proofread + 4 conflict questions).
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-02'
COPY = BASE / 'rehearsal-copy'
DOC_GRZ = 'doc_b4cf0a76c954435aadd6'
DOC_CTL = 'doc_4f2cd96c3b1e413ea4b5'
DOC_C3 = 'doc_3eab668d697f4e4598c8'
DOC_TP3 = 'doc_883418b36ea44369adbe'
DOC_SM = 'doc_404c8747ba8047ab8f12'
DOC_U1 = 'doc_c0ce31dea65b4d4caef4'
DOC_PID = 'doc_bca09d68af9b43e3b633'
DOC_PSH = 'doc_8d973a7544ef4a488e98'

EBD1 = 'ent_6d32d897d9f24094b563'
EBD2 = 'ent_3c6409c508c1406eafda'
EBD3 = 'ent_0ddac9566081464c9f15'
EBD4 = 'ent_13ced5c3046a4471927b'
UEE1 = 'ent_92291cd617b04811bc28'
EAC3A = 'ent_9f1ca0f604de4bdda3a5'
EAC3B = 'ent_fb331701a6c04437842b'
UEF3 = 'ent_d8d8763a4bc2400882b9'
SMP = 'ent_037e08c0c8134297a954'
FG1 = 'ent_6d0d953b7e804240a2e4'
FG2 = 'ent_13a6597186a24acf8e6a'

BASIS_GRZ = ('GA 175064: TCS Rev 1 AOC 07-Jan-19 with BHEL replies; GA Rev 2 approved 21-Jan-2019; '
             'motor calc SO 200999 Rev 001 16/01/2019 (Page 1 of 2 in corpus; Page 2 of 2 absent). Design only.')
BASIS_CTL = ('Control write-up IS-4-CW-702-101-E914 Rev04 26.03.2020 (BIFPCL doc MAITREE-00-EBY-DB-179162-ISG), '
             'AOC 06-Apr-2020 subject to necessary corrections; AOC conditions sheet not in corpus. Design only.')
BASIS_C3 = ('GA and load data belt conveyor-3A/3B, dwg IS-1-GA-702-101-M013 Rev 3 (28.10.18; customer '
            'dwg Maitree-00-KT-LH-175013-ISG-3); status block FOR APPROVAL, sheet stamped APPROVED 26-Nov-2018. '
            'Design only.')
BASIS_TP3 = ('GA and mech load TP-3 175035; TCS Rev 2 AOC 17-May-18 with BHEL replies to comment 41; '
             'Fichtner comments 16-May-18; GA approved 14-Dec-2018 (AOC revision distinct from approved revision). '
             'Design only.')
BASIS_SM = ('ASSPL sampling system GA 251A-MECH-SYS-100-1 and equipment GAs (Mar-Apr 2016), FOR APPROVAL; '
            'only TCS comments 17-36 (pp10-11) APPROVED 07-Jan-2019 (comments 1-16 and sheets p2/p9 unreviewed); '
            'Note 7 cross-refers 251B-MECH-SYS-100-1. Vendor supply versus BHEL system design; design only.')
BASIS_U1 = ('Piping layout DFDS/SW/PW UEE-1 175287 Rev 2, FIO 12-Sep-2019; TCS Rev1 FIO-R 08-Jul-19 '
            '(FFL routing and FAS/PRU locations to be revised). FIO non-approved layout data only; never overrides '
            'approved P&ID tag allocation.')
BASIS_PID = ('P&ID for DFDS System (13.10.2018-comment revision); status block FOR APPROVAL, sheet stamped '
             'APPROVED 14-Dec-2018. Design only.')
BASIS_PSH = ('GA and mech load PSH 175034: TCS AOC 30-Apr-19; GA Rev 2 approved 01-Oct-2019 '
             '(AOC revision distinct from approved revision). Design only.')


def ev(eid, region):
    return dict(evidence_id=eid, quote='', region=region)


FULL = [0.03, 0.05, 0.97, 0.97]


def pkg_grz():
    drive = ('Per-screen drive train (application data QTY 4 NOS, all EBD units): 2 nos exciter DF601V; '
             'cardan shaft assy Type-II + intermediate cardan shaft assy Type-II with guard; motor 55kW '
             '1500rpm; 10 nos front springs d27 (Cv 31.2, CH 12.5) + 14 nos rear springs d27, 50CrV4, on '
             'front/rear support structures and plates; 12 sets front/rear amplitude limiters (rubber); '
             'blind deck 20thk Tiscral/equivalent; grizzly bar assembly 50thk Mn steel casting; screen body. '
             'Operating RPM 725-800; separation 100mm; ROM coal 0.8/1.1, 1700/1870 TPH at PSH.')
    sup_drive = [ev('ev_b3c37ba7231443ef84bb', [0.62, 0.40, 1.0, 0.80]),
                 ev('ev_b3c37ba7231443ef84bb', [0.78, 0.10, 1.0, 0.42])]
    settings = ('Size selection: 0.75 sq.m per 100 TPH tender basis; 12.75 sq.m rated / 14.025 design; '
                'bar deck 5.39m x 2.7m = 14.55 sq.m + 1.5m blind deck + 0.2m lip = 7.09m total. Torque basis '
                '(Rev 001 calc): vibrating weight 17600kg + 1420kg (approx. 10% wet-coal allowance) = 19020kg gross; '
                'stroke 13mm primary; working moment 123.63 kg-m at 750rpm; starting HP 72.4 '
                '(C1 2, C2 1.15); required starting torque at motor shaft 64.39 kgf-m at 1440rpm; selected '
                '55kW motor rated 36 / starting 86.4 (240% FLT), 68.4 at 90% voltage; bulk density 1.1 T/cu.m (TCS '
                'reply c); feed adjust 40-100% by DF exciter unbalance weights (TCS reply f).')
    sup_set = [ev('ev_0062eb6d6a764351bb61', FULL), ev('ev_38c26247cadd4f978386', FULL),
               ev('ev_ff40a5dad7cf42e0b0d2', FULL)]
    ops = []
    for subj in [EBD1, EBD2, EBD3, EBD4]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=drive,
                        context=dict(kind='specification', basis=BASIS_GRZ + ' All four EBD units.'),
                        origin='explicit', confidence=0.9, evidence=sup_drive))
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=settings,
                        context=dict(kind='specification', basis=BASIS_GRZ + ' Selection + torque basis.'),
                        origin='explicit', confidence=0.9, evidence=sup_set))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9,
                    evidence=[ev('ev_ff40a5dad7cf42e0b0d2', FULL)],
                    text=('TCS 07-Jan-19 close-out: (a) 0.75 sq.m basis answered by selection sheet; (b) stroke '
                          'revised to 13mm primary / 12mm secondary (GA range note 11-13mm); (c) vibrating weight '
                          'is equipment + 10% wet-coal allowance at 1.1 T/cu.m; (d) torque shortfall comment (old '
                          'calc 55/105.6 vs motor 36/86.4) replied as revised calc, package approved 21-Jan-2019 '
                          '(top-model Q4 confirms: starting arithmetic closes; old rated figures superseded; Page 2 of 2 '
                          'of SO 200999 Rev 001 absent from the 4-page PDF is the deciding record for any separate '
                          'running-torque check); (e) spring constants incorporated '
                          'as d27/Cv/CH entries; (f) feed adjust via unbalance weights. Secondary-screen 12mm class '
                          'mapping outside EBD-1..4 per accepted Tier-1 mapping (all four EBD units are primary '
                          'screens); detailed spring-constant units and '
                          'P03 gate/actuator GAs not in corpus (gate logic taken from control write-up + TP3/PSH '
                          'hoist schedules instead).')))
    return dict(summary='EBD1-4 exciter/shaft/spring/liner detail, stroke/weight/torque basis, TCS close-out (grizzly GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record screen drive-train vendor data and TCS close-out',
                    questions=['What exciter/shaft/spring/liner detail, settings and torque basis apply to EBD1-4?'],
                    reviewed_evidence_ids=[], gaps=['Secondary-screen unit mapping; spring-constant units; P03 gate GAs.']))


def pkg_ctl():
    fg = ('Flap-gate travel trips: MCC disturbed, travel-end limit operated, torque limit operated, local stop. '
          'Conveyor-trip auto logic: conveyor off T1 10s changes FG position (forward if FG reverse and vice versa) '
          'and returns after T2 5s. Feeding-conveyor-trip logic: off T1 4hrs changes position, returns after T2 120s.')
    sup_fg = [ev('ev_ae22065dbd4145a4a7fd', FULL)]
    ops = [dict(op='assert', subject=FG1, predicate='operating_requirement', value=fg,
                context=dict(kind='specification', basis=BASIS_CTL + ' FG scheme, both TP3 gates.'),
                origin='explicit', confidence=0.9, evidence=sup_fg),
           dict(op='assert', subject=FG2, predicate='operating_requirement', value=fg,
                context=dict(kind='specification', basis=BASIS_CTL + ' FG scheme, both TP3 gates.'),
                origin='explicit', confidence=0.9, evidence=sup_fg),
           dict(op='assert', subject=UEF3, predicate='operating_requirement',
                value=('Flow divider positioned along length with AI 4-20mA position to DCS; stop command at '
                       'site-adjustable position; permissives and trips same as flap gate.'),
                context=dict(kind='specification', basis=BASIS_CTL + ' TP3 divider.'),
                origin='explicit', confidence=0.9, evidence=[ev('ev_8cf0f05229034667adb1', FULL)]),
           dict(op='assert', subject=UEE1, predicate='operating_requirement',
                value=('VGF at UEE-1: no auto-on/off except sequence; permissives electrical healthy, local reset, '
                       'respective belt conveyor ON, CBS clear; trips on electrical trip, conveyor OFF, CBS operated, '
                       'local stop. (VGF at UEE-3 permissives/trips read but out of Pass-2 scope.)'),
                context=dict(kind='specification', basis=BASIS_CTL + ' Screens feeder logic.'),
                origin='explicit', confidence=0.9, evidence=[ev('ev_8cf0f05229034667adb1', FULL)])]
    csu1 = ('CSU-1 (EAU-1, samples EAC-3A/3B): dedicated PLC, DCS start/stop, ASTM-D-2234; one auto pushbutton + local '
            'stations; cutter stuck between parkings trips preceding conveyor with MCR annunciation; coupling-failure '
            'fall protection via cutter-rotation timing; MCR signals CSU ON/OFF/Trip, Cutter-1/2 stuck, Cutter-1/2 parked. '
            'Equipment: primary sampler rotary-scoop x2 (control states "It consists of 30 kw motor" without specifying '
            'total vs per-unit, sheets 19-20); reversible '
            'belt feeder (2.2kW, VVVF, zero-speed + sway switches, reverse for bias with sampler only); hammer crusher '
            '(45kW, zero-speed); secondary sampler (2.2kW, proximity cycle); rotary collector (2.2kW, proximity + brake, '
            '60min cycle); reject screw (7.5kW continuous); slide gate (1.1kW, reverse-open/forward-close limit logic; '
            'control20 routes reject to EAC-4A closed / EAC-4B open while control21 (g) names EAC-3A with verbatim '
            '"when conveyor 2B runs then Slide gate will be open condition" typo preserved as internal conflict, '
            'top-model Q3).')
    csu2_note = ('CSU-2 outline reviewed on sheets 21-22 (samples EBA-18A/18B; primary sampler x2 15kW; reversible belt '
                 'feeder 1.5kW; hammer crusher 18.5kW; secondary sampler 2.2kW; reject screw to EBA-19A (gate closed) / '
                 'EBA-19B (gate open); bias mode feeder-reverse with sampler only; collector/screw/gate ratings past '
                 'sheet 22 not reviewed). Not asserted on any entity: CSU-2 is outside Pass-2 entity scope (no CSU-2 '
                 'system entity in corpus; EAU-2 units outside DQ-B11-001 target).')
    sup_csu = [ev('ev_726e1a50673047efb681', FULL), ev('ev_257cbf85b38f4ea6bf47', FULL),
               ev('ev_24a2c85d3aa9459c9a68', FULL)]
    sup_csu2 = [ev('ev_24a2c85d3aa9459c9a68', FULL), ev('ev_7a1df48bb94943439096', FULL)]
    ops.append(dict(op='assert', subject=SMP, predicate='operating_requirement', value=csu1,
                    context=dict(kind='specification', basis=BASIS_CTL + ' CSU-1 schedule, sheets 19-21.'),
                    origin='explicit', confidence=0.9, evidence=sup_csu))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.85, evidence=sup_csu2, text=csu2_note))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_csu,
                    text=('Reject-routing conflict within this control write-up, preserved: sheet-20 narrative routes '
                          'CSU-1 reject to EAC-4A (gate closed) / EAC-4B (gate open); sheet-21 items (f)/(g) name '
                          'EAC-3A/3B with verbatim "conveyor 2B" typo. Position A (4A/4B) governs by agreement with the '
                          'vendor system GA discharge conveyors (recorded under sampling-GA proposal); position B kept '
                          'as internal conflict. Deciding record: approved control-write-up revision closing the AOC '
                          'conditions, or PLC interlock logic diagram. Numeric PLC timer settings are stated adjustable '
                          'with no values printed: deciding record is the PLC program or loop-setting sheet.')))
    return dict(summary='FG/FD/divider/VGF logic + CSU-1/CSU-2 schedules with reject-routing conflict (control write-up)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record gate/divider/sampler control logic',
                    questions=['What FG/FD/VGF/CSU sequence logic applies at TP3 and the samplers?'],
                    reviewed_evidence_ids=[], gaps=['Numeric PLC timer values; CSU-2 sheets past 22; VGF UEE-3.']))


def pkg_c3():
    chart = [ev('ev_a2fbfdaf239949dc99e5', [0.78, 0.0, 1.0, 0.68])]
    key = [ev('ev_a2fbfdaf239949dc99e5', [0.15, 0.20, 0.55, 0.30])]
    pulleys = ('Pulleys (approved 26-Nov-2018): drive 800 dia x 2200 face, 1 no/conv, 12mm diamond-groove lagging; '
               'bend and snub 630 dia x 2200 face, 3 nos/conv, lagged; tail and take-up 630 dia x 2200 face, 2 nos/conv, '
               'lagged; deflector 219 dia face, 2 nos/conv, lagged.')
    idlers_a = ('Idlers/rollers EAC-3A: transition sets; impact sets 12 nos; carrying sets 151 nos; '
                'self-aligning carrying 11 nos; self-cleaning return 1 no at discharge pulley; return trough '
                'sets 46 nos; SA/FSA return sets; flat return rollers 2 nos at tail, head and take-up.')
    idlers_b = ('Idlers/rollers EAC-3B: transition sets; impact sets 12 nos; carrying sets 154 nos; '
                'self-aligning carrying 11 nos; self-cleaning return 1 no at discharge pulley; return trough '
                'sets 46 nos; SA/FSA return sets; flat return rollers 3 nos at tail, head and take-up.')
    prot = ('Protection key layout: belt sway switches both sides at 40m intervals, 5 pairs/conv; pull-cord switches '
            'both sides at 30m spacing, 5 pairs/conv; zero-speed switch on tail pulley, 1 no/conv.')
    struct = ('Skirt 14m, 20thk Hardox 400 with top cover; deck plate 3.15mm continuous; seal plate; vertical gravity '
              'take-up with mark-up scale; head frame with drive arrangement (motor-gearbox-scoop-brake line) and '
              'discharge hood; belt-curve/takeup zones as drawn.')
    ops = []
    sup_struct = chart + [ev('ev_c697bd5170dd485aa5fb', FULL)]
    for subj, tag, idlers in [(EAC3A, '3A', idlers_a), (EAC3B, '3B', idlers_b)]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=pulleys,
                        context=dict(kind='specification', basis=BASIS_C3 + ' EAC-%s.' % tag),
                        origin='explicit', confidence=0.95, evidence=chart))
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=idlers,
                        context=dict(kind='specification', basis=BASIS_C3 + ' EAC-%s idler counts.' % tag),
                        origin='explicit', confidence=0.95, evidence=chart))
        ops.append(dict(op='assert', subject=subj, predicate='operating_requirement', value=prot,
                        context=dict(kind='specification', basis=BASIS_C3 + ' EAC-%s switch layout.' % tag),
                        origin='explicit', confidence=0.95, evidence=key))
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=struct,
                        context=dict(kind='specification', basis=BASIS_C3 + ' EAC-%s skirt/takeup/head.' % tag),
                        origin='explicit', confidence=0.9, evidence=sup_struct))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=chart,
                    text=('Characteristics table corroborates Tier-1 belt/tension/coupling/brake/coasting/rope numerics '
                          '(not re-asserted). Piece-level idler/roller vendor BOM and drive foundation loads remain P3; '
                          'foundation loads live in the TP3/PSH tables.')))
    return dict(summary='EAC-3A/3B pulleys, idlers, protection layout, skirt/takeup/head details (conveyor-3 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record conveyor-3 internals and protection layout',
                    questions=['What pulley/idler/protection internals apply to EAC-3A/3B?'],
                    reviewed_evidence_ids=[], gaps=['Piece-level idler BOM (P3).']))


def pkg_tp3():
    sup_sched = [ev('ev_b82878abeca04c678b88', [0.10, 0.64, 0.62, 1.0])]
    hook = ('Hook schedule TP-3: H-1 and H-2, 2.5T, for EAC-3A/3B bend pulleys; H-3, 1T, CSU sampler crusher; H-4 and '
            'H-5, 1T, CSU belt feeder; H-6, 1T, CSU secondary sampler; H-7, 1T, CSU screw conveyor.')
    hoist = ('Hoist schedule TP-3: EH-1 10T lift 26.5m B.O.M.R. EL+26.500M for EAC-3A/3B head and snub pulleys + drive '
             'units; EH-2 5.5T/7.0m/EL+26.500M for 3A/3B head and snub; EH-3 4T/9.0m/EL+9.200M for EAC-4A/4B and EAC-13 '
             'tail pulleys; MH-1 3T/17.0m/EL+17.400M for 3A/3B take-up pulley frames; MH-2 1T/3.0m/EL+17.100M for CSU belt '
             'feeder and flow divider; MH-3 1.5T/9.0m/EL+9.200M for 3A/3B counterweight frames; MH-4 1T/5.0m/EL+13.300M '
             'for flap-gate KB-FG-1 and KB-FG-2 actuators. KB-FG-1/2 to FG-1/FG-2 identity is unconfirmed in reviewed '
             'sources; labels kept verbatim.')
    access = ('Structural/access close-out (TCS replies incorporated, approved 14-Dec-2018): take-up platforms with '
              'ladders at initial and final positions; 1100mm clear CSU passage at middle walkway; monorail routings '
              'revised for take-up/counterweight/CSU handling with MH-3 on the 3A/3B centreline; 800mm walkways with '
              'handrail; flow-divider space 4500x2000x2300mm; chutes supported four sides with beams; 30kN minimum '
              'live+dead load; member sizes indicated; CSU cutter outside transition zone; floor openings with removable '
              'grating or handrail; EAC-4A/4B tail floor EL 4.0M; take-up safety-mesh approach door.')
    sup_tcs = [ev('ev_0f63e72f0d0d44688285', FULL), ev('ev_19e572e4d4924f89834e', FULL),
               ev('ev_f906f6ca34b743f3b961', FULL), ev('ev_5d1e62f21be6476b9023', FULL)]
    csu = ('CSU mechanical loads at TP-3 (kgs static/dynamic per bolt unless noted): primary sampler +580/+750; '
           'garland idler +595/+760; belt feeder P3 +250 with +65/+115 horizontal at EL+14.100M, 10 nos; sample crusher '
           'P4 +200/+300; bias sample bin P5 +550 at EL+10.000M, 1 no; sample divider P6 +390/+175 at EL+10.000M, 4 nos; '
           'sample collector P7 +200/+250; screw conveyor P8 +300/+325 at EL+7.300M, 10 nos. Foundation load-per-footing '
           'table read for civil coordination.')
    sup_csu = [ev('ev_554896e3aff74e368515', [0.24, 0.72, 0.62, 0.92])]
    ops = [dict(op='assert', subject=UEF3, predicate='assembly_arrangement', value=hook,
                context=dict(kind='specification', basis=BASIS_TP3 + ' Maintenance hooks.'),
                origin='explicit', confidence=0.95, evidence=sup_sched),
           dict(op='assert', subject=UEF3, predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_TP3 + ' Hoists and monorails.'),
                origin='explicit', confidence=0.95, evidence=sup_sched),
           dict(op='assert', subject=UEF3, predicate='document_note', value=access,
                context=dict(kind='specification', basis=BASIS_TP3 + ' TCS close-out.'),
                origin='explicit', confidence=0.9, evidence=sup_tcs),
           dict(op='assert', subject=SMP, predicate='assembly_arrangement', value=csu,
                context=dict(kind='specification', basis=BASIS_TP3 + ' CSU loads at TP3.'),
                origin='explicit', confidence=0.9, evidence=sup_csu),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_tcs,
                    text=('Per-nozzle DFDS internals at TP3 need vendor sheets (P&ID UEF-3 AP-13..20 recorded under '
                          'P&ID proposal). KB-FG-1/2 versus FG-1/FG-2 identity unresolved: deciding record is the '
                          'actuator loop schedule or as-built label register. CSU load/elevation differences against '
                          'the vendor system GA are preserved, not overwritten: TP-3 GA 175035 (approved 14-Dec-2018) '
                          'lists feeder P3 at EL+14.100M with +65/+115 horizontal, divider P6 at EL+10.000M 4 nos '
                          '+390/+175, screw P8 at EL+7.300M 10 nos, while vendor system GA (FOR APPROVAL 2016) lists '
                          'F3 at EL+16.000M with (+)15 across, F5 at EL+11.600M 6 pts (+)35/(+)40, F7 at EL+10.000M '
                          '8 pts (recorded under sampling-GA proposal).'))]
    return dict(summary='TP-3 hook/hoist schedules, CSU loads, structural/access TCS close-out (TP3 GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record TP3 handling/structural/access detail',
                    questions=['What hoist/rail, CSU loads and access provisions apply at TP3?'],
                    reviewed_evidence_ids=[], gaps=['DFDS nozzle internals; KB-FG identity.']))


def pkg_sm():
    sup_p1 = [ev('ev_e71bf9537b084038a6eb', [0.03, 0.55, 0.45, 0.97]),
              ev('ev_e71bf9537b084038a6eb', [0.75, 0.05, 1.0, 0.97])]
    drives = ('ASSPL system drive detail (FOR APPROVAL, UEF-3): primary sampler geared brake 15.0kW x 2 nos, 160M, '
              '44rpm approx; belt feeder reversible geared 2.2kW x 1, 90L, 10rpm approx; crusher V-belt standard motor '
              '18.5kW x 1, 160L, 1440rpm approx; secondary sampler geared brake 0.37kW x 1, 71M, 15rpm approx; bottle '
              'collector geared brake 0.37kW x 1, 71M, 1.1rpm approx; screw feeder geared 2.2kW x 1, 100L, 29rpm approx; '
              'slide gate linear electrical actuator 0.25kW x 1. Basic parameters: feed EAC-3A/3B, coal 0.8 (VOL.) / 1.2 '
              '(POWER) (verbatim BULK DENCITY), '
              '3400 TPH rated, 100mm maximum top size, belt 2000mm at 3.5 m/s, 35deg troughing, discharge EAC-4A/4B. '
              'Chutes: sample ASI 409M 6thk, reject ASI 409M 6thk, flanges IS 2062 8thk, neoprene gaskets 6thk.')
    tcs = ('Vendor TCS resolutions (approved 07-Jan-2019): belt-feeder sway switch NOT required (short/slow feeder), PNP '
           'proximity doubles as zero/under-speed switch (#19/20/24); primary delivers 40kg per increment through 60deg '
           'chute (#22, preserved against system-GA 80.95 kg per increment); sampling-zone idlers are two 35deg 5-roll sets per side of cutter, confirmed (#25); sampler '
           'support from TP floor (#27); input lump 100mm (not 50), system designed for single AND both streams per '
           'Design Memorandum p49 either-of-two-conveyors (#30); motor ratings carry 20% margin over absorbed power, '
           'confirmed (#31); lot size and sample qty/hr incorporated with proximity + mechanical back-stop in BOM, no '
           'front/rear skirt curtain per standard (#32); screw trough MS 6mm standard, ONE slide gate suffices with '
           'run-conveyor selection logic (open to first-discharge conveyor, else closed to second opening) (#33); '
           'collector capacity/pan rpm/proximity incorporated (#34); crusher is Jeffrey import, MOC per Jeffrey (#35); '
           'feeder idler spacing finalised in detail engineering at most 1250mm, takeup travel incorporated (#36).')
    sup_tcs = [ev('ev_a1411e4e96e347ccacb5', FULL), ev('ev_7b5e4e598c5440e59b61', FULL)]
    screw = ('Screw feeder (251A-MECH-EQP-213-1): U-trough 7245mm, screw 230 dia, 29rpm approx, rated 3000 kg/hr on '
             '95%(-)8mesh/100%(-)4mesh feed, assembly 2400kgs, heaviest 200kgs; 2.2kW 100L 415V drive without brake; '
             'slide-gate arrangement with electrical actuator 0.25/0.55kW each; bearing units UCT211 SKF/FAG; proximity '
             'sensing wheel. Rated-capacity versus system 5100 kg/h and 2.2 versus control 7.5kW stay preserved on the '
             'EAU-1 screw entities (top-model Q2).')
    sup_screw = [ev('ev_4b615fb3d0ba40119a8f', FULL)]
    primary = ('Primary sampler (251A-MECH-EQP-112-1): sweep-arm type on 2000mm belt, EAC-3A/3B at 3400 TPH, cutter '
               'opening 300mm, 44rpm approx, 26 cuts/hr, assembly 3500kgs, heaviest 870kgs, lots 20400/3500 MT; 15kW '
               '160M drive; loads F1 4 pts (+)580/(+)750, F2 8 pts (+)585/(+)760; bearings 22222K SKF/FAG, shaft EN-8 dia100, '
               'cutter AISI-304 16thk with replaceable PU lip, skirts with 3thk AISI-304 liner; belt sway allowance '
               '100mm max per side, edge clearance 125mm.')
    sup_primary = [ev('ev_4b58f514a4284ab485ef', FULL)]
    small = ('Bottle collector (EQP-151-1): 4-station rotary, 40L x 4 AISI-304 containers, 1.1rpm, 800/200kgs, 0.37kW '
             '71M geared brake with shrink disc, 2 proximity switches; load F6 4pts +200/+250. Secondary sampler '
             '(EQP-135-1): rotary, 45mm cutter opening, enclosed, 200/80kgs, 0.37kW 1440rpm geared to 15rpm, 71M, '
              'AISI-304 cutter; load F5 6pts +35/+40. Belt feeder (EQP-211-1): 600mm reversible (preserved against '
              'system-GA 500mm width), 5100 kg/hr, 8780mm C/C, '
             '9.5 m/min, flat, 2500/300kgs; geared 2.2kW 1440rpm to 10rpm, 90L, without brake; 270x600 pulleys, 22212 '
             'bearings, screw take-up, VVVF-class speed range. Crusher (EQP-234-1): Jeffrey hammer mill, 5100 kg/hr, '
             '50mm/100mm feed, (-)8mesh 95% / (-)4mesh 100% output, 18.5kW 1440rpm 160L, 4 V-belts, 1000kgs assembly, '
             'load F4 8pts +200/+300.')
    sup_small = [ev('ev_bb7d9da36d3d44c7ac3a', FULL), ev('ev_ddd92dddbbfb4422aadd', FULL),
                 ev('ev_6b4953052c7343fbbef7', FULL), ev('ev_53403056417b468b8606', FULL)]
    ops = [dict(op='assert', subject=SMP, predicate='assembly_arrangement', value=drives,
                context=dict(kind='specification', basis=BASIS_SM + ' Vendor drive table + routing.'),
                origin='explicit', confidence=0.9, evidence=sup_p1),
           dict(op='assert', subject=SMP, predicate='document_note', value=tcs,
                context=dict(kind='specification', basis=BASIS_SM + ' TCS resolutions.'),
                origin='explicit', confidence=0.9, evidence=sup_tcs),
           dict(op='assert', subject=SMP, predicate='assembly_arrangement', value=screw,
                context=dict(kind='specification', basis=BASIS_SM + ' Screw feeder detail.'),
                origin='explicit', confidence=0.9, evidence=sup_screw),
           dict(op='assert', subject=SMP, predicate='assembly_arrangement', value=primary,
                context=dict(kind='specification', basis=BASIS_SM + ' Primary sampler detail.'),
                origin='explicit', confidence=0.9, evidence=sup_primary),
           dict(op='assert', subject=SMP, predicate='assembly_arrangement', value=small,
                context=dict(kind='specification', basis=BASIS_SM + ' Collector/secondary/feeder/crusher detail.'),
                origin='explicit', confidence=0.9, evidence=sup_small),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_p1 + sup_tcs,
                    text=('GA-vs-control rating table preserved (primary 15.0x2 vs 30; crusher 18.5 vs 45; secondary '
                          '0.37 vs 2.2; collector 0.37 vs 2.2; screw 2.2 vs 7.5; gate 0.25 vs 1.1; feeder 2.2 both): vendor '
                          '2016 FOR-APPROVAL supply versus BHEL 2020 AOC system schedule; TCS-31 confirms 20% margin on '
                          'vendor ratings. Deciding record is commissioning/as-built or approved vendor QA doc (top-model '
                          'Q2). BSS on belt feeder: control says provided, vendor TCS says not required with proximity '
                          'zero-speed instead (top-model Q2 confirms preserved). Internal vendor-package discrepancies '
                          'preserved, not overwritten: feeder width 500mm (system p1 DESIGN BASIS) vs 600mm (EQP-211-1); '
                          'increment 80.95kg (system p1) vs 40kg (TCS-22); primary loads F1/F2 as printed per sheet. '
                          'Sheets p2/p9 unreviewed; numeric PLC timer values not '
                          'printed anywhere reviewed.'))]
    return dict(summary='Sampling vendor GA drive table, equipment details, TCS resolutions, preserved rating table (sampling GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record sampling vendor supply data and TCS resolutions',
                    questions=['What drive ratings, capacities and TCS resolutions apply to the UEF-3 sampler?'],
                    reviewed_evidence_ids=[], gaps=['As-built ratings; PLC timer values; sheets p2/p9.']))


def pkg_u1():
    sup_views = [ev('ev_089deb0d6bdc4e548534', [0.0, 0.0, 0.62, 0.72]),
                 ev('ev_4571a8b4b9e341c4a1e3', [0.0, 0.0, 0.62, 0.72])]
    mapping = ('UEE-1 DFDS air/water station mapping (FIO layout Rev 2, verbatim tags per view): View 4-4: '
               'PAS-05/PRU-05 to EAC-2A; PAS-09/PRU-09 to EAC-2B; PFL legs. View 1-1: PAS-08/PRU-08 and PAS-07/PRU-07 '
               'both to ECA-3A [layout spelling]; PFL legs. View 3-3: FAS-6/PRU-6 to EBD-1; FAS-6A/PRU-6A to EBD-2; '
               'FAS-10/PRU-10 to EBD-3; FAS-10A with duplicate PRU-6A tag (copied from the EBD-2 branch) to EBD-4, '
               'against P&ID AP-10A PRU-10A/FAS-10A which governs (label conflict preserved, top-model Q1 corrected); '
               'FFL legs. View 2-2: PAS-11/PRU-11 and PAS-12/PRU-12 both to ECA-3B [layout spelling], confirmed by '
               'P&ID AP-11/AP-12; PFL legs. Headers 80NB air / 32NB water with 15NB water / 20NB air drops. FIO layout '
               'with TCS FIO-R revisions (FFL routing, FAS/PRU locations) outstanding.')
    sup_bom = [ev('ev_089deb0d6bdc4e548534', [0.60, 0.0, 1.0, 1.0]),
               ev('ev_4571a8b4b9e341c4a1e3', [0.60, 0.0, 1.0, 1.0])]
    bom = ('UEE-1 piping BOM (Rev 2): DFDS air 80/50/32/20NB pipe with elbows, tees, reducers, sockets and U-clamps; '
           'DFDS water 32NB 96m, 20NB 6m, 15NB 244m with 100 elbows, 61 unions, sockets and clamps; service water '
           '125NB 96m, 100NB 8m, 32NB 8m with 2 hose boxes and 4 QRC; potable galvanized 32NB 96m, 25NB 78m, 20NB 6m; '
           '64 nos 1/4in nozzles; 8 each 4/5/9-spray headers; PU tube 8mm OD 320m; BIB taps, angles and plates. The 64 '
           'nozzles equal the P&ID nozzle sum over PRU-05..12 (4+5+5+9+9+4+5+5+9+9). Pipe supports PS-1 13 nos, PS-2 10 '
           'nos, PS-3 5 nos, PS-4 10 nos.')
    sup_p1 = [ev('ev_f149acf086284e0994e8', [0.40, 0.15, 0.80, 0.65])]
    supply = ('Layout-scoped supply at UEE-1: service and potable water enter FROM PUMP HOUSE-2 (layout lower level); '
              'local SW extensions are 2 hose boxes + 4 QRC with 125/100/32NB distribution; potable galvanized branches '
              '32/25/20NB. DFDS air/water plant location is outside these layout sheets (P&ID scope, recorded under P&ID '
              'proposal). UEE-1 as drawn is a flow-through screens house; no storage bins on these sheets.')
    ops = [dict(op='assert', subject=UEE1, predicate='assembly_arrangement', value=mapping,
                context=dict(kind='specification', basis=BASIS_U1 + ' Station mapping.'),
                origin='explicit', confidence=0.85, evidence=sup_views),
           dict(op='assert', subject=UEE1, predicate='assembly_arrangement', value=bom,
                context=dict(kind='specification', basis=BASIS_U1 + ' Piping and nozzle BOM.'),
                origin='explicit', confidence=0.9, evidence=sup_bom),
           dict(op='assert', subject=UEE1, predicate='document_note', value=supply,
                context=dict(kind='specification', basis=BASIS_U1 + ' Supply reconciliation.'),
                origin='explicit', confidence=0.85, evidence=sup_p1)]
    receipts = [(EBD1, 'EBD-1 from FAS-6/PRU-6, AP-06, 5 nozzles (layout View 3-3).'),
                (EBD2, 'EBD-2 from FAS-6A/PRU-6A, AP-06A, 5 nozzles (layout View 3-3).'),
                (EBD3, 'EBD-3 from FAS-10/PRU-10, AP-10, 5 nozzles (layout View 3-3).'),
                (EBD4, 'EBD-4 from FAS-10A, AP-10A, 5 nozzles; layout PRU tag reads PRU-6A duplicating the '
                       'EBD-2 unit, against P&ID PRU-10A which governs (conflict preserved, top-model Q1 corrected).')]
    for subj, txt in receipts:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value='DFDS dry-fog receipt: ' + txt,
                        context=dict(kind='specification', basis=BASIS_U1 + ' Per-screen receipt.'),
                        origin='explicit', confidence=0.85, evidence=sup_views))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.85, evidence=sup_views + sup_p1,
                    text=('P&ID AP-01..AP-04 (PRU-01..04) serve UEF-1 transfer points per P&ID Sl. No. 1 (recorded under '
                          'P&ID proposal on the UEF-1 entity), hence absent from the UEE-1 layout sheets. P&ID AP-10A '
                          'PRU-10A governs the EBD-4 tag over the FIO layout duplicate pending a later '
                          'approved layout revision or loop-check record.')))
    return dict(summary='UEE-1 DFDS station mapping, piping/nozzle BOM with 64-count reconciliation, supply split (UEE-1 piping)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record UEE-1 DFDS installation scope',
                    questions=['How is DFDS/SW/PW laid out and supplied at UEE-1?'],
                    reviewed_evidence_ids=[], gaps=['EBD-4 PRU tag deciding record; PRU-01..04 on UEF-1 entity.']))


def pkg_pid():
    sup_uee1 = [ev('ev_08ec0122d044468d8975', FULL), ev('ev_02ba8d819eac482f9cc9', FULL),
                ev('ev_a6d89effc78d46bab679', FULL)]
    uee1 = ('UEE-1 DFDS System-1 application points, Sl. No. 2 Primary Screen House (approved P&ID, 10 points, '
            '64 nozzles): AP-05 EAC-2A discharge 4/4 PRU-05/FAS-05; AP-06 screen EBD-1 5/5 PRU-06/FAS-06; AP-06A screen '
            'EBD-2 5/5 PRU-06A/FAS-06A; AP-07 EAC-3A receipt 9/9 PRU-07/FAS-07; AP-08 EAC-3A receipt 9 total / 0 operating '
            'PRU-08/FAS-08; AP-09 EAC-2B discharge 4/4 PRU-09/FAS-09; AP-10 screen EBD-3 5/5 PRU-10/FAS-10; AP-10A screen '
            'EBD-4 5/5 PRU-10A/FAS-10A; AP-11 EAC-3B receipt 9/9 PRU-11/FAS-11; AP-12 EAC-3B receipt 9 total / 0 operating '
            'PRU-12/FAS-12. Both PRU-11 and PRU-12 genuinely serve EAC-3B (two receipt points, mirroring AP-07/AP-08 on '
            'EAC-3A); AP-08 and AP-12 are standby points.')
    uef1 = ('UEF-1 DFDS System-1 application points, Sl. No. 1 (approved P&ID, 4 points, 26 nozzles): AP-01 EAC-1A '
            'discharge 4/4 PRU-01/FAS-01; AP-02 EAC-2A receipt 9/9 PRU-02/FAS-02; AP-03 EAC-1B discharge 4/4 '
            'PRU-03/FAS-03; AP-04 EAC-2B receipt 9/9 PRU-04/FAS-04.')
    ebd4 = ('P&ID-side corroboration for EBD-4 (top-model Q1 corrected): AP-10A allocates PRU-10A/FAS-10A, 5 total / 5 '
            'operating nozzles, and governs over the FIO layout duplicate PRU-6A tag (preserved under UEE-1 piping '
            'proposal) pending approved layout revision or loop-check record.')
    uef3 = ('UEF-3 DFDS points: AP-13 EAC-3A discharge 4/4 PRU-13/FAS-13; AP-14 EAC-4A receipt 9/9 PRU-14/FAS-14; '
            'AP-15 EAC-4B receipt 9/0 PRU-15/FAS-15; AP-16 EAC-13 from 3A 9/0 PRU-16/FAS-16; AP-17 EAC-3B discharge 4/4 '
            'PRU-17/FAS-17; AP-18 EAC-4A receipt 9/9 PRU-18/FAS-18; AP-19 EAC-4B receipt 9/0 PRU-19/FAS-19; AP-20 EAC-13 '
            'from 3B 9/0 PRU-20/FAS-20; 62 nozzles over 8 points. '
            'PRU regulates air and water pressure per header group; FAS holds the activation solenoids; typical '
            'arrangements for PRU, FAS and air-atomizing nozzle as drawn.')
    sup_uef3 = [ev('ev_a6d89effc78d46bab679', FULL), ev('ev_5bfb0b3f7efe4b938282', FULL)]
    ops = [dict(op='assert', subject=UEE1, predicate='assembly_arrangement', value=uee1,
                context=dict(kind='specification', basis=BASIS_PID + ' UEE-1 application points.'),
                origin='explicit', confidence=0.95, evidence=sup_uee1),
           dict(op='assert', subject='ent_108b99f6c64844df8cf8', predicate='assembly_arrangement', value=uef1,
                context=dict(kind='specification', basis=BASIS_PID + ' UEF-1 application points.'),
                origin='explicit', confidence=0.95, evidence=[ev('ev_08ec0122d044468d8975', FULL)]),
           dict(op='assert', subject=EBD4, predicate='assembly_arrangement', value=ebd4,
                context=dict(kind='specification', basis=BASIS_PID + ' EBD-4 P&ID-side corroboration.'),
                origin='explicit', confidence=0.95, evidence=[ev('ev_a6d89effc78d46bab679', FULL)]),
           dict(op='assert', subject=UEF3, predicate='assembly_arrangement', value=uef3,
                context=dict(kind='specification', basis=BASIS_PID + ' UEF-3 application points; nozzle/valve scope.'),
                origin='explicit', confidence=0.9, evidence=sup_uef3),
           dict(op='source_note', origin='explicit', confidence=0.95, evidence=sup_uee1,
                    text=('P&ID AP-10A PRU-10A/FAS-10A for EBD-4 governs tagging over the FIO layout duplicate PRU-6A '
                          'pending later approved revision (top-model Q1). Per-nozzle internal piece detail needs vendor '
                          'sheets; UEF-4..7 and future-UEF points are outside Pass-2 scope.'))]
    return dict(summary='UEE-1 10-point, UEF-1 4-point and UEF-3 8-point DFDS application tables with standby points (DFDS P&ID)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record DFDS application allocation',
                    questions=['Which PRU/FAS points and nozzle counts serve UEE-1 and UEF-3?'],
                    reviewed_evidence_ids=[], gaps=['Vendor nozzle internals; other houses.']))


def pkg_psh():
    sup_p2 = [ev('ev_5c320e9f04fb44359bb8', [0.22, 0.78, 0.60, 1.0])]
    hoist = ('Hoist schedule PSH: EH-1 10T lift 24.5m at +20.000M for EAC-2A/2B drive units; EH-2 10T/17.5m/+18.600M for '
             'EBD-1 and EBD-3 and drive; EH-3 10T/17.5m/+18.600M for EBD-2 and EBD-4 and drive; EH-4 5.5T/24.5m/+20.000M '
             'for EAC-2A/2B head and snub pulleys; MH-1 3T/17.5m/+18.500M for 2A/2B take-up pulley; MH-2 10T/18.0m/+18.400M '
             'for 2A/2B counterweight frames; MH-3 2T/3.5m/+8.800M for 2A/2B tail pulleys; MH-4 1T/18m/+18.600M for rotary '
             'actuator of SR and F gate; hooks H-1 and H-2 2T for EAC-2A/2B bend pulleys.')
    forces = ('Screen support forces F1/F2/F3 (kgf, static / operating / start-stop with 12.5 Hz operating and 2-4 Hz '
              'start-stop frequency, about 30 load cycles): F1 vertical 7400 / +-660 / +-5280, horizontal +-410 / +-3280; '
              'F2 vertical 4500 / +-440 / +-3520, horizontal +-340 / +-2720; F3 800.')
    sup_p1 = [ev('ev_c42a2d9b6f2f4e45afc7', FULL)]
    tcs = ('PSH TCS close-out (Rev 2 AOC 30-Apr-19, approved 01-Oct-2019): VSF-coordination observations noted with '
           'drawing revised per approved VSF GA; MH-2 monorail U-type (not straight) for counterweight eccentric '
           'handling; building entrance relocated for 2-5% oversize dumping (34 TPH per stream at 2%); 800mm clear '
           'handrail to motor belt guard; monorail routings revised clear of structural columns. Corroborates existing '
           'Tier-1 coordination records without re-asserting them.')
    sup_p3 = [ev('ev_af0fecd628d5428d906a', FULL)]
    ops = [dict(op='assert', subject=UEE1, predicate='assembly_arrangement', value=hoist,
                context=dict(kind='specification', basis=BASIS_PSH + ' Handling schedule.'),
                origin='explicit', confidence=0.95, evidence=sup_p2),
           dict(op='assert', subject=UEE1, predicate='assembly_arrangement', value=forces,
                context=dict(kind='specification', basis=BASIS_PSH + ' Screen support forces.'),
                origin='explicit', confidence=0.9, evidence=sup_p2 + sup_p1),
           dict(op='assert', subject=UEE1, predicate='document_note', value=tcs,
                context=dict(kind='specification', basis=BASIS_PSH + ' TCS close-out.'),
                origin='explicit', confidence=0.9,
                evidence=sup_p3 + [ev('ev_c42a2d9b6f2f4e45afc7', FULL), ev('ev_5c320e9f04fb44359bb8', FULL)]),
           dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup_p2,
                    text=('PSH force table corroborates the grizzly GA force table (doc_b4cf0a76c954435aadd6) with '
                          'identical F1/F2/F3 figures.'))]
    return dict(summary='PSH hoist schedule, screen support forces, TCS close-out (PSH GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record PSH handling and structural coordination',
                    questions=['What hoists, forces and TCS outcomes apply at PSH/UEE-1?'],
                    reviewed_evidence_ids=[], gaps=[]))


PACKAGES = [(DOC_GRZ, pkg_grz, 'grz', 732), (DOC_CTL, pkg_ctl, 'ctl', 733),
            (DOC_C3, pkg_c3, 'c3', 734), (DOC_TP3, pkg_tp3, 'tp3', 735),
            (DOC_SM, pkg_sm, 'sm', 736), (DOC_U1, pkg_u1, 'u1', 737),
            (DOC_PID, pkg_pid, 'pid', 738), (DOC_PSH, pkg_psh, 'psh', 739)]


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
        assert base_version == 731, base_version
    running = base_version if not args.apply else 731
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
