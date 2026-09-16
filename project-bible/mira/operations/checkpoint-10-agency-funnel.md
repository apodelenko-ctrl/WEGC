# Checkpoint 10 — dedicated agency acquisition landing

2026-09-16. Owner request: publish a separate agency funnel rather than reuse the generic MIRA landing URL.

## Delivered source

`/mira/agency/`: editorial responsive landing with accepted client/brand positioning, distinct entry routes for four agency models, Phuket-first explanation, links to actual demo views, onboarding sequence, FAQ and local three-question qualification.

A valid combination yields a preparation plan, appropriate demo entry and user-triggered text brief. No personal-data fields, server storage, analytics, API requests, email links or public submit endpoint. Changes invalidate the previous plan. Without JavaScript, controls stay disabled and static links remain usable. Four allowlisted `segment` values support different campaign entries without creating tracking or sending a request.

Main landing / demo / webinar entry links, acquisition kit, bible index/decisions and the existing public_landing dashboard capability are integrated through hash-checked literal edits. Earlier protected APIs, private materials, research registers and unknown operating metrics are unchanged. No private contract or contact information is published.

## Checks before publication

66 Node tests and 66 Python tests passed locally. Nine Node cases cover the new flow, including all64 choice combinations. Ten offline browser cases passed; six widths320/360/390/768/1024/1440 show no horizontal overflow. A duplicate anchor ID found during testing was fixed and protected by a regression test.

Offline screenshots are layout evidence, not a production/E2E assertion. A separate read-only GitHub Actions workflow runs after Pages, checks actual modules/CSP and demo navigation on localhost, then requests the published HTML/CSS/modules and matches SHA256 to the checkout. Its artifact records actual outcomes. Inspect that result before claiming the public URL is verified.

## Remaining boundaries

The page is acquisition preparation, not a working intake system. Access/D1/R2 deployment, approved privacy/controller data, a current project registration path and separate outreach approval remain open. No external outreach, client registration or payment execution was performed.

Implementation and campaign routes: `../product/agency-funnel.md`. The final publication result is recorded below after verification; absence of it must not be interpreted as success.
