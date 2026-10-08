// vrchol — experiment: two straight legs meeting at the apex, built as
// polygons (rotated rectangles clipped flat at the baseline). The left leg is
// hairline; the heavy right leg's outer edge runs through the apex and its
// inner edge meets the hairline below the apex, so the top is a solid wedge.

import { roundedPolygon } from '../geometry.js';

export const id = 'vrchol';
export const name = 'Vrchol';

export const params = {
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 40 },
  uholVlavo: { label: 'uhol vľavo', type: 'number', min: 0, max: 60 },
  uholVpravo: { label: 'uhol vpravo', type: 'number', min: 0, max: 60 },
};

const RAD = Math.PI / 180;

function intersect(p1, p2, p3, p4) {
  const d = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x);
  const a = p1.x * p2.y - p1.y * p2.x;
  const b = p3.x * p4.y - p3.y * p4.x;
  return {
    x: (a * (p3.x - p4.x) - (p1.x - p2.x) * b) / d,
    y: (a * (p3.y - p4.y) - (p1.y - p2.y) * b) / d,
  };
}

export function build(p, axes, prop) {
  const { hair: h, heavy: H } = axes;
  const V = p.vyska;
  const hw = h / Math.cos(p.uholVlavo * RAD); // horizontal widths of the legs
  const Hw = H / Math.cos(p.uholVpravo * RAD);
  const apex = { x: V * Math.tan(p.uholVlavo * RAD), y: 0 };
  const bl = { x: 0, y: V };
  const br = { x: apex.x + V * Math.tan(p.uholVpravo * RAD), y: V };
  // heavy leg: outer edge apex→br, inner edge parallel, Hw to the left
  const innerTop = { x: apex.x - Hw, y: 0 };
  const innerBot = { x: br.x - Hw, y: V };
  const q = intersect(innerTop, innerBot, bl, apex); // inner edge meets the hairline
  // hairline leg: its right edge ends on the heavy leg's outer edge
  const c = intersect({ x: hw, y: V }, { x: apex.x + hw, y: 0 }, apex, br);
  const rA = h * prop.proporcie.vrchol.apexRadius;
  const tazka = roundedPolygon([apex, br, innerBot, q], [rA, 0, 0, 0]);
  const vlas = roundedPolygon([bl, { x: hw, y: V }, c, apex], [0, 0, 0, rA]);
  return {
    subpaths: [{ segs: vlas, part: 'obdlznik' }, { segs: tazka, part: 'obdlznik' }],
    joints: [
      { x: hw / 2, y: V, dir: 'down' },
      { x: br.x - Hw / 2, y: V, dir: 'down' },
    ],
  };
}
