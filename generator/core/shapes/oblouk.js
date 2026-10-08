// oblouk — an arch like n: hairline leg + half ring on top + heavy leg.
//
// Design choice `hrubnutie`:
//   stala    the ring keeps hairline thickness; the heavy leg sits flush with
//            its outer edge, the ring's inner circle notched into the leg's top
//   plynula  the ring thickens smoothly from hair to heavy: its inner circle is
//            smaller and shifted towards the hairline, so the heavy leg's
//            inner edge continues straight into the arc

import { obdlznik, prstenec, zrkadliX } from '../primitives/index.js';
import { moveTo, lineTo, closePath, appendArc } from '../geometry.js';

export const id = 'oblouk';
export const name = 'Oblúk';

export const params = {
  sirka: { label: 'šírka', type: 'number', min: 0.2, max: 20 },
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 40 },
  plnaStrana: { label: 'plná strana', type: 'enum', values: ['vpravo', 'vlavo'] },
  hrubnutie: { label: 'hrubnutie oblúka', type: 'enum', values: ['stala', 'plynula'] },
};

// Upper half ring between an outer circle (centre cx, radius R) and an inner
// circle with its own centre and radius, both centred on the line y = cy.
function polkruhPlynuly(cx, cy, R, icx, ir) {
  const segs = [moveTo(cx - R, cy)];
  appendArc(segs, cx, cy, R, R, Math.PI, Math.PI * 2);
  segs.push(lineTo(icx + ir, cy));
  appendArc(segs, icx, cy, ir, ir, Math.PI * 2, Math.PI);
  segs.push(closePath());
  return { segs, part: 'prstenec' };
}

export function build(p, axes, prop) {
  const { hair: h, heavy: H } = axes;
  const R = p.sirka / 2;
  const cy = R;
  const legH = Math.max(p.vyska - cy, 0.001);
  const pp = prop.proporcie.oblouk;
  const plynula = p.hrubnutie === 'plynula';
  const ir = Math.max((p.sirka - h - H) / 2, 0); // inner radius when it thickens
  let subpaths = [
    obdlznik({ x: 0, y: cy, w: h, h: legH, radii: [0, 0, pp.patkaVlas, pp.patkaVlas] }),
    ...(plynula
      ? [polkruhPlynuly(R, cy, R, h + ir, ir)]
      : prstenec({ cx: R, cy, R, t: h, start: 180, sweep: 180 })),
    obdlznik({
      x: p.sirka - H, y: cy, w: H, h: legH, radii: [0, 0, pp.patkaPlna, 0],
      vyrez: plynula ? null : { cx: R, r: R - h },
    }),
  ];
  let joints = [
    { x: h / 2, y: p.vyska, dir: 'down' },
    { x: p.sirka - H / 2, y: p.vyska, dir: 'down' },
  ];
  if (p.plnaStrana === 'vlavo') {
    subpaths = zrkadliX(subpaths, R);
    joints = joints.map((j) => ({ ...j, x: 2 * R - j.x }));
  }
  return { subpaths, joints };
}
