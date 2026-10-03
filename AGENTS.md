# CHP plant-model continuation

For a general request to continue or finish the detailed plant implementation, read:

1. `docs/plant-handoff/FIVE_PHASE_PLAN.md`
2. `docs/plant-handoff/phase-progress.json`
3. `docs/plant-handoff/CONTINUATION_GUIDE.md`
4. The indicated batch checkpoint, section/family contract and original source material.

Resume the saved phase/batch and exact next action. A named user target takes priority. Do not restart accepted pilots or stop after replanning when implementation is requested. Check live model IDs/version; frozen v510 inventories and historical accepted exports are not current state.

**Work breadth-first.** While `phase-progress.json` has `"pass": "A"`, take each batch only to the plan's Tier 1 ("breadth-complete") definition, record finer detail in `docs/plant-handoff/current/depth-queue.json`, mark the batch `breadth_complete` and move to the next batch in the same run. Do not go deeper into one subsystem (vendor BOM rows, internals, setting tables, exhaustive per-claim checks) until Pass B, unless the user names that target for full depth.

Update the phase pointer, batch status, depth queue and source/claim/verification checkpoint after accepted work, then commit the repository changes (docs/tools/code; `data/` and `output/` stay untracked). Keep canonical changes source-reviewed through the existing proposal APIs; no direct SQL edits or replay of old enrichment migrations. Preserve unrelated workspace changes. See the plan for acceptance and source-gap rules.
