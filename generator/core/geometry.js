// Geometry foundation: vectors, path model, Bézier arcs, tangents, corner fillets.
// All coordinates are in dielik units, origin top-left, y axis points down.

export function sub(a, b) { return { x: a.x - b.x, y: a.y - b.y }; }
export function add(a, b) { return { x: a.x + b.x, y: a.y + b.y }; }
export function mul(a, k) { return { x: a.x * k, y: a.y * k }; }
export function len(a) { return Math.hypot(a.x, a.y); }
export function norm(a) { const l = len(a) || 1; return { x: a.x / l, y: a.y / l }; }
export function dot(a, b) { return a.x * b.x + a.y * b.y; }
export function cross(a, b) { return a.x * b.y - a.y * b.x; }
export function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }
export function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
export function rotCw(v) { return { x: -v.y, y: v.x }; } // 90° clockwise on screen (y down)

// --- Path model ------------------------------------------------------------
// A subpath is an array of segments:
//   { c: 'M' | 'L', x, y }
//   { c: 'C', x1, y1, x2, y2, x, y }
//   { c: 'Z' }
// Segments are transformed point-wise, so transforms never touch path syntax.

export function moveTo(x, y) { return { c: 'M', x, y }; }
export function lineTo(x, y) { return { c: 'L', x, y }; }
export function curveTo(x1, y1, x2, y2, x, y) {
  return { c: 'C', x1, y1, x2, y2, x, y };
}
export function closePath() { return { c: 'Z' }; }

// Every coordinate a segment carries (Bézier controls included).
export function segPoints(seg) {
  if (seg.c === 'C') {
    return [{ x: seg.x1, y: seg.y1 }, { x: seg.x2, y: seg.y2 }, { x: seg.x, y: seg.y }];
  }
  if (seg.c === 'M' || seg.c === 'L') return [{ x: seg.x, y: seg.y }];
  return [];
}

export function subpathPoints(segs) {
  const pts = [];
  for (const s of segs) pts.push(...segPoints(s));
  return pts;
}

// Bounding box over all segment points (control hull bounds the curves).
export function bboxOfPoints(pts) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of pts) {
    if (p.x < minX) minX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x;
    if (p.y > maxY) maxY = p.y;
  }
  if (!Number.isFinite(minX)) return { x: 0, y: 0, w: 0, h: 0 };
  return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

// Shoelace over the polyline through segment endpoints (curve chords).
// Positive = clockwise on screen (y down). Good enough for winding decisions.
export function signedArea(segs) {
  const pts = [];
  for (const s of segs) {
    if (s.c === 'M' || s.c === 'L' || s.c === 'C') pts.push({ x: s.x, y: s.y });
  }
  let a = 0;
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    const q = pts[(i + 1) % pts.length];
    a += p.x * q.y - q.x * p.y;
  }
  return a / 2;
}

// Reverse a closed subpath (keeps geometry, flips winding).
export function reverseSubpath(segs) {
  const items = []; // { from, to, c1?, c2? } per drawn segment
  let cur = null;
  for (const s of segs) {
    if (s.c === 'M' || s.c === 'L' || s.c === 'C') {
      const to = { x: s.x, y: s.y };
      if (cur) {
        if (s.c === 'L') items.push({ from: cur, to });
        else if (s.c === 'C') {
          items.push({ from: cur, to, c1: { x: s.x1, y: s.y1 }, c2: { x: s.x2, y: s.y2 } });
        }
      }
      cur = to;
    }
  }
  const out = [moveTo(cur.x, cur.y)];
  for (let i = items.length - 1; i >= 0; i--) {
    const it = items[i];
    if (it.c1) {
      out.push(curveTo(it.c2.x, it.c2.y, it.c1.x, it.c1.y, it.from.x, it.from.y));
    } else {
      out.push(lineTo(it.from.x, it.from.y));
    }
  }
  out.push(closePath());
  return out;
}

// --- Number formatting (deterministic output) ------------------------------

export function fmt(n) {
  const r = Math.round(n * 1e4) / 1e4;
  return Object.is(r, -0) ? '0' : String(r);
}

export function serializeSubpath(segs) {
  const parts = [];
  for (const s of segs) {
    if (s.c === 'M' || s.c === 'L') parts.push(`${s.c} ${fmt(s.x)} ${fmt(s.y)}`);
    else if (s.c === 'C') {
      parts.push(`C ${fmt(s.x1)} ${fmt(s.y1)} ${fmt(s.x2)} ${fmt(s.y2)} ${fmt(s.x)} ${fmt(s.y)}`);
    } else parts.push('Z');
  }
  return parts.join(' ');
}

// --- Ellipse arcs as cubic Béziers -----------------------------------------
// Angles in radians, screen convention: atan2(dy, dx), 0 = +x, +π/2 = down.
// The arc runs from a0 to a1 linearly; a1 < a0 sweeps the other way.
export function arcPoint(cx, cy, rx, ry, a) {
  return { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a) };
}

export function appendArc(segs, cx, cy, rx, ry, a0, a1) {
  const total = a1 - a0;
  if (Math.abs(total) < 1e-9) return;
  const n = Math.max(1, Math.ceil(Math.abs(total) / (Math.PI / 2 + 1e-6)));
  const step = total / n;
  const k = (4 / 3) * Math.tan(step / 4);
  for (let i = 0; i < n; i++) {
    const t0 = a0 + i * step;
    const t1 = t0 + step;
    const p0 = arcPoint(cx, cy, rx, ry, t0);
    const p1 = arcPoint(cx, cy, rx, ry, t1);
    // tangent direction (derivative wrt angle), scaled by k
    const g0x = -rx * Math.sin(t0) * k, g0y = ry * Math.cos(t0) * k;
    const g1x = -rx * Math.sin(t1) * k, g1y = ry * Math.cos(t1) * k;
    if (i === 0) segs.push(lineTo(p0.x, p0.y));
    segs.push(curveTo(p0.x + g0x, p0.y + g0y, p1.x - g1x, p1.y - g1y, p1.x, p1.y));
  }
}

export function circleSegments(cx, cy, r) {
  const segs = [moveTo(cx + r, cy)];
  appendArc(segs, cx, cy, r, r, 0, Math.PI / 2);
  appendArc(segs, cx, cy, r, r, Math.PI / 2, Math.PI);
  appendArc(segs, cx, cy, r, r, Math.PI, Math.PI * 1.5);
  appendArc(segs, cx, cy, r, r, Math.PI * 1.5, Math.PI * 2);
  segs.push(closePath());
  return segs;
}

// --- Tangents from an external point to a circle ---------------------------

export function ensureExternal(p, c, r, factor = 1.05) {
  const d = dist(p, c);
  const min = r * factor;
  if (d >= min) return { x: p.x, y: p.y };
  const u = d > 1e-9 ? { x: (p.x - c.x) / d, y: (p.y - c.y) / d } : { x: -1, y: 0 };
  return { x: c.x + u.x * min, y: c.y + u.y * min };
}

// Both tangent points on circle (c, r) seen from external point p.
export function tangentPoints(p, c, r) {
  const d = dist(p, c);
  const back = Math.atan2(p.y - c.y, p.x - c.x); // direction c -> p
  const alpha = Math.acos(clamp(r / d, -1, 1));
  return [
    { x: c.x + r * Math.cos(back + alpha), y: c.y + r * Math.sin(back + alpha), a: back + alpha },
    { x: c.x + r * Math.cos(back - alpha), y: c.y + r * Math.sin(back - alpha), a: back - alpha },
  ];
}

// --- Corner fillets --------------------------------------------------------

// Round corner b (between edges a->b and b->c) with radius r.
// Returns { p1, p2, c1, c2 } where p1/p2 are the fillet endpoints and
// c1/c2 the Bézier controls of the replacement arc, or null when not possible.
export function fillet(a, b, c, r) {
  const u = norm(sub(b, a));
  const v = norm(sub(c, b));
  const cosT = clamp(dot(u, v), -1, 1);
  const theta = Math.acos(cosT);
  if (!(r > 0) || theta < 1e-4 || Math.abs(cross(u, v)) < 1e-9) return null;
  // clamp the radius so the fillet still fits on both adjacent edges
  const e1 = dist(a, b), e2 = dist(b, c);
  const maxR = Math.min(e1, e2) * 0.49 * Math.tan(theta / 2);
  const rr = Math.min(r, maxR);
  if (rr <= 1e-9) return null;
  const sgn = Math.sign(cross(u, v));
  const t = rr / Math.tan(theta / 2);
  const p1 = { x: b.x - u.x * t, y: b.y - u.y * t };
  const p2 = { x: b.x + v.x * t, y: b.y + v.y * t };
  const kk = (4 / 3) * Math.tan(theta / 4) * rr;
  const c1 = { x: p1.x + u.x * kk, y: p1.y + u.y * kk };
  const c2 = { x: p2.x - v.x * kk, y: p2.y - v.y * kk };
  return { p1, p2, c1, c2, r: rr };
}

// Closed polygon with per-vertex corner radii (0 = sharp).
// pts: [{x,y}...], radii: [number...] of the same length.
export function roundedPolygon(pts, radii) {
  const n = pts.length;
  const f = [];
  for (let i = 0; i < n; i++) {
    const prev = pts[(i - 1 + n) % n];
    const next = pts[(i + 1) % n];
    f.push(fillet(prev, pts[i], next, radii[i] || 0));
  }
  const segs = [];
  const start = f[0] ? f[0].p2 : pts[0];
  segs.push(moveTo(start.x, start.y));
  for (let i = 1; i < n; i++) {
    if (f[i]) {
      segs.push(lineTo(f[i].p1.x, f[i].p1.y));
      segs.push(curveTo(f[i].c1.x, f[i].c1.y, f[i].c2.x, f[i].c2.y, f[i].p2.x, f[i].p2.y));
    } else {
      segs.push(lineTo(pts[i].x, pts[i].y));
    }
  }
  if (f[0]) {
    segs.push(lineTo(f[0].p1.x, f[0].p1.y));
    segs.push(curveTo(f[0].c1.x, f[0].c1.y, f[0].c2.x, f[0].c2.y, f[0].p2.x, f[0].p2.y));
  }
  segs.push(closePath());
  return segs;
}

// Rectangle with per-corner radii [tl, tr, br, bl].
export function roundedRect(x, y, w, h, radii) {
  const [tl, tr, br, bl] = radii.map((r) => clamp(r, 0, Math.min(w, h) / 2));
  return roundedPolygon(
    [
      { x, y },
      { x: x + w, y },
      { x: x + w, y: y + h },
      { x, y: y + h },
    ],
    [tl, tr, br, bl],
  );
}
