# SEO / GEO-аудит wegc.fund

**Домен:** https://wegc.fund · **Репо:** apodelenko-ctrl/wegc (main)
**Бренд:** WEGC / WET — фонд + агентство недвижимости Пхукета, private capital, research
**Языки:** EN (`index.html`), RU (`index-ru.html`), ZH (`index-zh.html`)
**Дата аудита:** 2026-06-02
**Эталон процесса:** внутренний (cluster-аудит → SEO-страницы → GEO → перелинковка через футер, без засорения topbar). Бренд независимый, ссылок на сторонние проекты нет и не будет.

---

## 0. Резюме (TL;DR)

Сайт технически здоров: один `sitemap.xml` (56 URL, есть `lastmod`/`changefreq`/`priority`), корректный `robots.txt` с Disallow для backup/preview-страниц, рабочие `canonical` + `hreflang` (ru/en/zh + x-default) на главных и паспортах проектов. Сильная локальная SEO-база: `rayony/*` (8 районов) + хаб `rayony-phuket.html` с калькулятором + `sravnenie/*` (Дубай, Бали).

**3 главные проблемы:**
1. **GEO-слой отсутствует** — нет `llms.txt`, нет `FAQPage`/`BreadcrumbList`-разметки, нет «answer-блоков» под AI-выдачу. Конкуренты (MORE Group, ReloSale, RestProperty) выигрывают именно гайдами с прямыми ответами.
2. **Нет коммерческих гайд-хабов под транзакционно-информационный спрос.** Термины `freehold/leasehold` используются 50+ раз на главной, но **нет страницы-объяснения**; «удалённая покупка» встречается **1 раз во всём сайте**; due diligence и налоги — разрозненно.
3. **Schema.org отсутствует на ключевых страницах** — `index-ru/en/zh`, `rayony/*`, `sravnenie/*`, `private-capital*`, `research*`. Есть только на `fund-*` и `projects/*` (Product/Organization).

---

## 1. Технический аудит

### 1.1 robots.txt — ✅ ОК
- `User-agent: * / Allow: /`, `Sitemap: https://wegc.fund/sitemap.xml`.
- Корректно закрыты backup/preview: `fund-alt`, `fund-new`, `fund-redesigned`, `fund-with-tax-disclaimer`, `fund_backup_*`, `_archive-*`, `index1`, `til*`, `passport*`, `wet-trading-house`, `partners-ru`, и `.md`-заметки.
- ⚠️ Эти же backup-страницы **физически существуют** в репо и содержат `application/ld+json` (см. 1.4). Disallow в robots не гарантирует деиндексацию — стоит добавить `<meta name="robots" content="noindex">` в сами файлы (часть P3).

### 1.2 sitemap.xml — ⚠️ хорошо, можно усилить
- 56 `<loc>`, UTF-8, у всех есть `lastmod` (2026-05-31), `changefreq`, `priority`. Дублей не замечено.
- ⚠️ **Нет `xhtml:link rel="alternate" hreflang"`** внутри sitemap (есть только в `<head>` страниц). Для трёхъязычного сайта полезно добавить hreflang-аннотации в sitemap.
- ⚠️ Нет `image:image`/`image:title` (некритично).
- ❗ **Orphan-риск:** в sitemap включён `wet-agency*.html`, но это теперь **301-редирект-страницы** (см. 1.5). Их стоит убрать из sitemap, чтобы не отдавать редиректы в индекс.

### 1.3 llms.txt — ❌ ОТСУТСТВУЕТ
Создаётся в рамках Фазы 2. План v1: блоки `# WEGC`, `## Real estate (RU/EN/ZH)`, `## Districts`, `## Comparisons`, `## Guides`, `## Fund & capital`, `## Legal`, глоссарий (freehold, leasehold 30+30+30, FET, foreign quota 49%, WET, GIDR).

### 1.4 Schema.org — ⚠️ частично
| Тип страниц | Schema | Статус |
|---|---|---|
| `projects/*` | Product + AggregateOffer + Brand | ✅ есть |
| `fund-*` | Organization/WebPage | ✅ есть |
| `index-ru/en/zh` (главные) | — | ❌ **нет** |
| `rayony/*`, `rayony-phuket` | — | ❌ нет (нужен Place/FAQPage/Breadcrumb) |
| `sravnenie/*` | — | ❌ нет (нужен FAQPage/Article) |
| `private-capital*`, `research*` | — | ❌ нет |
| backup `fund_*`, `_archive-*` | ld+json есть | ⚠️ должны быть noindex |

**Рекомендация:** на главных — `RealEstateAgent` + `Organization` + `WebSite`(SearchAction); на гайдах/районах/сравнениях — `WebPage` + `FAQPage` + `BreadcrumbList`.

### 1.5 canonical / hreflang — ✅ ОК (с нюансом)
- `index-ru.html`: canonical=self, hreflang en→`/`, ru→`/index-ru.html`, zh→`/index-zh.html`, x-default→`/`. Корректно.
- Паспорта проектов: canonical + hreflang ru/en/zh настроены (только что добавлен zh для Vivi).
- **Нюанс:** `wet-agency.html` / `-en` / `-zh` — это **noindex meta-refresh редиректы** на `index-*.html` (контент агентства переехал на главную). Внутренние ссылки на них стоит заменить прямыми на `/index-ru.html`, а из sitemap — удалить.

### 1.6 Контактный механизм (для форм на посадочных)
- Forms: Formspree endpoint `https://formspree.io/f/xrbyywrr` + mailto-fallback `post@wegc.fund`. Email недвижимости: `property@wegc.fund`.
- Новые посадочные используют CTA-ссылку на `/index-ru.html#contact` (единая форма), чтобы не плодить endpoint'ы. При желании — переиспользовать тот же Formspree.

### 1.7 PageSpeed (оценка статики, без прогона Lighthouse)
- Страницы статические, инлайновый CSS, шрифт Inter через Google Fonts (`preconnect` есть), Leaflet/карта подгружается `defer`. Изображения — крупные JPG без `width/height`-атрибутов и без `loading="lazy"` в части галерей → возможен CLS. **Рекомендация P3:** добавить размеры изображениям, проверить вес hero-JPG, рассмотреть WebP. Полноценный прогон Lighthouse — вне scope Фазы 1.

### 1.8 Sitemap vs реальные файлы (orphan/missing)
- 81 HTML-файл в репо; 56 в sitemap. Разница — это (корректно) исключённые backup/preview/redirect/служебные (`yandex_*`, `google*`, `404`, `passport*`, `til*`, `fund_backup*`, `partners-ru`, `wet-agency*`).
- ✅ Новый `projects/title-vivi-zh.html` уже добавлен в sitemap.
- ❗ К удалению из sitemap: `wet-agency*.html` (редиректы).

---

## 2. Семантика — кластеры WEGC

Подсчёт вхождений ключевых терминов по `*.html` (grep, корневой уровень + rayony/sravnenie/projects):

| Приоритет | Кластер | Запросы | Что есть | Вхождения | Пробел |
|---|---|---|---|---|---|
| **P1** | Покупка недвижимости Пхукет | купить квартиру Пхукет, недвижимость Пхукет для россиян | index-ru, projects/*, rayony/* | много | **нет хаба «как купить»** (пошагово: выбор→DD→доверенность→FET→Land Dept) |
| **P1** | Freehold / Leasehold | freehold Таиланд, leasehold 30+30, квота 49% | упоминается на index/projects | 50–54 на главной | **нет страницы-объяснения** форм собственности |
| **P1** | Инвестиции / доходность | инвестиции в недвижимость Таиланда, доходность аренды Пхукет, net yield | fund-ru, rayony-phuket(24), index-ru(13), sravnenie | средне | **нет коммерческого гайда «реальная доходность»** (gross vs net 4–6%) |
| **P2** | Районы | где купить, Bang Tao, Kamala, Layan… | `rayony/*` ✅ + хаб + калькулятор | сильно | усилить: FAQ-schema, answer-блоки, перелинковка на гайды |
| **P2** | Сравнения | Пхукет vs Бали, vs Дубай | `sravnenie/*` ✅ | ок | добавить FAQ-schema; рассмотреть vs Бали/Дубай по налогам/визам |
| **P2** | Удалённая покупка | купить недвижимость удалённо Таиланд, через ОАЭ, FET | — | **1 (!)** | **отдельная страница** (доверенность, маршрут оплаты, FET, риски) |
| **P2** | Due diligence | проверка застройщика, безопасная сделка | fund-ru(6), index-ru(4), rayony(1×) | слабо | **хаб «безопасная покупка / DD»** (роль WET) |
| **P3** | Налоги / оформление | налоги при покупке, transfer fee, sinking fund, land&building tax | sravnenie-dubai(9), projects(FAQ), index-ru(3) | разрозненно | **справочник по налогам и расходам сделки** (7–15% сверху) |
| **P3** | Private capital / фонд | фонд недвижимости, co-invest | private-capital-ru, fund-ru | ок | SEO-усиление + перелинковка с гайдов |

**Вывод:** контент-ядро (проекты, районы, сравнения) сильное. Дыра — **информационно-транзакционные гайды** под спрос «как, безопасно, удалённо, налоги, доходность», которые сейчас собирают трафик у MORE Group / ReloSale / RestProperty.

---

## 3. Конкуренты (RU-выдача)

| Конкурент | Что у них сильно |
|---|---|
| **MORE Group** (moregroupestate.ru) | Подробные гайды: «как купить иностранцу», «через ОАЭ 2026», «реальная доходность: маркетинг vs факты». Прямые ответы, таблицы, честные цифры net yield. |
| **ReloSale** | Гайд «кондо 2026: квота 49%», FETF, риски без обещаний доходности. |
| **RestProperty / aiproperty-phuket** | Доходность 6–12% с разбором net/gross, по-районно, калькуляторы расходов. |
| **vc.ru / homeinphuket / Virto** | Обзорные статьи «купить в Таиланде: ловушки», сравнения стран по yield. |

**Что у них есть, чего нет у нас:** пошаговый how-to-buy, маршрут оплаты RU→UAE→Thailand + FET, freehold/leasehold explainer, честный net-yield разбор, налоговый справочник, страница удалённой покупки.

**Наше конкурентное преимущество (использовать в копии):** прямой контракт с застройщиком и **0% комиссии покупателю**, due diligence через независимого юриста, принадлежность к сингапурской группе WET с международной банковской инфраструктурой, беспроцентная рассрочка застройщика, фактологичный тон без хайпа.

---

## 4. Карта новых страниц

### P1 (Спринт 1)
| Slug | Кластер | Язык | Schema |
|---|---|---|---|
| `buy-property-phuket-ru.html` | Как купить недвижимость на Пхукете (пошагово) | RU (→EN) | WebPage+RealEstateAgent+FAQPage+Breadcrumb |
| `freehold-leasehold-thailand-ru.html` | Freehold vs Leasehold (формы собственности, квота 49%) | RU (→EN) | WebPage+FAQPage+Breadcrumb |
| `phuket-investment-yield-ru.html` | Реальная доходность / инвестиции (net vs gross) | RU (→EN) | WebPage+FAQPage+Breadcrumb |

### P2 (Спринт 1–2)
| Slug | Кластер | Язык |
|---|---|---|
| `remote-purchase-phuket-ru.html` | Удалённая покупка (доверенность, оплата, FET, риски) | RU |
| `safe-buy-due-diligence-ru.html` | Безопасная сделка и DD (роль WET) | RU |

### P3 (Спринт 2)
| Slug | Кластер | Язык |
|---|---|---|
| `phuket-property-taxes-ru.html` | Налоги и расходы сделки (transfer fee, stamp, sinking fund, PIT) | RU |
| EN-версии P1-страниц | — | EN |
| ZH-версии хабов | — | ZH |

### Усилить (не дублировать)
- `rayony-phuket.html` + `rayony/*` → FAQPage-schema, answer-блок, перелинковка на новые гайды.
- `sravnenie/*` → FAQPage-schema, перелинковка.
- `index-ru/en/zh` → добавить `RealEstateAgent`+`Organization`+`WebSite` schema; футер «Справочник».

---

## 5. Принципы реализации (Фаза 2)
1. Не переписывать `index-*`, `fund-*` — только новые страницы + точечные meta/schema/футер.
2. Шаблон посадочной = стиль `rayony/*` (inline CSS WEGC, topbar `#topbar`, hero, секции `.s`, `.facts`, `.card`, CTA, footer `.f` + `.f-disc`).
3. Каждая посадочная: breadcrumb + answer-блок + что/шаги/риски/FAQ + CTA на `/index-ru.html#contact` + JSON-LD (WebPage+FAQPage+BreadcrumbList, где уместно RealEstateAgent/Service).
4. `llms.txt` в корне; новые URL — в `sitemap.xml`.
5. Перелинковка: блок «Справочник» в футере главных RU-страниц; cross-links хаб ↔ `rayony/*` ↔ `projects/*` ↔ `sravnenie/*`. **Не** в topbar.
6. Дисклеймер на каждой странице: не оферта, не гарантия доходности, не инвестрекомендация; каждую сделку проверяет независимый юрист.

---

## 6. Чеклист по каждой странице
- [ ] HTML создан в стиле WEGC
- [ ] FAQPage + BreadcrumbList schema
- [ ] Добавлена в `sitemap.xml` и `llms.txt`
- [ ] Блок «Справочник» в футере главных RU-страниц
- [ ] Cross-link минимум с 2 существующими страницами
- [ ] Дисклеймер (не оферта / не гарантия доходности)
- [ ] git commit + push (main)
