"""Static release checks: local browser with real CSP, then public GET/hash checks.
No external form, API write, email, telemetry or real client data is submitted.
"""
import hashlib, json, os, threading, time
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/mira-agency'
PATHS = {
    '/mira/agency/': 'mira/agency/index.html',
    '/mira/agency/agency.css': 'mira/agency/agency.css',
    '/mira/agency/agency.mjs': 'mira/agency/agency.mjs',
    '/mira/agency/qualification.mjs': 'mira/agency/qualification.mjs'
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def browser_check():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            opts = {'headless': True, 'args': ['--no-sandbox']}
            if os.environ.get('CHROMIUM_PATH'):
                opts['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = p.chromium.launch(**opts)
            page = browser.new_page(viewport={'width':1440,'height':960}, accept_downloads=True)
            writes, external, errors = [], [], []
            page.on('request', lambda r: writes.append(r.method) if r.method != 'GET' else None)
            page.on('pageerror', lambda e: errors.append(str(e)))
            def route(r):
                if r.request.url.startswith(origin+'/'):
                    r.continue_()
                else:
                    external.append(r.request.url)
                    r.abort()
            page.route('**/*', route)
            page.goto(origin+'/mira/agency/', wait_until='networkidle')
            assert page.locator('#model').is_enabled(), 'module failed under actual CSP'
            page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
            page.screenshot(path=str(OUT/'hero-desktop.png'))
            page.locator('[data-model="overseas_desk"]').click()
            assert page.locator('#model').input_value()=='overseas_desk'
            page.select_option('#goal','improve_process')
            page.select_option('#owner','assigned_manager')
            page.locator('#build-plan').click()
            assert 'Дополнить зарубежный' in page.locator('#plan-title').inner_text()
            with page.expect_download() as info:
                page.locator('#download-brief').click()
            info.value.save_as(str(OUT/'synthetic-brief.txt'))
            assert 'Не отправлен' in (OUT/'synthetic-brief.txt').read_text(encoding='utf-8-sig')
            page.select_option('#owner','not_assigned')
            assert page.locator('#plan').is_hidden()
            page.locator('#build-plan').click()
            assert 'Сначала определите ответственного' in page.locator('#plan-steps li').first.inner_text()
            page.locator('#plan-demo').click()
            page.wait_for_selector('#cards .card')
            assert page.locator('#cards .card').count()>0
            assert '/mira/marketplace.html' in page.url
            page.goto(origin+'/mira/agency/?segment=thailand_desk')
            assert page.locator('#model').input_value()=='thailand_desk'
            page.goto(origin+'/mira/agency/?segment=__proto__')
            assert page.locator('#model').input_value()==''
            for width in [320,360,390,768,1024,1440]:
                page.set_viewport_size({'width':width,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), f'overflow: {width}'
                if width==390:
                    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
                    page.screenshot(path=str(OUT/'hero-mobile.png'))
            assert not writes and not external and not errors, (writes,external,errors)
            context = browser.new_context(java_script_enabled=False)
            static = context.new_page()
            static.goto(origin+'/mira/agency/')
            assert static.locator('#model').is_disabled()
            assert static.locator('noscript').is_visible()
            browser.close()
        return {'result':'passed','actual_csp':True,'widths':[320,360,390,768,1024,1440],
                'external_requests':external,'write_requests':writes,'js_errors':errors,
                'scope':'local real-browser navigation; not Cloudflare pilot E2E'}
    finally:
        server.shutdown()
        server.server_close()

def public_check():
    results=[]
    for url_path, local_path in PATHS.items():
        expected = sha((ROOT/local_path).read_bytes())
        url = 'https://wegc.fund'+url_path
        last_error = None
        for attempt in range(6):
            try:
                req = Request(url, headers={'Cache-Control':'no-cache','User-Agent':'MIRA-static-release-check'})
                with urlopen(req, timeout=20) as response:
                    data = response.read(2_000_000)
                    assert response.status==200
                    assert response.url.startswith('https://wegc.fund/mira/agency/'), 'unexpected redirect'
                    mime = response.headers.get_content_type()
                assert sha(data)==expected, 'published bytes do not match checked-out source'
                if local_path.endswith('.mjs'):
                    assert mime in ['text/javascript','application/javascript'], 'module MIME: '+mime
                results.append({'url':url,'status':200,'sha256':expected,'mime':mime})
                last_error = None
                break
            except Exception as exc:
                last_error = str(exc)
                if attempt < 5:
                    time.sleep(12)
        if last_error:
            raise RuntimeError(url+': '+last_error)
    return results

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report={'source_commit':os.environ.get('MIRA_SOURCE_SHA','local'),
            'started_at':datetime.now(timezone.utc).isoformat(),
            'outreach_sent':False,'worker_deployed':False}
    try:
        report['browser']=browser_check()
        report['public_files']=public_check()
        report['result']='passed'
    except Exception as exc:
        report['result']='failed'
        report['error']=str(exc)
        raise
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        (OUT/'release.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
