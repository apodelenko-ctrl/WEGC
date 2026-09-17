"""Browser acceptance through HTTP, real CSP; GET-only public routes, no real signup.
Use --base for own live domain. Run from localhost before public verification.
"""
import argparse,json,os,time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def run(base,out):
 allowed={'127.0.0.1','localhost','wegc.fund','glistening-baklava-2ca58f.netlify.app','bespoke-elf-196a9d1.netlify.app'}
 assert urlsplit(base).hostname in allowed,'Only the owners known sites or localhost may be tested'
 out.mkdir(parents=True,exist_ok=True);checks=[];errors=[];blocked=[]
 def mark(name,details=None):checks.append({'name':name,'passed':True,'details':details})
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH')or None,args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
  def guard(route):
   req=route.request
   if req.method not in ['GET','HEAD'] or urlsplit(req.url).netloc!=urlsplit(base).netloc:
    blocked.append({'method':req.method,'url':req.url.split('?')[0]});route.abort()
   else:route.continue_()
  context.route('**/*',guard)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  csp=[];page.on('console',lambda m:csp.append(m.text)if m.type=='error'and('Content Security Policy'in m.text or'violates'in m.text)else None)
  def goto(path):
   r=page.goto(base+path,wait_until='networkidle',timeout=45000);assert r and r.ok,f'{path}: {r.status if r else None}';return r
  for route in ['start','growth','business']:
   goto(f'/mira/{route}/');assert page.locator('h1').count()==1
   for width in [320,360,390,768,1024,1440]:
    page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
   page.screenshot(path=str(out/f'{route}-desktop.png'))
   page.locator('#brief-form button[type=submit]').click();page.locator('#brief-result').wait_for(state='visible')
   with page.expect_download()as info:page.locator('#download-brief').click()
   download=info.value;content=Path(download.path()).read_text();assert'не отправленная заявка'in content
   page.locator('select[name=market]').select_option('bali');page.locator('#brief-form button[type=submit]').click();assert'Действующего каталога' in page.locator('#brief-result p').inner_text()
   mark('funnel_'+route,{'widths':[320,360,390,768,1024,1440],'local_brief':True,'bali_not_live':True})
  page.set_viewport_size({'width':1440,'height':1000});goto('/mira/phuket/');page.wait_for_selector('.project-card')
  assert page.locator('#total').inner_text()=='618';assert page.locator('.project-card').count()==24
  slugs=set();loops=0
  while True:
   slugs.update(page.locator('.project-card').evaluate_all('(cards)=>cards.map(c=>c.dataset.project)'));loops+=1
   if page.locator('#next').is_disabled():break
   assert loops<30;page.locator('#next').click()
  assert len(slugs)==618,(len(slugs),loops);mark('all_618_paginated',{'pages':loops})
  page.locator('#reset').click();page.locator('#q').fill('the title');page.wait_for_timeout(180);assert page.locator('.project-card').count()>0
  page.locator('.save').first.click();page.locator('#saved').click();assert page.locator('.project-card').count()==1
  with page.expect_download()as info:page.locator('#download-selection').click()
  text=Path(info.value.path()).read_text();assert'не регистрация'in text
  page.locator('.detail-button').first.click();assert page.locator('#detail').is_visible();page.keyboard.press('Escape');assert not page.locator('#detail').is_visible()
  page.locator('#reset').click();page.locator('#q').fill('<script>alert(1)</script>');page.wait_for_timeout(180);assert page.locator('#empty').is_visible()
  page.locator('#empty-reset').click();assert page.locator('.project-card').count()==24
  mark('search_selection_dialog_empty')
  # Controlled negative responses prove UI failure states, not a production outage.
  context.route('**/mira/data/phuket.json',lambda route:route.fulfill(status=503,body='test'))
  goto('/mira/phuket/');page.locator('#catalog-error').wait_for(state='visible');assert page.locator('.project-card').count()==0;mark('catalogue_503_fails_closed')
  context.unroute('**/mira/data/phuket.json');page.locator('#retry').click();page.wait_for_selector('.project-card');mark('catalogue_retry')
  page.set_viewport_size({'width':390,'height':844});goto('/mira/phuket/');page.wait_for_selector('.project-card');assert not page.locator('#filter-options').evaluate('(e)=>e.open');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=str(out/'catalogue-mobile.png'));mark('catalogue_mobile')
  goto('/mira/access/');assert'пока закрыта'in page.locator('main').inner_text();assert page.locator('input').count()==0;mark('registration_honestly_closed')
  goto('/mira/documents/');assert page.locator('.doc-card').count()==9
  for path,magic in [('/mira/documents/downloads/agency-agreement.pdf',b'%PDF'),('/mira/documents/downloads/agency-agreement.docx',b'PK')]:
   response=context.request.get(base+path);assert response.ok and response.body().startswith(magic),(path,response.status)
  goto('/mira/documents/agency-agreement.html');assert'Приложение 5' in page.locator('main').inner_text();mark('nine_documents_and_downloads')
  goto('/mira/variants/');assert page.locator('.variant-card').count()==3;goto('/mira/expo/');assert page.locator('.expo-preview').evaluate('(e)=>e.complete&&e.naturalWidth>0');mark('variants_and_banner')
  # Optional motion respects reduced-motion and explicit pause.
  page.emulate_media(reduced_motion='no-preference');goto('/mira/start/');assert page.locator('body').evaluate('(e)=>e.classList.contains("animate")')
  page.locator('#motion-toggle').click();assert not page.locator('body').evaluate('(e)=>e.classList.contains("animate")');page.emulate_media(reduced_motion='reduce');assert not page.locator('body').evaluate('(e)=>e.classList.contains("animate")');mark('motion_pause_and_reduced')
  assert not errors,errors;assert not csp,csp;assert not blocked,blocked
  browser.close()
 report={'base':base,'scope':'real HTTP/CSP public pages; negative catalogue fixtures; no real registration or third-party submission','checks':checks,'page_errors':errors,'csp_errors':csp,'blocked_requests':blocked,'live_registration_tested':False}
 (out/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'passed':len(checks),'base':base,'live_registration_tested':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base',default='http://127.0.0.1:8765');ap.add_argument('--out',type=Path,default=Path('/tmp/mira-browser'));a=ap.parse_args();run(a.base.rstrip('/'),a.out)
