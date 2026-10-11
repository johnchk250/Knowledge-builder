# Visual check guidance

Every accepted batch finishes with a visual pass before commit. Model/data work
(B-phases) changes what the plant explorer draws, so projection tests alone are
not enough: render the affected scenes in a real browser at desktop and narrow
widths and inspect them.

## Tier 1 — code checks (fast, every batch)

```powershell
node --check dist/app.js
node --check dist/operations-ui.js
node --check dist/plant-model.js
node --check dist/plant-scene.js
node --check dist/plant-explorer.js
node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs tests/test_plant_scene_render.cjs tests/test_viewer_math.cjs
.\.venv-cad\Scripts\python.exe -m unittest discover -s tests
.\.venv-cad\Scripts\python.exe -m chp.verify --data data/plant
```

All green before Tier 2. (`start.bat` uses `.venv` then falls back to `py -3`;
`.venv-cad` is the checked-in local environment.)

## Tier 2 — browser sweep (visual pass)

One-time setup (stays inside gitignored `tmp/`, repo stays clean):

```powershell
cd tmp/visual-checks; npm init -y; npm i -D playwright@1.64.0; npx playwright install chromium; cd ..\..
```

Per batch (app must be running, e.g. `start.bat` on port 8765):

```powershell
node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/<batch> --tags <TAG1>,<TAG2>
```

Tags are the batch's equipment labels (e.g. B17: `--tags EAC-9,EBA-10`).
The script captures, per viewport (`desktop-1440`, `mobile-480`): overview,
each tagged equipment with inspector open, connections view, operations desk —
plus console/page errors into `<out>/manifest.json`.

## Review checklist (every PNG)

- Breadcrumbs show the right area/membership (e.g. Plant › Stockyard › Coal Yard 2).
- Route context correct: upstream → equipment → downstream (e.g. EAF-2 → EBA-10 → FG-9).
- Owned vs located equipment distinguished; shared services stay external.
- Drive/component chain renders (motor → coupling → gearbox → pulley) with inspect links.
- Inspector: documented values carry source buttons (page/region), qualifications
  listed, fact/connection counts sane.
- No clipped labels, no overlapping cards hiding the scene (use Fit / Spread parts
  when reviewing assembly layout), legend + layer links intact.
- Narrow 480px: scene stacks above inspector, no page-width overflow.
- `manifest.json`: zero console/page errors (report standard: "none observed").

## Acceptance

`manifest.json` has no step `error`, no console/page errors, and every checklist
item holds at both widths. Record one line in the batch checkpoint, e.g.
`Visual pass: 10/10 PNG, 0 console errors (desktop-1440 + mobile-480).`
Interactive browser journeys are never skipped for batches that touch scenes —
"no browser tool" is not an excuse; this sweep is the tool.

## Worked example (B17, v664)

```powershell
node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/B17-auto --tags EAC-9,EBA-10
```

10/10 PNG, 0 errors. EAC-9: Yard2 membership, KB-FD-5/6 → EAD-2 inlets,
Rated 3400 / Design 3740 t/h / 3.5 m/s (Page 5), 49 facts, 17 connections.
EBA-10: EAF-2 → FG-9 outlet, weigher, 2.7 m/s / 270 kW / 1375 T/hr
(Page 2 text block 1), 40 facts, 12 connections. Desk: 3116 identities, 266 docs.

## Notes

- `tools/visual_sweep.cjs` resolves Playwright from `tmp/visual-checks/node_modules`
  as fallback, so the committed script works with the tmp-local install.
- Sweep output lives under `tmp/visual-checks/` (gitignored). Commit the script,
  the guidance and the checkpoint line — never the PNGs.
- The equipment scene shows no inspector until a hotspot is picked; the script
  clicks the first `[data-action="scene-pick"]` for that reason.
