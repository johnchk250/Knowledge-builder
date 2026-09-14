# Existing committed data: completed migration and residual review

The pre-migration inventory was checked against plant version **302** on 2026-09-14. The schema/charter rebuild first preserved that corpus unchanged. The subsequent deterministic context migration is now complete at plant version **309**: it appended reviewed operational context for all 1,599 active legacy assertions without rewriting their original values, units, evidence, identities or source rows.

## What is preserved

The historical baseline contained **170 source documents, 3,253 evidence blocks, 509 identities, 1,599 unretired assertions and 302 committed versions**. A row-for-row preservation comparison confirmed that documents, evidence, entities, aliases, ontology, assertions, retirements and merges were unchanged by the schema migration, and the original/render hashes, SQLite references and version hash chain passed verification.

After the append-only context qualification, the current checkpoint is **177 source documents, 3,260 evidence blocks and 309 committed versions**. The seven additional documents/evidence blocks are migration audit/proposal provenance; the original 1,599 legacy assertions remain in place and now have appended contexts. The completed qualification is: **1,120 classification**, **477 specification** and **2 documented material connection** contexts.

- Consistent pre-change database and code backup: `output/operations-rebuild-backup-20260914/`.
- Automatic pre-schema-upgrade database backup: `data/plant/plant-before-operations-v4.sqlite3`.
- Pre-context-migration database backup: `output/plant-before-context-migration-20260914.sqlite3`.
- Context-migration audit result: `output/operations-context-migration-result.json`.
- Detailed review list with assertion IDs, equipment and source references: `output/operations-existing-data-review.json`.
- Preservation comparison: `output/operations-migration-preservation.json`.
- The original 3D assets, dossiers and revisions remain in storage and full backups. The active app no longer offers or ingests them.

You do **not** need to re-upload, re-extract or manually qualify the accepted legacy corpus. Old extraction mistakes should still be corrected through the app, never by direct SQL cleanup.

## Review priorities

| Area | Actual inventory | What to do |
|---|---:|---|
| Document identities mixed with equipment | 172 records classified as document/report/drawing types | Already hidden from equipment selectors by their existing classifications. They remain accessible through “Include document records” and history. Preserve source-reference relationships; do not turn them into flow links. Review any misclassification separately. |
| Operational fact context | 1,599 legacy assertions qualified | Complete. Contexts were appended through reviewed proposals: 1,120 `classification`, 477 `specification`, 2 `connection`. `missing_context=0` at v309. |
| Existing candidate flow relationships | 4 reviewed | Complete for the initial EAC/jetty/UEF group. `EAC-1A/EAC-1B discharges_to UEF-1` are documented material connections. The inverse `conveys_from Coal Jetty` claims remain descriptive classification facts and are intentionally excluded from topology. `network_review=0`. |
| Units requiring interpretation | 8 pump-head values use `mwc` | The bounded normalizer now recognizes `mwc` as hydraulic head (`mH2O`) while preserving the original unit. It deliberately does not convert this to generic pressure; reference/basis remains unknown unless supported. |
| Counts and ratios | 49 numeric values without units: 37 quantities, 11 gear ratios, 1 elbow-radius ratio | Usually dimensionless. Confirm meaning; do not invent physical units just to fill a field. |
| Entities without unretired facts | 30 | Inspect the source and correction history. Some are old grouped or document-like identities. Invalidate only if proven false or superseded; an empty record is not automatically wrong. |
| Dedicated operating history | 0 events at the migration checkpoint | Start the shift log now. Selectively convert dated historical breakdown/inspection records when equipment, event time, and outcome are supported. Do not invent timestamps for undated notes. |

The bounded unit normalizer already handles existing volume-flow spellings (`m3/h`, `m3/hr`, `CMH`) and durations (`s`, `h`), as well as common power, length, mass-flow and other supported quantities. Original numeric values and units are not rewritten.

At the completed migration checkpoint, `missing_context=0`, `network_review=0` and `unsupported_units=0`. No conflicts are currently reported by the deterministic checker. That is **not** evidence that the corpus is semantically correct or complete; it only describes comparable single-valued claims under the current rules.

Also review **plant applicability and installed-asset identity**. For example, the current corpus includes records named “Rihand STPP stage-2 Crusher House” alongside the main plant equipment, and several generic equipment-family or standard-drawing records. These may be valid reference material rather than installed assets in your plant. Keep their sources, but establish their scope before using them in local operating answers or networks. The automatic document filter uses existing classifications only; unclassified document-like records still need review.

## Initial network qualification result

The initial migration reviewed these existing facts:

- `EAC-1A discharges_to UEF-1`
- `EAC-1B discharges_to UEF-1`
- `EAC-1A conveys_from Coal Jetty`
- `EAC-1B conveys_from Coal Jetty`

The first pair is now qualified as documented downstream material connections. A downstream trace from EAC-1A reaches UEF-1 through `discharges_to`.

The second pair expresses the inverse direction: the conveyor is the subject of `conveys_from`. Operational traversal requires **upstream/supplying subject → downstream/receiving object**, so those assertions were deliberately retained as descriptive classification facts rather than mislabeled as network edges. Add a Coal Jetty → EAC connection only if a source explicitly supports that directed topology; do not derive it merely by reversing the predicate.

Most other entity-valued links are `depicted_in` (205), `references_drawing` (4), `report_about` (3), location or hierarchy. They are useful references, not material/electrical/control topology. Electrical supply, drive trains, protection logic and utility networks still need focused source review before those queries can return useful paths.

## Automated migration command

### Automated qualification

The current workspace is already migrated. The command remains available as idempotent/reusable guidance for an equivalent unmigrated copy. Run a dry plan first:

`python -m chp.existing_migration --root data/plant`

To apply it, provide a new backup path. The command creates append-only reviewed proposals and commits context revisions in bounded batches; it never updates assertion values, units, evidence, identities or source files:

`python -m chp.existing_migration --root data/plant --apply --backup output/plant-before-context-migration-20260914.sqlite3 --report output/operations-context-migration-result.json`

The deterministic rules are deliberately narrow: document/reference/descriptive metadata becomes `classification`; equipment values become `specification` without guessed basis/condition/dates; explicit `discharges_to` facts become documented material connections; `conveys_from` remains descriptive because its subject/object semantics are inverse to the operational graph and is never silently reversed. The command stops rather than committing if it encounters another entity relation whose direction cannot be classified safely.

New document ingestion does not need this backfill: the operations intake policy rejects new assertions without `context.kind`, and network assertions must use supported directed-network context.

## Post-migration review sequence

1. Inspect the **30 empty identity** candidates. Use invalidation/restoration and merge reversal only when the source/history proves a correction is required.
2. Review the **49 dimensionless numeric properties** (37 quantities, 11 gear ratios, 1 elbow-radius ratio) for semantic meaning; do not invent units.
3. Verify equipment labels, aliases, functional locations/KKS, plant applicability and installed-asset identity where source scope is ambiguous. Keep physical replacement identity separate from location.
4. Expand material/electrical/mechanical/control/utility networks only from explicit source-backed directed relationships. Unknown branches and ports remain explicit gaps.
5. Start dated shift entries, structured readings, breakdowns, actions and linked follow-ups. Promote a supported lesson only after reviewing evidence and outcome.
6. Re-analyze only selected source gaps or ambiguous claims that answer a concrete operational question. Existing raw sources remain searchable and reusable.

Old **pending** proposals cannot be accepted under the new policy. Reject and re-analyze them with the new charter and intake assessment. All already accepted versions remain readable.

## Upgrade and rollback

Launch with `start.bat` as usual after closing any older app process. Schema version is now 4; old v0.4 code deliberately refuses schema 4. Use the pre-upgrade database with the backed-up old code in a **separate** data root to roll back. Do not overwrite the new working database if new operational entries have been added.

The prototype remains local and single-user. Team accounts/roles, a CMMS bridge, automated historian/DCS feeds, broad semantic question answering and isolation authorization are not implemented. The new model and workflows support manual daily use and source-backed development of the networks first.
