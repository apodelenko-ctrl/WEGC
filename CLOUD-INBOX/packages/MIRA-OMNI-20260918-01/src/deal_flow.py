"""Agency client brief and source-backed research shortlist, not live inventory advice."""
import json, time, re
from urllib.parse import urlparse

FIELDS={'market','property_type','purpose','budget','district','timing'}
QUESTIONS={
 'market':'В какой стране или на каком рынке клиент рассматривает недвижимость?',
 'property_type':'Какой тип недвижимости нужен клиенту: квартира, вилла или другой?',
 'purpose':'Для какой цели клиент подбирает недвижимость?',
 'budget':'Какой бюджет указал клиент и в какой валюте?',
 'district':'Есть ли предпочтительный район?',
 'timing':'Какие сроки покупки или готовности объекта важны клиенту?'}
ALIASES={
 'market':{'phuket':['пхукет','phuket'],'bali':['бали','bali'],'dubai':['дубай','дубае','dubai'],
           'vietnam':['вьетнам','vietnam'],'montenegro':['черногор','montenegro']},
 'property_type':{'condo':['квартир','апартамент','кондо','condo','apartment'],
                  'villa':['вилл','villa'],'townhouse':['таунхаус','townhouse']}}

def canonical(field, quote):
    if field not in ALIASES: return quote
    q=quote.casefold()
    matches=[k for k,values in ALIASES[field].items() if any(v in q for v in values)]
    return matches[0] if len(matches)==1 else None

def normalize_catalog(document, *, market, source):
    """Explicit source path + known feed market; no provider/price/status upgrades."""
    out=[]
    for p in document.get('projects',[]):
        if not p.get('id') or not p.get('name'): continue
        if not re.fullmatch(r'[a-z0-9_-]+',p['id']): continue
        out.append({'id':p['id'],'name':p['name'],'market':p.get('market') or market,
          'kind':p.get('kind'),'propertyTypes':p.get('propertyTypes',[]),'district':p.get('district'),
          'source':source,'source_url':p.get('sourceURL'),
          'url':'https://wegc.fund/mira/catalog/projects/'+p['id']+'/',
          'metadata_status':p.get('metadataStatus','unknown'),
          'status':'research_only','availability':'not_confirmed','price':None})
    return out

def shortlist(catalog, brief, limit=3):
    found=[]
    for p in catalog:
        if p.get('market')!=brief['market']['normalized']: continue
        kind=brief['property_type']['normalized']
        types=p.get('propertyTypes',[])
        accepted={'condo':{'apartment','studio','condo'},'villa':{'villa'},'townhouse':{'townhouse'}}.get(kind,{kind})
        if types:
            if not accepted.intersection(types): continue
        elif p.get('kind')!=kind: continue
        district=brief.get('district',{}).get('value','')
        if district and district.casefold() not in str(p.get('district','')).casefold(): continue
        if not p.get('source') or urlparse(p.get('url','')).scheme!='https': continue
        found.append({**p,'match_basis':['market','property_type']+(['district'] if district else []),
                      'not_checked':['budget','purpose_suitability','timing','availability','price','commission']})
    # Stable selection, no invented suitability score or predictive ranking.
    return sorted(found,key=lambda p:p['id'])[:limit]

class DealFlow:
    def __init__(self, store, catalog):
        if store.profile!='mira_agency': raise ValueError('deal flow is agency-only')
        self.store,self.catalog=store,catalog
        with store.tx() as db:
            db.execute('CREATE TABLE IF NOT EXISTS client_briefs(contact TEXT PRIMARY KEY, body TEXT NOT NULL, updated REAL)')
            db.execute('CREATE TABLE IF NOT EXISTS saved_shortlists(contact TEXT PRIMARY KEY, body TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS knowledge_gaps(id TEXT PRIMARY KEY, contact TEXT, body TEXT NOT NULL, state TEXT NOT NULL)')
    def current(self, cid):
        with self.store.connect() as db:
            row=db.execute('SELECT body FROM client_briefs WHERE contact=?',(cid,)).fetchone()
        return json.loads(row['body']) if row else {}
    def propose(self,cid,event,decision):
        action=decision.get('action')
        if action not in {'collect_brief','shortlist','request_specialist'}: return None
        brief=self.current(cid); changes=decision.get('criteria_updates',{})
        if not isinstance(changes,dict): raise ValueError('criteria schema')
        for field,update in changes.items():
            if field not in FIELDS or not isinstance(update,dict): raise ValueError('criterion')
            quote=update.get('quote')
            if not isinstance(quote,str) or not quote.strip() or len(quote)>200 or quote not in event['text']:
                raise ValueError('criterion must quote current message verbatim')
            value=canonical(field,quote)
            if value is None: continue # ambiguous market/type remains unanswered
            brief[field]={'value':quote,'normalized':value,'source_message_id':event['message_id']}
        missing=[f for f in ['market','property_type','purpose','budget'] if f not in brief]
        result={'brief':brief,'action':action,'missing':missing,'candidates':[],
                'handoff':action=='request_specialist','reply':None}
        if result['handoff']:
            with self.store.connect() as db:
                saved=db.execute('SELECT body FROM saved_shortlists WHERE contact=?',(cid,)).fetchone()
            prior=json.loads(saved['body']) if saved else {}
            if prior.get('brief')==brief: result['candidates']=prior.get('candidates',[])
            return result
        if missing:
            result['reply']=' '.join(QUESTIONS[f] for f in missing[:2]); return result
        if action=='shortlist':
            result['candidates']=shortlist(self.catalog,brief)
            if not result['candidates']:
                result['handoff']=True; result['reason']='no_catalog_match'; return result
            text=['Проекты для предварительного изучения по рынку и типу недвижимости:']
            for p in result['candidates']:
                reason='рынок '+p['market']+', тип '+brief['property_type']['normalized']
                if 'district' in p['match_basis']: reason+=', район '+p['district']
                text.append(p['name']+' — совпадение по данным каталога: '+reason+'.\n'+p['url'])
            text.append('Бюджет, пригодность для цели клиента, сроки, актуальные цены и наличие ещё не подтверждены. Это исследовательские проекты, не предложение свободных лотов. Передать эти варианты специалисту для проверки условий?')
            result['reply']='\n\n'.join(text)
        else:
            result['reply']='Основные критерии запроса сохранены. Подготовить предварительную подборку по каталогу?'
        return result
    def persist(self,db,cid,eid,event,ctx,plan):
        s=self.store
        db.execute('INSERT INTO client_briefs VALUES(?,?,?) ON CONFLICT(contact) DO UPDATE SET body=excluded.body,updated=excluded.updated',
                   (cid,json.dumps(plan['brief'],ensure_ascii=False),time.time()))
        if plan['candidates'] and plan['action']=='shortlist':
            db.execute('INSERT INTO saved_shortlists VALUES(?,?) ON CONFLICT(contact) DO UPDATE SET body=excluded.body',
                       (cid,json.dumps({'brief':plan['brief'],'candidates':plan['candidates']},ensure_ascii=False)))
        s.queue(db,eid+':brief',cid,'crm_note',{'context':ctx,'source_event':eid,'client_brief':plan['brief'],
          'research_shortlist':plan['candidates'],'next_action':'specialist_review' if plan['handoff'] else 'continue_dialogue'})
        if plan['handoff']:
            s.queue(db,eid+':specialist',cid,'crm_task',{'context':ctx,'intent':'REQUEST_PROJECTS',
              'reason':plan.get('reason','requested_project_review'),
              'summary':'Проверить клиентский запрос и актуальные условия проектов.',
              'client_brief':plan['brief'],'research_shortlist':plan['candidates'],'source_event':eid})
        s.log(db,eid+':brief_saved',cid,{'direction':'action','action':'client_brief_saved','source_event':eid})
    def gap(self,db,cid,eid,event,reason,draft=None):
        # Private improvement backlog, never an automatic knowledge-base write.
        body={'question':event['text'],'reason':reason,'source_event':eid,'draft_for_review':draft}
        db.execute('INSERT OR IGNORE INTO knowledge_gaps VALUES(?,?,?,?)',
                   (eid,cid,json.dumps(body,ensure_ascii=False),'needs_human_review'))
