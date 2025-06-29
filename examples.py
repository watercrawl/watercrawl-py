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
