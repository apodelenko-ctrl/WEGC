/** Use ONLY a public research test export, never private native backup. No network. */
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,copyFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import assert from 'node:assert/strict';
import {createResearchView} from './research-view.mjs';
const source=process.argv[2];if(!source)throw Error('Provide a local public research SQLite test export');
const dir=mkdtempSync(join(tmpdir(),'mira-research-view-'));let db;
try{
 const path=join(dir,'test.sqlite');copyFileSync(source,path);db=new DatabaseSync(path);
 db.exec("INSERT INTO mira_memberships(subject,agency_id,role,active) VALUES ('CF006-SYNTHETIC',NULL,'operator',1)");
 const snap=db.prepare('SELECT * FROM mira_research_summary WHERE contains_private=0').all();assert.equal(snap.length,1);
 const env={APP_ORIGIN:'https://example.test',MIRA_RESEARCH_SNAPSHOT:snap[0].snapshot_id,MIRA_DB:{prepare(sql){assert.match(sql,/^SELECT/i);return{bind(...args){const p=db.prepare(sql);return{first:async()=>p.get(...args)||null,all:async()=>({results:p.all(...args)})};}};}}};
 const handler=createResearchView(async()=>({subject:'CF006-SYNTHETIC'}));
 const get=async(path)=>{const r=await handler(new Request(env.APP_ORIGIN+'/mira/api/admin/research'+path),env);assert.equal(r.status,200);return r.json();};
 const summary=(await get('')).snapshot;assert.equal(summary.agency_candidates,405);assert.equal(summary.developer_groups,43);assert.equal(summary.research_project_links,618);
 let fields=0;const counts={};
 for(const kind of ['agency','developer']){let cursor='',count=0;do{const page=await get('/entities?'+new URLSearchParams({kind,cursor,limit:100}));count+=page.records.length;for(const row of page.records){const detail=await get('/entity?'+new URLSearchParams({kind,id:row.source_id}));fields+=detail.fields.length;assert.ok(detail.fields.every(f=>Object.hasOwn(f,'value')&&Object.hasOwn(f,'verification_status')));}cursor=page.next_cursor;}while(cursor);counts[kind]=count;}
 assert.equal(fields,7742);console.log(JSON.stringify({scope:'local public source export, not CF005 remote export',counts,fields,project_links:summary.research_project_links,source_commit:summary.source_commit,read_only_queries:true,private_lineage_exposed:false}));
}finally{db?.close();rmSync(dir,{recursive:true,force:true});}
