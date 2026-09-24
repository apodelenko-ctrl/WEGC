/** Loopback-only fixture. Public source DB + ephemeral signed synthetic roles.
 * No production identity, private export or remote DB is used. Never deploy. */
import http from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {mkdtempSync,copyFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import site from '../cloudflare-worker/mira/site-worker.mjs';
const source=process.env.MIRA_PUBLIC_SOURCE_DB;
if(!source)throw Error('MIRA_PUBLIC_SOURCE_DB must be a public-source-only fixture');
const dir=mkdtempSync(join(tmpdir(),'mira-cf006-browser-'));
copyFileSync(source,join(dir,'test.sqlite'));
const db=new DatabaseSync(join(dir,'test.sqlite'));
if(db.prepare('SELECT count(*) AS n FROM mira_memberships').get().n!==0)throw Error('Fixture source must contain no operational memberships');
db.exec("INSERT INTO mira_agencies(id,name,city,status,created_at) VALUES ('CF006-TEST','SYNTHETIC Agency','TEST','pending','2026-09-22T00:00:00Z'); INSERT INTO mira_memberships VALUES ('TEST-OPERATOR',NULL,'operator',1),('TEST-MEMBER','CF006-TEST','agency_owner',1)");
const snapshot=db.prepare('SELECT snapshot_id FROM mira_research_summary WHERE contains_private=0').get().snapshot_id;
const MIRA_DB={prepare(sql){if(!/^SELECT\b/i.test(sql))throw Error('Read-only fixture');return{bind(...args){const s=db.prepare(sql);return{first:async()=>s.get(...args)||null,all:async()=>({results:s.all(...args)})};}};}};
const keys=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
const issuer='https://cf006-fixture.cloudflareaccess.com';
const jwk={...await crypto.subtle.exportKey('jwk',keys.publicKey),kid:'CF006-TEST',alg:'RS256',use:'sig'};
globalThis.fetch=async(url,options)=>{if(url!==issuer+'/cdn-cgi/access/certs'||options.redirect!=='manual')throw Error('Unexpected fixture egress');return Response.json({keys:[jwk]});};
const b64=v=>Buffer.from(JSON.stringify(v)).toString('base64url');
async function token(subject){const n=Math.floor(Date.now()/1000),p=b64({alg:'RS256',kid:jwk.kid})+'.'+b64({iss:issuer,aud:['TEST-AUD'],sub:subject,email:subject.toLowerCase()+'@example.test',type:'app',iat:n,exp:n+3600});return p+'.'+Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',keys.privateKey,new TextEncoder().encode(p))).toString('base64url');}
const server=http.createServer(async(req,res)=>{try{
 const origin='http://127.0.0.1:'+server.address().port,headers=new Headers();
 const role=req.headers['x-mira-fixture-role'];
 if(['TEST-OPERATOR','TEST-MEMBER'].includes(role))headers.set('Cf-Access-Jwt-Assertion',await token(role));
 const r=await site.fetch(new Request(new URL(req.url,origin),{method:req.method,headers}),{MIRA_DB,APP_ORIGIN:origin,ACCESS_TEAM_DOMAIN:issuer,ACCESS_AUDIENCE:'TEST-AUD',MIRA_RESEARCH_SNAPSHOT:snapshot});
 res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));
}catch{res.writeHead(500);res.end('Fixture error');}});
server.listen(0,'127.0.0.1',()=>console.log('FIXTURE_ORIGIN=http://127.0.0.1:'+server.address().port));
for(const sig of ['SIGINT','SIGTERM'])process.on(sig,()=>{server.close();db.close();rmSync(dir,{recursive:true,force:true});process.exit();});
