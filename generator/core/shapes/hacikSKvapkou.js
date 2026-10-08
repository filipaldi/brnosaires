// hacikSKvapkou — a leg rising from the baseline, a hairline quarter ring
// turning right at the top, ending in the designer's teardrop. A heavy leg
// sits flush with the ring's outer edge; the ring's inner circle is notched
// into its top so the bend stays round.

import { obdlznik, prstenec, kvapka } from '../primitives/index.js';

export const id = 'hacikSKvapkou';
export const name = 'Háčik s kvapkou';

export const params = {
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 40 },
  polomer: { label: 'polomer ohybu', type: 'number', min: 0.02, max: 20 },
  kvapka: { label: 'kvapka (× heavy)', type: 'number', min: 0.1, max: 40 },
  hrubka: { label: 'hrúbka nohy', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const { hair: h, heavy: H } = axes;
  const P = p.polomer;
  const t = p.hrubka === 'vlas' ? h : H;
  const legH = Math.max(p.vyska - P, 0.001);
  const subpaths = [
    obdlznik({ x: 0, y: P, w: t, h: legH, vyrez: t > h ? { cx: P, r: Math.max(P - h, 0) } : null }),
    ...prstenec({ cx: P, cy: P, R: P, t: h, start: 180, sweep: 90 }),
    kvapka({ x: P, y: 0, hair: h, vyska: p.kvapka * H }),
  ];
  return { subpaths, joints: [{ x: t / 2, y: p.vyska, dir: 'down' }] };
}
