"""
Standardized Response Formatter
Epic 7 Sprint 2 - Response Format Standardization

Provides consistent response formatting across all API endpoints.
"""

from flask import jsonify, request
from datetime import datetime
from typing import Any, Dict, Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class StandardResponse:
    """Standardized response structure for Epic 7"""
    
    @staticmethod
    def success(data: Any, message: Optional[str] = None, status_code: int = 200, 
                meta: Optional[Dict] = None) -> tuple:
        """Create standardized success response"""
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'data': data
        }
        
        if message:
            response['message'] = message
            
        if meta:
            response['meta'] = meta
            
        # Add request context if available
        if request:
            response['request_info'] = {
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            }
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(error_type: str, message: str, status_code: int = 400, 
              details: Optional[Union[str, Dict]] = None, 
              suggestion: Optional[str] = None) -> tuple:
        """Create standardized error response"""
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'error',
            'error': {
                'type': error_type,
                'message': message,
                'status_code': status_code
            }
        }
        
        if details:
            response['error']['details'] = details
            
        if suggestion:
            response['error']['suggestion'] = suggestion
            
        # Add request context if available
        if request:
            response['request_info'] = {
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            }
        
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(data: List[Any], page: int, per_page: int, total: int,
                  message: Optional[str] = None) -> tuple:
        """Create standardized paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'prev_page': page - 1 if page > 1 else None
            }
        }
        
        if message:
            response['message'] = message
            
        # Add request context if available
        if request:
            response['request_info'] = {
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            }
        
        return jsonify(response), 200
    
    @staticmethod
    def api_info(name: str, version: str, description: str, 
                 endpoints: Dict[str, str], consolidates: Optional[List[str]] = None,
                 status: str = "active") -> tuple:
        """Create standardized API info response"""
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'api_info': {
                'name': name,
                'version': version,
                'description': description,
                'status': status,
                'endpoints': endpoints
            }
        }
        
        if consolidates:
            response['api_info']['consolidates'] = consolidates
            
        # Add request context if available
        if request:
            response['request_info'] = {
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            }
        
        return jsonify(response), 200
    
    @staticmethod
    def health_check(service_name: str, status: str = "healthy", 
                     checks: Optional[Dict] = None,
                     version: Optional[str] = None) -> tuple:
        """Create standardized health check response"""
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': status,
            'service': service_name
        }
        
        if version:
            response['version'] = version
            
        if checks:
            response['health_checks'] = checks
            
        # Add request context if available
        if request:
            response['request_info'] = {
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint
            }
        
        status_code = 200 if status == "healthy" else 503
        return jsonify(response), status_code


# Convenience functions for common use cases
def success_response(data: Any, message: Optional[str] = None, 
                    status_code: int = 200, meta: Optional[Dict] = None) -> tuple:
    """Convenience function for success responses"""
    return StandardResponse.success(data, message, status_code, meta)


def error_response(error_type: str, message: str, status_code: int = 400,
                  details: Optional[Union[str, Dict]] = None,
                  suggestion: Optional[str] = None) -> tuple:
    """Convenience function for error responses"""
    return StandardResponse.error(error_type, message, status_code, details, suggestion)


def paginated_response(data: List[Any], page: int, per_page: int, total: int,
                      message: Optional[str] = None) -> tuple:
    """Convenience function for paginated responses"""
    return StandardResponse.paginated(data, page, per_page, total, message)


def api_info_response(name: str, version: str, description: str,
                     endpoints: Dict[str, str], consolidates: Optional[List[str]] = None,
                     status: str = "active") -> tuple:
    """Convenience function for API info responses"""
    return StandardResponse.api_info(name, version, description, endpoints, consolidates, status)


def health_response(service_name: str, status: str = "healthy",
                   checks: Optional[Dict] = None,
                   version: Optional[str] = None) -> tuple:
    """Convenience function for health check responses"""
    return StandardResponse.health_check(service_name, status, checks, version)


# Response format validation helpers
def validate_success_data(data: Any) -> bool:
    """Validate that data is suitable for success response"""
    if data is None:
        return False
    return True


def validate_error_type(error_type: str) -> bool:
    """Validate error type format"""
    valid_error_types = {
        'validation_error',
        'not_found', 
        'bad_request',
        'unauthorized',
        'forbidden',
        'conflict',
        'internal_server_error',
        'service_unavailable',
        'rate_limit_exceeded',
        'conversion_error',
        'backtest_error',
        'database_error',
        'external_service_error'
    }
    return error_type in valid_error_types or '_' in error_type


# Helper decorators for consistent responses
def standardize_response(f):
    """Decorator to ensure consistent response format"""
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # If result is already a tuple with response and status code, return as-is
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if hasattr(response_data, 'json'):  # Already a Flask response
                    return result
            
            # If result is raw data, wrap in success response
            return success_response(result)
            
        except Exception as e:
            logger.error(f"Endpoint {f.__name__} error: {e}", exc_info=True)
            return error_response(
                'internal_server_error',
                'An unexpected error occurred',
                500,
                str(e) if logger.level <= logging.DEBUG else None
            )
    
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper