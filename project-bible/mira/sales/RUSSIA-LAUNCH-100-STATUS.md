# МИРА — Russia Launch-100 status

Дата: 2026-09-16

## Текущий результат

Сформирован первый **source-backed cohort на 100 уникальных российских agency organizations** для launch QA:

- `russia-launch-50-seed.csv` — ranks 1–50;
- `russia-launch-50-batch-02.csv` — ranks 51–100.

Это **не 100 outreach-ready контактов** и не «100 полностью verified partnership contacts».

## Live contact / role QA

На 2026-09-16 опубликованы семь отдельных QA batch-файлов:

- `russia-contact-qa-batch-01.csv` — 6 организаций;
- `russia-contact-qa-batch-02.csv` — 7;
- `russia-contact-qa-batch-03.csv` — 7;
- `russia-contact-qa-batch-04.csv` — 6;
- `russia-contact-qa-batch-05.csv` — 4;
- `russia-contact-qa-batch-06.csv` — 9;
- `russia-contact-qa-batch-07.csv` — 11.

Итого **50 уникальных приоритетных организаций прошли отдельный свежий contact / role / entity review**.

Это означает, что для половины Launch-100 уже есть новый слой evidence по текущему сайту, public contact route, named role, foreign-property signal или явный hold. General phone/email по-прежнему не повышается автоматически до `partnership_contact_verified`.

## Новая сегментация, выявленная QA

Один общий pitch для всех агентств теперь запрещён как рабочая модель.

QA уже выявил минимум следующие типы:

- `greenfield_overseas` — агентство с сильной локальной/new-build базой, но без подтверждённого зарубежного направления;
- `existing_foreign_property_desk` — уже продаёт зарубежную недвижимость;
- `existing_phuket_direction` — уже имеет Пхукет/Таиланд в продукте;
- `network_platform` — федеральная / franchise / network-модель, где нужен HQ-level pitch;
- `premium_investment` — премиальная/investment аудитория;
- `newbuild_regional` — сильная новостроечная региональная команда;
- `hold_entity_resolution` — нельзя трогать до разрешения домена/юрлица/роли.

Evidence-backed примеры:

- `Диал` — отдельный директор по развитию / зарубежной недвижимости и существующая partner-mediated foreign-property модель;
- `Квартирант Плюс` — текущий официальный сайт прямо предлагает продажу недвижимости на Пхукете и публикует named CEO / sales leadership;
- `Панорама недвижимости` — текущий официальный сайт содержит направление «Недвижимость в Турции»;
- `Городской Риэлторский Центр` — официальный named partner/development leadership route;
- `Центр недвижимости` Тюмень — named leadership route + developer partner/new-build layer.

Для этих групп персонализация должна отличаться: агентству с уже работающей зарубежкой нельзя отправлять текст «откройте зарубежное направление с нуля».

## Owner-review assets

- `russia-priority-30-review.csv` — 30 unique priority organizations;
- `russia-wave-01-owner-review.csv` — первая сегментированная очередь на 12 компаний;
- `russia-wave-01-personalized-drafts.md` — персонализированные черновики первой ручной волны;
- все внешние отправки остаются `not_approved`.

## Domain/entity QA

`data/russia-domain-qa-corrections.csv` хранит конфликты доменов/юрлиц. Строки с unresolved conflict не переводятся в outreach-ready.

Дополнительно batch-07 удерживает в manual/hold режимах компании, где текущая marketplace presence видна, но first-party route или canonical entity недостаточно чисты.

## Следующий quality gate

Для priority A/B строки, готовой к owner review, по возможности должны быть заполнены:

1. active company / canonical official domain;
2. parent-brand / branch resolution;
3. public direct route;
4. named owner / commercial / partnership / foreign-property role;
5. new-build / investment / premium signal;
6. current foreign-property status;
7. правильный pitch segment;
8. `ready_for_owner_review` или честный hold status.

## Следующий operational step

Milestone **50/100 live-reviewed достигнут**.

Теперь приоритет:

- построить canonical segmentation register для всех Launch-100;
- довести 15–20 лучших до truly ready-for-owner-review;
- не отправлять outbound до owner approval;
- параллельно продолжать полный Phuket project → developer → commercial-terms pipeline;
- после проверки качества direct-contact conversion расширять curated cohort к Launch-200.
