// The construction kit: every shape is assembled from these three primitives.
export { obdlznik } from './obdlznik.js';
export { prstenec } from './prstenec.js';
export { kvapka } from './krivka.js';

// Mirror a list of subpaths horizontally around x = axis (for shapes whose
// heavy side is a parameter; the generic `mirror` transform stays separate).
export function zrkadliX(subpaths, axis) {
  const fx = (x) => 2 * axis - x;
  return subpaths.map((sp) => ({
    ...sp,
    segs: sp.segs.map((s) => {
      if (s.c === 'Z') return s;
      if (s.c !== 'C') return { ...s, x: fx(s.x) };
      return { ...s, x1: fx(s.x1), x2: fx(s.x2), x: fx(s.x) };
    }),
  }));
}
