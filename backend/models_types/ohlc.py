"""OHLC data type definitions."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class OHLCRecord:
    """Single OHLC record."""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

    def __post_init__(self):
        """Validate OHLC data integrity."""
        if self.high < max(self.open, self.close):
            raise ValueError(f"High {self.high} < max(open={self.open}, close={self.close})")
        if self.low > min(self.open, self.close):
            raise ValueError(f"Low {self.low} > min(open={self.open}, close={self.close})")
        if any(price <= 0 for price in [self.open, self.high, self.low, self.close]):
            raise ValueError("All prices must be positive")


class OHLCDataFrame:
    """Wrapper for OHLC pandas DataFrame with validation."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = self._validate_and_clean(df)
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean OHLC DataFrame."""
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have DatetimeIndex")
        
        # Sort by time
        df = df.sort_index()
        
        # Basic validation
        invalid_rows = (
            (df['high'] < df[['open', 'close']].max(axis=1)) |
            (df['low'] > df[['open', 'close']].min(axis=1)) |
            (df[required_cols] <= 0).any(axis=1)
        )
        
        if invalid_rows.any():
            print(f"Warning: {invalid_rows.sum()} invalid OHLC records found and removed")
            df = df[~invalid_rows]
        
        return df
    
    @property
    def data(self) -> pd.DataFrame:
        """Access the underlying DataFrame."""
        return self.df
    
    def __len__(self) -> int:
        return len(self.df)
    
    def __getitem__(self, key):
        return self.df[key]