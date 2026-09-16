"""Offline DOM regression only. No navigations or external forms are sent.
Test fixture replaces location/history/fetch to exercise controls under an
execution environment that blocks browser navigation. NOT deployed E2E QA.
Requires Playwright and Chromium; CHROMIUM_PATH may override the binary path.
"""
import asyncio,json,re,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
async def shell(page,name):
    raw=(ROOT/'mira'/name).read_text()
    raw=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',raw)
    raw=re.sub(r'<script[^>]*>.*?</script>','',raw,flags=re.S)
    raw=re.sub(r'<link[^>]*>','',raw)
    raw=raw.replace('<head>','<head><base href="https://mira.test/mira/'+name+'">')
    await page.set_content(raw,wait_until='domcontentloaded')
    await page.add_style_tag(content=(ROOT/'mira/marketplace.css').read_text())
async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=await browser.new_page(viewport={'width':1400,'height':950})
    page.set_default_timeout(4000)
    await page.route('**/*',lambda route:route.abort())
    catalog=json.loads((ROOT/'mira/data/catalog.json').read_text())
    await shell(page,'marketplace.html')
    core=(ROOT/'mira/core.mjs').read_text().replace('export ','')
    app=re.sub(r'^import .*?;\n','',(ROOT/'mira/marketplace.mjs').read_text())
    harness="const location=new URL('https://mira.test/mira/marketplace.html');const history={pushState(a,b,u){location.href=String(u);}};const crypto={randomUUID:()=>String(++window.testID)};"
    await page.evaluate('(async()=>{window.testID=0;window.testRequests=[];'+harness+'const fetch=async(url,opts)=>{window.testRequests.push({url,opts});return new Response('+json.dumps(json.dumps(catalog,ensure_ascii=False))+',{headers:{"Content-Type":"application/json"}});};'+core+'\n'+app+'})()')
    assert await page.locator('#cards .card').count()==len(catalog['projects'])
    await page.locator('#search').fill('sierra')
    assert await page.locator('#cards .card').count()==1
    await page.locator('#cards a').click()
    assert await page.locator('#client-ref').count()==1
    await page.locator('#lead-form button').click()
    assert 'DEMO-CLIENT-1' in await page.locator('#content').inner_text()
    assert 'Не подтверждена застройщиком' in await page.locator('#content').inner_text()
    await page.locator('[data-payment]').click()
    assert 'Платёжная поддержка' in await page.locator('h1').inner_text()
    assert 'Не передано на исполнение' in await page.locator('#content').inner_text()
    await page.locator('[data-view="catalog"]').click()
    await page.locator('#search').fill('sierra');await page.locator('#cards a').click();await page.locator('#lead-form button').click()
    assert 'уже есть' in await page.locator('#lead-message').inner_text()
    await page.locator('[data-view="profile"]').click()
    assert 'DEMO-AGENCY' in await page.locator('#content').inner_text()
    await page.set_viewport_size({'width':390,'height':844})
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    requests=await page.evaluate('window.testRequests');assert len(requests)==1 and requests[0]['opts'].get('method','GET')=='GET'
    await page.screenshot(path=str(ROOT/'mobile-pilot-demo-qa.png'),full_page=True)
    # Real pilot UI with an in-memory API mock, never an external POST.
    await shell(page,'pilot.html')
    script=(ROOT/'mira/pilot.mjs').read_text()
    mock=r'''const location=new URL('https://mira.test/mira/pilot.html');const crypto={randomUUID:()=> 'TEST-IDEMPOTENCY'};
    const fetch=async(url,opts={})=>{window.pilotCalls.push({url,method:opts.method||'GET'});let data={};
    if(url.endsWith('/session'))data={subject:'TEST',email:'TEST@example.test',membership:{role:'agency_owner'},applications_enabled:true,privacy_version:'TEST-v1',privacy_notice_url:'https://mira.test/privacy-test'};
    else if(url.endsWith('/applications')&&opts.method==='POST'){window.savedApplication=true;data={id:'TEST-RECEIPT',status:'received',received_at:'TEST-TIME'};}
    else if(url.endsWith('/applications'))data={records:window.savedApplication?[{id:'TEST-RECEIPT',company:'TEST COMPANY',city:'TEST CITY',status:'received',created_at:'TEST-TIME'}]:[]};
    else throw Error('Unexpected mock endpoint');return new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});};'''
    await page.evaluate('(async()=>{window.pilotCalls=[];window.savedApplication=false;'+mock+script+'})()')
    await page.locator('input[name="company"]').fill('TEST COMPANY');await page.locator('input[name="city"]').fill('TEST CITY');await page.locator('input[name="name"]').fill('TEST REPRESENTATIVE');await page.locator('input[type="checkbox"]').check();await page.locator('#application button').click()
    await page.wait_for_function("document.querySelector('#application [role=status]').textContent.includes('TEST-RECEIPT')")
    assert len([r for r in await page.evaluate('window.pilotCalls') if r['method']=='POST'])==1
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    await shell(page,'pilot.html')
    await page.evaluate('(async()=>{const fetch=async()=>new Response("not api",{headers:{"Content-Type":"text/html"}});'+script+'})()')
    assert await page.locator('form').count()==0
    assert 'Заявка не отправлена' in await page.locator('#pilot-content').inner_text()
    await browser.close()
    print(json.dumps({'offline_demo_flow':'passed','duplicate_draft':'passed','no_external_posts':'passed','pilot_mock_receipt':'passed','pilot_non_api_failure_closed':'passed','mobile_overflow':'passed','deployed_e2e':'not_run'},ensure_ascii=False))
if __name__=='__main__':asyncio.run(main())
