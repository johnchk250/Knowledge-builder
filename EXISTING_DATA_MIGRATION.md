# Existing committed data: completed migration and residual review

The pre-migration inventory was checked against plant version **302** on 2026-09-14. The schema/charter rebuild first preserved that corpus unchanged. The subsequent deterministic context migration is now complete at plant version **309**: it appended reviewed operational context for all 1,599 active legacy assertions without rewriting their original values, units, evidence, identities or source rows.

## Current live checkpoint

The migration figures below remain the audit trail for versions 302–309. They no longer describe the size of the live plant model. The verified snapshot on **2026-09-18 at model version 466** is:

| Measure | Current value |
|---|---:|
| Source documents | 266 |
| Evidence blocks | 5,196 |
| Raw entity rows | 1,089 |
| Canonical identities | 1,071 |
| Canonical equipment / document / unclassified | 845 / 171 / 55 |
| Active assertions | 7,655 |
| Active assertions without context | 0 |
| Active `part_of` relationships | 516 |
| Documented network connections | 517 |
| Network split | 212 material / 164 utility / 139 control / 2 mechanical / 0 electrical |
| Canonical identities with no active fact/relation | 29 |
| Formal deterministic conflicts | 0 |
| Pending proposals | 0 |

Read-only integrity verification passes all **266 documents, 5,196 evidence blocks and 466 version records** with no reported errors. The zero formal-conflict count does not mean the engineering corpus has no contradictory source material: unresolved source discrepancies remain explicitly preserved where the evidence does not support a single reconciled assertion.

## What is preserved

The historical baseline contained **170 source documents, 3,253 evidence blocks, 509 identities, 1,599 unretired assertions and 302 committed versions**. A row-for-row preservation comparison confirmed that documents, evidence, entities, aliases, ontology, assertions, retirements and merges were unchanged by the schema migration, and the original/render hashes, SQLite references and version hash chain passed verification.

After the append-only context qualification, the **migration checkpoint** was **177 source documents, 3,260 evidence blocks and 309 committed versions**. The seven additional documents/evidence blocks were migration audit/proposal provenance; the original 1,599 legacy assertions remained in place and received appended contexts. The completed qualification was: **1,120 classification**, **477 specification** and **2 documented material connection** contexts.

- Consistent pre-change database and code backup: `output/operations-rebuild-backup-20260914/`.
- Automatic pre-schema-upgrade database backup: `data/plant/plant-before-operations-v4.sqlite3`.
- Pre-context-migration database backup: `output/plant-before-context-migration-20260914.sqlite3`.
- Context-migration audit result: `output/operations-context-migration-result.json`.
- Detailed review list with assertion IDs, equipment and source references: `output/operations-existing-data-review.json`.
- Preservation comparison: `output/operations-migration-preservation.json`.
- The original 3D assets, dossiers and revisions remain in storage and full backups. The active app no longer offers or ingests them.

You do **not** need to re-upload, re-extract or manually qualify the accepted legacy corpus. Old extraction mistakes should still be corrected through the app, never by direct SQL cleanup.

## Historical v309 migration review inventory

| Area | v309 migration inventory | What to do |
|---|---:|---|
| Document identities mixed with equipment | 172 records classified as document/report/drawing types | Already hidden from equipment selectors by their existing classifications. They remain accessible through “Include document records” and history. Preserve source-reference relationships; do not turn them into flow links. Review any misclassification separately. |
| Operational fact context | 1,599 legacy assertions qualified | Complete. Contexts were appended through reviewed proposals: 1,120 `classification`, 477 `specification`, 2 `connection`. `missing_context=0` at v309. |
| Existing candidate flow relationships | 4 reviewed | Complete for the initial EAC/jetty/UEF group. `EAC-1A/EAC-1B discharges_to UEF-1` are documented material connections. The inverse `conveys_from Coal Jetty` claims remain descriptive classification facts and are intentionally excluded from topology. `network_review=0`. |
| Units requiring interpretation | 8 pump-head values use `mwc` | The bounded normalizer now recognizes `mwc` as hydraulic head (`mH2O`) while preserving the original unit. It deliberately does not convert this to generic pressure; reference/basis remains unknown unless supported. |
| Counts and ratios | 49 numeric values without units: 37 quantities, 11 gear ratios, 1 elbow-radius ratio | Usually dimensionless. Confirm meaning; do not invent physical units just to fill a field. |
| Entities without unretired facts | 30 | Inspect the source and correction history. Some are old grouped or document-like identities. Invalidate only if proven false or superseded; an empty record is not automatically wrong. |
| Dedicated operating history | 0 events at the migration checkpoint | Start the shift log now. Selectively convert dated historical breakdown/inspection records when equipment, event time, and outcome are supported. Do not invent timestamps for undated notes. |

The bounded unit normalizer already handles existing volume-flow spellings (`m3/h`, `m3/hr`, `CMH`) and durations (`s`, `h`), as well as common power, length, mass-flow and other supported quantities. Original numeric values and units are not rewritten.

At the completed migration checkpoint, `missing_context=0`, `network_review=0` and `unsupported_units=0`. No formal conflicts were reported by the deterministic checker at that checkpoint. The live v466 snapshot likewise has no active assertion missing context and reports zero formal conflicts, but that is **not** evidence that the corpus is semantically correct or complete; it only describes comparable single-valued claims under the current rules.

Also review **plant applicability and installed-asset identity**. For example, the current corpus includes records named “Rihand STPP stage-2 Crusher House” alongside the main plant equipment, and several generic equipment-family or standard-drawing records. These may be valid reference material rather than installed assets in your plant. Keep their sources, but establish their scope before using them in local operating answers or networks. The automatic document filter uses existing classifications only; unclassified document-like records still need review.

## Initial network qualification result

The initial migration reviewed these existing facts:

- `EAC-1A discharges_to UEF-1`
- `EAC-1B discharges_to UEF-1`
- `EAC-1A conveys_from Coal Jetty`
- `EAC-1B conveys_from Coal Jetty`

The first pair is now qualified as documented downstream material connections. A downstream trace from EAC-1A reaches UEF-1 through `discharges_to`.

The second pair expresses the inverse direction: the conveyor is the subject of `conveys_from`. Operational traversal requires **upstream/supplying subject → downstream/receiving object**, so those assertions were deliberately retained as descriptive classification facts rather than mislabeled as network edges. Add a Coal Jetty → EAC connection only if a source explicitly supports that directed topology; do not derive it merely by reversing the predicate.

At v309, most other entity-valued links were document references, location or hierarchy rather than operational topology. The live v466 model has since expanded to **517 documented network edges**, with substantial material, utility and control coverage. Mechanical topology remains very sparse at **2 documented edges**, and the electrical network currently has **0 documented edges** even though electrical feeder/supply specifications exist elsewhere in the model. Continue treating document-reference, location and hierarchy relations as non-network relationships.

## Automated migration command

### Automated qualification

The current workspace is already migrated. The command remains available as idempotent/reusable guidance for an equivalent unmigrated copy. Run a dry plan first:

`python -m chp.existing_migration --root data/plant`

To apply it, provide a new backup path. The command creates append-only reviewed proposals and commits context revisions in bounded batches; it never updates assertion values, units, evidence, identities or source files:

`python -m chp.existing_migration --root data/plant --apply --backup output/plant-before-context-migration-20260914.sqlite3 --report output/operations-context-migration-result.json`

The deterministic rules are deliberately narrow: document/reference/descriptive metadata becomes `classification`; equipment values become `specification` without guessed basis/condition/dates; explicit `discharges_to` facts become documented material connections; `conveys_from` remains descriptive because its subject/object semantics are inverse to the operational graph and is never silently reversed. The command stops rather than committing if it encounters another entity relation whose direction cannot be classified safely.

New document ingestion does not need this backfill: the operations intake policy rejects new assertions without `context.kind`, and network assertions must use supported directed-network context.

## Current review sequence

1. Resolve the **55 unclassified canonical identities** where the source evidence supports a classification; do not classify from naming convention alone.
2. Inspect the **29 canonical identities with no active fact or relationship**. Use invalidation/restoration and merge reversal only when source/history proves a correction is required.
3. Verify equipment labels, aliases, functional locations/KKS, plant applicability and installed-asset identity where source scope is ambiguous. Keep generic design-package identities separate from numbered installed assets unless evidence supports the merge.
4. Reconcile explicitly retained cross-source discrepancies only when stronger evidence establishes the applicable design/as-built/operating truth. Zero formal database conflicts does not close these source discrepancies.
5. Expand mechanical and electrical topology first, then other known boundaries, using explicit source-backed directed relationships. Unknown branches, ports and conditions remain explicit gaps.
6. Continue dated shift entries, structured readings, breakdowns, actions and linked follow-ups. Promote a supported lesson only after reviewing evidence and outcome.
7. Re-analyze selected source gaps or ambiguous claims that answer a concrete operational question. Existing raw sources remain searchable and reusable.

Old **pending** proposals cannot be accepted under the new policy. Reject and re-analyze them with the new charter and intake assessment. All already accepted versions remain readable.

## Upgrade and rollback

Launch with `start.bat` as usual after closing any older app process. Schema version is now 4; old v0.4 code deliberately refuses schema 4. Use the pre-upgrade database with the backed-up old code in a **separate** data root to roll back. Do not overwrite the new working database if new operational entries have been added.

The prototype remains local and single-user. Team accounts/roles, a CMMS bridge, automated historian/DCS feeds, broad semantic question answering and isolation authorization are not implemented. The new model and workflows support manual daily use and source-backed development of the networks first.
