// Free placement (`rozmiestnenie: "volne"`). Shapes chain at their joints like
// the typeface itself joins components: a chain starts at a free grid position
// and grows by attaching the next shape's opposite-direction, same-thickness
// joint onto one of the chain's open joints (exact coincidence). Joined ends
// are recorded in `spoje` on both shapes so the rebuild keeps them square.
// Accents without joints (kruh, bod) and a kvapka on its own are placed after
// the chains, scattered with the normal gap. Filling stops at the area target
// (`hustota` × free area) or after `maxPokusov` shape draws.

import { rngInt, rngPick } from './rng.js';
import { drawSize, paramsFor } from './velkost.js';

const OPPOSITE = { down: 'up', up: 'down', left: 'right', right: 'left' };

// Are two rects closer than `gap` to each other? dx/dy is the separation on
// each axis (negative when the projections overlap); the distance between
// the rects is max(dx, dy), so gap = 0 means plain intersection.
function blizsieAko(a, b, gap) {
  const dx = Math.max(b.x - (a.x + a.w), a.x - (b.x + b.w));
  const dy = Math.max(b.y - (a.y + a.h), a.y - (b.y + b.h));
  return dx < gap - 1e-9 && dy < gap - 1e-9;
}

// Do two rects overlap by more than `inset` on both axes? Used only for the
// directly joined pair: their bboxes share the boundary through the joint, so
// any overlap beyond the inset would be real ink crash.
function prekryv(a, b, inset) {
  const dx = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const dy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return dx > inset && dy > inset;
}

function vZone(box, zone) {
  if (zone.spravanie === 'okraj') {
    // blizsieAko(gap) demands `gap` of separation between the two rects
    return blizsieAko(box, zone.rect, zone.okraj);
  }
  if (zone.spravanie === 'presah') {
    const cx = box.x + box.w / 2;
    const cy = box.y + box.h / 2;
    const r = zone.rect;
    return cx > r.x && cx < r.x + r.w && cy > r.y && cy < r.y + r.h;
  }
  return blizsieAko(box, zone.rect, 0); // prazdna — no shape touches
}

function voFormate(box, { stlpce, bandY, bandH }) {
  return box.x >= -1e-9 && box.y >= bandY - 1e-9
    && box.x + box.w <= stlpce + 1e-9 && box.y + box.h <= bandY + bandH + 1e-9;
}

function nahodnaPozicia(rng, box, { stlpce, bandY, bandH, zony, placed, medzera, skok }) {
  const stepsX = Math.floor((stlpce - box.w) / skok + 1e-9);
  const stepsY = Math.floor((bandH - box.h) / skok + 1e-9);
  if (stepsX < 0 || stepsY < 0) return null;

  // All grid cells that fit this size, visited in PRNG order: a big shape on
  // a half-blocked canvas has few valid anchors, so we scan every cell
  // instead of gambling on one random position per attempt.
  const cells = [];
  for (let i = 0; i <= stepsX; i++) {
    for (let j = 0; j <= stepsY; j++) cells.push([i, j]);
  }
  for (let i = cells.length - 1; i > 0; i--) {
    const j = rngInt(rng, i + 1);
    [cells[i], cells[j]] = [cells[j], cells[i]];
  }

  for (const [i, j] of cells) {
    const candidate = { x: i * skok, y: bandY + j * skok, w: box.w, h: box.h };
    if (zony.some((z) => vZone(candidate, z))) continue;
    if (placed.some((p) => blizsieAko(candidate, p.bbox, medzera))) continue;
    return candidate;
  }
  return null;
}

const ORIENTACIE = [0, 90, 180, 270].flatMap((rotate) => [false, true].map((mirror) => ({ rotate, mirror })));

// Type and size drawn from the spec's distributions, before orientation.
function potiahniRozmer(rng, typ, ctx, sPevne = null) {
  const s = sPevne ?? drawSize(rng, {
    velkost: ctx.velkost, variacia: ctx.variacia, rozlozenie: ctx.rozlozenie, koeficienty: ctx.rozlozenieKoef,
  });
  const params = paramsFor(typ, s, ctx.defaultsOf(typ), ctx.velkostTvaru);
  // every drop in the composition gets its own tail and height
  const [c0, c1] = ctx.kvapka.chvost;
  const [v0, v1] = ctx.kvapka.vyska;
  if ('chvost' in params) params.chvost = Math.round(c0 + rng() * (c1 - c0));
  if ('kvapkaVyska' in params) params.kvapkaVyska = Math.round(v0 + rng() * (v1 - v0));
  if (typ === 'kvapka') params.vyska = Math.round(v0 + rng() * (v1 - v0));
  const [k0, k1] = ctx.kvapka.krk;
  if ('krk' in params) params.krk = Math.round(k0 + rng() * (k1 - k0));
  if (typ === 'kvapka') params.hrubka = rng() < 0.5 ? 'vlas' : 'plna';
  return { typ, s, params };
}

function orientuj(r, { rotate, mirror }, ctx) {
  return { ...r, rotate, mirror, shape: ctx.build(r.typ, { ...r.params, rotate, mirror }, ctx.axes) };
}

// One shape drawn from the spec's distributions: type, size, orientation.
function potiahni(rng, typ, ctx) {
  return orientuj(potiahniRozmer(rng, typ, ctx), rngPick(rng, ORIENTACIE), ctx);
}

// Shuffled copy (Fisher-Yates with the composition's PRNG).
function zamiesaj(rng, list) {
  const out = list.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = rngInt(rng, i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

function umiestni(k, box) {
  return {
    typ: k.typ, params: k.params, rotate: k.rotate, mirror: k.mirror, spoje: [],
    x: box.x, y: box.y, bbox: box,
    joints: k.shape.joints.map((j) => ({ ...j, x: j.x + box.x, y: j.y + box.y })),
  };
}

// Try to attach one shape to an open joint of a chain. Returns the placed
// entry (with the joint it used) or null when no candidate fits.
function prirast(rng, chain, ctx, pokusy) {
  const otvoren = chain.open[rngInt(rng, chain.open.length)];
  for (let i = 0; i < pokusy && ctx.pokusov < ctx.maxPokusov; i++) {
    ctx.pokusov++;
    const typ = rngPick(rng, ctx.typyRetezi);
    const r0 = potiahniRozmer(rng, typ, ctx);
    // a chain winds through the space left between other figures: when the
    // drawn size does not fit, the same type is tried smaller, down to the
    // minimum size
    const sMin = ctx.velkost[0];
    const rozmery = [r0, ...[0.6, 0.35].map((k) => r0.s * k).filter((s) => s > sMin)
      .map((s) => potiahniRozmer(rng, typ, ctx, Math.round(s * 2) / 2)), potiahniRozmer(rng, typ, ctx, sMin)];
    for (const r of rozmery) {
      // every orientation of the drawn shape, in PRNG order, and every joint of
      // it that fits the open end: opposite direction, same stroke thickness
      for (const o of zamiesaj(rng, ORIENTACIE)) {
        const k = orientuj(r, o, ctx);
        const zhody = k.shape.joints.filter(
          (j) => OPPOSITE[j.dir] === otvoren.j.dir && Math.abs(j.t - otvoren.j.t) < 1e-9);
        for (const m of zhody) {
          // translate so the two joints coincide exactly
          const box = {
            x: k.shape.bbox.x + otvoren.j.x - m.x,
            y: k.shape.bbox.y + otvoren.j.y - m.y,
            w: k.shape.bbox.w, h: k.shape.bbox.h,
          };
          if (!voFormate(box, ctx)) continue;
          if (ctx.zony.some((z) => vZone(box, z))) continue;
          if (ctx.placed.some((p) => (p === otvoren.entry
            ? prekryv(box, p.bbox, ctx.dotyk)
            : blizsieAko(box, p.bbox, ctx.medzera)))) continue;
          const entry = umiestni(k, box);
          entry.spoje.push(m.id);
          otvoren.entry.spoje.push(otvoren.j.id);
          return { entry, spoj: m, otvoren };
        }
      }
    }
  }
  return null;
}

// zones: [{ rect: {x, y, w, h}, spravanie, okraj }]
export function placeShapes(rng, {
  build, axes, defaultsOf, typy, velkostTvaru, vahyTvaru,
  velkost: velkostCfg, variacia, rozlozenie, rozlozenieKoef,
  stlpce, bandY, bandH, zony, medzera, hustota, maxPokusov, skok,
  retazenie, retazenieDlzka, retazeniePokusy, dotyk, neuspechov, kvapka,
}) {
  const zoneArea = zony.reduce((a, z) => a + z.rect.w * z.rect.h, 0);
  const freeArea = Math.max(stlpce * bandH - zoneArea, 0);
  // Ink-weighted coverage: a bare bbox area counts empty space, so sparse
  // shapes (nota, oblouk) would hit the target while the canvas stays empty.
  const pokrytie = (typ, box) => box.w * box.h * (vahyTvaru[typ] ?? 1);
  const target = hustota * freeArea;

  // A kvapka can only ever terminate a chain (its neck is its single joint),
  // so chains are started by the types that can grow; kruh and bod have no
  // joints at all and stay scattered accents.
  const maSpoje = {};
  for (const typ of new Set(typy)) {
    maSpoje[typ] = build(typ, defaultsOf(typ), axes).joints.length > 0;
  }
  const typyRetezi = typy.filter((t) => maSpoje[t]);
  const typyZakladne = typyRetezi.filter((t) => t !== 'kvapka');
  const typyAkcentov = typy.filter((t) => !maSpoje[t] || t === 'kvapka');

  const ctx = {
    build, axes, defaultsOf, velkostTvaru, velkost: velkostCfg, variacia, rozlozenie,
    rozlozenieKoef, stlpce, bandY, bandH, zony, medzera, dotyk, pokusov: 0, maxPokusov,
    typyRetezi, placed: null, kvapka,
  };

  const placed = [];
  ctx.placed = placed;
  const chains = [];
  let area = 0;

  const zacniRetaz = () => {
    const k = potiahni(rng, rngPick(rng, typyZakladne), ctx);
    const bb = k.shape.bbox;
    if (bb.w > stlpce + 1e-9 || bb.h > bandH + 1e-9) return;
    const box = nahodnaPozicia(rng, bb, { stlpce, bandY, bandH, zony, placed, medzera, skok });
    if (!box) return false;
    const entry = umiestni(k, box);
    placed.push(entry);
    area += pokrytie(k.typ, box);
    const [minD, maxD] = retazenieDlzka;
    chains.push({
      members: [entry],
      open: entry.joints.map((j) => ({ entry, j })),
      target: rngInt(rng, maxD - minD + 1) + minD,
      closed: false,
    });
    return true;
  };

  // Phase 1 — chains: each drawn shape either continues a chain (probability
  // `retazenie`) or starts a new one.
  // Phase 1 stops after `neuspechov` failures in a row, so the leftover space
  // still gets its accents.
  let zlyhania = 0;
  while (area < target && ctx.pokusov < maxPokusov && zlyhania < neuspechov && typyZakladne.length) {
    const rastuce = chains.filter((c) => !c.closed && c.open.length && c.members.length < c.target);
    if (rastuce.length && rng() < retazenie / 100) {
      const chain = rastuce[rngInt(rng, rastuce.length)];
      const vysledok = prirast(rng, chain, ctx, retazeniePokusy);
      if (!vysledok) {
        chain.closed = true;
        zlyhania++;
        continue;
      }
      zlyhania = 0;
      const { entry, spoj, otvoren } = vysledok;
      placed.push(entry);
      area += pokrytie(entry.typ, entry.bbox);
      chain.members.push(entry);
      chain.open = chain.open.filter((o) => o !== otvoren);
      chain.open.push(...entry.joints.filter((j) => j.id !== spoj.id).map((j) => ({ entry, j })));
      if (chain.members.length >= chain.target) chain.closed = true;
    } else {
      ctx.pokusov++;
      zlyhania = zacniRetaz() ? 0 : zlyhania + 1;
    }
  }

  // Phase 2 — accents in the leftover space, with the normal gap.
  let akcentov = 0;
  while (area < target && akcentov < maxPokusov && typyAkcentov.length) {
    akcentov++;
    const k = potiahni(rng, rngPick(rng, typyAkcentov), ctx);
    const bb = k.shape.bbox;
    if (bb.w > stlpce + 1e-9 || bb.h > bandH + 1e-9) continue;
    const box = nahodnaPozicia(rng, bb, { stlpce, bandY, bandH, zony, placed, medzera, skok });
    if (!box) continue;
    placed.push(umiestni(k, box));
    area += pokrytie(k.typ, box);
  }

  const varovania = [];
  if (!placed.length) varovania.push('Na plátne sa nezmestil žiadny tvar.');
  else if (area < target) varovania.push(`Na plátne sa zmestilo len ${placed.length} tvarov.`);
  return { placed, varovania };
}
