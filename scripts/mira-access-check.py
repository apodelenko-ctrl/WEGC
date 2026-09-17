#!/usr/bin/env python3
"""Read-only pre-login check from the user's actual network. No credentials/sends.

Run on the intended Russian network with VPN disabled. Network labels and VPN
state are declarations, not independently detected facts. Never a signup test.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, HTTPRedirectHandler, HTTPSHandler, build_opener

PUBLIC = 'https://wegc.fund'
PILOT = 'https://pilot.wegc.fund'
MAX_BYTES = 3 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[1]


def validate_access_origin(value):
    if not re.fullmatch(r'https://[a-z0-9-]+\.cloudflareaccess\.com', value):
        raise ValueError('Use the actual team HTTPS origin; no path, port, query or credentials')
    return value


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def get(url, timeout=12):
    """No cookies, Authorization, redirects, email addresses or secret output."""
    started = time.monotonic()
    opener = build_opener(NoRedirect, HTTPSHandler(context=ssl.create_default_context()))
    request = Request(url, headers={'User-Agent': 'MIRA-owner-network-check/1',
                                   'Accept-Encoding': 'identity'}, method='GET')
    response = None
    try:
        try:
            response = opener.open(request, timeout=timeout)
        except HTTPError as error:
            response = error
        body = response.read(MAX_BYTES + 1)
        result = {'status': response.code, 'headers': dict(response.headers),
                  'body': body[:MAX_BYTES], 'too_large': len(body) > MAX_BYTES}
    except (URLError, OSError, TimeoutError, ValueError) as error:
        # Exception strings may contain URLs/queries. Persist class/category only.
        reason = getattr(error, 'reason', error)
        category = ('tls_error' if isinstance(reason, ssl.SSLError) else
                    'dns_error' if isinstance(reason, socket.gaierror) else
                    'timeout' if isinstance(reason, (TimeoutError, socket.timeout)) else 'network_error')
        result = {'status': None, 'headers': {}, 'body': b'', 'error': category}
    except Exception:
        result = {'status': None, 'headers': {}, 'body': b'', 'error': 'incomplete_response'}
    finally:
        if response is not None:
            response.close()
    result['elapsed_ms'] = round((time.monotonic() - started) * 1000)
    return result


def header(result, name):
    return next((str(v) for k, v in result.get('headers', {}).items()
                 if k.lower() == name.lower()), '')


def public_spec(root):
    files = [('/mira/go/', 'mira/go/index.html'),
             ('/mira/catalog/', 'mira/catalog/index.html'),
             ('/mira/catalog/data.json', 'mira/catalog/data.json')]
    data = json.loads((root / 'mira/catalog/data.json').read_text())
    image = next((p.get('image') for p in data.get('projects', []) if p.get('image')), None)
    if not image or not image.startswith('/images/') or '..' in image or '?' in image or '#' in image:
        raise ValueError('No exact existing project image in the current catalogue')
    files.append((image, image.lstrip('/')))
    specs = []
    for path, filename in files:
        source = root / filename
        if source.is_symlink() or not source.resolve().is_relative_to(root.resolve()):
            raise ValueError('Public asset must remain inside the local source tree')
        content = source.read_bytes()
        if not content or len(content) > MAX_BYTES:
            raise ValueError('Public source asset is empty or exceeds bounded check size')
        specs.append({'path': path, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    return specs


def run(specs, access_origin, network_label, vpn, requester=get):
    validate_access_origin(access_origin)
    if vpn not in ('off', 'on', 'unknown') or not re.fullmatch(r'[A-Za-z0-9_-]{1,48}', network_label):
        raise ValueError('Use a short non-personal network label and off/on/unknown VPN declaration')
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'network_label_user_declared': network_label, 'vpn_user_declared': vpn,
              'geography_independently_verified': False,
              'scope': 'bounded anonymous GET; no login/OTP submission/database writes',
              'live_signup_verified': False, 'production_ready': False, 'checks': []}
    for spec in specs:
        if not spec['path'].startswith('/mira/') and not spec['path'].startswith('/images/'):
            raise ValueError('Only known public MIRA pages and exact project images may be probed')
        if any(c in spec['path'] for c in ('?', '#', '\\')) or '..' in spec['path'] or spec['path'].startswith('//'):
            raise ValueError('Unexpected public asset path')
        r = requester(PUBLIC + spec['path'])
        digest = hashlib.sha256(r.get('body', b'')).hexdigest()
        ok = r.get('status') == 200 and not r.get('too_large') and digest == spec['sha256']
        report['checks'].append({'kind': 'public_exact_asset', 'path': spec['path'], 'passed': ok,
            'status': r.get('status'), 'received_bytes': len(r.get('body', b'')),
            'expected_bytes': spec['bytes'], 'sha256_matches': digest == spec['sha256'],
            'elapsed_ms': r.get('elapsed_ms'), 'error': r.get('error')})
    for path in ('/mira/pilot.html', '/mira/library.html', '/mira/api/session'):
        r = requester(PILOT + path)
        # Inspect but NEVER follow login redirects or persist query/cookie values.
        location = urlsplit(urljoin(PILOT, header(r, 'location')))
        destination = location.scheme + '://' + location.netloc
        good = (r.get('status') in (302, 303, 307, 308) and destination == access_origin
                and location.path.startswith('/cdn-cgi/access/login')
                and not location.username and not location.password)
        report['checks'].append({'kind': 'anonymous_access_redirect', 'path': path,
            'passed': good, 'status': r.get('status'), 'expected_login_destination': good,
            'elapsed_ms': r.get('elapsed_ms'), 'error': r.get('error')})
    r = requester(access_origin + '/cdn-cgi/access/certs')
    try:
        keys = json.loads(r.get('body', b'')).get('keys', [])
        certs_ok = r.get('status') == 200 and not r.get('too_large') and isinstance(keys, list) and any(
            isinstance(k, dict) and k.get('kty') == 'RSA' and k.get('kid') and k.get('n') and k.get('e') for k in keys)
    except (ValueError, TypeError, AttributeError):
        certs_ok = False
    report['checks'].append({'kind': 'public_access_certificate_endpoint', 'passed': bool(certs_ok),
                            'status': r.get('status'), 'elapsed_ms': r.get('elapsed_ms'), 'error': r.get('error')})
    report['prelogin_checks_passed'] = all(c['passed'] for c in report['checks'])
    report['target_no_vpn_condition_observed'] = report['prelogin_checks_passed'] and vpn == 'off'
    report['remaining'] = ['Real OTP delivery, login/logout and second-session receipt',
                           'Operator approval, isolation and revocation on deployment',
                           'Actual target-network browser check and data-handling review']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--access-origin', required=True, type=validate_access_origin)
    parser.add_argument('--network-label', required=True, help='e.g. RU-home; no names or email addresses')
    parser.add_argument('--vpn', required=True, choices=['off', 'on', 'unknown'])
    parser.add_argument('--out', required=True, type=Path, help='New private report outside the repository, e.g. /tmp/mira-network.json')
    args = parser.parse_args()
    if args.out.is_symlink() or args.out.resolve().is_relative_to(ROOT.resolve()):
        parser.error('Keep this network report outside the public repository')
    report = run(public_spec(ROOT), args.access_origin, args.network_label, args.vpn)
    # A new file only; no accidental overwrite of an existing report or credential.
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'prelogin_checks_passed': report['prelogin_checks_passed'],
                      'live_signup_verified': False, 'production_ready': False}))
    raise SystemExit(0 if report['prelogin_checks_passed'] else 1)


if __name__ == '__main__':
    main()
