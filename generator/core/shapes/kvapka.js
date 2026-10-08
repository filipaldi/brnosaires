// kvapka — a standalone teardrop: a circle plus a tail of two tangent lines
// from the tip. `smer` aims the tip (0 = up, clockwise, degrees); the tail
// length is a proportion of the radius, the tip is slightly rounded.

import { teardropSubpath } from './teardrop.js';

export const id = 'kvapka';
export const name = 'Kvapka';

export const params = {
  velkost: { label: 'veľkosť (násobok heavy)', type: 'number', min: 0.05, max: 5 },
  smer: { label: 'smer špičky', type: 'number', min: -360, max: 360 },
};

const DEG = Math.PI / 180;

export function build(p, axes, prop) {
  const pr = prop.proporcie.kvapka;
  const r = p.velkost * axes.heavy;
  const a = p.smer * DEG;
  const v = { x: Math.sin(a), y: -Math.cos(a) }; // 0 = up, clockwise
  const tail = pr.tail * r;
  const tip = { x: v.x * (r + tail), y: v.y * (r + tail) };
  const segs = teardropSubpath({
    cx: 0, cy: 0, r, tip, tipRadius: pr.tipRadius * axes.hair,
  });
  return { subpaths: [{ segs }], joints: [] };
}
