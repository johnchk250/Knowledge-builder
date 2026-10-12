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

Two routes satisfy the visual pass. Prefer Route A whenever a browser-driving
tool is available; otherwise Route B is the required fallback ("no browser
tool" is never an excuse on its own).

- **Route A — interactive browser journeys.** Drive the running app directly:
  overview → each tagged equipment → subpart → individual fact/source modal →
  Escape returns to the same assembly; tag search; neighbouring equipment;
  shared-service boundary; narrow-panel and desktop widths. Screenshot each
  leg into `tmp/visual-checks/<batch>/` and review against the checklist below.
- **Route B — `tools/visual_sweep.cjs`.** Scripted equivalent of Route A:
  per viewport it captures overview, each tagged equipment with inspector
  open, connections view and operations desk; then one source-open/return
  journey per tag (first `pe-source` button → evidence modal screenshot →
  Escape → inspector retained). Results and console/page errors land in
  `<out>/manifest.json`.

One-time setup (stays inside gitignored `tmp/`, repo stays clean):

```powershell
cd tmp/visual-checks; npm init -y; npm i -D playwright@1.64.0; npx playwright install chromium; cd ..\..
```

Per batch — start the server and sweep back-to-back **in the same run**:

```powershell
python -m chp.launcher
node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/<batch> --tags <TAG1>,<TAG2>
```

Rules learned the hard way (B17):

- Start with `python -m chp.launcher` (or `start.bat`). It retires a verified
  orphan on 8765 and uses the correct `--data data`, so workspace `plant`
  serves the live model. **Never pass `--data data/plant`** — that serves a
  stale workspace whose `Documented model` badge stays at v0 and every tag
  search fails.
- Background servers may be reaped between runs. Start, verify the listener,
  then sweep immediately in the same run; stop your server process when done
  (the next launcher run retires verified orphans).
- The sweep waits for the `Documented model · v<live>` badge before touching
  anything. If it never flips from v0, the server is on the wrong data dir.
- Inspector source buttons are `button.pe-source` (explorer cite helper);
  `button.ps-source` is a different helper used elsewhere. Expand `<details>`
  with real summary clicks only — setting `.open` via evaluate wedges the page.
- Viewport screenshots for modals (centered, fast); full-page for scenes.

Tags are the batch's equipment labels (e.g. B17: `--tags EAC-9,EBA-10`;
a machine batch might pass `--tags EAD-2,EAF-2`). The script captures,
per viewport (`desktop-1440`, `mobile-480`): overview, each tagged equipment
with inspector open, connections view, operations desk — plus console/page
errors into `<out>/manifest.json`. Shot counts scale with the tag list, they
are not a fixed target: per viewport the sweep takes overview + one shot per
tag + connections + desk, and one source journey per tag. A 1-tag batch
yields 8 PNGs, 2 tags yield 10, 3 tags yield 12. The run prints a totals line
(`Screenshots: N/N steps; source journeys: M/M clean`) — copy those actuals
into the checkpoint one-liner.

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
item holds at both widths. Record one line in the batch checkpoint with the
run's actual totals, e.g.
`Visual pass: 10/10 PNG + 2/2 source journeys, 0 console errors (desktop-1440 + mobile-480).`
Route A records the same line with its journey legs instead of PNG counts.
Interactive browser journeys are never skipped for batches that touch scenes —
use Route A when a browser tool exists, Route B otherwise; this sweep is the tool.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Badge stays at `Documented model · v0`, every tag search times out | Server started with `--data data/plant` (stale workspace) | Restart via `python -m chp.launcher` (correct `--data data`) |
| `ERR_CONNECTION_REFUSED` at sweep start | Server reaped between runs | Start the server and sweep back-to-back in the same run; verify the 8765 listener first |
| Model badge flips but search finds nothing | Interaction raced the async `/api/state` load | `waitForModel` gate in the script; do not remove it |
| Script wedges expanding inspector sections | `.open` set via evaluate | Expand with real summary clicks only (baked into the script) |
| Source-button locator finds nothing | Wrong class: scene uses `ps-source`, inspector uses `pe-source` | Locator in the script targets `button.pe-source`; keep it so |
| Full-page scene shots take minutes | Huge SVG DOM on assembly scenes | Expected; viewport shots are used for modals |

## Worked example (B17, v664)

```powershell
node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/B17-auto --tags EAC-9,EBA-10
```

10/10 PNG + 2/2 source journeys, 0 errors. EAC-9: Yard2 membership, KB-FD-5/6 → EAD-2 inlets,
Rated 3400 / Design 3740 t/h / 3.5 m/s (Page 5), 49 facts, 17 connections.
EBA-10: EAF-2 → FG-9 outlet, weigher, 2.7 m/s / 270 kW / 1375 T/hr
(Page 2 text block 1), 40 facts, 12 connections. Desk: 3116 identities, 266 docs.
Source journeys: control write-up p29 and GA 175020 p5 modals open with
correct document/page/SHA-256; Escape returns to the same inspector.

## Notes

- `tools/visual_sweep.cjs` resolves Playwright from `tmp/visual-checks/node_modules`
  as fallback, so the committed script works with the tmp-local install.
- Sweep output lives under `tmp/visual-checks/` (gitignored). Commit the script,
  the guidance and the checkpoint line — never the PNGs.
- The equipment scene shows no inspector until a hotspot is picked; the script
  clicks the first `[data-action="scene-pick"]` for that reason.
