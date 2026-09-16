#!/usr/bin/env python3
"""Canonical launch view and private, operator-owned stage journal. No network IO.

Research extraction never grants access or sends outreach. Private event imports
are operator attestations, not document-authenticity or complete-CRM assertions.
"""
from __future__ import annotations
import csv, hashlib, html, json, re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('project-bible/mira')
OPS = BASE / 'operations'
REGISTER = BASE / 'sales/phuket-developer-stage-register.csv'
MANIFEST = OPS / 'launch-build-manifest.json'
AGENCY_STAGES = ('qualified','contact_verified','owner_review_ready','owner_approved','contacted','conversation','demo','contract','onboarding','activated','client_registered','active_deal','booking','developer_commission_received','agency_settlement')
DEVELOPER_STAGES = ('identified','contact_verified','intro','terms_requested','legal_commercial_review','agreement_ready','signed','projects_loaded','inventory_verified','lead_registration_tested','first_agency_activated','first_lead_registered','first_booking')
STAGES = {'agency': AGENCY_STAGES, 'developer': DEVELOPER_STAGES}
ACTIONS = {'confirm_identity','confirm_contact','request_evidence','review_terms','prepare_demo','approve_outreach','wait_owner','onboard','activate','review_registration','review_commission','follow_up','none'}
EXTERNAL = {'contacted','intro','terms_requested','lead_registration_tested','client_registered','first_lead_registered'}
FIELDS = {'id','entity_type','entity_id','stage','occurred_at','operator_ref','evidence_ref','previous_event_id','mode','next_action','approval_ref'}
REQUIRED = FIELDS - {'approval_ref'}
PRODUCT = [
 ('public_landing','implemented_code','mira/index.html','Accepted positioning and actual demo/closed-pilot entry.'),
 ('application','implemented_code_collection_closed','cloudflare-worker/mira/worker.mjs','Protected durable intake exists; public brief remains local.'),
 ('authentication','implemented_code_not_deployed','cloudflare-worker/mira/auth.mjs','Verified Access identity and server-side membership; no guessed login.'),
 ('agency_profile','implemented_code','cloudflare-worker/mira/experience.mjs','Scoped profile and assigned markets.'),
 ('markets_catalogue','implemented_code','mira/marketplace.mjs','Demo market selection and protected assigned-market metadata.'),
 ('developer_catalogue','partial','mira/marketplace.mjs','Group filters/metadata, not a complete standalone developer cabinet.'),
 ('project_catalogue','implemented_code','mira/marketplace.mjs','Source seed demo and assigned protected project catalogue.'),
 ('filters','source_limited','mira/marketplace.mjs','Only evidenced fields; no invented budget, delivery or payment-plan filters.'),
 ('project_detail','implemented_code','cloudflare-worker/mira/experience.mjs','Current evidence checks and explicit readiness limits.'),
 ('source_metadata','implemented_code','cloudflare-worker/mira/experience.mjs','Reviewed/expiry metadata; private vault paths not disclosed to agency.'),
 ('client_registration','implemented_code_supply_gate_closed','cloudflare-worker/mira/worker.mjs','Intake, developer acknowledgement and protection are distinct.'),
 ('lead_status','implemented_code','cloudflare-worker/mira/worker.mjs','Scoped history and evidence-gated transitions.'),
 ('lead_protection','implemented_code','cloudflare-worker/mira/rules.mjs','No unconditional protection; project-specific evidence required.'),
 ('deal_status','implemented_code','cloudflare-worker/mira/worker.mjs','Audited evidence-backed stage sequence.'),
 ('commission_status','implemented_code','cloudflare-worker/mira/worker.mjs','Exact-evidence decimal records; no default rate or financial estimate.'),
 ('payment_request','implemented_code','cloudflare-worker/mira/worker.mjs','Separate package-review request, not execution or quote.'),
 ('documents_materials','partial','mira/phuket-starter-kit.html','Public starter kit exists; protected project-material delivery remains incomplete.'),
 ('onboarding','implemented_code_and_runbook','project-bible/mira/sales/AGENCY-ACTIVATION-KIT.md','Real-product demo/onboarding; contract and access are not activation.'),
 ('admin_workflow','implemented_code_partly_manual','cloudflare-worker/mira/worker.mjs','Operator application queue plus protected administration API.')
]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f); records=list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in records):
        raise ValueError('Malformed register: '+str(path))
    return records

def protect_generated_register(root: Path):
    """Refuse destructive rebuilds; never silently overwrite human stage edits."""
    target=root/REGISTER; manifest=root/MANIFEST
    if manifest.exists():
        expected=json.loads(manifest.read_text()).get('generated_register_sha256')
        if not re.fullmatch(r'[a-f0-9]{64}',str(expected)):
            raise ValueError('Invalid generated-register manifest')
        if not target.exists() or sha(target.read_bytes())!=expected:
            raise ValueError('Generated developer register edited: preserve changes in a PRIVATE operator journal before rebuilding')
    elif target.exists():
        for row in read_csv(target):
            if row.get('stage')!='identified' or row.get('operator') or row.get('outreach_status') not in ('not_sent','') or row.get('owner_approval') not in ('not_approved',''):
                raise ValueError('Unmigrated operator-owned register state; refuse overwrite')
            if any(v and k.endswith('_evidence') and k!='contact_evidence' for k,v in row.items()):
                raise ValueError('Unmigrated private evidence in generated register; refuse overwrite')

def developer_id(group: str) -> str:
    return 'PHK-D-'+sha(group.encode())[:12]

def timestamp(value: str) -> datetime:
    if not isinstance(value,str): raise ValueError('Timestamp must be a string')
    try: result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as e: raise ValueError('Invalid timestamp') from e
    if result.tzinfo is None: raise ValueError('Timestamp requires timezone')
    return result.astimezone(timezone.utc)

def opaque(value, prefix):
    if not isinstance(value,str) or not re.fullmatch(prefix+r'[A-Za-z0-9_-]{1,100}',value):
        raise ValueError('Opaque reference required: '+prefix)
    return value

def validate_journal(payload, known, now=None):
    if not isinstance(payload,dict) or set(payload)!={'schema_version','events'} or payload['schema_version']!=1 or not isinstance(payload['events'],list):
        raise ValueError('Unsupported private operator journal')
    now=now or datetime.now(timezone.utc)
    last={}; seen=set(); reached=defaultdict(set)
    for e in payload['events']:
        if not isinstance(e,dict) or set(e)-FIELDS or not REQUIRED<=set(e): raise ValueError('Unexpected/missing event fields; raw PII is not accepted')
        opaque(e['id'],'EVT-');opaque(e['operator_ref'],'OP-');opaque(e['evidence_ref'],'EVID-')
        if e['id'] in seen: raise ValueError('Duplicate event ID')
        seen.add(e['id'])
        kind=e['entity_type']; ident=e['entity_id']; stage=e['stage']
        if not all(isinstance(x,str) for x in (kind,ident,stage)) or kind not in STAGES or ident not in known[kind] or stage not in STAGES[kind]: raise ValueError('Unknown entity or stage')
        if not isinstance(e['next_action'],str) or not isinstance(e['mode'],str) or e['next_action'] not in ACTIONS or e['mode'] not in ('observation','transition','hold','resume'): raise ValueError('Unknown event action')
        if timestamp(e['occurred_at'])>now: raise ValueError('Future event cannot be observed')
        prior=last.get((kind,ident))
        if e['previous_event_id'] != (prior['id'] if prior else None): raise ValueError('Event chain mismatch')
        if prior and timestamp(e['occurred_at'])<timestamp(prior['occurred_at']): raise ValueError('Non-monotonic event time')
        if not prior:
            if e['mode']!='observation': raise ValueError('Initial historical evidence must be an explicit observation')
        else:
            old=STAGES[kind].index(prior['stage']); new=STAGES[kind].index(stage)
            if e['mode']=='transition' and (new!=old+1 or prior['mode']=='hold'): raise ValueError('Invalid stage transition')
            if e['mode']=='observation' and (new<old or prior['mode']=='hold'): raise ValueError('Invalid observation; resolve hold first')
            if e['mode']=='hold' and stage!=prior['stage']: raise ValueError('Hold cannot invent a new stage')
            if e['mode']=='resume' and (prior['mode']!='hold' or stage!=prior['stage']): raise ValueError('Invalid resume')
        if stage in EXTERNAL and e['mode'] in ('observation','transition'):
            opaque(e.get('approval_ref'),'APR-')
        elif 'approval_ref' in e: opaque(e['approval_ref'],'APR-')
        last[(kind,ident)]=e
        if e['mode'] in ('observation','transition'): reached[(kind,stage)].add(ident)
    return last,reached

def require_append_only(previous, current):
    old=previous.get('events'); new=current.get('events')
    if previous.get('schema_version')!=1 or current.get('schema_version')!=1 or not isinstance(old,list) or not isinstance(new,list) or new[:len(old)]!=old:
        raise ValueError('Private journal changed/deleted existing events; preserve audit history')

def product_rows(root):
    result=[]
    for key,state,path,note in PRODUCT:
        p=root/path
        result.append({'capability':key,'implementation':state if p.is_file() else 'source_missing','source_path':path,'source_sha256':sha(p.read_bytes()) if p.is_file() else None,'deployment':'not_verified','note':note})
    return result

def write_views(directory: Path, data):
    def esc(value): return html.escape(str(value))
    directory.mkdir(parents=True,exist_ok=True)
    text=['# MIRA — canonical launch dashboard','',f'Source commit: `{data["source_commit"]}`.','',data['scope'],'','**No launch-readiness assertion.** Implemented code, deployed behavior and commercial evidence are separate.','','## Product','','| Capability | Source implementation | Deployment |','|---|---|---|']
    text += [f'| {r["capability"]} | {r["implementation"]} | {r["deployment"]} |' for r in data['product']]
    text += ['','## Research coverage','','| Counter | Observed repository rows |','|---|---:|']+[f'| {k} | {v} |' for k,v in data['counts'].items()]
    text += ['','## Business operations','','Business KPI values remain unknown without a defined operational dataset. Stage-journal counts below count agency/developer entities with an explicit observation, NOT numbers of clients, transactions or payments. Missing stages are not backfilled. No conversion rates or financial totals are computed.','','| Entity scope / observed stage | Entities evidenced in imported journal |','|---|---:|']
    observed=data.get('operator_stage_observations',[])
    text += [f'| {x["entity_type"]} / {x["stage"]} | {x["entities_observed"]} |' for x in observed] or ['| No private journal imported | unknown |']
    text += ['','## Controls and next actions','',*['- '+x for x in data['blockers']],'','Research register is generated. Operator events remain in a separate private journal. A changed generated register blocks rebuilding instead of losing manual updates. See `OPERATOR-JOURNAL.md`.']
    md='\n'.join(text)+'\n'
    overview='<section class="overview"><article><b>'+esc(data['counts']['russia_source_backed_accounts'])+'</b><span>агентств в источниках</span><small>'+esc(data['counts']['russia_launch_cohort_live_review_matches'])+' сопоставленных прежних live-review; не действующих партнёров</small></article><article><b>'+esc(data['counts']['phuket_normalized_coverage_rows'])+'</b><span>строк проектов</span><small>Нормализация не означает текущий inventory или подтверждённого продавца</small></article><article><b>Пилот закрыт</b><span>Есть код и демо</span><small>Нужны deployment, supply gate и отдельные разрешения владельца</small></article></section>'
    body='<h1>МИРА · Launch dashboard</h1>'+overview+'<aside>Код ≠ развёрнутый сервис ≠ коммерческий допуск. Нет утверждения о готовности пилота.</aside><p>'+esc(data['scope'])+'</p><p>Source commit: <code>'+esc(data['source_commit'])+'</code></p><h2>Продукт</h2><table><thead><tr><th>Функция</th><th>Состояние кода</th><th>Deployment</th></tr></thead><tbody>'+''.join('<tr><td>'+esc(r['capability'])+'</td><td>'+esc(r['implementation'])+'<small>'+esc(r['note'])+'</small></td><td>'+esc(r['deployment'])+'</td></tr>' for r in data['product'])+'</tbody></table><details><summary>Исследовательское покрытие</summary><table>'+''.join('<tr><th>'+esc(k)+'</th><td>'+esc(v)+'</td></tr>' for k,v in data['counts'].items())+'</table></details><h2>Реальные операции</h2><p>Без журнала и определённой когорты значения неизвестны, а не нулевые. Наблюдение стадии агентства не равно количеству его клиентов или сделок.</p>'
    if observed: body+='<table><thead><tr><th>Scope</th><th>Стадия</th><th>Организаций с наблюдением</th></tr></thead><tbody>'+''.join('<tr><td>'+esc(x['entity_type'])+'</td><td>'+esc(x['stage'])+'</td><td>'+esc(x['entities_observed'])+'</td></tr>' for x in observed)+'</tbody></table>'
    body+='<h2>Открытые условия</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in data['blockers'])+'</ul>'
    page='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; form-action \'none\'"><title>МИРА · Launch dashboard</title><style>body{font:16px/1.6 system-ui;margin:30px auto;max-width:1180px;padding:20px;background:#f3f0e9;color:#172820}h1,h2{font-family:Georgia;font-weight:400}h1{font-size:42px}aside{padding:20px;background:#e8e1d3}table{border-collapse:collapse;width:100%;background:white;margin:20px 0;table-layout:fixed}td,th{padding:12px;text-align:left;border-bottom:1px solid #ccd2c9;overflow-wrap:anywhere}small{display:block;color:#56635b}code{overflow-wrap:anywhere}details{margin:24px 0}summary{cursor:pointer;font-weight:650}.overview{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.overview article{background:white;padding:20px}.overview b,.overview span{display:block}.overview b{font:32px Georgia}.overview small{margin-top:8px}@media(max-width:620px){body{padding:12px;font-size:14px}td,th{padding:7px}h1{font-size:32px}.overview{grid-template-columns:1fr}}</style></head><body>'+body+'</body></html>'
    for name,content in [('launch-dashboard.json',json.dumps(data,ensure_ascii=False,indent=2)+'\n'),('LAUNCH-DASHBOARD.md',md),('launch-dashboard.html',page)]:
        p=directory/name
        if p.is_symlink(): raise ValueError('Refuse symlink output')
        p.write_text(content,encoding='utf-8')

def augment_public(root, dashboard):
    dashboard=dict(dashboard,schema_version=2,product=product_rows(root),operator_stage_observations=[],operator_state='not_imported')
    dashboard['build_command']='python scripts/mira-launch-build.py'
    dashboard['readiness']['mvp0']='demo_source_available_static_deployment_separate'
    dashboard['blockers']=[x for x in dashboard['blockers'] if 'No project-specific' not in x]
    dashboard['blockers'] += ['Primary private supply documents have been reviewed separately; a complete current seller/inventory/registration gate is not imported or enabled.','Protected project-material delivery is still partial.','Owner-held operator events must remain outside this public repository.']
    write_views(root/OPS,dashboard)
    (root/MANIFEST).write_text(json.dumps({'schema_version':1,'source_commit':dashboard['source_commit'],'generated_register_sha256':sha((root/REGISTER).read_bytes()),'operator_records_included':False},indent=2)+'\n')
    return dashboard

def private_overlay(root, state_path, output_dir, now=None):
    root=root.resolve(); state_path=state_path.resolve(); output_dir=output_dir.resolve()
    if state_path.is_relative_to(root) or output_dir.is_relative_to(root) or state_path.is_relative_to(output_dir):
        raise ValueError('Private operator input/output must be outside repository and source must not be an output file')
    if state_path.stat().st_size>5_000_000: raise ValueError('Oversized private journal')
    payload=json.loads(state_path.read_text())
    agencies=read_csv(root/BASE/'sales/russia-launch-100-quality.csv')
    developers=read_csv(root/REGISTER)
    known={'agency':{a['agency_id'] for a in agencies},'developer':{developer_id(d['developer_group']) for d in developers}}
    last,reached=validate_journal(payload,known,now)
    archive=output_dir/'operator-journal.snapshot.json'
    if archive.exists(): require_append_only(json.loads(archive.read_text()),payload)
    data=json.loads((root/OPS/'launch-dashboard.json').read_text())
    data.update(schema_version=2,product=product_rows(root))
    data['scope']='PRIVATE owner view: repository research plus operator-attested event observations. Not a complete CRM and not deployment authorization.'
    data['operator_state']='private_journal_imported'
    data['operator_journal_sha256']=sha(state_path.read_bytes())
    data['operator_stage_observations']=[{'entity_type':kind,'stage':stage,'entities_observed':len(ids)} for (kind,stage),ids in sorted(reached.items())]
    for d in developers:
        ident=developer_id(d['developer_group']); e=last.get(('developer',ident)); d['developer_id']=ident
        if e:
            d['seed_owner_approval']=d.pop('owner_approval')
            d['seed_outreach_status']=d.pop('outreach_status')
            d.update(stage=e['stage'],operator=e['operator_ref'],last_event_id=e['id'],observed_at=e['occurred_at'],evidence_ref=e['evidence_ref'],next_action=e['next_action'],operational_hold=str(e['mode']=='hold').lower(),authorization_granted='false')
    output_dir.mkdir(mode=0o700,parents=True,exist_ok=True)
    outputs=['operator-journal.snapshot.json','phuket-developer-stage-register.csv','agency-stage-register.json','launch-dashboard.json','launch-dashboard.html','LAUNCH-DASHBOARD.md']
    if not archive.exists() and any((output_dir/name).exists() for name in outputs):
        raise ValueError('Unrecognised private output files; use a new output directory')
    for name in outputs:
        if (output_dir/name).is_symlink(): raise ValueError('Refuse symlink private output')
    write_views(output_dir,data)
    fields=list(dict.fromkeys(k for d in developers for k in d))
    with (output_dir/'phuket-developer-stage-register.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(developers)
    (output_dir/'agency-stage-register.json').write_text(json.dumps([e for (kind,_),e in last.items() if kind=='agency'],indent=2)+'\n')
    archive.write_text(json.dumps(payload,indent=2)+'\n')
    for name in outputs: (output_dir/name).chmod(0o600)
    return data
