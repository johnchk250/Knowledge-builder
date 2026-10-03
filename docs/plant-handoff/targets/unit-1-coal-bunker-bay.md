# Unit-1 Coal Bunker Bay

Planning card at model v628. Package **P14** — Unit 1/2 bunkers and bunker dust extraction. Primary implementation batch **B41**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p14) and [family contract](../ASSEMBLY_CONTRACTS.md#bunker) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_862e744e8fb24d65901c`.
- Existing containment closure: 7 record(s) including root; 5 assertions on root. These are model records, not a count of physical devices.
- Aliases: Unit-1 Coal Bunker Bay
- Existing parents: Maitree Coal Handling Plant
- Direct components: Bunker-A of Unit-1, Bunker-B of Unit-1, Bunker-C of Unit-1, Bunker-D of Unit-1, Bunker-E of Unit-1, Bunker-F of Unit-1
- Located equipment: TT-1, TT-3

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **bunker** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-19A | TT-1 | Tripper positioned for selected bunker | `fact_83879c2dc5af45988112` |
| TT-1 | FG-19 | No condition recorded; review source | `fact_0afacd69b931451d8652` |
| FG-19 | Unit-1 Coal Bunker Bay | Selected bunker feed; exact bunker depends on tripper position | `fact_3ab4bd954b6741cd83e6` |
| EBA-19B | TT-3 | Tripper positioned for selected bunker | `fact_cd0bc73782e648e1929d` |
| TT-3 | FG-21 | No condition recorded; review source | `fact_25272eba9f33475b9781` |
| FG-21 | Unit-1 Coal Bunker Bay | Selected bunker feed; exact bunker depends on tripper position | `fact_263ba637cb5d47919ca1` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
