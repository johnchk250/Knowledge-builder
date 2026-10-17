"""Assemble the Passes 6-10 top-model handover package (one zip).

The user hands this package plus cloud access to the original source PDFs to
the top model. The top model works the full depth of Passes 6-10 (Yard 4,
reclaim->TP13, trippers/bunkers/DE, common services + Yard 1, plant-wide
closeout) and returns one delta file applicable with
tools/apply_pass06_10_delta.py.

Package layout (output/plant-enrichment/pass06-10-zip, zipped to
output/plant-enrichment/pass06-10-top-model.zip):

  TOP_MODEL_BRIEF.md      master brief (paste-ready)
  DELTA_FORMAT.md         return format specification + examples
  APPLY_NOTES.md          how the local side applies the returned delta
  checks.txt              current model state and verification baseline
  passes/pass-06..10.md   per-pass scope, focus, depth-item checklists
  passes/scope.json       machine-readable scope (depth items + primary docs)
  shared/model-state/     entities, ontology, assertions, contexts, aliases,
                          retirements, versions, documents at v789
  evidence/<doc>.json     266 documents: immutable extracted text + block ids
  contracts/              plan, contracts, findings, breadth notes, checkpoints
  formats/                ops reference, delta template, worked examples
  code/                   apply_pass06_10_delta.py, evidence_helper.py
"""
import json
import re
import shutil
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DBSRC = ROOT / 'data/plant/plant.sqlite3'
ZIP = ROOT / 'output/plant-enrichment/pass06-10-zip'
ARCHIVE = ROOT / 'output/plant-enrichment/pass06-10-top-model.zip'

BASE_VERSION = 789

DOC_RE = re.compile(r'doc_[0-9a-f]{18,24}')

PASS_BATCHES = {
    'pass-06-yard4': ['B23', 'B24', 'B25'],
    'pass-07-reclaim-tp13': ['B26', 'B27', 'B28', 'B29', 'B37', 'B38'],
    'pass-08-trippers-bunkers-de': ['B39', 'B40', 'B41', 'B42'],
    'pass-09-common-services-yard1': ['B02', 'B03', 'B04', 'B05', 'B15', 'B16'],
    'pass-10-plantwide': ['B43', 'B44', 'B45', 'B46'],
}
DEPTH = {
    'pass-06-yard4': ['DQ-B23-001', 'DQ-B23-002', 'DQ-B24-001', 'DQ-B24-002',
                      'DQ-B25-001', 'DQ-B25-002', 'DQ-B25-003', 'DQ-B25-004'],
    'pass-07-reclaim-tp13': ['DQ-B26-001', 'DQ-B27-001', 'DQ-B28-001', 'DQ-B29-001',
                             'DQ-B37-001', 'DQ-B38-001'],
    'pass-08-trippers-bunkers-de': ['DQ-B39-001', 'DQ-B40-001', 'DQ-B41-001', 'DQ-B42-001'],
    'pass-09-common-services-yard1': ['DQ-B02-001', 'DQ-B02-003', 'DQ-B02-004',
                                      'DQ-B03-001', 'DQ-B04-001', 'DQ-B05-001',
                                      'DQ-B15-001', 'DQ-B16-001'],
    'pass-10-plantwide': ['DQ-B43-001', 'DQ-B44-001', 'DQ-B45-001', 'DQ-PILOT-001', 'DQ-B46-001'],
}
PASS_NAMES = {
    'pass-06-yard4': 'Pass 6 - Yard 4 full',
    'pass-07-reclaim-tp13': 'Pass 7 - Reclaim to TP13',
    'pass-08-trippers-bunkers-de': 'Pass 8 - Trippers / Bunkers / DE',
    'pass-09-common-services-yard1': 'Pass 9 - Common services + TP1/Yard 1',
    'pass-10-plantwide': 'Pass 10 - Plant-wide closeout',
}

FOCUS = {
    'pass-06-yard4': (
        "Machine drives + fire/lube/AP-SV (workflow plan), Yard 4 source set.\n\n"
        "Accepted-work awareness: the stacker/reclaimer family documents (stacker BOD 175249, stacker GA/TDS\n"
        "175126, reclaimer GA/TDS 175127, reclaimer BOD 175119, fire FDA 175248-family, onboard DSS, lube)\n"
        "were already mined for EAD-2/EAD-3/EAF-2/EAF-3 in Passes 4-5 and those notes are live at v789 - see\n"
        "them in shared/model-state/assertions.json (search document_note values mentioning the doc ids and\n"
        "'retain_disagreement'). Yard-4 legs are: EAC-13/EBA-14 GA rows from 175023/175024 (not yet mined),\n"
        "family-applicability declarations that explicitly name a fourth yard machine, P08 vendor drive/lube\n"
        "sources for EAC-13/EBA-14 component internals, and explicit source_gap records where only\n"
        "commissioning records/serials would settle a leg. Do not duplicate accepted notes.\n\n"
        "Constraints: keep family (4-machine) vs per-unit applicability explicit; TP3 coal sampling is not\n"
        "owned by Yard 4; EAC-13 reuses existing drive motor/gearbox identities (see entities.json)."),
    'pass-07-reclaim-tp13': (
        "Actuators + weigher calibration + sampler timer (workflow plan).\n\n"
        "Scope: FG-7/8/9/10 flap-gate actuator internals (vendor model, stroke limits, torque switches);\n"
        "EBA-15A/B + AT-3/4 multi-idler weigher calibration (calibration constants, test-chain weights,\n"
        "integrator terminals); EBA-16A/B + CV-3/4 incline-belt tension reconciliation;\n"
        "EAU-2 sampler primary-cutter interval timer, crusher screen mesh, elevator controller wiring;\n"
        "EBA-19A/B reducer bearing list, brake setting, sealing-belt tensioner.\n\n"
        "Constraints: keep one belt per stream with several placed receiving interfaces (B28 contract);\n"
        "16A->EBB-1 and 16B->EBB-2 endpoints retained; sampler sample-vs-main material routes distinct;\n"
        "weigher calibration constants only from vendor weigher documents, never inferred from GA geometry."),
    'pass-08-trippers-bunkers-de': (
        "Limit tags + clamp pressure + level/CO + fan curves (workflow plan).\n\n"
        "Scope: TT-1..TT-4 tripper per-bunker position switch tags and hydraulic rail-clamp pressure\n"
        "settings; TT-2/TT-4 head-end Bunker-A interlock wiring; Unit-1/2 bunker radar/capacitance probe\n"
        "KKS tags and mill-outlet gate actuator detail; Bunker House DE bagfilter cage/bag BOM, fan\n"
        "static-pressure curve, rotary airlock motor detail, dryer purge timer.\n\n"
        "Constraints: no invented field/KKS tags - record the missing tag as source_gap naming the\n"
        "deciding record when the source documents do not print it; DE is dry dedusting, not the DFDS\n"
        "wet suppression, never merged; per-bunker tags must be per-bunker."),
    'pass-09-common-services-yard1': (
        "PS polarity + 5/10m3 pit + header branches (workflow plan).\n\n"
        "Scope: DFDS common compressors model-reference internals and protection-table reconciliation;\n"
        "DFDS pumps/filters level/MGV tag mapping, PS polarity and filter trip/annunciation\n"
        "disagreements; DFDS Systems 1/2 distribution mains finer decomposition (trunk tees, intermediate\n"
        "isolation, branches to UEE-1/2 and UEF-3..12) with Tier-1 consumer connections left to their own\n"
        "batches; SPDS/SW1/SW2/PW local detail (AP/SC/SV mapping, valve/recirculation, hose/tank/gallery\n"
        "assemblies); sump/runoff 5 vs 10 m3 pit-capacity review discrepancy and pump/valve detail;\n"
        "UEF-1/TP1 hoist/access/tank detail from the found TP1 GA; Yard-1 machine safety/anchor/lube\n"
        "follow-ups and the Yard-1 qualification inventory (PCS count units, scoop model, AP/SV unique\n"
        "mapping, SC-01 count, pump-head choice).\n\n"
        "Constraints: never collapse System1/System2 or connect TP1 to System2; no new physical pipes -\n"
        "only explicit drawings connections; SPDS pump naming 1A/B vs 2A/B and 124 vs 115 mwc heads stay\n"
        "reconciled-not-overwritten; AP suffix is not valve suffix; DQ-B02-002 (missing 180055) stays\n"
        "parked, do not re-open it.\n\n"
        "Reference: output/plant-enrichment/B02 review findings are included under contracts/reviews/B02/;\n"
        "COAL_YARD_1_PILOT_REPORT.md is at contracts/COAL_YARD_1_PILOT_REPORT.md."),
    'pass-10-plantwide': (
        "MCC cubicles + thin-target scope only (workflow plan).\n\n"
        "Scope: MCC-1..4 cubicle-by-cubicle GA compartment schedule from the 59-page MCC document and\n"
        "protection relay settings (standalone I/O list 178158/180014 if present); HVAC fan curves across\n"
        "the 92-page HVAC package; electric hoist wiring/brake tables; stacker fire cylinder BOM detail\n"
        "(the fire package identity/zones were already recorded in Pass 5 - only the cylinder/BOM detail\n"
        "remains); unplaced-record disposition for record-review-queue rows (assign/reclassify/qualify/\n"
        "reuse or retain explicit unresolved status); accepted-followup thin targets CV-5, CV-6, FG-15A/B,\n"
        "TP-16/17/18, UEF-2 (scope review only).\n\n"
        "Constraints: thin-target scope only - do not mass-merge leftovers; a disposition is a review\n"
        "decision with evidence, not permission to invent identity; UEF-2/TP-16/17/18 stay reference\n"
        "boundaries (never create UEF-14/15); DQ-B46-001 is local exhaustive verification, not a top-model\n"
        "deliverable - but open_questions here feed it."),
}

GLOBAL_RULES = """\
## Hard rules (verbatim from the Pass B workflow + intake policy)

- No invented field/KKS/cable/spare tags; no invented ratings/settings or dimensions.
- Keep family (4-machine) vs per-unit applicability explicit; keep A/B lanes, numbered-machine and
  revision applicability explicit; keep descriptive names when no tag exists.
- Preserve disagreements as qualified alternatives with the record needed to settle them; disagreeing
  document values normally coexist as conflicts. Use retain_disagreement-style notes.
- Never merge the two DFDS systems, never collapse System1/2, never connect every tripper to every
  bunker; design capacity is not live inventory; a monitor is not proof of an interlock.
- Never infer isotope/activity, certification, isolation safety, live route state or missing
  connections from incomplete drawings.
- FIO documents are non-approved layout/vendor data; FOR APPROVAL + APPROVED stamp governs over FIO.
  Document authority is contextual guidance, not automatic truth; model revisions are not chronological
  unless source metadata establishes chronology.
- Every operation carries provenance: confidence (0-1), origin ("explicit" for printed facts,
  "inferred" only when genuinely derived), and 1-30 evidence references that must belong to the
  proposal's own source document.
- Quotes must be exact substrings of the immutable extracted text in evidence/<doc>.json. If a quote
  cannot be found there (bad OCR), use a region-only visual support for a rendered page, or place the
  item in open_questions asking for a re-crop; never invent text.
- Retire an existing assertion only with strong crop-level evidence that the prior interpretation was
  wrong or explicitly replaced; give the reason and the deciding evidence. Prefer conflicts over
  retirements.
"""

OPS_REFERENCE = """\
# Operations reference (what the delta's operations array must contain)

Base operations (chp/patches validation):

- define: {op, key, kind:"entity_type"|"property"|"relation", definition, cardinality:"one"|"many",
  value_type:"string"|"number"|"boolean"|"entity", ...provenance}
- entity: {op, id:"tmp_...", label, ...provenance}   (new entity; label must not collide)
- alias: {op, entity:"existing_or_tmp", alias, ...provenance}
- assert: {op, subject:"existing_or_tmp", predicate, value OR object_entity, unit (numbers only),
  context:{...}, ...provenance}
- retire: {op, assertion_id:"existing_fact_id", reason, ...provenance}
- merge: {op, source, target, reason, ...provenance}

Operational extensions (same provenance requirements):

- source_note: {op, text, ...provenance}   (index a drawing region without asserting a fact;
  every operation in a reference-route proposal must be a source_note)
- qualify: {op, assertion_id, context, reason, ...provenance}
- invalidate_entity / restore_entity / unmerge: {op, entity, reason, ...}
- retract_alias / restore_alias: {op, alias_id, reason, ...}
- event: {op, equipment, event_type, occurred_at, summary, details?, status?, related_event?,
  measurements?, ...provenance}  (not expected for Pass B depth work)

Provenance (every operation): {confidence: number 0-1, origin: "explicit"|"inferred",
evidence: [support, ...]} with 1-30 supports. Support forms:

1. {"evidence_id": "ev_...", "quote": "exact substring of that block's text"}
2. {"evidence_id": "ev_...", "region": [left,top,right,left-bottom] 0..1, "quote": ""}
   (visual support for image blocks; region must bound the supporting area)
3. Delta convenience form the local applier resolves first:
   {"document": "doc_...", "page": N, "quote": "..."}  or
   {"document": "doc_...", "page": N, "region": [l,t,r,b]}

assert context (required on every assert): kind must be one of specification | observation |
hypothesis | connection | classification. Recommended for this work:

  context: {"kind": "specification", "basis": "<source citation, revision, sheet/page>",
            "condition": "<source-stated operating condition, optional>"}

For plant network connections add network:"material"|"mechanical"|"electrical"|"control"|"utility" and
verification:"documented"|"unverified"; direction is subject -> object; only explicit source
connectors, never inferred routing. Monitoring/part_of links are not network edges.

Validator limits: max 500 operations and 500 KB per proposal; field strings max 2000 chars; units max
60 chars on numeric properties; max 30 supports per operation. Split a source that exceeds this into
multiple proposals for the SAME document (state "part 1/2" in the summary).

Patterns used by accepted Pass 4-5 work (follow this style):

- document_note: one string with "label: value (condition)" segments, semicolon-joined, each row
  traceable to a support; context.basis cites the sheet/page.
- source_gap: value starts "Absent from corpus: ..." and ends "Deciding records: ...".
- Conflicts: keep both values as separate notes or one note naming both readings + the deciding
  record; do not silently normalize.
"""

DELTA_FORMAT = """\
# Return format: one delta file

Return exactly one UTF-8 JSON file (suggested name delta.json), schema_version 1:

{
  "schema_version": 1,
  "passes": ["pass-06-yard4", "...all five pass ids..."],
  "base_version": 789,
  "model": "<your model name>",
  "date": "<ISO date>",
  "proposals": [ <one object per source document, applied in array order> ],
  "registry_notes": [ ... ],
  "open_questions": [ ... ],
  "revision_sweep_flags": [ "..." ],
  "proofread_notes": [ "..." ]
}

## proposals[]

{
  "pass_id": "pass-06-yard4",
  "depth_ids": ["DQ-B23-001"],
  "document": "doc_...",              // exactly one source document (validator rule)
  "summary": "one line for the version history",
  "purpose": "what this source is for (intake purpose)",
  "questions": ["operator question this intake supports"],
  "route": "mixed",                    // reference|register|network|operations|mixed;
                                       // "reference" only if every op is a source_note
  "operations": [ ...chp/patches operations, see OPS_REFERENCE.md... ]
}

Evidence references must belong to the proposal's own document. A fact corroborated by a second
document gets its own proposal on that document (or a basis mention), never merged supports.

## registry_notes[] (sources.json corrections the local side applies after review)

{"document": "doc_...", "field": "revision"|"authority"|"name", "current": "...", "suggested": "...",
 "page": 1, "quote": "exact title-block text", "note": "why"}

## open_questions[] (legs you could not close)

{"pass_id": "...", "depth_id": "DQ-...", "question": "...", "needs": "the exact record/page sought",
 "candidates": ["doc_..."], "evidence": [support] }

## revision_sweep_flags[] and proofread_notes[]

Free-text lines: FOR APPROVAL vs approved, FIO vs AOC, title-block vs revision-table mismatches,
revision-to-revision inference risks, invented tags/values, copied values without per-unit evidence,
merged systems, normalized spellings that should stay verbatim, applicability overreach.

## Acceptable terminal states for every depth item

- asserted: operations with exact evidence; or
- gap: source_gap operation / open_question naming the exact deciding record; or
- not applicable: state so with evidence.  "Unopened" is not terminal.
"""

EXAMPLES = """\
# Worked examples

`example-proposal-body.json` is an accepted Pass-5 proposal body (EBA-12 depth rows, committed live as
v772) - copy its operation/evidence/context style.

`example-delta-DO-NOT-APPLY.json` wraps that body in the delta shape so you can see exactly how one
proposal looks inside delta.json. Its operations were already applied to the live model in Pass 5 -
never include them in your return, and never run the applier on the example file.

`delta-template.json` is the empty skeleton to fill.
"""

APPLY_NOTES = """\
# Applying the returned delta (local side)

1. Save the returned file, e.g. `output/plant-enrichment/pass06-10-delta/returned-delta.json`.
   It must have `"base_version": 789`. If the live model has moved past v789 since this package was
   built, do not force it: export a fresh model-state and have the model rebase, or apply the delta on
   a branch of work that starts from v789.

2. Validate everything without touching the plant:

   `python tools/apply_pass06_10_delta.py output/plant-enrichment/pass06-10-delta/returned-delta.json`

   Writes `output/plant-enrichment/pass06-10-delta/check/` and `last-run.json`. Every problem is
   listed with the proposal index, document, operation and evidence id. Send unresolved-quote
   problems back to the model together with the exact text from `evidence/<doc>.json`.

3. Rehearse the full chain on a throwaway copy of the live DB:

   `python tools/apply_pass06_10_delta.py <delta> --rehearse`

   Creates `output/plant-enrichment/pass06-10-delta/rehearsal/plant.sqlite3` (copy), per-proposal
   packages under `rehearsal/NN-doc/`, and `rehearsal-summary.json` (delta hash, version chain,
   repairs). Inspect `validation.json` warnings before proceeding.

4. Apply live (guarded): the tool refuses unless the delta file hash matches the rehearsal, the live
   version still equals 789, and every proposal validates against the then-current version:

   `python tools/apply_pass06_10_delta.py <delta> --apply`

   Proposals commit in file order as v790, v791, ... Reports land in the `apply/` folder;
   `last-run.json` records the applied chain.

5. Post-apply verification (same standard as Passes 1-5):

   - `.venv-cad\\Scripts\\python.exe -m chp.verify --data data/plant`   -> ok:true, 0 errors
   - `node --check dist/app.js dist/operations-ui.js dist/plant-model.js dist/plant-scene.js dist/plant-explorer.js`
   - `node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs tests/test_plant_scene_render.cjs tests/test_viewer_math.cjs`
   - `.venv-cad\\Scripts\\python.exe -m unittest discover -s tests`
   - visual sweep per VISUAL_CHECK_GUIDANCE.md (server on port 8765, then tools/visual_sweep.cjs)

6. Then update `docs/plant-handoff/phase-progress.json`, `current/depth-queue.json` (items to
   done/evidence_gap per the open_questions), apply the delta's `registry_notes` to
   `docs/plant-handoff/inventory/sources.json` after crop-verifying each, write the pass checkpoints
   under `output/plant-enrichment/`, and commit docs/tools.

Notes:

- Whitespace-tolerant quote repair is automatic (line-wraps); repairs are logged in the summary.
- Operations are staged through the same proposal APIs the workflow requires; nothing is written to
  SQL by the tool itself.
- `registry_notes` and `open_questions` are reports for the local side; the applier does not touch
  sources.json or the queues.
"""


def load_queue():
    queue = json.loads((ROOT / 'docs/plant-handoff/current/depth-queue.json').read_text(encoding='utf-8'))
    return queue, {it['id']: it for it in queue['items']}


def doc_ids_in(path):
    if not path.exists():
        return set()
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return set()
    return set(DOC_RE.findall(text))


def batch_docs(batch):
    docs = doc_ids_in(ROOT / 'docs/plant-handoff/current' / ('%s-breadth.md' % batch))
    base = ROOT / 'output/plant-enrichment' / batch
    if base.exists():
        for p in base.rglob('*'):
            if p.suffix.lower() in ('.md', '.json', '.txt') and p.is_file() and p.stat().st_size < 2_000_000:
                docs |= doc_ids_in(p)
    return docs


def compute_scope(by_id):
    scope = {}
    for pid, batches in PASS_BATCHES.items():
        docs = set()
        for batch in batches:
            docs |= batch_docs(batch)
        for dq in DEPTH[pid]:
            item = by_id.get(dq)
            if item:
                docs |= set(DOC_RE.findall(item.get('source') or ''))
        scope[pid] = sorted(docs)
    return scope


def doc_meta(con):
    meta = {}
    for r in con.execute('SELECT * FROM documents'):
        d = dict(r)
        meta[d['id']] = d
    return meta


def evidence_stats(con):
    stats = {}
    for r in con.execute("SELECT document_id, COUNT(*) n, MAX(page) max_page,"
                         " SUM(CASE WHEN image IS NOT NULL AND image != '' THEN 1 ELSE 0 END) imgs"
                         " FROM evidence GROUP BY document_id"):
        stats[r['document_id']] = {'blocks': r['n'], 'pages': r['max_page'], 'images': r['imgs']}
    return stats


def build_model_state(dir_, con):
    out = dir_ / 'shared/model-state'
    out.mkdir(parents=True, exist_ok=True)
    meta = doc_meta(con)
    stats = evidence_stats(con)

    def dump(name, rows):
        (out / name).write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n',
                                encoding='utf-8', newline='\n')
        return out / name

    m = con.execute('SELECT value FROM meta WHERE key=?', ('version',)).fetchone()
    last = con.execute('SELECT version, proposal_id, created, summary FROM versions ORDER BY version DESC LIMIT 1').fetchone()
    version = {'version': int(m[0]), 'schema_meta': {'intake_policy': 'operations/1'},
               'latest_version_record': dict(last)}
    dump('version.json', version)

    entities = [dict(r) for r in con.execute('SELECT id, label, created_version, provenance FROM entities')]
    dump('entities.json', entities)

    ontology = [dict(r) for r in con.execute(
        'SELECT key, kind, definition, cardinality, value_type FROM ontology ORDER BY kind, key')]
    dump('ontology.json', ontology)

    assertions = []
    for r in con.execute('SELECT id, subject, predicate, value, object_entity, unit, confidence,'
                         ' origin, evidence, created_version FROM assertions'):
        d = dict(r)
        for key in ('value', 'evidence'):
            if d[key] is not None:
                try:
                    d[key] = json.loads(d[key])
                except (TypeError, ValueError):
                    pass
        assertions.append(d)
    dump('assertions.json', assertions)

    contexts = []
    for r in con.execute('SELECT assertion_id, context FROM assertion_contexts ORDER BY assertion_id'):
        try:
            ctx = json.loads(r['context'])
        except (TypeError, ValueError):
            ctx = r['context']
        contexts.append({'assertion_id': r['assertion_id'], 'context': ctx})
    dump('contexts.json', contexts)

    retirements = [dict(r) for r in con.execute('SELECT assertion_id, version, reason FROM retirements')]
    dump('retirements.json', retirements)

    aliases = [dict(r) for r in con.execute(
        'SELECT id, entity_id, alias, created_version FROM aliases ORDER BY entity_id')]
    dump('aliases.json', aliases)

    versions = [dict(r) for r in con.execute('SELECT version, proposal_id, created, summary FROM versions ORDER BY version')]
    dump('versions.json', versions)

    documents = []
    for doc_id, d in sorted(meta.items()):
        s = stats.get(doc_id, {'blocks': 0, 'pages': 0, 'images': 0})
        documents.append({'document': doc_id, 'name': d['name'], 'sha256': d['sha256'],
                          'bytes': d['bytes'], 'media_type': d['media_type'],
                          'revision': d['revision'], 'authority': d['authority'],
                          'evidence_blocks': s['blocks'], 'page_images': s['images'],
                          'pages': s['pages']})
    dump('documents.json', documents)
    return {'entities': len(entities), 'assertions': len(assertions), 'contexts': len(contexts),
            'aliases': len(aliases), 'retirements': len(retirements),
            'documents': len(documents), 'ontology': len(ontology)}


def build_evidence(dir_, con):
    out = dir_ / 'evidence'
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for row in con.execute('SELECT id FROM documents ORDER BY id'):
        doc = row['id']
        blocks = []
        for e in con.execute('SELECT id, page, locator, text, image FROM evidence WHERE document_id=?'
                             ' ORDER BY page, id', (doc,)):
            blocks.append({'id': e['id'], 'page': e['page'], 'locator': e['locator'],
                           'text': e['text'] or '', 'has_image': bool(e['image'])})
        (out / (doc + '.json')).write_text(
            json.dumps({'document': doc, 'evidence': blocks}, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8', newline='\n')
        count += 1
    return count


def copy_contracts(dir_):
    out = dir_ / 'contracts'
    out.mkdir(parents=True, exist_ok=True)
    copied = []
    docs = [
        'docs/plant-handoff/FIVE_PHASE_PLAN.md',
        'docs/plant-handoff/PASS_B_TWO_TIER_WORKFLOW.md',
        'docs/plant-handoff/ASSEMBLY_CONTRACTS.md',
        'docs/plant-handoff/SECTION_PLANS.md',
        'docs/plant-handoff/FINDINGS.md',
        'docs/plant-handoff/CONTINUATION_GUIDE.md',
        'docs/plant-handoff/BACKLOG.md',
        'docs/plant-handoff/current/CURRENT_STATUS.md',
        'docs/plant-handoff/current/yard-machine-applicability.md',
        'docs/plant-handoff/current/accepted-followups.json',
        'docs/plant-handoff/current/record-review-queue.json',
        'docs/plant-handoff/current/depth-queue.json',
        'COAL_YARD_1_PILOT_REPORT.md',
    ]
    for rel in docs:
        src = ROOT / rel
        if src.exists():
            dst = out / Path(rel).name
            shutil.copyfile(src, dst)
            copied.append(str(dst.relative_to(dir_)))
    targets = ROOT / 'docs/plant-handoff/targets'
    if targets.exists():
        shutil.copytree(targets, out / 'targets', dirs_exist_ok=True)
        copied.append('contracts/targets/ (%d target cards)' % len(list(targets.glob('*.md'))))
    for pid, batches in PASS_BATCHES.items():
        for batch in batches:
            src = ROOT / 'docs/plant-handoff/current' / ('%s-breadth.md' % batch)
            if src.exists():
                rel = 'contracts/breadth-notes/%s-breadth.md' % batch
                dst = dir_ / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                copied.append(rel)
            cp = ROOT / 'output/plant-enrichment' / batch / 'checkpoint.md'
            if cp.exists():
                rel = 'contracts/checkpoints/%s-checkpoint.md' % batch
                dst = dir_ / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(cp, dst)
                copied.append(rel)
    for batch in ('B02', 'B03', 'B04', 'B05'):
        base = ROOT / 'output/plant-enrichment' / batch / 'review'
        if not base.exists():
            continue
        for src in sorted(base.rglob('*.json')):
            if src.stat().st_size > 400_000:
                continue
            rel = 'contracts/reviews/%s/%s' % (batch, src.relative_to(base).as_posix())
            dst = dir_ / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            copied.append(rel)
    return copied


def build_formats(dir_):
    out = dir_ / 'formats'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'OPS_REFERENCE.md').write_text(OPS_REFERENCE, encoding='utf-8', newline='\n')
    (out / 'EXAMPLES.md').write_text(EXAMPLES, encoding='utf-8', newline='\n')
    src = ROOT / 'output/plant-enrichment/pass-05-zip/proposal-bodies/rehearsal-a12.json'
    if src.exists():
        body = json.loads(src.read_text(encoding='utf-8'))
        (out / 'example-proposal-body.json').write_text(
            json.dumps(body, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
        example = {'_warning': 'Illustrative only. These operations were already applied in Pass 5 '
                               '(v772). Never include them in a return and never apply this file.',
                   'schema_version': 1, 'passes': ['pass-06-yard4'], 'base_version': BASE_VERSION,
                   'model': 'example', 'date': '2026-10-17',
                   'proposals': [{'pass_id': 'example', 'depth_ids': ['DQ-EXAMPLE'],
                                  'document': 'doc_0adf08e6189847b88503',
                                  'summary': body.get('summary', ''), 'route': 'mixed',
                                  'operations': body.get('operations', [])}],
                   'registry_notes': [], 'open_questions': [],
                   'revision_sweep_flags': [], 'proofread_notes': []}
        (out / 'example-delta-DO-NOT-APPLY.json').write_text(
            json.dumps(example, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    template = {'schema_version': 1, 'passes': list(PASS_NAMES), 'base_version': BASE_VERSION,
                'model': '', 'date': '',
                'proposals': [{'pass_id': 'pass-06-yard4', 'depth_ids': ['DQ-B23-001'],
                               'document': 'doc_...', 'summary': '', 'purpose': '', 'questions': [],
                               'route': 'mixed', 'operations': []}],
                'registry_notes': [], 'open_questions': [], 'revision_sweep_flags': [],
                'proofread_notes': []}
    (out / 'delta-template.json').write_text(
        json.dumps(template, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def build_passes(dir_, scope, by_id, meta, stats):
    out = dir_ / 'passes'
    out.mkdir(parents=True, exist_ok=True)
    scope_doc = {'base_version': BASE_VERSION, 'generated_from_live_version': BASE_VERSION, 'passes': {}}
    for pid, items in DEPTH.items():
        scope_doc['passes'][pid] = {
            'name': PASS_NAMES[pid], 'batches': PASS_BATCHES[pid], 'focus': FOCUS[pid],
            'depth_items': [by_id[i] for i in items if i in by_id],
            'primary_docs': scope[pid],
        }
        lines = ['# %s' % PASS_NAMES[pid], '',
                 'Base version %d. Read `TOP_MODEL_BRIEF.md` first; this file is your scope.' % BASE_VERSION, '',
                 '## Focus and accepted-work awareness', '', FOCUS[pid], '',
                 '## Depth items (close EVERY named leg; terminal state per item)', '']
        for dq in items:
            item = by_id.get(dq)
            if not item:
                continue
            lines += ['### %s  (%s)' % (item['id'], item.get('priority', '')),
                      '- target: %s' % item.get('target', ''),
                      '- missing (these are the legs): %s' % item.get('missing', ''),
                      '- queue source hint: %s' % item.get('source', ''), '']
        lines += ['## Primary documents (also see shared/model-state/documents.json for all 266)', '',
                  '| document | name | rev | authority | evidence blocks | image pages |',
                  '|---|---|---|---|---|---|']
        for doc in scope[pid]:
            d = meta.get(doc)
            if not d:
                continue
            s = stats.get(doc, {'blocks': 0, 'images': 0})
            lines.append('| %s | %s | %s | %s | %d | %d |'
                         % (doc, d['name'].replace('|', '/'), d['revision'] or '-',
                            d['authority'] or '-', s['blocks'], s['images']))
        lines += ['', '## Contracts to respect',
                  '- `contracts/%s-breadth.md` and the batch checkpoints in `contracts/checkpoints/`'
                  % (PASS_BATCHES[pid][0]),
                  '  list what Tier-1 already asserted (do not re-assert); the per-batch notes for',
                  '  every batch in this pass are in `contracts/breadth-notes/`.',
                  '- Global planning: `contracts/FIVE_PHASE_PLAN.md`, `contracts/SECTION_PLANS.md` (P08/P09/P15),',
                  '  `contracts/ASSEMBLY_CONTRACTS.md`, `contracts/FINDINGS.md`,',
                  '  `contracts/PASS_B_TWO_TIER_WORKFLOW.md`.', '']
        (out / (pid + '.md')).write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    (out / 'scope.json').write_text(
        json.dumps(scope_doc, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def build_brief(dir_, counts, scope, meta, stats):
    total_ev = sum(s['blocks'] for s in stats.values())
    doc_count = len(meta)
    lines = [
        '# Passes 6-10 full-depth handover - top-model brief',
        '',
        'You are the reviewing/commissioning engineer. The local tier is suspended for Passes 6-10:',
        'you perform the complete depth work for all five passes against the accepted plant model at',
        'v%d and return ONE delta file that the local side applies through its proposal APIs.' % BASE_VERSION,
        '',
        '## What this package contains',
        '',
        '- `passes/pass-06..10.md` + `passes/scope.json` - the five pass scopes: depth items with their',
        '  named legs, primary documents and focus; close EVERY leg of EVERY item (a pass is complete',
        '  only when each item reaches a terminal state: asserted with exact evidence, or an explicit',
        '  gap naming the deciding record).',
        '- `shared/model-state/` - the live model at v%d: %d entities, %d ontology keys,' % (
            BASE_VERSION, counts['entities'], counts['ontology']),
        '  %d assertions, %d assertion contexts, %d aliases, %d retirements, %d documents,' % (
            counts['assertions'], counts['contexts'], counts['aliases'], counts['retirements'],
            counts['documents']),
        '  full version history. Read `assertions.json` before asserting anything: it is what is',
        '  already accepted; do not duplicate it, and preserve its recorded conflicts.',
        '- `evidence/<doc>.json` - for every corpus document the immutable extracted text with block',
        '  ids (`ev_...`), page numbers and image availability. THIS is the citable text: quotes in',
        '  your operations must be exact substrings of it (or use a region support on an image page).',
        '  Total: %d evidence blocks across %d documents.' % (total_ev, doc_count),
        '- `contracts/` - the plan, workflow, assembly contracts, findings, breadth notes/checkpoints',
        '  per batch (what Tier 1 already asserted - do not re-assert), B02-B05 review findings, the',
        '  Yard-1 pilot report, target cards, accepted-followups and the record-review queue.',
        '- `formats/` - OPS_REFERENCE.md (operation schema + validator limits), EXAMPLES.md,',
        '  delta-template.json, an accepted proposal body and a delta-shape example.',
        '- `code/` - the applier the local side runs on your return (for reference).',
        '',
        '## The original source PDFs',
        '',
        'Originals are NOT in this package (size). They are in cloud storage provided alongside this',
        'package (266 files). `shared/model-state/documents.json` maps each `doc_...` id to its file',
        'name, byte size and sha256 - use it to open the right file and to state which revision you',
        'read. The extracted text in `evidence/` is what the local validator can cite; the PDFs are',
        'for reading the actual drawings/cells (fonts, digits, title blocks, notes). If a cell is not',
        'legible or the OCR text cannot support an exact quote, put the item in `open_questions`',
        'asking the local side for a re-crop at the exact page/region, or use a region-only support.',
        '',
        '## How to work',
        '',
        '1. Work pass by pass, depth item by depth item, using the queue "source" hints as entry',
        '   points; search the other included documents when a leg points elsewhere (e.g. vendor',
        '   manuals for actuator/weigher/hoist internals).',
        '2. For every leg decide the terminal state and record it: an operation (assertion etc.) with',
        '   exact evidence, a source_gap naming the exact deciding record, or an open_question.',
        '3. Group operations by source document - exactly one `document` per proposal - in the order',
        '   they should be applied. Splitting a document across passes is fine; splitting a proposal',
        '   across documents is not.',
        '4. Prefer existing entity ids and ontology predicates. New entities only with evidence and a',
        '   `tmp_` id; new ontology keys only when nothing existing fits.',
        '5. Keep every open conflict open (qualified alternatives + deciding record). Retire only',
        '   with crop-level proof that the earlier reading was wrong.',
        '6. Finish with the standing sweeps: `revision_sweep_flags` (approval/FIO/title-block vs',
        '   revision-table mismatches, revision clouds treated as selections) and `proofread_notes`',
        '   (invented tags, copied values, merged systems, over-normalized spellings).',
        '',
        '## Non-negotiables (full detail in formats/OPS_REFERENCE.md)',
        '',
        GLOBAL_RULES,
        '',
        '## Deliverable',
        '',
        'Exactly one UTF-8 JSON file following `DELTA_FORMAT.md` (see also `formats/delta-template.json`).',
        'Set `base_version` to %d. The local side validates with the canonical validator, rehearses on a' % BASE_VERSION,
        'copy, then applies guarded - see `APPLY_NOTES.md`. No SQL, no direct database writes, no',
        'proposal bodies outside the delta format.',
        '',
        '## Depth-item summary per pass',
        '',
    ]
    for pid, items in DEPTH.items():
        lines.append('- **%s** (%s): %s' % (PASS_NAMES[pid], ', '.join(PASS_BATCHES[pid]),
                                            ', '.join(items)))
    (dir_ / 'TOP_MODEL_BRIEF.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    (dir_ / 'DELTA_FORMAT.md').write_text(DELTA_FORMAT, encoding='utf-8', newline='\n')
    (dir_ / 'APPLY_NOTES.md').write_text(APPLY_NOTES, encoding='utf-8', newline='\n')


def build_checks(dir_, counts):
    text = [
        'Passes 6-10 handover package - state at generation',
        '',
        'Live model: v%d (Passes 1-5 complete live: v718 baseline -> v789).' % BASE_VERSION,
        'Corpus: %d documents, %d evidence blocks.' % (counts['documents'], counts['evidence']),
        'Model: %d entities, %d assertions, %d contexts, %d aliases, %d retirements.' % (
            counts['entities'], counts['assertions'], counts['contexts'], counts['aliases'],
            counts['retirements']),
        '',
        'Last verified state (Pass 5, v789):',
        '  chp.verify --data data/plant -> ok (266 documents, 5196 evidence blocks, 789 versions, 0 errors)',
        '  node tests 53/53; unittest 76 OK; visual sweep 18/18 steps + 4/4 source journeys, 0 console errors.',
        '',
        'Verification commands to repeat after applying the delta:',
        '  .venv-cad\\Scripts\\python.exe -m chp.verify --data data/plant',
        '  node --check dist/app.js dist/operations-ui.js dist/plant-model.js dist/plant-scene.js dist/plant-explorer.js',
        '  node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs tests/test_plant_scene_render.cjs tests/test_viewer_math.cjs',
        '  .venv-cad\\Scripts\\python.exe -m unittest discover -s tests',
        '  tools/visual_sweep.cjs sweep per VISUAL_CHECK_GUIDANCE.md (server on port 8765)',
    ]
    (dir_ / 'checks.txt').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')


def main():
    con = sqlite3.connect(DBSRC.as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    version = int(con.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0])
    assert version == BASE_VERSION, 'live version %s != package base %s' % (version, BASE_VERSION)

    queue, by_id = load_queue()
    meta = doc_meta(con)
    stats = evidence_stats(con)
    scope = compute_scope(by_id)

    if ZIP.exists():
        shutil.rmtree(ZIP)
    ZIP.mkdir(parents=True)

    counts = build_model_state(ZIP, con)
    counts['evidence'] = con.execute('SELECT COUNT(*) FROM evidence').fetchone()[0]
    counts['documents'] = len(meta)
    n_ev = build_evidence(ZIP, con)
    assert n_ev == len(meta), (n_ev, len(meta))
    copied = copy_contracts(ZIP)
    build_formats(ZIP)
    build_passes(ZIP, scope, by_id, meta, stats)
    build_brief(ZIP, counts, scope, meta, stats)
    build_checks(ZIP, counts)

    code = ZIP / 'code'
    code.mkdir(parents=True, exist_ok=True)
    for name in ('apply_pass06_10_delta.py', 'evidence_helper.py'):
        src = ROOT / 'tools' / name
        if src.exists():
            shutil.copyfile(src, code / name)

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(ZIP.rglob('*')):
            if path.is_file():
                zf.write(path, path.relative_to(ZIP.parent).as_posix())
    raw = sum(p.stat().st_size for p in ZIP.rglob('*') if p.is_file())
    print(json.dumps({'zip_folder': str(ZIP), 'archive': str(ARCHIVE),
                      'files': sum(1 for p in ZIP.rglob('*') if p.is_file()),
                      'raw_bytes': raw, 'zip_bytes': ARCHIVE.stat().st_size,
                      'evidence_files': n_ev, 'contracts': len(copied)}, indent=2))


if __name__ == '__main__':
    main()
