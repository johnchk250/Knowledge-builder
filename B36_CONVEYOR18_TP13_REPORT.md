# B36 — conveyor18 and TP13 implementation

**Follow-up, 1 October 2026:** [review corrections](output/plant-enrichment/B36-corrections/checkpoint.md) accepted at **v593** fix the TP13 GK/PC legend and expose both chutes, SNC-2 and source-linked level context in the scene. The v592 acceptance records below remain historical. Default continuation follows [the five-phase plan](docs/plant-handoff/FIVE_PHASE_PLAN.md).

Acceptance: model **v558 → v592**, 1 October 2026. Status: **complete_with_gaps**; final verification gates are recorded. Scope is EBA-18A/B, UEF-13, FG-17/18, QB-3/4, EAT-3/4 and their local services. B37 sampling, elevator and access expansion remains a separate batch.

Open [TP13](http://127.0.0.1:8775/#overview?area=bunkerfeed). Select the incoming lane and receiving conveyor, then open a drive, gate or local service. The model is a documented design; route animation is illustrative. Source selection retains the current assembly when closed. The detail display strengthens faint source ink; original PDFs remain unchanged.

## What became usable

Each conveyor has its own motor → Premium PST-570 scoop coupling → B3-500 reducer → RG-12 low-speed coupling → head-pulley drive. Coupling detail includes the oil sump, strainer, isolation valve, 150 L/min pump and its 2.2 kW motor, cooler and its 0.55 kW fan, filtration, scoop actuator, instrumentation and separately qualified alarm/trip actions. Reducer, brake and geared-coupling drawings supply the next maintainable level, including bearings, seals and lubrication interfaces. The main motors are 500 kW; no crusher motor/rating was copied.

Belt/mechanical detail includes the 1400 mm belt, head/snub/tail/bend/take-up and deflector groups, shaft/bearing selections, gravity take-up, 32 mm rope, 14,000 kg counterweight design, idler groups, skirt/deck, Hardox discharge-chute interfaces and three distinct scrapers. GA and supplier count differences remain visible. Protection retains **16 PCS pairs** and **12 BSS pairs** per conveyor, with separate derived device counts; ZSS is distinct from belt-weigher speed sensing. Family design details do not establish installed addresses or cam settings.

QB-3/4 expose the tandem probe, SQTA electronics, sandbag marker, interlock, reset/indication and alarm, with measurement/control connections and source-qualified sensitivity and terminal mapping. EAT-3/4 expose the four-idler bridge, four load cells, check rods/frame, calibration supports, summing box, tail-driven 60-12C sensor and its shaft/arm/spring/stop, Micro-Tech9101 integrator and local rate/totalizer. Signals reach the existing DCS; input voltage does not invent a plant feeder.

FG-17/18 expose casing/flap/shaft, EN8/C40 shaft, SKF22230CCK/W33/H3130 bearings and housings, felt seals, inspection doors, actuator and 7.5 kW motor, handwheel/trunnion and travel/thrust/interlock devices. REV selects19A and FWD selects19B. The scene selects one branch; control modes and anti-jam timer disagreements stay descriptive.

TP13 is a place containing its local services and exposing located conveyor-owned head drives/chutes/gates. The desktop illustration shows both lanes; the narrow illustration keeps the selected route readable with selectors for alternatives. Shared and neighbouring equipment remains reachable outside the local assembly.

## Service and preservation boundaries

The local DFDS reuses System-2, PS-03 and the existing UEF13 FAS/PRU11–16. Air/water continuation comes from UEE-3; a local 200 L receiver, six independent FAS/PRU assemblies, headers/gauges/nozzle groups and LCP-03 are connected. A data-driven supply overview shows each FAS→PRU→application chain, with exact connection sources and qualified destinations. AP11–16 carry4/9/9/4/9/9 nozzles, **44 design total**, with distinct discharge/receiving destinations. This is not a simultaneous operating total. Piping/P&ID destination disagreements are retained.

Service water reaches local 32NB hose points through the existing shared system. Potable water reaches the 300 L roof tank through its shared boundary. No common pump, feeder or isolation tag is invented. SP-2A/B are independently modeled as7.5 kW Flowmore pumps with shaft/impeller, cutless bushes, self-water line, thrust lubrication and 7311/6011 bearing support. The pump illustration follows motor, coupling, thrust support, shaft, impeller and suction, with lubrication and column support alongside. Their65NB discharge reaches the 30 m3 intermediate sump near UEF-1 and existing SP-4A/4B, not an invented direct LHP-pond connection.

All **14,098 baseline assertions and 2,326 identities** are preserved exactly. Crusher dust returns, screen/crusher/bypass routes and existing sampling assertions are unchanged. B02/B04 are resolved only at the relevant local boundaries; neither global batch is declared complete.

## Source qualifications

The package adds 1,756 assertions and 362 identities, using 29 original documents across 34 documented source dispositions and 34 sequential accepted proposals. Every addition has individual evidence and applicability. These counts are an audit description, not a depth/completion score. Exact reviewed pages/regions, original hashes, source revisions and semantic versus inventory-only review are recorded in [sources.json](output/plant-enrichment/B36/sources.json); [claims.json](output/plant-enrichment/B36/claims.json) resolves each claim to its exact source links.

The 67 added gap/disagreement records include gearbox thermal rating 633 kW at 50°C versus 905 kW with no ambient basis; EBTF/EBTM brake selection and rating; GA/idler and nonmagnetic quantities; shaft/calculation differences; profile/skirt/deflector calculation inputs; seal-plate printing; detector speed/sensitivity/IO; DFDS receiving assignments; gate timing/CBS polarity; and 5 m3 depicted sump versus 10 m3 revision response. Nominal28.4 versus exact29.2 gear ratio is an explicitly documented distinction.160 kgf-m assumed brake torque is a calculation input, not an installed adjustment.

Resolution requires final vendor selection/BOM, as-built civil and piping drawings, nameplates, shaft fits, loop/feeder records, commissioning settings, calibration and approved maintenance records. Vendor guidance is identified separately from plant PM schedules. See [uncertainties.json](output/plant-enrichment/B36/uncertainties.json) and the 90-cell [coverage.csv](output/plant-enrichment/B36/coverage.csv).

## Verification and continuation

See [verification.md](output/plant-enrichment/B36/verification.md) for final integrity, semantic/preservation audits, tests, evidence API and actual browser journeys. The 36 Node tests pass. Python discovery has 73 passing executable tests and one unrelated import error for the absent `triple_model_session` package; full discovery is not clean. The consistent baseline backup, proposal bodies, accepted version/hash log and fresh final snapshot are in [the B36 checkpoint](output/plant-enrichment/B36/checkpoint.md).

Next bounded work is **B37**: first inspect sampling GA `doc_98b9805fdd334190a93f`, TP13 GA175047 pp1/3 and control pp22–23/53–55; reconcile existing EAU-2/sampling/elevator/SNC-2 identities before modeling sample/bias/reject/slide-gate returns and access. Reuse B36 local services and preserve the main coal routes. Do not replay either B36 acceptance script.
