#!/usr/bin/env python3
"""Original vector exhibition creative and exact QR. No generated/scanned QR guesses.

Default builds SVG assets without external requests. --downloads adds vector PDFs
and PNG previews. Working dimensions need owner/printer approval before printing.
"""
from pathlib import Path
import argparse,html,json
ROOT=Path(__file__).resolve().parents[1]
URL='https://wegc.fund/mira/go/'
RED='#e9273b';INK='#171b22'
def matrix():
 import qrcode
 q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=4,box_size=10)
 q.add_data(URL);q.make(fit=True);return q.get_matrix()
def qr_svg(x,y,size):
 m=matrix();step=size/len(m);path=' '.join(f'M{x+c*step:.4f},{y+r*step:.4f}h{step:.4f}v{step:.4f}h-{step:.4f}z' for r,row in enumerate(m) for c,on in enumerate(row) if on)
 return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="white"/><path d="{path}" fill="black"/>'
def text(x,y,value,size=30,color=INK,weight=400):
 return f'<text x="{x}" y="{y}" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(value)}</text>'
def art_svg(x,y,scale=1):
 return f'''<g transform="translate({x} {y}) scale({scale})"><path d="M0 570L490 485V700H0Z" fill="{RED}"/><rect x="155" y="75" width="255" height="490" fill="#af1929"/><rect x="170" y="90" width="225" height="475" fill="#d7edf0"/><path d="M170 365H395V565H170Z" fill="#72bdb5"/><path d="M170 445L395 405V565H170Z" fill="#e2dccc"/><path d="M263 312L389 290V410L263 430Z" fill="white"/><path d="M278 336L374 320V388L278 406Z" fill="#568d91"/><path d="M264 306L389 284L404 300L268 327Z" fill="#eeeae3"/><path d="M345 315Q335 250 353 194" fill="none" stroke="#1b715b" stroke-width="8"/><path d="M353 194Q307 180 300 210Q331 192 353 200Q379 169 400 187Q375 190 354 202Q389 207 398 235Q369 212 352 204Q325 223 304 247Q310 215 345 202Z" fill="#1b715b"/><path d="M155 75L315 35V615L155 565Z" fill="{RED}"/><path d="M315 35L322 40V615L315 615Z" fill="#ba1c2d"/><rect x="288" y="316" width="7" height="55" rx="3" fill="white"/>{text(190,305,'М',96,'#ffabb3',700)}<path d="M26 571L129 546L142 607L41 635Z" fill="white"/><path d="M62 608L95 578M72 579L96 576L95 602" fill="none" stroke="{RED}" stroke-width="5"/></g>'''
def banner_svg(vertical=False):
 if vertical:
  w,h=850,2000
  body=f'<rect width="850" height="2000" fill="white"/>'+text(65,120,'МИРА',64,INK,700)+text(65,184,'ДЛЯ АГЕНТСТВ НЕДВИЖИМОСТИ',20,RED,700)
  for y,s in [(315,'Откройте'),(412,'клиентам'),(509,'зарубежную'),(606,'недвижимость.')]:body+=text(65,y,s,76,RED if y==509 else INK,700)
  body+=text(65,690,'Ваш клиент. Ваш бренд.',34,INK,700)+text(65,743,'Новое направление — Пхукет.',27)
  body+=art_svg(140,760,1.08)
  body+='<rect x="0" y="1518" width="850" height="482" fill="#171b22"/>'+qr_svg(61,1570,294)
  for y,s in [(1620,'Сканируйте.'),(1670,'Смотрите проекты.'),(1720,'Добавляйте'),(1770,'новое направление.')]:body+=text(391,y,s,29,'white',700)
  body+=text(391,1840,'wegc.fund/mira/go',23,'#b9c4cc')+text(65,1935,'Каталог открыт. Рабочее подключение — после согласования.',18,'#b9c4cc')
 else:
  w,h=1920,1080
  body=f'<rect width="1920" height="1080" fill="white"/>'+text(90,119,'МИРА',72,INK,700)+text(92,185,'ДЛЯ АГЕНТСТВ НЕДВИЖИМОСТИ',23,RED,700)
  for y,s in [(325,'Откройте клиентам'),(440,'зарубежную'),(555,'недвижимость.')]:body+=text(87,y,s,98,RED if y==440 else INK,700)
  body+=text(94,635,'Ваш клиент. Ваш бренд. Новое направление — Пхукет.',28)
  body+=art_svg(1260,77,1.11)
  body+='<rect x="0" y="766" width="1920" height="314" fill="#171b22"/>'+qr_svg(95,795,254)
  body+=text(392,872,'Сканируйте — откройте каталог.',46,'white',700)+text(395,935,'Выберите проекты. Подготовьте подключение агентства.',27,'#b9c4cc')+text(395,1000,'wegc.fund/mira/go',25,'white')
  body+=text(1310,1028,'Рабочее подключение — после согласования.',17,'#b9c4cc')
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>МИРА — откройте клиентам зарубежную недвижимость</title>{body}</svg>'
def pdf(svg,path,width,height):
 import cairosvg
 cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(path),output_width=width,output_height=height)
def build(downloads=False,root=ROOT):
 out=root/'mira/exhibition';out.mkdir(parents=True,exist_ok=True)
 for name,vertical in [('banner-landscape',False),('banner-rollup',True)]:
  svg=banner_svg(vertical);(out/(name+'.svg')).write_text(svg,'utf-8')
  if downloads:
   import cairosvg
   # SVG uses 96px/in; requested vector rollup physical size is 85x200cm.
   w,h=(850/25.4*96,2000/25.4*96) if vertical else (1920,1080)
   pdf(svg,out/(name+'.pdf'),w,h)
   cairosvg.svg2png(bytestring=svg.encode(),write_to=str(out/(name+'.png')),output_width=850 if vertical else 1920,output_height=2000 if vertical else 1080)
 m=matrix();n=len(m);(out/'qr.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{n*10}" height="{n*10}" viewBox="0 0 {n*10} {n*10}">'+qr_svg(0,0,n*10)+'</svg>')
 if downloads:
  import qrcode
  qrcode.make(URL,error_correction=qrcode.constants.ERROR_CORRECT_M,border=4).save(out/'qr.png')
 manifest={'destination':URL,'date_context':'25 September 2026 supplied by owner; organizer not independently verified','creative':'original vector artwork; no third-party imagery','owner_approved':False,'print_approved':False,'working_formats':['1920x1080 digital','85x200cm roll-up vector PDF'],'print_gate':'Confirm actual placement dimensions, bleed/safe area, color profile and printer proof. No claim of internet-ad labeling clearance.'}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 page='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>МИРА — выставочный баннер и QR</title><link rel="stylesheet" href="/mira/catalog/catalog.css"></head><body><main><a href="/mira/launch/">← Материалы запуска</a><p class="eyebrow">К ВЫСТАВКЕ 25 СЕНТЯБРЯ / НА СОГЛАСОВАНИЕ</p><h1>Откройте клиентам<br>зарубежную недвижимость.</h1><p>Продающий креатив, оригинальная векторная иллюстрация и проверяемый QR. Прежние дизайны сохранены.</p><figure class="detail-image"><img src="banner-landscape.svg" alt="Баннер МИРА с открытой дверью и QR" width="1920" height="1080"></figure><div class="actions"><a class="button" href="banner-landscape.png">Баннер PNG 1920×1080</a><a class="button secondary" href="banner-landscape.pdf">Векторный PDF</a><a class="button secondary" href="banner-rollup.pdf">Roll-up 85×200 см</a><a class="button secondary" href="qr.svg">QR SVG</a><a class="button secondary" href="qr.png">QR PNG</a></div><p>QR ведёт на <a href="/mira/go/">wegc.fund/mira/go/</a> — постоянный собственный адрес, без стороннего сервиса QR.</p><p class="notice">Это рабочие форматы для утверждения, не команда в печать. Размер места, вылеты, безопасные поля, цветовой профиль и требования типографии нужно подтвердить. Дата 25 сентября указана владельцем; организатор отдельно не проверен. Для внешнего интернет-размещения отдельно проверяются обязательные рекламные сведения и маркировка.</p><p><a href="banner-rollup.svg">Посмотреть вертикальный макет</a> · <a href="/mira/documents/">Договор и документы</a></p></main></body></html>'''
 (out/'index.html').write_text(page,'utf-8');print(json.dumps(manifest));return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--downloads',action='store_true');a=p.parse_args();build(a.downloads)
