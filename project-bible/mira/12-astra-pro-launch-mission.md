# 12 — Astra Pro launch mission

**Дата:** 2026-09-16  
**Статус:** ready to run after owner starts a new ChatGPT Work/Astra session.  
**Цель:** не исследование ради исследования, а доведение МИРА до рабочего pilot-launch состояния: сайт/marketplace MVP + воронка агентств + developer acquisition + launch operations.

## Главный принцип

Не считать завершением задачи создание документов, списка контактов, красивого лендинга или подписанного агентского договора.

Главная бизнес-воронка МИРА:

`qualified agency → verified contact → conversation → demo → contract → onboarding → activated market → registered client → active deal → developer commission received → agency settlement`

Успех агентского направления начинается после activation / registered client, а не после подписания договора.

Главная supply-воронка:

`developer identified → legal/sales entity resolved → channel owner verified → commercial terms received → agreement signed → project/inventory onboarded → lead-registration tested → first agency enabled → first registered buyer → first booking`

## Режим работы Astra

Это один длинный execution run. Не останавливайся после отдельного batch/worker/artifact. Любой milestone — checkpoint.

После каждого значимого блока:

1. сохранить результат в GitHub;
2. обновить `WORK-STATUS.md` и `RESUME-STATE.md`;
3. немедленно взять следующий независимый блок;
4. не ждать пользователя, если решение можно безопасно принять как рабочую гипотезу.

Не создавать десятки коротких агентов ради счётчика. Использовать параллельные workers только для действительно независимых задач.

Не отправлять внешний outreach/forms/messages без отдельного owner approval.

---

# MISSION A — MIRA marketplace MVP

## A1. Аудит текущего сайта

Начать с:

- `/mira/index.html`;
- `project-bible/mira/product/mvp-spec.md`;
- `04-platform-data.md`;
- `05-payments-legal.md`;
- `06-roadmap.md`;
- существующего Phuket catalog/data layer;
- существующих Cloudflare Worker scripts и доступной инфраструктуры repo.

Сначала определить минимальную архитектуру, которая может быть реально запущена без превращения проекта в тяжёлую CRM.

## A2. Что должно работать в первом MVP

Минимальный functional marketplace:

1. public agency landing;
2. agency application / qualification form;
3. agency login / access layer, если текущая инфраструктура позволяет безопасно реализовать;
4. agency profile;
5. markets catalogue;
6. developer catalogue;
7. project catalogue;
8. filters by country / area / property type / budget / delivery / payment plan where source-backed;
9. project detail page;
10. source/last-verified metadata internally;
11. client registration form;
12. lead status;
13. agency/client protection status as confirmed by developer rules;
14. deal status;
15. commission ledger/status;
16. payment-support request;
17. documents / material links;
18. onboarding/training section;
19. admin data-management path, even if partially manual for MVP.

Do not build telephony, full CRM, internal chat or unnecessary enterprise features.

## A3. Data policy

Do not expose unverified inventory, price, commission or lead protection as current fact.

Each critical field should support:

- source URL/type;
- verified date;
- status;
- manual override reason;
- responsible operator where relevant.

Project brand != legal seller.

## A4. Delivery stages

### MVP-0 — sellable demo

A polished public landing + clickable/functional agency demo with real Phuket examples and no fake functionality.

### MVP-1 — pilot operations

Functional agency onboarding, project catalogue, client registration and manual backend/admin workflow.

### MVP-2 — transaction layer

Deal/commission/payment-request statuses and operational logs.

Do not wait for MVP-2 to begin the manual pilot if MVP-0/1 is operationally safe.

---

# MISSION B — agency acquisition machine

Source of truth:

- `sales/AGENCY-SALES-PLAYBOOK.md`;
- `sales/agency-crm-template.csv`;
- `sales/russia-live-50-segmentation.csv`;
- `sales/russia-wave-01-owner-review.csv`;
- `sales/MIRA-PILOT-PACK.md`;
- `sales/MIRA-ONE-PAGER.md`;
- `/mira/` landing;
- `research/mira-first-webinar.md`.

## B1. Finish Launch-100 quality layer

For all 100 agencies classify:

- greenfield overseas;
- existing foreign-property desk;
- existing Phuket/Thailand direction;
- network/franchise/platform;
- premium/investment;
- regional new-build;
- resort agency;
- hold/entity-resolution.

Do not use one generic pitch for all segments.

## B2. Decision-maker coverage

Goal:

- 50 fresh live-reviewed accounts;
- 25–30 strong decision routes;
- 15–20 owner-review-ready accounts;
- first 10 manual outreach drafts fully personalized;
- no sending before owner approval.

Priority decision roles:

- owner / founder;
- CEO;
- commercial director;
- head of new-build sales;
- business development;
- partnerships;
- international / foreign-property director.

## B3. Marketing funnel

Build one integrated funnel:

`database / Telegram / webinar / content / partner referral / direct outreach → landing → qualification → call → demo → contract → onboarding → activated project → registered client`.

Required artifacts:

- CTA matrix by segment;
- first 30 publish-ready Telegram posts;
- first webinar invite/landing/follow-up sequence;
- downloadable Phuket starter kit;
- qualification scorecard;
- demo script;
- onboarding checklist;
- reactivation sequence for agencies that sign but do not activate;
- CRM fields and stage-entry/stage-exit rules;
- KPI dashboard definition.

Main KPI is not signed agreements. Track:

- qualified;
- conversations;
- demos;
- signed;
- onboarded;
- activated;
- registered clients;
- active deals;
- bookings;
- developer commission received;
- agency settlement.

---

# MISSION C — Phuket developer machine

Source of truth:

- internal ~618-project WEGC catalog;
- `data/phuket-developer-master.csv`;
- `data/phuket-developer-alias-map-v1.csv`;
- `data/phuket-project-master-seed-45.csv`;
- `sales/phuket-developer-outreach-queue.csv`;
- `sales/phuket-p0-commercial-verification.csv`;
- `sales/developer-acquisition-pack.md`.

## C1. Full project normalization

Continue from 45 normalized rows through the entire internal Phuket backbone.

Output:

`project → developer family → legal/contracting seller → operator/brand if different → official source → current status`.

Do not convert project names into fake developers.

## C2. P0 developer commercial readiness

For priority groups resolve where possible:

- named agency-relations/channel owner;
- contracting entity;
- agreement template;
- eligible projects;
- current inventory mechanism;
- commission schedule;
- commission trigger;
- payout timing;
- client-registration method;
- lead-protection period/rules;
- duplicate-lead dispute process;
- marketing-material rules;
- broker portal/API/feed if available;
- buyer/payment-plan constraints.

Unknown stays unknown until evidenced.

## C3. Developer onboarding pipeline

Create an operational developer CRM schema and stage rules:

`identified → contact verified → intro → terms requested → legal/commercial review → agreement ready → signed → projects loaded → inventory verified → first agency activated → first lead registered → first booking`.

Build owner-review wave for P0 Phuket developers, but do not send without approval.

---

# MISSION D — supply expansion

Only after Phuket P0 is under control, continue Bali / Vietnam / Dubai.

For each market separate:

- developer;
- master agent;
- brokerage;
- operator;
- project brand;
- legal seller.

Goal is actionable supply, not a list of names.

For each developer capture official first-party route and commercial onboarding path.

---

# MISSION E — operations and launch readiness

Create one canonical launch dashboard covering:

## Agency side

- source-backed accounts;
- live-reviewed;
- decision maker found;
- owner-review ready;
- approved;
- contacted;
- conversation;
- demo;
- contract;
- onboarding;
- activated;
- client registered;
- active deal.

## Developer side

- identified;
- entity resolved;
- channel owner found;
- terms received;
- agreement under review;
- signed;
- inventory loaded;
- lead registration tested;
- agency enabled;
- first lead;
- first booking.

## Product

- public landing;
- application form;
- authentication/access;
- catalogue;
- client registration;
- deal status;
- commission status;
- payment request;
- admin workflow;
- deployment status;
- known blockers.

---

# Definition of launch-ready

## Marketing/pilot-ready

MIRA can start controlled manual agency acquisition when:

1. landing is production-quality and accurate;
2. application/qualification route works;
3. first owner-approved agency wave exists;
4. demo and onboarding are ready;
5. at least one real Phuket supply path can accept a registered client under known rules;
6. sales manager has playbook + CRM + next-action discipline.

## Marketplace pilot-ready

The actual MIRA marketplace MVP is pilot-ready when an agency can:

1. enter the system;
2. see allowed markets/projects;
3. open a project card;
4. submit/register a client;
5. see acknowledgement/status;
6. see a deal/commission status path;
7. request payment support;
8. access materials and onboarding.

Manual operator actions behind the scenes are acceptable in MVP.

## Commercially repeatable

Do not call the model repeatable until there is evidence of:

- multiple agencies activated;
- real registered clients;
- at least one active/closed deal;
- developer lead-registration working as expected;
- commission/settlement path evidenced;
- no material client-ownership conflict in the pilot process.

---

# First execution order

1. Read current `WORK-STATUS.md` and `RESUME-STATE.md`.
2. Audit `/mira/` and implement the highest-value MVP-0/1 gap.
3. Finish Russia live-review/segmentation and owner-review wave.
4. Continue full Phuket project normalization and P0 commercial verification.
5. Build agency + developer CRM stage registers.
6. Build demo/onboarding assets around actual product behavior.
7. Update launch dashboard.
8. Commit checkpoints.
9. Continue automatically until actual runtime/allowance exhaustion or a blocker affecting all independent workstreams.

No mass outreach and no external form submissions without separate owner approval.
