import {ApiError} from './auth.mjs';
export const TRANSITIONS=Object.freeze({
 submitted:['review','needs_information','rejected','duplicate','conflict'],
 review:['needs_information','developer_submitted','rejected','duplicate','conflict'],
 needs_information:['review','closed'],
 developer_submitted:['developer_confirmed','needs_information','rejected','duplicate','conflict'],
 developer_confirmed:['conflict','expired','closed'],
 duplicate:['review','closed'],conflict:['review','rejected','closed'],rejected:['closed'],expired:['review','closed'],closed:[]
});
export const STAGES=Object.freeze(['consultation','booking','contract','buyer_payment','commission_accrued','commission_received','agency_paid']);
export const EVIDENCE_KINDS=Object.freeze(['agency_agreement','project_agreement','inventory','registration_rules','commission_schedule','materials_rights','client_consent','owner_approval','developer_submission','developer_confirmation','lead_protection','booking','contract','buyer_payment','commission_accrued','commission_received','agency_paid','cancellation','payment_consent']);
export function requireKeys(data,allowed,required=[]) {
 if(!data || typeof data!=='object' || Array.isArray(data) || Object.keys(data).some(k=>!allowed.includes(k)) || required.some(k=>data[k]===undefined))throw new ApiError(400,'invalid_fields');
}
export function string(value,min=1,max=120) {
 if(typeof value!=='string'||value.trim().length<min||value.trim().length>max||/[\u0000-\u001f\u007f]/.test(value))throw new ApiError(400,'invalid_value');
 return value.trim();
}
export function identifier(value) {
 const s=string(value,1,100);if(!/^[A-Za-z0-9_-]+$/.test(s))throw new ApiError(400,'invalid_identifier');return s;
}
export function evidenceRef(value) {const s=identifier(value);if(!s.startsWith('EVID-'))throw new ApiError(400,'invalid_evidence_reference');return s;}
export function iso(value) {const s=string(value,20,30);if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/.test(s)||!Number.isFinite(Date.parse(s)))throw new ApiError(400,'invalid_timestamp');const canonical=new Date(s).toISOString();if(canonical!==(s.includes('.')?s:s.replace('Z','.000Z')))throw new ApiError(400,'invalid_timestamp');return canonical;}
export function currentEvidence(e,kind,scope,now=Date.now()) {
 return Boolean(e && e.kind===kind && e.verified===1 && !e.revoked_at && e.verified_at && Date.parse(e.verified_at)<=now && (!e.expires_at||Date.parse(e.expires_at)>now) &&
   (scope.project_id===undefined||e.project_id===scope.project_id) && (scope.agency_id===undefined||e.agency_id===scope.agency_id) && (scope.entity_id===undefined||e.entity_id===scope.entity_id));
}
export function leadTransition(current,body) {
 requireKeys(body,['status','version','evidence_ref','owner_approval_ref','protection_ref','protection_until','reason'],['status','version','reason']);
 if(!Number.isSafeInteger(body.version)||body.version!==current.version)throw new ApiError(409,'stale_version');
 if(!TRANSITIONS[current.status]?.includes(body.status))throw new ApiError(409,'invalid_transition');
 string(body.reason,3,240);
 if(['developer_submitted','developer_confirmed'].includes(body.status))evidenceRef(body.evidence_ref);
 if(body.status==='developer_submitted')evidenceRef(body.owner_approval_ref);
 if(body.protection_ref||body.protection_until){if(body.status!=='developer_confirmed'||!body.protection_ref||!body.protection_until)throw new ApiError(400,'invalid_protection');evidenceRef(body.protection_ref);iso(body.protection_until);}
 return body;
}
export function decimalAmount(value) {
 if(typeof value!=='string'||! /^(0|[1-9]\d{0,14})(\.\d{1,4})?$/.test(value)||!/[1-9]/.test(value))throw new ApiError(400,'invalid_amount');return value;
}
export function currency(value){if(typeof value!=='string'||!/^[A-Z]{3}$/.test(value))throw new ApiError(400,'invalid_currency');return value;}
