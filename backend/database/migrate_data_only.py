#!/usr/bin/env python3
"""
Simple data migration script for PineOpt
Assumes unified database already exists with schema
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_market_data():
    """Migrate crypto_ohlc_data to market_data"""
    logger.info("Migrating market data...")
    
    source = sqlite3.connect('database/pineopt.db')
    target = sqlite3.connect('database/pineopt_unified.db')
    
    # Get data from source
    cursor = source.cursor()
    cursor.execute("""
        SELECT symbol, exchange, timeframe, timestamp_utc, datetime_str,
               open_price, high_price, low_price, close_price, volume
        FROM crypto_ohlc_data
        ORDER BY symbol, timeframe, timestamp_utc
    """)
    
    rows = cursor.fetchall()
    logger.info(f"Found {len(rows)} market data records")
    
    # Insert into target
    target_cursor = target.cursor()
    target_cursor.executemany("""
        INSERT OR IGNORE INTO market_data 
        (symbol, exchange, timeframe, timestamp_utc, datetime_str,
         open_price, high_price, low_price, close_price, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    
    target.commit()
    source.close()
    target.close()
    
    logger.info(f"✅ Migrated {len(rows)} market data records")

def migrate_strategies():
    """Migrate strategies"""
    logger.info("Migrating strategies...")
    
    source = sqlite3.connect('api/strategies.db')
    target = sqlite3.connect('database/pineopt_unified.db')
    
    cursor = source.cursor()
    cursor.execute("""
        SELECT name, description, pine_source, python_code, 
               metadata, created_at, updated_at
        FROM strategies
    """)
    
    rows = cursor.fetchall()
    logger.info(f"Found {len(rows)} strategies")
    
    target_cursor = target.cursor()
    target_cursor.executemany("""
        INSERT OR IGNORE INTO strategies
        (name, description, pine_script, python_code, 
         metadata, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    
    target.commit()
    source.close()
    target.close()
    
    logger.info(f"✅ Migrated {len(rows)} strategies")

def migrate_market_tickers():
    """Migrate market tickers"""
    logger.info("Migrating market tickers...")
    
    source = sqlite3.connect('market_data.db')
    target = sqlite3.connect('database/pineopt_unified.db')
    
    cursor = source.cursor()
    cursor.execute("""
        SELECT symbol, price, change_24h, change_percent_24h,
               volume_24h, high_24h, low_24h, last_updated
        FROM market_tickers
    """)
    
    rows = cursor.fetchall()
    logger.info(f"Found {len(rows)} market tickers")
    
    target_cursor = target.cursor()
    target_cursor.executemany("""
        INSERT OR REPLACE INTO market_tickers
        (symbol, price, change_24h, change_percent_24h,
         volume_24h, high_24h, low_24h, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    
    target.commit()
    source.close()
    target.close()
    
    logger.info(f"✅ Migrated {len(rows)} market tickers")

if __name__ == "__main__":
    migrate_market_data()
    migrate_strategies()
    migrate_market_tickers()
    
    # Validate
    conn = sqlite3.connect('database/pineopt_unified.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM market_data")
    market_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM strategies")
    strategy_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM market_tickers")
    ticker_count = cursor.fetchone()[0]
    
    conn.close()
    
    logger.info("🎉 Migration completed!")
    logger.info(f"  Market data: {market_count:,} records")
    logger.info(f"  Strategies: {strategy_count} records")
    logger.info(f"  Market tickers: {ticker_count} records")