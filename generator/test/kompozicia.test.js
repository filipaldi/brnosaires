// Composition: determinism, zone behaviour (prazdna / okraj), shapes inside
// the format, validation errors, no NaN in the SVG.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

import { normalizujSpec, komponuj } from '../core/kompozicia/index.js';
import { ValidationError } from '../core/errors.js';

const plagat = JSON.parse(readFileSync(new URL('../priklady/plagat-a2.json', import.meta.url), 'utf8'));
const nahlad = JSON.parse(readFileSync(new URL('../priklady/nahlad-akcie.json', import.meta.url), 'utf8'));

// rect helpers — zone rects and placed bboxes share the {x, y, w, h} shape
const prekryv = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
const vzdialenost = (a, b) => Math.max(
  b.x - (a.x + a.w), a.x - (b.x + b.w),
  b.y - (a.y + a.h), a.y - (b.y + b.h),
);

const EPS = 1e-6;

test('rovnaký spec dvakrát dáva bajtovo rovnaké SVG', () => {
  const a = komponuj(plagat);
  const b = komponuj(JSON.parse(JSON.stringify(plagat)));
  assert.equal(a.svg, b.svg);
  assert.deepEqual(a.tvary, b.tvary);
});

test('iný variant dáva iné SVG', () => {
  const a = komponuj(plagat);
  const b = komponuj({ ...plagat, variant: 'iný' });
  assert.notEqual(a.svg, b.svg);
});

test('nahlad v px bez zón beží a má vrstvy', () => {
  const { svg, sirkaPx, vyskaPx, tvary } = komponuj(nahlad);
  assert.ok(tvary.length > 0, 'žiadny tvar nebol umiestnený');
  assert.equal(sirkaPx, 1200);
  assert.equal(vyskaPx, 630);
  for (const id of ['fotky', 'pattern', 'text', 'spadavka']) {
    assert.ok(svg.includes(`id="${id}"`), `chýba vrstva ${id}`);
  }
});

test('žiadny tvar sa nedotýka zóny so správaním prazdna', () => {
  const { tvary } = komponuj(plagat);
  const zony = plagat.zony.filter((z) => z.spravanie === 'prazdna')
    .map((z) => ({ x: z.x, y: z.y, w: z.w, h: z.h }));
  assert.ok(zony.length > 0);
  for (const t of tvary) {
    for (const z of zony) {
      assert.ok(!prekryv(t.bbox, z), `tvar ${t.typ} ${JSON.stringify(t.bbox)} prekrýva zónu ${JSON.stringify(z)}`);
    }
  }
});

test('okraj drží jeden dielik bieleho okolo zóny', () => {
  const { tvary } = komponuj(plagat);
  const zony = plagat.zony.filter((z) => z.spravanie === 'okraj')
    .map((z) => ({ x: z.x, y: z.y, w: z.w, h: z.h }));
  assert.ok(zony.length > 0);
  for (const t of tvary) {
    for (const z of zony) {
      assert.ok(!prekryv(t.bbox, z), `tvar ${t.typ} prekrýva zónu s okrajom`);
      assert.ok(vzdialenost(t.bbox, z) >= 1 - EPS,
        `tvar ${t.typ} je bližšie ako 1 dielik: ${vzdialenost(t.bbox, z)}`);
    }
  }
});

test('všetky tvary sú vnútri orezaného formátu', () => {
  const { tvary } = komponuj(plagat);
  const W = plagat.grid.stlpce;
  const H = (plagat.format.vyska * W) / plagat.format.sirka;
  assert.ok(tvary.length > 0);
  for (const t of tvary) {
    assert.ok(t.bbox.x >= -EPS && t.bbox.y >= -EPS, `tvar ${t.typ} trčí hore/vľavo`);
    assert.ok(t.bbox.x + t.bbox.w <= W + EPS, `tvar ${t.typ} trčí vpravo`);
    assert.ok(t.bbox.y + t.bbox.h <= H + EPS, `tvar ${t.typ} trčí dole: ${JSON.stringify(t.bbox)} nad ${H}`);
  }
});

test('SVG neobsahuje NaN ani Infinity', () => {
  for (const spec of [plagat, nahlad, { ...plagat, inverzia: true }]) {
    const { svg } = komponuj(spec);
    assert.doesNotMatch(svg, /NaN|Infinity/);
  }
});

test('prázdna fotková zóna bez zdroja kreslí šedý placeholder', () => {
  const { svg } = komponuj(plagat);
  assert.match(svg, /id="fotky"/);
  assert.match(svg, /#e3e3e3/);
});

test('normalizujSpec doplní všetky predvolené polia', () => {
  const spec = normalizujSpec({});
  assert.equal(spec.format.sirka, 420);
  assert.equal(spec.grid.stlpce, 30);
  assert.equal(spec.kompozicia.rozlozenie, 'rovnomerne');
  assert.equal(spec.variant, '1');
  assert.deepEqual(spec.zony, []);
  assert.equal(typeof spec.kompozicia.typy[0], 'string');
});

test('rozmiestnenie dlazdice varuje a beží ako voľné', () => {
  const { varovania, svg } = komponuj({ ...nahlad, kompozicia: { ...nahlad.kompozicia, rozmiestnenie: 'dlazdice' } });
  assert.ok(varovania.some((v) => v.includes('dlazdice')));
  assert.ok(svg.includes('id="pattern"'));
});

test('neplatný spec skončí na ValidationError so slovenskou správou', () => {
  const pripady = [
    [{ format: { sirka: -1 } }, /sirka/],
    [{ format: { jednotka: 'cm' } }, /jednotka/],
    [{ grid: { stlpce: 1.5 } }, /stlpce/],
    [{ grid: { zvysok: 'hore' } }, /zvysok/],
    [{ kresba: { weight: 140 } }, /weight/],
    [{ kompozicia: { velkost: [6, 1] } }, /velkost/],
    [{ kompozicia: { typy: ['acky'] } }, /Neznámy typ/],
    [{ kompozicia: { typy: [] } }, /typy/],
    [{ variant: true }, /variant/],
    [{ inverzia: 'nie' }, /inverzia/],
    [{ zony: [{ typ: 'text', x: 1, y: 1, w: 99, h: 2 }] }, /presahuje šírku/],
    [{ zony: [{ typ: 'fotka', x: 1, y: 40, w: 2, h: 4 }] }, /presahuje výšku/],
    [{ zony: [{ typ: 'text', x: 0, y: 0, w: 2, h: 1, pismo: 'Comic Sans' }] }, /pismo/],
    [{ zony: [{ typ: 'fotka', x: 0, y: 0, w: 2, h: 1, rezim: 'vyrez' }] }, /rezim/],
    [{ neviem: 1 }, /Neznáme pole/],
  ];
  for (const [spec, rx] of pripady) {
    assert.throws(() => normalizujSpec(spec), (e) => {
      assert.ok(e instanceof ValidationError, `nie ValidationError pre ${JSON.stringify(spec)}`);
      assert.match(e.message, rx);
      return true;
    }, JSON.stringify(spec));
  }
});

test('tvary sa reťazia cez spoje rovnakej hrúbky', async () => {
  const { komponuj } = await import('../core/kompozicia/index.js');
  const spec = JSON.parse(readFileSync(new URL('../priklady/plagat-a2.json', import.meta.url), 'utf8'));
  const { tvary } = komponuj(spec);
  const spojene = tvary.filter((t) => t.spoje.length);
  assert.ok(spojene.length >= 2, 'aspoň jedna reťaz');
  const OPAK = { down: 'up', up: 'down', left: 'right', right: 'left' };
  for (const t of spojene) {
    for (const id of t.spoje) {
      const j = t.joints.find((q) => q.id === id);
      const partner = tvary.some((u) => u !== t && u.joints.some((q) => u.spoje.includes(q.id)
        && Math.hypot(q.x - j.x, q.y - j.y) < 1e-6 && Math.abs(q.t - j.t) < 1e-9 && OPAK[q.dir] === j.dir));
      assert.ok(partner, `spoj ${t.typ}.${id} má protikus`);
    }
  }
});

test('dĺžka reťaze [min, max] sa dá zadať a overuje sa', () => {
  const spec = JSON.parse(readFileSync(new URL('../priklady/plagat-a2.json', import.meta.url), 'utf8'));
  // [1, 1]: one shape per chain, joined only to the teardrops ending it
  const jeden = komponuj({ ...spec, kompozicia: { ...spec.kompozicia, retazenieDlzka: [1, 1] } });
  for (const t of jeden.tvary.filter((u) => u.typ !== 'kvapka')) {
    for (const id of t.spoje) {
      const j = t.joints.find((q) => q.id === id);
      const partner = jeden.tvary.find((u) => u !== t
        && u.joints.some((q) => Math.hypot(q.x - j.x, q.y - j.y) < 1e-6));
      assert.equal(partner?.typ, 'kvapka', `${t.typ}.${id} je napojený na ${partner?.typ}`);
    }
  }
  assert.throws(
    () => komponuj({ ...spec, kompozicia: { ...spec.kompozicia, retazenieDlzka: [5, 2] } }),
    /retazenieDlzka/);
});

test('každá čiara končí slzou: tvar reťaze má obsadené všetky spoje', () => {
  const { tvary } = komponuj({ variant: '7' });
  const reťaz = tvary.filter((t) => t.joints.length);
  assert.ok(reťaz.length > 0);
  for (const t of reťaz) {
    assert.equal(t.spoje.length, t.joints.length, `${t.typ} má voľný koniec`);
  }
});
