# EAC-3A

Planning card at model v628. Package **P03** — Primary screening, EAC-3 and UEF-3. Primary implementation batch **B10**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p03) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_9f1ca0f604de4bdda3a5`.
- Existing containment closure: 1 record(s) including root; 50 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-3A
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_3eab668d697f4e4598c8` — GA & LOAD DATA OF BELT CONVEYOR-3A-B.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 20–21, 27–28, 37–38, 55.
- `doc_3eab668d697f4e4598c8` — GA & LOAD DATA OF BELT CONVEYOR-3A-B.pdf, PDF pp. 1–2.

Existing explicitly applicable reference identities: UEF-3 Coal Sampling System (`ent_037e08c0c8134297a954`), 20DR2 (`ent_0bda87e7a4284cc78e03`), 20ND1 (`ent_48f3fa98490349ab9a70`), 20ND3 (`ent_54f0ffd4b8824691b339`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), EAC-3A/3B Power and Belt-Tension Calculation (Rev 03) (`ent_fc05c948c301492db8f2`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEE-1 | EAC-3A | No condition recorded; review source | `fact_551f69a5732d442c9559` |
| EAC-3A | UEF-3 | No condition recorded; review source | `fact_03e4c581e4514612ac36` |
| EBD-1 | EAC-3A | Undersize -100 mm | `fact_82930e30ba0942118fd6` |
| EBD-2 | EAC-3A | Undersize -100 mm | `fact_06e36e9dd1bb4a299915` |
| EAC-3A | KB-FD-1 | No condition recorded; review source | `fact_180c5a998959481f8577` |
| EAC-3A | EAU-1 Primary Sampler-1 | Sample cut only | `fact_d2f1acd1650845e4a53e` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
