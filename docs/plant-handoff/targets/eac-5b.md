# EAC-5B

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B13**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_84e3b6b3057944c68607`.
- Existing containment closure: 2 record(s) including root; 51 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-5B
- Existing parents: Maitree Coal Handling Plant
- Direct components: FTR-4
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_b74a01e57a2b4792883c` — GA & LOAD DATA OF BELT CONVEYOR-5 A&B.pdf; available PDF pp. 1–6. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 27–28, 36, 40–41, 49, 55.
- `doc_b74a01e57a2b4792883c` — GA & LOAD DATA OF BELT CONVEYOR-5 A&B.pdf, PDF pp. 3.

Existing explicitly applicable reference identities: 20DR2 (`ent_0bda87e7a4284cc78e03`), 20ND1 (`ent_48f3fa98490349ab9a70`), 20ND3 (`ent_54f0ffd4b8824691b339`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), EAC-5A/5B Power and Belt-Tension Calculation (Rev 03) (`ent_8a85bc65ae9e422a93f7`), 20ND4 (`ent_b74e472627604876a214`), 20ND5 (`ent_b94d221596d045e6818e`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-5 | EAC-5B | No condition recorded; review source | `fact_4689884333e54a9dbd80` |
| EAC-5B | UEF-7 | No condition recorded; review source | `fact_b000f95c8fc945bdab7c` |
| FG-3 | EAC-5B | Gate aligned to selected downstream conveyor | `fact_2486c7afc21343c7bf37` |
| FG-4 | EAC-5B | Gate aligned to selected downstream conveyor | `fact_91c26346827747759de9` |
| EAC-5B | FTR-4 | No condition recorded; review source | `fact_5808e7001c264b73a7c7` |
| FTR-4 | KB-FD-8 | No condition recorded; review source | `fact_8d19cb70a9034aa391d0` |
| KB-FD-8 | EAC-5B | Through-flow beyond fixed tripper; same continuous conveyor, not a recirculation loop | `fact_78025cd3d8164c9db8df` |
| EAC-5B | FG-6 | No condition recorded; review source | `fact_0f1540b83ca14272b4b4` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
