"""Public routing and real mobile menu acceptance; never submit a live form."""
import argparse, json, pathlib, os
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from mira_browser_network import fixture_analytics

parser=argparse.ArgumentParser()
parser.add_argument('--base',default='http://127.0.0.1:8765')
parser.add_argument('--out',default='/tmp/mira-navigation')
args=parser.parse_args(); base=args.base.rstrip('/'); out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
routes=['/mira/','/mira/payments/','/mira/go/','/mira/catalog/','/mira/catalog/dubai/',
        '/mira/catalog/projects/botanica-montazure/','/mira/catalog/botanica/',
        '/mira/documents/','/mira/documents/payment-support.html','/mira/start/',
        '/mira/agency/','/mira/design/','/mira/access/','/mira/phuket/',
        '/mira/practical/','/mira/corporate/','/mira/growth/','/mira/business/','/mira/en/']
report={'pages':[],'errors':[],'unexpected_requests':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
    context=browser.new_context(reduced_motion='reduce')
    def guard(route):
        request=route.request
        if fixture_analytics(route): return
        if request.method not in ['GET','HEAD'] or urlsplit(request.url).netloc!=urlsplit(base).netloc:
            # Font and embedded enquiry loads are outside this static navigation test.
            if request.method not in ['GET','HEAD']:report['unexpected_requests'].append(request.url)
            route.abort()
        else:route.continue_()
    context.route('**/*',guard)
    page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
    try:
        for path in routes:
            response=page.goto(base+path+'?mira_analytics=off',wait_until='networkidle')
            assert response.ok, (path,response.status)
            assert page.locator('.mira-shell').count()==1,path
            for width in [320,390,768,1280]:
                page.set_viewport_size({'width':width,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(path,width)
                if width<=900:
                    menu=page.locator('.mira-shell-mobile')
                    if menu.get_attribute('open') is None:menu.locator('summary').click()
                    links=menu.locator('nav a'); assert links.count()==(4 if path=='/mira/en/' else 7)
                    for link in links.all():
                        assert link.is_visible(),(path,width,link.inner_text())
                        rect=link.bounding_box();assert rect['width']>0 and rect['x']>=0 and rect['x']+rect['width']<=width+1,(path,width,rect)
                    if path=='/mira/go/' and width==390:page.screenshot(path=str(out/'go-menu-mobile.png'))
                    menu.locator('summary').click()
                else:assert page.locator('.mira-shell-desktop').is_visible(),path
            report['pages'].append(path)
        page.goto(base+'/mira/go/?mira_analytics=off',wait_until='networkidle')
        page.get_by_role('navigation',name='Основная навигация',exact=True).get_by_role('link',name='Оплата',exact=True).click()
        assert page.url.endswith('#payments')
        pay=page.locator('#payments');assert pay.is_visible()
        assert pay.get_by_role('link',name='Обсудить оплату ↗').get_attribute('href')=='https://pilot.wegc.fund/mira/request/'
        pay.get_by_role('link',name='Как работает сопровождение ↗').click()
        page.wait_for_load_state('networkidle')
        page.get_by_role('navigation',name='Основная навигация',exact=True).get_by_role('link',name='Каталог',exact=True).click()
        page.wait_for_url(base+'/mira/catalog/')
        assert not report['errors'],report['errors']
        assert not report['unexpected_requests'],report['unexpected_requests']
        # Native details remains usable even if JavaScript is unavailable.
        offline=browser.new_context(java_script_enabled=False,viewport={'width':320,'height':740})
        offline.route('**/*',guard);fallback=offline.new_page()
        fallback.goto(base+'/mira/documents/',wait_until='networkidle')
        fallback.locator('.mira-shell-mobile summary').click()
        fallback.get_by_role('navigation',name='Мобильная навигация').get_by_role('link',name='Начать работу',exact=True).click()
        fallback.wait_for_url(base+'/mira/go/')
        report['passed']=True
    finally:
        (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        browser.close()
print(json.dumps(report,ensure_ascii=False))
