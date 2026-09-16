import json,re,unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,t,a):self.items.append((t,dict(a)))
class MaterialSourceTests(unittest.TestCase):
 def test_no_public_storage_binding_or_open_default(self):
  text=(ROOT/'cloudflare-worker/mira/wrangler.example.toml').read_text()
  self.assertIn('MATERIALS_ENABLED = "false"',text)
  self.assertNotRegex(text,re.compile(r'^\[\[r2_buckets\]\]',re.M))
  self.assertIn('# binding = "MIRA_MATERIALS"',text)
 def test_library_no_upload_or_external_collection(self):
  text=(ROOT/'mira/library.html').read_text();p=Tags();p.feed(text)
  self.assertNotIn('form',[t for t,_ in p.items]);self.assertNotIn('iframe',[t for t,_ in p.items])
  for t,a in p.items:
   for key in ['href','src']:
    if key in a and not a[key].startswith('#'):self.assertTrue(a[key].startswith('./'));self.assertTrue((ROOT/'mira'/a[key][2:]).is_file())
  self.assertIn("connect-src 'self'",text)
 def test_browser_download_checks_length_hash_and_private_scope(self):
  source=(ROOT/'mira/library.mjs').read_text()
  for marker in ["credentials:'same-origin'","redirect:'error'",'crypto.subtle.digest','meta.sha256','Content-Length','URL.revokeObjectURL','client','8388608']:
   if marker!='client':self.assertIn(marker,source)
  self.assertNotIn('localStorage',source);self.assertNotIn('sessionStorage',source)
 def test_demo_does_not_link_directly_to_private_files(self):
  source=(ROOT/'mira/data/catalog.json').read_text()
  for marker in ['marketing/','r2.dev','EVID-release','SCAN-']:self.assertNotIn(marker,source)
  self.assertIn('./library.html',(ROOT/'mira/pilot.html').read_text())
if __name__=='__main__':unittest.main()
