#!/usr/bin/env python3
"""Validate first-party route observations; no contacts, approvals or sends created."""
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import csv,json,re

REL=Path('project-bible/mira/sales/russia-decision-routes-2026-09-16.json')
STATES={'ready_for_owner_review','hold_decision_owner','hold_wrong_function','hold_entity_mismatch'}
KINDS={'named_direct','named_role_shared_office','general_office','restricted_purpose'}

def host(url):
    p=urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password:
        raise ValueError('HTTPS primary source required')
    return p.hostname.lower().removeprefix('www.')

def validate(payload,cohort,today=None):
    today=today or date.today()
    if payload.get('schema_version')!=1 or payload.get('outreach_authorized') is not False or payload.get('reachability_tested') is not False:
        raise ValueError('Research review cannot grant outreach authority or claim delivery testing')
    rows=payload.get('reviews')
    if not isinstance(rows,list):raise ValueError('Missing review list')
    seen=set();wave=set();contact_pairs=set()
    for row in rows:
        aid=row['agency_id']
        if aid not in cohort or aid in seen:raise ValueError('Duplicate or unknown cohort ID')
        seen.add(aid)
        if row['company']!=cohort[aid]['company'] or row['city']!=cohort[aid]['city']:raise ValueError('Identity label mismatch')
        if date.fromisoformat(row['reviewed_on'])>today:raise ValueError('Future verification')
        if row['send_status']!='not_approved' or row['greenfield_confirmed'] is not False:raise ValueError('Unsupported approval or greenfield claim')
        if row['review_state'] not in STATES or row['source_pass'] not in {'CP08','CP05_reused'}:raise ValueError('Unknown review provenance/state')
        if row['overseas_status'] not in {'unknown','existing_foreign_desk','existing_foreign_offer'}:raise ValueError('Unsupported overseas assertion')
        if not row['source_urls'] or any(host(u)!=host(cohort[aid]['website']) for u in row['source_urls']):raise ValueError('Primary source domain mismatch')
        rank=row['wave_rank']
        if rank is not None:
            if type(rank) is not int or rank not in range(1,13) or rank in wave:raise ValueError('Invalid/duplicate wave slot')
            wave.add(rank)
        direct=[]
        for r in row['routes']:
            if r['kind'] not in KINDS or r['partnership_mandate']!='not_confirmed':raise ValueError('Unsupported route/mandate')
            if r['phone'] and not re.fullmatch(r'\+\d{10,15}',r['phone']):raise ValueError('Invalid phone shape')
            if r['email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',r['email']):raise ValueError('Invalid email shape')
            if not r['phone'] and not r['email']:raise ValueError('Empty contact route')
            if r['extension'] and not re.fullmatch(r'\d{1,6}',r['extension']):raise ValueError('Invalid extension')
            if r['kind'].startswith('named_') and not r['person']:raise ValueError('Unnamed named route')
            if r['kind']=='named_direct':
                key=(aid,r['phone'],r['email'].lower(),r['extension'])
                if key in contact_pairs:raise ValueError('Repeated contact cannot inflate direct route count')
                contact_pairs.add(key);direct.append(key)
            if r['kind']=='restricted_purpose' and row['review_state']=='ready_for_owner_review':raise ValueError('Restricted route cannot count as ready')
        if row['review_state']=='ready_for_owner_review' and not any(r['kind'].startswith('named_') for r in row['routes']):raise ValueError('Ready review needs named role evidence')
        if row['review_state']=='hold_entity_mismatch' and row['routes']:raise ValueError('Never copy contacts from a different business')
    if wave!=set(range(1,13)):raise ValueError('Review must preserve all original wave12 slots')
    counts=Counter(r['review_state'] for r in rows)
    kinds=Counter(r['kind'] for row in rows for r in row['routes'])
    return {'reviewed_accounts':len(rows),'new_focused_reviews':sum(r['source_pass']=='CP08' for r in rows),'reused_cp05_reviews':sum(r['source_pass']=='CP05_reused' for r in rows),'named_direct_routes':kinds['named_direct'],'accounts_with_named_direct_route':sum(any(r['kind']=='named_direct' for r in row['routes']) for row in rows),'named_shared_office_routes':kinds['named_role_shared_office'],'ready_for_owner_review':counts['ready_for_owner_review'],'held_accounts':len(rows)-counts['ready_for_owner_review'],'entity_mismatch_holds':counts['hold_entity_mismatch'],'wave12_draft_candidates':sum(r['wave_rank'] is not None and r['review_state']=='ready_for_owner_review' for r in rows),'approved_to_send':0,'reachability':'not_tested','partnership_mandate':'not_confirmed'}

def load(root):
    path=root/REL
    if not path.exists():return None
    with (root/'project-bible/mira/sales/russia-launch-100-quality.csv').open(encoding='utf-8-sig',newline='') as f:
        cohort={r['agency_id']:r for r in csv.DictReader(f)}
    return validate(json.loads(path.read_text()),cohort)

if __name__=='__main__':
    print(json.dumps(load(Path(__file__).resolve().parents[1]),ensure_ascii=False,indent=2))

def augment(root,dashboard):
    result=load(root)
    if result is None:return dashboard
    dashboard['acquisition_review']=result
    for key in ('reviewed_accounts','new_focused_reviews','reused_cp05_reviews','named_direct_routes','accounts_with_named_direct_route','ready_for_owner_review','held_accounts','entity_mismatch_holds','wave12_draft_candidates'):
        dashboard['counts']['focused_route_'+key]=result[key]
    dashboard['scope']+=' Focused route review is separate from the inherited 50 reviews; 100 source rows are not 100 currently verified agency identities.'
    dashboard['blockers'].append('Focused route review preserves one positive domain/entity mismatch (Monolit: inherited domain identifies a woodworking business). Do not release that account without identity correction.')
    dashboard['blockers'].append('Ten named direct contacts cover seven accounts; shared offices and franchise-opening routes are not counted as direct decision routes. All draft contacts remain unapproved and untested.')
    return dashboard
