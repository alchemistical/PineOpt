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
            'ohlc': '/api/v1/market/ohlc/<symbol>',
            'futures': '/api/v1/market/futures/pairs'
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
        # TODO: Implement actual market overview logic
        # This is a placeholder for Sprint 1 development
        
        # Import database access
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Get market tickers
        tickers = da.get_market_tickers()
        
        # Sort by various criteria
        gainers = sorted(tickers, key=lambda x: x.get('change_percent_24h', 0), reverse=True)[:10]
        losers = sorted(tickers, key=lambda x: x.get('change_percent_24h', 0))[:10]
        volume_leaders = sorted(tickers, key=lambda x: x.get('volume_24h', 0), reverse=True)[:10]
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'market_overview': {
                'total_pairs': len(tickers),
                'gainers': gainers,
                'losers': losers,
                'volume_leaders': volume_leaders
            },
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        symbols = da.get_available_symbols()
        
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Parse query parameters
        symbols_param = request.args.get('symbols')
        symbols = symbols_param.split(',') if symbols_param else None
        
        tickers = da.get_market_tickers(symbols)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'tickers': tickers,
            'count': len(tickers),
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 100))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get market data
        df = da.get_market_data(
            symbol=symbol.upper(),
            timeframe=timeframe,
            limit=limit,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        # Convert to JSON-serializable format
        if df.empty:
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 Sprint 1',
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'data': [],
                'count': 0,
                'message': 'No data found for specified parameters',
                'status': 'success'
            })
        
        # Convert DataFrame to records
        records = df.to_dict('records')
        
        # Convert timestamps to ISO format
        for record in records:
            if 'timestamp_utc' in record:
                record['timestamp_utc'] = record['timestamp_utc'].isoformat()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'data': records,
            'count': len(records),
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Get available symbols (futures pairs)
        symbols = da.get_available_symbols()
        
        # Format as futures pairs (add USDT suffix if needed)
        futures_pairs = []
        for symbol in symbols:
            if symbol.endswith('USDT'):
                futures_pairs.append({
                    'symbol': symbol,
                    'baseAsset': symbol[:-4],  # Remove USDT
                    'quoteAsset': 'USDT',
                    'status': 'TRADING'  # Placeholder
                })
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'futures_pairs': futures_pairs,
            'count': len(futures_pairs),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get futures pairs failed: {e}")
        return jsonify({
            'error': 'Failed to fetch futures pairs',
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