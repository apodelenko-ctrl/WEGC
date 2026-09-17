"""Public legal package integrity, not a certification of legal compliance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'mira/documents'

class DocumentPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT/'scripts/mira-build-documents.py')], check=True, capture_output=True)
        cls.manifest = json.loads((DOCS/'manifest.json').read_text())
        cls.agreement = (DOCS/'source/agency-agreement.md').read_text()

    def test_nine_documents_not_an_active_offer(self):
        self.assertEqual(len(self.manifest['documents']), 9)
        self.assertFalse(self.manifest['owner_approved'])
        self.assertFalse(self.manifest['acceptance_enabled'])
        self.assertTrue(all(not d['effective'] for d in self.manifest['documents']))

    def test_framework_parts_are_complete(self):
        parts = sorted((DOCS/'source/agreement-parts').glob('*.md'))
        self.assertEqual(len(parts), 4)
        self.assertEqual(self.agreement, ''.join(p.read_text() for p in parts))
        self.assertGreater(len(self.agreement.split()), 5000)
        self.assertEqual(len(re.findall(r'^## \d+\.',self.agreement,re.M)), 19)
        self.assertEqual(len(re.findall(r'^## Приложение \d+\.',self.agreement,re.M)), 5)

    def test_sources_are_hashed_and_each_html_exists(self):
        for d in self.manifest['documents']:
            with self.subTest(d=d['id']):
                raw = (DOCS/d['source']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),d['source_sha256'])
                text=(DOCS/d['html']).read_text()
                self.assertIn('Content-Security-Policy',text)
                self.assertNotIn('<form',text)
                self.assertIn(d['pdf'],text)

    def test_no_fabricated_operator_requisites_or_rate(self):
        self.assertIn('UEN [подтвердить',self.agreement)
        self.assertIn('не применяются автоматически',self.agreement)
        self.assertNotRegex(self.agreement,r'GB[0-9]{2}[A-Z]{4}')
        self.assertNotIn('mailto:',self.agreement)
        self.assertIn('неопределённый срок',self.agreement)

    def test_data_localization_and_separate_consents(self):
        self.assertIn('части 5 статьи 18',self.agreement)
        self.assertIn('Согласие на передачу не считается',self.agreement)
        self.assertIn('Согласие оформляется отдельно',self.agreement)
        self.assertIn('не объявляется обезличенным',self.agreement)
        privacy=(DOCS/'source/privacy.md').read_text()
        self.assertIn('IP-адресов',privacy)
        self.assertIn('первичный',privacy.lower())
        marketing=(DOCS/'source/marketing-consent.md').read_text()
        self.assertIn('не условие сотрудничества',marketing)

    def test_sources_page_preserves_primary_law_links(self):
        text=(DOCS/'sources.html').read_text()
        self.assertIn('https://npd.nalog.ru/faq/',text)
        self.assertIn('cons_doc_LAW_61801',text)
        self.assertIn('полный скачиваемый документ',text)
        self.assertNotIn('drive.google.com',text)

if __name__=='__main__':
    unittest.main()
