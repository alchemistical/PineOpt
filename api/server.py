#!/usr/bin/env python3
"""Flask API server for Pine2Py conversion and strategy management."""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pine2py.codegen.emit import convert_simple_rsi_strategy, PythonCodeGenerator
from pine2py.parser.parser import PineParser

# Binance crypto data provider (real live data)
try:
    from research.data.providers.binance_provider import get_binance_provider
    BINANCE_AVAILABLE = True
except ImportError as e:
    BINANCE_AVAILABLE = False
    print(f"WARNING: Binance provider not available: {e}")

# Tardis.dev crypto data provider (fallback)
try:
    from research.data.providers.tardis_provider import get_tardis_provider
    TARDIS_AVAILABLE = True
except ImportError as e:
    TARDIS_AVAILABLE = False
    print(f"WARNING: Tardis provider not available: {e}")

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Import and register database routes
try:
    from database_routes import db_api
    app.register_blueprint(db_api)
    logger.info("✅ Database routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import database routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering database routes: {e}")

# Import and register enhanced data routes
try:
    from enhanced_data_routes import enhanced_data_api
    app.register_blueprint(enhanced_data_api)
    logger.info("✅ Enhanced data routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import enhanced data routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering enhanced data routes: {e}")

# Import and register futures routes
try:
    from futures_routes import futures_bp
    app.register_blueprint(futures_bp)
    logger.info("✅ Futures routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import futures routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering futures routes: {e}")

# Import and register strategy routes (Epic 5)
try:
    from strategy_routes import strategy_bp
    app.register_blueprint(strategy_bp)
    logger.info("✅ Strategy routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import strategy routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering strategy routes: {e}")

# Database setup
DATABASE_PATH = Path(__file__).parent / "strategies.db"

def init_database():
    """Initialize SQLite database for strategies."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            pine_source TEXT NOT NULL,
            python_code TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Pine2Py API Server Running"})

@app.route('/api/convert-pine', methods=['POST'])
def convert_pine():
    """Convert Pine Script to Python strategy."""
    try:
        data = request.get_json()
        
        pine_code = data.get('pine_code', '')
        strategy_name = data.get('strategy_name', 'Unnamed Strategy')
        description = data.get('description', '')
        
        if not pine_code.strip():
            return jsonify({"error": "Pine code is required"}), 400
        
        # Create code generator
        generator = PythonCodeGenerator()
        
        # For MVP, detect RSI pattern and use simple conversion
        if 'ta.rsi' in pine_code.lower() or 'rsi' in pine_code.lower():
            # Extract RSI parameters if possible
            parameters = {
                'rsi_length': {'default': 14, 'min': 1, 'max': 100, 'title': 'RSI Length'},
                'rsi_overbought': {'default': 70.0, 'min': 50, 'max': 100, 'title': 'RSI Overbought'},
                'rsi_oversold': {'default': 30.0, 'min': 0, 'max': 50, 'title': 'RSI Oversold'}
            }
            
            python_code = generator.generate_strategy_module(
                strategy_name=strategy_name,
                parameters=parameters,
                pine_logic=pine_code
            )
        else:
            # Fallback to basic template
            python_code = f'''# Generated from Pine Script
# Strategy: {strategy_name}
# {description}

import pandas as pd
import numpy as np
from pine2py.runtime import ta, nz, change, crossover, crossunder
from shared.types.strategy import StrategySignals, StrategyParameter, StrategyMetadata

STRATEGY_NAME = "{strategy_name}"

def build_signals(df: pd.DataFrame, **params) -> StrategySignals:
    """Build trading signals from OHLC data."""
    # TODO: Implement strategy logic from Pine Script
    # Original Pine Script:
    # {pine_code}
    
    # Initialize empty signals for now
    entries = pd.Series(False, index=df.index)
    exits = pd.Series(False, index=df.index)
    
    return StrategySignals(entries=entries, exits=exits)

METADATA = StrategyMetadata(
    name="{strategy_name}",
    description="{description}"
)
'''
        
        # Validate generated Python code
        try:
            compile(python_code, '<generated>', 'exec')
        except SyntaxError as e:
            return jsonify({"error": f"Generated Python code has syntax error: {e}"}), 500
        
        return jsonify({
            "success": True,
            "strategy_name": strategy_name,
            "python_code": python_code,
            "conversion_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies', methods=['POST'])
def save_strategy():
    """Save converted strategy to database."""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        pine_source = data.get('pine_source')
        python_code = data.get('python_code')
        metadata = data.get('metadata', {})
        
        if not name or not pine_source or not python_code:
            return jsonify({"error": "Name, pine_source, and python_code are required"}), 400
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategies (name, description, pine_source, python_code, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, pine_source, python_code, json.dumps(metadata)))
        
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "id": strategy_id,
            "message": f"Strategy '{name}' saved successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all saved strategies."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, created_at, updated_at 
            FROM strategies 
            ORDER BY created_at DESC
        ''')
        
        strategies = []
        for row in cursor.fetchall():
            strategies.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            })
        
        conn.close()
        
        return jsonify({"strategies": strategies})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """Get specific strategy by ID."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, pine_source, python_code, metadata, created_at, updated_at
            FROM strategies 
            WHERE id = ?
        ''', (strategy_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"error": "Strategy not found"}), 404
        
        strategy = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "pine_source": row[3],
            "python_code": row[4],
            "metadata": json.loads(row[5]) if row[5] else {},
            "created_at": row[6],
            "updated_at": row[7]
        }
        
        return jsonify(strategy)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-conversion', methods=['GET'])
def test_conversion():
    """Test endpoint to verify conversion pipeline."""
    try:
        # Generate a simple RSI strategy for testing
        python_code = convert_simple_rsi_strategy()
        
        return jsonify({
            "success": True,
            "message": "Conversion pipeline is working",
            "sample_output": python_code[:500] + "..." if len(python_code) > 500 else python_code
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crypto/ohlc', methods=['GET'])
def get_crypto_ohlc():
    """Fetch crypto OHLC data from Binance (real live data) with Tardis fallback."""
    try:
        # Get query parameters
        symbol = request.args.get('symbol')
        exchange = request.args.get('exchange', 'BINANCE')
        timeframe = request.args.get('timeframe', '1h')
        n_bars = int(request.args.get('n_bars', 1000))
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'
        
        # Validate required parameters
        if not symbol:
            return jsonify({"error": "Missing required parameter: symbol"}), 400
        
        data = None
        provider_used = None
        
        # Try Binance first (real live data)
        if BINANCE_AVAILABLE:
            try:
                provider = get_binance_provider()
                data = provider.fetch_ohlc(
                    symbol=symbol.upper(),
                    exchange=exchange.upper(),
                    timeframe=timeframe,
                    n_bars=n_bars,
                    use_cache=use_cache
                )
                provider_used = "Binance (Live Data)"
            except Exception as binance_error:
                logger.error(f"Binance failed: {binance_error}")
                # Continue to Tardis fallback
        
        # Fallback to Tardis if Binance failed
        if data is None and TARDIS_AVAILABLE:
            try:
                provider = get_tardis_provider()
                data = provider.fetch_ohlc(
                    symbol=symbol.upper(),
                    exchange=exchange.upper(),
                    timeframe=timeframe,
                    n_bars=n_bars,
                    use_cache=use_cache
                )
                provider_used = "Tardis.dev (Demo Data)"
            except Exception as tardis_error:
                logger.error(f"Tardis failed: {tardis_error}")
        
        if data is None:
            if not BINANCE_AVAILABLE and not TARDIS_AVAILABLE:
                return jsonify({"error": "No crypto data providers available"}), 503
            else:
                return jsonify({"error": "Failed to fetch data from all available providers"}), 500
        
        # Add provider info to response
        data["provider"] = provider_used
        return jsonify(data)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crypto/exchanges', methods=['GET'])
def get_crypto_exchanges():
    """Get list of supported crypto exchanges."""
    if not TARDIS_AVAILABLE:
        # Return default crypto exchanges if Tardis not available
        exchanges = ['BINANCE', 'COINBASE', 'KRAKEN', 'BITSTAMP', 'BYBIT', 'BITFINEX']
        return jsonify({"exchanges": exchanges})
        
    try:
        provider = get_tardis_provider()
        exchanges = provider.get_available_exchanges()
        return jsonify({"exchanges": exchanges})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crypto/symbols', methods=['GET'])
def get_crypto_symbols():
    """Get popular crypto symbols for an exchange."""
    try:
        exchange = request.args.get('exchange', 'BINANCE')
        
        if not TARDIS_AVAILABLE:
            # Return default crypto symbols
            default_symbols = {
                'BINANCE': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'SOLUSDT'],
                'COINBASE': ['BTCUSD', 'ETHUSD', 'ADAUSD', 'DOTUSD', 'LINKUSD', 'SOLUSD'],
                'KRAKEN': ['XBTUSD', 'ETHUSD', 'ADAUSD', 'DOTUSD', 'LINKUSD'],
                'BITSTAMP': ['BTCUSD', 'ETHUSD', 'ADAUSD'],
                'BYBIT': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT'],
                'BITFINEX': ['BTCUSD', 'ETHUSD', 'ADAUSD']
            }
            symbols = default_symbols.get(exchange.upper(), ['BTCUSDT', 'ETHUSDT'])
        else:
            provider = get_tardis_provider()
            symbols = provider.get_popular_symbols(exchange.upper())
        
        return jsonify({"exchange": exchange.upper(), "symbols": symbols})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Crypto-focused endpoints
@app.route('/api/crypto/status', methods=['GET'])
def get_crypto_status():
    """Get crypto data provider status."""
    providers = []
    available = False
    
    if BINANCE_AVAILABLE:
        providers.append("Binance (Live Data)")
        available = True
    
    if TARDIS_AVAILABLE:
        providers.append("Tardis.dev (Demo Data)")
        available = True
    
    if available:
        message = f"Crypto data providers available: {', '.join(providers)}"
        primary_provider = providers[0] if providers else "None"
    else:
        message = "No crypto data providers available"
        primary_provider = "None"
    
    return jsonify({
        "available": available,
        "provider": primary_provider,
        "providers": providers,
        "authenticated": False,  # Public APIs
        "message": message
    })

# Backward compatibility routes (redirect to crypto endpoints)
@app.route('/api/tv/status', methods=['GET'])
def get_tv_status_compat():
    """Backward compatibility for existing frontend."""
    return get_crypto_status()

@app.route('/api/tv/exchanges', methods=['GET'])
def get_tv_exchanges_compat():
    """Backward compatibility for existing frontend."""
    return get_crypto_exchanges()

@app.route('/api/tv/symbols', methods=['GET'])
def get_tv_symbols_compat():
    """Backward compatibility for existing frontend."""
    return get_crypto_symbols()

@app.route('/api/tv/ohlc', methods=['GET'])
def get_tv_ohlc_compat():
    """Backward compatibility for existing frontend."""
    return get_crypto_ohlc()

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start server
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Pine2Py API Server starting on port {port}")
    print(f"📁 Database: {DATABASE_PATH}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)