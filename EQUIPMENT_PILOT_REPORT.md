# Conveyor 1A / 1B and Transfer Point 1 enrichment

Implemented in the accepted plant model on 19 September 2026: **version 466 → 484**, through 18 reviewed, version-guarded ingestion batches.

## Open the result

- [EAC-1A assembly facts](http://127.0.0.1:8765/#overview?equipment=ent_141f73b0a4ef460b9830&tab=assembly)
- [EAC-1B assembly facts](http://127.0.0.1:8765/#overview?equipment=ent_8e0a39fb6e844f8a90d6&tab=assembly)
- [UEF-1 / TP-1 structure and equipment located here](http://127.0.0.1:8765/#overview?equipment=ent_108b99f6c64844df8cf8&tab=structure)
- [Reusable agent prompt](EQUIPMENT_ENRICHMENT_AGENT_PROMPT.md)

The local application must be running for these links. Launch `start.bat` if needed.

## What changed

The pilot adds **186 component/assembly records and 1,222 assertions** from **16 documents and 35 cited PDF pages**. The assertion count includes 394 classifications and component-membership relations; it is not 1,222 independent numeric specifications. Existing canonical identities were reused where present, and previous assertions were preserved.

Each target now has 66 records in its containment tree, including the root and existing components. This is a navigation count, not a physical equipment or spare-parts quantity. Groups such as PCS pairs, idlers and nozzles remain groups where individual installed tags are unavailable.

### EAC-1A and EAC-1B

The navigable structure covers the main motor, scoop coupling, gearbox, low-speed coupling and head pulley; coupling oil pump and motor, radiator and motor, filters/strainer, oil sump, actuator, fusible plug and instruments; gearbox holdback, fan and service fittings; thruster brake, shoes/liners, spring and position feedback; belt, pulleys, head-pulley bearing design selection, idler groups, scrapers, take-up pulley, rope, sheave and counterweight; PCS, BSS, ZSS and the DFDS load input.

Separate mechanical, oil-utility and control relationships explain how these components interact. Original control wording remains qualified where its action or polarity is unclear. Head-end drive and chute location links connect the conveyor to UEF-1 without transferring ownership of the whole conveyor to the building.

Representative source-backed details:

| Item | Recorded detail | Basis |
|---|---|---|
| PCS, each conveyor | 14 pairs; separately derived 28 individual switches; 30 m spacing | Conveyor GA PDF p4 |
| BSS, each conveyor | 11 pairs; separately derived 22 individual switches; 40 m interval | Conveyor GA PDF p4 |
| ZSS | 1 at tail pulley; general threshold below 85% rated belt speed; separately stated 60 s on-delay in scoop-disengagement list | GA p4; control pp9,29 |
| Main motor | 315 kW, 3.3 kV, 1488 rpm in GA | GA p4; conflicting brake-design entry retained |
| Scoop oil pump | 150 L/min design rating, 2.2 kW motor | Applicable 530 PST GA p2 |
| Scoop oil | 270 L capacity and source-listed oil grades | Scoop GA p2 |
| Scoop instruments | Separate nominal values, measurement ranges, alarm/trip values and unresolved final action | Scoop P&I p5; control pp28,29,34 |
| Gearbox | B3-450; actual ratio 17.820; ISO VG-320; approximately 205 L; ambient-qualified thermal ratings | Gearbox GA p7 |
| Low-speed coupling | RG-10, gearbox/pulley-side bores, grease grade and 8.5 kg/set fill | Geared coupling GA p2 |
| Head-pulley bearing | 23148 CCK calculation selection, linked to the equipment applicability column | Pulley calculation pp3–4; installation unverified |
| Belt | 2,000 mm width; endless lengths 820 m for 1A and 825 m for 1B | Conveyor GA p4 |

The user's “40 PCS” example was treated as a provenance example, not imported as a plant value.

### UEF-1 / TP-1

The model distinguishes incoming discharge and outgoing receiving interfaces. The reviewed DFDS P&ID depicts A-to-A and B-to-B transfers; no crossover was inferred from the sketch.

| DFDS application point | Interface | Design nozzle count |
|---|---|---:|
| AP-01 | EAC-1A discharge | 4 |
| AP-02 | EAC-2A receiving | 9 |
| AP-03 | EAC-1B discharge | 4 |
| AP-04 | EAC-2B receiving | 9 |
| Total | Four local application points | 26, derived |

Each zone leads to its FAS, PRU, separate air/water headers and nozzle group. The standard FAS/PRU internals include the air/water solenoid valves, air filter, water strainer and regulators, with design applicability retained. The local air and water mains connect to the FAS equipment; shared upstream supply equipment remains linked as a service rather than cloned locally.

The DFDS automatic conditions are attached to the affected zones: healthy PS-02 air pressure, the corresponding loaded conveyor input from UBS-1 or UBS-2, and AUTO selection. Manual mode is recorded separately. Local layout/elevation descriptions, potable-water tank and washing hose boxes are also navigable.

SP-4A and SP-4B are mapped to UEF-1 from the sump P&ID, not from the order of a grouped vendor list. Each has the 30 m³/h, 45 m, 22 kW design duty, its motor and selected pump components; the pair retains its one-working/one-standby arrangement and level-control requirement.

## Browsing and evidence

- **Structure & auxiliaries** follows component membership. **Equipment located here** exposes conveyor-owned items physically located at the transfer point.
- **Assembly facts** searches the complete component tree, with filters for protection, ranges, mechanical information, operation and gaps. Try `Pull-cord`, `oil`, `gearbox`, `nozzle` or `SP-4A`.
- Every assertion has a source button. A region citation opens an enlarged original-PDF detail, with a highlighted full-page view and a link to the original PDF page. Multiple supports remain available under **Basis & evidence**.
- The source viewer shows the claim's basis separately from the imported catalogue classification. Some existing catalogue labels say “Approved as-built drawing”; the pilot uses the actual drawing approval/revision wording and does not claim installation or commissioning verification.

## Source coverage

Numbers below are one-based PDF pages. Printed sheet numbering can differ. These are the pages supporting accepted pilot claims; the complete document/corpus is not claimed to have been exhaustively extracted. Exact document IDs, original hashes and cited page lists are in [the source manifest](output/equipment-pilot/accepted/source-manifest.json).

| Original document | Cited PDF pages |
|---|---|
| GA & LOAD DATA OF BELT CONVEYOR-1A-B.pdf | 1, 3, 4 |
| DRIVE SCHEDULE-.pdf | 2 |
| GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf | 2, 5, 14 |
| GA OF GEAR BOX.pdf | 7 |
| GA OF GEARED COUPLING.pdf | 2 |
| BRG SELECTION & SHELL & DIAPHRAGM THICKNESS CALCULATION FOR CONVEYOR PULLEYS.pdf | 3, 4 |
| GA OF BRAKE FOR CHP CONVEYORS.pdf | 3 |
| P & ID FOR DFDS SYSTEM.pdf | 1 |
| Piping Layout for DFDS, SW & PW System at UEF-1.pdf | 1, 2, 3 |
| OPERATION & CONTROL PHILOSOPHY OF DFDS SYSTEM.pdf | 2, 3, 4, 5 |
| GA OF FAS PRU FOR DFDS SYSTEM.pdf | 2, 3 |
| GA OF SPRAY HEADER FOR DFDS SYSTEM.pdf | 1, 2 |
| GA - DATA SHEET OF NOZZLES FOR DFDS SYSTEM.pdf | 2 |
| P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf | 1 |
| GA & Data Sheet of Sump Pump.pdf | 15, 16 |
| Control Write up for Coal Handling System.pdf | 9, 26, 27, 28, 29, 34, 38 |

Other scoop sizes, unrelated conveyor columns and the five-outlet screening header were not applied to this pilot. The standard nozzle schedule's whole-system quantities were not used as UEF-1 counts. The specific 530 PST / B3-450 / RG-10 applicability and the four-/nine-outlet header correspondence were used instead.

## Unresolved points retained in the model

| Topic | What remains to resolve |
|---|---|
| Motor and supply data | GA and schedule supply tolerances differ; brake design lists 350 kW against the GA/schedule's 315 kW. Requires applicable final motor/nameplate and design records. |
| Counterweight | 994 × 17.5 kg = 17,395 kg, while GA design weight is 17,400 kg. Both printed basis and arithmetic are retained. |
| Oil-filter naming | GA supply-list wording and P&I distinguish 20-mesh suction strainer and 40-mesh Y-filter differently. Identify the installed component before treating these as interchangeable. |
| Chute blockage logic | Control write-up prints “CBS not operated” in both permissive and trip lists. Polarity/action remains unresolved. |
| 1B scoop permissive | The path table refers to 1A's main motor for the 1B actuator. This copy inconsistency is preserved. |
| Differential-pressure action | One source gives an alarm value; the write-up also says “trip the motor” without a clear motor identity. No invented trip target was created. |
| Brake feedback | Vendor drawing's engaged indication and control requirement for released feedback need reconciliation. |
| DFDS pressure-switch tags | UEF-1 inset contains PS-01 and PS-02 wording; control philosophy uses PS-02. The inset PS-01 was not merged with the pump-house identity. |
| Structural/mechanical TP drawing | Historical pilot finding: referenced UEF-1 GA175033 was not identified then. **Review update20 September2026:** the imported `GA & MECH LOAD OF TP-1.pdf` is this source (GA p1, review p2). See F02 in the whole-plant handoff. The stale canonical missing-source assertion still requires reviewed correction; finding the drawing does not establish access certification or installed acceptance. |
| Installed field detail | Individual switch/nozzle/valve tags, calibration records, cable/terminal references, serial numbers, actual settings, full electrical feed/loop records and commissioning results remain incomplete. |
| Maintenance | Service intervals, wear/replacement limits, overhaul tolerances and actual inspection/repair history are not established by these design drawings. |

This completes a substantive, source-backed pilot baseline. It does not certify all installed plant details or replace final commissioned records. Further extraction can add information as additional applicable records are found.

## Validation and audit trail

- 76 Python tests passed; 17 plant-explorer JavaScript tests passed; changed JavaScript passed syntax checks.
- Integrity verification passed at v484: 266 documents, 5,196 evidence blocks, no errors.
- Data audit confirmed every new assertion has evidence and a locator; exact quotes match immutable evidence; original assertion IDs remain; numeric pair/nozzle counts and representative drive values reconcile; uncertainty records remain inferred; network assertions retain documented metadata.
- Rehearsed all 18 batches in an isolated SQLite copy before accepting them. No existing assertion was retired or overwritten. Validator warnings concerned new ontology concepts and explicitly inferred review findings/derived counts; they were reviewed, with no validation errors.
- Browser checks cover assembly search, individual quantity evidence, readable drawing detail, claim basis, deep component navigation and transfer-point browsing.

Artifacts:

- [Accepted batch log](output/equipment-pilot/accepted/commits.jsonl), individual accepted JSON envelopes in the same folder.
- [Pilot audit](output/equipment-pilot/accepted/audit.json) and [source manifest](output/equipment-pilot/accepted/source-manifest.json).
- [Version-466 database backup](output/equipment-pilot/backup-v466.sqlite3). It relies on the unchanged local originals/renders folders; it is not a self-contained portable backup.
- [Reviewed pilot builder](tools/enrich_conveyor_tp1_pilot.py). Version-guarded migration record; it intentionally refuses replay against v484.
- [Generalized agent prompt](EQUIPMENT_ENRICHMENT_AGENT_PROMPT.md).

The next useful bounded expansion is EAC-2A/B and the primary screen-house interfaces, followed by the connected transfer points. Reuse the extraction method and schema, but establish every equipment-specific value and application relation from its own sources.
