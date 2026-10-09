// Fallback engine used until generator/core/kompozicia/ exists (phase 2).
// It implements the same normalizujSpec / komponuj contract with a trivial
// seeded random-grid placement built on buildShape from the core, so the UI
// is usable now and switches to the real engine automatically later.

import { buildShape, computeAxes, defaultParams, TYPES, proporcie } from '../core/index.js';
import { ValidationError } from '../core/errors.js';

const ALL_TYPES = TYPES.map((t) => t.id);

const DEFAULTS = {
  format: { sirka: 420, vyska: 594, jednotka: 'mm', dpi: 300, spadavka: 3 },
  grid: { stlpce: 8, zvysok: 'okraje' },
  kresba: { weight: 60, contrast: 70, zaoblenie: 30 },
  kompozicia: {
    velkost: [1, 6], rozlozenie: 'rovnomerne',
    typy: [...ALL_TYPES], rozmiestnenie: 'volne',
  },
  variant: '42',
  inverzia: false,
  zony: [],
};

// ---------- validation helpers ----------

function num(value, name, { min = -Infinity, max = Infinity, integer = false } = {}) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ValidationError(`${name} musí byť číslo (dostal som „${value}“).`);
  }
  if (integer && !Number.isInteger(value)) {
    throw new ValidationError(`${name} musí byť celé číslo (dostal som ${value}).`);
  }
  if (value < min || value > max) {
    throw new ValidationError(`${name} musí byť v rozsahu ${min}–${max} (dostal som ${value}).`);
  }
  return value;
}

function enumv(value, name, values) {
  if (!values.includes(value)) {
    throw new ValidationError(`${name} prijíma iba ${values.join(' | ')} (dostal som „${value}“).`);
  }
  return value;
}

function validateZone(z, index) {
  const kde = `Zóna č. ${index + 1}`;
  if (!z || typeof z !== 'object') throw new ValidationError(`${kde} nie je objekt.`);
  enumv(z.typ, `${kde}: typ`, ['text', 'fotka', 'prazdna']);
  num(z.x, `${kde}: x`, { integer: true });
  num(z.y, `${kde}: y`, { integer: true });
  num(z.w, `${kde}: šírka`, { min: 1, integer: true });
  num(z.h, `${kde}: výška`, { min: 1, integer: true });
  if (z.spravanie !== undefined) enumv(z.spravanie, `${kde}: správanie`, ['prazdna', 'presah', 'okraj']);
  if (z.typ === 'text') {
    if (typeof z.text !== 'string') throw new ValidationError(`${kde}: text musí byť reťazec.`);
    if (z.pismo !== undefined) enumv(z.pismo, `${kde}: písmo`, ['Brnos Aires', 'Nunito']);
    if (z.velkost !== undefined) num(z.velkost, `${kde}: veľkosť písma`, { min: 0.1, max: 40 });
    if (z.zarovnanie !== undefined) enumv(z.zarovnanie, `${kde}: zarovnanie`, ['vlavo', 'na stred', 'vpravo']);
    if (z.riadkovanie !== undefined) num(z.riadkovanie, `${kde}: riadkovanie`, { min: 0.5, max: 4 });
  }
  if (z.typ === 'fotka') {
    if (typeof z.zdroj !== 'string' || !z.zdroj) {
      throw new ValidationError(`${kde}: chýba zdroj fotky.`);
    }
    enumv(z.rezim, `${kde}: režim`, ['ramik', 'maska', 'prekrytie']);
    if (z.posun !== undefined) {
      if (!Array.isArray(z.posun) || z.posun.length !== 2
        || typeof z.posun[0] !== 'number' || typeof z.posun[1] !== 'number') {
        throw new ValidationError(`${kde}: posun musí byť dvojica čísel.`);
      }
    }
    if (z.zoom !== undefined) num(z.zoom, `${kde}: zoom`, { min: 0.1, max: 10 });
  }
}

export function normalizujSpec(input) {
  const spec = input && typeof input === 'object' ? input : {};
  const out = structuredClone(DEFAULTS);
  for (const key of ['format', 'grid', 'kresba', 'kompozicia']) {
    if (spec[key] && typeof spec[key] === 'object') Object.assign(out[key], spec[key]);
  }
  const f = out.format, g = out.grid, k = out.kresba, c = out.kompozicia;

  num(f.sirka, 'Šírka formátu', { min: 10, max: 20000 });
  num(f.vyska, 'Výška formátu', { min: 10, max: 20000 });
  enumv(f.jednotka, 'Jednotka', ['mm', 'px']);
  num(f.dpi, 'DPI', { min: 18, max: 2400, integer: true });
  num(f.spadavka, 'Spadávka', { min: 0, max: 50 });
  num(g.stlpce, 'Grid', { min: 1, max: 64, integer: true });
  enumv(g.zvysok, 'Zvyšok výšky', ['okraje', 'natiahnutie', 'orez']);
  num(k.weight, 'Weight', { min: 0, max: 100 });
  num(k.contrast, 'Contrast', { min: 0, max: 100 });
  num(k.zaoblenie, 'Zaoblenie', { min: 0, max: 100 });

  if (!Array.isArray(c.velkost) || c.velkost.length !== 2) {
    throw new ValidationError('Veľkosť musí byť dvojica [min, max] v dielikoch.');
  }
  num(c.velkost[0], 'Veľkosť min', { min: 0.2, max: 40 });
  num(c.velkost[1], 'Veľkosť max', { min: 0.2, max: 40 });
  if (c.velkost[0] > c.velkost[1]) {
    throw new ValidationError('Veľkosť min musí byť menšia alebo rovná max.');
  }
  enumv(c.rozlozenie, 'Rozloženie', ['rovnomerne', 'malePlusVelke', 'krajne']);
  if (!Array.isArray(c.typy) || c.typy.length === 0) {
    throw new ValidationError('Typy: vyber aspoň jeden typ tvaru.');
  }
  for (const t of c.typy) {
    if (!ALL_TYPES.includes(t)) {
      throw new ValidationError(`Neznámy typ tvaru „${t}“. Platné typy: ${ALL_TYPES.join(', ')}.`);
    }
  }
  enumv(c.rozmiestnenie, 'Rozmiestnenie', ['volne', 'dlazdice']);

  if (spec.variant !== undefined) {
    if (typeof spec.variant !== 'string' && typeof spec.variant !== 'number') {
      throw new ValidationError('Variant musí byť text alebo číslo.');
    }
    out.variant = String(spec.variant);
  }
  if (spec.inverzia !== undefined) {
    if (typeof spec.inverzia !== 'boolean') {
      throw new ValidationError('Inverzia musí byť true/false.');
    }
    out.inverzia = spec.inverzia;
  }
  if (spec.zony !== undefined) {
    if (!Array.isArray(spec.zony)) throw new ValidationError('Zóny musia byť pole.');
    out.zony = spec.zony.map((z) => {
      validateZone(z, spec.zony.indexOf(z));
      const base = {
        typ: z.typ, x: z.x, y: z.y, w: z.w, h: z.h, spravanie: z.spravanie || 'prazdna',
      };
      if (z.typ === 'text') {
        return {
          ...base, text: z.text ?? '', pismo: z.pismo || 'Brnos Aires',
          velkost: z.velkost ?? 1.2, zarovnanie: z.zarovnanie || 'vlavo',
          riadkovanie: z.riadkovanie ?? 1.1,
        };
      }
      if (z.typ === 'fotka') {
        return {
          ...base, zdroj: z.zdroj, rezim: z.rezim || 'ramik',
          posun: z.posun ?? [0, 0], zoom: z.zoom ?? 1,
        };
      }
      return base;
    });
  }
  return out;
}

// ---------- determinism ----------

function hashString(s) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Round to 3 decimals, trim trailing zeros: stable bytes, readable SVG.
function fmt(n) {
  const r = Math.round(n * 1000) / 1000;
  return Object.is(r, -0) ? '0' : String(r);
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function escAttr(s) {
  return esc(s).replace(/"/g, '&quot;');
}

// ---------- placement ----------

function pickSize(rng, c) {
  const [mn, mx] = c.velkost;
  if (c.rozlozenie === 'krajne') return rng() < 0.5 ? mn : mx;
  if (c.rozlozenie === 'malePlusVelke') {
    const small = rng() < 0.72;
    const mid = (mn + mx) / 2;
    const base = small ? mn : mx;
    return mid + (base - mid) * (0.35 + 0.65 * rng());
  }
  // uniform over the whole range
  return mn + rng() * (mx - mn);
}

function rectsIntersect(a, b, pad = 0) {
  return a.x - pad < b.x + b.w && a.x + a.w + pad > b.x
    && a.y - pad < b.y + b.h && a.y + a.h + pad > b.y;
}

function zoneBlockers(zony) {
  // Rects a placed shape must avoid entirely, and rects where a shape's
  // bbox centre is forbidden (presah).
  const blockers = [];
  const centres = [];
  for (const z of zony) {
    if (z.typ === 'prazdna' || z.spravanie === 'prazdna') {
      blockers.push({ x: z.x, y: z.y, w: z.w, h: z.h });
    } else if (z.spravanie === 'okraj') {
      blockers.push({ x: z.x - 1, y: z.y - 1, w: z.w + 2, h: z.h + 2 });
    } else if (z.spravanie === 'presah') {
      centres.push({ x: z.x, y: z.y, w: z.w, h: z.h });
    }
  }
  return { blockers, centres };
}

function centreIn(rect, zone) {
  const cx = rect.x + rect.w / 2;
  const cy = rect.y + rect.h / 2;
  return cx > zone.x && cx < zone.x + zone.w && cy > zone.y && cy < zone.y + zone.h;
}

function placeShapes(spec, geom, rng, axes) {
  const c = spec.kompozicia;
  const { W, H } = geom;
  const { blockers, centres } = zoneBlockers(spec.zony);
  const placed = [];
  const avg = (c.velkost[0] + c.velkost[1]) / 2;
  const target = Math.max(3, Math.round((W * H * 1.9) / (avg * avg)));
  for (let i = 0; i < target; i++) {
    const typ = c.typy[Math.floor(rng() * c.typy.length)];
    const size = pickSize(rng, c);
    const rotate = [0, 90, 180, 270][Math.floor(rng() * 4)];
    const mirror = rng() < 0.5;
    let shape;
    try {
      shape = buildShape(typ, { rotate, mirror }, axes);
    } catch {
      continue; // a type that rejects these axes: skip it
    }
    const maxDim = Math.max(shape.bbox.w, shape.bbox.h) || 1;
    const s = size / maxDim;
    const w = shape.bbox.w * s;
    const h = shape.bbox.h * s;
    let rect = null;
    for (let attempt = 0; attempt < 120; attempt++) {
      const x = rng() * (W - w);
      const y = rng() * (H - h);
      const candidate = { x, y, w, h };
      if (blockers.some((b) => rectsIntersect(candidate, b, 0.05))) continue;
      if (centres.some((z) => centreIn(candidate, z))) continue;
      if (placed.some((p) => rectsIntersect(candidate, p.rect, 0.12))) continue;
      rect = candidate;
      break;
    }
    if (!rect) continue;
    placed.push({
      typ, rotate, mirror, scale: s, rect,
      params: { ...defaultParams(typ), rotate, mirror },
      d: shape.paths.join(' '),
      bx: shape.bbox.x,
      by: shape.bbox.y,
      bw: shape.bbox.w * s,
      bh: shape.bbox.h * s,
    });
  }
  return placed;
}

// ---------- SVG assembly ----------

function fontFaceCss(fontUrls) {
  const faces = [];
  if (fontUrls['Brnos Aires']) {
    faces.push(
      `@font-face{font-family:'Brnos Aires';src:url('${escAttr(fontUrls['Brnos Aires'])}') format('woff2')}`);
  }
  if (fontUrls.Nunito) {
    faces.push(
      `@font-face{font-family:'Nunito';src:url('${escAttr(fontUrls.Nunito)}') format('truetype');font-weight:300 1000`);
  }
  return faces.length ? faces.join('}') + '}' : '';
}

function patternSvg(placed, fill) {
  return placed.map((p) => (
    `<path d="${p.d}" fill="${fill}" fill-rule="nonzero" `
    + `transform="translate(${fmt(p.rect.x - p.bx * p.scale)} ${fmt(p.rect.y - p.by * p.scale)}) `
    + `scale(${fmt(p.scale)})"/>`
  )).join('');
}

function textZoneSvg(z, fill, dielikUnits) {
  const anchor = z.zarovnanie === 'na stred' ? 'middle' : (z.zarovnanie === 'vpravo' ? 'end' : 'start');
  const pad = 0.15;
  const x = z.zarovnanie === 'na stred' ? z.x + z.w / 2
    : (z.zarovnanie === 'vpravo' ? z.x + z.w - pad : z.x + pad);
  const lines = String(z.text).split('\n');
  const tspans = lines.map((line, i) => (
    `<tspan x="${fmt(x)}" y="${fmt(z.y + z.velkost * 0.78 + i * z.velkost * z.riadkovanie)}">${esc(line)}</tspan>`
  )).join('');
  return `<text font-family="${escAttr(z.pismo)}" font-size="${fmt(z.velkost)}" `
    + `text-anchor="${anchor}" fill="${fill}">${tspans}</text>`;
}

function photoZoneSvg(z, i, geom, fill) {
  const hair = Math.max(geom.b, 0.02) * 0.35; // frame line, visible at any format
  const px = z.x, py = z.y, pw = z.w, ph = z.h;
  const cx = px + pw / 2, cy = py + ph / 2;
  const inner = `<g transform="translate(${fmt(z.posun[0])} ${fmt(z.posun[1])})">`
    + `<image href="${escAttr(z.zdroj)}" x="${fmt(px)}" y="${fmt(py)}" width="${fmt(pw)}" height="${fmt(ph)}" `
    + `preserveAspectRatio="xMidYMid slice" transform="translate(${fmt(cx)} ${fmt(cy)}) scale(${fmt(z.zoom)}) translate(${fmt(-cx)} ${fmt(-cy)})"/></g>`;
  if (z.rezim === 'maska') {
    const maskTyp = 'kruh';
    const shape = buildShape(maskTyp, { priemer: Math.min(pw, ph) }, geom.axes);
    const bx = shape.bbox.x, by = shape.bbox.y;
    const offX = px + (pw - shape.bbox.w) / 2, offY = py + (ph - shape.bbox.h) / 2;
    return `<clipPath id="maska-${i}"><path d="${shape.paths.join(' ')}" `
      + `transform="translate(${fmt(offX - bx)} ${fmt(offY - by)})"/></clipPath>`
      + `<g clip-path="url(#maska-${i})">${inner}</g>`;
  }
  if (z.rezim === 'prekrytie') {
    return `<g style="mix-blend-mode:multiply">${inner}</g>`;
  }
  return inner + `<rect x="${fmt(px)}" y="${fmt(py)}" width="${fmt(pw)}" height="${fmt(ph)}" `
    + `fill="none" stroke="${fill}" stroke-width="${fmt(hair)}"/>`;
}

function spadavkaSvg(geom, fill) {
  const { b, W, H } = geom;
  if (b <= 0.0005) return '';
  const o = b * 0.35; // gap between trim corner and mark
  const l = b * 0.55; // mark length
  const marks = [
    // top-left
    [-o, -o, -o - l, -o], [-o, -o, -o, -o - l],
    // top-right
    [W + o, -o, W + o + l, -o], [W + o, -o, W + o, -o - l],
    // bottom-left
    [-o, H + o, -o - l, H + o], [-o, H + o, -o, H + o + l],
    // bottom-right
    [W + o, H + o, W + o + l, H + o], [W + o, H + o, W + o, H + o + l],
  ];
  return marks.map(([x1, y1, x2, y2]) => (
    `<line x1="${fmt(x1)}" y1="${fmt(y1)}" x2="${fmt(x2)}" y2="${fmt(y2)}" `
    + `stroke="${fill}" stroke-width="${fmt(b * 0.08)}"/>`
  )).join('');
}

export function komponuj(spec, { fontUrls = {} } = {}) {
  spec = normalizujSpec(spec);
  const { format: f, grid: g, kresba: k } = spec;

  const axes = computeAxes(k.weight, k.contrast, proporcie, k.zaoblenie);
  const dielikUnits = f.sirka / g.stlpce; // mm or px per dielik
  const W = g.stlpce;
  const H = f.vyska / dielikUnits;
  const b = f.spadavka / dielikUnits; // bleed in dieliks
  const geom = { W, H, b, dielikUnits, axes };

  const rng = mulberry32(hashString(spec.variant));
  const placed = placeShapes(spec, geom, rng, axes);

  const black = spec.inverzia ? '#fff' : '#000';
  const white = spec.inverzia ? '#000' : '#fff';
  const varovania = [];
  if (spec.kompozicia.rozmiestnenie === 'dlazdice') {
    varovania.push('Rozmiestnenie dlaždice ešte nie je postavené, používam voľné.');
  }
  if (placed.length === 0) {
    varovania.push('Nepodarilo sa umiestniť ani jeden tvar, skús iný variant alebo menšiu veľkosť.');
  }

  const svgParts = [];
  svgParts.push(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${fmt(f.sirka)}${f.jednotka === 'mm' ? 'mm' : ''}" `
    + `height="${fmt(f.vyska)}${f.jednotka === 'mm' ? 'mm' : ''}" `
    + `viewBox="${fmt(-b)} ${fmt(-b)} ${fmt(W + 2 * b)} ${fmt(H + 2 * b)}">`);
  const css = fontFaceCss(fontUrls);
  if (css) svgParts.push(`<defs><style>${css}}</style></defs>`);
  svgParts.push(`<rect x="${fmt(-b)}" y="${fmt(-b)}" width="${fmt(W + 2 * b)}" height="${fmt(H + 2 * b)}" fill="${white}"/>`);

  svgParts.push('<g id="pattern">');
  svgParts.push(patternSvg(placed, black));
  svgParts.push('</g>');

  svgParts.push('<g id="fotky">');
  spec.zony.forEach((z, i) => {
    if (z.typ === 'fotka') svgParts.push(photoZoneSvg(z, i, geom, black));
  });
  svgParts.push('</g>');

  svgParts.push('<g id="text">');
  spec.zony.forEach((z) => {
    if (z.typ === 'text' && z.text) svgParts.push(textZoneSvg(z, black, dielikUnits));
  });
  svgParts.push('</g>');

  svgParts.push('<g id="spadavka">');
  svgParts.push(spadavkaSvg(geom, spec.inverzia ? '#fff' : '#000'));
  svgParts.push('</g>');

  svgParts.push('</svg>');
  svgParts.push('');

  const pxPerUnit = f.jednotka === 'mm' ? f.dpi / 25.4 : 1;
  return {
    svg: svgParts.join('\n'),
    sirkaPx: Math.round(f.sirka * pxPerUnit),
    vyskaPx: Math.round(f.vyska * pxPerUnit),
    dielik: dielikUnits,
    tvary: placed.map((p) => ({
      typ: p.typ,
      params: { ...p.params },
      rotate: p.rotate,
      mirror: p.mirror,
      x: p.rect.x,
      y: p.rect.y,
      bbox: { x: p.rect.x, y: p.rect.y, w: p.bw, h: p.bh },
    })),
    varovania,
  };
}
