"""
Epic 5 Sprint 2: Comprehensive Backtesting Engine
Integrates strategy execution, portfolio simulation, and historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from .strategy_executor import StrategyExecutor, ExecutionResult, OrderSide
from .portfolio_engine import PortfolioSimulator, PortfolioMetrics, RiskMetrics, TradeAnalysis
from database.strategy_models import StrategyDatabase, StrategyMetadata

logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtest execution"""
    strategy_id: str
    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 100000.0
    commission_rate: float = 0.001
    slippage_rate: float = 0.0001
    max_position_size_pct: float = 10.0
    risk_per_trade_pct: float = 2.0
    strategy_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BacktestResult:
    """Comprehensive backtest results"""
    config: BacktestConfig
    success: bool
    message: str
    start_time: datetime
    end_time: datetime
    execution_time_seconds: float
    
    # Core metrics
    portfolio_metrics: PortfolioMetrics
    risk_metrics: RiskMetrics
    
    # Detailed data
    trades: List[TradeAnalysis] = field(default_factory=list)
    portfolio_history: List[Dict[str, Any]] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    drawdown_series: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Strategy-specific results
    signals_generated: int = 0
    signals_executed: int = 0
    execution_rate_pct: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result_dict = {
            'config': self.config.to_dict(),
            'success': self.success,
            'message': self.message,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'execution_time_seconds': self.execution_time_seconds,
            'portfolio_metrics': asdict(self.portfolio_metrics),
            'risk_metrics': asdict(self.risk_metrics),
            'signals_generated': self.signals_generated,
            'signals_executed': self.signals_executed,
            'execution_rate_pct': self.execution_rate_pct,
            'trades': [asdict(trade) for trade in self.trades],
            'portfolio_history': self.portfolio_history,
            'daily_returns': self.daily_returns,
            'equity_curve': [(ts.isoformat(), val) for ts, val in self.equity_curve],
            'drawdown_series': [(ts.isoformat(), val) for ts, val in self.drawdown_series]
        }
        return result_dict

class BacktestEngine:
    """
    Comprehensive backtesting engine that combines strategy execution,
    portfolio simulation, and performance analysis
    """
    
    def __init__(self, database_path: str = None):
        if database_path:
            self.strategy_db = StrategyDatabase(database_path)
        else:
            # Default database path
            db_path = Path(__file__).parent.parent.parent / "database" / "pineopt.db"
            self.strategy_db = StrategyDatabase(str(db_path))
        
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
    
    def load_market_data(self, symbol: str, timeframe: str, 
                        start_date: str = None, end_date: str = None,
                        n_bars: int = 5000) -> pd.DataFrame:
        """
        Load market data for backtesting using real Binance data
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Data timeframe (e.g., '1h', '4h', '1d')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            n_bars: Number of bars to load if dates not specified
        
        Returns:
            OHLC DataFrame with datetime index
        """
        cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}_{n_bars}"
        
        if cache_key in self.market_data_cache:
            logger.info(f"Using cached data for {symbol} {timeframe}")
            return self.market_data_cache[cache_key].copy()
        
        try:
            # First try to use our market data service for real Binance data
            try:
                # Import market data service
                import sys
                from pathlib import Path
                sys.path.append(str(Path(__file__).parent.parent.parent / "api"))
                from market_data_service import market_service
                
                # Convert dates to days if specified
                days = n_bars // 24 if timeframe == '1h' else n_bars // 6 if timeframe == '4h' else n_bars
                if start_date and end_date:
                    from datetime import datetime
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    days = (end_dt - start_dt).days
                
                days = min(max(days, 1), 365)  # Limit to 1-365 days
                
                # Format symbol for our market service (e.g., 'BTCUSDT' -> 'BTC/USDT')
                formatted_symbol = symbol
                if '/' not in symbol and symbol.endswith('USDT'):
                    base = symbol.replace('USDT', '')
                    formatted_symbol = f"{base}/USDT"
                
                # Fetch real historical data
                historical_data = market_service.fetch_historical_data(
                    symbol=formatted_symbol,
                    timeframe=timeframe,
                    days=days
                )
                
                if historical_data:
                    # Convert to DataFrame
                    data_list = []
                    for candle in historical_data:
                        data_list.append({
                            'timestamp': candle.timestamp,
                            'open': candle.open,
                            'high': candle.high,
                            'low': candle.low,
                            'close': candle.close,
                            'volume': candle.volume
                        })
                    
                    df = pd.DataFrame(data_list)
                    df.set_index('timestamp', inplace=True)
                    df.index = pd.to_datetime(df.index)
                    
                    # Filter by date range if specified
                    if start_date or end_date:
                        if start_date:
                            df = df[df.index >= pd.to_datetime(start_date)]
                        if end_date:
                            df = df[df.index <= pd.to_datetime(end_date)]
                    
                    # Cache the data
                    self.market_data_cache[cache_key] = df.copy()
                    
                    logger.info(f"Loaded {len(df)} real bars from market service for {symbol} {timeframe}")
                    return df
                else:
                    raise Exception("No historical data returned from market service")
            
            except Exception as market_service_error:
                logger.warning(f"Market service failed: {market_service_error}, trying fallback provider")
                
                # Fallback to original provider
                from research.data.providers.binance_provider import get_binance_provider
                
                provider = get_binance_provider()
                data = provider.fetch_ohlc(
                    symbol=symbol,
                    exchange="BINANCE",
                    timeframe=timeframe,
                    n_bars=n_bars,
                    use_cache=True
                )
                
                if 'data' in data and not data['data'].empty:
                    df = data['data']
                    
                    # Filter by date range if specified
                    if start_date or end_date:
                        if start_date:
                            df = df[df.index >= pd.to_datetime(start_date)]
                        if end_date:
                            df = df[df.index <= pd.to_datetime(end_date)]
                    
                    # Cache the data
                    self.market_data_cache[cache_key] = df.copy()
                    
                    logger.info(f"Loaded {len(df)} bars from fallback provider for {symbol} {timeframe}")
                    return df
                else:
                    raise Exception("No data returned from fallback provider")
                
        except Exception as e:
            logger.error(f"Failed to load market data from all sources: {e}")
            
            # Generate sample data for testing if real data fails
            logger.warning("Generating sample data for backtesting")
            return self._generate_sample_data(symbol, timeframe, n_bars)
    
    def _generate_sample_data(self, symbol: str, timeframe: str, n_bars: int = 1000) -> pd.DataFrame:
        """Generate sample OHLC data for testing"""
        
        # Create datetime index
        if timeframe == '1h':
            freq = 'H'
        elif timeframe == '4h':
            freq = '4H'
        elif timeframe == '1d':
            freq = 'D'
        else:
            freq = 'H'  # Default to hourly
        
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=n_bars if freq == 'H' else n_bars * 4)
        
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)[:n_bars]
        
        # Generate realistic price data with trends and volatility
        np.random.seed(42)  # For reproducible results
        
        initial_price = 45000 if 'BTC' in symbol else 3000  # Rough crypto prices
        returns = np.random.normal(0.0002, 0.02, len(dates))  # Small positive drift, 2% daily vol
        
        # Create price series
        prices = [initial_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        prices = np.array(prices)
        
        # Generate OHLC from close prices
        highs = prices * (1 + np.abs(np.random.normal(0, 0.01, len(prices))))
        lows = prices * (1 - np.abs(np.random.normal(0, 0.01, len(prices))))
        
        # Ensure OHLC relationships are valid
        opens = np.roll(prices, 1)  # Previous close as next open
        opens[0] = prices[0]
        
        volumes = np.random.lognormal(15, 1, len(prices))  # Realistic volume distribution
        
        df = pd.DataFrame({
            'open': opens,
            'high': np.maximum.reduce([opens, highs, prices]),
            'low': np.minimum.reduce([opens, lows, prices]),
            'close': prices,
            'volume': volumes
        }, index=dates)
        
        logger.info(f"Generated {len(df)} sample bars for {symbol}")
        return df
    
    def run_backtest(self, config: BacktestConfig) -> BacktestResult:
        """
        Execute a complete backtest
        
        Args:
            config: Backtest configuration
        
        Returns:
            BacktestResult with comprehensive results
        """
        start_time = datetime.now()
        
        try:
            # Load strategy from database
            strategy = self.strategy_db.get_strategy(config.strategy_id)
            if not strategy:
                return BacktestResult(
                    config=config,
                    success=False,
                    message=f"Strategy {config.strategy_id} not found",
                    start_time=start_time,
                    end_time=datetime.now(),
                    execution_time_seconds=0,
                    portfolio_metrics=PortfolioMetrics(),
                    risk_metrics=RiskMetrics()
                )
            
            # Load market data
            data = self.load_market_data(
                symbol=config.symbol,
                timeframe=config.timeframe,
                start_date=config.start_date,
                end_date=config.end_date
            )
            
            if data.empty:
                return BacktestResult(
                    config=config,
                    success=False,
                    message="No market data available",
                    start_time=start_time,
                    end_time=datetime.now(),
                    execution_time_seconds=0,
                    portfolio_metrics=PortfolioMetrics(),
                    risk_metrics=RiskMetrics()
                )
            
            # Initialize portfolio simulator
            portfolio_sim = PortfolioSimulator(
                initial_capital=config.initial_capital,
                max_position_size_pct=config.max_position_size_pct,
                commission_rate=config.commission_rate,
                slippage_rate=config.slippage_rate
            )
            
            # Load benchmark data for comparison
            portfolio_sim.set_benchmark(data)
            
            # Initialize strategy executor
            executor = StrategyExecutor(
                initial_capital=config.initial_capital,
                commission_rate=config.commission_rate,
                slippage_rate=config.slippage_rate
            )
            
            # Load strategy code
            strategy_loaded = executor.load_strategy(
                strategy.source_code,
                {
                    'id': strategy.id,
                    'name': strategy.name,
                    'symbol': config.symbol
                }
            )
            
            if not strategy_loaded:
                return BacktestResult(
                    config=config,
                    success=False,
                    message="Failed to load strategy code",
                    start_time=start_time,
                    end_time=datetime.now(),
                    execution_time_seconds=0,
                    portfolio_metrics=PortfolioMetrics(),
                    risk_metrics=RiskMetrics()
                )
            
            # Generate trading signals
            signals_result = executor.strategy_function(data, **config.strategy_params)
            
            # Handle both StrategySignals objects and dict returns
            if hasattr(signals_result, 'entries') and hasattr(signals_result, 'exits'):
                # StrategySignals object
                entries = signals_result.entries
                exits = signals_result.exits
            elif isinstance(signals_result, dict) and 'entries' in signals_result:
                # Dict format
                entries = signals_result['entries']
                exits = signals_result.get('exits', pd.Series(False, index=data.index))
            else:
                return BacktestResult(
                    config=config,
                    success=False,
                    message="Strategy must return StrategySignals object or dict with 'entries'",
                    start_time=start_time,
                    end_time=datetime.now(),
                    execution_time_seconds=0,
                    portfolio_metrics=PortfolioMetrics(),
                    risk_metrics=RiskMetrics()
                )
            
            # Convert to boolean series if needed
            if not isinstance(entries, pd.Series):
                entries = pd.Series(entries, index=data.index, dtype=bool)
            if not isinstance(exits, pd.Series):
                exits = pd.Series(exits, index=data.index, dtype=bool)
            
            # Count signals
            signals_generated = entries.sum() + exits.sum()
            signals_executed = 0
            
            # Execute backtest
            position_open = False
            
            for i, (timestamp, row) in enumerate(data.iterrows()):
                current_price = row['close']
                
                # Update portfolio valuation
                portfolio_sim.update_portfolio_value({config.symbol: current_price}, timestamp)
                
                # Process entry signals
                if i < len(entries) and entries.iloc[i] and not position_open:
                    # Calculate position size
                    position_size = portfolio_sim.calculate_position_size(
                        config.symbol, current_price, config.risk_per_trade_pct
                    )
                    
                    if position_size > 0:
                        trade_id = portfolio_sim.open_position(
                            symbol=config.symbol,
                            side=OrderSide.BUY,
                            quantity=position_size,
                            price=current_price,
                            timestamp=timestamp,
                            strategy_id=config.strategy_id
                        )
                        
                        if trade_id:
                            position_open = True
                            signals_executed += 1
                            logger.debug(f"Opened position: {position_size:.6f} @ {current_price:.2f}")
                
                # Process exit signals
                elif i < len(exits) and exits.iloc[i] and position_open:
                    closed_trades = portfolio_sim.close_position(
                        symbol=config.symbol,
                        quantity=None,  # Close entire position
                        price=current_price,
                        timestamp=timestamp,
                        strategy_id=config.strategy_id
                    )
                    
                    if closed_trades:
                        position_open = False
                        signals_executed += 1
                        logger.debug(f"Closed position @ {current_price:.2f}")
            
            # Final portfolio update
            if not data.empty:
                final_price = data['close'].iloc[-1]
                final_timestamp = data.index[-1]
                portfolio_sim.update_portfolio_value({config.symbol: final_price}, final_timestamp)
            
            # Close any remaining open positions
            if position_open:
                portfolio_sim.close_position(
                    symbol=config.symbol,
                    quantity=None,
                    price=data['close'].iloc[-1],
                    timestamp=data.index[-1],
                    strategy_id=config.strategy_id
                )
            
            # Calculate comprehensive metrics
            portfolio_metrics, risk_metrics = portfolio_sim.calculate_comprehensive_metrics()
            
            # Prepare equity curve and drawdown series
            equity_curve = [(ts, val) for ts, val in portfolio_sim.daily_values]
            
            # Calculate drawdown series
            portfolio_values = [val for _, val in equity_curve]
            if portfolio_values:
                cumulative_max = np.maximum.accumulate(portfolio_values)
                drawdown_values = [(val - cum_max) / cum_max * 100 for val, cum_max in zip(portfolio_values, cumulative_max)]
                drawdown_series = [(ts, dd) for (ts, _), dd in zip(equity_curve, drawdown_values)]
            else:
                drawdown_series = []
            
            # Calculate execution rate
            execution_rate = (signals_executed / max(signals_generated, 1)) * 100
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            result = BacktestResult(
                config=config,
                success=True,
                message=f"Backtest completed successfully. {signals_executed}/{signals_generated} signals executed.",
                start_time=start_time,
                end_time=end_time,
                execution_time_seconds=execution_time,
                portfolio_metrics=portfolio_metrics,
                risk_metrics=risk_metrics,
                trades=portfolio_sim.closed_trades,
                portfolio_history=portfolio_sim.portfolio_history,
                daily_returns=portfolio_sim.daily_returns,
                equity_curve=equity_curve,
                drawdown_series=drawdown_series,
                signals_generated=int(signals_generated),
                signals_executed=signals_executed,
                execution_rate_pct=execution_rate
            )
            
            logger.info(f"Backtest completed in {execution_time:.2f}s: "
                       f"Return: {portfolio_metrics.total_return_pct:.2f}%, "
                       f"Sharpe: {portfolio_metrics.sharpe_ratio:.2f}, "
                       f"Max DD: {portfolio_metrics.max_drawdown_pct:.2f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}")
            return BacktestResult(
                config=config,
                success=False,
                message=f"Backtest failed: {str(e)}",
                start_time=start_time,
                end_time=datetime.now(),
                execution_time_seconds=(datetime.now() - start_time).total_seconds(),
                portfolio_metrics=PortfolioMetrics(),
                risk_metrics=RiskMetrics()
            )
    
    def save_backtest_result(self, result: BacktestResult) -> str:
        """
        Save backtest result to database
        
        Returns:
            Backtest ID
        """
        try:
            # For now, save to the backtests table using Epic 5 schema
            backtest_data = {
                'strategy_id': result.config.strategy_id,
                'name': f"Backtest {result.start_time.strftime('%Y-%m-%d %H:%M')}",
                'config': json.dumps(result.config.to_dict()),
                'symbol': result.config.symbol,
                'timeframe': result.config.timeframe,
                'start_date': result.start_time.date(),
                'end_date': result.end_time.date(),
                'initial_capital': result.config.initial_capital,
                'status': 'completed' if result.success else 'failed',
                'progress_percent': 100,
                'execution_time_ms': int(result.execution_time_seconds * 1000),
                'error_message': result.message if not result.success else None,
                'total_return': result.portfolio_metrics.total_return_pct / 100,
                'sharpe_ratio': result.portfolio_metrics.sharpe_ratio,
                'max_drawdown': result.portfolio_metrics.max_drawdown_pct / 100,
                'total_trades': result.portfolio_metrics.total_trades,
                'win_rate': result.portfolio_metrics.win_rate_pct / 100,
                'started_at': result.start_time,
                'completed_at': result.end_time
            }
            
            backtest_id = self.strategy_db._execute_query(
                """INSERT INTO backtests (
                    strategy_id, name, config, symbol, timeframe, start_date, end_date,
                    initial_capital, status, progress_percent, execution_time_ms, error_message,
                    total_return, sharpe_ratio, max_drawdown, total_trades, win_rate,
                    started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(backtest_data.values())
            )
            
            logger.info(f"Backtest result saved with ID: {backtest_id}")
            return str(backtest_id)
            
        except Exception as e:
            logger.error(f"Failed to save backtest result: {e}")
            return ""
    
    def get_backtest_results(self, strategy_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get historical backtest results"""
        try:
            if strategy_id:
                query = """
                    SELECT * FROM backtests 
                    WHERE strategy_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                params = (strategy_id, limit)
            else:
                query = """
                    SELECT * FROM backtests 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                params = (limit,)
            
            results = self.strategy_db._fetch_all(query, params)
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Failed to get backtest results: {e}")
            return []