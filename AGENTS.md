# CHP plant-model continuation

For a general request to continue or finish the detailed plant implementation, read:

1. `docs/plant-handoff/FIVE_PHASE_PLAN.md`
2. `docs/plant-handoff/phase-progress.json`
3. `docs/plant-handoff/CONTINUATION_GUIDE.md`
4. The indicated batch checkpoint, section/family contract and original source material.

Resume the saved phase/batch and exact next action. A named user target takes priority. Do not restart accepted pilots or stop after replanning when implementation is requested. Check live model IDs/version; frozen v510 inventories and historical accepted exports are not current state.

**Work breadth-first.** While `phase-progress.json` has `"pass": "A"`, take each batch only to the plan's Tier 1 ("breadth-complete") definition, record finer detail in `docs/plant-handoff/current/depth-queue.json`, mark the batch `breadth_complete` and move to the next batch in the same run. Do not go deeper into one subsystem (vendor BOM rows, internals, setting tables, exhaustive per-claim checks) until Pass B, unless the user names that target for full depth.

Update the phase pointer, batch status, depth queue and source/claim/verification checkpoint after accepted work, then commit the repository changes (docs/tools/code; `data/` and `output/` stay untracked). Finish every accepted batch with the visual pass in `VISUAL_CHECK_GUIDANCE.md` (Tier 1 checks + `tools/visual_sweep.cjs` sweep, 0 console errors) and record its one-line result in the batch checkpoint before committing. Keep canonical changes source-reviewed through the existing proposal APIs; no direct SQL edits or replay of old enrichment migrations. Preserve unrelated workspace changes. See the plan for acceptance and source-gap rules.

## Quiet working mode (transcript hygiene)

Keep the session transcript readable: reasoning summaries first, verbose tool output last.
- Prefer dedicated tools (`read`, `glob`, `grep`, `edit`, `write`) over `shell` for file inspection and edits.
- Reserve `shell` for builds, tests, and commands that require execution. Use quiet flags, combine related checks into one call, and avoid dump-style output (`Write-Host` of full listings, `tar -tf` of whole archives, recursive unfiltered logs).
- When verification needs a large listing, summarize counts and failures in chat and leave full output in the tool result; do not re-echo it.
- Batch independent file reads in parallel via Code Mode `execute` where supported.
- Narrate each step briefly in chat (goal, result, next action) so progress is visible without expanding collapsed tool calls.
