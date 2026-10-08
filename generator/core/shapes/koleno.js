// koleno — the perpendicular half-ring join, after the designer's reference:
// a hairline half ring (left half, open to the right) + a heavy block flush
// with the ring's outer left edge below it. Left of the ring centre the block
// starts at the ring centre with the inner disc cut out; right of it the block
// starts where the inner circle ends. Optional hairline arm from the ring top.

import { obdlznik, prstenec } from '../primitives/index.js';

export const id = 'koleno';
export const name = 'Koleno';

export const params = {
  polomer: { label: 'polomer', type: 'number', min: 0.05, max: 20 },
  sirka: { label: 'šírka bloku', type: 'number', min: 0.05, max: 20 },
  dlzka: { label: 'dĺžka bloku', type: 'number', min: 0.05, max: 40 },
  ramenoX: { label: 'rameno', type: 'number', min: 0, max: 40 },
};

export function build(p, axes) {
  const { hair: h, zaoblenie: z } = axes;
  const P = p.polomer;
  const r = Math.max(P - h, 0);
  const B = p.sirka;
  const bottom = P + p.dlzka;
  const subpaths = [
    ...prstenec({
      cx: P, cy: P, R: P, t: h, start: 90, sweep: 180, zaoblenie: z, konce: [false, !(p.ramenoX > 0)],
    }),
    // block under the counter, full width, rounded top-right corner
    obdlznik({ x: 0, y: P + r, w: B, h: bottom - P - r, zaoblenie: z, rohy: [false, true, true, true] }),
    // block beside the counter: from the ring centre down, inner circle notched in
    obdlznik({
      x: 0, y: P, w: Math.min(P, B), h: r + (bottom - P - r) / 2, rohy: [false, false, false, false], vyrez: { cx: P, r },
    }),
  ];
  const joints = [{ x: B / 2, y: bottom, dir: 'down' }];
  if (p.ramenoX > 0) {
    subpaths.push(obdlznik({ x: P, y: 0, w: p.ramenoX, h, zaoblenie: z, rohy: [false, true, true, false] }));
    joints.push({ x: P + p.ramenoX, y: h / 2, dir: 'right' });
  }
  return { subpaths, joints };
}
