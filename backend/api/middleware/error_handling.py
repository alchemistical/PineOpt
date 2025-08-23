"""
Error Handling Middleware
Epic 7 Sprint 2 - Production Middleware

Provides standardized error handling across all API endpoints.
"""

from flask import jsonify, request, current_app
from datetime import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


def create_error_response(error_type, message, status_code=500, details=None):
    """Create standardized error response"""
    error_response = {
        'timestamp': datetime.utcnow().isoformat(),
        'epic': 'Epic 7 - API Architecture Rationalization',
        'error': {
            'type': error_type,
            'message': message,
            'status_code': status_code
        },
        'request': {
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint
        },
        'status': 'error'
    }
    
    if details:
        error_response['error']['details'] = details
    
    if current_app.debug:
        error_response['debug'] = {
            'args': dict(request.args),
            'user_agent': request.headers.get('User-Agent')
        }
    
    return error_response


def handle_400_bad_request(e):
    """Handle 400 Bad Request errors"""
    logger.warning(f"Bad request: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='bad_request',
        message='Invalid request format or missing required parameters',
        status_code=400,
        details=str(e) if current_app.debug else None
    )
    
    return jsonify(response), 400


def handle_404_not_found(e):
    """Handle 404 Not Found errors"""
    logger.warning(f"Not found: {request.path}")
    
    response = create_error_response(
        error_type='not_found',
        message=f'Endpoint {request.path} not found',
        status_code=404
    )
    
    return jsonify(response), 404


def handle_405_method_not_allowed(e):
    """Handle 405 Method Not Allowed errors"""
    logger.warning(f"Method not allowed: {request.method} {request.path}")
    
    response = create_error_response(
        error_type='method_not_allowed',
        message=f'Method {request.method} not allowed for {request.path}',
        status_code=405
    )
    
    return jsonify(response), 405


def handle_413_payload_too_large(e):
    """Handle 413 Request Entity Too Large errors"""
    logger.warning(f"Payload too large: {request.path}")
    
    response = create_error_response(
        error_type='payload_too_large',
        message='Request payload too large',
        status_code=413
    )
    
    return jsonify(response), 413


def handle_415_unsupported_media_type(e):
    """Handle 415 Unsupported Media Type errors"""
    logger.warning(f"Unsupported media type: {request.content_type} - Path: {request.path}")
    
    response = create_error_response(
        error_type='unsupported_media_type',
        message='Unsupported media type. Expected application/json',
        status_code=415
    )
    
    return jsonify(response), 415


def handle_429_rate_limit_exceeded(e):
    """Handle 429 Too Many Requests errors"""
    logger.warning(f"Rate limit exceeded: {request.remote_addr} - Path: {request.path}")
    
    response = create_error_response(
        error_type='rate_limit_exceeded',
        message='Too many requests. Please try again later',
        status_code=429,
        details=getattr(e, 'description', None)
    )
    
    return jsonify(response), 429


def handle_500_internal_server_error(e):
    """Handle 500 Internal Server Error"""
    error_id = f"err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    logger.error(f"Internal server error [{error_id}]: {e} - Path: {request.path}")
    logger.error(f"Traceback [{error_id}]: {traceback.format_exc()}")
    
    response = create_error_response(
        error_type='internal_server_error',
        message='An internal server error occurred',
        status_code=500,
        details={
            'error_id': error_id,
            'debug_info': str(e) if current_app.debug else None
        }
    )
    
    return jsonify(response), 500


def handle_503_service_unavailable(e):
    """Handle 503 Service Unavailable errors"""
    logger.error(f"Service unavailable: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='service_unavailable',
        message='Service temporarily unavailable. Please try again later',
        status_code=503
    )
    
    return jsonify(response), 503


def handle_validation_error(e):
    """Handle validation errors from request parsing"""
    logger.warning(f"Validation error: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='validation_error',
        message='Request validation failed',
        status_code=422,
        details=str(e) if hasattr(e, 'messages') else str(e)
    )
    
    return jsonify(response), 422


def handle_database_error(e):
    """Handle database connection/query errors"""
    error_id = f"db_err_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    logger.error(f"Database error [{error_id}]: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='database_error',
        message='Database operation failed',
        status_code=503,
        details={
            'error_id': error_id,
            'debug_info': str(e) if current_app.debug else None
        }
    )
    
    return jsonify(response), 503


def handle_conversion_error(e):
    """Handle strategy conversion errors"""
    logger.warning(f"Conversion error: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='conversion_error',
        message='Strategy conversion failed',
        status_code=422,
        details=str(e) if current_app.debug else None
    )
    
    return jsonify(response), 422


def handle_backtest_error(e):
    """Handle backtesting errors"""
    logger.warning(f"Backtest error: {e} - Path: {request.path}")
    
    response = create_error_response(
        error_type='backtest_error',
        message='Backtesting operation failed',
        status_code=422,
        details=str(e) if current_app.debug else None
    )
    
    return jsonify(response), 422


def init_error_handlers(app):
    """Initialize error handlers for the Flask app"""
    
    # HTTP error handlers
    app.register_error_handler(400, handle_400_bad_request)
    app.register_error_handler(404, handle_404_not_found)
    app.register_error_handler(405, handle_405_method_not_allowed)
    app.register_error_handler(413, handle_413_payload_too_large)
    app.register_error_handler(415, handle_415_unsupported_media_type)
    app.register_error_handler(429, handle_429_rate_limit_exceeded)
    app.register_error_handler(500, handle_500_internal_server_error)
    app.register_error_handler(503, handle_503_service_unavailable)
    
    # Custom exception handlers
    try:
        # Register handlers for custom exceptions if they exist
        from werkzeug.exceptions import UnprocessableEntity
        app.register_error_handler(UnprocessableEntity, handle_validation_error)
        app.register_error_handler(422, handle_validation_error)
    except ImportError:
        pass
    
    # Add custom exception types if needed
    class ConversionError(Exception):
        pass
    
    class BacktestError(Exception):
        pass
    
    class DatabaseError(Exception):
        pass
    
    app.register_error_handler(ConversionError, handle_conversion_error)
    app.register_error_handler(BacktestError, handle_backtest_error)
    app.register_error_handler(DatabaseError, handle_database_error)
    
    # Store custom exception classes in app config for use in routes
    app.config['CUSTOM_EXCEPTIONS'] = {
        'ConversionError': ConversionError,
        'BacktestError': BacktestError,
        'DatabaseError': DatabaseError
    }
    
    app.logger.info("✅ Error handlers initialized - standardized error responses active")
    
    return app