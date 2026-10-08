// Deterministic randomness: the variant string seeds everything. The same
// variant always draws the same sequence, Math.random is never used.

// FNV-1a, 32-bit — small, stable across platforms, good enough for a seed.
export function hashString(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function createRng(variant) {
  return mulberry32(hashString(String(variant)));
}

// Integer 0..n-1, float in [lo, hi], item of an array.
export function rngInt(rng, n) {
  return Math.min(n - 1, Math.floor(rng() * n));
}

export function rngRange(rng, lo, hi) {
  return lo + rng() * (hi - lo);
}

export function rngPick(rng, arr) {
  return arr[rngInt(rng, arr.length)];
}
