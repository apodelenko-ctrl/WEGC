"""Offline DOM/layout regression. No external navigation, API or form submission.
The sandbox blocks navigation; this harness injects the checked-in HTML/CSS/JS.
It does not establish deployment or live end-to-end behavior.
"""
import asyncio, json, os, re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('MIRA_QA_OUTPUT', '/mnt/data/mira-agency-qa'))

async def load(page, segment=None, javascript=True):
    raw = (ROOT/'mira/agency/index.html').read_text()
    raw = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', raw)
    raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S)
    raw = re.sub(r'<link[^>]*>', '', raw)
    await page.set_content(raw)
    await page.add_style_tag(content=(ROOT/'mira/agency/agency.css').read_text())
    if javascript:
        core = (ROOT/'mira/agency/qualification.mjs').read_text().replace('export ', '')
        ui = (ROOT/'mira/agency/agency.mjs').read_text()
        ui = re.sub(r'^import .*?;\n', '', ui)
        ui = ui.replace('new URLSearchParams(window.location.search)', 'new URLSearchParams('+json.dumps('' if segment is None else '?segment='+segment)+')')
        await page.evaluate('()=>{'+core+'\n'+ui+'}')

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        page=await browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
        page.set_default_timeout(5000)
        requests=[]
        await page.route('**/*',lambda route:route.abort())
        page.on('request',lambda req:requests.append({'url':req.url,'method':req.method}))
        await load(page)
        assert await page.locator('#model').is_enabled()
        await page.locator('#build-plan').click()
        assert await page.locator('#plan').is_hidden()
        results.append('incomplete_answers_do_not_create_plan')
        for model,title in [('new_direction','Новое направление'),('overseas_desk','Дополнить зарубежный'),('thailand_desk','конкретной задаче'),('network','пилот для вашей сети')]:
            await page.select_option('#model',model)
            await page.select_option('#goal','client_request')
            await page.select_option('#owner','decision_maker')
            await page.locator('#build-plan').click()
            assert title in await page.locator('#plan-title').inner_text()
            assert 'Ничего не отправлено' in await page.locator('#form-message').inner_text()
        results.append('four_distinct_segments_and_fixed_demo_links')
        await page.select_option('#owner','not_assigned')
        assert await page.locator('#plan').is_hidden()
        await page.locator('#build-plan').click()
        assert 'Сначала определите ответственного' in await page.locator('#plan-steps li').first.inner_text()
        results.append('changing_answer_invalidates_previous_result')
        async with page.expect_download() as info:
            await page.locator('#download-brief').click()
        download=await info.value
        await download.save_as(str(OUT/'synthetic-brief.txt'))
        assert 'Локальный черновик. Не отправлен.' in (OUT/'synthetic-brief.txt').read_text(encoding='utf-8-sig')
        results.append('download_is_local_draft')
        await page.evaluate("document.querySelector('#model').add(new Option('<script>BAD</script>', '__proto__'))")
        await page.select_option('#model','__proto__')
        await page.locator('#build-plan').click()
        assert await page.locator('#plan').is_hidden()
        assert 'Выберите варианты из списка' in await page.locator('#form-message').inner_text()
        results.append('injected_select_value_rejected')
        await load(page,'thailand_desk')
        assert await page.locator('#model').input_value()=='thailand_desk'
        await load(page,'__proto__')
        assert await page.locator('#model').input_value()==''
        results.append('only_allowlisted_campaign_segment_is_read')
        for width in [320,360,390,768,1024,1440]:
            await page.set_viewport_size({'width':width,'height':900})
            await load(page)
            assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'overflow at '+str(width)
            if width in [390,1440]:
                await page.screenshot(path=str(OUT/f'agency-{width}.png'),full_page=True)
                await page.screenshot(path=str(OUT/f'hero-{width}.png'))
        results.append('six_responsive_widths_no_horizontal_overflow')
        await page.set_viewport_size({'width':390,'height':844})
        await page.select_option('#model','new_direction'); await page.select_option('#goal','build_direction'); await page.select_option('#owner','decision_maker')
        await page.locator('#build-plan').click()
        assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        await page.locator('#plan').screenshot(path=str(OUT/'qualification-mobile.png'))
        await page.locator('summary').first.click()
        assert await page.locator('details').first.get_attribute('open') is not None
        results.append('mobile_result_and_native_faq')
        await load(page,javascript=False)
        assert await page.locator('#model').is_disabled()
        assert await page.locator('a[href="/mira/marketplace.html"]').count()>=1
        results.append('no_javascript_no_submit_static_links_remain')
        assert len(requests)==0, requests
        results.append('zero_network_requests_no_external_submissions')
        (OUT/'browser-results.json').write_text(json.dumps({'scope':'offline DOM, not live E2E','passed':len(results),'cases':results,'network_requests':requests},ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'passed':len(results),'cases':results},ensure_ascii=False,indent=2))
        await browser.close()

if __name__=='__main__': asyncio.run(main())
