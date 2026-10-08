// Registry of all shape types, in specimen-sheet order.

import * as noha from './noha.js';
import * as oblouk from './oblouk.js';
import * as hmotaSoStrbinou from './hmotaSoStrbinou.js';
import * as hacikSKvapkou from './hacikSKvapkou.js';
import * as nota from './nota.js';
import * as kvapka from './kvapka.js';
import * as kruh from './kruh.js';
import * as bod from './bod.js';

export const SHAPES = [
  noha, oblouk, hmotaSoStrbinou, hacikSKvapkou,
  nota, kvapka, kruh, bod,
];

export function findShape(id) {
  return SHAPES.find((s) => s.id === id) || null;
}
