// Adapter between the UI and the composition engine. The real engine lives in
// generator/core/kompozicia/ (phase 2, built in parallel); until it exists we
// fall back to the local stub.js with the same signatures, so the UI works now
// and switches over automatically.

let impl;
let usingStub = false;
try {
  impl = await import('../core/kompozicia/index.js');
} catch (err) {
  impl = await import('./stub.js');
  usingStub = true;
  console.warn('Jadro kompozície (generator/core/kompozicia) nie je dostupné, beží náhradný engine.', err);
}

export const isStubEngine = usingStub;
export const normalizujSpec = impl.normalizujSpec;
export const komponuj = impl.komponuj;

// renderShapeSvg is only needed by the shape viewer; keep a local fallback in
// case core/svg.js changes shape while the other agents work on it.
export let renderShapeSvg = null;
try {
  ({ renderShapeSvg } = await import('../core/svg.js'));
} catch {
  renderShapeSvg = null;
}

// Minimal fallback with the same call contract as core/svg.js renderShapeSvg.
export function renderShapeSvgFallback(shape, { pxPerDielik = 100, margin = 0.25 } = {}) {
  const s = pxPerDielik;
  const vbX = (shape.bbox.x - margin) * s;
  const vbY = (shape.bbox.y - margin) * s;
  const vbW = (shape.bbox.w + 2 * margin) * s;
  const vbH = (shape.bbox.h + 2 * margin) * s;
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${Math.max(1, Math.round(vbW))}" `
      + `height="${Math.max(1, Math.round(vbH))}" viewBox="${vbX} ${vbY} ${vbW} ${vbH}">`,
    `<rect x="${vbX}" y="${vbY}" width="${vbW}" height="${vbH}" fill="#fff"/>`,
    `<path d="${shape.paths.join(' ')}" fill="#000" fill-rule="nonzero"/>`,
    '</svg>',
    '',
  ].join('\n');
}
