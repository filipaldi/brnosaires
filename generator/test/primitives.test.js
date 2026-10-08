import test from 'node:test';
import assert from 'node:assert/strict';
import { prstenec, kvapka, obdlznik } from '../core/primitives/index.js';
import { subpathPoints } from '../core/geometry.js';

test('prstenec má stálu hrúbku', () => {
  const [ring] = prstenec({ cx: 0, cy: 0, R: 2, t: 0.3, start: 180, sweep: 180 });
  const radii = ring.segs.filter((s) => s.c !== 'Z').map((s) => Math.hypot(s.x, s.y));
  for (const r of radii) assert.ok(Math.abs(r - 2) < 1e-9 || Math.abs(r - 1.7) < 1e-9, `polomer ${r}`);
});

// Bounds of a segment list, sampling the cubic curves.
function rozsah(segs) {
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, px = 0, py = 0;
  const bod = (x, y) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); };
  for (const s of segs) {
    if (s.c === 'C') {
      for (let i = 0; i <= 200; i++) {
        const t = i / 200, u = 1 - t;
        bod(u * u * u * px + 3 * u * u * t * s.x1 + 3 * u * t * t * s.x2 + t * t * t * s.x,
          u * u * u * py + 3 * u * u * t * s.y1 + 3 * u * t * t * s.y2 + t * t * t * s.y);
      }
    }
    if (s.c !== 'Z') { px = s.x; py = s.y; bod(s.x, s.y); }
  }
  return { w: x1 - x0, h: y1 - y0 };
}

test('krk kvapky sa rovná hair a rohy interpolácie sú mastre', () => {
  const hair = 0.05;
  const k = 0.05 / 10; // the masters' neck is 10 units
  // [chvost, vyska] → master size in units (width, height of its outline)
  const rohy = [[0, 0, 150, 205], [1, 0, 300, 205], [0, 1, 149, 248], [1, 1, 300, 249]];
  for (const [c, v, w, h] of rohy) {
    const d = kvapka({ x: 0, y: 0, t: hair, chvost: c, vyska: v });
    assert.equal(d.neck, hair);
    const pts = subpathPoints(d.segs);
    assert.ok(pts.some((p) => Math.abs(p.x) < 1e-9 && Math.abs(p.y) < 1e-9), 'krk začína v (0, 0)');
    assert.ok(pts.some((p) => Math.abs(p.x) < 1e-9 && Math.abs(p.y - hair) < 1e-9), 'krk má hrúbku hair');
    const r = rozsah(d.segs);
    assert.ok(Math.abs(r.w - w * k) < 0.02 * w * k, `šírka ${r.w}`);
    assert.ok(Math.abs(r.h - h * k) < 0.03 * h * k, `výška ${r.h}`);
    // the thick-neck master: neck 40 units, still exactly t thick
    const hr = kvapka({ x: 0, y: 0, t: hair, chvost: c, vyska: v, krk: 1 });
    const hp = subpathPoints(hr.segs);
    assert.ok(hp.some((p) => Math.abs(p.x) < 1e-9 && Math.abs(p.y - hair) < 1e-9), 'hrubý krk má hrúbku t');
  }
});

test('výrez v obdĺžniku nechá stred kruhu prázdny', () => {
  const o = obdlznik({ x: 0, y: 1, w: 2, h: 2, vyrez: { cx: 1, r: 0.8 } });
  const pts = subpathPoints(o.segs);
  assert.ok(pts.some((p) => Math.abs(p.x - 1) < 1e-9 && Math.abs(p.y - 1.8) < 1e-9));
});
