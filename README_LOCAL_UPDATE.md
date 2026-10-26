# CHP Knowledge Builder v1007 — Operating Route Selection & Visual Audit Fix Delta

## How to Apply This Delta to Your Local Project Folder

Extract `CHP-v1007-route-selection-fix-delta.zip` directly into the root of your local `CHP-Knowledge-Builder` project folder (allow it to overwrite the matched files in `chp/`, `dist/`, and `tests/`). It is 100% self-contained and can be applied on top of any previous delta or directly onto a clean `v1007` folder.

### What Was Fixed for the Top Bar Operating Route Selection (`Whole plant` / `Path 1..5`)

1. **Why Nothing Changed Previously (`dist/plant-scene.js`, `dist/plant-scene.css`)**:
   - In `plant()`, non-participating stages were assigned `class="ps-stage-scene ps-dimmed"`, **but `.ps-dimmed` was missing from `dist/plant-scene.css`**, so non-participating stages stayed at 100% opacity.
   - `plant()` also drew all 9 coal-flow arrows (`p.links`) identically without checking `path.stages`, so none of the arrows dimmed or highlighted when switching between `Path 1..5`.
2. **What Happens Now When You Select `Path 1..5`**:
   - **Stage & Arrow Isolation**: Non-participating stages and arrows immediately fade into the background (`.ps-dimmed { opacity: 0.15; filter: grayscale(0.9); }`), while the stages on the selected route get a crisp highlighted border card (`.ps-route-stage-active`) and the active coal-flow arrows animate with flowing dashes (`.ps-route-edge-active`).
   - **Equipment Tags on Every Stage Card**: Each process stage card on `#overview` now displays its key equipment tags (`Ship unloaders · EAC-1 / 2 · UEF-1`, `UEE-2 · EBB-1 / 2 · extractors`, etc.) and indicates `Active in Path N · Explore →`.
   - **Live Active Route Summary Banner**: Selecting `Path 1..5` opens a route summary bar right below the route pills displaying the documented sequence logic (`path.summary.value`), flow limit (e.g., `1250 t/h Maximum forward flow toward silos; excess diverted to stacking` on Paths 2 & 5), clickable stage chips for the active chain, and 1-click source evidence chips (`p.8 ↗`, `p.5 ↗`, `Route permissives & notes ↗`).
   - **Stream & Bypass Highlighting Inside Buildings (`UEE-3`, `UEF-1..13`, `UEF-4/6`)**: Selecting a stream, bypass path (`Screen & crush` vs. `Direct bypass`), or receiving conveyor in the Crusher House or Transfer Houses now also highlights and animates the active coal path while softly dimming unselected stream equipment (`.ps-stream-dimmed`).

### All Other Visual & Geometric Fixes Included in This Self-Contained Delta
- Fixed the `(true)` subtitle bug on openable hotspots (`silo · 5 parts ↗`).
- Fixed `UEE-2` Silo House `siloColumns()` root filtering so child liner records (`EBB-1/2 Shell and sloping liner`) no longer create empty ghost columns or push `EBB-2` onto `HOUSE SERVICES`.
- Fixed 1D Kinematic Conveyor Strip (`conveyorScene()`) belt-loop corridor spacing, left-to-right kinematic arrow routing, and `kind()` container regex anchoring (`EBA-18A/B` idlers, pulleys, and take-ups retain their true symbols).
- Fixed Transfer House (`UEF-1..13`) `HEAD DECK` central gravity shaft routing and added `directChuteTransferColumns()` for `UEF-1`.
- Unified the `.topbar` across all modes and memoized `p.assembly(id)` with $O(1)$ `_ids` lookups.
