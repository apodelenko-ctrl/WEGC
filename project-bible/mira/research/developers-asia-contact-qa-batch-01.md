# Developer contact QA — Bali, Vietnam, Dubai batch 01

**Проверено:** 2026-09-15 UTC  
**Поток:** active-markets contact QA  
**Файл данных:** `project-bible/mira/data/developers-asia-contact-qa-batch-01.csv`

## Результат

Добавлены 32 новые строки, которых не было в трёх исходных actionable CSV:

| Направление | Новые строки | Маршрут партнёрского контакта |
|---|---:|---:|
| Bali / Indonesia | 8 | 1 explicit agent route, 1 explicit partner route, 6 official contact routes |
| Vietnam | 12 | 12 official company contact routes; agency terms not published in reviewed source |
| Dubai / UAE | 12 | 2 broker registration, 4 channel/partner forms, 6 official contact routes |

## Качество источников

Каждая строка содержит first-party domain в `website`, `official_contact_url` и `source_urls`. В поле `contact_status` сохранено, какой маршрут был найден:

- `official_broker_registration` — официальная страница регистрации брокеров;
- `official_channel_partner_form` / `official_partner_form` — официальная форма для партнёров;
- `official_agent_route` — официальный сайт явно показывает маршрут для агентов;
- `official_contact_route` — официальный сайт компании или официальный контактный маршрут, без доказательства отдельной агентской программы.

Опубликованные контакты внесены только там, где они видны на официальной странице: Lyvin Properties (`sales@lyvinproperties.co`, `+62 811-3881-411`), Novo Development (`info@novoubud.com`), Wahi Group (`info@wahigroup.id`, `+62 813 5975 229`), AUM Development (`info@aumdevelopment.com`, `+971 4 346 9998`), Prestige One (`enquiries@prestigeone.ae`, `800 77378443`), Swank Development (`info@swankdevelopment.com`, `04 884 5648`), Avalon (`+62 812 4650 2783`) и Golden Woods (`+971 4 256 7646`).

Публичные агентские комиссии, lead protection, CRM/portal, payment plans и юридические contracting entities в этой волне не заполнялись без отдельного официального подтверждения и оставлены `unknown`.

## Источники прямых маршрутов

- Novo Development: https://novodevelopment.id/
- Lyvin Properties partner route: https://lyvinproperties.co/
- AUM broker registration: https://aumdevelopment.com/broker-registration/
- Prestige One broker registration: https://prestigeone.ae/broker-registration/
- The Luxe Developers channel partner: https://theluxedevelopers.com/become-a-channel-partner/
- Golden Woods channel partner: https://goldenwoodsuae.com/become-a-channel-partner/
- Swank Development broker registration: https://swankdevelopment.com/brokers-registration/
- Dar Al Aiham partner registration: https://www.daralaiham.com/register-as-partner
- Rabdan Developments partner route: https://rabdan.ae/partner
- Al Mizan broker-network route was reviewed but excluded from this developer batch because the page describes a broker network rather than a developer.

## Следующее действие

Ручная верификация contracting entity и ответственного sales / agency-relations человека по строкам с `official_contact_route`; затем запросить письменные условия агентской программы до переноса записи в `verified_partner_contact`.
