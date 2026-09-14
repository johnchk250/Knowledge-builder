# Triple Review Operations Ingestion Workflow

This is an optional maximum-accuracy extension of [Operations-focused document intake](OPERATIONS_INGESTION_WORKFLOW.md). The operations workflow remains authoritative for what may enter the plant model. Triple review improves source interpretation; it does not replace evidence validation, operational context, human review, or current-state reconciliation.

The historical live-orchestrated triple workflow is preserved in [the archived copy](docs/archive-pre-operations/TRIPLE_MODEL_INGESTION_WORKFLOW.md). Do not use its reconstruction/3D requirements for new intake.

The existing `make_source_packets.py`, `run_document_challengers.py`, `run_independent_challengers.py` and `validate_triple_coverage.py` remain for historical runs and recovery. They are not the normal entry point for this precomputed workflow.

## Design: precompute source review, reconcile later

Separate two concerns that were previously interleaved:

1. **Source interpretation, state-independent.** Gemini and Muse independently inspect the original document sources ahead of ingestion. Their outputs are bound to source-file SHA-256 hashes and contain source-relative candidate findings, evidence locations, uncertainties and route recommendations. They do not use plant entity IDs and do not produce canonical patch operations.
2. **Plant reconciliation, state-aware.** The current model later reads the same original sources, both challenger outputs and the current plant model. It independently interprets the sources, adjudicates disagreements, resolves identities against current state, chooses the operational intake route, and authors the one canonical `summary + operations + intake_assessment` envelope.

A challenger review does **not** become stale merely because the plant model version changes. It becomes unusable when its source hash no longer matches the source supplied for adjudication, its declared coverage is incomplete, or its review package is malformed. The final canonical proposal remains version-bound and must be reviewed again if the plant model changes before staging/commit.

## Phase A — build the prompt package

Given a folder containing the original documents, create a portable prompt package:

```powershell
.\.venv\Scripts\python.exe triple_model_session/build_precomputed_challenger_package.py `
  --source-dir "D:\path\to\source-documents" `
  --output-dir "D:\path\to\challenger-prompt-package"
```

The package contains:

- `CHALLENGER_PROMPT.md` — the exact task to give independently to Gemini and Muse;
- `source_manifest.json` — relative source paths, sizes and SHA-256 hashes;
- `review_jobs.json` — one stable document key and expected output path per source file;
- `precomputed_challenger_review.schema.json` — the required output contract;
- `OUTPUT_LAYOUT.md` — folder and handoff instructions.

Do not put plant-state exports, existing entity IDs, another reviewer's conclusions, or the current model's interpretation into this package. The challengers should be blind to each other and to current plant state.

## Phase B — independent Gemini and Muse review

Give **the same prompt package and the same original source folder** separately to Gemini and Muse. Give each reviewer a separate empty output root, for example:

```text
challenger-outputs/
  gemini/
    documents/<document_key>/review.json
  muse/
    documents/<document_key>/review.json
```

Each reviewer must inspect the complete source. Dense drawings, GAs, P&IDs/PFDs, SLDs, drive arrangements, schedules, title blocks and equipment schemes require deliberate visual review at sufficient zoom. Review connections, flow/direction cues, equipment identities, annotations, conditions, qualifiers, tables and important spatial/functional relationships. Do not downgrade a dense drawing to a superficial index-only pass merely because it is visually complex.

The extraction target is **operational understanding**, not CAD reconstruction. Preserve useful equipment schemes, explicit topology, network connections, specifications, operational events, identities, source metadata and searchable regions. Do not create 3D geometry dossiers or invent dimensions/connectivity that the source does not establish.

Every candidate finding is source-relative. Examples include:

- equipment/tag/alias candidates as written;
- specification values with original units, conditions, basis and applicability;
- explicit material/mechanical/electrical/control/utility connection candidates and direction cues;
- dated observations, breakdowns, actions and outcomes;
- document identity/revision/authority observations;
- source-index notes for useful regions that do not justify a plant fact;
- ambiguities, unreadable areas, off-sheet continuations and conflicting source statements.

Reviewers must not invent or resolve canonical database entity IDs. They must not output `assert`, `entity`, `merge`, `retire` or other final patch operations.

## Phase C — validate the returned challenger folders

Before adjudication, check that both output roots correspond to the exact source manifest:

```powershell
.\.venv\Scripts\python.exe triple_model_session/validate_precomputed_challengers.py `
  --prompt-package "D:\path\to\challenger-prompt-package" `
  --source-dir "D:\path\to\source-documents" `
  --gemini-dir "D:\path\to\challenger-outputs\gemini" `
  --muse-dir "D:\path\to\challenger-outputs\muse"
```

This is a structural/provenance gate, not an engineering correctness verdict. It verifies source hashes, reviewer identity, expected output paths, declared complete coverage and the required review shape. Missing or mismatched reviews are reported and block maximum-accuracy triple adjudication.

## Phase D — current-model adjudication and operational intake

The user supplies the current model with:

1. the original document source folder;
2. the generated prompt package (or at minimum its source manifest);
3. the Gemini output folder;
4. the Muse output folder.

For every document, the current model must:

1. verify the original source hash against `source_manifest.json`;
2. independently inspect the actual source, including dense visual material at sufficient detail;
3. read both challenger reviews only after forming its own source interpretation where practical;
4. compare all three interpretations candidate-by-candidate and investigate disagreements against the original source;
5. query the **current** plant state to resolve identities, aliases, existing facts, conflicts, revisions and applicable prior events/lessons;
6. choose `reference`, `register`, `network`, `operations` or `mixed` according to `OPERATIONS_INGESTION_WORKFLOW.md`;
7. author one canonical operational intake envelope with exact registered evidence IDs/quotes/regions and explicit gaps;
8. stage through `chp.reviewed_ingestion.stage` against the current model version, then review/commit through the normal validator.

Challenger consensus is not sufficient evidence. Two models repeating the same mistake does not override the source. Conversely, a minority challenger finding should not be discarded merely because the other two missed it; check it against the source and keep it if supported.

## Final commit boundary

Only the current-model reconciliation produces canonical plant operations. Once the source is registered and the adjudicated envelope is ready, use the same current operational boundary:

```powershell
.\.venv\Scripts\python.exe triple_model_session/current_codex_commit.py `
  --data data/plant `
  --document-id doc_ACTUAL `
  --body reviewed-intake.json `
  --expected-version CURRENT_VERSION
```

The default stages for human review. `--commit` accepts an explicitly reviewed package; it is never implied by challenger consensus. If current plant state changes after reconciliation, re-run the state-aware reconciliation against the new version. The source-only Gemini/Muse reviews may be reused if their source hashes and coverage remain valid.

## What “triple review” means now

Triple review means three independent source interpretations plus one authoritative, state-aware reconciliation:

```text
original source ──► Gemini source review ─┐
                └► Muse source review ───┼─► current-model adjudication ─► operational envelope
                └► current-model read ───┘             │
                                                       └► current plant state
```

It does not mean three models independently writing database patches. This separation preserves the accuracy benefit of independent source review while moving Gemini/Muse latency out of the live ingestion session.
