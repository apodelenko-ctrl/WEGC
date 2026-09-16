/** Read-only agency experience and operator qualification. Never sends external messages. */
import {ApiError} from './auth.mjs';
import {requireKeys,identifier,string,currentEvidence} from './rules.mjs';
const stmt=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
const first=(env,sql,...args)=>stmt(env,sql,...args).first();
const all=async(env,sql,...args)=>(await stmt(env,sql,...args).all()).results||[];
function check(ok,status,code){if(!ok)throw new ApiError(status,code);}
export const APPLICATION_TRANSITIONS=Object.freeze({
 received:['review','rejected'],review:['needs_information','qualified','rejected'],
 needs_information:['review','closed'],qualified:['onboarded','needs_information','rejected'],
 rejected:['review','closed'],onboarded:['closed'],closed:[]
});
const PROJECT_REQUIREMENTS=Object.freeze([
 ['agreement_ref','project_agreement'],['inventory_ref','inventory'],
 ['registration_rules_ref','registration_rules'],['commission_schedule_ref','commission_schedule'],
 ['materials_rights_ref','materials_rights']
]);
export async function projectDetail(env,id,m){
 const p=await first(env,'SELECT * FROM mira_projects WHERE id=?',identifier(id));
 check(p,404,'project_not_found');
 if(m.role!=='operator')check(await first(env,'SELECT 1 AS allowed FROM mira_agency_projects WHERE agency_id=? AND project_id=?',m.agency_id,id),404,'project_not_found');
 const checks=await Promise.all(PROJECT_REQUIREMENTS.map(async([field,kind])=>{
  const e=p[field]?await first(env,'SELECT * FROM mira_evidence WHERE id=?',p[field]):null;
  let state=!e?'missing':currentEvidence(e,kind,{project_id:id})?'current':'not_current';
  if(state==='current'&&kind==='inventory'&&!e.expires_at)state='expiry_missing';
  if(state==='current'&&kind==='project_agreement'){
   let facts={};try{facts=JSON.parse(e.facts_json);}catch{}
   if(!p.legal_seller||facts.legal_seller!==p.legal_seller||['unknown','not_verified'].includes(p.legal_seller.toLowerCase()))state='seller_mismatch';
  }
  // Do not disclose raw vault paths, contract contents or evidence IDs to agency users.
  return {kind,state,verified_at:e?.verified_at||null,expires_at:e?.expires_at||null};
 }));
 return {project:{id:p.id,name:p.name,market:p.market,developer_family:p.developer_family,legal_seller:p.legal_seller,enabled:p.enabled===1,updated_at:p.updated_at},checks,
  registration_eligible:p.enabled===1&&checks.filter(c=>c.kind!=='materials_rights').every(c=>c.state==='current'),
  materials_available:false,
  note:'Readiness is checked now and again on submission. Intake is not developer acknowledgement or lead protection. No inventory prices or commission amounts are inferred.'};
}
export async function agencyProfile(env,m){
 if(m.role==='operator')return {role:'operator',agency:null,available_markets:[],activation_status:'not_inferred_from_access'};
 const a=await first(env,'SELECT id,name,city,status,agreement_ref FROM mira_agencies WHERE id=?',m.agency_id);
 const e=a?.agreement_ref?await first(env,'SELECT * FROM mira_evidence WHERE id=?',a.agreement_ref):null;
 return {role:m.role,agency:a?{id:a.id,name:a.name,city:a.city,status:a.status}:null,
  agreement_current:currentEvidence(e,'agency_agreement',{agency_id:m.agency_id}),
  available_markets:(await all(env,'SELECT DISTINCT p.market FROM mira_projects p JOIN mira_agency_projects a ON a.project_id=p.id WHERE a.agency_id=? ORDER BY p.market',m.agency_id)).map(p=>p.market),
  activation_status:'not_inferred_from_access',note:'Assigned market metadata does not prove an enabled supply path. Client relationships remain with the agency.'};
}
export async function applicationDetail(env,id,identity,operatorMode=false){
 const a=await first(env,'SELECT id,subject,email,company,city,name,format,demand,markets_json,status,version,agency_id,created_at,updated_at FROM mira_applications WHERE id=?',identifier(id));
 check(a&&(operatorMode||a.subject===identity.subject),404,'application_not_found');
 const events=await all(env,'SELECT status,version,created_at'+(operatorMode?',reason,evidence_ref':'')+' FROM mira_events WHERE entity_type=\'application\' AND entity_id=? ORDER BY version',id);
 if(!operatorMode)delete a.subject;
 return {application:a,events,allowed_transitions:operatorMode?(APPLICATION_TRANSITIONS[a.status]||[]):[],meaning:'Qualification and onboarding are not agency activation or developer registration.'};
}
export async function reviewApplication(env,id,m,identity,b){
 check(m.role==='operator',403,'operator_required');
 const {application:a}=await applicationDetail(env,id,identity,true);
 requireKeys(b,['status','version','reason','evidence_ref','agency_id'],['status','version','reason']);
 check(Number.isSafeInteger(b.version)&&b.version===a.version,409,'stale_version');
 check(APPLICATION_TRANSITIONS[a.status]?.includes(b.status),409,'invalid_transition');
 const reason=string(b.reason,3,240);let agency=a.agency_id||null,proof=null;
 if(b.status==='qualified'||b.status==='onboarded'){
  const kind=b.status==='qualified'?'application_qualification':'agency_onboarding';
  proof=await first(env,'SELECT * FROM mira_evidence WHERE id=?',identifier(b.evidence_ref));
  if(b.status==='onboarded')agency=identifier(b.agency_id);
  check(currentEvidence(proof,kind,{entity_id:id,...(b.status==='onboarded'?{agency_id:agency}:{})}),409,'evidence_missing_stale_or_wrong_scope');
 }
 else check(b.agency_id===undefined&&b.evidence_ref===undefined,400,'unexpected_review_fields');
 if(b.status==='qualified')check(b.agency_id===undefined,400,'unexpected_review_fields');
 if(b.status==='onboarded'){
  const account=await first(env,'SELECT * FROM mira_agencies WHERE id=? AND status=\'active\'',agency);
  const agreement=account?.agreement_ref?await first(env,'SELECT * FROM mira_evidence WHERE id=?',account.agreement_ref):null;
  const owner=await first(env,'SELECT 1 AS present FROM mira_memberships WHERE subject=? AND agency_id=? AND role=\'agency_owner\' AND active=1',a.subject,agency);
  check(account&&owner&&currentEvidence(agreement,'agency_agreement',{agency_id:agency}),409,'onboarding_account_not_ready');
 }
 const event=crypto.randomUUID(),now=new Date().toISOString();
 const results=await env.MIRA_DB.batch([
  stmt(env,'UPDATE mira_applications SET status=?,version=version+1,agency_id=?,updated_at=?,last_event_id=? WHERE id=? AND version=?',b.status,agency,now,event,id,b.version),
  stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at) SELECT ?,'application',id,agency_id,?,status,version,?,?,? FROM mira_applications WHERE id=? AND last_event_id=?`,event,identity.subject,proof?.id||null,reason,now,id,event)
 ]);
 check(results[0].meta.changes===1,409,'stale_version');
 return {id,status:b.status,version:b.version+1,agency_id:agency,activation_recorded:false,outreach_sent:false};
}
