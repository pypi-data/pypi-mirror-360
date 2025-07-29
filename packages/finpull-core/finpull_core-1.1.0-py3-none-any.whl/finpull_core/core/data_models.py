"""
Data models for financial information
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class FinancialData:
    """Data class for financial information"""
    ticker: str = "N/A"
    company_name: str = "N/A"
    sector: str = "N/A"
    price: str = "N/A"
    change_5y: str = "N/A"
    dividend_yield: str = "N/A"
    dividend_ttm: str = "N/A"
    eps_ttm: str = "N/A"
    eps_next_year: str = "N/A"
    eps_next_5y: str = "N/A"
    revenue: str = "N/A"
    revenue_growth_5y: str = "N/A"
    operating_margin: str = "N/A"
    profit_margin: str = "N/A"
    roa: str = "N/A"
    roe: str = "N/A"
    roi: str = "N/A"
    pe_ratio: str = "N/A"
    ps_ratio: str = "N/A"
    pb_ratio: str = "N/A"
    total_assets: str = "N/A"
    total_liabilities: str = "N/A"
    market_cap: str = "N/A"
    volume: str = "N/A"
    avg_volume: str = "N/A"
    beta: str = "N/A"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialData':
        """Create instance from dictionary"""
        return cls(**data)
    
    def is_valid(self) -> bool:
        """Check if the data contains meaningful information"""
        # Consider data valid if we have at least ticker and one meaningful field
        meaningful_fields = [
            self.company_name, self.price, self.market_cap, 
            self.pe_ratio, self.sector
        ]
        return (self.ticker != "N/A" and 
                any(field != "N/A" and field != "" for field in meaningful_fields))
    
    def get_display_summary(self) -> str:
        """Get a one-line summary for display"""
        return f"{self.ticker}: {self.company_name} - ${self.price} (P/E: {self.pe_ratio})"
    
    def get_age_minutes(self) -> float:
        """Get age of data in minutes"""
        try:
            timestamp_dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            age = datetime.now() - timestamp_dt.replace(tzinfo=None)
            return age.total_seconds() / 60
        except:
            return float('inf')
    
    def is_stale(self, max_age_minutes: int = 60) -> bool:
        """Check if data is stale (older than max_age_minutes)"""
        return self.get_age_minutes() > max_age_minutes 