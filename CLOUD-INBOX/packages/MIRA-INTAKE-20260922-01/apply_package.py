#!/usr/bin/env python3
"""Selective local source integration only. Does not deploy, migrate D1 or enable intake."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='Default is read-only validation')
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    repo = args.repo.resolve()
    manifest = json.loads((package / 'patch-manifest.json').read_text())
    pending = []
    for item in manifest['files']:
        target = repo / item['path']
        source = package / 'replacement' / item['path']
        if not target.resolve().is_relative_to(repo):
            raise SystemExit('Refusing symlink outside target: ' + item['path'])
        if digest(source) != item['sha256_after']:
            raise SystemExit('Package checksum mismatch: ' + item['path'])
        actual = digest(target)
        if actual == item['sha256_after']:
            continue
        if actual != item['sha256_before']:
            raise SystemExit('Source changed; preserve it and review diff: ' + item['path'])
        pending.append((source, target))
    for item in manifest['dependencies']:
        if digest(repo / item['path']) != item['sha256']:
            raise SystemExit('Dependency changed; review before integration: ' + item['path'])
    if args.apply:
        # All inputs checked first. Replay accepts already-applied identical files.
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    print(json.dumps({'validated_files': len(manifest['files']), 'pending': len(pending),
                      'applied': len(pending) if args.apply else 0,
                      'deployed': False, 'remote_database_writes': 0}))

if __name__ == '__main__':
    main()
