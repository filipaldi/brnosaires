// Tiny zero-dependency static server for the generator UI. Serves the
// repository root so /generator/ui/, /generator/core/ and /theme/static/fonts/
// all resolve. Usage: node generator/ui/serve.js  (port 41235)

import http from 'node:http';
import { createReadStream, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PORT = 41235;
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.avif': 'image/avif',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
  '.txt': 'text/plain; charset=utf-8',
  '.ico': 'image/x-icon',
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, headers);
  res.end(body);
}

const server = http.createServer((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return send(res, 405, 'Nie je podporované', { 'Content-Type': 'text/plain; charset=utf-8' });
  }
  let pathname;
  try {
    pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  } catch {
    return send(res, 400, 'Neplatná adresa', { 'Content-Type': 'text/plain; charset=utf-8' });
  }
  const file = path.normalize(path.join(ROOT, pathname));
  if (!file.startsWith(ROOT + path.sep)) {
    return send(res, 403, 'Prístup zamietnutý', { 'Content-Type': 'text/plain; charset=utf-8' });
  }

  let stats;
  try {
    stats = statSync(file);
  } catch {
    return send(res, 404, 'Nenašlo sa', { 'Content-Type': 'text/plain; charset=utf-8' });
  }
  const target = stats.isDirectory() ? path.join(file, 'index.html') : file;
  try {
    stats = statSync(target);
  } catch {
    return send(res, 404, 'Nenašlo sa', { 'Content-Type': 'text/plain; charset=utf-8' });
  }

  const type = MIME[path.extname(target).toLowerCase()] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': type, 'Content-Length': stats.size });
  if (req.method === 'HEAD') return res.end();
  const stream = createReadStream(target);
  stream.on('error', () => send(res, 500, 'Chyba čítania', { 'Content-Type': 'text/plain; charset=utf-8' }));
  stream.pipe(res);
});

server.listen(PORT, () => {
  console.log(`Generátor beží na http://localhost:${PORT}/generator/ui/`);
});
