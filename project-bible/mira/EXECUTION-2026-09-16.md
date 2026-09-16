# МИРА — execution checkpoint 2026-09-16

Статус: активный launch-prep checkpoint. Массовый outreach не отправлялся.

## Решение владельца

**МИРА утверждено как финальный публичный бренд продукта.** Нейминг как продуктовый поток закрыт. IP/trademark/domain clearance остаётся отдельной юридико-брендовой задачей и не означает, что нужно продолжать генерировать альтернативные названия.

Зафиксировано в `08-decisions-log.md`; Issue #6 закрыт.

## Выполнено утром

### 1. Phuket developer normalization

Создан `data/phuket-developer-master.csv`.

Текущий v1 содержит **40 deduplicated developer / counterparty / branded-residence groups** на основе ранее собранного TOP-60 contact QA.

Ключевое исправление: project-level строки больше не считаются отдельными developers. Схлопнуты, в частности:

- THE TITLE projects → Rhom Bho Property / THE TITLE;
- Botanica Foresta / Hythe → Botanica / AAP;
- Origin project rows → Origin Property PCL;
- Sansiri project rows → Sansiri PCL;
- Laguna project rows → Laguna/Banyan operational group;
- Ozone projects → The Ozone Group Phuket;
- Anchan projects → Pearl Island Property / Anchan;
- The Zero projects → Zero Developments;
- Utopia projects → Utopia Corporation.

Branded-residence/operator records, где developer / seller не подтверждён, переведены в `hold_entity_resolution`.

### 2. Phuket developer outreach

Создан `sales/phuket-developer-outreach-queue.csv` на **20 уникальных developer groups**.

Первые P0/P1 маршруты включают official agent clubs / international-agent pages / direct sales routes там, где они уже подтверждены первичным источником. Очередь не отправлена наружу; следующий gate — manual owner review и named partner contact.

### 3. Russia launch seed

Создан `sales/russia-launch-50-seed.csv` — **50 уникальных российских agency organizations** для ручного launch QA.

Файл сознательно называется `seed`, а не `outreach_ready`. Для каждой строки сохранён официальный источник; публичные e-mail/phone указаны только там, где они уже присутствовали в source-backed dataset.

Следующий gate:

- direct owner/commercial/partnership contact;
- foreign-property / new-build / investment signal;
- final A/B grading;
- убрать network/branch duplication;
- расширить до `Russia Launch-200`.

### 4. Pilot Pack

Создан `sales/MIRA-PILOT-PACK.md`.

Внутри:

- agency proposition;
- 90/10 wording с ограничениями;
- шесть шагов сделки;
- payment messaging;
- MVP cabinet scope;
- первая Phuket developer queue;
- pilot gates;
- KPI от qualified agency до settlement.

### 5. Первый webinar

Создан `research/mira-first-webinar.md`.

Основной тезис:

**Не передавайте клиента — откройте зарубежное направление внутри своего агентства.**

Вебинар строится как B2B onboarding/funnel, а не как обычная презентация объектов Пхукета.

### 6. Landing copy brand lock

`product/landing-v2-copy.md` обновлён: МИРА больше не обозначается как временное имя. Отдельно сохранено ограничение, что до IP clearance нельзя заявлять юридическую эксклюзивность/регистрацию товарного знака или свободу домена.

## Текущий launch funnel

### Russia

- raw/source-backed pool: значительно больше 200 строк;
- current manually curated launch seed: **50 unique organizations**;
- target next gate: **Launch-200**;
- outreach: disabled pending contact QA and owner approval.

### Phuket

- old internal project backbone: ~618 project records;
- current developer master v1: **40 unique developer/counterparty/branded-residence groups from the first normalized contact layer**;
- current developer outreach queue: **20 unique groups**;
- remaining work: process the full ~618-project backbone into complete project→developer family mapping, not only TOP-60.

## Следующие активные блоки

1. Russia Launch-50 → verify contacts → expand to Launch-100 → Launch-200.
2. Full Phuket ~618 project rows → `phuket-project-master.csv` + complete developer-family map.
3. For Phuket P0 developers: resolve named agency-relations owner, agreement entity, lead registration/protection, commission schedule, payout timing and active inventory.
4. Assemble first agency-facing one-page/PDF-ready version from `MIRA-PILOT-PACK.md`.
5. Convert webinar outline into first event landing/invite sequence and post-webinar starter kit.
6. Continue CIS / Bali / Vietnam / Dubai only after P0 Russia/Phuket cleanup, unless an independent stream can proceed without reducing QA quality.

## Запрещено без отдельного owner approval

- массовый e-mail outreach;
- массовые Telegram/WhatsApp сообщения;
- отправка forms developers/agencies;
- публичное обещание конкретной комиссии там, где нет подтверждённого developer agreement;
- публичное раскрытие внутренних payment routes;
- утверждение, что бренд МИРА юридически зарегистрирован/эксклюзивен до IP clearance.
