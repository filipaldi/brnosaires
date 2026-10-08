// bod — a filled circle. Default diameter is derived (1.2 · heavy) when the
// parameter is left out (null).

import { circleSegments } from '../geometry.js';

export const id = 'bod';
export const name = 'Bod';

export const params = {
  priemer: {
    label: 'priemer (null = 1,2 · heavy)',
    type: 'number', min: 0.01, max: 20, nullable: true,
  },
};

export function build(p, axes) {
  const d = p.priemer ?? axes.heavy * 1.2;
  return {
    subpaths: [{ segs: circleSegments(d / 2, d / 2, d / 2) }],
    joints: [],
  };
}
