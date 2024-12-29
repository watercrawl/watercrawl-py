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
        self.assertIsInstance(response, list)

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


if __name__ == '__main__':
    unittest.main()
