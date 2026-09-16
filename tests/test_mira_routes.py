import copy,csv,importlib.util,json,unittest
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('routes',ROOT/'scripts/mira-acquisition-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
TODAY=date(2026,9,16)
class RouteTests(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((ROOT/m.REL).read_text())
        with (ROOT/'project-bible/mira/sales/russia-launch-100-quality.csv').open() as f:self.c={r['agency_id']:r for r in csv.DictReader(f)}
    def validate(self):return m.validate(self.p,self.c,TODAY)
    def test_actual_review_scope_and_no_inflation(self):
        result=self.validate()
        self.assertEqual(result['reviewed_accounts'],21)
        self.assertEqual(result['new_focused_reviews'],18)
        self.assertEqual(result['reused_cp05_reviews'],3)
        self.assertEqual(result['accounts_with_named_direct_route'],7)
        self.assertEqual(result['named_direct_routes'],10)
        self.assertEqual(result['ready_for_owner_review'],15)
        self.assertEqual(result['wave12_draft_candidates'],10)
        self.assertEqual(result['approved_to_send'],0)
    def test_contacted_and_greenfield_cannot_be_inferred(self):
        self.p['outreach_authorized']=True
        with self.assertRaises(ValueError):self.validate()
        self.p['outreach_authorized']=False;self.p['reviews'][0]['greenfield_confirmed']=True
        with self.assertRaises(ValueError):self.validate()
    def test_wrong_domain_cannot_supply_real_estate_contact(self):
        row=next(r for r in self.p['reviews'] if r['review_state']=='hold_entity_mismatch')
        row['routes']=[self.p['reviews'][0]['routes'][0]]
        with self.assertRaises(ValueError):self.validate()
    def test_franchise_route_is_not_ready(self):
        row=next(r for r in self.p['reviews'] if r['review_state']=='hold_wrong_function');row['review_state']='ready_for_owner_review'
        with self.assertRaises(ValueError):self.validate()
    def test_duplicate_contacts_and_wave_slots_rejected(self):
        r=self.p['reviews'][1];r['routes'].append(copy.deepcopy(r['routes'][0]))
        with self.assertRaises(ValueError):self.validate()
        r['routes'].pop();r['wave_rank']=1
        with self.assertRaises(ValueError):self.validate()
    def test_sources_and_dates_checked(self):
        row=self.p['reviews'][0];row['source_urls']=['https://unrelated.example.test/']
        with self.assertRaises(ValueError):self.validate()
        row['source_urls']=['https://www.granovit.ru/'];row['reviewed_on']='2026-09-17'
        with self.assertRaises(ValueError):self.validate()
    def test_drafts_cover_exact_ten_wave_candidates(self):
        text=(ROOT/'project-bible/mira/sales/russia-wave-01-reviewed-drafts.md').read_text()
        expected={r['agency_id'] for r in self.p['reviews'] if r['wave_rank'] is not None and r['review_state']=='ready_for_owner_review'}
        import re
        ids=re.findall(r'^Agency-ID: `(RU-A-[a-f0-9]+)`',text,re.M)
        self.assertEqual(set(ids),expected);self.assertEqual(len(ids),10)
        self.assertEqual(text.count('Статус: `not_approved / not_sent`'),10)
        self.assertNotIn('до 90%',text)
        self.assertNotIn('{{',text)
    def test_current_wave_overrides_do_not_mutate_historical_files(self):
        old=(ROOT/'project-bible/mira/sales/russia-wave-01-owner-review.csv').read_text()
        self.assertIn('direktor@granovit.ru',old)
        new=(ROOT/'project-bible/mira/sales/russia-wave-01-reviewed-drafts.md').read_text()
        self.assertIn('supersedes',new)
        self.assertIn('hold_wrong_function',new)
        self.assertIn('hold_decision_owner',new)
if __name__=='__main__':unittest.main()
