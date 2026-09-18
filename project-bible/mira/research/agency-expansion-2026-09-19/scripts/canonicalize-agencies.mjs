import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const sourceSha=JSON.parse(fs.readFileSync('repo-source-manifest.json')).source_sha;
const out='agency-expansion-2026-09-19'; fs.mkdirSync(out,{recursive:true});
const audit=JSON.parse(fs.readFileSync('agency-count-audit.json'));
const inputs=JSON.parse(fs.readFileSync('audit-input.json'));
const cities=JSON.parse(fs.readFileSync('repo-cities.json'));
const night=JSON.parse(fs.readFileSync('repo-night-sources.json'));
const now=process.env.CHECKED_AT||'2026-09-18T18:03:00Z';
function csv(s){let rows=[],r=[],v='',q=false;for(let i=0;i<s.length;i++){let c=s[i];if(c==='"'){if(q&&s[i+1]==='"'){v+='"';i++;}else q=!q;}else if(c===','&&!q){r.push(v);v='';}else if(c==='\n'&&!q){r.push(v.replace(/\r$/,''));rows.push(r);r=[];v='';}else v+=c;}if(v||r.length){r.push(v.replace(/\r$/,''));rows.push(r);}let h=rows.shift();return rows.filter(x=>x.some(Boolean)).map(x=>Object.fromEntries(h.map((k,i)=>[k,x[i]||''])));}
const hash=s=>crypto.createHash('sha256').update(s).digest('hex').slice(0,12);
const norm=s=>String(s||'').toLowerCase().replaceAll('ё','е').replace(/[^\p{L}\p{N}]/gu,'');
const country=s=>({'RU':'Russia','Россия':'Russia','BY':'Belarus','Беларусь':'Belarus'}[s]||s||'Russia');
const valid=v=>v!==null&&v!==undefined&&String(v).trim()&&!/^(unknown|not_found|not_checked|нет|не найдено|n\/a)$/i.test(String(v).trim());
const host=s=>{try{return new URL(/^https?:/.test(s)?s:'https://'+s).hostname.replace(/^www\./,'').toLowerCase();}catch{return '';}};
const registryHost=d=>/^(realting\.(uz|com)|reestr\.rgr\.ru|prrb\.by|2gis\.ru|cian\.ru)$/.test(d);
const groupKey=(c,d,n)=>{d=d?host(d):'';return c+'|'+(registryHost(d)||!d?'name:'+norm(n):(/(^|\.)etagi\.com$/.test(d)?'etagi.com':d));};
const groups=new Map(), crosswalk=[];
for(const g of audit.groups){const split=registryHost(g.domain);for(const n of split?g.names:[g.names[0]]){const key=groupKey(g.country,g.domain,n);if(!groups.has(key))groups.set(key,{key,country:g.country,domain:split?'':g.domain,names:[],cities:[],sources:[],baseline_keys:[]});const x=groups.get(key);for(const [k,vs] of Object.entries({names:split?[n]:g.names,cities:g.cities,sources:g.sources,baseline_keys:[g.key]})) x[k]=[...new Set([...x[k],...vs])];crosswalk.push({old_key:g.key,new_key:key,reason:split?'directory_domain_not_agency_identity':g.key!==key?'network_country_rollup_not_independent_branches':'preserved_domain_or_name_group'});}}
let raw=[];
for(const [p,s] of Object.entries(inputs))for(const [i,r] of csv(s).entries()){if(r.entity_type&&r.entity_type!=='agency')continue;raw.push({path:p,row:i+2,r});}
const nightRoot='project-bible/mira/research/night-2026-09-18/';
for(const [i,r] of csv(fs.readFileSync('repo-russia-a.csv','utf8')).entries())raw.push({path:nightRoot+'03-russia-a.csv',row:i+2,r});
for(const p of ['04-russia-b.json','05-belarus-agencies.json'])for(const [i,r] of night[p].records.entries())raw.push({path:nightRoot+p,row:i,r});
const quality=csv(inputs['project-bible/mira/sales/russia-launch-100-quality.csv']);
const c10=JSON.parse(fs.readFileSync('repo-c10.json')).records;
const fields=['city','brand','legal_name','parent_brand','canonical_domain','segment','company_phone','direct_business_phone','contact_first_name','contact_last_name','contact_role','general_email','direct_public_work_email','whatsapp_url','telegram_url','telegram_kind','vk_url','other_social_url','contact_page'];
const masters=[];const unmatched=[];
for(const g of groups.values()){
 const matches=raw.filter(({r})=>{let c=country(r.country),d=host(r.official_domain||r.official_site||r.website||r.official_domain||'');let n=r.brand||r.company||r.name||r.company_name||'';if(c!==g.country)return false;if(d&&!registryHost(d))return groupKey(c,d,n)===g.key;return g.names.some(x=>norm(x)===norm(n))&&(!r.city||g.cities.includes(r.city));});
 const q=g.country==='Russia'?quality.find(r=>groupKey('Russia',host(r.website),r.company)===g.key):null;
 const nid=matches.find(x=>x.r.id)?.r.id;
 const agency_id=q?.agency_id||nid||'MIRA-A-'+hash(g.key);
 const a={agency_id,country:g.country,city_id:cities.records.find(x=>g.cities.includes(x.city))?.city_id||null,city:q?.city||g.cities[0]||null,brand:q?.company||g.names[0],legal_name:null,parent_brand:null,branch_status:'not_checked',canonical_domain:g.domain||null,segment:'unknown',segment_evidence:[],overseas_status:'unknown',first_wave_fit:'not_checked',fit_reason:'Historical discovery only; independent entity and business fit not freshly established',company_phone:null,direct_business_phone:null,contact_first_name:null,contact_last_name:null,contact_role:null,general_email:null,direct_public_work_email:null,whatsapp_url:null,telegram_url:null,telegram_kind:null,vk_url:null,other_social_url:null,contact_page:null,field_evidence:[],checked_at:null,entity_status:'not_checked',completeness:{},next_action:'Verify current entity, independence, city, segment and all requested public business channels',legacy_ids:[...new Set(matches.flatMap(x=>[x.r.agency_id,x.r.id].filter(Boolean)))],legacy_names:g.names,legacy_cities:g.cities,baseline_keys:g.baseline_keys,source_records:[],inherited_classification:q||null,crm_import_status:c10.some(x=>host(x.website)===g.domain||x.id===nid)?'imported_C10_per_LOCAL_receipt':'not_confirmed',outreach_status:'not_authorized'};
 const add=(f,v,x)=>{if(!valid(v))return;const r=x.r;let url=r.source_url||r.sourceUrl||r.official_source||r.first_party_route_url||r.source||r.website||r.official_site||r.source_urls?.[0]||null;let at=r.checked_at||r.checked_date||r.source_checked_at||r.discovered_at||null;a.field_evidence.push({field:f,value:v,source_url:url,checked_at:at,status:'inherited_not_rechecked',verification_status:'inherited_not_rechecked',source_path:x.path,source_row:x.row,source_commit:sourceSha});if(!a[f])a[f]=v;};
 for(const x of matches){const r=x.r;a.source_records.push({path:x.path,row:x.row,legacy_id:r.id||r.agency_id||null,status:r.status||r.verification_status||r.source_status||null});
  add('legal_name',r.legal_name,x);add('company_phone',r.published_general_phone||r.general_phone||r.phone,x);add('general_email',r.published_general_email||r.general_email||r.email,x);add('contact_page',r.corporate_general_contact_page||r.contact_page||r.first_party_route_url,x);
  if(r.named_contact_or_role)add('legacy_named_contact_or_role',r.named_contact_or_role,x);
  if(r.telegram_social)add('legacy_social_unclassified',r.telegram_social,x);
  if(r.segment||r.business_segment||r.primary_segment)a.segment_evidence.push({value:r.segment||r.business_segment||r.primary_segment,source_path:x.path,source_row:x.row,status:'inherited_not_rechecked'});
  const overseas=r.overseas_status||r.overseas_desk_status||r.foreign_real_estate||r.foreign_property_signal;
  if(overseas&&(/confirmed_signal|existing_overseas|existing_thailand|^да$/i.test(overseas))){a.overseas_status=/thailand/.test(overseas)?'confirmed_signal_thailand_inherited':'confirmed_signal_inherited';}
 }
 const seg=q?.segment||matches.map(x=>x.r.business_segment||x.r.segment||'').find(Boolean)||'';
 if(/thailand/.test(a.overseas_status))a.segment='existing_thailand';else if(/confirmed_signal/.test(a.overseas_status)||/international|overseas/.test(seg))a.segment='existing_overseas';else if(/network|franchise/.test(seg)||/(^|\.)etagi\.com$/.test(g.domain)||['miel.ru','samoletplus.ru','vysotsky.estate'].includes(g.domain)){a.segment='network_or_franchise';a.parent_brand=a.brand;a.branch_status='network_rollup_not_independent_city_entities';}
 else if(/hold_entity/.test(seg))a.segment='hold_entity';else if(/newbuild|new_build/.test(seg))a.segment='local_newbuild';else if(/premium/.test(seg))a.segment='premium_local';else if(/regional|residential/.test(seg))a.segment='local_greenfield_candidate';
 if(!g.domain){a.entity_status='hold_directory_or_missing_official_domain';a.first_wave_fit='hold';}
 if(['existing_thailand','existing_overseas','network_or_franchise'].includes(a.segment)){a.first_wave_fit=false;a.fit_reason='Separate segment outside first priority; inherited evidence retained';}
 for(const f of fields){if(!a.field_evidence.some(e=>e.field===f))a.field_evidence.push({field:f,value:a[f]??null,source_url:null,checked_at:null,status:'not_checked',verification_status:'not_checked',reason:'Not freshly field-verified; see source lineage for inherited identity'});a.completeness[f]=a[f]?'inherited_not_rechecked':'not_checked';}
 if(!g.key.split('|')[1].startsWith('name:'))a.canonical_domain=g.key.split('|')[1];
 a.field_evidence=[...new Map(a.field_evidence.map(e=>[JSON.stringify([e.field,e.value,e.source_url,e.checked_at,e.status]),e])).values()];
 a.segment_evidence=[...new Map(a.segment_evidence.map(e=>[JSON.stringify(e),e])).values()];
 masters.push(a);
}
for(const x of raw){const r=x.r;if((r.id||r.agency_id)&&!masters.some(a=>a.legacy_ids.includes(r.id||r.agency_id)))unmatched.push(x);}
if(unmatched.length)console.log(JSON.stringify({unmatched},null,2));
assert.equal(unmatched.length,0,'Every source ID must be preserved');
assert.equal(new Set(masters.map(x=>x.agency_id)).size,masters.length);
assert.equal(new Set(crosswalk.map(x=>x.old_key)).size,audit.groups.length);
function exportCsv(rows,columns){const esc=x=>'"'+String(typeof x==='object'&&x!==null?JSON.stringify(x):x??'').replaceAll('"','""')+'"';return columns.join(',')+'\n'+rows.map(r=>columns.map(c=>esc(r[c])).join(',')).join('\n')+'\n';}
function save(n,d){fs.writeFileSync(out+'/'+n,typeof d==='string'?d:JSON.stringify(d,null,2)+'\n');}
const counts={canonical_candidate_groups:masters.length,country_counts:Object.fromEntries([...new Set(masters.map(x=>x.country))].map(c=>[c,masters.filter(x=>x.country===c).length])),fresh_verified_entities:0,fresh_first_wave_fit:0,legacy_crm_imports_confirmed:masters.filter(x=>x.crm_import_status.startsWith('imported')).length,crm_imports_this_task:0,baseline_groups:audit.groups.length,baseline_identity_keys_preserved:new Set(crosswalk.map(x=>x.old_key)).size,baseline_network_groups_collapsed:crosswalk.filter(x=>x.reason.startsWith('network')).length,directory_groups_split:crosswalk.filter(x=>x.reason.startsWith('directory')).length,legacy_rows_mapped:masters.reduce((n,a)=>n+a.source_records.length,0),fully_enriched:0};
save('master-agencies.json',{schema_version:1,task_id:'MIRA-AGENCIES-20260919-01',source_sha:sourceSha,generated_at:now,counting_unit:'Provisional canonical agency/brand candidates; not verified legal entities',records:masters});
save('master-agencies.csv',exportCsv(masters,Object.keys(masters[0]).filter(k=>!['source_records','segment_evidence','inherited_classification'].includes(k))));
save('aliases.json',{baseline_crosswalk:crosswalk,legacy_id_mappings:masters.flatMap(a=>a.legacy_ids.map(id=>({legacy_id:id,agency_id:a.agency_id,reason:'preserved_source_identity'}))),policy:'Never merge names merely because they share a directory host. Network offices do not count as independent agencies; legal franchise identity unresolved.'});
save('contacts.json',{records:masters.flatMap(a=>a.field_evidence.filter(e=>/phone|email|social|contact_or_role/.test(e.field)&&e.value).map(e=>({agency_id:a.agency_id,...e,channel_kind:'not_classified',direct_dialogue_verified:false}))),note:'Inherited contact evidence only; names and direct/channel status require field-level review.'});
save('rejected-or-held.json',{records:masters.filter(a=>a.first_wave_fit!==true).map(a=>({agency_id:a.agency_id,segment:a.segment,first_wave_fit:a.first_wave_fit,reason:a.fit_reason})),source_rows_deleted:0});
save('coverage-by-city.csv',exportCsv(cities.records.map(c=>({city_id:c.city_id,city:c.city,segment:c.segment,target_min_agencies:10,canonical_candidates:masters.filter(a=>a.country==='Russia'&&a.legacy_cities.includes(c.city)&&a.segment!=='network_or_franchise').length,verified_suitable:0,remaining_to_minimum:10,official_population_status:c.official_recheck,research_status:'queued'})),['city_id','city','segment','target_min_agencies','canonical_candidates','verified_suitable','remaining_to_minimum','official_population_status','research_status']));
save('CANONICAL-AUDIT.json',{...counts,source_sha:sourceSha,checked_at:now,tests:{legacy_ids_preserved:true,unique_canonical_ids:true,all_baseline_keys_preserved:true,no_automatic_direct_contact_promotion:true},limitations:['All identity groups remain provisional pending legal/alias checks','New record count must exclude corrected directory splits','Historical contact values are not marked freshly verified','Geographic targets pending official statistics']});
const compactMaster={schema_version:1,task_id:'MIRA-AGENCIES-20260919-01',source_sha:sourceSha,generated_at:now,counting_unit:'Provisional canonical candidates, not verified legal entities'};
save('master-agencies.json',JSON.stringify(compactMaster).slice(0,-1)+',"records":[\n'+masters.map(a=>JSON.stringify(a)).join(',\n')+'\n]}\n');
save('CANONICAL-AUDIT.json',{...counts,network_group_reduction:3,directory_group_increase:8,source_sha:sourceSha,checked_at:now,tests:{legacy_ids_preserved:true,unique_canonical_ids:true,all_baseline_keys_preserved:true,no_automatic_direct_contact_promotion:true},limitations:['All identity groups remain provisional pending legal/alias checks','Net +5 from identity corrections is NOT new discovery','Historical contact values are not freshly verified','Current official population not established']});
console.log(JSON.stringify(counts,null,2));
