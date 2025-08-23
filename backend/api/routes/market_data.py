"""
Market Data Routes
Epic 7 Sprint 1 - Foundation & Consolidation

Consolidates market data endpoints from:
- market_routes.py
- futures_routes.py  
- enhanced_data_routes.py

TODO Sprint 1 Tasks:
[ ] Migrate market overview endpoint
[ ] Migrate OHLC data endpoints
[ ] Migrate futures pairs endpoints
[ ] Migrate market tickers endpoints
[ ] Add standardized error handling
[ ] Add input validation
[ ] Add response formatting
[ ] Update frontend API calls
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import pandas as pd

# Create blueprint
market_bp = Blueprint('market', __name__, url_prefix='/api/v1/market')


@market_bp.route('/')
def market_info():
    """
    Market data API information
    
    Returns:
        JSON response with available market endpoints
    """
    return jsonify({
        'api': 'Market Data API',
        'version': '1.0.0',
        'epic': 'Epic 7 Sprint 1 - Foundation & Consolidation',
        'endpoints': {
            'overview': '/api/v1/market/overview',
            'symbols': '/api/v1/market/symbols',
            'tickers': '/api/v1/market/tickers',
            'ticker': '/api/v1/market/ticker/<symbol>',
            'ohlc': '/api/v1/market/ohlc/<symbol>',
            'futures_pairs': '/api/v1/market/futures/pairs',
            'futures_search': '/api/v1/market/futures/search',
            'status': '/api/v1/market/status'
        },
        'status': 'Sprint 1 - Implementation in progress',
        'consolidates': [
            'market_routes.py',
            'futures_routes.py', 
            'enhanced_data_routes.py'
        ]
    })


@market_bp.route('/overview')
def market_overview():
    """
    Get market overview with top gainers, losers, volume
    
    TODO Sprint 1: Consolidate from market_routes.py
    
    Returns:
        JSON response with market overview data
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Get market overview from service
        overview = market_service.get_market_overview()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'market_overview': overview,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Market overview failed: {e}")
        return jsonify({
            'error': 'Failed to fetch market overview',
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/symbols')
def get_symbols():
    """
    Get list of available trading symbols
    
    TODO Sprint 1: Consolidate from enhanced_data_routes.py
    
    Returns:
        JSON response with available symbols
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Get top crypto pairs as symbols
        limit = int(request.args.get('limit', 50))
        symbols = market_service.get_top_crypto_pairs(limit)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'symbols': symbols,
            'count': len(symbols),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get symbols failed: {e}")
        return jsonify({
            'error': 'Failed to fetch symbols',
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/tickers')
def get_tickers():
    """
    Get real-time market tickers
    
    TODO Sprint 1: Consolidate from market_routes.py
    
    Query Parameters:
        symbols: Comma-separated list of symbols (optional)
    
    Returns:
        JSON response with market ticker data
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Parse query parameters
        symbols_param = request.args.get('symbols')
        if symbols_param:
            symbols = [s.strip() for s in symbols_param.split(',')]
            # Format symbols properly
            formatted_symbols = []
            for symbol in symbols:
                if '/USDT' not in symbol.upper():
                    formatted_symbols.append(f"{symbol.upper()}/USDT")
                else:
                    formatted_symbols.append(symbol.upper())
            
            tickers = market_service.fetch_multiple_tickers(formatted_symbols)
        else:
            # Get default top pairs
            top_pairs = market_service.get_top_crypto_pairs(20)
            tickers = market_service.fetch_multiple_tickers(top_pairs)
        
        # Format tickers for response
        ticker_data = []
        for symbol, ticker in tickers.items():
            ticker_data.append({
                'symbol': ticker.symbol,
                'price': ticker.price,
                'change_24h': ticker.change_24h,
                'change_percent_24h': ticker.change_percent_24h,
                'volume_24h': ticker.volume_24h,
                'high_24h': ticker.high_24h,
                'low_24h': ticker.low_24h,
                'timestamp': ticker.timestamp.isoformat()
            })
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'tickers': ticker_data,
            'count': len(ticker_data),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get tickers failed: {e}")
        return jsonify({
            'error': 'Failed to fetch tickers',
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/ohlc/<symbol>')
def get_ohlc_data(symbol):
    """
    Get OHLC data for specific symbol
    
    TODO Sprint 1: Consolidate from enhanced_data_routes.py
    
    Path Parameters:
        symbol: Trading pair symbol (e.g., BTCUSDT)
    
    Query Parameters:
        timeframe: Time interval (default: 1h)
        limit: Number of records (default: 100)
        start_date: Start date (ISO format, optional)
        end_date: End date (ISO format, optional)
    
    Returns:
        JSON response with OHLC data
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 100))
        days = request.args.get('days', 30, type=int)
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
        if timeframe not in valid_timeframes:
            return jsonify({
                'error': f'Invalid timeframe. Valid options: {valid_timeframes}',
                'symbol': symbol,
                'status': 'error'
            }), 400
        
        # Format symbol properly
        if '/USDT' not in symbol.upper():
            symbol = f"{symbol.upper()}/USDT"
        else:
            symbol = symbol.upper()
        
        # Fetch historical data
        historical_data = market_service.fetch_historical_data(symbol, timeframe, days)
        
        # Convert to API response format
        data = []
        for candle in historical_data[:limit]:  # Apply limit
            data.append({
                'timestamp': candle.timestamp.isoformat(),
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'volume': candle.volume
            })
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'symbol': symbol,
            'timeframe': timeframe,
            'data': data,
            'count': len(data),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get OHLC data failed for {symbol}: {e}")
        return jsonify({
            'error': 'Failed to fetch OHLC data',
            'symbol': symbol,
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/futures/pairs')
def get_futures_pairs():
    """
    Get Binance Futures trading pairs
    
    TODO Sprint 1: Consolidate from futures_routes.py
    
    Returns:
        JSON response with futures trading pairs
    """
    try:
        # Import futures provider from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from research.data.providers.binance_futures_provider import BinanceFuturesProvider
        
        # Initialize futures provider
        futures_provider = BinanceFuturesProvider()
        
        # Parse query parameters
        limit = request.args.get('limit', type=int)
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'volume')
        force_refresh = request.args.get('refresh', '').lower() == 'true'
        
        # Get pairs from provider
        pairs = futures_provider.get_usdt_perpetual_pairs(force_refresh=force_refresh)
        
        if not pairs:
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 Sprint 1',
                'error': 'Failed to fetch futures pairs',
                'futures_pairs': [],
                'count': 0,
                'status': 'error'
            }), 500
        
        # Apply search filter
        if search_query:
            pairs = futures_provider.search_pairs(search_query)
        
        # Apply sorting
        if sort_by == 'price':
            pairs.sort(key=lambda x: x.get('price', 0), reverse=True)
        elif sort_by == 'change':
            pairs.sort(key=lambda x: abs(x.get('change24h', 0)), reverse=True)
        # Default is volume (already sorted in provider)
        
        # Apply limit
        if limit and limit > 0:
            pairs = pairs[:limit]
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'futures_pairs': pairs,
            'count': len(pairs),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get futures pairs failed: {e}")
        return jsonify({
            'error': 'Failed to fetch futures pairs',
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/ticker/<symbol>')
def get_ticker(symbol):
    """
    Get live ticker data for specific symbol
    
    Path Parameters:
        symbol: Trading pair symbol (e.g., BTC, BTCUSDT)
    
    Returns:
        JSON response with ticker data
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Format symbol properly
        if '/USDT' not in symbol.upper():
            formatted_symbol = f"{symbol.upper()}/USDT"
        else:
            formatted_symbol = symbol.upper()
        
        ticker = market_service.fetch_live_ticker(formatted_symbol)
        
        if ticker:
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 Sprint 1',
                'ticker': {
                    'symbol': ticker.symbol,
                    'price': ticker.price,
                    'change_24h': ticker.change_24h,
                    'change_percent_24h': ticker.change_percent_24h,
                    'volume_24h': ticker.volume_24h,
                    'high_24h': ticker.high_24h,
                    'low_24h': ticker.low_24h,
                    'timestamp': ticker.timestamp.isoformat()
                },
                'status': 'success'
            })
        else:
            return jsonify({
                'error': f'Ticker data not available for {symbol}',
                'symbol': symbol,
                'status': 'error'
            }), 404
    
    except Exception as e:
        current_app.logger.error(f"Get ticker {symbol} failed: {e}")
        return jsonify({
            'error': 'Failed to fetch ticker',
            'symbol': symbol,
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/futures/search')
def search_futures():
    """
    Search futures symbols by query
    
    Query Parameters:
        q: Search query string
        
    Returns:
        JSON response with matching futures symbols
    """
    try:
        # Import futures provider from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from research.data.providers.binance_futures_provider import BinanceFuturesProvider
        
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'error': 'Search query is required',
                'status': 'error'
            }), 400
        
        futures_provider = BinanceFuturesProvider()
        pairs = futures_provider.search_pairs(query)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'futures_search': pairs,
            'count': len(pairs),
            'query': query,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Futures search failed: {e}")
        return jsonify({
            'error': 'Failed to search futures',
            'message': str(e),
            'status': 'error'
        }), 500


@market_bp.route('/status')
def get_market_status():
    """
    Get market data service status and connectivity
    
    Returns:
        JSON response with service status
    """
    try:
        # Import market data service from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from api.market_data_service import market_service
        
        # Test connection by fetching BTC ticker
        btc_ticker = market_service.fetch_live_ticker('BTC/USDT')
        
        status = {
            'service_status': 'operational' if btc_ticker else 'degraded',
            'binance_connection': 'connected' if btc_ticker else 'disconnected',
            'cache_size': len(market_service.price_cache),
            'last_update': btc_ticker.timestamp.isoformat() if btc_ticker else None,
            'supported_timeframes': ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w'],
            'rate_limit_status': 'normal'
        }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'market_status': status,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Market status check failed: {e}")
        return jsonify({
            'error': 'Failed to check market status',
            'message': str(e),
            'status': 'error'
        }), 500


# Route registration helper
def register_market_routes(app):
    """Register market data routes with the app"""
    app.register_blueprint(market_bp)
    app.logger.info("Market data routes registered")


if __name__ == '__main__':
    # For testing individual blueprint
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(market_bp)
    
    print("Market data routes available:")
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/v1/market'):
            print(f"  {rule.methods} {rule.rule}")

"""
SPRINT 1 DEVELOPMENT NOTES:

CONSOLIDATION CHECKLIST:
[ ] Review original market_routes.py for missing functionality  
[ ] Review original futures_routes.py for missing functionality
[ ] Review original enhanced_data_routes.py for missing functionality
[ ] Add proper input validation (Sprint 2 middleware)
[ ] Add rate limiting (Sprint 2 middleware)
[ ] Add authentication if needed (Sprint 2 middleware)
[ ] Update frontend components to use new endpoints
[ ] Add comprehensive error handling
[ ] Add response caching if appropriate
[ ] Add OpenAPI documentation (Sprint 3)

TESTING CHECKLIST:
[ ] Unit tests for each endpoint
[ ] Integration tests with database
[ ] Performance tests for OHLC data endpoints
[ ] Error handling tests
[ ] Input validation tests

MIGRATION NOTES:
- This blueprint replaces market_routes.py, futures_routes.py, enhanced_data_routes.py
- All endpoints now under /api/v1/market/ prefix
- Standardized response format with timestamp, epic, status
- Uses unified database access layer
- Error responses include error type and message
"""