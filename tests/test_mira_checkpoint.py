"""Synthetic transport integrity tests; no operational data or external requests."""
import base64
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zlib

spec = importlib.util.spec_from_file_location('transport', Path(__file__).resolve().parents[1] / 'scripts/mira-apply-reviewed-checkpoint.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def bundle(path='mira/synthetic-test.mjs', before=None):
    data = b'// SYNTHETIC TEST\n'
    return {'id': 'TEST', 'kind': 'reviewed-public-source', 'version': 1, 'files': [
        {'path': path, 'before_sha256': before, 'sha256': m.digest(data),
         'zlib_base64': base64.b64encode(zlib.compress(data)).decode()}]}


class TransportTests(unittest.TestCase):
    def test_verified_payload_and_idempotent_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); prepared = m.prepare(root, bundle())
            path, data, changed = prepared[0]; self.assertTrue(changed)
            path.parent.mkdir(); path.write_bytes(data)
            self.assertFalse(m.prepare(root, bundle())[0][2])

    def test_concurrent_edit_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / 'mira').mkdir(); target = root / 'mira/synthetic-test.mjs'
            target.write_text('HUMAN CHANGE')
            with self.assertRaisesRegex(ValueError, 'Concurrent edit'): m.prepare(root, bundle())
            self.assertEqual(target.read_text(), 'HUMAN CHANGE')

    def test_paths_and_self_modification_rejected(self):
        for path in ['../mira/test', '/tmp/test', '.github/workflows/test.yml', 'private.db',
                     'mira/../secrets', 'mira/.env', 'scripts/mira-apply-reviewed-checkpoint.py', m.BUNDLE, m.APPLIED]:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as folder:
                with self.assertRaises(ValueError): m.prepare(Path(folder), bundle(path))

    def test_hash_symlink_and_size_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); b = bundle(); b['files'][0]['sha256'] = 'WRONG'
            with self.assertRaises(ValueError): m.prepare(root, b)
            (root / 'outside').mkdir(); (root / 'mira').symlink_to(root / 'outside', target_is_directory=True)
            with self.assertRaises(ValueError): m.prepare(root, bundle())

    def test_dictionary_delta_uses_exact_previous_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / 'mira/synthetic-test.mjs'; path.parent.mkdir()
            before = b'// SYNTHETIC OLD SOURCE\n' * 100
            after = before + b'// SYNTHETIC CHANGE\n'
            path.write_bytes(before)
            c = zlib.compressobj(9, zdict=before[-32768:])
            b = bundle(before=m.digest(before)); item = b['files'][0]
            item.update(codec='zlib-dict-v1', sha256=m.digest(after), zlib_base64=base64.b64encode(c.compress(after)+c.flush()).decode())
            result = m.prepare(root, b)[0]
            self.assertEqual(result[1], after); self.assertTrue(result[2])
            path.write_bytes(after); self.assertFalse(m.prepare(root, b)[0][2])
