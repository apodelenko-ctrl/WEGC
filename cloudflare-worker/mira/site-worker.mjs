/** Dedicated MIRA hostname. The public website is never proxied through this Worker. */
import api from './worker.mjs';
import {ApiError, verifyAccess} from './auth.mjs';

const pages = new Set(['/mira/pilot.html', '/mira/library.html']);
const files = new Set(['/mira/pilot.mjs', '/mira/library.mjs', '/mira/marketplace.css', '/mira/library.css', '/mira/documents/documents.css']);
// Available before sign-in; same-origin notice does not imply legal approval.
const notices = new Set(['/mira/documents/privacy.html']);
const publicPages = new Set(['/mira/marketplace.html', '/mira/phuket-starter-kit.html']);
const headers = {
  'Cache-Control': 'no-store, private',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
};
const failure = (status, error) => Response.json({error}, {status, headers});
const redirect = target => new Response(null, {status: 302, headers: {...headers, Location: target}});

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!env.APP_ORIGIN || url.origin !== env.APP_ORIGIN) return failure(421, 'unexpected_origin');
    if (url.pathname.startsWith('/mira/api/')) return api.fetch(request, env);
    if (!['GET', 'HEAD'].includes(request.method)) return failure(405, 'method_not_allowed');
    if (url.pathname === '/') return redirect('/mira/pilot.html');
    if (url.pathname === '/mira/' || publicPages.has(url.pathname)) {
      return redirect('https://wegc.fund' + url.pathname);
    }
    if (!pages.has(url.pathname) && !files.has(url.pathname) && !notices.has(url.pathname)) return failure(404, 'not_found');
    try {
      // Do not trust the existence of a dashboard policy or an unsigned identity header.
      if (pages.has(url.pathname)) await verifyAccess(request, env);
      if (!env.MIRA_ASSETS) return failure(503, 'assets_not_configured');
      const response = await env.MIRA_ASSETS.fetch(request);
      const secured = new Headers(response.headers);
      for (const [key, value] of Object.entries(headers)) secured.set(key, value);
      return new Response(response.body, {status: response.status, headers: secured});
    } catch (error) {
      return failure(error instanceof ApiError ? error.status : 500,
        error instanceof ApiError ? error.code : 'internal_error');
    }
  },
};
