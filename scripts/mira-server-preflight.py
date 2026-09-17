#!/usr/bin/env python3
"""Read-only audit of an explicit MIRA Wrangler TOML. No network, deployment or secret values.

Supports a single-environment API route or an explicitly selected dedicated pilot hostname.
A passing config audit is NOT an authorization, Cloudflare connectivity test,
legal opinion, successful signup or proof that the named DB is actually isolated.
Requires Python 3.11+ (tomllib).
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import urlsplit

MAX_CONFIG_BYTES = 65536
SAFE_TOP = {'name', 'main', 'account_id', 'compatibility_date', 'workers_dev',
            'preview_urls', 'routes', 'vars', 'd1_databases', 'r2_buckets'}
SAFE_VARS = {'APP_ORIGIN', 'ACCESS_TEAM_DOMAIN', 'ACCESS_AUDIENCE', 'APPLICATIONS_ENABLED',
             'MATERIALS_ENABLED', 'APPLICATION_RATE_LIMIT', 'PRIVACY_VERSION', 'PRIVACY_NOTICE_URL'}
HEX32 = re.compile(r'[0-9a-fA-F]{32}')
UUID = re.compile(r'[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}')
MIRA_NAME = re.compile(r'mira-[a-z0-9][a-z0-9-]{0,50}')


def https_origin(value: object) -> bool:
    if not isinstance(value, str) or len(value) > 253:
        return False
    try:
        u = urlsplit(value)
        return (u.scheme == 'https' and bool(u.hostname) and not u.username and not u.password
                and not u.query and not u.fragment and not u.path and u.port in (None, 443)
                and not any(c.isspace() for c in value))
    except ValueError:
        return False


def configured(value: object) -> bool:
    return (isinstance(value, str) and 1 <= len(value.strip()) <= 256
            and not any(c in value for c in '\r\n\x00')
            and not re.search(r'replace|placeholder|your[_ -]|example|<|>', value, re.I))


def inspect(config: dict, expected_account: str, expected_database: str,
            expected_origin: str, mode: str = 'closed-staging', topology: str = 'api-route') -> dict:
    report = {'scope': 'offline_single_environment_configuration_only', 'mode': mode,
              'topology': topology,
              'passed': False, 'live_signup_verified': False, 'production_ready': False,
              'remote_access_verified': False, 'checks': []}
    def check(name: str, passed: object, remedy: str) -> None:
        report['checks'].append({'name': name, 'passed': bool(passed),
                                 'remedy': None if passed else remedy})
    if not isinstance(config, dict):
        check('toml_document', False, 'Use a TOML mapping.'); return report
    vars_ = config.get('vars') if isinstance(config.get('vars'), dict) else {}
    site = topology == 'dedicated-site'
    check('supported_topology', topology in ('api-route', 'dedicated-site'), 'Choose api-route or dedicated-site explicitly.')
    check('supported_scope', not (set(config) - (SAFE_TOP | ({'assets'} if site else set()))),
          'Review unsupported keys/bindings or named environments separately; this checker must not guess inheritance.')
    check('no_plaintext_secrets', not (set(vars_) - SAFE_VARS),
          'Do not put tokens, passwords, bot keys or unrelated variables in the MIRA TOML. Use approved secret storage.')
    check('explicit_account_match', bool(HEX32.fullmatch(expected_account or ''))
          and config.get('account_id') == expected_account,
          'Copy the account ID from the authorized local account inspection and supply it explicitly.')
    check('dedicated_worker_name', bool(MIRA_NAME.fullmatch(str(config.get('name', '')))),
          'Use a new mira-* Worker, not an existing Charter, CCapital or Herd Worker.')
    check('known_entrypoint', config.get('main') == ('site-worker.mjs' if site else 'worker.mjs'),
          'Use the reviewed entrypoint matching the explicitly selected topology.')
    try:
        date = dt.date.fromisoformat(str(config.get('compatibility_date', '')))
        valid_date = dt.date(2024, 1, 1) <= date <= dt.datetime.now(dt.timezone.utc).date()
    except ValueError:
        valid_date = False
    check('compatibility_date', valid_date, 'Use an explicitly reviewed valid compatibility date, not a future date.')
    check('no_unprotected_preview_host', config.get('workers_dev') is False and config.get('preview_urls') is False,
          'Explicitly disable workers_dev and preview_urls; configure the approved protected route separately.')
    origin = vars_.get('APP_ORIGIN')
    check('exact_origin', https_origin(origin) and origin == expected_origin,
          'Set the exact approved HTTPS origin, without a path, credentials or wildcard.')
    routes = config.get('routes')
    route_ok = False
    if isinstance(routes, list) and len(routes) == 1 and isinstance(routes[0], dict) and https_origin(expected_origin):
        route = routes[0]; host = urlsplit(expected_origin).hostname
        zone = route.get('zone_name')
        if site:
            route_ok = (set(route) == {'pattern', 'custom_domain'} and route.get('pattern') == host
                        and route.get('custom_domain') is True and host.startswith('pilot.')
                        and bool(re.fullmatch(r'pilot\.[a-z0-9-]+(?:\.[a-z0-9-]+)+', host)))
        else:
            route_ok = (set(route) == {'pattern', 'zone_name'} and route.get('pattern') == host + '/mira/api/*'
                        and isinstance(zone, str) and bool(re.fullmatch(r'[a-z0-9.-]+', zone))
                        and (zone == host or host.endswith('.' + zone)))
    check('dedicated_site_route' if site else 'api_only_route', route_ok,
          'Use one explicitly approved unused pilot.* custom domain for dedicated-site, or the exact /mira/api/* route for api-route. Never replace the public apex.')
    if site:
        check('bounded_worker_first_assets', config.get('assets') == {
            'directory': './pilot-assets', 'binding': 'MIRA_ASSETS', 'run_worker_first': True,
            'html_handling': 'none', 'not_found_handling': 'none'},
            'Package only the reviewed pilot assets and always run the Worker before serving assets; do not expose the repository or use SPA/HTML fallbacks.')
    check('access_issuer', bool(re.fullmatch(r'https://[a-z0-9-]+\.cloudflareaccess\.com', str(vars_.get('ACCESS_TEAM_DOMAIN', '')))),
          'Use the actual Access team HTTPS origin from the approved Access application.')
    check('access_audience', configured(vars_.get('ACCESS_AUDIENCE')),
          'Set the actual Access application audience. A TOML value does not prove that its policies are correct.')
    d1 = config.get('d1_databases')
    db_ok = False
    if isinstance(d1, list) and len(d1) == 1 and isinstance(d1[0], dict):
        db = d1[0]
        db_ok = (set(db) == {'binding', 'database_name', 'database_id', 'migrations_dir'}
                 and db.get('binding') == 'MIRA_DB'
                 and bool(MIRA_NAME.fullmatch(str(db.get('database_name', ''))))
                 and bool(UUID.fullmatch(expected_database or ''))
                 and db.get('database_id') == expected_database and db.get('migrations_dir') == 'migrations')
    check('dedicated_database_binding', db_ok,
          'Use exactly one new MIRA_DB with the explicitly confirmed new database ID. Check its actual account/contents before migration.')
    try:
        rate = int(vars_.get('APPLICATION_RATE_LIMIT', '5'))
        quota_ok = 1 <= rate <= 1000 and str(rate) == str(vars_.get('APPLICATION_RATE_LIMIT', '5'))
    except (TypeError, ValueError):
        quota_ok = False
    check('intake_quota', quota_ok, 'Set an integer application quota supported by the Worker.')
    expected_flag = 'false' if mode == 'closed-staging' else 'true'
    check('intake_mode', vars_.get('APPLICATIONS_ENABLED') == expected_flag,
          'Match the explicitly selected mode. Do not enable real intake merely to satisfy a test.')
    if mode == 'intake-config':
        privacy = vars_.get('PRIVACY_NOTICE_URL')
        notice_ok = False
        if isinstance(privacy, str) and https_origin(origin):
            u = urlsplit(privacy)
            notice_ok = (u.scheme + '://' + u.netloc == origin and u.path not in ('', '/')
                         and not u.query and not u.fragment and not u.username and not u.password)
        check('privacy_version_and_notice', configured(vars_.get('PRIVACY_VERSION')) and notice_ok,
              'Publish reviewed privacy information at the same origin and configure its exact version. This checker does not grant legal approval.')
    check('material_gate_closed', vars_.get('MATERIALS_ENABLED') == 'false',
          'Keep material delivery closed during initial account onboarding; run its separate rights/storage acceptance before enabling.')
    buckets = config.get('r2_buckets', [])
    check('optional_private_material_binding', isinstance(buckets, list) and len(buckets) <= 1 and all(
          isinstance(b, dict) and set(b) == {'binding', 'bucket_name'} and b.get('binding') == 'MIRA_MATERIALS'
          and bool(MIRA_NAME.fullmatch(str(b.get('bucket_name', '')))) for b in buckets),
          'Use only a separately approved mira-* material bucket; verify public access is disabled in Cloudflare.')
    report['passed'] = all(c['passed'] for c in report['checks'])
    report['manual_acceptance_still_required'] = [
        'Actual account ownership and new database isolation; no existing service reused',
        'Access policies on the pilot page, library and API; real email login, expiry and logout',
        'Verified administrator identity and agency membership isolation',
        'Reviewed personal-data processing/location, privacy publication, retention and incident handling',
        'Actual receipt persistence, database recovery and an agreed safe capacity test',
        'Separate current developer/project rules before buyer registration']
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--expected-account-id', required=True)
    parser.add_argument('--expected-database-id', required=True)
    parser.add_argument('--expected-origin', required=True)
    parser.add_argument('--mode', choices=['closed-staging', 'intake-config'], default='closed-staging')
    parser.add_argument('--topology', choices=['api-route', 'dedicated-site'], default='api-route')
    args = parser.parse_args()
    try:
        # No exception text is returned: malformed TOML can contain secret values.
        with args.config.open('rb') as stream:
            raw = stream.read(MAX_CONFIG_BYTES + 1)
        if len(raw) > MAX_CONFIG_BYTES:
            raise ValueError('size')
        config = tomllib.loads(raw.decode('utf8'))
    except (OSError, UnicodeError, ValueError):
        print(json.dumps({'passed': False, 'error': 'config_missing_invalid_or_oversized',
                          'production_ready': False})); return 2
    report = inspect(config, args.expected_account_id, args.expected_database_id, args.expected_origin, args.mode, args.topology)
    report['config_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
