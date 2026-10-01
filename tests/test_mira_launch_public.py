import importlib.util,json,unittest,hashlib,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PublicLaunchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.root=Path(cls.tmp.name)
  files=['scripts/mira-launch-source.py','ru/wegc-catalog-data.js','project-bible/mira/data/phuket-project-master.csv','mira/catalog/data.json','mira/data/catalog.json','mira/launch/launch.mjs','mira/phuket/catalogue.mjs']
  for name in files:
   target=cls.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
  spec=importlib.util.spec_from_file_location('launch',ROOT/'scripts/mira-build-launch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.ROOT=cls.root;m.build();m.build_catalogue();cls.data=json.loads((cls.root/'mira/data/phuket.json').read_text())
  for row in cls.data['records']:
   if row['image']:
    name=row['image'].lstrip('/');target=cls.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)

 def test_618_real_source_records_and_detail_files(self):
  self.assertEqual(self.data['count'],618)
  self.assertEqual(len({r['slug']for r in self.data['records']}),618)
  for r in self.data['records']:self.assertTrue((self.root/f'mira/phuket/project/{r["slug"]}/index.html').is_file())
 def test_source_hash_is_exact(self):self.assertEqual(self.data['sourceSha256'],hashlib.sha256((self.root/'ru/wegc-catalog-data.js').read_bytes()).hexdigest())
 def test_old_demo_remains_45(self):self.assertEqual(len(json.loads((self.root/'mira/data/catalog.json').read_text())['projects']),45)
 def test_legal_docs_linked_in_all_variants(self):
  for route in ['start','growth','business','variants','access','phuket','expo']:
   s=(self.root/f'mira/{route}/index.html').read_text();self.assertIn('/mira/documents/',s);self.assertIn('Content-Security-Policy',s)
 def test_no_actual_registration_or_pii_fields(self):
  for route in ['start','growth','business','access']:
   s=(self.root/f'mira/{route}/index.html').read_text();self.assertNotIn('type="email"',s);self.assertNotIn('type="tel"',s);self.assertNotIn('data-netlify',s)
  self.assertFalse(json.loads((self.root/'mira/launch/release.json').read_text())['live_registration_enabled'])
 def test_all_three_visual_structures_are_distinct(self):
  self.assertIn('door-scene',(self.root/'mira/start/index.html').read_text());self.assertIn('chat-row',(self.root/'mira/growth/index.html').read_text());self.assertIn('proof-console',(self.root/'mira/business/index.html').read_text())
 def test_production_js_no_sender_or_tracking(self):
  for p in [self.root/'mira/launch/launch.mjs',self.root/'mira/phuket/catalogue.mjs']:
   s=p.read_text();self.assertNotIn('sendBeacon',s);self.assertNotIn('localStorage',s);self.assertNotIn('innerHTML',s)
 def test_unillustrated_records_do_not_get_wrong_project_image(self):
  self.assertEqual(sum(bool(r['image'])for r in self.data['records']),5)
  for r in self.data['records']:
   if r['image']:self.assertTrue((self.root/r['image'].lstrip('/')).exists())
if __name__=='__main__':unittest.main()
