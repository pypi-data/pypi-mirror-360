__version__ = "1.1.0"
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