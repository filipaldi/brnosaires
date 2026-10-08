// hmotaSoStrbinou — a U: two heavy legs + heavy half ring at the bottom.
// The ring's inner radius is hair / 2, so the slot is exactly hair wide.

import { obdlznik, prstenec } from '../primitives/index.js';

export const id = 'hmotaSoStrbinou';
export const name = 'Hmota so štrbinou';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.2, max: 40 },
};

export function build(p, axes, prop) {
  const { hair: h, heavy: H } = axes;
  const W = 2 * H + h;
  const R = W / 2;
  const cy = Math.max(p.dlzka - R, 0);
  const z = prop.proporcie.hmotaSoStrbinou.hornyRoh;
  return {
    subpaths: [
      obdlznik({ x: 0, y: 0, w: H, h: cy, radii: [z, 0, 0, 0] }),
      obdlznik({ x: W - H, y: 0, w: H, h: cy, radii: [0, z, 0, 0] }),
      ...prstenec({ cx: R, cy, R, t: H, start: 0, sweep: 180 }),
    ],
    joints: [
      { x: H / 2, y: 0, dir: 'up' },
      { x: W - H / 2, y: 0, dir: 'up' },
    ],
  };
}
