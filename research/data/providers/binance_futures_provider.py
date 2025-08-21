"""
Binance Futures Data Provider
Handles perpetual futures market data for USDT-denominated pairs
"""

import requests
import pandas as pd
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class BinanceFuturesProvider:
    """Provider for Binance Futures (Perpetual) market data"""
    
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.data_api_url = "https://data-api.binance.vision"
        self.websocket_url = "wss://fstream.binance.com"
        self.session = requests.Session()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_interval = 0.1  # 100ms between requests
        
        # Cache for symbol info
        self._symbol_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None, use_data_api: bool = False) -> Dict:
        """Make rate-limited request to Binance API"""
        self._rate_limit()
        
        base_url = self.data_api_url if use_data_api else self.base_url
        url = f"{base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params or {}, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance Futures API request failed: {e}")
            raise
    
    def get_usdt_perpetual_pairs(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get all USDT-denominated perpetual futures pairs
        
        Returns:
            List of dictionaries containing symbol information:
            - symbol: Trading pair symbol (e.g., 'BTCUSDT')
            - baseAsset: Base asset (e.g., 'BTC')
            - quoteAsset: Quote asset (always 'USDT')
            - status: Trading status
            - price: Current mark price
            - change24h: 24h price change
            - volume24h: 24h volume
            - contractType: 'PERPETUAL'
        """
        
        # Check cache first
        if not force_refresh and self._is_cache_valid():
            logger.info("Returning cached USDT perpetual pairs")
            return self._symbol_cache
        
        try:
            logger.info("Fetching USDT perpetual pairs from Binance Futures API")
            
            # Get exchange info for symbol details
            exchange_info = self._make_request("/fapi/v1/exchangeInfo")
            
            # Get 24hr ticker statistics for price data
            ticker_stats = self._make_request("/fapi/v1/ticker/24hr")
            ticker_dict = {item['symbol']: item for item in ticker_stats}
            
            # Filter for USDT perpetual contracts
            usdt_pairs = []
            
            for symbol_info in exchange_info['symbols']:
                if (symbol_info['quoteAsset'] == 'USDT' and 
                    symbol_info['contractType'] == 'PERPETUAL' and
                    symbol_info['status'] == 'TRADING'):
                    
                    symbol = symbol_info['symbol']
                    ticker = ticker_dict.get(symbol, {})
                    
                    pair_data = {
                        'symbol': symbol,
                        'baseAsset': symbol_info['baseAsset'],
                        'quoteAsset': symbol_info['quoteAsset'],
                        'status': symbol_info['status'],
                        'contractType': symbol_info['contractType'],
                        'price': float(ticker.get('lastPrice', 0)),
                        'change24h': float(ticker.get('priceChangePercent', 0)),
                        'volume24h': float(ticker.get('volume', 0)),
                        'quoteVolume24h': float(ticker.get('quoteVolume', 0)),
                        'high24h': float(ticker.get('highPrice', 0)),
                        'low24h': float(ticker.get('lowPrice', 0)),
                        'openPrice': float(ticker.get('openPrice', 0)),
                        'count': int(ticker.get('count', 0)),
                        # Trading rules
                        'pricePrecision': symbol_info.get('pricePrecision', 2),
                        'quantityPrecision': symbol_info.get('quantityPrecision', 3),
                        'minNotional': self._extract_min_notional(symbol_info.get('filters', [])),
                        'tickSize': self._extract_tick_size(symbol_info.get('filters', [])),
                    }
                    
                    usdt_pairs.append(pair_data)
            
            # Sort by 24h volume (descending)
            usdt_pairs.sort(key=lambda x: x['quoteVolume24h'], reverse=True)
            
            # Update cache
            self._symbol_cache = usdt_pairs
            self._cache_timestamp = time.time()
            
            logger.info(f"Successfully fetched {len(usdt_pairs)} USDT perpetual pairs")
            return usdt_pairs
            
        except Exception as e:
            logger.error(f"Failed to fetch USDT perpetual pairs: {e}")
            return []
    
    def get_historical_klines(self, symbol: str, interval: str, limit: int = 1000, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get historical kline/candlestick data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: Number of klines (max 1500)
            start_time: Start time for data
            end_time: End time for data
            
        Returns:
            DataFrame with OHLCV data
        """
        
        params = {
            'symbol': symbol.upper(),
            'interval': interval,
            'limit': min(limit, 1500)  # Binance max limit
        }
        
        if start_time:
            params['startTime'] = int(start_time.timestamp() * 1000)
        
        if end_time:
            params['endTime'] = int(end_time.timestamp() * 1000)
        
        try:
            logger.info(f"Fetching {limit} {interval} klines for {symbol}")
            
            klines = self._make_request("/fapi/v1/klines", params)
            
            if not klines:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # Convert types
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
            df[numeric_cols] = df[numeric_cols].astype(float)
            
            # Convert timestamps
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Add metadata
            df['symbol'] = symbol
            df['timeframe'] = interval
            df['timestamp'] = df['open_time'].astype(int) // 10**9  # Unix timestamp
            
            # Reorder columns for consistency
            df = df[['timestamp', 'open_time', 'symbol', 'timeframe', 'open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"Successfully fetched {len(df)} klines for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_top_pairs_by_volume(self, limit: int = 50) -> List[Dict]:
        """Get top trading pairs by 24h volume"""
        pairs = self.get_usdt_perpetual_pairs()
        return pairs[:limit] if pairs else []
    
    def search_pairs(self, query: str) -> List[Dict]:
        """Search pairs by symbol or base asset"""
        pairs = self.get_usdt_perpetual_pairs()
        query = query.upper()
        
        return [
            pair for pair in pairs
            if query in pair['symbol'] or query in pair['baseAsset']
        ]
    
    def _is_cache_valid(self) -> bool:
        """Check if symbol cache is still valid"""
        if self._symbol_cache is None or self._cache_timestamp is None:
            return False
        
        return (time.time() - self._cache_timestamp) < self._cache_ttl
    
    def _extract_min_notional(self, filters: List[Dict]) -> float:
        """Extract minimum notional value from symbol filters"""
        for filter_item in filters:
            if filter_item.get('filterType') == 'MIN_NOTIONAL':
                return float(filter_item.get('notional', 0))
        return 0.0
    
    def _extract_tick_size(self, filters: List[Dict]) -> float:
        """Extract tick size from symbol filters"""
        for filter_item in filters:
            if filter_item.get('filterType') == 'PRICE_FILTER':
                return float(filter_item.get('tickSize', 0))
        return 0.0

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    provider = BinanceFuturesProvider()
    
    # Test getting USDT pairs
    print("Fetching USDT perpetual pairs...")
    pairs = provider.get_usdt_perpetual_pairs()
    
    if pairs:
        print(f"\nFound {len(pairs)} USDT perpetual pairs")
        print("\nTop 10 by volume:")
        for i, pair in enumerate(pairs[:10], 1):
            print(f"{i:2d}. {pair['symbol']:12} | "
                  f"Price: ${pair['price']:>10.2f} | "
                  f"24h: {pair['change24h']:>6.2f}% | "
                  f"Volume: ${pair['quoteVolume24h']:>15,.0f}")
    
        # Test fetching historical data for top pair
        if pairs:
            top_symbol = pairs[0]['symbol']
            print(f"\nFetching 1h data for {top_symbol}...")
            
            df = provider.get_historical_klines(top_symbol, '1h', limit=100)
            if not df.empty:
                print(f"Fetched {len(df)} candles")
                print(f"Date range: {df['open_time'].min()} to {df['open_time'].max()}")
                print(f"Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")