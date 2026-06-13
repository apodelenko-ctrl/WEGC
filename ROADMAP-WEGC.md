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
- [x] PageSpeed: WebP для всех растровых изображений (через `<picture>` + JPG-fallback) — 78 файлов сгенерировано (37,5 МБ → 11,9 МБ, −68%), 226 `<img>` обёрнуты в `<picture>` на 33 живых страницах; `picture{display:contents}` сохраняет вёрстку

### Контент / доверие (после структуры)
- [ ] Анонимизированные кейсы покупателей (расширить блок «Истории» в гайды)
- [ ] Раздел «эксперты / юристы-партнёры» (E-E-A-T) — без раскрытия чужих брендов
- [x] `FAQPage`-разметка во все 11 RU паспортов (генерируется из видимых FAQ-блоков)

---

## Спринт 3 — AI-агент «Анна» и воронка лидов (2026-06-13)

**Инфраструктура (Cloudflare)**
- [x] AI-агент «Анна» на Cloudflare Worker (`wegc-ai-agent`) + Claude (`claude-sonnet-4-6`)
- [x] База знаний `wegc-kb.js`: 11 проектов, районы, компания, FAQ (оплата, freehold/leasehold, FET, доходность, отделка/мебель)
- [x] Память диалогов в KV; лог лидов и хендофф в D1; админ-дашборд `/admin?key=…`
- [x] Хендофф тёплых лидов менеджеру в Telegram (tool `notify_manager`), с указанием источника

**Каналы**
- [x] Telegram-бот «Анна» (вебхук, секрет)
- [x] Живой чат на сайте: эндпоинт `/web` (CORS только wegc.fund) + переписан `chat-widget.js` (пузыри, индикатор набора, память сессии, кликабельные ссылки)
- [x] Cache-bust `?v=20260613` для `chat-widget.js` на всех 62 страницах
- [ ] WhatsApp через Meta Cloud API (эндпоинт `/wa`) — ЖДЁТ провижн: Meta Business + отдельный номер + токен

**Поведение / качество**
- [x] Языковая директива по каналу: сайт — жёстко по языку страницы (RU/EN/ZH), Telegram — зеркалирование
- [x] Серверная зачистка markdown (`**`, `##`, `---`, буллеты, `[text](url)`) — чистый текст на всех языках
- [x] Прямые ссылки на паспорта проектов в ответах (валидность всех 11 URL проверена)
- [x] Оплата из России: рублёвая схема через финагента (договор+инвойс+поручение) — синхронизировано на сайте `oplata-iz-rossii-thailand-ru.html` и в базе знаний; счета UK/CN/SG для иностранцев
- [x] УТП «полная отделка (не серый ключ) + бесплатный мебельный пакет» — главная `/ru/` + база знаний
- [x] Анна не вбрасывает сама минусы/возражения — ведёт от выгод, риски только по запросу
- [x] Драйв-тест 5 персон (RU/EN/ZH, комплаенс/торг/инъекция/выдуманный проект) — пройден

**Масштабирование**
- [x] Кэширование системного промпта (Anthropic prompt caching) — ~90% дешевле/быстрее
- [x] Ретрай с бэкоффом на 429/5xx; нагрузочный мини-тест 10 параллельных = 10/10
- [ ] Поднять тариф Anthropic под пики рекламы (RPM/TPM) — на пользователе
- [ ] Счётчик диалогов/лидов за день в дашборде + алерт в Telegram при ошибках Claude

**Бэклог агента**
- [ ] EN/ZH-ссылки на паспорта там, где есть `-en`/`-zh` версии (чтобы не 404)
- [ ] Налоги в EN-ответах — только ориентировочно, точные ставки → к тайскому юристу
- [ ] Интеграция с AMO CRM + бронь Zoom (после обкатки на трафике)
- [ ] Ротация раскрытых ключей (Telegram bot token, Anthropic API key) — на пользователе

**Реклама / маркетинг**
- [x] Яндекс.Метрика (`id=109732633`) + цели (form_submit, chat_open, chat_send, video_play, chat_lead)
- [ ] Яндекс.Директ: запуск кампании (креативы и картинки готовы)
- [ ] Китай: каналы WeChat / Xiaohongshu / Baidu (Meta/FB в материковом Китае не работают)
- [ ] На пользователе: Яндекс.Бизнес + Google Business Profile

---

## Принципы (неизменны)
- Не переписывать главные/`fund-*` — только новые страницы + точечные meta/schema/футер.
- Не засорять topbar SEO-хабами — перелинковка через футер «Справочник» + контекстные cross-links.
- Дисклеймер на каждой странице: не оферта, не гарантия доходности, не инвест/налоговая консультация; сделку проверяет независимый юрист.
- SEO/GEO-хабы (справочник) — только на RU. EN/ZH-версии этих гайдов не делаем (основной трафик из РФ/СНГ). Существующие EN/ZH страницы сайта (главные, фонд, паспорта) остаются как есть.
- Фактологичный тон без хайпа; преимущества (0% комиссии, прямой контракт, DD) — только где это правда.
