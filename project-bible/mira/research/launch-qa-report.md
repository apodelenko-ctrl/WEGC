# MIRA Launch QA Report

**Проверено:** 2026-09-15 UTC  
**Назначение:** контроль готовности данных и launch материалов перед ручным outreach.

## Executive status

| Поток | Строк | QA результат | Действие |
|---|---:|---|---|
| Россия master | 324 | `source_seeded`; 207 повторов по первому полю после нормализации; 25 строк без даты | дедуплицировать по нормализованному домену и подтвердить филиал/контакты |
| Беларусь/СНГ pilot | 88 | в файле присутствуют повторяющиеся записи по первому полю; source/date присутствуют | дедуплицировать по домену + стране, затем разделить verified/candidate |
| Пхукет TOP-20 | 20 | все строки имеют source/date; контактный tier и direct-contact поля доступны в audit | outreach только rows с `direct_contact_verified=yes` или ручной проверкой |
| Bali actionable | 20 | source/date заполнены; поля partnership/payment часто `unknown` | подтвердить agency relations и lead registration |
| Vietnam actionable | 24 | source/date заполнены; partnership/payment часто `unknown` | подтвердить agency relations и lead registration |
| Dubai actionable | 24 | source/date заполнены; partnership/payment часто `unknown` | подтвердить broker/partner route и contracting entity |

## Rules applied

- Запись считается source-backed только при наличии официального URL/источника.
- Наличие сайта само по себе не доказывает активность филиала, агентскую программу или прямой sales contact.
- `unknown` сохраняется до подтверждения и не превращается в факт.
- Generic phone/email не маркируются как partnership contact.
- Outreach не отправляется; QA только формирует очереди и следующие действия.

## Priority queue

1. Phuket TOP-20: сначала direct sales/partner contacts, затем official sales forms, затем generic contact как fallback.
2. Developer streams: строки с официальным agency/broker URL и подтверждённым email; после них — official contact form.
3. Russia: A/B rows with unique normalized domain; C branch prospects остаются в validation queue.
4. CIS: unique country+domain rows; candidate file не смешивать с verified.

## Blocking issues

- В России текущий master смешивает verified и source-seeded строки; заявлять 324 verified нельзя.
- В CIS pilot есть повторения по company field; нужна нормализация доменов и юридических сущностей.
- Для developers официальная контактная страница не всегда означает агентскую программу; partnership status требует ручного ответа/подтверждения.
- Trademark/domain clearance финалистов нейминга остаётся отдельной юридической проверкой.

## Launch gate

Материалы можно передавать на внутренний dry run после: (a) очистки дублей; (b) ручной проверки TOP-20 Phuket; (c) выбора 10–15 первых агентств с подтверждённым контактом; (d) проверки payment copy юристом/провайдером под конкретный маршрут.
