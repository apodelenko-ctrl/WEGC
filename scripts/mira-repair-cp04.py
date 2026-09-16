#!/usr/bin/env python3
"""Repair two observed transport corruptions; never transform arbitrary source.

Each input and output is SHA-256 pinned. Unknown/later payloads are untouched.
Readable UTF-8 repository writes replace this transport for new checkpoints.
"""
from pathlib import Path
import hashlib
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATH = 'project-bible/mira/operations/reviewed-checkpoint.json'
REPAIRS = {
    'aa6f023fddae4039b8e9cd6c4ace40085b3469f62c99b4dacca29b77fc29c9ab': (
        '9e658486a0182328d9bf28ea1fe30d22b4ff10f512a8eabe2c90948b636bca4b',
        [(4532, 4533, b'X4'), (7630, 7638, b''),
         (14617, 14617, b'r'), (14618, 14619, b'y'),
         (14620, 14621, b''), (14693, 14701, b'')]),
    'e24086a338d0bc8d3285c36abedefa414f02d58e32ac91b010ef449b23bf2a98': (
        'bc24b40bae33b24bca5fbb530b4f49cb1a3e43fba97f7fb84dc8e0caf2c8c223',
        [(725, 737, b''), (1986, 1998, b''), (6704, 6708, b'9L'),
         (6748, 6749, b'Z'), (8146, 8146, b'Vszn+aIsZ1l5NZsLPM3VXN5kN4t'),
         (11078, 11083, b'Ny'), (11084, 11085, b'j'),
         (11086, 11087, b'xXHe'), (11088, 11090, b''), (11426, 11434, b'')])
}

def repair(data):
    rule = REPAIRS.get(hashlib.sha256(data).hexdigest())
    if rule is None:
        return data
    expected, edits = rule
    for start, end, replacement in reversed(edits):
        data = data[:start] + replacement + data[end:]
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Repair did not reproduce the reviewed source payload')
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
        print('Transport restored to exact reviewed SHA256; full validation follows.')
    else:
        print('No matching historical corruption; payload left unchanged.')

if __name__ == '__main__':
    main()
