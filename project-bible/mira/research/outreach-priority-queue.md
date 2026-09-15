# MIRA Outreach Priority Queue (QA-generated)

Дата проверки: 2026-09-15 UTC. Сообщения не отправлялись.

## Порядок работы

| Приоритет | Сегмент | Источник очереди | Критерий допуска | Следующий шаг |
|---|---|---|---|---|
| P0 | Phuket developers | `data/phuket-top20-outreach.csv` | `verification_status` подтверждён и есть sales/partner URL или прямой контакт | ручная проверка контакта, затем персонализировать письмо |
| P1 | Bali/Vietnam/Dubai | соответствующие `*-actionable.csv` | официальный contact URL + agency/broker signal | проверить lead registration, commission и payment terms |
| P1 | Russian agencies | `data/agencies-russia-pilot.csv` | уникальный домен, grade A/B, source и checked date | подтвердить foreign-property practice и partner owner |
| P2 | CIS agencies | `data/agencies-cis-pilot.csv` | уникальная пара country+domain, official source | сверить юрлицо и прямой партнёрский контакт |
| Hold | candidates/seeds | `data/agencies-cis-candidates.csv`, `russia-agencies-seed-01.csv` | нет полного evidence | не включать в outbound |

## Message assets

- Агент: `09-outreach-templates.md` и `sales/outreach-queue-template.csv`.
- Застройщик: `sales/developer-acquisition-pack.md`.
- Onboarding: `product/onboarding-scenarios-3.md`.

Каждая отправка должна иметь source URL, дату проверки, owner сегмента и opt-out поле. До ручного разрешения владельца сообщения не отправляются.
