// hmotaSoStrbinou — a U: two heavy legs + heavy half ring at the bottom.
// The ring's inner radius is hair / 2, so the slot is exactly hair wide.

import { obdlznik, prstenec } from '../primitives/index.js';

export const id = 'hmotaSoStrbinou';
export const name = 'Hmota so štrbinou';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.2, max: 40 },
};

export function build(p, axes) {
  const { hair: h, heavy: H } = axes;
  const W = 2 * H + h;
  const R = W / 2;
  const cy = Math.max(p.dlzka - R, 0);
  const z = axes.zaoblenie;
  const spoj = (id) => (p.spoje || []).includes(id);
  return {
    subpaths: [
      obdlznik({
        x: 0, y: 0, w: H, h: cy, zaoblenie: z,
        rohy: [!spoj('vlavo'), !spoj('vlavo'), false, false],
      }),
      obdlznik({
        x: W - H, y: 0, w: H, h: cy, zaoblenie: z,
        rohy: [!spoj('pravo'), !spoj('pravo'), false, false],
      }),
      ...prstenec({ cx: R, cy, R, t: H, start: 0, sweep: 180 }),
    ],
    joints: [
      { x: H / 2, y: 0, dir: 'up', id: 'vlavo', t: H },
      { x: W - H / 2, y: 0, dir: 'up', id: 'pravo', t: H },
    ],
  };
}
