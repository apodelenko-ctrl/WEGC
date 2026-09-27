import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source = fs.readFileSync(new URL('../mira/analytics.mjs', import.meta.url), 'utf8');

function run(hostname, search = '', existing = false) {
  const sent = [];
  vm.runInNewContext(source, {
    URLSearchParams, location: {hostname, search},
    document: {querySelector: () => existing ? {} : null,
      createElement: () => ({dataset: {}}), head: {append: x => sent.push(x)}}
  });
  return sent;
}
test('production installs one vendor collector without form data', () => {
  const sent = run('wegc.fund');
  assert.equal(sent.length, 1);
  assert.equal(sent[0].src, 'https://static.cloudflareinsights.com/beacon.min.js');
  assert.deepEqual(Object.keys(JSON.parse(sent[0].dataset.cfBeacon)), ['token']);
});
test('local, QA and pre-existing automatic collectors are not counted twice', () => {
  assert.equal(run('localhost').length, 0);
  assert.equal(run('127.0.0.1').length, 0);
  assert.equal(run('pilot.wegc.fund').length, 0);
  assert.equal(run('wegc.fund', '?mira_analytics=off').length, 0);
  assert.equal(run('wegc.fund', '', true).length, 0);
});
