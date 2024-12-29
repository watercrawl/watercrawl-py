# WaterCrawl Python Client
[![PyPI version](https://badge.fury.io/py/watercrawl-py.svg)](https://badge.fury.io/py/watercrawl-py)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Python client library for interacting with the WaterCrawl API - a powerful web crawling and scraping service.

## Installation

```bash
pip install watercrawl-py
```


## Quick Start

```python
from watercrawl import WaterCrawlAPIClient

# Initialize the client
client = WaterCrawlAPIClient('your-api-key')

# Simple URL scraping
result = client.scrape_url('https://example.com')

# Advanced crawling with options
crawl_request = client.create_crawl_request(
    url='https://example.com',
    spider_options={},
    page_options={},
    plugin_options={}
)

# Monitor and download results
for result in client.monitor_crawl_request(crawl_request['uuid']):
    if result['type'] == 'result':
        print(result['data']) // it is a result object per page
```

## Features

- Simple and intuitive API client
- Support for both synchronous and asynchronous crawling
- Comprehensive crawling options and configurations
- Built-in request monitoring and result downloading
- Efficient session management and request handling

## Documentation

For detailed documentation and examples, visit [WaterCrawl Documentation](https://docs.watercrawl.dev/).

## Requirements

- Python >= 3.7
- `requests` library

## Compatibility

- WaterCrawl API >= 0.1.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please visit:
- Issues: [GitHub Issues](https://github.com/watercrawl/watercrawl-py/issues)
- Homepage: [GitHub Repository](https://github.com/watercrawl/watercrawl-py)
- Documentation: [WaterCrawl Docs](https://docs.watercrawl.dev/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
