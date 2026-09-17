import unittest,importlib.util,json,tempfile,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=module('expansion_under_test',ROOT/'scripts/mira-build-market-expansion.py')
MEDIA=module('media_under_test',ROOT/'scripts/mira-market-media.py')
class ExpansionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.source=json.loads((ROOT/M.SOURCE).read_text());cls.projects=cls.source['projects']
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name)
  for name in [M.SOURCE,'scripts/mira-build-catalog.py','mira/catalog/data.json']:
   p=self.r/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,p)
  (self.r/'mira/catalog/index.html').write_text('<html><head></head><body><header></header><main>Phuket</main></body></html>')
 def tearDown(self):self.temp.cleanup()
 def test_counts(self):
  r=M.build(self.r);self.assertEqual(r['combinedProjects'],648);self.assertEqual(r['newDetailPages'],30)
  for market in ['bali','dubai']:self.assertEqual((self.r/f'mira/catalog/{market}/index.html').read_text().count('class="project-card"'),15)
 def test_phuket_bytes_unchanged(self):
  p=self.r/'mira/catalog/data.json';b=p.read_bytes();M.build(self.r);self.assertEqual(p.read_bytes(),b)
 def test_no_funnel_or_auth_mutation(self):
  for f in ['mira/go/index.html','cloudflare-worker/mira/worker.mjs','project-bible/mira/WORK-STATUS.md']:
   p=self.r/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('DO NOT TOUCH')
  M.build(self.r)
  for f in ['mira/go/index.html','cloudflare-worker/mira/worker.mjs','project-bible/mira/WORK-STATUS.md']:self.assertEqual((self.r/f).read_text(),'DO NOT TOUCH')
 def test_idempotent(self):
  M.build(self.r);before=(self.r/'mira/catalog/index.html').read_bytes();M.build(self.r);self.assertEqual((self.r/'mira/catalog/index.html').read_bytes(),before);self.assertEqual(before.count(b'data-mira-markets="v1"'),1)
 def test_strict_media_gate(self):
  with self.assertRaises(ValueError):M.build(self.r,require_images=True)
  self.assertFalse((self.r/'mira/catalog/bali/index.html').exists())
 def test_duplicate_ids_rejected(self):
  d=json.loads(json.dumps(self.source));d['projects'][1]['id']=d['projects'][0]['id']
  with self.assertRaises(AssertionError):M.validate(d)
 def test_financial_and_seller_rejected(self):
  for key,val in [('price',1),('roi',1),('legalSeller','unverified'),('commerciallyEnabled',True)]:
   d=json.loads(json.dumps(self.source));d['projects'][0][key]=val
   with self.assertRaises(AssertionError):M.validate(d)
 def test_html_escaping(self):
  M.build(self.r);d=json.loads((self.r/'mira/catalog/markets/data.json').read_text());p=d['projects'][0];p['name']='<script>BAD</script>';self.assertNotIn('<script>BAD</script>',M.card(p));self.assertIn('&lt;script&gt;',M.card(p))
 def test_images_require_review(self):
  p=self.projects[0]
  with self.assertRaises(AssertionError):M.approved_image(self.r,p,{p['id']:{'approvedForPublication':True}})
 def test_wrong_image_hash_rejected(self):
  p=self.projects[0];f=self.r/p['media']['localPath'].lstrip('/');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'x')
  with self.assertRaises(AssertionError):M.approved_image(self.r,p,{p['id']:{'path':p['media']['localPath'],'sha256':'bad','approvedForPublication':True,'visualReviewed':True,'rightsReference':'test'}})
 def test_coverage_limit_is_explicit(self):
  self.assertEqual(sum(bool(p['agencyObservations']) for p in self.projects),28)
  self.assertEqual({p['id'] for p in self.projects if not p['agencyObservations']},{'bali-edem-ii','bali-sunny-aparts-ii'})
 def test_research_not_approval(self):
  for p in self.projects:self.assertFalse(p['commerciallyEnabled']);self.assertIsNone(p['legalSeller']);self.assertFalse(p['media']['approvedForPublication'])
 def test_offline_media_inventory(self):
  result=MEDIA.inventory(self.r,self.r/'private');self.assertEqual(len(result['projects']),30);self.assertEqual(json.loads((self.r/'private/inventory.json').read_text())['directImageURLs'],16)
 def test_unsafe_media_urls(self):
  for u in ['http://example.com/x.jpg','file:///x','https://localhost/x','https://127.0.0.1/x','https://192.168.1.1/x','https://user:pass@example.com/x','https://example.com:444/x']:
   with self.assertRaises(ValueError):MEDIA.safe_url(u)
 def test_parser_no_upscale_or_logo(self):
  p=MEDIA.Images('https://example.com/project/');p.feed('<meta property="og:image" content="/project.webp"><img src="/logo.webp"><img data-original="/facade.jpg" src="/resize/20x/photo.jpg">')
  urls=[x['url'] for x in p.candidates];self.assertIn('https://example.com/facade.jpg',urls);self.assertNotIn('https://example.com/logo.webp',urls);self.assertFalse(any('resize/20x' in x for x in urls));self.assertFalse(any('approvedForPublication' in x for x in p.candidates))
 def test_media_parser_tolerates_boolean_attributes_and_excludes_tracking(self):
  p=MEDIA.Images('https://example.com/project/');p.feed('<a href>Empty</a><img src="https://www.facebook.com/tr?id=1"><img src="/icon.svg"><img data-original="/facade.webp">')
  self.assertEqual([x['url'] for x in p.candidates],['https://example.com/facade.webp'])
 def test_era_redirect_is_not_misrepresented_as_a_primary_source(self):
  M.build(self.r);page=(self.r/'mira/catalog/projects/bali-the-era-by-oxo/index.html').read_text()
  self.assertIn('https://rehouse.ae/ru/project/era',page);self.assertIn('Публикация агентства',page);self.assertNotIn('the-bank',page)
 def test_empty_review_does_not_publish_images(self):
  p=self.r/'review.json';p.write_text('{"items":[]}');self.assertEqual(MEDIA.publish(self.r,p)['copied'],0)
if __name__=='__main__':unittest.main()
