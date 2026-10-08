// Registry of all shape types, in specimen-sheet order.

import * as noha from './noha.js';
import * as oblouk from './oblouk.js';
import * as obloukPata from './obloukPata.js';
import * as stvrtoblouk from './stvrtoblouk.js';
import * as polkruh from './polkruh.js';
import * as stvrtkruh from './stvrtkruh.js';
import * as kvapka from './kvapka.js';
import * as kruh from './kruh.js';
import * as bod from './bod.js';

export const SHAPES = [
  noha, oblouk, obloukPata, stvrtoblouk, polkruh, stvrtkruh,
  kvapka, kruh, bod,
];

export function findShape(id) {
  return SHAPES.find((s) => s.id === id) || null;
}
