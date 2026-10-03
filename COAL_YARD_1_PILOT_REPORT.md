# Coal Yard 1 equipment dossier

This pilot organizes the EAE-1 yard into a navigable equipment and system hierarchy, using targeted reviews of the original drawings and control documents. It is source-backed design knowledge. It does not establish installed configuration, commissioned settings, current machine state or live coal inventory.

## Open and use it

[Coal Yard 1 overview](http://127.0.0.1:8765/#overview?equipment=ent_e7f3c29cc0b842269ada&area=stockyard&tab=overview) · [Equipment tree](http://127.0.0.1:8765/#overview?equipment=ent_e7f3c29cc0b842269ada&area=stockyard&tab=structure) · [Search all assembly facts](http://127.0.0.1:8765/#overview?equipment=ent_e7f3c29cc0b842269ada&area=stockyard&tab=assembly)

The Stockyard page has a direct Coal Yard 1 entry. Its equipment-flow diagram follows EAC-7 → EAD-1 → EAE-1 → EAF-1 → EBA-8. Select a machine, open Structure & auxiliaries, and drill into its component. Every new value and relationship has a source button. The evidence dialog retains the equipment context and offers the original PDF page.

Use Assembly facts to find `PCS`, `scoop`, `oil`, `nozzle`, `SP-8G`, `permissive` or `lubrication`. The gaps/disagreements filter gathers qualifications from throughout the assembly. Services & boundary connections exposes common pumps, tank dependencies, external controls and downstream connections without adding those assets to Yard 1 ownership.

## Coverage

| Target | Implemented detail | Remaining qualification |
|---|---|---|
| Yard boundary and stockpile | EAC-7, EAD-1, EAE-1, EAF-1, EBA-8, UEB-1, UAX-1 and UAX-5; route and transfer-point boundaries; design pile dimensions | Descriptive functional grouping, not surveyed geometry or live stock. Shed structural details and usable stock capacity need further sources. |
| EAC-7 and EBA-8 | Motor → scoop coupling → gearbox → output coupling → head pulley; brake, belt, take-up, rope/sheaves, counterweight, idlers, scrapers, BSS/PCS/ZSS; EBA-8 weigher | PCS quantities retain the unqualified source number; no invented individual switch total. |
| Coupling auxiliaries | Oil pump and motor, radiator and fan motor, filter, actuator/motor, switches/gauges, sight glass, junction box, oil specification/fill basis | EBA-8 GA selects PST-530 but scoop vendor GA assigns 500 PST. Auxiliary details retain this unresolved applicability. |
| Conveyor control | General HT sequence, motor temperature requirements, brake/oil-pump requirements, PCS/BSS/ZSS actions; EAD-1/EAC-7 engagement and FG-10/EBA-15A/B reclaim conditions | Design control requirements; CBS polarity ambiguity retained. No claim of final PLC implementation. |
| EAD-1 stacker | Boom drives, slew system, hydraulic power pack/pump/motors/filters/instruments, luffing assembly/cylinder, travel drives/wheels, tripper, cabin, boom belt scale | Project-family design mapped through the plant flow identity. Detailed travel/collision/limit and storm-parking records remain open. |
| EAF-1 portal reclaimer | Main/auxiliary scraper booms, drive motors/gearboxes, chains/blades/take-up, hoist drive/brakes/rope, travel wheels/drives/clamps/buffers, cable reels | Wind-unit, travel-speed and auxiliary-capacity source disagreements retained. This is a scraper reclaimer, not a bucket-wheel machine. |
| Yard SPDS | Ring header, 28 AP risers with sprinkler/isolation/globe valves, sprinkler datasheet at each point, 14 sectors and 28 tagged solenoid valves; SC-01 sequence | Physical APs and control SVs are separate groups until an explicit cross-reference establishes their mapping. |
| Shared SPDS | Common pumps and motor selection, tank level/inlet controls, pressure/filter interlocks, machine makeup QRCs | Common service remains separate. Control-text pump 2A/B and design 1A/B identities are not silently merged or counted as four installed pumps. |
| Onboard dust suppression | Stacker tripper/boom receipt/boom discharge application points, 34 nozzles, tank/pump/filter controls; reclaimer tank, pump, reel, six nozzles and conveyor-load/level controls | Stacker coal plain-water section only. Tentative motor selections and filter wording disagreements retained. |
| Lubrication | Stacker's three pump systems; reclaimer central grease and chain-oil systems, reservoirs, motors, valves, metering/nozzle equipment | First-fill values are not maintenance intervals. Machine GA and vendor motor selections differ. |
| Machine fire protection | EAD-1 FMZ5000 panel, electrical-house and cabin zones, cylinder groups, nozzles, detectors and release devices | BOM cylinder quantities do not establish duty/reserve allocation or simultaneous release. Not evidence of yard-wide fire coverage. |
| Runoff | Stockpile 1 / UEF-7 sump, SP-8G/H, level controls, local panel and connection to common runoff pond | Shared pit and common downstream facilities; local duty assignment and switch levels remain unverified. |

## Review priorities retained in the model

- **EBA-8 coupling:** reconcile conveyor PST-530 against the vendor's 500 PST assignment before applying the vendor auxiliaries to installed equipment.
- **Conveyor PCS:** 30 for EAC-7 and 31 for EBA-8 have no explicit quantity unit in the GA. BSS is explicitly 18/17 pairs; the corresponding 36/34 device counts are separately marked as arithmetic.
- **Reclaimer wind:** GA prints km/h, whereas the BOD prints m/s. These values are not promoted to safe operating or trip settings.
- **SPDS:** reconcile 124 versus 115 mwc pump head, pump naming, controller cycle wording versus arithmetic, and AP-to-SV mapping.
- **Motor selections:** reconcile reclaimer lubrication and onboard DSS selections across machine GA and vendor records.
- **Fire protection:** reconcile the schematic's cylinder notation, BOM quantities and final protected enclosure dimensions; obtain the final cause-and-effect and commissioning record.

Other gaps include individual field loop/serial numbers, calibrated setpoints, coal lot/age/temperature history, stockpile fire-water coverage, rail/anchor inspection information and approved maintenance intervals. Missing information in this pilot does not establish that a system is absent.

## Accepted data and reproducibility

Baseline **v484** → **v510**, through **26 reviewed batches**. The migration creates **404 entity records**, with one subsequently merged into the existing boom weigher identity (**403 net new canonical identities**), and **1,844 assertions**; assertion counts include classifications, component membership, connections, specifications and review qualifications. The Yard 1 assembly has **413 reachable records including its root**, reusing existing main equipment identities. This is not a count of individually tagged installed assets.

The new claims use **42 PDF pages from 18 documents**. There are **31 explicit gap/disagreement assertions**. Prior assertions are retained, as are the immutable originals and evidence. Shared-system facts can lie outside the local yard tree while remaining reachable through service links.

- Builder: `tools/enrich_yard1_pilot.py`; guarded migration from v484. Do not replay on the enriched model.
- Read-only semantic audit: `tools/audit_yard1_pilot.py`.
- Baseline backup: `output/yard1-pilot/backup-v484.sqlite3`.
- Final rehearsal: `output/yard1-pilot/rehearsal-final/`.
- Accepted proposals, version log and model: `output/yard1-pilot/accepted/`.
- Source IDs, immutable hashes and pages used: `output/yard1-pilot/source-manifest.json`.
- Updated continuation instructions: `EQUIPMENT_ENRICHMENT_AGENT_PROMPT.md`.

## Source coverage

Page numbers below are PDF page numbers. The full document inventory in an intake envelope is not a claim of exhaustive semantic review of every page.

| Original document | Pages used |
|---|---|
| Control Write up for Coal Handling System | 9, 26–29, 43, 46, 51, 55 |
| GA & LOAD DATA OF BELT CONVEYOR-7 | 5 |
| GA & LOAD DATA OF BELT CONVEYOR-8 | 5 |
| GA OF SCOOP TYPE FLUID COUPLING FOR CHP CONVEYORS | 1, 4 |
| Basis of Design for Coal Stacker Machine | 2, 3 |
| GA & TDS of Portal Type Scraper Reclaimer Machine | 3 |
| Basis of Design for Portal Reclaimer | 5, 6 |
| GA of Hydraulic Power Pack & Hydraulic Cylinder for Slew Drive and Luffing for Coal Stacker Machine | 2, 7 |
| DESIGN BASIS REPORT FOR PLAIN WATER DS SYSTEM FOR STOCKPILE FOR CHP | 2, 3 |
| OPERATION & CONTROL PHILOSOPHY FOR CHP STOCKPILE DS SYSTEM AND SW-PW PUMPING SYSTEM | 3, 4, 8, 10 |
| P & ID FOR PLAIN WATER DS SYSTEM FOR STOCKPILE FOR CHP | 1 |
| GA & DATA SHEET OF SPRINKLERS FOR PLAIN WATER DUST SUPPRESSION | 2 |
| DBR for Machine mounted DS system for Stacker Machine | 8, 21–23 |
| DBR for Machine mounted DS system for Portal Type Scraper Reclaimer Machine | 3–5 |
| GA, TDS & P&ID of Motorized Central lubrication system for Portal Type Scraper Reclaimer Machine | 4, 10 |
| GA, TDS & P&ID of Motorized Central lubrication system for Stacker Machine | 1 |
| Fire detection and extinguishon system of Stacker | 2, 5, 6 |
| P & ID FOR SUMP PUMP & STOCK YARD RUNOFF WATER PUMP SYSTEM | 1 |

Additional pages used as visual context included conveyor arrangement sheets, stockpile piping layout, stacker GA, hydraulic write-up/GA and fire layout/schematic sheets. They were not used to infer surveyed coordinates or undocumented component settings. The coal-stockpile-management document for Tanjung Jati B was excluded from Maitree operational requirements. Machine anchoring detail and the reclaimer safety-instrument drawing referenced by its GA remain follow-up review items.

## Verification

The final rehearsal passed versioned ingestion validation and a semantic audit of provenance, retained prior claims, local containment, shared-service boundaries, sprinkler/sector quantities, sump assignment, BSS arithmetic and retained source disagreements. Application regression checks passed: 76 Python tests and 18 JavaScript tests. The accepted-model semantic audit also passes, preserving all 9,132 prior assertions. Browser checks confirm the Yard 1 entry, scoped route, local SPDS hierarchy, 28-sprinkler count source and AP-28 individual datasheet source; original links retain their PDF page anchors and both cropped/full-page images load. The deep EAC-7 oil-pump motor source and EBA-8 competing coupling models also pass browser checks. Live integrity verification passes for all 266 documents, 5,196 evidence blocks and 510 versions; see `accepted/integrity.json`, `accepted/audit.json` and `accepted/browser-checks.json` under the output folder.

The next bounded enrichment should close Yard 1's machine safety/anchoring and SPDS identity/mapping gaps, then apply the same process to Yard 2 using its own source applicability and local P&ID branch.
