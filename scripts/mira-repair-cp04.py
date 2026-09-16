#!/usr/bin/env python3
"""Repair exactly the observed CP04 transport corruption, never arbitrary source.

Both input and output are pinned. Later payloads are untouched. No network calls.
"""
from pathlib import Path
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATH = 'project-bible/mira/operations/reviewed-checkpoint.json'
BEFORE = 'aa6f023fddae4039b8e9cd6c4ace40085b3469f62c99b4dacca29b77fc29c9ab'
AFTER = '9e658486a0182328d9bf28ea1fe30d22b4ff10f512a8eabe2c90948b636bca4b'
EDITS = [(4532, 4533, b'X4'), (7630, 7638, b''),
         (14617, 14617, b'r'), (14618, 14619, b'y'),
         (14620, 14621, b''), (14693, 14701, b'')]

def repair(data):
    if hashlib.sha256(data).hexdigest() != BEFORE:
        return data
    for start, end, replacement in reversed(EDITS):
        data = data[:start] + replacement + data[end:]
    if hashlib.sha256(data).hexdigest() != AFTER:
        raise ValueError('CP04 repair did not reproduce the reviewed source payload')
    return data

def main():
    path = ROOT / PATH
    if not path.exists():
        return
    original = path.read_bytes()
    fixed = repair(original)
    if original != fixed:
        path.write_bytes(fixed)
        subprocess.run(['git', 'add', '--', PATH], cwd=ROOT, check=True)
        print('CP04 transport restored to exact reviewed SHA256; full validation follows.')
    else:
        print('No matching CP04 corruption; payload left unchanged.')

if __name__ == '__main__':
    main()
