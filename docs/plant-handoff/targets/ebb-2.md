# EBB-2

Planning card at model v628. Package **P10** — Blending silos and extraction. Primary implementation batch **B30**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p10) and [family contract](../ASSEMBLY_CONTRACTS.md#silo) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_30e0f002e2b64c92a2a7`.
- Existing containment closure: 17 record(s) including root; 9 assertions on root. These are model records, not a count of physical devices.
- Aliases: EBB-2
- Existing parents: Maitree Coal Handling Plant, Coal Blending Silo House
- Direct components: EBB-2 Shell and sloping liner, EBB-2 Level and temperature instruments, EBB-2 Emergency bypass chute, EBB-2 Manholes and access openings, EBB-2 Vent filter system
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **silo, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 40, 45, 55.
- `doc_17dab58f999c4939bbc7` — GA & MECH LOAD OF CBSH.pdf, PDF pp. 1, 4, 6–7.
- `doc_a786031791b9437d9479` — OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf, PDF pp. 4, 15–16.
- `doc_84156b4bfaae4e6184fe` — SCHEMATIC DIAGRAM FOR DE SYSTEM.pdf, PDF pp. 3.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EBA-6A | EBB-2 | Corresponding silo not at high level | `fact_fe225482053943a58073` |
| EBA-16B | EBB-2 | Corresponding silo not at high level | `fact_8525d8d5a90542509ebb` |
| EBB-2 | EBE-CES-2 | No condition recorded; review source | `fact_c4283ca9fa2d4c4c9c96` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_c76cadd4f25941aba45f` (EBB-2 Level and temperature instruments Level indication): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_fbf58bb225214ff4957c` (EBB-2 Level and temperature instruments Temperature detector): GA notes establish the provision, not an installed tag, measurement range or alarm/trip setpoint.
- `fact_d597f67a59b447159168` (EBB-2 Emergency bypass chute): Bypass chute and rod gate are documented; discharge endpoint and operating/isolation procedure are not established by these reviewed views.
- `fact_5665f925834b4d63a5c4` (EBB-2 Vent filter system): Generic accessories legend also lists RAV and ZSS, but the direct-mount silo arrangement does not show a hopper/RAV. No such local components are inferred from that legend.
- `fact_63e835adbed04bc9aa51` (EBB-2 Vent filter system): Silo section inconsistently uses BU tags for fan/DP/timer in some steps and BS tags elsewhere. Existing BS identities retained with this qualification; no extra bunker-tagged devices created.
- `fact_84a6cf52e20547cba188` (DPS-BS-2-001): DP set value and precise timer setting are not given here; source says unhealthy within2–3 min, not a single commissioned trip delay.
