"""HTTP/CSP acceptance for additive campaign/catalogue; no real customer submissions.

Only an owner's known host or loopback may be used. Negative response fixtures are
explicitly labelled. A closed registration gate is tested, not called registration.
"""
from pathlib import Path
from urllib.parse import urlsplit
import argparse, json, os

ALLOWED={'wegc.fund','localhost','127.0.0.1'}
WIDTHS=[320,360,390,600,768,1024,1440]

def make_json_fixture(status, body):
    """Capture fixture values separately from Playwright's optional Request arg.

    Only used for labelled negative catalogue responses. Supports both callback
    forms without ever substituting a Request object for the HTTP status.
    """
    if type(status) is not int or not 100 <= status <= 599:
        raise ValueError('Fixture HTTP status must be an integer')
    if not isinstance(body, str):
        raise ValueError('Fixture body must be text')

    def handler(route, _request=None):
        route.fulfill(status=status, content_type='application/json', body=body)

    return handler


def run(base,out):
    from playwright.sync_api import sync_playwright

    assert urlsplit(base).hostname in ALLOWED
    out.mkdir(parents=True,exist_ok=True)
    report={'base':base,'scope':'real HTTP/CSP; local-only briefs; labelled negative fixtures',
            'passed':False,'live_registration_tested':False,'checks':[],
            'page_errors':[],'csp_errors':[],'unexpected_requests':[]}
    def mark(name,**details):report['checks'].append(dict(name=name,passed=True,**details))
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or None,args=['--no-sandbox'])
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
            def guard(route):
                req=route.request
                if req.method not in ['GET','HEAD'] or urlsplit(req.url).netloc!=urlsplit(base).netloc:
                    report['unexpected_requests'].append({'method':req.method,'url':req.url.split('?')[0]});route.abort()
                else:route.continue_()
            context.route('**/*',guard)
            page=context.new_page()
            page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
            page.on('console',lambda m:report['csp_errors'].append(m.text) if m.type=='error' and ('Content Security Policy' in m.text or 'violates' in m.text) else None)
            def goto(path):
                response=page.goto(base+path,wait_until='networkidle',timeout=45000)
                assert response and response.ok,(path,response.status if response else None)
                return response
            for route in ['go','practical','corporate']:
                goto('/mira/'+route+'/');assert page.locator('h1').count()==1
                page.wait_for_selector('#campaign-form fieldset:not([disabled])')
                for width in WIDTHS:
                    page.set_viewport_size({'width':width,'height':1000})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(route,width)
                page.screenshot(path=str(out/(route+'-desktop.png')))
                page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/(route+'-mobile.png')))
                assert not page.locator('#campaign-form').evaluate('(f)=>f.checkValidity()')
                assert page.locator('#plan').is_hidden()
                for name,value in [('model','new_direction'),('goal','client_request'),('owner','decision_maker')]:
                    page.locator('select[name='+name+']').select_option(value)
                page.locator('#prepare').click();page.locator('#plan').wait_for(state='visible')
                assert page.locator('#plan-title').evaluate('(el)=>document.activeElement===el')
                with page.expect_download() as d:page.locator('#download').click()
                text=Path(d.value.path()).read_text(encoding='utf-8-sig');assert 'МИРА' in text
                assert 'Не отправлен.' in text
                page.locator('select[name=goal]').select_option('explore');assert page.locator('#plan').is_hidden()
                assert page.locator('input').count()==0
                mark('funnel_'+route,widths=WIDTHS,required_choices=True,brief_download=True,change_invalidates=True)
            page.set_viewport_size({'width':1440,'height':1000});goto('/mira/catalog/')
            page.wait_for_function("document.querySelector('#search').disabled===false")
            assert '618' in page.locator('#result-count').inner_text()
            seen=set();pages=0
            while True:
                seen.update(page.locator('#cards [data-add]').evaluate_all('(els)=>els.map(e=>e.dataset.add)'))
                pages+=1
                if page.locator('#next').is_disabled():break
                assert pages<30;page.locator('#next').click()
            assert len(seen)==618 and pages==26,(len(seen),pages)
            mark('catalogue_every_record_reachable',unique_records=len(seen),pages=pages)
            page.locator('#filters-reset').click();page.locator('#kind').select_option('villa');page.wait_for_timeout(130)
            assert '143' in page.locator('#result-count').inner_text()
            page.locator('#filters-reset').click();page.locator('#search').fill('TITLE VIVI');page.wait_for_timeout(200)
            assert page.locator('#cards .project-card').count()==1
            page.locator('#cards [data-add]').click();page.locator('#shortlist-open').click()
            assert page.locator('#shortlist').is_visible()
            with page.expect_download() as d:page.locator('#shortlist-download').click()
            text=Path(d.value.path()).read_text();assert 'title-vivi' in text and 'Не отправлена' in text
            page.keyboard.press('Escape');assert page.locator('#shortlist').is_hidden()
            goto('/mira/catalog/projects/title-vivi/');page.wait_for_selector('[data-add]:not([disabled])')
            assert page.locator('[data-add]').get_attribute('aria-pressed')=='true'
            assert 'данные покупателей не принимаются' in page.locator('#registration-gate').inner_text()
            assert page.locator('input, form').count()==0
            for width in WIDTHS:
                page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('detail',width)
            mark('catalogue_filter_shortlist_detail',session_restore=True,registration_closed=True)
            goto('/mira/catalog/?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E&page=999');page.wait_for_function("document.querySelector('#search').disabled===false")
            assert page.locator('#cards .project-card').count()==0
            page.locator('#filters-reset').click();assert page.locator('#cards .project-card').count()==24
            for width in WIDTHS:
                page.set_viewport_size({'width':width,'height':1000});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('catalogue',width)
            page.screenshot(path=str(out/'catalogue-desktop.png'))
            mark('untrusted_query_empty_reset_and_responsive',widths=WIDTHS)
            # Corrupt storage never becomes HTML or a fabricated selected project.
            page.evaluate("localStorage.setItem('mira-research-selection-v1','{broken')")
            page.reload(wait_until='networkidle');page.wait_for_function("document.querySelector('#search').disabled===false")
            assert page.locator('#shortlist-open').is_hidden();mark('corrupt_local_selection_fallback')
            for name,body in [('503','temporary'),('malformed_json','{invalid')]:
                status=503 if name=='503' else 200
                context.route('**/mira/catalog/data.json', make_json_fixture(status, body))
                goto('/mira/catalog/');page.locator('#load-error').wait_for(state='visible')
                assert page.locator('#search').is_disabled() and page.locator('#cards .project-card').count()==24
                context.unroute('**/mira/catalog/data.json');mark('fixture_'+name,static_fallback=True)
            goto('/mira/catalog/');page.wait_for_function("document.querySelector('#search').disabled===false")
            mark('catalogue_recovery_after_fixture')
            # Public page links to the existing invited intake; this read-only test does not submit it.
            goto('/mira/access/');assert page.locator('input').count()==0 and 'приглаш' in page.locator('main').inner_text().lower();assert page.locator('a[href="https://pilot.wegc.fund/mira/pilot.html"]').count()==1
            mark('invited_agency_entry_no_public_signup',real_signup_success=False)
            goto('/mira/documents/');assert page.locator('.doc-card').count()==9
            names=['agency-agreement','project-rules','data-processing','privacy','data-consent','marketing-consent','materials-policy','payment-support','site-terms']
            for name in names:
                r=context.request.get(base+'/mira/documents/downloads/'+name+'.pdf');assert r.ok and r.body().startswith(b'%PDF'),name
            r=context.request.get(base+'/mira/documents/downloads/agency-agreement.docx');assert r.ok and r.body().startswith(b'PK')
            mark('all_nine_pdf_documents_and_docx_readable')
            goto('/mira/exhibition/');assert page.locator('img').first.evaluate('(i)=>i.complete&&i.naturalWidth>0')
            for name in ['banner-landscape.pdf','banner-rollup.pdf']:
                r=context.request.get(base+'/mira/exhibition/'+name);assert r.ok and r.body().startswith(b'%PDF')
            mark('exhibition_vector_downloads')
            page.emulate_media(reduced_motion='no-preference');goto('/mira/go/')
            assert page.locator('body').evaluate('(b)=>b.classList.contains("motion-on")')
            page.locator('#motion-toggle').click();assert not page.locator('body').evaluate('(b)=>b.classList.contains("motion-on")')
            page.emulate_media(reduced_motion='reduce');assert not page.locator('body').evaluate('(b)=>b.classList.contains("motion-on")')
            mark('motion_controls')
            plain=browser.new_context(java_script_enabled=False);plain.route('**/*',guard)
            p2=plain.new_page();r=p2.goto(base+'/mira/catalog/list.html',wait_until='networkidle');assert r and r.ok
            assert p2.locator('.all-projects a').count()==618
            r=p2.goto(base+'/mira/go/',wait_until='networkidle');assert r and r.ok
            assert p2.locator('h1').is_visible(), 'No-JS heading must remain visible'
            assert p2.locator('fieldset').get_attribute('disabled') is not None, 'No-JS fieldset attribute'
            assert p2.locator('fieldset select').count() == 3
            assert all(p2.locator('fieldset select').nth(i).is_disabled() for i in range(3)), 'No-JS choices must be disabled'
            assert p2.locator('#prepare').is_disabled(), 'No-JS submit must be disabled'
            plain.close();mark('no_javascript_routes',all_records=618)
            assert not report['page_errors'],report['page_errors']
            assert not report['csp_errors'],report['csp_errors']
            assert not report['unexpected_requests'],report['unexpected_requests']
            context.close();browser.close();report['passed']=True
    except Exception as exc:
        import traceback
        report['failure']=str(exc);report['traceback']=traceback.format_exc();raise
    finally:
        (out/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'base':base,'passed':report['passed'],'checks':len(report['checks']),'live_registration_tested':False}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.base.rstrip('/'),a.out)
