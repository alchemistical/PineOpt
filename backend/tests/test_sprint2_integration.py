"""
Integration Tests for Sprint 2 Complete System
Epic 7 Sprint 3 - Comprehensive Testing

Tests the full Sprint 2 system integration:
- Full middleware stack with all blueprints
- End-to-end API functionality
- Performance and load testing
- Error scenarios and edge cases
"""

import pytest
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch
from flask import Flask

# Import all Sprint 2 components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from app import create_app


class TestFullSystemIntegration:
    """Test complete system integration"""
    
    @pytest.fixture
    def app(self):
        """Create full application with all components"""
        return create_app('testing')
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_application_startup(self, app):
        """Test that application starts up correctly"""
        assert app is not None
        assert app.config['TESTING'] is True
        
        # Check that all blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        expected_blueprints = ['health', 'conversions', 'backtests', 'market_data', 'strategies']
        
        for expected in expected_blueprints:
            assert expected in blueprint_names
    
    def test_middleware_initialization(self, app):
        """Test that all middleware is properly initialized"""
        # Check that middleware configuration is present
        assert 'ENABLE_RATE_LIMITING' in app.config
        assert 'CORS_ORIGINS' in app.config
        
        # Test that middleware endpoints are available
        client = app.test_client()
        
        middleware_endpoints = [
            '/api/v1/rate-limit/status',
            '/api/v1/cors/config',
            '/api/v1/logs/config'
        ]
        
        for endpoint in middleware_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
    
    def test_all_api_endpoints_accessible(self, client):
        """Test that all major API endpoints are accessible"""
        endpoints = {
            # Health endpoints
            '/api/health': 200,
            '/api/v1/health/': 200,
            '/api/v1/health/metrics': 200,
            
            # API info endpoints
            '/api': 200,
            '/api/v1/conversions/': 200,
            '/api/v1/backtests/': 200,
            '/api/v1/market/': 200,
            '/api/v1/strategies/': 200,
            
            # Health check endpoints
            '/api/v1/conversions/health': 200,
            '/api/v1/backtests/health': 200,
            
            # Functional endpoints
            '/api/v1/conversions/indicators': 200,
            '/api/v1/backtests/pairs/available': 200,
            '/api/v1/backtests/history': 200,
            
            # Middleware endpoints
            '/api/v1/rate-limit/status': 200,
            '/api/v1/cors/config': 200,
            '/api/v1/logs/config': 200,
            '/api/v1/cors/test': 200
        }
        
        for endpoint, expected_status in endpoints.items():
            response = client.get(endpoint)
            assert response.status_code == expected_status, f"Endpoint {endpoint} returned {response.status_code}, expected {expected_status}"
    
    def test_error_handling_integration(self, client):
        """Test error handling across the full system"""
        # Test 404 error
        response = client.get('/nonexistent/endpoint')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'not_found'
        assert 'Epic 7' in data['epic']
        
        # Test method not allowed
        response = client.delete('/api/v1/health/')
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'method_not_allowed'
    
    def test_response_format_consistency(self, client):
        """Test that all endpoints return consistent response formats"""
        endpoints = [
            '/api/v1/health/',
            '/api/v1/conversions/',
            '/api/v1/backtests/',
            '/api/v1/rate-limit/status',
            '/api/v1/cors/config'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = json.loads(response.data)
            
            # All responses should have timestamp and epic
            assert 'timestamp' in data
            if 'epic' in data:
                assert 'Epic 7' in data['epic']
            
            # Should have either status field or be a success/error response
            assert 'status' in data or 'api' in data
    
    def test_cors_integration(self, client):
        """Test CORS functionality with actual requests"""
        # Test preflight request
        response = client.options('/api/v1/health/',
            headers={'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'GET'})
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers
        
        # Test actual request with CORS
        response = client.get('/api/v1/health/',
            headers={'Origin': 'http://localhost:3000'})
        assert response.status_code == 200
    
    def test_logging_integration(self, client):
        """Test that logging is working across requests"""
        # Make a request that should be logged
        response = client.get('/api/v1/health/')
        
        # Check that request ID is present in debug mode
        if response.headers.get('X-Request-ID'):
            assert len(response.headers.get('X-Request-ID')) > 0
        
        # Check response time header
        if response.headers.get('X-Response-Time'):
            assert 'ms' in response.headers.get('X-Response-Time')


class TestPerformanceAndLoad:
    """Test system performance and load handling"""
    
    @pytest.fixture
    def app(self):
        """Create application for performance testing"""
        app = create_app('testing')
        app.config['ENABLE_RATE_LIMITING'] = False  # Disable for load testing
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_response_times(self, client):
        """Test that endpoints respond within reasonable time"""
        endpoints = [
            '/api/v1/health/',
            '/api/v1/conversions/',
            '/api/v1/backtests/',
            '/api/v1/conversions/indicators'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 1.0, f"Endpoint {endpoint} took {response_time:.3f}s, should be < 1.0s"
    
    def test_concurrent_requests(self, app):
        """Test handling of concurrent requests"""
        def make_request():
            with app.test_client() as client:
                response = client.get('/api/v1/health/')
                return response.status_code
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10
    
    def test_memory_efficiency(self, client):
        """Test that repeated requests don't cause memory leaks"""
        # Make many requests to the same endpoint
        for _ in range(100):
            response = client.get('/api/v1/health/')
            assert response.status_code == 200
            
            # Clean up response data
            del response
    
    def test_rate_limiting_performance(self, app):
        """Test rate limiting doesn't significantly impact performance"""
        app.config['ENABLE_RATE_LIMITING'] = True
        app.config['GLOBAL_RATE_LIMIT_PER_MINUTE'] = 1000  # High limit for testing
        
        client = app.test_client()
        
        # Time requests with rate limiting
        start_time = time.time()
        for _ in range(10):
            response = client.get('/api/v1/health/')
            assert response.status_code == 200
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        # Should still be fast with rate limiting
        assert avg_time < 0.1, f"Average request time with rate limiting: {avg_time:.3f}s"


class TestEdgeCasesAndErrorScenarios:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def app(self):
        """Create application for error testing"""
        return create_app('testing')
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_malformed_json_requests(self, client):
        """Test handling of malformed JSON requests"""
        response = client.post('/api/v1/conversions/analyze',
                              data='{"malformed": json}',
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'bad_request'
    
    def test_missing_content_type(self, client):
        """Test handling of requests with missing content type"""
        response = client.post('/api/v1/conversions/analyze',
                              data='{"test": "data"}')
        
        # Should handle gracefully
        assert response.status_code in [400, 415]  # Bad Request or Unsupported Media Type
    
    def test_large_request_payload(self, client):
        """Test handling of large request payloads"""
        large_data = {'pine_code': 'x' * 10000}  # Large payload
        
        response = client.post('/api/v1/conversions/analyze',
                              json=large_data,
                              content_type='application/json')
        
        # Should handle large payloads (may return service error but not crash)
        assert response.status_code in [200, 400, 413, 422]
    
    def test_special_characters_in_urls(self, client):
        """Test handling of special characters in URLs"""
        special_urls = [
            '/api/v1/strategies/<script>alert(1)</script>',
            '/api/v1/conversions/策略',
            '/api/v1/backtests/results/test%20id'
        ]
        
        for url in special_urls:
            response = client.get(url)
            # Should not crash, may return 404 or other error
            assert response.status_code in [200, 400, 404, 422]
    
    def test_rate_limiting_edge_cases(self, app):
        """Test rate limiting edge cases"""
        app.config['ENABLE_RATE_LIMITING'] = True
        app.config['GLOBAL_RATE_LIMIT_PER_MINUTE'] = 2
        
        client = app.test_client()
        
        # First two requests should pass
        response1 = client.get('/api/v1/conversions/')
        response2 = client.get('/api/v1/conversions/')
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Third request should be rate limited
        response3 = client.get('/api/v1/conversions/')
        assert response3.status_code == 429
        
        data = json.loads(response3.data)
        assert data['error']['type'] == 'rate_limit_exceeded'
    
    def test_database_connection_errors(self, client):
        """Test handling of database connection errors"""
        # Test endpoints that might use database
        with patch('routes.backtests.get_strategy_database') as mock_db:
            mock_db.side_effect = Exception('Database connection failed')
            
            response = client.post('/api/v1/backtests/run',
                                 json={'strategy_id': 'test', 'symbol': 'BTCUSDT'},
                                 content_type='application/json')
            
            # Should handle database errors gracefully
            assert response.status_code in [200, 500, 503]
            if response.status_code != 200:
                data = json.loads(response.data)
                assert data['status'] == 'error'


class TestSecurityAndValidation:
    """Test security aspects and input validation"""
    
    @pytest.fixture
    def app(self):
        """Create application for security testing"""
        return create_app('testing')
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attempts"""
        malicious_inputs = [
            "'; DROP TABLE strategies; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post('/api/v1/conversions/convert/strategy/' + malicious_input)
            
            # Should not crash and should handle malicious input safely
            assert response.status_code in [200, 400, 404, 422]
    
    def test_xss_protection(self, client):
        """Test protection against XSS attempts"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            response = client.post('/api/v1/conversions/analyze',
                                 json={'pine_code': payload},
                                 content_type='application/json')
            
            # Response should not contain unescaped script tags
            response_text = response.get_data(as_text=True)
            assert '<script>' not in response_text
            assert 'javascript:' not in response_text
    
    def test_security_headers(self, client):
        """Test that security headers are present"""
        response = client.get('/api/v1/health/')
        
        # Check for security headers added by CORS middleware
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    
    def test_input_validation(self, client):
        """Test input validation across endpoints"""
        # Test invalid JSON structure
        invalid_inputs = [
            {'pine_code': None},
            {'pine_code': ''},
            {'pine_code': 123},  # Should be string
            {'invalid_field': 'value'},
            {}
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post('/api/v1/conversions/analyze',
                                 json=invalid_input,
                                 content_type='application/json')
            
            # Should handle invalid input gracefully
            assert response.status_code in [200, 400, 422]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])