"""
PineOpt Unified Database Access Layer
Provides single interface to the unified database

Replaces:
- database/data_access.py (for market data)
- api/strategy_routes.py database access
- Various scattered database calls

Created: August 22, 2025
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class UnifiedDataAccess:
    """Unified database access for all PineOpt data operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize with database path"""
        if db_path is None:
            # Default to unified database in same directory
            self.db_path = Path(__file__).parent / 'pineopt_unified.db'
        else:
            self.db_path = Path(db_path)
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test database connection and schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM market_data LIMIT 1")
                cursor.execute("SELECT COUNT(*) FROM strategies LIMIT 1") 
                cursor.execute("SELECT COUNT(*) FROM market_tickers LIMIT 1")
        except sqlite3.Error as e:
            raise ConnectionError(f"Database connection failed: {e}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    # =====================================================
    # MARKET DATA OPERATIONS
    # =====================================================
    
    def get_market_data(self, symbol: str, timeframe: str, 
                       limit: int = 1000, 
                       start_date: datetime = None,
                       end_date: datetime = None,
                       exchange: str = 'BINANCE') -> pd.DataFrame:
        """
        Get historical OHLC data for symbol/timeframe
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Time interval (e.g., '1h', '1d')
            limit: Maximum number of records
            start_date: Optional start date filter
            end_date: Optional end date filter
            exchange: Exchange name
            
        Returns:
            DataFrame with OHLC data
        """
        with self._get_connection() as conn:
            query = """
                SELECT timestamp_utc, datetime_str, open_price, high_price, 
                       low_price, close_price, volume
                FROM market_data 
                WHERE symbol = ? AND timeframe = ? AND exchange = ?
            """
            params = [symbol, timeframe, exchange]
            
            if start_date:
                query += " AND timestamp_utc >= ?"
                params.append(int(start_date.timestamp() * 1000000))
            
            if end_date:
                query += " AND timestamp_utc <= ?"
                params.append(int(end_date.timestamp() * 1000000))
            
            query += " ORDER BY timestamp_utc DESC LIMIT ?"
            params.append(limit)
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                # Convert timestamp to datetime
                df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], unit='us')
                df = df.sort_values('timestamp_utc').reset_index(drop=True)
            
            return df
    
    def get_available_symbols(self, exchange: str = 'BINANCE') -> List[str]:
        """Get list of available trading symbols"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT symbol FROM market_data 
                WHERE exchange = ? 
                ORDER BY symbol
            """, (exchange,))
            return [row[0] for row in cursor.fetchall()]
    
    def get_available_timeframes(self, symbol: str = None, 
                                exchange: str = 'BINANCE') -> List[str]:
        """Get list of available timeframes for symbol"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT DISTINCT timeframe FROM market_data 
                    WHERE symbol = ? AND exchange = ?
                    ORDER BY timeframe
                """, (symbol, exchange))
            else:
                cursor.execute("""
                    SELECT DISTINCT timeframe FROM market_data 
                    WHERE exchange = ?
                    ORDER BY timeframe
                """, (exchange,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_market_tickers(self, symbols: List[str] = None) -> List[Dict]:
        """Get current market ticker data"""
        with self._get_connection() as conn:
            if symbols:
                placeholders = ','.join(['?'] * len(symbols))
                query = f"SELECT * FROM market_tickers WHERE symbol IN ({placeholders})"
                cursor = conn.cursor()
                cursor.execute(query, symbols)
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM market_tickers ORDER BY symbol")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def save_market_data(self, symbol: str, timeframe: str, data: pd.DataFrame,
                        exchange: str = 'BINANCE') -> int:
        """
        Save OHLC data to database
        
        Args:
            symbol: Trading pair
            timeframe: Time interval
            data: DataFrame with OHLC data
            exchange: Exchange name
            
        Returns:
            Number of records inserted
        """
        if data.empty:
            return 0
        
        # Prepare data for insertion
        records = []
        for _, row in data.iterrows():
            timestamp_utc = int(pd.Timestamp(row['timestamp']).timestamp() * 1000000)
            datetime_str = pd.Timestamp(row['timestamp']).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            records.append((
                symbol, exchange, timeframe, timestamp_utc, datetime_str,
                float(row['open']), float(row['high']), 
                float(row['low']), float(row['close']), 
                float(row.get('volume', 0))
            ))
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR IGNORE INTO market_data
                (symbol, exchange, timeframe, timestamp_utc, datetime_str,
                 open_price, high_price, low_price, close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            
            inserted = cursor.rowcount
            conn.commit()
            
            logger.info(f"Saved {inserted} market data records for {symbol} {timeframe}")
            return inserted
    
    # =====================================================
    # STRATEGY OPERATIONS 
    # =====================================================
    
    def get_strategies(self, status: str = None, limit: int = None) -> List[Dict]:
        """Get list of strategies"""
        with self._get_connection() as conn:
            query = "SELECT * FROM strategy_overview"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_strategy(self, strategy_id: int = None, name: str = None) -> Optional[Dict]:
        """Get single strategy by ID or name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if strategy_id:
                cursor.execute("SELECT * FROM strategies WHERE id = ?", (strategy_id,))
            elif name:
                cursor.execute("SELECT * FROM strategies WHERE name = ?", (name,))
            else:
                raise ValueError("Either strategy_id or name must be provided")
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_strategy(self, name: str, pine_script: str, description: str = None,
                     python_code: str = None, metadata: Dict = None,
                     status: str = 'draft') -> int:
        """
        Save new strategy or update existing
        
        Returns:
            Strategy ID
        """
        if metadata is None:
            metadata = {}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if strategy exists
            cursor.execute("SELECT id FROM strategies WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE strategies 
                    SET description = ?, pine_script = ?, python_code = ?,
                        metadata = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (description, pine_script, python_code, 
                     json.dumps(metadata), status, name))
                strategy_id = existing[0]
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO strategies 
                    (name, description, pine_script, python_code, metadata, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, description, pine_script, python_code,
                     json.dumps(metadata), status))
                strategy_id = cursor.lastrowid
            
            conn.commit()
            logger.info(f"Saved strategy '{name}' with ID {strategy_id}")
            return strategy_id
    
    def delete_strategy(self, strategy_id: int) -> bool:
        """Delete strategy and related data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM strategies WHERE id = ?", (strategy_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted strategy ID {strategy_id}")
            
            return deleted
    
    # =====================================================
    # BACKTEST OPERATIONS
    # =====================================================
    
    def save_backtest_results(self, strategy_id: int, symbol: str, timeframe: str,
                             start_date: datetime, end_date: datetime,
                             results: Dict, metrics: Dict = None,
                             trades: List = None) -> int:
        """Save backtest results"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backtests
                (strategy_id, symbol, timeframe, start_date, end_date,
                 total_return, sharpe_ratio, max_drawdown, win_rate, total_trades,
                 results, metrics, trades)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_id, symbol, timeframe, 
                start_date.date(), end_date.date(),
                results.get('total_return'), results.get('sharpe_ratio'),
                results.get('max_drawdown'), results.get('win_rate'),
                results.get('total_trades'),
                json.dumps(results), json.dumps(metrics or {}), 
                json.dumps(trades or [])
            ))
            
            backtest_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Saved backtest results for strategy {strategy_id}: ID {backtest_id}")
            return backtest_id
    
    def get_backtest_results(self, strategy_id: int = None, 
                           limit: int = 10) -> List[Dict]:
        """Get backtest results"""
        with self._get_connection() as conn:
            query = """
                SELECT b.*, s.name as strategy_name
                FROM backtests b
                JOIN strategies s ON b.strategy_id = s.id
            """
            params = []
            
            if strategy_id:
                query += " WHERE b.strategy_id = ?"
                params.append(strategy_id)
            
            query += " ORDER BY b.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                # Parse JSON fields
                if result['results']:
                    result['results'] = json.loads(result['results'])
                if result['metrics']:
                    result['metrics'] = json.loads(result['metrics'])
                if result['trades']:
                    result['trades'] = json.loads(result['trades'])
                results.append(result)
            
            return results
    
    # =====================================================
    # CONVERSION OPERATIONS
    # =====================================================
    
    def save_conversion_result(self, strategy_id: int, pine_script: str,
                              python_code: str = None, success: bool = False,
                              error_message: str = None, 
                              conversion_time_ms: int = None) -> int:
        """Save conversion attempt result"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversions
                (strategy_id, input_pine, output_python, conversion_success,
                 error_message, conversion_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (strategy_id, pine_script, python_code, success,
                 error_message, conversion_time_ms))
            
            conversion_id = cursor.lastrowid
            conn.commit()
            
            return conversion_id
    
    def get_conversion_history(self, strategy_id: int) -> List[Dict]:
        """Get conversion history for strategy"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversions 
                WHERE strategy_id = ? 
                ORDER BY created_at DESC
            """, (strategy_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # =====================================================
    # UTILITY OPERATIONS
    # =====================================================
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['market_data', 'market_tickers', 'strategies', 
                     'backtests', 'conversions', 'ai_analysis']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Market data stats
            cursor.execute("""
                SELECT COUNT(DISTINCT symbol), COUNT(DISTINCT timeframe),
                       MIN(datetime_str), MAX(datetime_str)
                FROM market_data
            """)
            
            symbols, timeframes, min_date, max_date = cursor.fetchone()
            stats.update({
                'unique_symbols': symbols,
                'unique_timeframes': timeframes,
                'data_date_range': f"{min_date} to {max_date}" if min_date else "No data"
            })
            
            return stats
    
    def optimize_database(self):
        """Run database optimization"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            conn.commit()
            
            logger.info("Database optimization completed")
    
    def close(self):
        """Cleanup method (connection auto-closes with context manager)"""
        pass


# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

def get_data_access(db_path: str = None) -> UnifiedDataAccess:
    """Get UnifiedDataAccess instance"""
    return UnifiedDataAccess(db_path)

def get_market_data(symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
    """Quick function to get market data"""
    da = get_data_access()
    return da.get_market_data(symbol, timeframe, limit)

def get_strategies() -> List[Dict]:
    """Quick function to get all strategies"""
    da = get_data_access()
    return da.get_strategies()

# =====================================================
# CLI TESTING
# =====================================================

if __name__ == "__main__":
    # Test the unified data access
    import sys
    
    try:
        da = UnifiedDataAccess()
        
        print("🧪 Testing Unified Data Access...")
        
        # Test database stats
        stats = da.get_database_stats()
        print(f"📊 Database Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value:,}" if isinstance(value, int) else f"  {key}: {value}")
        
        # Test market data
        symbols = da.get_available_symbols()
        print(f"\n📈 Available symbols: {len(symbols)} (showing first 10)")
        print(f"  {symbols[:10]}")
        
        if symbols:
            # Get data for first symbol
            timeframes = da.get_available_timeframes(symbols[0])
            print(f"\n⏰ Timeframes for {symbols[0]}: {timeframes}")
            
            if timeframes:
                df = da.get_market_data(symbols[0], timeframes[0], limit=5)
                print(f"\n💹 Sample data for {symbols[0]} {timeframes[0]}:")
                print(df.head())
        
        # Test strategies
        strategies = da.get_strategies(limit=5)
        print(f"\n🧠 Strategies: {len(strategies)} total (showing first 5)")
        for strategy in strategies[:5]:
            print(f"  {strategy['name']} - {strategy['status']} - Created: {strategy['created_at']}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)