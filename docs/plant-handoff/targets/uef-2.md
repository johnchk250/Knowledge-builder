# UEF-2

Planning card at model v628. Package **P00** — Identity, scope and topology reconciliation. Primary implementation batch **B00**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p00) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_56e7a3ed39ed44749525`.
- Existing containment closure: 1 record(s) including root; 4 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-2
- Existing parents: none
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_411067c712284bc5a957` — Piping Layout for SW & DW system at UEF-2, 16, 17 & 18.pdf; available PDF pp. 1–5. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_411067c712284bc5a957` — Piping Layout for SW & DW system at UEF-2, 16, 17 & 18.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| No documented material connection in this scope | — | Review the section interface plan; this is not proof that no route exists | — |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
