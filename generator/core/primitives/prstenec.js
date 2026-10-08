// Primitive 2: ring segment of constant thickness.
//
// Angles in degrees on screen: 0 = +x (right), 90 = +y (down); a positive
// sweep runs clockwise on screen. Ends are cut radially. sweep = 360 gives a
// full ring as two subpaths (outer solid, inner hole). t >= R gives a disc
// or a pie slice.
//
// `konce: [startFree, endFree]` marks free ends; their two corners are
// rounded with the global zaoblenie (a fraction of half the thickness).
// Ends joined to another primitive stay sharp.

import { moveTo, lineTo, closePath, appendArc, circleSegments } from '../geometry.js';
import { filletArc } from './fillet.js';

const RAD = Math.PI / 180;

const polar = (cx, cy, rho, a) => ({ x: cx + rho * Math.cos(a), y: cy + rho * Math.sin(a) });

export function prstenec({
  cx, cy, R, t, start = 0, sweep = 360, zaoblenie = 0, konce = [false, false], part = 'prstenec',
}) {
  const r = Math.max(0, R - t);
  if (sweep >= 360) {
    const out = [{ segs: circleSegments(cx, cy, R), part }];
    if (r > 0) out.push({ segs: circleSegments(cx, cy, r), hole: true, part });
    return out;
  }
  const a0 = start * RAD;
  const a1 = (start + sweep) * RAD;
  if (r <= 0) {
    const segs = [moveTo(...Object.values(polar(cx, cy, R, a0)))];
    appendArc(segs, cx, cy, R, R, a0, a1);
    segs.push(lineTo(cx, cy), closePath());
    return [{ segs, part }];
  }
  const f = Math.min(Math.max(zaoblenie, 0), 1) * (t / 2);
  // corner geometry at a radial end: fillet centre offset by angle d from the
  // end, tangent points on the arc and on the radial cut
  const corner = (rho, a, sign) => {
    const d = Math.asin(Math.min(f / rho, 1));
    const F = polar(cx, cy, rho, a + sign * d);
    return { F, d, onCut: polar(cx, cy, rho * Math.cos(d), a) };
  };
  const [s0, s1] = konce.map((free) => free && f > 0);
  const oS = s0 && corner(R - f, a0, 1), iS = s0 && corner(r + f, a0, 1);
  const oE = s1 && corner(R - f, a1, -1), iE = s1 && corner(r + f, a1, -1);

  const segs = [];
  const outStart = a0 + (oS ? oS.d : 0);
  segs.push(moveTo(...Object.values(polar(cx, cy, R, outStart))));
  appendArc(segs, cx, cy, R, R, outStart, a1 - (oE ? oE.d : 0));
  if (oE) {
    filletArc(segs, oE.F, f, polar(cx, cy, R, a1 - oE.d), oE.onCut);
    segs.push(lineTo(iE.onCut.x, iE.onCut.y));
    filletArc(segs, iE.F, f, iE.onCut, polar(cx, cy, r, a1 - iE.d));
  } else {
    segs.push(lineTo(...Object.values(polar(cx, cy, r, a1))));
  }
  const inStart = a0 + (iS ? iS.d : 0);
  appendArc(segs, cx, cy, r, r, a1 - (iE ? iE.d : 0), inStart);
  if (iS) {
    filletArc(segs, iS.F, f, polar(cx, cy, r, inStart), iS.onCut);
    segs.push(lineTo(oS.onCut.x, oS.onCut.y));
    filletArc(segs, oS.F, f, oS.onCut, polar(cx, cy, R, outStart));
  }
  segs.push(closePath());
  return [{ segs, part }];
}
