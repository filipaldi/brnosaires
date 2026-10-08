// SVG serialization: every shape is filled outlines (fill only, no stroke)
// on a white background. Output is fully deterministic — same input, same
// bytes. The sheet also draws column headers, cell labels and (in specimens
// only) red joint markers. With `primitivy` it shows the construction instead:
// each subpath in the colour of its primitive, holes punched white on top.

import { fmt } from './geometry.js';

const BLACK = '#000';
const WHITE = '#fff';
const JOINT_COLOR = '#d40000';

// Construction view: one grey per primitive, red for the concave-corner
// patches. Labels are the Slovak names shown in the sheet legend.
const PART_COLORS = {
  obdlznik: '#9a9a9a',
  prstenec: '#5a5a5a',
  krivka: '#2a2a2a',
  roh: '#d40000',
};
const PART_LABELS = {
  obdlznik: 'obdĺžnik',
  prstenec: 'prstenec',
  krivka: 'krivka',
  roh: 'vnútorný roh',
};

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function shapePathD(shape) {
  return shape.paths.join(' ');
}

function shapeGroup(shape, { x, y, scale, showJoints, jointR, primitivy = false }) {
  const transform = `translate(${fmt(x)} ${fmt(y)}) scale(${fmt(scale)})`;
  const parts = [];
  if (primitivy && shape.parts) {
    // Solids semi-transparent so overlaps between primitives are visible;
    // holes are painted opaque white on top of everything in the cell.
    parts.push(shape.parts.filter((p) => !p.hole).map((p) => (
      `<path d="${p.d}" fill="${PART_COLORS[p.part] || BLACK}" fill-opacity="0.75" fill-rule="nonzero" transform="${transform}"/>`
    )).join(''));
    parts.push(shape.parts.filter((p) => p.hole).map((p) => (
      `<path d="${p.d}" fill="${WHITE}" fill-rule="nonzero" transform="${transform}"/>`
    )).join(''));
  } else {
    parts.push(`<path d="${shapePathD(shape)}" fill="${BLACK}" fill-rule="nonzero" transform="${transform}"/>`);
  }
  if (showJoints && shape.joints.length) {
    const dots = shape.joints
      .map((j) => `<circle cx="${fmt(j.x)}" cy="${fmt(j.y)}" r="${fmt(jointR / scale)}" fill="${JOINT_COLOR}"/>`)
      .join('');
    parts.push(`<g transform="translate(${fmt(x)} ${fmt(y)}) scale(${fmt(scale)})">${dots}</g>`);
  }
  return parts.join('');
}

// One tightly cropped shape, margin in dieliks, scale in px per dielik.
export function renderShapeSvg(shape, { pxPerDielik = 100, margin = 0.25, showJoints = false } = {}) {
  const s = pxPerDielik;
  const vbX = (shape.bbox.x - margin) * s;
  const vbY = (shape.bbox.y - margin) * s;
  const vbW = (shape.bbox.w + 2 * margin) * s;
  const vbH = (shape.bbox.h + 2 * margin) * s;
  const w = Math.max(1, Math.round(vbW));
  const h = Math.max(1, Math.round(vbH));
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${fmt(vbX)} ${fmt(vbY)} ${fmt(vbW)} ${fmt(vbH)}">`,
    `<rect x="${fmt(vbX)}" y="${fmt(vbY)}" width="${fmt(vbW)}" height="${fmt(vbH)}" fill="${WHITE}"/>`,
    shapeGroup(shape, { x: 0, y: 0, scale: s, showJoints, jointR: 6 }),
    '</svg>',
    '',
  ].join('\n');
}

// Specimen sheet: a grid of cells (one column per Weight value, one row per
// type × Contrast) and labels under each cell.
//
//   colHeaders  ['Weight 20', ...]
//   rows        [{ label, sub, cells: [{ shape }], jointDots }]
export function renderSheetSvg({
  title, colHeaders, rows, cellW = 200, cellH = 252, pxPerDielik = 52,
  showJoints = false, primitivy = false,
}) {
  const pad = 18;
  // In the construction view the legend line sits under the title, so the
  // header grows and the column headers move down with it.
  const headerH = primitivy ? 88 : 64;
  const colHeaderY = primitivy ? 76 : 52;
  const labelH = 42;
  const nCols = colHeaders.length;
  const nRows = rows.length;
  const W = pad * 2 + nCols * cellW;
  const H = headerH + nRows * cellH + pad;
  const out = [];

  out.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="sans-serif">`);
  out.push(`<rect width="${W}" height="${H}" fill="${WHITE}"/>`);

  out.push(
    `<text x="${pad}" y="30" font-size="17" font-weight="bold" fill="${BLACK}">${esc(title)}</text>`);
  if (primitivy) {
    let lx = pad;
    for (const part of Object.keys(PART_COLORS)) {
      out.push(`<rect x="${lx}" y="40" width="11" height="11" fill="${PART_COLORS[part]}"/>`);
      out.push(
        `<text x="${lx + 16}" y="50" font-size="11" fill="${BLACK}">${esc(PART_LABELS[part])}</text>`);
      lx += 16 + PART_LABELS[part].length * 6 + 22;
    }
  }
  colHeaders.forEach((hdr, c) => {
    const cx = pad + c * cellW + cellW / 2;
    out.push(
      `<text x="${cx}" y="${colHeaderY}" font-size="13" text-anchor="middle" fill="${BLACK}">${esc(hdr)}</text>`);
  });

  rows.forEach((row, r) => {
    const top = headerH + r * cellH;
    out.push(
      `<line x1="${pad}" y1="${top}" x2="${W - pad}" y2="${top}" stroke="#ddd" stroke-width="1"/>`);
    row.cells.forEach((cell, c) => {
      const left = pad + c * cellW;
      const baseline = top + cellH - labelH - 14;
      const shape = cell.shape;
      const contentH = cellH - labelH - 34;
      const scale = pxPerDielik * Math.min(1, contentH / Math.max(shape.bbox.h * pxPerDielik, 1));
      const wPx = shape.bbox.w * scale;
      const x = left + (cellW - wPx) / 2 - shape.bbox.x * scale;
      const y = baseline - (shape.bbox.y + shape.bbox.h) * scale;
      out.push(shapeGroup(shape, {
        x, y, scale, showJoints: showJoints && row.jointDots, jointR: 5, primitivy,
      }));
      const labelX = left + cellW / 2;
      out.push(
        `<text x="${labelX}" y="${top + cellH - labelH + 16}" font-size="12" text-anchor="middle" fill="${BLACK}">${esc(row.label)}</text>`);
      out.push(
        `<text x="${labelX}" y="${top + cellH - labelH + 32}" font-size="10" text-anchor="middle" fill="#555">${esc(row.sub)}</text>`);
    });
  });

  out.push('</svg>');
  out.push('');
  return out.join('\n');
}
