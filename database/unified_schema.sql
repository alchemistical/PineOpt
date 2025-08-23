-- PineOpt Unified Database Schema
-- Consolidates pineopt.db, strategies.db, and market_data.db into single database
-- Created: August 22, 2025

-- =====================================================
-- MARKET DATA TABLES
-- =====================================================

-- Historical OHLC data (from pineopt.db: crypto_ohlc_data)
CREATE TABLE market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core identifiers
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL DEFAULT 'BINANCE', 
    timeframe VARCHAR(10) NOT NULL,
    
    -- Timestamp handling (UTC only to avoid timezone bugs)
    timestamp_utc BIGINT NOT NULL,         -- Unix timestamp (microseconds) - pandas compatible
    datetime_str VARCHAR(25) NOT NULL,     -- ISO format: '2024-01-01T12:00:00.000Z' - human readable
    
    -- OHLCV data - HIGH PRECISION for financial calculations
    open_price DECIMAL(30,15) NOT NULL,    -- Prevents float precision bugs
    high_price DECIMAL(30,15) NOT NULL,
    low_price DECIMAL(30,15) NOT NULL, 
    close_price DECIMAL(30,15) NOT NULL,
    volume DECIMAL(30,8) DEFAULT 0,
    
    -- Additional fields for advanced analysis
    quote_asset_volume DECIMAL(30,8) DEFAULT 0,
    taker_buy_base_asset_volume DECIMAL(30,8) DEFAULT 0,
    taker_buy_quote_asset_volume DECIMAL(30,8) DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(symbol, exchange, timeframe, timestamp_utc)
);

-- Real-time market tickers (from market_data.db: market_tickers)
CREATE TABLE market_tickers (
    symbol VARCHAR(20) PRIMARY KEY,
    price DECIMAL(30,15),
    change_24h DECIMAL(30,15),
    change_percent_24h DECIMAL(10,4),
    volume_24h DECIMAL(30,8),
    high_24h DECIMAL(30,15),
    low_24h DECIMAL(30,15),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- STRATEGY MANAGEMENT TABLES
-- =====================================================

-- Converted strategies (from strategies.db: strategies)
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    pine_script TEXT NOT NULL,
    python_code TEXT,
    metadata JSON,
    status VARCHAR(20) DEFAULT 'draft' CHECK(status IN ('draft', 'converted', 'tested', 'validated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Strategy parameters (from strategies.db: strategy_parameters)
CREATE TABLE strategy_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_type VARCHAR(10) NOT NULL CHECK(parameter_type IN ('int', 'float', 'bool', 'str', 'list')),
    default_value TEXT,
    min_value DECIMAL(20,8),
    max_value DECIMAL(20,8),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- =====================================================
-- BACKTESTING & ANALYSIS TABLES
-- =====================================================

-- Backtest results
CREATE TABLE backtests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL DEFAULT 'BINANCE',
    timeframe VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20,8) DEFAULT 10000.0,
    
    -- Results summary
    total_return DECIMAL(10,4),
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(10,4),
    win_rate DECIMAL(6,4),
    total_trades INTEGER,
    
    -- Detailed results (JSON)
    results JSON,
    metrics JSON,
    trades JSON,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- Conversion history and logs
CREATE TABLE conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER,
    conversion_type VARCHAR(50) DEFAULT 'pine_to_python',
    input_pine TEXT NOT NULL,
    output_python TEXT,
    conversion_success BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    conversion_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE SET NULL
);

-- AI Analysis results
CREATE TABLE ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_results JSON,
    confidence_score DECIMAL(4,3),
    analysis_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Market data indexes
CREATE INDEX idx_market_data_symbol_timeframe ON market_data(symbol, timeframe);
CREATE INDEX idx_market_data_timestamp ON market_data(timestamp_utc);
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp_utc);
CREATE INDEX idx_market_data_exchange_symbol ON market_data(exchange, symbol);

-- Strategy indexes
CREATE INDEX idx_strategies_name ON strategies(name);
CREATE INDEX idx_strategies_status ON strategies(status);
CREATE INDEX idx_strategies_created ON strategies(created_at);

-- Parameter indexes
CREATE INDEX idx_strategy_parameters_strategy_id ON strategy_parameters(strategy_id);
CREATE INDEX idx_strategy_parameters_name ON strategy_parameters(parameter_name);

-- Backtest indexes
CREATE INDEX idx_backtests_strategy_id ON backtests(strategy_id);
CREATE INDEX idx_backtests_symbol ON backtests(symbol);
CREATE INDEX idx_backtests_timeframe ON backtests(timeframe);
CREATE INDEX idx_backtests_dates ON backtests(start_date, end_date);

-- Conversion indexes
CREATE INDEX idx_conversions_strategy_id ON conversions(strategy_id);
CREATE INDEX idx_conversions_type ON conversions(conversion_type);
CREATE INDEX idx_conversions_success ON conversions(conversion_success);

-- Analysis indexes
CREATE INDEX idx_ai_analysis_strategy_id ON ai_analysis(strategy_id);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Strategy overview with conversion status
CREATE VIEW strategy_overview AS
SELECT 
    s.*,
    COUNT(c.id) as conversion_attempts,
    MAX(c.conversion_success) as has_successful_conversion,
    COUNT(b.id) as backtest_count,
    MAX(b.total_return) as best_return
FROM strategies s
LEFT JOIN conversions c ON s.id = c.strategy_id
LEFT JOIN backtests b ON s.id = b.strategy_id
GROUP BY s.id;

-- Latest market data per symbol/timeframe
CREATE VIEW latest_market_data AS
SELECT DISTINCT
    symbol,
    timeframe,
    exchange,
    close_price as current_price,
    volume,
    datetime_str as last_update
FROM market_data md1
WHERE timestamp_utc = (
    SELECT MAX(timestamp_utc) 
    FROM market_data md2 
    WHERE md1.symbol = md2.symbol 
    AND md1.timeframe = md2.timeframe
);

-- =====================================================
-- TRIGGERS FOR DATA INTEGRITY
-- =====================================================

-- Auto-update strategy updated_at timestamp
CREATE TRIGGER update_strategy_timestamp 
    AFTER UPDATE ON strategies
    FOR EACH ROW
    BEGIN
        UPDATE strategies SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;

-- Validate market data constraints
CREATE TRIGGER validate_market_data
    BEFORE INSERT ON market_data
    FOR EACH ROW
    BEGIN
        -- Ensure prices are positive
        SELECT CASE
            WHEN NEW.open_price <= 0 THEN RAISE(ABORT, 'Open price must be positive')
            WHEN NEW.high_price <= 0 THEN RAISE(ABORT, 'High price must be positive')
            WHEN NEW.low_price <= 0 THEN RAISE(ABORT, 'Low price must be positive')
            WHEN NEW.close_price <= 0 THEN RAISE(ABORT, 'Close price must be positive')
            WHEN NEW.volume < 0 THEN RAISE(ABORT, 'Volume cannot be negative')
        END;
        
        -- Ensure OHLC relationships are valid
        SELECT CASE
            WHEN NEW.high_price < NEW.open_price THEN RAISE(ABORT, 'High must be >= Open')
            WHEN NEW.high_price < NEW.close_price THEN RAISE(ABORT, 'High must be >= Close')
            WHEN NEW.low_price > NEW.open_price THEN RAISE(ABORT, 'Low must be <= Open')
            WHEN NEW.low_price > NEW.close_price THEN RAISE(ABORT, 'Low must be <= Close')
        END;
    END;

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Insert metadata about database version
CREATE TABLE database_metadata (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO database_metadata (key, value) VALUES 
    ('schema_version', '1.0'),
    ('created_date', datetime('now')),
    ('description', 'PineOpt unified database - consolidates market data, strategies, and backtests');

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

/*
DATABASE DESIGN PRINCIPLES:

1. NORMALIZATION: 3NF normalized to eliminate redundancy
2. PRECISION: DECIMAL types for financial data to avoid float errors
3. CONSTRAINTS: Foreign keys and check constraints for data integrity
4. INDEXING: Comprehensive indexes for query performance
5. FLEXIBILITY: JSON fields for extensible metadata
6. AUDITABILITY: Timestamps and conversion logs
7. SCALABILITY: Designed to handle millions of OHLC records

MIGRATION NOTES:
- crypto_ohlc_data -> market_data (schema preserved)
- strategies table enhanced with status and JSON metadata
- strategy_parameters preserved with foreign key constraints
- market_tickers preserved for real-time data
- New tables added for backtests, conversions, AI analysis

PERFORMANCE CONSIDERATIONS:
- Partitioning by symbol/timeframe for large datasets
- Composite indexes for common query patterns
- Views for complex joins
- Triggers for data validation and maintenance
*/