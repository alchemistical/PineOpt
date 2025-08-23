"""
Logging Middleware
Epic 7 Sprint 2 - Production Middleware

Provides structured request/response logging with performance metrics.
"""

from flask import request, g, current_app, jsonify
from datetime import datetime
import time
import json
import logging
import uuid
from functools import wraps

logger = logging.getLogger(__name__)


class RequestLogger:
    """Handles structured request/response logging"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging middleware"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown)
    
    def _before_request(self):
        """Log incoming request details"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Skip logging for health checks and static files if configured
        if self._should_skip_logging():
            g.skip_logging = True
            return
        
        g.skip_logging = False
        
        # Log request start
        request_data = {
            'request_id': g.request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.content_type,
            'content_length': request.content_length,
            'args': dict(request.args) if current_app.debug else {},
            'epic': 'Epic 7 - API Architecture Rationalization',
            'event': 'request_start'
        }
        
        # Add form data in debug mode (be careful with sensitive data)
        if current_app.debug and request.is_json:
            try:
                request_data['json_data'] = request.get_json() or {}
            except Exception:
                request_data['json_data'] = 'Invalid JSON'
        
        logger.info(f"REQUEST START [{g.request_id}]: {request.method} {request.path}", 
                   extra={'request_data': request_data})
    
    def _after_request(self, response):
        """Log response details and performance metrics"""
        if getattr(g, 'skip_logging', True):
            return response
        
        # Calculate request duration
        duration = time.time() - getattr(g, 'start_time', time.time())
        
        # Log response
        response_data = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'status_code': response.status_code,
            'content_type': response.content_type,
            'content_length': response.content_length,
            'duration_ms': round(duration * 1000, 2),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'event': 'request_complete'
        }
        
        # Add response data in debug mode (truncated for large responses)
        if current_app.debug and response.is_json:
            try:
                response_json = response.get_json()
                if response_json and len(str(response_json)) < 1000:
                    response_data['response_data'] = response_json
                else:
                    response_data['response_data'] = 'Large response (truncated)'
            except Exception:
                response_data['response_data'] = 'Non-JSON response'
        
        # Log with appropriate level based on status code
        if response.status_code >= 500:
            log_level = logging.ERROR
            status_type = "ERROR"
        elif response.status_code >= 400:
            log_level = logging.WARNING
            status_type = "CLIENT_ERROR"
        else:
            log_level = logging.INFO
            status_type = "SUCCESS"
        
        logger.log(log_level, 
                  f"REQUEST {status_type} [{g.request_id}]: {request.method} {request.path} - {response.status_code} - {duration*1000:.2f}ms",
                  extra={'response_data': response_data})
        
        # Add custom headers for debugging
        if current_app.debug:
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            response.headers['X-Response-Time'] = f"{duration*1000:.2f}ms"
        
        return response
    
    def _teardown(self, exception):
        """Clean up request context"""
        if exception:
            error_data = {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'path': request.path,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'epic': 'Epic 7 - API Architecture Rationalization',
                'event': 'request_exception'
            }
            
            logger.error(f"REQUEST EXCEPTION [{getattr(g, 'request_id', 'unknown')}]: {type(exception).__name__} - {exception}",
                        extra={'error_data': error_data})
    
    def _should_skip_logging(self):
        """Determine if request should be skipped from logging"""
        skip_paths = current_app.config.get('LOGGING_SKIP_PATHS', [
            '/api/health',
            '/api/v1/health/status',
            '/static/'
        ])
        
        for skip_path in skip_paths:
            if request.path.startswith(skip_path):
                return True
        
        return False


def log_performance(operation_name):
    """Decorator to log performance of specific operations"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            request_id = getattr(g, 'request_id', 'no-request')
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"OPERATION SUCCESS [{request_id}]: {operation_name} completed in {duration*1000:.2f}ms",
                           extra={
                               'performance_data': {
                                   'request_id': request_id,
                                   'operation': operation_name,
                                   'duration_ms': round(duration * 1000, 2),
                                   'status': 'success',
                                   'timestamp': datetime.utcnow().isoformat()
                               }
                           })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(f"OPERATION FAILED [{request_id}]: {operation_name} failed after {duration*1000:.2f}ms - {type(e).__name__}: {e}",
                           extra={
                               'performance_data': {
                                   'request_id': request_id,
                                   'operation': operation_name,
                                   'duration_ms': round(duration * 1000, 2),
                                   'status': 'failed',
                                   'error': str(e),
                                   'error_type': type(e).__name__,
                                   'timestamp': datetime.utcnow().isoformat()
                               }
                           })
                
                raise
        
        return decorated_function
    return decorator


def init_logging(app):
    """Initialize structured logging middleware"""
    
    # Configure logging format for structured logs
    if not app.config.get('TESTING', False):
        # Set up structured JSON logging in production
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Configure app logger
        if not app.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
        
        app.logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)
    
    # Initialize request logger
    request_logger = RequestLogger(app)
    
    # Add logging configuration endpoint
    @app.route('/api/v1/logs/config')
    def logging_config():
        """Get current logging configuration"""
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'data': {
                'logging_enabled': True,
                'log_level': app.logger.level,
                'log_level_name': logging.getLevelName(app.logger.level),
                'debug_mode': app.debug,
                'skip_paths': app.config.get('LOGGING_SKIP_PATHS', []),
                'structured_logging': True
            }
        })
    
    app.logger.info("✅ Structured logging middleware initialized")
    app.logger.info(f"  • Log level: {logging.getLevelName(app.logger.level)}")
    app.logger.info(f"  • Debug mode: {app.debug}")
    
    return app