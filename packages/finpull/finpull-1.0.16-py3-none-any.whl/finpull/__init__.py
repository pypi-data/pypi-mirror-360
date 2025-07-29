"""
FinPull - Complete Financial Data Scraper

Enterprise-grade financial data scraping tool with comprehensive interfaces:
- API for programmatic access
- CLI for command-line operations  
- GUI for interactive desktop use

This package provides the complete FinPull experience including all interfaces
and features. For lightweight API-only usage, consider finpull-core.
"""

__version__ = "1.0.16"
__author__ = "Yevhenii Vasylevskyi"
__email__ = "yevhenii+finpull@vasylevskyi.net"

# Import core functionality from finpull-core
from finpull_core import (
    FinancialDataScraper,
    FinancialData,
    FinancialDataAPI,
    get_available_features,
    batch_fetch_tickers,
)

# Import additional interfaces
from .interfaces.cli import FinancialDataCLI
from .interfaces.gui import FinancialDataGUI

__all__ = [
    # Core classes (from finpull-core)
    "FinancialDataScraper",
    "FinancialData", 
    "FinancialDataAPI",
    
    # Additional interfaces (full package)
    "FinancialDataCLI",
    "FinancialDataGUI",
    
    # Utilities
    "get_available_features",
    "batch_fetch_tickers",
    
    # Metadata
    "__version__",
]

def get_package_info():
    """Get package information"""
    return {
        "name": "finpull",
        "version": __version__,
        "description": "Complete financial data scraper",
        "interfaces": ["API", "CLI", "GUI"],
        "features": get_available_features(),
        "core_package": "finpull-core"
    }

def get_available_interfaces():
    """Get list of available interfaces"""
    return ["API", "CLI", "GUI"] 