import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch
import route_check as c


class RouteTests(unittest.TestCase):
    def evaluate(self, name, status=200, body='', headers=None):
        route = next(r for r in c.ROUTES if r[0] == name)
        return c.evaluate(route, status, headers or {'Content-Type': 'text/html', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'}, body.encode())

    def test_closed_form_is_failure(self):
        self.assertEqual(self.evaluate('intake', 503, '{"error":"intake_disabled"}')['status'], 'FAIL')

    def test_valid_access_redirect(self):
        r = self.evaluate('research', 302, headers={'Location': 'https://sample.cloudflareaccess.com/cdn-cgi/access/login/path?token=PRIVATE'})
        self.assertEqual(r['status'], 'PASS')
        self.assertNotIn('PRIVATE', str(r))

    def test_false_auth_redirect_is_failure(self):
        for url in ['https://cloudflareaccess.com.attacker.test/cdn-cgi/access/login/x', 'https://example.test/login', 'http://sample.cloudflareaccess.com/cdn-cgi/access/login/x']:
            self.assertEqual(self.evaluate('research', 302, headers={'Location': url})['status'], 'FAIL')

    def test_public_operator_page_is_failure(self):
        self.assertEqual(self.evaluate('operator_inbox', 200, '<html>private</html>')['status'], 'FAIL')

    def test_missing_intake_link_is_failure(self):
        self.assertEqual(self.evaluate('agency_access', body='<html lang="ru">invite only</html>')['status'], 'FAIL')
        self.assertEqual(self.evaluate('agency_access', body='<html lang="ru"><a href="'+c.INTAKE+'">Подать</a></html>')['status'], 'PASS')

    def test_paused_or_prechecked_form_is_failure(self):
        html = '<html lang="ru"><form id="request" data-paused="false" data-consent="test"><input name="consent" type="checkbox" required><div data-action="mira_intake" data-sitekey="synthetic"></div><a href="'+c.INTAKE+'privacy">Privacy</a></form></html>'
        self.assertEqual(self.evaluate('intake', body=html)['status'], 'PASS')
        for changed in [html.replace('data-paused="false"', 'data-paused="true"'), html.replace('required>', 'required checked>'), html.replace('<form ', '<form hidden ')]:
            self.assertEqual(self.evaluate('intake', body=changed)['status'], 'FAIL')

    def test_private_body_not_returned(self):
        result = self.evaluate('research', 403, 'private-data-not-for-report')
        self.assertNotIn('private-data', str(result))

    def test_non_allowlisted_route_rejected_without_network(self):
        with patch('subprocess.run') as run:
            with self.assertRaises(ValueError):
                c.probe(('submit', c.INTAKE+'submit', 'form'))
            run.assert_not_called()

    def test_transport_timeout_is_unverified_not_success(self):
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('curl', 30)):
            self.assertEqual(c.probe(c.ROUTES[0])['status'], 'UNVERIFIED')

    def test_transport_error_does_not_publish_stderr(self):
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 7, '', 'private details')):
            result = c.probe(c.ROUTES[0])
            self.assertEqual(result['status'], 'UNVERIFIED')
            self.assertNotIn('private', str(result))

    def test_get_only_and_proxy_header_selection(self):
        def fake(command, **kwargs):
            self.assertEqual(command[:2], ['curl', '--disable'])
            self.assertEqual(command[command.index('--request')+1], 'GET')
            for forbidden in ['--location', '-L', '--data', '--cookie', '--user']:
                self.assertNotIn(forbidden, command)
            Path(command[command.index('--dump-header')+1]).write_text('HTTP/1.1 200 OK\n\nHTTP/2 403 Forbidden\nContent-Type: application/json\n\n')
            Path(command[command.index('--output')+1]).write_text('denied')
            return subprocess.CompletedProcess(command, 0, '403', '')
        with patch('subprocess.run', side_effect=fake):
            result = c.probe(next(r for r in c.ROUTES if r[0] == 'research'))
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['http_status'], 403)


if __name__ == '__main__':
    unittest.main()
