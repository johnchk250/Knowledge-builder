# EAT-4

Planning card at model v628. Package **P12** — EBA-18, UEF-13 and sampling. Primary implementation batch **B36**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p12) and [family contract](../ASSEMBLY_CONTRACTS.md#measurement) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_40d3cea32dba4fef8428`.
- Existing containment closure: 15 record(s) including root; 19 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAT-4
- Existing parents: Maitree Coal Handling Plant, EBA-18B
- Direct components: EAT-4 Four-idler weighbridge, EAT-4 Load-cell summing junction box, EAT-4 Micro-Tech9101 integrator, EAT-4 Speed sensor60-12C, EAT-4 Local rate meter and totalizer, EAT-4 Calibration test-weight arrangement
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 7, 18, 39, 55.
- `doc_a9043e95d82c40f399ec` — GA & MECH LOAD OF TP-13.pdf, PDF pp. 2.
- `doc_558ade05e4644a008b81` — GA OF BELT WEIGHER - Part 1.pdf, PDF pp. 1–7.
- `doc_3898269d389646c1829c` — GA OF BELT WEIGHER - Part 2.pdf, PDF pp. 100–101.

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

- `fact_fa32901fd4354258a913` (EAT-4): Drawing group totals of8 units cover several conveyor pairs, not8 per18 conveyor. Installed calibration results, load-cell serials and weighed-idler alignment require records.
