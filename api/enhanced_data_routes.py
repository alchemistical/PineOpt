"""
Enhanced Data Management API Routes
Supports bulk historical data fetching, synchronization, and 4-year data storage
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sys
import os
import logging
import pandas as pd

# Add database and provider modules to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.data.providers.enhanced_binance_provider import get_enhanced_binance_provider
from database.data_access import crypto_data, activity_data
from database.models import db_manager

# Create blueprint
enhanced_data_api = Blueprint('enhanced_data_api', __name__)
logger = logging.getLogger(__name__)

# Get enhanced provider
try:
    binance_provider = get_enhanced_binance_provider()
    BINANCE_AVAILABLE = True
    logger.info("✅ Enhanced Binance provider loaded")
except Exception as e:
    BINANCE_AVAILABLE = False
    logger.error(f"❌ Enhanced Binance provider not available: {e}")

# =======================
# BULK DATA FETCHING
# =======================

@enhanced_data_api.route('/api/data/bulk/historical', methods=['POST'])
def fetch_bulk_historical():
    """Fetch bulk historical data for a symbol."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        exchange = data.get('exchange', 'BINANCE')
        timeframe = data.get('timeframe', '1h')
        days_back = data.get('days_back', 365)  # Default 1 year
        
        # Calculate start date
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Validate input
        if days_back > 1460:  # 4 years
            return jsonify({
                'success': False,
                'error': 'Maximum 4 years (1460 days) of historical data allowed'
            }), 400
        
        logger.info(f"Bulk fetch requested: {symbol} {timeframe} for {days_back} days")
        
        # Fetch data
        result = binance_provider.fetch_historical_bulk(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            max_bars=days_back * 24  # Conservative estimate
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in bulk historical fetch: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/bulk/multi-asset', methods=['POST'])
def fetch_multi_asset_bulk():
    """Fetch bulk historical data for multiple assets and timeframes."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        data = request.get_json()
        
        # Get collection parameters
        symbols = data.get('symbols', ['BTCUSDT', 'ETHUSDT'])
        timeframes = data.get('timeframes', ['1h', '1d']) 
        exchange = data.get('exchange', 'BINANCE')
        days_back = data.get('days_back', 365)
        
        # Validate input
        if days_back > 1460:
            return jsonify({
                'success': False,
                'error': 'Maximum 4 years (1460 days) of historical data allowed'
            }), 400
            
        if len(symbols) > 20:
            return jsonify({
                'success': False, 
                'error': 'Maximum 20 symbols allowed per request'
            }), 400
            
        if len(timeframes) > 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 timeframes allowed per request'
            }), 400
        
        logger.info(f"Multi-asset bulk collection: {len(symbols)} symbols × {len(timeframes)} timeframes")
        
        # Collection results
        results = []
        total_bars_collected = 0
        total_bars_stored = 0
        failed_collections = []
        
        # Calculate dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Collect data for each symbol/timeframe combination
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    logger.info(f"Collecting {symbol} {timeframe}...")
                    
                    # Fetch data for this combination
                    result = binance_provider.fetch_historical_bulk(
                        symbol=symbol,
                        exchange=exchange,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date,
                        max_bars=days_back * 24
                    )
                    
                    if result.get('success'):
                        collection_info = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'bars_fetched': result.get('total_bars_fetched', 0),
                            'bars_stored': result.get('total_bars_stored', 0),
                            'status': 'success'
                        }
                        total_bars_collected += result.get('total_bars_fetched', 0)
                        total_bars_stored += result.get('total_bars_stored', 0)
                    else:
                        collection_info = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'error': result.get('error', 'Unknown error'),
                            'status': 'failed'
                        }
                        failed_collections.append(f"{symbol}_{timeframe}")
                    
                    results.append(collection_info)
                    
                    # Rate limiting between requests
                    import time
                    time.sleep(0.2)  # 200ms delay
                    
                except Exception as e:
                    logger.error(f"Failed to collect {symbol} {timeframe}: {e}")
                    failed_collections.append(f"{symbol}_{timeframe}")
                    results.append({
                        'symbol': symbol,
                        'timeframe': timeframe, 
                        'error': str(e),
                        'status': 'failed'
                    })
        
        # Summary
        total_combinations = len(symbols) * len(timeframes)
        successful_collections = total_combinations - len(failed_collections)
        success_rate = (successful_collections / total_combinations * 100) if total_combinations > 0 else 0
        
        summary = {
            'success': True,
            'collection_summary': {
                'total_combinations': total_combinations,
                'successful_collections': successful_collections,
                'failed_collections': len(failed_collections),
                'success_rate_pct': round(success_rate, 2),
                'total_bars_collected': total_bars_collected,
                'total_bars_stored': total_bars_stored
            },
            'detailed_results': results,
            'failed_collections': failed_collections,
            'parameters': {
                'symbols': symbols,
                'timeframes': timeframes,
                'exchange': exchange,
                'days_back': days_back,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Multi-asset collection complete: {successful_collections}/{total_combinations} successful")
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error in multi-asset bulk collection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/sync', methods=['POST'])
def sync_data():
    """Synchronize recent data for a symbol."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        exchange = data.get('exchange', 'BINANCE')
        timeframe = data.get('timeframe', '1h')
        days_back = data.get('days_back', 7)  # Default 1 week
        
        logger.info(f"Data sync requested: {symbol} {timeframe} for {days_back} days")
        
        # Sync data
        result = binance_provider.sync_data(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            days_back=days_back
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in data sync: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/fetch/enhanced', methods=['POST'])
def fetch_enhanced_ohlc():
    """Fetch recent OHLC data with enhanced storage."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        exchange = data.get('exchange', 'BINANCE')
        timeframe = data.get('timeframe', '1h')
        n_bars = data.get('n_bars', 1000)
        store_in_db = data.get('store_in_db', True)
        
        logger.info(f"Enhanced fetch requested: {symbol} {timeframe} {n_bars} bars")
        
        # Fetch data
        result = binance_provider.fetch_recent_ohlc(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            n_bars=n_bars,
            store_in_db=store_in_db
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in enhanced fetch: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =======================
# DATA ANALYSIS & EXPORT
# =======================

@enhanced_data_api.route('/api/data/analyze/<symbol>', methods=['GET'])
def analyze_data_quality(symbol):
    """Analyze data quality and completeness for a symbol."""
    try:
        exchange = request.args.get('exchange', 'BINANCE')
        timeframe = request.args.get('timeframe', '1h')
        
        # Get data from database
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe
        )
        
        if df.empty:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'exchange': exchange,
                'timeframe': timeframe,
                'analysis': {
                    'total_records': 0,
                    'date_range': None,
                    'completeness': 0,
                    'gaps': [],
                    'quality_score': 0
                }
            })
        
        # Calculate analysis metrics
        total_records = len(df)
        date_range = {
            'start': df.index.min().isoformat(),
            'end': df.index.max().isoformat(),
            'span_days': (df.index.max() - df.index.min()).days
        }
        
        # Calculate expected vs actual records
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }.get(timeframe, 60)
        
        expected_records = int(date_range['span_days'] * 24 * 60 / timeframe_minutes)
        completeness = (total_records / expected_records * 100) if expected_records > 0 else 100
        
        # Find gaps (simplified gap detection)
        gaps = []
        if len(df) > 1:
            time_diffs = df.index.to_series().diff()
            expected_diff = pd.Timedelta(minutes=timeframe_minutes)
            large_gaps = time_diffs[time_diffs > expected_diff * 1.5]  # 50% tolerance
            
            for gap_time, gap_size in large_gaps.items():
                gaps.append({
                    'timestamp': gap_time.isoformat(),
                    'gap_duration_minutes': int(gap_size.total_seconds() / 60),
                    'expected_duration_minutes': timeframe_minutes
                })
        
        # Calculate quality score (0-100)
        quality_score = min(100, int(completeness * 0.8 + (100 - min(len(gaps), 10) * 10) * 0.2))
        
        analysis = {
            'total_records': total_records,
            'date_range': date_range,
            'completeness_pct': round(completeness, 2),
            'expected_records': expected_records,
            'gaps_detected': len(gaps),
            'gaps': gaps[:10],  # First 10 gaps
            'quality_score': quality_score,
            'price_range': {
                'min': float(df['low'].min()),
                'max': float(df['high'].max()),
                'latest': float(df['close'].iloc[-1])
            }
        }
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'exchange': exchange,
            'timeframe': timeframe,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing data quality: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/export/<symbol>', methods=['GET'])
def export_data(symbol):
    """Export OHLC data in various formats."""
    try:
        exchange = request.args.get('exchange', 'BINANCE')
        timeframe = request.args.get('timeframe', '1h')
        format_type = request.args.get('format', 'json')  # json, csv
        limit = request.args.get('limit', type=int)
        
        # Get start/end dates if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        start_timestamp = None
        end_timestamp = None
        
        if start_date:
            start_timestamp = int(datetime.fromisoformat(start_date.replace('Z', '+00:00')).timestamp() * 1000000)
        if end_date:
            end_timestamp = int(datetime.fromisoformat(end_date.replace('Z', '+00:00')).timestamp() * 1000000)
        
        # Get data from database
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            limit=limit
        )
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found for the specified parameters'
            }), 404
        
        if format_type == 'csv':
            # Return CSV data
            csv_data = df.to_csv()
            return csv_data, 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename={symbol}_{exchange}_{timeframe}_export.csv'
            }
        else:
            # Return JSON data
            export_data = []
            for timestamp, row in df.iterrows():
                export_data.append({
                    'timestamp': timestamp.isoformat(),
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
                'count': len(export_data),
                'data': export_data
            })
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =======================
# ENHANCED SYMBOLS & INFO
# =======================

@enhanced_data_api.route('/api/data/symbols/available', methods=['GET'])
def get_available_symbols():
    """Get available trading symbols from Binance."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        symbols = binance_provider.get_available_symbols()
        
        return jsonify({
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        })
        
    except Exception as e:
        logger.error(f"Error getting available symbols: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/bulk/maximum-depth', methods=['POST'])
def fetch_maximum_depth_collection():
    """Fetch maximum historical depth for all USDT pairs and timeframes."""
    try:
        if not BINANCE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Enhanced Binance provider not available'
            }), 503
        
        data = request.get_json()
        
        # Maximum depth configuration
        max_depth_config = {
            '1d': 1460,   # 4 years daily
            '1w': 1460,   # 4+ years weekly  
            '1h': 1095,   # 3 years hourly
            '4h': 1095,   # 3 years 4-hourly
            '30m': 730,   # 2 years 30-minute
            '15m': 730,   # 2 years 15-minute
        }
        
        # Target USDT pairs in priority order
        target_symbols = [
            # Tier 1: Major pairs
            'BTCUSDT', 'ETHUSDT',
            # Tier 2: Top altcoins  
            'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOTUSDT',
            # Tier 3: Popular coins
            'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT', 'LINKUSDT', 'LTCUSDT'
        ]
        
        # Override from request
        symbols = data.get('symbols', target_symbols)
        timeframes = data.get('timeframes', ['1d', '1h', '4h', '1w'])
        exchange = data.get('exchange', 'BINANCE')
        
        # Validate timeframes against max depth config
        valid_timeframes = [tf for tf in timeframes if tf in max_depth_config]
        if not valid_timeframes:
            return jsonify({
                'success': False,
                'error': f'No valid timeframes provided. Supported: {list(max_depth_config.keys())}'
            }), 400
        
        logger.info(f"Maximum depth collection: {len(symbols)} symbols × {len(valid_timeframes)} timeframes")
        
        # Collection results
        results = []
        total_bars_collected = 0
        total_bars_stored = 0
        failed_collections = []
        
        # Collect maximum depth data for each combination
        for symbol in symbols:
            for timeframe in valid_timeframes:
                try:
                    days_back = max_depth_config[timeframe]
                    logger.info(f"Collecting maximum depth: {symbol} {timeframe} ({days_back} days)...")
                    
                    # Calculate dates for maximum depth
                    end_date = datetime.utcnow()
                    start_date = end_date - timedelta(days=days_back)
                    
                    # Fetch maximum historical data
                    result = binance_provider.fetch_historical_bulk(
                        symbol=symbol,
                        exchange=exchange,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date,
                        max_bars=days_back * 24  # Conservative estimate
                    )
                    
                    if result.get('success'):
                        collection_info = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'days_back': days_back,
                            'bars_fetched': result.get('total_bars_fetched', 0),
                            'bars_stored': result.get('total_bars_stored', 0),
                            'start_date': result.get('start_date'),
                            'end_date': result.get('end_date'),
                            'status': 'success'
                        }
                        total_bars_collected += result.get('total_bars_fetched', 0)
                        total_bars_stored += result.get('total_bars_stored', 0)
                    else:
                        collection_info = {
                            'symbol': symbol,
                            'timeframe': timeframe,
                            'days_back': days_back,
                            'error': result.get('error', 'Unknown error'),
                            'status': 'failed'
                        }
                        failed_collections.append(f"{symbol}_{timeframe}")
                    
                    results.append(collection_info)
                    
                    # Rate limiting between requests (important for large collections)
                    import time
                    time.sleep(0.5)  # 500ms delay for maximum depth collections
                    
                except Exception as e:
                    logger.error(f"Failed maximum depth collection {symbol} {timeframe}: {e}")
                    failed_collections.append(f"{symbol}_{timeframe}")
                    results.append({
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'days_back': max_depth_config.get(timeframe, 0),
                        'error': str(e),
                        'status': 'failed'
                    })
        
        # Summary
        total_combinations = len(symbols) * len(valid_timeframes)
        successful_collections = total_combinations - len(failed_collections)
        success_rate = (successful_collections / total_combinations * 100) if total_combinations > 0 else 0
        
        # Calculate average depth achieved
        successful_results = [r for r in results if r.get('status') == 'success']
        avg_bars_per_symbol = total_bars_stored / len(successful_results) if successful_results else 0
        
        summary = {
            'success': True,
            'maximum_depth_summary': {
                'total_combinations': total_combinations,
                'successful_collections': successful_collections,
                'failed_collections': len(failed_collections),
                'success_rate_pct': round(success_rate, 2),
                'total_bars_collected': total_bars_collected,
                'total_bars_stored': total_bars_stored,
                'avg_bars_per_combination': round(avg_bars_per_symbol, 0),
                'depth_configuration': max_depth_config
            },
            'detailed_results': results,
            'failed_collections': failed_collections,
            'parameters': {
                'symbols': symbols,
                'timeframes': valid_timeframes,
                'exchange': exchange,
                'collection_type': 'maximum_historical_depth'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Maximum depth collection complete: {successful_collections}/{total_combinations} successful, {total_bars_stored} total bars")
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error in maximum depth collection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/collection/progress', methods=['GET'])
def get_collection_progress():
    """Get progress of multi-asset data collection."""
    try:
        # Get all available symbols and recommended timeframes
        target_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 
                         'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT']
        target_timeframes = ['15m', '1h', '4h', '1d', '1w']
        
        # Query database for current coverage
        session = db_manager.get_session()
        
        try:
            from database.models import CryptoOHLCData, CryptoDataSource
            from sqlalchemy import func, distinct
            
            # Get existing symbol/timeframe combinations
            existing_combinations = session.query(
                CryptoDataSource.symbol,
                CryptoDataSource.timeframe,
                CryptoDataSource.total_records,
                CryptoDataSource.first_timestamp_utc,
                CryptoDataSource.last_timestamp_utc,
                CryptoDataSource.completeness_pct
            ).filter(
                CryptoDataSource.status == 'active'
            ).all()
            
            # Build coverage matrix
            coverage_matrix = {}
            total_records_by_symbol = {}
            
            for combo in existing_combinations:
                symbol = combo.symbol
                timeframe = combo.timeframe
                
                if symbol not in coverage_matrix:
                    coverage_matrix[symbol] = {}
                    total_records_by_symbol[symbol] = 0
                
                coverage_matrix[symbol][timeframe] = {
                    'records': combo.total_records or 0,
                    'first_date': datetime.fromtimestamp(combo.first_timestamp_utc / 1000000).isoformat() if combo.first_timestamp_utc else None,
                    'last_date': datetime.fromtimestamp(combo.last_timestamp_utc / 1000000).isoformat() if combo.last_timestamp_utc else None,
                    'completeness_pct': float(combo.completeness_pct or 0),
                    'status': 'collected' if combo.total_records and combo.total_records > 0 else 'empty'
                }
                
                total_records_by_symbol[symbol] += combo.total_records or 0
            
            # Calculate collection statistics
            total_target_combinations = len(target_symbols) * len(target_timeframes)
            collected_combinations = 0
            total_records = 0
            
            symbol_progress = []
            
            for symbol in target_symbols:
                symbol_data = {
                    'symbol': symbol,
                    'total_records': total_records_by_symbol.get(symbol, 0),
                    'timeframes': {}
                }
                
                timeframes_collected = 0
                for timeframe in target_timeframes:
                    if symbol in coverage_matrix and timeframe in coverage_matrix[symbol]:
                        tf_data = coverage_matrix[symbol][timeframe]
                        symbol_data['timeframes'][timeframe] = tf_data
                        if tf_data['records'] > 0:
                            timeframes_collected += 1
                            collected_combinations += 1
                            total_records += tf_data['records']
                    else:
                        symbol_data['timeframes'][timeframe] = {
                            'records': 0,
                            'status': 'missing',
                            'completeness_pct': 0
                        }
                
                symbol_data['timeframes_collected'] = timeframes_collected
                symbol_data['timeframes_total'] = len(target_timeframes)
                symbol_data['completion_pct'] = round((timeframes_collected / len(target_timeframes)) * 100, 1)
                
                symbol_progress.append(symbol_data)
            
            # Overall progress
            overall_completion_pct = round((collected_combinations / total_target_combinations) * 100, 1)
            
            progress_summary = {
                'overall_progress': {
                    'collected_combinations': collected_combinations,
                    'total_target_combinations': total_target_combinations,
                    'completion_pct': overall_completion_pct,
                    'total_records': total_records
                },
                'target_matrix': {
                    'symbols': target_symbols,
                    'timeframes': target_timeframes,
                    'total_combinations': total_target_combinations
                },
                'symbol_progress': symbol_progress,
                'recommendations': {
                    'next_priority': [],
                    'missing_combinations': total_target_combinations - collected_combinations
                }
            }
            
            # Add recommendations for next priority collections
            for symbol_data in symbol_progress:
                if symbol_data['completion_pct'] < 100:
                    for tf, tf_data in symbol_data['timeframes'].items():
                        if tf_data['status'] == 'missing':
                            progress_summary['recommendations']['next_priority'].append({
                                'symbol': symbol_data['symbol'],
                                'timeframe': tf,
                                'priority': 'high' if symbol_data['symbol'] in ['BTCUSDT', 'ETHUSDT'] else 'medium'
                            })
            
            # Limit recommendations to top 10
            progress_summary['recommendations']['next_priority'] = progress_summary['recommendations']['next_priority'][:10]
            
        finally:
            session.close()
        
        return jsonify({
            'success': True,
            'collection_progress': progress_summary,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting collection progress: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@enhanced_data_api.route('/api/data/status/enhanced', methods=['GET'])
def enhanced_data_status():
    """Get enhanced data management system status."""
    try:
        # Get database statistics
        session = db_manager.get_session()
        
        try:
            # Count total OHLC records
            from sqlalchemy import text, func
            from database.models import CryptoOHLCData, CryptoDataSource
            
            total_records = session.query(func.count(CryptoOHLCData.id)).scalar() or 0
            total_sources = session.query(func.count(CryptoDataSource.id)).scalar() or 0
            
            # Get latest data timestamp
            latest_record = session.query(CryptoOHLCData).order_by(
                CryptoOHLCData.timestamp_utc.desc()
            ).first()
            
            latest_timestamp = None
            if latest_record:
                latest_timestamp = datetime.fromtimestamp(
                    latest_record.timestamp_utc / 1000000
                ).isoformat()
            
            # Get system stats
            system_stats = activity_data.get_system_stats()
            
        finally:
            session.close()
        
        status = {
            'enhanced_provider_available': BINANCE_AVAILABLE,
            'database_connected': True,
            'total_ohlc_records': total_records,
            'total_data_sources': total_sources,
            'latest_data_timestamp': latest_timestamp,
            'system_stats': system_stats,
            'capabilities': {
                'bulk_historical_fetch': BINANCE_AVAILABLE,
                'data_synchronization': BINANCE_AVAILABLE,
                'four_year_storage': True,
                'data_quality_analysis': True,
                'export_functionality': True
            }
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting enhanced data status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =======================
# ERROR HANDLERS
# =======================

@enhanced_data_api.errorhandler(404)
def not_found_enhanced(error):
    return jsonify({
        'success': False,
        'error': 'Enhanced data endpoint not found'
    }), 404

@enhanced_data_api.errorhandler(500)
def internal_error_enhanced(error):
    return jsonify({
        'success': False,
        'error': 'Enhanced data internal server error'
    }), 500