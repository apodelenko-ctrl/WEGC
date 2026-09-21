#!/usr/bin/env python3
"""Preflight both exact source files before changing either; dry-run by default."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def inspect(root, package=HERE):
    manifest = json.loads((package / 'patch-manifest.json').read_text())
    states = []
    for row in manifest['files']:
        target = root / row['path']
        replacement = package / 'replacement' / row['path']
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        if not target.is_file():
            raise ValueError('Missing source: ' + row['path'])
        if digest(replacement) != row['after_sha256']:
            raise ValueError('Damaged package: ' + row['path'])
        current = digest(target)
        if current not in (row['before_sha256'], row['after_sha256']):
            raise ValueError('Source changed; review current diff: ' + row['path'])
        states.append((target, replacement, current == row['after_sha256']))
    return states

def apply(root, write=False, package=HERE):
    states = inspect(root, package)
    changed = []
    for target, replacement, already_applied in states:
        if not already_applied:
            if write:
                target.write_bytes(replacement.read_bytes())
            changed.append(str(target.relative_to(root)))
    return {'mode': 'applied' if write else 'dry_run', 'files_to_change': changed,
            'already_applied': len(states) - len(changed), 'deployed': False}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    print(json.dumps(apply(a.repo.resolve(), a.apply), ensure_ascii=False, indent=2))
