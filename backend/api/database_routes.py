"""
Flask API routes for database operations
Extends the existing API with database-backed endpoints
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os
import logging
from sqlalchemy import text

# Add database module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.data_access import crypto_data, strategy_data, backtest_data, activity_data
from database.models import db_manager

# Create blueprint
db_api = Blueprint('database_api', __name__)
logger = logging.getLogger(__name__)

# =======================
# CRYPTO DATA ENDPOINTS
# =======================

@db_api.route('/api/db/crypto/sources', methods=['GET'])
def get_crypto_sources():
    """Get all available crypto data sources."""
    try:
        sources = crypto_data.get_available_data_sources()
        return jsonify({
            'success': True,
            'sources': sources,
            'count': len(sources)
        })
    except Exception as e:
        logger.error(f"Error getting crypto sources: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/crypto/ohlc', methods=['GET'])
def get_crypto_ohlc():
    """Get OHLC data from database."""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        exchange = request.args.get('exchange', 'BINANCE')
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 1000))
        
        # Get data as DataFrame
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            limit=limit
        )
        
        if df.empty:
            return jsonify({
                'success': True,
                'ohlc': [],
                'count': 0,
                'message': 'No data found for the specified parameters'
            })
        
        # Convert to list of dictionaries
        ohlc_data = []
        for index, row in df.iterrows():
            ohlc_data.append({
                'time': index.isoformat(),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'exchange': exchange,
            'timeframe': timeframe,
            'ohlc': ohlc_data,
            'count': len(ohlc_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting OHLC data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/crypto/store', methods=['POST'])
def store_crypto_data():
    """Store OHLC data in database."""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol')
        exchange = data.get('exchange')
        timeframe = data.get('timeframe')
        ohlc_data = data.get('ohlc_data', [])
        source_type = data.get('source_type', 'api')
        
        if not all([symbol, exchange, timeframe, ohlc_data]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: symbol, exchange, timeframe, ohlc_data'
            }), 400
        
        # Store data
        records_inserted = crypto_data.store_ohlc_data(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            ohlc_data=ohlc_data,
            source_type=source_type
        )
        
        return jsonify({
            'success': True,
            'records_inserted': records_inserted,
            'message': f'Stored {records_inserted} OHLC records'
        })
        
    except Exception as e:
        logger.error(f"Error storing crypto data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =======================
# STRATEGY ENDPOINTS
# =======================

@db_api.route('/api/db/strategies', methods=['GET'])
def get_strategies():
    """Get all strategies."""
    try:
        status = request.args.get('status')
        strategies = strategy_data.get_strategies(status=status)
        
        return jsonify({
            'success': True,
            'strategies': strategies,
            'count': len(strategies)
        })
        
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy_details(strategy_id):
    """Get detailed strategy information."""
    try:
        strategy = strategy_data.get_strategy_with_parameters(strategy_id)
        
        if not strategy:
            return jsonify({
                'success': False,
                'error': 'Strategy not found'
            }), 404
        
        return jsonify({
            'success': True,
            'strategy': strategy
        })
        
    except Exception as e:
        logger.error(f"Error getting strategy details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/strategies', methods=['POST'])
def create_strategy():
    """Create a new strategy."""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        pine_script_content = data.get('pine_script_content')
        category = data.get('category', 'Custom')
        
        if not all([name, pine_script_content]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: name, pine_script_content'
            }), 400
        
        # Create strategy
        strategy_id = strategy_data.create_strategy(
            name=name,
            description=description,
            pine_script_content=pine_script_content,
            category=category
        )
        
        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'message': f'Created strategy: {name}'
        })
        
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/strategies/<int:strategy_id>/parameters', methods=['POST'])
def add_strategy_parameter(strategy_id):
    """Add parameter to strategy."""
    try:
        data = request.get_json()
        
        param_name = data.get('param_name')
        param_type = data.get('param_type')
        constraints = data.get('constraints', {})
        default_value = data.get('default_value')
        
        if not all([param_name, param_type, default_value is not None]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: param_name, param_type, default_value'
            }), 400
        
        # Add parameter
        param_id = strategy_data.add_strategy_parameter(
            strategy_id=strategy_id,
            param_name=param_name,
            param_type=param_type,
            constraints=constraints,
            default_value=default_value
        )
        
        return jsonify({
            'success': True,
            'parameter_id': param_id,
            'message': f'Added parameter: {param_name}'
        })
        
    except Exception as e:
        logger.error(f"Error adding parameter: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =======================
# BACKTESTING ENDPOINTS
# =======================

@db_api.route('/api/db/backtests', methods=['GET'])
def get_backtest_results():
    """Get backtest results."""
    try:
        strategy_id = request.args.get('strategy_id', type=int)
        limit = int(request.args.get('limit', 50))
        
        results = backtest_data.get_backtest_results(
            strategy_id=strategy_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error getting backtest results: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/backtests/config', methods=['POST'])
def create_backtest_config():
    """Create backtest configuration."""
    try:
        data = request.get_json()
        
        name = data.get('name')
        strategy_id = data.get('strategy_id')
        symbol = data.get('symbol')
        exchange = data.get('exchange')
        timeframe = data.get('timeframe')
        start_timestamp = data.get('start_timestamp')
        end_timestamp = data.get('end_timestamp')
        
        if not all([name, strategy_id, symbol, exchange, timeframe, start_timestamp, end_timestamp]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Create config
        config_id = backtest_data.create_backtest_config(
            name=name,
            strategy_id=strategy_id,
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            initial_capital=data.get('initial_capital', 10000),
            commission_rate=data.get('commission_rate', 0.001)
        )
        
        return jsonify({
            'success': True,
            'config_id': config_id,
            'message': f'Created backtest config: {name}'
        })
        
    except Exception as e:
        logger.error(f"Error creating backtest config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =======================
# SYSTEM MONITORING ENDPOINTS
# =======================

@db_api.route('/api/db/activity', methods=['GET'])
def get_recent_activity():
    """Get recent system activity."""
    try:
        limit = int(request.args.get('limit', 50))
        activities = activity_data.get_recent_activity(limit=limit)
        
        return jsonify({
            'success': True,
            'activities': activities,
            'count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics."""
    try:
        stats = activity_data.get_system_stats()
        db_stats = db_manager.get_db_stats()
        
        # Combine stats
        all_stats = {**stats, **db_stats}
        
        return jsonify({
            'success': True,
            'stats': all_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@db_api.route('/api/db/health', methods=['GET'])
def database_health_check():
    """Database health check endpoint."""
    try:
        # Test database connection
        session = db_manager.get_session()
        try:
            # Simple query to test connection
            result = session.execute(text("SELECT 1")).fetchone()
            session.close()
            
            if result:
                # Get basic stats
                stats = db_manager.get_db_stats()
                
                return jsonify({
                    'success': True,
                    'status': 'healthy',
                    'database_stats': stats,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'status': 'unhealthy',
                    'error': 'Database query failed'
                }), 500
                
        except Exception as e:
            session.close()
            raise e
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# =======================
# ERROR HANDLERS
# =======================

@db_api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@db_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500