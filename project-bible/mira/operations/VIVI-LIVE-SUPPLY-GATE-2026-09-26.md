# VIVI — первый live-supply gate МИРА

Проверено26 сентября 2026. VIVI остаётся первым проектом для сценария «агентство спрашивает → МИРА запрашивает The Title → получает текущий ответ → отвечает агентству».

## Что доказано

- официальный проект VIVI активен как discovery entry; сайт даёт gallery, floor plan и progress;
- существующая WET/The Title relationship и история VIVI transaction подтверждены санитарными private-evidence записями;
- LOCAL зафиксировал24.09 запрос в существующем треде по материалам, availability, партнёрской модели, регистрации и защите;
- public MIRA card честно показывает availability/price/terms «по запросу».

## Что не доказано

Текущие юниты, их цены/payment plans, exact seller, current agreement coverage, commission, registration/protection, право downstream agency и media scope. Маркетинговый label, старый договор или прошлый VIVI transaction это не заменяют.

## Рабочее правило

Каждый запрос агентства создаёт отдельный developer request. Ответ принимается только прямо от застройщика и только для этого request. Он может законно сообщать none_available; система не заставляет придумывать вариант. Старый response не переиспользуется как новый inventory. Регистрация клиента закрыта, пока developer acknowledgement и все current commercial controls не подтверждены.

## Operator handoff

1. Не отправлять повторный introduction — использовать тред24.09.
2. Сохранить direct response в private system, без Git/публичных контактов.
3. Заполнить private case по структуре package и выполнить python vivi_gate.py PRIVATE-CASE.json.
4. Показать Артёму получателя, ответ/quote, attachments и proposed agency reply.
5. Только после одобрения отправить ответ агентству; mail-draft/open не считать отправкой.

Public template сейчас проходит validator с безопасным HOLD: response/commercial/registration=false, errors0, семь mutable controls missing. Package: `CLOUD-INBOX/packages/MIRA-VIVI-LIVE-GATE-20260926-01`.
