// Export pipeline: SVG straight from the engine, PNG/AVIF rasterised through
// an offscreen canvas. For raster formats the fonts are inlined as data URLs
// so the SVG image (which cannot fetch external resources) still sets text
// in Brnos Aires / Nunito.

import { komponuj } from './engine.js';

const FONT_FILES = {
  'Brnos Aires': '/theme/static/fonts/brnos-aires.woff2',
  'Nunito': '/theme/static/fonts/nunito-variable.ttf',
};

// Absolute URLs: the downloaded SVG stays valid when opened from the server.
export function fontUrlsAbsolute() {
  const out = {};
  for (const [name, path] of Object.entries(FONT_FILES)) {
    out[name] = new URL(path, location.origin).href;
  }
  return out;
}

const dataUrlCache = new Map();

async function fontUrlsInlined() {
  const out = {};
  for (const [name, path] of Object.entries(FONT_FILES)) {
    if (!dataUrlCache.has(path)) {
      const blob = await (await fetch(path)).blob();
      dataUrlCache.set(path, await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      }));
    }
    out[name] = dataUrlCache.get(path);
  }
  return out;
}

export function download(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

export function safeVariant(variant) {
  return String(variant).replace(/[^a-zA-Z0-9-_]+/g, '-').slice(0, 40) || 'variant';
}

export async function exportSvgFile(spec) {
  const { svg } = komponuj(spec, { fontUrls: fontUrlsAbsolute() });
  download(new Blob([svg], { type: 'image/svg+xml' }), `brnos-aires-${safeVariant(spec.variant)}.svg`);
}

let avifSupport = null;

export async function avifSupported() {
  if (avifSupport !== null) return avifSupport;
  avifSupport = await new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    canvas.width = 2;
    canvas.height = 2;
    canvas.toBlob((blob) => resolve(Boolean(blob && blob.type === 'image/avif')), 'image/avif');
  });
  return avifSupport;
}

// Rasterise: render the SVG at sirkaPx × vyskaPx through an <img> (data URLs
// inside an SVG image are the one kind of reference Chromium keeps loading).
async function rasterise(spec, mime) {
  const fontUrls = await fontUrlsInlined();
  const { svg, sirkaPx, vyskaPx } = komponuj(spec, { fontUrls });
  // The engine sizes the root in mm/px of the format; pin it to raster pixels.
  const sized = svg.replace(/<svg([^>]*)>/, (m, attrs) => attrs
    .replace(/\swidth="[^"]*"/, ` width="${sirkaPx}"`)
    .replace(/\sheight="[^"]*"/, ` height="${vyskaPx}"`));
  const url = URL.createObjectURL(new Blob([sized], { type: 'image/svg+xml' }));
  try {
    const img = new Image();
    img.decoding = 'sync';
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = () => reject(new Error('SVG sa nepodarilo vykresliť na raster.'));
      img.src = url;
    });
    await img.decode().catch(() => {});
    const canvas = document.createElement('canvas');
    canvas.width = sirkaPx;
    canvas.height = vyskaPx;
    canvas.getContext('2d').drawImage(img, 0, 0, sirkaPx, vyskaPx);
    return await new Promise((resolve, reject) => {
      canvas.toBlob((blob) => (blob ? resolve(blob)
        : reject(new Error('Prehliadač nevedel zakódovať obrázok.'))), mime);
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function exportPngFile(spec) {
  const blob = await rasterise(spec, 'image/png');
  download(blob, `brnos-aires-${safeVariant(spec.variant)}.png`);
}

export async function exportAvifFile(spec) {
  const blob = await rasterise(spec, 'image/avif');
  download(blob, `brnos-aires-${safeVariant(spec.variant)}.avif`);
}

export function rasterDimensions(spec) {
  const pxPerUnit = spec.format.jednotka === 'mm' ? spec.format.dpi / 25.4 : 1;
  return {
    sirkaPx: Math.round(spec.format.sirka * pxPerUnit),
    vyskaPx: Math.round(spec.format.vyska * pxPerUnit),
  };
}
