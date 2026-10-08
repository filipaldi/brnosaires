import test from 'node:test';
import assert from 'node:assert/strict';
import { prstenec, kvapka, obdlznik } from '../core/primitives/index.js';
import { subpathPoints } from '../core/geometry.js';

test('prstenec má stálu hrúbku', () => {
  const [ring] = prstenec({ cx: 0, cy: 0, R: 2, t: 0.3, start: 180, sweep: 180 });
  const radii = ring.segs.filter((s) => s.c !== 'Z').map((s) => Math.hypot(s.x, s.y));
  for (const r of radii) assert.ok(Math.abs(r - 2) < 1e-9 || Math.abs(r - 1.7) < 1e-9, `polomer ${r}`);
});

test('krk kvapky sa rovná hair a výška kvapke', () => {
  for (const n of [10, 17, 25, 40]) {
    const vyska = 1.6;
    const hair = (n * vyska) / 228;
    const k = kvapka({ x: 0, y: 0, hair, vyska });
    assert.ok(Math.abs(k.neck - hair) < 1e-6);
    // sample the curves: the drop spans exactly 0..vyska vertically
    let lo = Infinity, hi = -Infinity, py = 0;
    for (const s of k.segs) {
      if (s.c === 'C') {
        for (let i = 0; i <= 200; i++) {
          const t = i / 200, u = 1 - t;
          const y = u * u * u * py + 3 * u * u * t * s.y1 + 3 * u * t * t * s.y2 + t * t * t * s.y;
          lo = Math.min(lo, y); hi = Math.max(hi, y);
        }
      }
      if (s.c !== 'Z') { py = s.y; lo = Math.min(lo, s.y); hi = Math.max(hi, s.y); }
    }
    assert.ok(Math.abs(hi - lo - vyska) < 0.01 * vyska, `výška ${hi - lo}`);
  }
});

test('výrez v obdĺžniku nechá stred kruhu prázdny', () => {
  const o = obdlznik({ x: 0, y: 1, w: 2, h: 2, vyrez: { cx: 1, r: 0.8 } });
  const pts = subpathPoints(o.segs);
  assert.ok(pts.some((p) => Math.abs(p.x - 1) < 1e-9 && Math.abs(p.y - 1.8) < 1e-9));
});
