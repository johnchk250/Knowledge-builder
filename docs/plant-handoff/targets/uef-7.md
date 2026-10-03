# UEF-7

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B14**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_dfd925fdeb7f4275b5f5`.
- Existing containment closure: 1 record(s) including root; 28 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-7
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: FG-5, FG-6, DFDSS-1 PS-08

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_f6e89f3b3d3b40eb8d80` — GA & MECH LOAD OF TP-7.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.
- `doc_d157f03e84e84c068b06` — Piping Layout for DFDS, SW & PW System at UEF-7.pdf; available PDF pp. 1–3. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_c91eac5d4c104264801f` — GA & LOAD DATA OF BELT CONVEYOR-6 A&B.pdf, PDF pp. 4.
- `doc_f6e89f3b3d3b40eb8d80` — GA & MECH LOAD OF TP-7.pdf, PDF pp. 2.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 17.
- `doc_d157f03e84e84c068b06` — Piping Layout for DFDS, SW & PW System at UEF-7.pdf, PDF pp. 1–2.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-5A | UEF-7 | No condition recorded; review source | `fact_a9299690b9c54efd9b7d` |
| EAC-5B | UEF-7 | No condition recorded; review source | `fact_b000f95c8fc945bdab7c` |
| UEF-7 | EBA-6A | No condition recorded; review source | `fact_0b243c312015488f97af` |
| UEF-7 | EBA-6B | No condition recorded; review source | `fact_31cb766b5cef42cf9ce4` |
| EAC-5A | FG-5 | No condition recorded; review source | `fact_7a1f295dbaeb497eb2ee` |
| FG-5 | EBA-6A | Gate FWD | `fact_f4038677d7a54ce090c0` |
| FG-5 | EBA-6B | Gate REV | `fact_bc8de823061540cd81cd` |
| EAC-5B | FG-6 | No condition recorded; review source | `fact_0f1540b83ca14272b4b4` |
| FG-6 | EBA-6A | Gate FWD | `fact_c56b48d83d4f49a391aa` |
| FG-6 | EBA-6B | Gate REV | `fact_1d705436e5364fd6a842` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
