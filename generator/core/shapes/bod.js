// bod — a filled disc (a ring whose thickness equals its radius).

import { prstenec } from '../primitives/index.js';

export const id = 'bod';
export const name = 'Bod';

export const params = {
  priemer: { label: 'priemer', type: 'number', min: 0.01, max: 20, nullable: true },
};

export function build(p, axes, prop) {
  const d = p.priemer ?? axes.heavy * prop.proporcie.bod.priemer;
  const R = d / 2;
  return { subpaths: prstenec({ cx: R, cy: R, R, t: R }), joints: [] };
}
