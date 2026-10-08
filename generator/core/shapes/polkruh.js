// polkruh — a plain half ring of constant thickness (hair or heavy), open
// downwards. It joins at both ends.

import { prstenec } from '../primitives/index.js';

export const id = 'polkruh';
export const name = 'Polooblúk';

export const params = {
  polomer: { label: 'polomer', type: 'number', min: 0.1, max: 20 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const t = Math.min(p.hrubka === 'vlas' ? axes.hair : axes.heavy, p.polomer);
  const R = p.polomer;
  const spoj = (id) => (p.spoje || []).includes(id);
  return {
    subpaths: prstenec({
      cx: R, cy: R, R, t, start: 180, sweep: 180, zaoblenie: axes.zaoblenie,
      konce: [!spoj('vlavo'), !spoj('vpravo')],
    }),
    joints: [
      { x: t / 2, y: R, dir: 'down', id: 'vlavo', t },
      { x: 2 * R - t / 2, y: R, dir: 'down', id: 'vpravo', t },
    ],
  };
}
