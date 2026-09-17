# Dedicated pilot hostname

The public `wegc.fund` apex resolves directly to GitHub Pages (DNS only).
Access policies on its URL paths do not intercept those requests. Do not enable
proxying for the entire apex just to launch MIRA: it also serves other projects.

The alternative entrypoint `site-worker.mjs` serves the existing pilot UI and API
at the same **dedicated, previously unused** hostname, `pilot.wegc.fund`. Use
`wrangler.site.example.toml` as the template for the local ignored `wrangler.toml`.
The original API-only entrypoint/configuration remain supported.

Before deployment:

1. Verify the new hostname is unused in the owner's zone. Do not overwrite an
   existing record. A Workers Custom Domain creates its own DNS record.
2. Configure one Access application with email allowlist and One-time PIN on
   `pilot.wegc.fund/mira/pilot.html`, `pilot.wegc.fund/mira/library.html`, and
   `pilot.wegc.fund/mira/api/*`. Obtain the actual issuer and application AUD tag;
   a Policy ID is not an AUD tag.
3. Set verified account/DB IDs, Access issuer/audience and
   `APP_ORIGIN=https://pilot.wegc.fund`. Keep intake/material delivery disabled.
4. Run `python3 scripts/mira-build-pilot-assets.py` from the repository root.
   Only six reviewed UI files are packaged in the ignored `pilot-assets/`.
   Never upload the repository root as static assets.
5. Run the existing preflight with `--topology dedicated-site` and the explicitly
   verified origin/account/database. The default remains the stricter API-only
   topology; it does not silently accept custom domains or asset bindings.
6. Run tests and Wrangler dry-run before deploying. Keep `run_worker_first=true`,
   HTML normalization/SPA fallback disabled and workers.dev/previews disabled.

The wrapper verifies signed Access JWTs before serving the HTML, even if the
dashboard policy is missing. It serves only allowlisted UI assets, delegates API
requests to the original Worker, rejects other origins and routes, and uses
private/no-store response headers. UI assets contain no private records. Fixed
public links redirect to the existing apex; the wrapper is not a general proxy.
The package adds the standard Access logout link to the two HTML pages.

After deployment verify the actual anonymous redirects on all three protected
paths, real OTP delivery/login/logout and remote D1 session behavior. The
synthetic RSA tests and successful asset build are not that acceptance.

The owner reports Cloudflare access issues from Russia without VPN. The dedicated
hostname isolates the change from the public website; it does **not** resolve or
prove Russian network availability. Test from the intended Russian network
before declaring the agency launch ready.

References:
- https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- https://developers.cloudflare.com/workers/static-assets/binding/
- https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
