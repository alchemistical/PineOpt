"""
CORS Middleware
Epic 7 Sprint 2 - Production Middleware

Provides enhanced CORS configuration with security controls.
"""

from flask import current_app, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class EnhancedCORS:
    """Enhanced CORS configuration with security controls"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CORS with security-focused configuration"""
        
        # Default CORS configuration
        cors_config = {
            'origins': self._get_allowed_origins(app),
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': [
                'Content-Type',
                'Authorization',
                'X-Requested-With',
                'X-Request-ID',
                'Accept',
                'Origin',
                'User-Agent'
            ],
            'expose_headers': [
                'X-Request-ID',
                'X-Response-Time',
                'X-RateLimit-Limit-Minute',
                'X-RateLimit-Remaining-Minute',
                'X-Total-Count'
            ],
            'supports_credentials': False,  # Security: disable credentials by default
            'max_age': 86400  # 24 hours
        }
        
        # Apply CORS configuration
        CORS(app, **cors_config)
        
        # Add CORS validation middleware
        app.before_request(self._validate_cors_request)
        
        # Add CORS info endpoint
        @app.route('/api/v1/cors/config')
        def cors_config_endpoint():
            """Get current CORS configuration"""
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 - API Architecture Rationalization',
                'status': 'success',
                'data': {
                    'cors_enabled': True,
                    'allowed_origins': cors_config['origins'],
                    'allowed_methods': cors_config['methods'],
                    'allowed_headers': cors_config['allow_headers'],
                    'exposed_headers': cors_config['expose_headers'],
                    'supports_credentials': cors_config['supports_credentials'],
                    'max_age': cors_config['max_age']
                }
            })
        
        logger.info("✅ Enhanced CORS middleware initialized")
        logger.info(f"  • Allowed origins: {cors_config['origins']}")
        logger.info(f"  • Credentials support: {cors_config['supports_credentials']}")
    
    def _get_allowed_origins(self, app):
        """Get allowed origins from configuration"""
        # Get from environment/config
        origins_str = app.config.get('CORS_ORIGINS', 'http://localhost:3000')
        
        if origins_str == '*':
            logger.warning("⚠️ CORS configured for all origins - not recommended for production")
            return '*'
        
        # Parse comma-separated origins
        origins = [origin.strip() for origin in origins_str.split(',')]
        
        # Validate origins format
        validated_origins = []
        for origin in origins:
            if self._is_valid_origin(origin):
                validated_origins.append(origin)
            else:
                logger.warning(f"⚠️ Invalid CORS origin format: {origin}")
        
        if not validated_origins:
            logger.warning("⚠️ No valid CORS origins configured, using localhost default")
            validated_origins = ['http://localhost:3000']
        
        return validated_origins
    
    def _is_valid_origin(self, origin):
        """Validate origin format"""
        if origin == '*':
            return True
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(origin))
    
    def _validate_cors_request(self):
        """Validate CORS requests for security"""
        # Skip validation for non-CORS requests
        origin = request.headers.get('Origin')
        if not origin:
            return None
        
        # Check if origin is explicitly blocked
        blocked_origins = current_app.config.get('CORS_BLOCKED_ORIGINS', [])
        if origin in blocked_origins:
            logger.warning(f"CORS request blocked from forbidden origin: {origin}")
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 - API Architecture Rationalization',
                'error': {
                    'type': 'cors_forbidden',
                    'message': 'Origin not allowed',
                    'status_code': 403
                },
                'status': 'error'
            }), 403
        
        # Log suspicious CORS patterns
        if self._is_suspicious_origin(origin):
            logger.warning(f"Suspicious CORS origin detected: {origin} - Path: {request.path}")
        
        return None
    
    def _is_suspicious_origin(self, origin):
        """Detect potentially suspicious origins"""
        suspicious_patterns = [
            r'.*\.tk$',  # .tk domains often used maliciously
            r'.*\.ml$',  # .ml domains often used maliciously
            r'.*\.ga$',  # .ga domains often used maliciously
            r'.*\.cf$',  # .cf domains often used maliciously
            r'localhost:\d{5,}',  # unusual high ports
            r'\d+\.\d+\.\d+\.\d+:\d{4,}',  # IP addresses with unusual ports
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, origin, re.IGNORECASE):
                return True
        
        return False


def cors_preflight_handler():
    """Handle CORS preflight requests explicitly"""
    def handle_preflight():
        if request.method == 'OPTIONS':
            # This is handled automatically by Flask-CORS
            # But we can add custom logic here if needed
            pass
    
    return handle_preflight


def init_cors(app):
    """Initialize enhanced CORS middleware"""
    
    # Set default CORS configuration if not set
    if 'CORS_ORIGINS' not in app.config:
        if app.config.get('ENV') == 'development':
            app.config['CORS_ORIGINS'] = 'http://localhost:3000,http://localhost:5173'
        else:
            app.config['CORS_ORIGINS'] = ''  # Must be explicitly configured in production
    
    # Initialize enhanced CORS
    enhanced_cors = EnhancedCORS(app)
    
    # Add CORS security headers
    @app.after_request
    def add_cors_security_headers(response):
        """Add additional security headers for CORS"""
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add CORS-specific security headers
        origin = request.headers.get('Origin')
        if origin:
            # Log CORS usage for monitoring
            if current_app.debug:
                logger.debug(f"CORS request from origin: {origin}")
        
        return response
    
    # Add CORS test endpoint
    @app.route('/api/v1/cors/test')
    def cors_test():
        """Test CORS functionality"""
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'data': {
                'message': 'CORS is working correctly',
                'origin': request.headers.get('Origin', 'No origin header'),
                'method': request.method,
                'headers': dict(request.headers),
                'cors_enabled': True
            }
        })
    
    logger.info("✅ Enhanced CORS security middleware initialized")
    
    return app