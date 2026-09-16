/** All organizations, bytes, identities and evidence here are synthetic fixtures. */
import test from 'node:test';import assert from 'node:assert/strict';
import {DatabaseSync}from'node:sqlite';import{readFileSync,readdirSync}from'node:fs';
import {createHandler}from'../cloudflare-worker/mira/worker.mjs';
import {hashBytes,objectKey,MAX_MATERIAL_BYTES}from'../cloudflare-worker/mira/materials.mjs';
class D1{
 constructor(){this.db=new DatabaseSync(':memory:');this.db.exec('PRAGMA foreign_keys=ON');for(const f of readdirSync('cloudflare-worker/mira/migrations').filter(x=>x.endsWith('.sql')).sort())this.db.exec(readFileSync('cloudflare-worker/mira/migrations/'+f,'utf8'));}
 prepare(sql){const d=this.db;return{bind(...v){const s=d.prepare(sql);return{_run:()=>s.run(...v),first:async()=>s.get(...v)||null,all:async()=>({results:s.all(...v)}),run:async()=>({meta:s.run(...v)})};}};}
 async batch(ss){this.db.exec('BEGIN');try{const r=ss.map(s=>({meta:s._run()}));this.db.exec('COMMIT');return r;}catch(e){this.db.exec('ROLLBACK');throw e;}}
}
const at=()=>new Date(Date.now()-5000).toISOString(),expiry=()=>new Date(Date.now()+86400000).toISOString();
async function setup(){
 const db=new D1(),sql=(q,...v)=>db.db.prepare(q).run(...v);
 const env={MIRA_DB:db,APP_ORIGIN:'https://mira.example.test',MATERIALS_ENABLED:'true'};
 for(const id of ['A','B'])sql('INSERT INTO mira_agencies (id,name,city,status,agreement_ref,created_at) VALUES (?,?,?,?,?,?)',id,'SYNTHETIC '+id,'SYNTHETIC City','active','EVID-agreement-'+id,at());
 for(const [sub,agency,role]of[['ownerA','A','agency_owner'],['brokerA','A','broker'],['ownerB','B','agency_owner'],['op',null,'operator']])sql('INSERT INTO mira_memberships VALUES (?,?,?,?)',sub,agency,role,1);
 for(const [id,family]of[['P','SYNTHETIC Family'],['Q','HIDDEN Family'],['R','SYNTHETIC Family']])sql('INSERT INTO mira_projects (id,name,market,developer_family,updated_at) VALUES (?,?,?,?,?)',id,'SYNTHETIC '+id,'phuket',family,at());
 sql('INSERT INTO mira_agency_projects VALUES (?,?)','A','P');sql('INSERT INTO mira_agency_projects VALUES (?,?)','B','Q');sql('INSERT INTO mira_agency_projects VALUES (?,?)','B','R');
 const ev=(id,kind,{project=null,agency=null,entity=null,facts={},until=expiry()}={})=>sql('INSERT INTO mira_evidence (id,kind,storage_ref,project_id,agency_id,entity_id,verified,verified_by,verified_at,expires_at,facts_json) VALUES (?,?,?,?,?,?,1,?,?,?,?)',id,kind,'EVID-PRIVATE-VAULT-POINTER',project,agency,entity,'SYNTHETIC-op',at(),until,JSON.stringify(facts));
 for(const id of ['A','B'])ev('EVID-agreement-'+id,'agency_agreement',{agency:id});
 const bytes=new TextEncoder().encode('%PDF-1.4\nSYNTHETIC TEST ASSET; not a production document.\n%%EOF'),sha=await hashBytes(bytes);
 const body={id:'MAT-one',project_id:'P',title:'SYNTHETIC brochure',kind:'brochure',language:'en',mime_type:'application/pdf',size_bytes:bytes.length,sha256:sha,rights_ref:'EVID-rights',release_ref:'EVID-release',expires_at:new Date(Date.now()+3600000).toISOString()};
 const facts={sha256:sha,mime_type:body.mime_type,size_bytes:bytes.length,audience:'agency_internal',allow_download:true,content_reviewed:true,malware_scan_ref:'SCAN-synthetic'};
 ev('EVID-rights','materials_rights',{project:'P',entity:body.id});ev('EVID-release','material_release',{project:'P',entity:body.id,facts});
 const objects=new Map([[objectKey(body),bytes]]),keys=[];
 env.MIRA_MATERIALS={async get(key){keys.push(key);const b=objects.get(key);return b?{size:b.length,body:new ReadableStream({start(c){c.enqueue(b);c.close();}})}:null;}};
 const handler=createHandler(async r=>({subject:r.headers.get('X-Test-Subject')||'ownerA',email:'synthetic@example.test'}));
 const request=(path,user='ownerA',data,headers={})=>handler(new Request(env.APP_ORIGIN+'/mira/api'+path,{method:data===undefined?'GET':'POST',headers:{'X-Test-Subject':user,...(data===undefined?{}:{Origin:env.APP_ORIGIN,'Content-Type':'application/json'}),...headers},body:data===undefined?undefined:JSON.stringify(data)}),env);
 const record=()=>request('/admin/materials','op',body);
 return {env,db,sql,ev,bytes,body,facts,objects,keys,request,record};
}
test('developer catalogue contains assigned groups only, not another agency portfolio',async()=>{
 const t=await setup(),r=await(await t.request('/developers')).json();assert.equal(r.records.length,1);assert.equal(r.records[0].assigned_project_count,1);assert.equal(r.records[0].identity_status,'catalogue_family_not_legal_identity');assert(!JSON.stringify(r).includes('HIDDEN'));
 const d=await(await t.request('/developers/'+r.records[0].id)).json();assert.deepEqual(d.projects.map(x=>x.id),['P']);
 const b=await(await t.request('/developers','ownerB')).json();const hidden=b.records.find(x=>x.name==='HIDDEN Family');assert.equal((await t.request('/developers/'+hidden.id)).status,404);
});
test('developer pagination and grouping do not claim a resolved legal seller',async()=>{
 const t=await setup(),r=await(await t.request('/developers?limit=1','ownerB')).json();assert.equal(r.records.length,1);assert(r.next_cursor);const next=await(await t.request('/developers?limit=1&cursor='+r.next_cursor,'ownerB')).json();assert.equal(next.records.length,1);assert.notEqual(next.records[0].id,r.records[0].id);assert.equal((await t.request('/developers?limit=1000')).status,400);
});
test('material release evidence API validates scope facts and scanner reference',async()=>{
 const t=await setup(),data={id:'EVID-release-api',kind:'material_release',storage_ref:'EVID-vault',project_id:'P',entity_id:'MAT-api',verified:true,verified_at:at(),expires_at:expiry(),facts:t.facts};
 assert.equal((await t.request('/admin/evidence','op',data)).status,201);assert.equal((await t.request('/admin/evidence','ownerA',{...data,id:'EVID-no'})).status,403);
 for(const facts of [{...t.facts,malware_scan_ref:''},{...t.facts,allow_download:false},{...t.facts,client_sharing:true},{...t.facts,mime_type:'text/html'}])assert.equal((await t.request('/admin/evidence','op',{...data,id:'EVID-bad',facts})).status,400);
});
test('only operator registers and registration validates actual immutable asset bytes',async()=>{
 const t=await setup();assert.equal((await t.request('/admin/materials','ownerA',t.body)).status,403);const r=await t.record();assert.equal(r.status,201);assert.equal((await r.json()).activation,false);assert.equal((await t.record()).status,200);assert.equal(t.db.db.prepare('SELECT COUNT(*) n FROM mira_materials').get().n,1);
 assert.equal((await t.request('/admin/materials','op',{...t.body,title:'Changed version'})).status,409);
 assert.throws(()=>t.sql('UPDATE mira_materials SET title=? WHERE id=?','changed','MAT-one'));assert.throws(()=>t.sql('DELETE FROM mira_materials WHERE id=?','MAT-one'));
});
test('listing hides evidence refs/storage paths and another tenant material metadata',async()=>{
 const t=await setup();await t.record();const r=await(await t.request('/projects/P/materials')).json();assert.equal(r.records.length,1);assert.equal(r.records[0].client_sharing_allowed,false);assert(!JSON.stringify(r).includes('PRIVATE-VAULT'));assert(!JSON.stringify(r).includes('rights_ref'));assert.equal((await t.request('/projects/P/materials','ownerB')).status,404);
});
test('download rechecks identity and delivers exact bytes as private attachment',async()=>{
 const t=await setup();await t.record();const r=await t.request('/materials/MAT-one/download','brokerA');assert.equal(r.status,200);assert.deepEqual(new Uint8Array(await r.arrayBuffer()),t.bytes);assert.equal(r.headers.get('Cache-Control'),'no-store, private');assert.equal(r.headers.get('X-Content-Type-Options'),'nosniff');assert.match(r.headers.get('Content-Disposition'),/^attachment/);assert(r.headers.get('Content-Security-Policy').includes('sandbox'));
 const log=t.db.db.prepare('SELECT * FROM mira_material_access').get();assert.equal(log.actor,'brokerA');assert.equal(log.sha256,t.body.sha256);assert.equal(t.db.db.prepare('SELECT COUNT(*) n FROM mira_leads').get().n,0);
 assert.throws(()=>t.sql('DELETE FROM mira_material_access'));assert.equal((await t.request('/materials/MAT-one/download','ownerB')).status,404);
});
test('closed or absent material binding never substitutes public files',async()=>{
 const t=await setup();await t.record();delete t.env.MIRA_MATERIALS;
 const list=await(await t.request('/projects/P/materials')).json();assert.deepEqual(list.records,[]);assert.equal(list.delivery_status,'not_configured_or_closed');assert.equal((await t.request('/materials/MAT-one/download')).status,503);
 const u=await setup();u.env.MATERIALS_ENABLED='false';await u.record();assert.equal((await u.request('/materials/MAT-one/download')).status,503);
});
test('revoked rights and revoked release immediately remove material visibility',async()=>{
 for(const id of ['EVID-rights','EVID-release']){const t=await setup();await t.record();t.sql('UPDATE mira_evidence SET revoked_at=? WHERE id=?',new Date().toISOString(),id);assert.deepEqual((await(await t.request('/projects/P/materials')).json()).records,[]);assert.equal((await t.request('/materials/MAT-one/download')).status,404);}
});
test('asset expiry cannot exceed evidence or use unbounded rights',async()=>{
 const t=await setup();assert.equal((await t.request('/admin/materials','op',{...t.body,expires_at:new Date(Date.now()+86400000*2).toISOString()})).status,409);
 t.ev('EVID-permanent','materials_rights',{project:'P',entity:'MAT-one',until:null});assert.equal((await t.request('/admin/materials','op',{...t.body,rights_ref:'EVID-permanent'})).status,409);
});
test('agency-specific rights do not cross agencies sharing project assignment',async()=>{
 const t=await setup();t.ev('EVID-rights-A','materials_rights',{project:'P',entity:'MAT-one',agency:'A'});t.ev('EVID-release-A','material_release',{project:'P',entity:'MAT-one',agency:'A',facts:t.facts});t.body.rights_ref='EVID-rights-A';t.body.release_ref='EVID-release-A';assert.equal((await t.record()).status,201);
 t.sql('INSERT INTO mira_agency_projects VALUES (?,?)','B','P');assert.equal((await t.request('/materials/MAT-one/download','ownerB')).status,404);assert.equal((await t.request('/materials/MAT-one/download','ownerA')).status,200);
});
test('wrong entity/scope/hash or active MIME cannot release a material',async()=>{
 const t=await setup();for(const delta of [{id:'MAT-other'},{project_id:'Q'},{sha256:'a'.repeat(64)},{size_bytes:t.bytes.length+1}])assert.equal((await t.request('/admin/materials','op',{...t.body,...delta})).status,409);
 for(const delta of [{mime_type:'image/svg+xml'},{mime_type:'text/html'},{size_bytes:MAX_MATERIAL_BYTES+1},{id:'MAT-../secrets'},{object_url:'https://example.test/private'},{title:'bad\r\nheader'}])assert.equal((await t.request('/admin/materials','op',{...t.body,...delta})).status,400);
});
test('changed stored bytes are not returned and object keys are never user URLs',async()=>{
 const t=await setup();await t.record();const bad=new Uint8Array(t.bytes);bad[10]^=1;t.objects.set(objectKey(t.body),bad);assert.equal((await t.request('/materials/MAT-one/download')).status,409);assert.equal(t.db.db.prepare('SELECT COUNT(*) n FROM mira_material_access').get().n,0);assert(t.keys.every(k=>k.startsWith('marketing/P/')&&!k.includes('://')));
});
test('MIME signature mismatch and oversized streamed data fail closed',async()=>{
 const t=await setup();const bad=new TextEncoder().encode('<html>synthetic</html>');t.body.size_bytes=bad.length;t.body.sha256=await hashBytes(bad);t.ev('EVID-html','material_release',{project:'P',entity:'MAT-one',facts:{...t.facts,sha256:t.body.sha256,size_bytes:bad.length}});t.body.release_ref='EVID-html';t.objects.set(objectKey(t.body),bad);assert.equal((await t.record()).status,409);
 const u=await setup();await u.record();u.env.MIRA_MATERIALS.get=async()=>({size:u.bytes.length,body:new ReadableStream({start(c){c.enqueue(new Uint8Array(u.bytes.length+1));c.close();}})});assert.equal((await u.request('/materials/MAT-one/download')).status,409);
});
test('membership/evidence changes during retrieval prevent byte release',async()=>{
 for(const type of ['member','rights','assignment','agreement']){const t=await setup();await t.record();const original=t.env.MIRA_MATERIALS.get;t.env.MIRA_MATERIALS.get=async key=>{const r=await original(key);if(type==='member')t.sql('UPDATE mira_memberships SET active=0 WHERE subject=?','ownerA');if(type==='rights')t.sql('UPDATE mira_evidence SET revoked_at=? WHERE id=?',new Date().toISOString(),'EVID-rights');if(type==='assignment')t.sql('DELETE FROM mira_agency_projects WHERE agency_id=?','A');if(type==='agreement')t.sql('UPDATE mira_evidence SET revoked_at=? WHERE id=?',new Date().toISOString(),'EVID-agreement-A');return r;};const r=await t.request('/materials/MAT-one/download');assert([403,404].includes(r.status));assert.equal(t.db.db.prepare('SELECT COUNT(*) n FROM mira_material_access').get().n,0);}
});
test('operator revocation is audited, irreversible and never silently reenabled',async()=>{
 const t=await setup();await t.record();assert.equal((await t.request('/admin/materials/MAT-one/revoke','ownerA',{reason:'SYNTHETIC hold'})).status,403);assert.equal((await t.request('/admin/materials/MAT-one/revoke','op',{reason:'SYNTHETIC hold'})).status,200);assert.equal((await t.record()).status,409);assert.equal((await t.request('/materials/MAT-one/download')).status,404);assert.throws(()=>t.sql('UPDATE mira_materials SET revoked_at=NULL WHERE id=?','MAT-one'));assert.equal(t.db.db.prepare("SELECT COUNT(*) n FROM mira_events WHERE entity_type='material'").get().n,2);
});
test('empty filtered material page still exposes continuation cursor',async()=>{
 const t=await setup();await t.record();t.sql('UPDATE mira_evidence SET revoked_at=? WHERE id=?',new Date().toISOString(),'EVID-release');t.body.id='MAT-two';t.ev('EVID-rights-two','materials_rights',{project:'P',entity:'MAT-two'});t.ev('EVID-release-two','material_release',{project:'P',entity:'MAT-two',facts:t.facts});t.body.rights_ref='EVID-rights-two';t.body.release_ref='EVID-release-two';await t.record();const r=await(await t.request('/projects/P/materials?limit=1')).json();assert.equal(r.records.length,0);assert.equal(r.next_cursor,'MAT-one');const n=await(await t.request('/projects/P/materials?limit=1&cursor='+r.next_cursor)).json();assert.equal(n.records[0].id,'MAT-two');
});
test('Range requests and unverified identities cannot get files',async()=>{
 const t=await setup();await t.record();assert.equal((await t.request('/materials/MAT-one/download','ownerA',undefined,{Range:'bytes=0-10'})).status,416);assert.equal((await t.request('/materials/MAT-one/download','unknown')).status,403);
 const handler=createHandler(async()=>{throw new Error('synthetic verifier failure');});const response=await handler(new Request(t.env.APP_ORIGIN+'/mira/api/materials/MAT-one/download'),t.env);assert.equal(response.status,500);assert(!JSON.stringify(await response.json()).includes('SYNTHETIC'));
});
