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
 const env={MIRA_DB:db,APP_ORIGIN:origin,PUBLIC_INTAKE_ENABLED:'true',PUBLIC_INTAKE_PRIVACY_APPROVED:'true',PRIVACY_VERSION:'test-v1',PRIVACY_NOTICE_URL:origin+'/mira/agency-privacy.html',INTAKE_OPERATOR_SUBJECT:'operator-test',INTAKE_RATE_SECRET:'synthetic-secret-not-production-00000000000000',TURNSTILE_SITE_KEY:'synthetic-site-key',TURNSTILE_SECRET_KEY:'synthetic-secret'};
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
test('disabled by default and consent/security/operator configuration fail closed',async()=>{
 for(const [k,v] of [['PUBLIC_INTAKE_ENABLED',undefined],['PUBLIC_INTAKE_PRIVACY_APPROVED','false'],['PRIVACY_VERSION',''],['PRIVACY_NOTICE_URL','https://evil.test/x'],['INTAKE_RATE_SECRET','short'],['TURNSTILE_SITE_KEY',''],['INTAKE_OPERATOR_SUBJECT','']]){const s=setup();s.env[k]=v;assert.equal((await s.call()).status,503,k);assert.equal(n(s,'mira_intake_requests'),0);}
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
 assert.ok(!intakePage({...s.env,PRIVACY_VERSION:'\"><script>alert(1)</script>'}).includes('<script>alert(1)</script>'));
});
