# МИРА — Phuket project → developer normalization rules

Дата: 2026-09-16

Цель: превратить существующий WEGC project catalog (~618 project rows) в две раздельные сущности:

1. `phuket-project-master.csv` — одна строка = один проект;
2. `phuket-developer-master.csv` — одна строка = один developer / contracting / commercial group.

## Главный принцип

**Project name ≠ developer ≠ brand/operator ≠ legal seller.**

Нельзя считать отдельными застройщиками:

- The Title Heritage, Legendary, Serenity и другие THE TITLE проекты;
- Botanica Foresta, Hythe, Forestique и другие Botanica проекты;
- отдельные Origin / SO Origin проекты;
- отдельные Sansiri / The Base проекты;
- Laguna branded projects;
- Ozone project names;
- Anchan project names;
- The Zero project names.

Они должны сначала схлопываться в `developer_family`, а уже потом для каждого проекта проверяется точный `contracting_entity`.

## Поля project master

Минимально:

- `project_id`
- `slug`
- `project_name`
- `district`
- `kind`
- `source_layer` (`direct`, `market`, `legacy`, `candidate`)
- `raw_developer`
- `developer_family`
- `brand_operator`
- `contracting_entity`
- `developer_mapping_confidence`
- `active_sales_status`
- `official_project_url`
- `internal_url`
- `inventory_status`
- `last_verified`
- `notes`

## Поля developer master

Минимально:

- `developer_id`
- `developer_group`
- `legal_name`
- `parent_group`
- `entity_type`
- `official_website`
- `agency_relations_route`
- `named_partner_contact`
- `commission_evidence`
- `lead_registration_evidence`
- `lead_protection_evidence`
- `payout_evidence`
- `agreement_status_with_mira`
- `priority`
- `last_verified`

## Mapping confidence

### high

Есть прямое внутреннее developer attribution или однозначный бренд-prefix + подтверждённая developer family.

Примеры:

- `The Title ...` → Rhom Bho / THE TITLE;
- `Botanica ...` → Botanica / AAP;
- `SO Origin ...` / Origin → Origin Property;
- `The Base ...` → Sansiri;
- `The Zero ...` → Zero Developments.

Даже при `high` exact `contracting_entity` может оставаться неизвестным.

### medium

Внутренний generator распознаёт developer family, но юридическая/коммерческая структура ещё не подтверждена первичным источником.

Примеры: Mouana, VIP, Mono, Unique, Aileen, Naturale.

### hold_entity_resolution

Есть branded-residence/operator signal, но нельзя безопасно считать бренд юридическим developer/seller.

Примеры: Marriott-, Rosewood-, Standard-, Wyndham-branded residences, Anantara/Minor-branded projects до проверки seller entity.

## Alias map

Использовать `data/phuket-developer-alias-map-v1.csv` как первый нормализатор.

Он хранит только **group mapping**. Он не заменяет проверку legal seller.

## Что делать с `developer = по запросу`

Не оставлять строку автоматически неизвестной.

Pipeline:

1. проверить project name против alias/prefix rules;
2. проверить `cloudflare-worker/wegc-kb.js`;
3. проверить `scripts/build-phuket-index.py` EXTRA_EN / developer regex;
4. проверить project passport / internal URL;
5. если developer family всё ещё не определён — внешний official-source research;
6. если остаётся неопределённым — `needs_entity_resolution`, без догадки.

## Active vs legacy

Проект не должен попадать в active supply только потому, что он есть в старом каталоге.

Разделять:

- `active_offplan`
- `active_ready`
- `sold_out_or_closed`
- `legacy_unknown`
- `resale_only`
- `hospitality_only`
- `needs_manual`

До подтверждения использовать `needs_manual`, а не придумывать текущий sales status.

## Conflict handling

Если разные внутренние файлы приписывают проект разным developers:

1. записать конфликт в `notes`;
2. не перезаписывать молча;
3. выбрать canonical mapping только после official-source verification;
4. сохранить старый raw attribution в `raw_developer`.

Известный пример для контроля QA: The Modeva в текущем generator относится к AssetWise; старые файлы местами содержали другую атрибуцию. Canonical mapping должен опираться на подтверждённый текущий источник.

## Output gate

`phuket-developer-master.csv` нельзя считать завершённым, пока:

- все project rows получили `developer_family` или explicit `needs_entity_resolution`;
- branded operator не смешан с seller;
- project duplicates схлопнуты;
- direct agreement status хранится отдельно от public broker-program evidence;
- у P0 developer groups есть хотя бы confirmed official route или explicit blocker.

## Следующий технический шаг

Прогнать полный WEGC catalog через alias rules и получить первый `phuket-project-master-v1.csv`. После этого агрегировать developer counts и проверить группы с наибольшим числом `unknown / needs_entity_resolution`.
