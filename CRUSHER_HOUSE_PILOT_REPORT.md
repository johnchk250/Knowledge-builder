# Crusher-house implementation report

Accepted model **v558**, base **v527**. Completed 29 September 2026. Scope: P11 / B32–B35, selected by the user after the blending-silo pilot.

The house is now a visual process assembly: two vertical coal lanes, floor context, selectable screening/direct-bypass routes and selected EBA-18 outlet. A component opens an inspector; opening its assembly reveals connected parts. Evidence stays at the individual value or connection. Illustrative motion explains documented paths and is never live status.

## Accepted scope

31 source-reviewed versioned batches add **418 active canonical components/assemblies** (419 records created, one descriptive pressure-switch duplicate merged into the existing identity) and **1,818 active assertions**, including **51 source qualifications**. These are model records and grouped components, not a count of physical installed devices. Twenty source documents supplied accepted claims. All 24 candidate original hashes were checked unchanged.

| Assembly | Implemented detail |
|---|---|
| UEE-3 | Two process lanes, house levels, inter-section links, local services, access, eleven scheduled hoists, elevator and drainage |
| EBD-5/6 | Blind deck, grizzly plates, enclosure, 37 kW motor, Cardan/intermediate shafts, two exciters, springs and amplitude limiters |
| EBC-1/2 | Housing and doors, rotor/shaft and 56 ring hammers, bearing/seal groups, cage/adjustment, hydraulic opening, monitoring and two separate spring-supported foundations |
| Crusher drive | 750 kW motor → PST-1150 scoop coupling → rotor; no invented reduction gearbox |
| Scoop auxiliaries | Sump → strainer → pump → radiator → return filter; lubrication branch → duplex filter → coupling. Pump motor, fan motor, actuator, local instruments and qualified controls |
| EBA-17A/B | Belt/mechanical, pulleys, idlers, take-up/counterweight, motor/PST-500/gearbox/brake chain and device groups. Existing CV-5/6 identities remain associated with their conveyors |
| KF-1/2 | Three feed interfaces, belt and pulleys, take-up, feeder-specific 45 kW/SDFC-370/gearbox/brake drive, and protection groups |
| Gates | FG-15A/B screening/bypass identities separate from downstream FG-15/16; supported outlet-gate actuator/flap/bearing/limit/access parts |
| DE-1/2 | Four capture points each → ducts → cyclone → filter → ID fan; pulse valves, hoppers, RALs, selected dust-return gates, crossover dampers, local panel and four distinct operating-mode references |
| DE fan/filter/RAL | Filter bags/cages and access qualifications; 90 kW fan drives; five existing airlocks decomposed into rotor/tips, shaft/coupling, bearings/seals and geared motors |
| DFDS | System2 UEE-3 AP/FAS/PRU35–40; 44 scheduled nozzles across six applications, associated receiving/discharge interfaces, load/pressure/control signals |
| Access and services | SNC-1 lift reused with traction drive, ropes/sheaves, car/doors and safety/control features; SW/PW risers, roof tank, sump duty/standby positions; shared DE compressed-air connection remains outside house ownership |

## Invariants for the next agent

1. A lane is EBA-17A → FG-15A → EBD-5 → oversize EBC-1 → KF-1 → FG-15 → selected EBA-18A/B. EBD-5 undersize also goes to KF-1; FG-15A direct bypass goes to KF-1 independently. B uses FG-15B/EBD-6/EBC-2/KF-2/FG-16. Never make bypass pass through the screen or crusher.
2. EBD-1–4 belong to primary screening. Control p5 and the hoist schedule have secondary-screen tag errors; they do not authorize merges. FG-15A is not an alias of FG-15.
3. EBA-17 spans UEE-2 to UEE-3. Its discharge-end location does not make the complete conveyor a house-owned child. EBA-18 stays external. Device ownership, placement and utility supply remain distinct.
4. Preserve direct motor/scoop/rotor drive for EBC; the conveyor and feeder reducers are different designs. Do not copy PST-1150 oil details into PST-500 or the earlier PST-530 pilot.
5. Keep raw protection quantities and derived counts separate: each EBA-17 has PCS9 pairs/18 switches and BSS7 pairs/14 switches; each KF has PCS1 pair/2 switches and BSS1 pair/2 switches. Individual location tags were not invented.
6. DFDS nozzle total44 means all six scheduled applications, not44 simultaneously active sprays. AP35/38 are feeder discharge; AP36/39 feed18A receiving; AP37/40 feed18B receiving. Same tag numbers elsewhere in System1 are different identities.
7. Existing `DFDSS-2 PS-09` is the canonical pressure switch; the new descriptive duplicate redirects there. Its existing schedule facts remain intact. SNC-1 is an alias of the existing crusher-house elevator.
8. The generic VIS record is an engineering reference applicable to two per-crusher foundations, not a third foundation. Rihand STPP references are not Maitree house candidates; area entry is scoped to the current process area.
9. Motor, rotor-bearing, oil-system and local indication facts have distinct action targets. Gauges monitor; their presence does not imply an automatic trip. Source-conditional controls are references, not executable plant logic or an isolation procedure.

## Qualifications to preserve

| Issue | Recorded distinction / next evidence needed |
|---|---|
| Bearing limits | GA rotor-bearing alarm/trip80/90°C versus control scoop permission≤70/disengagement>80°C; motor bearing/winding limits separate. Commissioned cause/effect needed |
| Oil pump stop | 30 s adjustable narrative versus300 s trip list. Do not pick a timer by preference |
| CBS polarity | Both NOT operated required for engage; disengage clause says ANY NOT operated. Wording unresolved |
| Coupling oil/actuator | 75°C design operating limit versus85/110°C P&I alarm/trip; 415 L/min pump GA versus405 nominal P&I; actuator power/speed/timing variants |
| Screen capacity | 1375 t/h GA versus1370 selection calculation; retain bases |
| Feeder voltage | KF GA says3.3 kV; generic control calls drive LT. Verify actual supply and starter |
| Crusher handedness | One LH + one RH stated, numbered EBC assignment not proven by common GA |
| Bypass gate actuators | Older gate GA does not schedule FG-15A/B. Do not reuse FG-15/16 ratings |
| DE fan rating | Schematic110 kW tentative versus later FIO GA90 kW; GA quantity01 despite two-stream applicability |
| Filter bags / dampers | Bag quantity basis between compartment/BOM unresolved; schematic damper summary differs from six tagged dampers |
| Airlock speed/material | RAL GA20 rpm versus bag-filter RAL schedule25 rpm; reviewer requests abrasion-resistant lining, vendor asks acceptance of MS casing/rotor |
| Shared air package | DBR heatless-desiccant dryer versus refrigeration GA; UGA-2 location wording conflicts with other catalog tag use. No duplicated compressor house |
| DFDS permissives | Uses EBA-17 running-with-load for feeder sprays; residual KF discharge/direct-bypass coverage is not fully resolved in philosophy |
| Lifting / levels | Hoist-to-screen/gate typos preserved. Elevator FFL/TOS landings differ from structural TOC levels. Design capacities are not current lifting certification |
| Remaining detail | Exact hydraulic-pack ratings, final MCC/cable mapping, commissioned setpoints, individual switch locations, sump suffixes, maintenance intervals and inspection/isolation procedures require additional evidence |

## Source ledger

PDF page numbers below are one-based. Each accepted proposal contains its exact evidence IDs, normalized regions/quotes, source basis and conditions. Full candidate metadata/hashes are in `output/crusher-pilot/source-ledger.json`; per-claim provenance is in `accepted/*.json` and the model. “Used” means the listed claims were reviewed, not every page was exhaustively re-extracted.

| Source | Document ID | Pages used | Disposition |
|---|---|---|---|
| Control Write up for Coal Handling System.pdf | `doc_4f2cd96c3b1e413ea4b5` | 5, 15, 16, 17, 29, 55 | used |
| GA OF CRUSHER (RING GRANULATOR).pdf | `doc_f608e15aedbf4f368692` | 1 | used |
| GA & MECH LOAD OF CRUSHER HOUSE.pdf | `doc_e082675ac82d4ad280d2` | 1, 6 | used |
| GA OF SCOOP TYPE COUPLING FOR CRUSHER.pdf | `doc_624bd9eb971746e293a8` | 1, 2, 12 | used |
| GA OF VIBRATING GRIZZLY FEEDER (INCLUDING TECH. DATA SHEET).pdf | `doc_4581250ffd114bacba82` | 1, 2, 4 | used |
| GA & LOAD DATA OF BELT FEEDER 1 & 2 AT CRH.pdf | `doc_3aed51331d5243ab85ab` | 1 | used |
| GA & LOAD DATA OF BELT CONVEYOR-17 A&B.pdf | `doc_b8025e4ba6564a7e9510` | 4 | used |
| G.A. OF VIBRATION ISOLATION SYSTEM FOR CRUSHERS.pdf | `doc_d4f87b906a964bd58c17` | 1 | used |
| DUCTING LAYOUT FOR DE SYSTEM AT CRH.pdf | `doc_3b65e744297d4a028320` | — | Layout retained for future duct sizing, support and damper placement detail; this pilot models the schematic capture/air/dust topology. No duct lengths or coordinates inferred. |
| SCHEMATIC DIAGRAM FOR DE SYSTEM.pdf | `doc_84156b4bfaae4e6184fe` | 1 | used |
| OPERATION & CONTROL PHILOSOPHY OF DUST EXRACTION SYSTEM.pdf | `doc_a786031791b9437d9479` | 3, 5, 6, 7, 8, 9, 10, 11 | used |
| DESIGN BASIS REPORT OF DE SYSTEM.pdf | `doc_d4f7140726b240f7b479` | 7, 8 | used |
| GA OF BAGFILTER FOR DE SYSTEM.pdf | `doc_7263469a9d61411dbe04` | 4 | used |
| GA OF CENTRIFUGAL FANS FOR DE SYSTEM.pdf | `doc_ae2f48499fd7429fad60` | 2 | used |
| GA OF COMPRESSOR FOR DE SYSTEM.pdf | `doc_de3a27b73e1944a8b702` | — | Shared external air package; no local compressor copies. DBR location and dryer technology need reconciliation before installed-unit mapping. |
| GA AND DATASHEET FOR AIR DRYER FOR DE SYSTEM.pdf | `doc_35bfe8a0c5e743d2ae35` | — | Refrigeration GA differs from DBR heatless-desiccant description. Shared-package applicability unresolved. |
| GA OF ROTARY AIR LOCK VALVE FOR DE SYSTEM.pdf | `doc_799aadaacc6e481e8595` | 1, 2 | used |
| Piping Layout for DFDS, SW & PW System at UEE-3.pdf | `doc_a58b0c516ef3413db6c0` | 1 | used |
| P & ID FOR DFDS SYSTEM.pdf | `doc_bca09d68af9b43e3b633` | 2 | used |
| OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf | `doc_294aacf286d246769e32` | 29, 30, 31 | used |
| GA OF FLAP GATE.pdf | `doc_9258f527621741938b79` | 5 | used |
| P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf | `doc_0453a0a014424f1cae06` | 1 | used |
| GA OF ELEVATOR AT CRH.pdf | `doc_4079754720fe4b6891c1` | 1 | used |
| DATASHEET OF BELT FOR BELT FEEDER AND BUNKER SEALING SYSTEM.pdf | `doc_f40f9df559824fc9b500` | — | Common feeder/sealing-belt datasheet retained for follow-up specification/revision comparison; unit-specific KF1/2 belt facts use their GA. |


## Implementation and verification

- Canonical changes went through stage/validate/commit; immutable originals stayed unchanged. Consistent base SQLite backup: `output/crusher-pilot/backup-v527.sqlite3`; originals/renders remain in `data/plant` and must accompany a restore.
- Rehearsal database: `output/crusher-pilot/final-rehearsal/`. Accepted proposal bodies, commit hashes and exported model: `output/crusher-pilot/accepted/`. Do not replay `tools/enrich_crusher_pilot.py --apply`; it deliberately requires v527.
- `node tools/audit_crusher_pilot.cjs output/crusher-pilot/accepted/model.json`: passed route, ownership, drive, quantities, utility, merged switch, VIS-reference, elevator, airlock and evidence checks at v558.
- Silo semantic audit passed against v558, preserving its prior1253 assertions, crossover mapping and dual-drive architecture.
- Projection/scene tests:33 passed. JavaScript syntax check passed. Final integrity and browser acceptance are recorded in `output/crusher-pilot/verification.md`.
- No backend code was changed for this crusher implementation. No full Python regression suite is claimed; the repository already contained unrelated backend changes.

The whole-plant handoff inventories remain frozen at v510. This implementation does not complete upstream B00–B29 identity/service work or downstream B36 onward. Continue from the accepted graph and these qualifications, not the frozen counts.

## Continuation instructions

For B36 / P12, reuse EBA-18A/B and FG-15/16 outlet boundaries. Build their actual conveyor assemblies and UEF-13 receiving, weighing/metal detection, sampling and FG-17/18 onward paths from original drawings. Preserve CRH DE dust returns and DFDS receiving interfaces on those belts. Do not move the local CRH services into UEF-13 just because they serve18A/B.

For follow-up P11 work, resolve qualifications individually using revision-aware drawings, vendor O&M or commissioned records. Add or retire only the specific supported claims. Read the current `OPERATIONS_INGESTION_WORKFLOW.md`, `PLANT_MODEL_IMPLEMENTATION_HANDOFF.md` and chosen checkpoint first; reconcile live IDs/version. Keep scene coordinates illustrative, every physical assertion sourced, shared utilities external, and deep component-to-source navigation working.
