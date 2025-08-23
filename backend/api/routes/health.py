"""
Health Check Routes
Epic 7 Sprint 1 - Foundation & Consolidation

Provides system health monitoring and status endpoints.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
import os

try:
    from ..utils.response_formatter import health_response, success_response, error_response
except ImportError:
    from utils.response_formatter import health_response, success_response, error_response

# Create blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/v1/health')


@health_bp.route('/')
def basic_health():
    """
    Basic health check endpoint
    
    Returns:
        JSON response with basic system status
    """
    return health_response(
        service_name='PineOpt API',
        status='healthy',
        version=current_app.config.get('API_VERSION', '1.0')
    )


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
        
        health_checks = {
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
        }
        
        return health_response(
            service_name='PineOpt API',
            status='healthy',
            checks=health_checks,
            version=current_app.config.get('API_VERSION', '1.0')
        )
    except Exception as e:
        current_app.logger.error(f"Detailed health check failed: {e}")
        return error_response(
            'health_check_failed',
            'Detailed health check failed',
            500,
            details=str(e)
        )


@health_bp.route('/metrics')
def metrics():
    """
    Performance metrics endpoint
    
    Returns:
        JSON response with API performance metrics
    """
    # TODO: Implement proper metrics collection in Sprint 3
    # For now, return basic placeholder metrics
    
    metrics_data = {
        'requests_total': 0,  # Placeholder - implement in Sprint 3
        'requests_per_second': 0,  # Placeholder
        'average_response_time': 0,  # Placeholder
        'error_rate': 0,  # Placeholder
        'active_connections': 0  # Placeholder
    }
    
    return success_response(
        data=metrics_data,
        message='Metrics collection will be implemented in Sprint 3'
    )


def check_database_health():
    """
    Check database connectivity and basic stats
    
    Returns:
        Dict with database health information
    """
    try:
        # Import database access here to avoid circular imports
        from .db_helper import get_database_access
        da = get_database_access()
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