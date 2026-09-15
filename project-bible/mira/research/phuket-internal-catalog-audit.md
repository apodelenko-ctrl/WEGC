# Phuket internal catalogue audit

Дата: 2026-09-16.

## Что уже есть внутри WEGC

Главный внутренний источник — `ru/wegc-catalog-data.js`. Это сгенерированный проектный каталог Пхукета, который используется страницей `ru/katalog.html`.

По структуре файла массив `WEGC_CATALOG` содержит 618 проектных записей: 11 direct-проектов с паспортами WEGC и большой market-слой. Это значительно богаче текущей вручную собранной developer-базы МИРА.

Генератор `scripts/build-phuket-index.py` показывает происхождение базы:

- direct list;
- вручную добавленные важные English project names;
- большой ранее собранный массив InDreams;
- нормализация района, типа проекта и части developers;
- официальный image layer через `covers-map.json` / `galleries-map.json`.

## Уже распознаваемые developer groups в генераторе

Rhom Bho / The Title; Botanica Luxury Phuket; Laguna / Banyan; Origin PCL; Sansiri; The Zero; Mouana; Wyndham; VIP Grand; The Ozone; Mono; Unique; Aileen; Anchan; AssetWise; Naturale.

Это не полный список developer groups в 618 проектах. Любой проект, который не попал под эти regex-правила, сейчас получает `developer = по запросу` даже если название проекта позволяет определить группу.

## Важное следствие

Нельзя строить Phuket supply map с нуля только из внешнего поиска. Сначала нужно пройти собственные 618 project rows, сгруппировать их в developer families, затем уже добирать для каждой группы legal entity и sales / agency relations / broker partnership contacts.

Текущий `phuket-top60-outreach.csv` также нельзя трактовать как 60 уникальных застройщиков: часть строк — проекты уже учтённых developer groups и branded-residence/operator records. Для подписания договоров единица учёта должна быть `unique developer / contracting counterparty`, а проекты должны находиться внутри его карточки.

## Новая схема обработки Пхукета

1. Internal catalogue extraction: 618 проектов.
2. Alias clustering: project -> developer family.
3. Separate active new-build/off-plan from resale/legacy/hospitality-only records.
4. Deduplicate by developer group and legal counterparty.
5. Enrich each retained developer with official site, legal entity, broker route, lead registration, commission evidence and current inventory.
6. Rank unique developers into A/B/C outreach tiers.
7. Keep project-level table separately for future marketplace inventory.

## Приоритет

Использовать внутреннюю WEGC базу как discovery backbone для Пхукета. Внешний research должен не заменять её, а подтверждать developer identity, текущую активность, проекты и partnership contacts.
