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
  // a joined end is not a visible corner — its two corners stay sharp
  const spoj = (id) => (p.spoje || []).includes(id);
  return {
    subpaths: [obdlznik({
      x: 0, y: 0, w: t, h: p.dlzka, zaoblenie: axes.zaoblenie,
      rohy: [!spoj('hore'), !spoj('hore'), !spoj('dole'), !spoj('dole')],
    })],
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down', id: 'dole', t },
      { x: t / 2, y: 0, dir: 'up', id: 'hore', t },
    ],
  };
}
