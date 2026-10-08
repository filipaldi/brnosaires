// Public API of the generator core.
//
//   TYPES          list of { id, name } in sheet order
//   defaultParams  clone of a type's default parameters (values live in
//                  proporcie.json, so the type designer tunes them there)
//   buildShape     (type, params, axes) → { paths, parts, bbox, joints }
//
// `params` may also carry `rotate` (0/90/180/270) and `mirror` (boolean);
// they are applied generically here, never inside individual shapes.

import { serializeSubpath, subpathPoints, bboxOfPoints } from './geometry.js';
import { loadProporcie } from './axes.js';
import { transformShape, normalizeWindings, validateRotate } from './transform.js';
import { SHAPES, findShape } from './shapes/index.js';
import { ValidationError } from './errors.js';

export { computeAxes, loadProporcie } from './axes.js';
export { ValidationError } from './errors.js';

export const proporcie = loadProporcie();

export const TYPES = SHAPES.map((s) => ({ id: s.id, name: s.name }));

export function defaultParams(type) {
  const shape = findShape(type);
  if (!shape) {
    throw new ValidationError(
      `Neznámy typ tvaru „${type}“. Platné typy: ${SHAPES.map((s) => s.id).join(', ')}.`);
  }
  return { ...proporcie.parametre[shape.id] };
}

function validateParams(shape, params) {
  const spec = shape.params;
  for (const [key, value] of Object.entries(params)) {
    const s = spec[key];
    if (!s) {
      throw new ValidationError(
        `Neznámy parameter „${key}“ pre typ ${shape.id}. Platné parametre: ${Object.keys(spec).join(', ')}.`);
    }
    if (value === null || value === undefined) {
      if (!s.nullable) {
        throw new ValidationError(`Parameter „${key}“ neprijíma hodnotu null.`);
      }
      continue;
    }
    if (s.type === 'enum') {
      if (!s.values.includes(value)) {
        throw new ValidationError(
          `Parameter „${key}“ prijíma iba ${s.values.join(' | ')} (dostal som „${value}“).`);
      }
    } else if (s.type === 'integer') {
      if (!Number.isInteger(value)) {
        throw new ValidationError(`Parameter „${key}“ musí byť celé číslo (dostal som „${value}“).`);
      }
      if (value < s.min || value > s.max) {
        throw new ValidationError(`Parameter „${key}“ musí byť v rozsahu ${s.min}–${s.max}.`);
      }
    } else {
      if (typeof value !== 'number' || !Number.isFinite(value)) {
        throw new ValidationError(`Parameter „${key}“ musí byť číslo (dostal som „${value}“).`);
      }
      if (value < s.min || value > s.max) {
        throw new ValidationError(
          `Parameter „${key}“ musí byť v rozsahu ${s.min}–${s.max} (dostal som ${value}).`);
      }
    }
  }
}

export function buildShape(type, params, axes) {
  const shape = findShape(type);
  if (!shape) {
    throw new ValidationError(
      `Neznámy typ tvaru „${type}“. Platné typy: ${SHAPES.map((s) => s.id).join(', ')}.`);
  }
  const { rotate = 0, mirror = false, spoje = [], ...rest } = params || {};
  validateRotate(rotate);
  if (typeof mirror !== 'boolean') {
    throw new ValidationError('mirror musí byť true/false.');
  }
  if (!Array.isArray(spoje) || spoje.some((id) => typeof id !== 'string')) {
    throw new ValidationError('spoje musí byť pole názvov koncov ťahu, napr. ["dole"].');
  }
  const merged = { ...defaultParams(type), ...rest };
  validateParams(shape, merged);

  // Which joint ids exist can depend on the parameters (oblouk's legs), so the
  // shape is built once to learn them; with any spoje it is rebuilt with the
  // joined ends kept square.
  let built = shape.build(merged, axes, proporcie);
  const ids = built.joints.map((j) => j.id);
  for (const id of spoje) {
    if (!ids.includes(id)) {
      throw new ValidationError(
        `Neznámy spoj „${id}“ pre typ ${shape.id}. Platné spoje: ${ids.join(', ') || 'žiadne'}.`);
    }
  }
  if (spoje.length) {
    built = shape.build({ ...merged, spoje }, axes, proporcie);
  }
  const transformed = normalizeWindings(transformShape(built, { rotate, mirror }));

  const pts = transformed.subpaths.flatMap((s) => subpathPoints(s.segs));
  const bbox = bboxOfPoints(pts);
  // `parts` keeps what `paths` drops: which primitive built each subpath and
  // whether it is a hole, so a renderer can show the construction.
  const parts = transformed.subpaths.map((s) => ({
    d: serializeSubpath(s.segs), part: s.part, hole: Boolean(s.hole),
  }));
  const paths = parts.map((p) => p.d);

  return { paths, parts, bbox, joints: transformed.joints };
}

export function paramSpec(type) {
  const shape = findShape(type);
  if (!shape) {
    throw new ValidationError(
      `Neznámy typ tvaru „${type}“. Platné typy: ${SHAPES.map((s) => s.id).join(', ')}.`);
  }
  return shape.params;
}
