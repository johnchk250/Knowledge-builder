# EAC-1A

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B05**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_141f73b0a4ef460b9830`.
- Existing containment closure: 66 record(s) including root; 76 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-1A, Belt Conveyor EAC-1A, Conveyor EAC-1A
- Existing parents: Maitree Coal Handling Plant
- Direct components: EAC-1A Drive Gearbox B3 450, EAC-1A Drive assembly, EAC-1A Belt and mechanical assemblies, EAC-1A Belt protection devices, EAC-1A discharge chute at UEF-1
- Located equipment: AT-1

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_603b4d9077e14d16b605` — GA & LOAD DATA OF BELT CONVEYOR-1A-B.pdf; available PDF pp. 1–7. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_41860f7c9ac2467bbdb4` — BRG SELECTION & SHELL & DIAPHRAGM THICKNESS CALCULATION FOR CONVEYOR PULLEYS.pdf, PDF pp. 3–4.
- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 1.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 4, 9, 26–29, 34, 38, 55.
- `doc_957d8f8bd41c4e71be3c` — DRIVE SCHEDULE-.pdf, PDF pp. 2.
- `doc_603b4d9077e14d16b605` — GA & LOAD DATA OF BELT CONVEYOR-1A-B.pdf, PDF pp. 1–4.
- `doc_64825298f3d243368408` — GA OF BRAKE FOR CHP CONVEYORS.pdf, PDF pp. 3.
- `doc_97e93732778e4618b52b` — GA OF GEAR BOX.pdf, PDF pp. 7.
- `doc_62fdccede7154dc2b8b6` — GA OF GEARED COUPLING.pdf, PDF pp. 2.
- `doc_7aa49cc0d1c34af7ac06` — GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf, PDF pp. 2, 5, 14.
- `doc_294aacf286d246769e32` — OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf, PDF pp. 3, 5.
- `doc_bca09d68af9b43e3b633` — P & ID FOR DFDS SYSTEM.pdf, PDF pp. 1.
- `doc_6d2b1e4a7f594b6ca3d9` — POWER & BELT TENSION CALC. FOR CONVEYORS.pdf, PDF pp. 2–3, 5, 12, 15, 17.
- `doc_7568f1550b254ee2a94a` — Piping Layout for DFDS, SW & PW System at UEF-1.pdf, PDF pp. 1–2.

Existing explicitly applicable reference identities: 20ND1 (`ent_48f3fa98490349ab9a70`), 20ND3 (`ent_54f0ffd4b8824691b339`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), 20DR1(SS) (`ent_8d97327b153e420ebaf0`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| EAC-1A | UEF-1 | No condition recorded; review source | `fact_124562f56d764560bebe` |
| Coal Jetty | EAC-1A | No condition recorded; review source | `fact_a608d0be11b34c559793` |
| Coal Ship Unloader-1 | EAC-1A | Shuttle selected to EAC-1A | `fact_83b29592d8c54a7989e2` |
| Coal Ship Unloader-2 | EAC-1A | Shuttle selected to EAC-1A | `fact_c031913e00884d638b23` |
| Coal Ship Unloader-3 | EAC-1A | Shuttle selected to EAC-1A | `fact_56fff835e5b245a1a4fb` |
| EAC-1A | EAC-2A | Transfer at UEF-1 | `fact_f544d2527f1e4102aebe` |
| EAC-1A | EAC-1A discharge chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_713d84b609484d63b5b5` |
| EAC-1A discharge chute at UEF-1 | EAC-2A receiving chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_57308b45afb94f21825b` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_988d4e703918477bb4c9` (EAC-1A Take-up counterweight): Rounding discrepancy: 994 blocks x 17.5 kg = 17395 kg, while the drawing states a 17400 kg design weight. Preserve both bases.
- `fact_e6def187fcba40ecbb34` (EAC-1A Pull-cord switches (PCS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_cbea2c4768e04b7f8468` (EAC-1A Belt-sway switches (BSS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_fea8f330952a48e5a5d5` (EAC-1A Zero-speed switch (ZSS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_8d3aeaa08dbf4ebe8022` (EAC-1A): Individual PCS/BSS tags, commissioning settings and complete chute-block-switch locations are unresolved. Counts here are approved GA design quantities.
- `fact_f87e81060af24bd6a91a` (EAC-1A Main motor): Supply-tolerance discrepancy: GA gives 3.3 kV +/-10%, 50 Hz +/-5%; drive schedule gives 3300 V +/-6%, 50 Hz +3%/-5%. Field/nameplate applicability unresolved.
- `fact_b9ce99c75a4a4c6f8663` (EAC-1A Scoop coupling PST-530): Filter nomenclature requires reconciliation: GA supply list calls a 20-mesh oil-filter screen; P&I distinguishes a 20-mesh suction strainer and 40-mesh Y-filter. Do not replace one with the other without identifying the component.
- `fact_f2d26b85919f4ac4bdb5` (EAC-1A Scoop TS1): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_f762811f0e5246b0b04b` (EAC-1A Scoop TS2): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_6f5a106fb9c346e69c9f` (EAC-1A Scoop PS): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_a516af5c522247e9b117` (EAC-1A Scoop DPS): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_dd02bf65a3c84ddcb7c8` (EAC-1A Scoop FSO): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_7e06148f7d2442ec8a7b` (EAC-1A Scoop coupling PST-530): Internal service procedures, overhaul tolerances, instrument calibration sheets and installed equipment serial numbers remain unresolved.
- `fact_05f7f7de00fb472989ea` (EAC-1A Head pulley bearings): Bearing selection is from calculation. Verify the installed bearing, adapter, housing, seals and clearance before using it for procurement or replacement.
- `fact_72605657eaa0448c95b9` (EAC-1A): Unresolved motor-rating discrepancy: brake GA EAC-1A/B row states 350 kW / 1480 rpm, whereas conveyor GA, drive schedule and gearbox GA state 315 kW. No installed/nameplate value has been selected.
- `fact_97288a26b7894a5ea556` (EAC-1A Thruster brake): Brake-position contact meaning requires reconciliation: sheet 3 calls the limit switch brake-engage; the control write-up uses brake-released feedback. Do not infer contact polarity from the component name.
- `fact_d02d900259fb485988c1` (EAC-1A Scoop actuator): CBS polarity unresolved: the permissive says both CBS are not operated, but the trip list also prints CBS not operated. Do not normalize this into executable logic. The succeeding-conveyor/scoop wording also requires application review.
- `fact_f30ad82668ae46a2b813` (EAC-1A Scoop DPS): Control write-up calls for indication/alarm and says trip the motor without identifying which motor; vendor P&I table provides an alarm value only. Trip target remains unresolved.
- `fact_7de418b752b444b2a4ca` (EAC-1A): CBS mounting/count, field loop IDs, path-specific magnetic-separator applicability, final relay logic and approved commissioned settings remain unresolved. Generic listed protections do not establish every installed sensor.
