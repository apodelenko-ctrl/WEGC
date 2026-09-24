/** SYNTHETIC fixtures only; no real contacts, account provisioning or external calls. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createPublicIntake} from '../cloudflare-worker/mira/public-intake.mjs';
import {createHandler} from '../cloudflare-worker/mira/worker.mjs';
import site from '../cloudflare-worker/mira/site-worker.mjs';
import {intakePage,intakeClient} from '../cloudflare-worker/mira/intake-ui.mjs';
const origin='https://pilot.example.test';
const migrations=new URL('../cloudflare-worker/mira/migrations/',import.meta.url);
const schema=readdirSync(migrations).filter(f=>f.endsWith('.sql')).sort().map(f=>readFileSync(new URL(f,migrations),'utf8')).join('\n');
class D1{
 constructor(path=':memory:',initialize=true){this.db=new DatabaseSync(path);if(initialize)this.db.exec(schema);}
 prepare(sql){return{bind:(...args)=>{const q=this.db.prepare(sql);return{first:async()=>q.get(...args)||null,all:async()=>({results:q.all(...args)}),run:async()=>({meta:{changes:Number(q.run(...args).changes)}})};}};}
 async batch(statements){const execute=async()=>{this.db.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());this.db.exec('COMMIT');return r;}catch(e){this.db.exec('ROLLBACK');throw e;}};const promise=(this.queue||Promise.resolve()).then(execute);this.queue=promise.catch(()=>{});return promise;}
}
const data={company:'SYNTHETIC Agency',city:'TEST City',name:'TEST Operator',email:'synthetic@example.test',consent_version:'test-v1',challenge:'synthetic-challenge'};
function setup(path){
 const db=new D1(path);db.db.exec("INSERT INTO mira_memberships VALUES ('operator-test',NULL,'operator',1)");
 const env={MIRA_DB:db,APP_ORIGIN:origin,PUBLIC_INTAKE_ENABLED:'true',PUBLIC_INTAKE_PRIVACY_APPROVED:'true',PUBLIC_INTAKE_PRIVACY_VERSION:'test-v1',PUBLIC_INTAKE_PRIVACY_NOTICE_URL:origin+'/mira/agency-privacy.html',INTAKE_OPERATOR_SUBJECT:'operator-test',INTAKE_RATE_SECRET:'synthetic-secret-not-production-00000000000000',TURNSTILE_SITE_KEY:'synthetic-site-key',TURNSTILE_SECRET_KEY:'synthetic-secret'};
 let calls=0,validation={success:true,hostname:'pilot.example.test',action:'mira_intake'};
 const handler=createPublicIntake(async(url,opts)=>{calls++;assert.equal(url,'https://challenges.cloudflare.com/turnstile/v0/siteverify');assert.equal(opts.redirect,'manual');return Response.json(validation);});
 const key=crypto.randomUUID(),token='a'.repeat(64);
 const request=(path,body,headers={})=>new Request(origin+'/mira/request/'+path,{method:body===undefined?'GET':'POST',headers:{Origin:origin,'Content-Type':'application/json','CF-Connecting-IP':'192.0.2.1',Authorization:'Bearer '+token,'Idempotency-Key':key,...headers},body:body===undefined?undefined:typeof body==='string'?body:JSON.stringify(body)});
 const call=async(path='submit',body=data,headers={})=>{const r=await handler(request(path,body,headers),env);return{status:r.status,body:await r.json(),headers:r.headers};};
 const admin=createHandler(async req=>({subject:req.headers.get('Test-Subject')||'operator-test',email:'operator@example.test'}));
 const review=async(id,body,headers={})=>{const r=await admin(new Request(origin+'/mira/api/admin/intake/'+id+'/review',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json',...headers},body:JSON.stringify(body)}),env);return{status:r.status,body:await r.json()};};
 return{db,env,handler,call,request,review,admin,key,token,get calls(){return calls;},set validation(v){validation=v;}};
}
const n=(s,t)=>s.db.db.prepare(`SELECT COUNT(*) AS n FROM ${t}`).get().n;
test('submission pause preserves replay, private receipt and page when operator goes offline',async()=>{
 const s=setup(),first=await s.call();
 s.env.PUBLIC_INTAKE_SUBMISSIONS_PAUSED='true';s.db.db.exec('UPDATE mira_memberships SET active=0');
 const replay=await s.call();assert.equal(replay.status,200);assert.equal(replay.body.id,first.body.id);
 assert.equal((await s.call('submit',data,{'Idempotency-Key':crypto.randomUUID()})).body.error,'intake_submissions_paused');
 assert.equal((await s.call('status',{id:first.body.id})).status,200);
 const page=await s.handler(new Request(origin+'/mira/request/'),s.env);assert.equal(page.status,200);assert.match(await page.text(),/data-paused="true"/);
 assert.equal(n(s,'mira_intake_requests'),1);assert.equal(s.calls,1);
 s.env.PUBLIC_INTAKE_SUBMISSIONS_PAUSED='false';s.db.db.exec('UPDATE mira_memberships SET active=1');
 assert.equal((await s.call('submit',data,{'Idempotency-Key':crypto.randomUUID()})).status,201);
});
test('public consent cannot fall back to the invitation policy or change invitation settings',async()=>{
 const s=setup();s.env.PRIVACY_VERSION='invitation-v1';s.env.PRIVACY_NOTICE_URL=origin+'/invitation.html';
 assert.equal((await s.call('submit',{...data,consent_version:'invitation-v1'})).status,400);
 assert.equal((await s.call()).status,201);assert.equal(s.env.PRIVACY_VERSION,'invitation-v1');
 delete s.env.PUBLIC_INTAKE_PRIVACY_VERSION;
 assert.equal((await s.call()).body.error,'intake_privacy_not_approved');
});
test('newest queue pagination is stable for timestamp ties and arrivals between pages',async()=>{
 const s=setup(),ids=['00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000002','ffffffff-ffff-4fff-8fff-ffffffffffff'];
 const insert=s.db.db.prepare(`INSERT INTO mira_intake_requests(id,idempotency_key,request_hash,token_hash,company,city,name,email,consent_version,assigned_subject,created_at,updated_at,last_event_id) VALUES (?,?,'test','test','TEST','TEST','TEST','synthetic@example.test','test-v1','operator-test',?,?,?)`);
 for(const [i,id] of ids.entries()){const time=i===2?'2026-09-23T01:00:00.000Z':'2026-09-24T01:00:00.000Z';insert.run(id,crypto.randomUUID(),time,time,id);}
 const a=(await adminCall(s,'?limit=1')).body;assert.equal(a.records[0].id,ids[1]);
 const newId=crypto.randomUUID();insert.run(newId,crypto.randomUUID(),'2026-09-25T01:00:00.000Z','2026-09-25T01:00:00.000Z',newId);
 const b=(await adminCall(s,'?'+new URLSearchParams({limit:'2',cursor:a.next_cursor}))).body;
 assert.deepEqual(b.records.map(r=>r.id),[ids[0],ids[2]]);assert.equal(b.next_cursor,null);
 assert.equal((await adminCall(s,'?limit=1')).body.records[0].id,newId);
 assert.equal((await adminCall(s,'?cursor=broken')).status,400);
});
test('operator summary works while public intake is disabled and never exposes contacts',async()=>{
 const s=setup(),r=await s.call();delete s.env.PUBLIC_INTAKE_ENABLED;
 const b=(await adminCall(s,'/summary')).body;assert.equal(b.public_intake_enabled,false);assert.equal(b.records[0].count,1);
 assert.equal(b.records[0].status,'received');assert.equal(b.records[0].oldest_at,r.body.received_at);
 assert.ok(!JSON.stringify(b).includes(data.email));assert.equal((await adminCall(s,'/summary',undefined,'uninvited')).status,403);
});
async function adminCall(s,path='',body,subject='operator-test'){
 const r=await s.admin(new Request(origin+'/mira/api/admin/intake'+path,{method:body?'POST':'GET',headers:{Origin:origin,'Content-Type':'application/json','Test-Subject':subject},...(body?{body:JSON.stringify(body)}:{})}),s.env);
 return{status:r.status,body:await r.json()};
}
test('assignment is active-operator-only, versioned, audited and never grants membership',async()=>{
 const s=setup(),r=await s.call(),id=r.body.id;
 s.db.db.exec("INSERT INTO mira_memberships VALUES ('operator-second',NULL,'operator',1),('operator-inactive',NULL,'operator',0)");
 assert.equal((await adminCall(s,'/'+id+'/assign',{version:0,assigned_subject:'operator-inactive'})).status,409);
 assert.equal((await adminCall(s,'/'+id+'/assign',{version:0,assigned_subject:'uninvited'})).status,409);
 const a=await adminCall(s,'/'+id+'/assign',{version:0,assigned_subject:'operator-second'});assert.equal(a.status,200);assert.equal(a.body.published_to_receipt,false);
 assert.equal((await adminCall(s,'/'+id)).body.assigned_subject,'operator-second');
 const h=(await adminCall(s,'/'+id+'/history')).body.records;assert.deepEqual(h.map(x=>x.event_kind),['received','assign']);assert.equal(h[1].assigned_subject,'operator-second');assert.equal(n(s,'mira_memberships'),3);
 assert.equal((await adminCall(s,'/'+id+'/assign',{version:0,assigned_subject:'operator-second'})).status,409);assert.equal(n(s,'mira_intake_events'),2);
});
test('assignment racing review has one winning version and one history event',async()=>{
 const s=setup(),r=await s.call();s.db.db.exec("INSERT INTO mira_memberships VALUES ('operator-second',NULL,'operator',1)");
 const a=await Promise.all([adminCall(s,'/'+r.body.id+'/assign',{version:0,assigned_subject:'operator-second'}),s.review(r.body.id,{version:0,status:'review',response:null})]);
 assert.deepEqual(a.map(x=>x.status).sort(),[200,409]);assert.equal(n(s,'mira_intake_events'),2);
});
test('status-only review retains published response and history marks only explicit publications',async()=>{
 const s=setup(),r=await s.call(),id=r.body.id;
 await s.review(id,{version:0,status:'responded',response:'SYNTHETIC published reply'});
 const update=await s.review(id,{version:1,status:'review',response:null});assert.equal(update.status,200);assert.equal(update.body.published_to_receipt,false);
 assert.equal((await s.call('status',{id})).body.response,'SYNTHETIC published reply');
 const h=(await adminCall(s,'/'+id+'/history')).body.records;assert.deepEqual(h.map(x=>x.response_published),[0,1,0]);assert.equal(h[2].public_response,null);
});
test('history is bounded, chronological and excludes receipt secrets',async()=>{
 const s=setup(),r=await s.call(),id=r.body.id;await s.review(id,{version:0,status:'review',response:null});
 const a=(await adminCall(s,'/'+id+'/history?limit=1')).body;assert.equal(a.records[0].version,0);assert.equal(a.next_after_version,0);
 const b=(await adminCall(s,'/'+id+'/history?after_version=0')).body;assert.equal(b.records[0].version,1);assert.equal(b.next_after_version,null);
 assert.equal((await adminCall(s,'/'+id+'/history?limit=101')).status,400);
 assert.equal((await adminCall(s,'/'+id+'/history',undefined,'uninvited')).status,403);
 assert.ok(!JSON.stringify(a).includes('token_hash'));assert.ok(!JSON.stringify(a).includes('request_hash'));
});
test('UI, script and operator directory require the existing active operator path',async()=>{
 const s=setup();for(const path of ['/view','/client.mjs','/operators']){
  const r=await s.admin(new Request(origin+'/mira/api/admin/intake'+path,{headers:{'Test-Subject':'uninvited'}}),s.env);assert.equal(r.status,403);
 }
 const r=await s.admin(new Request(origin+'/mira/api/admin/intake/view'),s.env);assert.equal(r.status,200);assert.match(r.headers.get('Cache-Control'),/no-store/);assert.match(await r.text(),/Входящие запросы/);
 const d=(await adminCall(s,'/operators')).body;assert.equal(d.current_subject,'operator-test');assert.equal(d.records.length,1);
});
test('failed assignment audit rolls back row and version',async()=>{
 const s=setup(),r=await s.call(),id=r.body.id;s.db.db.exec("INSERT INTO mira_memberships VALUES ('operator-second',NULL,'operator',1); CREATE TRIGGER synthetic_assignment_failure BEFORE INSERT ON mira_intake_events WHEN NEW.event_kind='assign' BEGIN SELECT RAISE(ABORT,'synthetic'); END;");
 assert.equal((await adminCall(s,'/'+id+'/assign',{version:0,assigned_subject:'operator-second'})).status,500);
 const row=(await adminCall(s,'/'+id)).body;assert.equal(row.assigned_subject,'operator-test');assert.equal(row.version,0);assert.equal(n(s,'mira_intake_events'),1);
});
test('public receipt never reveals operator identity or internal history',async()=>{
 const s=setup(),r=await s.call();await s.review(r.body.id,{version:0,status:'responded',response:'SYNTHETIC reply'});
 const b=(await s.call('status',{id:r.body.id})).body;for(const k of ['actor','assigned_subject','email','history','event_kind'])assert.equal(b[k],undefined);
 assert.ok(!JSON.stringify(b).includes('operator-test'));
});
test('disabled by default and consent/security/operator configuration fail closed',async()=>{
 for(const [k,v] of [['PUBLIC_INTAKE_ENABLED',undefined],['PUBLIC_INTAKE_PRIVACY_APPROVED','false'],['PUBLIC_INTAKE_PRIVACY_VERSION',''],['PUBLIC_INTAKE_PRIVACY_NOTICE_URL','https://evil.test/x'],['INTAKE_RATE_SECRET','short'],['TURNSTILE_SITE_KEY',''],['INTAKE_OPERATOR_SUBJECT','']]){const s=setup();s.env[k]=v;assert.equal((await s.call()).status,503,k);assert.equal(n(s,'mira_intake_requests'),0);}
});
test('durable receipt has unverified email and operator assignment, never activation',async()=>{
 const s=setup(),r=await s.call();assert.equal(r.status,201);assert.equal(r.body.status,'received');const row=s.db.db.prepare('SELECT * FROM mira_intake_requests').get();assert.equal(row.assigned_subject,'operator-test');assert.equal(row.email_verified,0);assert.notEqual(row.token_hash,s.token);assert.equal(n(s,'mira_intake_events'),1);
 for(const table of ['mira_agencies','mira_applications','mira_leads','mira_projects'])assert.equal(n(s,table),0);assert.equal(n(s,'mira_memberships'),1);
 assert.equal(r.body.email,undefined);assert.equal(r.body.token_hash,undefined);assert.match(r.headers.get('Cache-Control'),/no-store/);
});
test('same request replay returns one receipt and does not revalidate single-use challenge',async()=>{
 const s=setup(),a=await s.call(),b=await s.call();assert.equal(b.status,200);assert.equal(b.body.id,a.body.id);assert.equal(s.calls,1);assert.equal(n(s,'mira_intake_requests'),1);assert.equal(n(s,'mira_intake_events'),1);
});
test('replay rejects changed payload and wrong secret even with same key',async()=>{
 const s=setup();await s.call();assert.equal((await s.call('submit',{...data,company:'Changed'})).status,409);assert.equal((await s.call('submit',data,{Authorization:'Bearer '+'b'.repeat(64)})).status,409);assert.equal(n(s,'mira_intake_requests'),1);
});
test('concurrent identical attempts create one queue record and event',async()=>{
 const s=setup(),r=await Promise.all([s.call(),s.call()]);assert.deepEqual(r.map(x=>x.status).sort(),[200,201]);assert.equal(r[0].body.id,r[1].body.id);assert.equal(n(s,'mira_intake_events'),1);
});
test('request+event rollback on injected storage failure; safe retry succeeds',async()=>{
 const s=setup();s.db.db.exec("CREATE TRIGGER synthetic_failure BEFORE INSERT ON mira_intake_events BEGIN SELECT RAISE(ABORT,'synthetic'); END;");assert.equal((await s.call()).status,500);assert.equal(n(s,'mira_intake_requests'),0);s.db.db.exec('DROP TRIGGER synthetic_failure');assert.equal((await s.call()).status,201);
});
test('wrong Origin, host, method and unsigned forwarded address rejected',async()=>{
 const s=setup();assert.equal((await s.call('submit',data,{Origin:'https://evil.test'})).status,403);assert.equal((await s.call('submit',data,{'CF-Connecting-IP':'','X-Forwarded-For':'192.0.2.2'})).status,503);
 assert.equal((await s.handler(new Request('https://evil.test/mira/request/'),s.env)).status,421);assert.equal((await s.handler(new Request(origin+'/mira/request/submit'),s.env)).status,405);
});
test('strict fields, consent, email, body limit and content type validation',async()=>{
 for(const body of [{...data,company:''},{...data,email:'invalid'},{...data,consent_version:'old'},{...data,agency_id:'forged'},{...data,name:'bad\nvalue'},null,[]]){const s=setup();assert.equal((await s.call('submit',JSON.stringify(body))).status,400);assert.equal(n(s,'mira_intake_requests'),0);}
 const s=setup();assert.equal((await s.call('submit','x'.repeat(8193))).status,413);assert.equal((await s.call('submit','{')).status,400);assert.equal((await s.call('submit',data,{'Content-Type':'text/plain'})).status,415);
});
test('server-side challenge success, exact hostname and action are all required',async()=>{
 for(const v of [{success:false},{success:true,hostname:'evil.test',action:'mira_intake'},{success:true,hostname:'pilot.example.test',action:'other'}]){const s=setup();s.validation=v;assert.equal((await s.call()).status,400);assert.equal(n(s,'mira_intake_requests'),0);}
});
test('challenge transport failure is not a successful receipt and makes no intake record',async()=>{
 const s=setup(),h=createPublicIntake(async()=>{throw Error('timeout');});assert.equal((await h(s.request('submit',data),s.env)).status,503);assert.equal(n(s,'mira_intake_requests'),0);
});
test('inactive or missing designated operator blocks intake without provisioning one',async()=>{
 const s=setup();s.db.db.exec('UPDATE mira_memberships SET active=0');assert.equal((await s.call()).status,503);assert.equal(s.calls,0);assert.equal(n(s,'mira_intake_requests'),0);
});
test('atomic per-IP rate limit blocks repeated attempts before further Siteverify',async()=>{
 const s=setup();s.validation={success:false};for(let i=0;i<10;i++)assert.equal((await s.call()).status,400);assert.equal((await s.call()).status,429);assert.equal(s.calls,10);
 assert.ok(s.db.db.prepare('SELECT subject_hash FROM mira_intake_limits').all().every(r=>!r.subject_hash.includes('192.0.2.1')));
});
test('rotating addresses cannot evade global bounded quota',async()=>{
 const s=setup(),bucket=Math.floor(Date.now()/3600000);s.db.db.prepare('INSERT INTO mira_intake_limits VALUES (?,?,?)').run('global:submit',bucket,300);assert.equal((await s.call('submit',data,{'CF-Connecting-IP':'192.0.2.200'})).status,429);assert.equal(s.calls,0);
});
test('receipt requires secret outside URL; wrong ID or token returns same 404',async()=>{
 const s=setup(),r=await s.call();assert.equal((await s.call('status',{id:r.body.id},{Authorization:''})).status,401);assert.equal((await s.call('status',{id:r.body.id},{Authorization:'Bearer '+'b'.repeat(64)})).status,404);assert.equal((await s.call('status',{id:crypto.randomUUID()})).status,404);assert.equal((await s.call('status',{id:r.body.id})).status,200);
});
test('operator publishes response to private receipt; no email send or verified email claim',async()=>{
 const s=setup(),r=await s.call(),review=await s.review(r.body.id,{version:0,status:'responded',response:'SYNTHETIC operator response'});assert.equal(review.status,200);assert.equal(review.body.external_send,false);
 const b=(await s.call('status',{id:r.body.id})).body;assert.equal(b.response,'SYNTHETIC operator response');assert.equal(b.version,1);assert.equal(b.email,undefined);assert.equal(n(s,'mira_intake_events'),2);assert.equal(n(s,'mira_events'),0);
});
test('concurrent reviews use compare-and-swap and cannot duplicate audit',async()=>{
 const s=setup(),r=await s.call(),b={version:0,status:'review',response:null};const results=await Promise.all([s.review(r.body.id,b),s.review(r.body.id,b)]);assert.deepEqual(results.map(r=>r.status).sort(),[200,409]);assert.equal(n(s,'mira_intake_events'),2);
});
test('unsupported status, blank response and stale update rejected',async()=>{
 const s=setup(),r=await s.call();assert.equal((await s.review(r.body.id,{version:0,status:'active',response:null})).status,409);assert.equal((await s.review(r.body.id,{version:0,status:'responded',response:null})).status,400);assert.equal((await s.review(r.body.id,{version:8,status:'review',response:null})).status,409);
});
test('closed request cannot be silently reopened or promoted to membership',async()=>{
 const s=setup(),r=await s.call();assert.equal((await s.review(r.body.id,{version:0,status:'closed',response:'TEST closed'})).status,200);assert.equal((await s.review(r.body.id,{version:1,status:'review',response:null})).status,409);assert.equal(n(s,'mira_memberships'),1);
});
test('queue is bounded and redacts secret/hash; applicant and inactive operator denied',async()=>{
 const s=setup();await s.call();const get=async(subject,suffix='')=>s.admin(new Request(origin+'/mira/api/admin/intake'+suffix,{headers:{'Test-Subject':subject}}),s.env);
 const res=await get('operator-test'),b=await res.json();assert.equal(res.status,200);assert.equal(b.records.length,1);assert.equal(b.records[0].token_hash,undefined);assert.equal(b.records[0].request_hash,undefined);assert.equal((await get('operator-test','?limit=101')).status,400);assert.equal((await get('uninvited')).status,403);s.db.db.exec('UPDATE mira_memberships SET active=0');assert.equal((await get('operator-test')).status,403);
});
test('deployed entry remains pinned to Access for admin while intake defaults disabled',async()=>{
 const s=setup();s.env.ACCESS_TEAM_DOMAIN='https://test.cloudflareaccess.com';s.env.ACCESS_AUDIENCE='synthetic';const r=await site.fetch(new Request(origin+'/mira/api/admin/intake'),s.env);assert.equal(r.status,401);delete s.env.PUBLIC_INTAKE_ENABLED;assert.equal((await site.fetch(new Request(origin+'/mira/request/'),s.env)).status,503);
});
test('immutable source payload and audit cannot be overwritten',async()=>{
 const s=setup();await s.call();assert.throws(()=>s.db.db.exec("UPDATE mira_intake_requests SET email='different@example.test'"),/immutable/);assert.throws(()=>s.db.db.exec('DELETE FROM mira_intake_events'),/immutable/);assert.throws(()=>s.db.db.exec("UPDATE mira_intake_events SET status='active'"),/immutable/);
});
test('disk-backed restart preserves receipt and operator response',async()=>{
 const dir=mkdtempSync(join(tmpdir(),'mira-intake-test-')),path=join(dir,'db.sqlite');try{const s=setup(path),r=await s.call();await s.review(r.body.id,{version:0,status:'responded',response:'TEST persistent'});s.db.db.close();const restored=new D1(path,false);s.env.MIRA_DB=restored;const result=await s.call('status',{id:r.body.id});assert.equal(result.body.response,'TEST persistent');assert.equal(result.body.version,1);restored.db.close();}finally{rmSync(dir,{recursive:true,force:true});}
});
test('form uses explicit consent, separate route and no untrusted HTML insertion',async()=>{
 const s=setup(),page=await s.handler(new Request(origin+'/mira/request/'),s.env);assert.equal(page.status,200);const html=await page.text();assert.match(html,/type="checkbox" required/);assert.match(html,/data-action="mira_intake"/);assert.match(page.headers.get('Content-Security-Policy'),/frame-ancestors 'none'/);assert.ok(!intakeClient.includes('innerHTML'));assert.match(intakeClient,/textContent/);assert.match(intakeClient,/sessionStorage/);assert.match(intakeClient,/credentials:'omit'/);
 assert.ok(!intakePage({...s.env,PUBLIC_INTAKE_PRIVACY_VERSION:'\"><script>alert(1)</script>'}).includes('<script>alert(1)</script>'));
});

test('confirmed operator erasure removes contacts and every reply; receipt/replay become 410',async()=>{
 const s=setup(),r=await s.call(),id=r.body.id;await s.review(id,{version:0,status:'responded',response:'SYNTHETIC personal reply'});
 const body={version:1,confirmation:'erase_contact_and_history'};
 assert.equal((await adminCall(s,'/'+id+'/erase',body,'uninvited')).status,403);
 assert.equal((await adminCall(s,'/'+id+'/erase',{...body,confirmation:'no'})).status,400);
 assert.equal((await adminCall(s,'/'+id+'/erase',{...body,version:0})).status,409);assert.equal(n(s,'mira_intake_events'),2);
 assert.equal((await adminCall(s,'/'+id+'/erase',body)).status,200);assert.equal(n(s,'mira_intake_requests'),0);assert.equal(n(s,'mira_intake_events'),0);
 assert.equal((await s.call('status',{id})).status,410);assert.equal((await s.call()).status,410);assert.equal(s.calls,1);
 assert.equal((await s.call('status',{id},{Authorization:'Bearer '+'b'.repeat(64)})).status,404);
 const ledger=JSON.stringify(s.db.db.prepare('SELECT * FROM mira_intake_erasure').all());for(const sensitive of [data.email,data.company,data.name,'SYNTHETIC personal reply'])assert.ok(!ledger.includes(sensitive));
 assert.equal(n(s,'mira_memberships'),1);
});
test('erasure is atomic when reply deletion fails',async()=>{
 const s=setup(),r=await s.call();s.db.db.exec("CREATE TRIGGER synthetic_erase_failure BEFORE DELETE ON mira_intake_events BEGIN SELECT RAISE(ABORT,'synthetic'); END;");
 assert.equal((await adminCall(s,'/'+r.body.id+'/erase',{version:0,confirmation:'erase_contact_and_history'})).status,500);
 assert.equal(n(s,'mira_intake_requests'),1);assert.equal(n(s,'mira_intake_events'),1);assert.equal(n(s,'mira_intake_erasure'),0);
});
test('a concurrent in-flight submission cannot resurrect an erased idempotency key',async()=>{
 const s=setup(),handler=createPublicIntake(async()=>{const first=await s.call();await adminCall(s,'/'+first.body.id+'/erase',{version:0,confirmation:'erase_contact_and_history'});return Response.json({success:true,hostname:'pilot.example.test',action:'mira_intake'});});
 const result=await handler(s.request('submit',data),s.env);assert.equal(result.status,500);assert.equal(n(s,'mira_intake_requests'),0);assert.equal(n(s,'mira_intake_erasure'),1);
});
test('retention removes expired contact/history but preserves recent requests and short-lived tombstones',async()=>{
 const {expireIntakes}=await import('../cloudflare-worker/mira/intake-retention.mjs');const s=setup(),current=await s.call(),oldId=crypto.randomUUID();
 const old=new Date();old.setUTCFullYear(old.getUTCFullYear()-3);const time=old.toISOString();
 s.db.db.prepare(`INSERT INTO mira_intake_requests(id,idempotency_key,request_hash,token_hash,company,city,name,email,consent_version,assigned_subject,created_at,updated_at,last_event_id) VALUES (?,?,'test','test','TEST','TEST','TEST','synthetic@example.test','test-v1','operator-test',?,?,?)`).run(oldId,crypto.randomUUID(),time,time,oldId);
 s.db.db.prepare(`INSERT INTO mira_intake_events(id,request_id,actor,status,version,created_at) VALUES (?,?,'public_request','received',0,?)`).run(oldId,oldId,time);
 assert.equal((await expireIntakes(s.env)).enabled,false);assert.equal(n(s,'mira_intake_requests'),2);
 s.env.INTAKE_RETENTION_ENABLED='true';assert.equal((await expireIntakes(s.env)).erased,1);assert.equal(n(s,'mira_intake_requests'),1);assert.equal(n(s,'mira_intake_events'),1);
 assert.equal((await s.call('status',{id:current.body.id})).status,200);assert.equal(n(s,'mira_intake_erasure'),1);
 assert.equal((await expireIntakes(s.env)).erased,0);assert.equal(n(s,'mira_intake_erasure'),1);
});
test('public privacy notice is accessible before activation and describes the separate unverified request',async()=>{
 const s=setup();delete s.env.PUBLIC_INTAKE_ENABLED;const r=await s.handler(new Request(origin+'/mira/request/privacy'),s.env);assert.equal(r.status,200);const html=await r.text();assert.match(html,/mira-public-2026-09-24-v1/);assert.match(html,/Email в этой форме не подтверждается/);assert.match(r.headers.get('Cache-Control'),/no-store/);
});
