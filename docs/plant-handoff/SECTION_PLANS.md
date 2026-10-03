# Section implementation plans

These are implementation instructions for bounded enrichment, not a statement that all listed search targets exist. The [target index](TARGET_INDEX.md) supplies IDs, trees, neighbours and citations from the frozen v510 baseline; reconcile them with live data. The [source catalog](SOURCE_CATALOG.md) supplies source retrieval IDs, hashes and page/evidence maps. Apply the [family contracts](ASSEMBLY_CONTRACTS.md) to every member of a batch and start with the [current continuation guide](CONTINUATION_GUIDE.md).

Control references below mean **Control Write up for Coal Handling System.pdf**, `doc_4f2cd96c3b1e413ea4b5`, PDF pages, with p55 = flow drawing 175001 Rev 8 and p56 = layout 175002 Rev 0. The main write-up's approval is conditional; diagrams and annexes have their own revision context. Historical v510 material statements and conditions are in `inventory/connections.json`; use the accepted live graph for current interfaces.

## P00

**Identity, plant boundary and reuse decisions.** This is a finite preparatory review, not an instruction to clean up all history before useful work begins.

First close or explicitly defer F01–F04: UGA pump-house labels, found TP-1 GA, SUL versus Coal Ship Unloader mapping, UEF-2/TP16–18 scope. Create an identity decision ledger with old ID, candidate ID, compared source pages, conclusion and affected relationships. Reuse the current canonical label/alias mechanisms; read `chp/operating_model.py` before corrections. A merge requires proof of the same asset, not same family or model number.

Review every row assigned P00 in `record-review-queue.csv` and give it an owner/disposition: installed candidate to a section, generic design/reference, shared service, other-project reference, placeholder needing correction, or unresolved with a specific missing source. This can happen progressively as each consuming batch reaches it. No global batch may mark the plant complete while rows remain silently undispositioned.

Review aliases AT/ILMS, QB/MD, EAT/BW, EBE-TT/TT, RE/EBE-CES and equipment-specific gate prefixes through source applicability. Do not merge them solely by matching suffix. Resolve document-looking entities through classification review rather than adding them to a physical assembly.

Source starts: control pp 4–8,35,55–56; standalone COAL FLOW DIAGRAM pp 1–3; LAYOUT OF COAL HANDLING PLANT; GA & LOAD DATA OF DS PUMP HOUSE-1/2; GA & MECH LOAD OF TP-1 pp 1–2; 019676_03.PDF pp 1–6; SW/DW layout at UEF-2,16,17,18 pp 1–5. Review p55's complete legend against current named main-route targets (30 belts,12 in-scope TPs,4 yards,4 trippers,2 silos,2 crushers).

**Acceptance:** every critical identity decision has evidence and a change/deferral record; pilot references still resolve; no imported foreign-project note becomes a Maitree specification; affected labels/placements are intelligible in the browser. Gate all later work on any identity decision it depends upon, not on every unrelated P00 row.

## P01

**Shared utility backbone.** Own common tanks, pump houses, DFDS air/water production, common SPDS/SW/PW supplies, treatment/filters, distribution mains, runoff pond and common control. Local nozzle/header/sector assemblies remain with the section that uses them.

Establish DS Pump House-1/2 versus UGA-1/2 identity before linking consumers. Reconcile DFDS-1A/B versus DFDSP-1A/B grouped and individual records; SPDS/PWDSSP/SPDSP naming; screw-compressor SC identifiers versus stockpile sequential-controller SC-01. Keep tag namespace + system + source. One “SC” prefix is not one equipment type.

Build source/tank → suction/isolation/filter → pump/motor/check/pressure → common header → named branch, and compressor/receiver/dryer/air header where documented. Keep plantwide P&ID totals, local BOM quantities and standby logic distinct. Pressure range, working pressure, low-pressure permissive and alarm setpoint are separate claims. Sump pumps need local pit and discharge destination, not only a pump model.

Primary sources: DFDS P&ID `doc_bca09d68af9b43e3b633` p1; DFDS philosophy `doc_294aacf286d246769e32` pp 2–5; DFDS DBR and pump/compressor/FAS/PRU/filter/nozzle/solenoid datasheets. SPDS P&ID `doc_5a36f2843d504d6e96de` p1; stockpile DS/SW-PW philosophy `doc_e17edf6897d746fabe12` pp 3–4,8,10; plain-water DBR `doc_777d1a06d4fa4e8ba231` pp 2–3; sprinkler data p2. Sump/runoff P&ID `doc_0453a0a014424f1cae06` p1; run-off feed-water DBR/P&ID/layout, pump GA, pond GA; DW SYSTEMS. Control pp 25–26,30–31,53–54.

**Consumer contract:** each section receives the canonical service identity and one source-supported boundary node/tag, medium, direction, design condition and local isolation/filter facts where known. It must not clone the pump station or claim isolation completeness. F15 pump identity/head disagreements remain visible.

**Acceptance:** two sampled consumers in different areas reach the same common source ID; local systems keep their own counts; reverse navigation shows all documented consumers; standby action and sensor polarity have exact source support. A common plant service view remains available outside the nine coal-process stages.

## P02

**Jetty, ship unloaders, EAC-1A/B, UEF-1 and EAC-2A/B.** Preserve the 1AB/TP1 pilot and enrich its missing place/maintenance context before expanding the receiving stream.

Resolve three numbered ship-unloader identities using P00. Decompose the actual grab-unloader design: long travel/rails/clamps/buffers, boom hoist/latch, trolley traverse, grab holding/closing, receiving hopper, feeder, reversible shuttle conveyor, machinery house/cabin, cable feed/reel, lube system, onboard dust system, access/elevator and lifting. Follow mechanical drive, brake/holding and power/control paths separately. Review type1/type2 and SUL-1/2/3-specific columns before applying any common arrangement.

Source starts: General layout of Jetty; Type1/Type2 GA and cycle-time GA; DBR Ship Unloader; 019676_03.PDF and numerical drawing titles016535_04/016614_02; machinery house, main/aux trolley, holding/closing and trolley-travel drive, gearbox/coupling, rail fixing/end buffer, lube diagram, main chute/hopper, elevator and ship-unloader DSS P&ID. Compare capacity/cycle-time and stability/wheel-load calculations as calculated design cases, not throughput observations.

Conveyors 1/2 use individual GA1AB/2AB, drive schedule and conveyor library. Keep the accepted1AB oil-circuit, protection and take-up claims with their disagreements. EAC-2 currently has receiving-chute records; reuse these. Complete its own drive/head-end and screening inlet placement without moving EAC-1's chute into EAC-2 ownership.

UEF-1 GA p1 now supplies a concrete building/drive/chute composition. Review p2 tank-capacity comment, local piping pp 1–3, hoist schedule and sump branch; qualify actual dimensions/elevations and maintenance lifting data. Pilot flow remains1A→2A and 1B→2B; no unsupported crossover. AT-1/2, QB-1/2 and EAT-1/2 need equipment applicability checks rather than generic ILMS/metal-detector/belt-scale inheritance.

Control starts pp 4,9–12,18,26–29,34,38,52; review exact1B/1A copy error and brake/CBS ambiguity.

**Acceptance:** unloader → selected shuttle outlet →1A/B → local chute/TP1 →2A/B journey works; motor → coupling → oil pump and PCS group → own evidence work; both stream identities remain independent. Preserve 14 pairs PCS/28 derived devices,11 pairs BSS/22 derived devices, source-qualified ratings and separate 4/9/4/9 DFDS nozzle zones.

## P03

**Primary screening UEE-1, EAC-3A/B, UEF-3 and sampling1.** Own EBD-1–4, four rod gates KB-RG, four rack/pinion gates KB-RPG, reject collection and local dust/access systems. Do not confuse these with EBD-5/6 at UEE-3.

Show parallel primary-screen routes: conveyor 2A/B → appropriate gate/screen → undersize conveyor 3A/B and oversize reject branch. Verify each gate/screen lane from p55 and PSH GA rather than relying on numerical order. Screen assembly should expose grizzly deck, exciter/drive, suspension/support, liners and discharge chutes when shown.

At UEF-3, accepted EAC-3A→FD-1 and 3B→FD-2 split to Yard 4/EAC-13 or FG-1/2 toward either EAC-4 stream. Present split/onward flow distinctly. UEF-3 is both a sampling location and distribution boundary; retain one identity, visible from both journeys.

Sampling1 has primary sampler → belt feeder → sample crusher → secondary sampler → collector and reject return; review bias/reverse mode, selector gate, timing, own dust/drive/protection components. It is a process branch with a return, not a series machine in all coal flow. Existing EAU-1/UEF-3 sampling IDs and component identities must be compared before adding anything.

Source starts: GA & MECH LOAD OF PSH; grizzly-screen PSH GA `doc_b4cf0a76c954435aadd6` pp 1–4; rod/R&P gate GAs and actuator selection; GA3AB; GA TP3; coal sampling UEF-3 GA `doc_404c8747ba8047ab8f12`; sampling calculations; UEE-1 DFDS/SW/PW piping; DFDS P&ID; control pp 4,13–14,19–21,36–38,50–52,55. No UEF-3-specific piping title was found in the 266-document title inventory: inspect common P&ID/TP3 GA and record the specific layout search result, rather than declaring no DFDS.

**Acceptance:** two screen lanes and a reject path are selectable; sampling reject returns reach the source-stated conveyor; eachFD branch retains conditions; a screen drive and local dust zone reach their own facts and sources. No screen family data transfers to the crusher by tag coincidence.

## P04

**Distribution UEF-4/5/6/7, EAC-4A/B, EAC-5A/B, EBA-6A/B.** Make one connected through-route with distinct yard diversions.

| Place | Required composition and accepted boundary | Critical distinction |
|---|---|---|
| UEF-4 | EAC-4A/B fixed trippers FTR-1/2 → FD-3/4 → EAC-11 or continuation on the same EAC-4A/B | Same conveyor through-flow is not recycle or a second belt. |
| UEF-5 | EAC-4A/B → FD-5/6 → EAC-9 or FG-3/4 → either EAC-5 stream | Preserve split versus selector and actual gate conditions. |
| UEF-6 | EAC-5A/B fixed trippers FTR-3/4 → FD-7/8 → EAC-7 or continuation on EAC-5 | Yard 1 boundary; local fixed tripper differs from travelling bunker tripper. |
| UEF-7 | EAC-5A/B → FG-5/6 → EBA-6A/B | Accepted FWD→6A, REV→6B; verify individual source conditions. |

For each TP: local GA cutaway, incoming/head and outgoing/tail chutes, gates/actuators/limits, FAS/PRU and application zones, common utility boundary, local sump and access. Existing TP-prefixed DFDS records may currently be unplaced—reuse them after evidence review. Conveyors use their respective GA4/5/6AB and drive/control library; study end-specific location and partial-flow capacity rather than class defaults.

Sources: each TP GA and each UEF-4/5/6/7 piping layout; flow-divider GA/FLOW DIVIDER-01, rotary actuator and flap gate GAs; control pp 4–5,8–14,27–29,36–43,49–52,55. Source-specific capacity split1250 wording is a qualified design/path requirement, not a current flow reading. Check coal analysers CV-1/2 at the silo-bound conveyors and avoid duplicated generic analyser identities.

**Acceptance:** traverse from EAC-3 to each of four yard inlets and to each silo inlet; animate only the chosen branch; preserve EBA-6A→EBB-2 and 6B→EBB-1. Each local TP can expose a conveyor drive without taking ownership of the whole conveyor. FD and FG cannot be represented as the same generic two-way gate when their operation differs.

## P05

**Coal Yard 1: controlled extension of the accepted pilot.** Current area closure413 records; EAC-7 has 41, EBA-8 has 42, EAD-1 has 101, EAF-1 has 57. These are graph-record counts, not acceptance thresholds for other yards.

Preserve EAC-7→EAD-1→EAE-1→EAF-1→EBA-8, UEB-1, UAX-1/UAX-5, local SPDS, onboard machine DSS and runoff. Recheck the public journey into adjacent UEF-6/11. Expand only where targeted source review adds actual missing relationships/detail.

Use this section to build a **family applicability matrix** for later yards: source/model/revision → applies to which numbered stackers/reclaimers → common parameter → per-unit exception → evidence. Family design may be explicitly applicable without being field verified. Candidate differences include travel arrangement, drive ratings, onboard DSS/lube, rail clamps, storm anchors and fire equipment.

Follow referenced machine manuals and available detail drawings the first pilot did not fully decompose: boom drive, long travel, slew/hydraulic powerpack, luff cylinder, portal main/aux scraper hoist, gearbox/couplings/brakes, rail clamps/anchors, cable reel and instrumentation references. Keep structural/wind/load calculations as design records. Retain existing boom-weigher identity.

Local checks: EAC-7 BSS18 pairs→36 devices; EBA-8 BSS17 pairs→34; PCS30/31 count basis unresolved. EBA-8 scoop model discrepancy remains. Local runoff SP-8G/H, not8A/B. SPDS28AP/14 sectors/28 solenoids; do not infer AP↔SV one-to-one. Stacker/reclaimer DSS34/6 nozzle counts and lube pump quantities require their own source applicability.

Source starts: Yard 1 report and manifest, GA7/8 p5; control pp 43,46,51,55; stockpile piping; EAD/EAF GA/BOD and detailed mechanism/lube/fire drawings. F15/F16 and all existing pilot qualifications remain tracked.

**Acceptance:** no regression of the pilot audit; missing detailed drawings get an actual search disposition; each candidate common-machine fact has a precise applicability decision before use in P06–08.

## P06

**Coal Yard 2.** Create one descriptive area entry after proving its membership; keep canonical EAC-9, EAD-2, EAE-2, EAF-2, EBA-10, UEB-2, UAX-2, UAX-6. EAD-2 has only 2 records and EAF-2 only 1; both conveyors have 1 at baseline.

Build EAC-9→EAD-2→EAE-2→EAF-2→EBA-10. Input is UEF-5's FD-5/6 diversion; output is FG-9 at UEF-10→EBA-15A/B. Start from GA9/10, drive schedule columns and control p55/p46. Do not take Yard 1 motor/PCS/scoop selections as Yard 2 facts.

Instantiate source-supported machine composition using the P05 applicability matrix, verifying actual tags and any vendor-family limits on every source. Create Yard 2 SPDS application/sector mapping from stockpile P&ID and piping; trace the **actual local sump branch** and common supply. Identify local machine DSS refill boundaries and runoff route. Use UAX-2/6 drawings and shed/context source to place components, not to invent plant geometry.

**Acceptance:** complete conveyor, stacker, portal reclaimer, stockpile/shed, local SPDS and drainage journeys with readable evidence; demonstrate one unique Yard 2 quantity, one motion assembly and a local-to-shared utility path. If a sector or sump assignment cannot be established, leave it specifically unresolved rather than copying the adjacent yard.

## P07

**Coal Yard 3.** Planned area root contains EAC-11, EAD-3, EAE-3, EAF-3, EBA-12, UEB-3, UAX-3, UAX-7 after source review. Both conveyors have 1 record; EAD-3 has 2 and EAF-3 has 1.

Input from fixed-tripper diversion at UEF-4 (FD-3/4) to EAC-11; output EBA-12→FG-8 at UEF-9→EBA-15A/B. Build both machine lanes and local service branches. Read GA11/12 and correct drive columns, stockpile P&ID/piping, UAX-3/7 context, common machine applicability and UEF-9 interface sources. Fixed-tripper throughput versus side diversion must stay explicit at the upstream boundary.

**Acceptance:** same depth gates as Yard 2, using Yard 3's own counts/models and exact boundary tags; all local water/air/runoff equipment has supported ownership/place and is not cloned from shared services. Demonstrate that opening the Yard 3 reclaimer cannot display Yard 1 lubrication as installed without an explicit qualified applicability link.

## P08

**Coal Yard 4.** Planned area root contains EAC-13, EAD-4, EAE-4, EAF-4, EBA-14, UEB-4, UAX-4, UAX-8 after review. EAC-13 already has 3 records; inspect/reuse its existing parts. EBA-14 and EAF-4 each have 1; EAD-4 has 2.

Input from UEF-3 FD-1/2 to EAC-13; output EBA-14→FG-7 at UEF-8→EBA-15A/B. Read GA13/14, UAX-4/8, stockpile P&ID/piping and Yard 4-specific columns/branches. Sampling at UEF-3 does not become a Yard 4-owned system simply because it shares the inlet TP.

**Acceptance:** full yard composition with actual local source branches and all machine-family qualifications; verify both selectable return streams and distinguish local SPDS from onboard dust suppression. Explicitly reconcile existing EAC-13 measurement/protection records before creating new components.

## P09

**Reclaim TPs8–12 and EBA-15A/B,16A/B.** These form a common receiving corridor for four yard reclaim outlets.

| TP | Yard outlet | Selector | Accepted downstream choices |
|---|---|---|---|
| UEF-8 | EBA-14 / Yard 4 | FG-7 | EBA-15A REV /15B FWD |
| UEF-9 | EBA-12 / Yard 3 | FG-8 | EBA-15A REV /15B FWD |
| UEF-10 | EBA-10 / Yard 2 | FG-9 | EBA-15A REV /15B FWD |
| UEF-11 | EBA-8 / Yard 1 | FG-10 | EBA-15A REV /15B FWD |
| UEF-12 | EBA-15A/B | FG-11/12 | EBA-16A REV /16B FWD |

These are accepted edge conditions to recheck against source. Several incoming conveyors load the same EBA-15 stream at different places; preserve the single continuous conveyor and separate receiving interfaces. Do not turn the corridor into four copies of 15A/B or require coal to pass through a pile to reach the next receiving point.

Complete GA15/16 drive assemblies, mechanical/protection selections, material contacts, take-up, cleanup and place endpoints. Each TP needs its own local DFDS zones and existing FAS/PRU reuse, drain/sump and gate drive. AT-3/4 on the reclaim streams and CV-3/4 toward the silos need exact applicability.

Sources: five TP GAs and corresponding piping layouts (UEF-11 title omits hyphen); GA15/16; common gate/DFDS/sump packages; control pp 5,13–14,27–29,44–46,53–55. EBA-16A→EBB-1 and 16B→EBB-2 are fixed accepted endpoints, independent of the upstream A/B selector.

**Acceptance:** all four yard outlets can be followed to either15 stream and the source-permitted16 outlet; local FAS/nozzle evidence stays TP-specific; a15 belt appears once while its receiving chutes appear in several place scenes. Keep any unproven simultaneous reclaim operation outside the flow illustration.

## P10

**Implementation checkpoint:** B30/B31 were accepted at v527 on 20 September 2026 with source qualifications. Read [the silo report](../../COAL_BLENDING_SILO_PILOT_REPORT.md) and their checkpoints before follow-up. The counts and investigation tasks below describe the original v510 plan, not empty current assemblies.

**UEE-2 / Coal Blending Silo House.** Current named house closure19; each EBB vessel and EBE-CES extractor has 1 record. RE-1/2 and generic extractor dossiers exist elsewhere—resolve applicability/identity first.

Build two vertical assemblies with vessel, pressure-relief cone/support arms, reclaim platform, rotating blade, rotating tubular discharge chute, slew bearing/external gear, two motor/gear/pinion drives where supported, lubrication/seals and downstream KF-3/4. Keep vessel, extractor and feeder as separate assets. Locate VFD/LCS and access provisions from actual GA. Model the two-drive common-VFD arrangement only with its source, including individual motor overloads.

Source starts: silo-extractor philosophy `doc_ef73ffa11a1748979909` pp 3–9, review p10; extractor GA `doc_40baa8f059a0427f9567` pp 1–3; CBSH GA `doc_17dab58f999c4939bbc7`; KF-3/4 GA `doc_396739a89bde48f28f61`; feeder belt/tension/drive data; UEE-2 piping; control pp 5,25,39–49,55. **The philosophy filename says blending silo; p10 explicitly corrects its scope to silo extractor.** Do not use all its vendor input data as an independent vessel-design certification.

Initial claims to verify and qualify: rated1250 vs design1375 MTPH, adjustment250–1375,2–9 rpm,2×55 kW per machine,1000 MT hopper input,0.8 density for volume vs1.1 for structural/power basis. They are source-review leads, not committed new selections. Maintain remote/local/maintenance mode-specific permissives; p7 permits maintenance reverse, while earlier review replies use broader wording. Parse main text versus review history. Lubrication circuits and the review-sheet dust-seal/hydraulic request need closure against GA/BOM.

Show EBB-1→CES1→KF-3→FG-13 and EBB-2→CES2→KF-4→FG-14, with selected discharge to EBA-17A/B. Retain EBA-6 crossover and EBA-16 matching lanes. Inspect high-level instrumentation and receiving permissives; do not fabricate continuous level tags or fire/inerting systems merely because a silo normally needs them.

**Acceptance:** a user can open either extractor and see its actual drive arrangement, what rotates and what supports it; a capacity click displays its basis; selecting maintenance mode in the information view cannot mix its permissives with normal mode. The scene must preserve all four incoming conveyor-to-silo mappings.

## P11

**Implementation checkpoint — 29 September 2026:** B32–B35 implemented at v558 with source qualifications. Read [the report](../../CRUSHER_HOUSE_PILOT_REPORT.md), accepted claim/source ledgers and batch checkpoints. The specifications below are the original plan; do not recreate the completed trees. Remaining commissioning, identity, duct-layout and shared-package questions are explicitly listed in the report.

**UEE-3 crusher house, EBA-17A/B, EBD-5/6, EBC-1/2, KF-1/2 and local DE.** Source decisions on F09/F10 precede new control/identity connections.

Two lanes: EBA-17A→FG-15A→EBD-5→oversizeEBC1 and undersizeKF1; crusher discharge→KF-1. EBA-17B followsFG15B/EBD-6/EBC-2/KF-2. Direct FG-15A/B bypass to the respective feeder is a separate selectable path. KF-1/2 discharge throughFG15/16 to selectedEBA18A/B. Preserve conditional control and avoid depicting all bypasses active together.

Decompose ring granulator by source: casing/doors/liners, rotor/shaft/rings, bearings/support, screen/grate cage, drive motor→crusher scoop coupling/oil circuit→driven assembly, hydraulic opening/powerpack if shown, vibration isolation and monitoring. Gate hydraulic-door interlock needs actual sensing/action source. Grizzly/feeder drives, springs, chute plugging, tramp metal and maintenance lifting/access remain distinct.

Sources: crusher GA `doc_f608e15aedbf4f368692` pp 1–3; UEE-3 buildingGA; vibrating grizzly feeder GA/TDS; KF-1/2 GA; GA17AB; crusher-specific scoop coupling `doc_624bd9eb971746e293a8`; vibration-isolation GA; DE design, schematic, duct layout atCRH, bagfilter/fan/compressor/dryer/rotary-airlock GAs and DE philosophy pp 1–17; UEE-3 DFDS/SW/PW piping. Do not infer installed DFDS in lieu of DE from Rihand annexes; identify each local application from Maitree sources.

Control pp 15–17 give a **crusher-specific** radiator/oil-pump/main-motor/scoop sequence; this must not be copied from the conveyor sequence. Review pp 39–40,44–45,47–48 and the separate DE philosophy for real downstream permissives and start/stop delays.

**Acceptance:** all three lane paths (direct bypass, grizzly undersize, crushed oversize) visible and navigable; motor/oil/cooler and hydraulic door/vibration protections trace to sources; local extraction pickup reaches its own fan/filter/common air system. Crusher drive data never inherits a conveyor coupling by superficial similarity.

## P12

**EBA-18A/B, UEF-13 and sampling2.** Own GA18 drive/mechanical/protection enrichment, QB-3/4, EAT-3/4, local TP13FG17/18, sampling plant and elevator/SNC-2 place context. Reconcile generic “Transfer Point TP-13 Passenger and Goods Elevator” with existing SNC-2 before introducing another elevator.

Sampling2 must trace primary sampler → feeder/reverse bias path → sample crusher → secondary sampler → collector, reject conveyor and slide gate return to EBA-19A/B. Control p22 distinguishes open/closed slide-gate destination. Keep small sampler crusher distinct from EBC-1/2.

Sources: GA18AB; GA TP13; UEF-13 piping; sampler GA `doc_98b9805fdd334190a93f`; calculations; elevator GA; measurement library; control pp 6,18–19,22–23,27–29,39,44,47,53–55. Read each FAS/AP branch independently of the neighbouring crusher/silo system.

**Acceptance:** EBA18selected stream→FG-17/18→EBA-19 outlet, with source conditions, sampler sample/reject split and local utility chain; one deep sampler part, one main-conveyor part and one elevator/hoist identification reach correct evidence. No duplicated local DFDS identity.

## P13

**EBA-19A/B and TT-1–4.** EBA19Aowns TT-1/2;19BownsTT3/4 in the current graph. Keep through-conveyor identity, local tripper geometry and service connections separate.

Create tripper assembly from GA `doc_1217799da7124df5bbe5` pp 1–6: carriage/frame, top/bottom/bend pulleys and bearings, drive/non-drive wheel assemblies, travel geared motors, brakes/rail clamps, manual clamps where listed, cable reel, two-way chute/actuator/limits, sealing-belt rollers, overspeed, normal/overtravel limits, emergency stops, anti-collision and access/control station. P1 has common/handed arrangements and different travel distances for TT-1/3 vs2/4; preserve assignment, do not multiply whole-project quantities per tripper.

Use geared-motor GA/TDS, rail-clamp GA, conveyor 19GA, belt/sealing datasheet and actuator sources. Control pp 6,11,24,39,44,47. Evaluate normal-unit designation versus cross-unit provision and terminal head discharge explicitly with P14; a diagram of potential movement is not a verified present operating setting.

**Acceptance:** choose TT-1 and see19A+Unit 1 context; TT-2 sees19A+Unit 2; TT-3/4 corresponding19B. Open travel drive or rail clamp and get its own source. Distinguish forward/reverse travel, gate movement, conveyor run and rail-clamp release; do not treat DCS indication as proof of remote motion control.

## P14

**Unit 1/2 bunker bays and all A–F bunkers.** Both bays currently have 7 records including root; individual bunkers have 2own assertions. This is a substantial extraction/applicability task, not a request to copy generic vessel numbers into12entities.

Model each bay with two conveyor/tripper lanes, source-supported inlet slots/sealing system, six labelled vessels, vent/dust pickup, level indications and documented outlet interface to downstream plant. Do not claim mill/feeder details outside the corpus or assume that the 4 active/2 standby design scenario identifies which named bunkers are presently active.

Bunker sizing `doc_dd46f2c1532c4467a6e6` pp 1–9 includes calculation and review history. P2 states247 t/h per unit at 100%BMCR,4 active+2 standby,12h basis,0.8 t/m³,741t/926.25 m³ per bunker. Keep these as **design-case calculations with applicability**, distinct from present usable volume, coal inventory or level setpoint. Read later replies before choosing dimensions/liner materials. Original units/datum and nominal/inside diameter must remain clear.

Local DE: resolve existing Bunker House DE System with ducting/equipment layout `doc_40568f1cddaf46f08262`, DE schematic/DBR, DE philosophy pp 1–17 and fan/filter/airlock/pulse air sources. Pickup/duct/filter/fan/discharge and differential-pressure/cleaning logic are not the same as DFDS wet suppression. Link common air/electric supplies to P01/P15.

**Acceptance:** both bay scenes clearly show which bunker is being inspected and the known delivery interface; own inlet/vent/level/design-basis evidence is reachable; direct head-end-to-last-bunker mapping is supported or explicitly unresolved. No animated level/current tonnage without dated observations.

## P15

**Electrical, control, fire, access and remaining common infrastructure.** Review the non-process queue and establish a shared-services navigation entry with place/context links rather than stuffing these assets into a coal route.

Power: SLD BIFPCL.PDF, MCC ROOMS, drive schedule, motor data and control pp 6–7,12,30–35. Find feeder/switchgear/starter/VFD/MCC/voltage/earthing information only as the source supports. Locate MCC1–4 against UBA1–4, not UGA. Control I/O list178158 and temperature transmitter180014 are referenced on p35: record whether originals exist; do not substitute setpoint list for I/O wiring.

Fire: retain source-specific stacker fire package and other referenced plant-fire documentation. Search actual detector/cylinder/nozzle/zone/release/abort/interlock logic; preserve missing cause-and-effect and local duty/reserve uncertainty. Do not extrapolate the stacker system to conveyors, yards, silos or bunkers.

Access/maintenance: hoist schedule, manual/electric hoists, elevator GAs, ventilation/AC at MCCs/pump houses, vacuum cleaning, belt vulcanizing, dozer/loader data, common drains and water points. Show documented lifting capacity/reach/use location, not lifting certification or a work permit. Distinguish inventory of maintainable components, manufacturer inspection instructions, QAP manufacturing inspections and dated site maintenance events.

**Acceptance:** an equipment scene can follow a supported power/control/shared-service boundary and return; any missing field/commissioning record is explicit. Every remaining queue record has a disposition; reference-only documents remain searchable. Verify the SLD interpretation independently of motor-rating tables before showing electrical arrows.

## Final integration

After all chosen section batches, follow ship→yard→reclaim→silo→crusher→tripper→bunker and direct-to-silo paths in both streams; inspect every yard, every TP, every main conveyor and every unit interface. Verify deeply nested source opening and return context for each scene family. Cross-check schematic nodes/edges against accepted IDs, conditions and qualifications, including shared utility reuse. Report completed, completed-with-explicit-gaps and deferred targets separately. A visually populated overview alone does not establish model completeness.
