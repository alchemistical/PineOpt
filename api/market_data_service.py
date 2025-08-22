"""
Real Market Data Service - Binance Integration
Provides live and historical cryptocurrency market data
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import ccxt
import requests
from binance import Client, BinanceSocketManager
import sqlite3
import threading
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketTicker:
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

@dataclass
class HistoricalData:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime

class MarketDataService:
    def __init__(self):
        self.binance_client = None
        self.socket_manager = None
        self.ccxt_exchange = ccxt.binance({
            'sandbox': False,
            'rateLimit': 1200,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.price_cache = {}
        self.cache_expiry = 30  # seconds
        self.db_path = "market_data.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize market data database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create market data cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_tickers (
                symbol TEXT PRIMARY KEY,
                price REAL,
                change_24h REAL,
                change_percent_24h REAL,
                volume_24h REAL,
                high_24h REAL,
                low_24h REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create historical data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timeframe TEXT,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                timestamp TIMESTAMP,
                UNIQUE(symbol, timeframe, timestamp)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Market data database initialized")

    def get_top_crypto_pairs(self, limit: int = 20) -> List[str]:
        """Get top cryptocurrency trading pairs by volume"""
        try:
            tickers = self.ccxt_exchange.fetch_tickers()
            
            # Filter USDT pairs and sort by volume
            usdt_pairs = [(symbol, ticker) for symbol, ticker in tickers.items() 
                         if '/USDT' in symbol and ticker['quoteVolume']]
            
            # Sort by 24h volume descending
            sorted_pairs = sorted(usdt_pairs, 
                                key=lambda x: x[1]['quoteVolume'], 
                                reverse=True)
            
            return [pair[0] for pair in sorted_pairs[:limit]]
            
        except Exception as e:
            logger.error(f"Error fetching top crypto pairs: {e}")
            # Return fallback list
            return [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 
                'SOL/USDT', 'XRP/USDT', 'DOT/USDT', 'DOGE/USDT',
                'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT'
            ]

    def fetch_live_ticker(self, symbol: str) -> Optional[MarketTicker]:
        """Fetch live ticker data for a symbol"""
        try:
            # Check cache first
            cache_key = f"ticker_{symbol}"
            if cache_key in self.price_cache:
                cached_data, cache_time = self.price_cache[cache_key]
                if time.time() - cache_time < self.cache_expiry:
                    return cached_data
            
            # Fetch from Binance via CCXT
            ticker = self.ccxt_exchange.fetch_ticker(symbol)
            
            market_ticker = MarketTicker(
                symbol=symbol,
                price=ticker['last'],
                change_24h=ticker['change'] or 0,
                change_percent_24h=ticker['percentage'] or 0,
                volume_24h=ticker['quoteVolume'] or 0,
                high_24h=ticker['high'] or ticker['last'],
                low_24h=ticker['low'] or ticker['last'],
                timestamp=datetime.fromtimestamp(ticker['timestamp'] / 1000)
            )
            
            # Cache the result
            self.price_cache[cache_key] = (market_ticker, time.time())
            
            # Store in database
            self._store_ticker_data(market_ticker)
            
            return market_ticker
            
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return self._get_cached_ticker(symbol)

    def fetch_multiple_tickers(self, symbols: List[str]) -> Dict[str, MarketTicker]:
        """Fetch multiple tickers efficiently"""
        try:
            # Use fetchTickers for bulk request
            tickers = self.ccxt_exchange.fetch_tickers(symbols)
            
            result = {}
            for symbol in symbols:
                if symbol in tickers:
                    ticker = tickers[symbol]
                    market_ticker = MarketTicker(
                        symbol=symbol,
                        price=ticker['last'],
                        change_24h=ticker['change'] or 0,
                        change_percent_24h=ticker['percentage'] or 0,
                        volume_24h=ticker['quoteVolume'] or 0,
                        high_24h=ticker['high'] or ticker['last'],
                        low_24h=ticker['low'] or ticker['last'],
                        timestamp=datetime.fromtimestamp(ticker['timestamp'] / 1000)
                    )
                    result[symbol] = market_ticker
                    
                    # Cache and store
                    cache_key = f"ticker_{symbol}"
                    self.price_cache[cache_key] = (market_ticker, time.time())
                    self._store_ticker_data(market_ticker)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching multiple tickers: {e}")
            # Fallback to individual requests
            result = {}
            for symbol in symbols:
                ticker = self.fetch_live_ticker(symbol)
                if ticker:
                    result[symbol] = ticker
            return result

    def fetch_historical_data(self, symbol: str, timeframe: str = '1h', 
                            days: int = 30) -> List[HistoricalData]:
        """Fetch historical OHLCV data"""
        try:
            # Calculate timestamp for 'days' ago
            since = self.ccxt_exchange.milliseconds() - (days * 24 * 60 * 60 * 1000)
            
            # Fetch OHLCV data
            ohlcv = self.ccxt_exchange.fetch_ohlcv(symbol, timeframe, since)
            
            historical_data = []
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle
                
                hist_data = HistoricalData(
                    symbol=symbol,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                    timestamp=datetime.fromtimestamp(timestamp / 1000)
                )
                historical_data.append(hist_data)
                
                # Store in database
                self._store_historical_data(hist_data, timeframe)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return self._get_cached_historical_data(symbol, timeframe, days)

    def _store_ticker_data(self, ticker: MarketTicker):
        """Store ticker data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO market_tickers 
                (symbol, price, change_24h, change_percent_24h, volume_24h, 
                 high_24h, low_24h, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker.symbol, ticker.price, ticker.change_24h, 
                ticker.change_percent_24h, ticker.volume_24h,
                ticker.high_24h, ticker.low_24h, ticker.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing ticker data: {e}")

    def _store_historical_data(self, hist_data: HistoricalData, timeframe: str):
        """Store historical data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO historical_data 
                (symbol, timeframe, open_price, high_price, low_price, 
                 close_price, volume, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                hist_data.symbol, timeframe, hist_data.open, hist_data.high,
                hist_data.low, hist_data.close, hist_data.volume, hist_data.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing historical data: {e}")

    def _get_cached_ticker(self, symbol: str) -> Optional[MarketTicker]:
        """Get cached ticker from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT symbol, price, change_24h, change_percent_24h, volume_24h,
                       high_24h, low_24h, last_updated
                FROM market_tickers 
                WHERE symbol = ?
                ORDER BY last_updated DESC
                LIMIT 1
            """, (symbol,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return MarketTicker(
                    symbol=row[0], price=row[1], change_24h=row[2],
                    change_percent_24h=row[3], volume_24h=row[4],
                    high_24h=row[5], low_24h=row[6],
                    timestamp=datetime.fromisoformat(row[7])
                )
            
        except Exception as e:
            logger.error(f"Error getting cached ticker: {e}")
            
        return None

    def _get_cached_historical_data(self, symbol: str, timeframe: str, 
                                  days: int) -> List[HistoricalData]:
        """Get cached historical data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT symbol, open_price, high_price, low_price, close_price, 
                       volume, timestamp
                FROM historical_data 
                WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (symbol, timeframe, since))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                HistoricalData(
                    symbol=row[0], open=row[1], high=row[2], low=row[3],
                    close=row[4], volume=row[5],
                    timestamp=datetime.fromisoformat(row[6])
                )
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting cached historical data: {e}")
            return []

    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview with key metrics"""
        try:
            top_pairs = self.get_top_crypto_pairs(12)
            tickers = self.fetch_multiple_tickers(top_pairs)
            
            # Calculate market metrics
            total_volume = sum(ticker.volume_24h for ticker in tickers.values())
            gainers = sum(1 for ticker in tickers.values() if ticker.change_percent_24h > 0)
            losers = len(tickers) - gainers
            
            return {
                'total_pairs': len(tickers),
                'total_volume_24h': total_volume,
                'gainers': gainers,
                'losers': losers,
                'tickers': {symbol: {
                    'symbol': ticker.symbol,
                    'price': ticker.price,
                    'change': ticker.change_24h,
                    'change_percent': ticker.change_percent_24h,
                    'volume': ticker.volume_24h,
                    'high': ticker.high_24h,
                    'low': ticker.low_24h
                } for symbol, ticker in tickers.items()},
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'error': str(e),
                'total_pairs': 0,
                'total_volume_24h': 0,
                'gainers': 0,
                'losers': 0,
                'tickers': {},
                'last_updated': datetime.now().isoformat()
            }

# Global market data service instance
market_service = MarketDataService()