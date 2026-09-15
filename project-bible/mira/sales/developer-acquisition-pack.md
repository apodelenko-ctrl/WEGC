# Developer Acquisition Pack — МИРА

**Статус:** рабочий пакет для ручного, персонализированного outreach; массовая отправка не выполняется.  
**Дата подготовки:** 2026-09-15.  
**Назначение:** подключение иностранных застройщиков и проектов к B2B-маркетплейсу МИРА через единый developer-facing процесс.

## 1. Позиционирование

МИРА — B2B-маркетплейс зарубежной недвижимости для российских, белорусских и русскоязычных агентств. Для застройщика это единый коммерческий вход к распределённой сети независимых агентств и брокеров.

Агентство сохраняет собственные отношения с клиентом и работает под своим брендом. МИРА предоставляет каталог проектов, материалы застройщика, регистрацию и защиту лида, договорную инфраструктуру, статусы сделки и отдельное документированное платёжное сопровождение допустимых сделок.

### Value proposition для застройщика

**One relationship. A structured distribution channel to Russian-speaking real-estate agencies.**

Мы предлагаем застройщику:

- единое подключение проектов и коммерческих условий;
- доступ к агентствам, которые сохраняют своих клиентов и могут предлагать им ваш проект;
- структурированную регистрацию клиента и понятные правила lead protection;
- распространение актуальных project materials и payment plans;
- согласованный процесс коммуникации, статусов и отчётности;
- возможность согласовать отдельные условия для сети: campaign, inventory или payment-plan initiatives;
- локализацию ключевых материалов для профессиональной русскоязычной аудитории;
- отдельное платёжное сопровождение покупателя по документам сделки, если такая услуга допустима для конкретного кейса.

Публично не заявляем размер сети, количество брокеров, объём лидов, сделки, конверсию или buyer demand, пока эти показатели не подтверждены журналом МИРА.

### Что МИРА просит у developer

На первом этапе достаточно прислать:

1. стандартный agency agreement или partnership terms;
2. commission schedule и правила выплаты;
3. client / lead registration rules и срок защиты;
4. список проектов и актуальный inventory;
5. brochures, fact sheets, price lists, floor plans, renders и brand guidelines;
6. payment plans и валюту расчёта;
7. sales / agency relations contact;
8. сведения о broker portal, API или ином способе обновления inventory, если доступно;
9. ограничения по рекламе, использованию бренда и географии покупателей;
10. список документов, необходимых для регистрации сделки и выплаты комиссии.

Если конкретное поле не раскрывается публично, в CRM фиксируем 'not disclosed', а не предположение.

## 2. Message architecture

Основной порядок сообщения:

1. Кто мы и какой канал строим.
2. Как это снижает нагрузку developer: один процесс подключения и единые правила.
3. Как защищаются роли: агентство сохраняет своего клиента, developer сохраняет контроль над inventory и правилами.
4. Что требуется для fit review.
5. Следующий шаг: короткий call или обмен onboarding materials.

Не обещать гарантированный объём продаж, минимальный результат, определённую комиссию или платёжный маршрут без письменного подтверждения developer и проверки конкретной сделки.

## 3. First outreach email

### Subject options

- Russian-speaking agency distribution for {{Developer / Project}}
- Distribution partnership for {{Market}}
- One structured channel to Russian-speaking agencies
- Agency network partnership — {{Developer}}
- Introducing {{Project}} to qualified agency partners

### Email 1 — concise

Hello {{First name}},

I am reaching out on behalf of {{MIRA / working company name}}. We are building a B2B marketplace that connects international developers with real-estate agencies serving Russian-speaking buyers.

Our model gives developers one structured commercial relationship while agencies keep their own client relationships and brand. Through the platform, agencies can access project information, current sales materials, lead registration rules and commission documentation.

We are reviewing {{Market}} and would like to assess whether {{Developer / Project}} could be included.

Could you please share the appropriate sales or agency-relations contact, or send:

- your agency / partnership terms;
- commission schedule;
- lead-registration and protection rules;
- current project and inventory materials;
- payment plans;
- the contact responsible for international agency partnerships.

If there is a fit, we can arrange a short introductory call and follow your preferred onboarding process.

Best regards,  
{{Name}}  
{{Role}}  
{{MIRA / working company name}}  
{{Email}} | {{Website}}  
Singapore

## 4. Follow-up sequence

### Follow-up 1 — 3–5 business days

Subject: Re: Distribution partnership for {{Market}}

Hello {{First name}},

I wanted to follow up on my note about including {{Developer / Project}} in our review of {{Market}} supply.

The first step is only a fit check. We would like to understand your current agency terms, client-registration process, available materials and the right contact for international distribution.

If you are not the right person, could you please direct me to the relevant sales or partnerships colleague?

Best regards,  
{{Name}}

### Follow-up 2 — 5–7 business days later

Subject: {{Project}} — agency terms and lead registration

Hello {{First name}},

To keep this practical, we can review the following by email:

1. standard agency agreement or terms;
2. commission schedule;
3. lead-registration process and protection period;
4. current price / inventory materials;
5. payment plans and marketing guidelines.

We will then return a short list of questions and a proposed onboarding path.

Best regards,  
{{Name}}

### Follow-up 3 — value clarification

Subject: A structured channel for {{Developer}}

Hello {{First name}},

A developer joining MИРА can work with multiple independent agencies through one structured process. Each agency remains responsible for its client relationship; the developer receives the agreed registration, communication and reporting workflow.

We are designing the first project set for {{Market}} and would be glad to evaluate {{Project}} against the same documented criteria as the other projects.

Would {{two proposed time windows}} work for a brief call?

Best regards,  
{{Name}}

### Close-the-loop email

Subject: Closing the loop — {{Developer}}

Hello {{First name}},

I will close this thread for now. If international agency distribution becomes relevant, please feel free to contact me and we can review your current terms, project materials and lead-registration process.

Best regards,  
{{Name}}

**Operational rule:** send only after human review of recipient, company, source and personalisation. Add an opt-out or honour any request not to be contacted. Do not attach large files in the first email; use one reviewed link where necessary.

## 5. Call agenda

A 20–30 minute introductory call can follow this order:

- developer’s priority markets and buyer geographies;
- projects and inventory suitable for external agencies;
- current agency model and prohibited activities;
- lead registration, protection, duplicate-lead handling and reporting;
- commission event, payout timing, taxes and required documents;
- payment plans and materials available for translation or redistribution;
- marketing approvals and brand-use rules;
- technical delivery: portal, feed, spreadsheet or agreed update cadence;
- pilot project, owner on each side and next written step.

Record answers as facts with source or meeting date. Mark unresolved items as 'to verify'.

## 6. Developer onboarding checklist

### A. Identity and authority

- [ ] legal name and trading brand;
- [ ] official website and project URLs;
- [ ] jurisdiction and relevant registration details;
- [ ] authorised signatory / partnership contact;
- [ ] verification source and date;
- [ ] ownership or sales authority for each submitted project is documented.

### B. Commercial terms

- [ ] agency agreement or standard partnership terms;
- [ ] commission schedule;
- [ ] commission basis and triggering event;
- [ ] payout timing and required invoice / tax documents;
- [ ] currency, withholding and bank-payment requirements;
- [ ] rules for sub-agents or distributed agency networks;
- [ ] written confirmation of any special network terms.

### C. Lead protection

- [ ] registration channel and required fields;
- [ ] protection period;
- [ ] duplicate lead rules;
- [ ] definition of a qualified / accepted lead;
- [ ] status updates and escalation path;
- [ ] rules for direct enquiries from a registered buyer;
- [ ] permitted agency and platform representation.

### D. Inventory and content

- [ ] project list, location and status;
- [ ] current inventory or availability method;
- [ ] price list and validity date;
- [ ] unit types, plans and specifications;
- [ ] payment plans;
- [ ] brochures, images, video and brand guidelines;
- [ ] translation / redistribution permission;
- [ ] update owner and update cadence.

### E. Legal, compliance and operations

- [ ] permitted countries and buyer profiles;
- [ ] advertising restrictions;
- [ ] applicable licensing requirements;
- [ ] data-protection requirements;
- [ ] KYC/AML or source-of-funds requirements where relevant;
- [ ] payment instructions and buyer-document requirements;
- [ ] complaint and incident contact;
- [ ] written approval of final commercial and marketing materials.

A checked box means “documented and reviewed”, not merely “claimed on a website”.

## 7. Required data record

Store one row per developer-project relationship using the existing library schema:

| Field | Required treatment |
|---|---|
| developer_brand / legal_name | copy from official or agreement source |
| country / region | verify against official source |
| website / projects / districts | official URL and checked date |
| sales_email / sales_phone / partner_contact | publish only if source confirms it |
| agency_program | confirmed, probable, not_disclosed |
| published_agent_commission | exact public statement or not_disclosed |
| commission_source | URL, agreement, or meeting note |
| lead_registration | confirmed mechanics or not_disclosed |
| payment_plans | source and validity date |
| broker_portal | confirmed / not found / not disclosed |
| direct_agreement_status | known, unknown, existing |
| existing_wegc_relation | confirmed internal record or unknown |
| priority | reasoned A/B/C with evidence |
| source_urls | every external fact gets a source |
| last_verified | ISO date |
| verification_notes | facts, gaps and next action |

For outreach queue, additionally store:

queue_id, company_name, project, market, contact_name, contact_role, contact_email, source_url, source_checked_date, fit_segment, priority, personalisation_fact, last_touch_at, next_touch_at, status, owner, opt_out, notes

Allowed status values: research, ready_for_review, approved_to_send, sent, replied, meeting, docs_requested, onboarding, live, nurture, do_not_contact.

## 8. Qualification and KPI fields

Track operational outcomes without inventing targets:

- sourced developers;
- verified developer records;
- verified project records;
- records with named partnership contact;
- records with documented agency terms;
- records with documented commission schedule;
- records with documented lead-registration rules;
- outreach records approved for sending;
- messages sent;
- delivery / bounce status;
- replies;
- positive replies;
- calls booked;
- data rooms or terms received;
- agreements under review;
- projects approved;
- projects live in catalogue;
- registered leads by developer;
- accepted leads;
- duplicate / rejected leads;
- bookings;
- completed transactions;
- developer commission received;
- agency payout status;
- time from first contact to terms;
- time from terms to onboarding;
- reason for no-fit / loss;
- source and last-verified date for every factual claim.

Use rates only after the underlying counts exist. Do not publish network-size or demand claims based on outreach volume.

## 9. Internal review gate before sending

A record is approved_to_send only when:

- company and recipient identity are verified;
- source URL and checked date are present;
- the recipient role is relevant or referral path is explicit;
- first line contains a sourced, truthful personalisation;
- no unsupported network number, commission, client volume or result is included;
- the email uses the current approved company identity;
- any link has been reviewed;
- opt-out handling is available.

Mass sending is out of scope for this pack. Use small, manually reviewed batches after owner approval.

## 10. Sources and decision basis

This pack follows the project bible:

- README — product, two-sided model and accepted decisions (../README.md)
- 09 — existing outreach drafts (../09-outreach-templates.md)
- 03 — go-to-market and developer funnel (../03-go-to-market.md)
- 05 — payments, contracts and legal boundaries (../05-payments-legal.md)
- Competitor growth playbook (../research/competitor-growth-playbook.md)
- Data standard (../data/README.md)

External developer facts must be added only from the developer’s official site, official partner page, official registry, signed terms, or a dated meeting record. Public competitor claims remain claims of the source until independently verified.
