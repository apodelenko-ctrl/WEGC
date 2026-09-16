#!/usr/bin/env python3
"""Apply a hash-pinned public-source checkpoint; no downloads or arbitrary commands.

A small compressed UTF-8 transport avoids exporting the whole WEGC repository.
Readable generated source files, not this transport, are the product artefacts.
The caller must review the source changes before assembling a bundle. CI tests
all applied changes before its existing non-force checkpoint commit.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = 'project-bible/mira/operations/reviewed-checkpoint.json'
APPLIED = 'project-bible/mira/operations/reviewed-checkpoint-applied.json'
MAX_FILE = 2_000_000
MAX_TOTAL = 12_000_000


def digest(data):
    return hashlib.sha256(data).hexdigest()


def allowed(path):
    p = PurePosixPath(path)
    return bool(path and str(p) == path and not p.is_absolute() and '..' not in p.parts and
                '\\' not in path and not any(part.startswith('.') for part in p.parts) and
                (path.startswith(('mira/', 'cloudflare-worker/mira/', 'project-bible/mira/')) or
                 (path.startswith('scripts/mira-') and path.endswith('.py')) or
                 (path.startswith('tests/') and 'mira' in p.name and len(p.parts) == 2)))


def prepare(root, payload):
    if payload.get('kind') != 'reviewed-public-source' or payload.get('version') != 1:
        raise ValueError('Unsupported checkpoint format')
    files = payload.get('files')
    if not isinstance(files, list) or not 1 <= len(files) <= 100:
        raise ValueError('Invalid file count')
    result, seen, total = [], set(), 0
    for item in files:
        path = item['path']
        if not allowed(path) or path in seen or path in [BUNDLE, APPLIED] or path == 'scripts/mira-apply-reviewed-checkpoint.py':
            raise ValueError('Disallowed or duplicate path: ' + path)
        seen.add(path)
        target = root / path
        if any(parent.is_symlink() for parent in [target, *target.parents] if parent != root.parent):
            raise ValueError('Symlink target is not allowed')
        original = target.read_bytes() if target.exists() else None
        before = digest(original) if original is not None else None
        if before not in [item.get('before_sha256'), item['sha256']]:
            raise ValueError('Concurrent edit: ' + path)
        if before == item['sha256']:
            data = original
        else:
            codec = item.get('codec', 'zlib-v1')
            if codec not in ['zlib-v1', 'zlib-dict-v1']:
                raise ValueError('Unknown checkpoint codec')
            if codec == 'zlib-dict-v1' and original is None:
                raise ValueError('Dictionary source is missing')
            decoder = zlib.decompressobj(**({'zdict': original[-32768:]} if codec == 'zlib-dict-v1' else {}))
            packed = base64.b64decode(item['zlib_base64'], validate=True)
            data = decoder.decompress(packed, MAX_FILE + 1)
            if not decoder.eof or decoder.unused_data:
                raise ValueError('Invalid or oversized compressed file')
        data.decode('utf-8')
        total += len(data)
        if len(data) > MAX_FILE or total > MAX_TOTAL or digest(data) != item['sha256']:
            raise ValueError('Payload size/hash mismatch')
        result.append((target, data, before != item['sha256']))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate without writing or staging')
    args = parser.parse_args()
    source = ROOT / BUNDLE
    if not source.exists():
        print('No reviewed source checkpoint supplied; no changes.'); return
    if source.stat().st_size > MAX_TOTAL:
        raise ValueError('Oversized bundle')
    payload = json.loads(source.read_text())
    payload_hash = digest(source.read_bytes())
    marker = ROOT / APPLIED
    if marker.exists() and json.loads(marker.read_text()).get('payload_sha256') == payload_hash:
        print('Reviewed checkpoint already committed; preserve subsequent human/generated edits.'); return
    prepared = prepare(ROOT, payload)
    if not args.check:
        for target, data, changed in prepared:
            if changed:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        marker.write_text(json.dumps({'id': payload['id'], 'payload_sha256': payload_hash, 'source_ref': payload.get('source_ref'), 'files': [{'path': item['path'], 'sha256': item['sha256']} for item in payload['files']]}, indent=2) + '\n')
        # Only explicit source paths are staged; no client databases, credentials or logs.
        subprocess.run(['git', 'add', '--', APPLIED, *[str(p.relative_to(ROOT)) for p, _, _ in prepared]], cwd=ROOT, check=True)
    print(json.dumps({'checkpoint': payload['id'], 'verified_files': len(prepared),
                      'changed_files': sum(changed for _, _, changed in prepared),
                      'check_only': args.check, 'external_requests': 0}))


if __name__ == '__main__':
    main()
