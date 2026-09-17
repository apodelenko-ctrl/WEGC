/**
 * Server acceptance lane. Uses the production Worker and real RSA verification.
 * Only the Access certificate HTTP response is stubbed; no identity bypass.
 * All identities, company names, evidence and dates below are synthetic fixtures.
 * This is not an email-delivery, browser, deployed-D1 or production load test.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync, readdirSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import worker from '../cloudflare-worker/mira/worker.mjs';

const schemaDir = new URL('../cloudflare-worker/mira/migrations/', import.meta.url);
const schema = readdirSync(schemaDir).filter(f => f.endsWith('.sql')).sort()
  .map(f => readFileSync(new URL(f, schemaDir), 'utf8')).join('\n');
const encode = value => Buffer.from(typeof value === 'string' ? value : JSON.stringify(value)).toString('base64url');
const since = () => new Date(Date.now() - 60_000).toISOString();
const until = () => new Date(Date.now() + 3_600_000).toISOString();

class LocalD1 {
  constructor(filename, initialize = false) {
    this.db = new DatabaseSync(filename);
    this.db.exec('PRAGMA foreign_keys=ON');
    if (initialize) this.db.exec(schema);
    this.queue = Promise.resolve();
  }
  prepare(sql) {
    const owner = this;
    return {bind(...args) {
      return {
        async first() { return owner.db.prepare(sql).get(...args) ?? null; },
        async all() { return {results: owner.db.prepare(sql).all(...args)}; },
        async run() {
          const result = owner.db.prepare(sql).run(...args);
          return {success: true, meta: {changes: Number(result.changes)}};
        }
      };
    }};
  }
  batch(statements) {
    const execute = async () => {
      this.db.exec('BEGIN IMMEDIATE');
      try {
        const results = [];
        for (const statement of statements) results.push(await statement.run());
        this.db.exec('COMMIT');
        return results;
      } catch (error) { this.db.exec('ROLLBACK'); throw error; }
    };
    const next = this.queue.then(execute);
    this.queue = next.catch(() => {});
    return next;
  }
}

async function fixture(t) {
  const directory = mkdtempSync(join(tmpdir(), 'mira-synthetic-journey-'));
  const filename = join(directory, 'synthetic.sqlite');
  let database = new LocalD1(filename, true);
  const pair = await crypto.subtle.generateKey({name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048,
    publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256'}, true, ['sign', 'verify']);
  const kid = crypto.randomUUID();
  const issuer = `https://mira-test-${kid}.cloudflareaccess.com`;
  const publicKey = {...await crypto.subtle.exportKey('jwk', pair.publicKey), kid, alg: 'RS256', use: 'sig'};
  const certificateCalls = [];
  t.mock.method(globalThis, 'fetch', async (url) => {
    certificateCalls.push(String(url));
    assert.equal(String(url), issuer + '/cdn-cgi/access/certs', 'unexpected outbound call');
    return Response.json({keys: [publicKey]});
  });
  const env = {MIRA_DB: database, APP_ORIGIN: 'https://mira.example.test',
    ACCESS_TEAM_DOMAIN: issuer, ACCESS_AUDIENCE: 'synthetic-application-audience',
    APPLICATIONS_ENABLED: 'true', MATERIALS_ENABLED: 'false',
    PRIVACY_VERSION: 'SYNTHETIC-NOT-A-LEGAL-APPROVAL',
    PRIVACY_NOTICE_URL: 'https://mira.example.test/synthetic-privacy', APPLICATION_RATE_LIMIT: '5'};
  // The very first operator is an explicit local-only bootstrap fixture, not public signup.
  database.db.prepare("INSERT INTO mira_memberships(subject,agency_id,role,active) VALUES (?,NULL,'operator',1)").run('synthetic-operator');
  t.after(() => { database.db.close(); rmSync(directory, {recursive: true, force: true}); });
  async function token(subject, claims = {}) {
    const timestamp = Math.floor(Date.now() / 1000);
    const unsigned = `${encode({alg: 'RS256', kid})}.${encode({iss: issuer, aud: [env.ACCESS_AUDIENCE],
      iat: timestamp, exp: timestamp + 600, type: 'app', sub: subject,
      email: `${subject}@example.test`, ...claims})}`;
    const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', pair.privateKey, new TextEncoder().encode(unsigned));
    return `${unsigned}.${Buffer.from(sig).toString('base64url')}`;
  }
  async function call(subject, path, body, options = {}) {
    const headers = {'Content-Type': 'application/json', Origin: env.APP_ORIGIN,
      ...(subject ? {'Cf-Access-Jwt-Assertion': await token(subject, options.claims)} : {}), ...options.headers};
    const response = await worker.fetch(new Request(env.APP_ORIGIN + '/mira/api' + path,
      {method: options.method || (body === undefined ? 'GET' : 'POST'), headers,
        body: body === undefined ? undefined : JSON.stringify(body)}), env);
    return {status: response.status, headers: response.headers, body: await response.json()};
  }
  const application = {company: 'SYNTHETIC AGENCY', city: 'SYNTHETIC CITY', name: 'SYNTHETIC USER',
    format: 'agency', demand: 'learning', markets: ['phuket'], consent_version: env.PRIVACY_VERSION};
  const submit = (subject = 'synthetic-applicant', key = 'synthetic-request') => call(subject, '/applications',
    application, {headers: {'Idempotency-Key': key}});
  const proof = (id, kind, scope = {}) => call('synthetic-operator', '/admin/evidence', {
    id, kind, storage_ref: 'vault:SYNTHETIC-ONLY', verified: true, verified_at: since(), expires_at: until(), ...scope});
  async function qualified() {
    const receipt = await submit(); assert.equal(receipt.status, 201);
    const id = receipt.body.id;
    assert.equal((await call('synthetic-operator', `/admin/applications/${id}/status`,
      {status: 'review', version: 0, reason: 'Synthetic verification only'})).status, 200);
    assert.equal((await proof('EVID-test-qualified', 'application_qualification', {entity_id: id})).status, 201);
    assert.equal((await call('synthetic-operator', `/admin/applications/${id}/status`,
      {status: 'qualified', version: 1, reason: 'Synthetic verification only', evidence_ref: 'EVID-test-qualified'})).status, 200);
    return id;
  }
  async function activate() {
    const id = await qualified();
    const agency = {id: 'synthetic-agency', name: 'SYNTHETIC AGENCY', city: 'SYNTHETIC CITY', status: 'pending'};
    assert.equal((await call('synthetic-operator', '/admin/agencies', agency)).status, 200);
    assert.equal((await proof('EVID-test-agreement', 'agency_agreement', {agency_id: agency.id})).status, 201);
    assert.equal((await call('synthetic-operator', '/admin/agencies',
      {...agency, status: 'active', agreement_ref: 'EVID-test-agreement'})).status, 200);
    assert.equal((await call('synthetic-operator', '/admin/memberships',
      {subject: 'synthetic-applicant', agency_id: agency.id, role: 'agency_owner', active: true})).status, 200);
    assert.equal((await proof('EVID-test-onboarding', 'agency_onboarding', {entity_id: id, agency_id: agency.id})).status, 201);
    const result = await call('synthetic-operator', `/admin/applications/${id}/status`,
      {status: 'onboarded', version: 2, reason: 'Synthetic verification only', evidence_ref: 'EVID-test-onboarding', agency_id: agency.id});
    assert.equal(result.status, 200); assert.equal(result.body.activation_recorded, false);
    return {id, agency};
  }
  return {env, call, token, application, submit, proof, qualified, activate, certificateCalls,
    get db() { return database.db; },
    restoreSnapshot() { const restored = join(directory,'restored-separate.sqlite'); database.db.exec("VACUUM INTO '"+restored.replaceAll("'","''")+"'"); database.db.close(); database = new LocalD1(restored); env.MIRA_DB=database; },
    restart() { database.db.close(); database = new LocalD1(filename); env.MIRA_DB = database; }};
}

test('production auth: a verified email is not automatic business access', async t => {
  const f = await fixture(t);
  const session = await f.call('synthetic-applicant', '/session');
  assert.equal(session.status, 200); assert.equal(session.body.membership, null);
  assert.equal((await f.call('synthetic-applicant', '/projects')).status, 403);
  assert.equal((await f.call('synthetic-applicant', '/admin/applications')).status, 403);
  assert.equal((await f.call(null, '/session', undefined, {headers: {'Cf-Access-Authenticated-User-Email': 'synthetic-operator@example.test'}})).status, 401);
  assert.equal(f.certificateCalls.length, 1);
});

test('production JWT: wrong audience, expired and unsigned identities cannot create a receipt', async t => {
  const f = await fixture(t);
  for (const claims of [{aud: ['wrong-application']}, {exp: Math.floor(Date.now()/1000) - 1}, {type: 'service'}]) {
    const response = await f.call('synthetic-applicant', '/applications', f.application,
      {claims, headers: {'Idempotency-Key': 'rejected-request'}});
    assert.equal(response.status, 401);
  }
  const forged = `${encode({alg: 'none'})}.${encode({sub: 'synthetic-operator'})}.unsigned`;
  assert.equal((await f.call(null, '/session', undefined, {headers: {'Cf-Access-Jwt-Assertion': forged}})).status, 401);
  assert.equal(f.db.prepare('SELECT COUNT(*) n FROM mira_applications').get().n, 0);
});

test('durable application: receipt, ownership isolation and restart are one server journey', async t => {
  const f = await fixture(t);
  const receipt = await f.submit(); assert.equal(receipt.status, 201);
  f.restart();
  const repeated = await f.submit(); assert.equal(repeated.status, 200); assert.equal(repeated.body.id, receipt.body.id);
  const own = await f.call('synthetic-applicant', '/applications/' + receipt.body.id);
  assert.equal(own.status, 200); assert.equal(own.body.events.length, 1);
  assert.equal((await f.call('synthetic-stranger', '/applications/' + receipt.body.id)).status, 404);
  assert.deepEqual((await f.call('synthetic-stranger', '/applications')).body.records, []);
  const conflict = await f.call('synthetic-applicant', '/applications', {...f.application, company: 'SYNTHETIC CHANGED'},
    {headers: {'Idempotency-Key': 'synthetic-request'}});
  assert.equal(conflict.status, 409);
  assert.equal(f.db.prepare('SELECT COUNT(*) n FROM mira_applications').get().n, 1);
});

test('concurrent signed retries produce one application and one audit event', async t => {
  const f = await fixture(t);
  // Warm key cache to keep concurrency about database state, not certificate fetching.
  await f.call('synthetic-applicant', '/session');
  const results = await Promise.all(Array.from({length: 5}, () => f.submit()));
  assert(results.every(r => [200, 201].includes(r.status)), JSON.stringify(results));
  assert.equal(new Set(results.map(r => r.body.id)).size, 1);
  assert.equal(f.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='application'").get().n, 1);
});

test('onboarding: authenticated applicant -> operator review -> scoped agreement -> business access', async t => {
  const f = await fixture(t); const {id} = await f.activate();
  f.restart();
  const own = await f.call('synthetic-applicant', '/applications/' + id);
  assert.deepEqual(own.body.events.map(e => e.status), ['received', 'review', 'qualified', 'onboarded']);
  assert.equal((await f.call('synthetic-applicant', '/profile')).body.agency.status, 'active');
  assert.deepEqual((await f.call('synthetic-applicant', '/projects')).body.records, []);
  assert.equal((await f.call('synthetic-applicant', '/admin/dashboard')).status, 403);
  assert.equal((await f.call('synthetic-operator', '/admin/dashboard')).body.financial_totals, null);
});

test('onboarding cannot skip agreement, ownership or reviewed proof', async t => {
  const f = await fixture(t); const id = await f.qualified();
  const payload = {status: 'onboarded', version: 2, reason: 'Synthetic incomplete onboarding',
    evidence_ref: 'EVID-missing', agency_id: 'synthetic-agency'};
  assert.equal((await f.call('synthetic-operator', `/admin/applications/${id}/status`, payload)).status, 409);
  assert.equal((await f.call('synthetic-applicant', `/admin/applications/${id}/status`, payload)).status, 403);
  const unchanged = await f.call('synthetic-applicant', '/applications/' + id);
  assert.equal(unchanged.body.application.status, 'qualified'); assert.equal(unchanged.body.events.length, 3);
});

test('assigned project is not permission to register a buyer; revocation takes immediate effect', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  assert.equal((await f.call('synthetic-operator', '/admin/projects',
    {id: 'synthetic-project', name: 'SYNTHETIC PROJECT', market: 'phuket', enabled: false})).status, 200);
  assert.equal((await f.call('synthetic-operator', '/admin/agency-projects',
    {agency_id: agency.id, project_id: 'synthetic-project'})).status, 200);
  assert.equal((await f.call('synthetic-applicant', '/projects')).body.records.length, 1);
  assert.equal((await f.call('synthetic-applicant', '/projects/synthetic-project')).body.registration_eligible, false);
  assert.equal((await f.call('synthetic-applicant', '/leads',
    {project_id: 'synthetic-project', client_ref: 'SYNTHETIC-CLIENT', consent_ref: 'EVID-synthetic-missing'})).status, 409);
  assert.equal((await f.call('synthetic-operator', '/admin/evidence/EVID-test-agreement/revoke',
    {reason: 'Synthetic revoke acceptance'})).status, 200);
  assert.equal((await f.call('synthetic-applicant', '/profile')).status, 403);
  assert.equal(f.db.prepare('SELECT COUNT(*) n FROM mira_leads').get().n, 0);
});

test('an audit failure rolls back the application: no phantom successful receipt', async t => {
  const f = await fixture(t);
  f.db.exec(`CREATE TRIGGER synthetic_fail_audit BEFORE INSERT ON mira_events
    WHEN NEW.entity_type='application' BEGIN SELECT RAISE(ABORT,'synthetic-storage-failure'); END;`);
  const result = await f.submit(); assert.equal(result.status, 500);
  assert.equal(result.body.error, 'internal_error');
  assert(!JSON.stringify(result.body).includes('synthetic-storage-failure'));
  assert.equal(f.db.prepare('SELECT COUNT(*) n FROM mira_applications').get().n, 0);
  f.db.exec('DROP TRIGGER synthetic_fail_audit');
  assert.equal((await f.submit()).status, 201);
});

test('intake controls: closed mode, CSRF, replay limit and non-cacheable responses', async t => {
  const f = await fixture(t); f.env.APPLICATIONS_ENABLED = 'false';
  assert.equal((await f.submit()).status, 503);
  f.env.APPLICATIONS_ENABLED = 'true';
  assert.equal((await f.call('synthetic-applicant', '/applications', f.application,
    {headers: {Origin: 'https://unrelated.example.test', 'Idempotency-Key': 'synthetic-bad-origin'}})).status, 403);
  f.env.APPLICATION_RATE_LIMIT = '1';
  const first = await f.submit(); assert.equal(first.status, 201);
  assert.match(first.headers.get('Cache-Control'), /no-store/);
  assert.equal(first.headers.get('X-Content-Type-Options'), 'nosniff');
  assert.equal((await f.submit()).status, 200);
  assert.equal((await f.submit('synthetic-applicant', 'synthetic-second-request')).status, 429);
});

test('every operator access mutation has an immutable audit event', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  const rows = f.db.prepare("SELECT entity_type,entity_id,status,actor,version FROM mira_events WHERE entity_type IN ('agency','membership') ORDER BY entity_type,version").all();
  assert.equal(rows.filter(r => r.entity_type === 'agency').length, 2, 'pending and active agency mutations must be audited');
  assert.equal(rows.filter(r => r.entity_type === 'membership').length, 1, 'membership grant must be audited');
  assert(rows.every(r => r.actor === 'synthetic-operator'));
  assert.equal((await f.call('synthetic-operator', '/admin/memberships',
    {subject: 'synthetic-applicant', agency_id: agency.id, role: 'agency_owner', active: false})).status, 200);
  const revoked = f.db.prepare("SELECT status,version FROM mira_events WHERE entity_type='membership' ORDER BY version DESC").get();
  assert.equal(revoked.status, 'agency_owner_inactive'); assert.equal(revoked.version, 1);
  assert.equal((await f.call('synthetic-applicant', '/profile')).status, 403);
  assert.throws(() => f.db.exec("DELETE FROM mira_events WHERE entity_type='membership'"), /immutable/);
});

test('failed access-audit storage rolls back the actual access grant', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  f.db.exec(`CREATE TRIGGER synthetic_fail_membership_audit BEFORE INSERT ON mira_events
    WHEN NEW.entity_type='membership' BEGIN SELECT RAISE(ABORT,'synthetic-audit-fault'); END;`);
  const result = await f.call('synthetic-operator', '/admin/memberships',
    {subject: 'synthetic-second-user', agency_id: agency.id, role: 'broker', active: true});
  assert.equal(result.status, 500);
  assert.equal(f.db.prepare('SELECT COUNT(*) n FROM mira_memberships WHERE subject=?').get('synthetic-second-user').n, 0);
  assert.equal((await f.call('synthetic-second-user', '/profile')).status, 403);
});

test('project assignment changes are audited without duplicate no-op events', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  assert.equal((await f.call('synthetic-operator', '/admin/projects',
    {id: 'synthetic-project', name: 'SYNTHETIC PROJECT', market: 'phuket', enabled: false})).status, 200);
  const assignment = {agency_id: agency.id, project_id: 'synthetic-project'};
  assert.equal((await f.call('synthetic-operator', '/admin/agency-projects', assignment)).status, 200);
  assert.equal((await f.call('synthetic-operator', '/admin/agency-projects', assignment)).status, 200);
  assert.equal(f.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='project'").get().n, 1);
  assert.equal(f.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='agency_project'").get().n, 1);
});

test('concurrent administrative changes keep ordered distinct audit versions', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  const results = await Promise.all(Array.from({length: 5}, (_, i) =>
    f.call('synthetic-operator', '/admin/memberships', {subject: 'synthetic-additional',
      agency_id: agency.id, role: 'broker', active: i % 2 === 0})));
  assert(results.every(r => r.status === 200));
  const rows = f.db.prepare("SELECT version,status FROM mira_events WHERE entity_type='membership' AND entity_id=? ORDER BY version").all('synthetic-additional');
  assert.deepEqual(rows.map(r => r.version), [0, 1, 2, 3, 4]);
  const actual = f.db.prepare('SELECT active FROM mira_memberships WHERE subject=?').get('synthetic-additional');
  assert.equal(rows.at(-1).status, actual.active ? 'broker_active' : 'broker_inactive');
});

test('bootstrap-only operator cannot be reassigned and no false grant event is recorded', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  const before = f.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='membership'").get().n;
  const result = await f.call('synthetic-operator', '/admin/memberships',
    {subject: 'synthetic-operator', agency_id: agency.id, role: 'agency_owner', active: true});
  assert.equal(result.status, 409);
  assert.equal(f.db.prepare("SELECT role FROM mira_memberships WHERE subject='synthetic-operator'").get().role, 'operator');
  assert.equal(f.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='membership'").get().n, before);
});

test('operator audit query is paginated, scoped and not accessible to an agency', async t => {
  const f = await fixture(t); const {agency} = await f.activate();
  const path = '/admin/audit?entity_type=agency&entity_id=' + agency.id + '&limit=1';
  assert.equal((await f.call('synthetic-applicant', path)).status, 403);
  const first = await f.call('synthetic-operator', path);
  assert.equal(first.status, 200); assert.equal(first.body.records.length, 1);
  assert.equal(first.body.records[0].status, 'pending'); assert.equal(first.body.next_after_version, 0);
  const next = await f.call('synthetic-operator', path + '&after_version=0');
  assert.equal(next.body.records[0].status, 'active'); assert.equal(next.body.next_after_version, null);
  for (const suffix of ['&limit=1000', '&after_version=-2', '&after_version=1.5', '&unexpected=1']) {
    assert.equal((await f.call('synthetic-operator', path + suffix)).status, 400);
  }
  assert.deepEqual((await f.call('synthetic-operator', '/admin/audit?entity_type=agency&entity_id=synthetic-absent')).body.records, []);
  assert.equal((await f.call('synthetic-operator', '/admin/audit?entity_type=evidence&entity_id=x')).status, 400);
});


test('a snapshot restores into a separate local database with receipt, permissions and immutable audit', async t => {
 const f=await fixture(t),{id}=await f.activate();
 await f.call('synthetic-operator','/admin/memberships',{subject:'synthetic-applicant',agency_id:'synthetic-agency',role:'agency_owner',active:false});
 const before=f.db.prepare('SELECT COUNT(*) AS n FROM mira_events').get().n;
 f.restoreSnapshot();
 assert.equal(f.db.prepare('PRAGMA integrity_check').get().integrity_check,'ok');
 assert.deepEqual(f.db.prepare('PRAGMA foreign_key_check').all(),[]);
 assert.equal((await f.call('synthetic-applicant','/applications/'+id)).body.application.id,id);
 assert.equal((await f.call('synthetic-applicant','/profile')).status,403);
 assert.equal((await f.call('synthetic-other','/applications/'+id)).status,404);
 assert.equal(f.db.prepare('SELECT COUNT(*) AS n FROM mira_events').get().n,before);
 assert.throws(()=>f.db.prepare('DELETE FROM mira_events').run());
});
