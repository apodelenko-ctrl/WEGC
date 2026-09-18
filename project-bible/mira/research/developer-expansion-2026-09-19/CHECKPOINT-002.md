# Developers B002 — source enrichment, not CRM import

## Обе базы B002 — 2026-09-18T19:19:34Z

CLOUD source HEAD `6bdc7cccf753df3ad886b14e137f489d70d8a3e3`; перед публикацией прочитан `73ca08fe1d0fdfbdb30d4c18f005cfff6f1e1ed3`. Новые WORK-STATUS/RESUME-STATE LOCAL сохранены, не перезаписаны.

- Агентства: **345 → 348** canonical provisional candidates (RU206/BY59/other83). +3 новых кандидата: Миони, Союз застройщиков, Аркаир (403/hold). Обогащены 3 прежних записи: Империя, Бюро Виктории Пуховой (возможный старый бренд), Рост-Риелт (альтернативный домен/timeout). Саратов **7/10** research-fit, осталось3; Миони commercial-led и ниже приоритета чистого residential. Это не независимая проверка юрлиц и не готовность к рассылке.
- Пухова/Новострой-Инвест: совпали ИП Пухова В.В. и опубликованный номер; возможный старый бренд сохранён как alias candidate, **новую организацию не добавляли**. Удалено существующих строк0.
- Застройщики: master **40 → 41** (+AAG Development/Naturale Cherng Talay). Свежие контакты **3 → 6** групп: добавлены The Zero, Phuket9 и AAG. Группы с email6/phone6/WhatsApp1/LINE1/broker portal1; это публичные маршруты, не активные договоры.
- Все618 project IDs сохранены. Primary group links3; inherited94; ambiguous5; unmatched family8; missing family507; non-residential exclusion1 (Andamanda, ID сохранён). Zero exact master alias исправлен, Nai Yang/Silhouette возможные дубли не слиты; Naturale Kamala не приписан AAG по одному названию.
- **23/23** registry tests PASS, в том числе запрет превращения источника в seller/contract approval, отсутствие произвольного merge, unknown metrics=null. CRM imports0, external sends0, production/deploy0.
- Официальная численность населения города не получена: страницы Росстата/Саратовстата недоступны. 47+13 городов остаются предварительным списком; city ≠ городской округ.
- LOCAL closeout по-прежнему 18:39:09UTC: T11/T12 получены, T14 prepared_not_migrated. Новый vault receipt19:02:44UTC: 13 корпоративных PDF сохранены приватно, это НЕ backup CRM или cloud runtime. Private crosswalk78/87 ↔ research348/master41 и фактическая передача кода+encrypted backup+отдельного ключа не подтверждены. Cloud restore/live acceptance pending; native counts не складываются с research.

Детали: [agency COUNTS](https://github.com/apodelenko-ctrl/WEGC/blob/mira/research-night-20260918/project-bible/mira/research/agency-expansion-2026-09-19/COUNTS.json), [developer metrics](https://github.com/apodelenko-ctrl/WEGC/blob/mira/research-night-20260918/project-bible/mira/research/developer-expansion-2026-09-19/metrics.json), [event](https://github.com/apodelenko-ctrl/WEGC/blob/mira/research-night-20260918/CLOUD-INBOX/events/2026-09-18/cloud-both-bases-b002.json). Next: Саратов ещё3 подходящих, затем Тюмень; Aileen6/Unique1/Naturale Kamala1 и Banyan ambiguity5; private crosswalk и AUT-04 restore prerequisites. Исходная ограниченная серия до08:00 ICT не продлена.

Источники: https://thezerophuket.com/contact/ ; https://thezerophuket.com/bang-tao/ ; https://thezerophuket.com/silhouette-nai-yang/ ; https://www.naturalephuket.com/ ; https://www.naturalephuket.com/2155/ ; https://phuket9.com/b2b ; https://www.andamandaphuket.com/ . Field-level sources/dates: public-contact-observations.json.

Sources checked but not promoted: Sansiri agent registration page still offers international-agent process, but inherited email was NOT visible in current extract; retain it as inherited, do not call it freshly verified. New groups' named sales owners/direct-person emails/Telegram not found. Zero WhatsApp target unavailable; no URL fabricated. Naturale WhatsApp is a literal published link on dated official post; publication time is not deliverability test.
