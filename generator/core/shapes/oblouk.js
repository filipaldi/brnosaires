// oblouk — an arch like n: hairline leg + hairline half ring on top + heavy
// leg flush with the ring's outer edge. The ring's inner circle is notched into
// the heavy leg's top so the counter stays round.

import { obdlznik, prstenec, zrkadliX } from '../primitives/index.js';

export const id = 'oblouk';
export const name = 'Oblúk';

export const params = {
  sirka: { label: 'šírka', type: 'number', min: 0.2, max: 20 },
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 40 },
  plnaStrana: { label: 'plná strana', type: 'enum', values: ['vpravo', 'vlavo'] },
};

export function build(p, axes, prop) {
  const { hair: h, heavy: H } = axes;
  const R = p.sirka / 2;
  const cy = R;
  const legH = Math.max(p.vyska - cy, 0.001);
  const pp = prop.proporcie.oblouk;
  let subpaths = [
    obdlznik({ x: 0, y: cy, w: h, h: legH, radii: [0, 0, pp.patkaVlas, pp.patkaVlas] }),
    ...prstenec({ cx: R, cy, R, t: h, start: 180, sweep: 180 }),
    obdlznik({
      x: p.sirka - H, y: cy, w: H, h: legH, radii: [0, 0, pp.patkaPlna, 0], vyrez: { cx: R, r: R - h },
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
