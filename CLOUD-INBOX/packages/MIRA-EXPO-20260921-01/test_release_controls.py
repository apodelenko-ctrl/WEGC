import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
import apply_patch
import readiness

class PatchTests(unittest.TestCase):
    def fixture(self, root):
        pkg = root / 'package'; repo = root / 'repo'
        rows = []
        for name in ['a.txt', 'b.txt']:
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (pkg / 'replacement').mkdir(parents=True, exist_ok=True)
            (repo / name).write_bytes(b'old')
            (pkg / 'replacement' / name).write_bytes(b'new')
            rows.append({'path': name, 'before_sha256': hashlib.sha256(b'old').hexdigest(),
                         'after_sha256': hashlib.sha256(b'new').hexdigest()})
        (pkg / 'patch-manifest.json').write_text(json.dumps({'files': rows}))
        return repo, pkg

    def test_dry_run_and_repeated_application(self):
        with tempfile.TemporaryDirectory() as d:
            repo, pkg = self.fixture(Path(d))
            apply_patch.apply(repo, package=pkg)
            self.assertEqual((repo / 'a.txt').read_bytes(), b'old')
            apply_patch.apply(repo, True, pkg)
            self.assertEqual(apply_patch.apply(repo, True, pkg)['already_applied'], 2)

    def test_second_file_drift_preserves_first(self):
        with tempfile.TemporaryDirectory() as d:
            repo, pkg = self.fixture(Path(d)); (repo / 'b.txt').write_bytes(b'LOCAL change')
            with self.assertRaises(ValueError): apply_patch.apply(repo, True, pkg)
            self.assertEqual((repo / 'a.txt').read_bytes(), b'old')
            self.assertEqual((repo / 'b.txt').read_bytes(), b'LOCAL change')

    def test_damaged_package_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            repo, pkg = self.fixture(Path(d)); (pkg / 'replacement' / 'b.txt').write_bytes(b'bad')
            with self.assertRaises(ValueError): apply_patch.apply(repo, True, pkg)
            self.assertEqual((repo / 'a.txt').read_bytes(), b'old')

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
        self.doc = {'gates': [{'id': x, 'status': 'passed_live', 'evidence': ['receipt'],
            'checked_at': '2026-09-24T10:00:00Z', 'owner': 'LOCAL', 'next_action': 'none'}
            for x in sorted(readiness.REQUIRED)]}

    def test_complete_and_expired_evidence(self):
        self.assertTrue(readiness.assess(self.doc, self.now)['ready'])
        self.doc['gates'][0]['valid_until'] = '2026-09-24T11:00:00Z'
        self.assertFalse(readiness.assess(self.doc, self.now)['ready'])

    def test_prepared_code_does_not_mean_live(self):
        self.doc['gates'][0]['status'] = 'prepared'
        self.assertFalse(readiness.assess(self.doc, self.now)['ready'])

    def test_missing_duplicate_or_unknown_gates_rejected(self):
        for changed in [self.doc['gates'][:-1], self.doc['gates'] + [self.doc['gates'][0]],
                        self.doc['gates'][:-1] + [dict(self.doc['gates'][-1], id='EXPO-99')]]:
            with self.assertRaises(ValueError): readiness.assess({'gates': changed}, self.now)

    def test_unsupported_or_future_acceptance_rejected(self):
        for change in [{'evidence': []}, {'checked_at': '2026-09-25T10:00:00Z'}, {'status': 'done'}]:
            doc = copy.deepcopy(self.doc); doc['gates'][0].update(change)
            with self.assertRaises(ValueError): readiness.assess(doc, self.now)

if __name__ == '__main__': unittest.main()
