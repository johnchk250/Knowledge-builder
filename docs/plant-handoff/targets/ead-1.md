# EAD-1

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B15**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#stacker) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_838e4b6c7e0f4855962b`.
- Existing containment closure: 101 record(s) including root; 17 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAD-1
- Existing parents: Maitree Coal Handling Plant, Coal Yard 1
- Direct components: EAD-1 Boom Belt Weigher, EAD-1 Boom conveyor, EAD-1 Slew system, EAD-1 Luffing system, EAD-1 Travel system, EAD-1 Operator cabin, EAD-1 Travelling tripper, EAD-1 Onboard plain-water DSS, EAD-1 Central grease lubrication, EAD-1 Fire detection and clean-agent system, EAD-1 Electrical house
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **stacker** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_78bebe6773984d59b013` — Basis of Design for Coal Stacker Machine.pdf, PDF pp. 2–3.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 7, 43, 55.
- `doc_0f52c77514a74773ae30` — DBR for Machine mounted DS system for Stacker Machine.pdf, PDF pp. 8, 21–23.
- `doc_4d488fd685284c408297` — Fire detection and extinguishon system of Stacker.pdf, PDF pp. 2, 5–6.
- `doc_b7d031cc33c54157ad86` — GA , TDS & P&ID of Motorized Central lubrication system for Stacker Machine.pdf, PDF pp. 1.
- `doc_9f1d51138e104d5a905e` — GA of Hydraulic Power Pack & Hydraulic Cylinder for Slew Drive and Luffing for Coal Stacker Machine.pdf, PDF pp. 2, 7.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-7 | EAD-1 | No condition recorded; review source | `fact_f202b03c0f5740ceb2df` |
| EAD-1 | EAE-1 | Uncrushed coal stacking on one side of machine | `fact_2bffa6cbdf2349f09c80` |
| EAC-7 | EAD-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_145fcc205d5c4c4eae55` |
| EAD-1 | EAE-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_239c3944a41f4c95b147` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_a794efbd44a9400a8262` (EAD-1): BOD calls handled material crushed coal; yard conveyor GA and plant flow identify the pre-crushing stockyard stream. Preserve the BOD wording, without changing the documented plant route.
- `fact_01cdf7141e02427b8519` (EAD-1): Machine PLC cause/effect, collision and travel-limit loops, storm-parking procedure and field tag assignment require separate verification. Structural wind limits are not automatic trip thresholds.
- `fact_f18866e7c2c249038a0e` (EAD-1 Onboard plain-water DSS): Component list specifies duplex filter; alarm text says simplex filter choked. Preserve both; actual filter arrangement needs reconciliation.
- `fact_bba874b9e1fd4585b9cb` (EAD-1 Central grease lubrication): Drawing first-fill quantities do not establish routine regreasing quantity or interval. Pump labels are descriptive; installed tags and controller timings need verification.
- `fact_de7a5ead4cfe43dba691` (EAD-1 Fire detection and clean-agent system Z101 Protected zone): BOM shows two cylinders per zone, while schematic charge notation states one cylinder. Do not infer duty/reserve allocation or discharge quantity without the final release cause-and-effect.
- `fact_19e444d40db6441dbae2` (EAD-1 Fire detection and clean-agent system Z201 Protected zone): BOM shows two cylinders per zone, while schematic charge notation states one cylinder. Do not infer duty/reserve allocation or discharge quantity without the final release cause-and-effect.
- `fact_1d8e5c76e74045a7a24a` (EAD-1 Operator cabin): Machine BOD cabin dimensions are 2.4 x 1.9 x 2.4 m; fire design uses 2.4 x 1.9 x 2.5 m. Protected-volume design and final enclosure dimensions require reconciliation.
- `fact_ce90b808e9694b8ea123` (EAD-1 Fire detection and clean-agent system): Final release logic, commissioned delay, isolations and inspected cylinder status are not established. This machine system does not establish stockpile fire hydrant, monitor or coal-temperature coverage.
