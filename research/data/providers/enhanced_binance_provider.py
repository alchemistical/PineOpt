"""
Enhanced Binance Provider with Database Integration
Fetches crypto data and stores directly in PineOpt database
"""

import logging
import requests
import sys
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import time
import json

# Add database module to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from database.data_access import crypto_data, activity_data
from database.models import db_manager

logger = logging.getLogger(__name__)

class EnhancedBinanceProvider:
    """Enhanced Binance provider with database integration and bulk historical fetching."""
    
    def __init__(self):
        """Initialize enhanced Binance provider."""
        self.base_url = "https://api.binance.com/api/v3"
        self.max_bars_per_request = 1000  # Binance limit
        self.rate_limit_delay = 0.1  # Seconds between requests
        
    def _map_timeframe(self, timeframe: str) -> str:
        """Map timeframe to Binance format."""
        timeframe_map = {
            '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
            '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
        }
        return timeframe_map.get(timeframe, '1h')
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe to minutes for calculations."""
        timeframe_minutes = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
            '1d': 1440, '3d': 4320, '1w': 10080, '1M': 43200
        }
        return timeframe_minutes.get(timeframe, 60)
    
    def _convert_binance_to_ohlc(self, binance_data: List) -> List[Dict]:
        """Convert Binance klines data to our OHLC format."""
        ohlc_records = []
        
        for kline in binance_data:
            # Binance kline format: [timestamp, open, high, low, close, volume, ...]
            timestamp_ms = int(kline[0])
            timestamp_us = timestamp_ms * 1000  # Convert to microseconds
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            
            ohlc_record = {
                'timestamp_utc': timestamp_us,
                'datetime_str': dt.isoformat() + 'Z',
                'open_price': float(kline[1]),
                'high_price': float(kline[2]),
                'low_price': float(kline[3]),
                'close_price': float(kline[4]),
                'volume': float(kline[5]),
                'trades_count': int(kline[8]) if len(kline) > 8 else 0
            }
            ohlc_records.append(ohlc_record)
        
        return ohlc_records
    
    def fetch_recent_ohlc(
        self,
        symbol: str,
        exchange: str = "BINANCE",
        timeframe: str = '1h',
        n_bars: int = 1000,
        store_in_db: bool = True
    ) -> Dict:
        """Fetch recent OHLC data from Binance and optionally store in database."""
        try:
            logger.info(f"Fetching {n_bars} bars of {symbol} {timeframe} from Binance...")
            
            # Map timeframe and prepare request
            binance_interval = self._map_timeframe(timeframe)
            limit = min(n_bars, self.max_bars_per_request)
            
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol.upper(),
                'interval': binance_interval,
                'limit': limit
            }
            
            # Make API request
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            binance_klines = response.json()
            
            if not binance_klines:
                return {
                    'success': False,
                    'error': 'No data returned from Binance',
                    'count': 0
                }
            
            # Convert to our format
            ohlc_data = self._convert_binance_to_ohlc(binance_klines)
            
            # Store in database if requested
            records_stored = 0
            if store_in_db and ohlc_data:
                records_stored = crypto_data.store_ohlc_data(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    ohlc_data=ohlc_data,
                    source_type="binance_api"
                )
                
                # Log activity
                activity_data.update_system_stat(
                    'binance_fetch_count', 
                    str(int(activity_data.get_system_stats().get('binance_fetch_count', '0')) + 1),
                    'data'
                )
            
            result = {
                'success': True,
                'symbol': symbol,
                'exchange': exchange,
                'timeframe': timeframe,
                'ohlc': ohlc_data,
                'count': len(ohlc_data),
                'records_stored': records_stored,
                'source': 'binance_api',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Fetched {len(ohlc_data)} bars, stored {records_stored} new records")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API request failed: {e}")
            return {
                'success': False,
                'error': f'Binance API error: {str(e)}',
                'count': 0
            }
        except Exception as e:
            logger.error(f"Error fetching Binance data: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'count': 0
            }
    
    def fetch_historical_bulk(
        self,
        symbol: str,
        exchange: str = "BINANCE",
        timeframe: str = '1h',
        start_date: datetime = None,
        end_date: datetime = None,
        max_bars: int = 100000
    ) -> Dict:
        """Fetch bulk historical data in chunks and store in database."""
        try:
            # Default to 1 year of data if no dates specified
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            logger.info(f"Fetching bulk historical data: {symbol} from {start_date} to {end_date}")
            
            # Calculate total bars needed
            timeframe_minutes = self._timeframe_to_minutes(timeframe)
            total_minutes = int((end_date - start_date).total_seconds() / 60)
            estimated_bars = total_minutes // timeframe_minutes
            
            if estimated_bars > max_bars:
                logger.warning(f"Estimated {estimated_bars} bars exceeds limit of {max_bars}")
                estimated_bars = max_bars
            
            # Fetch data in chunks
            all_ohlc_data = []
            total_stored = 0
            current_end_time = end_date
            
            while len(all_ohlc_data) < estimated_bars and current_end_time > start_date:
                # Calculate chunk size
                remaining_bars = estimated_bars - len(all_ohlc_data)
                chunk_size = min(remaining_bars, self.max_bars_per_request)
                
                # Prepare chunk request
                end_timestamp = int(current_end_time.timestamp() * 1000)
                
                url = f"{self.base_url}/klines"
                params = {
                    'symbol': symbol.upper(),
                    'interval': self._map_timeframe(timeframe),
                    'limit': chunk_size,
                    'endTime': end_timestamp
                }
                
                # Make request
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                chunk_klines = response.json()
                
                if not chunk_klines:
                    break
                
                # Convert and add to collection
                chunk_ohlc = self._convert_binance_to_ohlc(chunk_klines)
                all_ohlc_data.extend(chunk_ohlc)
                
                # Store chunk in database
                chunk_stored = crypto_data.store_ohlc_data(
                    symbol=symbol,
                    exchange=exchange,
                    timeframe=timeframe,
                    ohlc_data=chunk_ohlc,
                    source_type="binance_bulk"
                )
                total_stored += chunk_stored
                
                # Update for next iteration
                if chunk_klines:
                    # Move end time to before the earliest bar in this chunk
                    earliest_timestamp = int(chunk_klines[0][0])
                    current_end_time = datetime.fromtimestamp(earliest_timestamp / 1000) - timedelta(minutes=timeframe_minutes)
                
                logger.info(f"Fetched chunk: {len(chunk_ohlc)} bars, stored {chunk_stored} new")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                # Stop if we've reached the start date
                if current_end_time <= start_date:
                    break
            
            # Remove duplicates and sort
            all_ohlc_data = sorted(all_ohlc_data, key=lambda x: x['timestamp_utc'])
            
            result = {
                'success': True,
                'symbol': symbol,
                'exchange': exchange,
                'timeframe': timeframe,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_bars_fetched': len(all_ohlc_data),
                'total_bars_stored': total_stored,
                'source': 'binance_bulk',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Bulk fetch complete: {len(all_ohlc_data)} total bars, {total_stored} stored")
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk historical fetch: {e}")
            return {
                'success': False,
                'error': f'Bulk fetch error: {str(e)}',
                'total_bars_fetched': 0,
                'total_bars_stored': 0
            }
    
    def sync_data(
        self,
        symbol: str,
        exchange: str = "BINANCE", 
        timeframe: str = '1h',
        days_back: int = 7
    ) -> Dict:
        """Synchronize recent data to fill any gaps."""
        try:
            logger.info(f"Syncing {symbol} data for last {days_back} days...")
            
            # Get the latest timestamp in database
            df = crypto_data.get_ohlc_data_as_dataframe(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                limit=1
            )
            
            if not df.empty:
                latest_db_time = df.index[-1].to_pydatetime()
                logger.info(f"Latest data in DB: {latest_db_time}")
            else:
                # No data in DB, sync last week
                latest_db_time = datetime.utcnow() - timedelta(days=days_back)
                logger.info(f"No data in DB, syncing from {latest_db_time}")
            
            # Fetch data from latest DB time to now
            sync_result = self.fetch_historical_bulk(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start_date=latest_db_time,
                end_date=datetime.utcnow(),
                max_bars=days_back * 24  # Assuming hourly data
            )
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error syncing data: {e}")
            return {
                'success': False,
                'error': f'Sync error: {str(e)}',
                'total_bars_stored': 0
            }
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols from Binance."""
        try:
            url = f"{self.base_url}/exchangeInfo"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            exchange_info = response.json()
            symbols = []
            
            for symbol_info in exchange_info.get('symbols', []):
                if symbol_info.get('status') == 'TRADING':
                    symbols.append(symbol_info.get('symbol'))
            
            # Filter to popular USDT pairs
            usdt_symbols = [s for s in symbols if s.endswith('USDT')]
            popular_symbols = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
                'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT'
            ]
            
            # Return popular symbols that are available
            available_popular = [s for s in popular_symbols if s in usdt_symbols]
            return available_popular[:20]  # Top 20
            
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return ['BTCUSDT', 'ETHUSDT']  # Fallback

# Global instance
enhanced_binance_provider = EnhancedBinanceProvider()

def get_enhanced_binance_provider():
    """Get the global enhanced Binance provider instance."""
    return enhanced_binance_provider