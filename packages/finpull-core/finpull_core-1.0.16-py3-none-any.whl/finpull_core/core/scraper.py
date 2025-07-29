"""
Main scraper class that coordinates data fetching and storage
"""

import logging
from typing import List, Optional

from .data_models import FinancialData
from .data_sources import DataSourceManager
from .storage import DataStorage
from ..utils.compatibility import HAS_OPENPYXL

if HAS_OPENPYXL:
    from ..utils.export import ExcelExporter

logger = logging.getLogger(__name__)


class FinancialDataScraper:
    """Main application class that coordinates data operations"""
    
    def __init__(self, storage_file: str = None):
        """
        Initialize the scraper
        
        Args:
            storage_file: Custom path for data storage file
        """
        self.data_source = DataSourceManager()
        self.storage = DataStorage(storage_file)
        
        logger.info(f"FinancialDataScraper initialized with {self.data_source.get_source_count()} data sources")
    
    def add_ticker(self, ticker: str) -> bool:
        """
        Add a ticker and fetch its data
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            bool: True if ticker was added successfully
            
        Raises:
            Exception: If data fetching fails
        """
        # Validate ticker format first
        if not self.validate_ticker(ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        if self.storage.add_ticker(ticker):
            try:
                data = self.data_source.fetch_data(ticker)
                self.storage.update_cache(ticker, data)
                logger.info(f"Successfully added and fetched data for {ticker}")
                return True
            except Exception as e:
                logger.error(f"Failed to fetch data for {ticker}: {e}")
                self.storage.remove_ticker(ticker)  # Remove if we can't fetch data
                raise
        else:
            logger.info(f"Ticker {ticker} already exists")
            return False
    
    def refresh_data(self, ticker: str = None):
        """
        Refresh data for a specific ticker or all tickers
        
        Args:
            ticker: Specific ticker to refresh, or None for all tickers
        """
        tickers_to_refresh = [ticker] if ticker else self.storage.get_all_tickers()
        
        successful = 0
        failed = 0
        
        for t in tickers_to_refresh:
            try:
                data = self.data_source.fetch_data(t)
                self.storage.update_cache(t, data)
                logger.info(f"Refreshed data for {t}")
                successful += 1
            except Exception as e:
                logger.error(f"Failed to refresh {t}: {e}")
                failed += 1
        
        if ticker is None:
            logger.info(f"Refresh complete: {successful} successful, {failed} failed")
    
    def get_all_data(self) -> List[FinancialData]:
        """
        Get all cached financial data
        
        Returns:
            List of FinancialData objects
        """
        all_data = []
        for ticker in self.storage.get_all_tickers():
            cached_data = self.storage.get_cached_data(ticker)
            if cached_data:
                all_data.append(cached_data)
        return all_data
    
    def get_ticker_data(self, ticker: str) -> Optional[FinancialData]:
        """
        Get data for a specific ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            FinancialData object or None if not found
        """
        return self.storage.get_cached_data(ticker)
    
    def remove_ticker(self, ticker: str):
        """
        Remove a ticker from tracking
        
        Args:
            ticker: Stock ticker symbol to remove
        """
        self.storage.remove_ticker(ticker)
        logger.info(f"Removed ticker {ticker}")
    
    def clear_all(self):
        """Clear all tracked tickers and cached data"""
        self.storage.clear_all()
        logger.info("Cleared all data")
    
    def export_data(self, format_type: str = "json", filename: str = None) -> str:
        """
        Export data in specified format
        
        Args:
            format_type: Export format ("json", "csv", or "xlsx")
            filename: Custom filename (optional)
            
        Returns:
            str: Path to exported file
            
        Raises:
            ValueError: If format is not supported
        """
        format_type = format_type.lower()
        
        if format_type == "csv":
            return self.storage.export_to_csv(filename)
        elif format_type == "json":
            return self.storage.export_to_json(filename)
        elif format_type == "xlsx" and HAS_OPENPYXL:
            return self._export_to_xlsx(filename)
        else:
            available_formats = ["json", "csv"]
            if HAS_OPENPYXL:
                available_formats.append("xlsx")
            raise ValueError(f"Unsupported format: {format_type}. Available formats: {', '.join(available_formats)}")
    
    def _export_to_xlsx(self, filename: str = None) -> str:
        """Export data to Excel file using openpyxl"""
        if not HAS_OPENPYXL:
            raise ValueError("openpyxl not available for Excel export")
        
        exporter = ExcelExporter()
        return exporter.export_data(self.get_all_data(), filename)
    
    def get_stats(self) -> dict:
        """
        Get statistics about the scraper state
        
        Returns:
            dict: Statistics including ticker counts, data sources, etc.
        """
        storage_stats = self.storage.get_stats()
        source_info = self.data_source.get_source_info()
        
        return {
            **storage_stats,
            'data_sources': source_info,
            'source_count': len(source_info)
        }
    
    def cleanup_stale_data(self, max_age_hours: int = 24) -> int:
        """
        Remove stale cached data
        
        Args:
            max_age_hours: Maximum age in hours before data is considered stale
            
        Returns:
            int: Number of stale records removed
        """
        return self.storage.cleanup_stale_data(max_age_hours)
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol appears to be valid
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            bool: True if ticker appears valid
        """
        ticker = ticker.strip().upper()
        
        # Basic validation rules
        if not ticker:
            return False
        if len(ticker) > 10:  # Most tickers are 1-5 characters
            return False
        if not ticker.isalnum():  # Should only contain letters and numbers
            return False
        
        return True
    
    def get_ticker_list(self) -> List[str]:
        """
        Get list of all tracked tickers
        
        Returns:
            List of ticker symbols
        """
        return self.storage.get_all_tickers()
    
    def has_ticker(self, ticker: str) -> bool:
        """
        Check if a ticker is being tracked
        
        Args:
            ticker: Ticker symbol to check
            
        Returns:
            bool: True if ticker is being tracked
        """
        return ticker.upper() in self.storage.get_all_tickers() 