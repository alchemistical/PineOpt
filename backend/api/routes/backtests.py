"""
Backtest Routes
Epic 7 Sprint 2 - Foundation & Middleware

Consolidates backtest endpoints from:
- backtest_routes.py
- real_backtest_routes.py

TODO Sprint 2 Tasks:
[ ] Migrate standard backtesting endpoints
[ ] Migrate real data backtesting endpoints
[ ] Add backtest progress tracking
[ ] Add standardized error handling
[ ] Add response formatting
[ ] Add backtest result persistence
[ ] Update frontend API calls
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import json
import logging
import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

# Create blueprint
backtest_bp = Blueprint('backtests', __name__, url_prefix='/api/v1/backtests')

# Global instances (will be lazy-loaded)
backtest_engine = None
converter = None


def get_backtest_engine():
    """Get or create backtest engine instance"""
    global backtest_engine
    if backtest_engine is None:
        try:
            # Add project root to path
            root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from research.backtest.backtest_engine import BacktestEngine
            db_path = os.path.join(root_path, 'database', 'pineopt.db')
            backtest_engine = BacktestEngine(str(db_path))
            current_app.logger.info("Backtest engine initialized")
        except ImportError as e:
            current_app.logger.warning(f"Backtest engine not available: {e}")
            backtest_engine = None
    return backtest_engine


def get_converter():
    """Get or create working converter instance"""
    global converter
    if converter is None:
        try:
            # Add project root to path
            root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from research.intelligent_converter.working_converter import WorkingPineConverter
            converter = WorkingPineConverter()
            current_app.logger.info("Working converter initialized")
        except ImportError as e:
            current_app.logger.warning(f"Working converter not available: {e}")
            converter = None
    return converter


@backtest_bp.route('/')
def backtest_info():
    """
    Backtest API information
    
    Returns:
        JSON response with available backtest endpoints
    """
    return jsonify({
        'api': 'Backtest Management API',
        'version': '1.0.0',
        'epic': 'Epic 7 Sprint 2 - Middleware & Advanced Features',
        'endpoints': {
            'health': 'GET /api/v1/backtests/health',
            'run': 'POST /api/v1/backtests/run',
            'convert_and_backtest': 'POST /api/v1/backtests/convert-and-backtest',
            'results': 'GET /api/v1/backtests/results/<backtest_id>',
            'history': 'GET /api/v1/backtests/history',
            'pairs_available': 'GET /api/v1/backtests/pairs/available',
            'progress': 'GET /api/v1/backtests/progress/<task_id>',
            'cancel': 'DELETE /api/v1/backtests/<backtest_id>'
        },
        'status': 'Sprint 2 - Implementation in progress',
        'consolidates': [
            'backtest_routes.py',
            'real_backtest_routes.py'
        ]
    })


@backtest_bp.route('/health', methods=['GET'])
def health_check():
    """
    Backtest service health check
    
    Returns:
        JSON response with service status and capabilities
    """
    try:
        # Check service availability
        engine_available = get_backtest_engine() is not None
        converter_available = get_converter() is not None
        
        # Test database connectivity
        db_status = 'unknown'
        try:
            from .db_helper import get_database_access
            da = get_database_access()
            stats = da.get_database_stats()
            db_status = 'available' if stats else 'unavailable'
        except Exception:
            db_status = 'unavailable'
        
        capabilities = []
        if engine_available:
            capabilities.extend([
                'strategy_backtesting',
                'portfolio_metrics',
                'risk_analysis',
                'performance_reporting'
            ])
        if converter_available:
            capabilities.extend([
                'pine_to_python_conversion',
                'real_time_backtesting',
                'multi_pair_testing'
            ])
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'service': 'Backtest Management',
            'status': 'healthy',
            'services': {
                'backtest_engine': 'available' if engine_available else 'unavailable',
                'working_converter': 'available' if converter_available else 'unavailable',
                'database': db_status
            },
            'capabilities': capabilities
        })
    
    except Exception as e:
        current_app.logger.error(f"Backtest health check failed: {e}")
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@backtest_bp.route('/run', methods=['POST'])
def run_backtest():
    """
    Run backtest on existing strategy
    
    Request Body:
        {
            "strategy_id": "123",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 10000,
            "parameters": {...}
        }
    
    Returns:
        JSON response with backtest results
    """
    try:
        data = request.get_json()
        
        if not data or 'strategy_id' not in data:
            return jsonify({
                'error': 'strategy_id is required in request body',
                'status': 'error'
            }), 400
        
        strategy_id = data['strategy_id']
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2023-12-31')
        initial_capital = data.get('initial_capital', 10000)
        parameters = data.get('parameters', {})
        
        # Get strategy from database
        from .db_helper import get_database_access
        da = get_database_access()
        
        strategy = da.get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Get backtest engine
        engine = get_backtest_engine()
        if not engine:
            return jsonify({
                'error': 'Backtest engine not available',
                'status': 'error'
            }), 503
        
        current_app.logger.info(f"Running backtest for strategy {strategy_id} on {symbol}")
        
        # Create backtest configuration
        backtest_config = {
            'strategy_id': strategy_id,
            'strategy_name': strategy['name'],
            'symbol': symbol,
            'timeframe': timeframe,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'parameters': parameters
        }
        
        # Run backtest (mock implementation for now)
        # TODO: Implement actual backtesting logic
        mock_results = {
            'backtest_id': f"bt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'strategy_id': strategy_id,
            'strategy_name': strategy['name'],
            'configuration': backtest_config,
            'performance_metrics': {
                'total_return': 15.2,
                'annual_return': 12.8,
                'sharpe_ratio': 1.45,
                'max_drawdown': -8.3,
                'win_rate': 0.62,
                'total_trades': 45,
                'profit_factor': 1.8
            },
            'execution_time': 2.3,
            'completed_at': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'backtest_results': mock_results,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Backtest run failed: {e}")
        return jsonify({
            'error': 'Failed to run backtest',
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/convert-and-backtest', methods=['POST'])
def convert_and_backtest():
    """
    Convert Pine Script strategy and immediately run backtest
    
    Request Body:
        {
            "pine_code": "Pine Script code",
            "strategy_name": "Test Strategy",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 10000,
            "save_strategy": true
        }
    
    Returns:
        JSON response with conversion and backtest results
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({
                'error': 'pine_code is required in request body',
                'status': 'error'
            }), 400
        
        pine_code = data['pine_code']
        strategy_name = data.get('strategy_name', 'Converted Strategy')
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2023-12-31')
        initial_capital = data.get('initial_capital', 10000)
        save_strategy = data.get('save_strategy', False)
        
        # Get converter
        converter = get_converter()
        if not converter:
            return jsonify({
                'error': 'Working converter not available',
                'status': 'error'
            }), 503
        
        current_app.logger.info(f"Converting and backtesting strategy: {strategy_name}")
        
        # Convert Pine Script
        conversion_result = {
            'success': True,
            'python_code': f'# Converted from Pine Script\\n# Strategy: {strategy_name}\\n# TODO: Implement conversion logic',
            'parameters': {},
            'indicators_used': []
        }
        
        # Save strategy if requested
        strategy_id = None
        if save_strategy:
            try:
                from .db_helper import get_database_access
                da = get_database_access()
                strategy_id = da.save_strategy(
                    name=strategy_name,
                    pine_script=pine_code,
                    python_code=conversion_result.get('python_code', ''),
                    description='Converted and backtested strategy',
                    status='tested'
                )
                current_app.logger.info(f"Saved strategy with ID: {strategy_id}")
            except Exception as e:
                current_app.logger.warning(f"Failed to save strategy: {e}")
        
        # Mock backtest results
        backtest_results = {
            'backtest_id': f"bt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'strategy_id': strategy_id,
            'strategy_name': strategy_name,
            'symbol': symbol,
            'timeframe': timeframe,
            'performance_metrics': {
                'total_return': 8.7,
                'annual_return': 7.2,
                'sharpe_ratio': 1.12,
                'max_drawdown': -12.1,
                'win_rate': 0.58,
                'total_trades': 32,
                'profit_factor': 1.4
            },
            'execution_time': 3.8,
            'completed_at': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'strategy_name': strategy_name,
            'strategy_id': strategy_id,
            'conversion_result': conversion_result,
            'backtest_results': backtest_results,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Convert and backtest failed: {e}")
        return jsonify({
            'error': 'Failed to convert and backtest strategy',
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/results/<backtest_id>', methods=['GET'])
def get_backtest_results(backtest_id):
    """
    Get detailed results for a specific backtest
    
    Path Parameters:
        backtest_id: Backtest ID
    
    Returns:
        JSON response with detailed backtest results
    """
    try:
        # TODO: Implement actual result retrieval from database
        # For now, return mock detailed results
        
        detailed_results = {
            'backtest_id': backtest_id,
            'strategy_name': 'Sample Strategy',
            'symbol': 'BTCUSDT',
            'timeframe': '1h',
            'period': {
                'start_date': '2023-01-01',
                'end_date': '2023-12-31',
                'total_days': 365
            },
            'performance_metrics': {
                'returns': {
                    'total_return': 15.2,
                    'annual_return': 12.8,
                    'cumulative_return': 18.9,
                    'benchmark_return': 8.3
                },
                'risk_metrics': {
                    'sharpe_ratio': 1.45,
                    'sortino_ratio': 1.92,
                    'calmar_ratio': 1.54,
                    'max_drawdown': -8.3,
                    'volatility': 0.18
                },
                'trading_metrics': {
                    'total_trades': 45,
                    'winning_trades': 28,
                    'losing_trades': 17,
                    'win_rate': 0.62,
                    'profit_factor': 1.8,
                    'average_trade': 2.1
                }
            },
            'equity_curve': [
                {'date': '2023-01-01', 'value': 10000},
                {'date': '2023-06-01', 'value': 10850},
                {'date': '2023-12-31', 'value': 11520}
            ],
            'trades': [
                {
                    'entry_date': '2023-02-15',
                    'exit_date': '2023-02-20',
                    'side': 'long',
                    'entry_price': 23450,
                    'exit_price': 24100,
                    'quantity': 0.42,
                    'pnl': 273.0,
                    'pnl_percent': 2.77
                }
            ],
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'backtest_id': backtest_id,
            'detailed_results': detailed_results,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get backtest results failed: {e}")
        return jsonify({
            'error': 'Failed to get backtest results',
            'backtest_id': backtest_id,
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/history', methods=['GET'])
def get_backtest_history():
    """
    Get backtest history for user/strategy
    
    Query Parameters:
        strategy_id: Filter by strategy (optional)
        limit: Number of results (default: 50)
        offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with backtest history
    """
    try:
        strategy_id = request.args.get('strategy_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # TODO: Implement actual history retrieval from database
        # For now, return mock history
        
        mock_history = [
            {
                'backtest_id': 'bt_20231215_143022',
                'strategy_id': 17,
                'strategy_name': 'HYE Strategy v2',
                'symbol': 'BTCUSDT',
                'timeframe': '1h',
                'total_return': 15.2,
                'sharpe_ratio': 1.45,
                'max_drawdown': -8.3,
                'total_trades': 45,
                'status': 'completed',
                'created_at': '2023-12-15T14:30:22.000000'
            },
            {
                'backtest_id': 'bt_20231214_095511',
                'strategy_id': 16,
                'strategy_name': 'Test Strategy',
                'symbol': 'ETHUSDT',
                'timeframe': '4h',
                'total_return': 8.7,
                'sharpe_ratio': 1.12,
                'max_drawdown': -12.1,
                'total_trades': 32,
                'status': 'completed',
                'created_at': '2023-12-14T09:55:11.000000'
            }
        ]
        
        # Apply strategy filter if provided
        if strategy_id:
            mock_history = [h for h in mock_history if h['strategy_id'] == int(strategy_id)]
        
        # Apply pagination
        paginated_history = mock_history[offset:offset+limit]
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'backtest_history': paginated_history,
            'count': len(paginated_history),
            'total_available': len(mock_history),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < len(mock_history)
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get backtest history failed: {e}")
        return jsonify({
            'error': 'Failed to get backtest history',
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/pairs/available', methods=['GET'])
def get_available_pairs():
    """
    Get available trading pairs for backtesting
    
    Returns:
        JSON response with available trading pairs
    """
    try:
        # Popular crypto pairs for backtesting
        available_pairs = {
            'major_pairs': [
                {'symbol': 'BTCUSDT', 'name': 'Bitcoin/USDT', 'category': 'crypto'},
                {'symbol': 'ETHUSDT', 'name': 'Ethereum/USDT', 'category': 'crypto'},
                {'symbol': 'BNBUSDT', 'name': 'Binance Coin/USDT', 'category': 'crypto'},
                {'symbol': 'ADAUSDT', 'name': 'Cardano/USDT', 'category': 'crypto'},
                {'symbol': 'SOLUSDT', 'name': 'Solana/USDT', 'category': 'crypto'}
            ],
            'altcoin_pairs': [
                {'symbol': 'DOTUSDT', 'name': 'Polkadot/USDT', 'category': 'crypto'},
                {'symbol': 'AVAXUSDT', 'name': 'Avalanche/USDT', 'category': 'crypto'},
                {'symbol': 'MATICUSDT', 'name': 'Polygon/USDT', 'category': 'crypto'},
                {'symbol': 'LINKUSDT', 'name': 'Chainlink/USDT', 'category': 'crypto'},
                {'symbol': 'UNIUSDT', 'name': 'Uniswap/USDT', 'category': 'crypto'}
            ],
            'timeframes': ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
        }
        
        # Check if we have real market data
        try:
            from .db_helper import get_database_access
            da = get_database_access()
            symbols = da.get_available_symbols()
            if symbols:
                available_pairs['database_pairs'] = [
                    {'symbol': symbol, 'name': f'{symbol}', 'category': 'database'} 
                    for symbol in symbols[:10]  # Limit to first 10
                ]
        except Exception as e:
            current_app.logger.warning(f"Could not get database symbols: {e}")
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'available_pairs': available_pairs,
            'total_pairs': len(available_pairs.get('major_pairs', [])) + len(available_pairs.get('altcoin_pairs', [])),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get available pairs failed: {e}")
        return jsonify({
            'error': 'Failed to get available pairs',
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/progress/<task_id>', methods=['GET'])
def get_backtest_progress(task_id):
    """
    Get progress of a long-running backtest
    
    Path Parameters:
        task_id: Task ID returned from backtest request
    
    Returns:
        JSON response with task progress
    """
    try:
        # TODO: Implement actual task tracking in Sprint 2 middleware
        # For now, return placeholder response
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'task_id': task_id,
            'progress': {
                'status': 'not_implemented',
                'message': 'Backtest progress tracking will be implemented in Sprint 2 middleware',
                'percentage': 0
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Failed to get backtest progress: {e}")
        return jsonify({
            'error': 'Failed to get backtest progress',
            'task_id': task_id,
            'message': str(e),
            'status': 'error'
        }), 500


@backtest_bp.route('/<backtest_id>', methods=['DELETE'])
def cancel_backtest(backtest_id):
    """
    Cancel a running backtest
    
    Path Parameters:
        backtest_id: Backtest ID to cancel
    
    Returns:
        JSON response confirming cancellation
    """
    try:
        # TODO: Implement actual backtest cancellation
        # For now, return success response
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'backtest_id': backtest_id,
            'message': 'Backtest cancellation not yet implemented',
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Failed to cancel backtest: {e}")
        return jsonify({
            'error': 'Failed to cancel backtest',
            'backtest_id': backtest_id,
            'message': str(e),
            'status': 'error'
        }), 500


# Route registration helper
def register_backtest_routes(app):
    """Register backtest routes with the app"""
    app.register_blueprint(backtest_bp)
    app.logger.info("Backtest routes registered")


if __name__ == '__main__':
    # For testing individual blueprint
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(backtest_bp)
    
    print("Backtest routes available:")
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/v1/backtests'):
            print(f"  {rule.methods} {rule.rule}")


"""
SPRINT 2 DEVELOPMENT NOTES:

CONSOLIDATION CHECKLIST:
[ ] Review original backtest_routes.py for missing functionality
[ ] Review original real_backtest_routes.py for missing functionality
[ ] Implement actual backtesting engine integration
[ ] Add backtest result persistence to database
[ ] Add proper input validation (Sprint 2 middleware)
[ ] Add authentication/authorization (Sprint 2 middleware)  
[ ] Update frontend components to use new endpoints
[ ] Add comprehensive error handling
[ ] Add task queue for long-running backtests
[ ] Add OpenAPI documentation (Sprint 3)

TESTING CHECKLIST:
[ ] Unit tests for each endpoint
[ ] Integration tests with backtest engine
[ ] Performance tests for large backtests
[ ] Error handling tests
[ ] Task progress tracking tests
[ ] Result persistence tests

MIGRATION NOTES:
- This blueprint replaces backtest_routes.py and real_backtest_routes.py
- All endpoints now under /api/v1/backtests/ prefix
- Standardized response format with timestamp, epic, status
- Uses unified database access layer
- Error responses include error type and message
- Mock implementations for complex backtesting logic (to be implemented)

FRONTEND UPDATE REQUIREMENTS:
- Update all backtest API calls to use /api/v1/backtests/
- Handle new response format (with timestamp, epic, status)
- Update error handling for new error format
- Test backtest workflows with new endpoints
"""