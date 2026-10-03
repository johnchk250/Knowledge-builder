# EAC-7

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B16**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#conveyor) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_55a98320cca54b6bb644`.
- Existing containment closure: 41 record(s) including root; 59 assertions on root. These are model records, not a count of physical devices.
- Aliases: EAC-7
- Existing parents: Maitree Coal Handling Plant, Coal Yard 1
- Direct components: EAC-7 Drive assembly, EAC-7 Head pulley, EAC-7 Belt, EAC-7 Take-up assembly, EAC-7 Belt protection devices, EAC-7 Idlers, EAC-7 External scrapers, EAC-7 Internal scraper
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- `doc_2664b59a573b467eb166` — GA & LOAD DATA OF BELT CONVEYOR-7.pdf; available PDF pp. 1–11. Retrieval candidate, not reviewed applicability.

Common source groups: **conveyor, measurement** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 9, 26–29, 36, 42–43, 51, 55.
- `doc_2664b59a573b467eb166` — GA & LOAD DATA OF BELT CONVEYOR-7.pdf, PDF pp. 5, 8–10.
- `doc_7aa49cc0d1c34af7ac06` — GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf, PDF pp. 4.

Existing explicitly applicable reference identities: EAC-7/9/11/13 Power and Belt-Tension Calculation (Rev 03) (`ent_4fa8e251333d4025bb2c`), 20ND3 (`ent_54f0ffd4b8824691b339`), 20ND2 (`ent_5716817375904c21bef4`), CHP General Conveyor Control Scheme (`ent_69e493280cf04abca5b8`), CHP HT Conveyor Drive Control Scheme (`ent_dee15248904f4820b982`), 20DR3 (`ent_fe07b3dff0234ed5bdde`).

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-6 | EAC-7 | No condition recorded; review source | `fact_ca5b4f1089c349e2925f` |
| EAC-7 | UAX-1 | No condition recorded; review source | `fact_c4a0505949f74ccfb540` |
| KB-FD-7 | EAC-7 | Full or partial stacking | `fact_be9779fbfd0b4ae28170` |
| KB-FD-8 | EAC-7 | Full or partial stacking | `fact_b24fb658dbb44b3b9664` |
| EAC-7 | EAD-1 | No condition recorded; review source | `fact_f202b03c0f5740ceb2df` |
| EAC-7 | EAD-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_145fcc205d5c4c4eae55` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_bdc4fc534ed8476e91f9` (EAC-7 Belt protection devices Pull-cord switches (PCS)): PCS total needs reconciliation of both-side symbols, schedule and quantity unit. No multiplication into an installed switch count has been made.
- `fact_6b23e33b951e43a1ba29` (EAC-7): Field sensor loop IDs, brake setting and final equipment-specific control settings require confirmation. Coupling oil details are recorded separately from the vendor design, with model applicability qualifications.
- `fact_76eb1177b181487384e1` (EAC-7 Drive assembly Scoop coupling): Instrument drawing symbols do not establish plant loop IDs. Alarm/trip thresholds, controller wiring and actual oil fill require applicable final records.
- `fact_810f2ec6a0534a37b46e` (EAC-7 Drive assembly Scoop coupling Scoop actuator): General CBS permissive and trip wording both say not operated, leaving trip polarity unresolved. Succeeding-conveyor/scoop conditions also require application review; no executable Boolean logic is inferred.
