/** Loopback-only synthetic integration. Real routes/SQLite/JWT; fake Siteverify.
 * HTTP loopback is mapped to a fixed internal HTTPS origin for the test only. */
import http from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import site from '../cloudflare-worker/mira/site-worker.mjs';
const db=new DatabaseSync(':memory:');
const migrations=new URL('../cloudflare-worker/mira/migrations/',import.meta.url);
for(const f of readdirSync(migrations).filter(f=>f.endsWith('.sql')).sort())db.exec(readFileSync(new URL(f,migrations),'utf8'));
db.exec("INSERT INTO mira_memberships VALUES ('TEST-OPERATOR',NULL,'operator',1),('TEST-SECOND',NULL,'operator',1)");
const MIRA_DB={prepare(sql){return{bind(...args){const s=db.prepare(sql);return{first:async()=>s.get(...args)||null,all:async()=>({results:s.all(...args)}),run:async()=>({meta:{changes:Number(s.run(...args).changes)}})};}};},async batch(statements){const execute=async()=>{db.exec('BEGIN');try{const rows=[];for(const s of statements)rows.push(await s.run());db.exec('COMMIT');return rows;}catch(e){db.exec('ROLLBACK');throw e;}};const p=(this.queue||Promise.resolve()).then(execute);this.queue=p.catch(()=>{});return p;}};
const origin='https://pilot.example.test',issuer='https://expo22-fixture.cloudflareaccess.com';
const keys=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
const jwk={...await crypto.subtle.exportKey('jwk',keys.publicKey),kid:'EXPO22-TEST',alg:'RS256',use:'sig'};
globalThis.fetch=async(url,opts)=>{if(url===issuer+'/cdn-cgi/access/certs'&&opts.redirect==='manual')return Response.json({keys:[jwk]});if(url==='https://challenges.cloudflare.com/turnstile/v0/siteverify'&&opts.redirect==='manual'){const b=JSON.parse(opts.body);return Response.json({success:b.response==='SYNTHETIC-NOT-LIVE',hostname:'pilot.example.test',action:'mira_intake'});}throw Error('Unexpected fixture egress');};
const b64=v=>Buffer.from(JSON.stringify(v)).toString('base64url');
async function token(subject){const n=Math.floor(Date.now()/1000),p=b64({alg:'RS256',kid:jwk.kid})+'.'+b64({iss:issuer,aud:['TEST-AUD'],sub:subject,email:subject.toLowerCase()+'@example.test',type:'app',iat:n,exp:n+3600});return p+'.'+Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',keys.privateKey,new TextEncoder().encode(p))).toString('base64url');}
const env={APP_ORIGIN:origin,MIRA_DB,ACCESS_TEAM_DOMAIN:issuer,ACCESS_AUDIENCE:'TEST-AUD',PUBLIC_INTAKE_ENABLED:'true',PUBLIC_INTAKE_PRIVACY_APPROVED:'true',PUBLIC_INTAKE_PRIVACY_VERSION:'SYNTHETIC-v1',PUBLIC_INTAKE_PRIVACY_NOTICE_URL:origin+'/mira/agency-privacy.html',INTAKE_OPERATOR_SUBJECT:'TEST-OPERATOR',INTAKE_RATE_SECRET:'SYNTHETIC-ONLY-NOT-PRODUCTION-0123456789',TURNSTILE_SITE_KEY:'synthetic',TURNSTILE_SECRET_KEY:'SYNTHETIC',APPLICATIONS_ENABLED:'false'};
const server=http.createServer(async(req,res)=>{try{
 const local='http://127.0.0.1:'+server.address().port;const headers=new Headers(req.headers);
 if(headers.get('Origin')===local)headers.set('Origin',origin);
 headers.set('CF-Connecting-IP','192.0.2.1');headers.delete('Cf-Access-Jwt-Assertion');
 const role=headers.get('x-mira-fixture-role');if(['TEST-OPERATOR','TEST-SECOND','TEST-APPLICANT'].includes(role))headers.set('Cf-Access-Jwt-Assertion',await token(role));
 let body='';for await(const c of req)body+=c;
 const r=await site.fetch(new Request(new URL(req.url,origin),{method:req.method,headers,...(body?{body}:{})}),env);
 res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));
}catch(e){console.error(e.message);res.writeHead(500);res.end('Fixture failure');}});
server.listen(0,'127.0.0.1',()=>console.log('FIXTURE_ORIGIN=http://127.0.0.1:'+server.address().port));
for(const sig of ['SIGTERM','SIGINT'])process.on(sig,()=>{server.close();db.close();process.exit();});
