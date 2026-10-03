# KB-FD-7

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B13**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_87427a115a584daab803`.
- Existing containment closure: 1 record(s) including root; 6 assertions on root. These are model records, not a count of physical devices.
- Aliases: KB-FD-7, FD-7
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_4a75d7803f1e4c7eb11a` — GA OF FLOW DIVIDER.pdf, PDF pp. 1–2.

Existing explicitly applicable reference identities: CHP Gate and Flow Divider Control Scheme (`ent_57fc8512e7f94395a9bd`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| FTR-3 | KB-FD-7 | No condition recorded; review source | `fact_a90ba3c422e748e5a2ce` |
| KB-FD-7 | EAC-5A | Through-flow beyond fixed tripper; same continuous conveyor, not a recirculation loop | `fact_8b3d2d115ff6425d96da` |
| KB-FD-7 | EAC-7 | Full or partial stacking | `fact_be9779fbfd0b4ae28170` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
