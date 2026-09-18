# Данные CLOUD → LOCAL — без пересылки ZIP владельцем

Этот индекс дополняет LOCAL-NEXT/задание MIRA-LOCAL-20260918-02. Он передаёт уже собранные данные и правила их выборочной интеграции, не публикует новые страны сам.

## Где читать

Репозиторий: apodelenko-ctrl/WEGC. Ветка обмена: mira/research-night-20260918.

- Неизменяемый ночной snapshot: `beb9707c8561c138c896b122c6776a217ee4b3f0`.
- Корень ночных файлов: `project-bible/mira/research/night-2026-09-18/`.
- Дневные уточнения: `project-bible/mira/research/day-2026-09-18/`.
- Последний прочитанный CLOUD snapshot перед записью этого задания: `234539023cb33b8cdbb307227fa79052645b5586`. Следующие дневные результаты могут быть новее: читать актуальный RESUME и фиксировать точный commit, не объявлять старый snapshot latest.

Для чтения достаточно fetch и git show; checkout/merge research-ветки не требуются. Например:

```sh
git fetch origin main mira/research-night-20260918
git show beb9707c8561c138c896b122c6776a217ee4b3f0:project-bible/mira/research/night-2026-09-18/vietnam-projects.json
git show origin/mira/research-night-20260918:project-bible/mira/research/day-2026-09-18/RESUME-STATE.json
```

При sparse checkout git show читает Git-объект без перезаписи рабочего дерева. Не задавать облачные команды с путями Mac: действовать в фактически активном репозитории LOCAL. Если Git-объект недоступен, зафиксировать ошибку; не заменять источники догадками.

## Проекты: 15 Вьетнам + 15 Черногория

Ночные исходные данные:

- [vietnam-projects.json](https://github.com/apodelenko-ctrl/WEGC/blob/beb9707c8561c138c896b122c6776a217ee4b3f0/project-bible/mira/research/night-2026-09-18/vietnam-projects.json)
- [montenegro-projects.json](https://github.com/apodelenko-ctrl/WEGC/blob/beb9707c8561c138c896b122c6776a217ee4b3f0/project-bible/mira/research/night-2026-09-18/montenegro-projects.json)
- [полная цепочка исследований и наблюдений](https://github.com/apodelenko-ctrl/WEGC/tree/beb9707c8561c138c896b122c6776a217ee4b3f0/project-bible/mira/research/night-2026-09-18)
- [явная карта всех 30 типов для интерфейса](./project-taxonomy-20260918.json) — вынесена из ранее проверенного owner-пакета; исходные propertyTypes не заменять.

Перед импортом учесть дневные дополнения:

1. [C02 — Waterpoint](../project-bible/mira/research/day-2026-09-18/results/C02-waterpoint-vietnam-closure.md).
2. [C03 — Heights, Merit, Porto Budva](../project-bible/mira/research/day-2026-09-18/results/C03-montenegro-heights-merit-porto-budva.md).
3. [C04 — Poljana, Kotor Bayview](../project-bible/mira/research/day-2026-09-18/results/C04-montenegro-poljana-kotor-bayview.md).
4. [TRANSFER-QA — исправления исходной передачи](../project-bible/mira/research/day-2026-09-18/TRANSFER-QA.md).

Ночной пакет содержал 24 complete-for-discovery / 6 partial. Последний прочитанный дневной RESUME рекомендует 27 / 3 после C03/C04; оставшиеся partial: Waterpoint, Merit Starlit, Porto Budva. Это качество discovery, не подтверждённый продавец/право продаж. Переносить изменения статуса только вместе с конкретными источниками и причиной из C-файлов; старые записи сохранять как provenance.

Поправка Lumi Hanoi: developerBrand = CapitaLand Development, developerGroup = CapitaLand Group. Не сохранять старое значение CapitaLand Investment. Основание и ссылка зафиксированы в TRANSFER-QA. legalSeller остаётся неизвестным.

Сохранять stable ID, name, district, developerBrand как family, propertyTypes и primary/agency sources. kindProposed — группа отображения, не правовой титул. Поддержать mixed и hotel в фильтрах/схеме явно. Новые карточки остаются research_only, commerciallyEnabled=false; image отсутствует до разрешённого файла либо ясно подписанной тематической обложки. Цены, комиссии, доходность, сроки/наличие и договоры не додумывать.

## Агентства: 50 Россия + 30 Беларусь

Все файлы ниже лежат в NIGHT root неизменяемого snapshot.

### Россия

- `russia-agencies.csv` — компактный индекс 50 stable IDs/статусов.
- `03-russia-a.csv` — подробности 29 записей.
- `04-russia-b.csv` — подробности 21 записи.
- соответствующие JSON/MD — контекст источников и проверки.

Сделать строгий join подробностей с компактным индексом по id; проверять один-к-одному и 50 уникальных id. Не объединять по одному совпадению названия и не превращать филиал в независимое юрлицо. Поле источника сохранить.

### Беларусь — важное исправление

**Не импортировать исторический подробный `05-belarus-agencies.csv`: 29 записей и 14 строк со сдвинутыми колонками.**

Авторитетная структурная основа передачи: `05-belarus-agencies.json`, массив `records` (30). Сопоставить по id с компактным `belarus-agencies.csv` (30). Так восстанавливается и `by-eksklyuziv-group`, отсутствовавший в повреждённом CSV. Не угадывать поля по запятым.

Точные переименования при нормализации:

| Из исходного JSON | Поле импорта |
|---|---|
| corporate_general_contact_page | contact_page |
| published_general_email | general_email |
| published_general_phone | general_phone |

Сохранить остальные факты, source_urls, legal_name, source_status и null. `owner_review` брать из compact ID-join. Из того же JSON перенести `regulatory_holds_not_counted` отдельным карантинным списком, не в 30 кандидатов. Запись в профессиональном каталоге не является актуальной проверкой лицензии. Отдельные точные корпоративные маршруты пока отсутствуют; не строить email из домена.

Сделать новые JSON/CSV через сериализатор и csv.DictWriter, проверить прямоугольность, count, uniqueness, ID-set и отсутствие None-ключей. Сохранить provenance исправления. Старый оригинал — только evidence.

Оба реестра: candidate/research, `outreach_status=not_authorized`; не импортировать как активные агентства, подписчиков или готовый audience маркетингового провайдера. Сверить с новейшим локальным CRM/state: прежняя проверка точных доменов по 52 main CSV не заменяет поиск юрлиц, филиалов, переименований и неопубликованной базы.

### Уже подготовленный отбор и тексты — не писать заново

- [C08 — шесть кандидатов РФ](../project-bible/mira/research/day-2026-09-18/results/C08-russia-six-review-candidates.md).
- [C09 — шесть кандидатов Беларуси](../project-bible/mira/research/day-2026-09-18/results/C09-belarus-six-review-candidates.md).
- [C10 — пакет 12 кандидатов для staging](../project-bible/mira/research/day-2026-09-18/results/C10-agency-review-pack.json), [правила](../project-bible/mira/research/day-2026-09-18/results/C10-owner-review-and-crm-staging.md).
- [C11 — демонстрация и предложение](../project-bible/mira/research/day-2026-09-18/results/C11-current-product-demo-and-one-pager.md).

## Медиа и первое предложение Пхукета

Не собирать подборку Бали/Дубая с нуля и не переустанавливать опубликованные 30 карточек.

- Baseline main: `project-bible/mira/research/bali-dubai-2026-09-17/MEDIA-GAPS.md` и `media-review.json`.
- [C05 — Бали: точные источники/правообладатели](../project-bible/mira/research/day-2026-09-18/results/C05-bali-media-rights-routes.md).
- [C06 — Дубай: точные источники/правообладатели](../project-bible/mira/research/day-2026-09-18/results/C06-dubai-media-rights-routes.md).
- [C07 — матрица запросов и задание на собственную съёмку](../project-bible/mira/research/day-2026-09-18/results/C07-permission-matrix-phuket-field-photo-brief.md).
- [C12 — VIVI: пробелы первого рабочего проекта](../project-bible/mira/research/day-2026-09-18/results/C12-phuket-vivi-commercial-evidence-gap.md).
- [C13 — выставочный QR и следующий шаг](../project-bible/mira/research/day-2026-09-18/results/C13-expo-qr-to-next-step-review.md).

Источник картинки, точное соответствие проекта, визуальный просмотр и разрешение публикации — отдельные поля. Новых publication-approved project images по прочитанной дневной сводке ноль. Собственная съёмка/запросы не выполнены фактом создания задания. Приватные условия и оригиналы договоров не копировать в этот inbox.

## Существующее mail/CRM-задание

MIRA-MKT-20260918-01 остаётся в QUEUE. Его материалы M02/M04/M05/M06 и C10/C11 уже доступны через README; сохранять текущую реализацию и не повторять выбор ПО. Эта передача не создаёт дополнительного разрешения на закупки, внешние письма, отправку форм или загрузку кандидатов в рассылку.

## Контрольные суммы ночных исходников (SHA-256)

```text
e4ee5b5255fa4a9d82160416e5acfd0422618fa5bb2faf942e6b62bccccb61c0  vietnam-projects.json
e6c1d2b20804d74a8a8d9aea4067d31aba9d46deea25f5ad395de2f12786b76a  montenegro-projects.json
fb51f56f6f085420a67d96518d8f6cb0ac1393e017e3263d5b895a4af4bc42f3  03-russia-a.csv
305bbda4df04ec0b2b91d24f09c9790c92b31cd87dfccdd5a3fa2437add3358f  04-russia-b.csv
faffd94a95e435c6d49b2dec96b63d0a3305af095c1326b387d9443e50d02b77  russia-agencies.csv
c74cb6ddf445592d12da414b5bdd409afd8d8faf572f835ad2a2241c7d1411d4  belarus-agencies.csv
2056743ce68fc67da2f3e410d085d5f3524be57de985484fd49653ee4b3965be  05-belarus-agencies.json
```

Суммы вычислены по файлам в ранее переданном архиве и относятся только к указанному неизменяемому NIGHT snapshot, не к дневным поправкам. Статус новой интеграции/build/browser/live неизвестен до отчёта LOCAL. ZIP из чата — удобная прежняя копия, не обязательная точка доступа и не причина повторно просить файлы у владельца.
