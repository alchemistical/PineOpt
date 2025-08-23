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

# Import blueprints (will be created in Sprint 1)
# from .routes.health import health_bp
# from .routes.market_data import market_bp
# from .routes.strategies import strategy_bp
# from .routes.conversions import conversion_bp
# from .routes.backtests import backtest_bp

# Import middleware (will be created in Sprint 2)  
# from .middleware.error_handling import init_error_handlers
# from .middleware.rate_limiting import init_rate_limiting
# from .middleware.logging import init_logging


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'epic-7-dev-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///backend/database/pineopt_unified.db'
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    API_PORT = int(os.environ.get('API_PORT', 5007))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
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
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize middleware (Sprint 2)
    # init_error_handlers(app)
    # init_rate_limiting(app)  
    # init_logging(app)
    
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
            'endpoints': {
                'health': '/api/health',
                'market': f"{app.config['API_PREFIX']}/market",
                'strategies': f"{app.config['API_PREFIX']}/strategies",
                'conversions': f"{app.config['API_PREFIX']}/conversions",
                'backtests': f"{app.config['API_PREFIX']}/backtests"
            }
        })
    
    return app


def register_blueprints(app):
    """
    Register all API blueprints
    
    This will be implemented in Sprint 1 as blueprints are created
    """
    # Sprint 1 blueprints
    # app.register_blueprint(health_bp)
    # app.register_blueprint(market_bp)
    # app.register_blueprint(strategy_bp)
    
    # Sprint 2 blueprints  
    # app.register_blueprint(conversion_bp)
    # app.register_blueprint(backtest_bp)
    
    app.logger.info("Blueprint registration completed")


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
  ✅ Application factory pattern implemented
  🔄 Sprint 1: Blueprint consolidation in progress
  ⏳ Sprint 2: Middleware implementation planned
  ⏳ Sprint 3: Documentation & testing planned

Ready for development! 🎯
""")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.debug
    )