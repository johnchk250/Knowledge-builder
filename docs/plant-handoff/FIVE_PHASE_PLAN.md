# Finish the detailed plant model in five phases

Prepared 1 October 2026 from the live **v593** model, all 179 target cards, 47 batch definitions, accepted checkpoints and pilot reports. **Revised 3 October 2026 at v628 to breadth-first execution** (see below). This is the default implementation order for a general **“continue”** request. A specifically named user target still takes priority.

Read [phase-progress.json](phase-progress.json) for the current pass, phase, batch and exact next action. Read [current/CURRENT_STATUS.md](current/CURRENT_STATUS.md) for the live inventory; [current/target-status.json](current/target-status.json) covers all 179 targets. Deferred detail lives in [current/depth-queue.json](current/depth-queue.json). The v510 inventory remains an unchanged historical retrieval index. Checkpoints that used to be appended here are in [history/PLAN_CHECKPOINT_LOG.md](history/PLAN_CHECKPOINT_LOG.md); new checkpoints go into the batch `checkpoint.md` and `phase-progress.json`, **not into this file**.

## Execution mode: breadth-first (from v628)

**Why.** By v628 the model held 68+28 pump/filter/receiver subparts down to O-rings and vent plugs, while 22 of 30 main conveyors and 10 transfer points still had 1–3 records each. Depth-first execution would take far too long to give a usable whole-plant model. From now on, the work goes **across the plant first, then deeper**.

**Two passes over the same 47 batches and dependency order:**

| Pass | What it does | Batch status when done |
|---|---|---|
| **Pass A — backbone (current)** | Walk B02 → B46 in the existing phase order, taking each batch only to **Tier 1** (below). Everything finer goes to the depth queue. | `breadth_complete` |
| **Pass B — depth** | Only after Pass A reaches B46: work the [depth queue](current/depth-queue.json) in priority order (below), not in batch order. | `complete` / `complete_with_gaps` |

A dependency is satisfied for Pass A when the predecessor is `breadth_complete` or better. Accepted pilot packages (B30–B36, and earlier B00/B01) already exceed Tier 1.

### Tier 1 — “breadth-complete” definition

A batch is `breadth_complete` when, from the principal sources (topology/control write-up, layout, the main GA and its schedule/BOM header block, the relevant P&ID sheet):

1. **Identity:** every in-scope target has one canonical identity with correct owner/place, or a recorded identity decision/gap. No duplicates.
2. **Route:** material in/out is connected to the actual neighbouring equipment, both A/B lanes, with branch conditions. Every scoped TP shows its incoming/outgoing conveyors.
3. **Major assemblies, one level down:** e.g. conveyor → drive unit(s) (motor, coupling, reducer, brake as supported), head/tail/take-up pulleys, belt, cleaners, main chute/gates; machine → each motion drive at assembly level; TP/building → chutes, gates, local dust/spray/drain points, hoist.
4. **Headline ratings** stated on the main GA/schedule (capacity, belt width/speed, motor kW, etc.), each with exact evidence.
5. **Protections and controls as groups** (e.g. “PCS — 14 pairs”, “BSS”, “ZSS”) with their source; not every setting or logic clause.
6. **Shared-service consumer links** to the existing canonical common asset (DFDS/SPDS/service water/runoff), not the internals of that asset.
7. **Visible and navigable:** the scene draws the new parts; overview → major part → source → return works.

**Not Tier 1 — record in the depth queue instead:** vendor BOM rows below a maintainable assembly (O-rings, plugs, spacers, seals, sleeves), pump/compressor/reducer internals, numeric protection/setting tables, detailed control logic clauses, revision-to-revision reconciliation beyond identity, motor-source hunting for a single rating, exhaustive per-claim browser verification. A depth item needs: target ID, what is missing, the exact source/page that would supply it, and a priority (P1–P3).

### Pass A budget and stop rules

- **Target ≤ 3 accepted proposals per batch** (one source document per proposal remains the API rule). If Tier 1 needs more, record why in the checkpoint and continue; never use the budget as a reason to leave a broken route or false identity.
- **Do not open vendor manuals or BOM detail sheets in Pass A** unless the headline rating or identity exists only there.
- When a batch reaches Tier 1, **stop that batch**: write the depth items, mark `breadth_complete`, advance the pointer and **start the next batch in the same run**. A “continue” invocation should normally move through several batches.
- Evidence rules are unchanged: immutable originals, claim-level evidence, applicability, isolated rehearsal, guarded sequential acceptance, no invented tags/values, preserved disagreements. Breadth-first changes **how far** a batch goes, never **how carefully** a claim is supported.

### Pass A verification (sampled, not exhaustive)

Per batch: fresh integrity/FK (`chp.verify`), Node scene tests, pilot audits when a pilot boundary is touched, preservation check. Browser: every new **major** component is drawn and selectable; at least one source-open/return per source document used; one narrow-width journey; the batch's route visible end to end. Exhaustive per-claim browser checks move to Pass B and B46.

### Pass B priority order

1. **P1:** drives and protections of main-route equipment (conveyors, crushers, unloaders, stacker/reclaimers, trippers), and known source disagreements that affect operation.
2. **P2:** maintainable auxiliaries operators actually service (lube/hydraulic circuits, brakes, take-ups, cleaners, sprays, dust collectors), electrical feeder/starter detail.
3. **P3:** vendor BOM rows, spare-part level groups, revision reconciliation, accepted-pilot thin targets (CV-5/6, FG-15A/B, etc.).

## Current position (v628, 3 October 2026)

- **Accepted with qualifications:** B00, B01 and B30–B36 (EAC-1A/B and TP1 pilot; Yard1 pilot; silo B30/B31; crusher B32–B35; conveyor18/TP13 B36). Do not replay their enrichment migrations.
- **B02 (in progress, Pass A):** the DFDS station front ends, receivers, filters, pumps, pump controls and compressor qualifications are already beyond Tier 1. **Only one Tier-1 item remains:** connect the existing common air/water outlet headers to the TP1 local mains and the TP13 inlet via UEE-3 (B02 exit check: two TPs trace to one common source). Compressor internals/protection-table reconciliation, model-to-unit mapping and source 180055 are moved to the depth queue.
- **22 of the 30 main conveyors still need Tier-1 work:** EAC-2A/B, 3A/B, 4A/B, 5A/B, 9, 11, 13; EBA-6A/B, 10, 12, 14, 15A/B, 16A/B, 19A/B.
- **Ten other in-scope transfer points need Tier-1 local detail:** UEF-3 through UEF-12. UEF-2 and TP16–18 are source-qualified utility reference boundaries from B00.
- **Major remaining assemblies:** three ship unloaders; primary screening; distribution dividers/fixed trippers; Yards 2–4; reclaim transfer; both sampling packages; conveyor19/four travelling trippers; two bunker bays/twelve bunkers; common utilities, power/control, fire/HVAC/access and final integration.
- At v628 the projection has **645 non-reference records outside the nine process areas** and **10 documented electrical edges**. These are review diagnostics, not completeness measures.
- **Accepted-package depth checks** (CV-5/CV-6, FG-15A/FG-15B thin targets) are Pass B P3 items; see [the follow-up queue](current/accepted-followups.json).

## Phase overview

| Phase | Batches in execution order | Usable outcome at end of Pass A |
|---|---|---|
| **1. Correct identities and connect common services** | B00 → B01 → B02 → B03 → B04 → B05 | Stable identities; common air/water/runoff sources connected to their consumers; TP1 boundaries rechecked |
| **2. Complete unloading, screening and distribution** | B06 → B07 → B08 → B09 → B10 → B11 → B12 → B13 → B14 | Three unloaders through primary screening to all yard inlets and direct silo feed |
| **3. Complete all yards and reclaim routes** | B15 → B16 → B17 → B18 → B19 → B20 → B21 → B22 → B23 → B24 → B25 → B26 → B27 → B28 → B29 | Four stacking/reclaiming areas and reclaim-to-silo connections |
| **4. Finish TP13 sampling and bunker delivery** | B37 → B38 → B39 → B40 → B41 → B42 | Sampling/reject at TP13, conveyor19, four trippers, both bunker bays |
| **5. Complete plant-wide systems and release review** | B43 → B44 → B45 → B46 | Electrical/control feeders mapped to consumers, common infrastructure, record disposition, whole-plant route walk |

These are five delivery phases, **not five single proposals**. Dependencies in [batches.json](batches.json) remain authoritative. All cross-phase dependencies point backward or to an accepted B30–B36 package. Recheck affected accepted boundaries before using them.

**Pilot follow-up batches in Pass A (B05, B15, B16):** the pilots already exceed Tier 1. In Pass A do only an identity/boundary recheck against neighbouring Tier-1 work (target: one session, zero or one proposal), record their follow-ups as depth items, and mark `breadth_complete`.

## Phase 1 — identities, common services and TP1

Use section P00/P01/P02 in [SECTION_PLANS.md](SECTION_PLANS.md), findings F01–F05/F13/F15/F18 and the existing TP1/Yard1/B36 reports.

1. **B00 (accepted):** UGA-1/2 labels, TP1 GA availability, SUL versus numbered unloader identity, UEF-2/TP16–18 boundaries.
2. **B01 (accepted):** shared pump houses, grouped/individual pumps, compressors and tanks; canonical shared-service ownership and 26-row consumer-boundary ledger.
3. **B02:** common **DFDS air and water**. Tier 1 remaining: connect the common headers to at least two local consumers (TP1 local mains, TP13 inlet via UEE-3).
4. **B03:** **SPDS, service and potable water** — source equipment → header → consumer branches at Tier 1; preserve pump-name/head and AP/sector/SV mapping disagreements.
5. **B04:** **sumps, runoff pond and feed-water return** — source-specific pit/pump assignments and destinations.
6. **B05:** TP1 boundary recheck against B02/B04 (Pass A); GA hoist/access/tank detail is depth.

Start sources: control write-up `doc_4f2cd96c3b1e413ea4b5` pp55–56; DS pump-house GAs `doc_af4f437e54f143af9f62` / `doc_d0cb76dd3ab3478295db`; TP1 GA `doc_71a0d8fc66304e93b9c1` pp1–2; DFDS P&ID `doc_bca09d68af9b43e3b633`; SPDS P&ID `doc_5a36f2843d504d6e96de`; sump/runoff P&ID `doc_0453a0a014424f1cae06`. Source titles alone do not prove asset identity.

**Pass A exit:** corrected identities or recorded decisions; no duplicate common supplies; two-area consumer → source journeys for DFDS, SPDS and runoff; TP1 boundaries consistent. Create an early electrical/source inventory for B43 without claiming power-network closure.

## Phase 2 — jetty to distribution and direct silo feed

Use P02–P04 and the conveyor, unloader, screen, sampling, transfer and measurement contracts.

- **B06:** EAC-2A/B and screening inlet, including relevant AT-1/2, QB-1/2 and EAT-1/2 interfaces; reuse TP1 chutes.
- **B07/B08:** identity and Tier-1 assemblies of all three unloaders: travel, hoist/trolley/grab, hopper/shuttle, main drives, cable reel, dust control; respect Type1/Type2 and unit applicability.
- **B09/B10:** UEE-1, EBD-1–4, rod/rack gates and reject routes; EAC-3A/B and TP3 dividers/selectors.
- **B11:** sampling1 at UEF-3: sample, bias and reject-return routes and major units.
- **B12/B13:** EAC-4A/B and EAC-5A/B, UEF-4/5/6, fixed trippers/dividers and branches to Yards 1–3; show through-flow along one continuous belt.
- **B14:** EBA-6A/B, UEF-7, CV-1/2 and the exact 6A→EBB-2 / 6B→EBB-1 crossover.

Source starts are indexed under P02–P04: exact conveyor and TP GAs, unloader Type1/Type2 GA/DBR drawings, primary-screen GA, sampling1 GA `doc_404c8747ba8047ab8f12`, control pp4–14/18–21/27–29/35–43/49–56 as applicable.

**Pass A exit:** each numbered unloader and both conveyor lanes navigable to primary screening, four yard inlets and direct silo boundaries; branch conditions retained; primary screens never merged with crusher-house screens.

## Phase 3 — four yards and reclaim to silos

Use P05–P09. Preserve Yard1's accepted model.

- **B15/B16:** Yard1 boundary recheck and numbered-machine applicability matrix (Pass A); residual machine/safety/lube detail is depth.
- **B17–B19:** Yard2: EAC-9, EAD-2, EAE-2, EAF-2, EBA-10, UEB-2, UAX-2/6 and its own services.
- **B20–B22:** Yard3: EAC-11, EAD-3, EAE-3, EAF-3, EBA-12, UEB-3, UAX-3/7 and its own services.
- **B23–B25:** Yard4: EAC-13, EAD-4, EAE-4, EAF-4, EBA-14, UEB-4, UAX-4/8 and its own services.
- **B26/B27:** UEF-8/9/10/11, FG-7–10 and each receiving, dust and drainage branch.
- **B28/B29:** EBA-15A/B, UEF-12, FG-11/12, AT-3/4; EBA-16A/B, CV-3/4 and the exact 16A→EBB-1 / 16B→EBB-2 interfaces.

Confirm each yard's local branch rather than copying Yard1 quantities or sump pair.

**Pass A exit:** four yard journeys from stacking inlet through stockpile/reclaimer to reclaim delivery; machines at motion-drive assembly level; all four yard outlets trace to the accepted silo inlets.

## Phase 4 — TP13 sampling, trippers and bunkers

Use P12–P14 and reuse B36's corrected v593 interfaces.

- **B37:** sampling2 primary samplers, feeder/bias bin, sample crusher, secondary sampler/collector, reject conveyor and returns to 19A/B; reconcile SNC-2 versus the generic TP13 elevator.
- **B38:** EBA-19A/B drives, protections and tripper interfaces.
- **B39/B40:** TT-1/3 Unit1 and TT-2/4 Unit2 travel/drive/chute/discharge at Tier 1, with per-unit reachable bunkers.
- **B41:** both bunker bays and all twelve A–F vessels: design sizing, inlet/outlet boundaries. No design capacity promoted to current inventory.
- **B42:** bunker dust extraction and local/shared-service integration.

Start B37 at sampler GA `doc_98b9805fdd334190a93f`, TP13 GA `doc_a9043e95d82c40f399ec` pp1/3, and control pp22–23/53–55. Tripper source starts at `doc_1217799da7124df5bbe5`.

**Pass A exit:** sample/reject logic distinct from main coal flow; no duplicated elevator; tripper → bunker paths per unit; B36 interfaces intact.

## Phase 5 — common infrastructure, remaining records and whole-plant acceptance

- **B43:** SLD `doc_c3a502c5677443c59183`: MCC/feeder/starter/VFD mapping to actual consumer IDs. Motor voltage alone is not a supply edge.
- **B44:** fire/HVAC, hoists/elevators, workshop and common access infrastructure at Tier 1.
- **B45:** disposition of unplaced/reference/placeholder records; do not place or delete records automatically.
- **B46 (Pass A):** whole-route walk ship → yard → reclaim → silo → crusher → tripper → bunker plus direct silo feed, both lanes and every branch, at Tier 1. **Then switch `pass` to `B`** and work the depth queue.

**Final exit (after Pass B):** no broken source link, silently omitted modeled major part, known false source interpretation, unowned component or unreviewed available critical source. Every target/dimension has a supported/not-applicable result or a specific evidence gap. Completion means the available-source design model is finished, not field commissioning.

## How “continue” resumes

1. Read this plan, `phase-progress.json` (check `execution_mode` and `pass`), `CONTINUATION_GUIDE.md` and the current batch checkpoint. Check the live model version and unfinished proposals. Never assume v628 is still current.
2. **Pass A:** resume `active_phase` / `next_batch`. Do only the remaining Tier-1 items, record everything finer in `current/depth-queue.json`, mark the batch `breadth_complete`, and move to the next dependency-ready batch in the same run. Do not produce another plan and stop.
3. **Pass B:** pick the highest-priority open depth items, grouped by source document; close them with the full G1–G8 gates.
4. After every accepted batch update `batches.json`, the batch `progress.json` / `checkpoint.md`, `phase-progress.json` (pointer, versions, verification, next action) and the depth queue. Refresh the current inventory from a fresh read-only snapshot. **Commit the repository docs/tools changes to Git** after each accepted batch (data/output stay untracked).
5. A phase is `breadth_complete` when all its batches are; advance the pointer. A request naming several phases authorizes continuation through them.
6. An unresolved field record blocks promotion of that claim, not independent work. A false identity, broken route/source or unread **principal** drawing prevents a batch reaching Tier 1.

Every source package still uses immutable originals, exact claim-level evidence, applicability, consistent backup, isolated rehearsal and sequential guarded stage/validate/commit. Change canonical facts only through supported correction APIs. Renderer-level tests must check that modeled located equipment is really drawn.

**Next action:** see `next_action` in [phase-progress.json](phase-progress.json).
