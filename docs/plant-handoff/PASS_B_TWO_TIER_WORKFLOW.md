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

## 3. Zip format (pilot and full passes)

```
pilot-<pass-id>/
  README.md           — depth IDs, exact questions, what failed locally
  draft-claims.json   — subject/predicate/value/unit, source doc/page/region,
                        basis/conditions, unsure flags (claims.json style)
  db-slice.json       — only affected canonical rows + active claims
  example-accepted.json — one prior accepted result for same family (format ref)
  images/             — 3-6 readable crops with headers/units, named by doc/page
  checks.txt          — verify/test output showing the failure
  code/               — relevant snippet only (proposal builder / check for family)
```

Guardrails: 2-4 hard questions per zip, 3-6 pages, <200 rows. Large docs
(92pp HVAC, 59pp MCC, 50pp fire) split across trips. Every returned claim still
needs doc_id/hash/revision/page/region + applicability to be accepted.

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
