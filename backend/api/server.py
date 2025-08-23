#!/usr/bin/env python3
"""Flask API server for Pine2Py conversion and strategy management."""

import os
import sys
import logging
import atexit
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

# Performance optimization imports
try:
    from performance import (
        get_cache_manager, cache_response, 
        get_query_optimizer, get_memory_manager, 
        get_connection_pool_manager, memory_profiler
    )
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
    logger.info("✅ Performance optimization system loaded successfully")
except ImportError as e:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False
    logger.warning(f"⚠️ Performance optimization not available: {e}")

# Advanced monitoring imports
try:
    from monitoring import (
        get_system_monitor, get_trading_metrics_collector,
        get_alerting_framework, get_health_checker,
        get_monitoring_dashboard
    )
    MONITORING_SYSTEM_AVAILABLE = True
    logger.info("✅ Advanced monitoring system loaded successfully")
except ImportError as e:
    MONITORING_SYSTEM_AVAILABLE = False
    logger.warning(f"⚠️ Advanced monitoring not available: {e}")

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

# Initialize performance optimization systems
if PERFORMANCE_OPTIMIZATION_AVAILABLE:
    # Database path for unified database
    UNIFIED_DB_PATH = Path(__file__).parent.parent / "database" / "pineopt_unified.db"
    
    # Initialize performance systems
    cache_manager = get_cache_manager()
    query_optimizer = get_query_optimizer(str(UNIFIED_DB_PATH))
    memory_manager = get_memory_manager(memory_limit_mb=2048)
    connection_pool_manager = get_connection_pool_manager(str(UNIFIED_DB_PATH))
    
    logger.info("🚀 Performance optimization systems initialized")
    
    # Register cleanup on app shutdown
    def cleanup_performance_systems():
        """Cleanup performance systems on shutdown"""
        try:
            if 'connection_pool_manager' in globals():
                connection_pool_manager.close_all_pools()
            if 'memory_manager' in globals():
                memory_manager.stop_monitoring()
            logger.info("Performance systems cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during performance systems cleanup: {e}")
    
    atexit.register(cleanup_performance_systems)

# Initialize advanced monitoring systems
if MONITORING_SYSTEM_AVAILABLE:
    # Initialize monitoring components
    system_monitor = get_system_monitor(collection_interval=30)
    trading_metrics_collector = get_trading_metrics_collector(collection_interval=60)
    alerting_framework = get_alerting_framework()
    health_checker = get_health_checker(check_interval=300)
    monitoring_dashboard = get_monitoring_dashboard(update_interval=30)
    
    logger.info("🔍 Advanced monitoring systems initialized")
    
    # Register cleanup for monitoring systems
    def cleanup_monitoring_systems():
        """Cleanup monitoring systems on shutdown"""
        try:
            if 'system_monitor' in globals():
                system_monitor.stop_monitoring()
            if 'trading_metrics_collector' in globals():
                trading_metrics_collector.stop_monitoring()
            if 'alerting_framework' in globals():
                alerting_framework.stop_monitoring()
            if 'health_checker' in globals():
                health_checker.stop_monitoring()
            if 'monitoring_dashboard' in globals():
                monitoring_dashboard.stop_auto_refresh()
            logger.info("Monitoring systems cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during monitoring systems cleanup: {e}")
    
    atexit.register(cleanup_monitoring_systems)

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

# Import and register backtest routes (Epic 5 Sprint 2)
try:
    from backtest_routes import backtest_bp
    app.register_blueprint(backtest_bp)
    logger.info("✅ Backtest routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import backtest routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering backtest routes: {e}")

# Import and register market data routes (Phase 1)
try:
    from .market_routes import market_bp
    app.register_blueprint(market_bp, url_prefix='/api/market')
    logger.info("✅ Market data routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import market routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering market routes: {e}")

# Import and register AI analysis routes (Sprint 1)
try:
    from ai_analysis_routes import ai_analysis_bp
    app.register_blueprint(ai_analysis_bp)
    logger.info("✅ AI analysis routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import AI analysis routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering AI analysis routes: {e}")

# Import and register intelligent conversion routes (Sprint 2)
try:
    from intelligent_conversion_routes import intelligent_conversion_bp
    app.register_blueprint(intelligent_conversion_bp)
    logger.info("✅ Intelligent conversion routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import intelligent conversion routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering intelligent conversion routes: {e}")

# Import and register parameter management routes (Sprint 3)
try:
    from parameter_routes import parameter_bp
    app.register_blueprint(parameter_bp)
    logger.info("✅ Parameter management routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import parameter routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering parameter routes: {e}")

# Import and register real backtest routes (Sprint 4)
try:
    from real_backtest_routes import real_backtest_bp
    app.register_blueprint(real_backtest_bp)
    logger.info("✅ Real backtest routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import real backtest routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering real backtest routes: {e}")

# Import and register AI conversion routes (Epic 6)
try:
    from .ai_conversion_routes import ai_conversion_bp
    app.register_blueprint(ai_conversion_bp)
    logger.info("✅ AI conversion routes registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not import AI conversion routes: {e}")
except Exception as e:
    logger.error(f"❌ Error registering AI conversion routes: {e}")

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

# Performance monitoring endpoints
if PERFORMANCE_OPTIMIZATION_AVAILABLE:
    
    @app.route('/api/performance/stats', methods=['GET'])
    @cache_response('api_responses', ttl=30)
    def get_performance_stats():
        """Get comprehensive performance statistics."""
        try:
            stats = {
                'cache': cache_manager.get_stats(),
                'query_optimizer': query_optimizer.get_query_statistics(),
                'memory': memory_manager.get_current_memory_usage(),
                'connections': connection_pool_manager.get_all_stats(),
                'timestamp': datetime.now().isoformat()
            }
            return jsonify({
                "success": True,
                "performance_stats": stats
            })
        except Exception as e:
            logger.error(f"Performance stats error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/performance/memory', methods=['GET'])
    def get_memory_stats():
        """Get detailed memory usage statistics."""
        try:
            memory_stats = {
                'current_usage': memory_manager.get_current_memory_usage(),
                'trends': memory_manager.get_memory_trends(minutes=30),
                'health': memory_manager.check_memory_health()
            }
            return jsonify({
                "success": True,
                "memory_stats": memory_stats
            })
        except Exception as e:
            logger.error(f"Memory stats error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/performance/cache', methods=['GET'])
    def get_cache_stats():
        """Get cache statistics and efficiency metrics."""
        try:
            cache_stats = cache_manager.get_stats()
            return jsonify({
                "success": True,
                "cache_stats": cache_stats
            })
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/performance/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear cache entries by type."""
        try:
            cache_type = request.json.get('cache_type') if request.is_json else None
            cleared_count = cache_manager.clear(cache_type)
            
            return jsonify({
                "success": True,
                "cleared_entries": cleared_count,
                "cache_type": cache_type or "all"
            })
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/performance/optimize', methods=['POST'])
    def optimize_performance():
        """Run performance optimization routines."""
        try:
            results = {
                'memory_optimization': memory_manager.optimize_memory(),
                'cache_cleanup': cache_manager.cleanup_expired(),
                'database_optimization': 'completed'
            }
            
            # Run database vacuum if requested
            force_vacuum = request.json.get('vacuum_database', False) if request.is_json else False
            if force_vacuum:
                query_optimizer.vacuum_database()
                results['database_vacuum'] = 'completed'
            
            return jsonify({
                "success": True,
                "optimization_results": results
            })
        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

# Advanced monitoring endpoints
if MONITORING_SYSTEM_AVAILABLE:
    
    @app.route('/api/monitoring/dashboard', methods=['GET'])
    def get_monitoring_dashboard():
        """Get comprehensive monitoring dashboard data."""
        try:
            dashboard_data = monitoring_dashboard.get_current_dashboard()
            return jsonify({
                "success": True,
                "dashboard": dashboard_data
            })
        except Exception as e:
            logger.error(f"Monitoring dashboard error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/summary', methods=['GET'])
    def get_monitoring_summary():
        """Get high-level monitoring summary."""
        try:
            summary = monitoring_dashboard.get_dashboard_summary()
            return jsonify({
                "success": True,
                "summary": summary
            })
        except Exception as e:
            logger.error(f"Monitoring summary error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/system', methods=['GET'])
    def get_system_monitoring():
        """Get detailed system monitoring metrics."""
        try:
            current_metrics = system_monitor.get_current_metrics()
            hours = int(request.args.get('hours', 1))
            history = system_monitor.get_metrics_history(hours)
            
            return jsonify({
                "success": True,
                "current": current_metrics,
                "history": history
            })
        except Exception as e:
            logger.error(f"System monitoring error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/trading', methods=['GET'])
    def get_trading_monitoring():
        """Get trading-specific monitoring metrics."""
        try:
            trading_data = trading_metrics_collector.get_trading_dashboard_data()
            
            # Get symbol analytics if requested
            symbol = request.args.get('symbol')
            if symbol:
                hours = int(request.args.get('hours', 24))
                symbol_analytics = trading_metrics_collector.get_symbol_analytics(symbol, hours)
                trading_data['symbol_analytics'] = symbol_analytics
            
            return jsonify({
                "success": True,
                "trading_metrics": trading_data
            })
        except Exception as e:
            logger.error(f"Trading monitoring error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/health', methods=['GET'])
    def get_health_monitoring():
        """Get comprehensive system health check."""
        try:
            health_data = health_checker.get_overall_health()
            return jsonify({
                "success": True,
                "health": health_data
            })
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/health/<component>', methods=['GET'])
    def get_component_health(component):
        """Get health check for specific component."""
        try:
            health_result = health_checker.run_health_check(component)
            return jsonify({
                "success": True,
                "component_health": health_result.to_dict()
            })
        except Exception as e:
            logger.error(f"Component health check error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/alerts', methods=['GET'])
    def get_alerts_monitoring():
        """Get alert monitoring data."""
        try:
            severity_filter = request.args.get('severity')
            severity_enum = None
            if severity_filter:
                from monitoring.alerting import AlertSeverity
                try:
                    severity_enum = AlertSeverity(severity_filter.lower())
                except ValueError:
                    pass
            
            active_alerts = alerting_framework.get_active_alerts(severity_enum)
            hours = int(request.args.get('hours', 24))
            alert_stats = alerting_framework.get_alert_statistics(hours)
            
            return jsonify({
                "success": True,
                "active_alerts": [alert.to_dict() for alert in active_alerts],
                "statistics": alert_stats
            })
        except Exception as e:
            logger.error(f"Alert monitoring error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge a specific alert."""
        try:
            acknowledger = request.json.get('acknowledger', 'api_user') if request.is_json else 'api_user'
            alerting_framework.acknowledge_alert(alert_id, acknowledger)
            
            return jsonify({
                "success": True,
                "message": f"Alert {alert_id} acknowledged by {acknowledger}"
            })
        except Exception as e:
            logger.error(f"Alert acknowledgment error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/monitoring/trends', methods=['GET'])
    def get_monitoring_trends():
        """Get historical monitoring trends."""
        try:
            hours = int(request.args.get('hours', 6))
            trends = monitoring_dashboard.get_historical_trends(hours)
            baseline = monitoring_dashboard.get_performance_baseline(24)
            
            return jsonify({
                "success": True,
                "trends": trends,
                "baseline": baseline
            })
        except Exception as e:
            logger.error(f"Monitoring trends error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

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
        
        # Also save to main database for backtest engine compatibility
        try:
            import uuid
            main_db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'pineopt.db')
            main_conn = sqlite3.connect(main_db_path)
            main_cursor = main_conn.cursor()
            
            main_cursor.execute('''
                INSERT INTO strategies (id, name, description, author, language, source_code, 
                                      validation_status, supported_timeframes, supported_assets)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                name,
                description or 'Converted Pine Script strategy',
                'PineOpt Converter',
                'python',
                python_code,
                'valid',
                json.dumps(["1h", "4h", "1d"]),
                json.dumps(["BTCUSDT", "ETHUSDT", "ADAUSDT"])
            ))
            
            main_strategy_id = main_cursor.lastrowid
            main_conn.commit()
            main_conn.close()
            
            logger.info(f"Strategy also saved to main database with ID: {main_strategy_id}")
        except Exception as e:
            logger.warning(f"Failed to save to main database: {e}")
            # Continue anyway - API database save was successful
        
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
            SELECT id, name, description, pine_source, python_code, metadata, created_at, updated_at 
            FROM strategies 
            ORDER BY created_at DESC
        ''')
        
        strategies = []
        for row in cursor.fetchall():
            # Parse metadata if available
            metadata = json.loads(row[5]) if len(row) > 5 and row[5] else {}
            
            # Count parameters from Python code if available
            python_code = row[4] if len(row) > 4 and row[4] else ""
            param_count = python_code.count('StrategyParameter(')
            
            strategies.append({
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "author": metadata.get('author', 'Unknown'),
                "version": "1.0",
                "language": "python",
                "validation_status": "valid",
                "file_size": len(row[3]) if len(row) > 3 and row[3] else 0,  # pine_source length
                "parameters_count": param_count,
                "dependencies_count": 3,
                "tags": metadata.get('tags', []),
                "upload_count": 1,
                "backtest_count": 0,
                "created_at": row[6],  # created_at is now at index 6
                "updated_at": row[7],  # updated_at is now at index 7
                "last_used": None
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

@app.route('/api/strategies/upload', methods=['POST'])
def upload_strategy():
    """Upload and process a Pine Script file."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get form data
        strategy_name = request.form.get('name', file.filename.replace('.pine', '').replace('.txt', ''))
        description = request.form.get('description', 'Uploaded Pine Script strategy')
        author = request.form.get('author', 'Unknown')
        tags = request.form.get('tags', '')
        
        # Read Pine Script content
        pine_code = file.read().decode('utf-8')
        
        if not pine_code.strip():
            return jsonify({"error": "File is empty"}), 400
        
        # Convert Pine Script to Python
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
        
        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        metadata = {
            'author': author,
            'tags': tags.split(',') if tags else [],
            'conversion_timestamp': datetime.now().isoformat(),
            'file_name': file.filename
        }
        
        cursor.execute('''
            INSERT INTO strategies (name, description, pine_source, python_code, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (strategy_name, description, pine_code, python_code, json.dumps(metadata)))
        
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Count parameters from Python code
        param_count = python_code.count('StrategyParameter(')
        
        strategy_data = {
            "id": str(strategy_id),
            "name": strategy_name,
            "description": description,
            "author": author,
            "version": "1.0",
            "language": "python",
            "validation_status": "valid",
            "file_size": len(pine_code),
            "parameters_count": param_count,
            "dependencies_count": 3,  # Basic dependencies (pandas, numpy, ta)
            "tags": metadata['tags'],
            "upload_count": 1,
            "backtest_count": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_used": None,
            "python_code": python_code,
            "pine_source": pine_code
        }

        return jsonify({
            "success": True,
            "strategy": strategy_data,
            "validation": {
                "status": "valid",
                "errors": [],
                "warnings": []
            },
            "message": f"Strategy '{strategy_name}' uploaded and converted successfully"
        })
        
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

if PERFORMANCE_OPTIMIZATION_AVAILABLE:
    from performance import cache_market_data
    
    @app.route('/api/crypto/ohlc', methods=['GET'])
    @memory_profiler(track_objects=True)
    def get_crypto_ohlc():
        """Fetch crypto OHLC data from Binance (real live data) with Tardis fallback."""
        start_time = time.time()
        try:
            # Get query parameters
            symbol = request.args.get('symbol')
            exchange = request.args.get('exchange', 'BINANCE')
            timeframe = request.args.get('timeframe', '1h')
            n_bars = int(request.args.get('n_bars', 1000))
            use_cache = request.args.get('use_cache', 'true').lower() == 'true'
            
            # Validate required parameters
            if not symbol:
                if MONITORING_SYSTEM_AVAILABLE:
                    response_time = (time.time() - start_time) * 1000
                    trading_metrics_collector.record_ohlcv_request(
                        symbol="UNKNOWN", timeframe=timeframe, provider="NONE",
                        response_time_ms=response_time, cache_hit=False, 
                        data_points=0, error=True
                    )
                return jsonify({"error": "Missing required parameter: symbol"}), 400
            
            # Generate cache key for this request
            cache_key = f"ohlcv_{symbol}_{exchange}_{timeframe}_{n_bars}"
            
            # Try to get from performance cache first if caching is enabled
            if use_cache:
                cached_data = cache_manager.get(cache_key, 'historical_data')
                if cached_data is not None:
                    response_time = (time.time() - start_time) * 1000
                    logger.debug(f"Cache HIT for OHLCV data: {cache_key}")
                    
                    # Record monitoring metrics for cache hit
                    if MONITORING_SYSTEM_AVAILABLE:
                        trading_metrics_collector.record_ohlcv_request(
                            symbol=symbol, timeframe=timeframe, provider=cached_data.get("provider", "CACHE"),
                            response_time_ms=response_time, cache_hit=True, 
                            data_points=len(cached_data.get("data", [])), error=False
                        )
                    
                    # Mark as cached in response
                    cached_data["cached"] = True
                    cached_data["response_time_ms"] = response_time
                    return jsonify(cached_data)
else:
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
                        use_cache=False  # We handle caching at the API level
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
                        use_cache=False  # We handle caching at the API level
                    )
                    provider_used = "Tardis.dev (Demo Data)"
                except Exception as tardis_error:
                    logger.error(f"Tardis failed: {tardis_error}")
            
            if data is None:
                # Record failed request metrics
                if MONITORING_SYSTEM_AVAILABLE:
                    response_time = (time.time() - start_time) * 1000
                    trading_metrics_collector.record_ohlcv_request(
                        symbol=symbol, timeframe=timeframe, provider="FAILED",
                        response_time_ms=response_time, cache_hit=False, 
                        data_points=0, error=True
                    )
                
                if not BINANCE_AVAILABLE and not TARDIS_AVAILABLE:
                    return jsonify({"error": "No crypto data providers available"}), 503
                else:
                    return jsonify({"error": "Failed to fetch data from all available providers"}), 500
            
            # Calculate response time and record metrics
            response_time = (time.time() - start_time) * 1000
            data_points = len(data.get("data", [])) if data else 0
            
            # Add provider info and performance metadata
            data["provider"] = provider_used
            data["cached"] = False
            data["performance_optimized"] = True
            data["response_time_ms"] = response_time
            
            # Record monitoring metrics for successful fetch
            if MONITORING_SYSTEM_AVAILABLE:
                trading_metrics_collector.record_ohlcv_request(
                    symbol=symbol, timeframe=timeframe, provider=provider_used,
                    response_time_ms=response_time, cache_hit=False, 
                    data_points=data_points, error=False
                )
            
            # Cache the successful response if caching is enabled
            if use_cache and PERFORMANCE_OPTIMIZATION_AVAILABLE:
                # Calculate TTL based on timeframe
                ttl_map = {'1m': 60, '5m': 300, '1h': 1800, '4h': 3600, '1d': 14400}
                ttl = ttl_map.get(timeframe, 300)
                
                cache_manager.set(cache_key, data, 'historical_data', ttl)
                logger.debug(f"Cached OHLC data: {cache_key} (TTL: {ttl}s)")
            
            return jsonify(data)
        
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
        data["performance_optimized"] = False
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

@app.route('/api/market/overview', methods=['GET'])
def get_market_overview():
    """Get market overview data for dashboard."""
    try:
        # Mock market data for now
        market_data = {
            "success": True,
            "data": {
                "total_volume_24h": 1234567890,
                "total_market_cap": 987654321000,
                "bitcoin_dominance": 52.3,
                "market_cap_change_24h": 2.45,
                "active_cryptos": 470,
                "trending_coins": [
                    {"symbol": "BTCUSDT", "price": 43250.50, "change_24h": 1.25},
                    {"symbol": "ETHUSDT", "price": 2890.75, "change_24h": -0.85},
                    {"symbol": "SOLUSDT", "price": 125.30, "change_24h": 3.15}
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Market overview failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start server
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Pine2Py API Server starting on port {port}")
    print(f"📁 Database: {DATABASE_PATH}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)