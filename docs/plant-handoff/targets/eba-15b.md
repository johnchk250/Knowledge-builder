# EBA-15B

Planning card at model v628. Package **P09** — Reclaim transfer: UEF-8/9/10/11/12 and EBA-15/16. Primary implementation batch **B28**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p09) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_3bfea8d78c08424894bf`.
- Existing containment closure: 1 record(s) including root; 44 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-15B, Belt Conveyor-15B
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: AT-4

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_98d5b2ca45584e948725` — GA & LOAD DATA OF BELT CONVEYOR-15 A&B.pdf; available PDF pp. 1–6. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 27–28, 39–40, 45–46, 48, 55.
- `doc_98d5b2ca45584e948725` — GA & LOAD DATA OF BELT CONVEYOR-15 A&B.pdf, PDF pp. 3.

Existing explicitly applicable reference identities: 14DR1(SS) (`ent_58b2a093400a4a3a9310`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14ND3 (`ent_9f27545b4c3944169e98`), EBA-15A/15B Power and Belt-Tension Calculation (Rev 03) (`ent_cf4450146b4743f3a995`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), 14ND2 (`ent_f5ea7fc0dc3044f286f8`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| FG-7 | EBA-15B | Gate FWD | `fact_4e1eba6022cd48bb880d` |
| FG-8 | EBA-15B | Gate FWD | `fact_b924c19742294637895f` |
| FG-9 | EBA-15B | Gate FWD | `fact_d26ecd87954d41db8328` |
| FG-10 | EBA-15B | Gate FWD | `fact_27e84d8a0be249b6be4f` |
| EBA-15B | FG-12 | No condition recorded; review source | `fact_0aeab63d42c44c2b9726` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
