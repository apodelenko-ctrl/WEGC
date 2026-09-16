"""Offline DOM/fixture API tests; no deployed navigation, contact or file release.

Browser hashing in this restricted about:blank harness is bridged to hashlib.
The production JS uses native WebCrypto. Synthetic downloads are intercepted.
"""
import asyncio,hashlib,json,os,re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
BYTES=b'%PDF-1.4\nSYNTHETIC TEST MATERIAL\n%%EOF'
HASH=hashlib.sha256(BYTES).hexdigest()
async def shell(page):
 text=(ROOT/'mira/library.html').read_text()
 text=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',text)
 text=re.sub(r'<script[^>]*>.*?</script>','',text,flags=re.S)
 text=re.sub(r'<link[^>]*>','',text)
 await page.set_content(text)
 for f in ['marketplace.css','library.css']:await page.add_style_tag(content=(ROOT/'mira'/f).read_text())
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  results=[]
  for mode,width,height in [('normal',1440,1000),('normal-mobile',390,844),('closed',390,844),('expired',390,844),('hash-mismatch',390,844),('unavailable',390,844)]:
   page=await browser.new_page(viewport={'width':width,'height':height});page.set_default_timeout(4000)
   external=[];page.on('request',lambda r:external.append(r.url));await page.route('**/*',lambda r:r.abort())
   await page.expose_function('testDigest',lambda b:list(hashlib.sha256(bytes(b)).digest()))
   await shell(page)
   mock=r'''const crypto={subtle:{digest:async(_,b)=>new Uint8Array(await window.testDigest(Array.from(b))).buffer}};
    const fetch=async(path,opts={})=>{window.calls.push({path,method:opts.method||'GET'});let data={};
    if(window.mode==='unavailable')throw Error('SYNTHETIC offline');
    if(path.endsWith('/session'))data={membership:{role:'agency_owner'}};
    else if(path==='/mira/api/developers')data={records:[{id:'DEV-aaaaaaaaaaaaaaaaaaaaaaaa',name:'SYNTHETIC FAMILY',markets:['phuket'],assigned_project_count:1}],next_cursor:null};
    else if(path.endsWith('/developers/DEV-aaaaaaaaaaaaaaaaaaaaaaaa'))data={id:'DEV-aaaaaaaaaaaaaaaaaaaaaaaa',name:'SYNTHETIC FAMILY',projects:[{id:'TEST-PROJECT',name:'SYNTHETIC PROJECT',market:'phuket'}]};
    else if(path.endsWith('/projects/TEST-PROJECT'))data={project:{id:'TEST-PROJECT',name:'SYNTHETIC PROJECT',market:'phuket',developer_family:'SYNTHETIC FAMILY'},registration_eligible:false};
    else if(path.endsWith('/projects/TEST-PROJECT/materials'))data={records:window.mode==='closed'?[]:[{id:'MAT-test',title:'SYNTHETIC BROCHURE',kind:'brochure',language:'en',size_bytes:window.bytes.length,mime_type:'application/pdf',sha256:window.hash,expires_at:'SYNTHETIC REVIEW DATE'}],next_cursor:null,delivery_status:window.mode==='closed'?'not_configured_or_closed':'configured_access_rechecked_at_download'};
    else if(path.endsWith('/materials/MAT-test/download')){
      if(window.mode==='expired')return new Response(JSON.stringify({error:'material_not_available'}),{status:404,headers:{'Content-Type':'application/json'}});
      const data=new Uint8Array(window.bytes);if(window.mode==='hash-mismatch')data[10]^=1;
      return new Response(data,{headers:{'Content-Type':'application/pdf','Content-Length':String(data.length)}});
    }else throw Error('Unexpected mock path '+path);
    return new Response(JSON.stringify(data),{headers:{'Content-Type':'application/json'}});
   };'''
   script=(ROOT/'mira/library.mjs').read_text()
   await page.evaluate('(async()=>{window.mode='+json.dumps(mode)+';window.calls=[];window.downloads=[];window.hash='+json.dumps(HASH)+';window.bytes='+json.dumps(list(BYTES))+';HTMLAnchorElement.prototype.click=function(){window.downloads.push({href:this.href,name:this.download});};'+mock+script+'})()')
   if mode=='unavailable':
    await page.wait_for_function("document.querySelector('#library-content').textContent.includes('Рабочий каталог пока недоступен')")
    assert await page.locator('[data-group]').count()==0
   else:
    await page.locator('[data-group]').click();await page.locator('[data-project]').click()
    await page.wait_for_function("document.querySelector('#library-content').textContent.includes('Коммерческая регистрация не открыта')")
    if mode=='closed':assert await page.locator('[data-asset]').count()==0
    else:
     await page.locator('[data-asset]').click()
     await page.wait_for_function("!document.querySelector('[data-asset]').disabled")
     downloads=await page.evaluate('window.downloads')
     if mode.startswith('normal'):assert len(downloads)==1 and downloads[0]['name']=='MAT-test.pdf'
     else:assert downloads==[]
     assert 'Проверяем права' not in await page.locator('.download-status').inner_text()
   assert not external,external
   calls=await page.evaluate('window.calls');assert all(x['method']=='GET' for x in calls)
   assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),mode
   await page.screenshot(path='/mnt/data/mira-library-'+mode+'.png',full_page=True)
   results.append({'view':mode,'fixture_get_requests':len(calls),'external_requests':0,'overflow':False,'mode':'offline DOM; synthetic API and intercepted download; not deployed E2E'})
   await page.close()
  await browser.close()
  Path('/mnt/data/mira-cp09-ui.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
asyncio.run(main())
