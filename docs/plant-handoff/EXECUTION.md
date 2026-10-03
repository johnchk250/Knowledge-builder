# Execution, worked examples and acceptance gates

For current pilot status and the full continuation method, start with [CONTINUATION_GUIDE.md](CONTINUATION_GUIDE.md). Source examples below remain useful patterns; reconcile their IDs and current applicability rather than replaying them.

## One bounded batch at a time

Use `batches.json` and the selected section plan. The next agent owns the review and implementation of that batch; it does not need to redesign the whole model. Continue independent work when a source ambiguity blocks only one claim. Do not ask the user to make routine architecture choices already settled here.

1. Read active `OPERATIONS_INGESTION_WORKFLOW.md`, this handoff and current ingestion contracts. Inspect Git changes and current model version; preserve unrelated work.
2. Refresh a read-only snapshot and capture baseline IDs, aliases, component closure, current supports and neighbouring boundaries. Inspect the actual browser. The handoff's v510 is a baseline, never a version to force onto a later database.
3. Make a consistent SQLite backup plus the required originals/renders or use the application's complete backup mechanism. Keep source files immutable. A JSON model export alone is not a restorable full backup.
4. Start the batch folder `output/plant-enrichment/<batch-id>/` with identity decisions, target coverage rows, source dispositions, claim ledger, boundary ledger and unresolved findings.
5. Inspect original candidate documents in the prescribed order. Follow source drawing references, model numbers and related equipment, not just tag text matches. Read title/revision/comment pages as well as relevant GA/BOM/P&ID regions. Register negative searches.
6. Reuse identities; construct supported components, ownership/place edges, then mechanical/material/utility/control/electrical relations, then specifications and source-qualified control requirements. Add only warranted ontology extensions.
7. Rehearse on a separate database copy. Stage one source at a time, validate, inspect warnings, accept through the versioned mechanism and resolve temporary IDs before the dependent source/batch. Check preservation and semantic expectations against originals.
8. Apply within the current user's authorized implementation scope, guarded against the current version. A stale proposal is rebuilt/reviewed; it is not forced through. This planning task itself did not authorize an unattended blanket re-ingestion of the plant.
9. Verify the actual scene and individual evidence journey. Record final model versions and reusable test/inspection evidence. Update batch progress and the next handoff checkpoint.

## Source review ledger

Every candidate needs: document ID/hash, filename/drawing number, PDF pages and printed sheets, title-block revision/status, exact regions reviewed, applicability, use/disposition and reason. Allowed dispositions: used, corroborating, superseded-with-evidence, not-applicable, ambiguous, illegible, deferred-with-reason. A keyword match is a retrieval lead, not applicable evidence.

Every proposed claim needs: component ID/temporary identity, predicate/value/unit or relationship endpoints, origin, basis/condition/mode/validity if supported, evidenceID+quote/region and related disagreement/gap. Keep raw reported quantity and any derived quantity separate. Confidence measures extraction judgement, not engineering reliability.

For source-logic claims add initiator, polarity, AND/OR grouping, target action, delay, mode, reset and exception. Empty fields mean “not stated / unresolved” with explanation; they do not authorize defaults.

## Worked example 1: a sourced component count

Accepted EAC-1A PCS component: `ent_2c78bd577184464394a0`.

| Claim | Accepted assertion | Support and semantics |
|---|---|---|
| `quantity = 14 pairs` | `fact_d99e684c38db42a38b0f` | Explicit original unit, per conveyor |
| `individual_device_count = 28 switches` | `fact_1c6934bc763b457989e2` | Inferred arithmetic:14 pairs ×2 switches/pair |

Both point to GA1AB PDF page 4, document `doc_603b4d9077e14d16b605`, evidence `ev_fab2c81084694e4e8126`, region `[0.757,0.686,0.949,0.718]`. Resolve the original hash through `inventory/sources.json`; inspect the count row and its headings before adopting the pattern elsewhere. The display should say **14 pairs (28 switches, derived)** with evidence at that PCS component. Do not create 28 switches with invented field tags.

Counterexample: EBA-8 PCS `ent_c761098e6a6044ec8b00` has `quantity=31` with **no unit**, assertion `fact_e415157635884efb8e00`, GA8 p5 evidence `ev_9641a8450bdd4e43aaff`, region `[0.777,0.758,0.96,0.794]`. Its qualification says both sides/30m spacing but count basis unresolved (`fact_75055f2203154fda954a`). Display the 31 with its qualification; neither31individual switches nor62 switches is established.

These are comparison examples already in the model, **not operations to replay**.

## Worked example 2: ownership, location and drive direction

`EAC-1A Drive assembly` = `ent_1743efce9abf4cfcb848`. Its accepted `located_at UEF-1` assertion is `fact_babaea6842544755b4f5`, GA1AB p3, evidence `ev_7ae50cb37456470f90d5`, region `[0.63,0.05,0.9,0.387]`. Retain its conveyor ownership and show it in UEF-1 via location.

`EAC-1A Scoop coupling PST-530` = `ent_77b2c39d90cb49af910a`; its accepted gearbox-side mechanical edge `fact_ad83c9e2502b4fecafc7` uses coupling GA PDF page 2, document `doc_7aa49cc0d1c34af7ac06`, evidence `ev_6ec2fe046a34404f8bc5`, region `[0.497,0.493,0.649,0.742]`. The oil-pump motor → oil-pump edge `fact_ad1b19b6f2114f679692` uses the same evidence with a different region `[0.656,0.229,0.81,0.301]`.

Pattern: `context.kind=connection`, `network=mechanical`, `verification=documented`, supplying/driving subject→receiving/driven object. Oil pipes instead use `network=utility`; an instrument condition uses control semantics. Assembly membership is not a substitute for either connection. A diagram line/crossing without source direction does not become a documented edge.

## Worked example 3: shared service versus local branch

Coal Yard 1 owns its local SPDS/sector/application assemblies. It does not own a second copy of the common SPDS pump or runoff pond. Its runoff pair is SP-8G/H, established by the actual P&ID branch, even though8A/B might look like an intuitive first-yard numbering.

For Yard 2 repeat the **method**: trace its branch → identify local pump/pit/valves and common header → establish exact ownership/location → connect to the existing common source. Do not repeat the Yard 1 facts. If AP and SV numbers do not establish correspondence, preserve both lists and mark mapping unresolved.

## Worked example 4: contradiction and qualified applicability

EBA-8 scoop has PST-530 in one design source and 500PST in another. Both remain inspectable at that coupling with source basis. An agent must not choose the most familiar value, or apply all 530auxiliary ratings to an unconfirmed500model.

Similarly, the silo-extractor write-up describes2×55 kW motors per machine and a common VFD output; the GA needs to prove which numbered extractor it describes. Keep an explicit design-applicability link until identity/installation scope is established. RE-1 and EBE-CES-1 are an identity question, not an automatic alias rule.

## Repository API details that matter

- `chp.reviewed_ingestion.stage(store, document_id, result, visual_ids=..., expected_version=...)` stages an externally reviewed result. The current envelope is `summary`, `operations`, `intake_assessment`.
- `chp.patches.validate(store, body, document_id, base_version, visual_ids=...)` checks a proposal. Each source support must belong to **that document**. Do not put cross-document supports into one proposal; accept per-source claims and connect their shared identities.
- Current proposal limits:500operations/500KB,1–30supports per operation. Split at meaningful source/assembly boundaries; sequentially resolve temporary entity IDs.
- Exact quotes must match immutable evidence text. Visual regions must use evidence IDs with rendered images passed in `visual_ids`. Never claim to have reviewed an image merely to satisfy validation.
- `stage` currently passes **all evidence IDs of the selected document** to intake validation, which requires exact inventory coverage. Maintain a document-wide block disposition inventory and clearly identify the small set of pages/regions semantically examined. Do not label unexamined material deeply reviewed. If genuinely unreviewed blocks prevent honest coverage, inspect them or use a supported scoped-intake change; do not bypass validation or quietly misstate coverage.
- `chp.patches.commit(store, proposal_id)` performs guarded versioned acceptance after staging. It does not take an `expected_version` argument; the proposal's base version is validated transactionally. Read the current contract before calling it.
- Preserve context qualifiers and existing facts. A `qualify` operation replaces complete context, so include still-valid fields. Corrections/retirements/merges need source-backed reasons and their impact reviewed.
- Do not edit canonical SQL tables, re-run guarded pilot migration builders, or hardcode extracted facts into a scene. Use `tools/audit_yard1_pilot.py` as a semantic-audit pattern, not universal expected counts.

## Gates that must pass for each batch

| Gate | Passing evidence | Typical failure |
|---|---|---|
| G1 Identity/scope | Canonical-ID and alias reuse; source applicability; named placeholders/foreign references dispositioned | New copy of an existing FAS or unloader; generic motor installed everywhere |
| G2 Assembly/place | Component closure coherent; no unintended containment cycles; place visibility with correct owner; shared services not cloned | TP owns entire conveyor to make drive visible |
| G3 Interfaces | Correct direction/endpoints, A/B lane, bypass/selection condition; both sides of package boundary reviewed | A→Silo1 assumption; same-belt through-flow shown as recycle |
| G4 Engineering semantics | Quantities/units/scopes/arithmetic checked; rated/design/calculated/observed separate; cause/action/mode complete or explicit gap | Pairs as devices; structural wind speed used as trip setting |
| G5 Provenance | Every added claim/relationship has readable exact support and applicability; original opens on intended page | One bibliography/whole drawing cited for an unreadable count |
| G6 Preservation | Baseline facts/evidence remain unless intentional reviewed corrections; no unrelated UI/data regression | Silent disappearance or global mass relabelling |
| G7 Visual usability | Actual browser journey through each target and one deep part/count/connection; click/source/return works; labels readable | Table-only or independent facts disconnected from the illustration |
| G8 Honest closure | Every coverage cell resolved or a specific evidence gap; current and next batch states recorded | Declaring complete because the scene renders or tests pass |

Data checks must independently examine outputs, not simply assert the builder's own intended counts. For example, trace TP piping against the actual P&ID, compare PCS source units, assert exact silo crossover, and ensure shared pumps have one canonical identity. Treat existing source disagreements as expected qualified states, not failing tests to be “fixed” by suppressing evidence.

For changed application behaviour run the relevant Node/Python suites. For canonical updates run model integrity and scoped semantic audits. Use `.venv/Scripts/python.exe` if available; otherwise verify the installed `python` and dependencies (the virtual environment was absent on 1 October 2026). Adapt these commands to that interpreter:

```powershell
python -m chp.verify --data data/plant
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs tests/test_plant_scene_render.cjs
```

Use the actual preview port; it was8775 during the recent pilot, but is not a permanent contract. Do not open a new server over an unknown existing process or force-kill a port owner. Source browsing, pan/zoom/selection/return and reduced-motion/animation behaviour require actual browser inspection when UI changes.

## Checkpoint format

Each finished or interrupted batch leaves `checkpoint.md` containing batchID, status, baseline/current versions, accepted proposal/version IDs, exact changed/reused entities, source pages actually examined, remaining candidate dispositions, all open disagreements, validation results and **the next concrete action**. Save structured progress alongside it:

```json
{
  "batch_id": "B04",
  "status": "in_progress",
  "baseline_version": null,
  "current_version": null,
  "accepted_proposals": [],
  "target_status": {},
  "source_dispositions_file": "source-dispositions.json",
  "boundary_ledger_file": "boundaries.json",
  "claim_ledger_file": "claims.json",
  "open_findings": [],
  "verification": [],
  "next_action": "Fill with the precise remaining source/page/component action."
}
```

This is a schema example, not a claim that B04 has started. Use statuses `not_started`, `in_progress`, `review_required`, `complete`, `complete_with_gaps`, `deferred`. `complete_with_gaps` requires specific unresolved evidence and must not hide an incorrect identity, orphaned new component, broken source link or known misrepresented safety action. A section with such defects remains `review_required`.
