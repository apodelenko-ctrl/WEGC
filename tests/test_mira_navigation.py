import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('navigation', ROOT/'scripts/mira-wire-navigation.py')
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)

class NavigationTests(unittest.TestCase):
    def test_repeated_public_build_preserves_page_body_and_scripts(self):
        for path, old in [('index.html', '<nav>old</nav><header class="hero">hero</header>'),
                          ('catalog/projects/example/index.html', '<header>old</header>')]:
            page = '<html><head></head><body>'+old+'<main id="main">KEEP BODY</main><script src="engine.mjs"></script></body></html>'
            result = nav.wire(page, path)
            self.assertEqual(result, nav.wire(result, path))
            self.assertIn('<main id="main">KEEP BODY</main>', result)
            self.assertIn('<script src="engine.mjs"></script>', result)
            self.assertEqual(result.count('<!-- mira-navigation -->'), 1)
            if path == 'index.html': self.assertIn('<header class="hero">hero</header>', result)

    def test_document_navigation_cannot_return_to_legacy_demos(self):
        shell = nav.navigation('documents/payment-support.html')
        for target in ['/mira/', '/mira/go/', '/mira/catalog/', '/mira/documents/', '/mira/#payments']:
            self.assertIn('href="'+target+'"', shell)
        for legacy in ['marketplace-design.html', 'marketplace.html', '/mira/agency/']:
            self.assertNotIn(legacy, shell)

    def test_missing_header_fails_without_replacing_unrelated_content(self):
        with self.assertRaises(ValueError): nav.wire('<main>keep</main>', 'go/index.html')

if __name__ == '__main__': unittest.main()
