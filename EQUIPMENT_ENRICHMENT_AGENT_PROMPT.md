# Equipment enrichment — reusable agent prompt

Copy the prompt below into an agent with access to the plant application and original document corpus. Replace the target list. The repository adapter at the end applies to CHP Knowledge Builder; adapt only that section for another application.

For continuation of this Maitree plant, start with [the current continuation guide](docs/plant-handoff/CONTINUATION_GUIDE.md) and [ready-to-paste prompt](docs/plant-handoff/READY_TO_PASTE_PROMPT.md), reviewed 1 October 2026 at live v558. The [whole-plant implementation handoff](PLANT_MODEL_IMPLEMENTATION_HANDOFF.md) supplies architecture, section plans, findings and ordered batches. Its target/source inventories are the historical v510 snapshot, not current completion status. This document remains the generalized extraction method.

---

## Assignment

Enrich the plant model for **[TARGET EQUIPMENT / AREA LIST]** into a coherent visual equipment assembly for daily operations and maintenance, with detailed facts and evidence available on selection. Start with a bounded group of connected equipment and finish it before expanding the scope. Use the EAC-1A/B, UEF-1, Coal Yard 1, blending-silo and crusher-house pilots as patterns for depth and provenance, not as templates of facts to copy to other machines.

Implement the enrichment in the existing application and its canonical model. Deliver the working result, a source/coverage report, unresolved questions, and verification results. Do not stop at suggestions, a flattened fact dump, a mockup, or pending extraction if the user's authorization includes applying reviewed changes. Preserve unrelated work. Do not commit Git, publish externally, or create other agents/tasks unless that is authorized.

The intended user should be able to start at a plant route, area, or equipment tag and answer:

1. What is this equipment, what does it do, and where is it physically located?
2. What is upstream and downstream, including documented alternative routes and their conditions?
3. What assemblies, auxiliaries and components belong to it, and which shared services support it?
4. What drives it, supplies it, monitors it and protects it?
5. What are its design/rated capacities, operating ranges, mechanical specifications and lubricant requirements?
6. What are the source-stated start permissives, sequence, alarms, trips, delays and resulting actions?
7. What can maintenance identify from the corpus: make/model, component selection, access, lubrication, replaceable parts, inspection requirements and previous work?
8. Where did **each individual claim** come from, and what remains unknown or disputed?

## 1. Establish scope and inspect the current model

- Read the active repository guidance and current ingestion/model contracts. Inspect the actual accepted model, source inventory, latest relevant changes, current UI and outstanding work before editing.
- Record the baseline model version, target canonical IDs, aliases, existing components, relationships and relevant assertions. Reuse identities wherever they already exist. Document numbers and drawing titles are source identities, not physical equipment.
- Resolve the requested names against actual plant tags. A designation such as TP-1 may correspond to UEF-1, but establish that mapping from the plant context. Do not assume every UEF is the same type of building.
- Preserve a consistent backup and keep a version guard. If the model changes during your work, reconcile against the new state rather than replaying a stale patch.
- Write a coverage matrix with one row per target and columns for purpose, location, coal flow, mechanical assembly, utilities, controls/protections, ratings, maintenance and provenance. Each cell must end as extracted, already adequate, partially supported, contradictory, illegible, or source not found.

## 2. Investigate the original corpus by engineering relationships

Do not merely search the equipment tag and collect nearby text. Search tags, aliases, drawing references, component models, equipment families, sheet continuations, vendor schedules, BOMs and connected equipment. Follow each discovered relationship into its supporting document.

Look for flow diagrams, equipment GAs, drive schedules, motor data, coupling and gearbox drawings, brake data, pulley/bearing calculations, electrical/IO/loop schedules, control write-ups, utility P&IDs, piping layouts, vendor manuals, revision replies, inspection records and maintenance history. Record negative searches and missing referenced drawings.

For every candidate source, record original document ID/hash, filename, drawing number, revision, date/approval wording, applicable tags/models, relevant PDF pages and printed sheet numbers. Read the header, row/column labels, units, notes and continuation context. Visually inspect readable original-page crops for dense drawings. OCR and extracted text are retrieval aids; do not treat them as proof of a visually ambiguous value or connection.

Keep a disposition for each candidate: used, corroborating, superseded with evidence, not applicable, ambiguous, unreadable, or deferred with a reason. State the pages actually examined. A document-wide evidence inventory required by an API is not a claim that every dimension was semantically reviewed.

## 3. Build the equipment tree and separate relationship networks

Model the target as a real assembly, with descriptive component names when individual field tags are unknown. Explicitly label those names as descriptive; never invent KKS, cable, switch or spare-part tags.

Use different relations for:

| Meaning | Example |
|---|---|
| Component membership | Oil-pump motor → part of → oil circulation pump |
| Physical location | Conveyor head-end drive → located at → transfer point |
| Mechanical transmission | Main motor → scoop coupling → gearbox → geared coupling → head pulley |
| Material flow | Discharge interface → receiving interface → next conveyor |
| Utility supply | Local air/water main → FAS → PRU → header → nozzle group |
| Measurement | Under-belt switch → monitors → conveyor load condition |
| Protection/control | PCS signal → documented action on scoop actuator, with conditions |
| Shared service | Pump house system → serves → local DFDS equipment |
| Design applicability | A specific calculation column → applies to → this pulley design |

Ownership is not location; location is not coal flow; monitoring is not automatically an interlock. Keep material, mechanical, electrical, control and utility connections separate. The subject of a directed connection must be the supplying/driving/upstream item and the object the receiving/driven/downstream item. Establish direction, endpoints, conditions and port references from the source. Never infer a connection from proximity, crossing lines, similar names or a generic engineering expectation.

Shared utility equipment should remain one canonical identity with service/location links. A transfer-point page must expose equipment located there even when it belongs to a conveyor. Do not duplicate a conveyor's drive under the transfer point just to make it visible.

Use component groups when the drawing gives only group quantities. For example, store “14 pairs” as the original quantity and “28 switches” as a separate derived count with the formula. Do not manufacture 28 independently tagged switch records. Keep per-equipment, per-set, per-pair, whole-project, spare and scheduled-operating quantities distinct.

## 4. Equipment-specific investigation checklists

These are search checklists, not assertions that the equipment exists. Record source-supported components; leave unresolved items as gaps.

**Conveyors:** receiving/discharge interfaces, main motor, starter/feeder if documented, fluid/scoop coupling and actuator, oil sump/pump/motor, cooler/fan, filters/strainers, temperature/pressure/differential-pressure/flow devices, gearbox/holdback/lubrication, high/low-speed couplings, brake drum/thruster/feedback, pulleys/shaft/bearings, belt construction/covers, idler groups, take-up/rope/sheaves/counterweights, scrapers, skirt/chute liners, guards and access. Search PCS, BSS, ZSS, CBS, emergency/local stop, winding/bearing protection, belt tear and other devices without assuming generic protections are installed on every conveyor.

**Transfer points:** incoming/outgoing interfaces and branch conditions, floor/elevation datums, chute arrangement and liners, gates/diverters, local conveyor drive locations, DFDS or extraction application zones, nozzles/headers, FAS/PRU and internal components, load/pressure permissives, local panels, drainage/sump pumps, washing/potable water, lifting and access provisions. Keep receiving and discharge spray zones distinct and reconcile all counts.

**Yards:** stockpile identities and usable/design capacity, routes and gates, stacking/reclaiming paths, machine/travel boundaries, stockpile equipment, drains/sumps, water/dust systems, fire/detection references and access. Do not convert a capacity or schematic into surveyed geometry or a live inventory.

For a yard, create one navigable functional-area entry with its own coal-flow overview. Keep the local SPDS branch, onboard machine dust suppression and shared pumping/tank supplies distinct. Reconcile physical application points, controller sectors, valve tags and KKS independently: a matching numeric suffix alone does not establish an AP-to-SV mapping. Assign each sump pump from the actual local P&ID branch, not alphabetical order in a project schedule. Distinguish local quantities from four-yard totals. Trace shared dependencies across the local assembly without claiming ownership of the common system.

Machine design data may apply to a project family; preserve that qualification on every inherited component fact. A drawing filename or KKS-like document prefix cannot override the equipment identity in the coal-flow diagram. Verify the actual machine type: for example, a portal scraper reclaimer should be decomposed into scraper booms, chains, take-up, hoist and travel assemblies, not an assumed bucket wheel. Separate structural wind design cases from wind alarm/trip settings. Keep different pump or coupling selections across documents visible until a final configuration record resolves them.

**Stackers and reclaimers:** machine → travel/slew/luff/boom/bucket-wheel assemblies → drives/brakes/couplings → lubrication/hydraulics → cylinders/pumps/valves/instruments; cable reel and electrical feeds, belt routes, limits, overload/wind/travel protections, parked/storm arrangements and documented machine-mode interlocks.

**Silos and bins:** vessel, receiving/discharge interfaces, feeders/extractors, flow aids, gates, level/temperature/pressure instruments, dust collection, ventilation, fire/inerting provisions if documented, access, structural/design capacity and operating volume bases. Separate geometric, bulk-density-based, usable and rated capacities.

**Crushers/screens:** feed and bypass routes, crusher/screen machine, rotor/shaft/hammer or screen-deck assembly, bearings/lubrication, drive train/brake if fitted, vibration/speed/temperature monitoring, hydraulic/access mechanisms, local utilities, wear parts, sizing/capacity basis and interlocks with upstream/downstream equipment.

## 5. Represent every fact with its evidence and basis

Each scalar and relationship must carry source evidence, applicability, original value/unit, and context. Store numeric values as numbers. Keep design/rated/calculated/commissioned/observed values distinguishable. Upload date is not commissioning date. A manufacturer's instrument range is not its trip setting. A design nozzle operating count is not the live number spraying.

- Attach the exact quote or normalized region of the original page actually examined. Preserve document/page IDs and immutable source content.
- A continued calculation table may require both the page mapping the equipment to the column and the page containing the value. Include both. Preserve the reasoning used to establish family/standard applicability.
- Match existing ontology definitions semantically. Do not use “coal capacity” for coupling kW, “main conveyor motor speed” for a small fan, or “trip threshold” for a fusible plug's design blowing temperature. Add a narrowly defined property when necessary.
- Mark arithmetic and review conclusions as derived/inferred, with the formula or rationale. Keep the underlying source claim alongside the conclusion.
- Preserve inequality, delay, mode and affected device in every protection claim. “Alarm”, “disengage scoop”, “stop oil pump”, “trip main motor” and “stop upstream equipment” are different actions. Ambiguous wording must not become a documented executable connection.
- Preserve disagreements without silently choosing a convenient value. Record which sources disagree, their respective bases, and what additional record would resolve the issue. A later date alone does not establish supersession.
- Unknown does not mean absent. Do not create negative assertions or fabricated values to fill the tree. Keep design selection separate from installed identification and replacement advice.
- General engineering knowledge may guide searches and questions, but cannot populate plant facts without plant evidence.

## 6. Make it useful in the application

Make the target part of the continuous visual plant explorer. Its opening scene must communicate its purpose, plant context, recognizable equipment, connected assemblies and auxiliaries before showing detailed facts. Clicking a component should preserve the surrounding assembly while offering deeper exploration and an on-demand evidence inspector. Keep ownership, physical location, coal flow, mechanical drive, utility supply and control relationships distinct. Avoid reverting to a dashboard of isolated fact cards or making equipment tabs the primary experience.

Use the shared scene projection and equipment symbols; extend reusable templates when necessary. Do not hardcode pilot IDs, source values, quantities or supposed physical coordinates into the UI. Template geometry is illustrative unless a separately evidenced spatial record supports it. Show shared services as connected assets rather than owned children. Keep every accepted component reachable through visual exploration or the assembly navigator. Verify the whole-plant → area → equipment → assembly → auxiliary journey, including return navigation.

Place a source button beside **each value and relationship**, not just a bibliography at the bottom. It should open the relevant original page/region at a readable scale, with the original PDF accessible, without losing the equipment browsing context. Preserve every support when there are multiple sources.

Surface gaps and contradictions within the affected component and through the assembly search. Keep long details collapsed until requested. Useful queries should include “PCS”, “oil”, “gearbox”, “brake”, “start permissive” and “nozzle”. Do not fill the overview with every fact or use DCS colours to imply live equipment states.

Allow recorded inspections, symptoms, repairs and outcomes to remain linked to their equipment without converting them into design specifications. Do not invent maintenance intervals, operating instructions, isolation boundaries or completed field checks.

## 7. Validate, apply, and demonstrate

Rehearse changes in an isolated database copy. Validate source references, types, units, identities, scope, connection direction, quantities and context. Inspect warnings. Confirm that existing evidence, unrelated facts and historical records are preserved. Apply through the normal versioned ingestion/acceptance mechanism within the user's authorized scope; do not write canonical tables directly.

Run meaningful automated checks for any changed application behavior. Independently audit the resulting data for orphan components, unintended cycles, duplicates, quantity arithmetic, cross-stream mistakes, references to missing sources, incorrect applicability, and undocumented control actions. Test at least one deep component and one grouped count from each target.

In the actual browser demonstrate: overview → target → component → individual fact → readable source → close/return. Test assembly search, location navigation, a mechanical or utility chain, and a discrepancy. Verify the original document link lands on the intended page. Inspect the rendered UI for clipped labels, unreadable drawings or excessive navigation.

Deliver a report stating:

- Before/after model versions; accepted batches; added/reused component and assertion counts (clarify whether counts include classifications/relations).
- What is now usable for each target, with direct application links and representative facts.
- Source manifest with exact page coverage and applicability; candidate-source dispositions.
- Unresolved gaps and source disagreements, with specific records needed to resolve them.
- Verification performed and its results; backup and reproducible patch/audit locations.
- A recommended next bounded batch, without claiming the whole plant or corpus is complete.

## Repository adapter: CHP Knowledge Builder

- Read `OPERATIONS_INGESTION_WORKFLOW.md`, `PLANT_EXPLORER.md`, `chp/patches.py`, `chp/reviewed_ingestion.py`, `chp/usage_intake.py`, and the current model. The operations workflow supersedes obsolete reconstruction workflows. Dense sources can support targeted reviewed facts when the active task explicitly requests that extraction; use the proper intake route and evidence.
- Live plant: `data/plant/plant.sqlite3`; originals: `data/plant/originals/<sha256>`; page renders: `data/plant/renders`. Use read-only SQLite connections for inspection and the SQLite backup API for a consistent snapshot. These local data files are not Git-tracked.
- Stage via `chp.reviewed_ingestion.stage`, validate via `chp.patches.validate`, accept via `chp.patches.commit`, and guard `expected_version`. Check current function contracts before invoking them. Never blindly replay the pilot builder: it is a version-466 migration record, not a generic ingestion command.
- `context.kind` is required. Directed network assertions require the matching network and documented verification. Record source qualifiers in context and explicit `source_gap` / `source_discrepancy` assertions. Preserve inferred origin where applicable.
- `dist/plant-model.js` projects accepted facts; `dist/plant-scene-model.js` preserves scene ownership/location and boundaries; `dist/plant-scene.js` and `dist/plant-scene.css` provide the visual-first equipment assemblies. `dist/plant-explorer.js` integrates browsing and assembly search; `dist/app.js` opens individual supports; `chp/evidence_view.py` renders readable source regions. Extend existing behavior rather than maintaining a separate hardcoded pilot model.
- Select an available Python interpreter: prefer `.venv/Scripts/python.exe` if present; otherwise verify `python` and its required imports. Run the relevant Python tests when backend behavior changes, `node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs` for affected projection/scene behavior, and `python -m chp.verify --data data/plant` after canonical changes. Also inspect the real browser and accepted target graph. Use the corresponding interpreter in each command.
- Read `EQUIPMENT_PILOT_REPORT.md` for the pilot's exact scope, source limitations and output artifacts. Continue with current IDs and model version; never copy its ratings/counts to another conveyor solely because the equipment looks similar.
- Read `COAL_YARD_1_PILOT_REPORT.md` for the yard pilot, shared-service boundaries, source coverage and unresolved design disagreements. `tools/enrich_yard1_pilot.py` is a guarded migration from version 484, not an instruction to replay against the enriched model. Use `tools/audit_yard1_pilot.py` as a pattern for independent semantic checks, adapting identities and expected counts to newly reviewed sources.
- Read `COAL_BLENDING_SILO_PILOT_REPORT.md` and `CRUSHER_HOUSE_PILOT_REPORT.md` for the later completed pilots. Preserve the silo crossovers and dual-drive architecture, crusher direct-drive and three-path routing, gauge-versus-trip distinction, local/shared service boundaries and source qualifications. Their builders are historical migrations, not reusable apply commands. Check the current graph before adopting any example IDs or expectations.
