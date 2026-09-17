# coding: utf-8
#!/usr/bin/env python3
"""Publish EVERY source record, without promoting it to current sale inventory.

Offline reproducible build. Original 45-record demo and private evidence untouched.
Exact project visuals stay distinct from clearly labelled MIRA editorial covers.
"""
from pathlib import Path
import csv, hashlib, html, importlib.util, json, re
ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'ru/wegc-catalog-data.js'
MASTER = 'project-bible/mira/data/phuket-project-master.csv'
MEDIA = {
    'casa-de-monte': '/images/projects/casademonte-hero.webp',
    'the-olive': '/images/projects/olive/facade.webp',
    'the-title-balcony': '/images/projects/balcony-hero.webp',
    'the-title-biancana': '/images/projects/biancana-hero.webp',
    'the-title-sierra': '/images/projects/sierra/facade.webp',
    'the-title-vivana': '/images/projects/vivana/facade.webp',
    'title-vivi': '/images/title-vivi-exterior-3.webp',
    'the-title-artrio': '/images/the-title-artrio-exterior-4-1.webp',
    'the-modeva': '/images/the-modeva-exterior-4-1.webp',
    'the-title-katabello': '/images/the-title-katabello-exterior-2.webp',
    'the-title-adora': '/images/the-title-adora-exterior-9.webp',
}
KIND = {'villa':'Вилла','condo':'Кондоминиум'}
def esc(value): return html.escape(str(value or ''), quote=True)
def load(root):
    spec=importlib.util.spec_from_file_location('mira_catalog_source',root/'scripts/mira-launch-source.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    raw=(root/SOURCE).read_bytes(); rows=module.read_catalog(raw.decode('utf-8'))
    with (root/MASTER).open(encoding='utf-8',newline='') as stream:
        masters={r['source_slug']:r for r in csv.DictReader(stream)}
    if set(masters)!={r['slug'] for r in rows}: raise ValueError('Master and raw catalogue differ; reconcile first')
    projects=[]
    for r in rows:
        slug=r['slug']; m=masters[slug]
        if not re.fullmatch(r'[a-z0-9-]{1,180}',slug): raise ValueError('Unsafe project slug')
        family=m['developer_family'] if m['developer_family']!='unknown' else None
        image=MEDIA.get(slug)
        if image and not (root/image.lstrip('/')).is_file(): raise ValueError('Missing reviewed image: '+image)
        projects.append({'id':slug,'name':r['name'],'district':r.get('district') or None,
          'kind':r.get('kind') or None,'family':family,'familyBasis':m['mapping_basis'],
          'metadataStatus':'inherited_research_not_reverified','sourceRow':int(m['source_row']),
          'image':image,'imageStatus':'archived_visualization' if image else 'not_reviewed',
          'commerciallyEnabled':False,'verifiedAt':None})
    projects.sort(key=lambda p:(not bool(p['image']),-sum(bool(p[k]) for k in ('district','kind','family')),p['name'].casefold(),p['id']))
    return {'schemaVersion':1,'mode':'public_research','source':{'path':SOURCE,
      'sha256':hashlib.sha256(raw).hexdigest(),'recordCount':len(rows),
      'metadataNotice':'Район, тип и группа — сведения исходного каталога, не новая проверка.',
      'commerciallyEnabled':0,'commercialVerificationDate':None},'projects':projects}

def header(title, description='Полный исследовательский каталог Пхукета для агентств недвижимости.'):
    return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'; style-src \'self\'; img-src \'self\'; connect-src \'self\'; object-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>'+esc(title)+' — МИРА</title><meta name="description" content="'+esc(description)+'"><link rel="stylesheet" href="/mira/catalog/catalog.css"><script type="module" src="/mira/catalog/catalog.mjs"></script></head><body><a class="skip" href="#main">К содержанию</a><header class="top"><a class="brand" href="/mira/go/">МИРА<span>Международное направление вашего агентства</span></a><nav><a href="/mira/catalog/">Каталог</a><a href="/mira/documents/">Документы</a><a class="button small" href="/mira/go/#start">Как подключиться</a></nav></header>'

def footer():
    return '''<footer><div><b>МИРА</b><p>Вы ведёте клиента. Мы соединяем вашу работу с зарубежным предложением.</p></div><nav><a href="/mira/documents/agency-agreement.html">Договор с агентством</a><a href="/mira/documents/site-terms.html">Правила каталога</a><a href="/mira/documents/privacy.html">Персональные данные</a><a href="/mira/go/#how">Как работает МИРА</a></nav><p class="fine">Каталог для знакомства с рынком, не оферта. Наличие, цены и условия сотрудничества подтверждаются по запросу. МИРА / WEST EAST TRADE GROUP PTE. LTD.</p></footer><button id="shortlist-open" class="shortlist-open" type="button" hidden>Моя подборка <span id="shortlist-count">0</span></button><dialog id="shortlist"><div class="dialog-head"><h2>Моя подборка</h2><button id="shortlist-close" class="secondary" type="button">Закрыть ×</button></div><p>Выбранные проекты сохраняются в этом браузере. Скачайте список, чтобы вернуться к нему позже. Наличие и условия — по запросу.</p><div id="shortlist-items"></div><div class="actions"><button id="shortlist-download" type="button">Скачать список</button><button id="shortlist-clear" class="secondary" type="button">Очистить</button></div><p id="shortlist-message" role="status"></p></dialog><div id="toast" class="toast" role="status"></div></body></html>'''

def cover(p):
    # Branded artwork is never presented as a photograph of this project.
    return '/images/hero/hero-phuket-' + ('aerial-sunset' if p['kind']=='villa' else 'bay-karst') + '-m.jpg'

def visual(p, detail=False):
    src=p['image'] or cover(p)
    label='Визуализация проекта' if p['image'] else 'МИРА / Пхукет · обложка каталога'
    return '<figure class="'+('detail-image' if detail else 'card-image')+'"><img src="'+esc(src)+'" data-fallback="'+cover(p)+'" alt="'+esc(('Визуализация '+p['name']) if p['image'] else 'Иллюстрация МИРА — Пхукет')+'" width="1200" height="750" '+('fetchpriority="high"' if detail else 'loading="lazy"')+' decoding="async"><figcaption>'+label+'</figcaption></figure>'

def card(p):
    url='/mira/catalog/projects/'+esc(p['id'])+'/'
    return '<article class="project-card"><a class="visual-link" href="'+url+'" aria-label="Подробнее: '+esc(p['name'])+'">'+visual(p)+'</a><div class="card-body"><p class="tag">'+esc(p['district'] or 'Пхукет')+' · '+esc(KIND.get(p['kind'],'Недвижимость'))+'</p><h2><a href="'+url+'">'+esc(p['name'])+'</a></h2><p class="family">'+esc(p['family'] or 'Коллекция проектов Пхукета')+'</p><p class="availability">Наличие и условия — по запросу</p><div class="card-actions"><a href="'+url+'">Подробнее ↗</a><button class="add secondary" data-add="'+esc(p['id'])+'" aria-pressed="false" type="button" disabled>В подборку +</button></div></div></article>'

def detail(p):
    facts=[('Район',p['district'] or 'Пхукет'),('Тип недвижимости',KIND.get(p['kind'],'По запросу')),('Группа / бренд',p['family'] or 'По запросу'),('Наличие и условия','По запросу'),('Цена','Предоставляется после подтверждения интереса'),('Комиссия и регистрация','По согласованным правилам проекта')]
    return header(p['name'])+'<main id="main" class="detail"><a class="back" data-catalog-back href="/mira/catalog/">← Весь каталог Пхукета</a><p class="eyebrow">МИРА / ПХУКЕТ</p><h1>'+esc(p['name'])+'</h1><div class="detail-grid"><div>'+visual(p,True)+'<dl>'+''.join('<div><dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd></div>' for k,v in facts)+'</dl></div><aside class="next-step"><p class="eyebrow">ВАША ПОДБОРКА</p><h2>Начните с проекта.</h2><p>Сохраните его в подборку и сравните с другими вариантами. Наличие, цены и условия работы подтверждаются по запросу.</p><button data-add="'+esc(p['id'])+'" aria-pressed="false" type="button" disabled>В подборку +</button><a class="button secondary" href="/mira/go/#start">Как работать с МИРА</a><p id="registration-gate" class="fine">Регистрация покупателя — после согласования проекта и условий сотрудничества. На этой странице данные покупателей не принимаются.</p><a href="/mira/documents/project-rules.html">Порядок работы с клиентом ↗</a></aside></div><details class="provenance"><summary>О проекте и источниках</summary><p>Исходный реестр WEGC: <code>'+SOURCE+'</code>, строка '+str(p['sourceRow'])+'. Район, тип и группа перенесены из исследовательского каталога; новая внешняя проверка не проводилась. Бренд не устанавливает юридического продавца.</p><p>Визуализации проекта взяты из архива WEGC. Обложки МИРА — редакционные иллюстрации направления, а не изображения конкретного объекта. Наличие, цены, сроки и договорные полномочия подтверждаются отдельно.</p></details></main>'+footer()

def build(root=ROOT):
    data=load(root); out=root/'mira/catalog';out.mkdir(parents=True,exist_ok=True)
    (out/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n','utf-8')
    rows=data['projects']; intro='<main id="main"><section class="catalog-hero"><div><p class="eyebrow">МИРА / ПХУКЕТ</p><h1>Найдите проект<br>под запрос клиента.</h1><p>Виллы и кондоминиумы Пхукета. Выберите район, найдите свой проект и сохраните лучшие варианты.</p></div><div class="catalog-total"><strong>'+str(len(rows))+'</strong><span>проектов в каталоге<br>виллы и кондоминиумы</span></div></section><p class="catalog-note">Наличие и условия — по запросу. <span class="sort-note">Сначала — проекты с визуализациями и наиболее полным описанием.</span></p>'
    controls='''<section aria-label="Фильтры каталога" class="filter-bar"><label class="search-label">Поиск<input id="search" type="search" maxlength="120" placeholder="Название проекта или район" autocomplete="off" disabled></label><label>Район<select id="district" disabled><option value="">Все районы</option></select></label><label>Тип<select id="kind" disabled><option value="">Все типы</option></select></label><label>Группа / бренд<select id="family" disabled><option value="">Все группы</option></select></label><button id="filters-reset" class="secondary" type="button" disabled>Сбросить</button></section><div class="catalog-tools"><p id="result-count" role="status">Проекты Пхукета</p><a href="/mira/catalog/list.html">Алфавитный список всех проектов</a></div><p id="load-error" role="alert" hidden></p>'''
    pagination='''<nav class="pagination" aria-label="Страницы каталога"><button id="prev" class="secondary" type="button" disabled>← Назад</button><span id="page-status"></span><button id="next" class="secondary" type="button" disabled>Дальше →</button></nav><noscript><p>JavaScript выключен. Откройте <a href="list.html">полный алфавитный список</a> — все карточки доступны без скриптов.</p></noscript></main>'''
    (out/'index.html').write_text(header('Все проекты Пхукета')+intro+controls+'<div id="cards" class="cards">'+''.join(card(p) for p in rows[:24])+'</div>'+pagination+footer(),'utf-8')
    (out/'list.html').write_text(header('Алфавитный список Пхукета')+'<main id="main"><a href="/mira/catalog/">← Поиск и фильтры</a><h1>Все проекты Пхукета</h1><p>'+str(len(rows))+' проектов для знакомства с рынком. Наличие и условия — по запросу.</p><ul class="all-projects">'+''.join('<li><a href="projects/'+esc(p['id'])+'/">'+esc(p['name'])+'</a></li>' for p in sorted(rows,key=lambda p:p['name'].casefold()))+'</ul></main>'+footer(),'utf-8')
    for p in rows:
        directory=out/'projects'/p['id'];directory.mkdir(parents=True,exist_ok=True)
        (directory/'index.html').write_text(detail(p),'utf-8')
    report={'source_records':len(rows),'public_cards':len(rows),'exact_image_associations':sum(bool(p['image']) for p in rows),'source_sha256':data['source']['sha256'],'commercially_enabled':0,'mode':'public_research'}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report))
    # Optional isolated public-market expansion; no funnel or auth changes.
    expansion_file = root / 'scripts/mira-build-market-expansion.py'
    if expansion_file.is_file():
        expansion_spec = importlib.util.spec_from_file_location('mira_market_expansion_build', expansion_file)
        expansion_module = importlib.util.module_from_spec(expansion_spec)
        expansion_spec.loader.exec_module(expansion_module)
        expansion_module.build(root)
    return data
if __name__=='__main__':build()
