import importlib.util,json,unittest,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PublicLaunchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('launch',ROOT/'scripts/mira-build-launch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.build();m.build_catalogue();cls.data=json.loads((ROOT/'mira/data/phuket.json').read_text())
 def test_618_real_source_records_and_detail_files(self):
  self.assertEqual(self.data['count'],618)
  self.assertEqual(len({r['slug']for r in self.data['records']}),618)
  for r in self.data['records']:self.assertTrue((ROOT/f'mira/phuket/project/{r["slug"]}/index.html').is_file())
 def test_source_hash_is_exact(self):self.assertEqual(self.data['sourceSha256'],hashlib.sha256((ROOT/'ru/wegc-catalog-data.js').read_bytes()).hexdigest())
 def test_old_demo_remains_45(self):self.assertEqual(len(json.loads((ROOT/'mira/data/catalog.json').read_text())['projects']),45)
 def test_legal_docs_linked_in_all_variants(self):
  for route in ['start','growth','business','variants','access','phuket','expo']:
   s=(ROOT/f'mira/{route}/index.html').read_text();self.assertIn('/mira/documents/',s);self.assertIn('Content-Security-Policy',s)
 def test_no_actual_registration_or_pii_fields(self):
  for route in ['start','growth','business','access']:
   s=(ROOT/f'mira/{route}/index.html').read_text();self.assertNotIn('type="email"',s);self.assertNotIn('type="tel"',s);self.assertNotIn('data-netlify',s)
  self.assertFalse(json.loads((ROOT/'mira/launch/release.json').read_text())['live_registration_enabled'])
 def test_all_three_visual_structures_are_distinct(self):
  self.assertIn('door-scene',(ROOT/'mira/start/index.html').read_text());self.assertIn('chat-row',(ROOT/'mira/growth/index.html').read_text());self.assertIn('proof-console',(ROOT/'mira/business/index.html').read_text())
 def test_production_js_no_sender_or_tracking(self):
  for p in [ROOT/'mira/launch/launch.mjs',ROOT/'mira/phuket/catalogue.mjs']:
   s=p.read_text();self.assertNotIn('sendBeacon',s);self.assertNotIn('localStorage',s);self.assertNotIn('innerHTML',s)
 def test_unillustrated_records_do_not_get_wrong_project_image(self):
  self.assertEqual(sum(bool(r['image'])for r in self.data['records']),5)
  for r in self.data['records']:
   if r['image']:self.assertTrue((ROOT/r['image'].lstrip('/')).exists())
if __name__=='__main__':unittest.main()
