"""Synthetic config checks only. No real account, host, database or credentials."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/mira-server-preflight.py'
spec = importlib.util.spec_from_file_location('mira_preflight', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ACCOUNT = 'a' * 32
DATABASE = '11111111-2222-3333-4444-555555555555'
ORIGIN = 'https://mira.example.test'

def config():
    return {'name': 'mira-synthetic-pilot', 'main': 'worker.mjs', 'account_id': ACCOUNT,
        'compatibility_date': '2025-01-01', 'workers_dev': False, 'preview_urls': False,
        'routes': [{'pattern': 'mira.example.test/mira/api/*', 'zone_name': 'example.test'}],
        'vars': {'APP_ORIGIN': ORIGIN, 'ACCESS_TEAM_DOMAIN': 'https://mira-synthetic.cloudflareaccess.com',
                 'ACCESS_AUDIENCE': 'a' * 64, 'APPLICATIONS_ENABLED': 'false',
                 'MATERIALS_ENABLED': 'false', 'APPLICATION_RATE_LIMIT': '5'},
        'd1_databases': [{'binding': 'MIRA_DB', 'database_name': 'mira-synthetic-db',
                         'database_id': DATABASE, 'migrations_dir': 'migrations'}]}

def check(value, mode='closed-staging'):
    return module.inspect(value, ACCOUNT, DATABASE, ORIGIN, mode)

class PreflightTests(unittest.TestCase):
    def site_config(self):
        c = config()
        c['main'] = 'site-worker.mjs'
        c['vars']['APP_ORIGIN'] = 'https://pilot.example.test'
        c['routes'] = [{'pattern': 'pilot.example.test', 'custom_domain': True}]
        c['assets'] = {'directory': './pilot-assets', 'binding': 'MIRA_ASSETS', 'run_worker_first': True,
                       'html_handling': 'none', 'not_found_handling': 'none'}
        return c

    def site_check(self, c, origin='https://pilot.example.test'):
        return module.inspect(c, ACCOUNT, DATABASE, origin, topology='dedicated-site')

    def test_dedicated_site_requires_explicit_topology(self):
        c = self.site_config()
        self.assertTrue(self.site_check(c)['passed'])
        self.assertFalse(check(c)['passed'])
        self.assertFalse(self.site_check(config())['passed'])

    def test_dedicated_site_rejects_apex_or_unrelated_hostname(self):
        for host in ['example.test', 'www.example.test', '*.example.test', 'pilot.example.test/*']:
            c = self.site_config()
            c['routes'][0]['pattern'] = host
            c['vars']['APP_ORIGIN'] = 'https://' + host
            self.assertFalse(self.site_check(c, 'https://' + host)['passed'])

    def test_assets_cannot_skip_auth_or_expose_repository(self):
        for key, value in [('run_worker_first', False), ('run_worker_first', ['/mira/api/*']),
                           ('directory', '../..'), ('not_found_handling', 'single-page-application'),
                           ('html_handling', 'auto-trailing-slash')]:
            c = self.site_config()
            c['assets'][key] = value
            self.assertFalse(self.site_check(c)['passed'])

    def test_valid_closed_config_is_not_production_ready(self):
        r = check(config()); self.assertTrue(r['passed']); self.assertFalse(r['production_ready'])
        self.assertFalse(r['remote_access_verified']); self.assertFalse(r['live_signup_verified'])

    def test_existing_resources_and_wrong_account_rejected(self):
        for name in ['charter-chat', 'ccapital-forms-proxy', 'ccapital-control-tower', 'herd-lab-bot']:
            with self.subTest(name=name):
                c = config(); c['name'] = name; self.assertFalse(check(c)['passed'])
        c = config(); c['account_id'] = 'b' * 32; self.assertFalse(check(c)['passed'])
        for field, value in [('database_name', 'charter_leads'), ('binding', 'CONV'), ('database_id', 'different')]:
            c = config(); c['d1_databases'][0][field] = value; self.assertFalse(check(c)['passed'])

    def test_broad_or_unrelated_route_rejected(self):
        for pattern in ['mira.example.test/*', '*.example.test/mira/api/*', 'unrelated.test/mira/api/*',
                        'mira.example.test/cdn-cgi/*', 'mira.example.test/mira/*']:
            with self.subTest(pattern=pattern):
                c = config(); c['routes'][0]['pattern'] = pattern; self.assertFalse(check(c)['passed'])

    def test_unknown_bindings_secrets_and_environments_rejected_without_values(self):
        marker = 'SYNTHETIC-DO-NOT-PRINT'
        for key in ['env', 'services', 'kv_namespaces', 'unsafe', 'build', 'assets']:
            c = config(); c[key] = marker; r = check(c)
            self.assertFalse(r['passed']); self.assertNotIn(marker, json.dumps(r))
        c = config(); c['vars']['BOT_TOKEN'] = marker; r = check(c)
        self.assertFalse(r['passed']); self.assertNotIn(marker, json.dumps(r))

    def test_implicit_preview_and_insecure_origin_rejected(self):
        for field in ['workers_dev', 'preview_urls']:
            c = config(); c.pop(field); self.assertFalse(check(c)['passed'])
            c = config(); c[field] = True; self.assertFalse(check(c)['passed'])
        for origin in ['http://mira.example.test', ORIGIN + '/', ORIGIN + '/mira',
                       'https://name:password@mira.example.test', ORIGIN + '?token=private']:
            c = config(); c['vars']['APP_ORIGIN'] = origin; self.assertFalse(check(c)['passed'])

    def test_identity_placeholder_and_future_compatibility_rejected(self):
        for field, value in [('ACCESS_AUDIENCE', ''), ('ACCESS_AUDIENCE', 'REPLACE_ME'),
                             ('ACCESS_TEAM_DOMAIN', 'https://evil.test')]:
            c = config(); c['vars'][field] = value; self.assertFalse(check(c)['passed'])
        c = config(); c['compatibility_date'] = '2999-01-01'; self.assertFalse(check(c)['passed'])

    def test_second_database_and_remote_binding_override_rejected(self):
        c = config(); c['d1_databases'].append(copy.deepcopy(c['d1_databases'][0])); self.assertFalse(check(c)['passed'])
        c = config(); c['d1_databases'][0]['preview_database_id'] = DATABASE; self.assertFalse(check(c)['passed'])

    def test_intake_requires_explicit_mode_and_privacy_configuration(self):
        c = config(); c['vars']['APPLICATIONS_ENABLED'] = 'true'; self.assertFalse(check(c)['passed'])
        self.assertFalse(check(c, 'intake-config')['passed'])
        c['vars'].update(PRIVACY_VERSION='reviewed-v1', PRIVACY_NOTICE_URL=ORIGIN+'/privacy')
        r = check(c, 'intake-config'); self.assertTrue(r['passed']); self.assertFalse(r['production_ready'])
        c['vars']['PRIVACY_NOTICE_URL'] = 'https://evil.test/privacy'; self.assertFalse(check(c, 'intake-config')['passed'])

    def test_quota_and_material_delivery_have_separate_checks(self):
        for value in ['0', '-1', '1001', 'not-a-number', '5.5']:
            c = config(); c['vars']['APPLICATION_RATE_LIMIT'] = value; self.assertFalse(check(c)['passed'])
        c = config(); c['vars']['MATERIALS_ENABLED'] = 'true'; self.assertFalse(check(c)['passed'])
        c = config(); c['r2_buckets'] = [{'binding': 'MIRA_MATERIALS', 'bucket_name': 'mira-synthetic-materials'}]
        self.assertTrue(check(c)['passed'])
        c['r2_buckets'][0]['bucket_name'] = 'existing-herd-bucket'; self.assertFalse(check(c)['passed'])

    def test_cli_does_not_print_invalid_toml_or_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.toml'; marker = 'SYNTHETIC-DO-NOT-PRINT'
            path.write_text('token = "' + marker + '\n')
            r = subprocess.run([sys.executable, str(SCRIPT), '--config', str(path),
                '--expected-account-id', ACCOUNT, '--expected-database-id', DATABASE, '--expected-origin', ORIGIN],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2); self.assertNotIn(marker, r.stdout + r.stderr)
            self.assertEqual(json.loads(r.stdout)['error'], 'config_missing_invalid_or_oversized')

if __name__ == '__main__':
    unittest.main()
