// Shared outline of a heavy foot (pätka) whose right side is cut by a
// quarter circle: top edge from x = 0 to R − r, the cut centred at (R, y0)
// with radius r running down into the foot's right end at (R, y0 + r), where
// it meets the bottom edge tangentially (no visible corner there). Used by
// obloukPata (under a quarter ring) and stvrtoblouk (on its own).

import { moveTo, lineTo, closePath, appendArc } from '../geometry.js';
import { filletArc } from '../primitives/fillet.js';

export function pata({ R, r, y0, zaoblenie, hore, dole }) {
  const z = Math.min(Math.max(zaoblenie, 0), 1);
  const t = R - r;
  const yb = y0 + r;
  const C = { x: R, y: y0 };
  const ft = hore ? z * t / 2 : 0;
  const fb = dole ? z * Math.min(R, r) / 2 : 0;
  const segs = [];

  // top-left corner
  if (ft > 0) {
    segs.push(moveTo(0, y0 + ft));
    filletArc(segs, { x: ft, y: y0 + ft }, ft, { x: 0, y: y0 + ft }, { x: ft, y: y0 });
  } else {
    segs.push(moveTo(0, y0));
  }
  // top edge into the cut, rounded where it meets the circle
  let a0 = Math.PI;
  if (ft > 0) {
    const F = { x: C.x - Math.sqrt((r + ft) ** 2 - ft ** 2), y: y0 + ft };
    const q = { x: C.x + (F.x - C.x) * r / (r + ft), y: C.y + (F.y - C.y) * r / (r + ft) };
    segs.push(lineTo(F.x, y0));
    filletArc(segs, F, ft, { x: F.x, y: y0 }, q);
    a0 = Math.atan2(q.y - C.y, q.x - C.x);
  } else {
    segs.push(lineTo(t, y0));
  }
  appendArc(segs, C.x, C.y, r, r, a0, Math.PI / 2);
  // bottom edge and its outer corner
  if (fb > 0) {
    segs.push(lineTo(fb, yb));
    filletArc(segs, { x: fb, y: yb - fb }, fb, { x: fb, y: yb }, { x: 0, y: yb - fb });
  } else {
    segs.push(lineTo(0, yb));
  }
  segs.push(closePath());
  return { segs, part: 'obdlznik' };
}
