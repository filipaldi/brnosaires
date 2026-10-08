// Shared teardrop geometry: a circle plus a tail formed by tangent lines.
// Used standalone (kvapka), attached to a leg (nota) and as the terminal of a
// bent leg (háčik s kvapkou). Everything is a filled outline of one closed
// subpath, tangent-continuous where the tail meets the circle.

import {
  appendArc, closePath, curveTo, ensureExternal, fillet, lineTo, moveTo,
  tangentPoints,
} from '../geometry.js';

// Append the arc of circle (c, r) from point `from` to point `to` (both with
// an `.a` angle property) choosing the sweep that avoids the given directions.
// This keeps the tail side of the circle open for the tangent lines.
function appendArcAvoiding(segs, cx, cy, r, from, to, avoidAngles) {
  const TAU = Math.PI * 2;
  let d = ((to.a - from.a) % TAU + TAU) % TAU; // positive sweep, [0, 2π)
  const hitsPositive = avoidAngles.some((av) => {
    const rel = ((av - from.a) % TAU + TAU) % TAU;
    return rel > 1e-6 && rel < d - 1e-6;
  });
  const sweep = hitsPositive ? d - TAU : d;
  appendArc(segs, cx, cy, r, r, from.a, from.a + sweep);
}

// Teardrop with one tip point: tail edges are the two tangent lines from the
// tip to the circle, the tip itself is rounded with `tipRadius`.
export function teardropSubpath({ cx, cy, r, tip, tipRadius }) {
  const c = { x: cx, y: cy };
  const t = ensureExternal({ x: tip.x, y: tip.y }, c, r);
  const [t1, t2] = tangentPoints(t, c, r);
  const back = Math.atan2(t.y - cy, t.x - cx);
  const f = fillet(t1, t, t2, tipRadius);
  const segs = [];
  if (f) {
    segs.push(moveTo(f.p1.x, f.p1.y));
    segs.push(curveTo(f.c1.x, f.c1.y, f.c2.x, f.c2.y, f.p2.x, f.p2.y));
    segs.push(lineTo(t2.x, t2.y));
  } else {
    segs.push(moveTo(t.x, t.y));
    segs.push(lineTo(t2.x, t2.y));
  }
  appendArcAvoiding(segs, cx, cy, r, t2, t1, [back]);
  segs.push(closePath());
  return segs;
}

// Teardrop merging into the end of an arm: the tail's upper edge is the
// tangent from corner `a` (on the arm's top edge), the lower edge the tangent
// from corner `b` (on the arm's bottom edge). Returns the two tangent points;
// the caller draws a → ta, the arc, tb → b.
export function armTeardropTangents({ cx, cy, r, a, b }) {
  const c = { x: cx, y: cy };
  const pa = ensureExternal(a, c, r);
  const pb = ensureExternal(b, c, r);
  const [a1, a2] = tangentPoints(pa, c, r);
  const [b1, b2] = tangentPoints(pb, c, r);
  const ta = a1.y <= a2.y ? a1 : a2; // upper tangent point
  const tb = b1.y >= b2.y ? b1 : b2; // lower tangent point
  return { ta, tb, avoid: [Math.atan2(pa.y - cy, pa.x - cx), Math.atan2(pb.y - cy, pb.x - cx)] };
}

export { appendArcAvoiding };
