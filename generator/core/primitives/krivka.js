// Primitive 3: a fixed outline drawn by the type designer (assets.json),
// interpolated point by point between its masters and placed by its anchor.
// The curve itself is never redrawn or smoothed.

import ASSETS from '../../assets.json' with { type: 'json' };
import { moveTo, lineTo, curveTo, closePath, clamp } from '../geometry.js';


// Minimal SVG path parser: M L H V C S Z (absolute and relative) to absolute
// segments in the geometry.js model.
export function parsePath(d) {
  const tokens = d.match(/[a-zA-Z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?/g);
  const segs = [];
  let i = 0, cmd = null;
  let x = 0, y = 0, sx = 0, sy = 0, lastC2 = null;
  const num = () => Number(tokens[i++]);
  while (i < tokens.length) {
    if (/[a-zA-Z]/.test(tokens[i])) cmd = tokens[i++];
    const rel = cmd === cmd.toLowerCase();
    const ox = rel ? x : 0, oy = rel ? y : 0;
    switch (cmd.toUpperCase()) {
      case 'M':
        x = ox + num(); y = oy + num(); sx = x; sy = y;
        segs.push(moveTo(x, y)); lastC2 = null;
        cmd = rel ? 'l' : 'L'; // further pairs are implicit lineto
        break;
      case 'L': x = ox + num(); y = oy + num(); segs.push(lineTo(x, y)); lastC2 = null; break;
      case 'H': x = ox + num(); segs.push(lineTo(x, y)); lastC2 = null; break;
      case 'V': y = oy + num(); segs.push(lineTo(x, y)); lastC2 = null; break;
      case 'C': {
        const x1 = ox + num(), y1 = oy + num(), x2 = ox + num(), y2 = oy + num();
        x = ox + num(); y = oy + num();
        segs.push(curveTo(x1, y1, x2, y2, x, y)); lastC2 = { x: x2, y: y2 };
        break;
      }
      case 'S': {
        const x1 = lastC2 ? 2 * x - lastC2.x : x, y1 = lastC2 ? 2 * y - lastC2.y : y;
        const x2 = ox + num(), y2 = oy + num();
        x = ox + num(); y = oy + num();
        segs.push(curveTo(x1, y1, x2, y2, x, y)); lastC2 = { x: x2, y: y2 };
        break;
      }
      case 'Z': segs.push(closePath()); x = sx; y = sy; lastC2 = null; break;
      default: throw new Error(`Nepodporovaný príkaz cesty „${cmd}“.`);
    }
  }
  return segs;
}

const KEYS = ['x1', 'y1', 'x2', 'y2', 'x', 'y'];

function lerpSegs(a, b, f) {
  if (a.length !== b.length || a.some((s, k) => s.c !== b[k].c)) {
    throw new Error('Mastre krivky nemajú rovnakú štruktúru bodov.');
  }
  return a.map((s, k) => {
    const out = { c: s.c };
    for (const key of KEYS) if (key in s) out[key] = s[key] + (b[k][key] - s[key]) * f;
    return out;
  });
}

const parsed = {};
function masters(id) {
  if (!parsed[id]) {
    const asset = ASSETS[id];
    if (!asset) throw new Error(`Neznáma krivka „${id}“.`);
    parsed[id] = { ...asset, masters: asset.masters.map((m) => ({ neck: m.neck, segs: parsePath(m.path) })) };
  }
  return parsed[id];
}

// Map every point of a segment list.
function mapSegs(segs, fn) {
  return segs.map((s) => {
    if (s.c === 'Z') return s;
    const p = fn({ x: s.x, y: s.y });
    if (s.c !== 'C') return { ...s, x: p.x, y: p.y };
    const c1 = fn({ x: s.x1, y: s.y1 });
    const c2 = fn({ x: s.x2, y: s.y2 });
    return { ...s, x1: c1.x, y1: c1.y, x2: c2.x, y2: c2.y, x: p.x, y: p.y };
  });
}

// The teardrop terminal. (x, y) is where the top of the neck lands; the neck
// heads right (before rotate/mirror) and is exactly `hair` thick as long as
// the masters allow it. `vyska` is the drop height in dielik units.
//   rotate: 0/90/180/270 clockwise around the anchor; mirror: flip horizontally
//   around the anchor (neck then heads left).
export function kvapka({ x, y, hair, vyska, rotate = 0, mirror = false, part = 'krivka' }) {
  const a = masters('kvapka');
  const [m0, m1] = a.masters;
  const scale = vyska / a.vyska;
  const n = hair / scale;
  // Outside the masters' range the nearest master is used, never extrapolated.
  const f = clamp((n - m0.neck) / (m1.neck - m0.neck), 0, 1);
  const rad = (rotate * Math.PI) / 180;
  const cos = Math.round(Math.cos(rad)), sin = Math.round(Math.sin(rad));
  const segs = mapSegs(lerpSegs(m0.segs, m1.segs, f), (p) => {
    let px = p.x * scale, py = p.y * scale;
    if (mirror) px = -px;
    return { x: x + px * cos - py * sin, y: y + px * sin + py * cos };
  });
  return { segs, part, neck: (m0.neck + (m1.neck - m0.neck) * f) * scale };
}
