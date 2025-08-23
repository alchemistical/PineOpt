"""
Conversion Routes
Epic 7 Sprint 2 - Foundation & Middleware

Consolidates conversion endpoints from:
- ai_conversion_routes.py
- intelligent_conversion_routes.py  
- ai_analysis_routes.py

TODO Sprint 2 Tasks:
[ ] Migrate AI conversion endpoints
[ ] Migrate intelligent conversion endpoints
[ ] Migrate AI analysis endpoints
[ ] Add standardized error handling
[ ] Add response formatting
[ ] Add conversion progress tracking
[ ] Update frontend API calls
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
import logging
import sys
import os
from typing import Dict, Any, Optional

# Create blueprint
conversion_bp = Blueprint('conversions', __name__, url_prefix='/api/v1/conversions')

# Global instances (will be lazy-loaded)
analyzer = None
converter = None
strategy_db = None

def get_analyzer():
    """Get or create AI analyzer instance"""
    global analyzer
    if analyzer is None:
        try:
            # Add project root to path
            root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from research.analysis.ai_strategy_analyzer import AIStrategyAnalyzer
            analyzer = AIStrategyAnalyzer()
            current_app.logger.info("AI Strategy Analyzer initialized")
        except ImportError as e:
            current_app.logger.warning(f"AI Analyzer not available: {e}")
            analyzer = None
    return analyzer

def get_converter():
    """Get or create PyneScript converter instance"""
    global converter
    if converter is None:
        try:
            # Add project root to path
            root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from research.intelligent_converter.intelligent_converter_fixed import IntelligentConverter
            converter = IntelligentConverter()
            current_app.logger.info(f"PyneScript Converter initialized")
        except ImportError as e:
            current_app.logger.warning(f"Intelligent Converter not available: {e}")
            converter = None
    return converter

def get_strategy_db():
    """Get or create strategy database instance"""
    global strategy_db
    if strategy_db is None:
        try:
            # Add project root to path
            root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from database.strategy_models import StrategyDatabase
            strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
            current_app.logger.info("Strategy Database initialized")
        except ImportError as e:
            current_app.logger.warning(f"Strategy Database not available: {e}")
            strategy_db = None
    return strategy_db


@conversion_bp.route('/')
def conversion_info():
    """
    Conversion API information
    
    Returns:
        JSON response with available conversion endpoints
    """
    return jsonify({
        'api': 'Conversion Management API',
        'version': '1.0.0',
        'epic': 'Epic 7 Sprint 2 - Middleware & Advanced Features',
        'endpoints': {
            'health': 'GET /api/v1/conversions/health',
            'analyze': 'POST /api/v1/conversions/analyze',
            'convert_working': 'POST /api/v1/conversions/convert/working',
            'convert_hye': 'POST /api/v1/conversions/convert/hye',
            'convert_strategy': 'POST /api/v1/conversions/convert/strategy/<id>',
            'test_conversion': 'POST /api/v1/conversions/test',
            'indicators': 'GET /api/v1/conversions/indicators',
            'progress': 'GET /api/v1/conversions/progress/<task_id>'
        },
        'status': 'Sprint 2 - Implementation in progress',
        'consolidates': [
            'ai_conversion_routes.py',
            'intelligent_conversion_routes.py',
            'ai_analysis_routes.py'
        ]
    })


@conversion_bp.route('/health', methods=['GET'])
def health_check():
    """
    Conversion service health check
    
    Returns:
        JSON response with service status and capabilities
    """
    try:
        # Check service availability
        analyzer_available = get_analyzer() is not None
        converter_available = get_converter() is not None
        db_available = get_strategy_db() is not None
        
        capabilities = []
        if analyzer_available:
            capabilities.extend([
                'ai_strategy_analysis',
                'parameter_extraction',
                'indicator_detection'
            ])
        if converter_available:
            capabilities.extend([
                'pine_to_python_conversion',
                'hye_strategy_conversion',
                'working_strategy_generation'
            ])
        if db_available:
            capabilities.append('strategy_persistence')
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'service': 'Conversion Management',
            'status': 'healthy',
            'services': {
                'ai_analyzer': 'available' if analyzer_available else 'unavailable',
                'intelligent_converter': 'available' if converter_available else 'unavailable',
                'strategy_database': 'available' if db_available else 'unavailable'
            },
            'capabilities': capabilities
        })
    
    except Exception as e:
        current_app.logger.error(f"Conversion health check failed: {e}")
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@conversion_bp.route('/analyze', methods=['POST'])
def analyze_strategy():
    """
    Perform AI analysis on Pine Script strategy
    
    Request Body:
        {
            "pine_code": "Pine Script code",
            "strategy_name": "Optional strategy name",
            "analysis_type": "general|hye|detailed"
        }
    
    Returns:
        JSON response with analysis results
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({
                'error': 'pine_code is required in request body',
                'status': 'error'
            }), 400
        
        pine_code = data['pine_code']
        strategy_name = data.get('strategy_name', 'Unnamed Strategy')
        analysis_type = data.get('analysis_type', 'general')
        
        # Get analyzer
        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({
                'error': 'AI analysis service not available',
                'status': 'error'
            }), 503
        
        # Perform analysis
        current_app.logger.info(f"Starting {analysis_type} analysis for: {strategy_name}")
        
        if analysis_type == 'hye':
            # Use specialized HYE analyzer if available
            try:
                root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
                if root_path not in sys.path:
                    sys.path.append(root_path)
                
                from research.ai_analysis.advanced_hye_analyzer import HYEStrategyAnalyzer
                hye_analyzer = HYEStrategyAnalyzer()
                analysis_result = hye_analyzer.analyze_hye_strategy(pine_code, strategy_name)
            except ImportError:
                # Fallback to general analysis
                analysis_result = analyzer.analyze_pine_script(pine_code, strategy_name)
        else:
            # General analysis
            analysis_result = analyzer.analyze_pine_script(pine_code, strategy_name)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'strategy_name': strategy_name,
            'analysis_type': analysis_type,
            'analysis_result': analysis_result,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Strategy analysis failed: {e}")
        return jsonify({
            'error': 'Failed to analyze strategy',
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/convert/working', methods=['POST'])
def convert_working_strategy():
    """
    Convert Pine Script to working Python strategy that generates real signals
    
    Request Body:
        {
            "pine_code": "Pine Script code",
            "strategy_name": "Optional strategy name",
            "save_to_db": true
        }
    
    Returns:
        JSON response with converted Python code and metadata
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
        save_to_db = data.get('save_to_db', False)
        
        # Get converter
        converter = get_converter()
        if not converter:
            return jsonify({
                'error': 'Intelligent conversion service not available',
                'status': 'error'
            }), 503
        
        # Perform conversion
        current_app.logger.info(f"Converting working strategy: {strategy_name}")
        
        conversion_result = converter.convert_to_working_strategy(
            pine_code=pine_code,
            strategy_name=strategy_name
        )
        
        # Save to database if requested
        strategy_id = None
        if save_to_db and conversion_result.get('success'):
            try:
                strategy_db = get_strategy_db()
                if strategy_db:
                    # Save converted strategy to database
                    from .db_helper import get_database_access
                    da = get_database_access()
                    strategy_id = da.save_strategy(
                        name=strategy_name,
                        pine_script=pine_code,
                        python_code=conversion_result.get('python_code', ''),
                        description='AI-converted working strategy',
                        status='converted'
                    )
                    current_app.logger.info(f"Saved converted strategy with ID: {strategy_id}")
            except Exception as e:
                current_app.logger.warning(f"Failed to save to database: {e}")
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'strategy_name': strategy_name,
            'strategy_id': strategy_id,
            'conversion_result': conversion_result,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Working strategy conversion failed: {e}")
        return jsonify({
            'error': 'Failed to convert strategy',
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/convert/hye', methods=['POST'])
def convert_hye_strategy():
    """
    Convert HYE-specific Pine Script to Python strategy
    
    Request Body:
        {
            "pine_code": "Pine Script code",
            "strategy_name": "Optional strategy name",
            "save_to_db": true
        }
    
    Returns:
        JSON response with converted HYE strategy
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({
                'error': 'pine_code is required in request body',
                'status': 'error'
            }), 400
        
        pine_code = data['pine_code']
        strategy_name = data.get('strategy_name', 'HYE Converted Strategy')
        save_to_db = data.get('save_to_db', False)
        
        # Get converter
        converter = get_converter()
        if not converter:
            return jsonify({
                'error': 'Intelligent conversion service not available',
                'status': 'error'
            }), 503
        
        # Perform HYE-specific conversion
        current_app.logger.info(f"Converting HYE strategy: {strategy_name}")
        
        conversion_result = converter.convert_hye_strategy(
            pine_code=pine_code,
            strategy_name=strategy_name
        )
        
        # Save to database if requested
        strategy_id = None
        if save_to_db and conversion_result.get('success'):
            try:
                from .db_helper import get_database_access
                da = get_database_access()
                strategy_id = da.save_strategy(
                    name=strategy_name,
                    pine_script=pine_code,
                    python_code=conversion_result.get('python_code', ''),
                    description='AI-converted HYE strategy',
                    status='converted'
                )
                current_app.logger.info(f"Saved HYE strategy with ID: {strategy_id}")
            except Exception as e:
                current_app.logger.warning(f"Failed to save to database: {e}")
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'strategy_name': strategy_name,
            'strategy_id': strategy_id,
            'conversion_result': conversion_result,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"HYE strategy conversion failed: {e}")
        return jsonify({
            'error': 'Failed to convert HYE strategy',
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/convert/strategy/<int:strategy_id>', methods=['POST'])
def convert_existing_strategy(strategy_id):
    """
    Convert existing strategy from database
    
    Path Parameters:
        strategy_id: Strategy ID from database
    
    Request Body:
        {
            "conversion_type": "working|hye|enhanced",
            "save_result": true
        }
    
    Returns:
        JSON response with conversion results
    """
    try:
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
        
        data = request.get_json() or {}
        conversion_type = data.get('conversion_type', 'working')
        save_result = data.get('save_result', False)
        
        # Get converter
        converter = get_converter()
        if not converter:
            return jsonify({
                'error': 'Intelligent conversion service not available',
                'status': 'error'
            }), 503
        
        # Perform conversion based on type
        current_app.logger.info(f"Converting existing strategy {strategy_id} as {conversion_type}")
        
        pine_code = strategy.get('pine_script', '')
        if not pine_code:
            return jsonify({
                'error': 'Strategy has no Pine Script code to convert',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 400
        
        if conversion_type == 'hye':
            conversion_result = converter.convert_hye_strategy(
                pine_code=pine_code,
                strategy_name=strategy['name']
            )
        else:  # working or enhanced
            conversion_result = converter.convert_to_working_strategy(
                pine_code=pine_code,
                strategy_name=strategy['name']
            )
        
        # Update strategy with conversion result if requested
        if save_result and conversion_result.get('success'):
            try:
                updated_strategy = da.save_strategy(
                    name=strategy['name'],
                    pine_script=pine_code,
                    python_code=conversion_result.get('python_code', ''),
                    description=strategy.get('description', '') + f' (Converted: {conversion_type})',
                    status='converted'
                )
                current_app.logger.info(f"Updated strategy {strategy_id} with conversion result")
            except Exception as e:
                current_app.logger.warning(f"Failed to update strategy: {e}")
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'strategy_id': strategy_id,
            'strategy_name': strategy['name'],
            'conversion_type': conversion_type,
            'conversion_result': conversion_result,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Existing strategy conversion failed: {e}")
        return jsonify({
            'error': 'Failed to convert existing strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/test', methods=['POST'])
def test_conversion():
    """
    Test conversion capabilities without saving
    
    Request Body:
        {
            "pine_code": "Simple Pine Script for testing",
            "test_type": "syntax|conversion|full"
        }
    
    Returns:
        JSON response with test results
    """
    try:
        data = request.get_json()
        
        if not data or 'pine_code' not in data:
            return jsonify({
                'error': 'pine_code is required in request body',
                'status': 'error'
            }), 400
        
        pine_code = data['pine_code']
        test_type = data.get('test_type', 'syntax')
        
        # Get converter and analyzer
        converter = get_converter()
        analyzer = get_analyzer()
        
        test_results = {
            'converter_available': converter is not None,
            'analyzer_available': analyzer is not None,
            'pine_code_length': len(pine_code),
            'test_type': test_type
        }
        
        if test_type in ['syntax', 'full']:
            # Basic syntax validation
            test_results['syntax_check'] = {
                'has_strategy_declaration': 'strategy(' in pine_code,
                'has_version_declaration': '//@version' in pine_code or 'version=' in pine_code,
                'estimated_complexity': 'simple' if len(pine_code) < 1000 else 'complex'
            }
        
        if test_type in ['conversion', 'full'] and converter:
            # Test basic conversion capability
            try:
                test_results['conversion_test'] = {
                    'service_available': True,
                    'test_status': 'ready_for_conversion'
                }
            except Exception as e:
                test_results['conversion_test'] = {
                    'service_available': False,
                    'error': str(e)
                }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'test_results': test_results,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Conversion test failed: {e}")
        return jsonify({
            'error': 'Failed to test conversion',
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/indicators', methods=['GET'])
def get_supported_indicators():
    """
    Get list of supported indicators for conversion
    
    Returns:
        JSON response with supported indicators and their capabilities
    """
    try:
        # Static list of supported indicators (could be dynamic based on converter capabilities)
        supported_indicators = {
            'trend_indicators': [
                'sma', 'ema', 'wma', 'vwma', 'swma',
                'rma', 'alma', 'smma', 'hma', 'tema'
            ],
            'momentum_indicators': [
                'rsi', 'stoch', 'stochrsi', 'cci', 'mfi',
                'tsi', 'uo', 'ao', 'roc', 'mom'
            ],
            'volume_indicators': [
                'volume', 'vwap', 'ad', 'obv', 'cmf', 'fi', 'nvi', 'pvi'
            ],
            'volatility_indicators': [
                'atr', 'natr', 'tr', 'bb', 'kc', 'dc'
            ],
            'custom_indicators': [
                'tsv', 'vidya', 'hye_vwap', 'leadline'
            ]
        }
        
        # Get converter status
        converter = get_converter()
        conversion_status = 'available' if converter else 'unavailable'
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 2',
            'conversion_service': conversion_status,
            'supported_indicators': supported_indicators,
            'total_indicators': sum(len(indicators) for indicators in supported_indicators.values()),
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Failed to get supported indicators: {e}")
        return jsonify({
            'error': 'Failed to get supported indicators',
            'message': str(e),
            'status': 'error'
        }), 500


@conversion_bp.route('/progress/<task_id>', methods=['GET'])
def get_conversion_progress(task_id):
    """
    Get progress of a long-running conversion task
    
    Path Parameters:
        task_id: Task ID returned from conversion request
    
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
                'message': 'Task progress tracking will be implemented in Sprint 2 middleware',
                'percentage': 0
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Failed to get conversion progress: {e}")
        return jsonify({
            'error': 'Failed to get conversion progress',
            'task_id': task_id,
            'message': str(e),
            'status': 'error'
        }), 500


# Route registration helper
def register_conversion_routes(app):
    """Register conversion routes with the app"""
    app.register_blueprint(conversion_bp)
    app.logger.info("Conversion routes registered")


if __name__ == '__main__':
    # For testing individual blueprint
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(conversion_bp)
    
    print("Conversion routes available:")
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/v1/conversions'):
            print(f"  {rule.methods} {rule.rule}")


"""
SPRINT 2 DEVELOPMENT NOTES:

CONSOLIDATION CHECKLIST:
[ ] Review original ai_conversion_routes.py for missing functionality
[ ] Review original intelligent_conversion_routes.py for missing functionality  
[ ] Review original ai_analysis_routes.py for missing functionality
[ ] Add conversion progress tracking and status updates
[ ] Add proper input validation (Sprint 2 middleware)
[ ] Add authentication/authorization (Sprint 2 middleware)
[ ] Update frontend components to use new endpoints
[ ] Add comprehensive error handling
[ ] Add task queue for long-running conversions
[ ] Add OpenAPI documentation (Sprint 3)

TESTING CHECKLIST:
[ ] Unit tests for each endpoint
[ ] Integration tests with conversion services
[ ] Conversion accuracy tests
[ ] Error handling tests
[ ] Performance tests for large Pine Scripts
[ ] Task progress tracking tests

MIGRATION NOTES:
- This blueprint replaces ai_conversion_routes.py, intelligent_conversion_routes.py, ai_analysis_routes.py
- All endpoints now under /api/v1/conversions/ prefix
- Standardized response format with timestamp, epic, status
- Uses unified database access layer
- Error responses include error type and message
- Lazy loading of conversion services for better performance

FRONTEND UPDATE REQUIREMENTS:
- Update all conversion API calls to use /api/v1/conversions/
- Handle new response format (with timestamp, epic, status)
- Update error handling for new error format
- Test conversion workflows with new endpoints
"""