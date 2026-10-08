// noha — a straight leg: one obdlznik.

import { obdlznik } from '../primitives/index.js';

export const id = 'noha';
export const name = 'Noha';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.1, max: 40 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
  zaoblenie: { label: 'zaoblenie', type: 'number', min: 0, max: 1 },
};

export function build(p, axes) {
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;
  const z = p.zaoblenie;
  return {
    subpaths: [obdlznik({ x: 0, y: 0, w: t, h: p.dlzka, radii: [z, z, z, z] })],
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down' },
      { x: t / 2, y: 0, dir: 'up' },
    ],
  };
}
