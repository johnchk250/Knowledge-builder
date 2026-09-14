# CHP Operations Helper v0.5

A local, single-user operations workspace built from reviewed plant evidence. Find the applicable drawing, inspect equipment and documented connections, record shift observations and breakdowns, and retain actions and outcomes for later use.

## Start

On Windows, run `start.bat` from this folder. If dependencies are missing, run `setup.bat` first. The app opens at http://127.0.0.1:8765. Python command alternative:

```powershell
.\.venv\Scripts\python.exe -m chp.server --data data --port 8765
```

Close an older application instance before restarting. The upgrade adds schema 4 and a new ingestion charter, preserves accepted evidence and identities, and creates a pre-upgrade database snapshot. Older code must use its pre-upgrade database in a separate data root.

## Daily workflow

- **Operations desk:** open issues, recent operating history, and shortcuts to the three main questions.
- **Equipment & evidence:** specifications, aliases, source citations and operating timeline. Document entities are excluded by default; select Include document records to inspect them.
- **Find source evidence:** literal text search across source text, names, revisions, locators and reviewed source-index notes. Open exact evidence or its reviewed drawing region. Search is not a general natural-language answer generator.
- **Connections:** trace a selected material, mechanical, electrical, control or utility network upstream/downstream. Only explicit documented links are followed; conditional links require the exact selected condition. Unverified boundaries and incomplete coverage stay visible.
- **Operating history:** add observations, structured readings, breakdowns, inspections, repairs, actions, outcomes and tentative lessons. Link a follow-up to an earlier event to record closure. Event time and entry time are separate. The original operator note is preserved.
- **Corrections:** qualify fact context, retract aliases, invalidate false identities and stage advanced reviewed batches. Review shows affected facts and context changes before acceptance. History remains accessible.
- **Existing-data review:** generate/download the actual context, connection, unit and empty-identity review queues.

Ordinary operator entries record what was submitted, not independently verified engineering truth. New lessons remain hypotheses until separately reviewed. Equipment specification and identity changes go through proposal review. No controls or report-generation buttons operate the plant.

## Future document ingestion

Read [OPERATIONS_INGESTION_WORKFLOW.md](OPERATIONS_INGESTION_WORKFLOW.md). This is the authoritative workflow for app analysis and external reviewers.

For maximum-accuracy review of important or visually dense sources, [TRIPLE_MODEL_INGESTION_WORKFLOW.md](TRIPLE_MODEL_INGESTION_WORKFLOW.md) defines a state-independent precomputed challenger path. Build one prompt package from the original source folder, have Gemini and Muse review the same sources independently ahead of time, validate their hash-bound outputs, then let the current model independently read the source and reconcile all three interpretations against the live plant state. Challengers never write canonical database operations.

Route each source to reference, register, network, operations or mixed intake. Preserve source evidence everywhere and structure only operationally useful knowledge. Every new assertion has a kind and supported conditions/time/basis; every intake states its purpose, supported questions and gaps. Reference intake may add cited search-index notes without equipment facts. CSV/XLSX records and supported PDF tables are parsed as table candidates for review. Never infer a dimension from an unclear drawing.

The app and `triple_model_session/current_codex_commit.py` use the same validator and intake assessment. The external CLI defaults to staging; `--commit` accepts an explicitly reviewed package. Old pending proposals must be rejected and re-analyzed under the new policy. Existing accepted versions remain intact.

3D reconstruction is paused: no 3D navigation, analysis prompts, mandatory dossiers or active modeling endpoints. Historical assets/revisions remain included in backups. Old workflow documents now point to the new intake guide; their prior contents are in `docs/archive-pre-operations/`.

## Existing data

Read [EXISTING_DATA_MIGRATION.md](EXISTING_DATA_MIGRATION.md). There is no need to re-upload the corpus or manually backfill operational context: the deterministic legacy migration is complete through model version 309. All 1,599 active legacy assertions now have operational context, the initial network-review queue is resolved, and supported legacy units are normalized without rewriting their original values/evidence.

Residual review is intentionally selective: inspect the 30 identities without active facts, confirm the semantics of 49 dimensionless numeric properties, establish plant applicability and installed-asset identity where sources are ambiguous, and re-analyze only concrete source gaps. Future document ingestion already requires operational context and directed-network semantics, so new accepted assertions do not need this legacy backfill.

## Storage and backup

`data/plant/plant.sqlite3` stores plant knowledge and operating records; originals and rendered pages are kept beside it. Full backup remains under Version history. Export includes operational events/readings, fact context, correction records, source index notes, the review/audit history and retained historical spatial records. Use a full backup to restore files as well as the database. Do not edit SQLite tables or original files manually.

AI analysis uses the configured API or authenticated CLI backend and sends selected source text/images plus relevant knowledge, reviewed notes and a bounded selection of related operational history. It does not retrain the model. Local source search, manual entries, corrections and network tracing do not call an AI provider.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check dist/app.js
node --check dist/operations-ui.js
.\.venv\Scripts\python.exe -m chp.verify --data data/plant
```

Retired 3D feature tests are preserved under `tests/archived_3d/`; the active tests verify disabled endpoints and retained backup assets.

## Practical limits

This version supports manual local daily use. It has no multi-user accounts, historian/DCS stream, CMMS synchronization, automatic KKS mapping, predicted failure probabilities, or approved isolation-boundary reasoning. Search uses literal matching and reviewed index notes; dense scans may need manual indexing/crops. Network tracing is a documented possible route, not live state or proof of complete coverage. Installed-unit replacement and functional-location history still require explicit source-backed identities/relationships and review. Events/readings are suitable for manual records and modest imports, not high-frequency telemetry.

[ARCHITECTURE.md](ARCHITECTURE.md) describes the current data and validation boundaries.
