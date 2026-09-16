"""Static boundaries of the owner-review visual preview; no deployment assertion."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json, re, unittest
ROOT=Path(__file__).resolve().parents[1]
class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__();self.items=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.items.append((tag,dict(attrs)))
class DesignPreviewTests(unittest.TestCase):
    def setUp(self):
        self.landing=(ROOT/'mira/design/index.html').read_text()
        self.market=(ROOT/'mira/marketplace-design.html').read_text()
        self.original=(ROOT/'mira/agency/index.html').read_text()
    def test_one_landing_heading_and_named_preview(self):
        self.assertEqual(len(re.findall(r'<h1\b',self.landing)),1)
        self.assertIn('дизайн-превью',self.landing.lower())
        self.assertIn('noindex,nofollow,noarchive',self.landing)
    def test_four_segments_preserved(self):
        pattern=r'data-model="([^"]+)"'
        self.assertEqual(sorted(re.findall(pattern,self.landing)),sorted(re.findall(pattern,self.original)))
    def test_same_qualification_values(self):
        pattern=r'<option value="([^"]*)"'
        self.assertEqual(re.findall(pattern,self.landing),re.findall(pattern,self.original))
        self.assertIn('id="qualification-fields"',self.landing)
        fields=[a for t,a in Tags(self.landing).items if a.get('id')=='qualification-fields']
        self.assertIn('disabled',fields[0])
    def test_no_external_form_or_script(self):
        for text in [self.landing,self.market]:
            for tag,attrs in Tags(text).items:
                if tag=='form':self.assertFalse(attrs.get('action'))
                if tag=='script':self.assertFalse(urlsplit(attrs.get('src','')).netloc)
            self.assertIn("form-action 'none'",text)
            self.assertNotIn('mailto:',text)
            self.assertNotIn('googletagmanager',text)
    def test_all_html_image_files_exist(self):
        for tag,attrs in Tags(self.landing).items:
            if tag in ['img','source']:
                path=attrs.get('src',attrs.get('srcset'))
                self.assertTrue((ROOT/path.lstrip('/')).is_file(),path)
                if tag=='img':self.assertTrue(attrs.get('alt'))
    def test_illustrations_have_exact_catalogue_ids(self):
        js=(ROOT/'mira/design/catalogue-visuals.mjs').read_text()
        ids={p['id'] for p in json.loads((ROOT/'mira/data/catalog.json').read_text())['projects']}
        rows=re.findall(r"'([^']+)': '(/images/[^']+)'",js)
        self.assertEqual(len(rows),5)
        for project,path in rows:
            self.assertIn(project,ids);self.assertTrue((ROOT/path.lstrip('/')).is_file())
        self.assertIn('Архивная визуализация',js)
        self.assertIn('Весь каталог',js)
    def test_uses_original_engine_and_qualification(self):
        self.assertIn('src="./marketplace.mjs"',self.market)
        self.assertIn('src="../agency/agency.mjs"',self.landing)
        self.assertTrue((ROOT/'mira/agency/qualification.mjs').is_file())
    def test_motion_is_optional(self):
        js=(ROOT/'mira/design/motion.mjs').read_text()
        for term in ['prefers-reduced-motion','saveData','document.hidden','pausedByUser','IntersectionObserver']:self.assertIn(term,js)
        self.assertIn('hidden',dict((a.get('id'),a) for t,a in Tags(self.landing).items if a.get('id'))['motion-toggle'])
        for term in ['fetch(', 'XMLHttpRequest', 'sendBeacon(', 'localStorage', 'sessionStorage']:self.assertNotIn(term,js)
    def test_preview_links_are_real_files_or_fragments(self):
        for file,text in [('mira/design/index.html',self.landing),('mira/marketplace-design.html',self.market)]:
            for tag,a in Tags(text).items:
                if tag!='a':continue
                href=a.get('href','');path=urlsplit(href).path
                if not path:continue
                target=ROOT/path.lstrip('/') if path.startswith('/') else (ROOT/file).parent/path
                if href.split('?')[0].split('#')[0].endswith('/'):target=target/'index.html'
                self.assertTrue(target.is_file(),f'{file} -> {href}')
    def test_no_backend_or_commercial_enabling(self):
        self.assertIn('Приём заявок сейчас закрыт',self.landing)
        self.assertIn('не конкретный объект',self.landing.lower())
        self.assertIn('только локальные демо-черновики',self.market)
        css=(ROOT/'mira/design/design.css').read_text()
        self.assertNotIn('@import',css)
        self.assertNotIn('@font-face',css)
if __name__=='__main__':unittest.main()
