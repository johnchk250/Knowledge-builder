# EAC-13

Planning card at model v628. Package **P08** — Coal Yard 4. Primary implementation batch **B23**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p08) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_6cbfa68852d842138a13`.
- Existing containment closure: 3 record(s) including root; 35 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-13, Belt Conveyor-13
- Existing parents: Maitree Coal Handling Plant
- Direct components: EAC-13 Main Drive Motor, EAC-13 Main Drive Gearbox
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_99b04888284c4cf0802b` — GA & LOAD DATA OF BELT CONVEYOR-13.pdf; available PDF pp. 1–6. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 36, 42, 51, 55.
- `doc_99b04888284c4cf0802b` — GA & LOAD DATA OF BELT CONVEYOR-13.pdf, PDF pp. 1–2, 4–5.

Existing explicitly applicable reference identities: EAC-7/9/11/13 Power and Belt-Tension Calculation (Rev 03) (`ent_4fa8e251333d4025bb2c`), 20ND3 (`ent_54f0ffd4b8824691b339`), 20ND2 (`ent_5716817375904c21bef4`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), 20DR3 (`ent_fe07b3dff0234ed5bdde`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| KB-FD-1 | EAC-13 | Full or partial stacking | `fact_1445e6bd7c6c4115859c` |
| KB-FD-2 | EAC-13 | Full or partial stacking | `fact_68a14314e9fc4f71a3e8` |
| EAC-13 | EAD-4 | No condition recorded; review source | `fact_c51fc378ab6d429c86f6` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
