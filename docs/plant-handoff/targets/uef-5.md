# UEF-5

Planning card at model v628. Package **P04** — Distribution: UEF-4/5/6/7, EAC-4/5 and EBA-6. Primary implementation batch **B13**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p04) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_ec4a66d4440444dcb00e`.
- Existing containment closure: 1 record(s) including root; 11 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-5
- Existing parents: Maitree Coal Handling Plant
- Direct components: none recorded
- Located equipment: KB-FD-5, FG-3, KB-FD-6, FG-4, DFDSS-1 PS-06

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_6d28742056e94651be04` — GA & MECH LOAD OF TP-5.pdf; available PDF pp. 1–3. Retrieval candidate, not reviewed applicability.
- `doc_e91d806d942243248e18` — Piping Layout for DFDS, SW & PW System at UEF-5.pdf; available PDF pp. 1–3. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 55.
- `doc_b74a01e57a2b4792883c` — GA & LOAD DATA OF BELT CONVEYOR-5 A&B.pdf, PDF pp. 3.
- `doc_cd640b41256b4b288744` — GA & LOAD DATA OF BELT CONVEYOR-9.pdf, PDF pp. 5.
- `doc_6d28742056e94651be04` — GA & MECH LOAD OF TP-5.pdf, PDF pp. 3.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 17.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-4A | UEF-5 | No condition recorded; review source | `fact_f4e5935621504a829307` |
| EAC-4B | UEF-5 | No condition recorded; review source | `fact_d5abf917e8da4756b662` |
| UEF-5 | EAC-5A | No condition recorded; review source | `fact_b8b1c7d390c64199a22c` |
| UEF-5 | EAC-5B | No condition recorded; review source | `fact_4689884333e54a9dbd80` |
| UEF-5 | EAC-9 | No condition recorded; review source | `fact_75a0eeb0ce2e40328ddc` |
| EAC-4A | KB-FD-5 | No condition recorded; review source | `fact_744b5a434cfa464a868e` |
| KB-FD-5 | EAC-9 | Full or partial stacking | `fact_f29a6d8a2a894b538c51` |
| KB-FD-5 | FG-3 | Onward flow | `fact_7f3612357b964e00a0fe` |
| FG-3 | EAC-5A | Gate aligned to selected downstream conveyor | `fact_317a920070bb455f807d` |
| FG-3 | EAC-5B | Gate aligned to selected downstream conveyor | `fact_2486c7afc21343c7bf37` |
| EAC-4B | KB-FD-6 | No condition recorded; review source | `fact_4e469bb4345d483c95e4` |
| KB-FD-6 | EAC-9 | Full or partial stacking | `fact_b56a0a21416643b1a706` |
| KB-FD-6 | FG-4 | Onward flow | `fact_5e7b2bb2e3674a898f3b` |
| FG-4 | EAC-5A | Gate aligned to selected downstream conveyor | `fact_60fe678dec604d7693cc` |
| FG-4 | EAC-5B | Gate aligned to selected downstream conveyor | `fact_91c26346827747759de9` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- None explicitly recorded under `source_gap`/`source_discrepancy`; this does not mean none exist. Read the findings register and source text.
