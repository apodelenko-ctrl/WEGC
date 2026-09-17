/** Access JWT verification. Trust only pinned issuer + audience + RSA signature.
 * Official contract: developers.cloudflare.com/cloudflare-one/access-controls/
 * applications/http-apps/authorization-cookie/validating-json/
 * No token, email-header or client-supplied agency-id bypass exists.
 */
export class ApiError extends Error {
  constructor(status, code) { super(code); this.status=status; this.code=code; }
}
const certificates = new Map();
function decoded(segment) {
  if (!/^[A-Za-z0-9_-]+$/.test(segment)) throw new ApiError(401,'invalid_identity');
  const s=segment.replace(/-/g,'+').replace(/_/g,'/');
  return Uint8Array.from(atob(s+'='.repeat((4-s.length%4)%4)),c=>c.charCodeAt(0));
}
export async function verifyAccess(request,env,fetcher=fetch,now=Date.now()) {
  const issuer=env.ACCESS_TEAM_DOMAIN;
  if (!/^https:\/\/[a-z0-9-]+\.cloudflareaccess\.com$/.test(issuer||'') || !env.ACCESS_AUDIENCE)
    throw new ApiError(503,'identity_not_configured');
  const token=request.headers.get('Cf-Access-Jwt-Assertion');
  if (!token || token.length>16384) throw new ApiError(401,'identity_required');
  let stage='decode';
  try {
    const parts=token.split('.');
    if (parts.length!==3) throw new Error('invalid');
    const head=JSON.parse(new TextDecoder().decode(decoded(parts[0])));
    const body=JSON.parse(new TextDecoder().decode(decoded(parts[1])));
    const seconds=Math.floor(now/1000);
    stage='header';
    if (head.alg!=='RS256' || typeof head.kid!=='string' || head.kid.length>200 || head.crit || head.jku || head.jwk || head.x5u) throw new Error('invalid');
    stage='issuer';
    if(body.iss!==issuer)throw new Error('invalid');
    stage='audience';
    if(!Array.isArray(body.aud)||!body.aud.includes(env.ACCESS_AUDIENCE))throw new Error('invalid');
    stage='time';
    if (!Number.isFinite(body.exp) || body.exp<=seconds || !Number.isFinite(body.iat) || body.iat>seconds+30 || (body.nbf!==undefined && (!Number.isFinite(body.nbf)||body.nbf>seconds+30))) throw new Error('invalid');
    stage='identity_claims';
    if (typeof body.sub!=='string' || !body.sub || body.sub.length>200 || typeof body.email!=='string' || body.email.length>254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email) || body.type!=='app') throw new Error('invalid');
    let cache=certificates.get(issuer);
    if (!cache || cache.expires<=now) {
      stage='certificate_fetch';
      // Workers supports manual/follow, not redirect:'error'. Reject redirects
      // through response.ok so key discovery stays on the pinned issuer.
      const response=await fetcher(issuer+'/cdn-cgi/access/certs',{redirect:'manual',signal:AbortSignal.timeout(5000)});
      if (!response.ok) throw new ApiError(503,'identity_provider_unavailable');
      stage='certificate_decode';
      const text=await response.text();
      if(text.length>65536) throw new Error('invalid');
      const data=JSON.parse(text);
      if(!Array.isArray(data.keys)) throw new Error('invalid');
      cache={keys:data.keys,expires:now+300000};certificates.set(issuer,cache);
    }
    stage='certificate_key';
    const jwk=cache.keys.find(k=>k.kid===head.kid && k.kty==='RSA' && (!k.alg||k.alg==='RS256') && (!k.use||k.use==='sig'));
    if(!jwk) {certificates.delete(issuer);throw new Error('invalid');}
    stage='key_import';
    const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
    stage='signature';
    const valid=await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,decoded(parts[2]),new TextEncoder().encode(parts[0]+'.'+parts[1]));
    if(!valid)throw new Error('invalid');
    return {subject:body.sub,email:body.email.toLowerCase()};
  } catch(error) {
    // Only a fixed stage label is logged. Never log JWTs, claims, cookies or exception text.
    console.warn(JSON.stringify({event:'mira_identity_rejected',stage}));
    if(error instanceof ApiError)throw error;
    throw new ApiError(401,'invalid_identity');
  }
}
