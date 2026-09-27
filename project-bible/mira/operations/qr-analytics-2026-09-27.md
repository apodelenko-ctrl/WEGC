# QR landing analytics

The owner requested measurement for already printed exhibition leaflets.
Stored artwork contains https://wegc.fund/mira/start/ and
https://wegc.fund/mira/go/ without campaign parameters. The final physical
leaflet has not been decoded in this task. Do not label all visits as scans.

Cloudflare Web Analytics existed for wegc.fund but the apex A records are
DNS-only, so automatic injection did not appear on MIRA. Existing CSP also
did not permit the beacon. The deploy build now installs the existing public
site collector on MIRA landing and catalogue pages with precise CSP allowances.
No DNS/proxy change, new analytics account, cookies, contact-field capture,
operator-page tracking or API credentials in the website.

Use Web Analytics for wegc.fund; filter paths /mira/start/ and /mira/go/,
then compare /mira/catalog/ views by day/hour. Visits and pageviews are not
unique people. Own checks count too: append ?mira_analytics=off to suppress
the manual collector during owner QA. Ad blockers can cause undercounting.
Cloudflare's existing automatic setting excludes EU traffic; the new manual
public-page snippet follows Cloudflare's manual installation behavior.

The baseline query on 2026-09-27 before deployment returned only two pageviews
for / and no MIRA rows. Missing historical telemetry is not proof of no visits.
No custom click or successful-application conversion tracking is claimed.
The collector has no UTM support. A future print run should use a dedicated
landing path that is not reused for ordinary messages, then preserve it.

Source: https://developers.cloudflare.com/web-analytics/faq/
