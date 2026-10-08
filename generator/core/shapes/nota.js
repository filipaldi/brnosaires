// nota — a leg with teardrops hanging off one side like flags on a note stem.

import { obdlznik, kvapka, vnutornyRoh } from '../primitives/index.js';

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
  // the top corner on the drop side is the first drop's join, kept sharp
  const subpaths = [obdlznik({
    x: 0, y: 0, w: t, h: p.dlzka, zaoblenie: axes.zaoblenie, rohy: [vpravo, !vpravo, true, true],
  })];
  const sx = vpravo ? t : 0; // the leg side the drops enter
  const out = vpravo ? 1 : -1;
  const f = axes.zaoblenie * h / 2;
  for (let i = 0; i < p.pocet; i++) {
    const y = i * p.rozostup;
    const k = kvapka({ x: sx, y, hair: h, vyska: p.kvapka * H, mirror: !vpravo });
    subpaths.push(k);
    // inner corners where the neck meets the leg: below it, and above it
    // unless the drop sits on the leg's top
    subpaths.push(vnutornyRoh({ x: sx, y: y + k.neck }, { x: out, y: 0 }, { x: 0, y: 1 }, f));
    if (y > 0) subpaths.push(vnutornyRoh({ x: sx, y }, { x: out, y: 0 }, { x: 0, y: -1 }, f));
  }
  return {
    subpaths: subpaths.filter(Boolean),
    joints: [
      { x: t / 2, y: p.dlzka, dir: 'down' },
      { x: t / 2, y: 0, dir: 'up' },
    ],
  };
}
