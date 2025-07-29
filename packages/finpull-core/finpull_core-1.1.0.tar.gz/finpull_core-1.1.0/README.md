# FinPull Core - Financial Data Scraper API

[![PyPI version](https://badge.fury.io/py/finpull-core.svg)](https://badge.fury.io/py/finpull-core)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FinPull Core is a lightweight financial data scraping library providing programmatic access to comprehensive financial metrics. This package contains only the essential API functionality, making it suitable for web applications, microservices, and minimal deployments.

## Installation

```bash
pip install finpull-core
```

## Quick Start

```python
from finpull_core import FinancialDataAPI

# Initialize the API
api = FinancialDataAPI()

# Add a ticker for tracking
result = api.add_ticker("AAPL")
print(result)
# {'success': True, 'message': 'Added AAPL', 'ticker': 'AAPL'}

# Retrieve financial data
data = api.get_data("AAPL")
if data['success']:
    stock_data = data['data']
    print(f"Company: {stock_data['company_name']}")
    print(f"Price: ${stock_data['price']}")
    print(f"P/E Ratio: {stock_data['pe_ratio']}")

# Batch operations
tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
results = api.batch_add_tickers(tickers)

# Export data
export_result = api.export_data("json")
```

## Performance

Benchmarked on typical hardware with 10 test runs:

| Metric | Value | Details |
|--------|-------|---------|
| **Package Size** | 21.9 KB (wheel) | Compressed distribution file |
| **Installed Size** | 134 KB | Uncompressed on disk |
| **Import Time** | 0.0002s (cached) | Cold import: 0.9s, cached: 0.0002s |
| **Dependencies** | 3 packages | requests, beautifulsoup4, yfinance |
| **API Response** | 100-500ms | Per ticker, varies by data source |

### Performance Characteristics

- **First Import**: ~0.9 seconds (includes dependency loading)
- **Subsequent Imports**: ~0.0002 seconds (module cache)
- **Standard Deviation**: 0.3s (due to first-time loading)
- **Consistency**: Very stable after initial load

### Optimization Features

- **Local Caching**: Automatic data caching reduces API calls
- **Rate Limiting**: Built-in throttling prevents API blocks (1 req/sec default)
- **Lazy Loading**: Components load only when needed
- **Efficient Storage**: JSON-based local storage with minimal overhead
- **Web Compatible**: Works in browser environments via Pyodide/WASM
- **Batch Operations**: Process multiple tickers efficiently

## Configuration

### Environment Variables

```bash
# Custom storage location
export FINPULL_STORAGE_FILE="/path/to/custom/storage.json"

# Rate limiting (seconds between requests)
export FINPULL_RATE_LIMIT="2"
```

### Storage

Data is stored locally in JSON format:
- **Linux/macOS**: `~/.finpull/data.json`
- **Windows**: `%USERPROFILE%\.finpull\data.json`

## Data Coverage

FinPull Core provides 27 financial metrics per ticker including price, P/E ratio, market cap, earnings data, profitability ratios, and growth metrics. Data is sourced from Finviz and Yahoo Finance with automatic fallback for high availability.

## Dependencies

### Required Packages
- **requests** (≥2.25.1): HTTP client for data fetching
- **beautifulsoup4** (≥4.9.3): HTML parsing for web scraping
- **yfinance** (≥0.1.63): Yahoo Finance API integration

### Optional Dependencies
- **psutil**: For memory usage monitoring (development/testing)
- **openpyxl**: Excel export (available in full `finpull` package)

## Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Data Format](docs/API_REFERENCE.md#data-format)** - JSON schema and field descriptions
- **[Error Handling](docs/API_REFERENCE.md#error-handling)** - Error codes and exception handling

## Web Integration

Works in browser environments via Pyodide and Node.js via subprocess calls. See main repository README for integration examples.

## Examples

### Basic Usage
```python
from finpull_core import FinancialDataAPI

api = FinancialDataAPI()

# Add and retrieve data
api.add_ticker("AAPL")
data = api.get_data("AAPL")
print(f"Price: ${data['data']['price']}")
```

### Batch Operations
```python
# Add multiple tickers
tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
results = api.batch_add_tickers(tickers)
print(f"Added {results['summary']['added_count']} tickers")

# Get all data
all_data = api.get_data()
for stock in all_data['data']:
    print(f"{stock['ticker']}: ${stock['price']} (P/E: {stock['pe_ratio']})")
```

### Data Export
```python
# Export to different formats
json_result = api.export_data("json", "portfolio.json")
csv_result = api.export_data("csv", "portfolio.csv")
print(f"Exported {json_result['record_count']} records")
```

### Error Handling
```python
try:
    result = api.add_ticker("INVALID_TICKER")
    if not result['success']:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Exception: {e}")
```

## Package Options

For complete functionality including CLI and GUI, use the full package:

```bash
pip install finpull
```

Or switch from core to full package:

```bash
pip uninstall finpull-core
pip install finpull
```

### Package Comparison
| Feature | finpull-core | finpull |
|---------|--------------|---------|
| **Size** | 21.9 KB | 27.2 KB |
| **API Access** | ✓ | ✓ |
| **CLI Interface** | ✗ | ✓ |
| **GUI Application** | ✗ | ✓ |
| **Excel Export** | ✗ | ✓ |
| **Web Compatible** | ✓ | ✓ |

All API calls are identical between packages - simply change the import statement when switching.

## License

MIT License - see [LICENSE](https://github.com/Lavarite/FinPull/blob/main/LICENSE) file for details.

## Links

- **[Full Package](https://pypi.org/project/finpull/)** - Complete version with CLI/GUI
- **[Source Code](https://github.com/Lavarite/FinPull)** - GitHub repository
- **[Issues](https://github.com/Lavarite/FinPull/issues)** - Bug reports and feature requests 