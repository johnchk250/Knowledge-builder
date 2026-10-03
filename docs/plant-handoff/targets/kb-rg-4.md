# KB-RG-4

Planning card at model v628. Package **P03** — Primary screening, EAC-3 and UEF-3. Primary implementation batch **B09**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p03) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_18b389c8af96423ea39f`.
- Existing containment closure: 1 record(s) including root; 5 assertions on root. These are model records, not a count of physical devices.
- Aliases: KB-RG-4, RG-4
- Existing parents: UEE-1, Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_d91f96a250d048aeb54f` — GA & DETAIL OF ROD GATE.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-2B | KB-RG-4 | Selected primary screening chute | `fact_3c5fdf24b3f04dfb9dec` |
| KB-RG-4 | KB-RPG-4 | No condition recorded; review source | `fact_725d775682634abb8976` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
