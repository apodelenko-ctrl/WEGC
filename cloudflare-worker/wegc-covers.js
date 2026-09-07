/* Cloud cover + gallery proxy: official developer images only, cached at the edge.
   Nothing is stored on the laptop or in git. */
import map from './covers-map.json';
import galleries from './galleries-map.json';

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
  's3.ap-southeast-1.amazonaws.com',
  'origin.co.th',
  'www.origin.co.th'
]);

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': '*' }
  });
}

function galleryOf(slug) {
  const g = galleries[slug];
  if (!g) return null;
  if (Array.isArray(g)) return { page: '', images: g };
  return { page: g.page || '', images: g.images || [] };
}

async function proxy(src) {
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

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\//, '').replace(/\/$/, '');
    if (!path || path === 'health') {
      const gkeys = Object.keys(galleries);
      const shots = gkeys.reduce((n, k) => {
        const g = galleryOf(k);
        return n + (g ? g.images.length : 0);
      }, 0);
      return json({ ok: true, covers: Object.keys(map).length, galleries: gkeys.length, shots });
    }
    const parts = path.split('/');
    const slug = decodeURIComponent(parts[0] || '').replace(/\.(jpe?g|webp|png)$/i, '');
    const rest = parts[1] || '';

    if (rest === 'meta') {
      const g = galleryOf(slug);
      return json({
        slug,
        cover: !!map[slug],
        page: g ? g.page : '',
        n: g ? g.images.length : 0
      });
    }

    if (rest && /^\d+$/.test(rest)) {
      const g = galleryOf(slug);
      if (!g || !g.images[Number(rest)]) return new Response('not found', { status: 404 });
      return proxy(g.images[Number(rest)]);
    }

    const src = map[slug] || (galleryOf(slug) && galleryOf(slug).images[0]);
    if (!src) return new Response('not found', { status: 404 });
    return proxy(src);
  }
};
