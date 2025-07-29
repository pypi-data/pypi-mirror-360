"""
FinPull Core - Financial Data Scraper API

Enterprise-grade core package providing lightweight, programmatic access
to financial data scraping capabilities.

This package contains only the essential API functionality without
CLI or GUI interfaces, making it perfect for:
- Web applications and microservices
- JavaScript integration via Pyodide/WASM
- Docker containers and minimal deployments
- API-only applications

For full functionality including CLI and GUI interfaces,
install the complete package: pip install finpull
"""

__version__ = "1.0.16"
__author__ = "Yevhenii Vasylevskyi"
__email__ = "yevhenii+finpull@vasylevskyi.net"

# Core API exports
from .core.scraper import FinancialDataScraper
from .core.data_models import FinancialData
from .api import FinancialDataAPI

# Utility exports
from .utils.compatibility import get_available_features
from .utils.batch import batch_fetch_tickers

__all__ = [
    # Core classes
    "FinancialDataScraper",
    "FinancialData",
    "FinancialDataAPI",
    
    # Utilities
    "get_available_features",
    "batch_fetch_tickers",
    
    # Metadata
    "__version__",
]

def get_package_info():
    """Get package information"""
    return {
        "name": "finpull-core",
        "version": __version__,
        "description": "Financial data scraper core API",
        "interfaces": ["API"],
        "features": get_available_features(),
        "upgrade_info": "For CLI/GUI: pip install finpull"
    } 