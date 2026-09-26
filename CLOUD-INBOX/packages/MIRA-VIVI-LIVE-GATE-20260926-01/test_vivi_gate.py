import copy
import json
import unittest
from pathlib import Path
from vivi_gate import CONTROLS, assess

BASE = json.loads((Path(__file__).parent / 'vivi-gate.json').read_text())


def ready_case(units=True):
    case = copy.deepcopy(BASE)
    case['agency_request'] = {'id': 'AGENCY-REQUEST-1', 'received_at': '2026-09-26T01:00:00Z'}
    case['developer_request'] = {'id': 'DEVELOPER-REQUEST-1', 'agency_request_id': 'AGENCY-REQUEST-1', 'sent_at': '2026-09-26T01:01:00Z'}
    result = {'status': 'none_available', 'units': []}
    if units:
        result = {'status': 'units_available', 'units': [{'unit_id': 'PRIVATE-UNIT', 'quote_amount': 'PRIVATE-AMOUNT', 'currency': 'THB', 'payment_plan_reference': 'PRIVATE-PLAN'}]}
    case['developer_response'] = {'developer_request_id': 'DEVELOPER-REQUEST-1', 'source_type': 'developer_direct', 'received_at': '2026-09-26T01:02:00Z', 'inventory_as_of': '2026-09-26T01:02:00+07:00', 'unit_result': result, 'registration_ack_required': True}
    return case


class GateTests(unittest.TestCase):
    def test_public_template_is_closed_and_contains_no_quote(self):
        result = assess(BASE)
        self.assertFalse(result['response_ready'])
        self.assertFalse(result['commercially_enabled'])
        self.assertEqual(set(result['missing_commercial_controls']), set(CONTROLS))
        self.assertNotIn('quote_amount', json.dumps(BASE))

    def test_exact_direct_response_can_be_ready_without_commercial_enablement(self):
        result = assess(ready_case())
        self.assertTrue(result['response_ready'])
        self.assertFalse(result['commercially_enabled'])
        self.assertEqual(result['errors'], [])

    def test_no_availability_is_a_valid_live_answer(self):
        result = assess(ready_case(units=False))
        self.assertTrue(result['response_ready'])

    def test_old_or_unlinked_response_rejected(self):
        case = ready_case()
        case['developer_response']['developer_request_id'] = 'OTHER'
        self.assertIn('developer_response_not_linked_to_exact_request', assess(case)['errors'])
        case = ready_case()
        case['developer_response']['received_at'] = '2026-09-26T00:00:00Z'
        self.assertIn('response_precedes_request', assess(case)['errors'])

    def test_aggregator_is_not_live_developer_evidence(self):
        case = ready_case()
        case['developer_response']['source_type'] = 'portal_or_broker'
        self.assertIn('developer_response_not_direct', assess(case)['errors'])

    def test_available_unit_requires_quote_and_plan(self):
        case = ready_case()
        case['developer_response']['unit_result']['units'][0]['quote_amount'] = None
        self.assertIn('unit_0_quotation_incomplete', assess(case)['errors'])

    def test_all_current_private_controls_enable_project(self):
        case = ready_case()
        case['commercial_controls'] = {name: {'status': 'verified_current', 'private_evidence_ref': 'PRIVATE-'+name, 'verified_at': '2026-09-26T01:03:00Z'} for name in CONTROLS}
        result = assess(case)
        self.assertTrue(result['commercially_enabled'])
        self.assertTrue(result['customer_registration_enabled'])

    def test_registration_requires_explicit_ack(self):
        case = ready_case()
        case['commercial_controls'] = {name: {'status': 'verified_current', 'private_evidence_ref': 'PRIVATE-'+name, 'verified_at': '2026-09-26T01:03:00Z'} for name in CONTROLS}
        case['developer_response']['registration_ack_required'] = False
        self.assertFalse(assess(case)['customer_registration_enabled'])

    def test_unsafe_declared_true_is_rejected(self):
        for key in ('response_ready', 'commercially_enabled', 'customer_registration_enabled'):
            case = copy.deepcopy(BASE)
            case[key] = True
            self.assertIn('unsafe_true_'+key, assess(case)['errors'])

    def test_timestamp_requires_timezone(self):
        case = ready_case()
        case['developer_response']['received_at'] = '2026-09-26T01:02:00'
        self.assertIn('timezone_required', assess(case)['errors'])


if __name__ == '__main__':
    unittest.main()
