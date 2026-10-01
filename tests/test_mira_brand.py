import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('brand', Path(__file__).resolve().parents[1]/'scripts/mira-wire-brand.py')
brand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand)

class BrandTests(unittest.TestCase):
    def test_variants_preserve_links_and_subtitles(self):
        for body in ['МИРА','МИРА↗','МИРА<i>↗</i>','МИРА<span class="brand-mark" aria-hidden="true">↗</span>','МИРА<span>Кабинет агентства</span>']:
            page = '<head></head><a class="brand" href="/mira/catalog/" aria-label="МИРА — каталог">'+body+'</a>'
            out = brand.wire(page)
            self.assertEqual(out.count('↗'), 1)
            self.assertIn('href="/mira/catalog/"',out)
            self.assertIn('aria-label="МИРА — каталог"',out)
            if 'Кабинет' in body: self.assertIn('<span>Кабинет агентства</span>',out)
            self.assertEqual(out,brand.wire(out))
    def test_private_library_relative_stylesheet(self):
        text='<head></head><a class="brand" href="./pilot.html">МИРА</a>'
        out=brand.wire(text, relative=True)
        self.assertIn('href="./brand.css"',out)
        self.assertEqual(out,brand.wire(out,relative=True))
    def test_go_header_is_idempotent_and_does_not_restyle_footer(self):
        link='<a class="brand" href="/mira/go/">МИРА<span>Ваш клиент. Ваш бренд.</span></a>'
        page='<header>'+link+'</header><footer>'+link+'</footer>'
        out=brand.wire_go(brand.wire(page))
        self.assertEqual(out,brand.wire_go(brand.wire(out)))
        self.assertEqual(out.count('mira-marketplace-brand'),1)
        self.assertNotIn('mira-marketplace-brand',out.split('<footer>')[1])
    def test_unrelated_brand_is_untouched(self):
        text='<head></head><a class="brand" href="/">WEGC</a><p>МИРА</p>'
        self.assertEqual(text,brand.wire(text))

if __name__=='__main__': unittest.main()
