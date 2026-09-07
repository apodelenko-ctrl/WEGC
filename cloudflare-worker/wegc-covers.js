/* Cloud cover proxy: official developer images only, cached at the edge.
   Nothing is stored on the laptop or in git. */
import map from './covers-map.json';

const ALLOW = new Set([
  'thetitleresidence.com',
  'www.thetitleresidence.com',
  'botanicaluxuryvilla.com',
  'www.botanicaluxuryvilla.com',
  'banyangroupresidences.com',
  'www.banyangroupresidences.com',
  'hibiscus.lagunaproperty.com',
  'www.lagunaproperty.com',
  'lagunaproperty.com',
  'sansiri.com',
  'www.sansiri.com',
  'assets.sansiri.com',
  'o77site.s3.ap-southeast-1.amazonaws.com',
  'origin.co.th',
  'www.origin.co.th'
]);

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response(JSON.stringify({ ok: true, covers: Object.keys(map).length }), {
        headers: { 'content-type': 'application/json', 'cache-control': 'no-store' }
      });
    }
    const slug = url.pathname.replace(/^\//, '').replace(/\.(jpe?g|webp|png)$/i, '');
    const src = map[slug];
    if (!src) return new Response('not found', { status: 404 });
    let dest;
    try { dest = new URL(src); } catch (e) { return new Response('bad source', { status: 500 }); }
    if (!ALLOW.has(dest.hostname)) return new Response('host not allowed', { status: 403 });

    const upstream = await fetch(src, {
      cf: { cacheTtl: 2592000, cacheEverything: true, cacheTtlByStatus: { '200-299': 2592000, '404-599': 60 } },
      headers: {
        'accept': 'image/avif,image/webp,image/*,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (compatible; WEGC-covers/1.0; +https://wegc.fund/)',
        'referer': dest.origin + '/'
      }
    });
    if (!upstream.ok) return new Response('upstream ' + upstream.status, { status: 502 });
    const headers = new Headers();
    headers.set('content-type', upstream.headers.get('content-type') || 'image/jpeg');
    headers.set('cache-control', 'public, max-age=2592000, immutable');
    headers.set('access-control-allow-origin', '*');
    return new Response(upstream.body, { status: 200, headers });
  }
};
