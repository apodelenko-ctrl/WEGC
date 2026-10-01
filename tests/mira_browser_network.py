"""Suppress only the known analytics loader in owner acceptance tests.

This explicit fixture prevents QA pageviews from becoming visitor statistics.
Every other third-party URL and every write still goes through the strict guard.
"""
ANALYTICS_LOADER = 'https://static.cloudflareinsights.com/beacon.min.js'
def fixture_analytics(route):
    request = route.request
    if request.method == 'GET' and request.url == ANALYTICS_LOADER:
        route.fulfill(status=200, content_type='application/javascript', body='/* Owner QA: analytics intentionally not collected. */')
        return True
    return False
