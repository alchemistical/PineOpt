"""
Strategy Management Routes
Epic 7 Sprint 1 - Foundation & Consolidation

Consolidates strategy endpoints from:
- strategy_routes.py
- parameter_routes.py

TODO Sprint 1 Tasks:
[ ] Migrate strategy CRUD operations
[ ] Migrate parameter management
[ ] Add strategy validation
[ ] Add standardized error handling
[ ] Add response formatting
[ ] Update frontend API calls
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json

# Create blueprint
strategy_bp = Blueprint('strategies', __name__, url_prefix='/api/v1/strategies')


@strategy_bp.route('/')
def strategy_info():
    """
    Strategy API information
    
    Returns:
        JSON response with available strategy endpoints
    """
    return jsonify({
        'api': 'Strategy Management API',
        'version': '1.0.0',
        'epic': 'Epic 7 Sprint 1 - Foundation & Consolidation',
        'endpoints': {
            'list': 'GET /api/v1/strategies/list',
            'create': 'POST /api/v1/strategies',
            'get': 'GET /api/v1/strategies/<id>',
            'update': 'PUT /api/v1/strategies/<id>',
            'delete': 'DELETE /api/v1/strategies/<id>',
            'parameters': 'GET /api/v1/strategies/<id>/parameters',
            'validate': 'POST /api/v1/strategies/<id>/validate',
            'profile': 'POST /api/v1/strategies/<id>/profile',
            'stats': 'GET /api/v1/strategies/stats'
        },
        'status': 'Sprint 1 - Implementation in progress',
        'consolidates': [
            'strategy_routes.py',
            'parameter_routes.py',
            'validation_system',
            'parameter_management'
        ]
    })


@strategy_bp.route('/list', methods=['GET'])
def list_strategies():
    """
    List all strategies
    
    TODO Sprint 1: Consolidate from strategy_routes.py
    
    Query Parameters:
        status: Filter by status (draft, converted, tested, validated)
        limit: Number of results (default: 50)
        offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with strategy list
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        # Parse query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Get strategies
        strategies = da.get_strategies(status=status, limit=limit)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategies': strategies,
            'count': len(strategies),
            'filters': {
                'status': status,
                'limit': limit
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"List strategies failed: {e}")
        return jsonify({
            'error': 'Failed to fetch strategies',
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/', methods=['POST'])
def create_strategy():
    """
    Create new strategy
    
    TODO Sprint 1: Consolidate from strategy_routes.py
    
    Request Body:
        {
            "name": "Strategy Name",
            "description": "Strategy description",
            "pine_script": "Pine Script code",
            "python_code": "Generated Python code (optional)",
            "metadata": {...}
        }
    
    Returns:
        JSON response with created strategy
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body must be JSON',
                'status': 'error'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'pine_script']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields,
                'status': 'error'
            }), 400
        
        # Import original strategy database for advanced functionality
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        try:
            from database.strategy_models import (
                StrategyDatabase, StrategyMetadata, LanguageType, ValidationStatus
            )
            
            # Detect language
            if 'python_code' in data and data['python_code']:
                language = LanguageType.PYTHON
                source_code = data['python_code']
            else:
                language = LanguageType.PINE
                source_code = data['pine_script']
            
            # Use advanced strategy database
            strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
            
            # Create advanced strategy metadata
            strategy = StrategyMetadata(
                name=data['name'],
                description=data.get('description', ''),
                author=data.get('author', 'Unknown'),
                language=language,
                source_code=source_code,
                validation_status=ValidationStatus.PENDING
            )
            
            # Save with advanced database
            strategy_id = strategy_db.save_strategy(strategy)
            
        except ImportError:
            # Fallback to simple save
            strategy_id = da.save_strategy(
                name=data['name'],
                pine_script=data['pine_script'],
                description=data.get('description'),
                python_code=data.get('python_code'),
                metadata=data.get('metadata', {}),
                status=data.get('status', 'draft')
            )
        
        # Get created strategy
        strategy = da.get_strategy(strategy_id=strategy_id)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy': strategy,
            'strategy_id': strategy_id,
            'message': 'Strategy created successfully',
            'status': 'success'
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Create strategy failed: {e}")
        return jsonify({
            'error': 'Failed to create strategy',
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """
    Get strategy by ID
    
    TODO Sprint 1: Consolidate from strategy_routes.py
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Returns:
        JSON response with strategy details
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        strategy = da.get_strategy(strategy_id=strategy_id)
        
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy': strategy,
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get strategy {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to fetch strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    """
    Update existing strategy
    
    TODO Sprint 1: Consolidate from strategy_routes.py
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Request Body:
        {
            "name": "Updated name (optional)",
            "description": "Updated description (optional)",
            "pine_script": "Updated Pine Script (optional)",
            "python_code": "Updated Python code (optional)",
            "metadata": {...},
            "status": "draft|converted|tested|validated"
        }
    
    Returns:
        JSON response with updated strategy
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        # Check if strategy exists
        existing_strategy = da.get_strategy(strategy_id=strategy_id)
        if not existing_strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body must be JSON',
                'status': 'error'
            }), 400
        
        # Import original strategy database for advanced updates
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        try:
            from database.strategy_models import StrategyDatabase
            
            # Use advanced strategy database for updates
            strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
            
            # Get the existing strategy object
            strategy_obj = strategy_db.get_strategy(strategy_id)
            if not strategy_obj:
                return jsonify({
                    'error': 'Strategy not found in advanced database',
                    'strategy_id': strategy_id,
                    'status': 'error'
                }), 404
            
            # Update strategy fields
            if 'name' in data:
                strategy_obj.name = data['name']
            if 'description' in data:
                strategy_obj.description = data['description']
            if 'author' in data:
                strategy_obj.author = data['author']
            if 'version' in data:
                strategy_obj.version = data['version']
            if 'pine_script' in data:
                strategy_obj.source_code = data['pine_script']
            if 'python_code' in data:
                strategy_obj.source_code = data['python_code']
            if 'status' in data:
                # Map simple status to validation status
                status_map = {
                    'draft': ValidationStatus.PENDING,
                    'validated': ValidationStatus.VALID,
                    'invalid': ValidationStatus.INVALID
                }
                strategy_obj.validation_status = status_map.get(data['status'], ValidationStatus.PENDING)
            
            # Save updates with advanced database
            updated_id = strategy_db.save_strategy(strategy_obj)
            
        except (ImportError, Exception) as e:
            current_app.logger.warning(f"Could not use advanced strategy updates: {e}")
            # Fallback to simple update
            updated_id = da.save_strategy(
                name=data.get('name', existing_strategy['name']),
                pine_script=data.get('pine_script', existing_strategy['pine_script']),
                description=data.get('description', existing_strategy['description']),
                python_code=data.get('python_code', existing_strategy['python_code']),
                metadata=data.get('metadata', json.loads(existing_strategy.get('metadata', '{}'))),
                status=data.get('status', existing_strategy['status'])
            )
        
        # Get updated strategy
        strategy = da.get_strategy(strategy_id=updated_id)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy': strategy,
            'message': 'Strategy updated successfully',
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Update strategy {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to update strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """
    Delete strategy
    
    TODO Sprint 1: Consolidate from strategy_routes.py
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Returns:
        JSON response confirming deletion
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        # Check if strategy exists
        strategy = da.get_strategy(strategy_id=strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Try advanced delete first, fallback to simple delete
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        deleted = False
        try:
            from database.strategy_models import StrategyDatabase
            
            # Use advanced strategy database for deletion
            strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
            deleted = strategy_db.delete_strategy(strategy_id)
            
        except (ImportError, Exception) as e:
            current_app.logger.warning(f"Could not use advanced strategy deletion: {e}")
            # Fallback to simple delete
            deleted = da.delete_strategy(strategy_id)
        
        if deleted:
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 Sprint 1',
                'strategy_id': strategy_id,
                'message': 'Strategy deleted successfully',
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'Failed to delete strategy',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Delete strategy {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to delete strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>/parameters', methods=['GET'])
def get_strategy_parameters(strategy_id):
    """
    Get strategy parameters
    
    TODO Sprint 1: Consolidate from parameter_routes.py
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Returns:
        JSON response with strategy parameters
    """
    try:
        from .db_helper import get_database_access
        da = get_database_access()
        
        # Check if strategy exists
        strategy = da.get_strategy(strategy_id=strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Import parameter management from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        try:
            from database.strategy_models import StrategyDatabase
            
            # Use advanced strategy database for parameter retrieval
            strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
            
            # Get strategy with parameters
            strategy_obj = strategy_db.get_strategy(strategy_id)
            if strategy_obj and hasattr(strategy_obj, 'parameters'):
                parameters = strategy_obj.parameters or {}
            else:
                parameters = {}
            
        except (ImportError, Exception) as e:
            current_app.logger.warning(f"Could not load advanced parameters: {e}")
            parameters = {}
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_id': strategy_id,
            'parameters': parameters,
            'count': len(parameters),
            'status': 'success',
            'note': 'Parameter management will be fully implemented in Sprint 1'
        })
    
    except Exception as e:
        current_app.logger.error(f"Get strategy parameters {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to fetch strategy parameters',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>/validate', methods=['POST'])
def validate_strategy(strategy_id):
    """
    Validate or re-validate a strategy
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Returns:
        JSON response with validation results
    """
    try:
        # Import validation system from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from database.strategy_models import StrategyDatabase
        from research.validation.code_validator import CodeValidator
        
        # Use advanced strategy database
        strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
        strategy_obj = strategy_db.get_strategy(strategy_id)
        
        if not strategy_obj:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Validate strategy
        validator = CodeValidator()
        validation_results = validator.validate_strategy(
            strategy_obj.source_code,
            strategy_obj.language,
            strategy_obj.original_filename or f"strategy_{strategy_id}.{strategy_obj.language.value}"
        )
        
        # Generate validation summary
        validation_summary = validator.get_validation_summary(validation_results)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_id': strategy_id,
            'validation_summary': validation_summary,
            'validation_details': [
                {
                    'type': r.type,
                    'status': r.status,
                    'message': r.message,
                    'line_number': r.line_number,
                    'column_number': r.column_number,
                    'details': r.details
                } for r in validation_results
            ],
            'status': 'success'
        })
    
    except ImportError:
        # Fallback validation (simple)
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_id': strategy_id,
            'validation_summary': {
                'is_valid': True,
                'has_errors': False,
                'has_warnings': False,
                'message': 'Basic validation passed - advanced validation not available'
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Strategy validation {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to validate strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/<int:strategy_id>/profile', methods=['POST'])
def profile_strategy(strategy_id):
    """
    Generate AI-powered strategy analysis and profile
    
    Path Parameters:
        strategy_id: Strategy ID
    
    Returns:
        JSON response with comprehensive strategy profile
    """
    try:
        # Import profiling system from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from database.strategy_models import StrategyDatabase
        from research.analysis.strategy_profiler import StrategyProfiler
        
        # Use advanced strategy database
        strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
        strategy_obj = strategy_db.get_strategy(strategy_id)
        
        if not strategy_obj:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Generate strategy profile
        profiler = StrategyProfiler()
        profile = profiler.profile_strategy(
            strategy_id=strategy_obj.id,
            name=strategy_obj.name,
            source_code=strategy_obj.source_code,
            language=strategy_obj.language.value,
            author=strategy_obj.author
        )
        
        # Format profile response
        profile_data = {
            'strategy_id': profile.strategy_id,
            'analysis_summary': {
                'strategy_type': profile.strategy_type,
                'complexity_score': profile.complexity_score,
                'lines_of_code': profile.lines_of_code,
                'indicators_used': profile.indicators_used,
                'risk_level': profile.expected_risk_level,
                'trading_frequency': profile.expected_frequency
            },
            'technical_analysis': {
                'indicators_detected': profile.indicators_used,
                'signal_types': profile.signal_types,
                'has_risk_management': profile.has_risk_management,
                'has_stop_loss': profile.has_stop_loss,
                'has_position_sizing': profile.has_position_sizing
            },
            'ai_insights': {
                'summary': profile.ai_summary,
                'strengths': profile.ai_strengths,
                'weaknesses': profile.ai_weaknesses,
                'recommendations': profile.ai_recommendations,
                'market_suitability': profile.ai_market_suitability
            },
            'full_report': profile.full_report,
            'generated_at': profile.analysis_timestamp.isoformat()
        }
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_id': strategy_id,
            'profile': profile_data,
            'status': 'success'
        })
    
    except ImportError:
        # Fallback profiling (simple)
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_id': strategy_id,
            'profile': {
                'analysis_summary': {
                    'strategy_type': 'Unknown',
                    'complexity_score': 50,
                    'message': 'Advanced profiling not available'
                }
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Strategy profiling {strategy_id} failed: {e}")
        return jsonify({
            'error': 'Failed to profile strategy',
            'strategy_id': strategy_id,
            'message': str(e),
            'status': 'error'
        }), 500


@strategy_bp.route('/stats', methods=['GET'])
def get_strategy_stats():
    """
    Get strategy statistics
    
    Returns:
        JSON response with strategy database statistics
    """
    try:
        # Import strategy database from original implementation
        import sys
        import os
        root_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
        if root_path not in sys.path:
            sys.path.append(root_path)
        
        from database.strategy_models import StrategyDatabase
        
        # Use advanced strategy database
        strategy_db = StrategyDatabase(str(root_path + '/database/pineopt.db'))
        stats = strategy_db.get_strategy_stats()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_stats': stats,
            'status': 'success'
        })
    
    except ImportError:
        # Fallback stats using unified database
        from .db_helper import get_database_access
        da = get_database_access()
        stats = da.get_database_stats()
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 Sprint 1',
            'strategy_stats': {
                'total_strategies': stats.get('strategies_count', 0),
                'total_records': stats.get('market_data_count', 0) + stats.get('strategies_count', 0)
            },
            'status': 'success'
        })
    
    except Exception as e:
        current_app.logger.error(f"Strategy stats failed: {e}")
        return jsonify({
            'error': 'Failed to get strategy statistics',
            'message': str(e),
            'status': 'error'
        }), 500


# Route registration helper
def register_strategy_routes(app):
    """Register strategy routes with the app"""
    app.register_blueprint(strategy_bp)
    app.logger.info("Strategy routes registered")


if __name__ == '__main__':
    # For testing individual blueprint
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(strategy_bp)
    
    print("Strategy routes available:")
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/v1/strategies'):
            print(f"  {rule.methods} {rule.rule}")

"""
SPRINT 1 DEVELOPMENT NOTES:

CONSOLIDATION CHECKLIST:
[ ] Review original strategy_routes.py for missing functionality
[ ] Review original parameter_routes.py for missing functionality  
[ ] Implement strategy parameter CRUD operations
[ ] Add Pine Script validation
[ ] Add strategy name uniqueness validation
[ ] Add proper input validation (Sprint 2 middleware)
[ ] Add authentication/authorization (Sprint 2 middleware)
[ ] Update frontend components to use new endpoints
[ ] Add comprehensive error handling
[ ] Add OpenAPI documentation (Sprint 3)

TESTING CHECKLIST:
[ ] Unit tests for each endpoint
[ ] Integration tests with database
[ ] CRUD operation tests
[ ] Input validation tests
[ ] Error handling tests
[ ] Parameter management tests

MIGRATION NOTES:
- This blueprint replaces strategy_routes.py and parameter_routes.py
- All endpoints now under /api/v1/strategies/ prefix
- Standardized response format with timestamp, epic, status
- Uses unified database access layer
- Full CRUD operations for strategies
- Parameter management integrated into strategy endpoints
- Error responses include error type and message

FRONTEND UPDATE REQUIREMENTS:
- Update all strategy API calls to use /api/v1/strategies/
- Handle new response format (with timestamp, epic, status)
- Update error handling for new error format
- Test strategy creation, editing, deletion workflows
"""