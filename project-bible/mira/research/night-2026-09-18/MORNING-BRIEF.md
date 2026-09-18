# MIRA — утренний отчёт ночной исследовательской смены

Проверено: **18 сентября 2026, 08:02 Asia/Bangkok**.

## Итог ночи

Ночной research/data lane завершил все запланированные блоки и подготовил пакет для локального Codex. Это **не публикация и не разрешение на outreach**.

Фактически сохранено и сведено:

- **Вьетнам: 15 проектов** — 14 `complete_for_discovery`, 1 `partial` (`Waterpoint`).
- **Черногория: 15 проектов** — 10 `complete_for_discovery`, 5 `partial`.
- **Россия: 50 агентств-кандидатов** — 50 уникальных night-ID и 50 непустых уникальных доменов в компактном слое; 6 строк отмечены `owner_review=yes`.
- **Беларусь: 30 агентств-кандидатов** — 30 уникальных night-ID; 6 строк отмечены `owner_review=yes`; 5 организаций с текущими официальными уведомлениями о приостановлении лицензий не включены в 30.
- **Новые publication-approved project images: 0**.

Машинная проверка `VALIDATION.json` подтвердила парсинг, количества, уникальность ID/доменов и закрытые коммерческие/outreach-гейты. Она **не** доказывает юридическую уникальность всех компаний, seller appointment, права на медиа, актуальный inventory или production/browser acceptance.

## Проекты

### Вьетнам

14 из 15 строк закрыты для discovery-этапа. Единственный partial — `Waterpoint`: first-party identity сильная, но конкретная русскоязычная/русскоговорящая агентская публикация exact-project ночью не установлена.

Итоговый файл: `vietnam-projects.json`.

### Черногория

10 из 15 строк закрыты для discovery-этапа. Открыты 5: `Heights`, `Merit Starlit Hotel & Residence`, `Porto Budva`, `Poljana Olive Homes Pool Residence`, `Kotor Bayview Residence`.

Старые citizenship-by-investment / residence / return claims не переносились в MIRA и остаются карантинированными.

Итоговый файл: `montenegro-projects.json`.

## Агентства

### Россия

Итоговый слой: **50 research candidates** после repository-level дедупликации. Owner-review shortlist:

- AFLAT — Владивосток;
- Welcome — Ставрополь;
- Формула — Тюмень;
- Агентство на Ярославской / HOUSE GROUP — Чебоксары;
- БСН Недвижимость — Брянск;
- РИЭЛ-МАКС — Брянск.

Это shortlist для оценки владельцем, **не разрешение на контакт**. Отдельные holds: Аурум — entity metadata; Виктори — content quality; Good House — first-party recovery incomplete.

Итоговый файл: `russia-agencies.csv`; подробности остаются в `03-russia-a.*` и `04-russia-b.*`.

### Беларусь

Итоговый слой: **30 research candidates**. Owner-review shortlist:

- Абсолют Недвижимость — Минск;
- Центр недвижимости 24 на 7 — Борисов / Минская область;
- Сектор недвижимости Основа — Гомель;
- Гарант успеха — Брест;
- Агентство Уют и К — Витебск;
- ПАКОДАН ЭСТЕЙТ — Гродно.

Часть белорусских строк намеренно остаётся Chamber/marketplace-backed без закрытого corporate-domain route. Пять компаний с текущими официальными licence-suspension notices исключены и не должны возвращаться без нового авторитетного подтверждения статуса.

Итоговый файл: `belarus-agencies.csv`; подробности — `05-belarus-agencies.*`.

## Медиа

Ночной проход не выдавал найденный URL за право публикации.

По пяти проблемным Bali/Dubai кейсам:

- **ERA by OXO** — найден current exact OXO page и exact-project asset URL; права не подтверждены;
- **Secana Beachtown** — exact gallery candidate визуально проверен; условия Mirah требуют разрешения для коммерческого/public reuse;
- **Mudon Al Ranim** — найдены две exact first-party gallery routes; условия Dubai Properties требуют лицензии/письменного разрешения;
- **One River Point** — current Ellington source re-match закрыт; direct asset для публикации не одобрен;
- **DAMAC Riverside** — изображения Riverside Views жёстко отделены как другой development.

Итог: **0 новых изображений, разрешённых к публикации**. Ночной `MEDIA-GAPS.md` — только delta поверх main baseline.

## Финальный публичный spot-check утром

Без начала новой подборки выполнена узкая проверка ранее сохранённых источников:

- Nam Long: `https://www.namlongvn.com/en/news/4175-nam-long-signs-with-17-strategic-agencies-for-waterpoint-township-ushering-in-a-new-era-for-western-real-estate-market/` — first-party Waterpoint source остаётся доступным; публикация от 18 марта 2025 называет 17 strategic distribution agencies. Это не закрывает русскоязычный agency-observation gap.
- AFLAT: `https://aflat.online/` — текущий first-party сайт по-прежнему показывает отдельный раздел/сервис по недвижимости Таиланда; остаётся owner-review signal, не outreach permission.
- Абсолют Недвижимость: `https://aan.by/contacts/` — текущая корпоративная contact page доступна; остаётся owner-review signal, не outreach permission.

Счётчики пакета после spot-check **не менялись**.

## Пакет локальному Codex

Главная точка передачи: `LOCAL-AGENT-HANDOFF.md`.

Сводный пакет:

- `vietnam-projects.json`
- `montenegro-projects.json`
- `russia-agencies.csv`
- `belarus-agencies.csv`
- `source-observations.json`
- `MEDIA-GAPS.md`
- `VALIDATION.json`
- `LOCAL-AGENT-HANDOFF.md`

Рекомендуемая последовательность остаётся прежней:

1. Не прерывать текущий admin/release follow-up локального Codex.
2. Вьетнам/Черногорию интегрировать только в новой изолированной data-ветке после deterministic mapping `propertyTypes -> kind`.
3. При отсутствии лицензированных фото использовать явно обозначенные country/project covers, не выдавая их за фотографии объекта.
4. После интеграции прогнать тот же catalogue/build/routes/shortlist/back-navigation/mobile-desktop acceptance, что использовался для Bali/Dubai.
5. Все новые проектные строки оставить `research_only` и `commerciallyEnabled=false`.
6. Russia/Belarus сначала сравнить с самым свежим unpublished local CRM state локального агента.
7. Никаких сообщений/форм агентствам без отдельного owner approval.

## Текущее main-состояние, которое нельзя затереть этой веткой

На момент утреннего чтения `main` уже содержит PR #10, 648 public research records и исправления back-navigation. Последний записанный full release `35250357478` имеет **failing local browser stage**; его нельзя считать успешным до разбора логов и повторного полного acceptance. Ночная research-ветка этот production lane не изменяла.

## Граница результата

Исследовательская смена **не публикует боевой сайт**, не merge'ит ветку, не меняет Worker/Access/D1/DNS/права/воронки и не отправляет outreach. Пакет готов для **local integration review**, а не для автоматического production deploy.
