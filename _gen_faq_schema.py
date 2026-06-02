#!/usr/bin/env python3
"""Inject visible FAQ blocks + FAQPage/BreadcrumbList JSON-LD into rayony/* and sravnenie/* pages."""
import json, re, os

ROOT = os.path.dirname(os.path.abspath(__file__))

FAQ_CSS = """.faq{margin-top:30px;display:flex;flex-direction:column;gap:12px;max-width:880px}
.faq details{border:1px solid var(--line);border-radius:var(--radius-lg);background:#fff;overflow:hidden}
.faq summary{list-style:none;cursor:pointer;padding:20px 24px;display:flex;justify-content:space-between;align-items:center;gap:16px;font-size:1.02rem;font-weight:500;color:var(--ink)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:'+';font-size:1.5rem;font-weight:300;color:var(--gold);line-height:1}
.faq details[open] summary::after{content:'\\2013'}
.faq .a{padding:0 24px 22px;color:var(--body);font-size:14.5px;line-height:1.72}
"""

FONTS_LINE = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700;800&display=swap" rel="stylesheet"/>'
CRUMBS_CSS = '.crumbs{font-size:12px;color:var(--muted);padding:14px 0 0}'
CTA_OPEN = '<section class="cta"><div class="wrap">'

OWN = ("Да. В кондоминиумах доступно полное владение (freehold) в рамках 49% иностранной квоты, "
       "а виллы и землю иностранец оформляет в зарегистрированный долгосрочный лизхолд (leasehold). "
       "Подробнее — в гайде <a href=\"/freehold-leasehold-thailand-ru.html\" style=\"color:var(--gold)\">Freehold и Leasehold</a>.")

# slug -> (Имя, цена, доходность, тип спроса, флавор предложения для Q3)
DISTRICTS = {
    "bang-tao": ("Банг Тао", "от 3,5 млн ฿", "6–9%",
                 "Брутто-доходность обычно 6–9% при круглогодичном спросе и максимальной на острове ликвидности аренды."),
    "layan": ("Лаян", "от 3 млн ฿", "5–7%",
              "Брутто-доходность около 5–7%. Лаян — спокойный приватный район со спросом на долгосрочную аренду; ближайшие новые проекты — в соседнем Банг Тао."),
    "surin": ("Сурин", "от 8 млн ฿", "6–9%",
              "Брутто-доходность 6–9% в премиальном сегменте с высоким средним чеком аренды."),
    "kamala": ("Камала", "от 3 млн ฿", "6–8%",
               "Брутто-доходность 6–8% при устойчивом семейном и арендном спросе."),
    "nai-yang": ("Най Янг", "от 2,8 млн ฿", "6–10%",
                 "Брутто-доходность 6–10% при круглогодичном спросе рядом с аэропортом и пляжем."),
    "kata-karon": ("Ката · Карон", "от 3 млн ฿", "5–8%",
                   "Брутто-доходность 5–8%. Спрос сезонный курортный — пик в высокий сезон (ноябрь–апрель)."),
    "rawai": ("Раваи", "от 3 млн ฿", "5–8%",
              "Брутто-доходность 5–8%. Резидентный район юга со спросом на долгосрочную аренду."),
    "koh-kaew": ("Ко Кео", "от 9,5 млн ฿ (виллы)", "5–7%",
                 "Брутто-доходность 5–7%. Резидентный район у города и марины, в основном виллы."),
}

def district_faq(slug):
    name, price, yld, q3 = DISTRICTS[slug]
    return [
        (f"Может ли иностранец купить недвижимость в районе {name}?", OWN),
        (f"Сколько стоит недвижимость в районе {name}?",
         f"Порог входа — {price.replace('от ','от ')} за компактный юнит в новых проектах. Виллы и премиальные резиденции — заметно выше. Точную цену по конкретному объекту пришлём по запросу."),
        (f"Какая доходность аренды в районе {name}?",
         f"{q3} Чистая доходность (net) ниже — после управляющей компании, простоев и налогов."),
    ]

SRAVNENIE = {
    "phuket-vs-dubai": {
        "crumb": "Пхукет или Дубай",
        "faq": [
            ("Что выгоднее для инвестиций — Пхукет или Дубай?",
             "Зависит от цели. Дубай — дорогой вход, нулевой налог на доход и резидентская виза за покупку; Пхукет — ниже порог входа, сильная курортная аренда и оплата из России в своей валюте. Часто эти рынки совмещают: Дубай под капитал, Пхукет под доходность и образ жизни."),
            ("Где ниже порог входа — на Пхукете или в Дубае?",
             "На Пхукете: кондо от ~$80–90K против ~$200K в Дубае, а золотая виза в Дубае требует покупки от AED 2M (~$545K)."),
            ("Можно ли оплатить покупку из России?",
             "На Пхукете оплата возможна через сингапурскую группу в вашей валюте. В Дубае платежи из РФ проходят сложнее из-за усиленного банковского комплаенса."),
        ],
    },
    "phuket-vs-bali": {
        "crumb": "Пхукет или Бали",
        "faq": [
            ("Что надёжнее для инвестиций — Пхукет или Бали?",
             "По устойчивости актива Пхукет, как правило, надёжнее: кондо можно оформить во freehold, титул Chanote проверяем, инфраструктура развитее. На Бали freehold иностранцу недоступен, лизхолд короче (часто 25–30 лет), выше юридические риски nominee-схем."),
            ("Где выше доходность — на Пхукете или на Бали?",
             "Бали показывает более высокую валовую доходность (10–15%), но за счёт короткого лизхолда и юридических рисков — актив «тает» по сроку. На Пхукете доходность 6–10% при более устойчивой структуре владения и лучшей ликвидности при выходе."),
            ("Может ли иностранец купить freehold на Бали?",
             "Нет. На Бали иностранцу freehold недоступен — только лизхолд или рискованные nominee-структуры. На Пхукете кондо доступно во freehold в рамках 49% квоты, а земля под виллами — зарегистрированный долгосрочный лизхолд."),
        ],
    },
}


def build_faq_section(pairs):
    items = "\n".join(
        f"    <details><summary>{q}</summary><div class=\"a\">{a}</div></details>"
        for q, a in pairs
    )
    return (
        '<section class="s cream"><div class="wrap">\n'
        '  <h2>Частые вопросы</h2>\n'
        '  <div class="faq">\n' + items + '\n  </div>\n'
        '</div></section>\n\n'
    )


def build_schema(breadcrumb_items, faq_pairs):
    graph = []
    graph.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            ({"@type": "ListItem", "position": i + 1, "name": name, "item": url}
             if url else {"@type": "ListItem", "position": i + 1, "name": name})
            for i, (name, url) in enumerate(breadcrumb_items)
        ],
    })
    graph.append({
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in faq_pairs
        ],
    })
    payload = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">\n'
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + '\n</script>\n')


def inject(path, breadcrumb_items, faq_pairs):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if 'class="faq"' in html:
        print(f"  SKIP (already has faq): {path}")
        return

    # 1) FAQ CSS before .crumbs rule
    html = html.replace(CRUMBS_CSS, FAQ_CSS + CRUMBS_CSS, 1)

    # 2) JSON-LD before fonts link
    schema = build_schema(breadcrumb_items, faq_pairs)
    html = html.replace(FONTS_LINE, FONTS_LINE + "\n" + schema, 1)

    # 3) visible FAQ section before CTA
    html = html.replace(CTA_OPEN, build_faq_section(faq_pairs) + CTA_OPEN, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  OK: {path}")


def main():
    base = "https://wegc.fund"
    home = (f"{base}/index-ru.html", "Главная")

    # district pages
    for slug, (name, *_rest) in DISTRICTS.items():
        path = os.path.join(ROOT, "rayony", f"{slug}.html")
        bc = [("Главная", f"{base}/index-ru.html"),
              ("Районы Пхукета", f"{base}/rayony-phuket.html"),
              (name, None)]
        inject(path, bc, district_faq(slug))

    # district hub
    hub = os.path.join(ROOT, "rayony-phuket.html")
    hub_faq = [
        ("Какой район Пхукета лучший для инвестиций?",
         "Зависит от цели и бюджета. Под аренду и ликвидность — Банг Тао и Най Янг; премиальный сегмент — Сурин и Камала; для жизни и резидентства — Раваи и Ко Кео. Сезонный курортный спрос — Ката-Карон."),
        ("Где на Пхукете самый низкий порог входа?",
         "Самый доступный вход — Най Янг (от 2,8 млн ฿), а также Банг Тао, Камала и Раваи (от 3–3,5 млн ฿). Виллы в Ко Кео начинаются от 9,5 млн ฿."),
        ("Может ли иностранец купить недвижимость на Пхукете?", OWN),
    ]
    inject(hub, [("Главная", f"{base}/index-ru.html"), ("Районы Пхукета", None)], hub_faq)

    # sravnenie pages
    for slug, data in SRAVNENIE.items():
        path = os.path.join(ROOT, "sravnenie", f"{slug}.html")
        bc = [("Главная", f"{base}/index-ru.html"),
              ("Сравнения", None),
              (data["crumb"], None)]
        inject(path, bc, data["faq"])

    print("done")


if __name__ == "__main__":
    main()
