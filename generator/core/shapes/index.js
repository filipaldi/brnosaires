// Registry of all shape types, in specimen-sheet order.

import * as noha from './noha.js';
import * as stvrtoblouk from './stvrtoblouk.js';
import * as polkruh from './polkruh.js';
import * as stvrtkruh from './stvrtkruh.js';
import * as kvapka from './kvapka.js';
import * as kruh from './kruh.js';

export const SHAPES = [
  noha, stvrtoblouk, polkruh, stvrtkruh,
  kvapka, kruh,
];

export function findShape(id) {
  return SHAPES.find((s) => s.id === id) || null;
}
