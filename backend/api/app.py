"""
PineOpt Flask Application Factory
Epic 7 - API Architecture Rationalization
Created for Sprint 1 implementation

This is the main Flask application factory following modern patterns.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Import blueprints - Epic 7 implementation
try:
    # Try relative import first (when used as module)
    from .routes.health import health_bp
    from .routes.market_data import market_bp
    from .routes.strategies import strategy_bp
    from .routes.conversions import conversion_bp  # Sprint 2
    from .routes.backtests import backtest_bp     # Sprint 2
    from .routes.monitoring import monitoring_bp   # Sprint 3
except ImportError:
    # Fall back to absolute import (when run directly)
    from routes.health import health_bp
    from routes.market_data import market_bp
    from routes.strategies import strategy_bp
    from routes.conversions import conversion_bp  # Sprint 2
    from routes.backtests import backtest_bp     # Sprint 2
    from routes.monitoring import monitoring_bp   # Sprint 3

# Import middleware - Sprint 2 ACTIVE
try:
    # Try relative import first (when used as module)
    from .middleware import init_error_handlers, init_rate_limiting, init_logging, init_cors
except ImportError:
    # Fall back to absolute import (when run directly)
    from middleware import init_error_handlers, init_rate_limiting, init_logging, init_cors


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'epic-7-dev-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///backend/database/pineopt_unified.db'
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    API_PORT = int(os.environ.get('API_PORT', 5007))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173')
    
    # Rate Limiting Configuration
    ENABLE_RATE_LIMITING = os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    GLOBAL_RATE_LIMIT_PER_MINUTE = int(os.environ.get('GLOBAL_RATE_LIMIT_PER_MINUTE', 100))
    GLOBAL_RATE_LIMIT_PER_HOUR = int(os.environ.get('GLOBAL_RATE_LIMIT_PER_HOUR', 2000))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""  
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def create_app(config_name='default'):
    """
    Flask Application Factory
    
    Args:
        config_name: Configuration environment ('development', 'production', 'testing')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Configure basic logging (enhanced by middleware)
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize production middleware - Sprint 2 ACTIVE
    init_error_handlers(app)
    init_rate_limiting(app)
    init_logging(app)
    init_cors(app)  # This replaces the basic CORS setup above
    
    # Register blueprints (Sprint 1)
    register_blueprints(app)
    
    # Add basic health check (temporary)
    @app.route('/api/health')
    def basic_health():
        """Temporary health check - will be moved to health blueprint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config['API_VERSION'],
            'epic': 'Epic 7 - API Rationalization In Progress'
        })
    
    # Add API info endpoint
    @app.route('/api')
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': 'PineOpt API',
            'version': app.config['API_VERSION'],
            'prefix': app.config['API_PREFIX'],
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'Under Development',
            'documentation': {
                'interactive': '/docs/',
                'swagger_ui': '/docs/swagger',
                'openapi_spec': '/docs/openapi.json'
            },
            'endpoints': {
                'health': '/api/health',
                'market': f"{app.config['API_PREFIX']}/market",
                'strategies': f"{app.config['API_PREFIX']}/strategies",
                'conversions': f"{app.config['API_PREFIX']}/conversions",
                'backtests': f"{app.config['API_PREFIX']}/backtests",
                'monitoring': f"{app.config['API_PREFIX']}/monitoring"
            }
        })
    
    # Initialize interactive documentation - Sprint 3 Task 2
    try:
        from docs.doc_generator import create_interactive_docs
        create_interactive_docs(app, route_prefix="/docs")
        app.logger.info("📚 Interactive API documentation available at /docs/")
    except ImportError as e:
        app.logger.warning(f"Documentation system not available: {e}")
    
    return app


def register_blueprints(app):
    """
    Register all API blueprints
    
    Sprint 1: Health, Market Data, Strategy blueprints
    Sprint 2: Conversion, Backtest blueprints
    """
    # Sprint 1 blueprints - ACTIVE
    app.register_blueprint(health_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(strategy_bp)
    
    # Sprint 2 blueprints - NOW ACTIVE
    app.register_blueprint(conversion_bp)
    app.register_blueprint(backtest_bp)
    
    # Sprint 3 blueprints - NOW ACTIVE  
    app.register_blueprint(monitoring_bp)
    
    app.logger.info("Epic 7 Sprint 3 blueprints registered successfully")
    app.logger.info("  ✅ Health check routes: /api/v1/health/")
    app.logger.info("  ✅ Market data routes: /api/v1/market/")
    app.logger.info("  ✅ Strategy routes: /api/v1/strategies/")
    app.logger.info("  ✅ Conversion routes: /api/v1/conversions/")
    app.logger.info("  ✅ Backtest routes: /api/v1/backtests/")
    app.logger.info("  ✅ Monitoring routes: /api/v1/monitoring/")


if __name__ == '__main__':
    """Development server entry point"""
    app = create_app('development')
    port = app.config['API_PORT']
    
    print(f"""
🚀 PineOpt API Server Starting
Epic 7: API Architecture Rationalization
    
Server Info:
  • Environment: {app.config.__class__.__name__}
  • Port: {port}
  • Debug: {app.debug}
  • Database: {app.config['DATABASE_URL']}
  
API Endpoints:
  • Health Check: http://localhost:{port}/api/health
  • API Info: http://localhost:{port}/api
  
Epic 7 Progress:
  ✅ Sprint 1: Blueprint consolidation complete
  ✅ Sprint 2: Conversion & production middleware complete
  ⏳ Sprint 3: Documentation & testing planned

Ready for development! 🎯
""")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.debug
    )