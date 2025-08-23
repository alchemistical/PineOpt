"""
Health Check Routes
Epic 7 Sprint 1 - Foundation & Consolidation

Provides system health monitoring and status endpoints.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
import os

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/v1/health')


@health_bp.route('/')
def basic_health():
    """
    Basic health check endpoint
    
    Returns:
        JSON response with basic system status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': current_app.config.get('API_VERSION', '1.0'),
        'epic': 'Epic 7 - API Rationalization'
    })


@health_bp.route('/detailed')
def detailed_health():
    """
    Detailed system health check
    
    Returns:
        JSON response with detailed system metrics
    """
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database health check
        database_status = check_database_health()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': current_app.config.get('API_VERSION', '1.0'),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'database': database_status,
            'environment': {
                'config': current_app.config.__class__.__name__,
                'debug': current_app.debug,
                'testing': current_app.testing
            }
        })
    except Exception as e:
        current_app.logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500


@health_bp.route('/metrics')
def metrics():
    """
    Performance metrics endpoint
    
    Returns:
        JSON response with API performance metrics
    """
    # TODO: Implement proper metrics collection in Sprint 3
    # For now, return basic placeholder metrics
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'epic': 'Epic 7 - API Architecture Rationalization',
        'metrics': {
            'requests_total': 0,  # Placeholder - implement in Sprint 2
            'requests_per_second': 0,  # Placeholder
            'average_response_time': 0,  # Placeholder
            'error_rate': 0,  # Placeholder
            'active_connections': 0  # Placeholder
        },
        'status': 'metrics_collection_not_yet_implemented'
    })


def check_database_health():
    """
    Check database connectivity and basic stats
    
    Returns:
        Dict with database health information
    """
    try:
        # Import database access here to avoid circular imports
        from backend.database.unified_data_access import UnifiedDataAccess
        
        da = UnifiedDataAccess()
        stats = da.get_database_stats()
        
        return {
            'status': 'healthy',
            'connection': 'ok',
            'records': {
                'market_data': stats.get('market_data_count', 0),
                'strategies': stats.get('strategies_count', 0),
                'market_tickers': stats.get('market_tickers_count', 0)
            }
        }
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'connection': 'failed',
            'error': str(e)
        }


# Route registration helper
def register_health_routes(app):
    """Register health check routes with the app"""
    app.register_blueprint(health_bp)
    app.logger.info("Health check routes registered")


if __name__ == '__main__':
    # For testing individual blueprint
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    
    print("Health routes available:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")