// Composition API (phase 2). `normalizujSpec` fills a partial spec with
// defaults from proporcie.json and validates everything with Slovak messages;
// `komponuj` places shapes around the zones and writes a standalone SVG.
//
//   import { komponuj } from './core/kompozicia/index.js';
//   const { svg, sirkaPx, vyskaPx, dielik, tvary, varovania } = komponuj(spec);
//
// Everything is deterministic: the `variant` string seeds the PRNG and the
// same spec always produces byte-identical SVG.

import { buildShape, computeAxes, defaultParams, loadProporcie, TYPES } from '../index.js';
import { ValidationError } from '../errors.js';
import { createRng } from './rng.js';
import { placeShapes } from './rozmiestnenie.js';
import { renderSvg, translatePathD } from './svg.js';

const KOMP = loadProporcie().kompozicia;

const JEDNOTKY = ['mm', 'px'];
const ZVYSOK = ['okraje', 'natiahnutie', 'orez'];
const ROZMIESTNENIE = ['volne', 'dlazdice'];
const SPRAVANIE = ['prazdna', 'okraj', 'presah'];
const TYPY_ZONY = ['text', 'fotka', 'prazdna'];
const PISMA = ['Brnos Aires', 'Nunito'];
const ZOROVNANIE = ['vlavo', 'stred', 'vpravo'];
const REZIMY = ['ramik', 'maska', 'prekrytie'];

// --- validation helpers -----------------------------------------------------

function cislo(value, name, { min = -Infinity, max = Infinity, cele = false } = {}) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ValidationError(`${name} musí byť číslo (dostal som „${value}“).`);
  }
  if (cele && !Number.isInteger(value)) {
    throw new ValidationError(`${name} musí byť celé číslo (dostal som ${value}).`);
  }
  if (value < min || value > max) {
    throw new ValidationError(`${name} musí byť v rozsahu ${min}–${max} (dostal som ${value}).`);
  }
  return value;
}

function moznosti(value, name, values) {
  if (!values.includes(value)) {
    throw new ValidationError(`${name} prijíma iba ${values.join(' | ')} (dostal som „${value}“).`);
  }
  return value;
}

function polia(obj, allowed, name) {
  for (const key of Object.keys(obj)) {
    if (!allowed.includes(key)) {
      throw new ValidationError(`Neznáme pole „${key}“ v ${name}. Platné polia: ${allowed.join(', ')}.`);
    }
  }
}

// Height of the format in dieliks — needed for zone bounds in normalizujSpec.
function vyskaVDielikoch(format, grid) {
  return (format.vyska * grid.stlpce) / format.sirka;
}

function normalizujFormat(raw) {
  const d = KOMP.predvolene.format;
  const format = { ...d, ...raw };
  if (raw) polia(raw, Object.keys(d), 'format');
  cislo(format.sirka, 'format.sirka', { min: 1, max: 100000 });
  cislo(format.vyska, 'format.vyska', { min: 1, max: 100000 });
  moznosti(format.jednotka, 'format.jednotka', JEDNOTKY);
  cislo(format.dpi, 'format.dpi', { min: 18, max: 2400 });
  cislo(format.spadavka, 'format.spadavka', { min: 0, max: 100 });
  return format;
}

function normalizujGrid(raw) {
  const d = KOMP.predvolene.grid;
  const grid = { ...d, ...raw };
  if (raw) polia(raw, Object.keys(d), 'grid');
  cislo(grid.stlpce, 'grid.stlpce', { min: 1, max: 100, cele: true });
  moznosti(grid.zvysok, 'grid.zvysok', ZVYSOK);
  return grid;
}

function normalizujKresba(raw) {
  const d = KOMP.predvolene.kresba;
  const kresba = { ...d, ...raw };
  if (raw) polia(raw, Object.keys(d), 'kresba');
  cislo(kresba.weight, 'kresba.weight', { min: 0, max: 100 });
  cislo(kresba.contrast, 'kresba.contrast', { min: 0, max: 100 });
  cislo(kresba.zaoblenie, 'kresba.zaoblenie', { min: 0, max: 100 });
  return kresba;
}

function normalizujKompozicia(raw) {
  const d = KOMP.predvolene.kompozicia;
  // older specs list the types in `typy`: each listed type gets its default
  // weight, the others 0
  if (raw && Array.isArray(raw.typy) && !raw.pomery) {
    const { typy, ...zvysok } = raw;
    raw = {
      ...zvysok,
      pomery: Object.fromEntries(Object.entries(d.pomery).map(([t, v]) => [t, typy.includes(t) ? v : 0])),
    };
  }
  // older specs give one size range for all types
  if (raw && Array.isArray(raw.velkost) && !raw.velkosti) {
    const { velkost, ...zvysok } = raw;
    raw = { ...zvysok, velkosti: Object.fromEntries(Object.keys(d.velkosti).map((t) => [t, velkost.slice()])) };
  }
  if (raw && 'rozlozenie' in raw) {
    // dropped setting: sizes are spread evenly over the range
    const { rozlozenie, ...zvysok } = raw;
    raw = zvysok;
  }
  const komp = { ...d, ...raw };
  if (raw) polia(raw, Object.keys(d), 'kompozicia');
  cislo(komp.variacia, 'kompozicia.variacia', { min: 0, max: 100 });
  if (!Array.isArray(komp.retazenieDlzka) || komp.retazenieDlzka.length !== 2) {
    throw new ValidationError('kompozicia.retazenieDlzka musí byť pole [min, max] tvarov v reťazi, napr. [5, 20].');
  }
  cislo(komp.retazenieDlzka[0], 'kompozicia.retazenieDlzka[0]', { min: 1, max: 50, cele: true });
  cislo(komp.retazenieDlzka[1], 'kompozicia.retazenieDlzka[1]', { min: 1, max: 50, cele: true });
  if (!Array.isArray(komp.akcentyNaRetaz) || komp.akcentyNaRetaz.length !== 2) {
    throw new ValidationError('kompozicia.akcentyNaRetaz musí byť pole [min, max] krúžkov a bodov pri jednej reťazi, napr. [1, 10].');
  }
  cislo(komp.akcentyNaRetaz[0], 'kompozicia.akcentyNaRetaz[0]', { min: 0, max: 50, cele: true });
  cislo(komp.akcentyNaRetaz[1], 'kompozicia.akcentyNaRetaz[1]', { min: 0, max: 50, cele: true });
  if (komp.akcentyNaRetaz[0] > komp.akcentyNaRetaz[1]) {
    throw new ValidationError('kompozicia.akcentyNaRetaz[0] musí byť menšia alebo rovná akcentyNaRetaz[1].');
  }
  if (komp.retazenieDlzka[0] > komp.retazenieDlzka[1]) {
    throw new ValidationError('kompozicia.retazenieDlzka[0] musí byť menšia alebo rovná retazenieDlzka[1].');
  }
  // pomery: one weight 0–100 per type; 0 leaves the type out. The share
  // of each type on the canvas follows these weights.
  const vsetky = TYPES.map((t) => t.id);
  // connectors (spojky) are switched on by contrast, never weighted by hand;
  // older specs that still weight them lose those keys
  const spojky = KOMP.rozmiestnenie.retazenie.spojky;
  const zname = vsetky.filter((t) => !spojky.includes(t));
  if (komp.pomery && typeof komp.pomery === 'object') {
    komp.pomery = Object.fromEntries(Object.entries(komp.pomery).filter(([t]) => !spojky.includes(t)));
  }
  if (!komp.pomery || typeof komp.pomery !== 'object' || Array.isArray(komp.pomery)) {
    throw new ValidationError('kompozicia.pomery musí byť objekt { typ: 0–100 }, napr. { "noha": 50, "polkruh": 50 }.');
  }
  for (const [typ, v] of Object.entries(komp.pomery)) {
    if (!zname.includes(typ)) {
      throw new ValidationError(`Neznámy typ tvaru „${typ}“ v kompozicia.pomery. Platné typy: ${zname.join(', ')}.`);
    }
    cislo(v, `kompozicia.pomery.${typ}`, { min: 0, max: 100, cele: true });
  }
  komp.pomery = Object.fromEntries(zname.map((t) => [t, komp.pomery[t] ?? 0]));
  komp.typy = zname.filter((t) => komp.pomery[t] > 0);
  if (!komp.typy.length) {
    throw new ValidationError('kompozicia.pomery: aspoň jeden typ musí mať pomer väčší ako 0.');
  }
  // velkosti: one size range [min, max] in dieliky per type
  if (!komp.velkosti || typeof komp.velkosti !== 'object' || Array.isArray(komp.velkosti)) {
    throw new ValidationError('kompozicia.velkosti musí byť objekt { typ: [min, max] }, napr. { "noha": [1, 6] }.');
  }
  for (const [typ, v] of Object.entries(komp.velkosti)) {
    if (!vsetky.includes(typ)) {
      throw new ValidationError(`Neznámy typ tvaru „${typ}“ v kompozicia.velkosti. Platné typy: ${vsetky.join(', ')}.`);
    }
    const kde = `kompozicia.velkosti.${typ}`;
    if (!Array.isArray(v) || v.length !== 2) {
      throw new ValidationError(`${kde} musí byť pole [min, max] v dielikoch, napr. [1, 6].`);
    }
    cislo(v[0], `${kde}[0]`, { min: 1, max: 40, cele: true });
    cislo(v[1], `${kde}[1]`, { min: 1, max: 40, cele: true });
    if (v[0] > v[1]) throw new ValidationError(`${kde}[0] musí byť menšia alebo rovná ${kde}[1].`);
  }
  komp.velkosti = Object.fromEntries(vsetky.map((t) => [t, komp.velkosti[t] ?? d.velkosti[t] ?? [1, 6]]));
  moznosti(komp.rozmiestnenie, 'kompozicia.rozmiestnenie', ROZMIESTNENIE);
  return komp;
}

function normalizujZonu(raw, index, stlpce, vyskaD) {
  const name = `zóna ${index + 1}`;
  polia(raw, [
    'typ', 'x', 'y', 'w', 'h', 'spravanie',
    'text', 'pismo', 'velkost', 'zarovnanie', 'riadkovanie',
    'zdroj', 'rezim', 'posun', 'zoom',
  ], name);
  const typ = moznosti(raw.typ ?? 'text', `${name}.typ`, TYPY_ZONY);
  const d = KOMP.zona[typ] || {};
  const zona = { typ, ...d, ...raw };
  cislo(zona.x, `${name}.x`, { min: 0, max: 64, cele: true });
  cislo(zona.y, `${name}.y`, { min: 0, max: 64, cele: true });
  cislo(zona.w, `${name}.w`, { min: 0.5, max: 1000 });
  cislo(zona.h, `${name}.h`, { min: 0.5, max: 1000 });
  if (zona.x + zona.w > stlpce + 1e-6) {
    throw new ValidationError(`${name} presahuje šírku formátu (${zona.x} + ${zona.w} > ${stlpce} stĺpcov).`);
  }
  if (zona.y + zona.h > vyskaD + 1e-6) {
    throw new ValidationError(`${name} presahuje výšku formátu (${zona.y} + ${zona.h} > ${Math.round(vyskaD * 100) / 100} dielika).`);
  }
  moznosti(zona.spravanie, `${name}.spravanie`, SPRAVANIE);

  if (typ === 'text') {
    if (zona.text != null && typeof zona.text !== 'string') {
      throw new ValidationError(`${name}.text musí byť reťazec.`);
    }
    moznosti(zona.pismo, `${name}.pismo`, PISMA);
    cislo(zona.velkost, `${name}.velkost`, { min: 0.1, max: 20 });
    moznosti(zona.zarovnanie, `${name}.zarovnanie`, ZOROVNANIE);
    cislo(zona.riadkovanie, `${name}.riadkovanie`, { min: 0.5, max: 3 });
  }
  if (typ === 'fotka') {
    if (zona.zdroj != null && typeof zona.zdroj !== 'string') {
      throw new ValidationError(`${name}.zdroj musí byť reťazec (cesta alebo data URL).`);
    }
    moznosti(zona.rezim, `${name}.rezim`, REZIMY);
    if (!Array.isArray(zona.posun) || zona.posun.length !== 2
      || zona.posun.some((v) => typeof v !== 'number' || !Number.isFinite(v))) {
      throw new ValidationError(`${name}.posun musí byť pole [x, y] čísel.`);
    }
    cislo(zona.zoom, `${name}.zoom`, { min: 0.05, max: 10 });
  }
  return zona;
}

// --- public API -------------------------------------------------------------

export function normalizujSpec(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new ValidationError('Spec kompozície musí byť JSON objekt.');
  }
  polia(input, ['format', 'grid', 'kresba', 'kompozicia', 'variant', 'inverzia', 'zony'], 'spec');
  const spec = structuredClone(input);

  spec.format = normalizujFormat(spec.format);
  spec.grid = normalizujGrid(spec.grid);
  spec.kresba = normalizujKresba(spec.kresba);
  spec.kompozicia = normalizujKompozicia(spec.kompozicia);
  if (spec.variant !== undefined && typeof spec.variant !== 'string' && typeof spec.variant !== 'number') {
    throw new ValidationError('variant musí byť text alebo číslo.');
  }
  if (spec.variant === undefined) spec.variant = KOMP.predvolene.variant;
  spec.variant = String(spec.variant);
  if (spec.inverzia === undefined) spec.inverzia = KOMP.predvolene.inverzia;
  if (typeof spec.inverzia !== 'boolean') {
    throw new ValidationError('inverzia musí byť true/false.');
  }

  const vyskaD = vyskaVDielikoch(spec.format, spec.grid);
  const zony = spec.zony ?? KOMP.predvolene.zony;
  if (!Array.isArray(zony)) {
    throw new ValidationError('zony musí byť pole zón.');
  }
  spec.zony = zony.map((z, i) => normalizujZonu(z ?? {}, i, spec.grid.stlpce, vyskaD));
  return spec;
}

export function komponuj(input, { fontUrls } = {}) {
  const spec = normalizujSpec(input);
  const { format, grid, kresba, kompozicia: komp } = spec;

  const dielik = format.sirka / grid.stlpce;
  const vyskaD = format.vyska / dielik;
  const bleedD = format.spadavka / dielik;

  // The usable band for shapes depends on how the leftover height is handled.
  // Zones always live in absolute dieliks from the top of the trimmed format.
  let bandY = 0;
  let bandH = vyskaD;
  if (grid.zvysok === 'okraje') {
    const rows = Math.floor(vyskaD + 1e-9);
    bandH = rows;
    bandY = (vyskaD - rows) / 2;
  } else if (grid.zvysok === 'orez') {
    bandH = Math.ceil(vyskaD - 1e-9); // the partial row is filled and cropped by the viewBox
  }

  const axes = computeAxes(kresba.weight, kresba.contrast, loadProporcie(), kresba.zaoblenie);
  const varovania = [];
  if (komp.rozmiestnenie === 'dlazdice') {
    varovania.push('Rozmiestnenie „dlazdice“ ešte nie je postavené, kreslím ako voľné.');
  }

  const rng = createRng(spec.variant);
  const zony = spec.zony.map((z) => ({
    ...z,
    rect: { x: z.x, y: z.y, w: z.w, h: z.h },
  }));
  const { placed, varovania: varovaniaUmiestnenia } = placeShapes(rng, {
    build: buildShape,
    axes,
    defaultsOf: defaultParams,
    typy: komp.typy,
    pomery: komp.pomery,
    velkostTvaru: KOMP.velkostTvaru,
    vahyTvaru: KOMP.vahyTvaru,
    velkosti: komp.velkosti,
    variacia: komp.variacia,
    stlpce: grid.stlpce,
    bandY,
    bandH,
    zony: zony.map((z) => ({ rect: z.rect, spravanie: z.spravanie, okraj: KOMP.svg.okraj })),
    medzera: KOMP.rozmiestnenie.medzera,
    hustota: KOMP.rozmiestnenie.hustota,
    maxPokusov: KOMP.rozmiestnenie.maxPokusov,
    skok: KOMP.rozmiestnenie.skok,
    retazenieDlzka: komp.retazenieDlzka,
    akcentyNaRetaz: komp.akcentyNaRetaz,
    retazeniePokusy: KOMP.rozmiestnenie.retazenie.pokusy,
    dotyk: KOMP.rozmiestnenie.retazenie.dotyk,
    neuspechov: KOMP.rozmiestnenie.retazenie.neuspechov,
    spojky: KOMP.rozmiestnenie.retazenie.spojky,
    spojkyMinKontrast: KOMP.rozmiestnenie.retazenie.spojkyMinKontrast,
    spojkaPomer: KOMP.rozmiestnenie.retazenie.spojkaPomer,
    zakazanePary: KOMP.rozmiestnenie.retazenie.zakazanePary,
    model: KOMP.rozmiestnenie.retazenie.model,
    kvapka: KOMP.kvapka,
  });
  varovania.push(...varovaniaUmiestnenia);

  // Rebuild accepted shapes and bake the translation into their path data —
  // the pattern layer is one compound path without per-shape transforms.
  // `spoje` names the ends joined to a neighbour, rebuilt square.
  const tvary = placed.map((p) => {
    const shape = buildShape(p.typ, {
      ...p.params, rotate: p.rotate, mirror: p.mirror, spoje: p.spoje,
    }, axes);
    return {
      ...p,
      bbox: { x: p.x, y: p.y, w: p.bbox.w, h: p.bbox.h },
      d: shape.paths.map((path) => translatePathD(path, p.x, p.y)).join(' '),
    };
  });

  const svg = renderSvg({
    stlpce: grid.stlpce,
    vyskaD,
    bleedD,
    jednotka: format.jednotka,
    sirka: format.sirka,
    vyska: format.vyska,
    spadavka: format.spadavka,
    placed: tvary,
    zony,
    inverzia: spec.inverzia,
    fontUrls,
    cfg: KOMP.svg,
  });

  const naPx = format.jednotka === 'mm' ? 25.4 / format.dpi : 1;
  return {
    svg,
    sirkaPx: Math.round(format.sirka / naPx),
    vyskaPx: Math.round(format.vyska / naPx),
    dielik,
    tvary: tvary.map(({ d, ...t }) => t),
    varovania,
  };
}
