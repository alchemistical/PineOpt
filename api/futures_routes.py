"""
Binance Futures API Routes
Handles perpetual futures market data endpoints
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.data.providers.binance_futures_provider import BinanceFuturesProvider

logger = logging.getLogger(__name__)

# Create Blueprint
futures_bp = Blueprint('futures', __name__, url_prefix='/api/futures')

# Initialize provider
futures_provider = BinanceFuturesProvider()

@futures_bp.route('/pairs', methods=['GET'])
def get_futures_pairs():
    """
    Get all USDT perpetual futures pairs
    
    Query parameters:
    - limit: Number of pairs to return (default: all)
    - search: Search query for filtering pairs
    - sort: Sort by 'volume' (default), 'price', 'change'
    - refresh: Force refresh cache ('true'/'false')
    """
    try:
        # Parse query parameters
        limit = request.args.get('limit', type=int)
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'volume')
        force_refresh = request.args.get('refresh', '').lower() == 'true'
        
        logger.info(f"Fetching futures pairs - limit: {limit}, search: '{search_query}', sort: {sort_by}")
        
        # Get pairs from provider
        pairs = futures_provider.get_usdt_perpetual_pairs(force_refresh=force_refresh)
        
        if not pairs:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch futures pairs',
                'data': []
            }), 500
        
        # Apply search filter
        if search_query:
            pairs = futures_provider.search_pairs(search_query)
        
        # Apply sorting
        if sort_by == 'price':
            pairs.sort(key=lambda x: x['price'], reverse=True)
        elif sort_by == 'change':
            pairs.sort(key=lambda x: abs(x['change24h']), reverse=True)
        # Default is volume (already sorted in provider)
        
        # Apply limit
        if limit and limit > 0:
            pairs = pairs[:limit]
        
        return jsonify({
            'success': True,
            'data': pairs,
            'count': len(pairs),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching futures pairs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@futures_bp.route('/pairs/top', methods=['GET'])
def get_top_pairs():
    """Get top futures pairs by volume"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        pairs = futures_provider.get_top_pairs_by_volume(limit=limit)
        
        return jsonify({
            'success': True,
            'data': pairs,
            'count': len(pairs)
        })
        
    except Exception as e:
        logger.error(f"Error fetching top pairs: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@futures_bp.route('/klines/<symbol>', methods=['GET'])
def get_klines(symbol):
    """
    Get historical kline data for a futures symbol
    
    Query parameters:
    - interval: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, etc.)
    - limit: Number of candles (max 1500, default 500)
    - start_time: Start time (ISO format or timestamp)
    - end_time: End time (ISO format or timestamp)
    """
    try:
        # Parse parameters
        interval = request.args.get('interval', '1h')
        limit = min(request.args.get('limit', 500, type=int), 1500)
        
        start_time = None
        end_time = None
        
        # Parse start_time
        start_param = request.args.get('start_time')
        if start_param:
            try:
                start_time = datetime.fromisoformat(start_param.replace('Z', '+00:00'))
            except:
                try:
                    start_time = datetime.fromtimestamp(float(start_param))
                except:
                    pass
        
        # Parse end_time
        end_param = request.args.get('end_time')
        if end_param:
            try:
                end_time = datetime.fromisoformat(end_param.replace('Z', '+00:00'))
            except:
                try:
                    end_time = datetime.fromtimestamp(float(end_param))
                except:
                    pass
        
        logger.info(f"Fetching klines for {symbol} - {interval}, limit: {limit}")
        
        # Get data from provider
        df = futures_provider.get_historical_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for {symbol}',
                'data': []
            }), 404
        
        # Convert DataFrame to list of dictionaries
        data = []
        for _, row in df.iterrows():
            data.append({
                'time': int(row['timestamp']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if 'volume' in row else 0
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'symbol': symbol,
            'interval': interval,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching klines for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@futures_bp.route('/symbol/<symbol>', methods=['GET'])
def get_symbol_info(symbol):
    """Get detailed information about a specific futures symbol"""
    try:
        pairs = futures_provider.get_usdt_perpetual_pairs()
        
        # Find the symbol
        symbol_info = None
        for pair in pairs:
            if pair['symbol'].upper() == symbol.upper():
                symbol_info = pair
                break
        
        if not symbol_info:
            return jsonify({
                'success': False,
                'error': f'Symbol {symbol} not found',
                'data': None
            }), 404
        
        return jsonify({
            'success': True,
            'data': symbol_info
        })
        
    except Exception as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': None
        }), 500

@futures_bp.route('/search', methods=['GET'])
def search_symbols():
    """Search futures symbols by query"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required',
                'data': []
            }), 400
        
        pairs = futures_provider.search_pairs(query)
        
        return jsonify({
            'success': True,
            'data': pairs,
            'count': len(pairs),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@futures_bp.route('/intervals', methods=['GET'])
def get_available_intervals():
    """Get available timeframe intervals"""
    intervals = [
        {'value': '1m', 'label': '1 Minute', 'seconds': 60},
        {'value': '5m', 'label': '5 Minutes', 'seconds': 300},
        {'value': '15m', 'label': '15 Minutes', 'seconds': 900},
        {'value': '30m', 'label': '30 Minutes', 'seconds': 1800},
        {'value': '1h', 'label': '1 Hour', 'seconds': 3600},
        {'value': '2h', 'label': '2 Hours', 'seconds': 7200},
        {'value': '4h', 'label': '4 Hours', 'seconds': 14400},
        {'value': '6h', 'label': '6 Hours', 'seconds': 21600},
        {'value': '8h', 'label': '8 Hours', 'seconds': 28800},
        {'value': '12h', 'label': '12 Hours', 'seconds': 43200},
        {'value': '1d', 'label': '1 Day', 'seconds': 86400},
        {'value': '3d', 'label': '3 Days', 'seconds': 259200},
        {'value': '1w', 'label': '1 Week', 'seconds': 604800},
    ]
    
    return jsonify({
        'success': True,
        'data': intervals
    })

@futures_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test API connectivity
        pairs = futures_provider.get_usdt_perpetual_pairs()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'pairs_count': len(pairs) if pairs else 0,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500