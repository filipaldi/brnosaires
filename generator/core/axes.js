// Axes: Weight and Contrast (both 0–100 %) resolve to the two stroke
// thicknesses everything else is derived from. Units are dieliks.
//
//   heavy = wMin + (wMax - wMin) · W/100        thickness of the solid mass
//   hair  = heavy - (heavy - hairMin) · C/100   hairline relative to heavy
//
// Contrast 0 is monoline (hair === heavy), 100 the thinnest hairline.
//
// Zaoblenie (0–100 %) is the global corner rounding: every free corner of
// every shape is rounded by this fraction of half its stroke thickness.

import { readFileSync } from 'node:fs';
import { ValidationError } from './errors.js';

export function loadProporcie() {
  const url = new URL('../proporcie.json', import.meta.url);
  return JSON.parse(readFileSync(url, 'utf8'));
}

export function validateAxis(name, value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ValidationError(`${name} musí byť číslo 0–100 (dostal som „${value}“).`);
  }
  if (value < 0 || value > 100) {
    throw new ValidationError(`${name} musí byť v rozsahu 0–100 (dostal som ${value}).`);
  }
  return value;
}

export function computeAxes(weight, contrast, proporcie, zaoblenie = proporcie.osi.zaoblenie) {
  validateAxis('Weight', weight);
  validateAxis('Contrast', contrast);
  validateAxis('Zaoblenie', zaoblenie);
  const { wMin, wMax, hairMin } = proporcie.osi;
  const heavy = wMin + (wMax - wMin) * (weight / 100);
  const hair = heavy - (heavy - hairMin) * (contrast / 100);
  return { weight, contrast, heavy, hair, zaoblenie: zaoblenie / 100 };
}
