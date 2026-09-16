import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
SALES = ROOT / 'project-bible/mira/sales'

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.tags = []; self.meta = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag); attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs: self.links.append(attrs['href'])
        if tag == 'meta': self.meta.append(attrs)

class AcquisitionTests(unittest.TestCase):
    def test_thirty_complete_numbered_posts(self):
        text = (SALES / 'content/telegram-launch-30.md').read_text()
        parts = re.split(r'^## Пост (\d{2}) — [^\n]+\n', text, flags=re.M)
        self.assertEqual([int(parts[n]) for n in range(1, len(parts), 2)], list(range(1, 31)))
        for body in parts[2::2]:
            self.assertGreater(len(body.strip()), 250)
            self.assertEqual(len(re.findall(r'\]\(https://', body)), 1)
            self.assertNotIn('{{', body)
            self.assertNotRegex(body, r'\d+\s*%|\$\s*\d|₽|฿')
        self.assertIn('not_approved / not_published', text)

    def test_post_links_use_existing_product_routes(self):
        text = (SALES / 'content/telegram-launch-30.md').read_text()
        for link in re.findall(r'\]\((https://[^)]+)\)', text):
            url = urlsplit(link)
            self.assertEqual(url.netloc, 'wegc.fund')
            target = ROOT / url.path.lstrip('/')
            if url.path.endswith('/'): target /= 'index.html'
            self.assertTrue(target.is_file(), str(target))
            if url.query:
                self.assertIn(parse_qs(url.query)['view'][0], ['catalog','markets','clients','payments','onboarding','profile','application'])

    def test_webinar_is_programme_not_fake_registration(self):
        text = (ROOT / 'mira/webinar.html').read_text()
        parser = Links(); parser.feed(text)
        self.assertNotIn('form', parser.tags)
        self.assertNotIn('script', parser.tags)
        self.assertIn('Дата и регистрация ещё не открыты', text)
        self.assertIn("form-action 'none'", text)
        self.assertIn('lang="ru"', text)
        for href in parser.links:
            if href.startswith('#'): continue
            self.assertTrue(href.startswith('/mira/'))
            path = urlsplit(href).path
            target = ROOT / path.lstrip('/')
            if path.endswith('/'): target /= 'index.html'
            self.assertTrue(target.is_file(), path)

    def test_activation_and_webinar_controls_remain_explicit(self):
        kit = (SALES / 'AGENCY-ACTIVATION-KIT.md').read_text()
        sequence = (SALES / 'WEBINAR-LAUNCH-SEQUENCE.md').read_text()
        self.assertIn('Hold / entity resolution', kit)
        self.assertIn('demo_ready', kit)
        self.assertIn('marketplace pilot-ready', kit)
        self.assertIn('opt-out', kit)
        self.assertIn('starts_at', sequence)
        self.assertIn('не подтверждены', sequence)
        self.assertIn('unknown', sequence)

if __name__ == '__main__':
    unittest.main()
