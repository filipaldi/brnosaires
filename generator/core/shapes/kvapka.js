// kvapka — the designer's teardrop curve alone (primitive krivka).

import { kvapka as krivka } from '../primitives/index.js';

export const id = 'kvapka';
export const name = 'Kvapka';

export const params = {
  chvost: { label: 'chvost (%)', type: 'number', min: 0, max: 100 },
  vyska: { label: 'výška (%)', type: 'number', min: 0, max: 100 },
  krk: { label: 'hrúbka krku (%)', type: 'number', min: 0, max: 100 },
  hrubka: { label: 'napojenie', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  // the neck is as thick as the stroke it hangs from: hairline or heavy
  const t = p.hrubka === 'plna' ? axes.heavy : axes.hair;
  const k = krivka({ x: 0, y: 0, t, chvost: p.chvost / 100, vyska: p.vyska / 100, krk: p.krk / 100 });
  // the neck end of the designer's outline is already cut square, so `spoje`
  // changes nothing here — the joint exists so a chain can hang the drop
  // off another shape's end of the same thickness
  return { subpaths: [k], joints: [{ x: 0, y: t / 2, dir: 'left', id: 'krk', t }] };
}
