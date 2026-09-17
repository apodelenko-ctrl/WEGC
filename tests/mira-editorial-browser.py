"""Read-only HTTP/CSP acceptance of the preserved editorial design and 45-demo.

This is deliberately separate from the current 618-record research catalogue.
No real account, client registration, email or payment is submitted.
"""
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'mira/design/index.html', 'mira/design/design.css', 'mira/design/motion.mjs',
    'mira/design/catalogue-visuals.mjs', 'mira/design/marketplace.css',
    'mira/marketplace-design.html', 'mira/marketplace.mjs', 'mira/core.mjs',
    'mira/agency/agency.mjs', 'mira/agency/qualification.mjs', 'mira/data/catalog.json',
]
WIDTHS = [320, 360, 390, 600, 768, 1024, 1440]

def run(base, out):
    from playwright.sync_api import sync_playwright
    parsed = urlsplit(base)
    if parsed.hostname not in {'wegc.fund', '127.0.0.1', 'localhost'} or parsed.scheme not in {'http', 'https'}:
        raise ValueError('Only the owner domain or loopback is allowed')
    out.mkdir(parents=True, exist_ok=True)
    report = {'base': base, 'passed': False, 'checks': [], 'files': [],
              'page_errors': [], 'csp_errors': [], 'unexpected_requests': [],
              'scope': 'preserved editorial design and legacy 45-demo; actual HTTP/CSP; no real signup',
              'live_registration_tested': False}
    def mark(name, **kw):
        report['checks'].append({'name': name, 'passed': True, **kw})
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None, args=['--no-sandbox'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce', accept_downloads=True, service_workers='block')
            def guard(route):
                req = route.request
                if req.method not in {'GET', 'HEAD'} or urlsplit(req.url).netloc != parsed.netloc:
                    report['unexpected_requests'].append({'method': req.method, 'url': req.url.split('?')[0]})
                    route.abort()
                else:
                    route.continue_()
            context.route('**/*', guard)
            for path in FILES:
                response = context.request.get(base + '/' + path, max_redirects=0)
                expected = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                assert response.status == 200 and hashlib.sha256(response.body()).hexdigest() == expected, path
                report['files'].append({'path': path, 'sha256': expected, 'status': response.status})
            page = context.new_page()
            page.on('pageerror', lambda err: report['page_errors'].append(str(err)))
            page.on('console', lambda msg: report['csp_errors'].append(msg.text) if msg.type == 'error' and ('Content Security Policy' in msg.text or 'violates' in msg.text) else None)
            def goto(path):
                response = page.goto(base + path, wait_until='networkidle', timeout=45000)
                assert response and response.ok, path
            goto('/mira/design/')
            page.wait_for_selector('#qualification-fields:not([disabled])')
            assert page.locator('h1').count() == 1
            assert page.locator('#hero-image').evaluate('(el) => el.complete && el.naturalWidth > 0')
            for width in WIDTHS:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
            page.screenshot(path=str(out / 'editorial-desktop.png'))
            page.set_viewport_size({'width': 390, 'height': 844})
            page.screenshot(path=str(out / 'editorial-mobile.png'))
            mark('preserved_design_http_assets_responsive', widths=WIDTHS)
            assert not page.locator('#qualification').evaluate('(form) => form.checkValidity()')
            for name, value in [('model', 'new_direction'), ('goal', 'client_request'), ('owner', 'decision_maker')]:
                page.locator('select[name=' + name + ']').select_option(value)
            page.locator('#build-plan').click()
            page.locator('#plan').wait_for(state='visible')
            with page.expect_download() as result:
                page.locator('#download-brief').click()
            assert 'МИРА' in Path(result.value.path()).read_text(encoding='utf-8-sig')
            destination = page.locator('#plan-demo').get_attribute('href')
            assert '/mira/marketplace-design.html' in destination, destination
            page.locator('#plan-demo').click()
            page.wait_for_url('**view=onboarding*')
            page.get_by_role('heading',name='Материалы и обучение',exact=True).wait_for(state='visible')
            page.locator('[data-view="catalog"]').click()
            page.wait_for_selector('[data-catalogue-mode="all"]')
            page.locator('[data-catalogue-mode="all"]').click()
            assert page.locator('#cards .card:visible').count() == 45
            for width in WIDTHS:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('legacy-demo', width)
            mark('preserved_qualifier_and_legacy_demo', local_brief=True, legacy_records=45)
            page.emulate_media(reduced_motion='no-preference')
            goto('/mira/design/')
            page.locator('#motion-toggle').wait_for(state='visible')
            page.locator('#motion-toggle').click()
            assert page.locator('#motion-toggle').get_attribute('aria-pressed') == 'true'
            assert page.locator('#hero-image').evaluate('(el) => el.getAnimations().every(a => a.playState === "paused")')
            page.emulate_media(reduced_motion='reduce')
            # Wait for the media-query handler without eval under the real CSP.
            page.locator('#motion-toggle').wait_for(state='hidden')
            assert page.locator('#hero-image').evaluate('(el) => el.getAnimations().length === 0')
            mark('preserved_motion_pause_and_reduced')
            plain = browser.new_context(java_script_enabled=False, service_workers='block')
            plain.route('**/*', guard)
            other = plain.new_page()
            response = other.goto(base + '/mira/design/', wait_until='networkidle', timeout=45000)
            assert response and response.ok
            assert other.locator('h1').is_visible()
            assert other.locator('#qualification-fields').get_attribute('disabled') is not None
            assert other.locator('#qualification-fields select').count() == 3
            assert all(other.locator('#qualification-fields select').nth(i).is_disabled() for i in range(3))
            assert other.locator('#build-plan').is_disabled()
            plain.close()
            mark('preserved_no_js_content')
            assert not report['page_errors'], report['page_errors']
            assert not report['csp_errors'], report['csp_errors']
            assert not report['unexpected_requests'], report['unexpected_requests']
            context.close()
            browser.close()
            report['passed'] = True
    except Exception as exc:
        import traceback
        report['failure'] = str(exc)
        report['traceback'] = traceback.format_exc()
        raise
    finally:
        (out / 'browser-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'base': base, 'passed': report['passed'], 'checks': len(report['checks']), 'live_registration_tested': False}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.base.rstrip('/'), args.out)
