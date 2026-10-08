// Primitive 2: ring segment of constant thickness.
//
// Angles in degrees on screen: 0 = +x (right), 90 = +y (down); a positive
// sweep runs clockwise on screen. Ends are cut radially. sweep = 360 gives a
// full ring as two subpaths (outer solid, inner hole). t >= R gives a disc
// or a pie slice.

import { moveTo, lineTo, closePath, appendArc, circleSegments } from '../geometry.js';

const RAD = Math.PI / 180;

export function prstenec({ cx, cy, R, t, start = 0, sweep = 360, part = 'prstenec' }) {
  const r = Math.max(0, R - t);
  if (sweep >= 360) {
    const out = [{ segs: circleSegments(cx, cy, R), part }];
    if (r > 0) out.push({ segs: circleSegments(cx, cy, r), hole: true, part });
    return out;
  }
  const a0 = start * RAD;
  const a1 = (start + sweep) * RAD;
  const segs = [moveTo(cx + R * Math.cos(a0), cy + R * Math.sin(a0))];
  appendArc(segs, cx, cy, R, R, a0, a1);
  if (r > 0) {
    segs.push(lineTo(cx + r * Math.cos(a1), cy + r * Math.sin(a1)));
    appendArc(segs, cx, cy, r, r, a1, a0);
  } else {
    segs.push(lineTo(cx, cy));
  }
  segs.push(closePath());
  return [{ segs, part }];
}
