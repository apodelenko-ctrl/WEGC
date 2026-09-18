import sys,pathlib,unittest,tempfile,time,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from core import Store,Engine,Dispatcher
from deal_flow import DealFlow,normalize_catalog

class DealFlowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.s=Store(pathlib.Path(self.tmp.name)/'db',profile='mira_agency')
  self.s.bind('agency',{'profile':'mira_agency','role':'agency','crm_account_id':'fixture'},'telegram','bot','peer','fixture')
  self.catalog=normalize_catalog({'projects':[{'id':'fixture-condo','name':'Synthetic condo','kind':'condo','district':'Банг Тао'},
    {'id':'fixture-town','name':'Synthetic townhouse','kind':'villa','propertyTypes':['townhouse']}]},market='phuket',source='https://example.invalid/feed')
  self.flow=DealFlow(self.s,self.catalog)
 def event(self,text,mid='1'):
  return {'profile':'mira_agency','channel':'telegram','account':'bot','peer':'peer','message_id':mid,'text':text,'occurred_at':time.time()}
 def decision(self,action,**quotes):
  return {'intent':'REQUEST_PROJECTS','action':action,'criteria_updates':{k:{'quote':v} for k,v in quotes.items()}}
 def process(self,text,decision,mid='1'):
  eid=self.s.ingest(self.event(text,mid))['id']
  Engine(self.s,lambda _:decision,[],self.flow).process(eid)
  return eid
 def test_multi_turn_brief_no_repeated_questions(self):
  self.process('Пхукет квартира',self.decision('collect_brief',market='Пхукет',property_type='квартира'))
  replies=[json.loads(r['payload'])['text'] for r in self.s.rows('outbox') if r['kind']=='reply']
  self.assertIn('цели',replies[0]); self.assertNotIn('каком рынке',replies[0])
  self.process('для жизни бюджет уточняется',self.decision('shortlist',purpose='для жизни',budget='бюджет уточняется'),'2')
  notes=[json.loads(r['payload']) for r in self.s.rows('outbox') if r['kind']=='crm_note']
  self.assertTrue(any(n.get('research_shortlist') for n in notes))
  replies=[json.loads(r['payload'])['text'] for r in self.s.rows('outbox') if r['kind']=='reply']
  self.assertIn('Synthetic condo',replies[-1]); self.assertIn('не подтверждены',replies[-1])
 def test_invented_criteria_rejected(self):
  self.process('квартира',self.decision('collect_brief',budget='999999 USD'))
  self.assertEqual(self.flow.current('agency'),{})
  self.assertEqual(self.s.rows('contacts')[0]['paused'],1)
 def test_profile_cannot_enable_deal_flow(self):
  buyer=Store(pathlib.Path(self.tmp.name)/'buyer',profile='phuket_buyer')
  with self.assertRaises(ValueError): DealFlow(buyer,self.catalog)
 def test_model_cannot_invent_shortlist(self):
  d=self.decision('shortlist',market='Пхукет',property_type='квартира',purpose='жизнь',budget='уточняется')
  d['project_ids']=['imaginary']; self.process('Пхукет квартира жизнь уточняется',d)
  result=json.dumps(self.s.rows('outbox'),ensure_ascii=False)
  self.assertNotIn('imaginary',result); self.assertIn('fixture-condo',result)
 def test_request_specialist_preserves_shortlist_and_pauses(self):
  self.process('Пхукет квартира жизнь уточняется',self.decision('shortlist',market='Пхукет',property_type='квартира',purpose='жизнь',budget='уточняется'))
  self.process('Проверьте условия',self.decision('request_specialist'),'2')
  tasks=[json.loads(r['payload']) for r in self.s.rows('outbox') if r['kind']=='crm_task']
  self.assertEqual(tasks[-1]['research_shortlist'][0]['id'],'fixture-condo')
  self.assertEqual(self.s.rows('contacts')[0]['paused'],1)
 def test_explicit_call_keeps_brief_and_shortlist(self):
  self.process('Пхукет квартира жизнь уточняется',self.decision('shortlist',market='Пхукет',property_type='квартира',purpose='жизнь',budget='уточняется'))
  self.process('Позвоните мне',{},'2')
  tasks=[json.loads(r['payload']) for r in self.s.rows('outbox') if r['kind']=='crm_task']
  self.assertEqual(len(tasks),1)
  self.assertEqual(tasks[0]['research_shortlist'][0]['id'],'fixture-condo')
  self.assertEqual(self.s.rows('contacts')[0]['paused'],1)
 def test_crm_task_assignee_native_contract(self):
  from adapters import Sender
  calls=[]
  def post(url,body,headers): calls.append(body); return {'id':'fixture-task'}
  payload={'context':{'crm_account_id':'fixture'},'intent':'REQUEST_PROJECTS'}
  env={'ESPO_URL':'https://example.invalid','ESPO_API_KEY':'fixture'}
  with self.assertRaises(ValueError): Sender(env,post)('crm_task',payload,'eid')
  self.assertEqual(calls,[])
  env['ESPO_TASK_ASSIGNEE_ID']='fixture-operator'
  Sender(env,post)('crm_task',payload,'eid')
  self.assertEqual(calls[0]['assignedUserId'],'fixture-operator')
 def test_townhouse_not_misrepresented_as_villa(self):
  plan=self.flow.propose('agency',self.event('Пхукет вилла жизнь уточняется'),self.decision('shortlist',market='Пхукет',property_type='вилла',purpose='жизнь',budget='уточняется'))
  self.assertEqual(plan['candidates'],[]); self.assertTrue(plan['handoff'])
 def test_gap_is_review_only(self):
  self.process('Вопрос без ответа',{'intent':'UNKNOWN','draft_reply':'UNREVIEWED DRAFT'})
  with self.s.connect() as db: gap=dict(db.execute('SELECT * FROM knowledge_gaps').fetchone())
  self.assertEqual(gap['state'],'needs_human_review'); self.assertIn('UNREVIEWED DRAFT',gap['body'])
  self.assertFalse(any(r['kind']=='reply' for r in self.s.rows('outbox')))
 def test_outbox_crm_pending_not_claimed_synced(self):
  self.process('Пхукет',self.decision('collect_brief',market='Пхукет'))
  self.assertTrue(all(r['state']=='pending' for r in self.s.rows('outbox')))
  self.assertNotIn('CRM', ''.join(json.loads(r['payload'])['text'] for r in self.s.rows('outbox') if r['kind']=='reply'))
 def test_ambiguous_market_is_not_guessed(self):
  plan=self.flow.propose('agency',self.event('Пхукет или Бали'),self.decision('collect_brief',market='Пхукет или Бали'))
  self.assertNotIn('market',plan['brief']); self.assertIn('рынке',plan['reply'])
 def test_provenance_and_original_currency_preserved(self):
  self.process('Пхукет квартира жить 200 тысяч евро',self.decision('collect_brief',market='Пхукет',property_type='квартира',purpose='жить',budget='200 тысяч евро'))
  brief=self.flow.current('agency'); self.assertEqual(brief['budget']['value'],'200 тысяч евро'); self.assertEqual(brief['budget']['source_message_id'],'1')

if __name__=='__main__': unittest.main()
