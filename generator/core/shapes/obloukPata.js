// obloukPata — a heavy foot whose top bends into a hairline quarter ring.
//
// The designer's drawing: outer quarter circle (radius R = foot width) from
// the foot's left edge up to the hairline end; below the ring's centre the
// foot is solid, its right side cut by the inner circle (radius R − hair), so
// the inner edge runs as one half circle from the hairline end down to the
// foot. It joins from below (the foot, thickness R) and to the right (hair).

import { prstenec } from '../primitives/index.js';
import { pata } from './pata.js';

export const id = 'obloukPata';
export const name = 'Oblúk s pätkou';

export const params = {
  polomer: { label: 'polomer (auto = heavy)', type: 'number', min: 0.02, max: 20, nullable: true },
};

export function build(p, axes) {
  const R = p.polomer ?? axes.heavy;
  const r = Math.max(R - axes.hair, R * 0.05);
  const t = R - r;
  const z = axes.zaoblenie;
  const spoj = (id) => (p.spoje || []).includes(id);
  return {
    subpaths: [
      ...prstenec({
        cx: R, cy: R, R, t, start: 180, sweep: 90, zaoblenie: z, konce: [false, !spoj('koniec')],
      }),
      pata({ R, r, y0: R, zaoblenie: z, hore: false, dole: !spoj('pata') }),
    ],
    joints: [
      { x: R / 2, y: R + r, dir: 'down', id: 'pata', t: R },
      { x: R, y: t / 2, dir: 'right', id: 'koniec', t },
    ],
  };
}
