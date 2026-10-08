// hmotaSoStrbinou — a solid U-shaped mass: two heavy legs joined at the
// bottom, separated by a hairline-wide slot ending in a round bottom, leaving
// a solid bottom of ~heavy. One closed outline (the slot opens through the
// top edge, so there is no separate counter contour). Rotate 90° for the C
// form.

import {
  appendArc, closePath, curveTo, fillet, lineTo, moveTo,
} from '../geometry.js';
import { ValidationError } from '../errors.js';

export const id = 'hmotaSoStrbinou';
export const name = 'Hmota so štrbinou';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.2, max: 20 },
  sirka: { label: 'šírka (null = 2·heavy + hair)', type: 'number', min: 0.1, max: 20, nullable: true },
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
  const pr = prop.proporcie.hmotaSoStrbinou;
  const t = axes.heavy;
  const W = p.sirka ?? 2 * t + axes.hair;
  const H = p.dlzka;

  const slot = Math.min(axes.hair, W - 0.08);
  if (slot <= 0.01) {
    throw new ValidationError('Hmota so štrbinou: šírka je príliš malá na štrbinu, zväčči ju.');
  }
  const xSL = W / 2 - slot / 2;
  const xSR = W / 2 + slot / 2;
  const legW = (W - slot) / 2;
  const yEnd = H - t - slot / 2; // slot bottom semicircle centre
  if (yEnd < slot / 2 + 0.02) {
    throw new ValidationError(
      'Hmota so štrbinou: dĺžka je príliš krátka na štrbinu s dnom, zväčči dĺžku.');
  }

  const rb = Math.min(pr.bottomCorner * t, legW * 0.49, H * 0.49);
  const rt = Math.min(pr.topCorner * t, legW * 0.49, yEnd * 0.4);

  // outer corners
  const TR = { x: W, y: 0 };
  const BR = { x: W, y: H };
  const BL = { x: 0, y: H };
  const TL = { x: 0, y: 0 };
  const fTR = fillet(TL, TR, { x: W, y: H }, rt);
  const fBR = fillet({ x: W, y: 0 }, BR, BL, rb);
  const fBL = fillet(BR, BL, { x: 0, y: 0 }, rb);
  const fTL = fillet(BL, TL, TR, rt);

  const segs = [];
  segs.push(moveTo(xSL, 0));
  segs.push(lineTo(xSL, yEnd));
  appendArc(segs, W / 2, yEnd, slot / 2, slot / 2, Math.PI, 0); // slot round bottom
  segs.push(lineTo(xSR, 0));
  pushFillet(segs, fTR, TR);
  pushFillet(segs, fBR, BR);
  pushFillet(segs, fBL, BL);
  pushFillet(segs, fTL, TL);
  segs.push(closePath());

  return {
    subpaths: [{ segs }],
    joints: [
      { x: xSL / 2, y: 0, dir: 'up' },
      { x: (xSR + W) / 2, y: 0, dir: 'up' },
    ],
  };
}
