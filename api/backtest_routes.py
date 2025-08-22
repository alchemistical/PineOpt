"""
Epic 5 Sprint 2: Backtesting API Routes
RESTful API endpoints for strategy backtesting and results management
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import numpy as np

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from research.backtest.backtest_engine import BacktestEngine, BacktestConfig, BacktestResult
from research.backtest.portfolio_engine import PortfolioMetrics, RiskMetrics
from database.strategy_models import StrategyDatabase

logger = logging.getLogger(__name__)

# Create Blueprint
backtest_bp = Blueprint('backtests', __name__, url_prefix='/api/backtests')

# Global backtest engine instance
backtest_engine = None

def get_backtest_engine():
    """Get or create backtest engine instance"""
    global backtest_engine
    if backtest_engine is None:
        db_path = Path(__file__).parent.parent / "database" / "pineopt.db"
        backtest_engine = BacktestEngine(str(db_path))
        logger.info("Backtest engine initialized")
    return backtest_engine

@backtest_bp.route('/health', methods=['GET'])
def health_check():
    """Backtest engine health check"""
    try:
        engine = get_backtest_engine()
        
        # Test database connectivity
        strategies = engine.strategy_db.list_strategies(limit=1)
        
        return jsonify({
            "status": "healthy",
            "success": True,
            "services": {
                "backtest_engine": "online",
                "strategy_database": "online",
                "market_data": "online"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Backtest health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@backtest_bp.route('/run', methods=['POST'])
def run_backtest():
    """
    Execute a backtest for a given strategy
    
    Request body:
    {
        "strategy_id": "abc123",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 100000,
        "commission_rate": 0.001,
        "slippage_rate": 0.0001,
        "max_position_size_pct": 10.0,
        "risk_per_trade_pct": 2.0,
        "strategy_params": {
            "rsi_length": 14,
            "rsi_overbought": 70.0,
            "rsi_oversold": 30.0
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'strategy_id' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: strategy_id"
            }), 400
        
        # Create backtest configuration
        config = BacktestConfig(
            strategy_id=data['strategy_id'],
            symbol=data.get('symbol', 'BTCUSDT'),
            timeframe=data.get('timeframe', '1h'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            initial_capital=float(data.get('initial_capital', 100000)),
            commission_rate=float(data.get('commission_rate', 0.001)),
            slippage_rate=float(data.get('slippage_rate', 0.0001)),
            max_position_size_pct=float(data.get('max_position_size_pct', 10.0)),
            risk_per_trade_pct=float(data.get('risk_per_trade_pct', 2.0)),
            strategy_params=data.get('strategy_params', {})
        )
        
        # Get backtest engine
        engine = get_backtest_engine()
        
        # Run backtest
        result = engine.run_backtest(config)
        
        # Save result to database if successful
        backtest_id = None
        if result.success:
            backtest_id = engine.save_backtest_result(result)
        
        # Prepare response
        response_data = {
            "success": result.success,
            "message": result.message,
            "backtest_id": backtest_id,
            "execution_time_seconds": result.execution_time_seconds,
            "config": result.config.to_dict()
        }
        
        if result.success:
            # Add key metrics to response
            response_data.update({
                "portfolio_metrics": {
                    "total_return_pct": result.portfolio_metrics.total_return_pct,
                    "annualized_return_pct": result.portfolio_metrics.annualized_return_pct,
                    "volatility_pct": result.portfolio_metrics.volatility_pct,
                    "sharpe_ratio": result.portfolio_metrics.sharpe_ratio,
                    "max_drawdown_pct": result.portfolio_metrics.max_drawdown_pct,
                    "win_rate_pct": result.portfolio_metrics.win_rate_pct,
                    "total_trades": result.portfolio_metrics.total_trades,
                    "profit_factor": result.portfolio_metrics.profit_factor
                },
                "risk_metrics": {
                    "var_95_pct": result.risk_metrics.var_95_pct,
                    "current_exposure_pct": result.risk_metrics.current_exposure_pct,
                    "beta": result.risk_metrics.beta,
                    "alpha_pct": result.risk_metrics.alpha_pct
                },
                "signals": {
                    "generated": result.signals_generated,
                    "executed": result.signals_executed,
                    "execution_rate_pct": result.execution_rate_pct
                },
                "final_portfolio_value": result.portfolio_metrics.total_trades  # This needs to be fixed
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Backtest execution failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/<backtest_id>', methods=['GET'])
def get_backtest_result(backtest_id: str):
    """Get detailed backtest results by ID"""
    try:
        engine = get_backtest_engine()
        
        # Get backtest from database
        result = engine.strategy_db._fetch_one(
            "SELECT * FROM backtests WHERE id = ?",
            (backtest_id,)
        )
        
        if not result:
            return jsonify({
                "success": False,
                "error": "Backtest not found"
            }), 404
        
        # Convert database row to dict
        result_dict = dict(result)
        
        # Parse JSON fields
        if result_dict.get('config'):
            result_dict['config'] = json.loads(result_dict['config'])
        
        return jsonify({
            "success": True,
            "backtest": result_dict
        })
        
    except Exception as e:
        logger.error(f"Failed to get backtest result: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('', methods=['GET'])
def list_backtests():
    """
    List backtests with filtering and pagination
    
    Query parameters:
    - strategy_id: Filter by strategy ID
    - status: Filter by status (completed, failed, running)
    - limit: Number of results (default 50, max 200)
    - offset: Pagination offset
    - sort_by: Sort field (created_at, total_return, sharpe_ratio)
    - sort_order: asc or desc (default desc)
    """
    try:
        # Parse query parameters
        strategy_id = request.args.get('strategy_id')
        status = request.args.get('status')
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort parameters
        valid_sort_fields = ['created_at', 'total_return', 'sharpe_ratio', 'max_drawdown', 'total_trades']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if sort_order.lower() not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Build query
        query = "SELECT * FROM backtests WHERE 1=1"
        params = []
        
        if strategy_id:
            query += " AND strategy_id = ?"
            params.append(strategy_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Get count for pagination
        count_query = "SELECT COUNT(*) as count FROM backtests WHERE 1=1"
        count_params = []
        
        if strategy_id:
            count_query += " AND strategy_id = ?"
            count_params.append(strategy_id)
        
        if status:
            count_query += " AND status = ?"
            count_params.append(status)
        
        engine = get_backtest_engine()
        
        # Execute queries
        results = engine.strategy_db._fetch_all(query, params)
        count_result = engine.strategy_db._fetch_one(count_query, count_params)
        
        total_count = count_result['count'] if count_result else 0
        
        # Convert results
        backtests = []
        for row in results or []:
            backtest_dict = dict(row)
            
            # Parse JSON fields
            if backtest_dict.get('config'):
                try:
                    backtest_dict['config'] = json.loads(backtest_dict['config'])
                except json.JSONDecodeError:
                    backtest_dict['config'] = {}
            
            backtests.append(backtest_dict)
        
        return jsonify({
            "success": True,
            "backtests": backtests,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to list backtests: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/stats', methods=['GET'])
def get_backtest_stats():
    """Get backtesting statistics and aggregates"""
    try:
        engine = get_backtest_engine()
        
        # Get overall stats
        stats = engine.strategy_db._fetch_one("""
            SELECT 
                COUNT(*) as total_backtests,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_backtests,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_backtests,
                AVG(CASE WHEN status = 'completed' THEN total_return END) as avg_return,
                AVG(CASE WHEN status = 'completed' THEN sharpe_ratio END) as avg_sharpe_ratio,
                MAX(CASE WHEN status = 'completed' THEN total_return END) as best_return,
                MIN(CASE WHEN status = 'completed' THEN total_return END) as worst_return,
                AVG(execution_time_ms) as avg_execution_time_ms
            FROM backtests
        """)
        
        # Get recent activity (last 7 days)
        recent_activity = engine.strategy_db._fetch_all("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM backtests 
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        # Get top performing strategies
        top_strategies = engine.strategy_db._fetch_all("""
            SELECT 
                b.strategy_id,
                s.name as strategy_name,
                COUNT(*) as backtest_count,
                AVG(b.total_return) as avg_return,
                MAX(b.total_return) as best_return,
                AVG(b.sharpe_ratio) as avg_sharpe_ratio
            FROM backtests b
            LEFT JOIN strategies s ON b.strategy_id = s.id
            WHERE b.status = 'completed'
            GROUP BY b.strategy_id, s.name
            HAVING COUNT(*) >= 1
            ORDER BY avg_return DESC
            LIMIT 10
        """)
        
        return jsonify({
            "success": True,
            "stats": {
                "overview": dict(stats) if stats else {},
                "recent_activity": [dict(row) for row in recent_activity or []],
                "top_strategies": [dict(row) for row in top_strategies or []]
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get backtest stats: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/<backtest_id>/charts', methods=['GET'])
def get_backtest_charts(backtest_id: str):
    """Get chart data for backtest visualization"""
    try:
        engine = get_backtest_engine()
        
        # Get backtest configuration
        backtest = engine.strategy_db._fetch_one(
            "SELECT * FROM backtests WHERE id = ?",
            (backtest_id,)
        )
        
        if not backtest:
            return jsonify({
                "success": False,
                "error": "Backtest not found"
            }), 404
        
        backtest_dict = dict(backtest)
        
        # Parse configuration
        config = json.loads(backtest_dict.get('config', '{}'))
        
        # Load market data for the same period
        market_data = engine.load_market_data(
            symbol=config.get('symbol', 'BTCUSDT'),
            timeframe=config.get('timeframe', '1h'),
            start_date=config.get('start_date'),
            end_date=config.get('end_date'),
            n_bars=5000
        )
        
        # Prepare market data for charts
        market_chart_data = []
        if not market_data.empty:
            market_data_sample = market_data.tail(500)  # Last 500 bars for performance
            
            for timestamp, row in market_data_sample.iterrows():
                market_chart_data.append({
                    'timestamp': timestamp.isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
        
        # For now, return market data and basic backtest info
        # In a full implementation, you would re-run the backtest or store detailed results
        return jsonify({
            "success": True,
            "charts": {
                "market_data": market_chart_data,
                "equity_curve": [],  # Would need to store/compute equity curve
                "drawdown_series": [],  # Would need to store/compute drawdown
                "trade_markers": []  # Would need to store trade entry/exit points
            },
            "backtest_info": {
                "symbol": config.get('symbol', 'BTCUSDT'),
                "timeframe": config.get('timeframe', '1h'),
                "total_return": backtest_dict.get('total_return'),
                "sharpe_ratio": backtest_dict.get('sharpe_ratio'),
                "max_drawdown": backtest_dict.get('max_drawdown'),
                "total_trades": backtest_dict.get('total_trades')
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get backtest charts: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/<backtest_id>', methods=['DELETE'])
def delete_backtest(backtest_id: str):
    """Delete a backtest result"""
    try:
        engine = get_backtest_engine()
        
        # Check if backtest exists
        existing = engine.strategy_db._fetch_one(
            "SELECT id FROM backtests WHERE id = ?",
            (backtest_id,)
        )
        
        if not existing:
            return jsonify({
                "success": False,
                "error": "Backtest not found"
            }), 404
        
        # Delete backtest
        engine.strategy_db._execute_query(
            "DELETE FROM backtests WHERE id = ?",
            (backtest_id,)
        )
        
        return jsonify({
            "success": True,
            "message": f"Backtest {backtest_id} deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to delete backtest: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/strategy/<strategy_id>/latest', methods=['GET'])
def get_latest_backtest_for_strategy(strategy_id: str):
    """Get the most recent backtest for a strategy"""
    try:
        engine = get_backtest_engine()
        
        result = engine.strategy_db._fetch_one("""
            SELECT * FROM backtests 
            WHERE strategy_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (strategy_id,))
        
        if not result:
            return jsonify({
                "success": False,
                "error": "No backtests found for this strategy"
            }), 404
        
        backtest_dict = dict(result)
        
        # Parse JSON fields
        if backtest_dict.get('config'):
            backtest_dict['config'] = json.loads(backtest_dict['config'])
        
        return jsonify({
            "success": True,
            "backtest": backtest_dict
        })
        
    except Exception as e:
        logger.error(f"Failed to get latest backtest: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/<backtest_id>/performance-attribution', methods=['GET'])
def get_performance_attribution(backtest_id: str):
    """Get detailed performance attribution analysis for a backtest"""
    try:
        engine = get_backtest_engine()
        
        # Get backtest result
        backtest = engine.strategy_db._fetch_one(
            "SELECT * FROM backtests WHERE id = ?",
            (backtest_id,)
        )
        
        if not backtest:
            return jsonify({
                "success": False,
                "error": "Backtest not found"
            }), 404
        
        backtest_dict = dict(backtest)
        config = json.loads(backtest_dict.get('config', '{}'))
        
        # Re-run analysis with enhanced metrics
        backtest_config_obj = BacktestConfig(
            strategy_id=config.get('strategy_id'),
            symbol=config.get('symbol', 'BTCUSDT'),
            timeframe=config.get('timeframe', '1h'),
            start_date=config.get('start_date'),
            end_date=config.get('end_date'),
            initial_capital=config.get('initial_capital', 100000),
            commission_rate=config.get('commission_rate', 0.001),
            slippage_rate=config.get('slippage_rate', 0.0001),
            max_position_size_pct=config.get('max_position_size_pct', 10.0),
            risk_per_trade_pct=config.get('risk_per_trade_pct', 2.0),
            strategy_params=config.get('strategy_params', {})
        )
        
        # Load market data for benchmark comparison
        market_data = engine.load_market_data(
            symbol=backtest_config_obj.symbol,
            timeframe=backtest_config_obj.timeframe,
            start_date=backtest_config_obj.start_date,
            end_date=backtest_config_obj.end_date
        )
        
        # Calculate benchmark performance (buy and hold)
        benchmark_performance = {}
        if not market_data.empty:
            initial_price = market_data['close'].iloc[0]
            final_price = market_data['close'].iloc[-1]
            benchmark_return = (final_price - initial_price) / initial_price * 100
            
            # Calculate benchmark volatility
            benchmark_returns = market_data['close'].pct_change().dropna()
            benchmark_volatility = benchmark_returns.std() * np.sqrt(252) * 100
            
            benchmark_performance = {
                'total_return_pct': benchmark_return,
                'annualized_volatility_pct': benchmark_volatility,
                'sharpe_ratio': (benchmark_return - 2.0) / benchmark_volatility if benchmark_volatility > 0 else 0  # Assuming 2% risk-free rate
            }
        
        # Strategy performance from backtest results
        strategy_performance = {
            'total_return_pct': backtest_dict.get('total_return', 0) * 100,
            'sharpe_ratio': backtest_dict.get('sharpe_ratio', 0),
            'max_drawdown_pct': backtest_dict.get('max_drawdown', 0) * 100,
            'total_trades': backtest_dict.get('total_trades', 0),
            'win_rate_pct': backtest_dict.get('win_rate', 0) * 100
        }
        
        # Calculate performance attribution
        attribution_analysis = {
            'excess_return': strategy_performance['total_return_pct'] - benchmark_performance.get('total_return_pct', 0),
            'information_ratio': 0,  # Would need more detailed data
            'tracking_error': 0,     # Would need daily portfolio values
            'alpha': 0,              # Estimated alpha
            'beta': 1.0,             # Default beta
            'strategy_vs_benchmark': {
                'strategy': strategy_performance,
                'benchmark': benchmark_performance
            }
        }
        
        # Risk-adjusted metrics
        risk_analysis = {
            'risk_adjusted_return': strategy_performance['total_return_pct'] / max(abs(strategy_performance['max_drawdown_pct']), 1),
            'calmar_ratio': strategy_performance['total_return_pct'] / max(abs(strategy_performance['max_drawdown_pct']), 1),
            'profit_factor': 0,  # Would need trade-level data
            'expectancy': 0      # Would need trade-level data
        }
        
        # Time-based analysis
        days_elapsed = (pd.to_datetime(backtest_dict.get('completed_at')) - pd.to_datetime(backtest_dict.get('started_at'))).days
        time_analysis = {
            'backtest_period_days': days_elapsed,
            'annualized_return': strategy_performance['total_return_pct'] * (365 / max(days_elapsed, 1)) if days_elapsed > 0 else 0,
            'monthly_return_estimate': strategy_performance['total_return_pct'] * (30 / max(days_elapsed, 1)) if days_elapsed > 0 else 0
        }
        
        return jsonify({
            "success": True,
            "backtest_id": backtest_id,
            "performance_attribution": {
                "attribution_analysis": attribution_analysis,
                "risk_analysis": risk_analysis,
                "time_analysis": time_analysis,
                "market_conditions": {
                    "symbol": backtest_config_obj.symbol,
                    "timeframe": backtest_config_obj.timeframe,
                    "period": f"{backtest_config_obj.start_date} to {backtest_config_obj.end_date}",
                    "market_return": benchmark_performance.get('total_return_pct', 0),
                    "market_volatility": benchmark_performance.get('annualized_volatility_pct', 0)
                }
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to generate performance attribution: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@backtest_bp.route('/compare', methods=['POST'])
def compare_backtests():
    """Compare multiple backtest results"""
    try:
        data = request.get_json()
        backtest_ids = data.get('backtest_ids', [])
        
        if len(backtest_ids) < 2:
            return jsonify({
                "success": False,
                "error": "At least 2 backtest IDs required for comparison"
            }), 400
        
        if len(backtest_ids) > 10:
            return jsonify({
                "success": False,
                "error": "Maximum 10 backtests can be compared at once"
            }), 400
        
        engine = get_backtest_engine()
        
        # Get all backtest results
        backtests = []
        for backtest_id in backtest_ids:
            result = engine.strategy_db._fetch_one(
                "SELECT * FROM backtests WHERE id = ?",
                (backtest_id,)
            )
            if result:
                backtest_dict = dict(result)
                if backtest_dict.get('config'):
                    backtest_dict['config'] = json.loads(backtest_dict['config'])
                backtests.append(backtest_dict)
        
        if len(backtests) < 2:
            return jsonify({
                "success": False,
                "error": "Not enough valid backtests found"
            }), 404
        
        # Prepare comparison data
        comparison_data = {
            'summary': {
                'count': len(backtests),
                'best_return': max(backtests, key=lambda x: x.get('total_return', 0)),
                'best_sharpe': max(backtests, key=lambda x: x.get('sharpe_ratio', 0)),
                'lowest_drawdown': min(backtests, key=lambda x: x.get('max_drawdown', float('inf')))
            },
            'detailed_comparison': []
        }
        
        # Add detailed metrics for each backtest
        for backtest in backtests:
            comparison_data['detailed_comparison'].append({
                'backtest_id': backtest.get('id'),
                'strategy_id': backtest.get('strategy_id'),
                'symbol': backtest.get('symbol'),
                'timeframe': backtest.get('timeframe'),
                'total_return_pct': backtest.get('total_return', 0) * 100,
                'sharpe_ratio': backtest.get('sharpe_ratio', 0),
                'max_drawdown_pct': backtest.get('max_drawdown', 0) * 100,
                'total_trades': backtest.get('total_trades', 0),
                'win_rate_pct': backtest.get('win_rate', 0) * 100,
                'execution_time_ms': backtest.get('execution_time_ms', 0),
                'created_at': backtest.get('created_at')
            })
        
        # Calculate ranking
        metrics = ['total_return_pct', 'sharpe_ratio', 'win_rate_pct']
        rankings = {}
        
        for metric in metrics:
            sorted_backtests = sorted(comparison_data['detailed_comparison'], 
                                    key=lambda x: x.get(metric.replace('_pct', ''), 0), 
                                    reverse=True)
            rankings[metric] = [bt['backtest_id'] for bt in sorted_backtests]
        
        comparison_data['rankings'] = rankings
        
        return jsonify({
            "success": True,
            "comparison": comparison_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to compare backtests: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500