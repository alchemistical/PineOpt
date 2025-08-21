"""
PineOpt SQLAlchemy ORM Models
Optimized for pandas, backtrader, and optimization libraries
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, DECIMAL, 
    ForeignKey, UniqueConstraint, Index, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import json
from decimal import Decimal
from typing import Dict, List, Optional, Any

Base = declarative_base()

# =======================
# CRYPTO MARKET DATA
# =======================

class CryptoOHLCData(Base):
    """Historical OHLC data optimized for time-series analysis."""
    __tablename__ = 'crypto_ohlc_data'
    
    id = Column(Integer, primary_key=True)
    
    # Core identifiers
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    
    # Timestamp handling (UTC microseconds for pandas compatibility)
    timestamp_utc = Column(BigInteger, nullable=False, index=True)
    datetime_str = Column(String(25), nullable=False)
    
    # OHLCV data with high precision
    open_price = Column(DECIMAL(30, 15), nullable=False)
    high_price = Column(DECIMAL(30, 15), nullable=False)
    low_price = Column(DECIMAL(30, 15), nullable=False)
    close_price = Column(DECIMAL(30, 15), nullable=False)
    volume = Column(DECIMAL(30, 8), default=0)
    
    # Additional fields
    vwap = Column(DECIMAL(30, 15))
    trades_count = Column(Integer, default=0)
    
    # Data quality flags
    is_complete = Column(Boolean, default=True)
    has_gaps = Column(Boolean, default=False)
    source_type = Column(String(20), nullable=False)
    
    # JSON data for backtrader compatibility
    ohlcv_json = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('symbol', 'exchange', 'timeframe', 'timestamp_utc'),
        Index('idx_ohlc_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp_utc'),
    )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'exchange': self.exchange,
            'timeframe': self.timeframe,
            'timestamp_utc': self.timestamp_utc,
            'datetime_str': self.datetime_str,
            'open_price': float(self.open_price) if self.open_price else None,
            'high_price': float(self.high_price) if self.high_price else None,
            'low_price': float(self.low_price) if self.low_price else None,
            'close_price': float(self.close_price) if self.close_price else None,
            'volume': float(self.volume) if self.volume else 0,
            'source_type': self.source_type,
            'is_complete': self.is_complete
        }
    
    def to_backtrader_dict(self) -> Dict:
        """Convert to backtrader-compatible format."""
        if self.ohlcv_json:
            return json.loads(self.ohlcv_json)
        
        return {
            'Open': float(self.open_price),
            'High': float(self.high_price),
            'Low': float(self.low_price),
            'Close': float(self.close_price),
            'Volume': float(self.volume) if self.volume else 0
        }

class CryptoDataSource(Base):
    """Metadata for crypto data sources."""
    __tablename__ = 'crypto_data_sources'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    
    # Data range info
    total_records = Column(Integer, default=0)
    first_timestamp_utc = Column(BigInteger)
    last_timestamp_utc = Column(BigInteger)
    price_min = Column(DECIMAL(30, 15))
    price_max = Column(DECIMAL(30, 15))
    
    # Library compatibility settings
    pandas_freq = Column(String(10))  # 'H', 'D', '5T'
    backtrader_compression = Column(Integer)  # 1, 5, 60
    ccxt_timeframe = Column(String(10))  # '1h', '1d'
    
    # Data quality metrics
    completeness_pct = Column(DECIMAL(5, 2))
    gap_count = Column(Integer, default=0)
    
    status = Column(String(20), default='active')
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('symbol', 'exchange', 'timeframe'),
    )

# =======================
# STRATEGY MANAGEMENT
# =======================

class PineScriptFile(Base):
    """Pine Script file storage."""
    __tablename__ = 'pine_script_files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_content = Column(Text, nullable=False)
    file_size = Column(Integer)
    file_hash = Column(String(64), index=True)  # SHA256
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategies = relationship("Strategy", back_populates="pine_script_file")

class Strategy(Base):
    """Trading strategy definitions."""
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # RSI, MA, Bollinger, etc.
    pine_script_file_id = Column(Integer, ForeignKey('pine_script_files.id'))
    python_code = Column(Text)
    strategy_type = Column(String(30), default='trend_following')
    status = Column(String(20), default='draft', index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pine_script_file = relationship("PineScriptFile", back_populates="strategies")
    parameters = relationship("StrategyParameter", back_populates="strategy", cascade="all, delete-orphan")
    backtest_configs = relationship("BacktestConfig", back_populates="strategy")
    optimization_campaigns = relationship("OptimizationCampaign", back_populates="strategy")

class StrategyParameter(Base):
    """Strategy parameters with optimization support."""
    __tablename__ = 'strategy_parameters'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    
    # Type system
    parameter_type = Column(String(20), nullable=False)  # int, float, bool, categorical
    constraints_json = Column(Text, nullable=False)
    
    # Default values
    default_value_str = Column(String(100))
    default_value_num = Column(DECIMAL(20, 8))
    default_value_bool = Column(Boolean)
    
    # Optimization settings
    optuna_suggest_type = Column(String(30))
    scipy_bounds_json = Column(Text)
    is_optimizable = Column(Boolean, default=True)
    
    # Pine Script metadata
    pine_input_name = Column(String(100))
    pine_input_type = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="parameters")
    
    def get_default_value(self) -> Any:
        """Get the default value in proper Python type."""
        if self.parameter_type == 'int':
            return int(self.default_value_num) if self.default_value_num else 0
        elif self.parameter_type == 'float':
            return float(self.default_value_num) if self.default_value_num else 0.0
        elif self.parameter_type == 'bool':
            return self.default_value_bool if self.default_value_bool is not None else False
        else:
            return self.default_value_str if self.default_value_str else ""
    
    def get_constraints(self) -> Dict:
        """Parse constraints JSON."""
        try:
            return json.loads(self.constraints_json) if self.constraints_json else {}
        except json.JSONDecodeError:
            return {}

# =======================
# BACKTESTING FRAMEWORK
# =======================

class BacktestConfig(Base):
    """Backtest configuration."""
    __tablename__ = 'backtest_configs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    
    # Market data config
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_timestamp_utc = Column(BigInteger, nullable=False)
    end_timestamp_utc = Column(BigInteger, nullable=False)
    
    # Trading config
    initial_capital = Column(DECIMAL(20, 8), default=10000)
    commission_rate = Column(DECIMAL(10, 8), default=0.001)
    slippage_model = Column(String(20), default='fixed')
    slippage_value = Column(DECIMAL(10, 8), default=0.0005)
    
    # Engine configs (JSON)
    backtrader_config_json = Column(Text)
    vectorbt_config_json = Column(Text)
    bt_config_json = Column(Text)
    
    preferred_engine = Column(String(20), default='backtrader')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtest_configs")
    parameter_sets = relationship("BacktestParameterSet", back_populates="backtest_config")
    results = relationship("BacktestResult", back_populates="backtest_config")

class BacktestParameterSet(Base):
    """Parameter combinations for backtests."""
    __tablename__ = 'backtest_parameter_sets'
    
    id = Column(Integer, primary_key=True)
    backtest_config_id = Column(Integer, ForeignKey('backtest_configs.id'), nullable=False, index=True)
    parameter_set_name = Column(String(255))
    
    parameters_json = Column(Text, nullable=False)
    parameters_dict_str = Column(Text)
    parameters_hash = Column(String(64), nullable=False, index=True)
    
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest_config = relationship("BacktestConfig", back_populates="parameter_sets")
    results = relationship("BacktestResult", back_populates="parameter_set")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('backtest_config_id', 'parameters_hash'),
    )
    
    def get_parameters(self) -> Dict:
        """Parse parameters JSON."""
        try:
            return json.loads(self.parameters_json) if self.parameters_json else {}
        except json.JSONDecodeError:
            return {}

class BacktestResult(Base):
    """Backtest execution results."""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True)
    backtest_config_id = Column(Integer, ForeignKey('backtest_configs.id'), nullable=False, index=True)
    parameter_set_id = Column(Integer, ForeignKey('backtest_parameter_sets.id'), nullable=False, index=True)
    execution_engine = Column(String(20), nullable=False)
    
    # Execution info
    execution_status = Column(String(20), nullable=False)
    execution_time_ms = Column(Integer)
    memory_usage_mb = Column(Integer)
    data_points_processed = Column(Integer)
    
    # Performance metrics
    total_return_pct = Column(DECIMAL(12, 6))
    annual_return_pct = Column(DECIMAL(12, 6))
    max_drawdown_pct = Column(DECIMAL(12, 6))
    sharpe_ratio = Column(DECIMAL(10, 6), index=True)
    sortino_ratio = Column(DECIMAL(10, 6))
    calmar_ratio = Column(DECIMAL(10, 6))
    
    # Trading stats
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate_pct = Column(DECIMAL(8, 4))
    profit_factor = Column(DECIMAL(10, 6))
    
    # Engine-specific results
    backtrader_analyzer_results = Column(Text)
    vectorbt_stats_json = Column(Text)
    bt_stats_json = Column(Text)
    
    # Portfolio values for plotting
    portfolio_values_json = Column(Text)
    
    # Risk metrics
    var_95 = Column(DECIMAL(12, 6))
    cvar_95 = Column(DECIMAL(12, 6))
    beta = Column(DECIMAL(8, 6))
    
    start_timestamp_utc = Column(BigInteger)
    end_timestamp_utc = Column(BigInteger)
    final_portfolio_value = Column(DECIMAL(20, 8))
    
    error_message = Column(Text)
    error_traceback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    backtest_config = relationship("BacktestConfig", back_populates="results")
    parameter_set = relationship("BacktestParameterSet", back_populates="results")
    trades = relationship("BacktestTrade", back_populates="backtest_result")

class BacktestTrade(Base):
    """Individual trades from backtests."""
    __tablename__ = 'backtest_trades'
    
    id = Column(Integer, primary_key=True)
    backtest_result_id = Column(Integer, ForeignKey('backtest_results.id'), nullable=False, index=True)
    trade_number = Column(Integer, nullable=False)
    
    # Timestamps
    entry_timestamp_utc = Column(BigInteger, nullable=False, index=True)
    exit_timestamp_utc = Column(BigInteger)
    
    # Trade details
    side = Column(String(10), nullable=False)  # long, short
    entry_price = Column(DECIMAL(30, 15), nullable=False)
    exit_price = Column(DECIMAL(30, 15))
    quantity = Column(DECIMAL(30, 8), nullable=False)
    
    # P&L
    pnl_gross = Column(DECIMAL(30, 8))
    pnl_net = Column(DECIMAL(30, 8))
    pnl_pct = Column(DECIMAL(12, 6))
    commission_paid = Column(DECIMAL(30, 8), default=0)
    slippage_cost = Column(DECIMAL(30, 8), default=0)
    
    # Trade metadata
    entry_reason = Column(String(100))
    exit_reason = Column(String(100))
    trade_duration_bars = Column(Integer)
    
    # Risk metrics
    mfe_pct = Column(DECIMAL(10, 6))  # Maximum Favorable Excursion
    mae_pct = Column(DECIMAL(10, 6))  # Maximum Adverse Excursion
    
    trade_status = Column(String(20), default='closed')
    
    # Relationships
    backtest_result = relationship("BacktestResult", back_populates="trades")

# =======================
# OPTIMIZATION FRAMEWORK
# =======================

class OptimizationCampaign(Base):
    """Optimization campaign configuration and results."""
    __tablename__ = 'optimization_campaigns'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    
    # Algorithm config
    optimization_algorithm = Column(String(30), nullable=False)
    target_metric = Column(String(50), nullable=False)
    optimization_direction = Column(String(10), nullable=False)
    
    # Algorithm-specific settings
    optuna_study_config = Column(Text)
    scipy_optimize_config = Column(Text)
    grid_search_config = Column(Text)
    
    parameter_space_json = Column(Text, nullable=False)
    
    # Data config
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    train_start_utc = Column(BigInteger, nullable=False)
    train_end_utc = Column(BigInteger, nullable=False)
    validation_start_utc = Column(BigInteger)
    validation_end_utc = Column(BigInteger)
    
    # Execution settings
    max_concurrent_backtests = Column(Integer, default=1)
    timeout_minutes = Column(Integer, default=60)
    early_stopping_rounds = Column(Integer)
    
    # Progress tracking
    status = Column(String(20), default='pending')
    current_iteration = Column(Integer, default=0)
    max_iterations = Column(Integer, default=100)
    best_metric_value = Column(DECIMAL(12, 6))
    best_parameters_json = Column(Text)
    
    # Resource usage
    total_backtests_run = Column(Integer, default=0)
    total_execution_time_ms = Column(BigInteger, default=0)
    peak_memory_usage_mb = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="optimization_campaigns")
    iterations = relationship("OptimizationIteration", back_populates="campaign")

class OptimizationIteration(Base):
    """Individual optimization iterations."""
    __tablename__ = 'optimization_iterations'
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('optimization_campaigns.id'), nullable=False, index=True)
    iteration_number = Column(Integer, nullable=False)
    parameters_json = Column(Text, nullable=False)
    backtest_result_id = Column(Integer, ForeignKey('backtest_results.id'))
    metric_value = Column(DECIMAL(12, 6), index=True)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("OptimizationCampaign", back_populates="iterations")
    
    # Composite index for performance
    __table_args__ = (
        Index('idx_optimization_metric', 'campaign_id', 'metric_value'),
    )

# =======================
# SYSTEM MONITORING
# =======================

class Conversion(Base):
    """Pine Script conversion attempts."""
    __tablename__ = 'conversions'
    
    id = Column(Integer, primary_key=True)
    pine_script_file_id = Column(Integer, ForeignKey('pine_script_files.id'))
    strategy_id = Column(Integer, ForeignKey('strategies.id'))
    conversion_status = Column(String(20), nullable=False)
    python_output = Column(Text)
    error_message = Column(Text)
    conversion_time_ms = Column(Integer)
    parameters_extracted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class DataSession(Base):
    """Data fetch session tracking."""
    __tablename__ = 'data_sessions'
    
    id = Column(Integer, primary_key=True)
    session_type = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    records_fetched = Column(Integer, default=0)
    fetch_duration_ms = Column(Integer)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class ActivityLog(Base):
    """System activity logging."""
    __tablename__ = 'activity_log'
    
    id = Column(Integer, primary_key=True)
    activity_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SystemStat(Base):
    """System statistics cache."""
    __tablename__ = 'system_stats'
    
    id = Column(Integer, primary_key=True)
    stat_name = Column(String(100), nullable=False, unique=True)
    stat_value = Column(String(255), nullable=False)
    stat_category = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow)

# =======================
# DATABASE UTILITIES
# =======================

class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, db_url: str = "sqlite:///database/pineopt.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
        
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        
    def get_db_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        session = self.get_session()
        try:
            stats = {}
            for table_name in ['strategies', 'crypto_ohlc_data', 'backtest_results']:
                # Get table class
                table_cls = globals().get(
                    ''.join(word.capitalize() for word in table_name.split('_'))
                )
                if table_cls:
                    count = session.query(table_cls).count()
                    stats[f"{table_name}_count"] = count
            return stats
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager()