# C13 — Exhibition conversion route review: QR → Phuket → next step

**Checked:** 2026-09-18, Asia/Bangkok.  
**Scope:** source/content review only. No design, code, deploy, DNS, form, invite or external message changed.

## Observed route in current main

The existing exhibition QR is deterministic and inspectable: `mira/expo/qr.svg` encodes **https://wegc.fund/mira/start/**. The exhibition page also links to `/mira/start/` as the QR check destination.

Current source path:

`physical QR → /mira/start/ → /mira/phuket/ → /mira/access/`

The first two surfaces are coherent for discovery:

- `/mira/start/` is explicitly Phuket-first and says the catalogue is open without registration.
- `/mira/phuket/` exposes 618 source/research records and correctly warns that they are not confirmed availability.
- both surfaces distinguish research records from current inventory and require project-specific confirmation before a real offer.

## Material conversion defect: the last step is stale relative to the accepted controlled intake

The public source currently sends the user to `/mira/access/`, whose page says **working registration is closed**. `/mira/start/` repeats the same closed-intake statement, and its local qualification form is rendered disabled. The catalogue's main conversion button also routes to `/mira/access/`.

However, the newer operational source `project-bible/mira/operations/AGENCY-INTAKE-OPERATIONS.md` records that the owner approved **controlled agency intake for invited agency representatives** on 2026-09-18 and documents the live notice plus the invite → OTP → application → receipt → operator-review workflow.

Therefore the exhibition journey has a source-level contradiction:

- **operational layer:** invited controlled intake exists;
- **QR landing/access copy:** says working intake is closed;
- **public visitor:** can browse research and documents, but the displayed conversion path ends at a closed page.

This is not a claim that production is down. It is a content/routing reconciliation defect between current source surfaces and newer operational evidence.

## What the exhibition route should mean

The QR should remain a **public discovery route**, not an unauthenticated buyer-registration or instant-agency-activation route. The agreed next step should match the actual controlled operating model.

Recommended funnel semantics for LOCAL:

1. **QR scan:** `/mira/start/` — clear B2B promise, Phuket-first.
2. **Discovery:** `/mira/phuket/` — research catalogue with explicit supply caveat.
3. **Interest:** user selects a project/problem and sees one unambiguous agency next step.
4. **Human qualification at exhibition / agreed contact:** confirm that the person represents an agency and that an invitation is appropriate.
5. **Controlled invite:** owner/operator-agreed email is added through existing Access policy.
6. **Representative action:** their own OTP → agency application → immutable receipt.
7. **Operator review:** reasoned stage; a real agreement reference is required before agency activation.
8. **First commercial action:** separately admit one current project/supply path (C12 starts with VIVI), then register a real client only under that project's current rules.

The funnel should not imply that scanning the QR, downloading a local brief, viewing 618 records, authenticating with Access or submitting an application equals activation.

## Suggested source changes for LOCAL — no code change performed by CLOUD

### P0 — reconcile the CTA state

Replace the stale binary statement “рабочая регистрация пока закрыта” on exhibition-path surfaces with wording consistent with the accepted state: **controlled intake is available by invitation; public self-registration is not open**. The exact wording must remain consistent with the versioned privacy/intake notice and actual deployment state at release time.

Do not simply enable the disabled local form and call it registration. That form deliberately stores no PII/server submission and remains useful only as a local self-qualification tool.

### P0 — make the next step singular

After catalogue browsing, show one operationally true CTA such as **“Получить приглашение / подключить агентство”** only if there is a real staff-assisted/invited route behind it. If the exhibition process is staff-assisted, say so instead of presenting a dead public registration link.

Do not point an unknown public visitor straight into buyer operations. Buyer registration remains a separate closed gate.

### P0 — preserve the catalogue caveat at the conversion point

The 618 records are research/discovery coverage, not live inventory. At the CTA nearest the project selection, keep the sequence explicit:

`research record → current project verification → agency/project terms → client registration`.

C12 shows why: even a project with strong private evidence still needs current continuity, inventory, lead-protection and media/downstream-right checks before operational release.

### P1 — exhibition operator handoff

Give booth/operator staff a compact internal handoff rule:

- capture no buyer passport/banking/signed contract through the public page;
- for an agency representative, use only the approved invite path;
- record the resulting application receipt privately;
- do not call an authenticated user an active agency until a current agreement reference exists;
- after interest in a project, attach the exact project acceptance status rather than a generic “Phuket available” flag.

### P1 — measurement without fake conversion

For the printed QR proof, measure only events that the system can actually distinguish, for example QR landing, catalogue navigation and entry into the approved agency-intake path. Do not report a local brief download as a lead, an Access login as an agency, or application CI/tests as real conversion.

No analytics implementation is proposed here; this is a measurement-definition requirement for LOCAL.

## Physical QR / print gate

Existing QR target is stable in source and does not need regeneration **unless LOCAL intentionally changes the canonical landing URL**. Before print freeze, test the actual rendered QR on the physical proof with at least representative iOS/Android cameras and the final size/material. Existing source itself says print size/vendor/profile and physical QR proof are not yet owner/vendor-approved.

No claim is made here that `wegc.fund/mira/start/` was successfully fetched from a Russian network in this run. Source inspection is not a Russia-without-VPN measurement.

## Acceptance checklist for LOCAL

- [ ] QR still resolves to the chosen canonical public landing after the final release.
- [ ] Landing and `/mira/access/` no longer contradict the current controlled-intake state.
- [ ] Public self-registration remains closed if the operating model is invite-only.
- [ ] Catalogue still states research ≠ inventory.
- [ ] One visible next step maps to a real operator workflow.
- [ ] Local brief/download is not counted as submitted application.
- [ ] Access authentication is not counted as membership/activation.
- [ ] Buyer registration remains separate/closed until its own acceptance.
- [ ] Physical print proof and QR scan are tested before print approval.
- [ ] Russia reachability is measured separately by a real target-network tester.

## Result

The QR destination itself is coherent and Phuket-first, but the **conversion tail is stale**: current source pages still describe working intake as closed while the newer operational handoff records an owner-approved, invite-only controlled intake. C13 recommends reconciliation in source by LOCAL and a single truthful agency next step. No source page, QR, form or deployment was changed. External submissions/messages: **0**.