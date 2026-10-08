// stvrtoblouk — a hairline coming down into a heavy foot along a quarter
// circle: the transition from a thin stroke to a heavy one. It joins from
// above (the hairline) and from below (the heavy foot).

import { pata } from './pata.js';

export const id = 'stvrtoblouk';
export const name = 'Štvrťoblúk s pätkou';

export const params = {
  polomer: { label: 'polomer (auto = heavy, min heavy)', type: 'number', min: 0.02, max: 20, nullable: true },
};

export function build(p, axes) {
  const H = axes.heavy;
  const R = Math.max(p.polomer ?? H, H);
  const r = Math.max(R - axes.hair, R * 0.05);
  const t = R - r;
  const spoj = (id) => (p.spoje || []).includes(id);
  const noha = pata({ R, H, r, y0: 0, zaoblenie: axes.zaoblenie, hore: false, dole: !spoj('pata') });
  return {
    subpaths: [noha],
    joints: [
      { x: t / 2, y: 0, dir: 'up', id: 'vlas', t },
      { x: H / 2, y: noha.yb, dir: 'down', id: 'pata', t: H },
    ],
  };
}
