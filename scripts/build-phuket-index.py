#!/usr/bin/env python3
"""Build WEGC project-index catalog from public project names. No competitor photos."""
from pathlib import Path
import json
import re

ROOT = Path("/Users/ktel25/Documents/GitHub/WEGC")
INDREAMS = Path(
    "/Users/ktel25/.cursor/projects/Users-ktel25-Documents-GitHub-WEGC/agent-tools/"
    "96ff800c-4797-46a8-98f2-2849003b0f45.txt"
)

CYR = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

COVER_CDN = "https://wegc-covers.wegc.workers.dev"
COVER_MAP_PATH = ROOT / "cloudflare-worker" / "covers-map.json"
OFFICIAL_COVERS = json.loads(COVER_MAP_PATH.read_text()) if COVER_MAP_PATH.exists() else {}

COVERS = {
    "condo": "/images/the-modeva-exterior-4-1.jpg",
    "villa": "/images/projects/casademonte-hero.jpg",
    "Банг Тао": "/images/projects/sierra/facade.jpg",
    "Лаян": "/images/hero/hero-phuket-infinity-pool.jpg",
    "Чернг Талай": "/images/hero/hero-phuket-infinity-pool.jpg",
    "Сурин": "/images/hero/hero-phuket-villa-architecture.jpg",
    "Камала": "/images/hero/hero-phuket-infinity-pool.jpg",
    "Най Янг": "/images/projects/olive/facade.jpg",
    "Ката · Карон": "/images/hero/hero-phuket-bay-karst.jpg",
    "Раваи": "/images/hero/hero-phuket-aerial-sunset.jpg",
    "Ко Кео": "/images/projects/casademonte-hero.jpg",
    "Патонг": "/images/hero/hero-phuket-villa-architecture.jpg",
    "Чалонг": "/images/hero/hero-phuket-aerial-sunset.jpg",
    "Май Кхао": "/images/projects/olive/facade.jpg",
    "Най Харн": "/images/hero/hero-phuket-bay-karst.jpg",
    "Калим": "/images/hero/hero-phuket-villa-architecture.jpg",
    "Мыс Яму": "/images/hero/hero-phuket-aerial-sunset.jpg",
    "Панва": "/images/hero/hero-phuket-bay-karst.jpg",
    "Таланг": "/images/projects/sierra/facade.jpg",
    "Кату": "/images/hero/hero-phuket-villa-architecture.jpg",
    "Найтон": "/images/projects/olive/facade.jpg",
    "Пхукет Таун": "/images/hero/hero-phuket-aerial-sunset.jpg",
    "Ратсада": "/images/projects/casademonte-hero.jpg",
    "Вичит": "/images/hero/hero-phuket-aerial-sunset.jpg",
    "Пхукет": "/images/hero/hero-phuket-infinity-pool.jpg",
}

DIRECT = [
    {"slug": "the-title-sierra", "name": "The Title Sierra", "district": "Банг Тао", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 2870000, "area": 28, "beds": "студия", "delivery": "3 кв. 2028", "struct": "Freehold / Leasehold", "source": "direct", "url": "/projects/the-title-sierra.html", "cover": "/images/projects/sierra/facade.jpg"},
    {"slug": "title-vivi", "name": "The Title Vivi", "district": "Банг Тао", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 3160000, "area": 27, "beds": "студия", "delivery": "4 кв. 2027", "struct": "Leasehold", "source": "direct", "url": "/projects/title-vivi.html", "cover": "/images/the-modeva-exterior-4-1.jpg"},
    {"slug": "the-title-artrio", "name": "The Title Artrio", "district": "Банг Тао", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 4260000, "area": 28, "beds": "студия", "delivery": "2026", "struct": "Leasehold", "source": "direct", "url": "/projects/the-title-artrio.html", "cover": "/images/the-modeva-exterior-4-1.jpg"},
    {"slug": "the-modeva", "name": "The Modeva", "district": "Банг Тао", "kind": "condo", "developer": "AssetWise", "price": 4780000, "area": 41, "beds": "1 спальня", "delivery": "1 кв. 2027", "struct": "Leasehold", "source": "direct", "url": "/projects/the-modeva.html", "cover": "/images/the-modeva-exterior-4-1.jpg"},
    {"slug": "the-title-vivana", "name": "The Title Vivana", "district": "Камала", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 3620000, "area": 30, "beds": "студия", "delivery": "4 кв. 2028", "struct": "Freehold / Leasehold", "source": "direct", "url": "/projects/the-title-vivana.html", "cover": "/images/hero/hero-phuket-infinity-pool.jpg"},
    {"slug": "the-title-biancana", "name": "The Title Biancana", "district": "Сурин", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 6300000, "area": 31, "beds": "1 спальня", "delivery": "4 кв. 2028", "struct": "Leasehold", "source": "direct", "url": "/projects/the-title-biancana.html", "cover": "/images/hero/hero-phuket-villa-architecture.jpg"},
    {"slug": "the-title-balcony", "name": "The Title Balcony", "district": "Най Янг", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 5240000, "area": 33, "beds": "1 спальня", "delivery": "4 кв. 2027", "struct": "Leasehold", "source": "direct", "url": "/projects/the-title-balcony.html", "cover": "/images/projects/olive/facade.jpg"},
    {"slug": "the-olive", "name": "The Olive", "district": "Най Янг", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 4990000, "area": 32, "beds": "1 спальня", "delivery": "окт. 2028", "struct": "Freehold / Leasehold", "source": "direct", "url": "/projects/the-olive.html", "cover": "/images/projects/olive/facade.jpg"},
    {"slug": "the-title-katabello", "name": "The Title Katabello", "district": "Ката · Карон", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 3830000, "area": 28, "beds": "студия", "delivery": "3 кв. 2027", "struct": "Leasehold", "source": "direct", "url": "/projects/the-title-katabello.html", "cover": "/images/hero/hero-phuket-bay-karst.jpg"},
    {"slug": "the-title-adora", "name": "The Title Adora", "district": "Раваи", "kind": "condo", "developer": "Rhom Bho / The Title", "price": 4200000, "area": 32, "beds": "1 спальня", "delivery": "1 кв. 2027", "struct": "Leasehold", "source": "direct", "url": "/projects/the-title-adora.html", "cover": "/images/hero/hero-phuket-aerial-sunset.jpg"},
    {"slug": "casa-de-monte", "name": "Casa de Monte", "district": "Ко Кео", "kind": "villa", "developer": "Rhom Bho", "price": 28200000, "area": 297, "beds": "3–4 спальни", "delivery": "июль 2029", "struct": "Leasehold / Freehold", "source": "direct", "url": "/projects/casa-de-monte.html", "cover": "/images/projects/casademonte-hero.jpg"},
]

# Extra English names commonly searched (Title / Botanica / Laguna / Origin), if not already in InDreams.
EXTRA_EN = [
    ("The Title Coralina", "Камала", "condo", "Rhom Bho / The Title"),
    ("The Title Cielo", "Банг Тао", "condo", "Rhom Bho / The Title"),
    ("The Title Halo", "Банг Тао", "condo", "Rhom Bho / The Title"),
    ("The Title Heritage", "Банг Тао", "condo", "Rhom Bho / The Title"),
    ("The Title Legendary", "Банг Тао", "condo", "Rhom Bho / The Title"),
    ("The Title Serenity", "Камала", "condo", "Rhom Bho / The Title"),
    ("The Title Villa Kirara", "Банг Тао", "villa", "Rhom Bho / The Title"),
    ("The Title Villa Estella", "Банг Тао", "villa", "Rhom Bho / The Title"),
    ("Botanica Grand Avenue", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Hythe", "Чернг Талай", "condo", "Botanica Luxury Phuket"),
    ("Botanica Four Seasons", "Чалонг", "villa", "Botanica Luxury Phuket"),
    ("Botanica Modern Loft", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Chalong Bay", "Чалонг", "villa", "Botanica Luxury Phuket"),
    ("Botanica Foresta", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Forestique", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Prestige", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica MontAzure", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Sky Valley", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Botanica Wisdom", "Чернг Талай", "villa", "Botanica Luxury Phuket"),
    ("Rhea by Sansiri", "Сурин", "condo", "Sansiri"),
    ("So Origin Lagoon", "Чернг Талай", "condo", "Origin PCL"),
    ("Origin Residences Bangtao", "Банг Тао", "condo", "Origin PCL"),
    ("SO Origin Kata", "Ката · Карон", "condo", "Origin PCL"),
    ("The Base Cherngtalay", "Чернг Талай", "condo", "Sansiri"),
    ("The Base Rise", "Патонг", "condo", "Sansiri"),
    ("Laguna Bayside", "Чернг Талай", "condo", "Banyan Group Residences"),
    ("Laguna Lakeside", "Банг Тао", "condo", "Laguna Property"),
    ("Cassia Phuket", "Банг Тао", "condo", "Banyan Group"),
    ("Angsana Oceanview Residences", "Банг Тао", "condo", "Banyan Group / Laguna"),
    ("Banyan Tree Beach Residences Oceanus", "Банг Тао", "condo", "Laguna Property"),
    ("Andamanda Phuket", "Май Кхао", "condo", "Andamanda"),
    ("The Zero Bang Tao", "Банг Тао", "condo", "The Zero"),
    ("The Zero Nai Yang", "Най Янг", "condo", "The Zero"),
    ("Silhouette by The Zero", "Най Янг", "condo", "The Zero"),
]

DISTRICT_RULES = [
    (r"чернг|cherng|talay", "Чернг Талай"),
    (r"банг\s*тао|bang\s*tao|bangtao|лагун|laguna", "Банг Тао"),
    (r"лаян|layan", "Лаян"),
    (r"камала|kamala", "Камала"),
    (r"сурин|surin", "Сурин"),
    (r"най\s*янг|nai\s*yang|naiyang", "Най Янг"),
    (r"май\s*кхао|майкао|mai\s*khao|maikhao", "Май Кхао"),
    (r"ката|карон|kata|karon", "Ката · Карон"),
    (r"най\s*харн|найхарн|naiharn|nai\s*harn", "Най Харн"),
    (r"раваи|равай|rawai", "Раваи"),
    (r"чалонг|chalong", "Чалонг"),
    (r"патонг|patong", "Патонг"),
    (r"кату|kathu", "Кату"),
    (r"ко\s*кео|кокео|koh\s*kaew|ko\s*kaeo", "Ко Кео"),
    (r"яму|yamu", "Мыс Яму"),
    (r"панва|panwa", "Панва"),
    (r"калим|kalim", "Калим"),
    (r"найтон|naithon", "Найтон"),
    (r"таланг|thalang", "Таланг"),
    (r"ратсада|ratsada", "Ратсада"),
    (r"вичит|wichit", "Вичит"),
    (r"таун|town|пхукет\s*таун", "Пхукет Таун"),
]

DEV_RULES = [
    (r"title|тайтл|титл|rhom|ром бо", "Rhom Bho / The Title"),
    (r"botanica|ботаника", "Botanica Luxury Phuket"),
    (r"angsana|ангсана|banyan|баньян|cassia|кассия|laguna|лагуна property", "Laguna / Banyan"),
    (r"origin|ориджин|so origin", "Origin PCL"),
    (r"sansiri|сансири|rhea|реа\b|the base|base ", "Sansiri"),
    (r"zero|зеро|silhouette|силуэт", "The Zero"),
    (r"mouana|муана", "Mouana"),
    (r"wyndham|виндх", "Wyndham"),
    (r"\bvip\b", "VIP Grand"),
    (r"ozone|озон", "The Ozone"),
    (r"mono", "Mono"),
    (r"unique|юник", "Unique"),
    (r"aileen|айлин", "Aileen"),
    (r"anchan|анчан", "Anchan"),
    (r"assetwise|modeva|модева", "AssetWise"),
    (r"naturale|натурале", "Naturale"),
]


def latin(s: str) -> str:
    out = []
    for ch in s.lower():
        out.append(CYR.get(ch, ch))
    t = "".join(out)
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def slugify(name: str) -> str:
    s = "".join(CYR.get(ch, ch) for ch in name.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "project")[:60]


def district_of(name: str) -> str:
    key = name.lower()
    for pat, dist in DISTRICT_RULES:
        if re.search(pat, key):
            return dist
    return "Пхукет"


def developer_of(name: str) -> str:
    key = name.lower()
    for pat, dev in DEV_RULES:
        if re.search(pat, key):
            return dev
    return "по запросу"


def kind_of(name: str) -> str:
    if re.search(r"вилл|villa|пул вилл|pool villa", name.lower()):
        return "villa"
    return "condo"


def cover_of(district: str, kind: str, slug: str = "") -> str:
    if slug and slug in OFFICIAL_COVERS:
        return f"{COVER_CDN}/{slug}"
    return COVERS.get(district) or COVERS[kind]


def beds_of(kind: str) -> str:
    return "3–4 спальни" if kind == "villa" else "студия · 1–2 спальни"


def struct_of(kind: str) -> str:
    return "Leasehold / компания" if kind == "villa" else "Freehold / Leasehold"


def market_item(name: str, district=None, kind=None, developer=None) -> dict:
    d = district or district_of(name)
    k = kind or kind_of(name)
    dev = developer or developer_of(name)
    slug = slugify(name)
    return {
        "slug": slug,
        "name": name,
        "district": d,
        "kind": k,
        "developer": dev,
        "price": None,
        "area": None,
        "beds": beds_of(k),
        "delivery": "по запросу",
        "struct": struct_of(k),
        "source": "market",
        "url": f"/ru/podbor.html?project={slug}",
        "cover": cover_of(d, k, slug),
    }


def main():
    seen = {latin(p["name"]) for p in DIRECT}
    # also skip obvious Title twins
    for extra in ("sierra", "artrio", "vivana", "biancana", "katabello", "adoraphuket",
                  "theolive", "olive", "modeva", "casademonte", "titlevivi", "thetitlevivi"):
        seen.add(extra)

    catalog = list(DIRECT)

    for name, dist, kind, dev in EXTRA_EN:
        key = latin(name)
        if key in seen or any(key.find(s) >= 0 and len(s) > 6 for s in seen):
            if key in seen:
                continue
        if key in seen:
            continue
        seen.add(key)
        catalog.append(market_item(name, dist, kind, dev))

    blocks = []
    if INDREAMS.exists():
        raw = INDREAMS.read_text()
        parts = re.split(r"^### ", raw, flags=re.M)[1:]
        for part in parts:
            lines = part.strip().splitlines()
            name = lines[0].strip()
            blurb = " ".join(lines[1:3]) if len(lines) > 1 else ""
            blocks.append((name, blurb))

    added = 0
    for name, blurb in blocks:
        name = name.strip()
        key = latin(name)
        if not key or key in seen:
            continue
        if re.search(r"sierra|artrio|vivana|biancana|balcony|katabello|adora|modeva|casademonte|titlevivi", key):
            continue
        seen.add(key)
        hay = f"{name} {blurb}"
        item = market_item(name, district=district_of(hay))
        year = re.search(r"\b(20[12]\d)\b", blurb)
        if re.search(r"Готовый", blurb):
            item["delivery"] = "готово / ресейл"
        elif year:
            item["delivery"] = year.group(1)
        elif re.search(r"Строящийся|Офф\.план", blurb):
            item["delivery"] = "строится"
        catalog.append(item)
        added += 1

    # unique slugs
    used = set()
    for p in catalog:
        s = p["slug"]
        i = 2
        while s in used:
            s = f"{p['slug']}-{i}"
            i += 1
        p["slug"] = s
        if p["source"] == "market":
            p["url"] = f"/ru/podbor.html?project={s}"
        if s in OFFICIAL_COVERS:
            p["cover"] = f"{COVER_CDN}/{s}"
        used.add(s)

    out = ROOT / "ru" / "wegc-catalog-data.js"
    lines = [
        "/* Индекс проектов Пхукета. direct — паспорт WEGC; market — запрос застройщику.",
        "   Обложки: официальные баннеры застройщика через wegc-covers, иначе /images.",
        "   Чужие фото и логотипы агентств не используем. */",
        "window.WEGC_CATALOG_FX = { THB_RUB: 2.5 };",
        "",
        "window.WEGC_COVERS = " + json.dumps(COVERS, ensure_ascii=False, indent=2) + ";",
        "",
        "window.WEGC_CATALOG = [",
    ]
    for p in catalog:
        lines.append("  " + json.dumps(p, ensure_ascii=False) + ",")
    lines.append("];")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    n_dir = sum(1 for p in catalog if p["source"] == "direct")
    print(f"wrote {out} · {len(catalog)} projects · direct {n_dir} · market {len(catalog)-n_dir} · from InDreams +{added}")


if __name__ == "__main__":
    main()
