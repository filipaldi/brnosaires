// Primitive 1: rectangle with per-corner radii [tl, tr, br, bl], each 0–1 as
// a fraction of min(w, h) / 2 (0 sharp, 1 fully round).
//
// Optional `vyrez: { cx, r }` cuts a circular notch into the top edge: a
// circle centred on the top edge at x = cx. This is how a heavy block sits
// flush against a ring: the ring's inner circle is cut out of the block as
// part of the block's own outline, so no separate hole subpath is needed.

import { moveTo, lineTo, closePath, appendArc, roundedRect } from '../geometry.js';

export function obdlznik({ x, y, w, h, radii = [0, 0, 0, 0], vyrez = null, part = 'obdlznik' }) {
  const half = Math.min(w, h) / 2;
  const [tl, tr, br, bl] = radii.map((r) => Math.min(Math.max(r, 0), 1) * half);
  if (!vyrez || vyrez.r <= 0) {
    return { segs: roundedRect(x, y, w, h, [tl, tr, br, bl]), part };
  }
  const { cx, r } = vyrez;
  const a = Math.max(x, cx - r);
  const b = Math.min(x + w, cx + r);
  if (a >= b) return { segs: roundedRect(x, y, w, h, [tl, tr, br, bl]), part };

  const depth = (px) => Math.sqrt(Math.max(r * r - (px - cx) ** 2, 0));
  const ang = (px) => Math.atan2(depth(px), px - cx);
  const segs = [];
  if (a > x) {
    segs.push(moveTo(x, y + tl));
    if (tl > 0) appendArc(segs, x + tl, y + tl, tl, tl, Math.PI, Math.PI * 1.5);
    segs.push(lineTo(a, y));
  } else {
    segs.push(moveTo(x, y + depth(x)));
  }
  appendArc(segs, cx, y, r, r, ang(a), ang(b)); // along the circle below the top edge
  if (b < x + w) {
    segs.push(lineTo(x + w - tr, y));
    if (tr > 0) appendArc(segs, x + w - tr, y + tr, tr, tr, Math.PI * 1.5, Math.PI * 2);
  }
  segs.push(lineTo(x + w, y + h - br));
  if (br > 0) appendArc(segs, x + w - br, y + h - br, br, br, 0, Math.PI / 2);
  segs.push(lineTo(x + bl, y + h));
  if (bl > 0) appendArc(segs, x + bl, y + h - bl, bl, bl, Math.PI / 2, Math.PI);
  segs.push(closePath());
  return { segs, part };
}
