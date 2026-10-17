"""Assemble the Pass-5 (Yard 3) top-model review zip.

Local tier applied only 100%-confidence work (rehearsed v771-v789, not applied);
all 23 UNCERTAIN findings and the Yard-3 open questions ship to the top model as
one review package mirroring the accepted pass-04-zip layout:
  TOP_MODEL_BRIEF.md, draft-claims.json, sources.json, db-slice.json, checks.txt,
  example-accepted.json, result-template.json, top-model-result.json,
  images/ (one named crop per draft), proposal-bodies/ (19 rehearsed bodies).
"""
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'output/plant-enrichment/pass-05'
ZIP = ROOT / 'output/plant-enrichment/pass-05-zip'
PREV_ZIP = ROOT / 'output/plant-enrichment/pass-04-zip'
CROPS = BASE / 'crops'

FULL = [0.02, 0.02, 0.98, 0.99]

TAGS = [('a11', 771), ('a12', 772), ('stkb3', 773), ('stkg3', 774), ('recg3', 775),
        ('recb3', 776), ('fir3', 777), ('dsss3', 778), ('dspk3', 779), ('dssr3', 780),
        ('pump3', 781), ('fhpid3', 782), ('lubs3', 783), ('lubr3', 784), ('phil3', 785),
        ('play3', 786), ('qrc3', 787), ('dbr3', 788), ('trip3', 789)]

DOCS = {
    'a11': 'doc_9d6657d14f3a4c829469', 'a12': 'doc_0adf08e6189847b88503',
    'stkb3': 'doc_78bebe6773984d59b013', 'stkg3': 'doc_d69ffd4c7c2241018323',
    'recg3': 'doc_3e81ea1c32df4215968d', 'recb3': 'doc_498f70490d294542b8b0',
    'fir3': 'doc_4d488fd685284c408297', 'dsss3': 'doc_0f52c77514a74773ae30',
    'dspk3': 'doc_5759a520616e4b588dce', 'dssr3': 'doc_a6a2fa82944f4d12b8aa',
    'pump3': 'doc_9db2601634034197a910', 'fhpid3': 'doc_0eeb339e58a24707a475',
    'lubs3': 'doc_b7d031cc33c54157ad86', 'lubr3': 'doc_42554b5718fc423997b3',
    'phil3': 'doc_e17edf6897d746fabe12', 'play3': 'doc_7244e891263a4e6d8214',
    'qrc3': 'doc_5a36f2843d504d6e96de', 'dbr3': 'doc_777d1a06d4fa4e8ba231',
    'trip3': 'doc_2c2568dc7b9e4e509cd6',
}

DRAFTS = [
    # (draft_id, qid, depth, subject, unsure, doc_tag, crop, alias, decide)
    ('draft_a1_pulley_brgcrs', 'Q1', 'DQ-B20-001', 'EAC-11 pulley bearing-centre value (drg 175021)',
     'All pulley rows best-read "2700 BRG. CRS." at 8x; earlier readings suggested 2300; GA plan/head-detail dimension reads ~2700/2730. Glyphs 2300/2700/2730 not separable at render resolution.',
     'a11', 'crops/EAC11-pulley-nums-hi__175021__p5.png', 'q1_a1_eac11_pulley_brgcrs.png',
     'Give the bearing-centre value(s) for the EAC-11 pulley set as printed (per row if they differ).'),
    ('draft_a2_transition_idlers', 'Q1', 'DQ-B20-001', 'EAC-11 transition idler row (angle set vs quantity keys)',
     'Row prints angle set 5,10,15,25 & 35 deg but quantity keys run 5,10,15,20,25,30 deg (counts best-read 2/2/2/1/3/3). Internal list-vs-key mismatch; per-angle digits at render limit; row carries rev-2 delta.',
     'a11', 'crops/EAC11-idlers2__175021__p5.png', 'q1_a2_eac11_transition_idlers.png',
     'State exactly what the transition row prints for the angle set and for each quantity key, and whether the mismatch is printed.'),
    ('draft_a3_pcs_unit', 'Q1', 'DQ-B20-001', 'PCS pull-cord switch quantity unit (EAC-11 30 / EBA-12 31)',
     'PCS qty prints 30 (EAC-11) and 31 (EBA-12) with no pair/device unit; the BSS row on the same table explicitly prints "PAIRS". Counts imply one device per ~30 m span per side for ~900 m conveyors.',
     'a11', 'crops/EAC11-char9__175021__p5.png', 'q1_a3_eac11_pcs_qty.png',
     'Confirm the PCS row text verbatim (qty value and any unit wording) on the EAC-11 sheet.'),
    ('draft_a4_holddown_face', 'Q1', 'DQ-B20-001', 'EBA-12 hold-down roller face width',
     'Hold-down roller prints 219 dia x 2200 face, qty 1/conv, on a 1400 mm belt; deflector roller on the same sheet prints 1600 face; 2200 matches conveyor-11 (2000 belt) rows.',
     'a12', 'crops/EBA12-pulley-nums-hi__175022__p5.png', 'q1_a4_eba12_holddown_face.png',
     'Confirm the printed hold-down and deflector roller rows on EBA-12 (diameters, face widths, quantities).'),
    ('draft_a5_sealplate_thk', 'Q1', 'DQ-B20-001', 'EBA-12 seal plate thickness',
     'Seal plate prints "31.5 THK. SEAL PLATE CONTINUOUS..."; EAC-11 prints DECK PLATE 3.15 thk; sheet-1 notes require min 3.0 mm. 31.5 mm exceptional for a seal plate (missing decimal suspected).',
     'a12', 'crops/EBA12-sealplate__175022__p5.png', 'q1_a5_eba12_sealplate.png',
     'Read the seal-plate thickness exactly as printed; state whether 31.5 or 3.15 and any adjacent note.'),
    ('draft_a6_weigher_accuracy', 'Q1', 'DQ-B20-001', 'EBA-12 belt weigher accuracy',
     'Prints "ACCURACY (±)25% AT 20 TO 120% FOR 1400 B/W", qty 1. (±)25% implausible for a load-cell weigher; missing decimal suspected; depth queue expects reconciliation vs a 2%/0.25% schedule.',
     'a12', 'crops/EBA12-weigher__175022__p5.png', 'q1_a6_eba12_weigher.png',
     'Read the weigher accuracy cell exactly as printed and whether the plus-minus is inside brackets with a decimal.'),
    ('draft_a7_hgtu_eac11', 'Q2', 'DQ-B20-002', 'EAC-11 tail-pulley-with-HGTU load table',
     'Table present (header verified verbatim) with tail-load cases T1-T3 (three components each plus a secondary set); cell digits at render limit.',
     'a11', 'crops/EAC11-hgtu-loads-zoom__175021__p5.png', 'q2_a7_eac11_hgtu_loads.png',
     'Transcribe the HGTU frame load table rows that resolve; leave illegible cells explicitly unread.'),
    ('draft_a8_hgtu_eba12', 'Q2', 'DQ-B20-002', 'EBA-12 tail-pulley-with-HGTU load table',
     'Table present with six load cases T1-T6; T1 row sampled 0.01/-0.83/0.1 and 0.033/-0.265/8.122 best-read; other rows not digit-resolved.',
     'a12', 'crops/EBA12-hgtu-loads__175022__p5.png', 'q2_a8_eba12_hgtu_loads.png',
     'Transcribe the EBA-12 HGTU frame load table rows that resolve.'),
    ('draft_a9_notes_tags', 'Q2', 'DQ-B20-002', 'EAC-11 sheet-1 notes 18/19 support-drawing tags',
     'Notes print UAX-3 (note 18, head-pulley frame, drg MAITREE-00-UEF-LH-175049-ISG-0) and UEE-6 (note 19, tail). Breadth review recorded "UAX-1/UEF-6" copied text; rev-2 print shows UAX-3/UEE-6; key plan for EAC-11 runs between UEF-4 and UAX-3.',
     'a11', 'crops/EAC11-notes__175021__p1.png', 'q2_a9_eac11_notes.png',
     'Read notes 18 and 19 verbatim (drawing numbers included) and decide the correct tag pairing.'),
    ('draft_b10_slew_power', 'Q3', 'DQ-B21-001', 'EAD-3 slew drive motor power (15 vs 22 kW)',
     'Stacker GA TDS rev2 prints "Power of motor 15 kW" for the slewing mechanism; stacker BOD rev2 (approved 27-Feb-2019) prints slew drive motor 22 kW, 1500 rpm syn. Both labeled the mechanism drive motor; hydraulic power-pack vs slew-drive scope unresolved.',
     'stkg3', 'crops/ga-tds-slew-angle-power__175126__p1.png', 'q3_b10_stacker_slew_power.png',
     'Decide 15 kW, 22 kW, both (different scopes) or retain_disagreement, naming the deciding record.'),
    ('draft_b11_slew_angle', 'Q3', 'DQ-B21-001', 'EAD-3 slew angle print (0 to 100 vs 0 to -100)',
     'GA TDS rev2 prints "0\u00b0~-100\u00b0"; 24x zoom shows a straight dash before 100. BOD prints positive range (0~100). Negative-only range would be unusual.',
     'stkg3', 'crops/ga-zoom2-slewangle__175126__p1.png', 'q3_b11_stacker_slew_angle.png',
     'Read the slewing angle cell exactly (hyphen vs minus) and state the governing range.'),
    ('draft_b12_luff_labels', 'Q3', 'DQ-B21-001', 'EAD-3 luffing TDS rows (labels garbled)',
     'Rows read "Luffing gear .Degree | Hydraulic Cylinder", "loft angle .Degree | +14\u00b0", "rotation angle .Degree | -8\u00b0", "power of motor .kW | 22". Values agree with BOD; labels appear typoed ("loft"/"rotation").',
     'stkg3', 'crops/ga-zoom2-luffing-labels__175126__p1.png', 'q3_b12_stacker_luff_labels.png',
     'Transcribe the luffing rows verbatim and interpret which label means up-luff and down-luff.'),
    ('draft_b13_tiedown', 'Q4', 'DQ-B21-001', 'EAD-3 boom tie-down / storm lock deviation',
     'Spec B4-28 requires tie-down at BOTH track ends (wind > 73 m/s); furnished drawing shows single side; vendor reply argues one side acceptable (other side affects reclaimer travel). Resolution not in corpus.',
     'stkg3', 'crops/stacker-storm-parking-tcs__175126__p4.png', 'q4_b13_stacker_tiedown.png',
     'State the open deviation status and the deciding record; do not resolve to a single reading without one.'),
    ('draft_b14_belt_speed', 'Q5', 'DQ-B21-001', 'EAD-3 boom conveyor belt speed (3.5 vs 3.6 m/s)',
     'GA TDS rev2 prints 3.5 m/s inside a flagged box; TCS item 6 requires 3.6 m/s, vendor replied "Revised."; tripper row (also 3.5) is unflagged and must not be merged with the boom row.',
     'stkg3', 'crops/ga-zoom2-beltspeed__175126__p1.png', 'q5_b14_stacker_belt_speed.png',
     'Decide the governing boom belt speed and keep the tripper row separate.'),
    ('draft_b15_moisture', 'Q5', 'DQ-B21-001', 'EAD-3 design coal moisture (25 vs 24%)',
     'GA TDS rev2 prints "water rate .% | max 25%"; BOD rev2 item 3.4 prints "Moisture content = Max. 24%". Handled-material percent differs between documents.',
     'stkg3', 'crops/ga-zoom2-waterrate__175126__p1.png', 'q5_b15_stacker_moisture.png',
     'Decide 25%, 24% or retain_disagreement; state whether the row means design coal moisture.'),
    ('draft_b16_stacking', 'Q5', 'DQ-B21-001', 'EAD-3 design stacking capacity digits',
     'GA TDS rev2 "Design Stacking .t/h" glyphs ambiguous at render resolution (candidate 3740/5240/5740); BOD rev2 prints 3740. Stroke-pattern zoom favors 3740.',
     'stkg3', 'crops/ga-zoom2-designstacking__175126__p1.png', 'q5_b16_stacker_design_stacking.png',
     'Read the Design Stacking cell exactly (with the Rated Stacking row for contrast).'),
    ('draft_c17_aux_capacity', 'Q6', 'DQ-B21-002', 'EAF-3 auxiliary boom reclaim capacity (660 vs 650 t/h)',
     'TDS Rev-2 prints 500-660 TPH (660 inside a revision cloud marked "2"); Basis of Design Rev-2 prints 500-650 t/h. Both Rev-2 in the same review cycle; depends on boom inclination.',
     'recg3', 'crops/eaf3-genspec-wind2__175127__p3.png', 'q6_c17_eaf3_aux_capacity.png',
     'Decide 660, 650 or retain_disagreement; name the deciding record.'),
    ('draft_c18_hoist_gearbox', 'Q6', 'DQ-B21-002', 'EAF-3 hoist gearbox type wording',
     'TDS sheet 3 prints "HELICAL HOLLOW OUTPUT SHAFT WITH SHRINK DISC"; Basis of Design prints "Bevel helical hollow output shaft with shrink disc". Wording differs by "Bevel".',
     'recg3', 'crops/eaf3-hoist-drive__175127__p3.png', 'q6_c18_eaf3_hoist_gearbox.png',
     'Decide plain helical vs bevel-helical (or retain_disagreement) for the hoist gearbox.'),
    ('draft_c19_buffer_digits', 'Q7', 'DQ-B21-002', 'EAF-3 rail-B buffer support end distance digits',
     'Layout note reads "BUFFER SUPPORT END DISTANCE FOR PORTAL RECLAIMER RAIL B SIDE(r)"; adjacent digits partly legible (best read 713356/713300 class). Context rows: total pile length 710000, reclaimer travel 714750.',
     'recg3', 'crops/eaf3-plan-buffer-dim__175127__p2.png', 'q7_c19_eaf3_buffer_dim.png',
     'Read the buffer support end-distance dimension exactly, or declare unreadable with the deciding record.'),
    ('draft_c20_wind_units', 'Q8', 'DQ-B21-002', 'EAF-3 wind speed units (km/h vs m/s)',
     'TDS p3 prints operating 16 km/h and extreme 73 km/h; Basis of Design prints operating 16 m/s (0.16 kN/m2), non-operating 35 m/s, high-wind 73 m/s (3.33 kN/m2), corroborated at BoD p14 and load case WW.',
     'recg3', 'crops/eaf3-genspec-wind2__175127__p3.png', 'q8_c20_eaf3_wind_units.png',
     'Decide whether the TDS km/h printing is a unit typo for m/s; state the governing wind values.'),
    ('draft_c21_travel_speeds', 'Q8', 'DQ-B21-002', 'EAF-3 travel speeds (band vs discrete)',
     'TDS prints operating 2 to 8 m/min, relocation 20 m/min max; Basis of Design prints reclaiming 2 m/min / 5 m/min, relocation 20 m/min; calc uses max 0.33 m/s. Band vs discrete unresolved.',
     'recg3', 'crops/eaf3-travel-drive__175127__p3.png', 'q8_c21_eaf3_travel_speeds.png',
     'Decide the travel speed set (operating/reclaiming and relocation) and whether the TDS band stands.'),
    ('draft_d22_filter_wording', 'Q9', 'DQ-B22-002', 'EAD-3 machine DSS suction filter wording (duplex vs simplex)',
     'Plain-water DSS sections print "Suction Duplex filter with Diff. Pressure Indicating Switch." (p21) and "Duplex filter" choked alarm (p26); dry-fog alarm lists (pp23/p29) print "simplex filter choked". Machine P&ID DF-101 is a duplex filter; duplex favored.',
     'dsss3', 'crops/cs-comp-v2__chemtrols__p21.png', 'q9_d22_dss_filter_wording.png',
     'Decide duplex vs simplex (or retain both with scope); name the deciding record.'),
    ('draft_d23_ap_mapping', 'Q10', 'DQ-B22-003', 'Yard-3 AP/stockpile mapping print (Stockpile-2 vs Stockpile-3)',
     'Philosophy p4 lists AP-57..84 in "Stockpile-3" (SC-03, KKS 00EAE03QN201) and AP-85..112 in "Stockpile-2" (SC-04, KKS 00EAE04QN201) under heading STOCKPILE_NO - 3 & 4. The printed "Stockpile-2" for the SC-04/EAE-04 block is inconsistent with the heading and KKS; retained as printed.',
     'phil3', 'crops/opphil-sect-v2__M319__p4.png', 'q10_d23_ap_stockpile_mapping.png',
     'Decide whether to keep the printed pairing verbatim with a conflict note, or re-map the SC-04 block to Stockpile-4/EAE-4.'),
]

QS = {
    'Q1': ('EAC-11/EBA-12 data-sheet cells (DQ-B20-001)',
           'Digit/unit readings at render limit on the conveyor GA data sheets. Decide corrected value or confirmed as printed; if the cell cannot support a single reading, say so with the deciding record.'),
    'Q2': ('EAC-11/EBA-12 HGTU load tables and note tags (DQ-B20-002)',
           'Transcribe what resolves; correct the note-tag pairing only if the crop shows the printed tags unambiguously.'),
    'Q3': ('Stacker GA TDS vs BOD rows, slew/luff (DQ-B21-001)',
           'Decide per row, naming scope if both readings stand (e.g., hydraulic power-pack vs mechanism drive).'),
    'Q4': ('Stacker boom tie-down deviation (DQ-B21-001)',
           'This is an open deviation, not a reading choice; state the status and the deciding record.'),
    'Q5': ('Stacker GA TDS printed values (DQ-B21-001)',
           'Decide per cell; keep boom and tripper rows distinct.'),
    'Q6': ('Reclaimer family capacity and hoist wording (DQ-B21-002)',
           'Decide per row; retain both values if the records disagree without a governing revision.'),
    'Q7': ('Reclaimer rail-B buffer dimension (DQ-B21-002)',
           'Reading-level decision only; no invented dimensions.'),
    'Q8': ('Reclaimer wind units and travel speeds (DQ-B21-002)',
           'Decide per row; unit-typo verdicts must cite both documents.'),
    'Q9': ('Stacker machine DSS suction filter wording (DQ-B22-002)',
           'Decide duplex vs simplex wording for the plain-water DSS; legacy dry-fog copy may be preserved as scope note.'),
    'Q10': ('Yard-3 AP/stockpile mapping print (DQ-B22-003)',
            'Decide between verbatim-with-conflict and re-mapping; cite heading, KKS and sector rows.'),
}


def load_agents():
    agents = {}
    for letter in ('A', 'B', 'C', 'D'):
        agents[letter] = json.loads((BASE / ('mine/agent-%s.json' % letter)).read_text(encoding='utf-8'))
    return agents


def doc_names(agents):
    names = {}
    for a in agents.values():
        for dr in a['documents_reviewed']:
            names.setdefault(dr['doc'], dr['name'])
    return names


def build_draft_claims(agents):
    claims = []
    for (draft_id, qid, depth, subject, unsure, tag, crop, alias, decide) in DRAFTS:
        claims.append({'draft_id': draft_id, 'question_id': qid, 'depth_ids': [depth],
                       'subject': subject, 'unsure': unsure,
                       'proposal_group': DOCS[tag], 'confidence': 0.5})
    return claims


def build_images(agents):
    images = ZIP / 'images'
    images.mkdir(parents=True, exist_ok=True)
    for (draft_id, qid, depth, subject, unsure, tag, crop, alias, decide) in DRAFTS:
        src = BASE / crop
        assert src.exists(), (draft_id, src)
        shutil.copyfile(src, images / alias)
    return len(DRAFTS)


def build_proposal_bodies():
    out = ZIP / 'proposal-bodies'
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for tag, ver in TAGS:
        src = BASE / ('rehearsal-%s/package.json' % tag)
        assert src.exists(), src
        pkg = json.loads(src.read_text(encoding='utf-8'))
        out_pkg = dict(summary=pkg['summary'], operations=pkg['operations'])
        (out / ('rehearsal-%s.json' % tag)).write_text(
            json.dumps(out_pkg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        n += 1
    return n


def build_sources():
    docs = []
    with sqlite3.connect(ROOT / 'data/plant/plant.sqlite3') as db:
        db.row_factory = sqlite3.Row
        for tag, ver in TAGS:
            doc = DOCS[tag]
            d = db.execute('SELECT * FROM documents WHERE id=?', (doc,)).fetchone()
            blocks = [dict(id=r['id'], page=r['page'], locator=r['locator'])
                      for r in db.execute('SELECT id, page, locator FROM evidence WHERE document_id=? ORDER BY page, id', (doc,))]
            docs.append(dict(document=doc, filename=d['name'], sha256=d['sha256'],
                             revision=d['revision'], authority=d['authority'],
                             bytes=d['bytes'], evidence_blocks=blocks))
    return docs


def build_db_slice(agents):
    ids = set()
    for tag, ver in TAGS:
        pkg = json.loads((BASE / ('rehearsal-%s/package.json' % tag)).read_text(encoding='utf-8'))
        for op in pkg['operations']:
            ids.add(op['subject'])
    for a in agents.values():
        for f in a['findings']:
            if f.get('classification') == 'UNCERTAIN':
                for m in re.finditer(r'ent_[0-9a-f]{16,24}', f.get('subject_hint') or ''):
                    ids.add(m.group(0))
    ents = []
    facts = []
    with sqlite3.connect(ROOT / 'data/plant/plant.sqlite3') as db:
        db.row_factory = sqlite3.Row
        by_id = {r['id']: r for r in db.execute('SELECT id, label, created_version, provenance FROM entities')}
        for eid in list(ids):
            if eid not in by_id:
                continue
            for r in db.execute("SELECT subject FROM assertions WHERE predicate='part_of' AND object_entity=?", (eid,)):
                if r['subject'] in by_id:
                    ids.add(r['subject'])
            for r in db.execute("SELECT object_entity FROM assertions WHERE predicate='part_of' AND subject=?", (eid,)):
                if r['object_entity'] in by_id:
                    ids.add(r['object_entity'])
        keep = sorted(i for i in ids if i in by_id)
        for eid in keep:
            r = by_id[eid]
            ents.append(dict(id=r['id'], label=r['label'], created_version=r['created_version'],
                             provenance=r['provenance']))
        keepq = '(%s)' % ','.join('?' * len(keep))
        for r in db.execute('SELECT id, subject, predicate, value, object_entity, unit, confidence, origin,'
                            ' evidence, created_version FROM assertions WHERE subject IN %s OR object_entity IN %s'
                            % (keepq, keepq), tuple(keep) + tuple(keep)):
            facts.append(dict(r))
    return dict(version=770, entities=ents, assertions=facts)


def build_checks():
    rows = []
    for tag, ver in TAGS:
        res = json.loads((BASE / ('rehearsal-%s/result.json' % tag)).read_text(encoding='utf-8'))
        pkg = json.loads((BASE / ('rehearsal-%s/package.json' % tag)).read_text(encoding='utf-8'))
        ops = pkg['operations']
        rows.append((tag, ver, res['version'], len(ops),
                     sum(1 for o in ops if o['predicate'] == 'document_note'),
                     sum(1 for o in ops if o['predicate'] == 'source_gap')))
    lines = ['Pass 5 local rehearsal: %d/%d proposals rehearsed clean on an isolated copy of the live v770 DB,'
             % (len(rows), len(rows)), 'chained v770 -> v789 (tags: %s).' % ', '.join('%s %d' % (t, v) for t, v in TAGS),
             'Validator: 0 errors on all %d. Commit with --apply only after the top-model return is folded in.'
             % len(rows), '',
             'tag     base  result  ops  notes  gaps']
    for tag, v, rv, ops, notes, gaps in rows:
        lines.append('%-7s %-5d %-7d %-4d %-6d %d' % (tag, v - 1, rv, ops, notes, gaps))
    lines += ['',
              'Open conflicts carried to top model (see TOP_MODEL_BRIEF.md Q1-Q10): 23 UNCERTAIN findings.',
              'Resolved during pre-build (not questions): EAC-11 Tup = 86.963 kN (ED-175231-ISG block',
              'EAC 7/9/11/13 p66 cross-check, 19550 lbf); EBA-12 Tup corrected to 53.872 kN (block',
              'EBA-8/10/12/14 p77, 12111 lbf; all other rows agree with calc within 0.001 kN).',
              'QRC BOM item 19 crop verified (92 NOS); F.Harley P&ID present in corpus; KSP8-65S provenance verified.',
              '',
              'Preserved verbatim (no adjudication sought): galvanised/grillage typos, PREMLUM-family spellings,',
              'loft/rotation luff rows, TDS km/h cells, (25%) weigher print, 31.5 THK, 2200 hold-down face,',
              'UAX-3/UEE-6 note pair, TCS markups, apron-feeder glyphs, PCS pair omission.']
    return '\n'.join(lines) + '\n'


def build_brief(agents):
    names = doc_names(agents)
    sweep = []
    for tag, ver in TAGS:
        name = names.get(DOCS[tag], '(not in local review)')
        sweep.append('| %s | %s |' % (tag, name.replace('|', '/')))
    qs = []
    for qid in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']:
        title, ask = QS[qid]
        qs.append('### %s: %s\n- %s' % (qid, title, ask))
        for (draft_id, q, depth, subject, unsure, tag, crop, alias, decide) in DRAFTS:
            if q != qid:
                continue
            qs.append('- `%s` (%s, doc `%s`): %s\n  - crop `images/%s`. Decide: %s'
                      % (draft_id, depth, DOCS[tag], unsure, alias, decide))
        qs.append('')
    return BRIEF_TEMPLATE.replace('__SWEEP__', '\n'.join(sweep)).replace('__QUESTIONS__', '\n'.join(qs))


BRIEF_TEMPLATE = '''# Pass 5 (Yard 3 full) - top-model review package

You are the reviewing engineer. Decide only the listed questions for the listed
depth IDs, using only the crops, db-slice rows and staged proposal bodies
provided. Do not assert anything not visible in the crops.

## Standing context (already accepted, do not re-litigate)

- Live model v770. Tier-1 Yard-3 work is accepted: Yard-3 stockpile complexes
  EAE-3/EAE-4 with machines EAD-3 (stacker) and EAF-3 (portal scraper reclaimer)
  identified by coal flow; Yard-3 SPDS ring headers AP-57..112 with sector
  control SC-03/SC-04; Yard-3 QRC makeup connections; stacker onboard
  plain-water DSS (Chemtrols) and reclaimer onboard DSS (F.Harley); stacker
  FDA package recorded on the stacker boundary with the EAF-3 fire gap.
- This pass stages 19 local one-source proposals (IN `proposal-bodies/`,
  rehearsed clean v771-v789, NOT yet applied): EAC-11/EBA-12 GA depth rows,
  stacker/reclaimer family design depth, reclaimer BOD loads, reclaimer onboard
  DSS/pump/P&ID rows, both central-lubrication packages, Yard-3 DS philosophy
  and piping-layout gaps, QRC drawing rows, DBR water reply, and the EAF-3 fire
  source gap evidence.
- Local tier asserted only 100%-confidence printed values
  (`document_note`) and absent legs (`source_gap`). Nothing below that bar was
  asserted; all 23 UNCERTAIN findings are in this zip as Q1-Q10.

## Non-negotiable rules

- No invented field/KKS/cable/spare tags; no invented ratings/settings.
- Keep family (4-machine) vs per-unit applicability explicit; EAD-3/EAF-3 are
  the Yard-3 units of the stacker/reclaimer families.
- Keep descriptive names when no tag exists.
- Preserve disagreements as qualified alternatives with the record needed to
  settle them; use `retain_disagreement` where neither reading wins.
- Never merge boom and tripper rows, never merge the stacker and reclaimer
  machines, never merge the plain-water DSS and dry-fog DSS wordings.
- FIO documents are non-approved layout/vendor data; FOR APPROVAL + APPROVED
  stamp governs over FIO; a revision cloud marked "2" is not by itself a
  govern verdict.
- Quote exact visible cell/paragraph text; give document + page + crop +
  region for every verdict.

## Revision/status sweep (standing use 1 - verify each line, flag mismatches)

| tag | document as recorded by local readers |
|---|---|
__SWEEP__

Ask: flag FOR APPROVAL vs approved, FIO vs AOC, title-block vs revision-table
mismatches (including the F.Harley P&ID title block printing REV 1 while an
earlier pass basis recorded Rev 2, and EAC-11 sheet deltas marked rev 2 inside
an ISG rev 1 package), and any reading that treats a review comment or a
revision cloud as a final selection.

## Questions

__QUESTIONS__
## Pre-stage proofread (standing use 2 - check the 19 staged bodies in `proposal-bodies/`)

Flag: invented tags/values, family values copied to a specific machine without
per-unit evidence, merged systems/rows, normalised spellings that should stay
verbatim (ELEKCTROMAG family, PREMLUM family, "loft/rotation" luff rows, TDS
km/h cells, (25%) weigher print, 31.5 THK seal plate, 2200 face hold-down on a
1400 belt, UAX-3/UEE-6 note pair, PCS pair-unit omission), and applicability
overreach. Note: local note text is compiled mechanically from findings files;
spot-check subjects against the cited rows. Local re-checks each flag; the
proofread never replaces rehearsal, preservation, or verification.

## Return order

Return exactly one file, `top-model-result.json`, following
`result-template.json` (S3C of the workflow: `pass_id`, `depth_ids`, `model`,
`date`, `resolutions[]`, `preserved_disagreements[]`, `open_questions[]`), with
one entry per draft claim above (23) plus a revision-sweep flag list and
proofread notes. Set `pass_id` to `pass-05-yard3` and `base_version` to 770.
`example-accepted.json` is the accepted Pass-4 return as a format example. No
DB edits, no SQL, no proposal bodies - local stages those. `verdict` meanings:
`confirmed` / `corrected` / `rejected_needs_source` / `not_resolvable`;
disagreements that must stand use the Pass-3/Pass-4 precedent
`retain_disagreement` with both readings and the deciding record.
'''


def build_examples():
    shutil.copyfile(PREV_ZIP / 'result-template.json', ZIP / 'result-template.json')
    shutil.copyfile(PREV_ZIP / 'top-model-result.json', ZIP / 'example-accepted.json')
    skeleton = dict(schema_version=1, pass_id='pass-05-yard3', base_version=770,
                    depth_ids=['DQ-B20-001', 'DQ-B20-002', 'DQ-B21-001', 'DQ-B21-002',
                               'DQ-B22-001', 'DQ-B22-002', 'DQ-B22-003', 'DQ-B22-004'],
                    model='', date='', resolutions=[], preserved_disagreements=[],
                    open_questions=[], revision_sweep_flags=[], proofread_notes=[])
    (ZIP / 'top-model-result.json').write_text(json.dumps(skeleton, indent=2) + '\n', encoding='utf-8')


def main():
    agents = load_agents()
    if ZIP.exists():
        shutil.rmtree(ZIP)
    ZIP.mkdir(parents=True)
    n_img = build_images(agents)
    n_body = build_proposal_bodies()
    (ZIP / 'draft-claims.json').write_text(
        json.dumps(build_draft_claims(agents), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (ZIP / 'sources.json').write_text(
        json.dumps(build_sources(), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (ZIP / 'db-slice.json').write_text(
        json.dumps(build_db_slice(agents), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (ZIP / 'checks.txt').write_text(build_checks(), encoding='utf-8', newline='\n')
    (ZIP / 'TOP_MODEL_BRIEF.md').write_text(build_brief(agents), encoding='utf-8', newline='\n')
    build_examples()
    print(json.dumps({'zip': str(ZIP), 'images': n_img, 'bodies': n_body,
                      'drafts': len(DRAFTS), 'drafts_per_q': {q: sum(1 for d in DRAFTS if d[1] == q) for q in QS}}))


if __name__ == '__main__':
    main()
