# EBA-6A

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B14**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_968579cda95c43f49626`.
- Existing containment closure: 1 record(s) including root; 57 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBA-6A
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: CV-1

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_c91eac5d4c104264801f` — GA & LOAD DATA OF BELT CONVEYOR-6 A&B.pdf; available PDF pp. 1–8. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 27–28, 39–40, 45–46, 48, 55.
- `doc_c91eac5d4c104264801f` — GA & LOAD DATA OF BELT CONVEYOR-6 A&B.pdf, PDF pp. 4, 6–7.

Existing explicitly applicable reference identities: EBA-6A/6B Power and Belt-Tension Calculation (Rev 03) (`ent_2d8a8e151689435086ad`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-7 | EBA-6A | No condition recorded; review source | `fact_0b243c312015488f97af` |
| EBA-6A | Coal Blending Silo House | No condition recorded; review source | `fact_9151c5c4a1b84210b35a` |
| FG-5 | EBA-6A | Gate FWD | `fact_f4038677d7a54ce090c0` |
| FG-6 | EBA-6A | Gate FWD | `fact_c56b48d83d4f49a391aa` |
| EBA-6A | EBB-2 | Corresponding silo not at high level | `fact_fe225482053943a58073` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
