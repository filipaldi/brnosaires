#!/usr/bin/env node
// CLI of the Brnos Aires shape generator (phase 1).
//
//   node generator/cli.js typy
//   node generator/cli.js tvar --typ oblouk --weight 60 --contrast 80 --out /tmp/o.svg
//   node generator/cli.js vzorkovnik --spoje --out /tmp/v.svg --png
//
// Only node:util parseArgs, no CLI libraries. Exit codes: 0 ok, 1 bad input.

import { parseArgs } from 'node:util';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import {
  existsSync, readdirSync, statSync, writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { TYPES, defaultParams, paramSpec, buildShape, proporcie } from './core/index.js';
import { computeAxes } from './core/axes.js';
import { renderShapeSvg, renderSheetSvg } from './core/svg.js';
import { ValidationError } from './core/errors.js';

const SCRIPT = 'node generator/cli.js';

function die(msg) {
  console.error(`Chyba: ${msg}`);
  process.exit(1);
}

function usage() {
  console.log(`Generátor tvarov Brnos Aires — fáza 1

Použitie:
  ${SCRIPT} typy
  ${SCRIPT} tvar --typ <id> [--weight <0-100>] [--contrast <0-100>] [--zaoblenie <0-100>]
            [--param kľúč=hodnota]... [--rotate 0|90|180|270] [--mirror]
            --out <súbor.svg> [--png]
  ${SCRIPT} vzorkovnik [--typ <id|all>] [--weight 20,40,60,80] [--contrast 70] [--zaoblenie <0-100>]
            [--spoje] --out <súbor.svg> [--png]

Zoznam typov a ich parametrov: ${SCRIPT} typy`);
}

function parse(command, args, options) {
  try {
    return parseArgs({ args, options, strict: true, allowPositionals: false }).values;
  } catch (e) {
    die(`zlé voľby príkazu ${command}: ${e.message.split('\n')[0]}. Spusti „${SCRIPT}“ bez argumentov pre nápovedu.`);
  }
}

function fmtSk(n) {
  return String(n).replace('.', ',');
}

function parseAxisNumber(value, name) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0 || n > 100) {
    die(`${name} musí byť číslo v rozsahu 0–100 (dostal som „${value}“).`);
  }
  return n;
}

function parseAxisList(raw, name) {
  const parts = raw.split(',').map((s) => s.trim()).filter(Boolean);
  if (!parts.length) die(`${name}: zadaný zoznam je prázdny, formát je napr. „20,40,60,80“.`);
  return parts.map((p) => parseAxisNumber(p, name));
}

function resolveType(typ) {
  const ids = TYPES.map((t) => t.id);
  if (!ids.includes(typ)) {
    die(`Neznámy typ tvaru „${typ}“. Platné typy: ${ids.join(', ')}.`);
  }
  return typ;
}

function parseParams(typ, rawList) {
  const spec = paramSpec(typ);
  const out = {};
  for (const raw of rawList) {
    const eq = raw.indexOf('=');
    if (eq < 1) die(`--param očakáva tvar kľúč=hodnota (dostal som „${raw}“).`);
    const key = raw.slice(0, eq);
    const s = spec[key];
    if (!s) {
      die(`Neznámy parameter „${key}“ pre typ ${typ}. Platné parametre: ${Object.keys(spec).join(', ')}.`);
    }
    const value = raw.slice(eq + 1);
    if (s.type === 'enum') {
      if (!s.values.includes(value)) {
        die(`Parameter „${key}“ prijíma iba ${s.values.join(' | ')} (dostal som „${value}“).`);
      }
      out[key] = value;
      continue;
    }
    const n = Number(value);
    if (!Number.isFinite(n)) die(`Parameter „${key}“ musí byť číslo (dostal som „${value}“).`);
    if (s.type === 'integer' && !Number.isInteger(n)) {
      die(`Parameter „${key}“ musí byť celé číslo (dostal som „${value}“).`);
    }
    if (n < s.min || n > s.max) {
      die(`Parameter „${key}“ musí byť v rozsahu ${fmtSk(s.min)}–${fmtSk(s.max)} (dostal som ${fmtSk(n)}).`);
    }
    out[key] = n;
  }
  return out;
}

function paramsSummary(typ) {
  const spec = paramSpec(typ);
  const values = defaultParams(typ);
  return Object.keys(spec)
    .map((key) => (values[key] === null ? 'auto' : String(values[key]).replace('.', ',')))
    .join(' · ');
}

function writeOut(file, content) {
  writeFileSync(file, content, 'utf8');
  console.log(`Zapísané: ${file}`);
}

// --- typy ------------------------------------------------------------------

function cmdTypy() {
  console.log('Tvary generátora Brnos Aires:\n');
  for (const { id, name } of TYPES) {
    console.log(`${id} — ${name}`);
    const spec = paramSpec(id);
    const values = defaultParams(id);
    for (const [key, s] of Object.entries(spec)) {
      let type;
      if (s.type === 'enum') type = s.values.join(' | ');
      else if (s.type === 'integer') type = `celé číslo ${fmtSk(s.min)}–${fmtSk(s.max)}`;
      else type = `číslo ${fmtSk(s.min)}–${fmtSk(s.max)}`;
      const def = values[key] === null ? 'auto' : String(values[key]).replace('.', ',');
      console.log(`  ${key.padEnd(12)} ${s.label.padEnd(26)} ${type}, predvolené ${def}`);
    }
    console.log('');
  }
  console.log('Spoločné pre každý tvar: rotate (0|90|180|270), mirror (true/false).');
  console.log('Hodnoty proporcií sa ladia v generator/proporcie.json.');
}

// --- tvar ------------------------------------------------------------------

function cmdTvar(args) {
  const opts = parse('tvar', args, {
    typ: { type: 'string' },
    weight: { type: 'string', default: '60' },
    contrast: { type: 'string', default: '70' },
    zaoblenie: { type: 'string', default: String(proporcie.osi.zaoblenie) },
    param: { type: 'string', multiple: true, default: [] },
    rotate: { type: 'string', default: '0' },
    mirror: { type: 'boolean', default: false },
    out: { type: 'string' },
    png: { type: 'boolean', default: false },
  });
  if (!opts.typ) die("Chýba --typ <id>. Zoznam typov: node generator/cli.js typy");
  if (!opts.out) die('Chýba --out <súbor.svg>, kam mám výsledok zapísať.');

  const typ = resolveType(opts.typ);
  const rotate = Number(opts.rotate);
  if (![0, 90, 180, 270].includes(rotate)) {
    die(`--rotate prijíma iba 0, 90, 180 alebo 270 (dostal som „${opts.rotate}“).`);
  }
  const axes = computeAxes(
    parseAxisNumber(opts.weight, 'Weight'),
    parseAxisNumber(opts.contrast, 'Contrast'),
    proporcie,
    parseAxisNumber(opts.zaoblenie, 'Zaoblenie'));
  const params = { ...parseParams(typ, opts.param), rotate, mirror: opts.mirror };
  const shape = buildShape(typ, params, axes);
  const svg = renderShapeSvg(shape, { pxPerDielik: 100, margin: 0.25 });
  writeOut(opts.out, svg);
  if (opts.png) return renderPng(opts.out, pngPathFor(opts.out));
}

// --- vzorkovnik ------------------------------------------------------------

function pngPathFor(svgFile) {
  return svgFile.replace(/\.svg$/i, '') + '.png';
}

function cmdVzorkovnik(args) {
  const opts = parse('vzorkovnik', args, {
    typ: { type: 'string', default: 'all' },
    weight: { type: 'string', default: '20,40,60,80' },
    contrast: { type: 'string', default: '70' },
    zaoblenie: { type: 'string', default: String(proporcie.osi.zaoblenie) },
    spoje: { type: 'boolean', default: false },
    out: { type: 'string' },
    png: { type: 'boolean', default: false },
  });
  if (!opts.out) die('Chýba --out <súbor.svg>, kam mám vzorkovník zapísať.');

  const types = opts.typ === 'all'
    ? TYPES.map((t) => t.id)
    : opts.typ.split(',').map((s) => s.trim()).filter(Boolean).map(resolveType);
  const weights = parseAxisList(opts.weight, 'Weight');
  const contrasts = parseAxisList(opts.contrast, 'Contrast');
  const zaoblenie = parseAxisNumber(opts.zaoblenie, 'Zaoblenie');

  const colHeaders = weights.map((w) => `Weight ${fmtSk(w)}`);

  const rows = [];
  for (const typ of types) {
    const spec = paramSpec(typ);
    const values = defaultParams(typ);
    const summary = Object.keys(spec)
      .map((key) => (values[key] === null ? 'auto' : String(values[key]).replace('.', ',')))
      .join(' · ');
    for (const c of contrasts) {
      const cells = weights.map((w) => ({
        shape: buildShape(typ, defaultParams(typ), computeAxes(w, c, proporcie, zaoblenie)),
      }));
      const label = TYPES.find((t) => t.id === typ).name
        + (contrasts.length > 1 ? ` · C ${fmtSk(c)}` : '');
      rows.push({ label, sub: summary, cells, jointDots: true });
    }
  }

  const svg = renderSheetSvg({
    title: 'Vzorkovník tvarov · Brnos Aires',
    colHeaders,
    rows,
    showJoints: opts.spoje,
  });
  writeOut(opts.out, svg);
  if (opts.png) return renderPng(opts.out, pngPathFor(opts.out));
}

// --- PNG rendering ---------------------------------------------------------

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

async function renderPng(svgFile, pngFile) {
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

// --- main ------------------------------------------------------------------

const [command, ...rest] = process.argv.slice(2);

try {
  if (!command) {
    usage();
    process.exit(1);
  }
  let promise;
  switch (command) {
    case 'typy': cmdTypy(); break;
    case 'tvar': promise = cmdTvar(rest); break;
    case 'vzorkovnik': promise = cmdVzorkovnik(rest); break;
    default:
      usage();
      die(`neznámy príkaz „${command}“. Platné príkazy: typy, tvar, vzorkovnik.`);
  }
  if (promise) await promise;
} catch (e) {
  if (e instanceof ValidationError) die(e.message);
  die(e?.stack || e?.message || String(e));
}
