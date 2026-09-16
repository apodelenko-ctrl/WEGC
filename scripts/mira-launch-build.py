#!/usr/bin/env python3
"""Build source-backed launch registers. Offline only; never sends outreach.
Coverage != verification. Source catalogue association is NOT a legal seller.
Original seed, live reviews and owner approval queue are never overwritten.
"""
from __future__ import annotations
import argparse, csv, hashlib, html, json, os, re, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('project-bible/mira')
UNKNOWN={'','unknown','по запросу','не найдено','not_verified','not_public'}
def norm(value):
    return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',value).casefold())
def rows(root,path):
    with (root/path).open(encoding='utf-8-sig',newline='') as fh:return list(csv.DictReader(fh))
def write_csv(root,path,data,fields=None):
    target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
    if not fields and not data:raise ValueError(f'Cannot infer headers for {path}')
    with target.open('w',encoding='utf-8',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=fields or list(data[0]));writer.writeheader();writer.writerows(data)
def read_catalog(raw):
    match=re.search(r'window\.WEGC_CATALOG\s*=\s*\[\s*\n(.*?)\n\s*\];',raw,re.S)
    if not match:raise ValueError('WEGC_CATALOG assignment not found; refuse empty replacement')
    result=[]
    for line in match.group(1).splitlines():
        line=line.strip().rstrip(',')
        if line:
            item=json.loads(line)
            if not isinstance(item,dict) or not item.get('name') or not item.get('slug'):raise ValueError('Missing name/slug')
            result.append(item)
    if not result or len({p['slug'] for p in result})!=len(result):raise ValueError('Empty catalog or duplicate source slugs')
    return result
def normalize_phuket(catalog,seeds,aliases,developers):
    seed_map={}
    for row in seeds:
        k=norm(row['project_name'])
        if k in seed_map:raise ValueError('Duplicate normalized seed project name')
        seed_map[k]=row
    alias_map={}
    for row in aliases:
        k=norm(row['alias'])
        if k in alias_map and alias_map[k]['canonical_group']!=row['canonical_group']:raise ValueError(f'Conflicting alias: {row["alias"]}')
        alias_map[k]=row
    dev_sources=defaultdict(set)
    for d in developers:
        for key in [d['developer_group'],d.get('legal_name','')]:
            canonical=alias_map.get(norm(key),{}).get('canonical_group',key)
            if d.get('official_website'):dev_sources[norm(canonical)].add(d['official_website'])
    output,matched=[],set()
    for index,raw in enumerate(catalog,1):
        seed=seed_map.get(norm(raw['name']));raw_dev=raw.get('developer','');alias=alias_map.get(norm(raw_dev))
        group,operator,basis,confidence='','','unresolved','unknown'
        if seed:
            group,basis=seed['developer_family'],'existing_seed_mapping';confidence=seed['developer_mapping_confidence'];matched.add(norm(seed['project_name']))
        elif alias:
            if alias.get('legal_entity_status')=='operator_or_brand_only':operator=alias['canonical_group'];basis,confidence='operator_brand_signal_only','low'
            else:group=alias['canonical_group'];basis,confidence='generator_alias_candidate','low'
        elif raw_dev.casefold().strip() not in UNKNOWN:basis='unmapped_raw_developer_candidate'
        official=sorted(dev_sources.get(norm(group),[])) if group else []
        output.append({'project_id':'PHK-P-'+hashlib.sha256(raw['slug'].encode()).hexdigest()[:12],
            'source_row':index,'source_slug':raw['slug'],'project_name':raw['name'],'raw_developer':raw_dev,
            'developer_family':group or 'unknown','mapping_basis':basis,'mapping_confidence':confidence,
            'legal_contracting_seller':'unknown','legal_seller_status':'not_verified','operator_or_brand_signal':operator or 'unknown',
            'district_raw':raw.get('district',''),'property_type_raw':raw.get('kind',''),
            'location_type_evidence':'existing_seed' if seed else 'catalog_generator_candidate',
            'official_group_source':'; '.join(official),'official_project_source':'',
            'source_path':'ru/wegc-catalog-data.js','source_layer':raw.get('source','unknown'),'source_project_path':raw.get('url',''),
            'source_verified_at':'','inventory_status':'not_verified','registration_enabled':'false','commercial_status':'not_verified',
            'next_action':'verify_project_seller_terms_inventory_and_lead_rules' if seed else 'resolve_project_and_family_before_commercial_verification',
            'notes':seed.get('notes','') if seed else 'Preserved source index; generator may infer group/district/type from project wording. Not current inventory.'})
    missing=sorted(set(seed_map)-matched)
    if missing:raise ValueError(f'Seed rows missing in generated backbone: {missing}. Reconcile, do not drop.')
    return output
def resolve_review(company,city,index,by_name):
    exact=index.get((norm(company),norm(city)))
    if exact:return exact,'company_city'
    candidates=by_name.get(norm(company),[])
    if len(candidates)==1 and norm(city)==norm(candidates[0].get('city','')):return candidates[0],'unique_name_same_city'
    return None,'unmatched'
def segment_agencies(cohort,reviews,owner_wave):
    index,by_name={},defaultdict(list)
    for row in reviews:
        key=(norm(row['company']),norm(row['city']))
        if key in index:raise ValueError(f'Duplicate live review key: {key}')
        index[key]=row;by_name[key[0]].append(row)
    wave={(norm(x['company']),norm(x['city'])):x for x in owner_wave}
    seen,output,matched=set(),[],set()
    for row in cohort:
        key=(norm(row['company']),norm(row['city']))
        if key in seen:raise ValueError(f'Duplicate launch agency: {row["company"]}')
        seen.add(key);review,join=resolve_review(row['company'],row['city'],index,by_name);w=wave.get(key,{})
        inherited=review['primary_segment'] if review else '';evidence=row.get('why_relevant','').lower()
        basis='inherited_live_review' if review else 'source_cohort_signal_only'
        segment,overseas,pitch='hold_first_party_review','unknown','qualification_first'
        if inherited:
            matched.add(key)
            if inherited.startswith('hold_'):segment=inherited
            elif inherited=='existing_phuket_direction':segment,overseas,pitch=inherited,'thailand_signal_evidenced','complement_existing_phuket_desk'
            elif inherited=='existing_foreign_property_desk':segment,overseas,pitch=inherited,'foreign_desk_signal_evidenced','extend_existing_foreign_desk'
            elif inherited=='network_platform':segment,pitch='network_franchise_platform','hq_network_pilot'
            elif 'premium' in inherited:segment,pitch='premium_investment','premium_phuket_fit'
            elif 'newbuild' in inherited:segment,pitch=('regional_new_build' if 'large' not in inherited else 'large_new_build'),'new_build_extension_fit'
            elif 'resort' in inherited:segment,pitch='resort_agency','resort_comparison_fit'
            else:segment='hold_segment_fit'
        elif any(x in evidence for x in ['network','franchise','франшиз','сеть']):segment,pitch='network_franchise_platform_candidate','hq_qualification'
        elif any(x in evidence for x in ['premium','investment','преми','инвест']):segment,pitch='premium_investment_candidate','investment_fit_qualification'
        elif any(x in evidence for x in ['new-build','newbuild','новостро']):segment,pitch='regional_new_build_candidate','new_build_fit_qualification'
        elif any(x in evidence for x in ['resort','курорт']):segment,pitch='resort_agency_candidate','resort_fit_qualification'
        readiness=review.get('readiness','not_live_reviewed') if review else 'not_live_reviewed'
        output.append({'agency_id':'RU-A-'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:12],
            'rank':row['rank'],'company':row['company'],'city':row['city'],'website':row['website'],
            'segment':segment,'segmentation_basis':basis,'inherited_segment':inherited,'overseas_status':overseas,'greenfield_confirmed':'false',
            'pitch_mode':pitch,'live_reviewed':str(bool(review)).lower(),'review_join':join,
            'decision_route_signal':review.get('secondary_signal','') if review else '',
            'readiness':readiness,'owner_review_wave':str(bool(w)).lower(),'send_status':w.get('send_status','not_approved'),
            'source_url':row.get('source_url',''),'source_checked_at':row.get('checked_at',''),
            'review_source_path':'sales/russia-live-50-segmentation.csv' if review else '',
            'evidence_note':review.get('evidence_note','') if review else row.get('why_relevant',''),
            'next_action':w.get('next_action') or row.get('next_action') or 'qualify_decision_route_and_foreign_desk'})
    return output,[r for k,r in index.items() if k not in matched]
def replace_generated_section(path,body):
    start,end='<!-- MIRA-LAUNCH-AUTO:START -->','<!-- MIRA-LAUNCH-AUTO:END -->';existing=path.read_text(encoding='utf-8');block=f'{start}\n{body}\n{end}'
    if start in existing and end in existing:existing=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,existing,flags=re.S)
    else:existing+='\n\n'+block+'\n'
    path.write_text(existing,encoding='utf-8')
def build(root,source_commit):
    paths=['ru/wegc-catalog-data.js',*(str(BASE/p) for p in ['data/phuket-project-master-seed-45.csv','data/phuket-developer-alias-map-v1.csv','data/phuket-developer-master.csv','sales/russia-launch-50-seed.csv','sales/russia-launch-50-batch-02.csv','sales/russia-live-50-segmentation.csv','sales/russia-wave-01-owner-review.csv','sales/phuket-p0-commercial-verification.csv'])]
    provenance={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
    catalog=read_catalog((root/paths[0]).read_text(encoding='utf-8'));seed,aliases,developers=[rows(root,p) for p in paths[1:4]]
    project_master=normalize_phuket(catalog,seed,aliases,developers);cohort=rows(root,paths[4])+rows(root,paths[5]);live,wave,p0=[rows(root,p) for p in paths[6:9]]
    agencies,unmatched=segment_agencies(cohort,live,wave)
    write_csv(root,BASE/'data/phuket-project-master.csv',project_master)
    write_csv(root,BASE/'sales/russia-launch-100-quality.csv',agencies)
    write_csv(root,BASE/'sales/russia-review-join-exceptions.csv',unmatched,list(live[0]))
    register=[]
    for r in p0:
        register.append(dict(developer_group=r['developer_group'],stage='identified',public_route=r['partner_route'],contact_evidence=r['contact'],route_status=r['agent_program'],channel_owner='unknown',contracting_entity='unknown',agreement_evidence='',eligible_projects_evidence='',inventory_evidence='',commission_schedule_evidence='',commission_trigger_evidence='',payout_timing_evidence='',registration_rules_evidence='',protection_rules_evidence='',duplicate_dispute_evidence='',materials_permissions_evidence='',first_agency_enabled_evidence='',first_lead_evidence='',first_booking_evidence='',source_url=r['source_url'],source_checked_at=r['checked_at'],owner_approval='not_approved',outreach_status='not_sent',operator='',next_action=r['next_action'],gate_note='Public route exists; no agreement, active inventory or buyer registration is inferred from it.'))
    write_csv(root,BASE/'sales/phuket-developer-stage-register.csv',register)
    counts={'phuket_source_rows':len(catalog),'phuket_normalized_coverage_rows':len(project_master),
        'phuket_seed_mappings_preserved':sum(p['mapping_basis']=='existing_seed_mapping' for p in project_master),
        'phuket_generator_family_candidates':sum(p['mapping_basis']=='generator_alias_candidate' for p in project_master),
        'phuket_operator_only_rows':sum(p['mapping_basis']=='operator_brand_signal_only' for p in project_master),
        'phuket_family_unresolved_rows':sum(p['developer_family']=='unknown' for p in project_master),
        'phuket_project_legal_sellers_verified':0,'phuket_projects_enabled_for_registration':0,
        'phuket_group_master_rows':len(developers),'phuket_p0_public_evidence_groups':len(p0),
        'russia_source_backed_accounts':len(agencies),'russia_live_review_rows_inherited':len(live),
        'russia_launch_cohort_live_review_matches':sum(a['live_reviewed']=='true' for a in agencies),
        'russia_live_review_join_exceptions':len(unmatched),
        'russia_named_route_signals_in_cohort':sum(a['decision_route_signal'].startswith('named_') for a in agencies),
        'russia_inherited_owner_review_ready':sum(a['readiness']=='ready_for_owner_review' for a in agencies),
        'russia_owner_review_wave_accounts':len(wave),'russia_send_approved_in_source_wave':sum(w['send_status']=='approved' for w in wave),
        'russia_classification_coverage':len(agencies),'russia_needing_live_review':sum(a['live_reviewed']!='true' for a in agencies),
        'russia_segment_holds':sum(a['segment'].startswith('hold_') for a in agencies)}
    observation={k:{'value':None,'status':'no_operational_evidence_imported'} for k in ['agencies_contacted','conversations','demos','agreements_signed','onboarded','activated','clients_registered','active_deals','bookings','developer_commission_received','agency_settlements']}
    dashboard={'schema_version':1,'source_commit':source_commit,'source_sha256':provenance,
        'scope':'Repository evidence only; not a live CRM and not a claim that unobserved activity is zero.',
        'readiness':{'mvp0':'demo_code_available_deployment_qa_separate','marketing_pilot':False,'marketplace_pilot':False,'commercially_repeatable':False},
        'counts':counts,'operations':observation,'segments':dict(sorted(Counter(a['segment'] for a in agencies).items())),
        'mapping_statuses':dict(sorted(Counter(p['mapping_basis'] for p in project_master).items())),
        'blockers':['Owner approval required before any external outreach or forms.','Secure backend deployment and live receipt/access QA remain unverified.','No project-specific complete current legal/lead/inventory gate is imported.','Real operating events have not been imported; conversion rates cannot be calculated.'],
        'controls':{'outreach_automated':False,'financial_defaults':False,'real_client_data_in_repository':False}}
    dest=root/BASE/'operations/launch-dashboard.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(dashboard,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# MIRA — canonical launch dashboard','',f'Source commit: `{source_commit}`. Rebuild with `python scripts/mira-launch-build.py`.','','**Not pilot-ready.** Coverage, commercial verification and real activation are separate gates.','','## Source-backed counters','','| Counter | Repository evidence |','|---|---:|']
    lines += [f'| `{k}` | {v} |' for k,v in counts.items()]
    lines += ['','## Live operations','','No operational evidence imported. Contacted, signed, activated, registered clients, bookings, receipts and settlements are **unknown**, not inferred zeros. No conversion percentages are calculated.','','## Product','','Public demo: existing-project catalog, filters, detail, local pseudonymous drafts, status path, payment draft, qualification brief and starter kit. No live application receipt, authentication or commercial registration is inferred from the demo.','','## Next independent work','','Resolve join exceptions; verify unreviewed agencies and decision owners; resolve non-seed project/family candidates; obtain current seller/terms/inventory/lead-rule evidence; deploy and test protected pilot endpoints. External messages require separate owner approval.','','## Provenance','','SHA-256 hashes for each source file are in `launch-dashboard.json`. Source observation dates remain inherited and are never overwritten by extraction time.']
    (root/BASE/'operations/LAUNCH-DASHBOARD.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    private_html='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>MIRA · Launch dashboard</title><style>body{font:16px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f4f1eb;color:#172820}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;border-bottom:1px solid #d6d9d0;text-align:left}code{overflow-wrap:anywhere}h1{font:44px Georgia}aside{padding:20px;background:#eee7d7}</style><h1>МИРА · Launch dashboard</h1><aside>Не готово к реальному пилоту. Это данные репозитория, не live CRM. Неизвестное не заменено нулём.</aside><p>Source commit: <code>'+html.escape(source_commit)+'</code></p><table><thead><tr><th>Показатель</th><th>Подтверждено в реестрах</th></tr></thead><tbody>'+''.join('<tr><td>'+html.escape(k)+'</td><td>'+str(v)+'</td></tr>' for k,v in counts.items())+'</tbody></table><h2>Реальные операции</h2><p>Звонки, встречи, договоры, активации, клиенты, сделки и выплаты: нет импортированного журнала подтверждений. Значение неизвестно.</p><h2>Блокеры</h2><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in dashboard['blockers'])+'</ul><p>Внутренний документ. Не включать в Pages output; не хранить здесь клиентские данные.</p></html>'
    (root/BASE/'operations/launch-dashboard.html').write_text(private_html,encoding='utf-8')
    summary=(f'## Generated source checkpoint\n\nSource commit: `{source_commit}`.\n\n'
        f'Phuket: **{len(project_master)} / {len(catalog)}** source rows covered; **{counts["phuket_seed_mappings_preserved"]}** seed mappings preserved; **{counts["phuket_generator_family_candidates"]}** generator family candidates; **{counts["phuket_family_unresolved_rows"]}** family-unresolved rows. **0 project legal sellers verified / 0 registration-enabled projects in this generated layer.**\n\n'
        f'Russia: **{len(agencies)}** quality-layer rows; **{counts["russia_launch_cohort_live_review_matches"]}** matched to inherited live reviews; **{len(unmatched)}** review join exceptions. **{counts["russia_inherited_owner_review_ready"]}** inherited ready-for-owner-review; wave approval remains as in source. No new live verification or sending performed.\n\n'
        'Canonical dashboard: `operations/LAUNCH-DASHBOARD.md` and JSON/HTML beside it. Full project register: `data/phuket-project-master.csv`. Agency quality layer: `sales/russia-launch-100-quality.csv`. Developer stage register: `sales/phuket-developer-stage-register.csv`.\n\n'
        'Continue: resolve evidence gaps, complete acquisition assets, implement/deploy protected pilot. Generated coverage is not business launch readiness.')
    for name in ['WORK-STATUS.md','RESUME-STATE.md']:replace_generated_section(root/BASE/name,summary)
    print(json.dumps(counts,ensure_ascii=False,indent=2));return dashboard
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--source-commit',default=os.environ.get('GITHUB_SHA','local-uncommitted'));args=parser.parse_args();build(args.root,args.source_commit)
