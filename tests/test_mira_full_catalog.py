import importlib.util, pathlib, unittest, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalog_builder',ROOT/'scripts/mira-build-catalog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FullCatalogTests(unittest.TestCase):
 def test_source_and_public_identity(self):
  d=m.load(ROOT);self.assertEqual(618,len(d['projects']));self.assertEqual(618,len({p['sourceRow'] for p in d['projects']}))
 def test_project_images_are_exact_and_covers_are_separate(self):
  d=m.load(ROOT);self.assertEqual(20,sum(bool(p['image']) for p in d['projects']));self.assertTrue(all('price' not in p for p in d['projects']))
 def test_all_detail_pages_exist_and_registration_is_closed(self):
  for p in m.load(ROOT)['projects']:
   text=m.detail(p);self.assertIn('данные покупателей не принимаются',text);self.assertNotIn('Регистрация клиента закрыта',text);self.assertIn('disabled',text);self.assertNotIn('type="email"',text);self.assertIn(m.esc(p['name']),text)
 def test_escape(self):
  self.assertEqual('&lt;script&gt;',m.esc('<script>'));self.assertEqual('&quot;',m.esc('"'))
 def test_botanica_media_matches_exact_phase_and_keeps_source_ids(self):
  rows={p['id']:p for p in m.load(ROOT)['projects']}
  self.assertEqual('Камала',rows['botanica-montazure']['district'])
  self.assertEqual('Пру Джампа',rows['botanica-four-seasons']['district'])
  self.assertEqual('villa',rows['botanika-montazur']['kind'])
  self.assertEqual(rows['botanica-montazure']['gallery'],rows['botanika-montazur']['gallery'])
  self.assertEqual(3,len(rows['botanika-foresta-2']['gallery']))
  self.assertNotIn('gallery',rows['botanica-foresta'])
  self.assertNotIn('gallery',rows['botanica-forestique'])
  self.assertEqual('Zone C1 · фасад',rows['botanica-grand-avenue']['gallery'][0]['caption'])
 def test_aliases_keep_source_records_and_old_detail_links(self):
  data=m.load(ROOT);visible=m.canonical_projects(data['projects']);by_id={p['id']:p for p in data['projects']}
  self.assertEqual(614,len(visible))
  aliases=[p for p in data['projects'] if p.get('canonicalId')];self.assertEqual(4,len(aliases))
  for p in aliases:
   canonical=by_id[p['canonicalId']];self.assertIn(p['id'],canonical['aliases'])
   text=(ROOT/'mira/catalog/projects'/p['id']/'index.html').read_text()
   self.assertIn('data-add="'+canonical['id']+'"',text)
   self.assertNotIn('data-add="'+p['id']+'"',text)
 def test_old_demo_is_still_45(self):
  self.assertEqual(45,len(json.loads((ROOT/'mira/data/catalog.json').read_text())['projects']))
if __name__=='__main__':unittest.main()
