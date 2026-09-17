import test from 'node:test';
import assert from 'node:assert/strict';
import site from '../cloudflare-worker/mira/site-worker.mjs';

const origin = 'https://pilot.example.test';
const request = (path, options) => new Request(origin + path, options);
const base = {APP_ORIGIN: origin, ACCESS_TEAM_DOMAIN: 'https://mira-site-test.cloudflareaccess.com', ACCESS_AUDIENCE: 'synthetic-audience'};

test('dedicated hostname rejects other origins, unsupported methods and unlisted files', async () => {
  const env = {...base, MIRA_ASSETS: {fetch() {throw Error('must not serve');}}};
  assert.equal((await site.fetch(new Request('https://wegc.fund/mira/pilot.html'), env)).status, 421);
  assert.equal((await site.fetch(request('/mira/pilot.html'), {})).status, 421);
  for (const path of ['/wrangler.toml', '/mira/pilot', '/mira/pilot.html/', '/mira/catalog/', '/mira/%70ilot.html']) {
    assert.equal((await site.fetch(request(path), env)).status, 404, path);
  }
  assert.equal((await site.fetch(request('/mira/pilot.html', {method: 'POST'}), env)).status, 405);
});

test('HTML fails closed without signed identity even with an email header or cookie', async () => {
  for (const path of ['/mira/pilot.html', '/mira/library.html']) {
    const response = await site.fetch(request(path, {headers: {'Cf-Access-Authenticated-User-Email': 'fake@example.test', Cookie: 'CF_Authorization=fake'}}), base);
    assert.equal(response.status, 401);
    assert.equal((await response.json()).error, 'identity_required');
  }
  const bad = await site.fetch(request('/mira/pilot.html', {headers: {'Cf-Access-Jwt-Assertion': 'fake.jwt.value'}}), base);
  assert.equal(bad.status, 401);
});

test('UI assets use explicit binding and enforce private cache and CSP headers', async () => {
  const env = {...base, MIRA_ASSETS: {async fetch(req) {
    assert.equal(new URL(req.url).pathname, '/mira/pilot.mjs');
    return new Response('/* public UI code */', {headers: {'Content-Type': 'text/javascript', 'Cache-Control': 'public, max-age=86400'}});
  }}};
  const response = await site.fetch(request('/mira/pilot.mjs'), env);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('Cache-Control'), 'no-store, private');
  assert.match(response.headers.get('Content-Security-Policy'), /frame-ancestors 'none'/);
  assert.equal(response.headers.get('Content-Type'), 'text/javascript');
  assert.equal((await site.fetch(request('/mira/pilot.mjs'), base)).status, 503);
});

test('public links redirect only to fixed public destinations, query strings are not forwarded', async () => {
  for (const path of ['/mira/', '/mira/marketplace.html', '/mira/phuket-starter-kit.html']) {
    const response = await site.fetch(request(path + '?next=https://evil.test'), base);
    assert.equal(response.status, 302);
    assert.equal(response.headers.get('Location'), 'https://wegc.fund' + path);
  }
  assert.equal((await site.fetch(request('/'), base)).headers.get('Location'), '/mira/pilot.html');
});

test('the intake notice is readable before login, without exposing other HTML', async () => {
  const env = {...base, MIRA_ASSETS: {fetch() {return new Response('intake notice', {headers: {'Content-Type': 'text/html'}});}}};
  for (const path of ['/mira/agency-privacy.html', '/mira/pilot.css']) {
    const response = await site.fetch(request(path), env);
    assert.equal(response.status, 200);
    assert.match(response.headers.get('Content-Security-Policy'), /script-src 'self'/);
  }
  assert.equal((await site.fetch(request('/mira/documents/privacy.html'), env)).status, 404);
  assert.equal((await site.fetch(request('/mira/pilot.html'), env)).status, 401);
});

test('API requests remain JSON and cannot fall back to static HTML', async () => {
  const env = {...base, MIRA_DB: {}, MIRA_ASSETS: {fetch() {throw Error('must not serve');}}};
  const response = await site.fetch(request('/mira/api/session'), env);
  assert.equal(response.status, 401);
  assert.match(response.headers.get('Content-Type'), /application\/json/);
  assert.equal((await response.json()).error, 'identity_required');
  const post = await site.fetch(request('/mira/api/applications', {method: 'POST', headers: {Origin: 'https://wegc.fund'}}), env);
  assert.equal(post.status, 403);
  assert.equal((await post.json()).error, 'origin_rejected');
});

test('a real RSA-signed synthetic Access JWT is required to serve protected HTML', async t => {
  const pair = await crypto.subtle.generateKey({name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048,
    publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256'}, true, ['sign', 'verify']);
  const kid = crypto.randomUUID(), issuer = `https://site-${kid}.cloudflareaccess.com`;
  const env = {...base, ACCESS_TEAM_DOMAIN: issuer, MIRA_ASSETS: {async fetch() {return new Response('<h1>Pilot</h1>');}}};
  const jwk = {...await crypto.subtle.exportKey('jwk', pair.publicKey), kid};
  t.mock.method(globalThis, 'fetch', async url => {
    assert.equal(url, issuer + '/cdn-cgi/access/certs');
    return Response.json({keys: [jwk]});
  });
  const encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
  async function token(aud) {
    const now = Math.floor(Date.now() / 1000);
    const data = encode({alg: 'RS256', kid}) + '.' + encode({iss: issuer, aud: [aud], iat: now,
      exp: now + 60, type: 'app', sub: 'synthetic-user', email: 'synthetic@example.test'});
    const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', pair.privateKey, new TextEncoder().encode(data));
    return data + '.' + Buffer.from(sig).toString('base64url');
  }
  for (const path of ['/mira/pilot.html', '/mira/library.html']) {
    const response = await site.fetch(request(path, {headers: {'Cf-Access-Jwt-Assertion': await token(env.ACCESS_AUDIENCE)}}), env);
    assert.equal(response.status, 200);
    assert.equal(await response.text(), '<h1>Pilot</h1>');
  }
  assert.equal((await site.fetch(request('/mira/pilot.html', {headers: {'Cf-Access-Jwt-Assertion': await token('wrong-audience')}}), env)).status, 401);
});
