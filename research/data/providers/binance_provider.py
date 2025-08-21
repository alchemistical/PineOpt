"""Binance data provider for real live crypto market data."""

import logging
import requests
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent.parent.parent.parent / "outputs" / "datasets" / "binance"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class BinanceProvider:
    """Provider for fetching real live crypto OHLC data from Binance public API."""
    
    def __init__(self):
        """Initialize Binance provider (no credentials needed for public data)."""
        self.base_url = "https://api.binance.com/api/v3"
        self._authenticated = False  # Public API
    
    def _map_timeframe(self, timeframe: str) -> str:
        """Map timeframe to Binance format."""
        timeframe_map = {
            '1m': '1m',
            '3m': '3m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '2h': '2h',
            '4h': '4h',
            '6h': '6h',
            '8h': '8h',
            '12h': '12h',
            '1d': '1d',
            '3d': '3d',
            '1w': '1w',
            '1M': '1M'
        }
        return timeframe_map.get(timeframe, '1h')
    
    def _get_cache_path(self, symbol: str, exchange: str, timeframe: str, n_bars: int) -> Path:
        """Get cache file path for given parameters."""
        filename = f"{exchange}_{symbol}_{timeframe}_{n_bars}.parquet"
        return CACHE_DIR / filename
    
    def _normalize_data(self, df: pd.DataFrame, symbol: str, exchange: str, timeframe: str) -> Dict:
        """Normalize DataFrame to standard OHLC format."""
        if df is None or df.empty:
            return {
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": timeframe,
                "count": 0,
                "ohlc": []
            }
        
        # Reset index to make datetime a column
        df_normalized = df.reset_index()
        df_normalized = df_normalized.rename(columns={'open_time': 'time'})
        
        # Convert time to ISO string
        if pd.api.types.is_datetime64_any_dtype(df_normalized['time']):
            df_normalized['time'] = df_normalized['time'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Fill NaN values
        df_normalized = df_normalized.fillna(0)
        
        # Convert to list of dictionaries
        ohlc_data = df_normalized[['time', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')
        
        return {
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "count": len(ohlc_data),
            "ohlc": ohlc_data
        }
    
    def fetch_ohlc(self, 
                   symbol: str, 
                   exchange: str, 
                   timeframe: str = '1h', 
                   n_bars: int = 1000,
                   use_cache: bool = True) -> Dict:
        """
        Fetch real crypto OHLC data from Binance public API.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            exchange: Exchange name (not used for Binance, but kept for compatibility) 
            timeframe: Timeframe string (e.g., '1h', '1d')
            n_bars: Number of bars to fetch (max 1000)
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary with normalized OHLC data
        """
        # Check cache first
        cache_path = self._get_cache_path(symbol, "BINANCE", timeframe, n_bars)
        if use_cache and cache_path.exists():
            try:
                # Check if cache is recent (less than 5 minutes old)
                cache_age = time.time() - cache_path.stat().st_mtime
                max_age = 300  # 5 minutes
                
                if cache_age < max_age:
                    logger.info(f"Loading from cache: {cache_path}")
                    df = pd.read_parquet(cache_path)
                    return self._normalize_data(df, symbol, "BINANCE", timeframe)
                else:
                    logger.info(f"Cache expired, fetching fresh data")
            except Exception as e:
                logger.warning(f"Failed to load cache {cache_path}: {e}")
        
        # Fetch real data from Binance
        try:
            # Map timeframe to Binance format
            binance_interval = self._map_timeframe(timeframe)
            
            # Limit bars to Binance max
            limit = min(n_bars, 1000)
            
            # Build request URL
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol.upper(),
                'interval': binance_interval,
                'limit': limit
            }
            
            logger.info(f"Fetching {symbol} from Binance API with interval={binance_interval}, limit={limit}")
            
            # Make request to Binance API
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            klines_data = response.json()
            
            if not klines_data:
                logger.warning(f"No data returned for {symbol}")
                return self._normalize_data(None, symbol, "BINANCE", timeframe)
            
            # Parse Binance klines format
            ohlc_data = []
            for kline in klines_data:
                # Binance klines format:
                # [0] Open time, [1] Open, [2] High, [3] Low, [4] Close, [5] Volume,
                # [6] Close time, [7] Quote volume, [8] Count, [9] Taker buy volume, 
                # [10] Taker buy quote volume, [11] Ignore
                
                ohlc_data.append({
                    'open_time': pd.to_datetime(int(kline[0]), unit='ms'),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlc_data)
            df.set_index('open_time', inplace=True)
            
            logger.info(f"Successfully fetched {len(df)} bars for {symbol} from Binance")
            
            # Cache the result
            try:
                df.to_parquet(cache_path)
                logger.info(f"Cached data to: {cache_path}")
            except Exception as e:
                logger.warning(f"Failed to cache data: {e}")
            
            return self._normalize_data(df, symbol, "BINANCE", timeframe)
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data from Binance API: {e}")
            raise RuntimeError(f"Binance API request failed: {e}")
        except Exception as e:
            logger.error(f"Failed to process Binance data for {symbol}: {e}")
            raise RuntimeError(f"Binance data processing failed: {e}")
    
    def get_available_exchanges(self) -> List[str]:
        """Get list of supported exchanges (only Binance for this provider)."""
        return ['BINANCE']
    
    def get_popular_symbols(self, exchange: str = 'BINANCE') -> List[str]:
        """Get list of popular crypto symbols on Binance."""
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOTUSDT', 'LINKUSDT', 'MATICUSDT', 'AVAXUSDT'
        ]


# Global provider instance
_binance_provider = None

def get_binance_provider() -> BinanceProvider:
    """Get global Binance provider instance."""
    global _binance_provider
    if _binance_provider is None:
        _binance_provider = BinanceProvider()
    return _binance_provider