"""Reproducible research projection; no CRM/network writes or message delivery.

Canonical research inputs remain in project-bible/mira/data. Operational state is
owned by private CRM, not by these generated files. Python standard library only.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = Path('project-bible/mira/data')
OUT = Path('project-bible/mira/research/developer-expansion-2026-09-19')
UNKNOWN = {'', 'unknown', 'not_found', 'not_checked', 'null', 'none'}

def known(value):
    return value is not None and str(value).strip().casefold() not in UNKNOWN

def norm(value):
    return ' '.join(str(value or '').casefold().split())

def read_csv(root, path):
    with (root / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def read_json(root, path):
    return json.loads((root / path).read_text())

def build(root, observations):
    master_path = DATA / 'phuket-developer-master.csv'
    alias_path = DATA / 'phuket-developer-alias-map-v1.csv'
    catalog_path = Path('mira/catalog/data.json')
    master = read_csv(root, master_path)
    aliases = read_csv(root, alias_path)
    projects = read_json(root, catalog_path)['projects']
    if len({r['developer_id'] for r in master}) != len(master):
        raise ValueError('duplicate developer ID')
    if len({r['id'] for r in projects}) != len(projects):
        raise ValueError('duplicate project ID')
    # Exact, documented aliases only. Ambiguity is retained, never resolved by
    # first match, substring guessing, hotel brand, or model confidence.
    canonical = {norm(r['alias']): norm(r['canonical_group']) for r in aliases}
    identities = defaultdict(set)
    for r in master:
        name = norm(r['developer_group'])
        identities[name].add(r['developer_id'])
        identities[canonical.get(name, name)].add(r['developer_id'])
    developers = []
    by_id = {}
    for r in master:
        d = {
            'developer_id': r['developer_id'], 'name': r['developer_group'],
            'entity_type': r['entity_type'], 'legal_name_candidate': r['legal_name'],
            'legal_entity_status': 'requires_project_specific_verification',
            'website': r['official_website'], 'contacts': [],
            'relationship_stage': 'crm_reconciliation_required',
            'agreement_status': 'unknown', 'agreement_evidence': None,
            'outreach_status': 'unknown_pending_mail_crm_reconciliation',
            'source': {'path': str(master_path), 'checked_at': r['checked_at']},
        }
        for kind in ('email', 'phone'):
            if known(r[kind]):
                d['contacts'].append({'kind': kind, 'value': r[kind],
                    'source_url': r['source_url'], 'checked_at': r['checked_at'],
                    'verification_status': 'inherited_not_rechecked',
                    'purpose': 'unclassified', 'direct_dialogue_verified': False})
        developers.append(d)
        by_id[d['developer_id']] = d
    seen = set()
    for row in observations['records']:
        did = row['developer_id']
        if did not in by_id:
            raise ValueError('observation has unknown developer ID: ' + did)
        if row.get('visibility') != 'public_business':
            raise ValueError('private evidence is not allowed in public research projection')
        for c in row['contacts']:
            if not all(known(c.get(k)) for k in ('kind', 'value', 'source_url', 'checked_at')):
                raise ValueError('contact missing field evidence')
            if not c['source_url'].startswith('https://'):
                raise ValueError('non-web source in public projection')
            signature = (did, c['kind'], norm(c['value']), c['source_url'])
            if signature in seen:
                continue
            seen.add(signature)
            by_id[did]['contacts'].append(dict(c))
        for field in row.get('field_evidence', []):
            if not all(known(field.get(k)) for k in ('field', 'value', 'source_url', 'checked_at', 'verification_status')) or not field['source_url'].startswith('https://'):
                raise ValueError('developer field missing public evidence')
        by_id[did].setdefault('field_evidence', []).extend(row.get('field_evidence', []))
        by_id[did]['missing_fields'] = {name: {'verification_status': status, 'checked_at': observations.get('checked_at'), 'source_url': row['contacts'][0]['source_url'] if row['contacts'] else None} for name, status in row.get('missing_fields', {}).items()}
        if row.get('note'):
            by_id[did]['research_note'] = row['note']
    project_ids = {p['id'] for p in projects}
    verified_links = {}
    for row in observations.get('project_observations', []):
        pid = row.get('project_id')
        if pid not in project_ids or pid in verified_links:
            raise ValueError('unknown or duplicate observed project ID')
        if row.get('visibility') != 'public_business':
            raise ValueError('private project observation')
        if not all(known(row.get(k)) for k in ('source_url', 'checked_at', 'basis')):
            raise ValueError('project observation lacks evidence')
        if not row['source_url'].startswith('https://'):
            raise ValueError('non-web project source')
        if row.get('mapping_status') not in {'verified_primary_source', 'verified_public_sources', 'excluded_non_residential'}:
            raise ValueError('unsupported project observation status')
        if row['mapping_status'] in {'verified_primary_source', 'verified_public_sources'} and row.get('developer_id') not in by_id:
            raise ValueError('unknown observed developer ID')
        if row['mapping_status'] == 'excluded_non_residential' and row.get('developer_id') is not None:
            raise ValueError('excluded taxonomy must not silently assign a developer')
        verified_links[pid] = row
    links = []
    queue = []
    for p in projects:
        family = p.get('family')
        key = canonical.get(norm(family), norm(family))
        candidates = sorted(identities.get(key, set())) if family else []
        status = ('unresolved_no_family' if not family else
                  'unresolved_family_not_in_master' if not candidates else
                  'ambiguous_group' if len(candidates) > 1 else
                  'inherited_group_match_needs_verification')
        link = {'project_id': p['id'], 'name': p['name'], 'market': 'phuket',
                'family': family, 'developer_id': candidates[0] if len(candidates) == 1 else None,
                'candidate_developer_ids': candidates, 'mapping_status': status,
                'mapping_evidence': {'path': str(catalog_path), 'source_row': p.get('sourceRow'),
                    'family_basis': p.get('familyBasis'), 'alias_path': str(alias_path)},
                'legal_seller_verified': False, 'contract_covered': None,
                'commercially_enabled': False}
        observation = verified_links.get(p['id'])
        if observation:
            link['inherited_mapping_status'] = status
            link['inherited_candidate_developer_ids'] = candidates
            link['mapping_status'] = observation['mapping_status']
            link['developer_id'] = observation.get('developer_id')
            link['candidate_developer_ids'] = ([link['developer_id']] if link['developer_id'] else [])
            link['primary_evidence'] = dict(observation)
            # This overlay can never set seller, contract or commercial gates.
            status = link['mapping_status']
        links.append(link)
        queue.append({'task_key': 'project-developer:' + p['id'], 'project_id': p['id'],
                      'developer_id': link['developer_id'], 'status': 'queued',
                      'reason': status, 'next_action': 'Find primary project source, verify developer and project legal seller; preserve all candidate IDs'})
    for d in developers:
        fresh = [c for c in d['contacts'] if c.get('verification_status') == 'verified_public_source']
        d['fresh_contact_verified'] = bool(fresh)
        d['project_candidate_count'] = sum(d['developer_id'] in p['candidate_developer_ids'] for p in links)
        queue.append({'task_key': 'developer-contact:' + d['developer_id'],
            'developer_id': d['developer_id'], 'status': 'partial' if fresh else 'queued',
            'reason': 'contract_and_crm_state_not_imported',
            'next_action': 'Reconcile existing CRM/mail, legal entity, named partner contact, project coverage and agreement evidence; do not restart existing conversation'})
    counts = Counter(p['mapping_status'] for p in links)
    metrics = {
        'projects_total': len(links), 'developer_master_rows': len(developers),
        'developer_rows_are_verified_legal_entities': False,
        'projects_with_inherited_family': sum(bool(p['family']) for p in links),
        'project_mapping_counts': dict(counts),
        'developers_with_fresh_public_contacts': sum(d['fresh_contact_verified'] for d in developers),
        'projects_excluded_non_residential': counts.get('excluded_non_residential', 0),
        'projects_with_primary_developer_group': counts.get('verified_primary_source', 0),
        'projects_with_verified_public_developer_group': counts.get('verified_primary_source', 0) + counts.get('verified_public_sources', 0),
        'fresh_contact_coverage_by_kind': {kind: sum(any(c.get('kind') == kind and c.get('verification_status') == 'verified_public_source' for c in d['contacts']) for d in developers) for kind in ('email', 'phone', 'whatsapp', 'telegram', 'line', 'broker_portal')},
        'signed_contracts_total': None, 'projects_covered_by_active_contract': None,
        'emails_sent_total': None, 'developer_replies_total': None,
        'unknown_metric_reason': 'Private CRM, mail history and agreements have not been imported. Unknown is not zero.',
        'crm_imports_this_run': 0, 'external_sends_this_run': 0,
    }
    manifest = {str(p): hashlib.sha256((root/p).read_bytes()).hexdigest()
                for p in (master_path, alias_path, catalog_path)}
    manifest['public_observations_canonical_json'] = hashlib.sha256(json.dumps(observations, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    receipt_path = Path('CLOUD-INBOX/receipts/MIRA-MKT-20260918-01.json')
    if (root/receipt_path).exists():
        receipt = read_json(root, receipt_path)
        checkpoint = receipt.get('current_checkpoint', {})
        metrics['native_crm_snapshot'] = {
            'source_path': str(receipt_path), 'updated_at': receipt.get('updated_at'),
            'counts': checkpoint.get('counts', receipt.get('native_import', {})),
            'scope': checkpoint.get('scope', 'see_receipt'),
            'source': 'LOCAL_receipt_not_independent_cloud_live_test',
            'crosswalk_to_research_master': 'pending; do not add these counts together',
        }
        manifest[str(receipt_path)] = hashlib.sha256((root/receipt_path).read_bytes()).hexdigest()
    return {'developers': developers, 'project_links': links, 'enrichment_queue': queue,
            'metrics': metrics, 'source_sha256': manifest}

def plan_inquiry(case, link, developer, agreement):
    """Pure dry-run planner. Arguments are trusted CRM adapter data, never LLM text.

    Returns a proposal for the existing OMNI outbox; does not create a second
    transport or automatically grant sending permission. Each buyer has case_id.
    """
    for field in ('case_id', 'agency_id', 'project_id', 'request_revision'):
        if not known(case.get(field)):
            raise ValueError('missing ' + field)
    if case.get('profile') != 'mira_agency':
        raise ValueError('buyer/product profile may not route agency inquiries')
    if case.get('project_id') != link.get('project_id'):
        raise ValueError('project scope mismatch')
    reasons = []
    if not link.get('developer_id') or link['developer_id'] != developer.get('developer_id'):
        reasons.append('developer_unresolved')
    if link.get('mapping_status') != 'verified_primary_source' or not link.get('primary_evidence'):
        reasons.append('project_developer_not_verified')
    if not link.get('legal_seller_verified'):
        reasons.append('project_seller_not_verified')
    if not (agreement.get('status') == 'active' and agreement.get('evidence_ref')
            and agreement.get('developer_id') == developer.get('developer_id')
            and case['project_id'] in agreement.get('project_ids', [])
            and agreement.get('valid_at_request') is True):
        reasons.append('active_project_contract_not_verified')
    contacts = [c for c in developer.get('contacts', []) if
        c.get('kind') == 'email' and c.get('verification_status') == 'verified_public_source'
        and c.get('purpose') in {'sales', 'agency_relations'} and c.get('source_url')
        and c.get('checked_at') and c.get('value')]
    if len(contacts) != 1:
        reasons.append('unique_sales_recipient_not_verified')
    if case.get('suppressed') or case.get('paused'):
        reasons.append('contact_suppressed_or_paused')
    key = hashlib.sha256(json.dumps([case[k] for k in ('agency_id','case_id','project_id','request_revision')]).encode()).hexdigest()
    return {'case_id': case['case_id'], 'agency_id': case['agency_id'],
        'project_id': case['project_id'], 'idempotency_key': key,
        'state': 'needs_verification' if reasons else 'draft_ready_for_review',
        'blockers': reasons, 'recipient': contacts[0]['value'] if len(contacts) == 1 and not reasons else None,
        'outbox_kind': 'developer_inquiry_draft', 'send_authorized': False,
        'crm_write_confirmed': False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    observations = read_json(args.root, OUT / 'public-contact-observations.json')
    result = build(args.root, observations)
    output = args.root / args.output
    output.mkdir(parents=True, exist_ok=True)
    for key in ('developers', 'project_links', 'enrichment_queue', 'metrics', 'source_sha256'):
        (output/(key.replace('_','-') + '.json')).write_text(json.dumps(result[key], ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['metrics'], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
