# Whole-plant implementation handoff

**Current entry point, reviewed 1 October 2026:** read [CONTINUATION_GUIDE.md](docs/plant-handoff/CONTINUATION_GUIDE.md) and use [READY_TO_PASTE_PROMPT.md](docs/plant-handoff/READY_TO_PASTE_PROMPT.md). The live database was checked at v593. For the default five-phase finish plan and saved next action, use [FIVE_PHASE_PLAN.md](docs/plant-handoff/FIVE_PHASE_PLAN.md) and [phase-progress.json](docs/plant-handoff/phase-progress.json). The guide reconciles the completed pilots, gives recursive extraction and visual acceptance requirements, and explains how to use the historical inventories safely. Recheck the live version at the start of every implementation run.

Prepared 20 September 2026 against accepted **model v510**. This is the design and review handoff for extending the visual plant model with GPT-5.6 Sol or another agent. Canonical plant data and application behaviour were not changed by this review.

**Implementation checkpoint, 20 September 2026:** the user subsequently selected the coal blending silo for implementation. **B30/B31 are implemented with documented source qualifications at v527.** Read [the silo report](COAL_BLENDING_SILO_PILOT_REPORT.md) and `output/plant-enrichment/B30/checkpoint.md` / `B31/checkpoint.md` before planning a follow-up. The inventories below remain the frozen v510 baseline; they are not current completion status. Other backlog packages are not marked complete by the silo work.

**Crusher-house checkpoint, 29 September 2026:** P11 / B32–B35 are implemented with source qualifications at **v558**. Read [the crusher-house report](CRUSHER_HOUSE_PILOT_REPORT.md) and the B32–B35 checkpoints before continuing. This includes EBA-17A/B, EBD-5/6, EBC-1/2, KF-1/2, local DE/DFDS, lifting/elevator and service boundaries. Current completion is recorded separately from the frozen v510 inventories.

**B36 checkpoint, 1 October 2026:** EBA-18A/B, UEF-13, FG17/18, QB3/4, EAT3/4 and local dust/water/drainage are implemented with explicit source gaps at **v592**. Read [the B36 report](B36_CONVEYOR18_TP13_REPORT.md) and `output/plant-enrichment/B36/checkpoint.md`. All v558 crusher and sampling assertions are preserved. Relevant B02/B04 boundaries are locally resolved/qualified; global services remain open. B37 sampling/access remains a separate run.

The next agent should **extend the existing visual model one connected section at a time**, with source-backed assemblies beneath it. The architecture, boundaries, investigation order, known pitfalls and completion checks are specified here; individual engineering claims still require examination of their original source.

## Start here

1. Read [the current continuation guide](docs/plant-handoff/CONTINUATION_GUIDE.md), then [the design contract](docs/plant-handoff/DESIGN.md).
2. Read [the findings and correction priorities](docs/plant-handoff/FINDINGS.md), especially F01–F06.
3. Reconcile checkpoints and the live model before choosing work from [the ordered backlog](docs/plant-handoff/BACKLOG.md). Without a user-selected section, the original dependency order begins with **B00, then B01**. For an explicitly selected section, resolve its relevant identity/service boundaries as described in the continuation guide; do not recreate completed pilots or claim unfinished global dependencies complete.
4. For the chosen batch, open its [section plan](docs/plant-handoff/SECTION_PLANS.md) and [individual target cards](docs/plant-handoff/TARGET_INDEX.md).
5. Follow [the assembly contracts](docs/plant-handoff/ASSEMBLY_CONTRACTS.md) and [execution and acceptance protocol](docs/plant-handoff/EXECUTION.md).

Use [this ready-to-paste prompt](docs/plant-handoff/READY_TO_PASTE_PROMPT.md) to start the next agent. The older SOL_START_PROMPT entry points to the same current instructions.

## What this review established

The snapshot contains 266 documents, 5,196 evidence blocks and 1,660 active canonical records. The application treats 1,461 as equipment/non-reference records. **600 are outside its nine process areas**, including generic designs, shared services and locally named equipment with missing placement relations. This is a review queue, not a finding that all 600 should be placed in the process diagram.

The handoff covers **30 main conveyors, all 12 in-scope transfer points, four yard branches, ship unloading, screening, silos, crushing, bunker feed, all four travelling trippers, both bunker bays and their 12 bunkers**, plus shared services and boundary references. There are 179 named target cards; their record counts describe the historical v510 graph, not physical device counts or completion percentages.

Important findings include an incorrect UGA “Dozer Shed” label, an obsolete TP-1 “GA not found” assertion, separate ship-unloader identities, unconnected local DFDS equipment, and missing electrical-network coverage. Specific evidence and actions are in the findings register. These have been **identified for controlled correction**, not silently edited during the planning pass.

## Package contents

| Need | File |
|---|---|
| Current progress, depth standard and end-to-end continuation method | [CONTINUATION_GUIDE.md](docs/plant-handoff/CONTINUATION_GUIDE.md) |
| Model-independent starter prompt | [READY_TO_PASTE_PROMPT.md](docs/plant-handoff/READY_TO_PASTE_PROMPT.md) |
| Visual and information architecture | [DESIGN.md](docs/plant-handoff/DESIGN.md) |
| Exact section work and interfaces | [SECTION_PLANS.md](docs/plant-handoff/SECTION_PLANS.md) |
| Investigation depth by equipment family | [ASSEMBLY_CONTRACTS.md](docs/plant-handoff/ASSEMBLY_CONTRACTS.md) |
| Ordered bounded batches and dependencies | [BACKLOG.md](docs/plant-handoff/BACKLOG.md), [batches.json](docs/plant-handoff/batches.json) |
| Baseline tags, IDs, trees, source pages and connections to reconcile | [TARGET_INDEX.md](docs/plant-handoff/TARGET_INDEX.md) |
| Original document discovery | [SOURCE_CATALOG.md](docs/plant-handoff/SOURCE_CATALOG.md), [sources.json](docs/plant-handoff/inventory/sources.json) |
| Every v510 canonical record, including unplaced records | [record-review-queue.csv](docs/plant-handoff/inventory/record-review-queue.csv) |
| Coverage dimensions to finish for every target | [coverage.csv](docs/plant-handoff/inventory/coverage.csv) |
| Exact v510 network assertions and supports | [connections.json](docs/plant-handoff/inventory/connections.json) |
| The 85 explicit gap/disagreement assertions recorded at v510 | [existing-qualifications.json](docs/plant-handoff/inventory/existing-qualifications.json) |
| Worked examples, evidence rules and release gates | [EXECUTION.md](docs/plant-handoff/EXECUTION.md) |
| What was actually reviewed and what was not | [REVIEW_LOG.md](docs/plant-handoff/REVIEW_LOG.md) |

The generated inventories are baseline observations. Keep implementation progress separately; refreshing an inventory must not erase batch decisions. Live data under `data/plant` is local and not supplied by a Git checkout alone. An agent needs that database, its immutable originals/renders and the application repository.

This plan reduces the architectural decisions Sol needs to make. It cannot establish an installed configuration, resolve a contradictory drawing, or guarantee another model's judgement without source review and the prescribed checks.
