"""Offline visual/interaction regression. NOT deployed navigation or CSP verification.

The test mounts local HTML/CSS/media in an isolated DOM and replaces the demo's
one catalogue fetch and browser location with explicit test fixtures. All network
requests are blocked. No real application, contact or form submission occurs.
"""
from pathlib import Path
import base64, json, mimetypes, os, re, argparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]

def image_data(path):
    file = ROOT / path.lstrip('/')
    return 'data:' + (mimetypes.guess_type(file)[0] or 'application/octet-stream') + ';base64,' + base64.b64encode(file.read_bytes()).decode()

def mount(page, path, styles):
    soup = BeautifulSoup((ROOT / path).read_text(), 'html.parser')
    for node in soup.select('meta[http-equiv],script,link'): node.decompose()
    soup.head.append(soup.new_tag('base', href='https://mira.test/' + path))
    for css in styles:
        tag = soup.new_tag('style'); tag.string = (ROOT / css).read_text(); soup.head.append(tag)
    for node in soup.select('img[src],source[srcset]'):
        attr = 'src' if node.name == 'img' else 'srcset'
        node[attr] = image_data(node[attr])
        if node.name == 'img': node['loading'] = 'eager'
    page.set_content(str(soup), wait_until='load')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
    page.evaluate('''document.addEventListener('click',e=>{const a=e.target.closest('a');if(a?.getAttribute('href')?.startsWith('#')){e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({behavior:'instant'});}})''')

def agency_js(page):
    core = (ROOT / 'mira/agency/qualification.mjs').read_text().replace('export ', '')
    app = re.sub(r'^import .*?;\n', '', (ROOT / 'mira/agency/agency.mjs').read_text())
    page.evaluate('(()=>{' + core + '\n' + app + '})()')
    page.evaluate('(()=>{' + (ROOT / 'mira/design/motion.mjs').read_text() + '})()')

def market_js(page, catalog):
    page.evaluate("window.__testLocation=new URL('https://mira.test/mira/marketplace-design.html');window.__requests=[];window.__uuid=0;")
    script = (ROOT / 'mira/design/catalogue-visuals.mjs').read_text().replace('new URL(window.location.href)', 'new URL(window.__testLocation.href)')
    for path in re.findall(r"'(/images/[^']+)'", script): script = script.replace("'" + path + "'", json.dumps(image_data(path)))
    page.evaluate('(()=>{' + script + '})()')
    core = (ROOT / 'mira/core.mjs').read_text().replace('export ', '')
    app = re.sub(r'^import .*?;\n', '', (ROOT / 'mira/marketplace.mjs').read_text())
    harness = "const location=window.__testLocation;const history={pushState(a,b,u){location.href=String(u)}};const crypto={randomUUID:()=>String(++window.__uuid)};"
    fetch = 'const fetch=async(url,opts)=>{window.__requests.push({url,opts});return new Response(' + json.dumps(json.dumps(catalog, ensure_ascii=False)) + ',{headers:{"Content-Type":"application/json"}});};'
    page.evaluate('(async()=>{' + harness + fetch + core + '\n' + app + '})()')
    page.wait_for_selector('.catalogue-controls')

def run(out):
    out.mkdir(parents=True, exist_ok=True)
    cases = []; console_errors = []; widths = [320,360,390,600,768,1024,1440]
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        context = browser.new_context(viewport={'width':1440,'height':1000}, reduced_motion='reduce', accept_downloads=True)
        context.route('**/*', lambda r:r.abort())
        page=context.new_page();page.set_default_timeout(5000);page.on('pageerror',lambda e:console_errors.append(str(e)))
        mount(page,'mira/design/index.html',['mira/design/design.css']);agency_js(page)
        assert page.locator('h1').count()==1
        assert page.locator('#motion-toggle').is_hidden()
        assert page.evaluate('document.getAnimations().length')==0
        assert page.locator('img').evaluate_all('(es)=>es.every(i=>i.naturalWidth>0)')
        page.screenshot(path=str(out/'landing-desktop.png'))
        # A full-page screenshot with all embedded media decoded, not just requested.
        page.screenshot(path=str(out/'landing-full.png'),full_page=True)
        cases.append('reduced-motion renders without active animation; all four images decoded')
        for width in widths:
            page.set_viewport_size({'width':width,'height':844});page.evaluate('scrollTo(0,0)')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'landing overflow at {width}'
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'landing-mobile.png'))
        page.locator('[data-model="overseas_desk"]').click()
        assert page.locator('#model').input_value()=='overseas_desk'
        page.locator('#goal').select_option('improve_process');page.locator('#owner').select_option('decision_maker');page.locator('#build-plan').click()
        assert page.locator('#plan').is_visible()
        assert 'Ничего не отправлено' in page.locator('#form-message').inner_text()
        assert page.locator('#plan-title').evaluate('(e)=>document.activeElement===e')
        page.locator('#goal').select_option('explore');assert page.locator('#plan').is_hidden()
        page.locator('#build-plan').click()
        with page.expect_download() as download: page.locator('#download-brief').click()
        assert download.value.suggested_filename=='mira-agency-brief.txt'
        cases.append('segment shortcut, validated qualification, focus, invalidation and local download')
        page.locator('.faq summary').first.click();assert page.locator('.faq details').first.get_attribute('open') is not None
        cases.append('native FAQ interaction')
        # Normal motion, user pause/resume, reduced-motion preference change.
        page.emulate_media(reduced_motion='no-preference');page.evaluate('scrollTo(0,0)');page.wait_for_timeout(150)
        assert page.locator('#motion-toggle').is_visible()
        page.locator('#motion-toggle').click();assert page.locator('#motion-toggle').get_attribute('aria-pressed')=='true'
        page.locator('#motion-toggle').click();assert page.locator('#motion-toggle').get_attribute('aria-pressed')=='false'
        page.emulate_media(reduced_motion='reduce');page.locator('#motion-toggle').wait_for(state='hidden')
        cases.append('motion play, user pause/resume, preference change respected')
        # Market preview uses the unchanged engine with the exact local catalogue.
        page=context.new_page();page.set_default_timeout(5000);page.on('pageerror',lambda e:console_errors.append(str(e)))
        mount(page,'mira/marketplace-design.html',['mira/design/design.css','mira/design/marketplace.css'])
        catalog=json.loads((ROOT/'mira/data/catalog.json').read_text());market_js(page,catalog)
        assert page.locator('#cards .card').count()==len(catalog['projects'])
        assert page.locator('#cards .card:visible').count()==5
        assert 'Всего в текущей выборке: 45' in page.locator('#count').inner_text()
        for width in widths:
            page.set_viewport_size({'width':width,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'market overflow at {width}'
        page.set_viewport_size({'width':1440,'height':1080})
        page.locator('img').evaluate_all('(es)=>es.forEach(i=>i.loading="eager")')
        page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
        assert page.locator('.project-visual img').evaluate_all('(es)=>es.every(i=>i.naturalWidth>0)')
        page.screenshot(path=str(out/'marketplace-desktop.png'))
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/'marketplace-mobile.png'))
        page.locator('#search').fill('sierra');page.wait_for_timeout(50)
        assert page.locator('#cards .card:visible').count()==0
        assert page.locator('.catalogue-empty').is_visible()
        page.locator('[data-catalogue-mode="all"]').click();assert page.locator('#cards .card:visible').count()==1
        page.locator('#cards .card a').click();page.locator('#lead-form button').click()
        assert 'DEMO-CLIENT-1' in page.locator('#content').inner_text()
        assert 'Не подтверждена застройщиком' in page.locator('#content').inner_text()
        page.locator('[data-payment]').click();assert 'Не передано на исполнение' in page.locator('#content').inner_text()
        cases.append('five exact illustrated projects; all 45 accessible; filter with no art has explicit fallback; demo lead and payment unchanged')
        page.locator('[data-view="catalog"]').click();page.locator('#search').fill('vivi');page.locator('#cards a').click()
        page.wait_for_selector('.detail-visual');assert page.locator('.detail-visual img').count()==1
        assert 'Архивная визуализация' in page.locator('.detail-visual').inner_text()
        page.screenshot(path=str(out/'project-mobile.png'))
        page.locator('#reset').click()
        page.locator('[data-view="clients"]').click();assert 'Клиентов пока нет' in page.locator('#content').inner_text()
        req=page.evaluate('window.__requests');assert len(req)==1 and req[0]['opts'].get('method','GET')=='GET'
        cases.append('project art, original disclosure, reset, only one in-memory catalogue GET')
        # Static landing with JS disabled: content and links remain, qualification closed.
        static=context.new_page();mount(static,'mira/design/index.html',['mira/design/design.css'])
        assert static.locator('#model').is_disabled()
        assert static.locator('h1').is_visible()
        assert static.locator('.hero-actions a').count()==2
        cases.append('no-JS static content preserved; inert form, real links')
        assert console_errors==[],console_errors
        browser.close()
    report={'mode':'offline DOM and local image rendering; browser navigation/CSP/deployed E2E not verified','responsive_widths':widths,'passed_cases':cases,'page_errors':console_errors,'external_submissions':0,'production_gates_changed':False}
    (out/'design-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--output',type=Path,default=ROOT/'design-qa');run(args.parse_args().output)
