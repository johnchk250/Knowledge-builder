# EAC-1B

Planning card at model v628. Package **P02** — Jetty, ship unloaders, EAC-1/2 and UEF-1. Primary implementation batch **B05**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p02) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_8e0a39fb6e844f8a90d6`.
- Existing containment closure: 66 record(s) including root; 76 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-1B, Belt Conveyor EAC-1B, Conveyor EAC-1B
- Existing parents: Maitree Coal Handling Plant
- Direct components: EAC-1B Drive Gearbox B3 450, EAC-1B Drive assembly, EAC-1B Belt and mechanical assemblies, EAC-1B Belt protection devices, EAC-1B discharge chute at UEF-1
- Located equipment: AT-2

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
| EAC-1B | UEF-1 | No condition recorded; review source | `fact_776415bdc56546ffaa3e` |
| Coal Jetty | EAC-1B | No condition recorded; review source | `fact_12ac5ba6c3544e539ef1` |
| Coal Ship Unloader-1 | EAC-1B | Shuttle selected to EAC-1B | `fact_487200c4c3204e16ace2` |
| Coal Ship Unloader-2 | EAC-1B | Shuttle selected to EAC-1B | `fact_35887dd739c84cebb2fb` |
| Coal Ship Unloader-3 | EAC-1B | Shuttle selected to EAC-1B | `fact_41f3e632ea9d4ba5a581` |
| EAC-1B | EAC-2B | Transfer at UEF-1 | `fact_55fb76ff94ec43a9a5b3` |
| EAC-1B | EAC-1B discharge chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_e443533cb23149a799ba` |
| EAC-1B discharge chute at UEF-1 | EAC-2B receiving chute at UEF-1 | A-to-A / B-to-B path drawn in DFDS P&ID UEF-1 inset; no crossover inferred | `fact_8b8867b14a0e45b0bb65` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_cb0854c5798549ca9f8e` (EAC-1B Take-up counterweight): Rounding discrepancy: 994 blocks x 17.5 kg = 17395 kg, while the drawing states a 17400 kg design weight. Preserve both bases.
- `fact_1e3ec70cd8024919832f` (EAC-1B Pull-cord switches (PCS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_90af7f986adb48b29558` (EAC-1B Belt-sway switches (BSS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_c764f4295ce74536b859` (EAC-1B Zero-speed switch (ZSS)): Individual field tag, cable/terminal and commissioning test record are unresolved in this drawing.
- `fact_fb19f6fba3314416a426` (EAC-1B): Individual PCS/BSS tags, commissioning settings and complete chute-block-switch locations are unresolved. Counts here are approved GA design quantities.
- `fact_95866261442c4b57b62c` (EAC-1B Main motor): Supply-tolerance discrepancy: GA gives 3.3 kV +/-10%, 50 Hz +/-5%; drive schedule gives 3300 V +/-6%, 50 Hz +3%/-5%. Field/nameplate applicability unresolved.
- `fact_29300b1d2967430c9d97` (EAC-1B Scoop coupling PST-530): Filter nomenclature requires reconciliation: GA supply list calls a 20-mesh oil-filter screen; P&I distinguishes a 20-mesh suction strainer and 40-mesh Y-filter. Do not replace one with the other without identifying the component.
- `fact_0bf147040ba34ea691af` (EAC-1B Scoop TS1): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_681a7b8b0cd2462abd18` (EAC-1B Scoop TS2): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_b7f92a4722d641dabe41` (EAC-1B Scoop PS): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_8958104e64ba4902a761` (EAC-1B Scoop DPS): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_8e380bdcff234579aa9d` (EAC-1B Scoop FSO): Field calibration and commissioned setting are not established by the vendor design table.
- `fact_cbf12399e901432d8907` (EAC-1B Scoop coupling PST-530): Internal service procedures, overhaul tolerances, instrument calibration sheets and installed equipment serial numbers remain unresolved.
- `fact_0035d7cc280e4994ba07` (EAC-1B Head pulley bearings): Bearing selection is from calculation. Verify the installed bearing, adapter, housing, seals and clearance before using it for procurement or replacement.
- `fact_070cb36d99bc4e8f85b0` (EAC-1B): Unresolved motor-rating discrepancy: brake GA EAC-1A/B row states 350 kW / 1480 rpm, whereas conveyor GA, drive schedule and gearbox GA state 315 kW. No installed/nameplate value has been selected.
- `fact_468663d53adf4d6c9bc9` (EAC-1B Thruster brake): Brake-position contact meaning requires reconciliation: sheet 3 calls the limit switch brake-engage; the control write-up uses brake-released feedback. Do not infer contact polarity from the component name.
- `fact_325fd4f38eed4b259678` (EAC-1B Scoop actuator): CBS polarity unresolved: the permissive says both CBS are not operated, but the trip list also prints CBS not operated. Do not normalize this into executable logic. The succeeding-conveyor/scoop wording also requires application review.
- `fact_077bbfbbe79547d9bfbf` (EAC-1B Scoop actuator): Path-table discrepancy: page 38 lists main motor for conveyor 1A running as the scoop-actuator permissive for 1B. General section requires the respective conveyor motor. This is retained as an unresolved source inconsistency.
- `fact_5bc78f718148426ba702` (EAC-1B Scoop DPS): Control write-up calls for indication/alarm and says trip the motor without identifying which motor; vendor P&I table provides an alarm value only. Trip target remains unresolved.
- `fact_d12a68e81c9d4806a4a9` (EAC-1B): CBS mounting/count, field loop IDs, path-specific magnetic-separator applicability, final relay logic and approved commissioned settings remain unresolved. Generic listed protections do not establish every installed sensor.
