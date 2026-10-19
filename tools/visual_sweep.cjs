'use strict';
// Visual sweep for CHP-Knowledge-Builder 3D (committed copy).
// Captures overview / tagged equipment / connections / desk at 1440px + 480px,
// plus browser console + page errors, into tmp/visual-checks/<batch>/.
//
// Prerequisites (one time; stays inside gitignored tmp/ so the repo stays clean):
//   cd tmp/visual-checks && npm init -y && npm i -D playwright@1.64.0
//   npx playwright install chromium
//
// Usage (app must be running on port 8765 with the LIVE workspace):
//   python -m chp.launcher   (safe orphan handling, correct --data data)
//   node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/B17 [--tags EAC-9,EBA-10] [--no-source-journeys]
//
// Start the server and run the sweep back-to-back in the same run: background
// servers may be reaped between runs. Never start with --data data/plant —
// that serves a stale workspace whose badge stays at v0 and every search fails.
// After the sweep, stop the server process you started.
//
// Output:
//   <out>/<viewport>/<name>.png  +  <out>/source-journeys/<tag>-source.png
//   +  <out>/manifest.json
// Review the PNGs against VISUAL_CHECK_GUIDANCE.md before committing the batch.

const fs = require('node:fs');
const path = require('node:path');

function loadPlaywright() {
  try { return require('playwright'); } catch { /* try fallback below */ }
  try {
    return require(path.join(__dirname, '..', 'tmp', 'visual-checks', 'node_modules', 'playwright'));
  } catch { /* handled below */ }
  return null;
}
const playwright = loadPlaywright();
if (!playwright) {
  console.error(
    "Missing module 'playwright'.\n" +
    'Run once:\n' +
    '  cd tmp/visual-checks && npm init -y && npm i -D playwright@1.64.0\n' +
    '  npx playwright install chromium'
  );
  process.exit(2);
}

const args = process.argv.slice(2);
const opt = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};
const PORT = Number(opt('--port', '8765'));
const OUT = opt('--out', 'tmp/visual-checks/sweep');
const TAGS = opt('--tags', 'EAC-9,EBA-10').split(',').map(s => s.trim()).filter(Boolean);
const WITH_SOURCE = !args.includes('--no-source-journeys');
const BASE = `http://127.0.0.1:${PORT}`;

const VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 900 },
  { name: 'mobile-480', width: 480, height: 900 },
];

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function shot(page, file, errors) {
  await page.screenshot({ path: file, fullPage: true });
  return { file, url: page.url(), consoleErrors: [...errors.console], pageErrors: [...errors.page] };
}

async function waitForModel(page) {
  // The explorer fetches /api/model asynchronously; search and scenes stay
  // empty (badge shows v0) until the projection loads. Never interact before.
  await page.waitForFunction(
    () => /v[1-9]\d*/.test(document.querySelector('.ps-model')?.textContent || ''),
    undefined,
    { timeout: 180000 }
  );
}

async function openTag(page, tag) {
  // Uses the explorer's own tag search: exact label match sorts first.
  await page.goto(`${BASE}/#overview`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.ps-root', { timeout: 30000 });
  await waitForModel(page);
  await page.fill('#ps-search', tag);
  await page.waitForSelector('#ps-search-results:not([hidden])', { timeout: 15000 });
  const first = page.locator('#ps-search-results a').first();
  await first.waitFor({ state: 'visible', timeout: 15000 });
  await first.click();
  await page.waitForSelector('.ps-root', { timeout: 15000 });
  await sleep(800);
  // The equipment scene itself has no inspector until a hotspot is picked.
  const hotspot = page.locator('[data-action="scene-pick"]').first();
  await hotspot.waitFor({ state: 'visible', timeout: 15000 });
  await hotspot.click();
  await page.waitForSelector('.ps-inspector h2', { timeout: 15000 });
  await sleep(600);
}

async function runViewport(browser, vp) {
  const results = [];
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const page = await ctx.newPage();
  const errors = { console: [], page: [] };
  page.on('console', m => { if (m.type() === 'error') errors.console.push(m.text().slice(0, 500)); });
  page.on('pageerror', e => errors.page.push(String(e).slice(0, 500)));
  const dir = path.join(OUT, vp.name);
  fs.mkdirSync(dir, { recursive: true });

  // 1. Overview (whole coal journey).
  await page.goto(`${BASE}/#overview`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.ps-root', { timeout: 30000 });
  await waitForModel(page);
  await sleep(800);
  results.push({ step: 'overview', ...(await shot(page, path.join(dir, '01-overview.png'), errors)) });

  // 2+. Tagged equipment (--tags) with inspector open.
  let n = 2;
  for (const tag of TAGS) {
    try {
      await openTag(page, tag);
      results.push({ step: `equipment-${tag}`, ...(await shot(page, path.join(dir, `${String(n++).padStart(2, '0')}-equipment-${tag}.png`), errors)) });
    } catch (e) {
      results.push({ step: `equipment-${tag}`, error: String(e).slice(0, 300), url: page.url() });
    }
  }

  // Connections view for the last tag (documented directions only).
  try {
    const conn = page.getByRole('link', { name: /View connections/ }).first();
    if (await conn.count()) {
      await conn.click();
      await sleep(800);
      results.push({ step: 'connections', ...(await shot(page, path.join(dir, `${String(n++).padStart(2, '0')}-connections.png`), errors)) });
    } else {
      results.push({ step: 'connections', error: 'View-connections link not found', url: page.url() });
    }
  } catch (e) {
    results.push({ step: 'connections', error: String(e).slice(0, 300), url: page.url() });
  }

  // Operations desk (second main surface).
  await page.goto(`${BASE}/#desk`, { waitUntil: 'domcontentloaded' });
  await sleep(600);
  results.push({ step: 'desk', ...(await shot(page, path.join(dir, `${String(n++).padStart(2, '0')}-desk.png`), errors)) });

  await ctx.close();
  return { viewport: vp.name, results };
}

async function runSourceJourneys(browser) {
  // One source-open/return journey per tag on a desktop context: equipment
  // scene -> inspector -> first summary -> first pe-source button ("Page N" /
  // "Source N") -> evidence modal screenshot -> Escape -> inspector retained.
  // Inspector source buttons are button.pe-source (explorer cite helper), not
  // button.ps-source (scene helper, used elsewhere). Expand <details> with
  // real summary clicks only: setting .open via evaluate wedges the page.
  const out = [];
  const dir = path.join(OUT, 'source-journeys');
  fs.mkdirSync(dir, { recursive: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  ctx.setDefaultTimeout(25000);
  ctx.setDefaultNavigationTimeout(60000);
  const page = await ctx.newPage();
  const errors = { console: [], page: [] };
  page.on('console', m => { if (m.type() === 'error') errors.console.push(m.text().slice(0, 500)); });
  page.on('pageerror', e => errors.page.push(String(e).slice(0, 500)));
  try {
    await page.goto(`${BASE}/#overview`, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector('.ps-root', { timeout: 30000 });
    await waitForModel(page);
    for (const tag of TAGS) {
      const entry = { step: `source-${tag}`, consoleErrors: [...errors.console], pageErrors: [...errors.page] };
      try {
        await page.goto(`${BASE}/#overview`, { waitUntil: 'domcontentloaded' });
        await page.waitForSelector('.ps-root', { timeout: 30000 });
        await page.fill('#ps-search', tag);
        await page.waitForSelector('#ps-search-results:not([hidden])', { timeout: 15000 });
        await page.locator('#ps-search-results a').first().click();
        await page.waitForSelector('.ps-root', { timeout: 15000 });
        await sleep(800);
        const hotspot = page.locator('[data-action="scene-pick"]').first();
        await hotspot.waitFor({ state: 'visible', timeout: 15000 });
        await hotspot.click();
        await page.waitForSelector('.ps-inspector h2', { timeout: 15000 });
        await sleep(500);
        const summary = page.locator('.ps-inspector summary').first();
        await summary.waitFor({ state: 'visible', timeout: 15000 });
        await summary.click();
        await sleep(500);
        // The inspector's source button is keyed by its data-action; the
        // cosmetic class has been renamed over time (pe-source in the explorer
        // panel, ps-source / ps-source-chip in the scene inspector), so match
        // on the action inside the inspector and stay class-agnostic.
        const link = page.locator('.ps-inspector button[data-action="fact-source"]').first();
        await link.waitFor({ state: 'visible', timeout: 15000 });
        entry.button = ((await link.textContent()) || '').trim().slice(0, 60);
        await link.click();
        await sleep(1200);
        entry.file = path.join(dir, `${tag}-source.png`);
        await page.screenshot({ path: entry.file });
        await page.keyboard.press('Escape');
        await sleep(400);
        entry.returned = ((await page.locator('.ps-inspector h2').first().textContent().catch(() => '(gone)')) || '').trim();
        if (!entry.returned || entry.returned === '(gone)') entry.error = 'Inspector not retained after Escape';
      } catch (e) {
        entry.error = String(e).split('\n')[0].slice(0, 300);
        entry.url = page.url();
      }
      entry.consoleErrors = [...errors.console];
      entry.pageErrors = [...errors.page];
      out.push(entry);
    }
  } catch (e) {
    out.push({ step: 'source-setup', error: String(e).split('\n')[0].slice(0, 300) });
  }
  await ctx.close().catch(() => {});
  return out;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await playwright.chromium.launch().catch(e => {
    console.error('Could not launch Chromium. Did you run `npx playwright install chromium`?\n' + String(e).slice(0, 400));
    process.exit(3);
  });
  const manifest = { base: BASE, tags: TAGS, at: new Date().toISOString(), viewports: [], sourceJourneys: [] };
  try {
    for (const vp of VIEWPORTS) manifest.viewports.push(await runViewport(browser, vp));
    if (WITH_SOURCE) manifest.sourceJourneys = await runSourceJourneys(browser);
  } finally {
    await browser.close().catch(() => {});
  }
  const allSteps = [
    ...manifest.viewports.flatMap(v => v.results),
    ...manifest.sourceJourneys,
  ];
  const fail = allSteps.filter(r => r.error);
  // Counts are dynamic, not fixed: per viewport the sweep captures overview +
  // one equipment shot per --tags entry + connections + desk, and one source
  // journey per tag. Report actuals (a 1-tag batch yields 8 PNGs, not 10).
  const shots = allSteps.filter(r => r.file);
  const journeys = manifest.sourceJourneys.filter(r => !r.error);
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`Done -> ${OUT}`);
  for (const v of manifest.viewports)
    for (const r of v.results)
      console.log(`- ${v.viewport}/${r.step}: ${r.file || r.error}`);
  for (const r of manifest.sourceJourneys)
    console.log(`- source/${r.step}: ${r.error || `${r.button} -> returned to ${r.returned}`}`);
  console.log(`Screenshots: ${shots.length}/${allSteps.length} steps; source journeys: ${journeys.length}/${manifest.sourceJourneys.length} clean`);
  const errs = allSteps.flatMap(r => [...(r.consoleErrors || []), ...(r.pageErrors || [])]);
  console.log(errs.length ? `Console/page errors: ${errs.length} (see manifest.json)` : 'Console/page errors: none');
  process.exit(fail.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
