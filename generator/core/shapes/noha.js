// noha — a straight vertical leg. Rounded ends via `zaoblenie` (0 = square,
// 1 = fully round stadium ends, corner radius = zaoblenie · width / 2).

import { roundedRect } from '../geometry.js';

export const id = 'noha';
export const name = 'Noha';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.2, max: 20 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
  zaoblenie: { label: 'zaoblenie', type: 'number', min: 0, max: 1 },
};

export function build(p, axes) {
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;
  const r = (p.zaoblenie * t) / 2;
  const segs = roundedRect(0, 0, t, p.dlzka, [r, r, r, r]);
  return {
    subpaths: [{ segs }],
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down' },
      { x: t / 2, y: 0, dir: 'up' },
    ],
  };
}
