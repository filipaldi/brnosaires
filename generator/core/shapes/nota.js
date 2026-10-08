// nota — a vertical leg with teardrops hanging off one side like flags on a
// music-note stem. Each teardrop's tail attaches to the leg (rounded tip on
// the leg's edge) and the round part sits to the side and slightly below.

import { roundedRect } from '../geometry.js';
import { ValidationError } from '../errors.js';
import { teardropSubpath } from './teardrop.js';

export const id = 'nota';
export const name = 'Nota';

export const params = {
  dlzka: { label: 'dĺžka nohy', type: 'number', min: 0.2, max: 20 },
  pocet: { label: 'počet kvapiek', type: 'integer', min: 1, max: 8 },
  rozostup: { label: 'rozostup', type: 'number', min: 0.05, max: 10 },
  kvapka: { label: 'kvapka (násobok heavy)', type: 'number', min: 0.1, max: 5 },
  strana: { label: 'strana', type: 'enum', values: ['vpravo', 'vlavo'] },
  hrubka: { label: 'hrúbka nohy', type: 'enum', values: ['vlas', 'plna'] },
};

const DEG = Math.PI / 180;

export function build(p, axes, prop) {
  const pr = prop.proporcie.kvapka; // shared teardrop proportions
  const t = p.hrubka === 'vlas' ? axes.hair : axes.heavy;
  const r = p.kvapka * axes.heavy;
  const side = p.strana === 'vpravo' ? 1 : -1;

  const firstY = r * 0.4;
  const lastY = firstY + (p.pocet - 1) * p.rozostup;
  if (lastY + r > p.dlzka + 1e-6) {
    throw new ValidationError(
      'Nota: noha je príliš krátka pre tento počet kvapiek. Zväčči dĺžku alebo rozostup zmenši.');
  }

  const subpaths = [{ segs: roundedRect(0, 0, t, p.dlzka, [0, 0, 0, 0]) }];

  const d = pr.notaOffset * r;
  const phi = pr.notaOffsetAngle * DEG;
  for (let i = 0; i < p.pocet; i++) {
    const tip = { x: side > 0 ? t : 0, y: firstY + i * p.rozostup };
    const cx = tip.x + side * d * Math.cos(phi);
    const cy = tip.y + d * Math.sin(phi);
    subpaths.push({
      segs: teardropSubpath({ cx, cy, r, tip, tipRadius: pr.tipRadius * axes.hair }),
    });
  }

  return {
    subpaths,
    joints: [
      { x: t / 2, y: 0, dir: 'up' },
      { x: t / 2, y: p.dlzka, dir: 'down' },
    ],
  };
}
