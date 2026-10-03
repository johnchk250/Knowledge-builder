# UEF-12

Planning card at model v628. Package **P09** — Reclaim transfer: UEF-8/9/10/11/12 and EBA-15/16. Primary implementation batch **B28**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p09) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_1e2add4bc52c4a5fb2f2`.
- Existing containment closure: 1 record(s) including root; 11 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-12
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: FG-11, FG-12, DFDSS-2 PS-04

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_90dd538dc5104f57884f` — GA & MECH LOAD OF TP-12.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.
- `doc_7a21556f8f304d4097ff` — Piping Layout for DFDS, SW & PW System at UEF-12.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_90dd538dc5104f57884f` — GA & MECH LOAD OF TP-12.pdf, PDF pp. 2.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 31.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-15A | FG-11 | No condition recorded; review source | `fact_3025179fcab94539a3e3` |
| FG-11 | EBA-16A | Gate REV | `fact_5ea157eeea154dc7af3c` |
| FG-11 | EBA-16B | Gate FWD | `fact_0d9e01d878734b5898d3` |
| EBA-15B | FG-12 | No condition recorded; review source | `fact_0aeab63d42c44c2b9726` |
| FG-12 | EBA-16A | Gate REV | `fact_07efdd06dd2c475a976b` |
| FG-12 | EBA-16B | Gate FWD | `fact_a14a743e1d4940e28925` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
