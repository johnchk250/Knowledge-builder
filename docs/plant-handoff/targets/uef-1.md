# UEF-1

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B05**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#transfer) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_108b99f6c64844df8cf8`.
- Existing containment closure: 66 record(s) including root; 11 assertions on root. These are model records, not a count of physical devices.
- Aliases: UEF-1, Transfer Point UEF-1
- Existing parents: Maitree Coal Handling Plant
- Direct components: UEF-1 DFDS application equipment, UEF-1 Potable-water tank, UEF-1 Service-water hose boxes, UEF-1 Sump Pumps SP-4A/4B
- Located equipment: DFDSS-1 PS-02, EAC-1A Drive assembly, EAC-1B Drive assembly, EAC-1A discharge chute at UEF-1, EAC-2A receiving chute at UEF-1, EAC-1B discharge chute at UEF-1, EAC-2B receiving chute at UEF-1, UEF-1 FAS-01, UEF-1 PRU-01, UEF-1 FAS-02, UEF-1 PRU-02, UEF-1 FAS-03, UEF-1 PRU-03, UEF-1 FAS-04, UEF-1 PRU-04, UEF-1 Sump Pumps SP-4A/4B, CHP Intermediate sump near UEF-1

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_71a0d8fc66304e93b9c1` — GA & MECH LOAD OF TP-1.pdf; available PDF pp. 1–2. Retrieval candidate, not reviewed applicability.
- `doc_7568f1550b254ee2a94a` — Piping Layout for DFDS, SW & PW System at UEF-1.pdf; available PDF pp. 1–3. Retrieval candidate, not reviewed applicability.

Common source groups: **transfer, dfds** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 26, 55.
- `doc_31b03f5030bc4db69d8d` — GA & Data Sheet of Sump Pump.pdf, PDF pp. 15–16.
- `doc_603b4d9077e14d16b605` — GA & LOAD DATA OF BELT CONVEYOR-1A-B.pdf, PDF pp. 2.
- `doc_030c8f82fb674548a4dc` — GA & LOAD DATA OF BELT CONVEYOR-2A-B.pdf, PDF pp. 1.
- `doc_71a0d8fc66304e93b9c1` — GA & MECH LOAD OF TP-1.pdf, PDF pp. 1–2.
- `doc_5537009e2cff4fad875e` — GA - DATA SHEET OF NOZZLES FOR DFDS SYSTEM.pdf, PDF pp. 2.
- `doc_3cfdfb0f23c6429eb268` — GA OF FAS PRU FOR DFDS SYSTEM.pdf, PDF pp. 2–3.
- `doc_9b7d3360a5e84ec2abc3` — GA OF SPRAY HEADER FOR DFDS SYSTEM.pdf, PDF pp. 1–2.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 2, 4–5.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 1.
- `doc_0453a0a014424f1cae06` — P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf, PDF pp. 1.
- `doc_7568f1550b254ee2a94a` — Piping Layout for DFDS, SW & PW System at UEF-1.pdf, PDF pp. 2–3.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-1A | UEF-1 | No condition recorded; review source | `fact_124562f56d764560bebe` |
| EAC-1B | UEF-1 | No condition recorded; review source | `fact_776415bdc56546ffaa3e` |
| UEF-1 | EAC-2A | No condition recorded; review source | `fact_2603f4cc0765482f9d0a` |
| UEF-1 | EAC-2B | No condition recorded; review source | `fact_fff27dc6f3654329ab2f` |
| EAC-1A | EAC-1A discharge chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_713d84b609484d63b5b5` |
| EAC-1A discharge chute at UEF-1 | EAC-2A receiving chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_57308b45afb94f21825b` |
| EAC-2A receiving chute at UEF-1 | EAC-2A | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_6b7b490f27f541e7b727` |
| EAC-1B | EAC-1B discharge chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_e443533cb23149a799ba` |
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

- `fact_79ede34f1b464e888b85` (UEF-1 AP-01): Individual nozzle identification, installed orientation and commissioning checks remain unresolved; this record preserves the design application-point quantity.
- `fact_3d0b591a5bf54f68bebe` (UEF-1 AP-02): Individual nozzle identification, installed orientation and commissioning checks remain unresolved; this record preserves the design application-point quantity.
- `fact_c7014af59af544d191ad` (UEF-1 AP-03): Individual nozzle identification, installed orientation and commissioning checks remain unresolved; this record preserves the design application-point quantity.
- `fact_875ac581e7d4419e98f2` (UEF-1 AP-04): Individual nozzle identification, installed orientation and commissioning checks remain unresolved; this record preserves the design application-point quantity.
- `fact_17117f8335a8441dbeb6` (UEF-1 DFDS application equipment): Pressure-switch tag discrepancy: the UEF-1 P&ID inset shows both PS-01 and PS-02 labels; the DFDS control philosophy uses PS-02 for all four UEF-1 FAS permissives. Do not merge the inset PS-01 with the pump-house PS-01.
- `fact_fe59003670ee4989bafc` (UEF-1 FAS-01): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_9b0074c6ae6e4bba9ed2` (UEF-1 PRU-01): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_27bdfe6108514f2c8066` (UEF-1 FAS-02): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_bdb08186773e4bcfaa41` (UEF-1 PRU-02): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_be98af7edad34f6981e7` (UEF-1 FAS-03): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_67753d8fa9fd4be79883` (UEF-1 PRU-03): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_4bc0c7ea119b4000944f` (UEF-1 FAS-04): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_04e52e6ae9c74557a436` (UEF-1 PRU-04): Internal components follow the project standard assembly linked to this FAS/PRU identity. Individual installed valve/filter/regulator tags and settings need field records.
- `fact_6d4d30c0b6574f2e852c` (UEF-1 Sump Pumps SP-4A/4B): Duty selection and installed pump condition are not live; local motor/level-switch cable tags and discharge isolation details need field/loop records.
- `fact_bad5b44547f6462eb439` (UEF-1): Finding TP1 GA 175033 resolves the earlier missing-drawing search only. Available GA arrangement, hoist schedule and tank/review details remain B05 work. Access certification, field condition and liner wear limits are not established by this GA.
