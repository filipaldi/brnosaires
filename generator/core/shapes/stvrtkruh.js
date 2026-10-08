// stvrtkruh — a plain quarter ring of constant thickness (hair or heavy),
// from its left end pointing down to its top end pointing right. It joins at
// both ends.

import { prstenec } from '../primitives/index.js';

export const id = 'stvrtkruh';
export const name = 'Štvrťoblúk';

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
      cx: R, cy: R, R, t, start: 180, sweep: 90, zaoblenie: 0,
      konce: [!spoj('dole'), !spoj('vpravo')],
    }),
    joints: [
      { x: t / 2, y: R, dir: 'down', id: 'dole', t },
      { x: R, y: t / 2, dir: 'right', id: 'vpravo', t },
    ],
  };
}
