// Every type builds cleanly across the whole Weight × Contrast grid, output
// is deterministic, transforms behave and joints land inside the bbox.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { TYPES, defaultParams, buildShape } from '../core/index.js';
import { computeAxes, loadProporcie } from '../core/axes.js';

const prop = loadProporcie();
const axesFor = (w, c) => computeAxes(w, c, prop);

test('každý typ sa postaví na celej mriežke Weight × Contrast', () => {
  for (const { id } of TYPES) {
    for (const w of [0, 50, 100]) {
      for (const c of [0, 50, 100]) {
        const shape = buildShape(id, defaultParams(id), axesFor(w, c));
        assert.ok(shape.paths.length >= 1, `${id} W${w} C${c}: žiadna cesta`);
        for (const d of shape.paths) {
          assert.ok(d.startsWith('M '), `${id} W${w} C${c}: cesta nezačína na M`);
          assert.ok(!/NaN|Infinity/.test(d), `${id} W${w} C${c}: ${d}`);
        }
        assert.ok(shape.bbox.w > 0, `${id} W${w} C${c}: bbox.w ${shape.bbox.w}`);
        assert.ok(shape.bbox.h > 0, `${id} W${w} C${c}: bbox.h ${shape.bbox.h}`);
      }
    }
  }
});

test('rovnaký vstup dáva bajtovo rovnaký výstup', () => {
  for (const { id } of TYPES) {
    for (const extra of [{}, { rotate: 90 }, { rotate: 180, mirror: true }, { mirror: true }]) {
      const params = { ...defaultParams(id), ...extra };
      const a = buildShape(id, params, axesFor(60, 70));
      const b = buildShape(id, params, axesFor(60, 70));
      assert.deepEqual(a, b, `${id} ${JSON.stringify(extra)} nie je deterministický`);
    }
  }
});

test('rotate 90 vymení šírku a výšku bbox', () => {
  for (const { id } of TYPES) {
    const a = buildShape(id, defaultParams(id), axesFor(60, 70));
    const b = buildShape(id, { ...defaultParams(id), rotate: 90 }, axesFor(60, 70));
    assert.ok(Math.abs(a.bbox.w - b.bbox.h) < 1e-6, `${id}: šírka ${a.bbox.w} vs výška ${b.bbox.h}`);
    assert.ok(Math.abs(a.bbox.h - b.bbox.w) < 1e-6, `${id}: výška ${a.bbox.h} vs šírka ${b.bbox.w}`);
  }
});

test('mirror zachová rozmery bbox', () => {
  for (const { id } of TYPES) {
    const a = buildShape(id, defaultParams(id), axesFor(60, 70));
    const b = buildShape(id, { ...defaultParams(id), mirror: true }, axesFor(60, 70));
    assert.ok(Math.abs(a.bbox.w - b.bbox.w) < 1e-9, id);
    assert.ok(Math.abs(a.bbox.h - b.bbox.h) < 1e-9, id);
  }
});

test('spoj sa nachádza v bboxe tvaru', () => {
  for (const { id } of TYPES) {
    for (const w of [0, 100]) {
      const s = buildShape(id, defaultParams(id), axesFor(w, 70));
      for (const j of s.joints) {
        assert.ok(j.x >= s.bbox.x - 1e-6 && j.x <= s.bbox.x + s.bbox.w + 1e-6, `${id}: joint x mimo`);
        assert.ok(j.y >= s.bbox.y - 1e-6 && j.y <= s.bbox.y + s.bbox.h + 1e-6, `${id}: joint y mimo`);
        assert.ok(['down', 'up', 'left', 'right'].includes(j.dir), `${id}: neznámy smer ${j.dir}`);
      }
    }
  }
});

test('parts zodpovedajú paths a každá má názov primitívy', () => {
  for (const { id } of TYPES) {
    const s = buildShape(id, defaultParams(id), axesFor(60, 70));
    assert.equal(s.parts.length, s.paths.length, `${id}: parts iná dĺžka ako paths`);
    assert.deepEqual(s.parts.map((p) => p.d), s.paths, `${id}: d v parts nesedí na paths`);
    for (const p of s.parts) {
      assert.equal(typeof p.part, 'string', `${id}: part nie je reťazec`);
      assert.equal(typeof p.hole, 'boolean', `${id}: hole nie je boolean`);
    }
  }
});

test('kruh má vonkajšiu aj vnútornú cestu', () => {
  const s = buildShape('kruh', defaultParams('kruh'), axesFor(60, 70));
  assert.equal(s.paths.length, 2);
});

test('nota má nohu, kvapky a zaoblené vnútorné rohy', () => {
  const s = buildShape('nota', defaultParams('nota'), axesFor(60, 70));
  // leg + 2 drops + 3 inner corners (the top drop has only the lower one)
  assert.equal(s.paths.length, 6);
});

test('defaultParams vracia nezávislú kópiu', () => {
  const a = defaultParams('noha');
  a.dlzka = 99;
  assert.equal(defaultParams('noha').dlzka, 3);
});

test('neznámy typ aj parameter hlásia chybu', () => {
  assert.throws(() => buildShape('nekonecko', {}, axesFor(50, 50)), /Neznámy typ/);
  assert.throws(() => buildShape('noha', { strasne: 1 }, axesFor(50, 50)), /Neznámy parameter/);
  assert.throws(() => buildShape('noha', { dlzka: 999 }, axesFor(50, 50)), /dlzka/);
});
