"""
Data storage and persistence functionality
"""

import json
import os
import csv
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .data_models import FinancialData

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles data persistence"""
    
    def __init__(self, storage_file: str = None):
        # Determine storage file location
        if storage_file is None:
            # Check environment override first
            env_path = os.getenv('FINPULL_STORAGE_FILE')
            if env_path:
                storage_file = env_path
            else:
                # Default to user home directory ~/.finpull/financial_data.json to avoid permission issues
                home_dir = os.path.expanduser('~')
                default_dir = os.path.join(home_dir, '.finpull')
                try:
                    os.makedirs(default_dir, exist_ok=True)
                except PermissionError:
                    # Fallback to current directory if home directory not writable
                    default_dir = os.getcwd()
                storage_file = os.path.join(default_dir, 'financial_data.json')
        
        self.storage_file = storage_file
        self.data_cache: Dict[str, FinancialData] = {}
        self.tickers_list: List[str] = []
        self.load_data()
    
    def load_data(self):
        """Load data from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tickers_list = data.get('tickers', [])
                    
                    # Convert dict data back to FinancialData objects
                    cache_data = data.get('cache', {})
                    for ticker, item_data in cache_data.items():
                        self.data_cache[ticker] = FinancialData.from_dict(item_data)
                        
                logger.info(f"Loaded {len(self.tickers_list)} tickers from {self.storage_file}")
        except PermissionError as e:
            logger.error(f"Permission denied when reading storage file: {e}")
            print(f"⚠️  FinPull cannot read the storage file due to permission error. Data will not be persisted. Path: {self.storage_file}")
            # Initialize empty state on error
            self.data_cache = {}
            self.tickers_list = []
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            # Initialize empty state on error
            self.data_cache = {}
            self.tickers_list = []
    
    def save_data(self):
        """Save data to storage file"""
        try:
            # Import version dynamically
            from .. import __version__
            
            data = {
                'tickers': self.tickers_list,
                'cache': {ticker: data.to_dict() for ticker, data in self.data_cache.items()},
                'last_updated': datetime.now().isoformat(),
                'version': __version__
            }
            
            # Create backup if file exists
            if os.path.exists(self.storage_file):
                backup_file = f"{self.storage_file}.backup"
                try:
                    import shutil
                    shutil.copy2(self.storage_file, backup_file)
                except Exception as backup_error:
                    logger.warning(f"Could not create backup: {backup_error}")
            
            # Write data atomically
            temp_file = f"{self.storage_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Replace original file
            os.replace(temp_file, self.storage_file)
            logger.debug(f"Saved data to {self.storage_file}")
            
        except PermissionError as e:
            logger.error(f"Permission denied when writing storage file: {e}")
            print(f"⚠️  FinPull cannot save data due to permission error. Changes will not persist. Path: {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            # Clean up temp file if it exists
            temp_file = f"{self.storage_file}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def add_ticker(self, ticker: str) -> bool:
        """Add ticker to the list if not already present"""
        ticker = ticker.upper().strip()
        if ticker and ticker not in self.tickers_list:
            self.tickers_list.append(ticker)
            self.save_data()
            logger.info(f"Added ticker {ticker}")
            return True
        return False
    
    def remove_ticker(self, ticker: str):
        """Remove ticker from the list"""
        ticker = ticker.upper().strip()
        if ticker in self.tickers_list:
            self.tickers_list.remove(ticker)
            if ticker in self.data_cache:
                del self.data_cache[ticker]
            self.save_data()
            logger.info(f"Removed ticker {ticker}")
    
    def clear_all(self):
        """Clear all tickers and cached data"""
        self.tickers_list.clear()
        self.data_cache.clear()
        self.save_data()
        logger.info("Cleared all data")
    
    def update_cache(self, ticker: str, data: FinancialData):
        """Update cached data for a ticker"""
        ticker = ticker.upper().strip()
        self.data_cache[ticker] = data
        self.save_data()
        logger.debug(f"Updated cache for {ticker}")
    
    def get_cached_data(self, ticker: str) -> Optional[FinancialData]:
        """Get cached data for a ticker"""
        return self.data_cache.get(ticker.upper())
    
    def get_all_tickers(self) -> List[str]:
        """Get all ticker symbols"""
        return self.tickers_list.copy()
    
    def get_all_cached_data(self) -> Dict[str, FinancialData]:
        """Get all cached data"""
        return self.data_cache.copy()
    
    def export_to_json(self, filename: str = None) -> str:
        """Export data to JSON file"""
        if not filename:
            filename = f"financial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = []
        for ticker in self.tickers_list:
            if ticker in self.data_cache:
                export_data.append(self.data_cache[ticker].to_dict())
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(export_data)} records to {filename}")
        return filename
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export data to CSV file"""
        if not filename:
            filename = f"financial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.data_cache:
            # Create empty CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ticker'])  # At least write header
            return filename
        
        # Get all field names from the first item
        first_item = next(iter(self.data_cache.values()))
        fieldnames = list(first_item.to_dict().keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for ticker in self.tickers_list:
                if ticker in self.data_cache:
                    writer.writerow(self.data_cache[ticker].to_dict())
                    count += 1
        
        logger.info(f"Exported {count} records to {filename}")
        return filename
    
    def get_stats(self) -> Dict[str, any]:
        """Get storage statistics"""
        total_tickers = len(self.tickers_list)
        cached_tickers = len(self.data_cache)
        stale_count = sum(1 for data in self.data_cache.values() if data.is_stale())
        
        return {
            'total_tickers': total_tickers,
            'cached_tickers': cached_tickers,
            'missing_cache': total_tickers - cached_tickers,
            'stale_data': stale_count,
            'storage_file': self.storage_file,
            'file_exists': os.path.exists(self.storage_file),
            'file_size': os.path.getsize(self.storage_file) if os.path.exists(self.storage_file) else 0
        }
    
    def cleanup_stale_data(self, max_age_hours: int = 24):
        """Remove stale data from cache"""
        removed_count = 0
        tickers_to_remove = []
        
        for ticker, data in self.data_cache.items():
            if data.is_stale(max_age_hours * 60):  # Convert hours to minutes
                tickers_to_remove.append(ticker)
        
        for ticker in tickers_to_remove:
            del self.data_cache[ticker]
            removed_count += 1
        
        if removed_count > 0:
            self.save_data()
            logger.info(f"Cleaned up {removed_count} stale records")
        
        return removed_count 