import importlib.util, pathlib, unittest, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalog_builder',ROOT/'scripts/mira-build-catalog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FullCatalogTests(unittest.TestCase):
 def test_source_and_public_identity(self):
  d=m.load(ROOT);self.assertEqual(618,len(d['projects']));self.assertEqual(618,len({p['sourceRow'] for p in d['projects']}))
 def test_project_images_are_exact_and_covers_are_separate(self):
  d=m.load(ROOT);self.assertEqual(11,sum(bool(p['image']) for p in d['projects']));self.assertTrue(all('price' not in p for p in d['projects']))
 def test_all_detail_pages_exist_and_registration_is_closed(self):
  for p in m.load(ROOT)['projects']:
   text=m.detail(p);self.assertIn('данные покупателей не принимаются',text);self.assertNotIn('Регистрация клиента закрыта',text);self.assertIn('disabled',text);self.assertNotIn('type="email"',text);self.assertIn(m.esc(p['name']),text)
 def test_escape(self):
  self.assertEqual('&lt;script&gt;',m.esc('<script>'));self.assertEqual('&quot;',m.esc('"'))
 def test_old_demo_is_still_45(self):
  self.assertEqual(45,len(json.loads((ROOT/'mira/data/catalog.json').read_text())['projects']))
if __name__=='__main__':unittest.main()
