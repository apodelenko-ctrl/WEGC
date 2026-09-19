import fs from 'node:fs';
import assert from 'node:assert/strict';

const dir='project-bible/mira/research/agency-expansion-2026-09-19/';
const read=n=>JSON.parse(fs.readFileSync(dir+n,'utf8'));
const save=(n,o)=>fs.writeFileSync(dir+n,typeof o==='string'?o:JSON.stringify(o,null,2)+'\n');
const batch=read('batch-007-barnaul-observations.json');
const master=read('master-agencies.json');
const contacts=read('contacts.json');
const before=master.records.length;
const beforeIds=new Set(master.records.map(a=>a.agency_id));
const fields=['brand','city','legal_name','parent_brand','canonical_domain','segment','company_phone','direct_business_phone','contact_first_name','contact_last_name','contact_role','general_email','direct_public_work_email','whatsapp_url','telegram_url','telegram_kind','vk_url','other_social_url','contact_page'];
contacts.records=contacts.records.filter(e=>e.batch_id!==batch.batch_id);
let added=0;

function evidence(a,field,value,source,status='verified_public_source',reason){
  const e={field,value,source_url:source,checked_at:batch.checked_at,status,verification_status:status,batch_id:batch.batch_id,...(reason?{reason}:{})};
  if(!a.field_evidence.some(x=>JSON.stringify(x)===JSON.stringify(e)))a.field_evidence.push(e);
  return e;
}

for(const row of batch.records){
  let a=master.records.find(x=>x.agency_id===row.agency_id);
  if(!a){
    if(row.domain)assert(!master.records.some(x=>x.canonical_domain===row.domain),'domain already exists: '+row.domain);
    a={agency_id:row.agency_id,country:'Russia',city_id:batch.city_id,...Object.fromEntries(fields.map(k=>[k,null])),field_evidence:[],completeness:{},segment_evidence:[],legacy_ids:[],legacy_names:[],legacy_cities:[],baseline_keys:[],source_records:[],crm_import_status:'not_confirmed',outreach_status:'not_authorized'};
    master.records.push(a);added++;
  }
  const set=(k,v,source,status='verified_public_source')=>{a[k]=v;a.completeness[k]=status;evidence(a,k,v,source,status);};
  for(const [k,v] of Object.entries(row.fields))set(k,v,row.source_url,k==='whatsapp_url'?'verified_published_link':'verified_public_source');
  if(row.person)for(const [k,v] of Object.entries(row.person))if(k!=='source_url')set(k,v,row.person.source_url,'verified_public_work_contact');
  for(const [k,v] of Object.entries(row.gaps)){a.completeness[k]=v;evidence(a,k,a[k]??null,row.source_url,v,row.reason);}
  set('segment',row.segment,row.source_url,'analyst_classification');
  a.first_wave_fit=row.fit;a.fit_reason=row.reason;a.overseas_status='unknown';a.checked_at=batch.checked_at;
  a.entity_status=row.fields.legal_name?'public_registry_legal_identity':'public_business_identity_legal_registry_pending';
  a.branch_status=row.segment==='regional_multicity_candidate'?'one_organisation_all_branches_counted_once':'local_business_candidate';
  a.next_action='Verify overseas activity and remaining public work channels before outreach';
  a.segment_evidence.push({value:row.segment,source_url:row.source_url,checked_at:batch.checked_at,status:'analyst_classification',reason:row.reason,batch_id:batch.batch_id});
  for(const e of a.field_evidence.filter(e=>e.batch_id===batch.batch_id&&e.value&&/phone|email|telegram|whatsapp|vk_url|other_social_url/.test(e.field))){
    if(['not_checked','not_found','blocked'].includes(e.verification_status))continue;
    contacts.records.push({agency_id:a.agency_id,...e,channel_kind:e.field==='whatsapp_url'?'direct_dialogue':e.field.startsWith('direct_')?'public_person_work_contact':'public_company_contact',direct_endpoint_published:e.field==='whatsapp_url',direct_dialogue_verified:false});
  }
}

const reviewed=master.records.filter(a=>a.city==='Барнаул'&&a.field_evidence.some(e=>e.batch_id===batch.batch_id));
const verified=e=>['verified_public_source','verified_public_work_contact','verified_published_link'].includes(e.verification_status);
const has=(a,f)=>a.field_evidence.some(e=>e.field===f&&e.value&&verified(e))||contacts.records.some(e=>e.agency_id===a.agency_id&&e.field===f&&e.value&&verified(e));
const count=f=>reviewed.filter(a=>has(a,f)).length;
const country=c=>master.records.filter(a=>a.country===c).length;
const suitable=reviewed.filter(a=>a.first_wave_fit===true).length;
assert.equal(reviewed.length,10);assert.equal(suitable,10);assert.equal(added,10);
assert.equal(master.records.length,before+10);assert.equal(new Set(master.records.map(a=>a.agency_id)).size,master.records.length);
assert([...beforeIds].every(id=>master.records.some(a=>a.agency_id===id)));

const counters={checked_at:batch.checked_at,scope:'Canonical provisional candidates; channel counts are companies with fresh verified fields in Barnaul B007 reviewed set',canonical_candidate_groups:master.records.length,RU:country('Russia'),BY:country('Belarus'),other:master.records.length-country('Russia')-country('Belarus'),new_candidates_this_block:added,existing_records_enriched:0,reviewed_records:reviewed.length,first_wave_suitable_candidates:suitable,separate_overseas_or_network_segment:0,named_role:reviewed.filter(a=>has(a,'contact_first_name')&&has(a,'contact_role')).length,full_named_role:reviewed.filter(a=>has(a,'contact_first_name')&&has(a,'contact_last_name')&&has(a,'contact_role')).length,phone:count('company_phone'),general_email:count('general_email'),direct_business_phone:count('direct_business_phone'),direct_public_work_email:count('direct_public_work_email'),whatsapp_published_link:count('whatsapp_url'),telegram_direct:0,telegram_channel:0,vk:0,other_social:0,fully_enriched:reviewed.filter(a=>['company_phone','general_email','direct_business_phone','direct_public_work_email','whatsapp_url','telegram_url','vk_url','contact_first_name','contact_last_name','contact_role'].every(f=>has(a,f))).length,crm_imports_this_task:0,external_sends:0,cities_target_complete:5,barnaul_remaining_to_10:0,existing_rows_deleted:0,native_crm_agency_snapshot:78,native_crm_snapshot_source:'CLOUD-INBOX/receipts/MIRA-MKT-20260918-01.json',native_crm_not_added_to_research:true};
master.generated_at=batch.checked_at;master.source_sha=batch.source_commit;
for(const a of master.records)a.segment_evidence=[...new Map(a.segment_evidence.map(e=>[JSON.stringify(e),e])).values()];
contacts.records=[...new Map(contacts.records.map(e=>[JSON.stringify(e),e])).values()];
const esc=v=>'"'+String(typeof v==='object'&&v!==null?JSON.stringify(v):v??'').replaceAll('"','""')+'"';
function csv(rows,keys){return keys.join(',')+'\n'+rows.map(r=>keys.map(k=>esc(r[k])).join(',')).join('\n')+'\n';}
save('master-agencies.json',JSON.stringify({...master,records:undefined}).replace(/}$/,'\,"records":[\n')+master.records.map(a=>JSON.stringify(a)).join(',\n')+'\n]}\n');
const columns=[...new Set(master.records.flatMap(a=>Object.keys(a)))].filter(k=>!['source_records','segment_evidence','inherited_classification'].includes(k));
save('master-agencies.csv',csv(master.records,columns));save('contacts.json',contacts);save('COUNTS.json',counters);save('batch-007-barnaul.csv',csv(reviewed,columns));
const cityRows=fs.readFileSync(dir+'coverage-by-city.csv','utf8').split('\n'),header=cityRows[0].split(',');
const coverage={city_id:'RU-CITY-005',city:'Барнаул',segment:'core_300k_to_1m',target_min_agencies:10,canonical_candidates:reviewed.length,verified_suitable:suitable,remaining_to_minimum:0,official_population_status:'blocked_official_source',research_status:'minimum_met_fields_incomplete'};
const ci=cityRows.findIndex(l=>l.includes('RU-CITY-005'));if(ci>0)cityRows[ci]=header.map(k=>esc(coverage[k])).join(',');else cityRows.splice(cityRows.length-1,0,header.map(k=>esc(coverage[k])).join(','));save('coverage-by-city.csv',cityRows.join('\n'));
const resume=read('RESUME.json');Object.assign(resume,{sourceCommitRead:batch.source_commit,canonicalCandidateGroups:master.records.length,canonicalRussiaGroups:country('Russia'),newAgenciesCollectedThisTask:(resume.newAgenciesCollectedThisTask||0)+added,freshFirstWaveSuitableCandidates:suitable,latestBatch:'batch-007-barnaul-observations.json',lastCheckpointAt:batch.checked_at,completedCityIds:[...new Set([...(resume.completedCityIds||[]),'RU-CITY-005'])],nextCityId:'RU-CITY-006',latestCheckpointEvent:'CLOUD-INBOX/events/2026-09-19/cloud-both-bases-b007.json',remaining:'Barnaul minimum met at 10/10 research-fit public business identities; nine legal identities are current RGR registry entries and one is a first-party public business identity. Overseas activity and many direct/social channels remain unknown; official city-proper population is blocked.',nextStep:'continue_city_cursor_RU-CITY-006_Izhevsk; official population still requires primary verification'});save('RESUME.json',resume);
save('POPULATION-CHECK-B007.json',{checked_at:batch.checked_at,...batch.population_check});
save('rejected-or-held.json',{records:master.records.filter(a=>a.first_wave_fit!==true).map(a=>({agency_id:a.agency_id,segment:a.segment,first_wave_fit:a.first_wave_fit,reason:a.fit_reason})),source_rows_deleted:0});
save('B007-TEST-REPORT.json',{id_preserved:true,unique_ids:true,before_at_source_commit:before,after:master.records.length,added_this_checkpoint:added,replay_actual_additions:added,existing_enriched:0,barnaul_reviewed:reviewed.length,barnaul_suitable:suitable,regional_multicity_counted_once:1,crm_imports:0,external_sends:0});
console.log(JSON.stringify(counters,null,2));
