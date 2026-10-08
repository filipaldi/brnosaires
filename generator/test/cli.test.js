// CLI: typy prints the catalogue, tvar writes a deterministic SVG, bad input
// exits with code 1 and a Slovak message.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const exec = promisify(execFile);
const CLI = fileURLToPath(new URL('../cli.js', import.meta.url));
const NODE = process.execPath;

test('typy vypíše katalóg tvarov', async () => {
  const { stdout } = await exec(NODE, [CLI, 'typy']);
  assert.match(stdout, /noha — Noha/);
  assert.match(stdout, /polkruh — Polooblúk/);
  assert.match(stdout, /dlzka/);
});

test('tvar zapíše SVG a je deterministický', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'brnos-gen-'));
  try {
    const out = path.join(dir, 'oblouk.svg');
    const first = await exec(NODE, [CLI, 'tvar', '--typ', 'oblouk', '--weight', '60',
      '--contrast', '80', '--out', out]);
    assert.match(first.stdout, /Zapísané/);
    const svg1 = readFileSync(out, 'utf8');
    assert.ok(svg1.startsWith('<svg'));
    assert.match(svg1, /fill-rule="nonzero"/);
    assert.doesNotMatch(svg1, /NaN|Infinity/);

    const out2 = path.join(dir, 'oblouk2.svg');
    await exec(NODE, [CLI, 'tvar', '--typ', 'oblouk', '--weight', '60',
      '--contrast', '80', '--out', out2]);
    assert.equal(readFileSync(out2, 'utf8'), svg1, 'rovnaké vstupy majú dať rovnaké bajty');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('vzorkovnik zapíše SVG', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'brnos-gen-'));
  try {
    const out = path.join(dir, 'vzorkovnik.svg');
    await exec(NODE, [CLI, 'vzorkovnik', '--typ', 'noha,kruh', '--weight', '40,80',
      '--contrast', '70', '--out', out]);
    const svg = readFileSync(out, 'utf8');
    assert.match(svg, /Weight 40/);
    assert.match(svg, /Weight 80/);
    assert.match(svg, /Noha/);
    assert.match(svg, /Kruh/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('zlý typ skončí s kódom 1 a slovenskou správou', async () => {
  await assert.rejects(
    exec(NODE, [CLI, 'tvar', '--typ', 'neexistuje', '--out', '/tmp/x.svg']),
    (e) => e.code === 1 && /Neznámy typ/.test(e.stderr),
  );
});

test('zlá hodnota osi skončí s kódom 1', async () => {
  await assert.rejects(
    exec(NODE, [CLI, 'tvar', '--typ', 'noha', '--weight', '140', '--out', '/tmp/x.svg']),
    (e) => e.code === 1 && /Weight/.test(e.stderr),
  );
});

test('bez príkazu vypíše nápovedu a skončí kódom 1', async () => {
  await assert.rejects(
    exec(NODE, [CLI]),
    (e) => e.code === 1 && /Použitie/.test(e.stdout),
  );
});
