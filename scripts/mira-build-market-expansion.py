#!/usr/bin/env python3
"""Add Bali/Dubai public research pages without touching auth, funnel or Phuket data.
Default output can contain explicitly labelled typographic covers. Use
--require-project-images for a media-complete release. This command never deploys.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit
import argparse,hashlib,html,importlib.util,json,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE='project-bible/mira/data/markets/dubai-bali-30.json'
MARKETS={'phuket':('Пхукет','Таиланд','/mira/catalog/'),'bali':('Бали','Индонезия','/mira/catalog/bali/'),'dubai':('Дубай','ОАЭ','/mira/catalog/dubai/')}
TYPES={'apartment':'Апартаменты','studio':'Студии','villa':'Виллы','townhouse':'Таунхаусы','penthouse':'Пентхаусы','duplex':'Дуплексы','hotel_suite':'Гостиничные номера','serviced_apartment':'Сервисные апартаменты'}
E=lambda s:html.escape(str(s or ''),quote=True)
def validate(d):
 rows=d.get('projects');assert d.get('schemaVersion')==1 and isinstance(rows,list) and len(rows)==30,'Expected 30 research projects'
 assert Counter(p['market'] for p in rows)=={'bali':15,'dubai':15}
 ids=set()
 for p in rows:
  assert re.fullmatch(p['market']+r'-[a-z0-9-]{1,170}',p['id']) and p['id'] not in ids;ids.add(p['id'])
  assert p['commerciallyEnabled'] is False and p['legalSeller'] is None and p['availabilityStatus']=='on_request'
  assert not any(k in p for k in ['price','roi','commission','availableUnits','bookingEnabled','priceFrom'])
  assert p['propertyTypes'] and all(t in TYPES for t in p['propertyTypes'])
  assert len(set(p['propertyTypes']))==len(p['propertyTypes'])
  u=urlsplit(p['projectSource']['url']);assert u.scheme=='https' and u.hostname and not u.username and not u.password
  for k in ['name','developerBrand','district','summary']:assert isinstance(p[k],str) and 0<len(p[k])<1500
 return rows
def nav(m):
 return '<nav class="market-switch" aria-label="Направления недвижимости" data-mira-markets="v1">'+''.join('<a href="'+v[2]+'"'+(' aria-current="page"' if k==m else '')+'><span><strong>'+v[0]+'</strong><small>'+v[1]+'</small></span><span class="market-count">'+str(618 if k=='phuket' else 15)+' проектов ↗</span></a>' for k,v in MARKETS.items())+'</nav>'
def market_from_path(p):
 s=str(p).replace('\\','/')
 return 'bali' if '/bali/' in s or '/projects/bali-' in s else ('dubai' if '/dubai/' in s or '/projects/dubai-' in s else 'phuket')
def integrate_text(text,market):
 if 'data-mira-markets="v1"' not in text:text=text.replace('</header>','</header>'+nav(market),1)
 if '/mira/catalog/markets/markets.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/mira/catalog/markets/markets.css"></head>',1)
 text=text.replace('src="/mira/catalog/catalog.mjs"','src="/mira/catalog/markets/controller.mjs"')
 # A static back link still restores filters if detail-page JavaScript never loads.
 for path in ['/mira/catalog/','/mira/catalog/bali/','/mira/catalog/dubai/']:
  text=text.replace('data-catalog-back href="'+path+'"','data-catalog-back href="'+path+'?restore=1"')
 return text
def approved_image(root,p,approvals):
 a=approvals.get(p['id'])
 if not a:return None
 assert a.get('approvedForPublication') is True and a.get('visualReviewed') is True and a.get('rightsReference'),'Incomplete media approval: '+p['id']
 expected='/images/mira-markets/'+p['market']+'/'+p['slug']+'.webp';assert a.get('path')==expected
 file=root/expected.lstrip('/');assert file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest()==a.get('sha256'),'Media hash mismatch'
 return expected
def public_record(root,p,approvals):
 image=approved_image(root,p,approvals)
 return {'id':p['id'],'name':p['name'],'market':p['market'],'countryCode':p['countryCode'],'district':p['district'],'kind':'villa' if set(p['propertyTypes'])<= {'villa','townhouse'} else 'condo','propertyTypes':p['propertyTypes'],'typeLabel':' / '.join(TYPES[t] for t in p['propertyTypes']),'family':p['developerBrand'],'summary':p['summary'],'amenities':p['amenities'],'sourceURL':p['projectSource']['url'],'sourceRole':p['projectSource']['role'],'researchReviewedAt':p['reviewedAt'],'verifiedAt':None,'image':image,'imageStatus':'reviewed_project_media' if image else 'typographic_market_cover','imageCaption':('Материал проекта · '+p['developerBrand']) if image else None,'commerciallyEnabled':False,'availabilityStatus':'on_request','legalSeller':None,'metadataStatus':'source_linked_project_description'}
def cover(p,detail=False):
 return '<figure class="market-cover '+E(p['market'])+'"><span class="cover-brand">МИРА / НОВОЕ НАПРАВЛЕНИЕ</span><span class="cover-market">'+MARKETS[p['market']][0]+'</span><span class="cover-type">'+E(p['typeLabel'])+'</span><figcaption>Обложка направления · не изображение проекта</figcaption></figure>'
def visual(p,detail=False):
 if not p['image']:return cover(p,detail)
 return '<figure class="market-visual"><img src="'+E(p['image'])+'" alt="'+E(p['name'])+' — материал проекта" width="1400" height="875" '+('fetchpriority="high"' if detail else 'loading="lazy"')+' decoding="async"><figcaption>'+E(p['imageCaption'])+'</figcaption></figure><template class="image-recovery">'+cover(p,detail)+'</template>'
def card(p):
 href='/mira/catalog/projects/'+p['id']+'/'
 return '<article class="project-card" data-market="'+p['market']+'"><a class="visual-link" href="'+href+'" aria-label="Подробнее: '+E(p['name'])+'">'+visual(p)+'</a><div class="card-body"><p class="tag">'+E(p['district'])+' · '+E(p['typeLabel'])+'</p><h2><a href="'+href+'">'+E(p['name'])+'</a></h2><p class="family">'+E(p['family'])+'</p><p class="market-card-summary">'+E(p['summary'])+'</p><p class="availability">Наличие и условия — по запросу</p><div class="card-actions"><a href="'+href+'">Подробнее ↗</a><button class="add secondary" data-add="'+p['id']+'" aria-pressed="false" type="button" disabled>В подборку +</button></div></div></article>'
def build(root=ROOT,require_images=False,integrate=True):
 root=Path(root); raw=(root/SOURCE).read_bytes(); source=json.loads(raw); research=validate(source)
 pfile=root/'mira/catalog/data.json';before=pfile.read_bytes();phuket=json.loads(before);assert len(phuket['projects'])==618,'Phuket baseline must stay 618'
 spec=importlib.util.spec_from_file_location('mira_existing_builder',root/'scripts/mira-build-catalog.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 af=root/'mira/catalog/markets/media-approved.json'; approvals=json.loads(af.read_text()) if af.exists() else {}
 rows=[public_record(root,p,approvals) for p in research]
 if require_images and any(p['image'] is None for p in rows):raise ValueError('Release media incomplete: '+str(sum(p['image'] is None for p in rows))+' projects')
 out=root/'mira/catalog/markets';out.mkdir(parents=True,exist_ok=True)
 data={'schemaVersion':1,'mode':'public_research','source':{'recordCount':30,'commerciallyEnabled':0,'researchDate':source['researchDate'],'sourceSHA256':hashlib.sha256(raw).hexdigest()},'projects':rows}
 (out/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 def head(title,m,desc):return integrate_text(old.header(title,desc),m)
 for market in ['bali','dubai']:
  selected=[p for p in rows if p['market']==market];name=MARKETS[market][0];dest=root/MARKETS[market][2].lstrip('/');dest.mkdir(parents=True,exist_ok=True)
  intro='<main id="main"><section class="catalog-hero"><div><p class="eyebrow">МИРА / '+name.upper()+'</p><h1>Новая география.<br>Тот же ваш клиент.</h1><p>Знакомьтесь с проектами, сравнивайте форматы и собирайте предварительную подборку.</p></div><div class="catalog-total"><strong>15</strong><span>проектов в коллекции<br>'+name+'</span></div></section><p class="catalog-note">Подбор по запросу. Условия работы по выбранному проекту согласуются отдельно.</p>'
  controls='<section aria-label="Фильтры каталога" class="filter-bar"><label class="search-label">Поиск<input id="search" type="search" maxlength="120" placeholder="Проект, район или застройщик" autocomplete="off" disabled></label><label>Район<select id="district" disabled><option value="">Все районы</option></select></label><label>Тип<select id="kind" disabled><option value="">Все типы</option></select></label><label>Группа / бренд<select id="family" disabled><option value="">Все группы</option></select></label><button id="filters-reset" class="secondary" type="button" disabled>Сбросить</button></section><div class="catalog-tools"><p id="result-count" role="status">15 проектов</p><a href="'+MARKETS[market][2]+'list.html">Все проекты направления</a></div><p id="load-error" role="alert" hidden></p>'
  ending='<nav class="pagination" aria-label="Страницы каталога"><button id="prev" class="secondary" type="button" disabled>← Назад</button><span id="page-status"></span><button id="next" class="secondary" type="button" disabled>Дальше →</button></nav><noscript><p>Карточки доступны без JavaScript; интерактивную подборку можно составить после его включения.</p></noscript></main>'
  (dest/'index.html').write_text(head(name+' — каталог проектов',market,'Проекты '+name+' для агентств недвижимости: застройщики, форматы и предварительный подбор.')+intro+controls+'<div id="cards" class="cards">'+''.join(card(p) for p in selected)+'</div>'+ending+old.footer())
  (dest/'list.html').write_text(head(name+' — все проекты',market,'Алфавитный список коллекции.')+'<main id="main"><a href="'+MARKETS[market][2]+'">← Поиск и фильтры</a><h1>'+name+': все проекты</h1><ul class="all-projects">'+''.join('<li><a href="/mira/catalog/projects/'+p['id']+'/">'+E(p['name'])+'</a> — '+E(p['family'])+'</li>' for p in sorted(selected,key=lambda p:p['name'].casefold()))+'</ul></main>'+old.footer())
 for p in rows:
  m=p['market'];name=MARKETS[m][0];dest=root/'mira/catalog/projects'/p['id'];dest.mkdir(parents=True,exist_ok=True)
  facts=[('Направление',MARKETS[m][1]+' / '+name),('Район',p['district']),('Форматы',p['typeLabel']),('Девелопер / бренд',p['family']),('Наличие и цена','По запросу'),('Условия работы','Согласуются по проекту')]
  body='<main id="main" class="detail"><a class="back" data-catalog-back href="'+MARKETS[m][2]+'">← '+name+': каталог</a><p class="eyebrow">МИРА / '+name.upper()+'</p><h1>'+E(p['name'])+'</h1><p class="project-intro">'+E(p['summary'])+'</p><div class="detail-grid"><div>'+visual(p,True)+'<ul class="market-amenities">'+''.join('<li>'+E(a)+'</li>' for a in p['amenities'])+'</ul><dl>'+''.join('<div><dt>'+E(k)+'</dt><dd>'+E(v)+'</dd></div>' for k,v in facts)+'</dl></div><aside class="next-step"><p class="eyebrow">ВАША ПОДБОРКА</p><h2>Сохраните проект.</h2><p>Сравните его с другими вариантами. Наличие и порядок работы уточняются перед предложением клиенту.</p><button data-add="'+p['id']+'" aria-pressed="false" disabled type="button">В подборку +</button><a class="button secondary" href="'+MARKETS[m][2]+'">Другие проекты: '+name+'</a><p id="registration-gate" class="fine">Новый рынок: условия сотрудничества по проекту согласуются отдельно. Данные покупателей здесь не принимаются.</p><a href="/mira/documents/project-rules.html">Порядок работы с проектом ↗</a></aside></div><details class="provenance"><summary>Описание и источник</summary><p>Описание подготовлено по открытым материалам проекта. Проверка описания: '+E(p['researchReviewedAt'])+'. Это не подтверждение актуального наличия или агентского договора МИРА.</p><p><a class="source-link" href="'+E(p['sourceURL'])+'" target="_blank" rel="noopener noreferrer">'+('Публикация агентства ↗' if p['sourceRole']=='broker_catalogue' else 'Первоисточник проекта ↗')+'</a></p><p>Бренд, оператор и юридический продавец могут различаться. Сторона сделки и условия подтверждаются отдельно.</p></details></main>'
  (dest/'index.html').write_text(head(p['name'],m,p['summary'])+body+old.footer())
 changed=[]
 if integrate:
  for f in (root/'mira/catalog').rglob('*.html'):
   text=f.read_text();new=integrate_text(text,market_from_path('/'+f.relative_to(root).as_posix()))
   if text!=new:f.write_text(new);changed.append(f.relative_to(root).as_posix())
 assert pfile.read_bytes()==before,'Phuket data changed'
 report={'newProjects':30,'markets':{'phuket':618,'bali':15,'dubai':15},'combinedProjects':648,'reviewedProjectImages':sum(bool(p['image']) for p in rows),'typographicCovers':sum(not p['image'] for p in rows),'newDetailPages':30,'newMarketIndexPages':4,'existingHTMLIntegrated':len(changed),'commerciallyEnabled':0,'deployed':False,'phuketDataSHA256':hashlib.sha256(before).hexdigest(),'researchSHA256':hashlib.sha256(raw).hexdigest(),'requiresMediaCompletion':any(p['image'] is None for p in rows)}
 (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--require-project-images',action='store_true');p.add_argument('--no-integrate',action='store_true');a=p.parse_args();build(a.root,a.require_project_images,not a.no_integrate)
