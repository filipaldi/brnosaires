// Free placement (`rozmiestnenie: "volne"`). Shapes are drawn in batches of
// `davka`, sorted largest bbox first, so the big masses claim space first and
// the accents fill the gaps — otherwise scattered dots block the canvas early.
// Each shape then scans all grid-snapped candidate positions in PRNG order;
// the first position that respects the zones and keeps the configured gap
// from every placed bbox wins. Filling stops at the area target (`hustota` ×
// free area) or after `maxPokusov` shape draws.

import { rngInt, rngPick } from './rng.js';
import { drawSize, paramsFor } from './velkost.js';

// Are two rects closer than `gap` to each other? dx/dy is the separation on
// each axis (negative when the projections overlap); the distance between
// the rects is max(dx, dy), so gap = 0 means plain intersection.
function blizsieAko(a, b, gap) {
  const dx = Math.max(b.x - (a.x + a.w), a.x - (b.x + b.w));
  const dy = Math.max(b.y - (a.y + a.h), a.y - (b.y + b.h));
  return dx < gap - 1e-9 && dy < gap - 1e-9;
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

// zones: [{ rect: {x, y, w, h}, spravanie, okraj }]
export function placeShapes(rng, {
  build, axes, defaultsOf, typy, velkostTvaru, vahyTvaru,
  velkost: velkostCfg, variacia, rozlozenie, rozlozenieKoef,
  stlpce, bandY, bandH, zony, medzera, hustota, maxPokusov, skok, davka,
}) {
  const zoneArea = zony.reduce((a, z) => a + z.rect.w * z.rect.h, 0);
  const freeArea = Math.max(stlpce * bandH - zoneArea, 0);
  // Ink-weighted coverage: a bare bbox area counts empty space, so sparse
  // shapes (nota, oblouk) would hit the target while the canvas stays empty.
  const pokrytie = (typ, box) => box.w * box.h * (vahyTvaru[typ] ?? 1);
  const target = hustota * freeArea;

  const placed = [];
  let area = 0;
  let pokusov = 0;

  while (area < target && pokusov < maxPokusov) {
    // draw a batch, then place largest first (stable order keeps the draw
    // deterministic: same rng consumption regardless of sorting)
    const kandidati = [];
    for (let i = 0; i < davka && pokusov + i < maxPokusov; i++) {
      const typ = rngPick(rng, typy);
      const s = drawSize(rng, { velkost: velkostCfg, variacia, rozlozenie, koeficienty: rozlozenieKoef });
      const params = paramsFor(typ, s, defaultsOf(typ), velkostTvaru);
      const rotate = rngPick(rng, [0, 90, 180, 270]);
      const mirror = rng() < 0.5;
      const shape = build(typ, { ...params, rotate, mirror }, axes);
      kandidati.push({ typ, params, rotate, mirror, shape, s });
    }
    pokusov += kandidati.length;
    kandidati.sort((a, b) => (b.shape.bbox.w * b.shape.bbox.h) - (a.shape.bbox.w * a.shape.bbox.h)
      || b.s - a.s);

    for (const k of kandidati) {
      if (area >= target) break;
      const bb = k.shape.bbox;
      if (bb.w > stlpce + 1e-9 || bb.h > bandH + 1e-9) continue;
      const box = nahodnaPozicia(rng, bb, { stlpce, bandY, bandH, zony, placed, medzera, skok });
      if (!box) continue;
      placed.push({ typ: k.typ, params: k.params, rotate: k.rotate, mirror: k.mirror, x: box.x, y: box.y, bbox: box });
      area += pokrytie(k.typ, box);
    }
  }

  const varovania = [];
  if (!placed.length) varovania.push('Na plátne sa nezmestil žiadny tvar.');
  else if (area < target) varovania.push(`Na plátne sa zmestilo len ${placed.length} tvarov.`);
  return { placed, varovania };
}
