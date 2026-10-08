// kruh — a ring. Two subpaths with opposite winding under fill-rule
// "nonzero" (the inner one is marked as a hole). At extreme Weight the ring
// degrades gracefully to a solid circle (bod).

import { circleSegments } from '../geometry.js';

export const id = 'kruh';
export const name = 'Kruh';

export const params = {
  priemer: { label: 'priemer', type: 'number', min: 0.05, max: 20 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const R = p.priemer / 2;
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;
  const subpaths = [{ segs: circleSegments(R, R, R) }];
  const rInner = R - t;
  if (rInner > 0.02) {
    subpaths.push({ segs: circleSegments(R, R, rInner), hole: true });
  }
  return { subpaths, joints: [] };
}
