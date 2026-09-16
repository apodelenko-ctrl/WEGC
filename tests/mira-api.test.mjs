/** All names, IDs and amounts in these tests are SYNTHETIC fixtures, not business facts. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import worker,{createHandler} from '../cloudflare-worker/mira/worker.mjs';
import {verifyAccess} from '../cloudflare-worker/mira/auth.mjs';
import {decimalAmount} from '../cloudflare-worker/mira/rules.mjs';
const migrations=new URL('../cloudflare-worker/mira/migrations/',import.meta.url);
const schema=readdirSync(migrations).filter(f=>f.endsWith('.sql')).sort().map(f=>readFileSync(new URL(f,migrations),'utf8')).join('\n');
const past=new Date(Date.now()-60000).toISOString(),future=new Date(Date.now()+86400000).toISOString();
class D1 {
 constructor(){this.db=new DatabaseSync(':memory:');this.db.exec(schema);}
 prepare(sql) {
  const d=this;
  return {bind(...args) {
   const prepared=d.db.prepare(sql);
   return {sql,args,
    async first(){return prepared.get(...args)||null;},
    async all(){return {results:prepared.all(...args)};},
    async run(){const r=prepared.run(...args);return {success:true,meta:{changes:Number(r.changes)}};}
   };
  }};
 }
 async batch(statements){
  const perform=async()=>{this.db.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());this.db.exec('COMMIT');return r;}catch(e){this.db.exec('ROLLBACK');throw e;}};
  const result=(this.queue||Promise.resolve()).then(perform);this.queue=result.catch(()=>{});return result;
 }
}
function setup(){
 const db=new D1(),env={MIRA_DB:db,APP_ORIGIN:'https://mira.test',APPLICATIONS_ENABLED:'true',PRIVACY_VERSION:'test-consent-v1',PRIVACY_NOTICE_URL:'https://mira.test/privacy-test'};
 db.db.exec(`INSERT INTO mira_agencies (id,name,city,status,agreement_ref,created_at) VALUES ('agency-a','TEST A','TEST','active','EVID-agency-a','${past}'),('agency-b','TEST B','TEST','active','EVID-agency-b','${past}');
 INSERT INTO mira_memberships VALUES ('owner-a','agency-a','agency_owner',1),('broker-a','agency-a','broker',1),('owner-b','agency-b','agency_owner',1),('operator',NULL,'operator',1);
 INSERT INTO mira_projects (id,name,market,developer_family,legal_seller,enabled,agreement_ref,inventory_ref,registration_rules_ref,commission_schedule_ref,updated_at) VALUES ('project-1','TEST PROJECT','phuket','TEST GROUP','TEST SELLER',1,'EVID-agreement','EVID-inventory','EVID-rules','EVID-commission','${past}');
 INSERT INTO mira_agency_projects VALUES ('agency-a','project-1'),('agency-b','project-1');`);
 const addEvidence=(id,kind,{agency=null,project=null,entity=null,expires=null,facts={}}={})=>db.db.prepare('INSERT INTO mira_evidence (id,kind,project_id,agency_id,entity_id,storage_ref,facts_json,verified,verified_by,verified_at,expires_at) VALUES (?,?,?,?,?,?,?,1,?,?,?)').run(id,kind,project,agency,entity,'vault:TEST',JSON.stringify(facts),'operator',past,expires);
 addEvidence('EVID-agency-a','agency_agreement',{agency:'agency-a'});addEvidence('EVID-agency-b','agency_agreement',{agency:'agency-b'});
 for(const [id,kind] of [['agreement','project_agreement'],['inventory','inventory'],['rules','registration_rules'],['commission','commission_schedule']])addEvidence('EVID-'+id,kind,{project:'project-1',expires:kind==='inventory'?future:null,facts:kind==='project_agreement'?{legal_seller:'TEST SELLER'}:{}});
 addEvidence('EVID-client-a','client_consent',{agency:'agency-a',project:'project-1',entity:'CLIENT-TEST'});
 addEvidence('EVID-client-b','client_consent',{agency:'agency-b',project:'project-1',entity:'CLIENT-TEST'});
 const handler=createHandler(async req=>{const subject=req.headers.get('Test-Subject');if(!subject)throw Error('test requires subject');return {subject,email:subject+'@example.test'};});
 const call=async(subject,path,body,headers={})=>{const r=await handler(new Request('https://mira.test/mira/api'+path,{method:body===undefined?'GET':'POST',headers:{'Test-Subject':subject,Origin:env.APP_ORIGIN,'Content-Type':'application/json',...headers},body:body===undefined?undefined:JSON.stringify(body)}),env);return {status:r.status,body:await r.json()};};
 return {db,env,call,addEvidence};
}
const leadBody={project_id:'project-1',client_ref:'CLIENT-TEST',consent_ref:'EVID-client-a'};
test('production worker fails closed without configured DB or identity',async()=>{
 const r=await worker.fetch(new Request('https://mira.test/mira/api/leads'),{});assert.equal(r.status,503);
 const {env}=setup();const r2=await worker.fetch(new Request('https://mira.test/mira/api/leads'),env);assert.equal(r2.status,503);
});
test('health is read-only and cannot claim operational readiness',async()=>{const r=await worker.fetch(new Request('https://mira.test/mira/api/health'),{});const b=await r.json();assert.equal(b.configured,false);assert.equal(b.outreach_enabled,false);});
test('application receives durable receipt and idempotent replay',async()=>{
 const {call,db}=setup();const data={company:'TEST',city:'TEST',name:'TEST',format:'agency',demand:'learning',markets:['phuket'],consent_version:'test-consent-v1'};
 const a=await call('applicant','/applications',data,{'Idempotency-Key':'request-test'});assert.equal(a.status,201);assert.equal(a.body.status,'received');
 const b=await call('applicant','/applications',data,{'Idempotency-Key':'request-test'});assert.equal(b.status,200);assert.equal(b.body.id,a.body.id);
 const c=await call('applicant','/applications',{...data,company:'CHANGED'},{'Idempotency-Key':'request-test'});assert.equal(c.status,409);
 assert.equal(db.db.prepare('SELECT COUNT(*) AS n FROM mira_applications').get().n,1);
});
test('CSRF origin, content type and oversized body fail without writing',async()=>{
 const {call,db}=setup();assert.equal((await call('owner-a','/leads',leadBody,{Origin:'https://evil.test'})).status,403);
 assert.equal((await call('owner-a','/leads',leadBody,{'Content-Type':'text/plain'})).status,415);
 assert.equal((await call('owner-a','/leads',{...leadBody,extra:'x'.repeat(9000)})).status,413);
 assert.equal(db.db.prepare('SELECT COUNT(*) AS n FROM mira_leads').get().n,0);
});
test('same-tenant duplicate and cross-tenant isolation are independent',async()=>{
 const {call}=setup();const a=await call('owner-a','/leads',leadBody);assert.equal(a.status,201);assert.equal(a.body.protection_status,'not_confirmed');
 assert.equal((await call('owner-a','/leads',leadBody)).status,409);
 assert.equal((await call('owner-b','/leads/'+a.body.id)).status,404);
 assert.equal((await call('owner-b','/leads')).body.records.length,0);
 const b=await call('owner-b','/leads',{...leadBody,consent_ref:'EVID-client-b'});assert.equal(b.status,201);
});
test('broker cannot see another creator lead in same agency',async()=>{
 const {call}=setup();const a=await call('owner-a','/leads',leadBody);
 assert.equal((await call('broker-a','/leads/'+a.body.id)).status,404);
 assert.equal((await call('broker-a','/leads')).body.records.length,0);
});
test('missing, revoked and expired evidence close registration gate',async()=>{
 for(const mutation of ["UPDATE mira_projects SET enabled=0", "UPDATE mira_evidence SET revoked_at='2020-01-01' WHERE id='EVID-inventory'", "UPDATE mira_evidence SET expires_at=verified_at WHERE id='EVID-inventory'", "UPDATE mira_projects SET legal_seller='WRONG SELLER'"]){
 const {call,db}=setup();if(mutation.includes('expires_at=verified_at')){db.db.exec('PRAGMA ignore_check_constraints=ON; DROP TRIGGER mira_evidence_immutable;');}db.db.exec(mutation);
 assert.equal((await call('owner-a','/leads',leadBody)).status,409);assert.equal(db.db.prepare('SELECT COUNT(*) AS n FROM mira_leads').get().n,0);}
});
test('agency agreement, project assignment and consent scope enforced',async()=>{
 {const {call,db}=setup();db.db.exec("UPDATE mira_agencies SET status='suspended' WHERE id='agency-a'");assert.equal((await call('owner-a','/leads',leadBody)).status,403);}
 {const {call,db}=setup();db.db.exec("DELETE FROM mira_agency_projects WHERE agency_id='agency-a'");assert.equal((await call('owner-a','/leads',leadBody)).status,403);}
 {const {call}=setup();assert.equal((await call('owner-a','/leads',{...leadBody,consent_ref:'EVID-client-b'})).status,409);}
});
test('agency cannot promote itself, record evidence or change lead status',async()=>{
 const {call}=setup();const a=await call('owner-a','/leads',leadBody);
 assert.equal((await call('owner-a','/admin/leads/'+a.body.id+'/status',{status:'review',version:0,reason:'TEST review'})).status,403);
 assert.equal((await call('owner-a','/admin/evidence',{})).status,403);
 assert.equal((await call('owner-a','/admin/memberships',{})).status,403);
});
test('ordered transitions, owner approval, developer proof and CAS',async()=>{
 const {call,addEvidence,db}=setup();const a=(await call('owner-a','/leads',leadBody)).body;
 const path='/admin/leads/'+a.id+'/status',scope={agency:'agency-a',project:'project-1',entity:a.id};
 assert.equal((await call('operator',path,{status:'developer_confirmed',version:0,evidence_ref:'EVID-x',reason:'TEST premature'})).status,409);
 assert.equal((await call('operator',path,{status:'review',version:0,reason:'TEST reviewed'})).status,200);
 assert.equal((await call('operator',path,{status:'needs_information',version:0,reason:'TEST stale'})).status,409);
 addEvidence('EVID-submission','developer_submission',scope);
 assert.equal((await call('operator',path,{status:'developer_submitted',version:1,evidence_ref:'EVID-submission',reason:'TEST submitted'})).status,400);
 addEvidence('EVID-approval','owner_approval',scope);
 assert.equal((await call('operator',path,{status:'developer_submitted',version:1,evidence_ref:'EVID-submission',owner_approval_ref:'EVID-approval',reason:'TEST submitted'})).status,200);
 assert.equal((await call('operator',path,{status:'developer_confirmed',version:2,evidence_ref:'EVID-submission',reason:'TEST wrong evidence'})).status,409);
 addEvidence('EVID-confirmed','developer_confirmation',scope);addEvidence('EVID-protection','lead_protection',{...scope,expires:future});
 assert.equal((await call('operator',path,{status:'developer_confirmed',version:2,evidence_ref:'EVID-confirmed',protection_ref:'EVID-protection',protection_until:future,reason:'TEST confirmed'})).status,200);
 const detail=await call('owner-a','/leads/'+a.id);assert.equal(detail.body.protection_status,'recorded_confirmation');assert.equal(detail.body.events.length,4);
 assert.throws(()=>db.db.exec("UPDATE mira_events SET reason='tampered'"),/immutable/);
 db.db.exec("UPDATE mira_evidence SET revoked_at='2020-01-01' WHERE id='EVID-protection'");
 assert.equal((await call('owner-a','/leads/'+a.id)).body.protection_status,'not_currently_confirmed');
});
test('payment support receipt is not execution or quote',async()=>{
 const {call,addEvidence}=setup();const lead=(await call('owner-a','/leads',leadBody)).body;
 addEvidence('EVID-payment','payment_consent',{agency:'agency-a',project:'project-1',entity:lead.id});
 const r=await call('owner-a','/payment-requests',{lead_id:lead.id,invoice_currency:'USD',consent_ref:'EVID-payment'});
 assert.equal(r.status,201);assert.equal(r.body.quote,null);assert.equal(r.body.payment_execution,null);
 assert.equal((await call('owner-b','/payment-requests',{lead_id:lead.id,invoice_currency:'USD',consent_ref:'EVID-payment'})).status,404);
});
test('financial records require exact evidence and never use 90/10 defaults',async()=>{
 const {call,addEvidence,db}=setup();const lead=(await call('owner-a','/leads',leadBody)).body;
 db.db.prepare("UPDATE mira_leads SET status='developer_confirmed' WHERE id=?").run(lead.id); // fixture only
 const scope={agency:'agency-a',project:'project-1',entity:lead.id},path='/admin/leads/'+lead.id+'/deal-events';
 for(const [i,stage] of ['booking','contract','buyer_payment','commission_accrued','commission_received','agency_paid'].entries()){
  const financial=i>=3,facts=financial?{amount_decimal:i===5?'70.00':'100.00',currency:'USD'}:{};
  addEvidence('EVID-'+stage,stage,{...scope,facts});
  if(financial)assert.equal((await call('operator',path,{stage,sequence:i+1,evidence_ref:'EVID-'+stage,amount_decimal:'999.00',currency:'USD'})).status,409);
  const r=await call('operator',path,{stage,sequence:i+1,evidence_ref:'EVID-'+stage,...facts});assert.equal(r.status,201,JSON.stringify(r));
 }
 assert.equal(db.db.prepare('SELECT amount_decimal FROM mira_deal_events WHERE stage=?').get('agency_paid').amount_decimal,'70.00');
 assert.throws(()=>db.db.exec('DELETE FROM mira_deal_events'),/immutable/);
});
test('financial decimals reject floats, negative values, exponent and precision loss',()=>{
 for(const value of [1.2,'-1','1e9','0','0.0000','1.12345','01.0'])assert.throws(()=>decimalAmount(value));
 assert.equal(decimalAmount('123.4567'),'123.4567');
});
test('evidence API rejects public signed URLs, wrong facts and repeated refs',async()=>{
 const {call}=setup();let data={id:'EVID-new',kind:'inventory',project_id:'project-1',storage_ref:'https://secret.test?token=bad',verified:true,verified_at:past,expires_at:future};
 assert.equal((await call('operator','/admin/evidence',data)).status,400);
 data={...data,storage_ref:'vault:TEST-record'};assert.equal((await call('operator','/admin/evidence',data)).status,201);
 assert.equal((await call('operator','/admin/evidence',data)).status,409);
});
test('API cannot provision or demote an operator',async()=>{
 const {call}=setup();assert.equal((await call('operator','/admin/memberships',{subject:'attacker',agency_id:'agency-a',role:'operator',active:true})).status,400);
 assert.equal((await call('operator','/admin/memberships',{subject:'operator',agency_id:'agency-a',role:'broker',active:true})).status,409);
});
const keypair=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
const jwk={...(await crypto.subtle.exportKey('jwk',keypair.publicKey)),kid:'test-key',alg:'RS256',use:'sig'};
const b64=value=>Buffer.from(value).toString('base64url');
const authEnv={ACCESS_TEAM_DOMAIN:'https://mira-test.cloudflareaccess.com',ACCESS_AUDIENCE:'test-audience'};
async function signed(overrides={},header={}){const now=Math.floor(Date.now()/1000),h=b64(JSON.stringify({alg:'RS256',kid:'test-key',...header})),p=b64(JSON.stringify({iss:authEnv.ACCESS_TEAM_DOMAIN,aud:[authEnv.ACCESS_AUDIENCE],sub:'test-sub',email:'test@example.test',type:'app',iat:now-1,exp:now+60,...overrides}));const sig=await crypto.subtle.sign('RSASSA-PKCS1-v1_5',keypair.privateKey,new TextEncoder().encode(h+'.'+p));return h+'.'+p+'.'+b64(sig);}
const certFetch=async url=>{assert.equal(url,authEnv.ACCESS_TEAM_DOMAIN+'/cdn-cgi/access/certs');return new Response(JSON.stringify({keys:[jwk]}));};
test('Access JWT accepts only signed pinned issuer/audience/user claim',async()=>{
 const token=await signed();const identity=await verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Jwt-Assertion':token}}),authEnv,certFetch);assert.equal(identity.subject,'test-sub');
 for(const change of [{iss:'https://evil.test'},{aud:['other']},{exp:1},{iat:9999999999},{sub:''},{type:'service'},{email:'invalid'}]){
  const t=await signed(change);await assert.rejects(()=>verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Jwt-Assertion':t}}),authEnv,certFetch));
 }
 for(const change of [{alg:'none'},{alg:'HS256'},{jku:'https://evil.test/keys'},{jwk}]){
  const t=await signed({},change);await assert.rejects(()=>verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Jwt-Assertion':t}}),authEnv,certFetch));
 }
 const parts=token.split('.');parts[1]=b64(JSON.stringify({sub:'attacker'}));await assert.rejects(()=>verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Jwt-Assertion':parts.join('.')}}),authEnv,certFetch));
});
test('application quota is atomic and idempotent retries do not consume it',async()=>{
 const {call,env}=setup();env.APPLICATION_RATE_LIMIT='2';
 const data={company:'TEST',city:'TEST',name:'TEST',format:'agency',demand:'learning',markets:['phuket'],consent_version:'test-consent-v1'};
 for(const key of ['one','one','two'])assert.ok([200,201].includes((await call('applicant','/applications',data,{'Idempotency-Key':key})).status));
 assert.equal((await call('applicant','/applications',data,{'Idempotency-Key':'three'})).status,429);
});
test('evidence revocation is audited, immutable and changes access immediately',async()=>{
 const {call,db}=setup();assert.throws(()=>db.db.exec("UPDATE mira_evidence SET kind='forged'"),/immutable/);
 const r=await call('operator','/admin/evidence/EVID-agency-a/revoke',{reason:'TEST revocation'});assert.equal(r.status,200);
 assert.equal((await call('owner-a','/leads')).status,403);
 assert.throws(()=>db.db.exec("UPDATE mira_evidence SET revoked_at=NULL WHERE id='EVID-agency-a'"),/immutable/);
 assert.equal(db.db.prepare("SELECT COUNT(*) AS n FROM mira_events WHERE entity_type='evidence'").get().n,1);
});
test('JWT forged signature is rejected despite valid claims',async()=>{
 const token=await signed(),parts=token.split('.');parts[2]=(parts[2][0]==='A'?'B':'A')+parts[2].slice(1);
 await assert.rejects(()=>verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Jwt-Assertion':parts.join('.')}}),authEnv,certFetch));
 await assert.rejects(()=>verifyAccess(new Request('https://mira.test',{headers:{'Cf-Access-Authenticated-User-Email':'test@example.test'}}),authEnv,certFetch));
});
test('concurrent valid status changes create one event and one conflict',async()=>{
 const {call,db}=setup();const lead=(await call('owner-a','/leads',leadBody)).body;
 const path='/admin/leads/'+lead.id+'/status';
 const results=await Promise.all([call('operator',path,{status:'review',version:0,reason:'TEST first'}),call('operator',path,{status:'needs_information',version:0,reason:'TEST second'})]);
 assert.deepEqual(results.map(r=>r.status).sort(),[200,409]);
 assert.equal(db.db.prepare("SELECT COUNT(*) AS n FROM mira_events WHERE entity_type='lead'").get().n,2);
});

test('additive migration preserves v1 receipts without manufacturing historical approvals',()=>{
 const db=new DatabaseSync(':memory:');db.exec(readFileSync(new URL('0001_mira.sql',migrations),'utf8'));
 db.prepare(`INSERT INTO mira_applications (id,subject,email,company,city,name,format,demand,markets_json,consent_version,created_at,idempotency_key,request_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`).run('old-app','TEST','TEST@example.test','TEST','TEST','TEST','agency','learning','["phuket"]','TEST',past,'TEST-key','TEST-hash');
 db.exec(readFileSync(new URL('0002_operations.sql',migrations),'utf8'));
 const a=db.prepare('SELECT status,version,agency_id,created_at,updated_at FROM mira_applications').get();
 assert.equal(a.status,'received');assert.equal(a.version,0);assert.equal(a.agency_id,null);assert.equal(a.created_at,past);assert.equal(a.updated_at,past);
 assert.equal(db.prepare('SELECT COUNT(*) AS n FROM mira_events').get().n,0);db.close();
});
const applicationFixture={company:'TEST',city:'TEST',name:'TEST',format:'agency',demand:'learning',markets:['phuket'],consent_version:'test-consent-v1'};
test('application receipt audit is atomic, immutable and replayed only once',async()=>{
 const {call,db}=setup();const a=await call('applicant','/applications',applicationFixture,{'Idempotency-Key':'request-audit'});
 const replay=await call('applicant','/applications',applicationFixture,{'Idempotency-Key':'request-audit'});
 assert.equal(replay.body.id,a.body.id);const events=db.db.prepare("SELECT * FROM mira_events WHERE entity_type='application'").all();assert.equal(events.length,1);assert.equal(events[0].version,0);
 assert.throws(()=>db.db.prepare('UPDATE mira_events SET reason=?').run('TEST CHANGED'),/immutable/);
});
test('applicant can read own history before membership but cannot inspect another applicant',async()=>{
 const {call}=setup();const a=(await call('new-applicant','/applications',applicationFixture,{'Idempotency-Key':'request-scope'})).body;
 assert.equal((await call('new-applicant','/applications/'+a.id)).status,200);
 assert.equal((await call('owner-a','/applications/'+a.id)).status,404);
 assert.equal((await call('new-applicant','/admin/applications/'+a.id)).status,403);
 assert.equal((await call('owner-a','/admin/applications/'+a.id)).status,403);
});
test('qualification requires reviewed evidence and is not onboarding, activation or sending',async()=>{
 const {call,addEvidence}=setup();const a=(await call('new-applicant','/applications',applicationFixture,{'Idempotency-Key':'request-qualification'})).body,p='/admin/applications/'+a.id+'/status';
 assert.equal((await call('operator',p,{status:'onboarded',version:0,reason:'TEST skip'})).status,409);
 assert.equal((await call('operator',p,{status:'review',version:0,reason:'TEST reviewed'})).status,200);
 assert.equal((await call('operator',p,{status:'qualified',version:1,reason:'TEST no proof',evidence_ref:'EVID-absent'})).status,409);
 addEvidence('EVID-qualification','application_qualification',{entity:a.id});
 const qualified=await call('operator',p,{status:'qualified',version:1,reason:'TEST evidence',evidence_ref:'EVID-qualification'});
 assert.equal(qualified.status,200);assert.equal(qualified.body.activation_recorded,false);assert.equal(qualified.body.outreach_sent,false);
 const own=await call('new-applicant','/applications/'+a.id);assert.equal(own.body.application.status,'qualified');assert(!('reason' in own.body.events.at(-1)));
});
test('onboarding requires scoped proof, current agreement and verified agency-owner membership',async()=>{
 const {call,addEvidence,db}=setup();const a=(await call('owner-a','/applications',applicationFixture,{'Idempotency-Key':'request-onboarding'})).body,p='/admin/applications/'+a.id+'/status';
 await call('operator',p,{status:'review',version:0,reason:'TEST reviewed'});
 addEvidence('EVID-q','application_qualification',{entity:a.id});await call('operator',p,{status:'qualified',version:1,reason:'TEST qualified',evidence_ref:'EVID-q'});
 addEvidence('EVID-onboard','agency_onboarding',{agency:'agency-a',entity:a.id});
 const body={status:'onboarded',version:2,reason:'TEST completed',evidence_ref:'EVID-onboard',agency_id:'agency-a'};
 assert.equal((await call('operator',p,{...body,agency_id:'agency-b'})).status,409);
 db.db.exec("UPDATE mira_memberships SET active=0 WHERE subject='owner-a'");assert.equal((await call('operator',p,body)).status,409);
 db.db.exec("UPDATE mira_memberships SET active=1 WHERE subject='owner-a'");const r=await call('operator',p,body);assert.equal(r.status,200);assert.equal(r.body.agency_id,'agency-a');assert.equal(r.body.activation_recorded,false);
});
test('simultaneous application review changes preserve one version and one event',async()=>{
 const {call,db}=setup();const a=(await call('applicant','/applications',applicationFixture,{'Idempotency-Key':'request-race'})).body,p='/admin/applications/'+a.id+'/status';
 const r=await Promise.all([call('operator',p,{status:'review',version:0,reason:'TEST review'}),call('operator',p,{status:'rejected',version:0,reason:'TEST reject'})]);
 assert.deepEqual(r.map(x=>x.status).sort(),[200,409]);assert.equal(db.db.prepare("SELECT COUNT(*) AS n FROM mira_events WHERE entity_type='application' AND entity_id=?").get(a.id).n,2);
});
test('project card reveals readiness timestamps, not vault paths or unconfirmed inventory',async()=>{
 const {call,db}=setup();const r=await call('owner-a','/projects/project-1');assert.equal(r.status,200);assert.equal(r.body.registration_eligible,true);assert.equal(r.body.materials_available,false);
 assert.equal(r.body.checks.find(c=>c.kind==='inventory').expires_at,future);
 const serialized=JSON.stringify(r.body);assert(!serialized.includes('vault:'));assert(!serialized.includes('EVID-'));assert(!serialized.includes('amount_decimal'));
 db.db.exec("UPDATE mira_evidence SET revoked_at='2020-01-01' WHERE id='EVID-inventory'");const closed=await call('owner-a','/projects/project-1');assert.equal(closed.body.registration_eligible,false);assert.equal(closed.body.checks.find(c=>c.kind==='inventory').state,'not_current');
});
test('project detail and profile respect tenant assignment and do not infer activation',async()=>{
 const {call,db}=setup();db.db.exec("DELETE FROM mira_agency_projects WHERE agency_id='agency-b'");
 assert.equal((await call('owner-b','/projects/project-1')).status,404);assert.equal((await call('operator','/projects/project-1')).status,200);
 const profile=await call('broker-a','/profile');assert.equal(profile.body.agency.id,'agency-a');assert.equal(profile.body.role,'broker');assert.deepEqual(profile.body.available_markets,['phuket']);assert.equal(profile.body.activation_status,'not_inferred_from_access');
 assert(!JSON.stringify(profile.body).includes('EVID-'));assert.equal((await call('owner-b','/profile')).body.available_markets.length,0);
});
test('lead receipt retry survives inventory expiry without registering a new client',async()=>{
 const {call,db}=setup();const a=await call('owner-a','/leads',leadBody,{'Idempotency-Key':'lead-retry'});assert.equal(a.status,201);
 db.db.exec("UPDATE mira_evidence SET revoked_at='2020-01-01' WHERE id='EVID-inventory'");
 const b=await call('owner-a','/leads',leadBody,{'Idempotency-Key':'lead-retry'});assert.equal(b.status,200);assert.equal(b.body.replayed,true);assert.equal(b.body.id,a.body.id);
 const c=await call('owner-a','/leads',{...leadBody,client_ref:'OTHER-TEST'},{'Idempotency-Key':'lead-retry'});assert.equal(c.status,409);
 assert.equal(db.db.prepare('SELECT COUNT(*) AS n FROM mira_leads').get().n,1);
});
test('concurrent identical lead attempts return one durable receipt and no duplicate audit',async()=>{
 const {call,db}=setup();const results=await Promise.all([call('owner-a','/leads',leadBody,{'Idempotency-Key':'lead-race'}),call('owner-a','/leads',leadBody,{'Idempotency-Key':'lead-race'})]);
 assert.deepEqual(results.map(r=>r.status).sort(),[200,201]);assert.equal(results[0].body.id,results[1].body.id);
 assert.equal(db.db.prepare("SELECT COUNT(*) AS n FROM mira_events WHERE entity_type='lead'").get().n,1);
});
test('payment replay returns the existing receipt, rejects changed fields and preserves audit',async()=>{
 const {call,addEvidence,db}=setup();const lead=(await call('owner-a','/leads',leadBody)).body;
 addEvidence('EVID-payment-repeat','payment_consent',{agency:'agency-a',project:'project-1',entity:lead.id});
 const b={lead_id:lead.id,invoice_currency:'USD',consent_ref:'EVID-payment-repeat'};
 const a=await call('owner-a','/payment-requests',b),r=await call('owner-a','/payment-requests',b);
 assert.equal(a.status,201);assert.equal(r.status,200);assert.equal(r.body.id,a.body.id);assert.equal(r.body.payment_execution,null);
 assert.equal((await call('owner-a','/payment-requests',{...b,invoice_currency:'EUR'})).status,409);
 assert.equal(db.db.prepare("SELECT COUNT(*) AS n FROM mira_events WHERE entity_type='payment_request'").get().n,1);
});
test('owner approval reference remains attached to immutable developer-submission audit',async()=>{
 const {call,addEvidence,db}=setup();const a=(await call('owner-a','/leads',leadBody)).body,path='/admin/leads/'+a.id+'/status';
 await call('operator',path,{status:'review',version:0,reason:'TEST review'});const scope={agency:'agency-a',project:'project-1',entity:a.id};
 addEvidence('EVID-owner-trace','owner_approval',scope);addEvidence('EVID-dev-trace','developer_submission',scope);
 const r=await call('operator',path,{status:'developer_submitted',version:1,reason:'TEST recorded',evidence_ref:'EVID-dev-trace',owner_approval_ref:'EVID-owner-trace'});assert.equal(r.status,200);
 assert.equal(db.db.prepare("SELECT owner_approval_ref FROM mira_events WHERE entity_type='lead' AND status='developer_submitted'").get().owner_approval_ref,'EVID-owner-trace');
});
