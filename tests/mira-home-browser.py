"""Read-only homepage acceptance: carousel, reduced motion, FAQ, payment route.
No CRM submission, outbound mail or payment instructions are sent.
"""
import argparse,json,os,pathlib
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
from mira_browser_network import fixture_analytics
p=argparse.ArgumentParser();p.add_argument('--base',default='http://127.0.0.1:8765');p.add_argument('--out',default='/tmp/mira-home');args=p.parse_args()
base=args.base.rstrip('/');out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
report={'passed':False,'widths':[],'errors':[],'unsafe_requests':[],'broken_images':[]}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
 def guard(route):
  if fixture_analytics(route):return
  r=route.request
  if r.method not in ['GET','HEAD']:
   report['unsafe_requests'].append(r.url);route.abort()
  elif urlsplit(r.url).netloc!=urlsplit(base).netloc:route.abort()
  else:route.continue_()
 context=browser.new_context(reduced_motion='reduce');context.route('**/*',guard)
 page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
 try:
  for width in [320,390,768,1280,1536]:
   page.set_viewport_size({'width':width,'height':900})
   for path in ['/mira/','/mira/payments/']:
    assert page.goto(base+path+'?mira_analytics=off',wait_until='networkidle').ok
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
    assert page.locator('h1').count()==1
    assert page.locator('.mira-footer').is_visible()
    if width<=900:
     page.locator('.mira-shell-mobile summary').click()
     expect(page.get_by_role('navigation',name='Мобильная навигация').get_by_role('link',name='Каталог',exact=True)).to_be_visible()
     page.locator('.mira-shell-mobile summary').click()
    faq=page.locator('.faq details').first;faq.locator('summary').click();expect(faq).to_have_attribute('open','')
    faq.locator('summary').press('Enter');assert faq.get_attribute('open') is None
    if path=='/mira/':
     for gallery in page.locator('[data-carousel]').all():
      gallery.scroll_into_view_if_needed()
      for i in range(gallery.locator('.mira-slide').count()):
       image=gallery.locator('.is-current img');expect(image).to_be_visible()
       page.wait_for_function('(selector)=>{const img=document.querySelector(selector); return img.complete && img.naturalWidth>0}',arg=('.hero-gallery' if 'hero-gallery' in gallery.get_attribute('class') else '.field-gallery')+' .is-current img',timeout=10000)
       assert image.evaluate('(img)=>img.naturalWidth>0')
       gallery.locator('[data-next]').click()
      expect(gallery).to_have_attribute('data-active-slide','0')
     assert 'field reports' not in page.locator('body').inner_text()
     assert 'Phuket Field Ops' not in page.locator('body').inner_text()
     assert page.locator('#payments a[href="/mira/payments/"]').count()==1
     page.locator('#payments a[href="/mira/payments/"]').click();page.wait_for_url(base+'/mira/payments/')
     assert 'переговорная редакция' not in page.locator('body').inner_text().lower()
    assert page.get_by_role('link',name='Обсудить мою сделку ↗').get_attribute('href')=='https://pilot.wegc.fund/mira/request/'
   report['widths'].append(width)
  page.set_viewport_size({'width':1280,'height':900});page.goto(base+'/mira/?mira_analytics=off',wait_until='networkidle')
  page.screenshot(path=str(out/'home-desktop.png'))
  page.locator('#payments').screenshot(path=str(out/'payment-block.png'))
  page.set_viewport_size({'width':390,'height':844});page.goto(base+'/mira/?mira_analytics=off',wait_until='networkidle');page.screenshot(path=str(out/'home-mobile.png'))
  # Autoplay really changes a slide; pause and reduced motion really stop it.
  animated=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='no-preference');animated.route('**/*',guard)
  moving=animated.new_page();moving.goto(base+'/mira/?mira_analytics=off',wait_until='networkidle')
  gallery=moving.locator('.hero-gallery');expect(gallery).to_have_attribute('data-active-slide','1',timeout=9000)
  gallery.locator('[data-pause]').click();before=gallery.get_attribute('data-active-slide');moving.mouse.click(20,700);moving.wait_for_timeout(6800);assert gallery.get_attribute('data-active-slide')==before
  moving.emulate_media(reduced_motion='reduce');moving.reload(wait_until='networkidle');moving.wait_for_timeout(6800);expect(gallery).to_have_attribute('data-active-slide','0')
  # No-JS fallback retains visible first image, menu and native accordion.
  fallback=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});fallback.route('**/*',guard);plain=fallback.new_page();plain.goto(base+'/mira/?mira_analytics=off',wait_until='networkidle')
  expect(plain.locator('.hero-gallery .is-current img')).to_be_visible();expect(plain.locator('.hero-gallery .carousel-controls')).to_be_hidden()
  plain.locator('.faq details summary').first.click();expect(plain.locator('.faq details').first).to_have_attribute('open','')
  assert not report['errors'],report['errors'];assert not report['unsafe_requests'],report['unsafe_requests'];report['passed']=True
 finally:
  (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));browser.close()
print(json.dumps(report,ensure_ascii=False))
