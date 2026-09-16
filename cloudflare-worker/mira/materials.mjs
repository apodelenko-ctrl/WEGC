/** Assigned developer catalogue and rights-gated, private R2 asset delivery.
 * No URL fetching, uploads, client sharing, deployment or external messaging.
 */
import {ApiError} from './auth.mjs';
import {currentEvidence,evidenceRef,identifier,iso,requireKeys,string} from './rules.mjs';
const stmt=(env,sql,...v)=>env.MIRA_DB.prepare(sql).bind(...v);
const first=(env,sql,...v)=>stmt(env,sql,...v).first();
const all=async(env,sql,...v)=>(await stmt(env,sql,...v).all()).results||[];
const nowISO=()=>new Date().toISOString();
function assert(condition,status,code){if(!condition)throw new ApiError(status,code);}
function pageSettings(url){const raw=url.searchParams.get('limit')||'50';assert(/^[0-9]+$/.test(raw),400,'invalid_page');const limit=Number(raw);assert(limit>=1&&limit<=100,400,'invalid_page');const cursor=url.searchParams.get('cursor')||'';if(cursor)identifier(cursor);return {limit,cursor};}
function pageResult(rows,limit){return {records:rows.slice(0,limit),next_cursor:rows.length>limit?rows[limit-1].id:null};}
const TYPES={'application/pdf':'pdf','image/png':'png','image/jpeg':'jpg','image/webp':'webp'};
export const MAX_MATERIAL_BYTES=8*1024*1024; // Deliberate MVP resource policy, not a provider limit.
export const hashBytes=async b=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b))).map(x=>x.toString(16).padStart(2,'0')).join('');
const materialId=id=>{identifier(id);assert(/^MAT-[A-Za-z0-9_-]+$/.test(id),400,'material_id_required');return id;};
const contentHash=h=>{assert(typeof h==='string'&&/^[a-f0-9]{64}$/.test(h),400,'content_hash_required');return h;};
const operator=m=>assert(m.role==='operator',403,'operator_required');
const enabled=env=>env.MATERIALS_ENABLED==='true'&&Boolean(env.MIRA_MATERIALS?.get);
export const objectKey=row=>`marketing/${identifier(row.project_id)}/${contentHash(row.sha256)}.${TYPES[row.mime_type]}`;

export function materialReleaseFacts(f){
 requireKeys(f,['sha256','mime_type','size_bytes','audience','allow_download','content_reviewed','malware_scan_ref'],['sha256','mime_type','size_bytes','audience','allow_download','content_reviewed','malware_scan_ref']);
 contentHash(f.sha256);assert(Object.hasOwn(TYPES,f.mime_type)&&Number.isSafeInteger(f.size_bytes)&&f.size_bytes>0&&f.size_bytes<=MAX_MATERIAL_BYTES,400,'unsupported_material');
 assert(f.audience==='agency_internal'&&f.allow_download===true&&f.content_reviewed===true,400,'material_release_required');
 assert(typeof f.malware_scan_ref==='string'&&/^SCAN-[A-Za-z0-9_-]{1,90}$/.test(f.malware_scan_ref),400,'scan_reference_required');
 return {...f};
}
async function assignedProject(env,id,m){
 const p=await first(env,'SELECT id,name,market,developer_family,enabled FROM mira_projects WHERE id=?',identifier(id));
 assert(p&&(m.role==='operator'||await first(env,'SELECT project_id FROM mira_agency_projects WHERE agency_id=? AND project_id=?',m.agency_id,id)),404,'project_not_found');
 return p;
}
async function activeAgreement(env,m){
 if(m.role==='operator')return;
 const a=await first(env,'SELECT status,agreement_ref FROM mira_agencies WHERE id=?',m.agency_id);
 const e=a?.agreement_ref?await first(env,'SELECT * FROM mira_evidence WHERE id=?',a.agreement_ref):null;
 assert(a?.status==='active'&&currentEvidence(e,'agency_agreement',{agency_id:m.agency_id}),403,'agency_agreement_not_current');
}
async function proofs(env,row,m){
 const scope={project_id:row.project_id,entity_id:row.id};
 const rights=await first(env,'SELECT * FROM mira_evidence WHERE id=?',row.rights_ref);
 const release=await first(env,'SELECT * FROM mira_evidence WHERE id=?',row.release_ref);
 if(!currentEvidence(rights,'materials_rights',scope)||!currentEvidence(release,'material_release',scope)||!rights.expires_at||!release.expires_at)return null;
 if(rights.agency_id!==release.agency_id||(m.role!=='operator'&&rights.agency_id&&rights.agency_id!==m.agency_id))return null;
 if(!row.expires_at||!Number.isFinite(Date.parse(row.expires_at))||Date.parse(row.expires_at)<=Date.now()||Date.parse(row.expires_at)>Math.min(Date.parse(rights.expires_at),Date.parse(release.expires_at)))return null;
 let f;try{f=materialReleaseFacts(JSON.parse(release.facts_json));}catch{return null;}
 if(f.sha256!==row.sha256||f.mime_type!==row.mime_type||f.size_bytes!==row.size_bytes)return null;
 return {rights,release};
}
async function eligible(env,row,m){
 return Boolean(row&&!row.revoked_at&&await proofs(env,row,m));
}
async function readBounded(object,expected){
 assert(object&&object.body&&object.size===expected.size_bytes,409,'material_object_missing_or_changed');
 assert(expected.size_bytes<=MAX_MATERIAL_BYTES,413,'material_too_large');
 const reader=object.body.getReader(),bytes=new Uint8Array(expected.size_bytes);let offset=0;
 try{
  while(true){const {value,done}=await reader.read();if(done)break;assert(value instanceof Uint8Array&&offset+value.length<=bytes.length,409,'material_size_mismatch');bytes.set(value,offset);offset+=value.length;}
 }catch(e){await reader.cancel().catch(()=>{});throw e;}finally{reader.releaseLock();}
 assert(offset===expected.size_bytes,409,'material_size_mismatch');
 const signature=expected.mime_type==='application/pdf'?new TextDecoder().decode(bytes.slice(0,5))==='%PDF-':expected.mime_type==='image/png'?[137,80,78,71,13,10,26,10].every((x,i)=>bytes[i]===x):expected.mime_type==='image/jpeg'?bytes[0]===255&&bytes[1]===216&&bytes[2]===255:expected.mime_type==='image/webp'?new TextDecoder().decode(bytes.slice(0,4))==='RIFF'&&new TextDecoder().decode(bytes.slice(8,12))==='WEBP':false;
 assert(signature&&await hashBytes(bytes)===expected.sha256,409,'material_content_changed');
 return bytes;
}
const publicMaterial=row=>({id:row.id,title:row.title,kind:row.kind,language:row.language,mime_type:row.mime_type,size_bytes:row.size_bytes,sha256:row.sha256,expires_at:row.expires_at,download_path:'/mira/api/materials/'+row.id+'/download',audience:'agency_internal',client_sharing_allowed:false});

export async function materialList(env,id,m,url){
 await assignedProject(env,id,m);await activeAgreement(env,m);
 if(!enabled(env))return {records:[],next_cursor:null,delivery_status:'not_configured_or_closed',note:'Storage or controlled material delivery is not enabled. No public URLs are substituted.'};
 const {limit,cursor}=pageSettings(url||new URL('https://internal.test/'));
 const rows=await all(env,'SELECT * FROM mira_materials WHERE project_id=? AND id>? ORDER BY id LIMIT ?',id,cursor,limit+1),page=pageResult(rows,limit),records=[];
 for(const row of page.records)if(await eligible(env,row,m))records.push(publicMaterial(row));
 return {records,next_cursor:page.next_cursor,delivery_status:'configured_access_rechecked_at_download',note:'Internal agency use only. No client-sharing or commercial availability is inferred. A page can be empty after rights filtering; follow next_cursor when present.'};
}
export async function developerCatalogue(env,m,url,groupId){
 const query='SELECT p.id,p.name,p.market,p.developer_family,p.enabled FROM mira_projects p';
 const projects=m.role==='operator'?await all(env,query+' ORDER BY p.id'):await all(env,query+' JOIN mira_agency_projects a ON a.project_id=p.id WHERE a.agency_id=? ORDER BY p.id',m.agency_id);
 const groups=new Map();
 for(const p of projects){const name=p.developer_family||null;if(!groups.has(name))groups.set(name,[]);groups.get(name).push(p);}
 const result=[];
 for(const [name,rows]of groups){const id='DEV-'+(await hashBytes(new TextEncoder().encode(JSON.stringify(name)))).slice(0,24);result.push({id,name,identity_status:'catalogue_family_not_legal_identity',markets:[...new Set(rows.map(p=>p.market))],assigned_project_count:rows.length,projects:rows});}
 result.sort((a,b)=>a.id.localeCompare(b.id));
 if(groupId){const r=result.find(x=>x.id===groupId);assert(r,404,'developer_not_found');return r;}
 const {limit,cursor}=pageSettings(url);return {...pageResult(result.filter(x=>x.id>cursor).map(({projects,...rest})=>rest),limit),note:'Only assigned project groups. Counts are scoped to this agency, not the full developer portfolio. Brand/family is not buyer seller or proof of an agency agreement.'};
}
export async function registerMaterial(env,m,identity,b){
 operator(m);
 requireKeys(b,['id','project_id','title','kind','language','mime_type','size_bytes','sha256','rights_ref','release_ref','expires_at'],['id','project_id','title','kind','language','mime_type','size_bytes','sha256','rights_ref','release_ref','expires_at']);
 const row={id:materialId(b.id),project_id:identifier(b.project_id),title:string(b.title,1,160),kind:b.kind,language:b.language,mime_type:b.mime_type,size_bytes:b.size_bytes,sha256:contentHash(b.sha256),rights_ref:evidenceRef(b.rights_ref),release_ref:evidenceRef(b.release_ref),expires_at:iso(b.expires_at)};
 assert(['brochure','floor_plan','field_report','training'].includes(row.kind)&&['ru','en','th'].includes(row.language)&&Object.hasOwn(TYPES,row.mime_type)&&Number.isSafeInteger(row.size_bytes)&&row.size_bytes>0&&row.size_bytes<=MAX_MATERIAL_BYTES,400,'unsupported_material');
 await assignedProject(env,row.project_id,m);
 assert(await proofs(env,row,m),409,'material_rights_or_release_not_current');
 const existing=await first(env,'SELECT * FROM mira_materials WHERE id=?',row.id);
 if(existing){assert(!existing.revoked_at&&Object.keys(row).every(k=>row[k]===existing[k]),409,'material_version_conflict');return {id:row.id,status:'recorded',created:false,activation:false};}
 assert(env.MIRA_MATERIALS?.get,503,'material_storage_not_configured');
 await readBounded(await env.MIRA_MATERIALS.get(objectKey(row)),row);
 assert(await proofs(env,row,m),409,'material_rights_or_release_not_current');
 const at=nowISO();
 try{await env.MIRA_DB.batch([
  stmt(env,`INSERT INTO mira_materials (id,project_id,title,kind,language,mime_type,size_bytes,sha256,rights_ref,release_ref,expires_at,created_by,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`,row.id,row.project_id,row.title,row.kind,row.language,row.mime_type,row.size_bytes,row.sha256,row.rights_ref,row.release_ref,row.expires_at,identity.subject,at),
  stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,status,version,actor,reason,evidence_ref,created_at) VALUES (?,'material',?,'registered',0,?,'Reviewed asset version recorded',?,?)`,crypto.randomUUID(),row.id,identity.subject,row.release_ref,at)
 ]);}catch(e){if(String(e.message).includes('UNIQUE'))throw new ApiError(409,'material_version_conflict');throw e;}
 return {id:row.id,status:'recorded',created:true,activation:false};
}
export async function revokeMaterial(env,m,identity,id,b){
 operator(m);materialId(id);requireKeys(b,['reason'],['reason']);const reason=string(b.reason,3,240),row=await first(env,'SELECT * FROM mira_materials WHERE id=?',id);assert(row,404,'material_not_found');
 if(row.revoked_at)return {id,status:'revoked',revoked_at:row.revoked_at};
 const at=nowISO();
 try{await env.MIRA_DB.batch([
 stmt(env,'UPDATE mira_materials SET revoked_at=? WHERE id=? AND revoked_at IS NULL',at,id),
 stmt(env,`INSERT INTO mira_events (id,entity_type,entity_id,status,version,actor,reason,created_at) VALUES (?,'material',?,'revoked',1,?,?,?)`,crypto.randomUUID(),id,identity.subject,reason,at)
 ]);}catch(e){if(String(e.message).includes('UNIQUE'))throw new ApiError(409,'material_version_conflict');throw e;}
 return {id,status:'revoked',revoked_at:at};
}
export async function downloadMaterial(request,env,m,identity,id){
 materialId(id);assert(!request.headers.has('Range'),416,'material_range_not_supported');
 const check=async()=>{
  const member=await first(env,'SELECT agency_id,role,active FROM mira_memberships WHERE subject=?',identity.subject);
  assert(member?.active&&member.role===m.role&&member.agency_id===m.agency_id,403,'membership_required');
  const row=await first(env,'SELECT * FROM mira_materials WHERE id=?',id);assert(row,404,'material_not_found');
  await assignedProject(env,row.project_id,m);await activeAgreement(env,m);
  assert(enabled(env),503,'material_delivery_closed');assert(await eligible(env,row,m),404,'material_not_available');return row;
 };
 const row=await check(),bytes=await readBounded(await env.MIRA_MATERIALS.get(objectKey(row)),row);
 await check(); // Do not release bytes when evidence or membership changed during retrieval.
 await stmt(env,'INSERT INTO mira_material_access (id,material_id,agency_id,actor,sha256,served_at) VALUES (?,?,?,?,?,?)',crypto.randomUUID(),id,m.agency_id,identity.subject,row.sha256,nowISO()).run();
 return new Response(bytes,{headers:{'Content-Type':row.mime_type,'Content-Length':String(bytes.length),'Content-Disposition':`attachment; filename="${row.id}.${TYPES[row.mime_type]}"`,'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"sandbox; default-src 'none'; frame-ancestors 'none'",'Cross-Origin-Resource-Policy':'same-origin'}});
}
export async function routeSupply(request,env,m,identity,{bodyOf,json}){
 const url=new URL(request.url),path=url.pathname;
 const developers=path.match(/^\/mira\/api\/developers(?:\/(DEV-[a-f0-9]{24}))?$/);
 if(developers&&request.method==='GET')return json(await developerCatalogue(env,m,url,developers[1]));
 const listing=path.match(/^\/mira\/api\/projects\/([A-Za-z0-9_-]+)\/materials$/);
 if(listing&&request.method==='GET')return json(await materialList(env,listing[1],m,url));
 if(path==='/mira/api/admin/materials'&&request.method==='POST'){const r=await registerMaterial(env,m,identity,await bodyOf(request));return json(r,r.created?201:200);}
 const revoke=path.match(/^\/mira\/api\/admin\/materials\/(MAT-[A-Za-z0-9_-]+)\/revoke$/);
 if(revoke&&request.method==='POST')return json(await revokeMaterial(env,m,identity,revoke[1],await bodyOf(request)));
 const download=path.match(/^\/mira\/api\/materials\/(MAT-[A-Za-z0-9_-]+)\/download$/);
 if(download&&request.method==='GET')return downloadMaterial(request,env,m,identity,download[1]);
 return null;
}
