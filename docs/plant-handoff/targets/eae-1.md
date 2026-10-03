# EAE-1

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B16**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#area) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_52adacf790fd4c449346`.
- Existing containment closure: 1 record(s) including root; 21 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAE-1
- Existing parents: Maitree Coal Handling Plant, Coal Stockpile Yard, Coal Yard 1
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **transfer** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_9c169bf7536b4ebca236` — COAL FLOW DIAGRAM.pdf, PDF pp. 1.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55–56.
- `doc_777d1a06d4fa4e8ba231` — DESIGN BASIS REPORT FOR PLAIN WATER DS SYSTEM FOR STOCKPILE FOR CHP.pdf, PDF pp. 3.
- `doc_3e81ea1c32df4215968d` — GA & TDS of Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 3.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAD-1 | EAE-1 | Uncrushed coal stacking on one side of machine | `fact_2bffa6cbdf2349f09c80` |
| EAE-1 | EAF-1 | Selected pile reclaiming | `fact_4878544d9bc54b96a73f` |
| EAD-1 | EAE-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_239c3944a41f4c95b147` |
| EAE-1 | EAF-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_5ee5189b6c77464e8d3e` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
