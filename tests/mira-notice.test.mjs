import test from 'node:test';
import assert from 'node:assert/strict';
import site from '../cloudflare-worker/mira/site-worker.mjs';
const origin='https://pilot.example.test';
const base={APP_ORIGIN:origin};
const request=(path,options)=>new Request(origin+path,options);

test('same-origin privacy notice is available before login without exposing other documents', async () => {
  const paths = [];
  const env = {...base, MIRA_ASSETS: {async fetch(req) {
    paths.push(new URL(req.url).pathname);
    return new Response('PUBLIC NEGOTIATION DRAFT', {headers: {'Content-Type': 'text/html'}});
  }}};
  for (const path of ['/mira/documents/privacy.html', '/mira/documents/documents.css']) {
    const response = await site.fetch(request(path), env);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('Cache-Control'), 'no-store, private');
  }
  for (const path of ['/mira/documents/agency-agreement.html', '/mira/documents/source/privacy.md',
    '/mira/documents/downloads/privacy.pdf', '/mira/documents/privacy.html/', '/mira/documents/%70rivacy.html']) {
    assert.equal((await site.fetch(request(path), env)).status, 404, path);
  }
  assert.deepEqual(paths, ['/mira/documents/privacy.html', '/mira/documents/documents.css']);
  assert.equal((await site.fetch(request('/mira/documents/privacy.html', {method: 'POST'}), env)).status, 405);
});
