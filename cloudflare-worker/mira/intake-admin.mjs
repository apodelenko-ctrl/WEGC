/** Existing signed Access identity + active operator only. No provisioning/sending. */
import {ApiError} from './auth.mjs';
import {intakeAdminHTML,intakeAdminClient} from './intake-admin-ui.mjs';
const ROOT='/mira/api/admin/intake';
const headers={'Cache-Control':'no-store, private','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow, noarchive','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"};
const json=b=>Response.json(b,{headers});
const check=(ok,status,code)=>{if(!ok)throw new ApiError(status,code);};
const s=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
const one=(env,sql,...args)=>s(env,sql,...args).first();
const all=async(env,sql,...args)=>(await s(env,sql,...args).all()).results||[];
const fields='id,company,city,name,email,email_verified,assigned_subject,status,version,created_at,updated_at,public_response';
const uuid=v=>{check(typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(v),400,'invalid_id');return v.toLowerCase();};
function text(v,min,max){check(typeof v==='string'&&v.trim().length>=min&&v.trim().length<=max&&!/[\u0000-\u001f\u007f]/.test(v),400,'invalid_field');return v.trim();}
function keys(b,allowed){check(b&&typeof b==='object'&&!Array.isArray(b)&&Object.keys(b).length===allowed.length&&allowed.every(k=>Object.hasOwn(b,k)),400,'invalid_fields');}
async function body(request){
 check((request.headers.get('Content-Type')||'').split(';')[0].trim()==='application/json',415,'json_required');
 const reader=request.body?.getReader();check(reader,400,'body_required');let chunks=[],size=0;
 try{while(true){const p=await reader.read();if(p.done)break;size+=p.value.length;if(size>8192){await reader.cancel();throw new ApiError(413,'payload_too_large');}chunks.push(p.value);}}finally{reader.releaseLock();}
 const bytes=new Uint8Array(size);let i=0;for(const c of chunks){bytes.set(c,i);i+=c.length;}
 try{return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));}catch{throw new ApiError(400,'invalid_json');}
}
export async function routeIntakeAdmin(request,env,m,identity){
 const url=new URL(request.url),path=url.pathname;
 if(path!==ROOT&&!path.startsWith(ROOT+'/'))return null;
 check(m.role==='operator'&&m.active===1,403,'operator_required');
 if(request.method==='GET'&&[ROOT+'/view',ROOT+'/client.mjs'].includes(path))return new Response(path.endsWith('/view')?intakeAdminHTML:intakeAdminClient,{headers:{...headers,'Content-Type':path.endsWith('/view')?'text/html; charset=utf-8':'text/javascript; charset=utf-8'}});
 if(request.method==='GET'&&path===ROOT+'/operators'){
  const rows=await all(env,"SELECT subject FROM mira_memberships WHERE role='operator' AND active=1 ORDER BY subject LIMIT 101");
  check(rows.length<=100,409,'operator_directory_limit');return json({records:rows,current_subject:identity.subject});
 }
 if(request.method==='GET'&&path===ROOT+'/summary'){
  const rows=await all(env,'SELECT status,COUNT(*) AS count,MIN(created_at) AS oldest_at FROM mira_intake_requests GROUP BY status');
  return json({records:rows,submissions_paused:env.PUBLIC_INTAKE_SUBMISSIONS_PAUSED==='true',public_intake_enabled:env.PUBLIC_INTAKE_ENABLED==='true'});
 }
 if(request.method==='GET'&&path===ROOT){
  const cursor=url.searchParams.get('cursor')||'',limit=Number(url.searchParams.get('limit')||25);
  check(Number.isSafeInteger(limit)&&limit>=1&&limit<=100,400,'invalid_limit');
  let rows;
  if(cursor){
   const parts=cursor.split('|');check(parts.length===2&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(parts[0]),400,'invalid_cursor');
   const id=uuid(parts[1]),time=parts[0];
   rows=await all(env,`SELECT ${fields} FROM mira_intake_requests WHERE created_at<? OR (created_at=? AND id<?) ORDER BY created_at DESC,id DESC LIMIT ?`,time,time,id,limit+1);
  }else rows=await all(env,`SELECT ${fields} FROM mira_intake_requests ORDER BY created_at DESC,id DESC LIMIT ?`,limit+1);
  const last=rows[limit-1];
  return json({records:rows.slice(0,limit),next_cursor:rows.length>limit?last.created_at+'|'+last.id:null,scope:'Unverified requests. No email sending, memberships or agency activation.'});
 }
 const match=path.match(/^\/mira\/api\/admin\/intake\/([0-9a-f-]+)(?:\/(history|assign|review))?$/i);check(match,404,'not_found');
 const id=uuid(match[1]),action=match[2];
 const row=await one(env,`SELECT ${fields} FROM mira_intake_requests WHERE id=?`,id);check(row,404,'receipt_not_found');
 if(request.method==='GET'&&!action)return json(row);
 if(request.method==='GET'&&action==='history'){
  const after=Number(url.searchParams.get('after_version')??-1),limit=Number(url.searchParams.get('limit')||50);
  check(Number.isSafeInteger(after)&&after>=-1&&Number.isSafeInteger(limit)&&limit>=1&&limit<=100,400,'invalid_history_page');
  const rows=await all(env,'SELECT actor,status,version,public_response,created_at,event_kind,assigned_subject,response_published FROM mira_intake_events WHERE request_id=? AND version>? ORDER BY version LIMIT ?',id,after,limit+1);
  return json({records:rows.slice(0,limit),next_after_version:rows.length>limit?rows[limit-1].version:null});
 }
 check(request.method==='POST'&&['assign','review'].includes(action),404,'not_found');
 check(request.headers.get('Origin')===env.APP_ORIGIN,403,'origin_rejected');
 const b=await body(request);keys(b,action==='assign'?['version','assigned_subject']:['version','status','response']);
 check(Number.isSafeInteger(b.version)&&b.version>=0,400,'invalid_version');check(row.version===b.version,409,'stale_version');
 let status=row.status,assigned=row.assigned_subject,response=row.public_response,published=false;
 if(action==='assign'){
  assigned=text(b.assigned_subject,1,200);check(row.status!=='closed',409,'request_closed');check(assigned!==row.assigned_subject,409,'already_assigned');
  check(await one(env,"SELECT subject FROM mira_memberships WHERE subject=? AND role='operator' AND active=1",assigned),409,'active_operator_required');
 }else{
  const transitions={received:['review','needs_information','responded','closed'],review:['needs_information','responded','closed'],needs_information:['review','responded','closed'],responded:['review','closed'],closed:[]};
  check(transitions[row.status]?.includes(b.status),409,'invalid_transition');status=b.status;
  // Null means status-only: retain the last explicitly published reply.
  published=b.response!==null;if(published)response=text(b.response,1,2000);
  check(!['responded','needs_information'].includes(status)||published,400,'public_response_required');
 }
 const event=crypto.randomUUID(),now=new Date().toISOString();
 const results=await env.MIRA_DB.batch([
  s(env,'UPDATE mira_intake_requests SET assigned_subject=?,status=?,public_response=?,version=version+1,updated_at=?,last_event_id=? WHERE id=? AND version=?',assigned,status,response,now,event,id,b.version),
  s(env,`INSERT INTO mira_intake_events(id,request_id,actor,status,version,public_response,created_at,event_kind,assigned_subject,response_published) SELECT ?,id,?,status,version,?,updated_at,?,assigned_subject,? FROM mira_intake_requests WHERE id=? AND last_event_id=?`,event,identity.subject,published?response:null,action,published?1:0,id,event)
 ]);
 check(results[0].meta.changes===1,409,'stale_version');
 return json({id,status,version:b.version+1,published_to_receipt:published,external_send:false});
}
