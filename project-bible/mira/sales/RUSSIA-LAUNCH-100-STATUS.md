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

На 2026-09-16 опубликованы пять live-QA batch-файлов:

- `russia-contact-qa-batch-01.csv` — 6 организаций;
- `russia-contact-qa-batch-02.csv` — 7 организаций;
- `russia-contact-qa-batch-03.csv` — 7 организаций;
- `russia-contact-qa-batch-04.csv` — 6 организаций;
- `russia-contact-qa-batch-05.csv` — 4 организации.

Итого **30 приоритетных организаций прошли отдельный свежий contact/role QA**.

Для owner review создан `russia-priority-20-review.csv` — первая консолидированная очередь из 20 компаний. Дополнительные 10 QA-accounts хранятся в batch-04/05 и должны войти в следующую consolidated priority queue после финального fit-scoring.

Сильные текущие route signals включают named owner / CEO / commercial / new-build contacts у Грановита, Визита, Орбиты 72, ЛЕДОН, Новосёла, Дома Недвижимости, ИНКОМ, ГОРОДОВ, АРЕВЕРА, Новых Домов, АВЕСТА-РИЭЛТ, Нового Города и Квартсервиса.

Важно: general phone/email или office contact не повышается автоматически до `partnership_contact_verified`. Статус отражает только то, что реально подтверждено источником: named role, general route, partner signal, office presence и т. д.

## Domain/entity QA

Создан `data/russia-domain-qa-corrections.csv`.

На текущем проходе выявлены как минимум три domain/entity conflict, которые запрещено замалчивать:

- Новосёл: launch seed `novosel.ru` vs live-QA `novosel99.ru`;
- СТАН: `stan-ufa.ru` vs `stanufa.ru`;
- Живем дома: `jivem-doma.ru` vs `jivemdoma.com`.

До entity resolution эти строки не переводятся в outreach-ready.

## Следующий quality gate

Launch-100 считается готовым к ручному outreach только после того, как для priority A/B строк заполнены по возможности:

1. active company / official domain check;
2. parent-brand / branch resolution;
3. public phone/email;
4. named owner / commercial / partnership route;
5. new-build / investment / premium signal;
6. current foreign-property activity;
7. final A/B priority;
8. `ready_for_review` status.

## Операционный приоритет

Первый milestone **top-30 live contact QA достигнут**.

Следующий шаг:

- сделать consolidated `Russia Priority-30`;
- выделить первые 10–15 действительно `ready_for_owner_review`;
- подготовить персонализированные manual outreach drafts без отправки;
- параллельно продолжить Phuket project normalization;
- затем расширять качественный cohort до Launch-200.

Массовый outbound не отправлять без owner approval.
