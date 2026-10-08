// A rounding arc of radius f around centre F from point p to point q, the
// short way round (fillets are always under 180°).

import { appendArc } from '../geometry.js';

export function filletArc(segs, F, f, p, q) {
  const a0 = Math.atan2(p.y - F.y, p.x - F.x);
  let a1 = Math.atan2(q.y - F.y, q.x - F.x);
  while (a1 - a0 > Math.PI) a1 -= 2 * Math.PI;
  while (a1 - a0 < -Math.PI) a1 += 2 * Math.PI;
  appendArc(segs, F.x, F.y, f, f, a0, a1);
}

// A concave (inner) corner at P where two edges leave along unit vectors u
// and v: returns a small solid patch that fills the corner with a rounding
// of radius f, so the white counter meets the corner along an arc.
export function vnutornyRoh(P, u, v, f) {
  const cos = u.x * v.x + u.y * v.y;
  const theta = Math.acos(Math.min(Math.max(cos, -1), 1));
  if (!(f > 0) || theta < 1e-4 || theta > Math.PI - 1e-4) return null;
  const t = f / Math.tan(theta / 2);
  const bx = u.x + v.x, by = u.y + v.y;
  const bl = Math.hypot(bx, by);
  const d = f / Math.sin(theta / 2);
  const F = { x: P.x + (bx / bl) * d, y: P.y + (by / bl) * d };
  const p = { x: P.x + u.x * t, y: P.y + u.y * t };
  const q = { x: P.x + v.x * t, y: P.y + v.y * t };
  const segs = [{ c: 'M', x: P.x, y: P.y }, { c: 'L', x: p.x, y: p.y }];
  filletArc(segs, F, f, p, q);
  segs.push({ c: 'Z' });
  return { segs, part: 'roh' };
}
