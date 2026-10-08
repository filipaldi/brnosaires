// vrchol — an apex like the letter A. A hair leg rises from the baseline to
// the apex; a heavy wedge descends from the apex to the baseline on the other
// side. The wedge's outer edge passes through the apex, its inner edge starts
// on the hair leg just below the apex (so the top is a solid wedge) and meets
// the baseline at horizontal width heavy · wedgeRatio. Both legs are cut flat
// on the baseline; the apex is rounded.

import { roundedPolygon } from '../geometry.js';
import { ValidationError } from '../errors.js';

export const id = 'vrchol';
export const name = 'Vrchol';

export const params = {
  uholVlavo: { label: 'uhol vľavo', type: 'number', min: 0, max: 60 },
  uholVpravo: { label: 'uhol vpravo', type: 'number', min: 0, max: 60 },
  vyska: { label: 'výška', type: 'number', min: 0.2, max: 20 },
};

const DEG = Math.PI / 180;

export function build(p, axes, prop) {
  const pr = prop.proporcie.vrchol;
  const H = p.vyska;
  const aL = p.uholVlavo * DEG;
  const aR = p.uholVpravo * DEG;

  const hh = axes.hair / Math.max(Math.cos(aL), 0.1); // hair leg horizontal width
  const xA = Math.tan(aL) * H;                        // apex x (left extent lands at 0)
  const Wb = xA + Math.tan(aR) * H;                   // wedge outer edge at the baseline

  const yQ = pr.wedgeStartDrop * axes.heavy;
  const Q = { x: xA + hh - Math.tan(aL) * yQ, y: yQ }; // wedge inner edge starts here
  let hw = axes.heavy * pr.wedgeRatio;                  // wedge horizontal width at the baseline
  hw = Math.min(hw, Math.max((Wb - Q.x) * 0.9, 0.01));

  const pts = [
    { x: xA, y: 0 },      // apex
    { x: 0, y: H },       // hair leg bottom-left
    { x: hh, y: H },      // hair leg bottom-right
    Q,                    // counter opening on the hair leg
    { x: Wb - hw, y: H }, // wedge inner bottom
    { x: Wb, y: H },      // wedge outer bottom
  ];
  const radii = [
    pr.apexRadius * axes.hair,
    0,
    0,
    pr.counterRadius * axes.hair,
    0,
    0,
  ];

  if (Wb - hw <= Q.x + 1e-6) {
    throw new ValidationError(
      'Vrchol: klin pravej nohy je pre tieto uhly a Weight príliš široký. Zmenši Weight alebo zväčči uhly.');
  }

  return {
    subpaths: [{ segs: roundedPolygon(pts, radii) }],
    joints: [
      { x: hh / 2, y: H, dir: 'down' },
      { x: Wb - hw / 2, y: H, dir: 'down' },
    ],
  };
}
