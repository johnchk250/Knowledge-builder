# EAC-2B

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B06**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_f4dc6c5b38d14bceb5e5`.
- Existing containment closure: 2 record(s) including root; 53 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-2B
- Existing parents: Maitree Coal Handling Plant
- Direct components: EAC-2B receiving chute at UEF-1
- Located equipment: QB-2, EAT-2

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_030c8f82fb674548a4dc` — GA & LOAD DATA OF BELT CONVEYOR-2A-B.pdf; available PDF pp. 1–5. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 4, 38, 43, 51–52, 55.
- `doc_030c8f82fb674548a4dc` — GA & LOAD DATA OF BELT CONVEYOR-2A-B.pdf, PDF pp. 1–2, 4–5.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 1.
- `doc_7568f1550b254ee2a94a` — Piping Layout for DFDS, SW & PW System at UEF-1.pdf, PDF pp. 1–2.

Existing explicitly applicable reference identities: 20DR2 (`ent_0bda87e7a4284cc78e03`), 20ND1 (`ent_48f3fa98490349ab9a70`), 20ND3 (`ent_54f0ffd4b8824691b339`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), EAC-2A/2B Power and Belt-Tension Calculation (Rev 03) (`ent_f686f77a5d4b4562b542`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-1 | EAC-2B | No condition recorded; review source | `fact_fff27dc6f3654329ab2f` |
| EAC-2B | UEE-1 | No condition recorded; review source | `fact_aaaa198ecc9d4b7e825d` |
| EAC-1B | EAC-2B | Transfer at UEF-1 | `fact_55fb76ff94ec43a9a5b3` |
| EAC-2B | KB-RG-3 | Selected primary screening chute | `fact_df9b3c3981024b568b92` |
| EAC-2B | KB-RG-4 | Selected primary screening chute | `fact_3c5fdf24b3f04dfb9dec` |
| EAC-1B discharge chute at UEF-1 | EAC-2B receiving chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_8b8867b14a0e45b0bb65` |
| EAC-2B receiving chute at UEF-1 | EAC-2B | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_8b2cf9dd98514b0196cd` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
