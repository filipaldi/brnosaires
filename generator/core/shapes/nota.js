// nota — a leg with teardrops hanging off one side like flags on a note stem.

import { obdlznik, kvapka } from '../primitives/index.js';

export const id = 'nota';
export const name = 'Nota';

export const params = {
  dlzka: { label: 'dĺžka', type: 'number', min: 0.2, max: 40 },
  pocet: { label: 'počet kvapiek', type: 'integer', min: 1, max: 12 },
  rozostup: { label: 'rozostup', type: 'number', min: 0.05, max: 20 },
  kvapka: { label: 'kvapka (× heavy)', type: 'number', min: 0.1, max: 40 },
  strana: { label: 'strana', type: 'enum', values: ['vpravo', 'vlavo'] },
  hrubka: { label: 'hrúbka nohy', type: 'enum', values: ['vlas', 'plna'] },
};

export function build(p, axes) {
  const { hair: h, heavy: H } = axes;
  const t = p.hrubka === 'vlas' ? h : H;
  const vpravo = p.strana === 'vpravo';
  const subpaths = [obdlznik({ x: 0, y: 0, w: t, h: p.dlzka })];
  for (let i = 0; i < p.pocet; i++) {
    subpaths.push(kvapka({
      x: vpravo ? t : 0, y: i * p.rozostup, hair: h, vyska: p.kvapka * H, mirror: !vpravo,
    }));
  }
  return {
    subpaths,
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down' },
      { x: t / 2, y: 0, dir: 'up' },
    ],
  };
}
