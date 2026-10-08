// koleno — a heavy L-shaped corner, like the top-left corner of E or F: a
// vertical arm going down and a horizontal arm going right. Arm ends are cut
// square; the outer corner is widely rounded, the inner corner only slightly.

import { roundedPolygon } from '../geometry.js';
import { ValidationError } from '../errors.js';

export const id = 'koleno';
export const name = 'Koleno';

export const params = {
  ramenoX: { label: 'rameno X', type: 'number', min: 0.1, max: 20 },
  ramenoY: { label: 'rameno Y', type: 'number', min: 0.1, max: 20 },
};

export function build(p, axes, prop) {
  const pr = prop.proporcie.koleno;
  const t = axes.heavy;

  if (p.ramenoX <= t + 0.01 || p.ramenoY <= t + 0.01) {
    throw new ValidationError(
      `Koleno: ramená musia byť dlhšie ako hrúbka (${t.toFixed(3)}). Zväčči ramenoX/ramenoY alebo zníž Weight.`);
  }

  const pts = [
    { x: 0, y: p.ramenoY },      // bottom of the vertical arm
    { x: 0, y: 0 },              // outer corner
    { x: p.ramenoX, y: 0 },      // end of the horizontal arm
    { x: p.ramenoX, y: t },      // arm end, inner side
    { x: t, y: t },              // inner corner
    { x: t, y: p.ramenoY },      // end of the vertical arm, inner side
  ];
  const radii = [0, pr.outerRadius * t, 0, 0, pr.innerRadius * t, 0];

  return {
    subpaths: [{ segs: roundedPolygon(pts, radii) }],
    joints: [
      { x: p.ramenoX, y: t / 2, dir: 'right' },
      { x: t / 2, y: p.ramenoY, dir: 'down' },
    ],
  };
}
