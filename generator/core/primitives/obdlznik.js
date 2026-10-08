// Primitive 1: rectangle. Every free corner is rounded with the global
// zaoblenie (0–1, a fraction of half the shorter side); `rohy` [tl, tr, br, bl]
// marks which corners are free (true) and which are joins hidden by another
// primitive (false, kept sharp so the join has no notch).
//
// Optional `vyrez: { cx, r }` cuts a circular notch into the top edge: a
// circle centred on the top edge at x = cx. This is how a heavy block sits
// flush against a ring: the ring's inner circle becomes part of the block's
// own outline. Where the circle leaves through a side of the block, that
// corner is rounded too.

import { moveTo, lineTo, closePath, appendArc, roundedRect } from '../geometry.js';
import { filletArc } from './fillet.js';

export function obdlznik({
  x, y, w, h, zaoblenie = 0, rohy = [true, true, true, true], vyrez = null, part = 'obdlznik',
}) {
  const f = Math.min(Math.max(zaoblenie, 0), 1) * (Math.min(w, h) / 2);
  const [tl, tr, br, bl] = rohy.map((free) => (free ? f : 0));
  const plain = () => ({ segs: roundedRect(x, y, w, h, [tl, tr, br, bl]), part });
  if (!vyrez || vyrez.r <= 0) return plain();
  const { cx, r } = vyrez;
  const a = Math.max(x, cx - r);
  const b = Math.min(x + w, cx + r);
  if (a >= b) return plain();

  const C = { x: cx, y };
  const depth = (px) => Math.sqrt(Math.max(r * r - (px - cx) ** 2, 0));
  const angOf = (p) => Math.atan2(p.y - C.y, p.x - C.x);
  // fillet between a vertical side at sx and the notch circle; centre inside the block
  const sideFillet = (sx, inward) => {
    const Fx = sx + inward * f;
    const Fy = y + Math.sqrt(Math.max((r + f) ** 2 - (Fx - cx) ** 2, 0));
    const F = { x: Fx, y: Fy };
    const k = r / (r + f);
    const onCircle = { x: cx + (Fx - cx) * k, y: y + (Fy - y) * k };
    return { F, onSide: { x: sx, y: Fy }, onCircle };
  };

  const segs = [];
  let arcFrom;
  if (a > x) {
    segs.push(moveTo(x, y + tl));
    if (tl > 0) appendArc(segs, x + tl, y + tl, tl, tl, Math.PI, Math.PI * 1.5);
    segs.push(lineTo(a, y));
    arcFrom = Math.PI;
  } else if (f > 0) {
    const s = sideFillet(x, 1);
    segs.push(moveTo(s.onSide.x, s.onSide.y));
    filletArc(segs, s.F, f, s.onSide, s.onCircle);
    arcFrom = angOf(s.onCircle);
  } else {
    segs.push(moveTo(x, y + depth(x)));
    arcFrom = angOf({ x, y: y + depth(x) });
  }
  if (b < x + w) {
    appendArc(segs, cx, y, r, r, arcFrom, 0);
    segs.push(lineTo(x + w - tr, y));
    if (tr > 0) appendArc(segs, x + w - tr, y + tr, tr, tr, Math.PI * 1.5, Math.PI * 2);
  } else if (f > 0) {
    const s = sideFillet(x + w, -1);
    appendArc(segs, cx, y, r, r, arcFrom, angOf(s.onCircle));
    filletArc(segs, s.F, f, s.onCircle, s.onSide);
  } else {
    const end = { x: x + w, y: y + depth(x + w) };
    appendArc(segs, cx, y, r, r, arcFrom, angOf(end));
  }
  segs.push(lineTo(x + w, y + h - br));
  if (br > 0) appendArc(segs, x + w - br, y + h - br, br, br, 0, Math.PI / 2);
  segs.push(lineTo(x + bl, y + h));
  if (bl > 0) appendArc(segs, x + bl, y + h - bl, bl, bl, Math.PI / 2, Math.PI);
  segs.push(closePath());
  return { segs, part };
}
