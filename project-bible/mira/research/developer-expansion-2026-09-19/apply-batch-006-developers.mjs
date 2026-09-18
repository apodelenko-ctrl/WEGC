import fs from 'node:fs';

const path='project-bible/mira/research/developer-expansion-2026-09-19/public-contact-observations.json';
const data=JSON.parse(fs.readFileSync(path,'utf8'));
const checkedAt='2026-09-18T23:11:27Z';
data.checked_at=checkedAt;

const laguna={
  developer_id:'PHK-007',visibility:'public_business',
  contacts:[
    {kind:'email',value:'info@lagunaphuket.com',purpose:'general',source_url:'https://www.lagunaphuket.com/contact/',checked_at:checkedAt,verification_status:'verified_public_source',direct_dialogue_verified:false,deliverability_tested:false},
    {kind:'phone',value:'+66 (0) 7636 2300',purpose:'general',source_url:'https://www.lagunaphuket.com/contact/',checked_at:checkedAt,verification_status:'verified_public_source',direct_dialogue_verified:false,deliverability_tested:false}
  ],
  field_evidence:[
    {field:'property_division',value:'Laguna Phuket branded residences and property division',source_url:'https://www.lagunaphuket.com/live/property/',checked_at:checkedAt,verification_status:'verified_public_source',note:'Official page routes current residential portfolio to Banyan Group Residences; this does not identify a project legal seller.'}
  ],
  missing_fields:{legal_name:'not_found',named_sales_person:'not_found',direct_public_work_email:'not_found',whatsapp_url:'not_found',telegram_url:'not_found',line_url:'not_found',agency_relations_email:'not_found'},
  note:'Fresh general Laguna Phuket contact route. It is not an agency-relations recipient and was not contacted.'
};
const ri=data.records.findIndex(r=>r.developer_id==='PHK-007');
if(ri>=0)data.records[ri]=laguna;else data.records.push(laguna);

const observations=[
  {
    project_id:'naturale-kamala',developer_id:'PHK-041',mapping_status:'verified_public_sources',visibility:'public_business',
    source_url:'https://kellerhenson.com/project/naturale-kamala',secondary_source_url:'https://www.facebook.com/naturalephuket/',checked_at:checkedAt,
    basis:'Current exact project page identifies Naturale Kamala developer as AAG Development; the public Naturale Phuket brand page independently publishes Naturale Kamala material. The primary Naturale website identifies AAG only for Cherng Talay, so this remains secondary-source mapping and does not verify the legal seller or contract coverage.'
  },
  {
    project_id:'laguna-lakeside',developer_id:'PHK-006',mapping_status:'verified_public_sources',visibility:'public_business',
    source_url:'https://www.lagunaphuket.com/live/property/',secondary_source_url:'https://www.fazwaz.com/projects/thailand/phuket/thalang/choeng-thale/laguna-lakeside',checked_at:checkedAt,
    basis:'Official Laguna Phuket property page states the residential portfolio is offered by Banyan Group Residences, while current exact project sources identify Laguna Lakeside as a Laguna Property development. PHK-007 is retained as the public Laguna sales-channel entity, but the canonical project developer-group link is PHK-006. Legal seller and contract coverage remain unverified.'
  }
];
for(const row of observations){
  const i=data.project_observations.findIndex(r=>r.project_id===row.project_id);
  if(i>=0)data.project_observations[i]=row;else data.project_observations.push(row);
}
fs.writeFileSync(path,JSON.stringify(data,null,2)+'\n');
