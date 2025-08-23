-- Epic 5: Strategy Execution & Backtesting - Database Schema
-- Sprint 1: Strategy Management Tables

-- Strategy Storage and Metadata
CREATE TABLE IF NOT EXISTS strategies (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    author VARCHAR(255) DEFAULT 'Unknown',
    version VARCHAR(50) DEFAULT '1.0',
    language TEXT NOT NULL CHECK(language IN ('python', 'pine')),
    
    -- File and Code Storage
    original_filename VARCHAR(255),
    file_size INTEGER,
    source_code TEXT NOT NULL,
    
    -- Strategy Metadata
    parameters JSON DEFAULT '{}',
    dependencies JSON DEFAULT '[]',
    supported_timeframes JSON DEFAULT '["1h", "4h", "1d"]',
    supported_assets JSON DEFAULT '["BTCUSDT"]',
    tags JSON DEFAULT '[]',
    
    -- Validation Status
    validation_status TEXT DEFAULT 'pending' CHECK(validation_status IN ('pending', 'valid', 'invalid', 'error')),
    validation_errors JSON DEFAULT '[]',
    validation_timestamp TIMESTAMP,
    
    -- Usage Statistics
    upload_count INTEGER DEFAULT 1,
    backtest_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    
    -- Audit Trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CHECK (file_size > 0 AND file_size <= 10485760), -- Max 10MB
    CHECK (length(source_code) > 0),
    CHECK (name IS NOT NULL AND trim(name) != '')
);

-- Strategy Parameters Definition
CREATE TABLE IF NOT EXISTS strategy_parameters (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    strategy_id TEXT NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_type TEXT NOT NULL CHECK(parameter_type IN ('int', 'float', 'bool', 'str', 'list')),
    default_value TEXT,
    min_value DECIMAL(20,8),
    max_value DECIMAL(20,8),
    description TEXT,
    is_required BOOLEAN DEFAULT TRUE,
    validation_rules JSON DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE,
    UNIQUE(strategy_id, parameter_name)
);

-- Strategy Dependencies
CREATE TABLE IF NOT EXISTS strategy_dependencies (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    strategy_id TEXT NOT NULL,
    dependency_name VARCHAR(100) NOT NULL,
    dependency_type TEXT NOT NULL CHECK(dependency_type IN ('import', 'library', 'module')),
    version_requirement VARCHAR(50),
    is_standard_library BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT FALSE,
    installation_command TEXT,
    
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE,
    UNIQUE(strategy_id, dependency_name)
);

-- Strategy Validation Results
CREATE TABLE IF NOT EXISTS strategy_validations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    strategy_id TEXT NOT NULL,
    validation_type TEXT NOT NULL CHECK(validation_type IN ('syntax', 'security', 'dependencies', 'parameters')),
    status TEXT NOT NULL CHECK(status IN ('pass', 'fail', 'warning')),
    message TEXT,
    details JSON DEFAULT '{}',
    line_number INTEGER,
    column_number INTEGER,
    
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- Strategy Tags for Organization
CREATE TABLE IF NOT EXISTS strategy_tags (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7), -- Hex color code
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Strategy-Tag Relationships
CREATE TABLE IF NOT EXISTS strategy_tag_relationships (
    strategy_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (strategy_id, tag_id),
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES strategy_tags(id) ON DELETE CASCADE
);

-- Future: Backtest Results (Sprint 3)
CREATE TABLE IF NOT EXISTS backtests (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    strategy_id TEXT NOT NULL,
    name VARCHAR(255),
    
    -- Configuration
    config JSON NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20,8) DEFAULT 100000.00,
    
    -- Execution Status
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress_percent INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    error_message TEXT,
    
    -- Results Summary (populated after completion)
    total_return DECIMAL(10,4),
    sharpe_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    total_trades INTEGER,
    win_rate DECIMAL(5,2),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_strategies_author ON strategies(author);
CREATE INDEX IF NOT EXISTS idx_strategies_language ON strategies(language);
CREATE INDEX IF NOT EXISTS idx_strategies_validation_status ON strategies(validation_status);
CREATE INDEX IF NOT EXISTS idx_strategies_created_at ON strategies(created_at);
CREATE INDEX IF NOT EXISTS idx_strategies_tags ON strategies(tags);

CREATE INDEX IF NOT EXISTS idx_strategy_params_strategy_id ON strategy_parameters(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_deps_strategy_id ON strategy_dependencies(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_deps_name ON strategy_dependencies(dependency_name);
CREATE INDEX IF NOT EXISTS idx_strategy_validations_strategy_id ON strategy_validations(strategy_id);
CREATE INDEX IF NOT EXISTS idx_strategy_validations_type ON strategy_validations(validation_type);
CREATE INDEX IF NOT EXISTS idx_strategy_validations_status ON strategy_validations(status);
CREATE INDEX IF NOT EXISTS idx_strategy_tags_name ON strategy_tags(name);
CREATE INDEX IF NOT EXISTS idx_backtests_strategy_id ON backtests(strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtests_status ON backtests(status);
CREATE INDEX IF NOT EXISTS idx_backtests_created_at ON backtests(created_at);

-- Create some default tags for organization
INSERT OR IGNORE INTO strategy_tags (name, description, color) VALUES
('rsi', 'RSI-based strategies', '#3b82f6'),
('moving-average', 'Moving average strategies', '#10b981'),
('momentum', 'Momentum-based strategies', '#f59e0b'),
('mean-reversion', 'Mean reversion strategies', '#ef4444'),
('breakout', 'Breakout strategies', '#8b5cf6'),
('scalping', 'Short-term scalping strategies', '#06b6d4'),
('swing', 'Swing trading strategies', '#84cc16'),
('experimental', 'Experimental or testing strategies', '#6b7280');

-- Update trigger for strategies table
CREATE TRIGGER IF NOT EXISTS update_strategies_timestamp
    AFTER UPDATE ON strategies
    FOR EACH ROW
BEGIN
    UPDATE strategies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;