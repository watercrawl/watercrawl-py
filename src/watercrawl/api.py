import json
from typing import Union, Generator
from urllib.parse import urljoin
import warnings

import requests
from requests import Response


class BaseAPIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.session = self.init_session()

    def init_session(self):
        session = requests.Session()
        session.headers.update({'X-API-Key': self.api_key})
        session.headers.update({'Content-Type': 'application/json'})
        session.headers.update({'Accept': 'application/json'})
        session.headers.update({'User-Agent': 'WaterCrawl-Plugin'})
        session.headers.update({'Accept-Language': 'en-US'})
        return session

    def _get(self, endpoint: str, query_params: dict = None, **kwargs):
        return self.session.get(
            urljoin(self.base_url, endpoint),
            params=query_params,
            **kwargs
        )

    def _post(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.post(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )

    def _put(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.put(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )

    def _delete(self, endpoint: str, query_params: dict = None, **kwargs):
        return self.session.delete(
            urljoin(self.base_url, endpoint),
            params=query_params,
            **kwargs
        )

    def _patch(self, endpoint: str, query_params: dict = None, data: dict = None, **kwargs):
        return self.session.patch(
            urljoin(self.base_url, endpoint),
            params=query_params,
            json=data, **kwargs
        )


class WaterCrawlAPIClient(BaseAPIClient):
    def __init__(self, api_key, base_url: str = 'https://app.watercrawl.dev/'):
        super().__init__(api_key, base_url)

    def process_eventstream(self, response: Response, download: bool = False):
        for line in response.iter_lines():
            line = line.decode('utf-8')
            if line.startswith('data:'):
                line = line[5:].strip()
                data = json.loads(line)
                yield data

    def process_response(self, response: Response) -> Union[dict, bytes, list, None, Generator]:
        response.raise_for_status()
        if response.status_code == 204:
            return None
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()

        if response.headers.get('Content-Type') == 'application/octet-stream':
            return response.content

        if response.headers.get('Content-Type') == 'text/event-stream':
            return self.process_eventstream(response)
        
        if response.headers.get('Content-Type') == 'application/zip':
            return response.content

        raise Exception(f'Unknown response type: {response.headers.get("Content-Type")}')

    def get_crawl_requests_list(self, page: int = None, page_size: int = None):
        query_params = {
            'page': page or 1,
            'page_size': page_size or 10
        }
        return self.process_response(
            self._get(
                '/api/v1/core/crawl-requests/',
                query_params=query_params,
            )
        )

    def get_crawl_request(self, item_id: str):
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/',
            )
        )

    def create_crawl_request(
            self,
            url: Union[list, str] = None,
            spider_options: dict = None,
            page_options: dict = None,
            plugin_options: dict = None
    ):
        data = {
            # 'urls': url if isinstance(url, list) else [url],
            'url': url,
            'options': {
                'spider_options': spider_options or {},
                'page_options': page_options or {},
                'plugin_options': plugin_options or {},
            }
        }
        return self.process_response(
            self._post(
                '/api/v1/core/crawl-requests/',
                data=data,
            )
        )

    def stop_crawl_request(self, item_id: str):
        return self.process_response(
            self._delete(
                f'/api/v1/core/crawl-requests/{item_id}/',
            )
        )

    def download_crawl_request(self, item_id: str):
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/download/',
            )
        )

    def monitor_crawl_request(self, item_id: str, download=True) -> Generator:
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/status/',
                stream=True,
                query_params={
                    'prefetched': download
                }
            )
        )

    def get_crawl_request_results(self, item_id: str, page: int = None, page_size: int = None):
        query_params = {
            'page': page or 1,
            'page_size': page_size or 10
        }
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{item_id}/results/',
                query_params=query_params,
            )
        )

    def scrape_url(self,
                   url: str,
                   page_options: dict = None,
                   plugin_options: dict = None,
                   sync: bool = True,
                   download: bool = True
                   ):
        result = self.create_crawl_request(
            url=url,
            page_options=page_options,
            plugin_options=plugin_options
        )
        if not sync:
            return result

        for result in self.monitor_crawl_request(result['uuid'], download):
            if result['type'] == 'result':
                return result['data']

    def download_result(self, result_object: dict):
        """[DEPRECATED] Download and parse the result object if necessary. Will be removed in a future version."""
        warnings.warn(
            "download_result is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        if isinstance(result_object['result'], dict):
            return result_object
        response = requests.get(result_object['result'])
        response.raise_for_status()
        result_object['result'] = response.json()
        return result_object
    
    def __get_crawl_request_for_sitemap(self, crawl_request: str or dict) -> dict:
        if isinstance(crawl_request, str):
            crawl_request = self.get_crawl_request(crawl_request)
            
        if 'sitemap' not in crawl_request:
            raise ValueError('Sitemap not found in crawl request')
        
        return crawl_request

    def download_sitemap(self, crawl_request: str or dict) -> bytes:
        """
        Download the sitemap for a given crawl request.
        it can be a string or crawl request object
        """
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)
        
        response = requests.get(crawl_request['sitemap'])
        response.raise_for_status()
        return response.json()
    
    def download_sitemap_graph(self, crawl_request: str or dict) -> bytes:
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)
        
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{crawl_request["uuid"]}/sitemap/graph/',
            )
        )
        
    def download_sitemap_markdown(self, crawl_request: str or dict) -> bytes:
        crawl_request = self.__get_crawl_request_for_sitemap(crawl_request)
        
        return self.process_response(
            self._get(
                f'/api/v1/core/crawl-requests/{crawl_request["uuid"]}/sitemap/markdown/',
            )
        )