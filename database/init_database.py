#!/usr/bin/env python3
"""
PineOpt Database Initialization Script
Creates and initializes the SQLite database with proper schema and validation.
"""

import sqlite3
import os
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseInitializer:
    def __init__(self, db_path="database/pineopt.db"):
        self.db_path = db_path
        self.schema_path = "database/schema.sql"
        self.connection = None
        
    def initialize(self):
        """Initialize the database with full schema and validation."""
        print("🔧 Initializing PineOpt Database...")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to database
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        try:
            # Create schema
            self._create_schema()
            
            # Validate schema
            self._validate_schema()
            
            # Apply minimal migrations for legacy DBs (idempotent)
            self._migrate_legacy_tables()
            
            # Insert sample data for testing
            self._insert_sample_data()
            
            # Run validation tests
            self._run_validation_tests()
            
            print("✅ Database initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            if self.connection:
                self.connection.close()
            return False
        
    def _create_schema(self):
        """Create database schema from SQL file."""
        print("📋 Creating database schema...")
        
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema creation
        self.connection.executescript(schema_sql)
        self.connection.commit()
        print("   ✓ Schema created")
        
    def _validate_schema(self):
        """Validate that all expected tables exist with correct structure."""
        print("🔍 Validating database schema...")
        
        expected_tables = [
            'crypto_ohlc_data',
            'crypto_data_sources', 
            'pine_script_files',
            'strategies',
            'strategy_parameters',
            'backtest_configs',
            'backtest_parameter_sets',
            'backtest_results',
            'backtest_trades',
            'optimization_campaigns',
            'optimization_iterations',
            'validation_tests',
            'conversions',
            'data_sessions',
            'activity_log',
            'system_stats',
            'schema_version'
        ]
        
        cursor = self.connection.cursor()
        
        # Check all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            if table not in actual_tables:
                raise ValueError(f"Missing table: {table}")
        
        print(f"   ✓ All {len(expected_tables)} tables created")
        
        # Check critical indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        critical_indexes = [
            'idx_ohlc_symbol_timeframe_timestamp',
            'idx_backtest_results_strategy_metric',
            'idx_optimization_iterations_campaign'
        ]
        
        for index in critical_indexes:
            if index not in indexes:
                raise ValueError(f"Missing critical index: {index}")
                
        print(f"   ✓ All critical indexes created")
        
    def _column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table (SQLite)."""
        cur = self.connection.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        return column in cols

    def _add_column_if_missing(self, table: str, column: str, column_def: str):
        """ALTER TABLE to add a column if it doesn't exist."""
        if not self._column_exists(table, column):
            print(f"   ↪ Adding missing column: {table}.{column}")
            self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")
            self.connection.commit()

    def _migrate_legacy_tables(self):
        """Ensure older databases are upgraded with required columns used by init."""
        print("🧭 Applying legacy migrations (if needed)...")
        # Detect legacy 'strategies' schema (pre-ORM) and rebuild table to current schema
        try:
            cur = self.connection.cursor()
            cur.execute("PRAGMA table_info(strategies)")
            cols = [row[1] for row in cur.fetchall()]
            is_legacy = ('author' in cols) and ('category' not in cols)
            if is_legacy:
                print("   ↪ Detected legacy 'strategies' schema. Backing up and creating fresh table...")
                self.connection.executescript(
                    """
                    BEGIN TRANSACTION;
                    ALTER TABLE strategies RENAME TO strategies_backup;
                    CREATE TABLE IF NOT EXISTS strategies (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        category VARCHAR(50),
                        pine_script_file_id INTEGER,
                        python_code TEXT,
                        strategy_type VARCHAR(30) DEFAULT 'trend_following',
                        status VARCHAR(20) DEFAULT 'draft',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                    COMMIT;
                    """
                )
                print("   ✓ Backed up legacy table as 'strategies_backup' and created fresh 'strategies'")
        except Exception as e:
            print(f"   ⚠️  strategies legacy rebuild note: {e}")

        # crypto_data_sources.status is used by sample inserts and API filters
        try:
            self._add_column_if_missing('crypto_data_sources', 'status', "VARCHAR(20) DEFAULT 'active'")
        except Exception as e:
            print(f"   ⚠️  crypto_data_sources.status migration note: {e}")

        # Timestamps on crypto_data_sources (best-effort; safe if already present)
        try:
            self._add_column_if_missing('crypto_data_sources', 'last_updated', "DATETIME")
        except Exception as e:
            print(f"   ⚠️  crypto_data_sources.last_updated migration note: {e}")
        try:
            self._add_column_if_missing('crypto_data_sources', 'created_at', "DATETIME")
        except Exception as e:
            print(f"   ⚠️  crypto_data_sources.created_at migration note: {e}")

    def _insert_sample_data(self):
        """Insert sample data for testing."""
        print("📊 Inserting sample data...")
        
        cursor = self.connection.cursor()
        
        # Helper: get existing columns for a table
        def table_columns(table: str):
            cursor.execute(f"PRAGMA table_info({table})")
            return [row[1] for row in cursor.fetchall()]
        
        # Sample Pine Script file
        sample_pine_content = '''
//@version=5
strategy("Sample RSI Strategy", overlay=true)

// Input parameters
rsi_period = input.int(14, title="RSI Period", minval=1, maxval=50)
rsi_upper = input.int(70, title="RSI Upper", minval=50, maxval=95)
rsi_lower = input.int(30, title="RSI Lower", minval=5, maxval=50)

// Calculate RSI
rsi = ta.rsi(close, rsi_period)

// Entry conditions
long_condition = ta.crossover(rsi, rsi_lower)
short_condition = ta.crossunder(rsi, rsi_upper)

// Execute trades
if long_condition
    strategy.entry("Long", strategy.long)
if short_condition
    strategy.close("Long")
'''
        
        # Insert Pine Script file
        file_hash = hashlib.sha256(sample_pine_content.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO pine_script_files 
            (filename, file_content, file_size, file_hash)
            VALUES (?, ?, ?, ?)
        """, ("sample_rsi_strategy.pine", sample_pine_content, len(sample_pine_content), file_hash))
        
        pine_file_id = cursor.lastrowid
        
        # Insert sample strategy (handle legacy without 'category')
        strategy_cols = table_columns('strategies')
        if 'category' in strategy_cols:
            cursor.execute(
                """
                INSERT INTO strategies 
                (name, description, category, pine_script_file_id, strategy_type, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("Sample RSI Strategy", "A simple RSI-based trading strategy for crypto",
                 "RSI", pine_file_id, "mean_reversion", "draft")
            )
        else:
            cursor.execute(
                """
                INSERT INTO strategies 
                (name, description, pine_script_file_id, strategy_type, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("Sample RSI Strategy", "A simple RSI-based trading strategy for crypto",
                 pine_file_id, "mean_reversion", "draft")
            )
        
        strategy_id = cursor.lastrowid
        
        # Insert strategy parameters
        parameters = [
            ("rsi_period", "int", '{"min": 5, "max": 50, "step": 1}', 14, "suggest_int", "rsi_period", "input.int"),
            ("rsi_upper", "int", '{"min": 50, "max": 95, "step": 1}', 70, "suggest_int", "rsi_upper", "input.int"),
            ("rsi_lower", "int", '{"min": 5, "max": 50, "step": 1}', 30, "suggest_int", "rsi_lower", "input.int")
        ]
        
        for param_name, param_type, constraints, default_val, optuna_type, pine_name, pine_type in parameters:
            cursor.execute("""
                INSERT INTO strategy_parameters 
                (strategy_id, parameter_name, parameter_type, constraints_json, 
                 default_value_num, optuna_suggest_type, pine_input_name, pine_input_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (strategy_id, param_name, param_type, constraints, 
                  default_val, optuna_type, pine_name, pine_type))
        
        # Insert sample data source (handle legacy without 'status')
        cds_cols = table_columns('crypto_data_sources')
        if 'status' in cds_cols and 'pandas_freq' in cds_cols and 'ccxt_timeframe' in cds_cols:
            cursor.execute(
                """
                INSERT INTO crypto_data_sources 
                (symbol, exchange, timeframe, pandas_freq, ccxt_timeframe, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("BTCUSDT", "BINANCE", "1h", "H", "1h", "active")
            )
        elif 'pandas_freq' in cds_cols and 'ccxt_timeframe' in cds_cols:
            cursor.execute(
                """
                INSERT INTO crypto_data_sources 
                (symbol, exchange, timeframe, pandas_freq, ccxt_timeframe)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("BTCUSDT", "BINANCE", "1h", "H", "1h")
            )
        else:
            # Minimal legacy form
            cursor.execute(
                """
                INSERT INTO crypto_data_sources 
                (symbol, exchange, timeframe)
                VALUES (?, ?, ?)
                """,
                ("BTCUSDT", "BINANCE", "1h")
            )
        
        # Sample OHLC data (1 week of hourly data)
        base_timestamp = int(datetime(2024, 1, 1).timestamp())
        sample_ohlc = []
        
        for i in range(168):  # 168 hours = 1 week
            timestamp = base_timestamp + (i * 3600)  # Add 1 hour
            price_base = 45000 + (i * 10)  # Trending price
            
            sample_ohlc.append((
                "BTCUSDT", "BINANCE", "1h", 
                timestamp * 1000000,  # Convert to microseconds
                datetime.fromtimestamp(timestamp).isoformat() + "Z",
                price_base, price_base + 100, price_base - 50, price_base + 50,
                1000.0, None, 100, True, False, "sample_data",
                json.dumps({
                    "Open": price_base, "High": price_base + 100, 
                    "Low": price_base - 50, "Close": price_base + 50, "Volume": 1000.0
                })
            ))
        
        cursor.executemany("""
            INSERT INTO crypto_ohlc_data 
            (symbol, exchange, timeframe, timestamp_utc, datetime_str,
             open_price, high_price, low_price, close_price, volume,
             vwap, trades_count, is_complete, has_gaps, source_type, ohlcv_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_ohlc)
        
        # Update system stats
        cursor.execute("UPDATE system_stats SET stat_value = '1' WHERE stat_name = 'total_strategies'")
        cursor.execute(f"UPDATE system_stats SET stat_value = '{len(sample_ohlc)}' WHERE stat_name = 'total_ohlc_records'")
        
        self.connection.commit()
        print(f"   ✓ Inserted 1 strategy with 3 parameters")
        print(f"   ✓ Inserted {len(sample_ohlc)} OHLC records")
        
    def _run_validation_tests(self):
        """Run comprehensive validation tests."""
        print("🧪 Running validation tests...")
        
        cursor = self.connection.cursor()
        
        # Test 1: Basic data integrity
        cursor.execute("SELECT COUNT(*) FROM strategies")
        strategy_count = cursor.fetchone()[0]
        assert strategy_count > 0, "No strategies found"
        
        cursor.execute("SELECT COUNT(*) FROM crypto_ohlc_data")
        ohlc_count = cursor.fetchone()[0]
        assert ohlc_count > 0, "No OHLC data found"
        
        # Test 2: Foreign key constraints work
        cursor.execute("SELECT COUNT(*) FROM strategy_parameters WHERE strategy_id = 1")
        param_count = cursor.fetchone()[0]
        assert param_count > 0, "No parameters found for strategy 1"
        
        # Test 3: Unique constraints work
        try:
            cursor.execute("""
                INSERT INTO crypto_data_sources 
                (symbol, exchange, timeframe, pandas_freq, ccxt_timeframe, status)
                VALUES ('BTCUSDT', 'BINANCE', '1h', 'H', '1h', 'active')
            """)
            assert False, "Unique constraint should have prevented duplicate"
        except sqlite3.IntegrityError:
            pass  # This is expected
        
        # Test 4: Complex query performance
        cursor.execute("""
            SELECT s.name, COUNT(sp.id) as param_count
            FROM strategies s
            LEFT JOIN strategy_parameters sp ON s.id = sp.strategy_id
            GROUP BY s.id
        """)
        results = cursor.fetchall()
        assert len(results) > 0, "Complex query failed"
        
        # Test 5: Time-series data query
        cursor.execute("""
            SELECT COUNT(*) FROM crypto_ohlc_data 
            WHERE symbol = 'BTCUSDT' AND timeframe = '1h'
            ORDER BY timestamp_utc
        """)
        ts_count = cursor.fetchone()[0]
        assert ts_count > 0, "Time-series query failed"
        
        # Test 6: JSON data integrity
        cursor.execute("SELECT ohlcv_json FROM crypto_ohlc_data LIMIT 1")
        json_data = cursor.fetchone()[0]
        parsed_json = json.loads(json_data)
        assert 'Open' in parsed_json, "JSON data structure invalid"
        
        print("   ✅ All validation tests passed")
        
    def get_database_stats(self):
        """Get database statistics."""
        if not self.connection:
            return None
            
        cursor = self.connection.cursor()
        
        stats = {}
        
        # Table counts
        tables = [
            'strategies', 'strategy_parameters', 'crypto_ohlc_data',
            'crypto_data_sources', 'backtest_results', 'optimization_campaigns'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        stats['database_size_bytes'] = cursor.fetchone()[0]
        stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

def main():
    """Main initialization function."""
    print("🚀 PineOpt Database Initialization")
    print("=" * 50)
    
    # Initialize database
    db_init = DatabaseInitializer()
    
    if db_init.initialize():
        # Show stats
        stats = db_init.get_database_stats()
        print("\n📊 Database Statistics:")
        print("-" * 30)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n✨ Database ready at: {os.path.abspath(db_init.db_path)}")
        print("   Ready for Epic 0 validation tests!")
        
    db_init.close()
    
    return db_init.db_path if os.path.exists(db_init.db_path) else None

if __name__ == "__main__":
    main()