"""Entirely synthetic network fixtures. No network, VPN or real signup measured."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

p = Path(__file__).resolve().parents[1] / 'scripts/mira-access-check.py'
spec = importlib.util.spec_from_file_location('network_check', p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ACCESS = 'https://synthetic-test.cloudflareaccess.com'
BODY = b'SYNTHETIC' * 4096
SPECS = [{'path': '/mira/go/', 'bytes': len(BODY), 'sha256': hashlib.sha256(BODY).hexdigest()}]


def response(status, body=b'', headers=None):
    return {'status': status, 'body': body, 'headers': headers or {}, 'elapsed_ms': 1}


def good(url):
    if url.startswith(m.PUBLIC): return response(200, BODY)
    if url.startswith(m.PILOT):
        return response(302, headers={'Location': ACCESS + '/cdn-cgi/access/login/secret?token=DO_NOT_SAVE',
                                      'Set-Cookie': 'SYNTHETIC_COOKIE_SECRET'})
    if url == ACCESS + '/cdn-cgi/access/certs':
        return response(200, json.dumps({'keys': [{'kty': 'RSA', 'kid': 'synthetic', 'n': 'x', 'e': 'AQAB'}]}).encode())
    raise AssertionError('Unexpected URL')


class AccessCheckTests(unittest.TestCase):
    def test_success_is_not_signup_or_geography_proof(self):
        r = m.run(SPECS, ACCESS, 'RU-home', 'off', good)
        self.assertTrue(r['prelogin_checks_passed'])
        self.assertTrue(r['target_no_vpn_condition_observed'])
        self.assertFalse(r['live_signup_verified']); self.assertFalse(r['production_ready'])
        self.assertFalse(r['geography_independently_verified'])

    def test_on_or_unknown_vpn_never_closes_no_vpn_condition(self):
        for v in ('on', 'unknown'):
            self.assertFalse(m.run(SPECS, ACCESS, 'unknown', v, good)['target_no_vpn_condition_observed'])

    def test_no_cookies_redirect_query_or_identity_persisted(self):
        text = json.dumps(m.run(SPECS, ACCESS, 'test', 'off', good))
        for secret in ('DO_NOT_SAVE', 'SYNTHETIC_COOKIE_SECRET', '/secret', 'token='):
            self.assertNotIn(secret, text)

    def test_partial_asset_fails_even_with_200(self):
        r = m.run(SPECS, ACCESS, 'test', 'off', lambda u: response(200, BODY[:16384]) if u.startswith(m.PUBLIC) else good(u))
        self.assertFalse(r['prelogin_checks_passed']); self.assertFalse(r['checks'][0]['sha256_matches'])

    def test_wrong_login_host_is_not_followed_or_accepted(self):
        calls = []
        def fetch(u):
            calls.append(u)
            return response(302, headers={'Location': 'https://evil.test/?secret=PRIVATE'}) if u.startswith(m.PILOT) else good(u)
        r = m.run(SPECS, ACCESS, 'test', 'off', fetch)
        self.assertFalse(r['prelogin_checks_passed'])
        self.assertTrue(all('evil.test' not in u for u in calls)); self.assertNotIn('PRIVATE', json.dumps(r))

    def test_worker_401_is_not_a_working_access_login(self):
        r = m.run(SPECS, ACCESS, 'test', 'off', lambda u: response(401, b'{"error":"identity_required"}') if u.startswith(m.PILOT) else good(u))
        self.assertFalse(r['prelogin_checks_passed'])

    def test_public_session_200_fails(self):
        r = m.run(SPECS, ACCESS, 'test', 'off', lambda u: response(200, b'{}') if u.startswith(m.PILOT) else good(u))
        self.assertFalse(r['prelogin_checks_passed'])

    def test_certificates_must_be_rsa_shape_not_html(self):
        for body in (b'<html>login</html>', b'{"keys":[]}', b'[]'):
            r = m.run(SPECS, ACCESS, 'test', 'off', lambda u: response(200, body) if u.endswith('/certs') else good(u))
            self.assertFalse(r['prelogin_checks_passed'])

    def test_rejects_non_https_and_credentials_in_issuer(self):
        for bad in ('http://x.cloudflareaccess.com', 'https://x.cloudflareaccess.com/',
                    'https://x.cloudflareaccess.com:443', 'https://x.cloudflareaccess.com.evil.test',
                    'https://person:secret@x.cloudflareaccess.com'):
            with self.assertRaises(ValueError): m.validate_access_origin(bad)

    def test_bad_label_or_asset_is_rejected_before_request(self):
        for label in ('someone@example.test', '../escape', 'name with spaces'):
            with self.assertRaises(ValueError): m.run(SPECS, ACCESS, label, 'off', good)
        for path in ('//evil.test/x', '/mira/../private', '/mira/api/session?secret=x', '/private'):
            with self.assertRaises(ValueError): m.run([{**SPECS[0], 'path': path}], ACCESS, 'test', 'off', good)

    def test_dns_failure_is_not_confused_with_existing_plan_absence(self):
        r = m.run(SPECS, ACCESS, 'test', 'off', lambda u: {'status': None, 'body': b'', 'headers': {}, 'error': 'dns_error'})
        self.assertFalse(r['prelogin_checks_passed'])
        self.assertNotIn('not_enabled', json.dumps(r))
