# Phuket supply map — pilot developer registry

**Проверено:** 2026-09-15. **Статус:** рабочая выборка для developer outreach и дальнейшей верификации.

## Что сохранено

`data/developers-phuket-pilot.csv` содержит 31 запись: 15 developer / branded-residence records с официальным сайтом и 16 кандидатов, обнаруженных в публичных каталогах. Кандидаты намеренно помечены `entity_type=candidate / requires verification`, `official_site_status=candidate`, `priority=C`; их нельзя считать подтверждёнными застройщиками и нельзя ставить в очередь контактов до независимой проверки юридического лица, официального сайта, актуального проекта и sales/agency contact.

В поле `projects` для подтверждённых записей указаны проекты, которые видны на официальном сайте либо уже присутствуют в инвентаризации WEGC. Если атрибуция проекта или роль стороны (developer, co-developer, brand/operator) неясна, это прямо отмечено в `notes`. Для `published_agent_commission`, `direct_agreement_status`, `sales_email`, `partner_contact` не заполнены догадки: `unknown` означает, что публичного подтверждения в текущем проходе нет.

## Подтверждённые записи для следующего шага

| Приоритет | Запись | Почему оставлена в пилоте | Что запросить у developer |
|---|---|---|---|
| A | Rhom Bho / THE TITLE | официальный news/site; большая представленная в WEGC линейка | developer agreement, lead registration, commission schedule, payment plans, broker materials |
| A | Botanica Luxury Villas | официальный сайт с портфелем Phuket | legal contracting entity, agency programme, inventory feed, commission |
| A | AssetWise | официальный корпоративный сайт; Phuket projects require project-level check | подтвердить роль в The Modeva и конкретный contracting entity |
| A | Origin Property | официальный корпоративный сайт и Phuket project footprint | sales/agency relations, registration rules, current inventory |
| A | Sansiri | официальная Phuket page | international sales / broker programme и контакт партнёрского отдела |
| A | Banyan Group Residences | официальный residence site и опубликованные контакты | developer vs brand/operator per project, referral/agency agreement |
| A | The Ozone Group Phuket | официальный сайт, legal/brand/contact опубликованы | agency programme, project sheets, commission and registration |
| B | Utopia; The Zero; Anchan; The ONE Group; Sunny Holding; Phuket9 | официальные домены подтверждают бренд и Phuket activity | legal entity, current projects, partner contact, terms |
| C | Bluepoint; SKHAI | проекты подтверждены официальными сайтами, но scope/scale ограничен | active inventory and willingness to join network |

## Источники и правила нормализации

Официальные источники, использованные для подтверждённых строк:

- https://thetitleresidence.com/news/ и https://title-phuket-official.com/en/ — Rhom Bho / THE TITLE;
- https://www.botanicaluxuryvilla.com/ — Botanica;
- https://www.assetwise.co.th/ — AssetWise;
- https://www.origin.co.th/ — Origin Property;
- https://www.sansiri.com/location/phuket-en/ — Sansiri Phuket;
- https://www.banyangroupresidences.com/ — Banyan Group Residences;
- https://utopia.co.th/ — Utopia Corporation;
- https://bluepointcondo.com/ и https://bluepoint.no/en/ — Thai Fareast / Bluepoint;
- https://www.ozonephuket.com/ — The Ozone Group Phuket;
- https://thezerophuket.com/ — The Zero Phuket;
- https://anchanvillas.com/ — Anchan Villas;
- https://theonephuket.com/ — The ONE Group;
- https://skhai.com/ — SKHAI;
- https://sunnyholding.com/development/ — Sunny Holding;
- https://phuket9.com/ — Phuket9.

Для discovery-кандидатов использованы публичные каталоги https://propertyscout.co.th/en/project/phuket/, https://houseviser.com/developers и https://thailand-real.estate/. Они служат только источниками очереди на проверку. Каталоги и агентские сайты не используются как доказательство опубликованной комиссии, договора или статуса официального developer.

`Wyndham Hotels & Resorts` и другие hospitality brands следует хранить отдельной ролью `operator / brand`, когда они встречаются в проекте: бренд отеля не равен юридическому застройщику. Аналогично `Laguna Property`, `Banyan Group Residences`, `Rhom Bho / THE TITLE` могут иметь разные роли на уровне конкретного проекта; перед outreach нужна project-level legal mapping.

## Следующая операция

1. Проверить 16 candidate records через официальный сайт и тайский DBD/документы проекта.
2. Для 15 подтверждённых строк провести отдельный контактный проход: sales email, phone, agency relations, lead registration, commission, payment plan и broker portal.
3. Сверить проекты CSV с `ru/wegc-catalog-data.js`, устранить дубликаты брендов и создать отдельный project-level файл, где developer, co-developer, brand и operator — разные поля.
