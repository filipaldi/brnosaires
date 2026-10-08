// Axes: Weight → heavy, Contrast → hair. Monotonicity and limits.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { computeAxes, loadProporcie } from '../core/axes.js';

const prop = loadProporcie();

test('heavy rastie s Weight', () => {
  let prev = -Infinity;
  for (let w = 0; w <= 100; w += 5) {
    const { heavy } = computeAxes(w, 50, prop);
    assert.ok(heavy > prev, `heavy má rásť, pri W=${w} je ${heavy}`);
    prev = heavy;
  }
});

test('hair klesá s Contrast', () => {
  for (const w of [0, 37, 100]) {
    let prev = Infinity;
    for (let c = 0; c <= 100; c += 5) {
      const { hair } = computeAxes(w, c, prop);
      assert.ok(hair <= prev + 1e-12, `hair má klesať, pri W=${w} C=${c} je ${hair}`);
      prev = hair;
    }
  }
});

test('pri Contrast 0 je hair === heavy (monoline)', () => {
  for (const w of [0, 50, 100]) {
    const { heavy, hair } = computeAxes(w, 0, prop);
    assert.equal(hair, heavy);
  }
});

test('pri Contrast 100 sa hair blíži hairMin', () => {
  const { hair } = computeAxes(50, 100, prop);
  assert.ok(Math.abs(hair - prop.osi.hairMin) < 1e-12);
});

test('hodnoty mimo 0–100 hodia chybu so slovenským textom', () => {
  assert.throws(() => computeAxes(101, 0, prop), /Weight/);
  assert.throws(() => computeAxes(0, -1, prop), /Contrast/);
  assert.throws(() => computeAxes('veľa', 0, prop), /Weight/);
});
