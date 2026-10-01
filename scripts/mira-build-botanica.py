#!/usr/bin/env python3
"""Curated Botanica presentation; stable source IDs and project-specific media."""
import json,re,html
from pathlib import Path
CSS='<link rel="stylesheet" href="/mira/catalog/botanica/botanica.css?v=20260927">'
E=lambda value:html.escape(str(value),quote=True)

def feature(english=False,compact=False):
    title='Botanica. A different way to live in Phuket.' if english else 'Botanica. Свой ритм жизни на Пхукете.'
    copy=('Explore pool villas and Hythe residences. Compare locations, architecture and layouts — our team can arrange current offers and a viewing.' if english else 'Виллы с собственными бассейнами и резиденции Hythe. Сравните районы, архитектуру и планировки — мы поможем запросить предложение и организовать просмотр.')
    button='Explore five projects' if english else 'Посмотреть 5 проектов'
    eyebrow = 'BOTANICA / PHUKET' if english else 'BOTANICA / ПХУКЕТ'
    zone = 'Zone C1' if english else 'зона C1'
    return '<!-- BOTANICA-FEATURE --><section id="botanica" class="botanica-feature'+(' botanica-feature--compact' if compact else '')+'" aria-label="Botanica"><a class="botanica-feature__image" href="/mira/catalog/botanica/"><img src="/images/projects/botanica/grand-avenue-3.jpg" alt="Botanica Grand Avenue · '+zone+'" width="1600" height="880" loading="lazy" decoding="async"><span>Grand Avenue · '+zone+'</span></a><div class="botanica-feature__copy"><p class="botanica-eyebrow">'+eyebrow+'</p><h2>'+title+'</h2><p>'+copy+'</p><a class="botanica-link" href="/mira/catalog/botanica/">'+button+' ↗</a></div></section><!-- /BOTANICA-FEATURE -->'

def insert_feature(path,anchor,english=False,compact=False):
    text=path.read_text()
    fragment=feature(english,compact)
    if '<!-- BOTANICA-FEATURE -->' in text:
        text=re.sub(r'<!-- BOTANICA-FEATURE -->.*?<!-- /BOTANICA-FEATURE -->',lambda _:fragment,text,flags=re.S)
    else:
        if anchor not in text:raise ValueError('Missing Botanica placement: '+str(path))
        text=text.replace(anchor,fragment+'\n'+anchor,1)
    if CSS not in text:text=text.replace('</head>',CSS+'</head>',1)
    path.write_text(text)

def build(root,data,header,footer,card):
    source=json.loads((root/'mira/catalog/botanica/projects.json').read_text())['projects']
    records={p['id']:p for p in data['projects']}
    selected=[records[p['id']] for p in source]
    title='Botanica на Пхукете — виллы и резиденции'
    head=header(title,'Пять проектов Botanica: Grand Avenue, Hythe, MontAzure, Four Seasons и Foresta II. Изображения проектов, районы, форматы и запрос предложения.').replace('</head>',CSS+'</head>').replace('<body>','<body class="botanica-page">')
    cards=''.join(card(p) for p in selected)
    # Existing card links and shortlist remain usable; no duplicate catalogue IDs.
    body='<main id="main" class="botanica-collection"><a class="back" href="/mira/catalog/">← Каталог Пхукета</a><section class="botanica-heading"><p class="eyebrow">BOTANICA / ПХУКЕТ</p><h1>Botanica на Пхукете.</h1><p>От вилл с собственными бассейнами до апартаментов Hythe. Пять проектов, разные районы и архитектура — с поддержкой команды МИРА на пути к сделке.</p></section><div class="cards botanica-cards">'+cards+'</div><section class="botanica-next"><h2>Какой Пхукет нужен вашему клиенту?</h2><p>Расскажите о подходящем формате и районе. Запросим варианты у застройщика, планировки и условия, поможем организовать просмотр.</p><a class="button" href="https://pilot.wegc.fund/mira/request/">Запросить подборку Botanica</a></section><p class="fine">Материалы проектов: Botanica Luxury Villas. Визуализации могут отличаться от готового объекта.</p></main>'
    (root/'mira/catalog/botanica/index.html').write_text(head+body+footer())
    insert_feature(root/'mira/index.html','<section class="fieldops">')
    insert_feature(root/'index.html','<!-- CATALOG -->',english=True)
    insert_feature(root/'mira/catalog/index.html','<section aria-label="Фильтры каталога"',compact=True)

