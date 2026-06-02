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
- [x] `phuket-investment-yield-ru.html` — реальная доходность: gross vs net (4–6%), расходы (УК, простои, налоги), доходность по районам, без «гарантий» (WebPage+FAQPage+Breadcrumb+RealEstateAgent)
- [x] Schema `FAQPage` + `BreadcrumbList` + видимые answer-блоки на `rayony/*` (8 районов), `rayony-phuket.html` (хаб) и `sravnenie/*` (Дубай, Бали)
- [x] Sitemap + llms.txt + футер «Справочник» + кросс-ссылки на страницу доходности

### P2
- [x] `remote-purchase-phuket-ru.html` — удалённая сделка: доверенность, маршрут оплаты, FET, риски (WebPage+FAQPage+Breadcrumb+RealEstateAgent)
- [x] `safe-buy-due-diligence-ru.html` — DD и безопасная сделка (роль WEGC, чек-лист застройщика, red flags) (WebPage+FAQPage+Breadcrumb+RealEstateAgent)
- [x] Sitemap + llms.txt + футер «Справочник» + кросс-ссылки (buy-property шаги 2/5, freehold, yield, главные/fund)
- [~] ~~EN-версия `buy-property-phuket-en.html`~~ — ОТМЕНЕНО: SEO-гайды только на RU (трафик из РФ/СНГ)

### P3
- [x] `phuket-property-taxes-ru.html` — налоги и расходы сделки (transfer fee 2%, stamp 0,5%, регистрация лизхолда 1,1%, sinking fund, CAM, land&building tax, налог с аренды, перепродажа) + Schema; ссылка из buy-property (шаг расходов)
- [x] Гигиена индекса: `<meta name="robots" content="noindex, nofollow">` во все backup/archive HTML (18 файлов)
- [x] Убрать `wet-agency*` из внутренних ссылок (promo-toast.js → язык-зависимый `#contact`); в sitemap их нет
- [x] sitemap: `xhtml:link rel="alternate" hreflang` для трёхъязычных групп (генерируется из on-page hreflang, 130 аннотаций)
- [~] ~~ZH-версии хабов (buy / freehold-leasehold)~~ — ОТМЕНЕНО: SEO-гайды только на RU
- [x] PageSpeed: `width/height` (интринсик-размеры из файлов) + `decoding="async"` на 226 `<img>` в 33 файлах (lazy уже был) — устраняет CLS
- [ ] PageSpeed (опц.): WebP для тяжёлых JPG (через `<picture>` + fallback) — отдельной задачей

### Контент / доверие (после структуры)
- [ ] Анонимизированные кейсы покупателей (расширить блок «Истории» в гайды)
- [ ] Раздел «эксперты / юристы-партнёры» (E-E-A-T) — без раскрытия чужих брендов
- [x] `FAQPage`-разметка во все 11 RU паспортов (генерируется из видимых FAQ-блоков)

---

## Принципы (неизменны)
- Не переписывать главные/`fund-*` — только новые страницы + точечные meta/schema/футер.
- Не засорять topbar SEO-хабами — перелинковка через футер «Справочник» + контекстные cross-links.
- Дисклеймер на каждой странице: не оферта, не гарантия доходности, не инвест/налоговая консультация; сделку проверяет независимый юрист.
- SEO/GEO-хабы (справочник) — только на RU. EN/ZH-версии этих гайдов не делаем (основной трафик из РФ/СНГ). Существующие EN/ZH страницы сайта (главные, фонд, паспорта) остаются как есть.
- Фактологичный тон без хайпа; преимущества (0% комиссии, прямой контракт, DD) — только где это правда.
