import {ApiError,verifyAccess} from './auth.mjs';
import {requireKeys,string,identifier,evidenceRef,iso,currentEvidence,leadTransition,decimalAmount,currency,STAGES,EVIDENCE_KINDS} from './rules.mjs';
const API='/mira/api';
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}});
const stmt=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
const first=(env,sql,...args)=>stmt(env,sql,...args).first();
const all=async(env,sql,...args)=>(await stmt(env,sql,...args).all()).results||[];
const run=(env,sql,...args)=>stmt(env,sql,...args).run();
const nowISO=()=>new Date().toISOString();
const uuid=()=>crypto.randomUUID();
function assert(condition,status,code){if(!condition)throw new ApiError(status,code);}
async function bodyOf(request) {
 assert((request.headers.get('Content-Type')||'').split(';')[0].trim()==='application/json',415,'json_required');
 const reader=request.body?.getReader();assert(reader,400,'body_required');let count=0,chunks=[];
 try {while(true){const part=await reader.read();if(part.done)break;count+=part.value.byteLength;if(count>8192){await reader.cancel();throw new ApiError(413,'payload_too_large');}chunks.push(part.value);}}
 finally {reader.releaseLock();}
 const bytes=new Uint8Array(count);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
 try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{throw new ApiError(400,'invalid_json');}
}
async function digest(data){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(data))))).map(n=>n.toString(16).padStart(2,'0')).join('');}
async function membership(env,identity) {
 const m=await first(env,'SELECT * FROM mira_memberships WHERE subject=? AND active=1',identity.subject);
 assert(m,403,'membership_required');
 if(m.role!=='operator'){
   const a=await first(env,'SELECT * FROM mira_agencies WHERE id=? AND status=\'active\'',m.agency_id);
   assert(a,403,'agency_not_active');
   const e=a.agreement_ref?await first(env,'SELECT * FROM mira_evidence WHERE id=?',a.agreement_ref):null;
   assert(currentEvidence(e,'agency_agreement',{agency_id:a.id}),403,'agency_agreement_not_current');
 }
 return m;
}
function operator(m){assert(m.role==='operator',403,'operator_required');}
async function evidence(env,id,kind,scope) {
 const e=await first(env,'SELECT * FROM mira_evidence WHERE id=?',evidenceRef(id));
 assert(currentEvidence(e,kind,scope),409,'evidence_missing_stale_or_wrong_scope');return e;
}
async function projectGate(env,id,agencyId) {
 const p=await first(env,'SELECT * FROM mira_projects WHERE id=?',id);
 assert(p&&p.enabled===1&&p.legal_seller&&!['unknown','not_verified'].includes(p.legal_seller.toLowerCase()),409,'project_not_enabled');
 assert(await first(env,'SELECT 1 AS permitted FROM mira_agency_projects WHERE agency_id=? AND project_id=?',agencyId,id),403,'project_access_required');
 for(const [field,kind] of [['agreement_ref','project_agreement'],['inventory_ref','inventory'],['registration_rules_ref','registration_rules'],['commission_schedule_ref','commission_schedule']]){
   const e=await evidence(env,p[field],kind,{project_id:id});
   if(kind==='inventory')assert(e.expires_at,409,'inventory_expiry_required');
   if(kind==='project_agreement')assert(JSON.parse(e.facts_json).legal_seller===p.legal_seller,409,'seller_not_evidenced');
 }
 return p;
}
async function getLead(env,id,m,identity) {
 const lead=await first(env,'SELECT * FROM mira_leads WHERE id=?',identifier(id));
 assert(lead&&(m.role==='operator'||(lead.agency_id===m.agency_id&&(m.role!=='broker'||lead.created_by===identity.subject))),404,'lead_not_found');return lead;
}
function pageSettings(url){const limit=Number(url.searchParams.get('limit')||50);assert(Number.isSafeInteger(limit)&&limit>0&&limit<=100,400,'invalid_limit');const cursor=url.searchParams.get('cursor')||'';if(cursor)identifier(cursor);return {limit,cursor};}
function pageResult(items,limit){const more=items.length>limit;const records=items.slice(0,limit);return {records,next_cursor:more?records.at(-1).id:null};}
async function application(request,env,identity) {
 assert(env.APPLICATIONS_ENABLED==='true'&&env.PRIVACY_VERSION&&env.PRIVACY_NOTICE_URL?.startsWith(env.APP_ORIGIN+'/'),503,'applications_not_enabled');
 const b=await bodyOf(request);requireKeys(b,['company','city','name','format','demand','markets','consent_version'],['company','city','name','format','demand','markets','consent_version']);
 assert(b.consent_version===env.PRIVACY_VERSION,400,'current_consent_required');
 assert(['agency','broker','network'].includes(b.format)&&['learning','potential','current'].includes(b.demand),400,'invalid_qualification');
 assert(Array.isArray(b.markets)&&b.markets.length>=1&&b.markets.length<=4&&b.markets.every(x=>['phuket','bali','vietnam','dubai'].includes(x)),400,'invalid_markets');
 const data={company:string(b.company),city:string(b.city),name:string(b.name),format:b.format,demand:b.demand,markets:[...new Set(b.markets)].sort(),consent_version:b.consent_version};
 const key=identifier(request.headers.get('Idempotency-Key'));const hash=await digest(data),id=uuid(),created=nowISO();
 const prior=await first(env,'SELECT id,status,created_at,request_hash FROM mira_applications WHERE subject=? AND idempotency_key=?',identity.subject,key);
 if(prior){assert(prior.request_hash===hash,409,'idempotency_payload_mismatch');return json({id:prior.id,status:prior.status,received_at:prior.created_at,meaning:'Recorded by MIRA; not activation.'});}
 const quota=Number(env.APPLICATION_RATE_LIMIT||5);assert(Number.isSafeInteger(quota)&&quota>0&&quota<=1000,503,'invalid_rate_configuration');
 const bucket=Math.floor(Date.now()/3600000);
 const budget=await run(env,'INSERT INTO mira_rate_limits (subject,bucket,uses) VALUES (?,?,1) ON CONFLICT(subject,bucket) DO UPDATE SET uses=uses+1 WHERE uses<?',identity.subject,bucket,quota);
 assert(budget.meta.changes===1,429,'application_rate_limit');
 await run(env,`INSERT INTO mira_applications (id,subject,email,company,city,name,format,demand,markets_json,consent_version,created_at,idempotency_key,request_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(subject,idempotency_key) DO NOTHING`,id,identity.subject,identity.email,data.company,data.city,data.name,data.format,data.demand,JSON.stringify(data.markets),data.consent_version,created,key,hash);
 const saved=await first(env,'SELECT id,status,created_at,request_hash FROM mira_applications WHERE subject=? AND idempotency_key=?',identity.subject,key);
 assert(saved&&saved.request_hash===hash,409,'idempotency_payload_mismatch');
 return json({id:saved.id,status:saved.status,received_at:saved.created_at,meaning:'Recorded by MIRA, not yet qualified, contracted or activated.'},saved.id===id?201:200);
}
async function createLead(request,env,m,identity) {
 assert(m.role!=='operator',403,'agency_context_required');
 const b=await bodyOf(request);requireKeys(b,['project_id','client_ref','consent_ref'],['project_id','client_ref','consent_ref']);
 const projectId=identifier(b.project_id),ref=identifier(b.client_ref);
 assert(!ref.toUpperCase().startsWith('DEMO-'),400,'demo_not_allowed_in_live_ledger');
 await projectGate(env,projectId,m.agency_id);
 await evidence(env,b.consent_ref,'client_consent',{agency_id:m.agency_id,project_id:projectId,entity_id:ref});
 const id=uuid(),event=uuid(),now=nowISO();
 try{await env.MIRA_DB.batch([
   stmt(env,`INSERT INTO mira_leads (id,agency_id,project_id,client_ref,consent_ref,created_by,created_at,updated_at,last_event_id) VALUES (?,?,?,?,?,?,?,?,?)`,id,m.agency_id,projectId,ref,b.consent_ref,identity.subject,now,now,event),
   stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at) VALUES (?,'lead',?,?,?,'submitted',0,?,'Received by MIRA; not submitted to developer',?)`,event,id,m.agency_id,identity.subject,b.consent_ref,now)
 ]);}catch(error){if(String(error.message).includes('UNIQUE'))throw new ApiError(409,'duplicate_registration_in_agency');throw error;}
 return json({id,status:'submitted',version:0,received_at:now,protection_status:'not_confirmed'},201);
}
async function transition(request,env,m,identity,id) {
 operator(m);const lead=await getLead(env,id,m,identity),b=leadTransition(lead,await bodyOf(request));
 const scope={agency_id:lead.agency_id,project_id:lead.project_id,entity_id:lead.id};
 if(b.status==='developer_submitted'){
   await evidence(env,b.evidence_ref,'developer_submission',scope);
   await evidence(env,b.owner_approval_ref,'owner_approval',scope);
 }
 if(b.status==='developer_confirmed')await evidence(env,b.evidence_ref,'developer_confirmation',scope);
 if(b.protection_ref){const e=await evidence(env,b.protection_ref,'lead_protection',scope);assert(e.expires_at&&iso(b.protection_until)===e.expires_at&&Date.parse(b.protection_until)>Date.now(),409,'protection_date_not_evidenced');}
 const event=uuid(),now=nowISO();const until=b.status==='developer_confirmed'?(b.protection_until?iso(b.protection_until):null):null;
 const result=await env.MIRA_DB.batch([
   stmt(env,'UPDATE mira_leads SET status=?,version=version+1,protection_ref=?,protection_until=?,last_event_id=?,updated_at=? WHERE id=? AND version=?',b.status,b.protection_ref||null,until,event,now,id,b.version),
   stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at) SELECT ?,'lead',id,agency_id,?,status,version,?,?,? FROM mira_leads WHERE id=? AND last_event_id=?`,event,identity.subject,b.evidence_ref||null,b.reason,now,id,event)
 ]);
 assert(result[0].meta.changes===1,409,'stale_version');return json({id,status:b.status,version:b.version+1,protection_until:until});
}
async function paymentRequest(request,env,m,identity) {
 assert(m.role!=='operator',403,'agency_context_required');
 const b=await bodyOf(request);requireKeys(b,['lead_id','invoice_currency','consent_ref'],['lead_id','invoice_currency','consent_ref']);
 const lead=await getLead(env,b.lead_id,m,identity);assert(!['closed','rejected','duplicate'].includes(lead.status),409,'lead_not_active');
 await evidence(env,b.consent_ref,'payment_consent',{agency_id:lead.agency_id,project_id:lead.project_id,entity_id:lead.id});
 const id=uuid(),now=nowISO(),curr=currency(b.invoice_currency);
 try{await run(env,`INSERT INTO mira_payment_requests (id,lead_id,agency_id,created_by,created_at,invoice_currency,consent_ref) VALUES (?,?,?,?,?,?,?)`,id,lead.id,lead.agency_id,identity.subject,now,curr,b.consent_ref);}
 catch(error){if(String(error.message).includes('UNIQUE'))throw new ApiError(409,'payment_request_already_exists');throw error;}
 return json({id,lead_id:lead.id,status:'package_review',received_at:now,quote:null,payment_execution:null},201);
}
async function dealEvent(request,env,m,identity,id) {
 operator(m);const lead=await getLead(env,id,m,identity);assert(lead.status==='developer_confirmed',409,'developer_confirmation_required');
 const b=await bodyOf(request);requireKeys(b,['stage','sequence','evidence_ref','amount_decimal','currency'],['stage','sequence','evidence_ref']);
 const prior=await first(env,'SELECT * FROM mira_deal_events WHERE lead_id=? ORDER BY sequence DESC LIMIT 1',id);
 const sequence=(prior?.sequence||0)+1;assert(b.sequence===sequence&&STAGES[sequence]===b.stage,409,'invalid_deal_sequence');
 const proof=await evidence(env,b.evidence_ref,b.stage,{agency_id:lead.agency_id,project_id:lead.project_id,entity_id:lead.id});
 const financial=['commission_accrued','commission_received','agency_paid'].includes(b.stage);
 const amount=financial?decimalAmount(b.amount_decimal):null,curr=financial?currency(b.currency):null;
 assert(financial||(b.amount_decimal===undefined&&b.currency===undefined),400,'amount_not_applicable');
 if(financial){const f=JSON.parse(proof.facts_json);assert(f.amount_decimal===amount&&f.currency===curr,409,'financial_value_not_evidenced');}
 if(financial&&prior?.currency)assert(curr===prior.currency,409,'cross_currency_settlement_requires_separate_ledger');
 if(b.stage==='agency_paid'){
   const scaled=s=>{const [a,c='']=s.split('.');return BigInt(a)*10000n+BigInt(c.padEnd(4,'0'));};
   assert(scaled(amount)<=scaled(prior.amount_decimal),409,'settlement_exceeds_recorded_receipt');
 }
 const event=uuid(),now=nowISO();
 try{await run(env,`INSERT INTO mira_deal_events (id,lead_id,agency_id,sequence,stage,evidence_ref,amount_decimal,currency,actor,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)`,event,id,lead.agency_id,sequence,b.stage,b.evidence_ref,amount,curr,identity.subject,now);}
 catch(error){if(String(error.message).includes('UNIQUE'))throw new ApiError(409,'stale_deal_sequence');throw error;}
 return json({id:event,lead_id:id,stage:b.stage,sequence,amount_decimal:amount,currency:curr},201);
}
async function recordEvidence(request,env,m,identity) {
 operator(m);const b=await bodyOf(request);
 requireKeys(b,['id','kind','project_id','agency_id','entity_id','storage_ref','verified_at','expires_at','verified','facts'],['id','kind','storage_ref','verified_at','verified']);
 assert(EVIDENCE_KINDS.includes(b.kind)&&b.verified===true,400,'verified_evidence_required');
 const id=evidenceRef(b.id),verified=iso(b.verified_at),expires=b.expires_at?iso(b.expires_at):null;
 assert(Date.parse(verified)<=Date.now()&&(!expires||Date.parse(expires)>Date.now()),400,'evidence_not_current');
 const storage=string(b.storage_ref,3,240);assert(/^[A-Za-z0-9_:./-]+$/.test(storage)&&!storage.includes('://')&&!storage.includes('..'),400,'opaque_vault_reference_required');
 const project=b.project_id?identifier(b.project_id):null,agency=b.agency_id?identifier(b.agency_id):null,entity=b.entity_id?identifier(b.entity_id):null;
 let facts={};
 if(['commission_accrued','commission_received','agency_paid'].includes(b.kind)){requireKeys(b.facts,['amount_decimal','currency'],['amount_decimal','currency']);facts={amount_decimal:decimalAmount(b.facts.amount_decimal),currency:currency(b.facts.currency)};}
 else if(b.kind==='project_agreement'){requireKeys(b.facts,['legal_seller'],['legal_seller']);facts={legal_seller:string(b.facts.legal_seller)};}
 else assert(b.facts===undefined||JSON.stringify(b.facts)==='{}',400,'facts_not_applicable');
 try{await run(env,`INSERT INTO mira_evidence (id,kind,project_id,agency_id,entity_id,storage_ref,facts_json,verified,verified_by,verified_at,expires_at) VALUES (?,?,?,?,?,?,?,1,?,?,?)`,id,b.kind,project,agency,entity,storage,JSON.stringify(facts),identity.subject,verified,expires);}
 catch(error){if(String(error.message).includes('UNIQUE'))throw new ApiError(409,'evidence_reference_exists');if(String(error.message).includes('FOREIGN KEY'))throw new ApiError(409,'evidence_scope_missing');throw error;}
 return json({id,kind:b.kind,verified_at:verified,expires_at:expires},201);
}
async function adminAgency(request,env,m) {
 operator(m);const b=await bodyOf(request);requireKeys(b,['id','name','city','status','agreement_ref'],['id','name','city','status']);
 assert(['pending','active','suspended'].includes(b.status),400,'invalid_agency_status');
 const id=identifier(b.id);
 if(b.status==='active')await evidence(env,b.agreement_ref,'agency_agreement',{agency_id:id});
 await run(env,`INSERT INTO mira_agencies (id,name,city,status,agreement_ref,created_at) VALUES (?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,city=excluded.city,status=excluded.status,agreement_ref=excluded.agreement_ref`,id,string(b.name),string(b.city),b.status,b.agreement_ref||null,nowISO());
 return json({id,status:b.status});
}
async function adminProject(request,env,m) {
 operator(m);const b=await bodyOf(request);requireKeys(b,['id','name','market','developer_family','legal_seller','enabled','agreement_ref','inventory_ref','registration_rules_ref','commission_schedule_ref','materials_rights_ref'],['id','name','market','enabled']);
 const id=identifier(b.id);assert(typeof b.enabled==='boolean'&&b.market==='phuket',400,'invalid_project');
 if(b.enabled){
   assert(b.legal_seller&&!['unknown','not_verified'].includes(b.legal_seller.toLowerCase()),409,'seller_required');
   for(const [field,kind] of [['agreement_ref','project_agreement'],['inventory_ref','inventory'],['registration_rules_ref','registration_rules'],['commission_schedule_ref','commission_schedule']]){
     const e=await evidence(env,b[field],kind,{project_id:id});if(kind==='inventory')assert(e.expires_at,409,'inventory_expiry_required');if(kind==='project_agreement')assert(JSON.parse(e.facts_json).legal_seller===b.legal_seller,409,'seller_not_evidenced');
   }
 }
 await run(env,`INSERT INTO mira_projects (id,name,market,developer_family,legal_seller,enabled,agreement_ref,inventory_ref,registration_rules_ref,commission_schedule_ref,materials_rights_ref,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,market=excluded.market,developer_family=excluded.developer_family,legal_seller=excluded.legal_seller,enabled=excluded.enabled,agreement_ref=excluded.agreement_ref,inventory_ref=excluded.inventory_ref,registration_rules_ref=excluded.registration_rules_ref,commission_schedule_ref=excluded.commission_schedule_ref,materials_rights_ref=excluded.materials_rights_ref,updated_at=excluded.updated_at`,id,string(b.name),b.market,b.developer_family?string(b.developer_family):null,b.legal_seller?string(b.legal_seller):null,b.enabled?1:0,b.agreement_ref||null,b.inventory_ref||null,b.registration_rules_ref||null,b.commission_schedule_ref||null,b.materials_rights_ref||null,nowISO());
 return json({id,enabled:b.enabled});
}
async function handle(request,env,identityVerifier) {
 const url=new URL(request.url),path=url.pathname;
 if(path===API+'/health'&&request.method==='GET')return json({service:'mira-pilot-api',configured:Boolean(env.MIRA_DB&&env.ACCESS_TEAM_DOMAIN&&env.ACCESS_AUDIENCE&&env.APP_ORIGIN),outreach_enabled:false});
 assert(path.startsWith(API+'/'),404,'not_found');assert(env.MIRA_DB&&env.APP_ORIGIN,503,'service_not_configured');
 if(!['GET','POST'].includes(request.method))throw new ApiError(405,'method_not_allowed');
 if(request.method==='POST')assert(request.headers.get('Origin')===env.APP_ORIGIN,403,'origin_rejected');
 const identity=await identityVerifier(request,env);
 if(path===API+'/applications'&&request.method==='POST')return application(request,env,identity);
 if(path===API+'/applications'&&request.method==='GET')return json({records:await all(env,'SELECT id,company,city,status,created_at FROM mira_applications WHERE subject=? ORDER BY created_at DESC LIMIT 100',identity.subject)});
 if(path===API+'/session'&&request.method==='GET'){
   const m=await first(env,'SELECT agency_id,role,active FROM mira_memberships WHERE subject=?',identity.subject);
   return json({subject:identity.subject,email:identity.email,membership:m,applications_enabled:env.APPLICATIONS_ENABLED==='true',privacy_version:env.PRIVACY_VERSION||null,privacy_notice_url:env.PRIVACY_NOTICE_URL||null});
 }
 const m=await membership(env,identity);
 if(path===API+'/projects'&&request.method==='GET'){
   const query='SELECT p.id,p.name,p.market,p.developer_family,p.legal_seller,p.enabled,p.updated_at FROM mira_projects p';
   return json({records:m.role==='operator'?await all(env,query+' ORDER BY p.name'):await all(env,query+' JOIN mira_agency_projects a ON a.project_id=p.id WHERE a.agency_id=? ORDER BY p.name',m.agency_id),note:'Enabled flag alone is not a freshness guarantee. Every client submission revalidates evidence.'});
 }
 if(path===API+'/leads'&&request.method==='POST')return createLead(request,env,m,identity);
 if(path===API+'/leads'&&request.method==='GET'){
   const {limit,cursor}=pageSettings(url);let where='id>?',args=[cursor];
   if(m.role!=='operator'){where+=' AND agency_id=?';args.push(m.agency_id);if(m.role==='broker'){where+=' AND created_by=?';args.push(identity.subject);}}
   return json(pageResult(await all(env,'SELECT id,agency_id,project_id,client_ref,status,version,created_at,updated_at,protection_until FROM mira_leads WHERE '+where+' ORDER BY id LIMIT ?',...args,limit+1),limit));
 }
 const detail=path.match(/^\/mira\/api\/leads\/([A-Za-z0-9_-]+)$/);
 if(detail&&request.method==='GET'){
   const lead=await getLead(env,detail[1],m,identity);
   const events=await all(env,'SELECT status,version,reason,created_at,evidence_ref FROM mira_events WHERE entity_type=\'lead\' AND entity_id=? ORDER BY version',lead.id);
   const deal=await all(env,'SELECT sequence,stage,evidence_ref,amount_decimal,currency,created_at FROM mira_deal_events WHERE lead_id=? ORDER BY sequence',lead.id);
   const payment=await first(env,'SELECT id,status,invoice_currency,created_at FROM mira_payment_requests WHERE lead_id=?',lead.id);
   const pe=lead.protection_ref?await first(env,'SELECT * FROM mira_evidence WHERE id=?',lead.protection_ref):null;
   const protectedNow=lead.status==='developer_confirmed'&&currentEvidence(pe,'lead_protection',{agency_id:lead.agency_id,project_id:lead.project_id,entity_id:lead.id})&&pe.expires_at===lead.protection_until;
   return json({lead,events,deal,payment,protection_status:protectedNow?'recorded_confirmation':'not_currently_confirmed'});
 }
 if(path===API+'/payment-requests'&&request.method==='POST')return paymentRequest(request,env,m,identity);
 const change=path.match(/^\/mira\/api\/admin\/leads\/([A-Za-z0-9_-]+)\/status$/);
 if(change&&request.method==='POST')return transition(request,env,m,identity,change[1]);
 const deal=path.match(/^\/mira\/api\/admin\/leads\/([A-Za-z0-9_-]+)\/deal-events$/);
 if(deal&&request.method==='POST')return dealEvent(request,env,m,identity,deal[1]);
 if(path===API+'/admin/evidence'&&request.method==='POST')return recordEvidence(request,env,m,identity);
 const revoke=path.match(/^\/mira\/api\/admin\/evidence\/([A-Za-z0-9_-]+)\/revoke$/);
 if(revoke&&request.method==='POST'){
   operator(m);const b=await bodyOf(request);requireKeys(b,['reason'],['reason']);const reason=string(b.reason,3,240);
   const e=await first(env,'SELECT * FROM mira_evidence WHERE id=?',evidenceRef(revoke[1]));assert(e,404,'evidence_not_found');
   if(e.revoked_at)return json({id:e.id,revoked:true});
   const id=uuid(),now=nowISO();
   await env.MIRA_DB.batch([stmt(env,'UPDATE mira_evidence SET revoked_at=? WHERE id=? AND revoked_at IS NULL',now,e.id),stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at) VALUES (?,'evidence',?,?,?,'revoked',1,?,?,?) ON CONFLICT(entity_type,entity_id,version) DO NOTHING`,id,e.id,e.agency_id,identity.subject,e.id,reason,now)]);
   return json({id:e.id,revoked:true});
 }
 if(path===API+'/admin/agencies'&&request.method==='POST')return adminAgency(request,env,m);
 if(path===API+'/admin/projects'&&request.method==='POST')return adminProject(request,env,m);
 if(path===API+'/admin/memberships'&&request.method==='POST'){
   operator(m);const b=await bodyOf(request);requireKeys(b,['subject','agency_id','role','active'],['subject','agency_id','role','active']);
   assert(['agency_owner','broker'].includes(b.role)&&typeof b.active==='boolean',400,'invalid_membership');
   const saved=await run(env,`INSERT INTO mira_memberships (subject,agency_id,role,active) VALUES (?,?,?,?) ON CONFLICT(subject) DO UPDATE SET agency_id=excluded.agency_id,role=excluded.role,active=excluded.active WHERE mira_memberships.role!='operator'`,string(b.subject,1,200),identifier(b.agency_id),b.role,b.active?1:0);
   assert(saved.meta.changes===1,409,'operator_membership_is_bootstrap_only');
   return json({subject:b.subject,agency_id:b.agency_id,role:b.role,active:b.active});
 }
 if(path===API+'/admin/agency-projects'&&request.method==='POST'){
   operator(m);const b=await bodyOf(request);requireKeys(b,['agency_id','project_id'],['agency_id','project_id']);
   await run(env,'INSERT INTO mira_agency_projects (agency_id,project_id) VALUES (?,?) ON CONFLICT DO NOTHING',identifier(b.agency_id),identifier(b.project_id));return json({granted:true});
 }
 if(path===API+'/admin/applications'&&request.method==='GET'){
   operator(m);const {limit,cursor}=pageSettings(url);return json(pageResult(await all(env,'SELECT id,subject,email,company,city,name,format,demand,markets_json,status,created_at FROM mira_applications WHERE id>? ORDER BY id LIMIT ?',cursor,limit+1),limit));
 }
 if(path===API+'/admin/dashboard'&&request.method==='GET'){
   operator(m);return json({scope:'This database only; counts are not market-wide totals.',
     agencies:await all(env,'SELECT status,COUNT(*) AS count FROM mira_agencies GROUP BY status'),
     leads:await all(env,'SELECT status,COUNT(*) AS count FROM mira_leads GROUP BY status'),
     deal_events:await all(env,'SELECT stage,COUNT(*) AS count FROM mira_deal_events GROUP BY stage'),
     payment_requests:await all(env,'SELECT status,COUNT(*) AS count FROM mira_payment_requests GROUP BY status'),
     applications:await all(env,'SELECT status,COUNT(*) AS count FROM mira_applications GROUP BY status'),
     financial_totals:null,financial_note:'No mixed-currency aggregation or assumed platform split.'});
 }
 throw new ApiError(404,'not_found');
}
/** Injectable verifier is only a test seam; the production export is pinned below. */
export function createHandler(identityVerifier=verifyAccess) {
 return async(request,env)=>{try{return await handle(request,env,identityVerifier);}catch(error){
   const status=error instanceof ApiError?error.status:500;
   return json({error:error instanceof ApiError?error.code:'internal_error',request_id:uuid()},status);
 }};
}
export default {fetch:createHandler()};
