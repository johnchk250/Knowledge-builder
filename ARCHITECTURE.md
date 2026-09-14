# CHP Operations Helper architecture

The authoritative local store remains SQLite. Immutable evidence, reviewed proposals and append-only version commits are retained. Schema 4 adds operational context, correction records, events/readings and source index notes. No separate graph server is required for the present single-user corpus.

## Data and projections

| Storage | Purpose | Current-view behavior |
|---|---|---|
| documents / evidence / original files | Source revision, authority, exact text and page/row/image locators | Never rewritten by interpretation changes |
| entities / aliases / ontology / assertions | Stable identities and original reviewed claims | Equipment/document category is derived from existing classifications; document records are excluded from equipment selectors |
| assertion_contexts | Versioned complete context per assertion | Latest context at requested model version; original scalar value/unit/evidence unchanged |
| identity_changes | Invalidation/restoration, alias retraction/restoration and merge/unmerge events | Invalidated identities, their aliases and affected facts disappear from active retrieval; history still resolves at its original version |
| operational_events / event_measurements | Occurred and recorded times, equipment, record kind, status, linked event, structured readings and source provenance | Equipment timeline and open-record view; linked closure updates displayed status without overwriting the original event |
| source_notes | Reviewed searchable descriptions with exact source/region evidence | Literal search includes note text and returns the cited source region |
| proposals / run_steps / versions | Proposed operations, intake assessments, exact prompts, reviews and commit hash chain | Optimistic version and charter checks; no partial knowledge commit |
| context_revisions / suggestions / decisions | Operator guidance and separately reviewed interpretation notes | Relevant reviewed notes plus bounded recent events/lessons accompany intake |
| historical spatial tables/assets | Retained v0.4 work | Backup/export only; active endpoints return 410 |

`Store.model()` uses one SQLite read snapshot for internally consistent projection. Raw assertions retain their created version. Separate retirement records mean a corrected value is retire + assert, not UPDATE. New merge operations use identity changes, enabling reversal and later re-merge without rewriting legacy merge rows. Retired primary aliases no longer act as current retrieval labels; active alternatives supply a display label when available.

## Quantities and applicability

`operating_model.quantity` uses a bounded dimensional unit map and preserves original inputs. Equivalent quantities compare with tight floating-point tolerance; unsupported units remain unresolved. Fact conflicts require matching kind, condition, basis and observation time and overlapping validity. End dates are exclusive. New ingestion never invents missing context. The accepted legacy corpus has since been qualified by the deterministic append-only migration described below; different condition strings are still not automatically reconciled semantically.

The equipment view retains reviewed, unretired claims with their context, including dated claims; it does not silently choose the current applicable specification from competing revisions. Network tracing applies requested-time validity separately. Operators must inspect applicability and evidence.

## Directed networks

Each participating assertion has `context.kind=connection`, an explicit network, verification status, optional ports, operating condition and validity interval. Subject is upstream/supplying and object is downstream/receiving. Document-reference, location and hierarchy predicates cannot be network edges. Inferred assertions cannot be marked documented.

Traversal is cycle-safe breadth-first search over documented edges in one selected network. It returns one discovery path per reachable item, all traversed edges and excluded boundaries. Conditional edges require an exact condition selection. It reports incomplete coverage on every result because endpoint degree does not establish that all connections are known. The service does not perform control simulation or isolation authorization.

## Intake and review

`usage_intake.py` is the common policy. `Service.analyze` and `reviewed_ingestion.stage` require an intake assessment, purpose, supported questions, gaps and exact evidence coverage. Every new assertion requires context.kind. Reference-only intake can create source index notes but cannot acquire equipment claims through an edit. The external CLI requires the reviewed model version and stages by default.

The parsers preserve table candidates and their header/row/region context. AI remains responsible for proposing supported interpretations; exact-quote/visual-source validation and human review remain necessary. Source text and metadata never become instructions. The app does not request geometry or reconstruction output and rejects active 3D envelopes.

`patches.validate` checks both provenance and operation semantics. It rejects alias collisions in the resulting correction projection, invalid entities, merge and hierarchy cycles, unsupported network categories, invalid times and invalid reading values. `commit` repeats validation and policy checks inside one immediate transaction, appends the version hash and updates proposal status atomically. Changes during analysis or review make the proposal stale.

Manual operating entry writes the operator's own immutable note, stages its event and commits that submitted record. Corrections preserve the reviewer note and stop at the review queue. These notes attest to what was entered; they do not independently verify engineering truth. An invalid/stale entry may leave its preserved source or pending proposal, but no partial committed plant change.

## Migration and compatibility

Opening schema 1-3 first creates a consistent SQLite pre-upgrade backup, then adds the schema-4 tables/triggers. New code appends an operations charter revision while preserving reviewed notes and old charter history. The schema upgrade itself does not rewrite existing assertions or source rows. A subsequent deterministic, append-only qualification migrated the accepted legacy corpus from model version 302 to 309 by adding complete contexts for all 1,599 active legacy assertions: 1,120 classifications, 477 specifications and 2 documented material connections. Original assertion values, units, evidence, identities and source rows remain immutable; context is appended through reviewed proposals/version commits.

At the v309 migration checkpoint, the legacy `missing_context`, network-review and unsupported-unit queues are resolved. Remaining manual review is semantic rather than structural: 49 dimensionless numeric properties, 30 identities without active facts, plant applicability/installed-asset identity, and any future evidence or applicability gaps discovered during use. The existing-data report remains the audit surface for these residual candidates. Old code refuses schema 4.

Normal exports include new tables. Full backup retains the SQLite snapshot, source files, page renders and historical 3D assets. Integrity verification checks original/render hashes, foreign keys, the database and every committed version hash. These checks detect accidental modification; they are not protection against a local administrator.

## Scope

No multi-user access system, CMMS/historian synchronization, broad semantic Q&A, calibrated fault diagnosis, automatic KKS mapping or safe-isolation proof is implemented. Manual records and source-backed topology are the current operational foundation. See OPERATIONS_INGESTION_WORKFLOW.md and EXISTING_DATA_MIGRATION.md for use and review instructions.
