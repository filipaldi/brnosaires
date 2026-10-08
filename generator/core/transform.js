// Generic transforms applied to every shape in one place: mirror (horizontal
// flip) and rotation in 90° steps. After transforming, the shape is translated
// back so its bounding box starts at (0, 0), and subpath windings are
// normalised (solids clockwise, holes counter-clockwise) so a single
// fill-rule="nonzero" paints overlaps solid and holes empty.

import {
  reverseSubpath, signedArea, subpathPoints, bboxOfPoints,
} from './geometry.js';
import { ValidationError } from './errors.js';

function mapSeg(seg, fn) {
  if (seg.c === 'M' || seg.c === 'L') {
    const p = fn(seg);
    return { ...seg, x: p.x, y: p.y };
  }
  if (seg.c === 'C') {
    const c1 = fn({ x: seg.x1, y: seg.y1 });
    const c2 = fn({ x: seg.x2, y: seg.y2 });
    const p = fn({ x: seg.x, y: seg.y });
    return { ...seg, x1: c1.x, y1: c1.y, x2: c2.x, y2: c2.y, x: p.x, y: p.y };
  }
  return seg; // Z passes through untouched
}

function mapSubpath(sub, fn) {
  return { ...sub, segs: sub.segs.map((s) => mapSeg(s, fn)) };
}

const ROTATE_DIRS = { down: 'left', left: 'up', up: 'right', right: 'down' };
const MIRROR_DIRS = { left: 'right', right: 'left' };

export function validateRotate(value) {
  if (![0, 90, 180, 270].includes(value)) {
    throw new ValidationError(`rotate musí byť jedno z 0, 90, 180, 270 (dostal som ${value}).`);
  }
  return value;
}

export function transformShape(shape, { rotate = 0, mirror = false } = {}) {
  validateRotate(rotate);
  let subpaths = shape.subpaths;
  let joints = shape.joints || [];
  const bbox = () => bboxOfPoints(subpaths.flatMap((s) => subpathPoints(s.segs)));

  if (mirror) {
    const bb = bbox();
    const cx = bb.x + bb.w / 2;
    subpaths = subpaths.map((s) => mapSubpath(s, (p) => ({ x: 2 * cx - p.x, y: p.y })));
    joints = joints.map((j) => ({ ...j, x: 2 * cx - j.x, dir: MIRROR_DIRS[j.dir] || j.dir }));
  }

  for (let step = 0; step < rotate / 90; step++) {
    const bb = bbox();
    const cx = bb.x + bb.w / 2;
    const cy = bb.y + bb.h / 2;
    // 90° clockwise on screen: a point right of the centre moves below it.
    subpaths = subpaths.map((s) =>
      mapSubpath(s, (p) => ({ x: cx - (p.y - cy), y: cy + (p.x - cx) })));
    joints = joints.map((j) => ({ ...j, x: cx - (j.y - cy), y: cy + (j.x - cx), dir: ROTATE_DIRS[j.dir] || j.dir }));
  }

  // re-anchor at the origin
  const bb = bbox();
  if (bb.x !== 0 || bb.y !== 0) {
    subpaths = subpaths.map((s) => mapSubpath(s, (p) => ({ x: p.x - bb.x, y: p.y - bb.y })));
    joints = joints.map((j) => ({ ...j, x: j.x - bb.x, y: j.y - bb.y }));
  }

  return { ...shape, subpaths, joints };
}

// Solids keep clockwise winding (positive shoelace area, y down), holes go
// counter-clockwise. Overlapping solid subpaths then fill as a union under
// the nonzero rule.
export function normalizeWindings(shape) {
  const subpaths = shape.subpaths.map((sub) => {
    const area = signedArea(sub.segs);
    if (sub.hole ? area > 0 : area < 0) {
      return { ...sub, segs: reverseSubpath(sub.segs) };
    }
    return sub;
  });
  return { ...shape, subpaths };
}
