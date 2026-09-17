import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot_assets', ROOT/'scripts/mira-build-pilot-assets.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PilotAssetsTests(unittest.TestCase):
    def test_bundle_is_bounded_and_preserves_same_origin_api(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            allowed = module.build(output)
            self.assertEqual(len(allowed), 8)
            self.assertEqual(sorted(p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()), allowed)
            for name in ('pilot.html', 'library.html'):
                self.assertIn('href="/cdn-cgi/access/logout"', (output/'mira'/name).read_text())
            self.assertIn("fetch('/mira/api'", (output/'mira/pilot.mjs').read_text())

    def test_unexpected_file_blocks_packaging(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            (output/'private.txt').write_text('synthetic-private-data')
            with self.assertRaises(ValueError):
                module.build(output)

    def test_symlink_blocks_packaging(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            (output/'mira').symlink_to(ROOT/'mira', target_is_directory=True)
            with self.assertRaises(ValueError):
                module.build(output)
