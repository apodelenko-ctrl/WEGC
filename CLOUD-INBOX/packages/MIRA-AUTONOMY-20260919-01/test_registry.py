import copy
import json
import tempfile
import unittest
from pathlib import Path
from registry import ROOT, OUT, build, plan_inquiry

class RegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs=json.loads((ROOT/OUT/'public-contact-observations.json').read_text())
        cls.result=build(ROOT,cls.obs)
    def test_catalog_reconciliation_is_complete(self):
        original=json.loads((ROOT/'mira/catalog/data.json').read_text())['projects']
        links=self.result['project_links']
        self.assertEqual({p['id'] for p in original},{p['project_id'] for p in links})
        self.assertEqual(len(links),len(original))
    def test_missing_and_inherited_family_never_become_verified(self):
        for p in self.result['project_links']:
            self.assertFalse(p['legal_seller_verified'])
            self.assertFalse(p['commercially_enabled'])
            self.assertIsNone(p['contract_covered'])
            if not p['family']:self.assertIsNone(p['developer_id'])
    def test_ambiguous_banyan_preserves_both_source_ids(self):
        links=[p for p in self.result['project_links'] if p['family']=='Banyan / Laguna residences']
        self.assertTrue(links)
        for p in links:
            self.assertEqual(p['candidate_developer_ids'],['PHK-006','PHK-007'])
            self.assertIsNone(p['developer_id'])
    def test_repeat_build_has_stable_ids_and_no_duplicates(self):
        self.assertEqual(self.result,build(ROOT,self.obs))
        keys=[x['task_key'] for x in self.result['enrichment_queue']]
        self.assertEqual(len(keys),len(set(keys)))
    def test_private_source_cannot_enter_public_projection(self):
        obs=copy.deepcopy(self.obs);obs['records'][0]['visibility']='private_mail'
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_observation_requires_field_evidence(self):
        obs=copy.deepcopy(self.obs);del obs['records'][0]['contacts'][0]['source_url']
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_unknown_operational_counts_are_not_zero(self):
        for k in ['signed_contracts_total','projects_covered_by_active_contract','emails_sent_total','developer_replies_total']:
            self.assertIsNone(self.result['metrics'][k])
    def test_primary_observation_does_not_grant_seller_or_contract(self):
        obs=copy.deepcopy(self.obs)
        obs['project_observations'][0].update(legal_seller_verified=True,contract_covered=True,commercially_enabled=True)
        row=next(p for p in build(ROOT,obs)['project_links'] if p['project_id']==obs['project_observations'][0]['project_id'])
        self.assertFalse(row['legal_seller_verified']);self.assertIsNone(row['contract_covered']);self.assertFalse(row['commercially_enabled'])
    def test_unknown_observed_project_rejected(self):
        obs=copy.deepcopy(self.obs);obs['project_observations'][0]['project_id']='missing-project'
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_duplicate_observed_project_rejected(self):
        obs=copy.deepcopy(self.obs);obs['project_observations'].append(obs['project_observations'][0])
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_private_project_observation_rejected(self):
        obs=copy.deepcopy(self.obs);obs['project_observations'][0]['visibility']='private_mail'
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_project_observation_requires_source(self):
        obs=copy.deepcopy(self.obs);del obs['project_observations'][0]['source_url']
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_unknown_observed_developer_rejected(self):
        obs=copy.deepcopy(self.obs);obs['project_observations'][0]['developer_id']='PHK-MISSING'
        with self.assertRaises(ValueError):build(ROOT,obs)
    def test_no_blanket_naturale_alias(self):
        links={p['project_id']:p for p in self.result['project_links']}
        self.assertEqual(links['naturale-cherngtalei']['developer_id'],'PHK-041')
        self.assertIsNone(links['naturale-kamala']['developer_id'])
    def test_nonresidential_record_preserved_but_held(self):
        p=next(p for p in self.result['project_links'] if p['project_id']=='andamanda-phuket')
        self.assertEqual(p['mapping_status'],'excluded_non_residential');self.assertIsNone(p['developer_id'])
    def test_new_developer_field_evidence_required(self):
        obs=copy.deepcopy(self.obs)
        row=next(r for r in obs['records'] if r.get('field_evidence'));del row['field_evidence'][0]['source_url']
        with self.assertRaises(ValueError):build(ROOT,obs)

class InquiryTest(unittest.TestCase):
    def setUp(self):
        self.case={'case_id':'case-test','agency_id':'agency-test','project_id':'project-test',
                   'request_revision':1,'profile':'mira_agency'}
        self.link={'project_id':'project-test','developer_id':'dev-test',
                   'mapping_status':'verified_primary_source','primary_evidence':'fixture',
                   'legal_seller_verified':True}
        self.dev={'developer_id':'dev-test','contacts':[{'kind':'email','value':'sales@example.test',
                  'purpose':'sales','source_url':'https://example.test','checked_at':'2026-09-18',
                  'verification_status':'verified_public_source'}]}
        self.contract={'developer_id':'dev-test','status':'active','evidence_ref':'fixture',
                       'project_ids':['project-test'],'valid_at_request':True}
    def plan(self):return plan_inquiry(self.case,self.link,self.dev,self.contract)
    def test_complete_inputs_only_prepare_draft(self):
        p=self.plan();self.assertEqual(p['state'],'draft_ready_for_review')
        self.assertFalse(p['send_authorized']);self.assertFalse(p['crm_write_confirmed'])
    def test_repeat_and_separate_buyer_cases(self):
        p=self.plan();self.assertEqual(p,self.plan())
        self.case['case_id']='another-buyer';self.assertNotEqual(p['idempotency_key'],self.plan()['idempotency_key'])
    def test_contract_scope_and_expiry_are_required(self):
        for bad in ({'project_ids':['different-project']},{'status':'expired'},{'developer_id':'other'},{'evidence_ref':None},{'valid_at_request':False}):
            before=copy.deepcopy(self.contract);self.contract.update(bad)
            self.assertIn('active_project_contract_not_verified',self.plan()['blockers']);self.contract=before
    def test_inherited_match_is_never_sendable(self):
        self.link['mapping_status']='inherited_group_match_needs_verification'
        self.assertEqual(self.plan()['state'],'needs_verification');self.assertIsNone(self.plan()['recipient'])
    def test_ambiguous_recipients_are_not_guessed(self):
        self.dev['contacts'].append(dict(self.dev['contacts'][0],value='other@example.test'))
        self.assertIn('unique_sales_recipient_not_verified',self.plan()['blockers'])
    def test_product_and_project_isolation(self):
        self.case['profile']='phuket_buyer'
        with self.assertRaises(ValueError):self.plan()
        self.case['profile']='mira_agency';self.case['project_id']='wrong-project'
        with self.assertRaises(ValueError):self.plan()
    def test_suppression_and_pause(self):
        for k in ['paused','suppressed']:
            self.case[k]=True;self.assertIsNone(self.plan()['recipient']);self.case[k]=False

if __name__=='__main__':unittest.main()
