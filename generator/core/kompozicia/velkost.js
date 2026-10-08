// Shape sizes: a size s in dieliks is drawn from the `velkost` range shaped by
// `variacia` and `rozlozenie`, then mapped to the type's length parameters.
// Shapes are never scaled afterwards — stroke thickness always comes from the
// axes, so only parameter values change with s.

import { clamp } from '../geometry.js';
import { rngRange } from './rng.js';

// Snap to half a dielik — the placement grid works in the same steps.
export function snapHalf(v) {
  return Math.round(v * 2) / 2;
}

// One draw from the size distribution. `variacia` first narrows the range
// around the midpoint (0 = everything at the midpoint, 100 = full range),
// `rozlozenie` then shapes what happens inside that range.
export function drawSize(rng, { velkost, variacia, rozlozenie, koeficienty }) {
  const [min, max] = velkost;
  const mid = (min + max) / 2;
  const half = ((max - min) / 2) * (variacia / 100);
  const lo = mid - half;
  const hi = mid + half;
  let s;
  if (rozlozenie === 'malePlusVelke') {
    s = rng() < koeficienty.pMalych ? rngRange(rng, lo, mid) : rngRange(rng, mid, hi);
  } else if (rozlozenie === 'krajne') {
    const spread = (hi - lo) * koeficienty.rozptyl;
    s = rng() < 0.5 ? rngRange(rng, lo, lo + spread) : rngRange(rng, hi - spread, hi);
  } else {
    s = rngRange(rng, lo, hi); // rovnomerne
  }
  return clamp(Math.round(s), min, max);
}

// Size s → parameters for one type. Ratios live in proporcie.json
// (kompozicia.velkostTvaru); this function only reads them, with the per-type
// mapping documented here:
//   noha, hmotaSoStrbinou  one length parameter equals s
//   oblouk                 vyska = s, sirka = max(1, round(s · sirkaPomer))
//   hacikSKvapkou          vyska = s
//   obloukPata, stvrtoblouk  polomer = s · polomerPomer (foot stays heavy)
//   kvapka, kruh, bod      accents — fixed sizes from proporcie (bod stays
//                          automatic, derived from heavy)
export function paramsFor(type, s, defaults, cfg) {
  const p = { ...defaults };
  const c = cfg[type] || {};
  for (const key of c.zVelkosti || []) p[key] = s;
  if (type === 'oblouk') p.sirka = Math.max(1, Math.round(s * c.sirkaPomer));
  // pätky: the arc radius grows with s, the foot stays heavy
  if (c.polomerPomer) p.polomer = snapHalf(s * c.polomerPomer);
  // fixed accents and fixed values — numbers other than the
  // named ratios are plain parameter values
  for (const [key, value] of Object.entries(c)) {
    if (['zVelkosti', 'sirkaPomer', 'polomerPomer'].includes(key)) continue;
    if (key in p || value === null) p[key] = value;
  }
  // bod with no explicit priemer keeps null (auto from heavy)
  return p;
}
