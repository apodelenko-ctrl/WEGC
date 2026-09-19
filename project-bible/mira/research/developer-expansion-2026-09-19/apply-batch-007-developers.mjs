import fs from 'node:fs';
import assert from 'node:assert/strict';

const dir='project-bible/mira/research/developer-expansion-2026-09-19/';
const read=n=>JSON.parse(fs.readFileSync(dir+n,'utf8'));
const save=(n,o)=>fs.writeFileSync(dir+n,JSON.stringify(o,null,2)+'\n');
const checkedAt='2026-09-19T00:09:13Z';
const sourceCommit='921dbb633db4402c05b2fe84c31a0f40929873fb';
const links=read('project-links.json');
const queue=read('enrichment-queue.json');
const observations=read('public-contact-observations.json');
const developers=read('developers.json');
const metrics=read('metrics.json');
const beforeIds=links.map(x=>x.project_id);

function project(id){const row=links.find(x=>x.project_id===id);assert(row,`missing ${id}`);return row;}
function task(id){const row=queue.find(x=>x.project_id===id);assert(row,`missing task ${id}`);return row;}

Object.assign(project('zero-bangtao'),{
  catalog_alias_of:'the-zero-bang-tao',
  alias_resolution_status:'confirmed_catalog_alias_preserve_id',
  alias_evidence:{source_url:'https://thezerophuket.com/bang-tao/',checked_at:checkedAt,verification_status:'verified_primary_source_plus_catalog_provenance',basis:'The preserved Russian generator row has the same group, district and official source as the exact English master row. ID is retained and routed to the canonical project; no inventory, seller or agreement is inferred.'}
});
Object.assign(project('zero-naiyang'),{
  catalog_alias_of:'the-zero-nai-yang',
  alias_resolution_status:'confirmed_catalog_alias_preserve_id',
  alias_evidence:{source_url:'https://thezerophuket.com/',checked_at:checkedAt,verification_status:'verified_primary_source_plus_catalog_provenance',basis:'The preserved Russian generator row is a transliterated duplicate of the English The Zero Nai Yang seed with the same group, district and official source. Both IDs remain; current relationship to Silhouette is unresolved.'}
});
Object.assign(project('the-zero-nai-yang'),{
  possible_rebrand_of:'silhouette-by-the-zero',
  duplicate_resolution_status:'hold_not_merged_current_primary_site_conflict',
  duplicate_review:{source_url:'https://thezerophuket.com/',secondary_source_url:'https://thezerophuket.com/silhouette-nai-yang/',checked_at:checkedAt,verification_status:'reviewed_primary_source_inconclusive',basis:'The current official site presents Silhouette as the Nai Yang project but also retains legacy The Zero Nai Yang text in duplicated/stale homepage content. No explicit first-party rename statement was found, so the two canonical IDs are not merged.'}
});

for(const [id,canonical] of [['zero-bangtao','the-zero-bang-tao'],['zero-naiyang','the-zero-nai-yang']]){
  Object.assign(task(id),{status:'completed_alias_resolved_id_preserved',reason:'catalog_alias_confirmed',next_action:`Route catalogue display to ${canonical}; verify legal seller, inventory and contract separately`,checked_at:checkedAt});
}
Object.assign(task('the-zero-nai-yang'),{status:'hold_possible_rebrand_not_merged',reason:'current_primary_site_inconclusive',next_action:'Obtain explicit developer confirmation whether The Zero Nai Yang was renamed to Silhouette; preserve both IDs meanwhile',checked_at:checkedAt});

const zero=developers.find(x=>x.developer_id==='PHK-011');assert(zero);
const booking={kind:'consultation_booking',value:'https://zerodevelopments.youcanbook.me/',purpose:'project_consultation',source_url:'https://thezerophuket.com/silhouette-nai-yang/',checked_at:checkedAt,verification_status:'verified_published_link',direct_dialogue_verified:false,deliverability_tested:false};
if(!zero.contacts.some(x=>x.kind===booking.kind&&x.value===booking.value))zero.contacts.push(booking);
zero.research_note='Official site now presents Bang Tao and Silhouette as current projects and publishes a consultation-booking route. Legacy The Zero Nai Yang text remains on the homepage without an explicit rename statement; IDs were not merged. WhatsApp target remains unextracted and was not inferred.';
zero.missing_fields.named_sales_person={verification_status:'not_found',checked_at:checkedAt,source_url:'https://thezerophuket.com/silhouette-nai-yang/'};
zero.missing_fields.agency_relations_email={verification_status:'not_found',checked_at:checkedAt,source_url:'https://thezerophuket.com/contact/'};

const oi=observations.records.findIndex(x=>x.developer_id==='PHK-011');assert(oi>=0);
if(!observations.records[oi].contacts.some(x=>x.kind===booking.kind&&x.value===booking.value))observations.records[oi].contacts.push(booking);
observations.records[oi].note=zero.research_note;
observations.duplicate_observations=[...(observations.duplicate_observations||[]).filter(x=>!['zero-bangtao','zero-naiyang','the-zero-nai-yang'].includes(x.project_id)),
  {project_id:'zero-bangtao',canonical_project_id:'the-zero-bang-tao',status:'confirmed_catalog_alias_preserve_id',source_url:'https://thezerophuket.com/bang-tao/',checked_at:checkedAt},
  {project_id:'zero-naiyang',canonical_project_id:'the-zero-nai-yang',status:'confirmed_catalog_alias_preserve_id',source_url:'https://thezerophuket.com/',checked_at:checkedAt},
  {project_id:'the-zero-nai-yang',candidate_project_id:'silhouette-by-the-zero',status:'hold_not_merged_current_primary_site_conflict',source_url:'https://thezerophuket.com/',checked_at:checkedAt}
];
observations.checked_at=checkedAt;

metrics.catalog_aliases_confirmed_preserving_ids=2;
metrics.possible_rebrands_held_not_merged=1;
metrics.zero_duplicate_review_checked_at=checkedAt;
metrics.projects_total=links.length;
metrics.crm_imports_this_run=0;metrics.external_sends_this_run=0;

assert.equal(links.length,618);assert.deepEqual(links.map(x=>x.project_id),beforeIds);
assert.equal(new Set(beforeIds).size,618);
assert.equal(project('zero-bangtao').catalog_alias_of,'the-zero-bang-tao');
assert.equal(project('zero-naiyang').catalog_alias_of,'the-zero-nai-yang');
assert.equal(project('the-zero-nai-yang').duplicate_resolution_status,'hold_not_merged_current_primary_site_conflict');

save('project-links.json',links);save('enrichment-queue.json',queue);save('public-contact-observations.json',observations);save('developers.json',developers);save('metrics.json',metrics);
const resume=read('RESUME.json');
resume.source_commit=sourceCommit;resume.checkpoint_at=checkedAt;
resume.completed=[...new Set([...(resume.completed||[]),'B007_two_Zero_generator_aliases_resolved_ids_preserved','B007_The_Zero_Nai_Yang_vs_Silhouette_held_not_merged','B007_Zero_public_consultation_booking_route'])];
resume.next_actions=(resume.next_actions||[]).filter(x=>!x.startsWith('Review possible Zero'));
resume.next_actions.unshift('Obtain explicit developer confirmation for The Zero Nai Yang ↔ Silhouette; preserve both IDs until then');
resume.developer_cursor='missing_family_507_exact_name_primary_source_pass';
resume.latest_checkpoint_event='CLOUD-INBOX/events/2026-09-19/cloud-both-bases-b007.json';
resume.counts={...resume.counts,catalog_aliases_confirmed_preserving_ids:2,possible_rebrands_held_not_merged:1};
resume.remaining='Two generated Zero catalogue aliases are resolved to canonical IDs without deleting any of 618 project IDs. The Zero Nai Yang versus Silhouette remains an explicit hold because the current first-party site is internally mixed and contains no rename statement. Other 507 missing-family and 60 other-market records remain; legal seller/contract counts and native CRM87 crosswalk remain pending.';
resume.latest_result_commit=null;resume.latest_result_commit_note='B007 working tree; commit recorded after publication.';save('RESUME.json',resume);
save('B007-TEST-REPORT.json',{checked_at:checkedAt,source_commit:sourceCommit,project_ids_preserved:true,projects_total:links.length,unique_project_ids:true,catalog_aliases_confirmed_preserving_ids:2,possible_rebrands_held_not_merged:1,developer_rows_before:43,developer_rows_after:developers.length,new_public_booking_routes:1,crm_imports:0,external_sends:0});
console.log(JSON.stringify({projects:links.length,aliases:2,holds:1,developers:developers.length},null,2));
