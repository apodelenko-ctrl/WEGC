"""Browser acceptance against local production Worker code, signed synthetic JWTs
and SQLite. No production data/email; NOT a Cloudflare Access/D1 live test."""
import asyncio,json,os,subprocess,sys,tempfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path(os.environ.get('MIRA_QA_OUTPUT',str(Path(tempfile.gettempdir())/'mira-pilot-browser')))
async def main():
 OUTPUT.mkdir(parents=True,exist_ok=True)
 process=subprocess.Popen(['node','tests/mira-pilot-browser-server.mjs'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  origin=process.stdout.readline().strip().removeprefix('FIXTURE_ORIGIN=')
  assert origin.startswith('http://127.0.0.1:')
  async with async_playwright() as p:
   browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' if Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists() else None),headless=True)
   contexts=[await browser.new_context(extra_http_headers={'x-mira-fixture-user':who},timezone_id='UTC',viewport={'width':1440,'height':1000}) for who in ['TEST-OPERATOR','TEST-APPLICANT','TEST-OTHER']]
   operator,applicant,other=[await c.new_page() for c in contexts]
   errors=[]
   for page in [operator,applicant,other]:
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' and ('Content Security Policy' in m.text or 'violates' in m.text) else None)
   await applicant.goto(origin+'/mira/pilot.html')
   await applicant.locator('[name=company]').fill('SYNTHETIC AGENCY')
   await applicant.locator('[name=city]').fill('TEST CITY')
   await applicant.locator('[name=name]').fill('TEST REPRESENTATIVE')
   await applicant.locator('#application input[type=checkbox]').check()
   await applicant.locator('#application button[type=submit]').click()
   await applicant.locator('#application [role=status]').filter(has_text='Получено МИРА').wait_for()
   appid=await applicant.locator('[data-application]').first.get_attribute('data-application')
   assert not await applicant.locator('[data-section=operator]').is_visible()
   await operator.goto(origin+'/mira/pilot.html')
   await operator.locator('[data-section=operator]').click()
   await operator.locator('[data-review]').first.click()
   async def review(status):
    await operator.locator('#application-review [name=status]').select_option(status)
    await operator.locator('#application-review [name=reason]').fill('SYNTHETIC reviewed evidence')
    await operator.locator('#application-review button[type=submit]').click()
   await review('review')
   await operator.locator('[data-proof=application_qualification]').wait_for()
   async def proof(kind,id):
    form=operator.locator('[data-proof='+kind+']')
    await form.locator('[name=id]').fill(id)
    await form.locator('[name=storage_ref]').fill('vault:SYNTHETIC-ONLY')
    await form.locator('[name=verified_at]').fill((datetime.now(timezone.utc)-timedelta(minutes=2)).strftime('%Y-%m-%dT%H:%M'))
    await form.locator('[name=reviewed]').check()
    await form.locator('button[type=submit]').click()
    await form.locator('[role=status]').filter(has_text='сохранено').wait_for()
   await proof('application_qualification','EVID-TEST-QUALIFIED')
   await review('qualified')
   await operator.locator('[data-app-access]').click()
   await operator.locator('#agency-create button[type=submit]').click()
   await operator.locator('#agency-state').wait_for()
   agencyid=await operator.locator('#pilot-content>code').inner_text()
   await operator.locator('#agency-state [name=status]').select_option('active')
   await operator.locator('#agency-state [name=agreement_ref]').fill('EVID-DOES-NOT-EXIST')
   await operator.locator('#agency-state button[type=submit]').click()
   await operator.locator('#agency-state [role=status]').filter(has_text='Подтверждение отсутствует').wait_for()
   await proof('agency_agreement','EVID-TEST-AGREEMENT')
   await operator.locator('#agency-state [name=status]').select_option('active')
   await operator.locator('#agency-state button[type=submit]').click()
   await operator.get_by_text('Договор: подтверждение актуально',exact=True).wait_for()
   await operator.locator('#bind-owner input[type=checkbox]').check()
   await operator.locator('#bind-owner button[type=submit]').click()
   await operator.locator('#bind-owner [role=status]').filter(has_text='Представитель назначен').wait_for()
   await operator.screenshot(path=str(OUTPUT/'operator-agency-desktop.png'),full_page=True)
   await operator.locator('#back-application').click()
   await operator.locator('#application-review [name=status]').select_option('onboarded')
   await operator.locator('#application-review [name=agency_id]').fill(agencyid)
   await operator.get_by_text('Добавить подтверждение подключения',exact=True).click()
   await proof('agency_onboarding','EVID-TEST-ONBOARDING')
   await review('onboarded')
   await operator.get_by_text('Onboarding завершён · версия 3',exact=True).wait_for()
   await applicant.reload()
   await applicant.locator('[data-section=profile]').click()
   await applicant.get_by_text('SYNTHETIC AGENCY',exact=True).wait_for()
   await applicant.screenshot(path=str(OUTPUT/'agency-profile-desktop.png'),full_page=True)
   await other.goto(origin+'/mira/pilot.html')
   denied=await other.evaluate("async id=>{const r=await fetch('/mira/api/applications/'+id);return r.status}",appid)
   assert denied==404
   admin_denied=await other.evaluate("async()=>{const r=await fetch('/mira/api/admin/agencies');return r.status}")
   assert admin_denied==403
   await operator.locator('[data-app-access]').click()
   await operator.locator('[data-agency="'+agencyid+'"]').click()
   await operator.locator('.member-access input[type=checkbox]').check()
   await operator.locator('.member-access button').click()
   await operator.get_by_text('Руководитель · Доступ выключен',exact=True).wait_for()
   await applicant.reload();await applicant.locator('[data-section=profile]').click()
   await applicant.get_by_text('Оператор ещё не назначил доступ агентству.',exact=True).wait_for()
   denied=await applicant.evaluate("async()=>{const r=await fetch('/mira/api/profile');return r.status}")
   assert denied==403
   await operator.locator('.member-access input[type=checkbox]').check()
   await operator.locator('.member-access button').click()
   await operator.get_by_text('Руководитель · Доступ включён',exact=True).wait_for()
   assert await applicant.evaluate("async()=>{const r=await fetch('/mira/api/profile');return r.status}")==200
   history=await operator.evaluate("async subject=>(await fetch('/mira/api/admin/audit?entity_type=membership&entity_id='+subject)).json()",'TEST-APPLICANT')
   assert [r['status'] for r in history['records']]==['agency_owner_active','agency_owner_inactive','agency_owner_active']
   await contexts[1].set_extra_http_headers({'x-mira-fixture-user':'TEST-APPLICANT','x-mira-fixture-expired':'true'})
   assert await applicant.evaluate("async()=>{const r=await fetch('/mira/api/session');return r.status}")==401
   await contexts[1].set_extra_http_headers({'x-mira-fixture-user':'TEST-APPLICANT'})
   restored=await applicant.evaluate("async id=>(await fetch('/mira/api/applications/'+id)).json()",appid)
   assert restored['application']['id']==appid
   # Exercise real audit pagination rather than replacing API responses in the browser.
   await operator.evaluate("""async id=>{for(let i=0;i<51;i++){const r=await fetch('/mira/api/admin/agencies',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,name:'SYNTHETIC AGENCY',city:'TEST CITY',status:'active',agreement_ref:'EVID-TEST-AGREEMENT'})});if(!r.ok)throw Error(await r.text());}}""",agencyid)
   await operator.locator('#back-agencies').click();await operator.locator('[data-agency="'+agencyid+'"]').click()
   await operator.locator('#agency-audit button').filter(has_text='Ещё события').wait_for()
   assert await operator.locator('#agency-audit .row').count()==50
   await operator.locator('#agency-audit button').click()
   await operator.locator('#agency-audit .row').nth(52).wait_for()
   for width in [390,768,1440]:
    await operator.set_viewport_size({'width':width,'height':900})
    assert await operator.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   await operator.set_viewport_size({'width':390,'height':844})
   await operator.screenshot(path=str(OUTPUT/'operator-agency-mobile.png'),full_page=True)
   assert not errors,errors
   await browser.close()
  result={'local_signed_worker_browser':'passed','receipt_and_reload':'passed','operator_qualification':'passed','agreement_activation_owner_binding':'passed','onboarding':'passed','other_identity_isolation':'passed','activation_without_evidence':'denied','revocation':'passed','restoration_with_audit':'passed','expired_session_receipt_preserved':'passed','audit_pagination':'passed','widths':[390,768,1440],'page_errors':errors,'live_access_d1_acceptance':False}
  (OUTPUT/'report.json').write_text(json.dumps(result,indent=2))
  print(json.dumps(result))
 finally:
  process.terminate();process.wait(timeout=10)
if __name__=='__main__':asyncio.run(main())
