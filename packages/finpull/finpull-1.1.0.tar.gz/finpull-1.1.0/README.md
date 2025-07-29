# FinPull - Financial Data Scraper

[![PyPI version](https://badge.fury.io/py/finpull.svg)](https://badge.fury.io/py/finpull)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FinPull is a comprehensive financial data scraping tool providing multiple interfaces for accessing financial market data. The package includes API, command-line, and graphical user interfaces, making it suitable for various use cases from automated trading systems to interactive data analysis.

## Installation

```bash
pip install finpull
```

For API-only usage (lightweight):
```bash
pip install finpull-core
```

## Quick Start

### GUI Mode (Default)
```bash
finpull
```

### Command Line Interface
```bash
# Interactive mode
finpull --interactive

# Direct commands
finpull add AAPL GOOGL MSFT
finpull show AAPL --full
finpull export portfolio.xlsx --xlsx
finpull refresh
```

### Programmatic API
```python
from finpull import FinancialDataAPI

api = FinancialDataAPI()
result = api.add_ticker("AAPL")
data = api.get_data("AAPL")

if data['success']:
    stock_info = data['data']
    print(f"Company: {stock_info['company_name']}")
    print(f"Price: ${stock_info['price']}")
    print(f"Market Cap: {stock_info['market_cap']}")
```

## Performance

Comprehensive benchmarks on typical hardware with 10 test runs each:

| Metric | Core Package | Full Package | Difference |
|--------|--------------|--------------|------------|
| **Package Size** | 21.9 KB | 27.2 KB | +5.3 KB (+24.2%) |
| **Installed Size** | 134 KB | 188 KB | +54 KB (+40.3%) |
| **Import Time (cached)** | 0.0002s | 0.0002s | No difference |
| **Dependencies** | 3 packages | 4 packages | +openpyxl |

### Key Features

- **Multiple Interfaces**: GUI, CLI, and API access
- **Export Options**: JSON, CSV, and Excel formats
- **Progress Tracking**: Real-time operation status
- **Cross-Platform**: Windows, macOS, and Linux support

## Interfaces

### Graphical User Interface (GUI)

**Launch**: `finpull` or `finpull --gui`

**Features**:
- **Data Grid**: Complete view of all 27 financial metrics with horizontal/vertical scrolling
- **Multi-Selection**: Select and manage multiple tickers simultaneously (Ctrl+Click, Shift+Click)
- **Smart Sorting**: Click column headers to sort by any metric with data type awareness
- **Real-time Updates**: Progress indicators showing 🔄 loading, ✅ success, ❌ error states
- **Export Dialog**: Save data to JSON, CSV, or Excel with file browser integration
- **Status Bar**: Current operation status and ticker count display
- **Responsive Layout**: Adapts to different screen sizes and resolutions

### Command Line Interface (CLI)

**Launch**: `finpull --interactive` or direct commands

**Available Commands**:
- `add <tickers>` - Add ticker symbols for tracking
- `remove <tickers>` - Remove tickers from tracking  
- `show [ticker] [--full]` - Display ticker information
- `refresh [ticker]` - Update data from sources
- `export <filename> [--json] [--csv] [--xlsx]` - Save data to files
- `stats` - Show system statistics and health
- `clear` - Remove all tracked data (with confirmation)

**Features**:
- **Interactive Mode**: Shell-like interface (`finpull>` prompt) for exploration
- **Direct Commands**: Single-command operations perfect for scripting and automation
- **Batch Operations**: Process multiple tickers efficiently in one command
- **Formatted Output**: Beautiful ASCII tables with aligned columns and borders
- **Progress Indicators**: Real-time status updates for long-running operations
- **Auto-completion**: Tab completion for commands and options (in interactive mode)

### API Interface

**Import**: `from finpull import FinancialDataAPI, FinancialDataScraper`

**Classes**:
- **FinancialDataAPI**: High-level interface with error handling and validation
- **FinancialDataScraper**: Low-level scraper for direct data access and control
- **FinancialData**: Data model with 27+ financial attributes

**Features**:
- **Consistent Responses**: All methods return standardized JSON format
- **Comprehensive Error Handling**: Detailed error codes and descriptive messages
- **Type Hints**: Full type annotation support for better IDE integration
- **Validation**: Built-in ticker format validation and data sanitization
- **Callback Support**: Progress callbacks for batch operations and real-time updates

## Data Coverage

Provides 27 financial metrics per ticker across all categories: basic info, valuation ratios, earnings, profitability, growth, financial position, and market data. Uses Finviz and Yahoo Finance with automatic failover for high reliability.

## Configuration

### Environment Variables

```bash
# Custom storage location
export FINPULL_STORAGE_FILE="/path/to/custom/storage.json"

# Rate limiting (seconds between requests)
export FINPULL_RATE_LIMIT="2"

# Logging level (DEBUG, INFO, WARNING, ERROR)
export FINPULL_LOG_LEVEL="INFO"

# GUI theme (if supported)
export FINPULL_GUI_THEME="default"
```

### Storage

Data is persisted locally in JSON format with automatic backups:
- **Linux/macOS**: `~/.finpull/data.json`
- **Windows**: `%USERPROFILE%\.finpull\data.json`
- **Backup**: Automatic backup before major operations
- **Format**: Human-readable JSON with proper indentation

### Rate Limiting

Built-in intelligent rate limiting prevents API blocks:
- **Default**: 1 request per second (configurable)
- **Adaptive**: Automatically increases delays if rate limits detected
- **Burst Protection**: Prevents accidental rapid-fire requests
- **Source-Specific**: Different limits for different data sources

## Documentation

- **[Interface Guide](docs/INTERFACES.md)** - Complete interface documentation
- **[API Reference](https://github.com/Lavarite/FinPull/blob/main/packages/finpull-core/docs/API_REFERENCE.md)** - API methods and responses
- **[Data Format](https://github.com/Lavarite/FinPull/blob/main/packages/finpull-core/docs/API_REFERENCE.md#data-format)** - JSON schema and field descriptions

## Web Integration

Supports browser integration via Pyodide and Node.js via CLI commands. See main repository README for complete integration examples and code samples.

## Package Architecture

```
finpull/
├── Core Package (finpull-core)
│   ├── API interface
│   ├── Data scraping engine
│   ├── Storage management
│   └── Utility functions
└── Interface Extensions
    ├── Command-line interface
    ├── Graphical user interface
    └── Excel export functionality
```

The full package depends on `finpull-core` for core functionality, ensuring:
- No code duplication between packages
- Consistent API across all interfaces
- Modular installation options
- Streamlined maintenance and updates

## Examples

### Portfolio Management

```python
from finpull import FinancialDataAPI

api = FinancialDataAPI()

# Build a technology portfolio
tech_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
results = api.batch_add_tickers(tech_stocks)

print(f"Successfully added {results['summary']['added_count']} stocks")

# Analyze portfolio performance
portfolio_data = api.get_data()
for stock in portfolio_data['data']:
    print(f"{stock['ticker']}: ${stock['price']} | P/E: {stock['pe_ratio']} | Cap: {stock['market_cap']}")
```

### Automated CLI Workflow

```bash
#!/bin/bash

# Daily portfolio update script
echo "Updating portfolio..."

# Add new stocks if needed
finpull add AAPL GOOGL MSFT

# Refresh all data
finpull refresh

# Generate reports
finpull export "reports/portfolio_$(date +%Y%m%d)" --json --csv --xlsx

# Show summary
finpull show --full

echo "Portfolio update complete"
```

### Real-time Monitoring

```python
import time
from finpull import FinancialDataAPI

api = FinancialDataAPI()

# Add watchlist
watchlist = ["AAPL", "GOOGL", "MSFT", "TSLA"]
api.batch_add_tickers(watchlist)

while True:
    # Refresh data every 5 minutes
    api.refresh_data()
    
    # Check for significant changes
    data = api.get_data()
    for stock in data['data']:
        change_5y = float(stock['change_5y'].replace('%', ''))
        if abs(change_5y) > 10:  # More than 10% change
            print(f"Alert: {stock['ticker']} changed {change_5y}% over 5 years")
    
    time.sleep(300)  # 5 minutes
```

### GUI Automation

```python
import threading
from finpull import FinancialDataGUI

def setup_automated_gui():
    gui = FinancialDataGUI()
    
    # Pre-populate with data
    gui.scraper.add_ticker("AAPL")
    gui.scraper.add_ticker("GOOGL")
    gui.refresh_display()
    
    # Run GUI in separate thread
    gui_thread = threading.Thread(target=gui.run)
    gui_thread.start()
    
    return gui

# Launch automated GUI session
gui = setup_automated_gui()
```

### Error Handling & Logging

```python
import logging
from finpull import FinancialDataAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = FinancialDataAPI()

def safe_operation(ticker):
    try:
        result = api.add_ticker(ticker)
        if result['success']:
            logger.info(f"Successfully added {ticker}")
            return True
        else:
            logger.warning(f"Failed to add {ticker}: {result.get('error')}")
            return False
    except Exception as e:
        logger.error(f"Exception for {ticker}: {e}")
        return False

# Safe batch processing
tickers = ["AAPL", "INVALID", "GOOGL", "MSFT"]
successful = [t for t in tickers if safe_operation(t)]
print(f"Successfully processed {len(successful)}/{len(tickers)} tickers")
```

## License

MIT License - see [LICENSE](https://github.com/Lavarite/FinPull/blob/main/LICENSE) file for details.

## Links

- **[Core Package](https://pypi.org/project/finpull-core/)** - Lightweight API-only version
- **[Source Code](https://github.com/Lavarite/FinPull)** - GitHub repository
- **[Issues](https://github.com/Lavarite/FinPull/issues)** - Bug reports and feature requests 