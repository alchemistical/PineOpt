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
            'list': 'GET /api/v1/strategies',
            'create': 'POST /api/v1/strategies',
            'get': 'GET /api/v1/strategies/<id>',
            'update': 'PUT /api/v1/strategies/<id>',
            'delete': 'DELETE /api/v1/strategies/<id>',
            'parameters': 'GET /api/v1/strategies/<id>/parameters'
        },
        'status': 'Sprint 1 - Implementation in progress',
        'consolidates': [
            'strategy_routes.py',
            'parameter_routes.py'
        ]
    })


@strategy_bp.route('/', methods=['GET'])
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
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
        
        # Create strategy
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
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
        
        # Update strategy with provided fields
        updated_id = da.save_strategy(
            name=existing_strategy['name'],  # Keep existing if not provided
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Check if strategy exists
        strategy = da.get_strategy(strategy_id=strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # Delete strategy
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
        from backend.database.unified_data_access import UnifiedDataAccess
        da = UnifiedDataAccess()
        
        # Check if strategy exists
        strategy = da.get_strategy(strategy_id=strategy_id)
        if not strategy:
            return jsonify({
                'error': 'Strategy not found',
                'strategy_id': strategy_id,
                'status': 'error'
            }), 404
        
        # TODO: Implement parameter retrieval from database
        # For now, return placeholder
        parameters = []  # da.get_strategy_parameters(strategy_id)
        
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