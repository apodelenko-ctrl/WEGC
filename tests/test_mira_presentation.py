"""Public first-partner regression: images, routes, truthful copy and closed intake."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import importlib.util, unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('presentation_builder',ROOT/'scripts/mira-build-catalog.py')
build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
class Tags(HTMLParser):
 def __init__(self,text): super().__init__(); self.tags=[];self.feed(text)
 def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))
class PresentationTests(unittest.TestCase):
 def test_every_card_and_detail_has_distinct_labelled_visual(self):
  for p in build.load(ROOT)['projects']:
   for markup in (build.card(p),build.detail(p)):
    tags=Tags(markup).tags;images=[a for t,a in tags if t=='img']
    self.assertEqual(len(images),1);self.assertTrue((ROOT/images[0]['src'].lstrip('/')).is_file())
    self.assertTrue((ROOT/images[0]['data-fallback'].lstrip('/')).is_file())
    self.assertNotIn('Изображение не проверено',markup)
    if not p['image']: self.assertIn('обложка каталога',markup)
 def test_image_priority_and_metadata_ranking(self):
  projects=build.load(ROOT)['projects'];self.assertTrue(all(p['image'] for p in projects[:11]))
  self.assertTrue(all(not p['image'] for p in projects[11:]))
  ranks=[sum(bool(p[k]) for k in ('district','kind','family')) for p in projects[11:]]
  self.assertEqual(ranks,sorted(ranks,reverse=True))
 def test_all_public_links_images_and_fragments_resolve(self):
  pages=[ROOT/'mira/go/index.html',ROOT/'mira/catalog/index.html',ROOT/'mira/catalog/list.html',*sorted((ROOT/'mira/catalog/projects').glob('*/index.html'))]
  for page in pages:
   for tag,attrs in Tags(page.read_text()).tags:
    value=attrs.get('href') or attrs.get('src')
    if not value:continue
    url=urlsplit(value)
    if url.scheme or url.netloc:continue
    target=ROOT/url.path.lstrip('/') if url.path.startswith('/') else page.parent/url.path if url.path else page
    if target.is_dir():target=target/'index.html'
    self.assertTrue(target.is_file(),(page,value))
    if url.fragment:
     self.assertIn(unquote(url.fragment),{a.get('id') for t,a in Tags(target.read_text()).tags},(page,value))
 def test_no_buyer_intake_or_disabled_registration_call_to_action(self):
  for p in build.load(ROOT)['projects']:
   tags=Tags(build.detail(p)).tags
   self.assertFalse(any(t in ('input','form') for t,a in tags))
   self.assertFalse(any(t=='button' and not a.get('data-add') and a.get('id') not in ('shortlist-open','shortlist-close','shortlist-download','shortlist-clear') for t,a in tags))
   self.assertFalse(p['commerciallyEnabled'])
if __name__=='__main__':unittest.main()
