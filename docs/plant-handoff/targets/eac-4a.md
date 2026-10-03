# EAC-4A

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B12**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_0318ac225b5a4a0f9349`.
- Existing containment closure: 2 record(s) including root; 51 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-4A
- Existing parents: Maitree Coal Handling Plant
- Direct components: FTR-1
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_a02d56b879734b5db189` — GA & LOAD DATA OF BELT CONVEYOR-4 A-B.pdf; available PDF pp. 1–5. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 27–28, 36–37, 41–42, 49–50, 55.
- `doc_a02d56b879734b5db189` — GA & LOAD DATA OF BELT CONVEYOR-4 A-B.pdf, PDF pp. 4.

Existing explicitly applicable reference identities: 20ND1 (`ent_48f3fa98490349ab9a70`), 20ND3 (`ent_54f0ffd4b8824691b339`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 20ND4 (`ent_b74e472627604876a214`), 20ND5 (`ent_b94d221596d045e6818e`), 20DR4 (`ent_bbd84cdbad5e468aa7a9`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), EAC-4A/4B Power and Belt-Tension Calculation (Rev 03) (`ent_eab489cccb8f4d7a9556`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-3 | EAC-4A | No condition recorded; review source | `fact_d9c0e0a4f45d42e1a935` |
| EAC-4A | UEF-5 | No condition recorded; review source | `fact_f4e5935621504a829307` |
| FG-1 | EAC-4A | Gate aligned to selected downstream conveyor | `fact_f536214811e441a5bb5c` |
| FG-2 | EAC-4A | Gate aligned to selected downstream conveyor | `fact_fe9e31c6d462459ea839` |
| EAC-4A | FTR-1 | No condition recorded; review source | `fact_0671e39938af4129b6d6` |
| FTR-1 | KB-FD-3 | No condition recorded; review source | `fact_856f0a7fd8f346028791` |
| KB-FD-3 | EAC-4A | Through-flow beyond fixed tripper; same continuous conveyor, not a recirculation loop | `fact_bc19865626d44443a764` |
| EAC-4A | KB-FD-5 | No condition recorded; review source | `fact_744b5a434cfa464a868e` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
