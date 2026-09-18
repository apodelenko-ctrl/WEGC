import sys, pathlib, tempfile, time, json, unittest, hashlib, hmac, concurrent.futures
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from core import Store,Engine,Dispatcher
from adapters import normalize,Sender,AnthropicIntelligence
from enrich import extract
from service import handler
from http.server import ThreadingHTTPServer
import threading, urllib.request

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=pathlib.Path(self.tmp.name)/'db.sqlite'; self.s=Store(self.path)
        self.ctx={'name':'Synthetic agency','role':'agency','crm_account_id':'fixture-account'}
        self.s.bind('fixture',self.ctx,'telegram','bot','10','synthetic operator evidence')
        self.facts=[{'id':'about','text':'SYNTHETIC APPROVED RESPONSE','source':'https://example.invalid/fixture',
                     'audience':'agency','approved':True,'valid_until':time.time()+1000}]
        self.calls=[]
        def ai(ctx): self.calls.append(ctx); return {'intent':'QUESTION','fact_ids':['about'],'handoff':False}
        self.ai=ai; self.engine=Engine(self.s,ai,self.facts)
    def event(self, mid='1', **kw):
        return {'channel':'telegram','account':'bot','peer':'10','message_id':mid,'text':'question',
                'occurred_at':time.time(),**kw}
    def process(self, **kw):
        result=self.s.ingest(self.event(**kw)); self.engine.process(result['id']); return result['id']
    def replies(self): return [r for r in self.s.rows('outbox') if r['kind']=='reply']
    def test_durable_restart_and_duplicate(self):
        e=self.event(); r=self.s.ingest(e); s2=Store(self.path)
        self.assertTrue(s2.ingest(e)['duplicate']); self.assertEqual(len(s2.rows('inbox')),1)
        self.engine.process(r['id']); self.assertEqual(self.engine.process(r['id']),'skipped'); self.assertEqual(len(self.replies()),1)
    def test_unverified_endpoint_quarantine(self):
        r=self.s.ingest(self.event(peer='unknown')); self.assertEqual(r['state'],'identity_review')
        self.assertEqual(self.engine.process(r['id']),'skipped'); self.assertEqual(self.calls,[])
    def test_binding_conflict(self):
        with self.assertRaises(ValueError): self.s.bind('other',{},'telegram','bot','10','evidence')
    def test_release_after_verified_binding(self):
        r=self.s.ingest(self.event(peer='20')); self.s.bind('fixture',self.ctx,'telegram','bot','20','verified')
        self.s.resolve(r['id']); self.engine.process(r['id']); self.assertEqual(len(self.replies()),1)
    def test_cross_channel_context_and_prior_outreach(self):
        self.s.bind('fixture',self.ctx,'whatsapp','sender','20','verified link')
        self.s.record_outreach('fixture',{'provider_id':'synthetic-sent','campaign':'fixture','template':'fixture','text':'earlier outreach'})
        self.process()
        r=self.s.ingest(self.event(mid='2',channel='whatsapp',account='sender',peer='20')); self.engine.process(r['id'])
        self.assertEqual(self.calls[-1]['context']['name'],'Synthetic agency')
        self.assertTrue(any(x.get('campaign')=='fixture' for x in self.calls[-1]['history']))
        self.assertTrue(any(x.get('channel')=='telegram' for x in self.calls[-1]['history']))
    def test_contact_isolation(self):
        self.s.bind('other',{'role':'agency'},'telegram','bot','30','verified')
        self.s.ingest(self.event(peer='30',text='PRIVATE OTHER'))
        self.process(); self.assertNotIn('PRIVATE OTHER',json.dumps(self.calls))
    def test_future_messages_not_in_context(self):
        r=self.s.ingest(self.event()); self.s.ingest(self.event(mid='2',text='FUTURE'))
        self.engine.process(r['id']); self.assertNotIn('FUTURE',json.dumps(self.calls))
    def test_handoff_pauses_followup(self):
        self.process(text='Позвоните мне'); self.process(mid='2',text='question')
        self.assertEqual(self.calls,[]); self.assertEqual(self.replies(),[])
        self.assertEqual(len([r for r in self.s.rows('outbox') if r['kind']=='crm_task']),1)
    def test_unknown_facts_handoff(self):
        self.engine=Engine(self.s,lambda _: {'intent':'QUESTION','fact_ids':['invented']},self.facts)
        self.process(); self.assertEqual(self.replies(),[]); self.assertEqual(self.s.rows('contacts')[0]['paused'],1)
    def test_expired_and_wrong_role_facts_excluded(self):
        self.facts[0]['valid_until']=0; self.process(); self.assertEqual(self.calls[0]['facts'],[]); self.assertEqual(self.replies(),[])
    def test_private_scope_excluded(self):
        self.facts[0]['contact_ids']=['other']; self.process(); self.assertEqual(self.calls[0]['facts'],[])
    def test_untrusted_model_prose_never_sent(self):
        self.engine=Engine(self.s,lambda _: {'intent':'QUESTION','fact_ids':['about'],'reply':'INVENTED PRICE'},self.facts)
        self.process(); self.assertNotIn('INVENTED',self.replies()[0]['payload'])
    def test_global_stop_cancels_pending_reply(self):
        self.process(); oid=self.replies()[0]['id']; self.process(mid='2',text='stop')
        calls=[]; d=Dispatcher(self.s,lambda *args:calls.append(args),True)
        self.assertEqual(d.dispatch(oid),'cancelled'); self.assertEqual(calls,[])
        self.s.resume('fixture','operator','review'); self.assertEqual(self.s.rows('contacts')[0]['suppressed'],1)
    def test_model_failure_creates_handoff(self):
        def fail(_): raise TimeoutError('private provider error')
        self.engine=Engine(self.s,fail,self.facts); self.process()
        self.assertNotIn('private provider error',json.dumps(self.s.rows('outbox')))
        self.assertEqual(self.s.rows('contacts')[0]['paused'],1)
    def test_sends_off_by_default(self):
        self.process(); self.assertEqual(Dispatcher(self.s,None).dispatch(self.replies()[0]['id']),'disabled')
    def test_ambiguous_send_not_retried(self):
        self.process(); oid=self.replies()[0]['id']; calls=[]
        def fail(*a): calls.append(1); raise TimeoutError()
        d=Dispatcher(self.s,fail,True); self.assertEqual(d.dispatch(oid),'uncertain')
        self.assertEqual(d.dispatch(oid),'skipped'); self.assertEqual(len(calls),1)
    def test_sent_receipt_persisted(self):
        self.process(); oid=self.replies()[0]['id']; d=Dispatcher(self.s,lambda *a:'provider-fixture',True)
        self.assertEqual(d.dispatch(oid),'sent'); self.assertEqual(d.dispatch(oid),'skipped')
        self.assertEqual(self.replies()[0]['provider_id'],'provider-fixture')
    def test_reply_window_enforced_at_dispatch(self):
        self.s.bind('fixture',self.ctx,'whatsapp','sender','20','verified')
        self.process(channel='whatsapp',account='sender',peer='20',occurred_at=time.time()-90000)
        self.assertEqual(Dispatcher(self.s,None,True).dispatch(self.replies()[0]['id']),'expired')
    def test_fact_expiry_enforced_at_dispatch(self):
        self.process(); oid=self.replies()[0]['id']
        with self.s.tx() as db:
            p=json.loads(self.replies()[0]['payload']); p['valid_until']=0
            db.execute('UPDATE outbox SET payload=? WHERE id=?',(json.dumps(p),oid))
        self.assertEqual(Dispatcher(self.s,None,True).dispatch(oid),'expired')
    def test_concurrent_duplicate_processing(self):
        eid=self.s.ingest(self.event())['id']
        with concurrent.futures.ThreadPoolExecutor(4) as pool: list(pool.map(self.engine.process,[eid]*4))
        self.assertEqual(len(self.replies()),1); self.assertEqual(len(self.calls),1)
    def test_concurrent_independent_contacts(self):
        ids=[]
        for i in range(20):
            self.s.bind('c'+str(i),self.ctx,'telegram','bot','p'+str(i),'synthetic')
            ids.append(self.s.ingest(self.event(peer='p'+str(i)))['id'])
        with concurrent.futures.ThreadPoolExecutor(4) as pool: outcomes=list(pool.map(self.engine.process,ids))
        self.assertEqual(outcomes.count('processed'),20); self.assertEqual(len(self.replies()),20)
    def test_out_of_order_processing_deferred(self):
        a=self.s.ingest(self.event()); b=self.s.ingest(self.event(mid='2'))
        self.assertEqual(self.engine.process(b['id']),'busy'); self.engine.process(a['id'])
        self.assertEqual(self.engine.process(b['id']),'processed')
    def test_telegram_secret_and_echo(self):
        e={'update_id':1,'message':{'chat':{'id':10,'type':'private'},'from':{'id':10},'text':'hi','date':time.time()}}
        raw=json.dumps(e).encode()
        with self.assertRaises(PermissionError): normalize('telegram','bot',raw,{}, {'WEBHOOK_SECRET':'secret'})
        self.assertEqual(len(normalize('telegram','bot',raw,{'X-Telegram-Bot-Api-Secret-Token':'secret'},{'WEBHOOK_SECRET':'secret'})),1)
        e['message']['from']['id']=20
        self.assertEqual(normalize('telegram','bot',json.dumps(e).encode(),{'X-Telegram-Bot-Api-Secret-Token':'secret'},{'WEBHOOK_SECRET':'secret'}),[])
    def test_whatsapp_batch_signature(self):
        data={'entry':[{'changes':[{'value':{'metadata':{'phone_number_id':'sender'},'messages':[
          {'from':'20','id':str(i),'timestamp':str(time.time()),'text':{'body':'hi'}} for i in range(2)]}}]}]}
        raw=json.dumps(data).encode(); signature='sha256='+hmac.new(b'secret',raw,hashlib.sha256).hexdigest()
        self.assertEqual(len(normalize('whatsapp','sender',raw,{'X-Hub-Signature-256':signature},{'META_APP_SECRET':'secret'})),2)
        with self.assertRaises(PermissionError): normalize('whatsapp','sender',raw+b' ',{'X-Hub-Signature-256':signature},{'META_APP_SECRET':'secret'})
    def test_max_inbound(self):
        data={'update_type':'message_created','timestamp':time.time()*1000,'message':{
         'sender':{'user_id':20},'recipient':{'chat_type':'dialog'},'body':{'mid':'fixture','text':'hi'}}}
        events=normalize('max','max-bot',json.dumps(data).encode(),{'X-Max-Bot-Api-Secret':'secret'},{'MAX_WEBHOOK_SECRET':'secret'})
        self.assertEqual(events[0]['peer'],'20')
    def test_enrichment_no_invented_membership(self):
        rows=extract('<a href="tel:+12345678901">phone</a><a href="https://wa.me/12345678901">WA</a><a href="https://t.me/fixture">TG</a>', 'https://example.invalid')
        self.assertEqual(len(rows),3); self.assertEqual(rows[0]['normalized_phone'],rows[1]['normalized_phone'])
        self.assertTrue(all(not r['membership_verified'] for r in rows))
    def test_sender_account_scoping_and_crm_mapping(self):
        calls=[]
        def transport(url,body,headers): calls.append((url,body)); return {'id':'fixture-note'}
        sender=Sender({'ESPO_URL':'https://example.invalid','ESPO_API_KEY':'fixture'},transport)
        self.assertEqual(sender('crm_note',{'context':self.ctx},'event'),'fixture-note')
        self.assertEqual(calls[0][1]['parentId'],'fixture-account')
        with self.assertRaises(ValueError): sender('reply',{'event':self.event(),'text':'fixture'},'event')
    def test_http_ingress_persists_before_ack(self):
        env={'TELEGRAM_ACCOUNT_ID':'bot','WEBHOOK_SECRET':'fixture-secret'}
        server=ThreadingHTTPServer(('127.0.0.1',0),handler(self.s,env))
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            data={'update_id':1,'message':{'chat':{'id':10,'type':'private'},'from':{'id':10},'text':'hi','date':time.time()}}
            req=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+'/telegram',data=json.dumps(data).encode(),
                 headers={'X-Telegram-Bot-Api-Secret-Token':'fixture-secret'})
            with urllib.request.urlopen(req) as res: result=json.load(res)
            self.assertEqual(result['accepted'][0]['state'],'pending'); self.assertEqual(len(Store(self.path).rows('inbox')),1)
        finally: server.shutdown(); server.server_close(); thread.join()

if __name__=='__main__': unittest.main()
