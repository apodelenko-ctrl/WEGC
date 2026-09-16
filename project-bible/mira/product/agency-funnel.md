# МИРА — отдельная воронка привлечения агентств

Checkpoint 10, 2026-09-16. Created at the owner's explicit request for an actual separate landing URL, not another list of documents. Canonical entry: `https://wegc.fund/mira/agency/`. The general `/mira/` landing and `/mira/marketplace.html` demo are retained.

## Source basis and copy boundaries

The page implements, rather than replaces, `landing-v3-copy.md`, `../01-product-positioning.md`, `../03-go-to-market.md`, `../sales/AGENCY-SALES-PLAYBOOK.md` and `../sales/AGENCY-ACTIVATION-KIT.md`. Marketplace behavior follows the checked-in code. The most recent WORK/RESUME deployment gates override aspirational marketing language in earlier copy.

Flow: offer → client/brand ownership and responsibilities → current agency model → Phuket → actual demo screens → onboarding path → three-question local brief → separately authorized pilot.

Public copy deliberately contains no current inventory, prices, yield, commission percentages, network size, testimonial, meeting date, permission to share developer assets or confidential contract information. The accepted commitment to preserving agency communication is not described as perpetual developer lead protection. Payment support remains separate from the commission.

## Four campaign entry routes

- `/mira/agency/?segment=new_direction`: the agency itself reports no overseas desk.
- `/mira/agency/?segment=overseas_desk`: augment an existing overseas operation.
- `/mira/agency/?segment=thailand_desk`: address a specific process gap, not teach Thailand from scratch.
- `/mira/agency/?segment=network`: establish the legal/operational boundary of one team's pilot.

Only the allowlisted segment value is read. Unknown segments, other URL fields and tracking parameters are ignored and never echoed or forwarded. Specialty such as premium/new-build/resort is not used to assume absence of an overseas desk.

## What the qualification actually does

Three fixed-choice questions: present model, immediate goal, responsible role. Every valid combination gives a local plan and a real demo link. If no person is responsible yet, assigning one becomes the first action. There is no numerical lead score, automatic rejection or onboarding approval.

No text fields, contact data, cookies, localStorage, sessionStorage, analytics, API calls or submit endpoint. Browser memory only; modifying any answer invalidates the previous result. A user-triggered `.txt` export includes the selected enum labels and preparation steps, never buyer data. The download is not an application receipt.

The form is initially disabled and activated only once no-submit handlers are installed. CSP blocks connections and form actions. Static product links remain available without JavaScript. Existing Access/D1 intake is NOT opened or changed. The closed-pilot link is explicitly marked as requiring operator-approved access.

## Integration

General landing primary CTA and brief CTA point to this page. The marketplace header and webinar preparation CTA also enter the new flow; existing demo views and local application preview remain unchanged. The canonical dashboard's existing public_landing capability now points to this entry, without adding invented business metrics or another dashboard.

## Measurement / next operational step

The following are future measurement events, not captured events: landing visit → scenario selected → local brief prepared → demo opened → working application received → operator qualification → onboarding → actual registered client. Currently no telemetry exists on this landing. Do not count tests, downloads or browser answers as acquired/activated agencies.

Before real intake opens: complete the protected service deployment and privacy/controller review, permit a real project under current evidence, approve outreach independently, and test the actual receipt path. Then separately connect consent-reviewed attribution; do not insert a public inbox, spreadsheet or third-party form as a silent workaround.

## QA and publication

- `node --test tests/mira-agency.test.mjs`: all choice combinations, segment copy, input rejection, local-only exports, CSP, anchors and integration links.
- `python tests/mira-agency-browser.py`: offline DOM/mobile checks; explicitly not deployed E2E.
- `python tests/mira-agency-release.py`: checked-in HTML/CSS/modules served on localhost with their actual CSP, followed by public GET/hash verification after Pages. Never sends a form or client data to an external service.
- `.github/workflows/mira-agency-release.yml`: runs after successful main-branch Pages deployment; saves browser screenshots and byte-level public verification as an Actions artifact. A failed check must not be described as a successful live release.

Exact checkpoint and outcomes: `../operations/checkpoint-10-agency-funnel.md`. No Cloudflare/real client E2E claim follows from this static page release.
