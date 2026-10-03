# Coal Yard 1

Planning card at model v628. Package **P05** — Coal Yard 1: preserve and close pilot gaps. Primary implementation batch **B16**; later service/integration batches also review its boundaries.

Read [section plan](../SECTION_PLANS.md#p05) and [family contract](../ASSEMBLY_CONTRACTS.md#yard) before editing. This card inventories accepted records; it does not certify their correctness or completeness.

- Canonical ID: `ent_e7f3c29cc0b842269ada`.
- Existing containment closure: 413 record(s) including root; 8 assertions on root. These are model records, not a count of physical devices.
- Aliases: Coal Yard 1
- Existing parents: Coal Stockpile Yard
- Direct components: EAC-7, EAD-1, EAE-1, EAF-1, EBA-8, UEB-1, UAX-1, UAX-5, Coal Yard 1 SPDS, Coal Yard 1 Runoff collection
- Located equipment: none recorded

## Source work

Start with these exact dedicated-source candidates; inspect originals, review replies and sheet continuations before using a value:

- No dedicated title match supplied by this card; use the section source list and family groups. This is not a corpus-wide negative search.

Common source groups: **yard, stacker, reclaimer** plus **topology** in [source catalog](../SOURCE_CATALOG.md). Exact evidence IDs by page and original hashes are in [sources.json](../inventory/sources.json).

Existing assembly citations (claims still require original-source review):

- `doc_78bebe6773984d59b013` — Basis of Design for Coal Stacker Machine.pdf, PDF pp. 2–3.
- `doc_498f70490d294542b8b0` — Basis of Design for Portal Reclaimer.pdf, PDF pp. 5–6.
- `doc_9c169bf7536b4ebca236` — COAL FLOW DIAGRAM.pdf, PDF pp. 1.
- `doc_0ed3cc8247ed4484ac8f` — COASTING TIME CALCULATION.pdf, PDF pp. 2–3.
- `doc_9ea3e0c55ca347ae96a2` — CONV. PROFILE FOR ALL CONV..pdf, PDF pp. 2.
- `doc_4f2cd96c3b1e413ea4b5` — Control Write up for Coal Handling System.pdf, PDF pp. 5, 7, 9, 26–29, 36, 42–43, 46, 51, 55–56.
- `doc_a6a2fa82944f4d12b8aa` — DBR for Machine mounted DS system for Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 3–5.
- `doc_0f52c77514a74773ae30` — DBR for Machine mounted DS system for Stacker Machine.pdf, PDF pp. 8, 21–23.
- `doc_777d1a06d4fa4e8ba231` — DESIGN BASIS REPORT FOR PLAIN WATER DS SYSTEM FOR STOCKPILE FOR CHP.pdf, PDF pp. 3.
- `doc_4d488fd685284c408297` — Fire detection and extinguishon system of Stacker.pdf, PDF pp. 2, 5–6.
- `doc_4b620e0e7bca45e3af10` — GA & DATA SHEET OF SPRINKLERS FOR PLAIN WATER DUST SUPPRESSION.pdf, PDF pp. 2.
- `doc_2664b59a573b467eb166` — GA & LOAD DATA OF BELT CONVEYOR-7.pdf, PDF pp. 5, 8–10.
- `doc_75a88e7148014a83aefd` — GA & LOAD DATA OF BELT CONVEYOR-8.pdf, PDF pp. 5.
- `doc_fb155ee4604c4209a7a0` — GA & MECH LOAD DATA OF DH-1,2,3,4.pdf, PDF pp. 1, 5.
- `doc_9079e1e97bcb45ad8e79` — GA & MECH LOAD DATA OF TPH-1,2,3,4.pdf, PDF pp. 1, 5.
- `doc_3e81ea1c32df4215968d` — GA & TDS of Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 3.
- `doc_42554b5718fc423997b3` — GA , TDS & P&ID of Motorized Central lubrication system for Portal Type Scraper Reclaimer Machine.pdf, PDF pp. 4, 10.
- `doc_b7d031cc33c54157ad86` — GA , TDS & P&ID of Motorized Central lubrication system for Stacker Machine.pdf, PDF pp. 1.
- `doc_7aa49cc0d1c34af7ac06` — GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS.pdf, PDF pp. 1, 4.
- `doc_9f1d51138e104d5a905e` — GA of Hydraulic Power Pack & Hydraulic Cylinder for Slew Drive and Luffing for Coal Stacker Machine.pdf, PDF pp. 2, 7.
- `doc_e17edf6897d746fabe12` — OPERATION & CONTROL PHILOSOPHY FOR CHP STOCKPILE DS SYSTEM AND SW-PW PUMPING SYSTEM.pdf, PDF pp. 3–4.
- `doc_5a36f2843d504d6e96de` — P & ID FOR PLAIN WATER DS SYSTEM FOR STOCKPILE FOR CHP.pdf, PDF pp. 1.
- `doc_0453a0a014424f1cae06` — P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM.pdf, PDF pp. 1.

Existing explicitly applicable reference identities: none.

## Existing material interfaces

These include the owned assembly and equipment explicitly located here. Located equipment retains its actual owner; showing its routes does not add containment.

| From | To | Source condition | Assertion |
|---|---|---|---|
| UEF-6 | EAC-7 | No condition recorded; review source | `fact_ca5b4f1089c349e2925f` |
| EAC-7 | UAX-1 | No condition recorded; review source | `fact_c4a0505949f74ccfb540` |
| UAX-5 | EBA-8 | No condition recorded; review source | `fact_0f1bb930b8ad415a81d9` |
| EBA-8 | UEF-11 | No condition recorded; review source | `fact_28e2e07361f3458c877b` |
| KB-FD-7 | EAC-7 | Full or partial stacking | `fact_be9779fbfd0b4ae28170` |
| KB-FD-8 | EAC-7 | Full or partial stacking | `fact_b24fb658dbb44b3b9664` |
| EAC-7 | EAD-1 | No condition recorded; review source | `fact_f202b03c0f5740ceb2df` |
| EAD-1 | EAE-1 | Uncrushed coal stacking on one side of machine | `fact_2bffa6cbdf2349f09c80` |
| EAE-1 | EAF-1 | Selected pile reclaiming | `fact_4878544d9bc54b96a73f` |
| EAF-1 | EBA-8 | No condition recorded; review source | `fact_2d1db428261446b78d76` |
| EBA-8 | FG-10 | No condition recorded; review source | `fact_5cd3fff5d2b24a0abf89` |
| EAC-7 | EAD-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_145fcc205d5c4c4eae55` |
| EAD-1 | EAE-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_239c3944a41f4c95b147` |
| EAE-1 | EAF-1 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_5ee5189b6c77464e8d3e` |
| EAF-1 | EBA-8 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_b8fe8e423a5c4cdebdc6` |
| EBA-8 | UEF-11 | Coal-flow diagram Yard 1 branch; no live route or current operating state implied. | `fact_c8d46fce0758442aa99e` |

All network boundaries, scene connections and exact supports are indexed in [targets.json](../inventory/targets.json) and [connections.json](../inventory/connections.json). Parallel statements are retained; do not count them as separate physical pipes or routes.

## Required closure

- Work through every dimension in the family contract. Finish with reviewed evidence, not-applicable evidence, or a specific unresolved gap for each dimension.
- Reuse existing components and locally named but unplaced records from the review queue. Check both aliases and source BOM/model applicability before adding identities.
- Keep equipment ownership, place, flow and shared services separate. A root with no location assertion can still have source-backed endpoints; a conveyor spans several places.
- Demonstrate plant → area → this target → drive/auxiliary → one individual fact → readable source → return, and verify one boundary into the neighbouring package.
- Preserve disagreements; do not substitute a family, calculation, or previous pilot value as an installed value.

Recorded gaps/disagreements in this assembly or applicable references:

- `fact_0e395e3be9ab4f528613` (Coal Yard 1): No live stock inventory, coal lot/age/temperature history, commissioned settings, field asset serial numbers or approved maintenance intervals are established by this drawing-based pilot.
- `fact_bdc4fc534ed8476e91f9` (EAC-7 Belt protection devices Pull-cord switches (PCS)): PCS total needs reconciliation of both-side symbols, schedule and quantity unit. No multiplication into an installed switch count has been made.
- `fact_6b23e33b951e43a1ba29` (EAC-7): Field sensor loop IDs, brake setting and final equipment-specific control settings require confirmation. Coupling oil details are recorded separately from the vendor design, with model applicability qualifications.
- `fact_75055f2203154fda954a` (EBA-8 Belt protection devices Pull-cord switches (PCS)): PCS total needs reconciliation of both-side symbols, schedule and quantity unit. No multiplication into an installed switch count has been made.
- `fact_a95eb9ff543044cfa77c` (EBA-8): Field sensor loop IDs, brake setting and final equipment-specific control settings require confirmation. Coupling oil details are recorded separately from the vendor design, with model applicability qualifications.
- `fact_76eb1177b181487384e1` (EAC-7 Drive assembly Scoop coupling): Instrument drawing symbols do not establish plant loop IDs. Alarm/trip thresholds, controller wiring and actual oil fill require applicable final records.
- `fact_044f267008454763aacc` (EBA-8 Drive assembly Scoop coupling): Conveyor GA sheet 5 selects PST-530; vendor scoop GA sheet 1 explicitly assigns EBA-8 to 500 PST. The auxiliaries below describe that vendor selection. Final installed model and component applicability remain unresolved.
- `fact_1c378fb544124fa888c9` (EBA-8 Drive assembly Scoop coupling): Instrument drawing symbols do not establish plant loop IDs. Alarm/trip thresholds, controller wiring and actual oil fill require applicable final records.
- `fact_a794efbd44a9400a8262` (EAD-1): BOD calls handled material crushed coal; yard conveyor GA and plant flow identify the pre-crushing stockyard stream. Preserve the BOD wording, without changing the documented plant route.
- `fact_01cdf7141e02427b8519` (EAD-1): Machine PLC cause/effect, collision and travel-limit loops, storm-parking procedure and field tag assignment require separate verification. Structural wind limits are not automatic trip thresholds.
- `fact_0334e15d95fc49748d4f` (EAF-1): Safety-instrument GA 179103 is referenced here; exact travel/collision/hoist interlock loops and wind trip settings still need verification. Do not infer the installed settings from structural design limits.
- `fact_e666ba65ec8149399451` (EAF-1): GA wind rows print 16 km/h operating and 73 km/h non-operating. Reclaimer BOD page 6 prints 16, 35 and 73 m/s. Units conflict; no authoritative trip or safe operating threshold is inferred.
- `fact_f7c5d1aafb184613b175` (EAF-1 Travel system): BOD travel row shows 2 m/min and a separate 5 m/min entry without a clear range; GA page 3 states operating 2 to 8 m/min. Retained as competing design information.
- `fact_f89c6ce6e6ed44f3b33e` (EAF-1 Auxiliary scraper boom): BOD gives 500-650 t/h depending on boom inclination; GA page 3 gives 500-660 t/h. Final applicable rating remains to be reconciled.
- `fact_aeeab1bec5db4d63a0e5` (Stockpile Sequential Controller SC-01): Controller KKS is printed with 00EAE001; field/IO confirmation is needed before treating a normalized tag as an alias.
- `fact_2e8ea97c8df14399a58f` (Stockpile Sequential Controller SC-01): Source calls one cycle 33 minutes but its expression 2 min x 14 + 20 s x 13 equals 32 min 20 s. Timing remains source-qualified; no PLC adjustment inferred.
- `fact_12d7128509694356bb4b` (Coal Yard 1 SPDS): AP and SV ranges/pairs are documented, but a unique AP-to-SV cross-reference and surveyed coordinates are not established here. APs and SVs remain separately navigable groups.
- `fact_8877484be657490e8a46` (Coal Yard 1 SPDS): This P&ID schedule gives pump head 124 mwc while its major BOM gives 115 mwc. DBR gives 124 mwc; final pump selection must be reconciled.
- `fact_f18866e7c2c249038a0e` (EAD-1 Onboard plain-water DSS): Component list specifies duplex filter; alarm text says simplex filter choked. Preserve both; actual filter arrangement needs reconciliation.
- `fact_ebbdf3e8f47746caa601` (EAF-1 Onboard plain-water DSS): Machine GA lists approximate DSS power 2.2 kW; this later BOD lists tentative 0.55 kW pump motor. A final vendor/nameplate check is required before assigning installed motor power.
- `fact_a8aa20262c3f4e559dee` (EAF-1 Central grease lubrication): Machine GA shows 0.37 kW lubrication motors; later Lincoln grease pump datasheet gives 0.55 kW. Source-specific values are retained pending final configuration confirmation.
- `fact_bba874b9e1fd4585b9cb` (EAD-1 Central grease lubrication): Drawing first-fill quantities do not establish routine regreasing quantity or interval. Pump labels are descriptive; installed tags and controller timings need verification.
- `fact_de7a5ead4cfe43dba691` (EAD-1 Fire detection and clean-agent system Z101 Protected zone): BOM shows two cylinders per zone, while schematic charge notation states one cylinder. Do not infer duty/reserve allocation or discharge quantity without the final release cause-and-effect.
- `fact_19e444d40db6441dbae2` (EAD-1 Fire detection and clean-agent system Z201 Protected zone): BOM shows two cylinders per zone, while schematic charge notation states one cylinder. Do not infer duty/reserve allocation or discharge quantity without the final release cause-and-effect.
- `fact_1d8e5c76e74045a7a24a` (EAD-1 Operator cabin): Machine BOD cabin dimensions are 2.4 x 1.9 x 2.4 m; fire design uses 2.4 x 1.9 x 2.5 m. Protected-volume design and final enclosure dimensions require reconciliation.
- `fact_ce90b808e9694b8ea123` (EAD-1 Fire detection and clean-agent system): Final release logic, commissioned delay, isolations and inspected cylinder status are not established. This machine system does not establish stockpile fire hydrant, monitor or coal-temperature coverage.
- `fact_9533fcf064ea4e158082` (Coal Yard 1): Stockpile fire-water coverage, coal-temperature/age monitoring, shed structural inspection details, rail alignment/anchoring records and approved maintenance intervals remain open. Absence from this pilot is not evidence that those systems are absent.
- `fact_810f2ec6a0534a37b46e` (EAC-7 Drive assembly Scoop coupling Scoop actuator): General CBS permissive and trip wording both say not operated, leaving trip polarity unresolved. Succeeding-conveyor/scoop conditions also require application review; no executable Boolean logic is inferred.
- `fact_c0ad9baf77444b18aeeb` (EBA-8 Drive assembly Scoop coupling Scoop actuator): General CBS permissive and trip wording both say not operated, leaving trip polarity unresolved. Succeeding-conveyor/scoop conditions also require application review; no executable Boolean logic is inferred.
