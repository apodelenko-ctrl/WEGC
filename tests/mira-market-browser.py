#!/usr/bin/env python3
"""Read-only actual-HTTP acceptance for the market addon. Run locally after integration.
Never sends user data; never tests or changes Access/Worker/admin functionality.
"""
from pathlib import Path
from urllib.parse import urlsplit
import argparse,json,os
from playwright.sync_api import sync_playwright,expect

def run(base,out):
 assert urlsplit(base).hostname in {'localhost','127.0.0.1','wegc.fund'}
 out.mkdir(parents=True,exist_ok=True)
 report={'base':base,'passed':False,'checks':[],'errors':[],'unexpectedRequests':[],'registrationTested':False}
 def ok(name,**extra):report['checks'].append({'name':name,'passed':True,**extra})
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  ctx=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
  def guard(route):
   req=route.request
   if req.method not in ['GET','HEAD'] or urlsplit(req.url).netloc!=urlsplit(base).netloc or '/mira/api/' in req.url:
    report['unexpectedRequests'].append({'method':req.method,'url':req.url.split('?')[0]});route.abort()
   else:route.continue_()
  ctx.route('**/*',guard);page=ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' and 'Content Security Policy' in m.text else None)
  try:
   def goto(path):
    r=page.goto(base+path,wait_until='networkidle');assert r and r.ok;return r
   links=set()
   def inspect_page():
    for img in page.locator('img').all():
     img.scroll_into_view_if_needed();expect(img).to_have_js_property('complete',True);assert img.evaluate('(i)=>i.naturalWidth>0'),img.get_attribute('src')
    links.update(page.locator('a[href^="/"]').evaluate_all('(els)=>els.map(a=>a.getAttribute("href").split("#")[0])'))
   for market in ['bali','dubai']:
    goto('/mira/catalog/'+market+'/');expect(page.locator('#search')).to_be_enabled();expect(page.locator('.market-switch a')).to_have_count(3);expect(page.locator('#cards .project-card')).to_have_count(15)
    for width in [320,360,390,600,768,1024,1440]:
     page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(market,width)
    inspect_page();page.screenshot(path=str(out/(market+'-desktop.png')),full_page=True)
    page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/(market+'-mobile.png')))
    page.locator('#cards [data-add]').first.click();page.locator('#shortlist-open').click();expect(page.locator('#shortlist')).to_be_visible();page.keyboard.press('Escape');expect(page.locator('#shortlist')).not_to_be_visible()
    page.locator('.market-switch a[href="/mira/catalog/"]').click();expect(page.locator('#result-count')).to_contain_text('618');page.locator('.market-switch a[href="/mira/catalog/'+market+'/"]').click();expect(page.locator('#cards .project-card')).to_have_count(15)
    for field,prop in [('district','district'),('family','family')]:
     value=page.locator('#'+field+' option').nth(1).get_attribute('value');page.locator('#'+field).select_option(value);expect(page.locator('#cards .project-card').first).to_be_visible();assert value in page.locator('#cards').inner_text();page.locator('#filters-reset').click()
    ok(market+'_cards_navigation_selection',records=15)
   goto('/mira/catalog/bali/');expect(page.locator('#search')).to_be_enabled();page.locator('#kind').select_option('hotel_suite');expect(page.locator('#cards .project-card')).to_have_count(1);expect(page.locator('#cards')).to_contain_text('SOMOSHOTELS');ok('hotel_format_not_condo')
   page.locator('#filters-reset').click();page.locator('#search').fill('INDARI');expect(page.locator('#cards .project-card')).to_have_count(1);page.locator('#cards h2 a').click();expect(page.locator('h1')).to_have_text('INDARI by BALIX');page.locator('[data-catalog-back]').click();expect(page.locator('#search')).to_have_value('INDARI');ok('detail_back_preserves_country_and_search')
   # Back links must not depend on fetching either catalogue feed on the detail page.
   page.locator('#cards h2 a').click();ctx.route('**/mira/catalog/**/data.json',lambda route:route.abort());ctx.route('**/mira/catalog/data.json',lambda route:route.abort())
   page.reload(wait_until='networkidle');expect(page.locator('[data-catalog-back]')).to_have_attribute('href','/mira/catalog/bali/?q=INDARI')
   ctx.unroute('**/mira/catalog/**/data.json');ctx.unroute('**/mira/catalog/data.json');page.locator('[data-catalog-back]').click();expect(page.locator('#search')).to_have_value('INDARI');ok('detail_back_independent_of_feed_loading')
   goto('/mira/catalog/');expect(page.locator('#search')).to_be_enabled();expect(page.locator('#result-count')).to_contain_text('618');page.locator('#cards [data-add]').first.click();page.locator('#shortlist-open').click();expect(page.locator('#shortlist-items')).to_contain_text('Бали');expect(page.locator('#shortlist-items')).to_contain_text('Дубай')
   with page.expect_download() as event:page.locator('#shortlist-download').click()
   body=Path(event.value.path()).read_text('utf-8-sig');assert 'Пхукет' in body and 'Бали' in body and 'Дубай' in body and 'Не отправлена' in body
   page.locator('#shortlist-items [data-remove]').first.click();expect(page.locator('#shortlist-items [data-remove]')).to_have_count(2);page.reload(wait_until='networkidle');page.locator('#shortlist-open').click();expect(page.locator('#shortlist-items [data-remove]')).to_have_count(2);page.locator('#shortlist-clear').click();expect(page.locator('#shortlist-items [data-remove]')).to_have_count(0);ok('mixed_country_shortlist_and_download')
   goto('/mira/catalog/dubai/?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E');expect(page.locator('#search')).to_be_enabled();expect(page.locator('#cards .project-card')).to_have_count(0);page.locator('#filters-reset').click();expect(page.locator('#cards .project-card')).to_have_count(15);ok('untrusted_query_reset')
   feed=ctx.request.get(base+'/mira/catalog/markets/data.json').json();assert len(feed['projects'])==30
   for p in feed['projects']:
    goto('/mira/catalog/projects/'+p['id']+'/');expect(page.locator('h1')).to_have_text(p['name']);expect(page.locator('[data-add]').first).to_be_enabled();inspect_page()
    for width in [390,1440]:
     page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(p['id'],width)
    if p['id'] in ['bali-magnum-resort-berawa','dubai-sobha-one']:
     page.screenshot(path=str(out/(p['market']+'-project-desktop.png')),full_page=True)
     page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/(p['market']+'-project-mobile.png')),full_page=True)
    page.locator('[data-add]').first.click();expect(page.locator('[data-add]').first).to_have_attribute('aria-pressed','true');page.reload(wait_until='networkidle');expect(page.locator('[data-add]').first).to_have_attribute('aria-pressed','true');page.locator('[data-add]').first.click();expect(page.locator('[data-add]').first).to_have_attribute('aria-pressed','false');page.locator('[data-catalog-back]').click();expect(page.locator('#result-count')).to_contain_text('15')
    if p['image']:
     r=ctx.request.get(base+p['image']);assert r.ok and r.headers.get('content-type','').startswith('image/'),p['id']
   ok('all_30_detail_urls_and_available_media',browserDetails=30,detailWidths=[390,1440])
   for href in sorted(links):
    r=ctx.request.get(base+href);assert r.ok,(href,r.status)
   ok('internal_links_resolve',links=len(links))
   # New feed failures must preserve the independent 618-record Phuket feed and saved expansion IDs.
   goto('/mira/catalog/bali/');expect(page.locator('#search')).to_be_enabled();page.locator('#cards [data-add]').first.click();saved=page.evaluate("localStorage.getItem('mira-research-selection-v1')")
   for status,body in [(503,'unavailable'),(200,'{}')]:
    ctx.route('**/mira/catalog/markets/data.json',lambda route,_request=None,status=status,body=body:route.fulfill(status=status,content_type='application/json',body=body))
    goto('/mira/catalog/');expect(page.locator('#search')).to_be_enabled();expect(page.locator('#result-count')).to_contain_text('618');page.locator('#cards [data-add]').first.click();assert json.loads(saved)[0] in json.loads(page.evaluate("localStorage.getItem('mira-research-selection-v1')"))
    goto('/mira/catalog/bali/');expect(page.locator('#search')).to_be_disabled();expect(page.locator('#load-error')).to_be_visible();ctx.unroute('**/mira/catalog/markets/data.json')
   ok('expansion_outage_preserves_phuket_and_selection')
   fallback=browser.new_context();fallback.route('**/*',guard);fallback.add_init_script("const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(this===localStorage)throw new DOMException('blocked','QuotaExceededError');return original.call(this,k,v);};");p3=fallback.new_page();p3.goto(base+'/mira/catalog/bali/',wait_until='networkidle');expect(p3.locator('#search')).to_be_enabled();p3.locator('#cards [data-add]').first.click();p3.goto(base+'/mira/catalog/dubai/',wait_until='networkidle');expect(p3.locator('#shortlist-open')).to_be_visible();p3.locator('#shortlist-open').click();expect(p3.locator('#shortlist-items')).to_contain_text('Бали');fallback.close();ok('session_storage_fallback_across_markets')
   nojs=browser.new_context(java_script_enabled=False);nojs.route('**/*',guard);p2=nojs.new_page();p2.goto(base+'/mira/catalog/bali/',wait_until='networkidle');expect(p2.locator('.project-card')).to_have_count(15);expect(p2.locator('[data-add]').first).to_be_disabled();nojs.close();ok('no_js_static_catalogue')
   assert not report['errors'],report['errors'];assert not report['unexpectedRequests'],report['unexpectedRequests'];report['passed']=True
  except Exception as e:report['failure']=str(e);raise
  finally:
   (out/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');browser.close()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',default='http://127.0.0.1:8765');p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.base.rstrip('/'),a.out)
