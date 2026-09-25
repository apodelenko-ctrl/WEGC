#!/usr/bin/env python3
"""MIRA exhibition GET-only smoke. No login, submission, emails or cookies.

Checks availability/markers, NOT end-to-end submission or commercial readiness.
Only fixed allowlisted routes; redirects are inspected, never followed.
Response bodies/headers stay in temporary files and are not included in output.
"""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PUBLIC = 'https://wegc.fund'
PILOT = 'https://pilot.wegc.fund'
INTAKE = PILOT + '/mira/request/'
ROUTES = (
    ('qr_start', PUBLIC + '/mira/start/', 'public'),
    ('agency_access', PUBLIC + '/mira/access/', 'access'),
    ('guided_start', PUBLIC + '/mira/go/', 'public'),
    ('catalogue', PUBLIC + '/mira/catalog/', 'public'),
    ('intake', INTAKE, 'form'),
    ('intake_client', INTAKE + 'client.mjs', 'client'),
    ('privacy', INTAKE + 'privacy', 'privacy'),
    ('research', PILOT + '/mira/research/', 'protected'),
    ('operator_inbox', PILOT + '/mira/api/admin/intake/view', 'protected'),
)


class Markers(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def evaluate(route, status, headers, body):
    name, url, kind = route
    headers = {k.lower(): v for k, v in headers.items()}
    checks = {}
    content_type = headers.get('content-type', '')
    text = body.decode('utf-8', errors='replace')
    if kind == 'protected':
        loc = urlparse(headers.get('location', ''))
        checks['anonymous_access_denied'] = status in (401, 403) or (
            status in (302, 303, 307) and loc.scheme == 'https'
            and loc.hostname is not None and loc.hostname.endswith('.cloudflareaccess.com')
            and loc.path.startswith('/cdn-cgi/access/login')
        )
    else:
        checks['http_200'] = status == 200
        checks['content_type'] = ('javascript' in content_type if kind == 'client' else 'text/html' in content_type)
        parsed = Markers()
        if kind != 'client':
            parsed.feed(text)
            checks['russian_document'] = any(t == 'html' and a.get('lang') == 'ru' for t, a in parsed.tags)
        if kind == 'access':
            checks['intake_link'] = any(t == 'a' and a.get('href') == INTAKE for t, a in parsed.tags)
        if kind == 'form':
            forms = [a for t, a in parsed.tags if t == 'form' and a.get('id') == 'request']
            checks['unpaused_form'] = len(forms) == 1 and forms[0].get('data-paused') == 'false' and 'hidden' not in forms[0]
            checks['versioned_consent'] = len(forms) == 1 and bool(forms[0].get('data-consent'))
            checks['consent_unchecked_required'] = any(t == 'input' and a.get('name') == 'consent' and a.get('type') == 'checkbox' and 'required' in a and 'checked' not in a for t, a in parsed.tags)
            checks['turnstile_present'] = any(a.get('data-action') == 'mira_intake' and bool(a.get('data-sitekey')) for _, a in parsed.tags)
            checks['privacy_link'] = any(t == 'a' and a.get('href') == INTAKE + 'privacy' for t, a in parsed.tags)
        if kind == 'client':
            checks['receipt_ui'] = 'Номер заявки' in text and 'mira-intake-receipt-v1' in text
        if kind == 'privacy':
            checks['published_notice'] = 'Срок хранения и удаление' in text and 'WEST EAST TRADE GROUP' in text
        if kind in ('form', 'client', 'privacy'):
            checks['no_store'] = 'no-store' in headers.get('cache-control', '')
            checks['nosniff'] = headers.get('x-content-type-options') == 'nosniff'
    return {
        'name': name, 'url': url, 'http_status': status,
        'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks,
        'body_sha256': hashlib.sha256(body).hexdigest(), 'body_bytes': len(body),
    }


def probe(route):
    if route not in ROUTES:
        raise ValueError('Route is not allowlisted')
    with tempfile.TemporaryDirectory(prefix='mira-get-smoke-') as directory:
        header = Path(directory) / 'headers'
        body = Path(directory) / 'body'
        command = ['curl', '--disable', '--silent', '--show-error', '--request', 'GET',
                   '--proto', '=https', '--max-time', '25', '--max-filesize', '2097152',
                   '--dump-header', str(header), '--output', str(body),
                   '--write-out', '%{http_code}', route[1]]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        except (subprocess.TimeoutExpired, OSError):
            return {'name': route[0], 'url': route[1], 'status': 'UNVERIFIED',
                    'reason': 'transport_unavailable_or_timeout'}
        if result.returncode:
            return {'name': route[0], 'url': route[1], 'status': 'UNVERIFIED',
                    'reason': 'curl_transport_error', 'curl_exit': result.returncode}
        # A network proxy may prepend a CONNECT response. Use the final HTTP header block.
        blocks = re.split(r'\r?\n\r?\n', header.read_text())
        responses = [b for b in blocks if b.startswith('HTTP/')]
        if not responses or not result.stdout.strip().isdigit():
            return {'name': route[0], 'url': route[1], 'status': 'UNVERIFIED',
                    'reason': 'invalid_transport_response'}
        final = responses[-1]
        headers = dict(line.split(':', 1) for line in final.splitlines()[1:] if ':' in line)
        headers = {k.strip(): v.strip() for k, v in headers.items()}
        return evaluate(route, int(result.stdout), headers, body.read_bytes())


def run():
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(probe, ROUTES))
    return {'checked_at': datetime.now(timezone.utc).isoformat(),
            'scope': 'GET-only availability and anonymous boundary; no form submission or login',
            'status': 'PASS' if all(r['status'] == 'PASS' for r in rows) else 'REVIEW_REQUIRED',
            'routes': rows, 'new_requests_created': 0, 'emails_sent': 0,
            'commercial_readiness': 'NOT_ASSESSED',
            'not_tested': ['Turnstile challenge', 'durable submission', 'authenticated roles',
                           'mail delivery', 'physical QR', 'Russia mobile network']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = run()
    output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(output)
    print(output)
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
