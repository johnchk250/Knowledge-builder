# Coal Ship Unloader-3

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B08**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#unloader) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_9b33c14cee7f4d749335`.
- Existing containment closure: 1 record(s) including root; 7 assertions on root. These are model records, not a count of physical devices.
- Aliases: Coal Ship Unloader-3
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **unloader** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 4, 56.
- `doc_cd1aae66b455491b8883` — DBR for Ship Unloader.pdf, PDF pp. 2.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| Coal Ship Unloader-3 | EAC-1A | Shuttle selected to EAC-1A | `fact_56fff835e5b245a1a4fb` |
| Coal Ship Unloader-3 | EAC-1B | Shuttle selected to EAC-1B | `fact_41f3e632ea9d4ba5a581` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_54d0aac1d9b9414bbeb2` (Coal Ship Unloader-3): B00 identity decision: retain this numbered layout identity separately from SUL-3 until a numbered layout/vendor cross-reference proves the mapping. DBR 175154 distinguishes two Type 1 units (SUL-1/2) and one Type 2 unit (SUL-3); matching suffix alone is insufficient. B07/B08 own the available Type1/Type2 GA and jetty-layout cross-check. These records are identity candidates, not evidence of six installed unloaders.
