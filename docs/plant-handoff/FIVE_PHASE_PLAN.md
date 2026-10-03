# Finish the detailed plant model in five phases

Prepared 1 October 2026 from the live **v593** model, all 179 target cards, 47 batch definitions, accepted checkpoints and pilot reports. This is the default implementation order for a general **“continue”** request. A specifically named user target still takes priority.

Read [phase-progress.json](phase-progress.json) for the current phase, batch and exact next action. Read [current/CURRENT_STATUS.md](current/CURRENT_STATUS.md) for the live inventory; [current/target-status.json](current/target-status.json) covers all 179 targets. The v510 inventory remains an unchanged historical retrieval index.

## Current position

- **Corrections finished:** TP13 service legend corrected through reviewed retirement/replacement at v593; both conveyor-owned discharge chutes now appear in the transfer scene; documented +68.000 m / +52.000 m levels have a direct source button. Existing SNC-2 is reachable as located equipment. Its identity/detail expansion remains B37.
- **Accepted assemblies to reuse:** EAC-1A/B and TP1 pilot; Yard1 pilot; silo B30/B31; crusher B32–B35; conveyor18/TP13 B36. They retain qualifications and follow-up work. Do not replay their enrichment migrations.
- **Nine batches accepted with qualifications:** B00, B01 and B30–B36. **Thirty-eight remaining batches**, including pilot follow-ups, are assigned exactly once below. This is not a percentage-complete estimate.
- **22 of the 30 main conveyors still need their detailed implementation batches:** EAC-2A/B, 3A/B, 4A/B, 5A/B, 9, 11, 13; EBA-6A/B, 10, 12, 14, 15A/B, 16A/B, 19A/B. Existing eight conveyor implementations require preservation and their stated follow-ups.
- **Ten other in-scope transfer points need local detail:** UEF-3 through UEF-12. TP1 needs its found GA/place follow-up; TP13 needs B37 sampling/access. UEF-2 and TP16–18 are source-qualified utility reference boundaries from B00.
- **Major remaining assemblies:** all three ship unloaders after identity reconciliation; primary screening; distribution dividers/fixed trippers; Yard1 residual machine work and Yards2–4; reclaim transfer; both sampling packages; conveyor19/four travelling trippers; two bunker bays/twelve bunkers; common utilities, power/control, fire/HVAC/access and final integration.
- The current projection at v628 has **645 non-reference records outside the nine process areas**, and **10 documented electrical edges**. Those are review diagnostics: shared assets may correctly sit outside a coal-flow area, and ten edges do not establish plant-wide feeder coverage.
- **Accepted-package depth checks remain:** CV-5/CV-6 each have five direct facts and no owned children; FG-15A/FG-15B each have twelve direct facts and no owned children. Review their original sources and accepted scope in B45. These counts identify follow-up candidates; they do not establish that additional parts exist. See [the follow-up queue](current/accepted-followups.json).

This review reconciled the current graph and recorded scope. It did not repeat every original-document extraction. Source availability, applicability and missing-depth decisions must be checked within each batch. An accepted batch with a thin target is a follow-up candidate, not permission to fabricate parts.

## Phase overview

| Phase | Batches in execution order | Usable outcome |
|---|---|---|
| **1. Correct identities and connect common services** | B00 → B01 → B02 → B03 → B04 → B05 | Stable equipment identities, common air/water/runoff paths and completed TP1 pilot follow-up |
| **2. Complete unloading, screening and distribution** | B06 → B07 → B08 → B09 → B10 → B11 → B12 → B13 → B14 | Three unloaders through primary screening to all yard inlets and direct silo feed |
| **3. Complete all yards and reclaim routes** | B15 → B16 → B17 → B18 → B19 → B20 → B21 → B22 → B23 → B24 → B25 → B26 → B27 → B28 → B29 | Four independent stacking/reclaiming areas, shared services and reclaim-to-silo connections |
| **4. Finish TP13 sampling and bunker delivery** | B37 → B38 → B39 → B40 → B41 → B42 | Sampling/reject/access at TP13, conveyor19, four trippers, both bunker bays and local dust services |
| **5. Complete plant-wide systems and release review** | B43 → B44 → B45 → B46 | Supported electrical/control and common infrastructure, disposition of remaining records, verified whole-plant journeys |

These are five delivery phases, **not five single proposals or a promise of five short chat turns**. Each phase contains bounded, source-scoped batches with durable checkpoints. Dependencies in [batches.json](batches.json) remain authoritative. All cross-phase dependencies point backward or to an accepted B30–B36 package. Recheck affected accepted boundaries before using them.

## Phase 1 — identities, common services and TP1

Use section P00/P01/P02 in [SECTION_PLANS.md](SECTION_PLANS.md), findings F01–F05/F13/F15/F18 and the existing TP1/Yard1/B36 reports.

1. **B00:** resolve UGA-1/2 pump-house labels; correct the obsolete “TP1 GA not found” statement; decide SUL versus numbered Coal Ship Unloader identity/applicability; retain UEF-2 and TP16–18 as qualified boundaries until source scope is proven. Check GK/PC/HDD interpretation on affected local service records using the same legend, without broad unreviewed replacement.
2. **B01:** reconcile shared pump houses, grouped/individual pumps, compressors and tanks. Establish canonical shared-service ownership and a consumer-boundary ledger.
3. **B02:** complete common **DFDS air and water** production/treatment/headers and trace at least two local consumers to the same common asset.
4. **B03:** complete **SPDS, service and potable water** supply; preserve pump-name/head and AP/sector/SV mapping disagreements.
5. **B04:** complete **sumps, runoff pond and feed-water return** routing with source-specific pit/pump assignments and destinations.
6. **B05:** extend TP1 from its found GA, hoist/access/tank details and review replies; recheck existing 1AB drive/protection/DFDS and receiving interfaces. Do not rebuild the pilot.

Start sources: control write-up `doc_4f2cd96c3b1e413ea4b5` pp55–56; DS pump-house GAs `doc_af4f437e54f143af9f62` / `doc_d0cb76dd3ab3478295db`; TP1 GA `doc_71a0d8fc66304e93b9c1` pp1–2; DFDS P&ID `doc_bca09d68af9b43e3b633`; SPDS P&ID `doc_5a36f2843d504d6e96de`; sump/runoff P&ID `doc_0453a0a014424f1cae06`. Retrieve original pages via the existing source catalog. Source titles alone do not prove asset identity.

**Exit:** corrected identities or specific source-backed unresolved decisions; no duplicate common supplies; two-area consumer→source journeys; TP1 own/located boundaries and deep source-return navigation; pilot regressions pass. Create an early electrical/source inventory for later B43, but do not declare power-network closure.

## Phase 2 — jetty to distribution and direct silo feed

Use P02–P04 and the conveyor, unloader, screen, sampling, transfer and measurement contracts.

- **B06:** EAC-2A/B and screening inlet, including relevant AT-1/2, QB-1/2 and EAT-1/2 interfaces; reuse TP1 chutes.
- **B07/B08:** resolve and detail all three unloaders: travel, hoist/trolley/grab, hopper/shuttle, drives/brakes/lube/cable/dust and access, respecting Type1/Type2 and unit applicability.
- **B09/B10:** UEE-1, EBD-1–4, rod/rack gates and reject routes; EAC-3A/B and TP3 dividers/selectors/local services.
- **B11:** sampling1 at UEF-3, including normal sample, bias and reject-return routes, small drives and controls.
- **B12/B13:** EAC-4A/B and EAC-5A/B, UEF-4/5/6, fixed trippers/dividers and branches to Yards1–3. Show through-flow along one continuous belt.
- **B14:** EBA-6A/B, UEF-7, CV-1/2 and the exact 6A→EBB-2 / 6B→EBB-1 crossover.

Source starts are indexed under P02–P04: exact conveyor and TP GAs, unloader Type1/Type2 GA/DBR/detail drawings, primary-screen GA, sampling1 GA `doc_404c8747ba8047ab8f12`, local piping and control pp4–14/18–21/27–29/35–43/49–56 as applicable.

**Exit:** each numbered unloader and both conveyor lanes navigable to primary screening, four yard inlets and direct silo boundaries; branch conditions retained; deep source/maintenance/control paths per family; primary screens never merged with crusher-house screens.

## Phase 3 — four yards and reclaim to silos

Use P05–P09. Preserve Yard1's accepted model; inspect remaining source references before applying family detail elsewhere.

- **B15/B16:** finish Yard1's supported machine detail and safety/anchor/lube/onboard-DSS follow-ups, EAC-7/EBA-8 qualifications, AP/sector/control mappings and SP-8G/H runoff. Build a source/model→numbered-machine applicability matrix.
- **B17–B19:** Yard2: EAC-9, EAD-2, EAE-2, EAF-2, EBA-10, UEB-2, UAX-2/6 and its own services.
- **B20–B22:** Yard3: EAC-11, EAD-3, EAE-3, EAF-3, EBA-12, UEB-3, UAX-3/7 and its own services.
- **B23–B25:** Yard4: EAC-13, EAD-4, EAE-4, EAF-4, EBA-14, UEB-4, UAX-4/8 and its own services.
- **B26/B27:** UEF-8/9/10/11, FG-7–10 and each source-specific receiving, dust and drainage branch.
- **B28/B29:** continuous multi-inlet EBA-15A/B, UEF-12, FG-11/12, AT-3/4; EBA-16A/B, CV-3/4 and exact 16A→EBB-1 / 16B→EBB-2 interfaces.

Source starts: Yard1 manifest, numbered conveyor GAs, stacker/reclaimer GA/BOD and mechanism/lube/anchor/fire references, stockpile P&ID/piping, each local TP drawing. Confirm each yard's local branch rather than copying Yard1 quantities or sump pair.

**Exit:** four separately verified yard journeys from stacking inlet through stockpile/reclaimer to reclaim delivery; source-qualified motion/drive/control/lube auxiliaries; explicit local versus common services; all four yard outlets trace to the accepted silo inlets.

## Phase 4 — TP13 sampling, trippers and bunkers

Use P12–P14 and reuse B36's corrected v593 interfaces.

- **B37:** sampling2 primary samplers, reversible feeder/bias bin, sample crusher, secondary sampler/collector, reject conveyor/slide gate and source-stated returns to 19A/B. Reconcile SNC-2 versus the generic TP13 elevator before decomposing elevator, hoists and access.
- **B38:** EBA-19A/B drives/mechanical/protection, sealing-belt and located tripper interfaces.
- **B39/B40:** TT-1/3 Unit1 and TT-2/4 Unit2 with independently verified travel envelope/handing, drive/brake/clamp/limits/cable/chute/control. Verify special head discharge/cross-unit provision separately from normal assignment.
- **B41:** both bunker bays and all twelve A–F vessels: design sizing, liners/inlet/sealing/access/level/dust/outlet boundaries. No design capacity promoted to current inventory.
- **B42:** bunker dust extraction, pickup/duct/filter/fan/pulse air and control, plus local/shared-service integration.

Start B37 at sampler GA `doc_98b9805fdd334190a93f`, TP13 GA `doc_a9043e95d82c40f399ec` pp1/3, and control pp22–23/53–55. Tripper source starts at `doc_1217799da7124df5bbe5`; use P13/P14 for other exact sources.

**Exit:** sample/reject logic is distinct from main coal flow; no duplicated elevator; supported tripper→bunker paths and last-bunker mappings are verified for each unit; B36 drives/chutes/sources and crusher interfaces remain intact.

## Phase 5 — common infrastructure, remaining records and whole-plant acceptance

Use P15, updated batch ledgers and the current record review queue.

- **B43:** SLD `doc_c3a502c5677443c59183`, MCC/feeder/starter/VFD/control-room/IO mapping to actual consumer IDs. Motor voltage alone is not a supply edge. Preserve unknown cable, loop, commissioned setting and isolation information as explicit gaps.
- **B44:** source-supported fire/HVAC, hoists/elevators, workshop/mobile/vacuum/vulcanizing equipment and remaining common-service/access infrastructure. A manufacturing QAP is not a maintenance record.
- **B45:** disposition every current unplaced/reference/placeholder candidate; audit accepted-pilot thin targets and unresolved source references. Correct local mistakes with reviewed history, assign missing supported detail to its owning package, and finish it before claiming closure. Do not place or delete all unplaced records automatically.
- **B46:** verify the entire ship→yard→reclaim→silo→crusher→tripper→bunker route plus direct silo feed, both lanes and every branch. Audit all 30 conveyors, 12 in-scope TPs, four yards, three unloaders, four trippers, two silos, two crushers and twelve bunkers, their maintainable parts and shared-service boundaries.

**Exit:** no broken source link, silently omitted modeled major part, known false source interpretation, unowned new component or unreviewed available critical source. Every target/dimension has a supported/not-applicable result or a specific evidence gap with search history and resolution requirement. Any information requiring field/vendor/as-built records remains in a handover register. Completion means the available-source design model is finished to this standard, not field commissioning or a complete operational safety system.

## How “continue” resumes

1. Read this plan, `phase-progress.json`, `CONTINUATION_GUIDE.md`, and the current batch checkpoint. Check the live model version and unfinished proposals. Never assume v593 is still current.
2. Resume `active_phase` / `next_batch`; if a batch is in progress, resume its exact source/page/component step. Otherwise choose the first unfinished dependency-ready batch in that phase. An accepted predecessor is rechecked at the affected boundary, not recreated.
3. Work through the phase's batches sequentially, completing supported detail and testing it. “Continue” authorizes implementation; do not produce another plan and stop. If the turn must end before the phase is finished, leave an exact checkpoint and keep the phase `in_progress`. Never promote available-but-unread work to `complete_with_gaps`.
4. After every accepted batch update `batches.json`, that batch's `progress.json` / `checkpoint.md`, and `phase-progress.json` with proposal/version IDs, verification, remaining evidence and next action. Keep original accepted pilot snapshots historical. Refresh the separate current inventory from a fresh read-only snapshot.
5. At phase completion set its status to `complete` or `complete_with_gaps` only when all included batches pass G1–G8. Advance the pointer to the next phase. End with the user-visible result, unresolved evidence and the next phase. A request naming several/all remaining phases authorizes continuation through them.
6. An unresolved field record blocks promotion of that claim, not independent work. A false identity, broken route/source or unread critical available drawing prevents the affected batch closing. Record exact dependency exceptions; do not silently skip them.

Every source package still uses immutable originals, exact claim-level evidence, applicability, consistent backup, isolated rehearsal and sequential guarded stage/validate/commit. Keep original documents immutable; change canonical facts only through supported correction APIs. Update implementation documentation normally. Actual desktop/narrow browser journeys are mandatory for scene changes. Renderer-level tests must check that modeled located equipment is really drawn; graph-only tests are insufficient.

**Checkpoint — B00 source review, 1 October 2026:** Live v593 confirmed, no pending proposals. Original p55 legend and each affected local service badge reviewed; both pump-house GAs and TP1 GA/review inspected. UGA alias/classification corrections, 15 individually checked service-badge corrections, UEF-2 scope note and TP1 obsolete-source-gap replacement are prepared for isolated rehearsal. See [B00 checkpoint](../../output/plant-enrichment/B00/checkpoint.md).

**Next action:** B02: trace and connect existing common air/water outlet headers to TP1 local mains and TP13 inlet via UEE-3, using175089 pp1-2 and corroborating175286/175300 local originals. Review/headers has original renders and enlarged route crops. Then finish model-reference compressor internals/protection-table reconciliation; individual mapping and180055 remain evidence gaps. Do not replay accepted packages through628.

### Implementation checkpoint — B00 corrections accepted at v595

UGA-1/2 labels/classes corrected without replacing IDs; 15 local service-badge interpretations corrected after individual drawing review; UEF-2 reference scope made explicit; obsolete TP1 missing-GA claim replaced with Rev6/Rev5-review-qualified availability. Proposals: `prop_52fe25003f254599a1a8` (v594), `prop_8e9125dfac134c3b8c4e` (v595). Isolated rehearsal and complete unrelated-assertion preservation passed. Browser/source-return checks and B00 applicability decisions remain before batch closure.

### Implementation checkpoint — B00 boundary decisions accepted at v598 (2 October 2026)

Three source-scoped proposals add 13 qualifications, preserving every prior assertion: DBR machine-type applicability and explicit no-merge decision (v596), SUL Type1/Type2 caption discrepancy and SUL-3 dual-material design boundary (v597), and UEF-2/TP16–18 SW/PW reference interfaces (v598). Numbered vendor/layout mapping is assigned to B07/B08; no extra main coal route is created. Browser/source-return verification is the remaining B00 acceptance step.

### Verification checkpoint — B00 closed, B01 active (2 October 2026)

B00 accepted at v598 with explicit deferrals to B01/B03/B05/B07/B08. Integrity and silo/crusher audits pass; 38 explorer/scene tests pass. Actual browser source-open/return journeys pass for all 27 affected records. See [B00](../../output/plant-enrichment/B00/checkpoint.md). Resume [B01](../../output/plant-enrichment/B01/checkpoint.md); Phase 1 remains in progress.

### Implementation checkpoint — B01 house identities accepted at v599 (2 October 2026)

Proposal `prop_060d5bc9677742f59538` reconciles both proven UGA/DS pump-house pairs and places eight existing DFDS pumps/compressors at their documented houses. Isolated rehearsal and complete assertion/alias preservation pass. Browser/regression verification follows; B01 remains in progress for grouped equipment, tanks and consumer boundaries.

### Verification checkpoint — B01 house milestone verified at v599

Both house scenes and all eight newly located components pass actual source-open/return checks; narrow-screen source/return also passes. Integrity and silo/crusher regression audits pass. Existing assertion and alias history is preserved. [B01 checkpoint](../../output/plant-enrichment/B01/checkpoint.md) records the remaining pump/compressor revision reconciliation, common tanks and consumer contract. B01 and Phase 1 remain in progress.

### Implementation checkpoint — B01 pump identity and duty bases accepted

- v600: `prop_806accad6bfb4af8a477` (doc_af4f437e54f143af9f62)
- v601: `prop_30654f535cd54b029075` (doc_b5188c19e5b942cfa976)
- v602: `prop_86cbbf101b4e439d94a7` (doc_d0cb76dd3ab3478295db)

Two individual DFDS-1A/B records now resolve to DFDSP-1A/B using the original house reference table. Earlier design and later vendor duties are retained with revision qualifications. Final reference-discrepancy package and verification are in progress; B01 remains active.

### Verification checkpoint — B01 pump milestone at v602

Two DFDS/DFDSP pump duplicates reconciled through the house drawing reference table; earlier/later duties retained with revision qualifications. House2 mixed-number reference discrepancy preserved. Seven changed claims pass actual source-open/return. Fresh integrity checks,39 explorer/scene tests and silo/crusher audits pass; pilot audits use the exact two-conflict manifest, with strict default and rejection behavior tested. Grouped compressor/tank/consumer work remains B01.

### Implementation checkpoint — B01 compressor/group identities at v606

Two proven SC/DFDSC pairs reconciled; three grouped source records classified as design references linked to individual assets. Vendor compressor motor-rating uncertainty remains explicit. Four reviewed proposals accepted at v603–606 after isolated rehearsal, with full prior assertion/alias preservation and unchanged pump conflicts. Browser and semantic verification pending; B01 remains active. See [checkpoint](../../output/plant-enrichment/B01/checkpoint.md).

### Verification checkpoint — B01 compressor/group milestone at v606

All16 added claims pass actual source-open/return. Integrity,40 explorer/scene tests and both pilot semantic audits pass; two existing pump duty conflicts remain. Source references display as references. Resume common tanks/SPDS and consumer boundaries; B01 stays in progress.

### Implementation checkpoint — B01 common tanks at v608

Duplicate House-1/Common DS Tank-1 reconciled. House-2 Tank-2 parent clarified as three service compartments; four existing inlet valves linked to their exact compartment. Source-local MGV/KKS disagreements preserved. Two reviewed proposals accepted after isolated rehearsal, with existing assertion history retained. Verification and SPDS identity work continue; B01 remains active.

### Verification checkpoint — B01 common tanks at v608

Thirteen claim source-open/return checks, integrity and both pilot audits pass. Three compartments and inlet valves are navigable. Motorized-valve symbol correction passes41/41 tests and desktop/narrow browser checks. SPDS identity and consumer-boundary work remains; B01 and Phase1 stay in progress.

### Implementation checkpoint — B01 SPDS acceptance started at v609

The same-sheet SPDSP1/2 reconciliation is accepted; remaining source-scoped vendor/group proposals are in progress. Inspect the live commit log before continuation. Isolated rehearsal preserves all assertions/aliases. Two additional formal head conflicts reflect preserved124m versus124mwc unit dimensions; see spds-head-unit-review.json.

### Implementation checkpoint — B01 SPDS identities accepted at v612

Four duplicate pump records reconciled into the two existing units, with two linked grouped design references and14 source-qualified claims. Full prior assertion/alias preservation passed. Two124m/mwc normalization conflicts are explicitly documented and retained alongside the two DFDS duty conflicts. Browser and current snapshot verification follow.

### Verification checkpoint — B01 SPDS milestone at v612

All14 claim sources and return paths pass; both canonical pumps are reachable from House2. Fresh integrity/FK and both pilot audits pass with the exact four-conflict manifest. B01 remains in progress for source-group ownership and consumer boundaries.

### Implementation checkpoint — B01 ownership corrections accepted at v615

TH/PSH generic owner merged into proven DFDSSystem1. Nozzle and stockpile-water solenoid-box groups are source references; incorrect physical classification/ownership retired. Nine claims added after isolated rehearsal and preservation checks. Consumer ledger now inventories23 relations; silo and TP13 reach the same canonical System2 source. Final verification and remaining B01 assessment follow.

### Verification checkpoint — B01 ownership at v615

Nine source journeys, corrected reference display, fresh integrity/FK and both pilot audits pass. Two separate consumer areas reach the same canonicalSystem2. Remaining PWP1/2 identity and service/runoff group assessment keep B01in progress;23-row ledger is not a claim of completed utility piping.

### Implementation checkpoint — B01 potable identities accepted at v616 (2 October 2026)

Two duplicate potable pump records reconcile through matching individual KKS on original175319 pp7/15. Naming/sheet discrepancies remain inspectable. Six source-qualified claims and two aliases added; all prior facts/aliases and four conflicts preserved. Proposal `prop_1845717d5403472f822b`; [B01 checkpoint](../../output/plant-enrichment/B01/checkpoint.md). Browser/audit verification and remaining runoff/stockpile ownership review follow.

### Verification checkpoint — potable milestone v616

Six added facts pass actual browser source-open/return; both pumps are selectable from House2 and retain the house context. Fresh snapshot integrity/FK and both silo/crusher semantic audits pass against the exact unchanged four-conflict manifest. Evidence: potable-browser-checks-v616.json and potable-source-v616.png in B01. Source disagreements remain visible. No application code changed. Remaining grouped runoff/reference and stockpile-owner correction is rehearsing.

### Checkpoint - 2 October 2026, B01 v620

Potable schedule/control identities accepted and verified at616. Runoff source-reference and single shared-SPDS-owner corrections accepted617-620 through four reviewed proposals; live source/return verification pending; isolated preservation and both pilot audits pass. B01 remains in progress. B01: verify accepted v617-620 grouped runoff/reference and shared-SPDS ownership changes, finish SW/PW source identity and consumer boundary ledger, then close identity scope and start B02 DFDS P&ID production/header detail. Do not replay accepted v599-620.

### Checkpoint - 3 October 2026, B01 accepted / B02 active

B01 identity/ownership scope is complete_with_gaps at620. All17 final source journeys, integrity/FK, preservation and bothpilot audits pass;26-rowconsumercontract finalized. Pump/source disagreements remain visible, and detailed production/control/routes explicitly belongB02-B04. Phase1 remains inprogress. B02: inspect DFDS P&ID175089 Rev1 pp1-2 original production/tank-suction/pump-discharge/air-treatment/header regions; reconcile existing component IDs and exact connections, then source-scoped rehearsal and guarded acceptance. Reuse B01 canonical identities and 26-row consumer ledger; do not replay accepted599-620.

### B02 checkpoint - System1 accepted621

22commonstationcomponents and26utilityconnections accepted;System2in-flight. Liveverificationpending;phase1/B02remaininprogress. B02: finish in-flight reviewed frontends acceptance and verify 621+ common station scenes/source-return, fresh integrity and pilot regressions. Do not replay accepted frontends packages. Then receiver accessories/vendor/motor/controls and exact common-header to local TP boundaries remain.

### B02 checkpoint - both station front ends accepted v622

44 components and52 utility connections accepted through two guarded proposals. Preservation and both pilot regressions pass; live source/return verification pending. Phase1/B02 remain in progress. B02: verify all new common-station components and critical connection/capacity source-return journeys at622; fresh snapshot and pilot audits. Then inspect compressor vendor doc_d91e9eef8a40479687cd cover/comments and applicable GA/BOM for receiver safety/drain/gauge and compressor/motor detail; inspect duplex-filter doc_48b502990d1f45009641 for scoped design applicability. Do not replay accepted frontends621-622.

### B02 front-end verification — 3 October 2026, v622

The two common DFDS station front ends are accepted and verified: 44 components, 52 utility paths, two monitoring links and source-stated receiver volumes/nominal bores. All 44 components and 106 distinct source claims passed browser selection/source-return; 44/44 renderer tests, database integrity/FK, preservation checks and both pilot audits pass. B02 remains in progress for available vendor, receiver accessory, motor/control and local consumer header work. The exact next action and source queue are saved in [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md) and phase-progress.json.

### Source-review checkpoint - B02 vendor detail (3 October2026)

All 36 original compressor pages and seven duplex-filter pages were inventoried. The DFDS-specific 32 NB schedule/GA was reviewed in detail, establishing vendor BOM/ratings for the two distinct DUP01 filters; the generic reference remains separate. The filter package entered isolated rehearsal. Final compressor motor source 180055 and PID/control disagreements remain recorded source work. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### Implementation checkpoint - B02 filter vendor detail acceptedv623

The two existing DFDS DUP01 filters now expose 16 maintainable groups and 118 supported facts through reviewed proposal `prop_5a82161ca67941438f8b`. The generic vendor record is a separate design reference. Older flow bases and the support-count disagreement are preserved; backup, rehearsal and preservation checks pass. Browser/integrity verification followed this acceptance milestone. B02 and Phase 1 remain in progress. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).
### B02 accepted milestone v624

Both common air receivers now have separately sourced PRV, pressure gauge, gauge isolation valve and ADT drain components (eight total). Source P&ID sheets were reviewed independently; no relief setting, gauge range or automatic drain mechanism is invented. Actual browser verification remains pending. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).
### B02 accepted milestone v625

The four existing DFDS pumps now expose 44 vendor-supported motor, rigid coupling, guard, shaft, impeller, seal, bearing-sleeve, stool, shroud, casing and spacer components. Twelve mechanical connections trace motor → coupling → shaft → impellers. Both motor-speed bases and distinct 14/16-stage quantities remain inspectable. Actual browser verification remains pending. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### B02 data verification checkpoint — v625

Fresh read-only snapshot: database integrity is OK, with no foreign-key errors. Independent checks confirm both filter assemblies, both receiver accessory assemblies and all four pump drive chains; eight generated desktop/narrow pump SVGs expose every new core part. All 46 Node tests and both silo/crusher pilot audits pass, preserving the four qualified conflicts. Source, claim, component, boundary and coverage ledgers are updated, and the current inventory is refreshed without replacing the historical v510 inventory.

Actual browser control timed out on both existing and fresh preview tabs; G7 remains pending, and v622 remains the last fully browser-verified version. Continue Phase 1 / B02 from the exact action in [phase-progress.json](phase-progress.json). Available compressor PID/controller, common control, remaining pump BOM maintenance groups and TP1/TP13 header work remain recorded in the [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### B02 browser verification checkpoint — v625

Actual browser verification at v625: 68 new components, 462 distinct claims at desktop, 16 narrow source journeys. Every cited crop loaded from the expected immutable source/page and returned to the selected component. Narrow source images fit the dialog; the original-image link remains available for further zoom. Source-based projection checks and preservation pass. Phase1/B02 remains in progress.
### B02 accepted milestone v626

The four canonical DFDS pumps now expose 28 additional vendor BOM groups: cover, vent plug, screwed plugs, row-qualified O-rings and short/shaft-end/seal-side spacers. All prior facts, aliases, merges and four qualified conflicts are preserved. Actual browser verification remains pending. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### B02 interruption checkpoint — v626

Accepted v626 adds28 pump maintenance groups and164 assertions. Fresh integrity/FK, independent assembly/source checks,46 Node tests and both pilot audits pass. Actual browser completion is4/28 groups and23/164 distinct claims. Last fully browser-verified version remains625. The narrow source-crop fix was visually verified at625. Current inventory still reflects625 and must be refreshed from accepted-v626.json.

### B02 browser verification checkpoint — v626

Actual browser verification at v626: 28 new components, 164 distinct claims at default browser width, 16 narrow source journeys. Every cited crop loaded from the expected immutable source/page and returned to the selected component. Narrow source images fit the dialog; the original-image link remains available for further zoom. Source-based projection checks and preservation pass. Phase1/B02 remains in progress.
### B02 accepted milestone v627

Eight source-specific PS-01/DPS-01 signal links now reach all four existing DFDS pumps;24 grouping/role/qualification claims preserve the original individual conditions, H/HH/L wording and unresolved alarm/trip and polarity differences. No new equipment or numeric setting was introduced. Actual browser verification remains pending. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### B02 verified control milestone - v627

v627 controls verified:32 claims on12 existing records passed original-page/crop/source-return checks at explicit1280x900 desktop width and in the default app panel;8 narrow journeys passed. All8 same-system PS/DPS-to-pump signal links are drawn.46 Node tests, independent control semantics, integrity/FK, preservation and both pilot audits pass.

Viewport correction: the earlier v626 exhaustive164 checks used the default app panel.16 mobile checks and16 additional explicit1280x900 checks across all four pumps pass; wide checks were performed on v627 with all v626 facts preserved.

### B02 compressor source-review checkpoint

Original175103 GA/PID/wiring and control references reviewed at v627. Staging, cooling, main starter and S2-prime interface conflicts identified; model-to-numbered-unit mapping and180055 remain missing. Sixteen source-qualified claims prepared for isolated rehearsal; no physical internals/settings assigned. Detailed model-reference and numeric protection reconciliation remain available work. See `output/plant-enrichment/B02/review/compressor/findings.json`.
### B02 accepted milestone v628

Sixteen compressor source qualifications accepted on two existing systems and four compressors: model applicability, staging, cooling, starter and S2-prime conflicts remain explicit; no installed internals or settings invented. Actual browser verification remains pending. See [B02 checkpoint](../../output/plant-enrichment/B02/checkpoint.md).

### B02 compressor verification checkpoint — v628

Compressor reconciliation v628 verified:16 claims on six existing records pass1280x900 source/crop/return checks;12 system claims also pass390x844. Integrity/FK, prior-fact/alias/conflict preservation and both pilot audits pass. No equipment, physical connections or numerical settings added.

**Next action:** B02: trace and connect existing common air/water outlet headers to TP1 local mains and TP13 inlet via UEE-3, using175089 pp1-2 and corroborating175286/175300 local originals. Review/headers has original renders and enlarged route crops. Then finish model-reference compressor internals/protection-table reconciliation; individual mapping and180055 remain evidence gaps. Do not replay accepted packages through628.
