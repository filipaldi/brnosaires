#!/usr/bin/env node
// porovnaj-koleno — the designer's reference koleno (red, semi-transparent)
// overlaid on the generator's construction (black) at the same scale, to check
// how the shape is assembled from the primitives.
//
// Reference (viewBox 0 0 200 810): hair = 10, ring outer radius 100, block
// 200 wide from y = 100 to 810, top-right corner radius 30. One dielik =
// 200 units, so ours is built with polomer 0.5, sirka 1, dlzka 3.55,
// ramenoX 0, hair 0.05 and zaoblenie 0.3 (radius = zaoblenie · min(w,h)/2,
// w = 200 units → 30). The axes are passed straight to the shape's build —
// koleno only reads hair and zaoblenie, heavy is never used.
//
//   node generator/scripts/porovnaj-koleno.js --out <súbor.svg> [--png]

import { parseArgs } from 'node:util';
import { writeFileSync } from 'node:fs';

import { findShape } from '../core/shapes/index.js';
import { serializeSubpath } from '../core/geometry.js';
import { parsePath } from '../core/primitives/krivka.js';
import { renderPng, pngPathFor } from '../png.js';

const SCRIPT = 'node generator/scripts/porovnaj-koleno.js';

const REFERENCE_D =
  'M200,810v-590c0-20-11-30-30-30h-70c-56,0-90-48-90-90h-10v710Z'
  + 'M0,100c0,55,45,100,100,100v-10c-49,0-90-41-90-90s41-90,90-90v-10c-55,0-100,45-100,100Z';

const UNITS_PER_DIELIK = 200; // 1 unit = 1 px in the output SVG
const W = 200;
const H = 810;

function die(msg) {
  console.error(`Chyba: ${msg}`);
  process.exit(1);
}

function parse(args) {
  try {
    return parseArgs({ args, options: {
      out: { type: 'string' },
      png: { type: 'boolean', default: false },
    }, strict: true, allowPositionals: false }).values;
  } catch (e) {
    die(`zlé voľby: ${e.message.split('\n')[0]}. Spusti „${SCRIPT} --out <súbor.svg> [--png]“.`);
  }
}

// --- our koleno, in the shape's own frame (ring centre 0.5, 0.5) ------------

const shape = findShape('koleno').build(
  { polomer: 0.5, sirka: 1, dlzka: 3.55, ramenoX: 0 },
  { heavy: 0.27, hair: 10 / UNITS_PER_DIELIK, zaoblenie: 30 / 100 },
);
const oursD = shape.subpaths.map((s) => serializeSubpath(s.segs)).join(' ');

// --- outline distance (rasterized, both directions) -------------------------
// Both shapes are unions of overlapping solids, so internal construction
// edges (e.g. the small block ending inside the big one) are not outline.
// Each union is rasterized to a 1 px grid; the visible outline is its
// boundary pixels, and the deviation is the nearest-distance maximum over
// both directions.

function cubicAt(p0, c1, c2, p1, t) {
  const u = 1 - t;
  const a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
  return {
    x: a * p0.x + b * c1.x + c * c2.x + d * p1.x,
    y: a * p0.y + b * c1.y + c * c2.y + d * p1.y,
  };
}

// Flatten one closed subpath (already in px) to a dense polyline: line
// segments (and the Z closing edge) subdivided to ~step px, curves sampled
// perCurve times.
function flatten(segs, perCurve = 24, step = 4) {
  const pts = [];
  let cur = null;
  let start = null;
  const line = (to) => {
    const n = Math.max(1, Math.ceil(Math.hypot(to.x - cur.x, to.y - cur.y) / step));
    for (let i = 1; i <= n; i++) {
      pts.push({ x: cur.x + (to.x - cur.x) * i / n, y: cur.y + (to.y - cur.y) * i / n });
    }
    cur = to;
  };
  for (const s of segs) {
    if (s.c === 'M') {
      cur = { x: s.x, y: s.y };
      start = cur;
      pts.push(cur);
    } else if (s.c === 'L') {
      line({ x: s.x, y: s.y });
    } else if (s.c === 'C') {
      const c1 = { x: s.x1, y: s.y1 }, c2 = { x: s.x2, y: s.y2 }, p1 = { x: s.x, y: s.y };
      for (let i = 1; i <= perCurve; i++) pts.push(cubicAt(cur, c1, c2, p1, i / perCurve));
      cur = p1;
    } else if (s.c === 'Z' && start) {
      if (cur.x !== start.x || cur.y !== start.y) line(start);
      cur = start;
    }
  }
  return pts;
}

// Split a parsed path (M...Z M...Z in one array) into subpath arrays.
function splitSubpaths(segs) {
  const out = [];
  let cur = null;
  for (const s of segs) {
    if (s.c === 'M') { cur = [s]; out.push(cur); } else if (cur) cur.push(s);
  }
  return out;
}

// Even-odd scanline fill of one simple polygon into a binary grid.
function fillPolygon(grid, poly, w, h) {
  for (let y = 0; y < h; y++) {
    const sy = y + 0.5;
    const xs = [];
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const a = poly[j], b = poly[i];
      if ((a.y > sy) !== (b.y > sy)) {
        xs.push(a.x + ((sy - a.y) / (b.y - a.y)) * (b.x - a.x));
      }
    }
    xs.sort((p, q) => p - q);
    for (let k = 0; k + 1 < xs.length; k += 2) {
      const x0 = Math.max(0, Math.round(xs[k]));
      const x1 = Math.min(w - 1, Math.round(xs[k + 1]));
      for (let x = x0; x <= x1; x++) grid[y * w + x] = 1;
    }
  }
}

function boundaryPixels(grid, w, h) {
  const out = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      if (!grid[y * w + x]) continue;
      const open = x === 0 || x === w - 1 || y === 0 || y === h - 1
        || !grid[y * w + x - 1] || !grid[y * w + x + 1]
        || !grid[(y - 1) * w + x] || !grid[(y + 1) * w + x];
      if (open) out.push({ x, y });
    }
  }
  return out;
}

// Max over `from` of the nearest distance to any pixel of `to`.
function maxNearest(from, to) {
  let worst = 0;
  for (const p of from) {
    let best = Infinity;
    for (const q of to) {
      const d = (p.x - q.x) ** 2 + (p.y - q.y) ** 2;
      if (d < best) best = d;
    }
    worst = Math.max(worst, Math.sqrt(best));
  }
  return worst;
}

const toPx = (s) => (s.c === 'C'
  ? { ...s, x1: s.x1 * UNITS_PER_DIELIK, y1: s.y1 * UNITS_PER_DIELIK, x2: s.x2 * UNITS_PER_DIELIK, y2: s.y2 * UNITS_PER_DIELIK, x: s.x * UNITS_PER_DIELIK, y: s.y * UNITS_PER_DIELIK }
  : s.c === 'Z' ? s : { ...s, x: s.x * UNITS_PER_DIELIK, y: s.y * UNITS_PER_DIELIK });

const oursGrid = new Uint8Array(W * H);
for (const s of shape.subpaths) fillPolygon(oursGrid, flatten(s.segs.map(toPx)), W, H);
const refGrid = new Uint8Array(W * H);
for (const s of splitSubpaths(parsePath(REFERENCE_D))) fillPolygon(refGrid, flatten(s), W, H);
const oursEdge = boundaryPixels(oursGrid, W, H);
const refEdge = boundaryPixels(refGrid, W, H);
const dOurs = maxNearest(oursEdge, refEdge);
const dRef = maxNearest(refEdge, oursEdge);
console.log(
  `Maximálna odchýlka obrysov: ${Math.max(dOurs, dRef).toFixed(2)} px `
  + `(naša → referencia ${dOurs.toFixed(2)} px, referencia → naša ${dRef.toFixed(2)} px).`);

// --- SVG ---------------------------------------------------------------------

const opts = parse(process.argv.slice(2));
if (!opts.out) die('Chýba --out <súbor.svg>, kam mám porovnanie zapísať.');

const svg = [
  `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`,
  `<rect width="${W}" height="${H}" fill="#fff"/>`,
  `<path d="${oursD}" fill="#000" fill-rule="nonzero" transform="scale(${UNITS_PER_DIELIK})"/>`,
  `<path d="${REFERENCE_D}" fill="#e00" fill-opacity="0.5" fill-rule="nonzero"/>`,
  '</svg>',
  '',
].join('\n');
writeFileSync(opts.out, svg, 'utf8');
console.log(`Zapísané: ${opts.out}`);
if (opts.png) await renderPng(opts.out, pngPathFor(opts.out));
