/** Loopback-only browser fixture. Synthetic identities/data, real Worker routes,
 * signed RSA JWT verification and SQLite migrations. Never deploy this file. */
import http from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import worker from '../cloudflare-worker/mira/worker.mjs';
import site from '../cloudflare-worker/mira/site-worker.mjs';
const root=new URL('../',import.meta.url),db=new DatabaseSync(':memory:');
for(const f of readdirSync(new URL('cloudflare-worker/mira/migrations/',root)).filter(f=>f.endsWith('.sql')).sort())db.exec(readFileSync(new URL('cloudflare-worker/mira/migrations/'+f,root),'utf8'));
db.exec("INSERT INTO mira_memberships VALUES ('TEST-OPERATOR',NULL,'operator',1)");
const database={
 prepare(sql){return {bind(...args){return {
  async first(){return db.prepare(sql).get(...args)||null;},
  async all(){return {results:db.prepare(sql).all(...args)};},
  async run(){return {meta:{changes:Number(db.prepare(sql).run(...args).changes)}};}
 };}};},
 async batch(statements){db.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());db.exec('COMMIT');return r;}catch(e){db.exec('ROLLBACK');throw e;}}
};
const keys=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
const issuer='https://mira-browser-test.cloudflareaccess.com';
const jwk={...await crypto.subtle.exportKey('jwk',keys.publicKey),kid:'TEST-KEY',alg:'RS256',use:'sig'};
globalThis.fetch=async(url,options)=>{if(url!==issuer+'/cdn-cgi/access/certs'||options.redirect!=='manual')throw Error('Unexpected fixture egress');return Response.json({keys:[jwk]});};
const b64=v=>Buffer.from(JSON.stringify(v)).toString('base64url');
async function token(subject,expired=false){const n=Math.floor(Date.now()/1000),p=b64({alg:'RS256',kid:'TEST-KEY'})+'.'+b64({iss:issuer,aud:['TEST-AUD'],sub:subject,email:subject.toLowerCase()+'@example.test',type:'app',iat:n,exp:expired?n-60:n+600});return p+'.'+Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',keys.privateKey,new TextEncoder().encode(p))).toString('base64url');}
const server=http.createServer(async(req,res)=>{try{
 const origin='http://127.0.0.1:'+server.address().port,url=new URL(req.url,origin);
 const subject=req.headers['x-mira-fixture-user'];if(!['TEST-OPERATOR','TEST-APPLICANT','TEST-OTHER'].includes(subject)){res.writeHead(401);res.end('Synthetic fixture identity required');return;}
 if(url.pathname.startsWith('/mira/api/')){
  let body='';for await(const chunk of req)body+=chunk;
  const env={MIRA_DB:database,APP_ORIGIN:origin,ACCESS_TEAM_DOMAIN:issuer,ACCESS_AUDIENCE:'TEST-AUD',APPLICATIONS_ENABLED:'true',PRIVACY_VERSION:'TEST-ONLY',PRIVACY_NOTICE_URL:origin+'/test-privacy',MATERIALS_ENABLED:'false'};
  const r=await worker.fetch(new Request(url,{method:req.method,headers:{...req.headers,'Cf-Access-Jwt-Assertion':await token(subject,req.headers['x-mira-fixture-expired']==='true')},...(body?{body}:{})}),env);
  res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));return;
 }
 const assets={'/mira/pilot.html':['mira/pilot.html','text/html'],'/mira/pilot.mjs':['mira/pilot.mjs','text/javascript'],'/mira/marketplace.css':['mira/marketplace.css','text/css']};
 if(url.pathname==='/test-privacy'){res.end('SYNTHETIC TEST NOTICE. Not a legal approval.');return;}
 const asset=assets[url.pathname];if(!asset){res.writeHead(404);res.end();return;}const r=await site.fetch(new Request(url,{headers:{'Cf-Access-Jwt-Assertion':await token(subject)}}),{APP_ORIGIN:origin,ACCESS_TEAM_DOMAIN:issuer,ACCESS_AUDIENCE:'TEST-AUD',MIRA_ASSETS:{fetch:async()=>new Response(readFileSync(new URL(asset[0],root)),{headers:{'Content-Type':asset[1]}})}});res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));
}catch(e){console.error(e);res.writeHead(500);res.end('Fixture error');}});
server.listen(0,'127.0.0.1',()=>console.log('FIXTURE_ORIGIN=http://127.0.0.1:'+server.address().port));
