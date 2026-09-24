/** Erase contact payload and every reply atomically; retain only a short-lived receipt tombstone. */
const s=(env,sql,...args)=>env.MIRA_DB.prepare(sql).bind(...args);
function dates(now){return {time:new Date(now).toISOString(),expiry:new Date(now+31*86400000).toISOString()};}
export async function eraseIntake(env,id,version,actor,now=Date.now()){
 const {time,expiry}=dates(now);
 const result=await env.MIRA_DB.batch([
  s(env,`INSERT INTO mira_intake_erasure(request_id,idempotency_key,token_hash,actor,reason,erased_at,expires_at)
   SELECT id,idempotency_key,token_hash,?,'request',?,? FROM mira_intake_requests WHERE id=? AND version=?`,actor,time,expiry,id,version),
  s(env,'DELETE FROM mira_intake_events WHERE request_id=? AND EXISTS(SELECT 1 FROM mira_intake_erasure WHERE request_id=?)',id,id),
  s(env,'DELETE FROM mira_intake_requests WHERE id=? AND EXISTS(SELECT 1 FROM mira_intake_erasure WHERE request_id=?)',id,id)
 ]);
 return result[0].meta.changes===1;
}
export async function expireIntakes(env,now=Date.now()){
 if(env.INTAKE_RETENTION_ENABLED!=='true')return {erased:0,enabled:false};
 const {time,expiry}=dates(now),cutoff=new Date(now);cutoff.setUTCFullYear(cutoff.getUTCFullYear()-2);
 // Also reapply retained tombstones if an operational restore brought rows back.
 await env.MIRA_DB.batch([s(env,'DELETE FROM mira_intake_events WHERE request_id IN (SELECT request_id FROM mira_intake_erasure)'),s(env,'DELETE FROM mira_intake_requests WHERE id IN (SELECT request_id FROM mira_intake_erasure)')]);
 let erased=0;
 // At most 1,000 requests per hourly run; greater than the 300/hour submission ceiling.
 for(let page=0;page<10;page++){
  const result=await env.MIRA_DB.batch([
   s(env,`INSERT INTO mira_intake_erasure(request_id,idempotency_key,token_hash,actor,reason,erased_at,expires_at)
    SELECT id,idempotency_key,token_hash,'retention_job','retention',?,? FROM mira_intake_requests
    WHERE updated_at<=? ORDER BY updated_at,id LIMIT 100`,time,expiry,cutoff.toISOString()),
   s(env,'DELETE FROM mira_intake_events WHERE request_id IN (SELECT request_id FROM mira_intake_erasure)'),
   s(env,'DELETE FROM mira_intake_requests WHERE id IN (SELECT request_id FROM mira_intake_erasure)')
  ]);
  erased+=result[0].meta.changes;if(result[0].meta.changes<100)break;
 }
 await s(env,'DELETE FROM mira_intake_erasure WHERE expires_at<=?',time).run();
 return {erased,enabled:true};
}
