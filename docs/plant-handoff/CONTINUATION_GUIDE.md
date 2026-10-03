# Continue the detailed visual plant model

Reviewed **1 October 2026**, against the live database at **v593**. This is the current entry guide for any agent extending a section. It brings together the existing whole-plant design and the lessons from the accepted pilots. It does not replace the ingestion validator, the original drawings, or the section-specific plans.

For a general “continue” request, use [FIVE_PHASE_PLAN.md](FIVE_PHASE_PLAN.md) and [phase-progress.json](phase-progress.json). The current resume point is Phase 1 / B02; reconcile the pointer and live state each time. See [the current inventory](current/CURRENT_STATUS.md). Use [READY_TO_PASTE_PROMPT.md](READY_TO_PASTE_PROMPT.md) to start a run. The desired result is a coherent, source-backed equipment model that people can explore from plant route to individual maintainable part. Record count, number of tabs and number of drawings searched are not quality targets.

> **Breadth-first execution (from 3 October 2026, v628).** While `phase-progress.json` says `"pass": "A"`, every batch is taken only to the **Tier 1** definition in [FIVE_PHASE_PLAN.md](FIVE_PHASE_PLAN.md#execution-mode-breadth-first-from-v628): identity, route connections, major assemblies one level down, headline ratings, grouped protections, shared-service consumer links, visible scene. The recursive extraction in §5, the full family depth in §6 and exhaustive verification in §10 apply in **Pass B** (the [depth queue](current/depth-queue.json)) or to a batch the user explicitly names for full depth. In Pass A, record deeper items in the depth queue and move on to the next batch. Evidence rules (§7, §9) apply unchanged in both passes.

## 1. Establish what already exists

| Accepted work | Historical acceptance | Read before touching it or its boundaries |
|---|---|---|
| EAC-1A/B and UEF-1 | v466 → v484 | [Equipment pilot](../../EQUIPMENT_PILOT_REPORT.md) |
| Coal Yard 1 and its machines/services | v484 → v510 | [Yard pilot](../../COAL_YARD_1_PILOT_REPORT.md) |
| Blending-silo house, vessels, extractors and KF-3/4 | B30/B31, v510 → v527 | [Silo pilot](../../COAL_BLENDING_SILO_PILOT_REPORT.md) |
| Crusher house, 17A/B, screens, crushers, feeders and local services | B32–B35, v527 → v558 | [Crusher pilot](../../CRUSHER_HOUSE_PILOT_REPORT.md) |
| Conveyor18A/B and TP13 drives, measurements, gates and local services | B36, v558 → v592 | [B36 report](../../B36_CONVEYOR18_TP13_REPORT.md) |

These pilots retain source qualifications and identified follow-up work. Their existence does not complete every planned correction, upstream dependency or common-service batch. In particular, the TP1/Yard1 follow-up packages can still contain work even though their original pilots exist. B30/B31, B32–B35 and B36 must not be recreated from old target cards.

The 179 target cards, inventory JSON/CSV files and many counts in the design package are a **frozen v510 discovery index**. Statements such as “no components”, “zero electrical edges” or “source missing” in that snapshot are not current findings. Reconcile against the live graph, current evidence, pilot reports and batch checkpoints. Never regenerate over the historical inventory just to hide this distinction.

At this review, checkpoints exist for B30–B36 under `output/plant-enrichment/`. Other packages' `not_started` labels are planning status, not proof that they have no accepted facts. Live data, originals, renders and local output artifacts are not supplied by a Git checkout alone. If local artifacts are missing, recover the relevant state from accepted model history and original evidence; do not reconstruct it from remembered pilot numbers.

## 2. Choose and bound the work

Honor the user's named section. If they ask generally to continue without choosing one, resume the saved phase/batch in phase-progress.json and work through the five-phase plan; do not create a new plan and stop. The next coal-flow section after crushing, B36, is accepted at v592. Its TP13 service-legend correction is accepted at v593 and the scene omissions are corrected; see output/plant-enrichment/B36-corrections/checkpoint.md. For a specifically requested downstream continuation, the next candidate is **B37: sampling2 and TP13 access** in Phase 4. This does not override the saved default phase order. Read the B36 report/checkpoint and preserve its qualified B02/B04 service boundaries and completed crusher interfaces.

Write a short scope record: selected batches/tags, reused IDs, upstream/downstream endpoints, shared services, locally required identity decisions, deferred neighbouring work and intended browser journeys. A large requested area may require several sequential source batches, but should remain one coherent deliverable. Do not end after a plan or one easy drawing when the requested section still has independent supported work.

An unfinished global dependency does not automatically require rebuilding the entire plant before a user-selected section. Resolve the relevant boundary from evidence, retain an explicit unresolved boundary where necessary, and record which dependency remains open. Do not create duplicate common assets or claim the global dependency is complete. If a missing identity prevents one branch, finish the independent branches and identify the exact evidence required.

## 3. Read the prepared plan, in this order

1. Current user scope, repository guidance and [OPERATIONS_INGESTION_WORKFLOW.md](../../OPERATIONS_INGESTION_WORKFLOW.md).
2. [DESIGN.md](DESIGN.md): visual experience, ownership/place distinction and network semantics.
3. [FINDINGS.md](FINDINGS.md): relevant identity, scope and source mistakes to resolve before propagation.
4. Your section in [SECTION_PLANS.md](SECTION_PLANS.md), batch in [BACKLOG.md](BACKLOG.md), and relevant cards from [TARGET_INDEX.md](TARGET_INDEX.md).
5. Applicable family checklists in [ASSEMBLY_CONTRACTS.md](ASSEMBLY_CONTRACTS.md), then [EXECUTION.md](EXECUTION.md) for source-scoped acceptance and gates G1–G8.
6. The closest completed pilot report, plus reports for both neighbouring sections. Use [SOURCE_CATALOG.md](SOURCE_CATALOG.md) and its inventory for retrieval, then inspect the actual source.

Do not load all target cards or PDFs indiscriminately. Keep a source queue and a claim ledger outside the conversation so the work survives context loss.

## 4. Design the visual story before filling it

The opening scene should answer, without opening a fact table: **what this is, where it sits, what its major parts are, how they connect, and where material goes next**. Use recognizable equipment forms, relative arrangement and labelled boundaries. A source-backed floor/head/tail position is useful; invented global coordinates are not.

Define at least these journeys for the section:

- Plant → section → machine → drive/working assembly → auxiliary → its individual value → original drawing detail → return to the same assembly.
- Section → incoming/outgoing interface → actual neighbouring equipment, preserving its owner and the selected route condition.
- Section → local dust/water/oil system → application/consumer → shared supply boundary, without duplicating the shared equipment.
- Equipment → protective device → source-stated condition/action and qualification → exact supporting paragraph or diagram.

Major parts should be visible as an arrangement. Deeper parts should be reachable by selecting their parent; do not draw hundreds of nodes at once. The inspector contains specifications and sources on demand. Assembly search is a supporting route, not the only way to discover major auxiliaries. Source close/return must retain the browsing context.

Use a place scene for a TP/building, a motion/assembly scene for a machine, and a process scene for an area. Keep the same canonical identity across them. Illustrative flow/rotation may explain a documented path; it must not imply live telemetry, an approved operating sequence or simultaneous operation of mutually exclusive branches.

## 5. Extract recursively through engineering relationships

For every major component, ask: **what drives it; what supports/lubricates/cools it; what senses/protects it; where does its output go; what can be maintained separately; which drawing proves this?** Follow each answer into the next document rather than stopping at a tag search.

Practical sequence:

1. Use topology/control and layout sources to establish identity, purpose, interfaces and alternatives.
2. Read the exact GA and its schedules/BOM/review replies. Build a component candidate tree and identify source model numbers.
3. Follow those models into vendor GAs, motor/coupling/reducer/brake data, hydraulic/oil circuits, belt/pulley calculations and component schedules.
4. Trace each utility from the actual local branch to its consumer and common source. Review P&ID continuation symbols and distinguish pipe crossings from junctions.
5. Read the equipment-specific control sections, IO/loop/electrical evidence where available, and exact action targets. Keep common control applicability explicit.
6. Inspect maintenance/access/wear/lubricant and replacement information supported by manuals, drawings or records. Retain absent manuals and missing final configuration as specific gaps.
7. Reconcile A/B, numbered-machine, drawing-revision, family and project-total scope. Independently inspect the second stream; do not clone the first stream's facts.

For each candidate source record its document ID, immutable hash, drawing/revision/status, applicable equipment, reviewed pages/regions and disposition. OCR is a search aid. Dense BOMs, table columns, small symbols and line directions require readable original-page inspection including headers and units. Unexamined pages are not “reviewed” just because an API inventories their evidence IDs.

Every discovered child leads to either a reviewed subassembly, already adequate accepted detail, an evidenced not-applicable decision, or a precise missing/ambiguous-source item. A sensible stopping point is a maintainable part or sourced group for which no further supported decomposition is found. Do not split every bolt into a fabricated asset, and do not stop at a generic “drive assembly” while its motor/coupling/pump drawings remain available and unexamined.

## 6. Use the correct section and family depth

The linked section plans contain exact tags, boundaries and source leads. This table defines the visual emphasis and the omission to guard against; it is not permission to assert every listed component exists.

| Section/family | Follow into detail | Essential distinction |
|---|---|---|
| [P02 jetty/unloading](SECTION_PLANS.md#p02) | Each unloader's motion drives, brakes, hoists/trolleys/grab, hopper/shuttle, cable supply, lubrication and dust control; 1AB/2AB and TP1 boundaries | Prove SUL/numbered identities and machine type; shuttle direction and stream selection are conditional |
| All conveyors | Receiving/head/tail, actual drive chain, coupling oil and actuator auxiliaries, reducer, brakes, belt/pulleys/bearings, take-up, cleaners, protection groups | Model-specific drive order; pairs versus switches; component location versus conveyor ownership |
| All TPs/buildings, [P04 distribution](SECTION_PLANS.md#p04), [P09 reclaim](SECTION_PLANS.md#p09) | Incoming/outgoing chutes, gates, discharge/receiving sprays, FAS/PRU/header/nozzles, local panels, sump/drainage, hoists and access | A place exposes located assets without owning copies; each branch and spray zone needs its own applicability |
| [P03 primary screening](SECTION_PLANS.md#p03) | Rod/rack gates, deck/grizzly, exciters/shafts/drives, springs/bearings, both material fractions, dust/access and sampling boundaries | EBD-1–4 are separate from EBD-5/6; undersize, reject and crusher bypass are not interchangeable |
| [P05 Yard1](SECTION_PLANS.md#p05), [P06 Yard2](SECTION_PLANS.md#p06), [P07 Yard3](SECTION_PLANS.md#p07), [P08 Yard4](SECTION_PLANS.md#p08) | Stacking lane → stacker → pile → portal reclaimer → reclaim lane, shed/UAX places, local SPDS/onboard sprays, runoff | Each yard needs its own AP/sector/valve mapping and P&ID sump assignment; common sources remain shared |
| Stackers/reclaimers | Every motion: motor/coupling/reducer/driven part, brake/hold, feedback, lube; hydraulic/hoist/rope/chain/cable subsystems as supported | Maitree pilot reclaimer is portal scraper; do not add a bucket wheel. Structural wind case is not a trip setting |
| [P10 silo](SECTION_PLANS.md#p10) | Vessel versus extractor, rotating working parts, dual drive/common VFD, lubrication/seals, feeder, selectors, level/access/dust | Preserve exact inlet crossovers and distinct extractor/feeder ownership and modes; existing pilot is the reuse baseline |
| [P11 crushing](SECTION_PLANS.md#p11) | Screen/granulator/collection feeder, rotor/rings/cage/bearings, scoop oil, hydraulic opening, foundation, DE/DFDS, airlocks and lifting | Direct bypass, grizzly undersize and crushed paths remain separate; direct crusher drive has no invented reducer |
| [P12 conveyor18/TP13](SECTION_PLANS.md#p12) | Belt drives/protections, metal detection and weighing, FG17/18, local dust/drainage; separate B37 sampler/reject/access assembly | Preserve crusher-side dust returns/sprays; a sample cut is not the main coal path; reconcile SNC-2 elevator identity |
| [P13 conveyor19/trippers](SECTION_PLANS.md#p13) | Conveyor base, travel carriage/drives/clamps/limits, pulleys, cable reel, chute/gate, sealing belt, through/side/head discharge | Unit, handedness, travel range and reachable bunkers are specific; do not connect every tripper to every bunker |
| [P14 bunker bays](SECTION_PLANS.md#p14) | Each A–F vessel, inlet/sealing/liner/access, level/dust/vent and supported outlet boundaries | Shared design must explicitly apply; design volume/BMCR case is not live inventory or current usable capacity |
| Sampling/instruments | Sample/reject/bias paths, sampler/feeder/crusher/collector drives and local control; host/measurement/marker connections | Small sample crusher is not EBC; measuring range is not alarm/trip; calibration record is not current status |
| [P01 shared services](SECTION_PLANS.md#p01), [P15 power/control/access](SECTION_PLANS.md#p15) | Source equipment → treatment/header → local branch → consumer; duty/standby, electrical feeder/starter/VFD and documented controls | One physical common asset; voltage alone does not prove an electrical connection or isolation boundary |

## 7. Apply the pilot's engineering safeguards

Keep component membership, physical location, mechanical drive, material flow, utility supply, electrical feed, measurement, control and design applicability separate. Give every scalar **and relationship** its own exact support and applicability. Descriptive untagged names are allowed; invented field/KKS/cable/spare tags are not.

Worked patterns to preserve, never blindly copy:

- EAC-1A PCS has 14 pairs in its source; EBA-17A has 9 pairs. Derived individual-switch counts stay separate with the formula. Neither value belongs on a new conveyor without its own applicability evidence.
- A crusher motor → PST-1150 coupling → rotor differs from a conveyor motor → coupling → reducer → pulley. The UI must follow the accepted component graph, not force every drive through one icon template.
- Oil-pump flow, pump-motor power and radiator-fan power belong to their respective components. Trace pressure and return/lubrication branches from the actual P&ID; do not manufacture a generic oil loop.
- A local pressure gauge monitors. Its presence does not establish an automatic trip. Motor-bearing, rotor-bearing and coupling-oil temperature conditions have different targets and bases.
- A source-logic claim preserves initiator, polarity, AND/OR clause, threshold/unit, delay, mode, action target, reset and exception where stated. Contradictory wording remains inspectable; it does not become executable logic.
- Silo 6A/6B crossovers, two extractor motors on a common VFD, and the crusher's three material paths are regression anchors. Preserve them when integrating neighbours.
- Source-total DFDS nozzles do not mean simultaneous active sprays. Keep discharge versus receiving applications and system-local tag namespaces separate.
- Yard1 SP-8G/H assignment came from the actual branch, not alphabetic order. AP, sector and solenoid suffixes do not prove a one-to-one map.
- Per-crusher foundations are physical instances; a generic VIS reference is not another foundation. An off-project Rihand document is not a Maitree installed asset.
- Conflicting oil temperatures, timer values, drive models, bag counts or airlock speeds require source-qualified alternatives and the record needed to settle them. “Zero formal conflicts” in the checker does not mean engineering disagreements disappeared.

## 8. Keep a compact, durable work package

Use `output/plant-enrichment/<batch-id>/` (or a clearly cross-linked section folder). Store these as readable JSON/CSV/Markdown, not just conversation notes:

| File/ledger | Required contents |
|---|---|
| `checkpoint.md` | Scope, baseline/current version, completed steps, accepted proposal/version IDs, exact next action and blockers |
| `identities.json` | Candidate ID/tag/alias, reused canonical ID, owner/place, instance-versus-reference decision, source and rationale |
| `coverage.csv` | Target, dimension, status, evidence/accepted claim or gap ID, searches performed, next evidence needed |
| `sources.json` | Document/hash/revision/applicability, actual pages/crops reviewed, used/corroborating/ambiguous/deferred disposition and reason |
| `claims.json` | Subject, predicate/value/unit or object, source supports, origin/basis/conditions, accepted assertion ID or rejection reason |
| `boundaries.json` | Owner/place, upstream/downstream/shared endpoint IDs, network/direction/condition, evidence, neighbour package and unresolved boundary |
| `verification.md` | Source-based expectations, command results, browser journeys/screenshots, regressions, limitations |
| accepted proposals / export | Reproducible source-scoped bodies, version/commit log, final model export; backups recorded separately |

Use the ten coverage dimensions in ASSEMBLY_CONTRACTS. Each cell must say supported, already adequate after recheck, not applicable with evidence, contradictory, illegible, or source not found with a recorded search. “Source missing” must name the drawing/manual/tag mapping sought, where it was searched and which decision it prevents. Available but unread material is deferred work, not a missing-source conclusion.

Checkpoint example (a format, not a statement that a batch has begun):

```text
Batch / targets:
Status: in_progress | review_required | complete | complete_with_gaps
Baseline/current model version:
Reused/new canonical IDs and accepted proposals/versions:
Sources actually reviewed (document, page, region, applicability):
Finished component branches and interfaces:
Unresolved claims; unread/deferred candidate sources and reasons:
Checks completed and their results:
Next action: open [document/page/region], verify [specific question],
             then update [component/relation/scene/test].
```

Existing `implemented_with_source_qualifications` checkpoints mean an accepted implementation with retained source limitations, corresponding to qualified closure. Preserve their wording/history. They are not permission to repeat the migration or evidence that every future enrichment is complete.

## 9. Implement through the existing application

Use read-only SQLite inspection and a consistent backup. Rehearse on a separate copy, keep originals immutable and perform sequential, version-guarded acceptance. Never write canonical tables directly, run concurrent writers, change only the guard to replay stale analysis, or rerun any `enrich_*_pilot.py --apply` migration against a later version.

Read the current `chp/reviewed_ingestion.py`, `chp/patches.py` and `chp/usage_intake.py` contracts. Stage one source document per proposal; the present validator requires every support in that proposal to belong to that document. Cross-document corroboration uses separate accepted claims on reused identities, preserving each basis. Follow EXECUTION.md for intake inventory, visual IDs and proposal limits. Never mark unseen evidence reviewed to satisfy the API.

Keep the UI data-driven:

- `dist/plant-model.js`: accepted graph projection.
- `dist/plant-scene-model.js`: ownership, location, scene selection and boundaries.
- `dist/plant-scene.js` / `.css`: reusable equipment composition and interactions.
- `dist/plant-explorer.js`: detailed browsing/search; `dist/app.js` and `chp/evidence_view.py`: individual evidence display.

A template may position a motor beside a driven machine illustratively. It must not invent the motor, fill a missing rating, or hardcode a pilot's IDs/quantities/topology. Preserve nearest-parent navigation, common service boundaries and source conditions. Maintainable subparts with specific types must not inherit the parent's generic symbol merely because its name contains “crusher” or “coupling”.

## 10. Verify richness, correctness and usability separately

Apply all G1–G8 in EXECUTION.md. Required acceptance evidence includes:

1. A source-to-claim audit of identity, units, quantities, direction, A/B applicability and qualifiers. Check the resulting accepted graph independently of the builder's intended output.
2. Every new part reachable from its correct assembly or place; every common service has one canonical owner; no unintended orphan, cycle, duplicate or silent disappearance of prior facts.
3. A complete main material route and each source-supported bypass/alternative, including both neighbouring boundaries. Highlighting a selected route must not activate mutually exclusive alternatives.
4. At least one deep maintainable auxiliary, grouped count, connection and protection/source discrepancy per applicable target family, each with readable exact evidence. Increase sampling for asymmetric equipment or risky source conflicts; a single happy path cannot validate every target.
5. Actual browser journeys: section overview → major part → subpart → individual fact/source → return; search; neighbouring equipment; shared service; narrow-panel and desktop readability; pan/zoom and optional animation. Screenshots should show the working result, not substitute for interaction testing.
6. Appropriate automated tests and integrity checks, with precise results and limitations. A passing suite alone does not close unused-source or missing-depth work.

Use a working Python interpreter: prefer `.venv/Scripts/python.exe` if it exists, otherwise check `python` and its required imports. The `.venv` was absent on this review date. Typical commands, adapted to the current runtime and changed scope:

```powershell
node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs tests/test_plant_scene_render.cjs
node --check dist/plant-scene.js
node --check dist/plant-scene-model.js
python -m chp.verify --data data/plant
```

Run relevant Python tests when backend behavior changes. Run the crusher/silo semantic audits against a fresh accepted export when their boundaries or shared scene behavior are affected; do not pass an old export and claim a live regression check. Read audit scripts before using them: some write report files even though they do not modify canonical data. Do not overwrite prior pilot evidence unintentionally.

Use the actual running application port. Check the process before starting a server; do not terminate an unknown port owner. Port 8775 was the crusher deliverable, not a permanent configuration promise. Reuse or start an appropriate local server without changing unrelated work.

## 11. Close the run honestly

Deliver the implemented section, a direct app link, source/coverage and discrepancy reports, accepted versions, verification, and the next concrete action. Update that batch's checkpoint and manifest consistently; keep the historical inventory unchanged. Cross-link the new report from the main handoff.

`complete_with_gaps` is appropriate for specifically documented missing/contradictory evidence after available relevant sources have been investigated. It is not appropriate for broken source links, incorrect ownership, a known false control action, a table-only scene, or a major available drawing left unread without an explicit deferral. Those remain `review_required` or `in_progress`.

If the run is interrupted, checkpoint the exact remaining source/component task. The next agent must reconcile live IDs/version and resume there, rather than repeat extraction or restart the design. Preserve unrelated Git changes. Commit Git, publish, message other tasks or delegate only if the user has separately authorized that action.
