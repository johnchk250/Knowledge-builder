# Assembly contracts and investigation depth

These contracts define the **questions that must be closed**, not a checklist of components to fabricate. For every target, each dimension ends as source-supported, already adequate after recheck, not applicable with evidence, contradictory, illegible, or source not found with a recorded search. “Done” without evidence or a specific gap is not a valid state.

The ten required dimensions are identity; purpose/place; containment; material routes; mechanical drive; utilities; control/protection; ratings/maintenance; provenance; visual journey. [coverage.csv](inventory/coverage.csv) initializes them for every named target. Copy the chosen rows into the batch's progress record and update there; do not overwrite the generated baseline.

## Conveyor

Read in this order: exact conveyor GA and all sheets/replies → drive schedule row → vendor model-specific motor/coupling/gearbox/brake → pulley/bearing/belt selections → protection/BOM → control scheme and path-specific rows → receiving/discharge TP layouts and utilities. Track both A/B columns separately.

| Assembly/location | Decomposition to investigate | Facts and relations needed |
|---|---|---|
| Whole belt route | Receiving end(s), carrying run, return run, discharge head, gallery and intermediate diversion | Actual upstream/downstream; each branch condition; length/belt width/speed/capacity with rated/design basis; location endpoints, not a single guessed place |
| Drive | Main motor, fluid/scoop or traction coupling, actuator, gearbox, geared coupling, head pulley | Source-stated mechanical order, input/output, ratings/model/ratio, brakes and holdback function; bearing and motor protection belongs to its component |
| Scoop circuit, if applicable | Sump, pump and pump motor, cooler/radiator and fan motor, strainer/filter, valves/instruments, scoop actuator/linkage | Oil direction/return, pump duty/flow, first fill/grade, heat rejection/cooling medium if documented; pressure/temp/flow/differential-pressure actions and exact trip target |
| Belt support | Head/tail/bend/snub/take-up pulleys, shafts, bearings, idler groups | Design-selection vs installed specification, lagging, dimensions, arrangement, lubricant and maintainable grouping |
| Take-up | Carriage/counterweight, ropes/sheaves, guides, travel stops and guards | Arrangement, required/selected mass and arithmetic, travel, quantity basis and inspection/access evidence |
| Material contacts | Receiving/discharge chute, skirts/liners, cleaners/scrapers, dribble chute | Which conveyor owns it, where it sits, and which local dust zone treats it; do not duplicate same chute under TP |
| Protection | PCS, BSS, ZSS, CBS and any stated belt-tear, emergency/local stop, speed/load/temperature devices | Original quantity unit and scope, spacing, grouping, sensor location, condition polarity, threshold/delay/action/reset if stated |
| Power/control | Starter/VFD/feeder, local station, DCS interface, permissive scheme | Exact applicability, start unloaded/engage sequence, normal stop vs trip; power path requires a source connection, not just motor voltage |

Minimum evidence demonstration: one grouped count with the original unit, one deep drive auxiliary, one mechanical connection, one protection condition with its target, one receiving/discharge relationship and one unresolved item if present. A whole-document bibliography does not meet this requirement.

## Transfer

Use a **place scene**. Show equipment explicitly located there as well as owned equipment, retaining its actual owning assembly.

Required investigation: building identity and GA revision; orientation/floor/elevation datum; head/tail/chute interfaces; actual stream/selector/divider logic; gate actuator/linkage/torque and position feedback; local sensing; dry fog versus dust extraction versus service-water washing; individual application points and receiving/discharge zones; local FAS/PRU/filter/regulators/solenoids/headers/nozzles; common supply interface; sump/pit/duty-standby pump/discharge; hoist/access/local panel and drainage.

Build an interface table per TP: `incoming equipment → chute/application zone → selector (if any) → outgoing equipment | condition | place/elevation basis | evidence`. Every parallel branch needs its own condition. Trace the pipe on the P&ID; a crossing line is not a tee. AP/FAS/PRU suffixes are scoped to the system/building; do not reconcile by suffix alone.

Count reconciliation must distinguish nozzles per header, headers per application, application points, PRUs, FASs, solenoid channels and whole-system quantities. If the source does not establish one-to-one relationships, retain groups rather than inventing device-level tags.

Minimum visual: one readable cutaway with clear incoming/outgoing belts and attached local services; clicking the head drive opens the original conveyor-owned drive, while clicking the sump opens the local drainage assembly.

## Yard

Build one functional area, two operating lanes and shared-service boundaries. Source-supported yard membership includes stacking belt, stacker, stockpile, portal reclaimer, reclaim belt, shed and drive/tail houses. Their geometry is a navigational arrangement unless the GA establishes surveyed placement.

Close: yard capacity/storage basis; source-specific pile dimensions/density; stacking/reclaim directions and gates; machine travel/slew/luff limits; collision and storm arrangements; local SPDS physical application points versus control sectors/valves; machine-mounted dust suppression; water refill; runoff collection/local pit and pump; connection to common pond; fire/water/access evidence. Live tonnage, coal age/temperature, reclaim schedule and inspection history require dated data and must not be synthesized from design capacity.

Deliver a yard mapping sheet with exact tags and sources for the two conveyor endpoints, both machines, pile/shed/UAX places, AP/sector/SV mappings, sump branch and common utility node. It must be specific to that yard. P06–08 cannot pass by renaming the Yard 1 graph.

## Stacker

Investigate machine frame/gantry, long travel wheel bogies/drives/brakes/rail clamps, boom structure and belt/drive/take-up/cleaners, slew drive/bearing, luff hydraulic circuit/cylinders, travelling tripper, cable reel and power/control/cabin, belt weigher, central grease circuit, onboard dust suppression, storm anchor/park arrangement and fire zones.

For each motion assembly: identify driving motor → coupling → reducer → driven element, brake/holding provision, limit/position feedback, permissive/trip cause and mode, lubricant points and model-specific spares where supplied. A hydraulic powerpack needs pump/motor/tank/filter/cooler/valve/accumulator/instrument/cylinder relationships only where shown. Do not assume every motion is hydraulically driven.

Keep rail loads/structural design wind/operating wind warnings/parking criteria separate. Component-selection and stability calculations stay qualified. Read machine-type/applicability and per-machine versus four-machine quantities before using any schedule.

## Reclaimer

The Maitree yard pilot is a **portal scraper reclaimer**. Investigate main and auxiliary scraper booms, chains/flights/sprockets/take-up, scraper drives/couplings/gearboxes/brakes, main/aux boom hoisting rope/sheave/drum/drive/brake, long travel/bogies/clamps, storm anchor, cable reel, lubrication and chain oil, impact/discharge interface and onboard dust system. Do not add a bucket wheel from a generic stacker-reclaimer template.

For boom/hoist geometry distinguish reach/load case from actual motion limit. Motor sizing, reeving count, rated line pull, emergency brake, end limits and ropes must be linked to the applicable source. Maintain GA/BOD differences as separate design claims until resolved. QAP/inspection-category sheets are not proof of completed in-service inspection.

## Silo

Separate house, vessel, rotating extractor and belt feeder. Investigate vessel/support/cone/platform/liners and access; incoming chutes/level monitoring/dust vent; rotating blade/tubular chute/slew bearing/pinions; motor/gear/VFD, lubrication and sealing; discharge gate/feeder/selector. Follow actual alloy/model/quantity applicability.

Close capacities by basis: geometric volume, stated hopper mass, density, rated extraction, design extraction and capacity adjustment. Distinguish input assumptions marked “client to confirm” from confirmed design facts. Two drive motors per extractor do not automatically imply two independent VFDs; the source must establish electrical/control architecture.

Capture local, remote and maintenance control modes separately. Link source-stated anti-consolidation/minimum-bed guidance as qualified requirements, not invented operating procedures or automatic controls. Fire/inerting/CO/temperature/ventilation features remain search questions until a plant-specific source supports them.

## Crusher

Separate the building, grizzly, ring granulator, collection feeder, direct bypass and local DE. Investigate rotor/rings/shaft/bearings/casing/liners/grate/doors, drive/coupling oil system, hydraulic opening, vibration isolation/sensors, upstream and downstream chutes, tramp removal and maintenance lifting.

Close design/rated throughput, feed/product sizing, speed, installed/selected drive basis, wearing parts and any documented adjustment/wear criteria. Maintain direct bypass and grizzly undersize bypass as separate material paths. Interpret each door/vibration/downstream interlock against the crusher-specific control sequence.

DE subassembly: pickup hood → branch/duct/damper → bagfilter → fan/outlet, hopper/airlock discharge, compressed-air pulse cleaning, pressure/differential-pressure feedback and dust disposal destination where documented. Fan motor/run command is not proof of adequate extraction flow; distinguish indication from permissive.

## Screen

Identify primary EBD-1–4 versus crusher-house EBD-5/6 before applying a vendor drawing. Investigate feed gate/chute, grizzly deck and replaceable bars/liners, exciter/eccentric shaft or source-stated vibrating drive, motor/coupling, bearings/lubrication, springs/supports and separate oversize/undersize discharge. Distinguish vibration isolation from an actual vibration trip instrument.

Close applicable aperture/cut size, capacity/material assumptions, motor/drive selection, adjustment and replacement information, downstream permissives and local dust pickup. Inspect the exact screen/feeder nomenclature: a file called vibrating grizzly feeder can contain the crusher-house screening equipment, but filename alone does not establish the numbered-unit mapping. Demonstrate both material fractions and a deep maintainable component with its own evidence.

## Feeder

Resolve KF-1/2 at the crusher house versus KF-3/4 below silo extractors. Investigate belt, drive motor/reducer/coupling, head/tail/bend pulleys, bearings, idlers, take-up, skirts and cleaners, receiving interface, discharge selector and protection devices. Use the feeder GA, feeder drive/tension calculation and feeder-specific belting source rather than the main-conveyor's schedule by default.

Close capacity/speed/drive basis, belt construction and dimensions, upstream extractor/crusher and downstream conveyor permissions, normal start/stop and local isolation information if documented. A feeder motor's running feedback is a distinct control claim from an extractor's mechanical drive. Retain per-feeder quantities and any common-design applicability.

## Tripper

Investigate carriage/frame/rails/wheels, travel motor/geared drives/brakes/clamps, top/bottom/bend pulleys/bearings, cable reel, chute/gate/actuator, sealing belt/rollers, local control, normal/overtravel/overspeed/anti-collision/emergency devices, platform/rail cleaners and maintenance access.

Close per-tripper/whole-project quantities, handed arrangement, travel range/unit assignment, normal versus alternative delivery, through versus side discharge, and head-end terminal discharge. Structural rail load is not wheel-drive torque or current load. A diagram of a reachable bunker does not establish current tripper position.

## Bunker

Investigate bay/inlet slot/sealing system, individual vessel/conical hopper/outlet, liner/support/access, level measurement and limits, vent/DE pickup, documented temperature/fire provisions and outlet boundary. Keep the A–F identity independently navigable even when a common design reference applies to all 12.

Close capacity/density/coal-case/BMCR basis, active/standby scenario, geometric elevations/datum, material/liner thickness and review comments. Do not attach hypothetical mill/feeder auxiliaries or infer in-service capacity from theoretical volume. Maintenance access information does not establish entry authorization or an isolation boundary.

## Unloader

Identify each machine type before assembly creation. Investigate long travel, boom hoist/latch, main/aux trolley, grab hoist/holding/closing, hopper/feeder/shuttle, machinery house/cabin, cable feed, brakes/clamps/storm restraint, lubrication, onboard dust system, elevators/hoists and emergency/limit feedback. Generic couplings or unnumbered vendor assemblies need explicit applicability.

Keep rated capacity, cycle-time assumptions, material/ship envelope and stability/wheel-load cases separate. Reversible shuttle direction must connect to the selected EAC-1 stream with a condition. Per-type differences must remain visible even if a shared design reference is reused.

## Sampling

Model sample and reject paths separately, including primary sampler, feeder, sample crusher, secondary sampler, collector, reject conveyor, slide gate and bias bin where supported. Capture intermittent cycle/timer/proximity logic, reverse-bias operation, drive/protection, local PLC/DCS interface and collector handling as source requirements. Do not treat sample-system crusher as a main plant crusher or its small motor ratings as main-conveyor data.

## Measurement

Resolve instrument/function/unit identity: AT/ILMS magnetic separation, QB/MD metal detection, EAT/BW belt scale, CV coal analyser. Record host conveyor, physical location, sensing principle, measuring range/accuracy basis, signal/interface, associated drive/cleaning/marker/reject apparatus and documented control action. A sensor's ability to measure does not establish an automatic trip or feedback loop. Calibration/test sheets are distinct from current calibration status.

## Area

For screen houses, UAX buildings, sheds, gates, feeders and other targets use the relevant parent section plus the transfer/place pattern. A building has owned civil/local-service assets and located equipment; a gate has its own material ports and drive/feedback; a screen/feeder has its actual motion drive/support and sizing branch. Explicitly select the appropriate contract in the batch ledger instead of accepting an empty generic scene.

## Shared services and maintenance information

Apply P01/P15 to pumps, compressors, filters, valves, tanks, HVAC, electrical distribution, fire, hoists and workshop equipment. The service path must show real endpoints, source directions and control dependencies. Maintenance support means identifying the actual maintainable component, its make/model/lubricant/access and supported inspection requirements. Do not create routine intervals, torque values, spare stock or completed jobs from engineering expectation.

When a relevant manual/loop schedule/commissioning test/field-tag or maintenance record is missing, name it precisely in the affected component. A useful gap says what is missing, what decision it blocks, which corpus sources were searched and where later evidence belongs.
