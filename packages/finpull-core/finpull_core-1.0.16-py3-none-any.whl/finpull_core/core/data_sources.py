"""
Data source managers for fetching financial data from various sources
"""

import time
import logging
from datetime import datetime
from typing import List, Callable

from .data_models import FinancialData
from ..utils.compatibility import HAS_REQUESTS, HAS_BS4, HAS_YFINANCE

if HAS_REQUESTS:
    import requests

if HAS_BS4:
    from bs4 import BeautifulSoup

if HAS_YFINANCE:
    import yfinance as yf

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manages multiple data sources with fallback mechanisms"""
    
    def __init__(self):
        self.sources: List[Callable[[str], FinancialData]] = []
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
        # Initialize available sources
        if HAS_REQUESTS and HAS_BS4:
            self.sources.append(self._fetch_from_finviz)
        if HAS_YFINANCE:
            self.sources.append(self._fetch_from_yahoo)
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _fetch_from_finviz(self, ticker: str) -> FinancialData:
        """Fetch data from Finviz"""
        self._rate_limit()
        
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            data = FinancialData(ticker=ticker.upper())
            
            # Extract company name
            company_tag = soup.find("h2", class_="quote-header_ticker-wrapper_company")
            if company_tag:
                data.company_name = company_tag.get_text(strip=True)
            
            # Extract price
            price_tag = soup.find("strong", class_="quote-price_wrapper_price")
            if price_tag:
                data.price = price_tag.get_text(strip=True)
            
            # Extract sector
            sector_div = soup.find("div", class_="flex space-x-0.5 overflow-hidden")
            if sector_div:
                sector_links = sector_div.find_all("a")
                if sector_links:
                    data.sector = sector_links[0].get_text(strip=True)
            
            # Extract metrics from snapshot table - improved parsing
            snapshot_table = soup.find("table", class_="snapshot-table2")
            if snapshot_table:
                # Parse the table more carefully - it has multiple columns per row
                rows = snapshot_table.find_all("tr")
                metrics = {}
                
                for row in rows:
                    cells = row.find_all("td")
                    # Each row has multiple key-value pairs (every 2 cells = 1 pair)
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            key_cell = cells[i]
                            value_cell = cells[i + 1]
                            
                            # Extract text and clean it
                            key = key_cell.get_text(strip=True)
                            value = value_cell.get_text(strip=True)
                            
                            # Clean up value (remove HTML formatting, extract main value)
                            if value:
                                # Handle cases like "1.01 (0.49%)" - extract both parts
                                if '(' in value and ')' in value:
                                    # For dividend: "1.01 (0.49%)" -> store both
                                    if 'Dividend' in key:
                                        parts = value.split('(')
                                        if len(parts) == 2:
                                            metrics[key] = parts[0].strip()
                                            metrics[f"{key} %"] = parts[1].replace(')', '').strip()
                                    else:
                                        metrics[key] = value.split('(')[0].strip()
                                else:
                                    metrics[key] = value
                
                # Enhanced field mapping with actual Finviz field names
                field_mapping = {
                    # Basic valuation metrics
                    "Market Cap": "market_cap",
                    "P/E": "pe_ratio",
                    "P/S": "ps_ratio", 
                    "P/B": "pb_ratio",
                    
                    # Earnings data
                    "EPS (ttm)": "eps_ttm",
                    "EPS next Y": "eps_next_year",
                    "EPS next 5Y": "eps_next_5y",
                    
                    # Dividend data
                    "Dividend TTM": "dividend_ttm",
                    "Dividend TTM %": "dividend_yield",
                    
                    # Performance metrics
                    "ROA": "roa",
                    "ROE": "roe", 
                    "ROIC": "roi",  # ROIC is closest to ROI
                    "Profit Margin": "profit_margin",
                    "Oper. Margin": "operating_margin",
                    
                    # Revenue data
                    "Sales": "revenue",
                    
                    # Performance over time
                    "Perf 5Y": "change_5y",
                    
                    # Volume and other metrics
                    "Volume": "volume",
                    "Avg Volume": "avg_volume", 
                    "Beta": "beta"
                }
                
                # Apply the mapping
                for finviz_key, data_field in field_mapping.items():
                    if finviz_key in metrics:
                        value = metrics[finviz_key]
                        setattr(data, data_field, value)
                
                # Special handling for 5-year revenue growth (if available)
                if "Sales past 3/5Y" in metrics:
                    # Extract 5Y growth: "2.25% 8.51%" -> "8.51%"
                    sales_growth = metrics["Sales past 3/5Y"]
                    parts = sales_growth.split()
                    if len(parts) >= 2:
                        data.revenue_growth_5y = parts[-1]  # Last part is 5Y
                
                # Debug: Log what was found
                logger.debug(f"Finviz metrics for {ticker}: {list(metrics.keys())}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching from Finviz for {ticker}: {e}")
            raise
    
    def _fetch_from_yahoo(self, ticker: str) -> FinancialData:
        """Fetch data from Yahoo Finance using yfinance"""
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            data = FinancialData(ticker=ticker.upper())
            
            # Basic info
            data.company_name = info.get('longName', 'N/A')
            data.sector = info.get('sector', 'N/A')
            data.price = str(info.get('currentPrice', 'N/A'))
            
            # Financial metrics
            data.market_cap = str(info.get('marketCap', 'N/A'))
            data.pe_ratio = str(info.get('trailingPE', 'N/A'))
            data.pb_ratio = str(info.get('priceToBook', 'N/A'))
            data.eps_ttm = str(info.get('trailingEps', 'N/A'))
            data.dividend_yield = str(info.get('dividendYield', 'N/A'))
            data.roa = str(info.get('returnOnAssets', 'N/A'))
            data.roe = str(info.get('returnOnEquity', 'N/A'))
            data.profit_margin = str(info.get('profitMargins', 'N/A'))
            data.beta = str(info.get('beta', 'N/A'))
            data.volume = str(info.get('volume', 'N/A'))
            data.avg_volume = str(info.get('averageVolume', 'N/A'))
            
            # Calculate 5-year price change
            try:
                hist = yf_ticker.history(period="5y")
                if not hist.empty:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    change_5y = ((end_price - start_price) / start_price) * 100
                    data.change_5y = f"{change_5y:.2f}%"
            except:
                pass
            
            # Balance sheet data
            try:
                balance_sheet = yf_ticker.balance_sheet
                if not balance_sheet.empty:
                    if 'Total Assets' in balance_sheet.index:
                        data.total_assets = str(balance_sheet.loc['Total Assets'].iloc[0])
                    if 'Total Liabilities Net Minority Interest' in balance_sheet.index:
                        data.total_liabilities = str(balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0])
            except:
                pass
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching from Yahoo Finance for {ticker}: {e}")
            raise
    
    def fetch_data(self, ticker: str) -> FinancialData:
        """Fetch data using available sources with intelligent data fusion"""
        ticker = ticker.upper().strip()
        
        primary_data = None
        errors = []
        
        # Try each source and collect data
        for i, source in enumerate(self.sources):
            try:
                logger.info(f"Attempting to fetch {ticker} using source {i+1}/{len(self.sources)}")
                data = source(ticker)
                
                if primary_data is None:
                    # First successful source becomes primary
                    primary_data = data
                    logger.info(f"Successfully fetched {ticker} from primary source")
                else:
                    # Supplement primary data with missing fields from other sources
                    logger.info(f"Supplementing {ticker} data from additional source")
                    self._merge_data(primary_data, data)
                
                # If we have primary data and this is Yahoo Finance, always try to get balance sheet
                if primary_data and hasattr(self, '_is_yahoo_source') and self._is_yahoo_source(source):
                    continue  # Always try Yahoo for balance sheet data
                    
            except Exception as e:
                logger.warning(f"Source {i+1} failed for {ticker}: {e}")
                errors.append(str(e))
                
        if primary_data is None:
            # If all sources failed, return a FinancialData object with N/A values and the ticker
            logger.warning(f"All sources failed for {ticker}: {errors}")
            return FinancialData(ticker=ticker.upper())
        
        logger.info(f"Successfully compiled data for {ticker}")
        return primary_data
    
    def _is_yahoo_source(self, source) -> bool:
        """Check if a source is the Yahoo Finance source"""
        return source.__name__ == '_fetch_from_yahoo' if hasattr(source, '__name__') else False
    
    def _merge_data(self, primary: FinancialData, supplementary: FinancialData):
        """Merge supplementary data into primary data for missing fields"""
        # List of fields to potentially supplement
        supplementary_fields = [
            'total_assets', 'total_liabilities', 'change_5y',
            'dividend_yield', 'beta', 'eps_ttm', 'pe_ratio'
        ]
        
        for field in supplementary_fields:
            primary_value = getattr(primary, field, "N/A")
            supp_value = getattr(supplementary, field, "N/A")
            
            # If primary doesn't have the field but supplementary does
            if primary_value == "N/A" and supp_value != "N/A":
                setattr(primary, field, supp_value)
                logger.debug(f"Supplemented {field}: {supp_value}")
    
    def get_source_count(self) -> int:
        """Get number of available sources"""
        return len(self.sources)
    
    def get_source_info(self) -> List[str]:
        """Get information about available sources"""
        info = []
        if HAS_REQUESTS and HAS_BS4:
            info.append("Finviz (web scraping)")
        if HAS_YFINANCE:
            info.append("Yahoo Finance (API)")
        return info 