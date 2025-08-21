-- =============================================================================
-- PineOpt Crypto Strategy Lab Database Schema
-- Optimized for pandas, backtrader, and optimization libraries
-- =============================================================================

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- =======================
-- CRYPTO MARKET DATA
-- =======================

-- Historical OHLC data - optimized for pandas/backtrader compatibility
CREATE TABLE IF NOT EXISTS crypto_ohlc_data (
    id INTEGER PRIMARY KEY,
    
    -- Core identifiers
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL, 
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
    vwap DECIMAL(30,15),                   -- Volume Weighted Average Price
    trades_count INTEGER DEFAULT 0,        -- Number of trades in this bar
    
    -- Data quality flags
    is_complete BOOLEAN DEFAULT TRUE,      -- False for partial bars
    has_gaps BOOLEAN DEFAULT FALSE,        -- True if data has missing periods
    source_type VARCHAR(20) NOT NULL,      -- 'binance_api', 'file_upload', 'tardis'
    
    -- Backtrader compatibility - store as JSON for easy DataFrame conversion
    ohlcv_json TEXT,                       -- {"Open": 45000.5, "High": 45100.0, ...} - exact column names backtrader expects
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate bars
    UNIQUE(symbol, exchange, timeframe, timestamp_utc)
);

-- Data source metadata with library-specific configurations
CREATE TABLE IF NOT EXISTS crypto_data_sources (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    
    -- Data range info
    total_records INTEGER DEFAULT 0,
    first_timestamp_utc BIGINT,            -- Unix timestamp for easy pandas operations
    last_timestamp_utc BIGINT,
    price_min DECIMAL(30,15),
    price_max DECIMAL(30,15),
    
    -- Library compatibility settings
    pandas_freq VARCHAR(10),               -- 'H', 'D', '5T' - pandas frequency strings
    backtrader_compression INTEGER,        -- 1, 5, 60 - backtrader compression values
    ccxt_timeframe VARCHAR(10),            -- '1h', '1d' - ccxt timeframe format
    
    -- Data quality metrics
    completeness_pct DECIMAL(5,2),         -- % of expected bars present
    gap_count INTEGER DEFAULT 0,           -- Number of missing periods
    
    status VARCHAR(20) DEFAULT 'active',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol, exchange, timeframe)
);

-- =======================
-- STRATEGY MANAGEMENT
-- =======================

-- Pine Script files storage
CREATE TABLE IF NOT EXISTS pine_script_files (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),                -- Actual file path on disk
    file_content TEXT NOT NULL,            -- Pine Script content
    file_size INTEGER,
    file_hash VARCHAR(64),                 -- SHA256 for deduplication
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Strategy definitions
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),                  -- 'RSI', 'MA', 'Bollinger', 'Custom'
    pine_script_file_id INTEGER,
    python_code TEXT,                      -- Converted Python code
    strategy_type VARCHAR(30) DEFAULT 'trend_following', -- 'trend_following', 'mean_reversion', 'momentum'
    status VARCHAR(20) DEFAULT 'draft',    -- 'draft', 'converted', 'tested', 'optimized'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pine_script_file_id) REFERENCES pine_script_files(id)
);

-- Strategy parameters with strict typing (prevents optuna/scipy bugs)
CREATE TABLE IF NOT EXISTS strategy_parameters (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    
    -- Strict parameter typing for optimization libraries
    parameter_type VARCHAR(20) NOT NULL,   -- 'int', 'float', 'bool', 'categorical'
    
    -- Type-specific constraints (JSON format for flexibility)
    constraints_json TEXT NOT NULL,        -- {"min": 10, "max": 30, "step": 1} for int
                                          -- {"low": 0.1, "high": 1.0} for float
                                          -- {"choices": ["sma", "ema", "wma"]} for categorical
    
    -- Default values with type validation
    default_value_str VARCHAR(100),        -- String representation
    default_value_num DECIMAL(20,8),       -- Numeric value (for int/float)
    default_value_bool BOOLEAN,            -- Boolean value
    
    -- Optimization library specific settings
    optuna_suggest_type VARCHAR(30),       -- 'suggest_int', 'suggest_float', 'suggest_categorical'
    scipy_bounds_json TEXT,                -- [lower, upper] for scipy.optimize
    is_optimizable BOOLEAN DEFAULT TRUE,   -- Can this parameter be optimized?
    
    -- Pine Script metadata
    pine_input_name VARCHAR(100),          -- Original name from Pine Script
    pine_input_type VARCHAR(50),           -- 'input.int', 'input.float', etc.
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- =======================
-- BACKTESTING FRAMEWORK
-- =======================

-- Backtest configurations with engine-specific settings
CREATE TABLE IF NOT EXISTS backtest_configs (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    strategy_id INTEGER NOT NULL,
    
    -- Market data configuration
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL, 
    timeframe VARCHAR(10) NOT NULL,
    start_timestamp_utc BIGINT NOT NULL,   -- Unix timestamp for precise range queries
    end_timestamp_utc BIGINT NOT NULL,
    
    -- Trading configuration
    initial_capital DECIMAL(20,8) DEFAULT 10000,
    commission_rate DECIMAL(10,8) DEFAULT 0.001,  -- Higher precision for accurate calculations
    slippage_model VARCHAR(20) DEFAULT 'fixed',   -- 'fixed', 'linear', 'sqrt'
    slippage_value DECIMAL(10,8) DEFAULT 0.0005,
    
    -- Engine-specific configurations (JSON)
    backtrader_config_json TEXT,          -- {"cash": 10000, "commission": 0.001, "slip_perc": 0.0005}
    vectorbt_config_json TEXT,            -- {"freq": "H", "init_cash": 10000}
    bt_config_json TEXT,                   -- {"lookahead_bias": False, "trade_on_open": False}
    
    -- Execution engine preference
    preferred_engine VARCHAR(20) DEFAULT 'backtrader', -- 'backtrader', 'vectorbt', 'bt', 'custom'
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- Parameter sets with validation
CREATE TABLE IF NOT EXISTS backtest_parameter_sets (
    id INTEGER PRIMARY KEY,
    backtest_config_id INTEGER NOT NULL,
    parameter_set_name VARCHAR(255),
    
    -- Parameters stored in multiple formats for different libraries
    parameters_json TEXT NOT NULL,         -- {"rsi_period": 14, "rsi_upper": 70}
    parameters_dict_str TEXT,              -- String representation for eval() if needed
    parameters_hash VARCHAR(64) NOT NULL,  -- SHA256 hash for deduplication
    
    -- Validation flags
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors TEXT,               -- JSON array of validation error messages
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (backtest_config_id) REFERENCES backtest_configs(id),
    UNIQUE(backtest_config_id, parameters_hash)  -- Prevent duplicate parameter sets
);

-- Enhanced backtest results with multi-engine support
CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY,
    backtest_config_id INTEGER NOT NULL,
    parameter_set_id INTEGER NOT NULL,
    execution_engine VARCHAR(20) NOT NULL, -- Which engine was used
    
    -- Execution info
    execution_status VARCHAR(20) NOT NULL,
    execution_time_ms INTEGER,
    memory_usage_mb INTEGER,               -- Track memory consumption
    data_points_processed INTEGER,
    
    -- Universal performance metrics (all engines support these)
    total_return_pct DECIMAL(12,6),        -- Higher precision for small returns
    annual_return_pct DECIMAL(12,6),
    max_drawdown_pct DECIMAL(12,6),
    sharpe_ratio DECIMAL(10,6),
    sortino_ratio DECIMAL(10,6),
    calmar_ratio DECIMAL(10,6),
    
    -- Trading statistics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate_pct DECIMAL(8,4),
    profit_factor DECIMAL(10,6),
    
    -- Engine-specific results (JSON)
    backtrader_analyzer_results TEXT,     -- Full analyzer results from backtrader
    vectorbt_stats_json TEXT,             -- vectorbt statistics
    bt_stats_json TEXT,                   -- bt library results
    
    -- Portfolio value series (for plotting) - compressed JSON
    portfolio_values_json TEXT,           -- [{"timestamp": 1640995200, "value": 10500.50}, ...]
    
    -- Risk metrics
    var_95 DECIMAL(12,6),                 -- Value at Risk (95%)
    cvar_95 DECIMAL(12,6),                -- Conditional Value at Risk
    beta DECIMAL(8,6),                    -- Market beta (if benchmark provided)
    
    start_timestamp_utc BIGINT,
    end_timestamp_utc BIGINT,
    final_portfolio_value DECIMAL(20,8),
    
    error_message TEXT,
    error_traceback TEXT,                 -- Full Python traceback for debugging
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    FOREIGN KEY (backtest_config_id) REFERENCES backtest_configs(id),
    FOREIGN KEY (parameter_set_id) REFERENCES backtest_parameter_sets(id)
);

-- Trades with precise execution info
CREATE TABLE IF NOT EXISTS backtest_trades (
    id INTEGER PRIMARY KEY,
    backtest_result_id INTEGER NOT NULL,
    trade_number INTEGER NOT NULL,
    
    -- Precise timestamps (microseconds)
    entry_timestamp_utc BIGINT NOT NULL,
    exit_timestamp_utc BIGINT,
    
    -- Trade details
    side VARCHAR(10) NOT NULL,             -- 'long', 'short'
    entry_price DECIMAL(30,15) NOT NULL,   -- High precision
    exit_price DECIMAL(30,15),
    quantity DECIMAL(30,8) NOT NULL,
    
    -- P&L calculations
    pnl_gross DECIMAL(30,8),              -- Before costs
    pnl_net DECIMAL(30,8),                -- After all costs
    pnl_pct DECIMAL(12,6),
    commission_paid DECIMAL(30,8) DEFAULT 0,
    slippage_cost DECIMAL(30,8) DEFAULT 0,
    
    -- Trade metadata
    entry_reason VARCHAR(100),            -- 'RSI_oversold', 'MA_crossover', etc.
    exit_reason VARCHAR(100),             -- 'take_profit', 'stop_loss', 'signal_exit'
    trade_duration_bars INTEGER,         -- How many bars the trade lasted
    
    -- Risk metrics per trade
    mfe_pct DECIMAL(10,6),               -- Maximum Favorable Excursion
    mae_pct DECIMAL(10,6),               -- Maximum Adverse Excursion
    
    trade_status VARCHAR(20) DEFAULT 'closed',
    
    FOREIGN KEY (backtest_result_id) REFERENCES backtest_results(id)
);

-- =======================
-- OPTIMIZATION FRAMEWORK
-- =======================

-- Optimization campaigns with algorithm-specific configurations
CREATE TABLE IF NOT EXISTS optimization_campaigns (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    strategy_id INTEGER NOT NULL,
    
    -- Algorithm configuration
    optimization_algorithm VARCHAR(30) NOT NULL, -- 'optuna_tpe', 'scipy_differential_evolution', 'grid_search'
    target_metric VARCHAR(50) NOT NULL,          -- 'sharpe_ratio', 'calmar_ratio', 'total_return'
    optimization_direction VARCHAR(10) NOT NULL, -- 'maximize', 'minimize'
    
    -- Algorithm-specific settings (JSON)
    optuna_study_config TEXT,            -- {"n_trials": 100, "sampler": "TPESampler"}
    scipy_optimize_config TEXT,          -- {"method": "differential_evolution", "maxiter": 1000}
    grid_search_config TEXT,             -- {"n_jobs": -1, "verbose": 1}
    
    -- Search space definition
    parameter_space_json TEXT NOT NULL,  -- Complete parameter space for the algorithm
    
    -- Data split configuration
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    train_start_utc BIGINT NOT NULL,
    train_end_utc BIGINT NOT NULL,
    validation_start_utc BIGINT,         -- For walk-forward analysis
    validation_end_utc BIGINT,
    
    -- Execution settings
    max_concurrent_backtests INTEGER DEFAULT 1,
    timeout_minutes INTEGER DEFAULT 60,
    early_stopping_rounds INTEGER,       -- Stop if no improvement for N rounds
    
    -- Progress tracking
    status VARCHAR(20) DEFAULT 'pending',
    current_iteration INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 100,
    best_metric_value DECIMAL(12,6),
    best_parameters_json TEXT,
    
    -- Resource usage
    total_backtests_run INTEGER DEFAULT 0,
    total_execution_time_ms BIGINT DEFAULT 0,
    peak_memory_usage_mb INTEGER,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- Individual optimization iterations
CREATE TABLE IF NOT EXISTS optimization_iterations (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL,
    iteration_number INTEGER NOT NULL,
    parameters_json TEXT NOT NULL,
    backtest_result_id INTEGER,            -- Links to actual backtest
    metric_value DECIMAL(12,6),
    execution_time_ms INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES optimization_campaigns(id),
    FOREIGN KEY (backtest_result_id) REFERENCES backtest_results(id)
);

-- Validation test results (out-of-sample testing)
CREATE TABLE IF NOT EXISTS validation_tests (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER NOT NULL,
    optimization_campaign_id INTEGER,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(30) NOT NULL,        -- 'walk_forward', 'monte_carlo', 'cross_validation'
    
    parameters_json TEXT NOT NULL,         -- Best parameters from optimization
    
    -- Test Configuration
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    test_start_utc BIGINT NOT NULL,
    test_end_utc BIGINT NOT NULL,
    
    -- Validation Results
    validation_score DECIMAL(12,6),        -- Overall validation score
    is_overfitted BOOLEAN DEFAULT FALSE,
    confidence_level DECIMAL(5,2),         -- Statistical confidence %
    
    backtest_result_id INTEGER,            -- Links to validation backtest
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id),
    FOREIGN KEY (optimization_campaign_id) REFERENCES optimization_campaigns(id),
    FOREIGN KEY (backtest_result_id) REFERENCES backtest_results(id)
);

-- =======================
-- SYSTEM MONITORING
-- =======================

-- Pine Script conversion attempts
CREATE TABLE IF NOT EXISTS conversions (
    id INTEGER PRIMARY KEY,
    pine_script_file_id INTEGER,
    strategy_id INTEGER,
    conversion_status VARCHAR(20) NOT NULL, -- 'success', 'failed', 'partial'
    python_output TEXT,
    error_message TEXT,
    conversion_time_ms INTEGER,
    parameters_extracted INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (pine_script_file_id) REFERENCES pine_script_files(id),
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

-- Data fetch sessions
CREATE TABLE IF NOT EXISTS data_sessions (
    id INTEGER PRIMARY KEY,
    session_type VARCHAR(20) NOT NULL,     -- 'live_fetch', 'file_upload', 'historical_sync'
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    records_fetched INTEGER DEFAULT 0,
    fetch_duration_ms INTEGER,
    status VARCHAR(20) NOT NULL,           -- 'success', 'failed', 'partial'
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System activity log
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY,
    activity_type VARCHAR(50) NOT NULL,    -- 'pine_converted', 'backtest_completed', 'optimization_started'
    entity_type VARCHAR(50),               -- 'strategy', 'backtest', 'optimization'
    entity_id INTEGER,
    details TEXT,                          -- JSON for additional context
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System statistics cache
CREATE TABLE IF NOT EXISTS system_stats (
    id INTEGER PRIMARY KEY,
    stat_name VARCHAR(100) NOT NULL,       -- 'total_strategies', 'avg_backtest_time', 'best_sharpe_ratio'
    stat_value VARCHAR(255) NOT NULL,
    stat_category VARCHAR(50),             -- 'conversion', 'backtesting', 'optimization', 'data'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =======================
-- PERFORMANCE INDEXES
-- =======================

-- OHLC data queries (time-series)
CREATE INDEX IF NOT EXISTS idx_ohlc_symbol_timeframe_timestamp 
ON crypto_ohlc_data(symbol, timeframe, timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp_utc 
ON crypto_ohlc_data(timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_ohlc_symbol_exchange 
ON crypto_ohlc_data(symbol, exchange);

-- Backtest performance indexes
CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy_metric 
ON backtest_results(backtest_config_id, sharpe_ratio DESC);

CREATE INDEX IF NOT EXISTS idx_backtest_configs_strategy 
ON backtest_configs(strategy_id);

CREATE INDEX IF NOT EXISTS idx_trades_timestamp 
ON backtest_trades(entry_timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_trades_result 
ON backtest_trades(backtest_result_id);

-- Strategy indexes
CREATE INDEX IF NOT EXISTS idx_strategies_status 
ON strategies(status);

CREATE INDEX IF NOT EXISTS idx_strategy_parameters_strategy 
ON strategy_parameters(strategy_id);

-- Optimization indexes
CREATE INDEX IF NOT EXISTS idx_optimization_iterations_campaign 
ON optimization_iterations(campaign_id);

CREATE INDEX IF NOT EXISTS idx_optimization_metric 
ON optimization_iterations(campaign_id, metric_value DESC);

-- Activity and monitoring
CREATE INDEX IF NOT EXISTS idx_activity_log_type_timestamp 
ON activity_log(activity_type, created_at);

CREATE INDEX IF NOT EXISTS idx_data_sessions_symbol_timeframe 
ON data_sessions(symbol, timeframe, created_at);

-- Data source indexes
CREATE INDEX IF NOT EXISTS idx_data_sources_symbol_exchange_timeframe 
ON crypto_data_sources(symbol, exchange, timeframe);

-- =======================
-- INITIAL SYSTEM STATS
-- =======================

-- Insert default system statistics
INSERT OR IGNORE INTO system_stats (stat_name, stat_value, stat_category) VALUES
('total_strategies', '0', 'conversion'),
('total_backtests', '0', 'backtesting'),
('total_optimizations', '0', 'optimization'),
('total_ohlc_records', '0', 'data'),
('system_uptime', '0', 'system'),
('avg_backtest_time_ms', '0', 'backtesting'),
('avg_optimization_time_ms', '0', 'optimization'),
('best_sharpe_ratio', '0', 'backtesting'),
('database_size_mb', '0', 'system');

-- Schema version for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (version) VALUES (1);