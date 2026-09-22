/** Read-only operator view. No write statements, private lineage or activation route. */
import {ApiError,verifyAccess} from './auth.mjs';
import {researchHTML,researchClient} from './research-ui.mjs';
const ROOT='/mira/api/admin/research';
const headers={'Cache-Control':'no-store, private','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow, noarchive','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"};
const json=(b,status=200)=>Response.json(b,{status,headers});
const ensure=(ok,status,code)=>{if(!ok)throw new ApiError(status,code);};
const stmt=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
const all=async(env,sql,...args)=>(await stmt(env,sql,...args).all()).results||[];
function value(url,key,max=240){const v=url.searchParams.get(key)||'';ensure(v.length<=max&&!/[\u0000-\u001f\u007f]/.test(v),400,'invalid_parameter');return v;}
function page(url){const limit=Number(url.searchParams.get('limit')||25);ensure(Number.isSafeInteger(limit)&&limit>0&&limit<=100,400,'invalid_limit');return{limit,cursor:value(url,'cursor')};}
function paged(rows,limit,key){return{records:rows.slice(0,limit),next_cursor:rows.length>limit?rows[limit-1][key]:null};}
export function createResearchView(verifier=verifyAccess){return async(request,env)=>{try{
 const url=new URL(request.url),path=url.pathname;
 ensure(url.origin===env.APP_ORIGIN,421,'unexpected_origin');ensure(request.method==='GET',405,'read_only');
 ensure(['/mira/research/','/mira/research/client.mjs',ROOT,ROOT+'/entities',ROOT+'/entity',ROOT+'/links'].includes(path),404,'not_found');
 ensure(env.MIRA_DB,503,'database_not_configured');
 const identity=await verifier(request,env);
 const member=await stmt(env,"SELECT subject FROM mira_memberships WHERE subject=? AND role='operator' AND active=1",identity.subject).first();ensure(member,403,'operator_required');
 if(path==='/mira/research/')return new Response(researchHTML,{headers:{...headers,'Content-Type':'text/html; charset=utf-8'}});
 if(path==='/mira/research/client.mjs')return new Response(researchClient,{headers:{...headers,'Content-Type':'text/javascript; charset=utf-8'}});
 const snapshot=env.MIRA_RESEARCH_SNAPSHOT;
 ensure(/^MIRA-IMPORT-[0-9a-f]{64}$/.test(snapshot||''),503,'research_snapshot_not_configured');
 const summary=await stmt(env,'SELECT * FROM mira_research_summary WHERE snapshot_id=? AND contains_private=0',snapshot).first();ensure(summary,503,'public_completed_snapshot_required');
 if(path===ROOT)return json({snapshot:summary,note:'Research candidates only. No verified legal-entity count, membership, agreement or current inventory is implied.'});
 const kind=value(url,'kind');ensure(['agency','developer'].includes(kind),400,'invalid_kind');
 if(path===ROOT+'/entities'){
  const {limit,cursor}=page(url),q=value(url,'q',120),city=value(url,'city',120);
  const rows=await all(env,`SELECT source_id,kind,name,city,market,segment FROM mira_published_research_entities
   WHERE snapshot_id=? AND kind=? AND source_id>? AND (?='' OR city=?)
   AND (?='' OR instr(lower(name),lower(?))>0 OR instr(lower(COALESCE(city,'')),lower(?))>0)
   ORDER BY source_id LIMIT ?`,snapshot,kind,cursor,city,city,q,q,q,limit+1);
  return json({snapshot_id:snapshot,...paged(rows,limit,'source_id')});
 }
 const id=value(url,'id');ensure(id,400,'id_required');
 const entity=await stmt(env,'SELECT source_id,kind,name,city,market,segment FROM mira_published_research_entities WHERE snapshot_id=? AND kind=? AND source_id=?',snapshot,kind,id).first();ensure(entity,404,'entity_not_found');
 if(path===ROOT+'/entity'){
  const rows=await all(env,'SELECT field_key,occurrence,value_json,evidence_json,verification_status,conversation_scope FROM mira_research_fields WHERE snapshot_id=? AND kind=? AND source_id=? ORDER BY field_key,occurrence LIMIT 201',snapshot,kind,id);
  ensure(rows.length<=200,409,'field_limit_exceeded');
  return json({snapshot_id:snapshot,entity,fields:rows.map(r=>({field:r.field_key,occurrence:r.occurrence,value:JSON.parse(r.value_json),evidence:JSON.parse(r.evidence_json),verification_status:r.verification_status,conversation_scope:r.conversation_scope})),note:'Missing/not_checked fields are not verified contacts. Public channel is not direct dialogue.'});
 }
 ensure(kind==='developer',400,'developer_required');const {limit,cursor}=page(url);
 const rows=await all(env,'SELECT project_id,market,mapping_status FROM mira_research_project_links WHERE snapshot_id=? AND developer_id=? AND project_id>? ORDER BY project_id LIMIT ?',snapshot,id,cursor,limit+1);
 return json({snapshot_id:snapshot,...paged(rows,limit,'project_id'),note:'Mapping is research evidence, not availability or legal seller approval.'});
 }catch(e){return json({error:e instanceof ApiError?e.code:'internal_error'},e instanceof ApiError?e.status:500);}};}
export const researchView=createResearchView();
