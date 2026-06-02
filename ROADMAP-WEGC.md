# ROADMAP WEGC — SEO/GEO

Статус-карта по спринтам. Эталон процесса: cluster-аудит → SEO-страницы → GEO → перелинковка через футер, без засорения topbar. Бренд независимый.

---

## Спринт 1 — СДЕЛАНО (2026-06-02)

**Фаза 1 — исследование**
- [x] Технический аудит (robots, sitemap, canonical/hreflang, schema) → `SEO-AUDIT-WEGC.md`
- [x] Семантика: подсчёт вхождений по кластерам + карта новых страниц
- [x] Скан конкурентов (MORE Group, ReloSale, RestProperty, aiproperty-phuket)

**Фаза 2 — реализация**
- [x] `llms.txt` v1 (структура URL + глоссарий freehold/leasehold/FET/WET/GIDR)
- [x] P1-посадочная `buy-property-phuket-ru.html` — «Как купить недвижимость на Пхукете»
      (hero + breadcrumb + answer-блок + формы собственности + 7 шагов + расходы + риски + FAQ + CTA)
- [x] Schema на посадочной: RealEstateAgent + WebPage + BreadcrumbList + FAQPage
- [x] `sitemap.xml` — добавлен URL гайда (lastmod 2026-06-02)
- [x] Футер «Справочник» на `index-ru.html` и `fund-ru.html` (6-я колонка)
- [x] Cross-links: `rayony-phuket.html` + `sravnenie/phuket-vs-dubai.html` + `sravnenie/phuket-vs-bali.html` → гайд

---

## Спринт 2 — план

### P1 — добить ядро гайдов (RU)
- [x] `freehold-leasehold-thailand-ru.html` — формы собственности, квота 49%, 30+30+30, FET (WebPage+FAQPage+Breadcrumb+RealEstateAgent)
- [x] Schema-инъекция на главные `index-ru/en/zh`: `Organization` + `WebSite` + `RealEstateAgent`
- [ ] `phuket-investment-yield-ru.html` — реальная доходность: gross vs net (4–6%), расходы (УК, простои, налоги), без «гарантий»
- [ ] Schema `FAQPage` + `BreadcrumbList` на `rayony/*` и `sravnenie/*` (answer-блоки)

### P2
- [ ] `remote-purchase-phuket-ru.html` — удалённая сделка: доверенность, маршрут оплаты, FET, риски
- [ ] `safe-buy-due-diligence-ru.html` — DD и безопасная сделка (роль WET, чек-лист проверки застройщика)
- [ ] EN-версия `buy-property-phuket-en.html` (+ hreflang-связка ru↔en)

### P3
- [ ] `phuket-property-taxes-ru.html` — налоги и расходы сделки (transfer fee, stamp, sinking fund, land&building tax, PIT)
- [ ] ZH-версии хабов (buy / freehold-leasehold) — `*-zh.html`
- [ ] Гигиена индекса: добавить `<meta name="robots" content="noindex">` в backup-файлы (`fund_backup_*`, `_archive-*`, `fund-alt/new/redesigned/with-tax-disclaimer`), которые сейчас закрыты только в robots.txt
- [ ] Убрать `wet-agency*` (редиректы) из внутренних ссылок; проверить, что их нет в sitemap (уже нет)
- [ ] sitemap: добавить `xhtml:link rel="alternate" hreflang` для трёхъязычных пар
- [ ] PageSpeed/Lighthouse прогон `index-ru.html` + гайдов; `width/height` и WebP для тяжёлых JPG

### Контент / доверие (после структуры)
- [ ] Анонимизированные кейсы покупателей (расширить блок «Истории» в гайды)
- [ ] Раздел «эксперты / юристы-партнёры» (E-E-A-T) — без раскрытия чужих брендов
- [ ] FAQ-блоки во все паспорта проектов с answer-разметкой (частично есть налоговый FAQ)

---

## Принципы (неизменны)
- Не переписывать главные/`fund-*` — только новые страницы + точечные meta/schema/футер.
- Не засорять topbar SEO-хабами — перелинковка через футер «Справочник» + контекстные cross-links.
- Дисклеймер на каждой странице: не оферта, не гарантия доходности, не инвест/налоговая консультация; сделку проверяет независимый юрист.
- Три языка: приоритет RU → EN → ZH.
- Фактологичный тон без хайпа; преимущества (0% комиссии, прямой контракт, DD) — только где это правда.
