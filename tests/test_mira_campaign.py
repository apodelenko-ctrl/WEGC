import importlib.util,pathlib,unittest
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('campaign',ROOT/'scripts/mira-build-campaign.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tags(HTMLParser):
 def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
class CampaignTests(unittest.TestCase):
 def test_three_distinct_routes(self):self.assertEqual({'go','practical','corporate'},set(m.VARIANTS));self.assertEqual(3,len({v['title'] for v in m.VARIANTS.values()}))
 def test_all_documents_and_catalogue_linked(self):
  for v in m.VARIANTS.values():
   s=m.build_page(v)
   for path in ['/mira/documents/','/mira/catalog/','/mira/documents/agency-agreement.html']:self.assertIn(path,s)
 def test_no_personal_data_fields_or_external_submissions(self):
  for v in m.VARIANTS.values():
   tags=Tags(m.build_page(v)).tags
   self.assertFalse(any(t=='input' for t,a in tags));self.assertFalse(any(t=='form' and a.get('action') for t,a in tags))
   self.assertTrue(any(t=='fieldset' and 'disabled' in a for t,a in tags))
 def test_source_boundary_and_bali(self):
  for v in m.VARIANTS.values():
   s=m.build_page(v);self.assertIn('Первый рынок нашего агентского предложения — Пхукет',s);self.assertIn('Регистрация покупателей сейчас выключена',s);self.assertIn('данные покупателей здесь не принимаются',s);self.assertIn('переговорные проекты',s)
 def test_unique_ids(self):
  for v in m.VARIANTS.values():
   ids=[a['id'] for t,a in Tags(m.build_page(v)).tags if 'id' in a];self.assertEqual(len(ids),len(set(ids)))
 def test_scripts_are_local_and_light(self):
  js=(ROOT/'mira/campaign/campaign.mjs').read_text();self.assertNotIn('fetch(',js);self.assertNotIn('localStorage',js);self.assertIn('prefers-reduced-motion',js);self.assertLess(len(js.encode()),6000)
 def test_previous_designs_preserved(self):
  for p in ['mira/design/index.html','mira/agency/index.html','mira/marketplace-design.html']:self.assertTrue((ROOT/p).is_file())
if __name__=='__main__':unittest.main()
