// Optional PNG export shared by the CLI and the scripts: render an SVG file
// with headless Chromium via Playwright from the global node_modules, browser
// in PLAYWRIGHT_BROWSERS_PATH. Zero runtime dependencies — when Playwright or
// the browser is missing, nothing is rendered and the SVG stays written.

import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { existsSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function pngPathFor(svgFile) {
  return svgFile.replace(/\.svg$/i, '') + '.png';
}

function findChromium() {
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH;
  if (!root || !existsSync(root)) return null;
  const dirs = readdirSync(root).sort().reverse(); // newest chromium-* first
  const candidates = [];
  for (const d of dirs) {
    const base = path.join(root, d);
    candidates.push(
      path.join(base, 'chrome-linux', 'chrome'),
      path.join(base, 'chrome-linux', 'headless_shell'),
    );
  }
  return candidates.find((p) => existsSync(p) && statSync(p).isFile()) || null;
}

export async function renderPng(svgFile, pngFile) {
  let chromium = null;
  try {
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    const require = createRequire(path.join(globalRoot, 'noop.js'));
    chromium = require('playwright').chromium;
  } catch {
    // handled below
  }
  if (!chromium) {
    console.error('Pozor: Playwright sa nenašiel v globálnych node_modules (npm root -g), PNG nebol vygenerovaný. SVG zostáva zapísané.');
    return;
  }

  let browser = null;
  try {
    browser = await chromium.launch();
  } catch {
    const exe = findChromium();
    if (!exe) {
      console.error('Pozor: nenašiel sa prehliadač Chromium (PLAYWRIGHT_BROWSERS_PATH), PNG nebol vygenerovaný. SVG zostáva zapísané.');
      return;
    }
    browser = await chromium.launch({ executablePath: exe });
  }

  try {
    const page = await browser.newPage({ deviceScaleFactor: 2 });
    await page.goto(pathToFileURL(path.resolve(svgFile)).href);
    const el = await page.$('svg');
    if (!el) throw new Error('v SVG chýba koreňový element <svg>');
    await el.screenshot({ path: pngFile });
    console.log(`Zapísané: ${pngFile}`);
  } finally {
    await browser.close();
  }
}
