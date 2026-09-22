/** Synthetic read-model fixtures; full imported schema/data smoke recorded separately. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {createResearchView,researchView} from '../cloudflare-worker/mira/research-view.mjs';
import {researchClient} from '../cloudflare-worker/mira/research-ui.mjs';
const origin='https://pilot.example.test',snapshot='MIRA-IMPORT-'+'a'.repeat(64);
function setup(){
 const db=new DatabaseSync(':memory:');db.exec(`
 CREATE TABLE mira_memberships(subject TEXT,role TEXT,active INTEGER);
 CREATE TABLE mira_research_summary(snapshot_id TEXT,source_commit TEXT,contains_private INTEGER,agency_candidates INTEGER,developer_groups INTEGER,research_project_links INTEGER);
 CREATE TABLE mira_published_research_entities(snapshot_id TEXT,kind TEXT,source_id TEXT,name TEXT,city TEXT,market TEXT,segment TEXT);
 CREATE TABLE mira_research_fields(snapshot_id TEXT,kind TEXT,source_id TEXT,field_key TEXT,occurrence INTEGER,value_json TEXT,evidence_json TEXT,verification_status TEXT,conversation_scope TEXT);
 CREATE TABLE mira_research_project_links(snapshot_id TEXT,developer_id TEXT,project_id TEXT,market TEXT,mapping_status TEXT);
 INSERT INTO mira_memberships VALUES ('operator','operator',1),('agency','agency_owner',1),('inactive','operator',0);
 `);
 db.prepare('INSERT INTO mira_research_summary VALUES (?,?,0,2,1,1)').run(snapshot,'c'.repeat(40));
 for(const [kind,id,name,city] of [['agency','A1','TEST Agency','TEST City'],['agency','A2','Other','Other'],['developer','D1','TEST Developer',null]])db.prepare('INSERT INTO mira_published_research_entities VALUES (?,?,?,?,?,?,?)').run(snapshot,kind,id,name,city,'phuket','research');
 db.prepare('INSERT INTO mira_research_fields VALUES (?,?,?,?,?,?,?,?,?)').run(snapshot,'agency','A1','email',0,'null','{"url":"https://example.test","checked_at":"2026-09-22"}','not_found','public_channel');
 db.prepare('INSERT INTO mira_research_project_links VALUES (?,?,?,?,?)').run(snapshot,'D1','P1','phuket','verified_public_sources');
 const env={APP_ORIGIN:origin,MIRA_RESEARCH_SNAPSHOT:snapshot,MIRA_DB:{prepare(sql){assert.match(sql,/^SELECT\b/i);return{bind(...args){const s=db.prepare(sql);return{first:async()=>s.get(...args)||null,all:async()=>({results:s.all(...args)})};}};}}};
 const handler=createResearchView(async r=>({subject:r.headers.get('Subject')||'operator'}));
 const call=async(path='',subject='operator',method='GET')=>{const r=await handler(new Request(origin+'/mira/api/admin/research'+path,{method,headers:{Subject:subject}}),env);return{status:r.status,body:await r.json(),headers:r.headers};};
 return{db,env,handler,call};
}
test('only active operator can read summary and contact records',async()=>{const s=setup();for(const who of ['agency','inactive','unknown'])assert.equal((await s.call('',who)).status,403);const r=await s.call();assert.equal(r.status,200);assert.equal(r.body.snapshot.agency_candidates,2);assert.match(r.headers.get('Cache-Control'),/no-store/);});
test('production export requires signed Access identity',async()=>{const s=setup();s.env.ACCESS_TEAM_DOMAIN='https://example.cloudflareaccess.com';s.env.ACCESS_AUDIENCE='synthetic';assert.equal((await researchView(new Request(origin+'/mira/api/admin/research'),s.env)).status,401);});
test('missing, incomplete and private snapshots fail closed',async()=>{const s=setup();s.env.MIRA_RESEARCH_SNAPSHOT='';assert.equal((await s.call()).status,503);s.env.MIRA_RESEARCH_SNAPSHOT='MIRA-IMPORT-'+'b'.repeat(64);assert.equal((await s.call()).status,503);s.env.MIRA_RESEARCH_SNAPSHOT=snapshot;s.db.exec('UPDATE mira_research_summary SET contains_private=1');assert.equal((await s.call()).status,503);});
test('query cannot select a different snapshot or leak its records',async()=>{const s=setup();s.db.prepare('INSERT INTO mira_published_research_entities VALUES (?,?,?,?,?,?,?)').run('other','agency','PRIVATE','other-snapshot-secret','TEST City',null,null);const r=await s.call('/entities?kind=agency&snapshot=other');assert.equal(r.body.records.length,2);assert.ok(!JSON.stringify(r.body).includes('other-snapshot-secret'));});
test('pagination, kind and literal substring search are bounded',async()=>{const s=setup();const a=await s.call('/entities?kind=agency&limit=1');assert.equal(a.body.next_cursor,'A1');const b=await s.call('/entities?kind=agency&limit=1&cursor=A1');assert.equal(b.body.records[0].source_id,'A2');assert.equal(b.body.next_cursor,null);assert.equal((await s.call('/entities?kind=agency&q=TEST')).body.records.length,1);assert.equal((await s.call('/entities?kind=agency&q=%25')).body.records.length,0);assert.equal((await s.call('/entities?kind=agency&city=Other')).body.records.length,1);});
test('invalid limits/fields and SQL injection strings never widen result',async()=>{const s=setup();for(const q of ['kind=agency&limit=0','kind=agency&limit=101','kind=agency&limit=NaN','kind=other'])assert.equal((await s.call('/entities?'+q)).status,400);assert.equal((await s.call('/entities?kind=agency&q='+encodeURIComponent("' OR 1=1 --"))).body.records.length,0);});
test('detail preserves missing evidence and channel semantics, no raw payload',async()=>{const s=setup(),r=await s.call('/entity?kind=agency&id=A1');assert.equal(r.body.fields[0].value,null);assert.equal(r.body.fields[0].verification_status,'not_found');assert.equal(r.body.fields[0].conversation_scope,'public_channel');assert.equal(r.body.fields[0].evidence.checked_at,'2026-09-22');assert.equal(r.body.entity.row_json,undefined);});
test('detail scopes kind/id and never exposes native lineage',async()=>{const s=setup();assert.equal((await s.call('/entity?kind=developer&id=A1')).status,404);assert.equal((await s.call('/entity?kind=agency&id=missing')).status,404);assert.equal((await s.call('/native-lineage')).status,404);});
test('developer links retain source status and stay paginated research records',async()=>{const s=setup(),r=await s.call('/links?kind=developer&id=D1');assert.equal(r.body.records[0].mapping_status,'verified_public_sources');assert.equal(r.body.records[0].available,undefined);assert.equal((await s.call('/links?kind=agency&id=A1')).status,400);});
test('read-only route rejects POST and foreign host',async()=>{const s=setup();assert.equal((await s.call('/entities','operator','POST')).status,405);assert.equal((await s.handler(new Request('https://evil.test/mira/research/'),s.env)).status,421);});
test('both HTML and script require operator; rendered values use textContent',async()=>{const s=setup();for(const p of ['/mira/research/','/mira/research/client.mjs']){const r=await s.handler(new Request(origin+p,{headers:{Subject:'agency'}}),s.env);assert.equal(r.status,403);assert.equal((await s.handler(new Request(origin+p),s.env)).status,200);}assert.ok(!researchClient.includes('innerHTML'));assert.match(researchClient,/textContent/);assert.match(researchClient,/credentials:'same-origin'/);});
