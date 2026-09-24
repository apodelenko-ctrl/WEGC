"""Real browser, real Worker/auth and public-source fixture; never production identities."""
import json, os, pathlib, subprocess
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parents[1]
out = pathlib.Path(os.environ['MIRA_BROWSER_OUTPUT'])
out.mkdir(parents=True, exist_ok=True)
server = subprocess.Popen(['node', 'tests/mira-research-browser-server.mjs'], cwd=root, stdout=subprocess.PIPE, text=True)
try:
    origin = server.stdout.readline().strip().split('=', 1)[1]
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        for role, code in [('', 401), ('TEST-MEMBER', 403)]:
            context = browser.new_context(extra_http_headers={'x-mira-fixture-role': role})
            page = context.new_page()
            for path in ['/mira/research/', '/mira/research/client.mjs', '/mira/api/admin/research', '/mira/api/admin/research/entities?kind=agency']:
                response = page.goto(origin + path)
                assert response.status == code, (role, path, response.status)
                assert 'agency_candidates' not in page.locator('body').inner_text()
            context.close()
        context = browser.new_context(extra_http_headers={'x-mira-fixture-role':'TEST-OPERATOR'}, viewport={'width':1440,'height':1000})
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(origin + '/mira/research/')
        page.locator('#summary').filter(has_text='Агентства: 405 · Группы застройщиков: 43 · Связи проектов: 618').wait_for()
        page.locator('#records article').first.wait_for()
        first = page.locator('#records h2').first.inner_text()
        page.locator('#next').click()
        page.wait_for_function('(first)=>document.querySelector("#records h2")?.textContent!==first', arg=first)
        page.locator('#query').fill(first)
        page.get_by_role('button', name='Найти', exact=True).click()
        page.locator('#records h2').filter(has_text=first).first.wait_for()
        page.locator('#records button').first.click()
        page.locator('#detail details').first.wait_for()
        page.locator('#detail summary').first.click()
        assert 'Проверка:' in page.locator('#detail').inner_text()
        page.screenshot(path=str(out/'research-agency-desktop.png'),full_page=True)
        page.locator('#kind').select_option('developer')
        page.locator('#query').fill('')
        page.get_by_role('button',name='Найти',exact=True).click()
        page.locator('#status').filter(has_text='Записей на странице:').wait_for()
        page.locator('#records button').first.click()
        page.get_by_role('button',name='Показать проекты',exact=True).click()
        page.wait_for_function('document.querySelector("#detail").innerText.includes("verified_") || document.querySelector("#detail").innerText.includes("research_")')
        page.screenshot(path=str(out/'research-developer-desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'mobile overflow'
        page.screenshot(path=str(out/'research-developer-mobile.png'),full_page=True)
        page.reload()
        page.locator('#summary').filter(has_text='Агентства: 405').wait_for()
        assert not errors, errors
        browser.close()
    result={'scope':'isolated public source + synthetic signed roles','anonymous':401,'ordinary_active_member':403,'operator_counts':[405,43,618],'search_pagination_cards_links_reload':True,'desktop_mobile':True}
    (out/'browser-proof.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
finally:
    server.terminate()
    server.wait(timeout=5)
