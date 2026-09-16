# МИРА — Russia Launch-100 status

Дата: 2026-09-16

## Текущий результат

Сформирован первый **source-backed cohort на 100 уникальных российских agency organizations** для launch QA.

Он хранится двумя lossless batch-файлами:

- `russia-launch-50-seed.csv` — ranks 1–50;
- `russia-launch-50-batch-02.csv` — ranks 51–100.

Это **не 100 outreach-ready контактов** и не «100 полностью verified partnership contacts».

Текущий статус означает:

- организация дедуплицирована внутри launch cohort по рабочей ручной проверке;
- есть first-party/official source из ранее собранного source-backed слоя;
- branch-level строки не должны считаться отдельной компанией без отдельного коммерческого основания;
- прямой owner/commercial/partnership contact ещё требуется для значительной части cohort.

## Live contact QA

Отдельный файл `russia-contact-qa-batch-01.csv` содержит первый свежий live-QA по приоритетным компаниям на 2026-09-16.

Проверены public routes / role signals для:

- ИНКОМ-Недвижимость;
- Метриум;
- Point Estate;
- АЯКС;
- Высоцкий Эстейт;
- ЖИЛФОНД.

Важно: general phone/email или office contact не повышается автоматически до `partnership_contact_verified`.

## Следующий quality gate

Launch-100 считается готовым к ручному outreach только после того, как для каждой priority A/B строки заполнены по возможности:

1. active company / official domain check;
2. parent-brand / branch resolution;
3. public phone/email;
4. named owner / commercial / partnership route;
5. new-build / investment / premium signal;
6. current foreign-property activity;
7. final A/B priority;
8. `ready_for_review` status.

## Операционный приоритет

Сначала довести top 25–30 агентств до действительно actionable состояния, не ждать одновременной глубокой проверки всех 100.

После этого:

- расширить качественный cohort до Launch-200;
- не возвращаться к массовому raw discovery, пока direct-contact conversion rate не станет понятен;
- массовый outbound не отправлять без owner approval.
