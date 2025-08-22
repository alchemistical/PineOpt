"""
Market Data API Routes
Provides endpoints for live and historical cryptocurrency data
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging
from .market_data_service import market_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
market_bp = Blueprint('market', __name__)

@market_bp.route('/overview', methods=['GET'])
def get_market_overview():
    """Get market overview with top cryptocurrencies"""
    try:
        overview = market_service.get_market_overview()
        
        return jsonify({
            'success': True,
            'data': overview,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in market overview endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/ticker/<symbol>', methods=['GET'])
def get_ticker(symbol):
    """Get live ticker data for a specific symbol"""
    try:
        # Format symbol properly (add /USDT if not present)
        if '/USDT' not in symbol.upper():
            symbol = f"{symbol.upper()}/USDT"
        
        ticker = market_service.fetch_live_ticker(symbol)
        
        if ticker:
            return jsonify({
                'success': True,
                'data': {
                    'symbol': ticker.symbol,
                    'price': ticker.price,
                    'change_24h': ticker.change_24h,
                    'change_percent_24h': ticker.change_percent_24h,
                    'volume_24h': ticker.volume_24h,
                    'high_24h': ticker.high_24h,
                    'low_24h': ticker.low_24h,
                    'timestamp': ticker.timestamp.isoformat()
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ticker data not available for {symbol}',
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Error in ticker endpoint for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/tickers', methods=['POST'])
def get_multiple_tickers():
    """Get ticker data for multiple symbols"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': 'No symbols provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Format symbols properly
        formatted_symbols = []
        for symbol in symbols:
            if '/USDT' not in symbol.upper():
                formatted_symbols.append(f"{symbol.upper()}/USDT")
            else:
                formatted_symbols.append(symbol.upper())
        
        tickers = market_service.fetch_multiple_tickers(formatted_symbols)
        
        ticker_data = {}
        for symbol, ticker in tickers.items():
            ticker_data[symbol] = {
                'symbol': ticker.symbol,
                'price': ticker.price,
                'change_24h': ticker.change_24h,
                'change_percent_24h': ticker.change_percent_24h,
                'volume_24h': ticker.volume_24h,
                'high_24h': ticker.high_24h,
                'low_24h': ticker.low_24h,
                'timestamp': ticker.timestamp.isoformat()
            }
        
        return jsonify({
            'success': True,
            'data': ticker_data,
            'count': len(ticker_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in multiple tickers endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/historical/<symbol>', methods=['GET'])
def get_historical_data(symbol):
    """Get historical OHLCV data for a symbol"""
    try:
        # Format symbol properly
        if '/USDT' not in symbol.upper():
            symbol = f"{symbol.upper()}/USDT"
        
        # Get query parameters
        timeframe = request.args.get('timeframe', '1h')
        days = int(request.args.get('days', 30))
        
        # Validate parameters
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
        if timeframe not in valid_timeframes:
            return jsonify({
                'success': False,
                'error': f'Invalid timeframe. Valid options: {valid_timeframes}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Days must be between 1 and 365',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        historical_data = market_service.fetch_historical_data(symbol, timeframe, days)
        
        if historical_data:
            data = []
            for candle in historical_data:
                data.append({
                    'timestamp': candle.timestamp.isoformat(),
                    'open': candle.open,
                    'high': candle.high,
                    'low': candle.low,
                    'close': candle.close,
                    'volume': candle.volume
                })
            
            return jsonify({
                'success': True,
                'data': {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'period_days': days,
                    'candles': data,
                    'count': len(data)
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Historical data not available for {symbol}',
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Error in historical data endpoint for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/top-pairs', methods=['GET'])
def get_top_pairs():
    """Get top cryptocurrency trading pairs by volume"""
    try:
        limit = int(request.args.get('limit', 20))
        
        if limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': 'Limit must be between 1 and 100',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        top_pairs = market_service.get_top_crypto_pairs(limit)
        
        return jsonify({
            'success': True,
            'data': {
                'pairs': top_pairs,
                'count': len(top_pairs)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in top pairs endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/status', methods=['GET'])
def get_market_status():
    """Get market data service status"""
    try:
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
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in market status endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@market_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'market_data',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in health check endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500