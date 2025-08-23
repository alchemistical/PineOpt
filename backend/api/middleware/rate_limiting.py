"""
Rate Limiting Middleware
Epic 7 Sprint 2 - Production Middleware

Provides configurable rate limiting for API endpoints.
"""

from flask import request, current_app, jsonify
from datetime import datetime, timedelta
import time
import logging
from collections import defaultdict
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory rate limit storage (use Redis in production)
rate_limit_storage = defaultdict(list)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    def is_rate_limited(self, client_id):
        """Check if client is rate limited"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Clean old requests
        client_requests = rate_limit_storage[client_id]
        client_requests[:] = [req_time for req_time in client_requests if req_time > hour_ago]
        
        # Count recent requests
        requests_last_minute = sum(1 for req_time in client_requests if req_time > minute_ago)
        requests_last_hour = len(client_requests)
        
        # Check limits
        if requests_last_minute >= self.requests_per_minute:
            return True, f"Rate limit exceeded: {requests_last_minute}/{self.requests_per_minute} per minute"
        
        if requests_last_hour >= self.requests_per_hour:
            return True, f"Rate limit exceeded: {requests_last_hour}/{self.requests_per_hour} per hour"
        
        # Record this request
        rate_limit_storage[client_id].append(now)
        return False, None
    
    def get_rate_limit_info(self, client_id):
        """Get current rate limit status"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        client_requests = rate_limit_storage[client_id]
        requests_last_minute = sum(1 for req_time in client_requests if req_time > minute_ago)
        requests_last_hour = sum(1 for req_time in client_requests if req_time > hour_ago)
        
        return {
            'requests_last_minute': requests_last_minute,
            'requests_last_hour': requests_last_hour,
            'limit_per_minute': self.requests_per_minute,
            'limit_per_hour': self.requests_per_hour,
            'remaining_minute': max(0, self.requests_per_minute - requests_last_minute),
            'remaining_hour': max(0, self.requests_per_hour - requests_last_hour)
        }


def get_client_id():
    """Get unique client identifier"""
    # Use IP address as client ID (in production, consider user ID or API key)
    return request.remote_addr or 'unknown'


def rate_limit_decorator(requests_per_minute=60, requests_per_hour=1000):
    """Decorator for rate limiting specific endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('ENABLE_RATE_LIMITING', True):
                return f(*args, **kwargs)
            
            limiter = RateLimiter(requests_per_minute, requests_per_hour)
            client_id = get_client_id()
            
            is_limited, message = limiter.is_rate_limited(client_id)
            
            if is_limited:
                logger.warning(f"Rate limit exceeded for {client_id}: {message} - Path: {request.path}")
                
                # Create 429 response
                from werkzeug.exceptions import TooManyRequests
                raise TooManyRequests(description=message)
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                rate_info = limiter.get_rate_limit_info(client_id)
                response.headers['X-RateLimit-Limit-Minute'] = str(rate_info['limit_per_minute'])
                response.headers['X-RateLimit-Limit-Hour'] = str(rate_info['limit_per_hour'])
                response.headers['X-RateLimit-Remaining-Minute'] = str(rate_info['remaining_minute'])
                response.headers['X-RateLimit-Remaining-Hour'] = str(rate_info['remaining_hour'])
            
            return response
        return decorated_function
    return decorator


def rate_limit_middleware(app):
    """Global rate limiting middleware"""
    @app.before_request
    def before_request():
        # Skip rate limiting for health checks and static files
        if request.path in ['/api/health', '/api/v1/health/status']:
            return None
        
        if request.path.startswith('/static/'):
            return None
        
        # Skip if rate limiting is disabled
        if not app.config.get('ENABLE_RATE_LIMITING', True):
            return None
        
        # Apply global rate limits
        limiter = RateLimiter(
            requests_per_minute=app.config.get('GLOBAL_RATE_LIMIT_PER_MINUTE', 100),
            requests_per_hour=app.config.get('GLOBAL_RATE_LIMIT_PER_HOUR', 2000)
        )
        
        client_id = get_client_id()
        is_limited, message = limiter.is_rate_limited(client_id)
        
        if is_limited:
            logger.warning(f"Global rate limit exceeded for {client_id}: {message} - Path: {request.path}")
            
            # Return 429 response
            response = jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 - API Architecture Rationalization',
                'error': {
                    'type': 'rate_limit_exceeded',
                    'message': 'Too many requests. Please try again later',
                    'status_code': 429,
                    'details': message
                },
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'client': client_id
                },
                'status': 'error'
            })
            response.status_code = 429
            return response
        
        return None


def init_rate_limiting(app):
    """Initialize rate limiting middleware"""
    
    # Set default configuration
    if 'ENABLE_RATE_LIMITING' not in app.config:
        app.config['ENABLE_RATE_LIMITING'] = True
    
    if 'GLOBAL_RATE_LIMIT_PER_MINUTE' not in app.config:
        app.config['GLOBAL_RATE_LIMIT_PER_MINUTE'] = 100
    
    if 'GLOBAL_RATE_LIMIT_PER_HOUR' not in app.config:
        app.config['GLOBAL_RATE_LIMIT_PER_HOUR'] = 2000
    
    # Initialize middleware only if enabled
    if app.config['ENABLE_RATE_LIMITING']:
        rate_limit_middleware(app)
        app.logger.info("✅ Rate limiting initialized")
        app.logger.info(f"  • Global limits: {app.config['GLOBAL_RATE_LIMIT_PER_MINUTE']}/min, {app.config['GLOBAL_RATE_LIMIT_PER_HOUR']}/hour")
    else:
        app.logger.info("⚠️ Rate limiting disabled")
    
    # Add rate limit status endpoint
    @app.route('/api/v1/rate-limit/status')
    def rate_limit_status():
        """Get current rate limit status for client"""
        if not app.config['ENABLE_RATE_LIMITING']:
            return jsonify({
                'timestamp': datetime.utcnow().isoformat(),
                'epic': 'Epic 7 - API Architecture Rationalization',
                'status': 'success',
                'data': {
                    'rate_limiting_enabled': False,
                    'message': 'Rate limiting is disabled'
                }
            })
        
        limiter = RateLimiter(
            requests_per_minute=app.config['GLOBAL_RATE_LIMIT_PER_MINUTE'],
            requests_per_hour=app.config['GLOBAL_RATE_LIMIT_PER_HOUR']
        )
        
        client_id = get_client_id()
        rate_info = limiter.get_rate_limit_info(client_id)
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'epic': 'Epic 7 - API Architecture Rationalization',
            'status': 'success',
            'data': {
                'rate_limiting_enabled': True,
                'client_id': client_id,
                'limits': rate_info,
                'reset_times': {
                    'minute_reset': (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                    'hour_reset': (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
            }
        })
    
    return app