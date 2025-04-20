import os
import unittest

from .api import WaterCrawlAPIClient


class TestWaterCrawlAPI(unittest.TestCase):
    def setUp(self):
        self.api = WaterCrawlAPIClient(
            api_key=os.environ['WATERCRAWL_API_KEY'],
        )

    def test_get_crawl_requests_list(self):
        response = self.api.get_crawl_requests_list()
        self.assertIsInstance(response['results'], list)

    def test_get_crawl_request(self):
        items = self.api.get_crawl_requests_list()
        response = self.api.get_crawl_request(items['results'][0]['uuid'])
        self.assertIsInstance(response, dict)

    def test_create_crawl_request(self):
        response = self.api.create_crawl_request(url='https://watercrawl.dev')
        self.assertIsInstance(response, dict)

    def test_stop_crawl_request(self):
        result = self.api.create_crawl_request(url='https://watercrawl.dev')
        response = self.api.stop_crawl_request(result['uuid'])
        self.assertIsNone(response)

    def test_download_crawl_request(self):
        result = self.api.get_crawl_requests_list()
        response = self.api.download_crawl_request(result['results'][0]['uuid'])
        self.assertIsInstance(response, bytes)

    def test_monitor_crawl_request(self):
        result = self.api.create_crawl_request(url='https://watercrawl.dev')
        response = self.api.monitor_crawl_request(result['uuid'])
        for item in response:
            self.assertIsInstance(item, dict)

    def test_get_crawl_request_results(self):
        result = self.api.get_crawl_requests_list()
        response = self.api.get_crawl_request_results(result['results'][-1]['uuid'])
        self.assertIsInstance(response['results'], list)

    def test_download_result(self):
        result_crawl = self.api.get_crawl_requests_list()
        index = 0
        while True:
            result = self.api.get_crawl_request_results(result_crawl['results'][index]['uuid'])
            if len(result['results']) > 0:
                break
            index += 1

        result = self.api.get_crawl_request_results(result_crawl['results'][index]['uuid'])
        response = self.api.download_result(result['results'][0])
        self.assertIsInstance(response, dict)

    def test_scrape_url(self):
        response = self.api.scrape_url(url='https://watercrawl.dev')
        self.assertIsInstance(response, dict)

    def test_download_sitemap(self):
        # Simulate a crawl_request dict with a sitemap key
        crawl_request = {'sitemap': 'https://example.com/sitemap.json'}
        self.api._WaterCrawlAPIClient__get_crawl_request_for_sitemap = lambda x: crawl_request
        # Mock requests.get
        import types
        class MockResponse:
            def raise_for_status(self): pass
            def json(self): return {'mock': 'data'}
        requests_get_backup = self.api.requests.get if hasattr(self.api, 'requests') else None
        import requests
        requests.get = lambda url: MockResponse()
        result = self.api.download_sitemap(crawl_request)
        self.assertEqual(result, {'mock': 'data'})
        if requests_get_backup:
            requests.get = requests_get_backup

    def test_download_sitemap_graph(self):
        crawl_request = {'uuid': '1234', 'sitemap': 'https://example.com/sitemap.json'}
        self.api._WaterCrawlAPIClient__get_crawl_request_for_sitemap = lambda x: crawl_request
        self.api._get = lambda url: {'graph': True}
        self.api.process_response = lambda resp: resp
        result = self.api.download_sitemap_graph(crawl_request)
        self.assertEqual(result, {'graph': True})

    def test_download_sitemap_markdown(self):
        crawl_request = {'uuid': '1234', 'sitemap': 'https://example.com/sitemap.json'}
        self.api._WaterCrawlAPIClient__get_crawl_request_for_sitemap = lambda x: crawl_request
        self.api._get = lambda url: {'markdown': True}
        self.api.process_response = lambda resp: resp
        result = self.api.download_sitemap_markdown(crawl_request)
        self.assertEqual(result, {'markdown': True})

    def test_get_crawl_request_for_sitemap_errors(self):
        # Should raise ValueError if sitemap is missing
        with self.assertRaises(ValueError):
            self.api._WaterCrawlAPIClient__get_crawl_request_for_sitemap({})


if __name__ == '__main__':
    unittest.main()
