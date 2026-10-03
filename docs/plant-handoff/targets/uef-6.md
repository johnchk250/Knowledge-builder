# UEF-6

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B13**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_9d8aaa767de440b18a1a`.
- Existing containment closure: 1 record(s) including root; 12 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-6
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: KB-FD-7, KB-FD-8, DFDSS-1 PS-07

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_eadc432afcad400192d0` — GA & MECH LOAD OF TP-6.pdf; available PDF pp. 1–6. Retrieval candidate, not reviewed applicability.
- `doc_f9f96af6a25e47179881` — Piping Layout for DFDS, SW & PW System at UEF-6.pdf; available PDF pp. 1–3. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_2664b59a573b467eb166` — GA & LOAD DATA OF BELT CONVEYOR-7.pdf, PDF pp. 5.
- `doc_eadc432afcad400192d0` — GA & MECH LOAD OF TP-6.pdf, PDF pp. 4–6.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 17.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-6 | EAC-7 | No condition recorded; review source | `fact_ca5b4f1089c349e2925f` |
| FTR-3 | KB-FD-7 | No condition recorded; review source | `fact_a90ba3c422e748e5a2ce` |
| KB-FD-7 | EAC-5A | Through-flow beyond fixed tripper; same continuous conveyor, not a recirculation loop | `fact_8b3d2d115ff6425d96da` |
| KB-FD-7 | EAC-7 | Full or partial stacking | `fact_be9779fbfd0b4ae28170` |
| FTR-4 | KB-FD-8 | No condition recorded; review source | `fact_8d19cb70a9034aa391d0` |
| KB-FD-8 | EAC-5B | Through-flow beyond fixed tripper; same continuous conveyor, not a recirculation loop | `fact_78025cd3d8164c9db8df` |
| KB-FD-8 | EAC-7 | Full or partial stacking | `fact_b24fb658dbb44b3b9664` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
