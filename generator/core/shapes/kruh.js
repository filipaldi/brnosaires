// kruh — a full ring.

import { prstenec } from '../primitives/index.js';

export const id = 'kruh';
export const name = 'Kruh';

export const params = {
  priemer: { label: 'priemer', type: 'number', min: 0.05, max: 20 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const R = p.priemer / 2;
  const t = Math.min(p.hrubka === 'vlas' ? axes.hair : axes.heavy, R);
  return { subpaths: prstenec({ cx: R, cy: R, R, t }), joints: [] };
}
