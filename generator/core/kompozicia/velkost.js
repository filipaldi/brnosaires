// Shape sizes: a size s in dieliks is drawn from the type's `velkosti` range shaped by
// `variacia`, then mapped to the type's length parameters.
// Shapes are never scaled afterwards — stroke thickness always comes from the
// axes, so only parameter values change with s.

import { clamp } from '../geometry.js';
import { rngRange } from './rng.js';

// Snap to half a dielik — the placement grid works in the same steps.
export function snapHalf(v) {
  return Math.round(v * 2) / 2;
}

// One draw from the size range. `variacia` narrows the range around the
// midpoint (0 = everything at the midpoint, 100 = full range); inside it the
// size is spread evenly.
export function drawSize(rng, { velkost, variacia }) {
  const [min, max] = velkost;
  const mid = (min + max) / 2;
  const half = ((max - min) / 2) * (variacia / 100);
  return clamp(Math.round(rngRange(rng, mid - half, mid + half)), min, max);
}

// Size s → parameters for one type. Ratios live in proporcie.json
// (kompozicia.velkostTvaru); this function only reads them, with the per-type
// mapping documented here:
//   noha                   one length parameter equals s
//   stvrtoblouk            polomer = s · polomerPomer (foot stays heavy)
//   polkruh, stvrtkruh     polomer = s · polomerPomer
//   kruh                   priemer = s · priemerPomer
//   kvapka                 width from kvapka.sirka, not from s
export function paramsFor(type, s, defaults, cfg) {
  const p = { ...defaults };
  const c = cfg[type] || {};
  for (const key of c.zVelkosti || []) p[key] = s;
  // arcs and pätky: the radius grows with s (a pätka's foot stays heavy)
  if (c.polomerPomer) p.polomer = snapHalf(s * c.polomerPomer);
  if (c.priemerPomer) p.priemer = s * c.priemerPomer;
  // fixed accents and fixed values — numbers other than the
  // named ratios are plain parameter values
  for (const [key, value] of Object.entries(c)) {
    if (['zVelkosti', 'sirkaPomer', 'polomerPomer', 'priemerPomer'].includes(key)) continue;
    if (key in p || value === null) p[key] = value;
  }
  return p;
}
