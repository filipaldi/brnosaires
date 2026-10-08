// hacikSKvapkou — a leg rising from the baseline, bending right at the top
// with a quarter circle and ending in a teardrop that hangs below the end of
// the bend. The tail's upper edge is tangent to the circle from the arm's top
// corner, the lower edge from the arm's bottom corner, so the merge with the
// circle is tangent-continuous. One closed outline.

import {
  appendArc, closePath, lineTo, moveTo,
} from '../geometry.js';
import { ValidationError } from '../errors.js';
import { appendArcAvoiding, armTeardropTangents } from './teardrop.js';

export const id = 'hacikSKvapkou';
export const name = 'Háčik s kvapkou';

export const params = {
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 20 },
  polomer: { label: 'polomer ohybu', type: 'number', min: 0.05, max: 10 },
  kvapka: { label: 'kvapka (násobok heavy)', type: 'number', min: 0.1, max: 5 },
  hrubka: { label: 'hrúbka', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes, prop) {
  const pr = prop.proporcie.hacikSKvapkou;
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;

  if (p.polomer <= t / 2 + 0.01) {
    throw new ValidationError(
      `Háčik s kvapkou: polomer ohybu musí byť väčší ako polovica hrúbky nohy (${(t / 2).toFixed(3)}). Zväčči polomer alebo zníž Weight.`);
  }

  const Ro = p.polomer + t / 2; // outer bend radius (centre at (Ro, Ro))
  const Ri = p.polomer - t / 2; // inner bend radius
  const H = p.vyska;
  if (H <= Ro + 0.02) {
    throw new ValidationError(
      `Háčik s kvapkou: výška musí byť väčšia ako polomer ohybu (${Ro.toFixed(3)}). Zväčči výšku.`);
  }

  const r = p.kvapka * axes.heavy;
  const A = { x: Ro + pr.armTop * r, y: 0 };      // arm top edge ends here
  const B = { x: Ro + pr.armBottom * r, y: t };   // arm bottom edge ends here
  const C = { x: A.x + pr.centerDX * r, y: t / 2 + pr.dropRatio * r };
  const { ta, tb, avoid } = armTeardropTangents({ cx: C.x, cy: C.y, r, a: A, b: B });

  const segs = [];
  segs.push(moveTo(0, H));
  segs.push(lineTo(0, Ro));
  appendArc(segs, Ro, Ro, Ro, Ro, Math.PI, Math.PI * 1.5); // outer bend
  segs.push(lineTo(A.x, A.y));
  segs.push(lineTo(ta.x, ta.y));
  appendArcAvoiding(segs, C.x, C.y, r, ta, tb, avoid);     // around the teardrop
  segs.push(lineTo(B.x, B.y));
  segs.push(lineTo(Ro, t));
  appendArc(segs, Ro, Ro, Ri, Ri, Math.PI * 1.5, Math.PI); // inner bend
  segs.push(lineTo(t, H));
  segs.push(closePath());

  return {
    subpaths: [{ segs }],
    joints: [{ x: t / 2, y: H, dir: 'down' }],
  };
}
