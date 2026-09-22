"""Full synthetic request→receipt→operator→reply; mock challenge is NEVER live acceptance."""
import json, os, pathlib, subprocess
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parents[1]
out = pathlib.Path(os.environ['MIRA_BROWSER_OUTPUT'])
out.mkdir(parents=True, exist_ok=True)
server = subprocess.Popen(['node','tests/mira-intake-browser-server.mjs'], cwd=root, stdout=subprocess.PIPE, text=True)
try:
    origin=server.stdout.readline().strip().split('=',1)[1]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome')
        applicant=browser.new_context(viewport={'width':390,'height':844})
        # No network challenge, real company data, or external mail in this fixture.
        applicant.route('https://challenges.cloudflare.com/**',lambda route:route.fulfill(content_type='text/javascript',body="const f=document.querySelector('#request');const n=document.createElement('input');n.type='hidden';n.name='cf-turnstile-response';n.value='SYNTHETIC-NOT-LIVE';f.append(n);window.turnstile={reset(){}};"))
        page=applicant.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        captured=[]
        page.on('request',lambda req:captured.append({'headers':req.headers,'body':req.post_data}) if req.url.endswith('/submit') else None)
        page.goto(origin+'/mira/request/')
        page.locator('[name=company]').fill('SYNTHETIC Expo Agency')
        page.locator('[name=city]').fill('TEST City')
        page.locator('[name=name]').fill('TEST Applicant')
        page.locator('[name=email]').fill('synthetic@example.test')
        page.locator('[name=consent]').check()
        page.get_by_role('button',name='Отправить запрос',exact=True).click()
        page.locator('#message').filter(has_text='Статус: Получен').wait_for()
        before=page.locator('#message').inner_text()
        # Replay the exact synthetic request via the same browser context.
        replay=applicant.request.post(origin+'/mira/request/submit',headers={k:v for k,v in captured[0]['headers'].items() if k in ['content-type','authorization','idempotency-key','origin']},data=captured[0]['body'])
        assert replay.status==200, replay.text()
        receipt=replay.json()['id']
        assert receipt in before
        page.reload()
        page.get_by_role('button',name='Проверить ответ',exact=True).click()
        page.locator('#message').filter(has_text='Статус: Получен').wait_for()
        assert receipt in page.locator('#message').inner_text()
        page.screenshot(path=str(out/'intake-receipt-mobile.png'),full_page=True)
        for role,code in [('',401),('TEST-APPLICANT',403)]:
            c=browser.new_context(extra_http_headers={'x-mira-fixture-role':role})
            r=c.new_page().goto(origin+'/mira/api/admin/intake/view')
            assert r.status==code
            c.close()
        operator=browser.new_context(extra_http_headers={'x-mira-fixture-role':'TEST-OPERATOR'},viewport={'width':1440,'height':1000})
        op=operator.new_page();op.on('pageerror',lambda e:errors.append(str(e)))
        op.goto(origin+'/mira/api/admin/intake/view')
        op.get_by_role('button',name='Открыть запрос',exact=True).click()
        op.locator('#assign select').select_option('TEST-SECOND')
        op.get_by_role('button',name='Назначить',exact=True).click()
        op.locator('#history').filter(has_text='Версия 1').wait_for()
        op.locator('#review select').select_option('review')
        op.get_by_role('button',name='Сохранить решение',exact=True).click()
        op.locator('#history').filter(has_text='Версия 2').wait_for()
        op.locator('#review select').select_option('responded')
        op.locator('#review textarea').fill('SYNTHETIC response: request received and reviewed.')
        op.get_by_role('button',name='Сохранить решение',exact=True).click()
        op.locator('#status').filter(has_text='Подтверди публикацию').wait_for()
        page.get_by_role('button',name='Проверить ответ',exact=True).click()
        page.locator('#message').filter(has_text='Статус: На рассмотрении').wait_for()
        assert 'SYNTHETIC response' not in page.locator('#message').inner_text()
        op.locator('#review [name=publish]').check()
        op.get_by_role('button',name='Сохранить решение',exact=True).click()
        op.locator('#history').filter(has_text='Версия 3').wait_for()
        op.reload()
        op.get_by_role('button',name='Открыть запрос',exact=True).click()
        op.locator('#history').filter(has_text='Версия 3').wait_for()
        assert op.locator('#history .history-row').count()==4
        assert op.locator('#queue article').count()==1
        op.screenshot(path=str(out/'intake-operator-desktop.png'),full_page=True)
        op.set_viewport_size({'width':390,'height':844})
        assert op.evaluate('document.documentElement.scrollWidth<=innerWidth')
        op.screenshot(path=str(out/'intake-operator-mobile.png'),full_page=True)
        page.reload()
        page.get_by_role('button',name='Проверить ответ',exact=True).click()
        page.locator('#message').filter(has_text='SYNTHETIC response').wait_for()
        assert receipt in page.locator('#message').inner_text()
        page.screenshot(path=str(out/'intake-response-mobile.png'),full_page=True)
        assert not errors,errors
        result={'scope':'isolated synthetic fixture; mock Turnstile; no live public acceptance','receipt_persisted_after_reload':True,'exact_replay_http':200,'queue_records':1,'assignment_status_explicit_reply_history':True,'history_versions':[0,1,2,3],'applicant_sees_published_reply_after_reload':True,'anonymous_admin':401,'ordinary_applicant_admin':403,'desktop_mobile':True,'external_messages_sent':0}
        (out/'intake-browser-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
        browser.close()
finally:
    server.terminate();server.wait(timeout=5)
