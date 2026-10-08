// noha — a straight leg: one obdlznik.

import { obdlznik } from '../primitives/index.js';

export const id = 'noha';
export const name = 'Noha';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.1, max: 40 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;
  return {
    subpaths: [obdlznik({ x: 0, y: 0, w: t, h: p.dlzka, zaoblenie: axes.zaoblenie })],
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down' },
      { x: t / 2, y: 0, dir: 'up' },
    ],
  };
}
