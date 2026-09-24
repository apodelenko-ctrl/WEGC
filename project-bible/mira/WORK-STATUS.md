# MIRA WORK-STATUS

## 24 сентября 2026 — публичный приём включён

Публичная форма: https://pilot.wegc.fund/mira/request/ . Приглашение не требуется. Worker source `f7e2a07`, version `b5345fe9-ca05-479d-94f7-2f2bfd6498a8`, D1 migrations 0001–0008. Включены отдельное уведомление, атомарное удаление контактов/истории и почасовое удаление по сроку хранения. 100/100 Node tests PASS.

Проверено в реальном браузере: настоящий Turnstile → сохранённая служебная заявка → назначенный оператор → ответ в личной квитанции. Проверка создана 2026-09-24T16:07:19Z, id `e19ca5be-7869-439d-9935-5740e065c446`; это тест запуска, не реальный лид. Публичный приём не означает автоматического коммерческого допуска проекта или регистрации покупателя.

Начата работа с застройщиками: 24 сентября отправлены follow-up Botanica по договору от 19 сентября и новый запрос The Title по VIVI, материалам и правилам партнёрских агентств. Условия не считаются подтверждёнными до ответа. Детали: [журнал контактов](operations/developer-outreach-2026-09-24.md).

Выставочный выпуск связывает страницы /mira/start/, /mira/go/, /mira/access/ и каталог с действующей формой. 60 текстовых обложек заменены четырьмя лицензированными фотографиями направлений; 678 карточек и исходные 618 записей Пхукета сохранены. Авторы и лицензии: /mira/catalog/photo-credits/. Проверки: 187 Node / 144 Python PASS; мобильный первый экран 390×844 и карточки проверены в браузере. Следующий шаг: пополнять карточки материалами конкретных проектов по ответам застройщиков. Приоритет коммерческого контура: актуальное наличие по запросу, регистрация/дубли/защита, договор и комиссия, допустимая субагентская модель.


## Актуальное продолжение — 24 сентября 2026

[Выпуск кабинета входящих и следующие шаги](operations/release-intake-2026-09-24.md). Worker source `6305604`, live version `74857851-4bcd-4ea5-9741-551b23defac6`; D1 0005–0007 применены, 95/95 тестов PASS. Реальный вход оператора в research и inbox проверен. Публичный приём пока выключен: следующие шаги — удаление/retention, отдельное уведомление, живой запрос/ответ и QR. VIVI — наличие по запросу; реальные сделки ещё NO-GO. Продолжать с ветки `codex/mira-expo22-operator-20260922`. Ниже сохранена историческая запись.

## 2026-09-18 — final QA follow-up: static back navigation and portable browser reports

PR #10 merged as `ce5153714cab8e83dd0a4243b123c627482bd006`; Pages run 35250067420 succeeded, snapshot `1129ee8014c5a022d418bcad7684982a6d0742cf`. A fresh real owner browser session confirmed the deployed operator dashboard and agency administration screen without creating production records.

The first return-link fix handled slow feeds but live testing exposed a click before the detail JavaScript itself initialized. Static detail back links now carry an explicit restore marker; the catalogue safely recovers only same-country stored filters. All 648 existing/new detail URLs are retained. A regression aborts the detail module entirely and still checks the restored search. Local expansion browser: 13 groups passed, including all 30 objects and 42 internal links. Combined 122 Node / 144 Python tests pass.

The new Linux CI pilot browser step also exposed the Mac-only default `/private/tmp` output path. It now uses the platform temporary directory; the complete local signed-identity/CSP browser scenario passed again. Full release 35250357478 had a failing local browser stage; its exact logs remain to be inspected when artifacts finish. Do not call that run successful or waive its checks. The follow-up release must repeat all CI/live suites.

Images, intake/privacy gates, Worker version and D1/Access/DNS remain unchanged. Cloud content gaps remain in `research/bali-dubai-2026-09-17/MEDIA-GAPS.md`. No buyer or agency intake was opened.

## 2026-09-17 — completed administration and separate deployed Worker checkpoint

The preserved admin branch now contains completion commit `74aae63` after WIP checkpoint `640c64e`. Its production Worker and six pilot assets were independently deployed as version `ba3d25b6-efdc-45ce-804e-4c7dc052fce9` (previous version `15da744a-8345-43f1-a2e4-e88ecbb4d00b` retained for rollback). Agency list/detail, verified application review, agreement reference, representative binding, operator decision, membership revoke/restore and paginated agency/member audit are implemented. The current integration brings only these completed source changes into main; no WIP screenshots are included.

Local combined regression: 122 Node / 144 Python tests passed. The isolated signed-identity browser scenario uses the actual site Worker CSP and all three migrations: receipt/reload, qualification, synthetic agreement/owner/onboarding, cross-identity denial, failed activation without evidence, revoke/restore, expired-session receipt recovery and 53-event audit pagination passed at 390/768/1440 widths, with no JS/CSP errors. This is not a real applicant or production agency activation. The browser scenario is now included in the existing release-verification workflow.

Live anonymous verification: protected pilot/library/session/admin endpoints redirect to Access; public pilot JS/CSS return 200, no-store, production CSP, and match deployed source bytes. Existing Access owner login/operator demonstration remains valid historical evidence; no new ordinary-applicant OTP/receipt/decision acceptance is claimed. Applications/material delivery stay disabled, privacy variables empty, buyer registration closed; Access allowlist and D1 schema unchanged.

An actual dedicated-D1 export was restored into a separate private local SQLite database. All 13 MIRA tables, integrity and foreign keys checked successfully; production was not restored or modified. Remote-D1 restore and maximum production capacity remain untested. Private dump/identity values are not included in this repository.

Public expansion PR #9 merged as `2d85898267b60c19a88b3a42b12388546070dfc0`, generated snapshot `e1a276a7d4f482a125eb92e7ef557e46df2f96ff`. Pages run 35248400519 and full local/live release acceptance 35248674309 succeeded. A separately observed fast detail-return race is being fixed with an explicit feed-failure regression; passing CI does not erase that observation. Media remains 11 inherited project-image associations plus 637 labelled covers across 648 records; none of the 30 expansion images is publication-approved. Cloud content follow-up: `research/bali-dubai-2026-09-17/MEDIA-GAPS.md`.

Remaining owner gates: approved privacy/processing-location/retention/deletion notice and narrowly approved ordinary-applicant Access/OTP test; actual business evidence before any activation; direct Russian-network probe. Continue from existing resources, never re-provision them. Previous entries below are preserved historical records.

## 2026-09-17 — current local integration checkpoint (supersedes stale launch blockers)

PR #8 is already merged. Owner email login and operator access on `https://pilot.wegc.fund/mira/pilot.html` were demonstrated in the real browser. Existing Worker `mira-pilot-api`, deployed source `5ab0824ea7061e0a8a5b731075d471421bbeb752`, version `15da744a-8345-43f1-a2e4-e88ecbb4d00b`; existing dedicated D1 has all three migrations. Do not recreate these resources or first operator. Historical entries below about missing Access/undeployed Worker are superseded. Intake/material delivery remain disabled; no real applicant receipt or business activation accepted yet. Buyer registration remains closed.

Unfinished admin work safely committed as `640c64e` on `codex/mira-admin-checkpoint-20260917`, separate from this public worktree. Public expansion branch `codex/mira-bali-dubai-public-20260917` starts at `cd76cb5`: 618 original Phuket rows preserved byte-for-byte (SHA256 `f3366c36c683e27e9f79d8db96a7f2985272395eba1906f751ebe019ac6b1bf4`) plus 15 Bali and 15 Dubai research projects. Package applied once. Phuket funnels, Worker, Access, D1 and rights unchanged.

Local public acceptance: 118 Node / 144 Python tests; expansion browser 11 groups including all 30 details and mixed shortlist; existing campaign 15 / editorial 4 groups. Real domain before release: Phuket 200, Bali/Dubai 404. This checkpoint is NOT a publication. Media: 28 local candidates inspected, zero publication-approved new project images, 30 labelled typographic covers. See `research/bali-dubai-2026-09-17/MEDIA-GAPS.md` for cloud content handoff. ERA primary source redirects to a different project; replacement broker source explicitly labelled, no substitute image used.

Next: finalize independent admin acceptance, preserve separate releases, verify actual domain after Pages publication. Intake privacy/data-location decision, ordinary applicant OTP and Russia-without-VPN remain separate live acceptance gates. No public personal identity values or credentials belong in these records.

## 2026-09-17 — Wrangler access restored; dedicated database prepared

Owner completed Wrangler OAuth. Live `whoami` and Cloudflare API confirmed access to the account containing active zone `wegc.fund`. Created a NEW dedicated `mira-pilot` D1 database, verified its creation time/empty schema and applied all three existing migrations (0001/0002/0003). Remote verification confirms 13 MIRA tables, zero applications and zero memberships. No synthetic users or real personal data were inserted. Region reported by D1: APAC (Singapore serving colo); no data-location approval is inferred.

The local ignored `cloudflare-worker/mira/wrangler.toml` contains verified account/database IDs and the narrow planned `/mira/api/*` route. Applications and material delivery remain false. `wrangler deploy --dry-run` built the Worker successfully; no Worker or route was published. Offline preflight fails only on the absent actual Access issuer/audience, as expected; do not substitute guessed values.

New concrete blocker: Cloudflare Access API returned 403 / `access.api.error.not_enabled`; the organization endpoint also rejected this OAuth scope. Owner was asked to initialize Zero Trust / Cloudflare One with the Free plan in the dashboard and provide its team domain. This account setup involves plan selection/terms; it has not been completed by the agent. After it is ready, configure/verify the Access application and policy, then deploy and run real login/receipt/operator acceptance. Do not treat Wrangler login, D1 schema or dry-run as successful agency signup. The prior expired-token blocker below is historical and now resolved. Existing unrelated resources were not mutated.

## 2026-09-17 — integrated release accepted; agency login still blocked

Public presentation is deployed, PR #8 is merged (`f25c32f75364de2feb9b7f1471955130432de218`), and full release verification **35223247185 succeeded** after the two editorial test fixes. Exact tested source: `e3a8d424062f471f102f103fbcc38cf71a1a3260`; generated snapshot: `6227865e4cfc82d273cdcc0f0690ad33fabb42f6`. Verified artifact `10498880419`, SHA256 `14b854c911562046a71720e3085ba6d5fc7f70cc8ed807ca81aec1921dcea35d`. Combined tests: **98 Node / 120 Python**, plus local and live public/campaign/editorial browser groups **12 / 15 / 4** and all 618 live project URLs. No assertions or CSP protections were removed.

Full Russian handoff: `operations/2026-09-17-local-integration-handoff.md`. Owner's next priority is actual agency login and administrative approval under `cloudflare-worker/mira/SERVER-START.md`, not more redesign. Real login has NOT passed acceptance: `/mira/api/health` returned 404; Wrangler authorization expired and OAuth was not completed. Owner was asked to refresh local login. No new Cloudflare resources, real intake or buyer registration enabled. Continue from this blocker after authentication; passing CI is explicitly not successful signup. Older entries below are historical checkpoints.

## 2026-09-17 — PR 8 integration and next priority

Owner explicitly requested reviewed integration of PR #8 while preserving the public presentation work, followed by actual agency login and operator approval using `cloudflare-worker/mira/SERVER-START.md`. Buyer registration remains separately closed. The presentation commit `e49c966607b8e33795f2eb1a6ed1194827bbac9a` and generated snapshot `86578fd839ca97c27ecc79c585fc9521fa1f8468` are preserved. PR head reviewed: `8567c8aa5a0015531016ae5b32a7bbce9048b4d6`; only WORK/RESUME conflicted, both histories retained below. No source transport was reapplied.

Combined local regression: **98 Node / 120 Python tests passed** (Node local runtime, Python 3.12.14; temporary SQLite/synthetic signed identities, not real signup). Public deploy run `35220869533` passed. Full acceptance `35221091559` passed local browser suites, actual-domain byte/link audit and public/campaign browser suites (618 records, 26 pages, seven widths); its live legacy-editorial check failed because an immediate `is_visible()` assertion ran before asynchronous rendering. Changed that assertion to wait for the same heading, without removing coverage. A fresh combined release must verify the fix.

Actual `/mira/api/health` returned HTTP 404 on this check. Local Wrangler credentials were expired; authorization refresh is in progress. No MIRA Worker/D1/Access deployment or successful real email login is claimed. Next: finish fresh live acceptance, inspect authorized Cloudflare resources and configure the dedicated service; verify real email delivery/login, durable receipt, administrative approval, isolation and revocation independently of CI. The historical checkpoints below describe their own times, not the latest priority.

## 2026-09-17 — local first-partner presentation checkpoint

Current owner priority: improve and publish the public MIRA catalogue for the first agency presentation; keep real registration disabled. All 618 cards/details now have labelled visuals (11 project-image associations plus editorial covers), refined copy and working shortlist/navigation. Local 83 Node / 110 Python tests passed; in-app browser checked 26 pages, 618 unique records, three detail pages, desktop/mobile and the preserved onboarding → 45-record catalogue route. See `operations/2026-09-17-first-partner-presentation.md` for exact scope and the standalone Chrome sandbox limitation. Live publication/acceptance remains the next step for this checkpoint. Earlier CP16 full-run failure below remains historical evidence, not erased.

## Parallel server checkpoint — 2026-09-17; isolated branch, not production

`mira/parallel-server-20260917` adds transactional administrative audit, operator-only paginated history, a signed-identity onboarding/receipt suite and read-only configuration preflight. No public `mira/` files were changed. Local Codex retains the public visuals and site-review lane.

Dedicated CI run `35219962533` completed successfully: **98 Node / 116 Python tests**. The ordinary Worker source was saved on the branch and its SHA256 matches `85fe3edcee9326c6b24546e79cd02705457cbdf2da1025caf2c251d0ded6ed25`. See `operations/parallel-server-result.json`, `operations/parallel-server-2026-09-17.md` and `cloudflare-worker/mira/SERVER-START.md`.

This fixes missing application audit records for agency/project/membership/assignment mutations, including rollback if audit storage fails. It does not log direct SQL administration or reconstruct earlier history. Tests use the actual Worker and migrations, synthetic RSA-signed users and local SQLite; only the Access certificate response is mocked. They do not prove email delivery, remote D1, deployed browser behavior or production capacity.

The branch has not been merged into main and no Cloudflare deployment or real intake has been enabled. Integrate through a reviewed PR without overwriting local work. Reconcile status updates from both lanes. Prior main status is retained below unchanged for continuity; its remaining visual-readiness statement must be reassessed after the owner's subsequent screenshot review.

## Preserved main status at 13360ee8e9b74f22b6e474f128bbd3ac5b5cd513

2026-09-17 — CP16 public acceptance inspected; first-partner introduction scope established. Real registration remains closed.

## Latest verified outcome

Full-public-release run `35201900100` has overall **failure**, not overall success. Its archive `10488591012` was downloaded and its SHA256 verified. See `operations/2026-09-17-first-partner-handoff.md` for exact provenance and scope.

The actual-domain campaign report passed all15groups for `/mira/go/`, `/mira/practical/`, `/mira/corporate/`, the618-record catalogue, filters, shortlist, details, error recovery, documents, motion and no-JavaScript behavior. Seven widths checked. No page/CSP/unexpected-request errors recorded. The actual-domain audit passed and covered all618projectURLs. The other public-page suite passed12groups. These results support sharing the new direct landing and research catalogue for a prospective agency's introduction, not promising working signup or developer registration. Russian-network reachability and maximum production capacity were not established.

The preserved editorial suite still failed waiting for a catalogue selector after qualification. Its preceding assets/responsive group passed. Investigate the onboarding-to-catalogue route; do not erase that failure or conflate it with the passing new campaign suite. Tested source `b5d5b6acbff0976669c4a2da60079bd12a88b8d8`; generated snapshot field `0eaee4a1d2f9065abff701f525947b17bb925ea6`.

## Owner launch decisions

WEST EAST TRADE GROUP PTE. LTD. confirmed as operating/contracting company. Owner confirmed as first administrator using the email supplied privately in conversation. Self-registration/email confirmation followed by operator-reviewed business access accepted as the intended process. Identity verification, actual provisioning and approved privacy configuration still required.

Owner prefers Cloudflare in the existing account and postponing migration. This is an infrastructure preference, not legal clearance for real-data collection. No new resources or signup were enabled. Cloudflare directory discovery returned no available entry; do not repeat an inactive/invented connection card. Local Wrangler login reported by owner does not authenticate this runtime. Keep unrelated Workers, databases and secrets untouched.

## Recovery history

Recovered snapshot `5a625ec1ef9977cacdf80bfe50accd5ccf526a49` from Actions35199078722/artifact10486879347; ZIP SHA256 matched `1ebef424cbd749fb4c4a1fd37623c4557ff4bed7c1702c7e3ee155fe1f662011`.

CP15acceptance35199313364 failed in a negative-response fixture: Playwright's Request argument displaced the lambda's HTTP status. Later stages were skipped. CP16 replaced it with a validated fixture factory and four regressions; local83Node/106Python passed. Browser navigation in the earlier execution container was blocked by administrator policy; authorized GitHub Actions was used for actual HTTP/CSP verification, without bypassing that policy.

## Published sources

CP12: nine draft legal documents,20-page framework PDF with19sections/5appendices and DOCX. Negotiation drafts, no acceptance.
CP13: all618research cards and individual URLs at `/mira/catalog/`, plus preserved `/mira/phuket/` skin. Original45-demo and earlier designs intact.
CP14: `/mira/go/`, `/mira/practical/`, `/mira/corporate/` funnels; `/mira/launch/` comparison; `/mira/exhibition/` vector banner and QR to `/mira/go/`. Source0f4413d6, QA35197901350 andPages35197901315 succeeded; snapshotc2f0dce5. Concurrent start/growth/business/variants/access/expo files preserved. No owner design or print approval.
CP15sourceQA35199078722 andPages35199078856 succeeded; actualacceptance35199313364 failed. Do not confuse these scopes.

## Real launch boundaries and next work

No real signup or buyer registration. Controller/company choice now confirmed, but privacy, data location, security, authentication, verified administrator provisioning and current project commercial gate remain unresolved. Do not treat future migration as compliance evidence. Project rows are not available units or verified sellers. Buyer funds and commission separate. Public drafts are not signed agreements or approvals. Private originals never enter GitHub. No external sends or retry of the denied email path.

Next: fix the preserved editorial acceptance route; obtain actual authorized deployment access; implement/verify the intended signup path without weakening privacy or project gates. Use the passed direct landing and catalogue for introduction meanwhile. Do not recollect618records or restart design.

Baseline:Phuket618/40groups/45seed/66candidates/507unresolved/20queue/8P0;Russia100source/50inheritedreviews,focused21/15reviewready/6holds/10directroutes7companies. Existing copy/playbooks and protectedAPI/materials sources retained. SyntheticAPI100retries/1000reads and5000catalogueoperations, boundedGET/HEAD andloopback smoke are not production capacity.

<!-- MIRA-LAUNCH-AUTO:START -->
## Generated source checkpoint

Source commit: `bc82eb97e1e6e8252e5ce689faaf730b02185866`.

Phuket: **618 / 618** source rows covered; **45** seed mappings preserved; **66** generator family candidates; **507** family-unresolved rows. **0 project legal sellers verified / 0 registration-enabled projects in this generated layer.**

Russia: **100** quality-layer rows; **50** matched to inherited live reviews; **0** review join exceptions. **13** inherited ready-for-owner-review; wave approval remains as in source. No new live verification or sending performed.

Canonical dashboard: `operations/LAUNCH-DASHBOARD.md` and JSON/HTML beside it. Full project register: `data/phuket-project-master.csv`. Agency quality layer: `sales/russia-launch-100-quality.csv`. Developer stage register: `sales/phuket-developer-stage-register.csv`.

Continue: resolve evidence gaps, complete acquisition assets, implement/deploy protected pilot. Generated coverage is not business launch readiness.
<!-- MIRA-LAUNCH-AUTO:END -->

## 2026-09-18 — controlled agency intake and guided cabinet

- Public PR 11 release acceptance completed: run 35251270668 SUCCESS, tested source `021a3dd51d7f9fe1732dc6c635d90ac442cca93a`; deployed Pages snapshot `91a2eae20ab65244d086135aada9fbdae3f6faf7`. All local/live public suites passed; isolated pilot acceptance passed. Live bounded GET smoke 80/80, concurrency 4; not a maximum-capacity claim.
- Owner explicitly requested opening agency intake and confirmed the concrete intake notice, its 24-month enquiry retention period and working privacy contact. Version `mira-agency-2026-09-18-v1` is scoped to invited agency representatives. This is not a legal-compliance finding or authorization for mass buyer collection.
- Cabinet form now has three steps, back navigation retaining input in memory, review, explicit initially-unchecked consent, native help disclosures, reduced-motion support, and a persisted server receipt. No personal-data browser storage added.
- Local acceptance: 123 Node, 144 Python tests; signed-Worker browser flow passed, including a lost POST response followed by recovery of the same receipt, no duplicate, operator workflow, missing-proof rejection, isolation, revoke/restore/audit and expiry recovery. Applicant widths 320/390/768/1440.
- Operator application card includes a compose-email link and document-template link. Neither sends mail nor represents a signed agreement; sent-message history is not implemented.
- Narrow asset allowlist grows from six to eight reviewed UI files (dedicated pilot CSS and same-origin agency notice); protected HTML and JWT verification remain unchanged. Existing public marketplace styles/funnels unchanged.
- Deployment and real second-email acceptance are the next steps. No real agency activated, no buyer registration enabled, no fabricated business evidence.

## 2026-09-18 — controlled intake published

- PR 12 merged as `bf704142eed89a5e976c8db15f548d1779470f32`; source cabinet commit `48737029628cb27164548ffb266eb3f35e5aea86`.
- Dedicated Worker version `38fd1679-40cf-44d6-a572-b760431555f9` is live with `APPLICATIONS_ENABLED=true`, approved notice `mira-agency-2026-09-18-v1`, and materials/buyer gates unchanged. Previous version: `ba3d25b6-efdc-45ce-804e-4c7dc052fce9`. Existing D1, JWT configuration and pilot custom domain retained; no migration or apex DNS change.
- Live owner session opened the three-step form and the operator queue. Queue/agency counts were empty; no fabricated production activation. Four public pilot assets (JS, base CSS, pilot CSS, notice) matched their packaged bytes; anonymous protected page/API probes redirect to Access.
- Owner was given the precise existing-policy change for the agreed second test address. Its OTP login and real receipt/re-login/operator decision remain pending. The agent has not expanded Access itself.
- Pages run 35254761053 and source QA 35254761013 succeeded. Generated Pages snapshot: `b8648c1cb2070aeb0c73610413bf00ee083ad1c2`. Full post-release verification 35255017692 is running; previous run 35251270668 is a separate successful milestone.
- Personal-data retention is a manual operator duty; no automated purge exists. The approved notice is for invited agency enquiries. Broader legal/location readiness and Russia-without-VPN availability have not been established.

### Final post-PR-12 verification

Run [35255017692](https://github.com/apodelenko-ctrl/WEGC/actions/runs/35255017692) completed SUCCESS for every step, including actual-domain browser acceptance. Pages 35254761053, built-in Pages 35254867047, source QA 35254761013 and agency landing 35255017625 also completed SUCCESS. No competing manual public deployment was started.

Artifact `mira-cp16-public-release`: SHA-256 `2f253f54c7261491755301dacb7d0932bc0c8f911c30ce399d063912d0abd93e`. Code/source and deployment evidence remain distinct from the still-pending real second-email applicant workflow. The live owner session is working, intake is enabled for allowed identities, and the owner-side Access/OTP action is the remaining live-acceptance dependency.
