'use strict';
// Visual sweep for CHP-Knowledge-Builder 3D (committed copy).
// Captures overview / tagged equipment / connections / desk at 1440px + 480px,
// plus browser console + page errors, into tmp/visual-checks/<batch>/.
//
// Prerequisites (one time; stays inside gitignored tmp/ so the repo stays clean):
//   cd tmp/visual-checks && npm init -y && npm i -D playwright@1.64.0
//   npx playwright install chromium
//
// Usage (app must be running, e.g. via start.bat on port 8765):
//   node tools/visual_sweep.cjs --port 8765 --out tmp/visual-checks/B17 [--tags EAC-9,EBA-10]
//
// Output:
//   <out>/<viewport>/<name>.png  +  <out>/manifest.json
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

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await playwright.chromium.launch().catch(e => {
    console.error('Could not launch Chromium. Did you run `npx playwright install chromium`?\n' + String(e).slice(0, 400));
    process.exit(3);
  });
  const manifest = { base: BASE, tags: TAGS, at: new Date().toISOString(), viewports: [] };
  try {
    for (const vp of VIEWPORTS) manifest.viewports.push(await runViewport(browser, vp));
  } finally {
    await browser.close();
  }
  const fail = manifest.viewports.flatMap(v => v.results).filter(r => r.error);
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2));
  console.log(`Done -> ${OUT}`);
  for (const v of manifest.viewports)
    for (const r of v.results)
      console.log(`- ${v.viewport}/${r.step}: ${r.file || r.error}`);
  const errs = manifest.viewports.flatMap(v => v.results).flatMap(r => [...(r.consoleErrors || []), ...(r.pageErrors || [])]);
  console.log(errs.length ? `Console/page errors: ${errs.length} (see manifest.json)` : 'Console/page errors: none');
  if (fail.length) process.exitCode = 1;
})().catch(e => { console.error(e); process.exit(1); });
