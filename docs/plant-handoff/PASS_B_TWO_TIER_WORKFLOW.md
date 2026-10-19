# Pass B two-tier workflow (local + top model) — 10 passes

Status: Pass A 100% breadth-complete, v718, 47/47 batches. Pass B depth work only;
Passes 1-5 complete live (v789), Passes 6-10 closeout applied live (v882, 2026-10-18,
including the returned Pass 11 silo-reference restructure) via the single top-model
package round (§2b): package `output/plant-enrichment/pass06-10-top-model.zip`, applied back with
`tools/apply_pass06_10_delta.py`. Passes 12-15 applied live on 2026-10-19 (v883-v999).
Source of truth: `docs/plant-handoff/FIVE_PHASE_PLAN.md` (Pass B priority),
`docs/plant-handoff/phase-progress.json` (resume pointer),
`docs/plant-handoff/current/depth-queue.json` (64 items; 62 done, 1 open, 1 evidence_gap as of 2026-10-19).
This file defines *how* Pass B runs in two tiers. It does not change acceptance rules.

## 1. Roles

- **Local agent (this repo, on user PC):** routine extraction, first-draft claims,
  all checks (`chp.verify`, Node scene tests, `tools/visual_sweep.cjs`,
  preservation + pilot audits), zip building for hard cases only, applying
  top-model returns through the existing proposal APIs, verification, commits.
- **Top model (Claude/Gemini, off-PC):** hard thinking only — tricky drawing crops,
  conflict resolution, fixing failed drafts. Never writes canonical tables directly.
  Returns a result file the local agent stages as one-source proposals.

Canonical changes only through supported proposal APIs. No direct SQL edits.
No replay of old enrichment migrations. `data/` and `output/` stay untracked;
commit `docs/tools/code` only.

## 2. One round

1. Local works one pass below (breadth items already done; depth detail only).
2. Local sorts claims into pass vs unsure/failed-check.
3. Script/manual assembles **one small zip per pass**: relevant db rows only
   (never whole DB), drawing pages as cropped images (never full originals),
   local draft answer, failed checks, exact questions.
4. User uploads zip to top model. Top returns fixed/confirmed claims.
5. Local stages each source as its own proposal (validator rule: one source
   document per proposal), rehearses on a copy, sequential guarded accept.
6. Local runs full verification (integrity/FK, preservation, both pilot audits,
   browser source-open/return + narrow-width journey, visual sweep 0 console errors).
7. Local marks `depth-queue.json` items `in_progress` -> `done`/`evidence_gap`,
   updates the pass checkpoint, commits docs/tools.

### 2a. Batched-run deviation (user-directed, Passes 5-10, from 2026-10-17)

The user directed Passes 5-10 to run as one batched effort with a stricter local
tier, deviating from §2 as follows (acceptance rules unchanged):

- The local tier applies only 100%-confidence work: CERTAIN printed rows become
  `document_note` ops and ABSENT legs `source_gap` ops. Every conflict, illegible
  digit, unit clash or mapping question ships in the pass zip as draft claims +
  numbered questions instead of being locally resolved (Pass 5: 23 drafts, 10 Qs).
- Each pass zip still gets its own top-model round; returns fold per pass as:
  retain/confirm notes on the subject entity, operation-text corrections,
  finding-row corrections, and evidence-backed retirements (crop-level re-read
  only, reason recorded; Pass 5 retired 2 prior facts). A pass is applied live
  only after its fold-in; verification (rehearsal equality, `chp.verify`, Node,
  unittest, visual sweep) is per pass, not per batch.
- Registry (`sources.json`) corrections are applied per pass for the
  unambiguous, crop-verified subset only; ambiguous/blank entries stay queued.
- Every pass checkpoint records this deviation and the pass's zip/return state.

### 2b. Single-package top-model round for Passes 6-10 (user-directed, 2026-10-17)

The user requested one complete handover package for all five remaining passes
instead of per-pass zips: `output/plant-enrichment/pass06-10-top-model.zip`
(16 MB; built by `tools/build_pass06_10_zip.py`; brief, return format, apply
notes, JSON model-state exports and a read-only `plant-v789.sqlite3` snapshot
inside). The top model works the full depth of Passes 6-10 (all 31 open queue
legs; B46 included for awareness only — DQ-B46-001 stays local) and returns one
`delta.json` pinned to `base_version` 789. The local side validates (`--check`),
rehearses on a DB copy (`--rehearse`) and applies guarded (`--apply`) with
`tools/apply_pass06_10_delta.py`; operations stage through the same proposal
APIs, so acceptance rules are unchanged. The local 100%-confidence tier is
suspended for these passes. Original PDFs are not in the zip; the user provides
cloud access to the 266 originals (match by `sha256`/name via
`shared/model-state/documents.json`). The return additionally carried a Pass 11
silo-reference restructure (22 proposals re-hierarchizing plant-wide blending-silo
assembly references), applied in the same delta at the user's direction
(Option A: apply everything in one pass).

### 2c. Stale entity IDs in a returned delta (Pass 15, 2026-10-19)

A returned delta may reference entity IDs that exist in **no** version of the live
model — the entity was re-created, or the model was rolled back and re-applied, after
the delta was authored. `--check` rejects such a proposal with "unknown entity
reference"; the operation is not silently dropped.

Repair it only when the identity is unambiguous, with
`tools/remap_delta_entity_ids.py`:

```powershell
python tools/remap_delta_entity_ids.py <delta.json> <mapping.json> <remapped-delta.json>
```

The mapping is explicit (`stale_id -> {id, label}`) and the tool refuses to remap
unless **all** of the following hold:

- the stale ID does not resolve in the live model (it is stale, not merged);
- the replacement ID resolves in the live model;
- the replacement's canonical label equals the expected label **exactly**;
- that label appears verbatim in the affected operation's own `basis`/context text;
- every mapping entry is actually used by the delta.

The remapped delta and a `.remap.json` report are kept beside the rehearsal. Every
other entity reference in the delta is left untouched, and the repair is recorded in
the pass checkpoint. Do not hand-edit a returned delta and do not invent a mapping:
an unmappable reference is an evidence question, not a rename.

## 3. Handoff package: what local sends, what top returns
### 3A. Input zip (local -> top), one per pass

```
<pass-id>/                       e.g. pilot-pass-1/, pass-04-yard2/
  TOP_MODEL_BRIEF.md    — paste-ready instruction package (§3B). The only file
                          the user pastes/uploads with the zip; everything else
                          is context it refers to.
  draft-claims.json     — local first-draft claims that failed or are unsure.
                          Same shape as repo claims: id, subject (canonical ent_
                          id or descriptive name), predicate, value/unit or
                          object_entity, basis/conditions, unsure flag + question id.
  db-slice.json         — only affected canonical rows + their active claims/
                          aliases/conflicts (never the whole DB).
  sources.json          — manifest for every cited page: document id, immutable
                          hash, drawing/revision/status, applicable equipment,
                          reviewed pages/regions, crop filename. Unreviewed pages
                          are listed as unreviewed, never marked reviewed.
  images/               — 3-6 readable crops (PNG) with headers/units visible,
                          named <doc>__p<page>__<region>.png; dense BOMs/tables/
                          symbols must be legible, not thumbnails.
  checks.txt            — the exact failed output (verify / tests / route check).
  example-accepted.json — one prior accepted result for the same family so the
                          top model copies the field style, never the values.
  result-template.json  — empty §3C template the top model fills in.
  code/ (optional)      — relevant snippet only for the family under review.
```

Guardrails: 2-4 hard questions per zip, 3-6 pages, <200 rows. Large docs
(92pp HVAC, 59pp MCC, 50pp fire) split across trips. Full originals and the live
`data/plant` directory never leave the PC.

### 3B. Instruction package (contents of TOP_MODEL_BRIEF.md)

Each brief is generated per pass from this template (concrete IDs/questions
filled in; rules below are fixed text):

1. Role + scope: "You are the reviewing engineer. Decide only the listed
   questions for the listed depth IDs using only the crops + slices provided.
   Do not assert anything not visible in the crops."
2. Non-negotiable rules: no invented field/KKS/cable/spare tags; no invented
   ratings/settings; keep A/B lanes, numbered-machine and revision applicability
   explicit; keep descriptive names when no tag exists; preserve disagreements
   as qualified alternatives with the record needed to settle them; never merge
   the two DFDS systems, never collapse System1/2, never connect every tripper
   to every bunker; design capacity is not live inventory.
3. Per-question block: question id, depth id, plain-language ask, local draft
   claim ids, the exact crops/rows that bear on it, what check failed.
4. Return order: "Return exactly one file, `top-model-result.json`, following
   `result-template.json` (§3C). No DB edits, no SQL, no proposal bodies —
   local stages those."

### 3C. Return contract (top -> local): output format

The top model returns exactly one machine-readable file plus an optional short
note. Local rejects anything else without review.

- File: `top-model-result.json` (UTF-8 JSON, schema_version 1).
- Top-level keys: `pass_id`, `depth_ids`, `model`, `date`,
  `resolutions[]`, `preserved_disagreements[]`, `open_questions[]`.
- One entry in `resolutions[]` per draft claim or per question:

```json
{
  "draft_id": "draft_001",
  "question_id": "Q1",
  "verdict": "confirmed | corrected | rejected_needs_source | not_resolvable",
  "subject": "ent_91dd763af7f4417ebaa6",
  "predicate": "has_motor_rating_kw",
  "value": "132",
  "unit": "kW",
  "object_entity": null,
  "applicability": "EAC-2A only; do not copy to 2B without its own evidence",
  "conditions": "duty drive as drawn; standby/commissioned values not asserted",
  "supports": [
    {"document": "doc_030c8f82fb674548a4dc", "page": 2,
     "crop": "doc_030c8f82fb674548a4dc__p2__schedule.png",
     "region": [0.10, 0.20, 0.80, 0.35],
     "quote": "exact visible cell/paragraph text"}
  ],
  "rationale": "why this reading wins over the alternative, in one paragraph",
  "confidence": 0.85,
  "proposal_group": "doc_030c8f82fb674548a4dc",
  "needs": "nothing | exact drawing/manual/page that would settle it"
}
```

- `proposal_group` must equal one source document: local splits the return into
  one proposal per group (validator rule). A resolution citing two sources is
  staged as corroborating claims on the reused identity, not one merged proposal.
- `verdict` meanings: `confirmed` (draft stands, supports added),
  `corrected` (use top's subject/predicate/value), `rejected_needs_source`
  (draft withdrawn, `needs` names the exact source/page sought),
  `not_resolvable` (kept as qualified disagreement in
  `preserved_disagreements[]` with both readings + deciding record).
- Local acceptance gate: every `confirmed`/`corrected` needs at least one
  legible support with document + page + crop + region/quote and explicit
  applicability. Missing supports, invented tags/values, merged systems/lanes,
  or revision-to-revision inference beyond identity are rejected and sent back
  as a narrowed follow-up zip. Accepted resolutions become repo `claims.json`
  entries with full evidence, then rehearsal -> guarded accept -> verification
  (§2 steps 5-7).

### 3D. Two standing text-only uses (no new zip, no new round trip)

Proven in Pass 1; run on every pass before staging:

1. **Revision-status sweep.** Paste the pass's source list (document, revision,
   approval/FIO stamp + date, sheet count) and ask: flag FOR APPROVAL vs approved,
   FIO vs AOC, title-block vs revision-table mismatches, same-date transmittal links
   that are not established, and any reading that treats a review comment or an
   approval stamp as a final selection. Local verifies each flag against the crops
   before staging.
2. **Pre-stage proofread.** Paste the staged proposal bodies (operations + evidence
   ids/regions, not the DB) and ask: flag invented tags/values, copied A/B-lane or
   Type-1/2 values without per-unit evidence, merged systems, normalised spellings
   that should stay verbatim, and applicability overreach. Local re-checks each flag;
   the proofread never replaces rehearsal, preservation, or verification.

## 4. The 10 passes (start at Pass 1)

Order respects plant flow (jetty -> yards -> reclaim -> bunkers -> services ->
plant-wide) and Pass B priority (P1 drives/protections first, P2 auxiliaries,
P3 BOM last). DQ-B02-002 (`evidence_gap`, 180055 missing) stays parked.
DQ-B46-001 is local exhaustive verification, no top trip.

| Pass | Name | Depth IDs |
|---|---|---|
| 1 | Jetty front end | DQ-B06-001(P1), DQ-B07-001(P1), DQ-B08-001(P1) |
| 2 | Screens / TP3 / Sampling1 | DQ-B09-001(P1), DQ-B09-002(P2), DQ-B10-001(P1), DQ-B10-002(P2), DQ-B11-001(P1) |
| 3 | Conveyors 4/5/6 chain | DQ-B12-001(P1), DQ-B12-002(P2), DQ-B13-001(P1), DQ-B13-002(P2), DQ-B14-001(P2), DQ-B14-002(P2), DQ-B14-003(P2) |
| 4 | Yard2 full | DQ-B17-001(P1), DQ-B17-002(P2), DQ-B18-001(P1), DQ-B18-002(P1), DQ-B19-001(P2), DQ-B19-002(P2), DQ-B19-003(P3), DQ-B19-004(P3) |
| 5 | Yard3 full | DQ-B20-001(P1), DQ-B20-002(P2), DQ-B21-001(P1), DQ-B21-002(P1), DQ-B22-001(P2), DQ-B22-002(P2), DQ-B22-003(P3), DQ-B22-004(P3) |
| 6 | Yard4 full | DQ-B23-001(P1), DQ-B23-002(P2), DQ-B24-001(P1), DQ-B24-002(P1), DQ-B25-001(P2), DQ-B25-002(P2), DQ-B25-003(P3), DQ-B25-004(P3) |
| 7 | Reclaim to TP13 | DQ-B26-001(P2), DQ-B27-001(P2), DQ-B28-001(P1), DQ-B29-001(P1), DQ-B37-001(P2), DQ-B38-001(P1) |
| 8 | Trippers / Bunkers / DE | DQ-B39-001(P1), DQ-B40-001(P1), DQ-B41-001(P2), DQ-B42-001(P2) |
| 9 | Common services + TP1/Yard1 | DQ-B02-001(P2), DQ-B02-003(P2), DQ-B02-004(P2), DQ-B03-001(P2), DQ-B04-001(P2), DQ-B05-001(P2), DQ-B15-001(B15/B16,P2), DQ-B15-001(B15,P2)*, DQ-B16-001(P2) |
| 10 | Plant-wide closeout | DQ-B43-001(P2), DQ-B44-001(P3), DQ-B45-001(P3), DQ-PILOT-001(P3), DQ-B46-001(P1-meta, local only) |

\* Former duplicate ID: the B15 EAD1/EAF1 item was renamed `DQ-B15-002` in
`depth-queue.json` when the Pass 9 leg was applied (2026-10-18, v882).

Top-model focus per pass: Pass 1 rope/sheave + drivetrain/brake + dust/lube;
Pass 2 exciter/settings + FD/FG logic + GA/control conflicts; Pass 3 drive
internals + HT/415V + cleaner qty + weigher limits; Passes 4-6 machine drives +
fire/lube/AP-SV; Pass 7 actuators + weigher calibration + sampler timer;
Pass 8 limit tags + clamp pressure + level/CO + fan curves; Pass 9 PS polarity
+ 5/10m3 pit + header branches (no new physical pipes, no System1/2 collapse);
Pass 10 MCC cubicles + thin-target scope only.

## 5. Complete-pass rule (no partial passes)

When the user asks for a pass, the pass is the unit of delivery — not the first
zip. A pass is complete only when **every depth item in its table row** reaches a
terminal state in the same run:

- For each item, close **every named leg** (e.g. drives *and* protections *and*
  schedule rows *and* internals verdicts): assert it with exact evidence, or record
  it as an explicit gap / `evidence_gap` naming the exact deciding record.
- Local extraction first (schedule rows, control clauses, vendor sheets already in
  the corpus); top model only for hard/conflict items. A pilot zip that answers 3
  questions while sibling legs sit unopened is a first round, never a completion.
- Follow-up zips (missing crops, deciding records) belong to the same pass until
  its items are terminal. Never report a pass complete, or move its items to `done`,
  with legs unaddressed and unnamed.
- Honest terminal states: `done` (all legs asserted or gapped with deciding record,
  residual P3 vendor-BOM piece detail transferred by name), or `evidence_gap`
  (deciding record identified but absent from the corpus). `in_progress` with a
  checkpoint listing open legs is the only acceptable mid-pass state.

## 6. Tracking for future sessions

Read order: this file -> `phase-progress.json` (`next_action`) ->
`current/depth-queue.json` -> pass checkpoint in `output/plant-enrichment/`.
Per trip: set items `in_progress` on zip build, `done`/`evidence_gap` only after
guarded accept + verification + visual pass. If top struggles on a yard pass
(4/5/6), split it into drives-trip + services-trip rather than enlarging the zip.

## Next action

**Passes 12-15 applied live v999 (2026-10-19).** Pass 12 physical parts and wiring
(v883-v932, 50 proposals / 7612 operations), Pass 13 plantwide discrepancy fixes
(v933-v940, 8 proposals / 574 operations, re-applied clean from v932), Pass 14
plantwide audit and completion (v941-v991, 51 proposals / 383 operations) and Pass 15
plantwide flow topology (v992-v999, 8 proposals / 1926 operations: 1698 `assert` +
228 `qualify`) were validated (`--check`), rehearsed (`--rehearse`) and accepted
(`--apply`) with `tools/apply_pass06_10_delta.py`; rehearsal and live chains matched
in every case, 0 repairs, 0 problems.

Pass 15 also needed the §2c stale-ID repair: two returned references
(`ent_3a18ea7ae39947879c1e`, `ent_1e7e545350a9400888f4`) existed in no model
version; both resolved to unique exact-label canonical entities created at v944
(KF-4 and EAC-5A discharge chutes), applied via
`tools/remap_delta_entity_ids.py` with a `.remap.json` report.

Verification at v999: `chp.verify` 0 errors (266 docs / 5196 evidence / 999 versions),
Node 53/53, unittest 76 OK (3 skipped), preservation 0 assertions/entities/aliases/
merges lost and 0 new retirements, +1698 assertions / +1926 `assertion_contexts`
(exact op accounting), visual sweep 18/18 steps + 4/4 source journeys, 0 console
errors — run `tools/visual_sweep.cjs` only after polling `/api/state` until 200 on a
fresh server (cold payload is ~46 MB / ~19 s and races the sweep's `.ps-root` wait),
and start the server in the same run as the sweep or it is reaped between them.
The sweep's source-button locator is class-agnostic
(`.ps-inspector button[data-action="fact-source"]`); the scene inspector's class was
renamed `ps-source` -> `ps-source-chip` on 2026-10-18 and a class-pinned locator
silently fails every source journey.

Depth queue: 62/64 `done`; DQ-B02-002 parked `evidence_gap`; DQ-B46-001 open for
local exhaustive per-claim verification; 10 residual field/commissioning questions
recorded in `depth-queue.json`. Checkpoint: `output/plant-enrichment/pass15/checkpoint.md`.
Next: local DQ-B46-001 exhaustive verification and any user-directed follow-up round.
