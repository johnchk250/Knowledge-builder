# CHP plant-model continuation

For a general request to continue or finish the detailed plant implementation, read:

1. `docs/plant-handoff/FIVE_PHASE_PLAN.md`
2. `docs/plant-handoff/phase-progress.json`
3. `docs/plant-handoff/CONTINUATION_GUIDE.md`
4. The indicated batch checkpoint, section/family contract and original source material.

Resume the saved phase/batch and exact next action. A named user target takes priority. Do not restart accepted pilots or stop after replanning when implementation is requested. Check live model IDs/version; frozen v510 inventories and historical accepted exports are not current state.

Update the phase pointer, batch status and source/claim/verification checkpoint after accepted work. Keep canonical changes source-reviewed through the existing proposal APIs; no direct SQL edits or replay of old enrichment migrations. Preserve unrelated workspace changes. See the plan for acceptance and source-gap rules.
