import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { MODELS, GOALS, OWNERS, validModel, createPlan, briefText } from '../mira/agency/qualification.mjs';
const html = readFileSync(new URL('../mira/agency/index.html', import.meta.url), 'utf8');
const js = readFileSync(new URL('../mira/agency/agency.mjs', import.meta.url), 'utf8');
const sample = { model: 'new_direction', goal: 'explore', owner: 'decision_maker' };

test('all 64 self-reported combinations produce local plans, never approvals', () => {
  let count = 0;
  for (const model of Object.keys(MODELS)) for (const goal of Object.keys(GOALS)) for (const owner of Object.keys(OWNERS)) {
    const p = createPlan({ model, goal, owner });
    assert.equal(p.steps.length, 3);
    assert.equal(p.submitted, false);
    assert.equal(p.approved, false);
    assert.match(p.demoUrl, /^\/mira\/marketplace\.html\?view=(catalog|clients|onboarding)$/);
    assert.match(p.boundary, /не одобрение/);
    count++;
  }
  assert.equal(count, 64);
});
test('existing overseas / Thailand desks do not get a greenfield script', () => {
  const overseas = createPlan({ ...sample, model: 'overseas_desk' });
  const thailand = createPlan({ ...sample, model: 'thailand_desk' });
  assert.match(overseas.description, /Сохраните действующую команду/);
  assert.match(thailand.description, /Вы уже работаете с рынком/);
  assert.notEqual(overseas.title, thailand.title);
});
test('unassigned owner is addressed first without marking the agency unfit', () => {
  const p = createPlan({ ...sample, owner: 'not_assigned' });
  assert.match(p.steps[0], /^Сначала определите ответственного/);
  assert.equal(p.steps.length, 3);
  assert.equal('score' in p, false);
});
test('network pilot scope and buyer-data boundary remain explicit', () => {
  const p = createPlan({ ...sample, model: 'network', goal: 'client_request' });
  assert.match(p.steps[0], /юридическое лицо/);
  assert.match(p.steps[1], /без имени, контактов и документов/);
});
test('rejects missing, malicious and prototype-derived values', () => {
  for (const input of [null, [], {}, { ...sample, goal: '' }, { ...sample, model: '__proto__' }, { ...sample, owner: 'constructor' }, { ...sample, goal: '<img src=x onerror=alert(1)>' }, Object.create(sample)]) {
    assert.throws(() => createPlan(input), TypeError);
  }
  for (const v of ['__proto__', 'constructor', 'https://example.test', null, {}, '<script>']) assert.equal(validModel(v), false);
  assert.equal(validModel('network'), true);
});
test('download is deterministic and includes only enum-based answers', () => {
  const text = briefText({ ...sample, email: 'SHOULD-NOT-APPEAR', amount: '999999', client: 'PRIVATE-CLIENT' });
  assert.equal(text, briefText(sample));
  assert.match(text, /Локальный черновик\. Не отправлен/);
  assert.doesNotMatch(text, /SHOULD-NOT-APPEAR|999999|PRIVATE-CLIENT/);
});
test('HTML offers a real demo and no active public intake endpoint', () => {
  assert.match(html, /connect-src 'none'/);
  assert.match(html, /form-action 'none'/);
  assert.match(html, /<fieldset id="qualification-fields" disabled>/);
  assert.match(html, /type="button" id="build-plan"/);
  assert.match(html, /<noscript>/);
  assert.match(html, /Приём заявок сейчас закрыт/);
  assert.doesNotMatch(html, /<input|<textarea|<iframe|mailto:|forms\.gle|action="https?:/i);
  assert.equal((html.match(/<h1\b/g) || []).length, 1);
});
test('all menu choices are backed by enums and modules do not transmit or persist', () => {
  const optionValues = [...html.matchAll(/<option value="([^\"]+)"/g)].map(x => x[1]);
  assert.deepEqual(optionValues, [...Object.keys(MODELS), ...Object.keys(GOALS), ...Object.keys(OWNERS)]);
  for (const token of ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'document.cookie', 'innerHTML', 'eval(']) assert.equal(js.includes(token), false, token);
  assert.match(js, /event\.preventDefault\(\)/);
  assert.match(js, /addEventListener\('change', invalidate\)/);
});

test('anchor IDs are unique and every in-page CTA resolves', () => {
  const ids = [...html.matchAll(/\bid="([^\"]+)"/g)].map(m => m[1]);
  assert.equal(new Set(ids).size, ids.length);
  for (const [, id] of html.matchAll(/href="#([^\"]+)"/g)) assert.ok(ids.includes(id), id);
});
