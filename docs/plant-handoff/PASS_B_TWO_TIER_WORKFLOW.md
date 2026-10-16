# Pass B two-tier workflow (local + top model) — 10 passes

Status: Pass A 100% breadth-complete, v718, 47/47 batches. Pass B depth work only.
Source of truth: `docs/plant-handoff/FIVE_PHASE_PLAN.md` (Pass B priority),
`docs/plant-handoff/phase-progress.json` (resume pointer),
`docs/plant-handoff/current/depth-queue.json` (64 items: 23x P1 open, 31x P2 open, 9x P3 open, 1x evidence_gap).
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

\* Known duplicate ID: two items share `DQ-B15-001`. Rename the B15 EAD1/EAF1
item to `DQ-B15-002` when Pass 9 starts; track both until then.

Top-model focus per pass: Pass 1 rope/sheave + drivetrain/brake + dust/lube;
Pass 2 exciter/settings + FD/FG logic + GA/control conflicts; Pass 3 drive
internals + HT/415V + cleaner qty + weigher limits; Passes 4-6 machine drives +
fire/lube/AP-SV; Pass 7 actuators + weigher calibration + sampler timer;
Pass 8 limit tags + clamp pressure + level/CO + fan curves; Pass 9 PS polarity
+ 5/10m3 pit + header branches (no new physical pipes, no System1/2 collapse);
Pass 10 MCC cubicles + thin-target scope only.

## 5. Tracking for future sessions

Read order: this file -> `phase-progress.json` (`next_action`) ->
`current/depth-queue.json` -> pass checkpoint in `output/plant-enrichment/`.
Per trip: set items `in_progress` on zip build, `done`/`evidence_gap` only after
guarded accept + verification + visual pass. If top struggles on a yard pass
(4/5/6), split it into drives-trip + services-trip rather than enlarging the zip.

## Next action

Start **Pass 1** (DQ-B06-001 + DQ-B07-001 + DQ-B08-001). Build
`pilot-pass-1/` per §3 with max 3 hard questions, upload, apply return through
normal proposals, verify, then continue Passes 2-10 in order.
