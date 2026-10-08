// oblouk — an arch like the letter n: a hair leg and a heavy leg joined by a
// round top. The outer contour is straight sides + a half-ellipse over the
// full width; the inner (counter) half-ellipse runs between the inner edges
// of the legs with its top lowered by ~the average of hair and heavy, so the
// arch thickness grows smoothly from hair to heavy.

import {
  appendArc, closePath, curveTo, fillet, lineTo, moveTo,
} from '../geometry.js';
import { ValidationError } from '../errors.js';

export const id = 'oblouk';
export const name = 'Oblúk';

export const params = {
  sirka: { label: 'šírka', type: 'number', min: 0.1, max: 20 },
  vyska: { label: 'výška', type: 'number', min: 0.1, max: 20 },
  plnaStrana: { label: 'plná strana', type: 'enum', values: ['vpravo', 'vlavo'] },
};

function pushFillet(segs, f, vertex) {
  if (f) {
    segs.push(lineTo(f.p1.x, f.p1.y));
    segs.push(curveTo(f.c1.x, f.c1.y, f.c2.x, f.c2.y, f.p2.x, f.p2.y));
  } else {
    segs.push(lineTo(vertex.x, vertex.y));
  }
}

export function build(p, axes, prop) {
  const pr = prop.proporcie.oblouk;
  const tHair = axes.hair;
  const tHeavy = axes.heavy;
  const W = p.sirka;
  const H = p.vyska;

  if (W < tHair + tHeavy + 0.04) {
    throw new ValidationError(
      `Oblúk: šírka ${W} je príliš malá pre tieto hrúbky nôh (hair ${tHair.toFixed(3)} + heavy ${tHeavy.toFixed(3)}). Zväčši šírku alebo zníž Weight.`);
  }

  // outer half-ellipse: centre (W/2, y0), spans the full width
  const y0 = pr.archRatio * H;
  if (y0 > H - 0.02) {
    throw new ValidationError('Oblúk: výška je príliš malá na oblúk, zväčči ju.');
  }

  // inner half-ellipse between the leg inner edges
  const xIL = tHair;
  const xIR = W - tHeavy;
  const innerTop = ((tHair + tHeavy) / 2) * pr.innerTopBias;
  const rx2 = (xIR - xIL) / 2;
  const rxOuter = W / 2;
  let ry2 = y0 * (rx2 / rxOuter);
  const yc2 = Math.min(innerTop + ry2, H - 0.02);
  ry2 = yc2 - innerTop;
  const cx2 = (xIL + xIR) / 2;

  const V1 = { x: 0, y: H };            // bottom-left outer corner
  const V2 = { x: 0, y: y0 };           // outer arc start (tangent)
  const V4 = { x: W, y: H };            // bottom-right outer corner
  const V5 = { x: xIR, y: H };          // bottom-right inner corner
  const V6 = { x: xIR, y: yc2 };        // inner arc start (tangent)
  const V8 = { x: xIL, y: H };          // bottom-left inner corner

  const f1 = fillet(V8, V1, V2, pr.endOuter * tHair);
  // the outer arc arrives at V4 vertically, so the fillet's incoming
  // direction is taken from a point straight above V4
  const f4 = fillet({ x: W, y: y0 }, V4, V5, pr.endOuter * tHeavy);
  const f5 = fillet(V4, V5, V6, pr.endInner * tHeavy);
  const f8 = fillet(V6, V8, V1, pr.endInner * tHair);

  const segs = [];
  const start = f1 ? f1.p2 : V1;
  segs.push(moveTo(start.x, start.y));
  segs.push(lineTo(V2.x, V2.y));
  appendArc(segs, W / 2, y0, rxOuter, y0, Math.PI, Math.PI * 2); // over the top
  pushFillet(segs, f4, V4);
  pushFillet(segs, f5, V5);
  segs.push(lineTo(V6.x, V6.y));
  appendArc(segs, cx2, yc2, rx2, ry2, 0, -Math.PI); // over the counter top
  pushFillet(segs, f8, V8);
  pushFillet(segs, f1, V1);
  segs.push(closePath());

  let subpaths = [{ segs }];
  let joints = [
    { x: tHair / 2, y: H, dir: 'down' },
    { x: W - tHeavy / 2, y: H, dir: 'down' },
  ];

  if (p.plnaStrana === 'vlavo') {
    subpaths = subpaths.map((s) => flipSubpath(s, W));
    joints = joints.map((j) => ({ ...j, x: W - j.x }));
  }

  return { subpaths, joints };
}

function flipSubpath(sub, W) {
  const map = (p) => ({ x: W - p.x, y: p.y });
  return {
    ...sub,
    segs: sub.segs.map((s) => {
      if (s.c === 'M' || s.c === 'L') return { ...s, ...map(s) };
      if (s.c === 'C') {
        return { ...s, x1: W - s.x1, x2: W - s.x2, x: W - s.x };
      }
      return s;
    }),
  };
}
