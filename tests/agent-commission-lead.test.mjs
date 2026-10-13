import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import handler from '../netlify/functions/agent-commission-lead.mjs';

const source = readFileSync(new URL('../7718426309/index.html', import.meta.url), 'utf8');
const select = (id) => source.match(new RegExp(`<select id="${id}"[^>]*><option>([^<]+)</option>`))[1];
const valid = {
  'form-name': 'wegc-agent-commission', 'bot-field': '', name: 'Technical check',
  contact: 'test@example.invalid', project: 'Technical check — no transaction',
  commission: '', comment: 'Local automated test. No actual submission is sent.',
  profile: select('profile'), payout: select('payout'), stage: select('stage'),
};
const request = (data = valid, origin = 'https://wegc.fund') => new Request('https://bespoke-elf-196a9d1.netlify.app/.netlify/functions/agent-commission-lead', {
  method: 'POST', headers: { Origin: origin, 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
  body: data instanceof URLSearchParams ? data.toString() : new URLSearchParams(data).toString(),
});

test('valid landing fields reach only the registered receiver, once, with a reference', async () => {
  const previous = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return new Response('Thank you', { status: 200 }); };
  try {
    const response = await handler(request());
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('access-control-allow-origin'), 'https://wegc.fund');
    const data = await response.json();
    assert.equal(data.status, 'submitted');
    assert.match(data.reference, /^[a-f0-9-]{36}$/);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, 'https://bespoke-elf-196a9d1.netlify.app/7718426309/lead-receiver.html');
    const body = new URLSearchParams(calls[0].options.body);
    for (const [key, value] of Object.entries(valid)) assert.equal(body.get(key), value);
    assert.equal(body.get('reference'), data.reference);
    assert.equal(body.get('source'), 'https://wegc.fund/7718426309/');
    assert.equal(body.get('to'), null);
  } finally { globalThis.fetch = previous; }
});

test('empty required fields, long inputs, unknown choices, duplicates, honeypot and extra recipients never forward', async () => {
  const previous = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => { calls++; throw new Error('unexpected network'); };
  try {
    const cases = [
      { ...valid, name: '   ' }, { ...valid, contact: '' }, { ...valid, project: '' },
      { ...valid, comment: 'x'.repeat(2001) }, { ...valid, profile: 'unknown' },
      { ...valid, 'bot-field': 'spam' }, { ...valid, to: 'other@example.invalid' },
      { ...valid, 'form-name': 'another-form' }, { ...valid, name: 'A\nB' },
    ];
    const duplicate = new URLSearchParams(valid); duplicate.append('contact', 'duplicate'); cases.push(duplicate);
    for (const input of cases) {
      const response = await handler(request(input));
      assert.equal(response.status, 422);
      assert.equal((await response.json()).ok, false);
    }
    assert.equal(calls, 0);
    assert.equal((await handler(request(valid, 'https://untrusted.example'))).status, 403);
    assert.equal((await handler(request({ ...valid, comment: 'x'.repeat(20000) }))).status, 413);
    assert.equal(calls, 0);
  } finally { globalThis.fetch = previous; }
});

test('upstream failures and timeout are never reported as accepted', async () => {
  const previous = globalThis.fetch;
  try {
    for (const status of [301, 404, 429, 500]) {
      globalThis.fetch = async () => new Response('receiver error', { status });
      const response = await handler(request());
      assert.equal(response.status, 502);
      assert.equal((await response.json()).ok, false);
    }
    globalThis.fetch = async () => { throw new Error('network timeout'); };
    const response = await handler(request());
    assert.equal(response.status, 503);
    assert.equal((await response.json()).error, 'unconfirmed');
  } finally { globalThis.fetch = previous; }
});

test('frontend retains fields on errors and prevents simultaneous duplicate submissions', async () => {
  const fields = Object.fromEntries(['name', 'contact', 'project'].map(id => [id, { value: valid[id], setCustomValidity() {} }]));
  const button = { disabled: false, textContent: '' };
  const status = { hidden: true, textContent: '', className: '' };
  let submit, calls = 0, reset = 0, release;
  const pending = new Promise(resolve => { release = resolve; });
  const form = {
    action: 'https://bespoke-elf-196a9d1.netlify.app/.netlify/functions/agent-commission-lead',
    querySelector: () => button, addEventListener: (name, callback) => { if (name === 'submit') submit = callback; },
    reportValidity: () => true, setAttribute() {}, removeAttribute() {}, reset() { reset++; },
  };
  vm.runInNewContext(readFileSync(new URL('../7718426309/lead-form.js', import.meta.url), 'utf8'), {
    document: { getElementById: id => id === 'leadForm' ? form : id === 'leadStatus' ? status : fields[id] },
    fetch: async () => { calls++; await pending; return { ok: false, status: 503, json: async () => ({ ok: false }) }; },
    FormData: class { [Symbol.iterator]() { return Object.entries(valid)[Symbol.iterator](); } },
    URLSearchParams, AbortController, setTimeout, clearTimeout,
  });
  const first = submit({ preventDefault() {} });
  assert.equal(button.disabled, true);
  await submit({ preventDefault() {} });
  assert.equal(calls, 1);
  release(); await first;
  assert.equal(reset, 0);
  assert.equal(fields.contact.value, valid.contact);
  assert.equal(status.className, 'form-status error');
  assert.match(status.textContent, /Не удалось подтвердить/);
  assert.equal(button.disabled, false);
});

test('Charter Capital origin accepts USDT and THB, with server-controlled source and original receiver', async () => {
  const previous = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return new Response('Thank you', { status: 200 }); };
  try {
    for (const payout of ['USDT', 'Наличные THB']) {
      const response = await handler(request({ ...valid, payout }, 'https://ccapital.pro'));
      assert.equal(response.status, 200);
      assert.equal(response.headers.get('access-control-allow-origin'), 'https://ccapital.pro');
      const data = await response.json();
      const forwarded = new URLSearchParams(calls.at(-1).options.body);
      assert.equal(forwarded.get('source'), 'https://ccapital.pro/pay_commission/');
      assert.equal(forwarded.get('payout'), payout);
      assert.match(forwarded.get('subject'), /^Charter Capital/);
      assert.equal(forwarded.get('reference'), data.reference);
      assert.equal(forwarded.get('to'), null);
      assert.equal(calls.at(-1).url, 'https://bespoke-elf-196a9d1.netlify.app/7718426309/lead-receiver.html');
    }
    assert.equal(calls.length, 2);
    for (const origin of ['https://www.ccapital.pro', 'https://www.wet-hk.pro', 'https://ccapital.pro.untrusted.example']) {
      assert.equal((await handler(request(valid, origin))).status, 403);
    }
    for (const injected of [{ source: 'https://untrusted.example' }, { subject: 'Spoofed' }, { to: 'other@example.invalid' }]) {
      assert.equal((await handler(request({ ...valid, ...injected }, 'https://ccapital.pro'))).status, 422);
    }
    assert.equal(calls.length, 2);
  } finally { globalThis.fetch = previous; }
});

test('native Charter response links back to Charter; all original WEGC origins retain source and brand', async () => {
  const previous = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => { calls.push({ url, options }); return new Response('Thank you', { status: 200 }); };
  try {
    const native = request({ ...valid, payout: 'USDT' }, 'https://ccapital.pro');
    native.headers.set('accept', 'text/html');
    const html = await (await handler(native)).text();
    assert.match(html, /Charter Capital/);
    assert.ok(html.includes('https://ccapital.pro/pay_commission/#lead'));
    for (const origin of ['https://wegc.fund', 'https://www.wegc.fund', 'https://bespoke-elf-196a9d1.netlify.app']) {
      const response = await handler(request(valid, origin));
      assert.equal(response.status, 200);
      const forwarded = new URLSearchParams(calls.at(-1).options.body);
      assert.equal(forwarded.get('source'), 'https://wegc.fund/7718426309/');
      assert.match(forwarded.get('subject'), /^WEGC/);
    }
  } finally { globalThis.fetch = previous; }
});
