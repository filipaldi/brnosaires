// Shape viewer (shortcut T): a full-window debugging tool for shapes and
// proporcie.json. Selected type large, sliders for Weight / Contrast /
// Zaoblenie and the type's own params, and a strip of all types at the
// current axes. Changes here are exploratory only — nothing flows back
// into the poster spec.

import { buildShape, paramSpec, defaultParams, TYPES, computeAxes, proporcie } from '../core/index.js';
import { renderShapeSvg, renderShapeSvgFallback } from './engine.js';

function draw(shape, opts) {
  return (renderShapeSvg || renderShapeSvgFallback)(shape, opts);
}

function sliderStep(min, max) {
  const span = max - min;
  if (span <= 2) return 0.05;
  if (span <= 10) return 0.1;
  return 1;
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'class') node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) node.append(child);
  return node;
}

export function createViewer(initialAxes) {
  const root = document.getElementById('viewer');
  const preview = document.getElementById('viewer-preview');
  const axesHost = document.getElementById('viewer-axes');
  const paramsHost = document.getElementById('viewer-params');
  const strip = document.getElementById('viewer-strip');

  const state = {
    typ: TYPES[0].id,
    axes: { ...initialAxes },
    params: defaultParams(TYPES[0].id),
  };

  function currentAxes() {
    return computeAxes(state.axes.weight, state.axes.contrast, proporcie, state.axes.zaoblenie);
  }

  function sliderRow(label, min, max, step, value, onInput) {
    const num = el('span', { class: 'num' });
    num.textContent = String(value);
    const range = el('input', { type: 'range', min: String(min), max: String(max), step: String(step) });
    range.value = String(value);
    range.addEventListener('input', () => {
      num.textContent = range.value;
      onInput(Number(range.value));
      refreshPreview();
      refreshStrip();
    });
    return el('div', { class: 'slider-row' }, el('label', {}, label), range, num);
  }

  function enumRow(label, values, value, onChange) {
    const select = el('select');
    for (const v of values) {
      const option = el('option', { value: v }, v);
      select.append(option);
    }
    select.value = value;
    select.addEventListener('change', () => {
      onChange(select.value);
      refreshPreview();
    });
    return el('div', { class: 'enum-row' }, el('label', {}, label), select);
  }

  function buildAxesPanel() {
    axesHost.replaceChildren(
      el('h3', {}, 'Osi'),
      sliderRow('Weight', 0, 100, 1, state.axes.weight,
        (v) => { state.axes.weight = v; }),
      sliderRow('Contrast', 0, 100, 1, state.axes.contrast,
        (v) => { state.axes.contrast = v; }),
      sliderRow('Zaoblenie', 0, 100, 1, state.axes.zaoblenie,
        (v) => { state.axes.zaoblenie = v; }),
    );
  }

  function buildParamsPanel() {
    const spec = paramSpec(state.typ);
    const children = [el('h3', {}, 'Parametre typu')];
    for (const [key, s] of Object.entries(spec)) {
      if (s.type === 'enum') {
        children.push(enumRow(s.label, s.values, state.params[key],
          (v) => { state.params[key] = v; }));
      } else {
        children.push(sliderRow(s.label, s.min, s.max, sliderStep(s.min, s.max),
          state.params[key], (v) => { state.params[key] = v; }));
      }
    }
    paramsHost.replaceChildren(...children);
  }

  function refreshPreview() {
    const shape = buildShape(state.typ, { ...state.params }, currentAxes());
    preview.replaceChildren();
    preview.insertAdjacentHTML('afterbegin', draw(shape, { pxPerDielik: 90, margin: 0.5 }));
  }

  function refreshStrip() {
    const cards = TYPES.map((t) => {
      const shape = buildShape(t.id, { ...defaultParams(t.id) }, currentAxes());
      const card = el('button', { class: 'type-card' + (t.id === state.typ ? ' sel' : ''), type: 'button' });
      card.insertAdjacentHTML('afterbegin', draw(shape, { pxPerDielik: 26, margin: 0.15 }));
      card.append(el('span', { class: 'name' }, t.name));
      card.addEventListener('click', () => {
        state.typ = t.id;
        state.params = defaultParams(t.id);
        buildParamsPanel();
        refreshPreview();
        refreshStrip();
      });
      return card;
    });
    strip.replaceChildren(...cards);
  }

  function open() {
    buildAxesPanel();
    buildParamsPanel();
    refreshPreview();
    refreshStrip();
    root.hidden = false;
  }

  function close() {
    root.hidden = true;
  }

  function toggle() {
    if (root.hidden) open();
    else close();
  }

  document.getElementById('viewer-close').addEventListener('click', close);

  return { open, close, toggle, isOpen: () => !root.hidden };
}
