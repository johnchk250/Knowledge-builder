"""Pass-1 completion packages (DQ-B06-001, DQ-B07-001, DQ-B08-001 remainder).

Locally reviewed (OCR text + visual crops) after the pilot round (v719/v720).
Nine one-source proposals, chained v720 -> v729. Default: isolated rehearsal
in pass-01-complete/rehearsal-copy; --apply performs guarded live acceptance.
"""
import argparse
import json
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = ROOT / 'output/plant-enrichment/pass-01-complete'
COPY = BASE / 'rehearsal-copy'
DOC_SEL = 'doc_60a920124be746f680ed'
DOC_CTL = 'doc_4f2cd96c3b1e413ea4b5'
DOC_GA = 'doc_030c8f82fb674548a4dc'
DOC_CPL = 'doc_7aa49cc0d1c34af7ac06'
DOC_BRK = 'doc_64825298f3d243368408'
DOC_DBR = 'doc_cd1aae66b455491b8883'
DOC_GBX = 'doc_35760c2e577d448b9c2b'
DOC_BUF = 'doc_d4314eb6930c4125b7a1'
DOC_LUB = 'doc_e3b865395f8640be9b3f'

EAC2A = 'ent_91dd763af7f4417ebaa6'
EAC2B = 'ent_f4dc6c5b38d14bceb5e5'
SUL1 = 'ent_1a57e15407c145a19284'
SUL2 = 'ent_f319b7a72a2e4c85a617'
SUL3 = 'ent_9b33c14cee7f4d749335'
CPL_A = 'ent_1c7c6ca22fc149fe9e58'
CPL_B = 'ent_44f4d1c3f0c94d5e8afb'
BRK_A = 'ent_d1f708b6949e4db0b9d0'
BRK_B = 'ent_4a03a026372a4a5d9ab4'

SEL_EVS = ['ev_736467b085914fce8fc3', 'ev_76ab6c07eee84180a3f1', 'ev_136d213579a945e7b55d',
           'ev_bf7478ff412944a2a9b5', 'ev_e4150068d5534911a3b5', 'ev_61eac3afab45445eaae0',
           'ev_a67e3da13eeb4124a757', 'ev_45375f83fcc8495fab9e']
CTL_EVS = ['ev_f2fd7725711f42e0993a', 'ev_a4478424942b446d891b', 'ev_7572c227d4fe482a8f58',
           'ev_5455b622b03e49e39c24']

BASIS_SEL = ('175052 Selection of drive components, brakes and belts for conveyors, approved 23-Nov-2018; '
             'EAC-2AB column. Design only.')
BASIS_CTL = ('Control write-up IS-4-CW-702-101-E914 Rev04 26.03.2020, AOC 06-Apr-2020. Design only.')
BASIS_GA = ('175012 GA Rev 2 29.10.18 FOR APPROVAL, schedule column p2. Design only.')
BASIS_CPL = ('Scoop coupling GA/circuits 19-Feb-2019 approved. Design only.')
BASIS_BRK = ('EBTM brake GA R2 FOR APPROVAL, BTL EPC. Design only.')
BASIS_DBR = ('Ship unloader DBR POC-771, AOC 13-Jul-2020. Design only.')
BASIS_GBX = ('Gearbox GA MAITREE-00-MG-DA-175181-ISG-TENOVA, FIO 28-Jan-2021. Design only.')
BASIS_BUF = ('Rail-fixing replies 19-Aug-2020 on 175194 Rev 4, FIO rail drawings. Design only.')
BASIS_LUB = ('SUL grease lubrication system docs, Lincoln two-line, FIO 26-Mar-2021. Design only.')


def ev(eid, region):
    return dict(evidence_id=eid, quote='', region=region)


def pkg_sel():
    col = ('EAC-2AB selection column. Gearbox: PA 296kW, PM 380kW, N0 1488rpm, V 3.5m/s, D 800mm, '
           'lagging 12mm, bevel-helical triple, s=1.5, f1=1.2, f2=1.07, f3=0.7, Premium make; R Mech 532.80kW, '
           'f2*PM 406.60, max 532.80; R Thrm 542.86kW; N1 81.12rpm; i 18.3, iN 17.1, iNi 17.82; size B3-450; '
           'mech rating 909kW, thermal 712kW; fan-cooled YES; holdback YES. Belt: Tmax 29596lb/131693N, '
           'T1S 35628lb/158534N, BW 2000mm, running 65.847kN/m, starting 79.267kN/m, continuous duty, '
           'NN1000/5, FOS 10, cover FR 5/2, RMBT 100kN/m, 5 ply, 13.40mm, 33.24kg/m; min drive 630 / non-drive '
           '500 / snub 400mm; selected drive 800 / non-drive 630 / snub 630mm. High-speed coupling: scoop '
           'type, PST-530, 380kW@1500rpm, brake drum dia 500mm, Premium. Low-speed coupling: geared RG-10, '
           '1150HP/100RPM, torque 8234kg-m, max bore 220mm, min 100mm, GBM. Brake: required 373.5kg-m; '
           'selected EBTM-500/DS/DG, 440kg-m, drum 500mm.')
    sup = [ev('ev_736467b085914fce8fc3', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_76ab6c07eee84180a3f1', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_136d213579a945e7b55d', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_bf7478ff412944a2a9b5', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_e4150068d5534911a3b5', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_61eac3afab45445eaae0', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_a67e3da13eeb4124a757', [0.03, 0.08, 0.97, 0.95]),
           ev('ev_45375f83fcc8495fab9e', [0.03, 0.08, 0.97, 0.60])]
    ops = []
    for subj, lane in [(EAC2A, 'EAC-2A'), (EAC2B, 'EAC-2B')]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=col,
                        context=dict(kind='specification', basis=BASIS_SEL + ' Applicability: %s only.' % lane),
                        origin='explicit', confidence=0.98, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.98,
                    evidence=[ev('ev_45375f83fcc8495fab9e', [0.03, 0.08, 0.97, 0.60])],
                    text=('175052 review replies: gearboxes per exact ratio; motor rating with 20% margin and '
                          'higher shaft power (selection ok); thermal rating revised; B3-500 force-lubricated; '
                          'belt ratings 4A/B 1250/5 etc. Motor piece internals (winding/bearing/seal data for the '
                          '380kW TEFC 1488rpm motor) have no vendor datasheet in the corpus; need the motor vendor '
                          'datasheet. Transferred as P3 vendor-BOM gap.')))
    return dict(summary='EAC-2A/B drive selection basis: gearbox, belt, couplings, brake (175052)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record the calculation-backed drive selection for conveyor 2',
                    questions=['What gearbox/belt/coupling/brake selection supports the EAC-2 drives?'],
                    reviewed_evidence_ids=SEL_EVS,
                    gaps=['Selection pp2-5 read as OCR text cross-checked across blocks; TCS p5 read. Remaining '
                          '175052 pages are other conveyors or repeats. Motor vendor internals need the motor datasheet.']))


def pkg_ctl():
    logic = ('Conveyor protection logic applied to this lane (generic clauses, per-conveyor counts from the GA '
             'schedule: PCS 4 pairs/30m, BSS 3 pairs/40m, ZSS 1 on tail). Scoop-coupling oil pump: auto-starts '
             'with conveyor command, auto-stops 30s (adjustable) after motor off; permissives: radiator motor ON, '
             'oil temperature normal, local stop reset, electrical healthy. Scoop engage (OUT) permissives (12): '
             'oil pump ON, main motor ON, both CBS not operated, PCS/BSS not operated, electrical healthy, brake '
             'released, succeeding conveyor motor on, scoop engaged, flap/shuttle drive in position, same-conveyor '
             'positioning rule, local stop reset. Disengage (IN) trips: CBS/PCS/BSS operated. Conveyor trips: '
             'electrical trip, PCS, BSS, ZSS with 60s on-delay, CBS, succeeding conveyor stopped, local stop. '
             'Zero-speed senses <85% rated speed. MD-1/MD-2 and EAT-1/EAT-2 already modeled on these lanes with '
             'their own control logic; retained.')
    sup = [ev('ev_a4478424942b446d891b', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_7572c227d4fe482a8f58', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_f2fd7725711f42e0993a', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_5455b622b03e49e39c24', [0.03, 0.05, 0.97, 0.60])]
    ops = []
    for subj, lane in [(EAC2A, 'EAC-2A'), (EAC2B, 'EAC-2B')]:
        ops.append(dict(op='assert', subject=subj, predicate='operating_requirement', value=logic,
                        context=dict(kind='specification', basis=BASIS_CTL + ' Applicability: %s only.' % lane),
                        origin='explicit', confidence=0.98, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.98,
                    evidence=[ev('ev_a4478424942b446d891b', [0.03, 0.05, 0.97, 0.97])],
                    text=('Unloader-specific protection/anti-collision/storm-parking logic searched in the control '
                          'write-up (storm/anti-collision/slew/luffing: zero hits; travel/limit/interlock hits are '
                          'tripper/gate/slide-gate/sampler context) and is absent from the DBR beyond drive '
                          'arrangement. Need: unloader PLC/IO list and anti-collision sensor datasheet. Recorded as '
                          'evidence gap.')))
    return dict(summary='EAC-2A/B protection-logic application; unloader logic gap (control write-up)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Apply generic protection clauses to conveyor 2; record unloader logic search',
                    questions=['What protection/trip logic governs EAC-2A/B?', 'Where is unloader protection logic stated?'],
                    reviewed_evidence_ids=CTL_EVS,
                    gaps=['pp4/9/28/29 read as OCR text. Remaining control pages are other equipment sections. '
                          'Unloader travel/anti-collision logic not in this source.']))


def pkg_ga_rows():
    sup_p = [ev('ev_e681c2f0a7c64430b4c4', [0.78, 0.28, 0.97, 0.46])]
    sup_i = [ev('ev_e681c2f0a7c64430b4c4', [0.78, 0.46, 0.97, 0.72])]
    sup_b = [ev('ev_e681c2f0a7c64430b4c4', [0.78, 0.72, 0.97, 0.96])]
    sched = ('PULLEYS as printed: drive pulleys 800 dia x 2200 face x 2700 bearing centres, 12mm diamond-groove '
             'rubber lagging, qty 1 per conveyor; tail/bend/snub combined group 630mm dia, qty 4 per conveyor; '
             'T-U pulley 630mm; deflector roller 219 dia x 2200 face, rubber lagging.')
    idlers = ('IDLERS as printed: transition 3-roll 10deg trough; impact group; carrying 3-roll 35deg trough at '
              '1500mm pitch; machined idler group; non-magnetic 1-roll 35deg; self-aligning carrying and return '
              'groups; return 10deg trough 3000mm pitch; flat return roller near head end and take-up. Individual '
              'roller counts are vendor BOM rows (P3); not asserted piece by piece.')
    bottom = ('Schedule bottom rows as printed: take-up vertical gravity with mark-up scale, travel 3700mm; '
              'counterweight 8100kg per conveyor; belt protection devices BSS both sides 40m interval 3 pairs, '
              'PCS both sides 30m spacing 4 pairs, ZSS on tail pulley 1 no per conveyor; EX scraper spring-loaded '
              'primary + secondary at discharge pulley; INT scraper V-plough near tail pulley; chute plate 10mm '
              'HARDOX 400 on non-impact sides, 20mm on impact sides; skirt board 52m 20thk HARDOX; deck plate '
              '3.15thk continuous.')
    kids = {'head': ('head drive pulley', sup_p, sched), 'tails': ('tail and bend/snub pulley group', sup_p, sched),
            'support': ('idler and belt-support assembly', sup_i, idlers),
            'chute': ('screening discharge chute', sup_b, bottom), 'protection': ('PCS BSS and ZSS protection group', sup_b, bottom)}
    order = ['head', 'tails', 'support', 'chute', 'protection']
    ops = []
    import sqlite3 as _sq
    _con = _sq.connect(ROOT / 'data/plant/plant.sqlite3')
    for lane, lent in [('A', EAC2A), ('B', EAC2B)]:
        for key in order:
            label, sup, val = kids[key]
            eid = _con.execute("SELECT subject FROM assertions WHERE object_entity=? AND predicate='part_of'", (lent,)).fetchall()
            match = None
            for (sid,) in eid:
                lab = _con.execute('SELECT label FROM entities WHERE id=?', (sid,)).fetchone()
                if lab and label.lower() in lab[0].lower():
                    match = sid
                    break
            assert match, (lane, key)
            ops.append(dict(op='assert', subject=match, predicate='assembly_arrangement', value=val,
                            context=dict(kind='specification', basis=BASIS_GA + ' Applicability: EAC-2%s only.' % lane),
                            origin='explicit', confidence=0.98, evidence=sup))
    _con.close()
    ops.append(dict(op='source_note', origin='explicit', confidence=0.98,
                    evidence=[ev('ev_e681c2f0a7c64430b4c4', [0.78, 0.46, 0.97, 0.72])],
                    text=('Idler schedule rows recorded as printed groups; per-roller piece counts and vendor BOM '
                          'rows below the maintainable assembly are P3 depth, not asserted here.')))
    return dict(summary='EAC-2A/B GA schedule rows: pulleys, idlers, bottom rows (175012 p2)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Capture printed GA schedule rows per assembly group',
                    questions=['What pulley/idler/protection rows does the EAC-2 schedule print?'],
                    reviewed_evidence_ids=['ev_e681c2f0a7c64430b4c4'],
                    gaps=['p2 schedule column visually reviewed in full-page render; rows transcribed as printed '
                          'groups. Individual roller counts are P3.']))


def pkg_cpl():
    circ = ('Scoop-coupling control circuit provisions (legends, default/unactuated): travel limits TLO/TLC '
            '(open/disengage, close/engage), overload limits OLO/OLC; oil temperature switches TS1 (inlet) / TS2 '
            '(outlet), oil pressure switch PS (inlet), differential pressure switch DPS across filter, oil flow '
            'switch FSO at circulating-pump outlet. Matches the control p28 engage/disengage + oil-pump logic at '
            'device level. Panel data (500 PST panel: IP65, 75kg, 350W control power, 25x3mm ground bus) is panel '
            'rated 500 PST while EAC-2 units are PST-530: panel applicability to EAC-2 unconfirmed, logic only.')
    sup = [ev('ev_f9eb53dcfb4c47269566', [0.03, 0.05, 0.97, 0.95]),
           ev('ev_7ef524566aa3476db2bb', [0.03, 0.05, 0.97, 0.95])]
    ops = []
    for subj in [CPL_A, CPL_B]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=circ,
                        context=dict(kind='specification', basis=BASIS_CPL + ' Circuit logic applies to scoop '
                                     'couplings; panel rating applicability qualified above.'),
                        origin='explicit', confidence=0.9, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup,
                    text=('Scoop tube/impeller/seal piece internals are vendor BOM detail (P3); need the coupling '
                          'vendor mechanical GA/data sheet. Panel-to-EAC-2 applicability needs the EAC-2 panel '
                          'schedule.')))
    return dict(summary='EAC-2 scoop-coupling circuit legends; panel applicability qualified (coupling GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record coupling protection-circuit provisions',
                    questions=['What protection switching does the scoop-coupling circuit provide?'],
                    reviewed_evidence_ids=['ev_f9eb53dcfb4c47269566', 'ev_7ef524566aa3476db2bb'],
                    gaps=['pp13-14 legends read; remaining coupling GA pages are panel/mechanical drawings. Piece '
                          'internals P3.']))


def pkg_brk():
    bom = ('EBTM electro-hydraulic thruster brake family BOM pattern (500/F sheet, family design): thruster '
           'ET-3150/TL 68kg thrust, 75mm stroke, 415V, 375W; main spring SP steel; shoes CI GR-14 with non-asbestos '
           'liners (200C), shoe width 180mm, drum dia 500; spring-pressure adjustment nut; lever/tie-rod/pins; '
           'shoe clearance + brake-stop bolts; base/legs; JAI BALAJI 45-18 + 2NO+2NC limit switch for brake release; '
           'transformer oil IS:335 EHV. Variant guard: this sheet tabulates EBTM-500/F for EBA rows (req 265kg-m, '
           'max 290); EAC-2 selection is EBTM-500/DS/DG at 373.5 req / 440 max / drum 500 (selection doc). BOM piece '
           'values cited as the F-variant pattern, not EAC-2 DS/DG piece values.')
    sup = [ev('ev_95dd459df70f48db8a29', [0.03, 0.05, 0.97, 0.95])]
    ops = []
    for subj in [BRK_A, BRK_B]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=bom,
                        context=dict(kind='specification', basis=BASIS_BRK + ' Family pattern; variant guard above.'),
                        origin='explicit', confidence=0.85, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup,
                    text=('Brake GA p1 render file is unreadable on disk (evidence record exists); EAC-row table '
                          'values come from the selection doc instead. Need: legible p1 or the EBTM-500/DS/DG data '
                          'sheet for EAC-2 piece values.')))
    return dict(summary='EBTM brake family BOM pattern with F vs DS/DG variant guard (brake GA p2)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record brake internals at BOM-pattern level',
                    questions=['What internals does the EBTM brake expose?'],
                    reviewed_evidence_ids=['ev_95dd459df70f48db8a29'],
                    gaps=['p2 visually reviewed. p1 render file unreadable; EAC rows via selection doc. Piece '
                          'values for DS/DG need its data sheet.']))


def pkg_dbr():
    arr = ('Ship unloader drive arrangement (Type 1 + Type 2, POC-771): hold/close, trolley traverse, discharge '
           'conveyor: motor VVVF + disc brake + reducer + drum coupling + rope drum (boom hoist adds emergency '
           'brake); long travel: geared brake motors VVVF on wheel axle; discharge conveyor motor RDOL + drum brake '
           '+ fluid coupling + reducer; shuttle conveyor: geared brake motor VVVF on wheel axle. Duty classes: '
           'steel B8-P3-E8; hold/close, traverse, discharge T9-L4-M6... [T9-L4-M8]; boom hoist T5-L3-M6; long travel '
           'T6-L3-M7. Wind: operation 16m/s (157N/m2), positioning 18m/s (199), out-of-service 73m/s (3267). Rail '
           'CR100, gauge 20000mm, max wheel load 50t; berth 540m; vessels 3-10k DWT barges, 10-25k DWT ships; '
           'coal 1.0/1.4t/m3, limestone bulk 0.8/load 1.4; free digging coal 1700 / limestone 1000 t/h.')
    sup = [ev('ev_33262138211444af8553', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_9cf7a4b7dc0d4a58aca9', [0.03, 0.05, 0.97, 0.97])]
    ops = []
    for subj in [SUL1, SUL2, SUL3]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=arr,
                        context=dict(kind='specification', basis=BASIS_DBR + ' DBR covers Type 1 and Type 2; '
                                     'per-machine applicability retained.'),
                        origin='explicit', confidence=0.95, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.95, evidence=sup,
                    text=('DBR states arrangement/duty/wind/rail only; numeric protection settings, anti-collision '
                          'logic and travel-limit wiring are not in the DBR. See control gap note.')))
    return dict(summary='Ship unloader drive arrangement, duty classes, wind/rail basis (DBR pp2-3)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record DBR drive/duty basis for all three unloaders',
                    questions=['What drive arrangement and duty classes do the unloaders use?'],
                    reviewed_evidence_ids=['ev_33262138211444af8553', 'ev_9cf7a4b7dc0d4a58aca9'],
                    gaps=['pp2-3 read. pp1/4+ are title/structural criteria, retained as reference.']))


def pkg_gbx():
    data = ('Grab hold/close gearbox SPL H3-630 (Premium, 6 nos total): motor installed 630kW, absorbed RMS '
            '477.5kW, peak 773kW, input 994-1350rpm, mechanical rating 1002kW, nominal ratio 31.4:1, actual '
            '32.234:1, SF 1.29 installed/RMS/peak-min, efficiency 97.5%, ISO VG320 splash 460L, SKF/FAG bearings '
            '80000h life, ambient 45C, thermal 700kW@45C, 85dB@1M, mechanism duty T9-L4-M8 FEM, fan cooling, '
            'EXTRA HEAVY DUTY 24hrs. Stages/pinions tabulated; seals, painting, materials (gears 18CrNiMo7-6 '
            '58-62HRc, output EN24T, casing E250). Index allocates 7 sheets: hold/close, trolley traverse + section, '
            'boom hoist, shuttle conveyor, long-travel geared motor, shuttle-travel geared motor. Matches the '
            'accepted SUL-2 2x630kW holding/closing record; asserted for Type 1 (SUL-1/SUL-2). FIO qualification.')
    sup = [ev('ev_7202d4ad041141c9afc7', [0.03, 0.10, 0.97, 0.60]),
           ev('ev_a9eaa28a152045e4b086', [0.55, 0.02, 0.99, 0.55])]
    ops = []
    for subj in [SUL1, SUL2]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=data,
                        context=dict(kind='specification', basis=BASIS_GBX + ' Type 1 only; FIO.'),
                        origin='explicit', confidence=0.9, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup,
                    text=('SUL-3 Type-2 grab motors need the p10 technical-table motor rows (follow-up already '
                          'queued). Gear teeth/bearing/seal piece detail is P3; sheet-level ratios recorded as '
                          'printed. Remaining gearbox sheets unreviewed.')))
    return dict(summary='SUL1/SUL2 grab gearbox SPL H3-630 data + sheet allocation (gearbox GA)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record vendor gearbox data for Type-1 grab drives',
                    questions=['What gearbox drives the SUL grab hold/close?'],
                    reviewed_evidence_ids=['ev_7202d4ad041141c9afc7', 'ev_a9eaa28a152045e4b086'],
                    gaps=['Index + hold/close sheet reviewed. Other sheets, piece internals P3 or deferred.']))


def pkg_buf():
    hard = ('Travel-end hardware per 175194 Rev-4 replies (19-Aug-2020): buffer-post member sizes/scope '
            'incorporated; buffer centre 1265mm vs 1256mm in LT assembly/wheel-load diagram (against 1100mm shown '
            'in the drawing) to be revised; buffer dimensions indicated; fixing locations/details aligned with '
            'approved civil drawing (jetty beam arrangement). Rail CR100 on 20000mm gauge (DBR cross-ref, not '
            're-asserted here). Rail drawing shows sole-plate anchorage, weldable clips, expansion joint, web '
            'reinforcement, storm tie-down bolts at storm-tie-down location, buffer-stop sections; FIO.')
    sup = [ev('ev_f43f51e9ca554ea2b098', [0.03, 0.05, 0.97, 0.97])]
    ops = [dict(op='assert', subject=SUL1, predicate='assembly_arrangement', value=hard,
                 context=dict(kind='specification', basis=BASIS_BUF + ' All three SULs jointly; per-type stroke '
                              'check below.'),
                 origin='explicit', confidence=0.85, evidence=sup)]
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup,
                    text=('Per-type buffer strokes (SUL-3: 600mm LT / 400mm trolley from p10) vs Type-1 strokes, LT '
                          'motor/brake models, and anti-collision/storm-parking logic need a legible long-travel '
                          'data page + unloader PLC/IO list + anti-collision datasheet. Calc-sheet OCR is garbled; '
                          'recorded as evidence gap.')))
    return dict(summary='Unloader travel-end hardware per rail replies; data-page gaps (buffer replies)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record rail/buffer reply outcomes; name data gaps',
                    questions=['What travel-end hardware is confirmed for the unloaders?'],
                    reviewed_evidence_ids=['ev_f43f51e9ca554ea2b098'],
                    gaps=['Reply sheet read. Rail GA drawings are FIO linework; data pages unreviewed. LT '
                          'motor/brake + anti-collision need named records.']))


def pkg_lub():
    sys_ = ('Common dual-line grease lubrication for SUL-1/2/3 (SYSTEM-1&11, Lincoln two-line): pump station with '
            'reservoir + grease-level switch; DU1-GKS change-over valve LineA/LineB on set pressure; end-of-line '
            'pressure switches both lines to last distributor; Local mode (panel start, per-half-cycle manual) and '
            'Remote mode (panel + DCS signal, automatic changeover, pump off at pause). Lincoln principle: pressure '
            'rise, changeover, pump off, pause; both halves feed all points per cycle. FIO.')
    sup = [ev('ev_531a4fdc8d2549619d46', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_6fdd515daa86441ab907', [0.03, 0.05, 0.97, 0.97]),
           ev('ev_01c6dfc2ddae4bd08d72', [0.03, 0.05, 0.97, 0.97])]
    ops = []
    for subj in [SUL1, SUL2, SUL3]:
        ops.append(dict(op='assert', subject=subj, predicate='assembly_arrangement', value=sys_,
                        context=dict(kind='specification', basis=BASIS_LUB + ' Common system, all three SULs.'),
                        origin='explicit', confidence=0.9, evidence=sup))
    ops.append(dict(op='source_note', origin='explicit', confidence=0.9, evidence=sup,
                    text=('Pump/motor ratings and per-point nozzle/distributor counts need the system P&ID or pump '
                          'schedule pages; recorded as evidence gap. Jetty water upstream stays the Tier-1 shared '
                          'boundary (reused, not re-asserted).')))
    return dict(summary='SUL-1/2/3 dual-line grease system composition + Local/Remote sequence (lube docs)',
                operations=ops,
                intake_assessment=dict(route='mixed', purpose='Record common lube system composition and sequence',
                    questions=['How is unloader grease lubrication sequenced?'],
                    reviewed_evidence_ids=['ev_531a4fdc8d2549619d46', 'ev_6fdd515daa86441ab907', 'ev_01c6dfc2ddae4bd08d72'],
                    gaps=['pp11-13 sequence read. Pump ratings/nozzle counts need diagram pages.']))


PACKAGES = [(DOC_SEL, pkg_sel, 'sel'), (DOC_CTL, pkg_ctl, 'ctl'), (DOC_GA, pkg_ga_rows, 'ga'),
            (DOC_CPL, pkg_cpl, 'cpl'), (DOC_BRK, pkg_brk, 'brk'), (DOC_DBR, pkg_dbr, 'dbr'),
            (DOC_GBX, pkg_gbx, 'gbx'), (DOC_BUF, pkg_buf, 'buf'), (DOC_LUB, pkg_lub, 'lub')]


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
        assert before['version'] == 720, before['version']
    if not args.apply:
        if COPY.exists():
            shutil.rmtree(COPY)
        COPY.mkdir(parents=True)
        with sqlite3.connect((plant / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
            with sqlite3.connect(COPY / 'plant.sqlite3') as dst:
                db.backup(dst)
    running = 720
    for doc, builder, tag in PACKAGES:
        out = BASE / ('accepted-%s' % tag if args.apply else 'rehearsal-%s' % tag)
        out.mkdir(parents=True, exist_ok=True)
        body = builder()
        body['intake_assessment']['reviewed_evidence_ids'] = all_ids(doc)
        if args.apply:
            assert body == json.loads((BASE / ('rehearsal-%s/package.json' % tag)).read_text(encoding='utf8'))
            assert json.loads((BASE / ('rehearsal-%s/result.json' % tag)).read_text(encoding='utf8'))['ok']
        (out / 'package.json').write_text(json.dumps(body, indent=2) + '\n', encoding='utf8')
        store = Store(plant if args.apply else COPY)
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
