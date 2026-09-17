"""Offline regression for the route-callback failure observed in CP15 CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

spec = spec_from_file_location('mira_campaign_acceptance', Path(__file__).with_name('mira-campaign-browser.py'))
suite = module_from_spec(spec)
spec.loader.exec_module(suite)

class Route:
    def __init__(self):
        self.response = None
    def fulfill(self, **kwargs):
        self.response = kwargs

class FixtureCallbackTests(unittest.TestCase):
    def test_two_argument_callback_preserves_status(self):
        route = Route()
        suite.make_json_fixture(503, 'temporary')(route, object())
        self.assertEqual(route.response, {'status': 503, 'content_type': 'application/json', 'body': 'temporary'})
    def test_one_argument_callback_preserves_body(self):
        route = Route()
        suite.make_json_fixture(200, '{invalid')(route)
        self.assertEqual(route.response['status'], 200)
        self.assertEqual(route.response['body'], '{invalid')
    def test_distinct_handlers_keep_distinct_fixtures(self):
        handlers = [suite.make_json_fixture(code, body) for code, body in [(503, 'temporary'), (200, '{invalid')]]
        routes = [Route(), Route()]
        for handler, route in zip(handlers, routes):
            handler(route, object())
        self.assertEqual([r.response['status'] for r in routes], [503, 200])
    def test_invalid_fixture_rejected(self):
        for status, body in [(True, '{}'), ('503', '{}'), (99, '{}'), (600, '{}'), (200, object())]:
            with self.subTest(status=status), self.assertRaises(ValueError):
                suite.make_json_fixture(status, body)

if __name__ == '__main__':
    unittest.main()
