"""MIRA communication runtime. Python 3.11+, no third-party dependencies.
SQLite is a private transport journal; the connected CRM owns organisations.
"""
import contextlib, hashlib, json, sqlite3, time, uuid
from profiles import profile_config, allowed_facts, model_context, model_history

CHANNELS = {'telegram', 'whatsapp', 'max', 'email', 'web'}
INTENTS = {'INTERESTED','QUESTION','REQUEST_DETAILS','REQUEST_PROJECTS','REQUEST_TERMS',
 'REQUEST_COMMISSION','REQUEST_PRESENTATION','REQUEST_CALL','OBJECTION','NOT_INTERESTED',
 'WRONG_CONTACT','UNSUBSCRIBE','HUMAN_REQUIRED','UNKNOWN'}

def packed(value): return json.dumps(value, ensure_ascii=False, separators=(',',':'))
def key(*parts): return hashlib.sha256(packed(parts).encode()).hexdigest()

class Store:
    def __init__(self, path, *, profile):
        self.profile = profile
        profile_config(profile)
        self.path = str(path)
        with self.connect() as db:
            existing=db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'").fetchone()
            meta=db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_profile'").fetchone()
            if existing and not meta: raise ValueError('unscoped legacy journal: explicit migration required')
            db.execute('CREATE TABLE IF NOT EXISTS product_profile(singleton INTEGER PRIMARY KEY CHECK(singleton=1), profile TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO product_profile VALUES(1,?)',(profile,))
            if db.execute('SELECT profile FROM product_profile WHERE singleton=1').fetchone()['profile']!=profile:
                raise ValueError('journal belongs to another product profile')
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS contacts(id TEXT PRIMARY KEY, context TEXT NOT NULL,
              paused INTEGER NOT NULL DEFAULT 0, suppressed INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS endpoints(channel TEXT, account TEXT, peer TEXT,
              contact TEXT NOT NULL REFERENCES contacts(id), evidence TEXT NOT NULL,
              PRIMARY KEY(channel,account,peer));
            CREATE TABLE IF NOT EXISTS inbox(id TEXT PRIMARY KEY, contact TEXT, payload TEXT,
              state TEXT NOT NULL DEFAULT 'pending', created REAL, error TEXT);
            CREATE TABLE IF NOT EXISTS leases(contact TEXT PRIMARY KEY, token TEXT, until REAL);
            CREATE TABLE IF NOT EXISTS timeline(id TEXT PRIMARY KEY, contact TEXT, event TEXT, created REAL);
            CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, contact TEXT, kind TEXT, payload TEXT,
              state TEXT NOT NULL DEFAULT 'pending', created REAL, provider_id TEXT, error TEXT);
            ''')
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db
    @contextlib.contextmanager
    def tx(self):
        db = self.connect()
        try:
            db.execute('BEGIN IMMEDIATE'); yield db; db.commit()
        except BaseException:
            db.rollback(); raise
        finally: db.close()
    def bind(self, contact, context, channel, account, peer, evidence):
        """Operator/private CRM call ONLY. Never trust identity from message text."""
        if context.get('profile')!=self.profile or context.get('role')!=profile_config(self.profile)['role']: raise ValueError('context profile/role mismatch')
        if channel not in CHANNELS or not all([contact,account,peer,evidence]): raise ValueError('invalid binding')
        with self.tx() as db:
            old = db.execute('SELECT contact FROM endpoints WHERE channel=? AND account=? AND peer=?',
                             (channel,account,str(peer))).fetchone()
            if old and old['contact'] != contact: raise ValueError('identity conflict: manual review required')
            db.execute('INSERT INTO contacts(id,context) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET context=excluded.context',
                       (contact,packed(context)))
            db.execute('INSERT OR IGNORE INTO endpoints VALUES(?,?,?,?,?)', (channel,account,str(peer),contact,evidence))
    def ingest(self, event):
        required = ['profile','channel','account','peer','message_id','text','occurred_at']
        if event.get('profile')!=self.profile: raise ValueError('event profile mismatch')
        if any(k not in event for k in required) or event['channel'] not in CHANNELS: raise ValueError('invalid event')
        if not isinstance(event['text'],str) or len(event['text']) > 16000: raise ValueError('invalid text')
        if not all(str(event[k]) for k in ['account','peer','message_id']): raise ValueError('empty ID')
        stamp=float(event['occurred_at'])
        if not 0 < stamp <= time.time()+300: raise ValueError('invalid timestamp')
        eid=key(self.profile,event['channel'],event['account'],str(event['peer']),str(event['message_id']))
        with self.tx() as db:
            old=db.execute('SELECT * FROM inbox WHERE id=?',(eid,)).fetchone()
            if old: return {'id':eid,'state':old['state'],'duplicate':True}
            found=db.execute('SELECT contact FROM endpoints WHERE channel=? AND account=? AND peer=?',
                             (event['channel'],event['account'],str(event['peer']))).fetchone()
            contact=found['contact'] if found else None
            state='pending' if contact else 'identity_review'
            db.execute('INSERT INTO inbox(id,contact,payload,state,created) VALUES(?,?,?,?,?)',
                       (eid,contact,packed(event),state,time.time()))
            if contact: self.log(db,eid,contact,{'direction':'in',**event})
            return {'id':eid,'state':state,'duplicate':False}
    def resolve(self, eid):
        """Release quarantined message only after an operator has bound its endpoint."""
        with self.tx() as db:
            row=db.execute("SELECT * FROM inbox WHERE id=? AND state='identity_review'",(eid,)).fetchone()
            if not row: raise ValueError('not quarantined')
            e=json.loads(row['payload'])
            target=db.execute('SELECT contact FROM endpoints WHERE channel=? AND account=? AND peer=?',
                              (e['channel'],e['account'],str(e['peer']))).fetchone()
            if not target: raise ValueError('endpoint not verified')
            db.execute("UPDATE inbox SET contact=?,state='pending' WHERE id=?",(target['contact'],eid))
            self.log(db,eid,target['contact'],{'direction':'in',**e})
    def log(self, db, eid, contact, event):
        db.execute('INSERT OR IGNORE INTO timeline VALUES(?,?,?,?)',(eid,contact,packed(event),time.time()))
    def queue(self, db, eid, contact, kind, payload):
        db.execute('INSERT OR IGNORE INTO outbox(id,contact,kind,payload,created) VALUES(?,?,?,?,?)',
                   (eid,contact,kind,packed(payload),time.time()))
    def record_outreach(self, contact, event):
        """Record an actual externally sent message with campaign/template IDs; does not send."""
        if not event.get('provider_id'): raise ValueError('actual provider_id required')
        with self.tx() as db:
            if not db.execute('SELECT 1 FROM contacts WHERE id=?',(contact,)).fetchone(): raise ValueError('unknown contact')
            self.log(db,key('outreach',contact,event['provider_id']),contact,{'direction':'out',**event})
    def resume(self, contact, operator, reason):
        if not operator or not reason: raise ValueError('operator and reason required')
        with self.tx() as db:
            # Resuming AI never clears the global opt-out flag.
            db.execute('UPDATE contacts SET paused=0 WHERE id=?',(contact,))
            self.log(db,str(uuid.uuid4()),contact,{'action':'resume','operator':operator,'reason':reason})
    def rows(self, table):
        if table not in {'contacts','endpoints','inbox','timeline','outbox'}: raise ValueError('table')
        with self.connect() as db: return [dict(r) for r in db.execute('SELECT * FROM '+table)]

class Engine:
    def __init__(self, store, intelligence, knowledge, deal_flow=None):
        self.store,self.intelligence,self.knowledge=store,intelligence,knowledge
        self.deal_flow=deal_flow
        if deal_flow and (store.profile != "mira_agency" or deal_flow.store is not store): raise ValueError("flow scope")
    def process(self, eid):
        s=self.store; token=str(uuid.uuid4()); now=time.time()
        with s.tx() as db:
            row=db.execute('SELECT * FROM inbox WHERE id=?',(eid,)).fetchone()
            if not row or row['state'] != 'pending': return 'skipped'
            cid=row['contact']; e=json.loads(row['payload'])
            lease=db.execute('SELECT * FROM leases WHERE contact=?',(cid,)).fetchone()
            if lease and lease['until']>now: return 'busy'
            # Preserve durable arrival order, including other channels.
            earlier=db.execute("SELECT id FROM inbox WHERE contact=? AND state='pending' ORDER BY created,id LIMIT 1",(cid,)).fetchone()
            if earlier['id']!=eid: return 'busy'
            db.execute('INSERT OR REPLACE INTO leases VALUES(?,?,?)',(cid,token,now+90))
            c=dict(db.execute('SELECT * FROM contacts WHERE id=?',(cid,)).fetchone())
            history=[json.loads(r['event']) for r in db.execute('SELECT event FROM timeline WHERE contact=? AND created<=? ORDER BY created DESC LIMIT 40',(cid,row['created']))][::-1]
        ctx=json.loads(c['context']); text=e['text'].lower().strip()
        # Exact stop commands take precedence over both paused AI and the model.
        stop=text in {'stop','/stop','unsubscribe','отписаться','не пишите','не пишите мне','удалите мой контакт'}
        human=any(v in text for v in ['позвоните','хочу поговорить с человеком','оператор','менеджера','call me','human please'])
        approved=allowed_facts(self.knowledge,s.profile,cid,now)
        reason=None; reply=None; intent='UNKNOWN'; selected=[]; flow_plan=None; decision={}
        try:
            if stop: intent='UNSUBSCRIBE'
            elif c['suppressed']: intent='UNSUBSCRIBE'
            elif c['paused']: intent='HUMAN_REQUIRED'
            elif human:
                intent='REQUEST_CALL'; reason='explicit_human_request'
                if self.deal_flow: flow_plan=self.deal_flow.propose(cid,e,{'action':'request_specialist'})
            else:
                decision=self.intelligence({'profile':s.profile,'context':model_context(ctx,s.profile),'history':model_history(history),'message':e,'facts':approved,'client_brief':self.deal_flow.current(cid) if self.deal_flow else {},'actions_enabled':bool(self.deal_flow)})
                intent=decision.get('intent','UNKNOWN')
                if intent not in INTENTS: intent='UNKNOWN'
                ids=decision.get('fact_ids',[])
                facts={f['id']:f for f in approved}
                if decision.get('handoff') or intent in {'HUMAN_REQUIRED','REQUEST_CALL','WRONG_CONTACT','UNKNOWN'}:
                    reason='human_or_uncertain'
                elif intent=='UNSUBSCRIBE': stop=True
                elif self.deal_flow and decision.get('action') in {'collect_brief','shortlist','request_specialist'}:
                    flow_plan=self.deal_flow.propose(cid,e,decision)
                    reply=flow_plan['reply']
                elif not isinstance(ids,list) or not ids or any(not isinstance(i,str) or i not in facts for i in ids):
                    reason='no_approved_answer'
                else:
                    selected=list(dict.fromkeys(ids))[:3]
                    # Automatic output is approved factual wording, NEVER unchecked model prose.
                    reply='\n\n'.join(facts[i]['text'] for i in selected)
                    if len(reply)>3500: reply=None; reason='answer_too_long'
        except Exception:
            reason='intelligence_error' # Never write keys, raw HTTP errors or prompts to public logs.
        with s.tx() as db:
            lease=db.execute('SELECT * FROM leases WHERE contact=?',(cid,)).fetchone()
            if not lease or lease['token']!=token or lease['until']<time.time(): return 'lease_lost'
            current=dict(db.execute('SELECT * FROM contacts WHERE id=?',(cid,)).fetchone())
            if stop: db.execute('UPDATE contacts SET suppressed=1,paused=1 WHERE id=?',(cid,))
            if self.deal_flow and reason and reason!='explicit_human_request':
                self.deal_flow.gap(db,cid,eid,e,reason,decision.get('draft_reply'))
            if flow_plan and not current['suppressed'] and not current['paused'] and not stop:
                self.deal_flow.persist(db,cid,eid,e,ctx,flow_plan)
                if flow_plan['handoff']:
                    db.execute('UPDATE contacts SET paused=1 WHERE id=?',(cid,)); reply=None
            if reason and not current['suppressed'] and not (flow_plan and flow_plan['handoff']):
                db.execute('UPDATE contacts SET paused=1 WHERE id=?',(cid,))
                s.queue(db,eid+':task',cid,'crm_task',{'context':ctx,'reason':reason,'intent':intent,
                    'summary':e['text'][:1500], 'recent_history':history[-6:], 'source_event':eid})
                reply=None # No claim that a human was notified before CRM delivery succeeds.
            if current['paused'] or current['suppressed'] or stop: reply=None
            if reply:
                s.queue(db,eid+':reply',cid,'reply',{'event':e,'text':reply,'fact_ids':selected,'valid_until':min(facts[i]['valid_until'] for i in selected) if selected else now+3600})
            s.queue(db,eid+':note',cid,'crm_note',{'context':ctx,'source_event':eid,'event':e,
                     'intent':intent,'handoff_reason':reason,'reply_planned':reply,'fact_ids':selected})
            s.log(db,eid+':decision',cid,{'direction':'decision','intent':intent,'reason':reason,'fact_ids':selected})
            db.execute("UPDATE inbox SET state='processed' WHERE id=?",(eid,))
            db.execute('DELETE FROM leases WHERE contact=? AND token=?',(cid,token))
        return 'processed'

class Dispatcher:
    def __init__(self, store, sender, enabled=False): self.store,self.sender,self.enabled=store,sender,enabled
    def dispatch(self, oid):
        if not self.enabled: return 'disabled'
        s=self.store
        with s.tx() as db:
            r=db.execute('SELECT * FROM outbox WHERE id=?',(oid,)).fetchone()
            if not r or r['state']!='pending': return 'skipped'
            p=json.loads(r['payload']); c=db.execute('SELECT * FROM contacts WHERE id=?',(r['contact'],)).fetchone()
            if r['kind']=='reply':
                if c['paused'] or c['suppressed']:
                    db.execute("UPDATE outbox SET state='cancelled' WHERE id=?",(oid,)); return 'cancelled'
                e=p['event']
                if p.get('valid_until',0)<=time.time():
                    db.execute("UPDATE outbox SET state='expired' WHERE id=?",(oid,)); return 'expired'
                # Do not retry outside the reply window or route an unsupported native email/web send.
                if (e['channel']=='whatsapp' or e.get('business_connection_id')) and time.time()-float(e['occurred_at'])>=86400:
                    db.execute("UPDATE outbox SET state='expired' WHERE id=?",(oid,)); return 'expired'
            db.execute("UPDATE outbox SET state='sending' WHERE id=?",(oid,))
        try:
            receipt=self.sender(r['kind'],p,oid)
            if not receipt: raise ValueError('missing provider receipt')
        except Exception:
            with s.tx() as db: db.execute("UPDATE outbox SET state='uncertain',error='delivery_not_confirmed' WHERE id=?",(oid,))
            return 'uncertain' # provider may have accepted: operator reconciles before retry.
        with s.tx() as db:
            db.execute("UPDATE outbox SET state='sent',provider_id=? WHERE id=?",(str(receipt),oid))
            s.log(db,oid+':sent',r['contact'],{'direction':'out','kind':r['kind'],'payload':p,'provider_id':str(receipt)})
            if r['kind']=='reply':
                context=json.loads(db.execute('SELECT context FROM contacts WHERE id=?',(r['contact'],)).fetchone()['context'])
                s.queue(db,oid+':delivery',r['contact'],'crm_note',{'context':context,'source_event':oid,
                    'delivery':'provider_accepted','provider_id':str(receipt),'event':p['event'],'reply':p['text']})
        return 'sent'
    def recover(self):
        """Run only at startup with no active dispatchers. Never resend crash-ambiguous sends."""
        with self.store.tx() as db: db.execute("UPDATE outbox SET state='uncertain',error='process_interrupted' WHERE state='sending'")
