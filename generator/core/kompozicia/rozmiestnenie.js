// Free placement (`rozmiestnenie: "volne"`). Shapes chain at their joints like
// the typeface itself joins components: a chain starts at a free grid position
// and grows by attaching the next shape's opposite-direction, same-thickness
// joint onto one of the chain's open joints (exact coincidence). Joined ends
// are recorded in `spoje` on both shapes so the rebuild keeps them square.
// Every open end of a finished chain gets a teardrop. Accents (kruh, and
// teardrops hung along a straight line) sit beside their chain. Filling stops
// at the area target (`hustota` × free area) or after `maxPokusov` draws.

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
  const s = sPevne ?? drawSize(rng, { velkost: ctx.velkosti[typ] });
  const params = paramsFor(typ, s, ctx.defaultsOf(typ), ctx.velkostTvaru);
  // every drop in the composition gets its own tail and height
  const [c0, c1] = ctx.kvapka.chvost;
  const [v0, v1] = ctx.kvapka.vyska;
  if ('chvost' in params) params.chvost = Math.round(c0 + rng() * (c1 - c0));
  if ('kvapkaVyska' in params) params.kvapkaVyska = Math.round(v0 + rng() * (v1 - v0));
  if (typ === 'kvapka') params.vyska = Math.round(v0 + rng() * (v1 - v0));
  // a leg is a hairline or a heavy stroke; arcs stay hairlines unless no
  // pätka can carry a hairline into a heavy stroke (low contrast)
  if (typ === 'noha' || (ctx.bezPatiek && 'hrubka' in params && typ !== 'kvapka')) {
    params.hrubka = rng() < 0.5 ? 'vlas' : 'plna';
  }
  if (typ === 'kvapka') {
    params.hrubka = rng() < 0.5 ? 'vlas' : 'plna';
    krkPreSirku(rng, params, params.hrubka === 'plna' ? ctx.axes.heavy : ctx.axes.hair, ctx);
  }
  return { typ, s, params };
}

function orientuj(r, { rotate, mirror }, ctx) {
  return { ...r, rotate, mirror, shape: ctx.build(r.typ, { ...r.params, rotate, mirror }, ctx.axes) };
}

// One shape drawn from the spec's distributions: type, size, orientation.
function potiahni(rng, typ, ctx) {
  return orientuj(potiahniRozmer(rng, typ, ctx), rngPick(rng, ORIENTACIE), ctx);
}

// Pick a type for a chain from what its quota still asks for: each type
// weighted by how many of it the chain still needs. Connectors (spojky) have
// no quota; they come in with a fixed share whenever a transition is needed.
function vyberTyp(rng, typy, ctx, chain) {
  const zostava = (t) => (ctx.spojky.includes(t) ? null : chain.kvoty[t] || 0);
  const spolu = typy.reduce((a, t) => a + (zostava(t) ?? 0), 0);
  const vahy = typy.map((t) => zostava(t) ?? ctx.spojkaPomer / 100 * Math.max(spolu, 1));
  const suma = vahy.reduce((a, v) => a + v, 0);
  if (!suma) return null;
  let r = rng() * suma;
  for (let i = 0; i < typy.length; i++) {
    r -= vahy[i];
    if (r < 0) return typy[i];
  }
  return typy[typy.length - 1];
}

// How many of each type one chain of n elements holds: the whole part of
// n · share, the rest handed out at random weighted by the fractions, so a
// small share still shows up in some chains.
function kvoty(rng, n, pomery) {
  const typy = Object.keys(pomery).filter((t) => pomery[t] > 0);
  const spolu = typy.reduce((a, t) => a + pomery[t], 0);
  const out = {};
  const zvysky = [];
  let pocet = 0;
  for (const t of typy) {
    const x = n * pomery[t] / spolu;
    out[t] = Math.floor(x);
    pocet += out[t];
    zvysky.push([t, x - out[t]]);
  }
  while (pocet < n && zvysky.length) {
    let r = rng() * zvysky.reduce((a, [, z]) => a + z, 0);
    let i = 0;
    while (i < zvysky.length - 1 && (r -= zvysky[i][1]) >= 0) i++;
    out[zvysky[i][0]]++;
    pocet++;
    zvysky.splice(i, 1);
  }
  return out;
}

// Neck blend (krk) that gives a teardrop the drawn width for a neck of
// thickness t: the drop's size follows its neck (scale = t / (10 + 30 · krk)),
// so a heavy neck would otherwise blow it up.
// width = (150 + 150 · chvost) · scale
function krkPreSirku(rng, params, t, ctx) {
  const [w0, w1] = ctx.kvapka.sirka;
  const sirka = w0 + rng() * (w1 - w0);
  const k = ((150 + 150 * params.chvost / 100) * t / sirka - 10) / 30;
  params.krk = Math.round(Math.min(Math.max(k, 0), 1) * 100);
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
function prirast(rng, chain, ctx, pokusy, minDlzka = 1, { koniec = null, typy = ctx.typyRetezi, kvota = true } = {}) {
  const otvoren = koniec ?? chain.open[rngInt(rng, chain.open.length)];
  chain.posledny = otvoren;
  // a drawn type with no joint of the open end's thickness cannot attach at
  // all; such draws are skipped without spending an attempt
  for (let i = 0, tahov = 0; i < pokusy && ctx.pokusov < ctx.maxPokusov && tahov < pokusy * 8; tahov++) {
    const typ = kvota ? vyberTyp(rng, typy, ctx, chain) : typy[rngInt(rng, typy.length)];
    if (!typ) return null;
    // some pairs never join directly (a half ring onto another half ring)
    if (ctx.zakazanePary.some(([a, b]) => (a === typ && b === otvoren.entry.typ)
      || (b === typ && a === otvoren.entry.typ))) continue;
    const r0 = potiahniRozmer(rng, typ, ctx);
    const spoje0 = orientuj(r0, ORIENTACIE[0], ctx).shape.joints;
    if (!spoje0.some((j) => Math.abs(j.t - otvoren.j.t) < 1e-9)) continue;
    // a shape with a single joint (kvapka) ends the chain on this
    // side; the last open end of a chain still below its minimum length
    // must keep growing
    if (spoje0.length < 2 && chain.open.length < 2 && chain.members.length + 1 < minDlzka) continue;
    i++;
    ctx.pokusov++;
    // a chain winds through the space left between other figures: when the
    // drawn size does not fit, the same type is tried smaller, down to the
    // minimum size
    const sMin = ctx.velkosti[typ][0];
    const rozmery = [r0, ...[0.6, 0.35].map((k) => r0.s * k).filter((s) => s > sMin)
      .map((s) => potiahniRozmer(rng, typ, ctx, Math.round(s))), potiahniRozmer(rng, typ, ctx, sMin)];
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
          // within its own chain a shape only must not overlap (a tiny pätka
          // leaves no room for the gap); other figures keep the normal gap
          if (ctx.placed.some((p) => (chain.members.includes(p)
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
  velkosti,
  stlpce, bandY, bandH, zony, medzera, hustota, maxPokusov, skok,
  retazenieDlzka, retazeniePokusy, dotyk, neuspechov, spojky = [], spojkyMinKontrast = 0.8, spojkaPomer = 30, zakazanePary = [], pomery = {}, kvapka,
}) {
  const zoneArea = zony.reduce((a, z) => a + z.rect.w * z.rect.h, 0);
  const freeArea = Math.max(stlpce * bandH - zoneArea, 0);
  // Ink-weighted coverage: a bare bbox area counts empty space, so sparse
  // shapes (kvapka, polkruh) would hit the target while the canvas stays empty.
  const pokrytie = (typ, box) => box.w * box.h * (vahyTvaru[typ] ?? 1);
  const target = hustota * freeArea;

  // Every element belongs to a chain. pomery give each type's share of one
  // chain: the chain's drawn length is split into a quota per type. Types
  // with joints are its links; a kvapka in the quota hangs along a straight
  // leg and a kruh sits beside the chain. The teardrops that end every line
  // come on top of the quota.
  // a pätka turns a hairline into a heavy foot: with contrast it is switched
  // on by itself as the connector between thin and heavy strokes; at low
  // contrast there is no such transition and it is left out
  const bezPatiek = axes.hair > spojkyMinKontrast * axes.heavy;
  if (!bezPatiek) typy = [...typy, ...spojky.filter((t) => !typy.includes(t))];
  const maSpoje = {};
  for (const typ of new Set(typy)) {
    maSpoje[typ] = build(typ, defaultsOf(typ), axes).joints.length > 0;
  }
  const typyRetezi = typy.filter((t) => maSpoje[t] && t !== 'kvapka');
  // connectors (spojky) only ever grow out of another shape's open joint
  const typyZakladne = typyRetezi.filter((t) => !spojky.includes(t));
  const typyKvapky = ['kvapka'];

  const ctx = {
    build, axes, defaultsOf, velkostTvaru, velkosti,
    stlpce, bandY, bandH, zony, medzera, dotyk, pokusov: 0, maxPokusov,
    typyRetezi, placed: null, kvapka, bezPatiek, zakazanePary, spojky, spojkaPomer,
  };

  const placed = [];
  ctx.placed = placed;
  const chains = [];
  let area = 0;
  // A finished chain ends every line with a teardrop: each open end, also
  // the ones growth found blocked, gets a kvapka with a neck of the same
  // thickness. A chain shorter than the minimum length, or with an end no
  // kvapka fits on, is taken back off the canvas, so no lone shape and no
  // bare line end is left over.
  const minDlzka = retazenieDlzka[0];
  const odstran = (chain) => {
    for (const m of chain.members) {
      placed.splice(placed.indexOf(m), 1);
      area -= pokrytie(m.typ, m.bbox);
    }
    chain.members = [];
    chain.open = [];
  };
  const vyber = (chain, m) => {
    placed.splice(placed.indexOf(m), 1);
    area -= pokrytie(m.typ, m.bbox);
    chain.members.splice(chain.members.indexOf(m), 1);
  };
  const uzavri = (chain) => {
    chain.closed = true;
    // the chain's length counts its links and the accents it will get
    const dlzka = () => chain.members.filter((m) => !m.cap && !spojky.includes(m.typ)).length + chain.akcenty;
    if (dlzka() < minDlzka) return odstran(chain);
    const konce = [...chain.open, ...chain.blokovane];
    chain.open = [];
    while (konce.length) {
      const koniec = konce.pop();
      const vysledok = typyKvapky.length
        ? prirast(rng, chain, ctx, retazeniePokusy, 1, { koniec, typy: typyKvapky, kvota: false })
        : null;
      if (vysledok) {
        Object.assign(vysledok.entry, { rodic: koniec, cap: true });
        placed.push(vysledok.entry);
        area += pokrytie(vysledok.entry.typ, vysledok.entry.bbox);
        chain.members.push(vysledok.entry);
        continue;
      }
      // no teardrop fits here: step back — take off the shape that owns this
      // end (when nothing but teardrops hangs on it) and end the line one
      // shape earlier
      const e = koniec.entry;
      const deti = chain.members.filter((m) => m.rodic?.entry === e);
      if (!e.rodic || !deti.every((m) => m.cap)) return odstran(chain);
      for (const m of [e, ...deti]) vyber(chain, m);
      const rodic = e.rodic.entry;
      rodic.spoje.splice(rodic.spoje.indexOf(e.rodic.j.id), 1);
      for (let i = konce.length - 1; i >= 0; i--) if (konce[i].entry === e) konce.splice(i, 1);
      konce.push(e.rodic);
    }
    if (dlzka() < minDlzka) odstran(chain);
  };

  const zacniRetaz = () => {
    const [minD, maxD] = retazenieDlzka;
    const n = rngInt(rng, maxD - minD + 1) + minD;
    const chain = { kvoty: kvoty(rng, n, pomery), blokovane: [], closed: false };
    // accents in the quota need something to sit by; a chain whose quota
    // has no link at all cannot start
    const typ = vyberTyp(rng, typyZakladne, ctx, chain);
    if (!typ) return false;
    const k = potiahni(rng, typ, ctx);
    const bb = k.shape.bbox;
    if (bb.w > stlpce + 1e-9 || bb.h > bandH + 1e-9) return false;
    const box = nahodnaPozicia(rng, bb, { stlpce, bandY, bandH, zony, placed, medzera, skok });
    if (!box) return false;
    const entry = umiestni(k, box);
    placed.push(entry);
    area += pokrytie(k.typ, box);
    chain.kvoty[typ]--;
    chain.members = [entry];
    chain.open = entry.joints.map((j) => ({ entry, j }));
    chain.akcenty = (chain.kvoty.kruh || 0) + (chain.kvoty.kvapka || 0);
    chains.push(chain);
    return true;
  };

  // Phase 1 — chains, one at a time: a new chain grows until it reaches its
  // drawn length (from retazenieDlzka [min, max]) or runs out of open ends.
  // Phase 1 stops after `neuspechov` failures in a row, so the leftover space
  // still gets its accents.
  let zlyhania = 0;
  while (area < target && ctx.pokusov < maxPokusov && zlyhania < neuspechov && typyZakladne.length) {
    ctx.pokusov++;
    if (!zacniRetaz()) {
      zlyhania++;
      continue;
    }
    const chain = chains[chains.length - 1];
    while (!chain.closed && ctx.pokusov < maxPokusov) {
      const linky = typyRetezi.some((t) => !spojky.includes(t) && chain.kvoty[t] > 0);
      if (!chain.open.length || !linky) {
        uzavri(chain);
        break;
      }
      const vysledok = prirast(rng, chain, ctx, retazeniePokusy, minDlzka);
      if (!vysledok) {
        // this end is blocked (it still gets its teardrop when the chain
        // closes); the chain stops growing only when no open end is left
        chain.open = chain.open.filter((o) => o !== chain.posledny);
        chain.blokovane.push(chain.posledny);
        continue;
      }
      const { entry, spoj, otvoren } = vysledok;
      entry.rodic = otvoren;
      placed.push(entry);
      area += pokrytie(entry.typ, entry.bbox);
      chain.members.push(entry);
      if (chain.kvoty[entry.typ]) chain.kvoty[entry.typ]--;
      chain.open = chain.open.filter((o) => o !== otvoren);
      chain.open.push(...entry.joints.filter((j) => j.id !== spoj.id).map((j) => ({ entry, j })));
    }
    zlyhania = chain.members.length ? 0 : zlyhania + 1;
  }

  for (const chain of chains) if (!chain.closed) uzavri(chain);

  // Phase 2 — the accents in each finished chain's quota. A kruh sits beside
  // one of the chain's shapes with the normal gap; a kvapka hangs along one
  // of its straight legs, parallel to it, its neck sunk into the leg.
  const bocnaKvapka = (chain) => {
    const nohy = chain.members.filter((m) => m.typ === 'noha');
    for (let pokus = 0; pokus < 20 && nohy.length; pokus++) {
      const host = nohy[rngInt(rng, nohy.length)];
      const hb = host.bbox;
      const zvisla = hb.h > hb.w;
      const t = zvisla ? hb.w : hb.h;
      const r = potiahniRozmer(rng, 'kvapka', ctx);
      r.params.hrubka = Math.abs(t - axes.heavy) < 1e-9 ? 'plna' : 'vlas';
      krkPreSirku(rng, r.params, t, ctx);
      for (const o of zamiesaj(rng, ORIENTACIE)) {
        const k = orientuj(r, o, ctx);
        const j = k.shape.joints[0];
        if (zvisla !== (j.dir === 'up' || j.dir === 'down')) continue;
        const bb = k.shape.bbox;
        // the whole drop lies alongside the leg, the joint on its axis
        const d0 = zvisla ? bb.y - j.y : bb.x - j.x;
        const d1 = zvisla ? bb.y + bb.h - j.y : bb.x + bb.w - j.x;
        const od = (zvisla ? hb.y : hb.x) - d0;
        const po = (zvisla ? hb.y + hb.h : hb.x + hb.w) - d1;
        if (po < od) continue;
        const pos = od + rng() * (po - od);
        const jx = zvisla ? hb.x + t / 2 : pos;
        const jy = zvisla ? pos : hb.y + t / 2;
        const box = { x: bb.x - j.x + jx, y: bb.y - j.y + jy, w: bb.w, h: bb.h };
        if (!voFormate(box, ctx)) continue;
        if (zony.some((z) => vZone(box, z))) continue;
        if (placed.some((p) => p !== host && blizsieAko(box, p.bbox, medzera))) continue;
        const entry = umiestni(k, box);
        entry.spoje.push(j.id);
        entry.bok = true;
        placed.push(entry);
        area += pokrytie('kvapka', box);
        return true;
      }
    }
    return false;
  };
  const kruzok = (chain) => {
    for (let pokus = 0; pokus < 40; pokus++) {
      const m = chain.members[rngInt(rng, chain.members.length)].bbox;
      const k = potiahni(rng, 'kruh', ctx);
      const bb = k.shape.bbox;
      const strana = rngInt(rng, 4);
      const box = { w: bb.w, h: bb.h };
      if (strana < 2) {
        box.x = m.x + rng() * m.w - bb.w / 2;
        box.y = strana === 0 ? m.y - medzera - bb.h : m.y + m.h + medzera;
      } else {
        box.y = m.y + rng() * m.h - bb.h / 2;
        box.x = strana === 2 ? m.x - medzera - bb.w : m.x + m.w + medzera;
      }
      if (!voFormate(box, ctx)) continue;
      if (zony.some((z) => vZone(box, z))) continue;
      if (placed.some((p) => blizsieAko(box, p.bbox, medzera))) continue;
      placed.push(umiestni(k, box));
      area += pokrytie('kruh', box);
      return true;
    }
    return false;
  };
  for (const chain of chains) {
    if (!chain.members.length) continue;
    for (let n = 0; n < (chain.kvoty.kvapka || 0); n++) bocnaKvapka(chain);
    for (let n = 0; n < (chain.kvoty.kruh || 0); n++) kruzok(chain);
  }

  const varovania = [];
  if (!placed.length) varovania.push('Na plátne sa nezmestil žiadny tvar.');
  else if (area < target) varovania.push(`Na plátne sa zmestilo len ${placed.length} tvarov.`);
  return { placed, varovania };
}
