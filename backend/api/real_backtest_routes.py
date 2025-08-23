"""
Sprint 4: Real Data Pipeline Integration
Connects AI-converted strategies with live cryptocurrency data for accurate backtesting
"""

import sys
from pathlib import Path
import logging
import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import importlib.util
import tempfile
import os

# Add project paths
sys.path.append(str(Path(__file__).parent.parent))

from research.intelligent_converter.working_converter import WorkingPineConverter
from database.data_access import crypto_data

logger = logging.getLogger(__name__)

# Create Blueprint
real_backtest_bp = Blueprint('real_backtest', __name__, url_prefix='/api/real-backtest')

@real_backtest_bp.route('/health', methods=['GET'])
def health_check():
    """Real backtesting service health check"""
    return jsonify({
        "status": "healthy",
        "service": "Real Data Backtesting",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "multi_pair_backtesting",
            "real_market_data",
            "ai_converted_strategies",
            "parallel_execution",
            "dynamic_parameters"
        ]
    })

@real_backtest_bp.route('/pairs/available', methods=['GET'])
def get_available_pairs():
    """Get available trading pairs for backtesting"""
    try:
        # Popular crypto pairs for backtesting
        pairs = [
            {"symbol": "BTCUSDT", "name": "Bitcoin/USDT", "exchange": "BINANCE"},
            {"symbol": "ETHUSDT", "name": "Ethereum/USDT", "exchange": "BINANCE"},
            {"symbol": "ADAUSDT", "name": "Cardano/USDT", "exchange": "BINANCE"},
            {"symbol": "SOLUSDT", "name": "Solana/USDT", "exchange": "BINANCE"},
            {"symbol": "DOTUSDT", "name": "Polkadot/USDT", "exchange": "BINANCE"},
            {"symbol": "LINKUSDT", "name": "Chainlink/USDT", "exchange": "BINANCE"},
            {"symbol": "MATICUSDT", "name": "Polygon/USDT", "exchange": "BINANCE"},
            {"symbol": "AVAXUSDT", "name": "Avalanche/USDT", "exchange": "BINANCE"}
        ]
        
        return jsonify({
            "success": True,
            "pairs": pairs,
            "total": len(pairs)
        })
        
    except Exception as e:
        logger.error(f"Failed to get available pairs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_backtest_bp.route('/timeframes', methods=['GET'])
def get_available_timeframes():
    """Get available timeframes for backtesting"""
    try:
        timeframes = [
            {"id": "1m", "name": "1 Minute", "recommended": False},
            {"id": "5m", "name": "5 Minutes", "recommended": False},
            {"id": "15m", "name": "15 Minutes", "recommended": True},
            {"id": "1h", "name": "1 Hour", "recommended": True},
            {"id": "4h", "name": "4 Hours", "recommended": True},
            {"id": "1d", "name": "1 Day", "recommended": True}
        ]
        
        return jsonify({
            "success": True,
            "timeframes": timeframes
        })
        
    except Exception as e:
        logger.error(f"Failed to get timeframes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@real_backtest_bp.route('/run', methods=['POST'])
def run_real_backtest():
    """
    Run backtest with real market data
    
    Request body:
    {
        "strategy_code": "Python strategy code or strategy_id",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000,
        "parameters": {"rsi_period": 14, "vwap_period": 20}
    }
    """
    try:
        data = request.get_json()
        
        # Extract parameters
        strategy_code = data.get('strategy_code')
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-12-31')
        initial_capital = float(data.get('initial_capital', 10000))
        parameters = data.get('parameters', {})
        
        if not strategy_code:
            return jsonify({"success": False, "error": "strategy_code is required"}), 400
        
        # If strategy_code is an ID, get strategy from database
        if isinstance(strategy_code, str) and len(strategy_code) < 100:
            try:
                db_path = Path(__file__).parent / "strategies.db"
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT name, python_code FROM strategies WHERE id = ?", (strategy_code,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    strategy_name, strategy_code = result
                else:
                    return jsonify({"success": False, "error": f"Strategy {strategy_code} not found"}), 404
            except:
                # Assume it's actual code if DB lookup fails
                strategy_name = "Custom Strategy"
        else:
            strategy_name = "Custom Strategy"
        
        # Fetch real market data
        logger.info(f"Fetching {symbol} data from {start_date} to {end_date} at {timeframe}")
        
        # Calculate data limit based on timeframe and date range
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00').replace('+00:00', ''))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00').replace('+00:00', ''))
        
        # Estimate required data points
        if timeframe == '1m':
            limit = int((end_dt - start_dt).total_seconds() / 60)
        elif timeframe == '5m':
            limit = int((end_dt - start_dt).total_seconds() / 300)
        elif timeframe == '15m':
            limit = int((end_dt - start_dt).total_seconds() / 900)
        elif timeframe == '1h':
            limit = int((end_dt - start_dt).total_seconds() / 3600)
        elif timeframe == '4h':
            limit = int((end_dt - start_dt).total_seconds() / 14400)
        elif timeframe == '1d':
            limit = int((end_dt - start_dt).days)
        else:
            limit = 1000  # Default
        
        limit = min(limit, 5000)  # Cap at 5000 for performance
        
        # Get real market data
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol=symbol,
            exchange="BINANCE",
            timeframe=timeframe,
            limit=limit
        )
        
        if df.empty:
            return jsonify({
                "success": False,
                "error": f"No market data available for {symbol} {timeframe}"
            }), 400
        
        logger.info(f"Retrieved {len(df)} data points for backtesting")
        
        # Prepare strategy execution environment
        strategy_globals = {
            'pd': pd,
            'np': np,
            'StrategySignals': create_strategy_signals_class(),
            'StrategyParameter': create_strategy_parameter_class(),
            'StrategyMetadata': create_strategy_metadata_class()
        }
        
        # Execute strategy code
        try:
            exec(strategy_code, strategy_globals)
            
            if 'build_signals' not in strategy_globals:
                return jsonify({
                    "success": False,
                    "error": "Strategy must define build_signals function"
                }), 400
            
            build_signals = strategy_globals['build_signals']
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return jsonify({
                "success": False,
                "error": f"Strategy execution failed: {str(e)}"
            }), 500
        
        # Generate trading signals
        try:
            signals = build_signals(df, **parameters)
            
            if not hasattr(signals, 'entries') or not hasattr(signals, 'exits'):
                return jsonify({
                    "success": False,
                    "error": "Strategy must return StrategySignals with entries and exits"
                }), 400
                
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return jsonify({
                "success": False,
                "error": f"Signal generation failed: {str(e)}"
            }), 500
        
        # Run backtest simulation
        backtest_results = run_backtest_simulation(
            df=df,
            signals=signals,
            initial_capital=initial_capital,
            commission=0.001  # 0.1% commission
        )
        
        return jsonify({
            "success": True,
            "strategy_name": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "data_points": len(df),
            "date_range": {
                "start": df.index[0].isoformat(),
                "end": df.index[-1].isoformat()
            },
            "parameters": parameters,
            "results": backtest_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def run_backtest_simulation(df: pd.DataFrame, signals, initial_capital: float, commission: float = 0.001):
    """Run realistic backtest simulation with proper trade management"""
    
    # Initialize backtest state
    capital = initial_capital
    position = 0.0
    position_value = 0.0
    trades = []
    equity_curve = []
    
    # Convert signals to numpy arrays for performance
    entries = np.array(signals.entries) if hasattr(signals.entries, '__iter__') else signals.entries
    exits = np.array(signals.exits) if hasattr(signals.exits, '__iter__') else signals.exits
    
    # Ensure entries and exits are boolean arrays
    if len(entries) != len(df):
        entries = np.zeros(len(df), dtype=bool)
    if len(exits) != len(df):
        exits = np.zeros(len(df), dtype=bool)
    
    for i in range(len(df)):
        current_price = df.iloc[i]['close']
        current_time = df.index[i]
        
        # Calculate current portfolio value
        if position > 0:
            position_value = position * current_price
            total_value = capital + position_value
        else:
            total_value = capital
        
        equity_curve.append({
            'timestamp': current_time.isoformat(),
            'equity': float(total_value),
            'position': float(position),
            'cash': float(capital)
        })
        
        # Handle exit signals first
        if position > 0 and (exits[i] if i < len(exits) else False):
            # Sell position
            sell_value = position * current_price
            commission_cost = sell_value * commission
            capital += sell_value - commission_cost
            
            trades.append({
                'type': 'sell',
                'timestamp': current_time.isoformat(),
                'price': float(current_price),
                'quantity': float(position),
                'value': float(sell_value),
                'commission': float(commission_cost),
                'capital_after': float(capital)
            })
            
            position = 0.0
            position_value = 0.0
        
        # Handle entry signals
        elif position == 0 and (entries[i] if i < len(entries) else False):
            # Buy position (invest all available capital)
            if capital > 100:  # Minimum trade size
                commission_cost = capital * commission
                available_for_investment = capital - commission_cost
                position = available_for_investment / current_price
                position_value = position * current_price
                capital = 0.0
                
                trades.append({
                    'type': 'buy',
                    'timestamp': current_time.isoformat(),
                    'price': float(current_price),
                    'quantity': float(position),
                    'value': float(position_value),
                    'commission': float(commission_cost),
                    'capital_after': float(capital)
                })
    
    # Calculate final portfolio value
    final_price = df.iloc[-1]['close']
    if position > 0:
        final_position_value = position * final_price
        final_total_value = capital + final_position_value
    else:
        final_total_value = capital
    
    # Calculate performance metrics
    total_return = (final_total_value - initial_capital) / initial_capital * 100
    
    # Calculate equity curve statistics
    equity_values = [point['equity'] for point in equity_curve]
    if len(equity_values) > 1:
        returns = np.diff(equity_values) / equity_values[:-1]
        returns = returns[~np.isnan(returns)]  # Remove NaN values
        
        if len(returns) > 0:
            volatility = np.std(returns) * np.sqrt(252 * 24)  # Annualized for hourly data
            sharpe_ratio = (np.mean(returns) * 252 * 24) / volatility if volatility > 0 else 0
        else:
            volatility = 0
            sharpe_ratio = 0
            
        max_drawdown = calculate_max_drawdown(equity_values)
    else:
        volatility = 0
        sharpe_ratio = 0
        max_drawdown = 0
    
    # Trade statistics
    winning_trades = [t for t in trades if t['type'] == 'sell' and len([b for b in trades if b['type'] == 'buy' and b['timestamp'] < t['timestamp']]) > 0]
    if len(winning_trades) > 0 and len(trades) >= 2:
        # Match buy/sell pairs to calculate profit/loss
        trade_pairs = []
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        for i, sell in enumerate(sell_trades):
            if i < len(buy_trades):
                buy = buy_trades[i]
                profit_loss = (sell['price'] - buy['price']) / buy['price'] * 100
                trade_pairs.append(profit_loss)
        
        win_rate = len([p for p in trade_pairs if p > 0]) / len(trade_pairs) * 100 if trade_pairs else 0
    else:
        win_rate = 0
    
    return {
        "initial_capital": float(initial_capital),
        "final_value": float(final_total_value),
        "total_return_pct": float(total_return),
        "total_trades": len(trades),
        "win_rate_pct": float(win_rate),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown_pct": float(max_drawdown),
        "volatility_pct": float(volatility * 100),
        "trades": trades[-10:],  # Last 10 trades for display
        "equity_curve": equity_curve[-100:],  # Last 100 equity points
        "signals_generated": {
            "total_entry_signals": int(np.sum(entries)) if hasattr(entries, '__iter__') else 0,
            "total_exit_signals": int(np.sum(exits)) if hasattr(exits, '__iter__') else 0
        }
    }

def calculate_max_drawdown(equity_values):
    """Calculate maximum drawdown percentage"""
    if len(equity_values) < 2:
        return 0.0
    
    peak = equity_values[0]
    max_drawdown = 0.0
    
    for value in equity_values[1:]:
        if value > peak:
            peak = value
        else:
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
    
    return max_drawdown

def create_strategy_signals_class():
    """Create StrategySignals class for strategy execution"""
    class StrategySignals:
        def __init__(self, entries, exits):
            self.entries = entries
            self.exits = exits
    return StrategySignals

def create_strategy_parameter_class():
    """Create StrategyParameter class for strategy execution"""
    class StrategyParameter:
        def __init__(self, name, default, min_val=None, max_val=None, description=None):
            self.name = name
            self.default = default
            self.min_val = min_val
            self.max_val = max_val
            self.description = description
    return StrategyParameter

def execute_backtest_logic(strategy_code, symbol, timeframe, start_date, end_date, initial_capital, parameters):
    """Execute backtest logic directly without Flask request context"""
    try:
        # Calculate data limit based on timeframe and date range
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00').replace('+00:00', ''))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00').replace('+00:00', ''))
        
        # Estimate required data points
        if timeframe == '1m':
            limit = int((end_dt - start_dt).total_seconds() / 60)
        elif timeframe == '5m':
            limit = int((end_dt - start_dt).total_seconds() / 300)
        elif timeframe == '15m':
            limit = int((end_dt - start_dt).total_seconds() / 900)
        elif timeframe == '1h':
            limit = int((end_dt - start_dt).total_seconds() / 3600)
        elif timeframe == '4h':
            limit = int((end_dt - start_dt).total_seconds() / 14400)
        elif timeframe == '1d':
            limit = int((end_dt - start_dt).days)
        else:
            limit = 1000  # Default
        
        limit = min(limit, 5000)  # Cap at 5000 for performance
        
        # Get real market data
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol=symbol,
            exchange="BINANCE",
            timeframe=timeframe,
            limit=limit
        )
        
        if df.empty:
            return {
                "success": False,
                "error": f"No market data available for {symbol} {timeframe}"
            }
        
        logger.info(f"Retrieved {len(df)} data points for backtesting")
        
        # Prepare strategy execution environment
        strategy_globals = {
            'pd': pd,
            'np': np,
            'StrategySignals': create_strategy_signals_class(),
            'StrategyParameter': create_strategy_parameter_class(),
            'StrategyMetadata': create_strategy_metadata_class()
        }
        
        # Execute strategy code
        try:
            exec(strategy_code, strategy_globals)
            
            if 'build_signals' not in strategy_globals:
                return {
                    "success": False,
                    "error": "Strategy must define build_signals function"
                }
            
            build_signals = strategy_globals['build_signals']
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return {
                "success": False,
                "error": f"Strategy execution failed: {str(e)}"
            }
        
        # Generate trading signals
        try:
            signals = build_signals(df, **parameters)
            
            if not hasattr(signals, 'entries') or not hasattr(signals, 'exits'):
                return {
                    "success": False,
                    "error": "Strategy must return StrategySignals with entries and exits"
                }
                
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return {
                "success": False,
                "error": f"Signal generation failed: {str(e)}"
            }
        
        # Run backtest simulation
        backtest_results = run_backtest_simulation(
            df=df,
            signals=signals,
            initial_capital=initial_capital,
            commission=0.001  # 0.1% commission
        )
        
        return {
            "success": True,
            "strategy_name": "Converted Strategy",
            "symbol": symbol,
            "timeframe": timeframe,
            "data_points": len(df),
            "date_range": {
                "start": df.index[0].isoformat(),
                "end": df.index[-1].isoformat()
            },
            "parameters": parameters,
            "results": backtest_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Backtest execution failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_strategy_metadata_class():
    """Create StrategyMetadata class for strategy execution"""
    class StrategyMetadata:
        def __init__(self, name, description, parameters):
            self.name = name
            self.description = description
            self.parameters = parameters
    return StrategyMetadata

@real_backtest_bp.route('/convert-and-backtest', methods=['POST'])
def convert_and_backtest():
    """
    Convert Pine Script strategy and immediately backtest with real data
    
    Request body:
    {
        "pine_code": "Pine Script code",
        "strategy_name": "MyStrategy",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000,
        "custom_parameters": {"rsi_period": 21}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({"success": False, "error": "pine_code is required"}), 400
        
        pine_code = data['pine_code']
        strategy_name = data.get('strategy_name', 'ConvertedStrategy')
        
        # Convert Pine Script using intelligent converter
        converter = WorkingPineConverter()
        conversion_result = converter.convert_strategy(pine_code, strategy_name)
        
        if not conversion_result.success:
            return jsonify({
                "success": False,
                "error": f"Conversion failed: {conversion_result.error_message}"
            }), 500
        
        # Merge default parameters with custom parameters
        default_params = {p.name: p.default for p in conversion_result.parameters}
        custom_params = data.get('custom_parameters', {})
        final_params = {**default_params, **custom_params}
        
        # Run backtest with converted strategy
        backtest_request = {
            "strategy_code": conversion_result.python_code,
            "symbol": data.get('symbol', 'BTCUSDT'),
            "timeframe": data.get('timeframe', '1h'),
            "start_date": data.get('start_date', '2024-01-01'),
            "end_date": data.get('end_date', '2024-12-31'),
            "initial_capital": data.get('initial_capital', 10000),
            "parameters": final_params
        }
        
        # Run backtest directly with converted strategy  
        backtest_data = execute_backtest_logic(
            strategy_code=conversion_result.python_code,
            symbol=data.get('symbol', 'BTCUSDT'),
            timeframe=data.get('timeframe', '1h'),
            start_date=data.get('start_date', '2024-01-01'),
            end_date=data.get('end_date', '2024-12-31'),
            initial_capital=data.get('initial_capital', 10000),
            parameters=final_params
        )
        
        return jsonify({
            "success": True,
            "conversion_summary": {
                "parameters_extracted": len(conversion_result.parameters),
                "indicators_found": len(getattr(conversion_result, 'analysis_used', {}).get('momentum_system', {}).get('indicators', {})),
                "conversion_steps": len(getattr(conversion_result, 'analysis_used', {}).get('conversion_roadmap', []))
            },
            "extracted_parameters": [
                {
                    "name": p.name,
                    "default": p.default,
                    "min_val": p.min_val,
                    "max_val": p.max_val,
                    "description": p.description
                } for p in conversion_result.parameters
            ],
            "final_parameters": final_params,
            "backtest_results": backtest_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Convert and backtest failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Export the blueprint
__all__ = ['real_backtest_bp']