// Generátor Brnos Aires — phase 4 UI. One top bar, one canvas, no modes.
// The whole spec lives in a single object; every change re-renders the sheet
// through the composition engine (debounced) and persists to localStorage.

import * as engine from './engine.js';
import { TYPES } from '../core/index.js';
import { createViewer } from './viewer.js';
import {
  exportSvgFile, exportPngFile, exportAvifFile, avifSupported,
  rasterDimensions, download, fontUrlsAbsolute,
} from './export.js';

const $ = (sel) => document.querySelector(sel);

const LS_KEY = 'brnosaires-generator-spec-v1';
const MM_TO_PX = 96 / 25.4; // CSS px per mm at zoom 100 %
const ZOOM_STEPS = [25, 33, 50, 67, 75, 90, 100, 125, 150, 200];

const FORMAT_PRESETS = {
  A2: { sirka: 420, vyska: 594, jednotka: 'mm', dpi: 300, spadavka: 3 },
  A3: { sirka: 297, vyska: 420, jednotka: 'mm', dpi: 300, spadavka: 3 },
  IG: { sirka: 1080, vyska: 1350, jednotka: 'px', dpi: 72, spadavka: 0 },
  web: { sirka: 1200, vyska: 630, jednotka: 'px', dpi: 72, spadavka: 0 },
};

const ROZLOZENIE = [
  ['rovnomerne', 'rovnomerne'],
  ['malePlusVelke', 'veľa malých a pár veľkých'],
  ['krajne', 'len krajné hodnoty'],
];

const SPRAVANIE = [
  ['prazdna', 'prázdna'],
  ['presah', 'presah'],
  ['okraj', 'okraj'],
];

// ---------- state ----------

let spec = loadSpec();
let result = null; // last good komponuj() output
let view = { s: 1, vbX: 0, vbY: 0, bleedD: 0, cols: 8, rowsD: 0 };
let zoomPct = 75;
let selected = -1;
let editorOpen = false;
let photoPan = false;
let dragging = null;

const overlay = $('#overlay');
const svgHost = $('#svg-host');
const zonesHost = $('#zones');
const gridLines = $('#grid-lines');
const bleedMark = $('#bleed-mark');
const zoneBar = $('#zone-bar');

function loadSpec() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      // types dropped from the set (e.g. koleno) must not discard the saved state
      const typy = saved?.kompozicia?.typy;
      if (Array.isArray(typy)) {
        saved.kompozicia.typy = typy.filter((t) => TYPES.some((x) => x.id === t));
      }
      return engine.normalizujSpec(saved);
    }
  } catch (err) {
    console.warn('Uložený stav sa nepodarilo načítať, začínam odznova.', err);
  }
  try {
    return engine.normalizujSpec({});
  } catch (err) {
    console.error(err);
    return null;
  }
}

let saveTimer = 0;
function saveLocal() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(spec));
    } catch {
      // private mode or full storage: working in memory is enough
    }
  }, 400);
}

// ---------- render pipeline ----------

let renderTimer = 0;
function scheduleRender() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(render, 50);
}

function render() {
  try {
    result = engine.komponuj(spec, { fontUrls: fontUrlsAbsolute() });
  } catch (err) {
    toast(err.message || String(err));
    return; // keep the last good sheet on screen
  }
  const svgEl = mountSvg(result.svg);
  layoutSheet(svgEl);
  drawOverlay();
  syncBar();
  if (result.varovania.length) toast(result.varovania.join(' '), 5000);
  saveLocal();
}

function mountSvg(svgString) {
  svgHost.innerHTML = svgString;
  const svgEl = svgHost.querySelector('svg');
  svgEl.style.width = '100%';
  svgEl.style.height = '100%';
  return svgEl;
}

function layoutSheet(svgEl) {
  const f = spec.format, g = spec.grid;
  const dielikUnits = f.sirka / g.stlpce; // mm or px per dielik
  const unitPx = f.jednotka === 'mm' ? MM_TO_PX : 1;
  const s = dielikUnits * unitPx * zoomPct / 100; // screen px per dielik
  const vb = svgEl.viewBox.baseVal;
  $('#sheet').style.width = `${Math.round(vb.width * s)}px`;
  $('#sheet').style.height = `${Math.round(vb.height * s)}px`;
  document.body.classList.toggle('inverted', spec.inverzia);
  view = {
    s, vbX: vb.x, vbY: vb.y,
    bleedD: f.spadavka / dielikUnits,
    cols: g.stlpce,
    rowsD: f.vyska / dielikUnits,
  };
}

function dielikPx() { return view.s; }

// Cursor position in dieliks, relative to the trimmed format origin.
function cursorDieliks(e) {
  const r = overlay.getBoundingClientRect();
  return {
    x: (e.clientX - r.left) / view.s - (view.bleedD - view.vbX),
    y: (e.clientY - r.top) / view.s - (view.bleedD - view.vbY),
  };
}

function zoneRectPx(z) {
  const off = view.bleedD - view.vbX;
  const offY = view.bleedD - view.vbY;
  return {
    left: (z.x + off) * view.s,
    top: (z.y + offY) * view.s,
    width: z.w * view.s,
    height: z.h * view.s,
  };
}

function maxCellY(h) {
  return Math.max(0, Math.floor(view.rowsD - h));
}

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

// ---------- overlay ----------

function drawOverlay() {
  overlay.style.setProperty('--dielik-px', `${view.s}px`);

  // Bleed: always faintly marked, inset from the sheet edge.
  const bi = view.bleedD * view.s;
  bleedMark.style.left = `${bi}px`;
  bleedMark.style.top = `${bi}px`;
  bleedMark.style.right = `${bi}px`;
  bleedMark.style.bottom = `${bi}px`;

  zonesHost.replaceChildren();
  spec.zony.forEach((z, i) => {
    const div = document.createElement('div');
    div.className = 'zone' + (i === selected ? ' sel' : '') + (z.typ === 'prazdna' ? ' prazdna' : '');
    if (i === selected && z.typ === 'fotka' && photoPan) div.classList.add('photo-pan');
    Object.assign(div.style, styleRect(zoneRectPx(z)));
    div.dataset.i = String(i);
    if (z.typ === 'prazdna') {
      const hint = document.createElement('span');
      hint.className = 'hint';
      hint.textContent = 'Píš text alebo pretiahni fotku';
      div.append(hint);
    }
    if (i === selected) {
      for (const corner of ['tl', 'tr', 'bl', 'br']) {
        const handle = document.createElement('div');
        handle.className = `handle ${corner}`;
        handle.dataset.corner = corner;
        div.append(handle);
      }
    }
    zonesHost.append(div);
  });

  drawZoneBar();
  positionEditor();
}

function styleRect(r) {
  return {
    left: `${r.left}px`, top: `${r.top}px`,
    width: `${r.width}px`, height: `${r.height}px`,
  };
}

function drawZoneBar() {
  if (selected < 0 || !spec.zony[selected]) {
    zoneBar.hidden = true;
    return;
  }
  const z = spec.zony[selected];
  zoneBar.hidden = false;
  zoneBar.replaceChildren();

  const makeSelect = (label, options, value, onInput) => {
    const wrap = document.createElement('label');
    wrap.append(label + ' ');
    const select = document.createElement('select');
    for (const [val, name] of options) {
      const option = document.createElement('option');
      option.value = val;
      option.textContent = name;
      select.append(option);
    }
    select.value = value;
    select.addEventListener('input', () => { onInput(select.value); scheduleRender(); });
    wrap.append(select);
    return wrap;
  };

  const makeNumber = (label, value, attrs, onInput) => {
    const wrap = document.createElement('label');
    wrap.append(label + ' ');
    const input = document.createElement('input');
    input.type = 'number';
    for (const [k, v] of Object.entries(attrs)) input.setAttribute(k, String(v));
    input.value = String(value);
    input.addEventListener('input', () => {
      const n = Number(input.value);
      if (Number.isFinite(n)) { onInput(n); scheduleRender(); }
    });
    wrap.append(input);
    return wrap;
  };

  if (z.typ === 'text') {
    zoneBar.append(
      makeSelect('Písmo', [['Brnos Aires', 'Brnos Aires'], ['Nunito', 'Nunito']], z.pismo,
        (v) => { z.pismo = v; positionEditor(); }),
      makeNumber('Veľkosť', z.velkost, { min: 0.2, max: 40, step: 0.1 },
        (v) => { z.velkost = v; }),
      makeSelect('Zarovnanie', [['vlavo', 'vľavo'], ['na stred', 'na stred'], ['vpravo', 'vpravo']],
        z.zarovnanie, (v) => { z.zarovnanie = v; }),
      makeSelect('Správanie', SPRAVANIE, z.spravanie, (v) => { z.spravanie = v; }),
    );
  } else if (z.typ === 'fotka') {
    zoneBar.append(
      makeSelect('Režim', [['ramik', 'rámik'], ['maska', 'maska'], ['prekrytie', 'prekrytie']],
        z.rezim, (v) => { z.rezim = v; }),
      makeSelect('Správanie', SPRAVANIE, z.spravanie, (v) => { z.spravanie = v; }),
    );
    if (photoPan) {
      const note = document.createElement('span');
      note.textContent = 'Posun fotky: ťahaj, kolieskom zoom';
      zoneBar.append(note);
    }
  }

  const del = document.createElement('button');
  del.className = 'del';
  del.title = 'Zmazať zónu';
  del.textContent = '✕';
  del.addEventListener('click', () => deleteZone(selected));
  zoneBar.append(del);

  // Place under the zone, above when there is no room.
  const r = zoneRectPx(z);
  zoneBar.style.left = '0px';
  zoneBar.style.top = '0px';
  const bw = zoneBar.offsetWidth;
  const bh = zoneBar.offsetHeight;
  const ow = overlay.clientWidth;
  const oh = overlay.clientHeight;
  let left = clamp(r.left, 0, Math.max(0, ow - bw));
  let top = r.top + r.height + 8;
  if (top + bh > oh) top = r.top - bh - 8;
  zoneBar.style.left = `${Math.max(0, left)}px`;
  zoneBar.style.top = `${Math.max(0, top)}px`;
}

function selectZone(i) {
  selected = i;
  photoPan = false;
  drawOverlay();
}

function deleteZone(i) {
  if (i < 0 || i >= spec.zony.length) return;
  closeEditor();
  spec.zony.splice(i, 1);
  selected = -1;
  scheduleRender();
}

// ---------- pointer interactions on the canvas ----------

overlay.addEventListener('pointerdown', (e) => {
  if (e.button !== 0) return;
  if (e.target.closest('#zone-bar')) return;
  const handle = e.target.closest('.handle');
  const zoneDiv = e.target.closest('.zone');
  const pos = cursorDieliks(e);

  if (handle) {
    const i = Number(handle.closest('.zone').dataset.i);
    selected = i;
    dragging = { kind: 'resize', corner: handle.dataset.corner, i };
    gridLines.hidden = false;
    overlay.setPointerCapture(e.pointerId);
    drawOverlay();
    return;
  }

  if (zoneDiv) {
    const i = Number(zoneDiv.dataset.i);
    const z = spec.zony[i];
    if (selected !== i) photoPan = false;
    selected = i;
    if (z.typ === 'fotka' && photoPan) {
      dragging = {
        kind: 'photo-pan', i,
        start: pos, posun: [...z.posun],
      };
      zoneDiv.classList.add('dragging-photo');
    } else {
      dragging = {
        kind: 'move', i,
        grabX: pos.x - z.x, grabY: pos.y - z.y,
        moved: false,
      };
    }
    gridLines.hidden = false;
    overlay.setPointerCapture(e.pointerId);
    drawOverlay();
    return;
  }

  // Empty space: start creating a zone (a plain click only deselects).
  closeEditor();
  selected = -1;
  const cell = {
    x: clamp(Math.floor(pos.x), 0, view.cols),
    y: clamp(Math.floor(pos.y), 0, Math.floor(view.rowsD)),
  };
  dragging = { kind: 'create', start: cell };
  gridLines.hidden = false;
  overlay.setPointerCapture(e.pointerId);
  drawOverlay();
});

overlay.addEventListener('pointermove', (e) => {
  if (!dragging) return;
  const pos = cursorDieliks(e);
  const posCell = {
    x: clamp(Math.floor(pos.x), 0, view.cols),
    y: clamp(Math.floor(pos.y), 0, Math.floor(view.rowsD)),
  };

  if (dragging.kind === 'create') {
    const rect = rectFromCells(dragging.start, posCell);
    let ghost = $('#zone-create-ghost');
    if (!ghost) {
      ghost = document.createElement('div');
      ghost.id = 'zone-create-ghost';
      overlay.append(ghost);
    }
    Object.assign(ghost.style, styleRect({
      left: (rect.x + view.bleedD - view.vbX) * view.s,
      top: (rect.y + view.bleedD - view.vbY) * view.s,
      width: rect.w * view.s,
      height: rect.h * view.s,
    }));
    return;
  }

  const z = spec.zony[dragging.i];
  if (!z) return;

  if (dragging.kind === 'move') {
    dragging.moved = true;
    z.x = clamp(Math.round(pos.x - dragging.grabX), 0, view.cols - z.w);
    z.y = clamp(Math.round(pos.y - dragging.grabY), 0, maxCellY(z.h));
  } else if (dragging.kind === 'resize') {
    const l = { x: z.x, y: z.y };
    const r = { x: z.x + z.w, y: z.y + z.h };
    const c = dragging.corner;
    if (c.includes('l')) l.x = clamp(posCell.x, 0, r.x - 1);
    if (c.includes('r')) r.x = clamp(posCell.x, l.x + 1, view.cols);
    if (c.includes('t')) l.y = clamp(posCell.y, 0, r.y - 1);
    if (c.includes('b')) r.y = clamp(posCell.y, l.y + 1, Math.ceil(view.rowsD));
    z.x = l.x; z.y = l.y; z.w = r.x - l.x; z.h = r.y - l.y;
    if (editorOpen) positionEditor();
  } else if (dragging.kind === 'photo-pan') {
    z.posun = [
      dragging.posun[0] + (pos.x - dragging.start.x),
      dragging.posun[1] + (pos.y - dragging.start.y),
    ];
  }

  const div = zonesHost.querySelector(`.zone[data-i="${dragging.i}"]`);
  if (div) Object.assign(div.style, styleRect(zoneRectPx(z)));
  drawZoneBar();
});

function rectFromCells(a, b) {
  return {
    x: Math.min(a.x, b.x), y: Math.min(a.y, b.y),
    w: Math.abs(b.x - a.x), h: Math.abs(b.y - a.y),
  };
}

overlay.addEventListener('pointerup', (e) => {
  if (!dragging) return;
  const d = dragging;
  dragging = null;
  gridLines.hidden = true;
  $('#zone-create-ghost')?.remove();

  if (d.kind === 'create') {
    const pos = cursorDieliks(e);
    const rect = rectFromCells(d.start, {
      x: clamp(Math.floor(pos.x), 0, view.cols),
      y: clamp(Math.floor(pos.y), 0, Math.floor(view.rowsD)),
    });
    if (rect.w >= 1 && rect.h >= 1) {
      rect.w = Math.min(rect.w, view.cols - rect.x);
      rect.h = Math.min(rect.h, Math.ceil(view.rowsD) - rect.y);
      spec.zony.push({ typ: 'prazdna', spravanie: 'prazdna', ...rect });
      selected = spec.zony.length - 1;
    }
    scheduleRender();
    return;
  }

  if (d.kind === 'photo-pan') {
    zonesHost.querySelector(`.zone[data-i="${d.i}"]`)?.classList.remove('dragging-photo');
  }
  scheduleRender();
});

overlay.addEventListener('pointercancel', () => {
  dragging = null;
  gridLines.hidden = true;
  $('#zone-create-ghost')?.remove();
  scheduleRender();
});

// Double-click: text zone opens the editor, photo zone toggles pan/zoom.
overlay.addEventListener('dblclick', (e) => {
  const zoneDiv = e.target.closest('.zone');
  if (!zoneDiv) return;
  const i = Number(zoneDiv.dataset.i);
  const z = spec.zony[i];
  if (!z) return;
  if (z.typ === 'text') {
    openEditor(i);
  } else if (z.typ === 'fotka') {
    photoPan = !photoPan;
    drawOverlay();
    if (photoPan) toast('Úprava fotky: ťahaj pre posun, kolieskom zoom, dvojklik ukončí.', 4000);
  }
});

// Wheel zooms the photo while its pan mode is on.
overlay.addEventListener('wheel', (e) => {
  if (!photoPan || selected < 0) return;
  const z = spec.zony[selected];
  if (!z || z.typ !== 'fotka') return;
  e.preventDefault();
  z.zoom = clamp(z.zoom * (e.deltaY < 0 ? 1.08 : 1 / 1.08), 0.2, 8);
  scheduleRender();
}, { passive: false });

// ---------- dropping photos ----------

function readImageFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Súbor sa nepodarilo prečítať.'));
    reader.readAsDataURL(file);
  });
}

overlay.addEventListener('dragover', (e) => e.preventDefault());

overlay.addEventListener('drop', async (e) => {
  e.preventDefault();
  const file = [...e.dataTransfer.files].find((f) => f.type.startsWith('image/'));
  if (!file) {
    toast('Pretiahni obrázkový súbor (JPG, PNG, WebP…).');
    return;
  }
  const pos = cursorDieliks(e);
  const cell = {
    x: clamp(Math.floor(pos.x), 0, view.cols - 1),
    y: clamp(Math.floor(pos.y), 0, maxCellY(1)),
  };
  const hit = spec.zony.findIndex((z) =>
    pos.x >= z.x && pos.x < z.x + z.w && pos.y >= z.y && pos.y < z.y + z.h);

  try {
    const zdroj = await readImageFile(file);
    if (hit >= 0) {
      const z = spec.zony[hit];
      Object.assign(z, { typ: 'fotka', zdroj, rezim: 'ramik', posun: [0, 0], zoom: 1 });
      selected = hit;
    } else {
      const w = Math.min(4, view.cols - cell.x);
      const h = Math.min(3, Math.ceil(view.rowsD) - cell.y);
      spec.zony.push({
        typ: 'fotka', x: cell.x, y: cell.y, w, h, spravanie: 'prazdna',
        zdroj, rezim: 'ramik', posun: [0, 0], zoom: 1,
      });
      selected = spec.zony.length - 1;
    }
    scheduleRender();
  } catch (err) {
    toast(err.message);
  }
});

// ---------- inline text editing ----------

function zoneToText(i, firstKey) {
  const z = spec.zony[i];
  z.typ = 'text';
  z.text = firstKey === 'Enter' ? '' : firstKey;
  z.pismo = 'Brnos Aires';
  z.velkost = Math.min(1.2, Math.max(0.4, z.h - 0.3));
  z.zarovnanie = 'vlavo';
  z.riadkovanie = 1.1;
  openEditor(i);
}

function openEditor(i) {
  const z = spec.zony[i];
  if (!z || z.typ !== 'text') return;
  selected = i;
  editorOpen = true;
  let ta = document.getElementById('text-editor');
  if (!ta) {
    ta = document.createElement('textarea');
    ta.id = 'text-editor';
    ta.spellcheck = false;
    ta.addEventListener('input', () => {
      z.text = ta.value;
      scheduleRender();
    });
    ta.addEventListener('blur', (e) => {
      // Clicking a control in the zone bar must not close the editor.
      if (e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('#zone-bar')) return;
      closeEditor();
    });
    ta.addEventListener('keydown', (e) => {
      e.stopPropagation();
      if (e.key === 'Escape') {
        e.preventDefault();
        closeEditor();
      }
    });
    overlay.append(ta);
  }
  positionEditor();
  ta.value = z.text;
  ta.focus();
  ta.setSelectionRange(ta.value.length, ta.value.length);
  drawOverlay();
}

function positionEditor() {
  const ta = document.getElementById('text-editor');
  if (!ta || selected < 0) return;
  const z = spec.zony[selected];
  if (!z || z.typ !== 'text') return;
  const r = zoneRectPx(z);
  Object.assign(ta.style, styleRect(r));
  ta.style.fontFamily = z.pismo === 'Brnos Aires' ? "'Brnos Aires', serif" : "'Nunito', sans-serif";
  ta.style.fontSize = `${z.velkost * dielikPx()}px`;
  ta.style.lineHeight = String(z.riadkovanie);
  ta.style.textAlign = z.zarovnanie === 'na stred' ? 'center' : (z.zarovnanie === 'vpravo' ? 'right' : 'left');
}

function closeEditor() {
  const ta = document.getElementById('text-editor');
  if (!ta) {
    editorOpen = false;
    return;
  }
  if (selected >= 0 && spec.zony[selected]) {
    const z = spec.zony[selected];
    if (z.typ === 'text' && !z.text) {
      // Nothing was written: the zone goes back to being empty.
      z.typ = 'prazdna';
      delete z.text; delete z.pismo; delete z.velkost;
      delete z.zarovnanie; delete z.riadkovanie;
    }
  }
  ta.remove();
  editorOpen = false;
  scheduleRender();
}

// ---------- top bar ----------

function syncBar() {
  const f = spec.format, g = spec.grid;
  $('#btn-format').textContent = `${f.sirka} × ${f.vyska} ${f.jednotka} · Grid ${g.stlpce} ▾`;
  const input = $('#variant-input');
  if (document.activeElement !== input) input.value = spec.variant;
}

function setVariant(value) {
  spec.variant = String(value);
  syncBar();
  scheduleRender();
}

function stepVariant(delta) {
  const n = parseInt(spec.variant, 10);
  setVariant(Number.isFinite(n) ? Math.max(1, n + delta) : 42);
}

$('#variant-prev').addEventListener('click', () => stepVariant(-1));
$('#variant-next').addEventListener('click', () => stepVariant(1));
$('#variant-random').addEventListener('click', () => setVariant(1 + Math.floor(Math.random() * 999)));
$('#variant-input').addEventListener('change', (e) => {
  setVariant(e.target.value.trim() || '1');
  e.target.blur();
});

// ---------- popovers ----------

const popovers = [];

function closePopovers() {
  for (const p of popovers) p.close();
}

function attachPopover(btn, buildContent) {
  const pop = document.createElement('div');
  pop.className = 'popover';
  pop.hidden = true;
  document.body.append(pop);
  const api = {
    close() {
      pop.hidden = true;
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    },
    toggle() {
      const willOpen = pop.hidden;
      closePopovers();
      if (willOpen) {
        buildContent(pop);
        pop.hidden = false;
        btn.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        // Align to the button, clamped to the viewport.
        const r = btn.getBoundingClientRect();
        pop.style.left = `${Math.min(r.left, window.innerWidth - pop.offsetWidth - 12)}px`;
      }
    },
    isOpen: () => !pop.hidden,
  };
  btn.addEventListener('click', () => api.toggle());
  popovers.push(api);
  return api;
}

document.addEventListener('pointerdown', (e) => {
  if (popovers.some((p) => p.isOpen()) && !e.target.closest('.popover')) closePopovers();
}, true);

function row(label, control) {
  const div = document.createElement('div');
  div.className = 'row';
  const l = document.createElement('label');
  l.textContent = label;
  div.append(l, control);
  return div;
}

function numberInput(value, attrs, onInput) {
  const input = document.createElement('input');
  input.type = 'number';
  for (const [k, v] of Object.entries(attrs)) input.setAttribute(k, String(v));
  input.value = String(value);
  input.addEventListener('input', () => {
    const n = Number(input.value);
    if (Number.isFinite(n)) { onInput(n); scheduleRender(); }
  });
  return input;
}

function selectInput(options, value, onInput) {
  const select = document.createElement('select');
  for (const [val, name] of options) {
    const option = document.createElement('option');
    option.value = val;
    option.textContent = name;
    select.append(option);
  }
  select.value = value;
  select.addEventListener('input', () => { onInput(select.value); scheduleRender(); });
  return select;
}

function sliderRow(label, value, onInput) {
  const div = document.createElement('div');
  div.className = 'row';
  const wrap = document.createElement('div');
  wrap.className = 'grow';
  const range = document.createElement('input');
  range.type = 'range';
  range.min = '0';
  range.max = '100';
  range.step = '1';
  range.value = String(value);
  const num = document.createElement('span');
  num.className = 'num';
  num.textContent = String(value);
  range.addEventListener('input', () => {
    num.textContent = range.value;
    onInput(Number(range.value));
    scheduleRender();
  });
  const l = document.createElement('label');
  l.textContent = label;
  div.append(l, wrap);
  wrap.append(range, num);
  return div;
}

// ----- format popover -----

attachPopover($('#btn-format'), (pop) => {
  const f = spec.format, g = spec.grid;

  const presets = document.createElement('div');
  presets.className = 'presets';
  for (const name of Object.keys(FORMAT_PRESETS)) {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = name;
    b.addEventListener('click', () => {
      Object.assign(spec.format, FORMAT_PRESETS[name]);
      closePopovers();
      scheduleRender();
    });
    presets.append(b);
  }

  const h3a = document.createElement('h3');
  h3a.textContent = 'Formát';
  const h3b = document.createElement('h3');
  h3b.textContent = 'Mriežka';

  const sizeWrap = document.createElement('div');
  sizeWrap.className = 'grow';
  sizeWrap.append(
    numberInput(f.sirka, { min: 10, max: 20000, step: 1 }, (v) => { spec.format.sirka = v; }),
    Object.assign(document.createElement('span'), { textContent: '×' }),
    numberInput(f.vyska, { min: 10, max: 20000, step: 1 }, (v) => { spec.format.vyska = v; }),
    selectInput([['mm', 'mm'], ['px', 'px']], f.jednotka, (v) => { spec.format.jednotka = v; }),
  );

  pop.replaceChildren(
    h3a,
    row('Predvoľba', presets),
    row('Rozmer', sizeWrap),
    row('DPI', numberInput(f.dpi, { min: 18, max: 2400, step: 1 }, (v) => { spec.format.dpi = v; })),
    row('Spadávka', numberInput(f.spadavka, { min: 0, max: 50, step: 0.5 }, (v) => { spec.format.spadavka = v; })),
    h3b,
    row('Grid', numberInput(g.stlpce, { min: 1, max: 100, step: 1 }, (v) => { spec.grid.stlpce = v; })),
    row('Zvyšok výšky', selectInput(
      [['okraje', 'okraje'], ['natiahnutie', 'natiahnutie'], ['orez', 'presah a orez']],
      g.zvysok, (v) => { spec.grid.zvysok = v; })),
  );

  const actions = document.createElement('div');
  actions.className = 'actions';
  const loadBtn = document.createElement('button');
  loadBtn.type = 'button';
  loadBtn.textContent = 'Načítať predvoľbu';
  loadBtn.addEventListener('click', () => $('#predvolba-file').click());
  const saveBtn = document.createElement('button');
  saveBtn.type = 'button';
  saveBtn.textContent = 'Uložiť predvoľbu';
  saveBtn.addEventListener('click', savePredvolba);
  actions.append(loadBtn, saveBtn);
  pop.append(actions);
});

function savePredvolba() {
  // A preset is the spec without the variant and without the zones.
  const { variant, zony, ...rest } = spec;
  download(
    new Blob([JSON.stringify(rest, null, 2)], { type: 'application/json' }),
    'predvolba-generator.json',
  );
  closePopovers();
}

$('#predvolba-file').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  e.target.value = '';
  if (!file) return;
  try {
    const loaded = JSON.parse(await file.text());
    spec = engine.normalizujSpec({
      ...loaded,
      variant: spec.variant, // a preset never touches the variant
      zony: spec.zony,       // ...nor the zones
    });
    selected = -1;
    closePopovers();
    render();
  } catch (err) {
    toast(`Predvoľbu sa nepodarilo načítať: ${err.message}`);
  }
});

// ----- parametre popover -----

attachPopover($('#btn-parametre'), (pop) => {
  const k = spec.kresba, c = spec.kompozicia;

  const invLabel = document.createElement('label');
  invLabel.style.cssText = 'display:flex;gap:8px;align-items:center;cursor:pointer';
  const invBox = document.createElement('input');
  invBox.type = 'checkbox';
  invBox.checked = spec.inverzia;
  invBox.addEventListener('change', () => {
    spec.inverzia = invBox.checked;
    scheduleRender();
  });
  invLabel.append(invBox, 'Inverzia (biele na čiernom)');

  const sizeWrap = document.createElement('div');
  sizeWrap.className = 'grow';
  sizeWrap.append(
    numberInput(c.velkost[0], { min: 0.2, max: 40, step: 0.5 }, (v) => {
      c.velkost[0] = v;
      if (c.velkost[1] < v) c.velkost[1] = v;
    }),
    Object.assign(document.createElement('span'), { textContent: '–' }),
    numberInput(c.velkost[1], { min: 0.2, max: 40, step: 0.5 }, (v) => {
      c.velkost[1] = v;
      if (c.velkost[0] > v) c.velkost[0] = v;
    }),
    Object.assign(document.createElement('span'), { textContent: 'dielikov' }),
  );

  const chainWrap = document.createElement('div');
  chainWrap.className = 'grow';
  chainWrap.append(
    numberInput(c.retazenieDlzka[0], { min: 1, max: 50, step: 1 }, (v) => {
      c.retazenieDlzka[0] = v;
      if (c.retazenieDlzka[1] < v) c.retazenieDlzka[1] = v;
    }),
    Object.assign(document.createElement('span'), { textContent: '–' }),
    numberInput(c.retazenieDlzka[1], { min: 1, max: 50, step: 1 }, (v) => {
      c.retazenieDlzka[1] = v;
      if (c.retazenieDlzka[0] > v) c.retazenieDlzka[0] = v;
    }),
    Object.assign(document.createElement('span'), { textContent: 'tvarov' }),
  );

  const typesGrid = document.createElement('div');
  typesGrid.className = 'types';
  for (const t of TYPES) {
    const l = document.createElement('label');
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.checked = c.typy.includes(t.id);
    box.addEventListener('change', () => {
      if (box.checked && !c.typy.includes(t.id)) c.typy.push(t.id);
      if (!box.checked) c.typy = c.typy.filter((x) => x !== t.id);
      scheduleRender();
    });
    l.append(box, t.name);
    typesGrid.append(l);
  }

  const note = document.createElement('p');
  note.className = 'note';
  note.textContent = 'Dlaždice zatiaľ fungujú ako voľné rozmiestnenie.';

  const mkH = (text) => {
    const h = document.createElement('h3');
    h.textContent = text;
    return h;
  };

  pop.replaceChildren(
    mkH('Kresba'),
    sliderRow('Weight', k.weight, (v) => { spec.kresba.weight = v; }),
    sliderRow('Contrast', k.contrast, (v) => { spec.kresba.contrast = v; }),
    sliderRow('Zaoblenie', k.zaoblenie, (v) => { spec.kresba.zaoblenie = v; }),
    row('Farby', invLabel),
    mkH('Kompozícia'),
    row('Veľkosť', sizeWrap),
    sliderRow('Variácia', c.variacia, (v) => { spec.kompozicia.variacia = v; }),
    sliderRow('Reťazenie', c.retazenie, (v) => { spec.kompozicia.retazenie = v; }),
    row('Dĺžka reťaze', chainWrap),
    row('Rozloženie', selectInput(ROZLOZENIE, c.rozlozenie, (v) => { spec.kompozicia.rozlozenie = v; })),
    row('Rozmiestnenie', selectInput(
      [['volne', 'voľné'], ['dlazdice', 'dlaždice']],
      c.rozmiestnenie, (v) => { spec.kompozicia.rozmiestnenie = v; })),
    note,
    mkH('Typy'),
    typesGrid,
  );
});

// ----- export popover -----

const exportPopover = attachPopover($('#btn-export'), (pop) => {
  const { sirkaPx, vyskaPx } = rasterDimensions(spec);
  const mkH = (text) => Object.assign(document.createElement('h3'), { textContent: text });
  const button = (text, fn) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = text;
    b.addEventListener('click', async () => {
      try {
        await fn();
      } catch (err) {
        toast(`Export sa nepodaril: ${err.message}`);
      }
    });
    return b;
  };

  const svgNote = document.createElement('p');
  svgNote.className = 'note';
  svgNote.textContent = 'Text v SVG zostáva upraviteľný, v krivkách bude neskôr.';

  const pngDims = document.createElement('span');
  pngDims.className = 'note';
  pngDims.textContent = `${sirkaPx} × ${vyskaPx} px`;

  const wrap = document.createElement('div');
  wrap.className = 'presets';
  wrap.append(
    button('Stiahnuť SVG', () => exportSvgFile(spec)),
    button('Stiahnuť PNG', () => exportPngFile(spec)),
  );
  const avifWrap = document.createElement('div');
  avifWrap.className = 'presets';

  pop.replaceChildren(
    mkH('Export'),
    wrap,
    pngDims,
    svgNote,
    avifWrap,
  );

  avifSupported().then((ok) => {
    if (ok) {
      avifWrap.append(button('Stiahnuť AVIF', () => exportAvifFile(spec)));
    }
  });
});

// ---------- zoom ----------

const zoomSelect = $('#zoom');

function fitZoomPct() {
  const vb = svgHost.querySelector('svg')?.viewBox.baseVal;
  if (!vb) return 75;
  const f = spec.format, g = spec.grid;
  const dielikUnits = f.sirka / g.stlpce;
  const unitPx = f.jednotka === 'mm' ? MM_TO_PX : 1;
  const w100 = vb.width * dielikUnits * unitPx;
  const h100 = vb.height * dielikUnits * unitPx;
  const stage = $('#stage');
  const pct = Math.min(
    (stage.clientWidth - 80) / w100,
    (stage.clientHeight - 80) / h100,
  ) * 100;
  return clamp(Math.round(pct), 10, 300);
}

function setZoomOptions() {
  zoomSelect.replaceChildren();
  for (const step of ZOOM_STEPS) {
    const option = document.createElement('option');
    option.value = String(step);
    option.textContent = `${step} %`;
    zoomSelect.append(option);
  }
  const fit = document.createElement('option');
  fit.value = 'fit';
  fit.textContent = 'Prispôsobiť';
  zoomSelect.append(fit);
}

function applyZoom(value) {
  if (value === 'fit') {
    zoomPct = fitZoomPct();
    // Show the computed percentage in the fit option label.
    zoomSelect.querySelector('option[value="fit"]').textContent = `Prispôsobiť (${zoomPct} %)`;
  } else {
    zoomPct = Number(value);
    zoomSelect.querySelector('option[value="fit"]').textContent = 'Prispôsobiť';
  }
  render();
}

zoomSelect.addEventListener('change', () => applyZoom(zoomSelect.value));

// ---------- toast ----------

let toastTimer = 0;
function toast(message, ms = 3200) {
  const el = $('#toast');
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, ms);
}

// ---------- keyboard shortcuts ----------

const viewer = createViewer(spec.kresba);

function isTypingTarget(e) {
  return e.target.closest('input, textarea, select, [contenteditable="true"], #zone-bar');
}

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (viewer.isOpen()) { viewer.close(); return; }
    if (editorOpen) { closeEditor(); return; }
    if (popovers.some((p) => p.isOpen())) { closePopovers(); return; }
    if (selected >= 0) { selected = -1; photoPan = false; drawOverlay(); }
    return;
  }
  if (viewer.isOpen() || isTypingTarget(e) || e.metaKey || e.ctrlKey || e.altKey) return;

  switch (e.key) {
    case 'ArrowLeft': stepVariant(-1); e.preventDefault(); break;
    case 'ArrowRight': stepVariant(1); e.preventDefault(); break;
    case 'r': case 'R': setVariant(1 + Math.floor(Math.random() * 999)); break;
    case 'i': case 'I':
      spec.inverzia = !spec.inverzia;
      scheduleRender();
      break;
    case 'e': case 'E':
      exportPopover.toggle();
      break;
    case 't': case 'T':
      viewer.toggle();
      break;
    case 'Delete': case 'Backspace':
      if (selected >= 0) { deleteZone(selected); e.preventDefault(); }
      break;
    default:
      // Typing over an empty zone turns it into a text zone.
      if (e.key.length === 1 || e.key === 'Enter') {
        if (selected >= 0 && spec.zony[selected]?.typ === 'prazdna') {
          e.preventDefault();
          zoneToText(selected, e.key);
        }
      }
  }
});

// ---------- boot ----------

if (engine.isStubEngine) $('#stub-note').hidden = false;

setZoomOptions();
render(); // first paint, so fitZoomPct has a sheet to measure
zoomSelect.value = 'fit';
applyZoom('fit');
