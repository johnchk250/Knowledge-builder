# EBA-12

Planning card at model v628. Package **P07** — Coal Yard 3. Primary implementation batch **B20**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p07) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_e0cd946e46264ec89bdc`.
- Existing containment closure: 1 record(s) including root; 41 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-12
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_0adf08e6189847b88503` — GA & LOAD DATA OF BELT CONVEYOR-12.pdf; available PDF pp. 1–7. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 46, 55.
- `doc_0adf08e6189847b88503` — GA & LOAD DATA OF BELT CONVEYOR-12.pdf, PDF pp. 5.

Existing explicitly applicable reference identities: CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 14DR2 (`ent_75f083d21aee4bbbbfbc`), 14ND3 (`ent_9f27545b4c3944169e98`), 14ND2 (`ent_f5ea7fc0dc3044f286f8`), EBA-8/10/12/14 Power and Belt-Tension Calculation (Rev 03) (`ent_fc7b03c245e6419cb264`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAF-3 | EBA-12 | No condition recorded; review source | `fact_e2a18dbfe3d142d1a787` |
| EBA-12 | FG-8 | No condition recorded; review source | `fact_03925388302d4073bc8b` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
