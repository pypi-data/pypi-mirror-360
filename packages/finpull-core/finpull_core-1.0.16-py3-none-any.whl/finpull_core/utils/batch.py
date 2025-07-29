"""
Batch processing utilities and helper functions
"""

import logging
from typing import List, Dict, Any

from ..core.data_models import FinancialData
from .compatibility import (
    HAS_REQUESTS, HAS_BS4, HAS_YFINANCE, HAS_TKINTER, HAS_OPENPYXL
)

logger = logging.getLogger(__name__)


def batch_fetch_tickers(tickers: List[str]) -> List[FinancialData]:
    """
    Batch fetch multiple tickers
    
    Args:
        tickers: List of ticker symbols to fetch
        
    Returns:
        List of FinancialData objects for successfully fetched tickers
    """
    # Import locally to avoid circular import
    from ..core.scraper import FinancialDataScraper
    
    scraper = FinancialDataScraper()
    results = []
    
    logger.info(f"Starting batch fetch for {len(tickers)} tickers")
    
    for ticker in tickers:
        try:
            scraper.add_ticker(ticker)
            data = scraper.storage.get_cached_data(ticker)
            if data:
                results.append(data)
        except ValueError as e:
            logger.error(f"Invalid ticker {ticker}: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch {ticker}: {e}")
    
    logger.info(f"Batch fetch complete: {len(results)}/{len(tickers)} successful")
    return results


def get_available_features() -> Dict[str, bool]:
    """
    Return dict of available features based on installed packages
    
    Returns:
        Dictionary mapping feature names to availability status
    """
    return {
        "web_scraping": HAS_REQUESTS and HAS_BS4,
        "yahoo_finance": HAS_YFINANCE,
        "gui": HAS_TKINTER,
        "excel_export": HAS_OPENPYXL,
        "json_export": True,
        "csv_export": True
    }


def create_portable_scraper():
    """
    Create a basic scraper instance for embedding in other applications
    
    Returns:
        FinancialDataScraper instance
    """
    from ..core.scraper import FinancialDataScraper
    return FinancialDataScraper()


def validate_ticker_list(tickers: List[str]) -> Dict[str, Any]:
    """
    Validate a list of ticker symbols
    
    Args:
        tickers: List of ticker symbols to validate
        
    Returns:
        Dictionary with validation results
    """
    from ..core.scraper import FinancialDataScraper
    
    scraper = FinancialDataScraper()
    
    valid_tickers = []
    invalid_tickers = []
    
    for ticker in tickers:
        if scraper.validate_ticker(ticker):
            valid_tickers.append(ticker.upper().strip())
        else:
            invalid_tickers.append(ticker)
    
    return {
        "valid": valid_tickers,
        "invalid": invalid_tickers,
        "total": len(tickers),
        "valid_count": len(valid_tickers),
        "invalid_count": len(invalid_tickers)
    }


def export_multiple_formats(scraper, formats: List[str] = None) -> Dict[str, str]:
    """
    Export data in multiple formats
    
    Args:
        scraper: FinancialDataScraper instance
        formats: List of formats to export (default: all available)
        
    Returns:
        Dictionary mapping format names to output filenames
    """
    if formats is None:
        formats = ["json", "csv"]
        if HAS_OPENPYXL:
            formats.append("xlsx")
    
    results = {}
    
    for fmt in formats:
        try:
            filename = scraper.export_data(fmt)
            results[fmt] = filename
            logger.info(f"Exported {fmt}: {filename}")
        except Exception as e:
            logger.error(f"Failed to export {fmt}: {e}")
            results[fmt] = f"ERROR: {e}"
    
    return results


def get_ticker_performance_summary(data_list: List[FinancialData]) -> Dict[str, Any]:
    """
    Get a performance summary from a list of financial data
    
    Args:
        data_list: List of FinancialData objects
        
    Returns:
        Dictionary with performance statistics
    """
    if not data_list:
        return {"error": "No data provided"}
    
    # Extract numeric values where possible
    pe_ratios = []
    prices = []
    market_caps = []
    
    for data in data_list:
        # Try to extract P/E ratios
        try:
            if data.pe_ratio != "N/A" and data.pe_ratio:
                pe_val = float(data.pe_ratio.replace('%', ''))
                if pe_val > 0:  # Valid P/E ratio
                    pe_ratios.append(pe_val)
        except (ValueError, AttributeError):
            pass
        
        # Try to extract prices
        try:
            if data.price != "N/A" and data.price:
                price_val = float(data.price.replace('$', '').replace(',', ''))
                if price_val > 0:
                    prices.append(price_val)
        except (ValueError, AttributeError):
            pass
    
    # Calculate statistics
    summary = {
        "total_tickers": len(data_list),
        "sectors": {},
        "avg_pe_ratio": None,
        "avg_price": None,
        "price_range": None,
        "pe_range": None
    }
    
    # Sector distribution
    for data in data_list:
        sector = data.sector if data.sector != "N/A" else "Unknown"
        summary["sectors"][sector] = summary["sectors"].get(sector, 0) + 1
    
    # P/E statistics
    if pe_ratios:
        summary["avg_pe_ratio"] = sum(pe_ratios) / len(pe_ratios)
        summary["pe_range"] = [min(pe_ratios), max(pe_ratios)]
    
    # Price statistics
    if prices:
        summary["avg_price"] = sum(prices) / len(prices)
        summary["price_range"] = [min(prices), max(prices)]
    
    return summary 