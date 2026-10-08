// stvrtoblouk — a hairline coming down into a heavy foot along a quarter
// circle: the same foot as obloukPata, without the ring above it. It joins
// from above (the hairline) and from below (the foot, thickness R).

import { pata } from './pata.js';

export const id = 'stvrtoblouk';
export const name = 'Štvrťoblúk s pätkou';

export const params = {
  polomer: { label: 'polomer (auto = heavy)', type: 'number', min: 0.02, max: 20, nullable: true },
};

export function build(p, axes) {
  const R = p.polomer ?? axes.heavy;
  const r = Math.max(R - axes.hair, R * 0.05);
  const t = R - r;
  const spoj = (id) => (p.spoje || []).includes(id);
  return {
    subpaths: [pata({ R, r, y0: 0, zaoblenie: axes.zaoblenie, hore: !spoj('vlas'), dole: !spoj('pata') })],
    joints: [
      { x: t / 2, y: 0, dir: 'up', id: 'vlas', t },
      { x: R / 2, y: r, dir: 'down', id: 'pata', t: R },
    ],
  };
}
