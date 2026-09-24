/** Public requests are unverified enquiries, never memberships or verified contacts. */
import {ApiError} from './auth.mjs';
import {intakePage, intakeClient} from './intake-ui.mjs';
const ROOT='/mira/request';
const fixedHeaders={'Cache-Control':'no-store, private','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow, noarchive'};
const json=(b,status=200)=>Response.json(b,{status,headers:{...fixedHeaders,'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}});
const check=(ok,status,code)=>{if(!ok)throw new ApiError(status,code);};
const s=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
const one=(env,sql,...args)=>s(env,sql,...args).first();
const hex=bytes=>Array.from(new Uint8Array(bytes),b=>b.toString(16).padStart(2,'0')).join('');
const sha=async text=>hex(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)));
function text(v,min,max){check(typeof v==='string'&&v.trim().length>=min&&v.trim().length<=max&&!/[\u0000-\u001f\u007f]/.test(v),400,'invalid_field');return v.trim();}
function keys(b,allowed){check(b&&typeof b==='object'&&!Array.isArray(b)&&Object.keys(b).every(k=>allowed.includes(k))&&allowed.every(k=>Object.hasOwn(b,k)),400,'invalid_fields');}
const uuid=v=>{check(typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(v),400,'invalid_id');return v.toLowerCase();};
function token(request){const v=request.headers.get('Authorization')||'';check(/^Bearer [0-9a-f]{64}$/.test(v),401,'receipt_token_required');return v.slice(7);}
async function body(request){
 check((request.headers.get('Content-Type')||'').split(';')[0].trim()==='application/json',415,'json_required');
 const reader=request.body?.getReader();check(reader,400,'body_required');let chunks=[],count=0;
 try{while(true){const p=await reader.read();if(p.done)break;count+=p.value.length;if(count>8192){await reader.cancel();throw new ApiError(413,'payload_too_large');}chunks.push(p.value);}}finally{reader.releaseLock();}
 const bytes=new Uint8Array(count);let i=0;for(const chunk of chunks){bytes.set(chunk,i);i+=chunk.length;}
 try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{throw new ApiError(400,'invalid_json');}
}
function config(env){
 check(env.PUBLIC_INTAKE_ENABLED==='true'&&env.MIRA_DB&&/^https:\/\/[^/]+$/.test(env.APP_ORIGIN||''),503,'intake_disabled');
 check(env.PUBLIC_INTAKE_PRIVACY_APPROVED==='true'&&typeof env.PUBLIC_INTAKE_PRIVACY_VERSION==='string'&&env.PUBLIC_INTAKE_PRIVACY_VERSION.length>0&&env.PUBLIC_INTAKE_PRIVACY_VERSION.length<=100,503,'intake_privacy_not_approved');
 let notice;try{notice=new URL(env.PUBLIC_INTAKE_PRIVACY_NOTICE_URL);}catch{throw new ApiError(503,'intake_privacy_not_approved');}
 check(notice.origin===env.APP_ORIGIN&&!notice.username&&!notice.password&&!notice.search&&!notice.hash,503,'intake_privacy_not_approved');
 check(typeof env.INTAKE_OPERATOR_SUBJECT==='string'&&env.INTAKE_OPERATOR_SUBJECT.length>0&&env.INTAKE_OPERATOR_SUBJECT.length<=200,503,'intake_operator_not_configured');
 check(typeof env.INTAKE_RATE_SECRET==='string'&&env.INTAKE_RATE_SECRET.length>=32&&env.TURNSTILE_SECRET_KEY&&/^[A-Za-z0-9_-]{3,100}$/.test(env.TURNSTILE_SITE_KEY||''),503,'intake_security_not_configured');
}
async function operatorReady(env){check(await one(env,"SELECT subject FROM mira_memberships WHERE subject=? AND role='operator' AND active=1",env.INTAKE_OPERATOR_SUBJECT),503,'intake_operator_unavailable');}
async function rate(request,env,kind){
 // Cloudflare-origin request header only; no X-Forwarded-For fallback.
 const ip=request.headers.get('CF-Connecting-IP');check(ip&&ip.length<=64,503,'trusted_client_address_required');
 const bucket=Math.floor(Date.now()/3600000);
 const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(env.INTAKE_RATE_SECRET),{name:'HMAC',hash:'SHA-256'},false,['sign']);
 const hash=hex(await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(`${kind}:${bucket}:${ip}`)));
 const quota=kind==='submit'?10:60;
 // An independently bounded global bucket also caps rotating-address abuse.
 for(const [subject,max] of [[`global:${kind}`,kind==='submit'?300:3000],[hash,quota]]){
  const r=await s(env,'INSERT INTO mira_intake_limits(subject_hash,bucket,uses) VALUES (?,?,1) ON CONFLICT(subject_hash,bucket) DO UPDATE SET uses=uses+1 WHERE uses<?',subject,bucket,max).run();
  check(r.meta.changes===1,429,'intake_rate_limit');
 }
 // Quota rows contain no raw IP; bounded retention, not an intake-record deletion.
 await s(env,'DELETE FROM mira_intake_limits WHERE bucket<?',bucket-48).run();
}
async function challenge(request,env,value,fetcher){
 text(value,1,2048);let r;
 try{const response=await fetcher('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:env.TURNSTILE_SECRET_KEY,response:value,remoteip:request.headers.get('CF-Connecting-IP')}),redirect:'manual',signal:AbortSignal.timeout(5000)});check(response.ok,503,'challenge_unavailable');r=await response.json();}catch{throw new ApiError(503,'challenge_unavailable');}
 check(r.success===true&&r.hostname===new URL(env.APP_ORIGIN).hostname&&r.action==='mira_intake',400,'challenge_rejected');
}
const receipt=r=>({id:r.id,status:r.status,version:r.version,received_at:r.created_at,updated_at:r.updated_at,response:r.public_response||null,meaning:'Запрос сохранён. Это не активация агентства и не подтверждение email.'});
async function submit(request,env,fetcher){
 const b=await body(request);keys(b,['company','city','name','email','consent_version','challenge']);
 const data={company:text(b.company,2,160),city:text(b.city,2,120),name:text(b.name,2,120),email:text(b.email,3,254).toLowerCase(),consent_version:b.consent_version};
 check(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email),400,'invalid_email');
 check(data.consent_version===env.PUBLIC_INTAKE_PRIVACY_VERSION,400,'current_consent_required');
 const idempotency=uuid(request.headers.get('Idempotency-Key')),tokenHash=await sha(token(request)),hash=await sha(JSON.stringify(data));
 await rate(request,env,'submit');
 const replay=async()=>{
  const row=await one(env,'SELECT * FROM mira_intake_requests WHERE idempotency_key=?',idempotency);
  if(!row)return null;
  check(row.token_hash===tokenHash&&row.request_hash===hash,409,'idempotency_payload_mismatch');return row;
 };
 const prior=await replay();if(prior)return json(receipt(prior));
 check(env.PUBLIC_INTAKE_SUBMISSIONS_PAUSED!=='true',503,'intake_submissions_paused');
 await operatorReady(env);await challenge(request,env,b.challenge,fetcher);
 const id=crypto.randomUUID(),now=new Date().toISOString();
 await env.MIRA_DB.batch([
  s(env,`INSERT INTO mira_intake_requests(id,idempotency_key,request_hash,token_hash,company,city,name,email,consent_version,assigned_subject,created_at,updated_at,last_event_id)
  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(idempotency_key) DO NOTHING`,id,idempotency,hash,tokenHash,data.company,data.city,data.name,data.email,data.consent_version,env.INTAKE_OPERATOR_SUBJECT,now,now,id),
  s(env,`INSERT INTO mira_intake_events(id,request_id,actor,status,version,created_at,event_kind,assigned_subject) SELECT id,id,'public_request',status,0,created_at,'received',assigned_subject FROM mira_intake_requests WHERE id=?`,id)
 ]);
 const saved=await replay();check(saved,500,'receipt_not_saved');return json(receipt(saved),saved.id===id?201:200);
}
/** Test seam injects only Siteverify transport; exported production handler uses fetch. */
export function createPublicIntake(fetcher=(...args)=>fetch(...args)){
 return async(request,env)=>{try{
  const url=new URL(request.url);check(url.origin===env.APP_ORIGIN,421,'unexpected_origin');
  check([ROOT+'/',ROOT+'/client.mjs',ROOT+'/submit',ROOT+'/status'].includes(url.pathname),404,'not_found');
  config(env);
  if(request.method==='GET'&&url.pathname===ROOT+'/client.mjs')return new Response(intakeClient,{headers:{...fixedHeaders,'Content-Type':'text/javascript; charset=utf-8'}});
  if(request.method==='GET'&&url.pathname===ROOT+'/'){
   if(env.PUBLIC_INTAKE_SUBMISSIONS_PAUSED!=='true')await operatorReady(env);
   return new Response(intakePage(env),{headers:{...fixedHeaders,'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; script-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; connect-src 'self' https://challenges.cloudflare.com; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"}});
  }
  check(request.method==='POST'&&[ROOT+'/submit',ROOT+'/status'].includes(url.pathname),405,'method_not_allowed');
  check(request.headers.get('Origin')===env.APP_ORIGIN,403,'origin_rejected');
  if(url.pathname===ROOT+'/submit')return await submit(request,env,fetcher);
  const b=await body(request);keys(b,['id']);const id=uuid(b.id),hash=await sha(token(request));await rate(request,env,'status');
  const row=await one(env,'SELECT * FROM mira_intake_requests WHERE id=? AND token_hash=?',id,hash);check(row,404,'receipt_not_found');
  return json(receipt(row));
 }catch(e){return json({error:e instanceof ApiError?e.code:'internal_error'},e instanceof ApiError?e.status:500);}};
}
export const publicIntake=createPublicIntake();
export {routeIntakeAdmin} from './intake-admin.mjs';
