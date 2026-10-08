// koleno — the perpendicular half-ring join, after the designer's reference:
// a hairline half ring (left half, open to the right) + a heavy block flush
// with the ring's outer left edge below it. Left of the ring centre the block
// starts at the ring centre with the inner disc cut out; right of it the block
// starts where the inner circle ends. Optional hairline arm from the ring top.
//
// The block is a heavy stroke: its width defaults to `heavy`, and the ring's
// radius to half the block width, as in the reference (block 200, ring 100).

import { obdlznik, prstenec } from '../primitives/index.js';

export const id = 'koleno';
export const name = 'Koleno';

export const params = {
  polomer: { label: 'polomer', type: 'number', min: 0.01, max: 20, nullable: true },
  sirka: { label: 'šírka bloku', type: 'number', min: 0.01, max: 20, nullable: true },
  dlzka: { label: 'dĺžka bloku', type: 'number', min: 0.05, max: 40 },
  ramenoX: { label: 'rameno', type: 'number', min: 0, max: 40 },
};

export function build(p, axes) {
  const { hair: h, zaoblenie: z } = axes;
  const B = p.sirka ?? axes.heavy;
  const P = p.polomer ?? B / 2;
  const r = Math.max(P - h, 0);
  const bottom = P + p.dlzka;
  const spoj = (id) => (p.spoje || []).includes(id);
  // the block bottom is a stroke end of width B; the ring's free top end (no
  // arm) and the arm's far end share the id 'rameno' — they sit at the same spot
  const maRameno = p.ramenoX > 0;
  const subpaths = [
    ...prstenec({
      cx: P, cy: P, R: P, t: h, start: 90, sweep: 180, zaoblenie: z,
      konce: [false, !maRameno && !spoj('rameno')],
    }),
    // block under the counter, full width, rounded top-right corner
    obdlznik({
      x: 0, y: P + r, w: B, h: bottom - P - r, zaoblenie: z,
      rohy: [false, true, !spoj('dole'), !spoj('dole')],
    }),
    // block beside the counter: from the ring centre down, inner circle notched in
    obdlznik({
      x: 0, y: P, w: Math.min(P, B), h: r + (bottom - P - r) / 2, rohy: [false, false, false, false], vyrez: { cx: P, r },
    }),
  ];
  const joints = [{ x: B / 2, y: bottom, dir: 'down', id: 'dole', t: B }];
  if (maRameno) {
    subpaths.push(obdlznik({
      x: P, y: 0, w: p.ramenoX, h, zaoblenie: z,
      rohy: [false, !spoj('rameno'), !spoj('rameno'), false],
    }));
    joints.push({ x: P + p.ramenoX, y: h / 2, dir: 'right', id: 'rameno', t: h });
  } else {
    joints.push({ x: P, y: h / 2, dir: 'up', id: 'rameno', t: h });
  }
  return { subpaths, joints };
}
