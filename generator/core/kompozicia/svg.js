// SVG assembly for compositions. One standalone document with layers
// fotky → pattern → text → spadavka (photos sit under the pattern so the
// `prekrytie` mode shows shapes over the image; clipped modes are unaffected
// because zones keep shapes away anyway). All numbers rounded to 4 decimals,
// output byte-deterministic.

import { fmt } from '../geometry.js';

export function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Translate serialized path data (absolute M/L/C/Z only, as produced by the
// core) without a per-shape transform attribute.
export function translatePathD(d, dx, dy) {
  const out = [];
  let cmd = null;
  let nums = [];
  const flush = () => {
    if (!cmd) return;
    if (cmd === 'Z') {
      out.push('Z');
    } else {
      const n = nums.map(Number);
      if (cmd === 'C') {
        out.push(`C ${f(n[0] + dx)} ${f(n[1] + dy)} ${f(n[2] + dx)} ${f(n[3] + dy)} ${f(n[4] + dx)} ${f(n[5] + dy)}`);
      } else {
        out.push(`${cmd} ${f(n[0] + dx)} ${f(n[1] + dy)}`);
      }
    }
    nums = [];
  };
  for (const m of d.match(/-?[\d.]+(?:e-?\d+)?|[A-Za-z]/g) || []) {
    if (/[A-Za-z]/.test(m)) {
      flush();
      cmd = m;
    } else {
      nums.push(m);
    }
  }
  flush();
  return out.join(' ');
}

function f(n) {
  const r = Math.round(n * 1e4) / 1e4;
  return Object.is(r, -0) ? '0' : String(r);
}

function fontFace(name, url, format) {
  return `@font-face { font-family: '${name}'; src: url('${url}') format('${format}'); }`;
}

const FONT_FORMATS = { 'Brnos Aires': 'woff2', Nunito: 'truetype' };

export function styleForFonts(fontUrls) {
  const faces = Object.entries(fontUrls || {})
    .filter(([name]) => FONT_FORMATS[name])
    .map(([name, url]) => fontFace(name, url, FONT_FORMATS[name]));
  return faces.length ? `<style>${faces.join(' ')}</style>` : '';
}

// --- layers -----------------------------------------------------------------

function photoLayer(zony, placed, cfg, uid) {
  const parts = [];
  const defs = [];
  for (const z of zony) {
    if (z.typ !== 'fotka') continue;
    const r = z.rect;
    if (!z.zdroj) {
      // empty photo zone — a light grey placeholder keeps the frame visible
      parts.push(`<rect x="${f(r.x)}" y="${f(r.y)}" width="${f(r.w)}" height="${f(r.h)}" fill="${cfg.placeholderFarba}"/>`);
      continue;
    }
    const href = esc(z.zdroj);
    const w = r.w * z.zoom;
    const h = r.h * z.zoom;
    const x = r.x + (z.posun ? z.posun[0] : 0) * r.w;
    const y = r.y + (z.posun ? z.posun[1] : 0) * r.h;
    if (z.rezim === 'maska') {
      // clip to the largest placed shape overlapping the zone, else the rect
      const overlapping = placed
        .filter((p) => p.bbox.x < r.x + r.w && p.bbox.x + p.bbox.w > r.x
          && p.bbox.y < r.y + r.h && p.bbox.y + p.bbox.h > r.y)
        .sort((a, b) => (b.bbox.w * b.bbox.h) - (a.bbox.w * a.bbox.h));
      const shape = overlapping[0];
      const id = `maska-${uid()}`;
      if (shape) {
        defs.push(`<clipPath id="${id}"><path d="${shape.d}" clip-rule="nonzero"/></clipPath>`);
        parts.push(`<image href="${href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>`);
      } else {
        parts.push(`<image href="${href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid slice"/>`);
      }
      continue;
    }
    if (z.rezim === 'prekrytie') {
      // full-zone image under the pattern layer — no clip at all
      parts.push(`<image href="${href}" x="${f(r.x)}" y="${f(r.y)}" width="${f(r.w)}" height="${f(r.h)}" preserveAspectRatio="xMidYMid slice"/>`);
      continue;
    }
    // ramik — clipped to the zone rect
    const id = `ramik-${uid()}`;
    defs.push(`<clipPath id="${id}"><rect x="${f(r.x)}" y="${f(r.y)}" width="${f(r.w)}" height="${f(r.h)}"/></clipPath>`);
    parts.push(`<image href="${href}" x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>`);
  }
  return { parts, defs };
}

function textLayer(zony, fg, cfg) {
  const parts = [];
  for (const z of zony) {
    if (z.typ !== 'text' || !z.text) continue;
    const r = z.rect;
    const anchor = z.zarovnanie === 'stred' ? 'middle' : z.zarovnanie === 'vpravo' ? 'end' : 'start';
    const x = z.zarovnanie === 'stred' ? r.x + r.w / 2 : z.zarovnanie === 'vpravo' ? r.x + r.w : r.x;
    const lineH = z.velkost * z.riadkovanie;
    const lines = String(z.text).split('\n');
    lines.forEach((line, i) => {
      const y = r.y + z.velkost * cfg.riadokPrvy + i * lineH;
      parts.push(
        `<text x="${f(x)}" y="${f(y)}" font-family="${esc(z.pismo)}" font-size="${f(z.velkost)}"`
        + ` text-anchor="${anchor}" fill="${fg}" style="font-feature-settings: 'liga', 'ss01'">${esc(line)}</text>`);
    });
  }
  return parts;
}

// --- document ---------------------------------------------------------------

export function renderSvg({
  stlpce, vyskaD, bleedD, jednotka, sirka, vyska, spadavka,
  placed, zony, inverzia, fontUrls, cfg,
}) {
  const fg = inverzia ? '#fff' : '#000';
  const bg = inverzia ? '#000' : '#fff';
  const unit = jednotka === 'mm' ? 'mm' : 'px';

  let uidN = 0;
  const uid = () => String(uidN++);

  const patternD = placed.map((p) => p.d).join(' ');
  const { parts: fotoParts, defs: fotoDefs } = photoLayer(zony, placed, cfg, uid);
  const textParts = textLayer(zony, fg, cfg);
  const style = styleForFonts(fontUrls);

  const vb = `${f(-bleedD)} ${f(-bleedD)} ${f(stlpce + 2 * bleedD)} ${f(vyskaD + 2 * bleedD)}`;
  const out = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${f(sirka + 2 * spadavka)}${unit}"`
    + ` height="${f(vyska + 2 * spadavka)}${unit}" viewBox="${vb}">`,
    style,
    ...(fotoDefs.length ? [`<defs>${fotoDefs.join('')}</defs>`] : []),
    `<rect x="${f(-bleedD)}" y="${f(-bleedD)}" width="${f(stlpce + 2 * bleedD)}" height="${f(vyskaD + 2 * bleedD)}" fill="${bg}"/>`,
    `<g id="fotky">${fotoParts.join('')}</g>`,
    `<g id="pattern">${patternD ? `<path d="${patternD}" fill="${fg}" fill-rule="nonzero"/>` : ''}</g>`,
    `<g id="text">${textParts.join('')}</g>`,
    `<g id="spadavka">${spadavka > 0
      ? `<rect x="0" y="0" width="${f(stlpce)}" height="${f(vyskaD)}" fill="none" stroke="${cfg.spadavkaFarba}" stroke-width="${f(cfg.spadavkaHrubka)}"/>`
      : ''}</g>`,
    '</svg>',
  ];
  return `${out.filter(Boolean).join('\n')}\n`;
}
