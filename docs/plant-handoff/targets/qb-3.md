# QB-3

Planning card at model v628. Package **P12** — EBA-18, UEF-13 and sampling. Primary implementation batch **B36**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p12) and [family contract](../ASSEMBLY_CONTRACTS.md#measurement) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_b86046eff65c4dafab32`.
- Existing containment closure: 7 record(s) including root; 21 assertions on root. These are model records, not a count of physical devices.
- Aliases: QB-3
- Existing parents: Maitree Coal Handling Plant, EBA-18A
- Direct components: QB-3 Tandem probe, QB-3 Electronic unit SQTA, QB-3 Sandbag marker, QB-3 Marker interlock switch, QB-3 Local start reset and indication panel, QB-3 Hooter and metal lamp
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_878e57f585f54e29b031` — 25_METAL DETECTOR.pdf, PDF pp. 16.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 17, 29, 55.
- `doc_41965812f7d842f3b1ef` — GA OF METAL DETECTOR.pdf, PDF pp. 2, 4, 8, 11–12.

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

- `fact_59fa7b62c2f043de9faa` (QB-3): Detector GA design speed 2.6 m/s differs from conveyor18 GA 2.7 m/s. Compliance review also requests small ferrous/nonferrous pieces. Field sensitivity tests/final vendor approval are required.
- `fact_c0254aaef74243a6b227` (QB-3): DCS IO table p12 maps ON T25/26, fault T22/23/24 and metal T27/28; wiring p11 labels relays differently. No definitive field terminal mapping is inferred.
- `fact_cd0c062ac77545a893a7` (QB-3): Support height is explicitly determined at site. Sensitivity, serial numbers, field cable lengths and final IP protection of hooter remain unresolved.
