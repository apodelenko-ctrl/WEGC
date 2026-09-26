#!/usr/bin/env python3
"""Validate one live VIVI request-response case without inferring supply.

The public template contains no buyer data or confidential terms. A private operator
may use this validator on an isolated case file; only the resulting status belongs in
public accounting. No network, mail, form or database operation is performed.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

CONTROLS = (
    'agreement_coverage', 'contracting_seller', 'commission_schedule',
    'lead_registration', 'lead_protection', 'downstream_partner_right',
    'media_use_scope',
)


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp_required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timezone_required')
    return result


def current_control(value):
    return (isinstance(value, dict)
            and value.get('status') == 'verified_current'
            and isinstance(value.get('private_evidence_ref'), str)
            and bool(value['private_evidence_ref'].strip())
            and bool(value.get('verified_at')))


def assess(case):
    errors = []
    agency = case.get('agency_request')
    developer = case.get('developer_request')
    response = case.get('developer_response')
    response_ready = False

    if any(value is not None for value in (agency, developer, response)):
        if not isinstance(agency, dict) or not agency.get('id') or not agency.get('received_at'):
            errors.append('agency_request_incomplete')
        if not isinstance(developer, dict) or not developer.get('id') or not developer.get('sent_at'):
            errors.append('developer_request_incomplete')
        elif developer.get('agency_request_id') != (agency or {}).get('id'):
            errors.append('developer_request_not_linked_to_agency_request')
        if not isinstance(response, dict):
            errors.append('developer_response_missing')
        else:
            if response.get('developer_request_id') != (developer or {}).get('id'):
                errors.append('developer_response_not_linked_to_exact_request')
            if response.get('source_type') != 'developer_direct':
                errors.append('developer_response_not_direct')
            try:
                if timestamp(response.get('received_at')) < timestamp((developer or {}).get('sent_at')):
                    errors.append('response_precedes_request')
            except ValueError as exc:
                errors.append(str(exc))
            if not response.get('inventory_as_of'):
                errors.append('inventory_as_of_missing')
            result = response.get('unit_result')
            if not isinstance(result, dict) or result.get('status') not in ('units_available', 'none_available'):
                errors.append('unit_result_missing')
            elif result['status'] == 'units_available':
                units = result.get('units')
                if not isinstance(units, list) or not units:
                    errors.append('available_units_missing')
                else:
                    for index, unit in enumerate(units):
                        required = ('unit_id', 'quote_amount', 'currency', 'payment_plan_reference')
                        if not isinstance(unit, dict) or any(unit.get(k) in (None, '') for k in required):
                            errors.append(f'unit_{index}_quotation_incomplete')
            elif result.get('units') not in (None, []):
                errors.append('none_available_must_not_list_units')
        response_ready = not errors

    controls = case.get('commercial_controls') or {}
    missing_controls = [name for name in CONTROLS if not current_control(controls.get(name))]
    commercially_enabled = response_ready and not missing_controls
    registration_enabled = commercially_enabled and bool(
        isinstance(response, dict) and response.get('registration_ack_required') is True)

    declared = {
        'response_ready': case.get('response_ready'),
        'commercially_enabled': case.get('commercially_enabled'),
        'customer_registration_enabled': case.get('customer_registration_enabled'),
    }
    computed = {
        'response_ready': response_ready,
        'commercially_enabled': commercially_enabled,
        'customer_registration_enabled': registration_enabled,
    }
    for key in declared:
        if declared[key] is True and computed[key] is not True:
            errors.append('unsafe_true_' + key)

    return {
        'project_id': case.get('project_id'),
        **computed,
        'missing_commercial_controls': missing_controls,
        'errors': errors,
        'safe_to_reply_with_live_availability': response_ready,
        'safe_to_register_customer': registration_enabled,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = assess(json.loads(args.case.read_text()))
    body = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(body)
    print(body)
    raise SystemExit(0 if not result['errors'] else 1)
