// kvapka — the designer's teardrop curve alone (primitive krivka).

import { kvapka as krivka } from '../primitives/index.js';

export const id = 'kvapka';
export const name = 'Kvapka';

export const params = {
  vyska: { label: 'výška (× heavy)', type: 'number', min: 0.1, max: 40 },
};

export function build(p, axes) {
  const k = krivka({ x: 0, y: 0, hair: axes.hair, vyska: p.vyska * axes.heavy });
  return { subpaths: [k], joints: [{ x: 0, y: k.neck / 2, dir: 'left' }] };
}
