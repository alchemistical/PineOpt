"""
Test Suite for Sprint 2 Consolidated Blueprints
Epic 7 Sprint 3 - Comprehensive Testing

Tests all consolidated blueprint components implemented in Sprint 2:
- Health blueprint
- Conversion blueprint
- Backtest blueprint
- Market data blueprint
- Strategy blueprint
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import blueprint components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from routes.health import health_bp
from routes.conversions import conversion_bp
from routes.backtests import backtest_bp
from routes.market_data import market_bp
from routes.strategies import strategy_bp
from utils.response_formatter import StandardResponse


class TestHealthBlueprint:
    """Test health blueprint functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application with health blueprint"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['API_VERSION'] = '1.0.0'
        app.register_blueprint(health_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_basic_health_endpoint(self, client):
        """Test basic health check endpoint"""
        response = client.get('/api/v1/health/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'PineOpt API'
        assert data['version'] == '1.0.0'
        assert 'timestamp' in data
        assert 'epic' in data
    
    def test_health_metrics_endpoint(self, client):
        """Test health metrics endpoint"""
        response = client.get('/api/v1/health/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'requests_total' in data['data']
        assert data['message'] == 'Metrics collection will be implemented in Sprint 3'
    
    @patch('routes.health.psutil')
    def test_detailed_health_endpoint_success(self, mock_psutil, client):
        """Test detailed health endpoint with mocked system info"""
        # Mock system metrics
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.virtual_memory.return_value = Mock(
            total=8000000000,
            available=4000000000,
            percent=50.0
        )
        mock_psutil.disk_usage.return_value = Mock(
            total=1000000000,
            free=500000000,
            used=500000000
        )
        
        response = client.get('/api/v1/health/detailed')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'health_checks' in data
        assert 'system' in data['health_checks']
        assert data['health_checks']['system']['cpu_percent'] == 25.5
    
    @patch('routes.health.psutil.cpu_percent')
    def test_detailed_health_endpoint_error(self, mock_cpu, client):
        """Test detailed health endpoint error handling"""
        mock_cpu.side_effect = Exception('System error')
        
        response = client.get('/api/v1/health/detailed')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['error']['type'] == 'health_check_failed'


class TestConversionsBlueprint:
    """Test conversions blueprint functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application with conversions blueprint"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(conversion_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_conversions_info_endpoint(self, client):
        """Test conversions info endpoint"""
        response = client.get('/api/v1/conversions/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'api' in data
        assert 'endpoints' in data
        assert data['api'] == 'Conversion Management API'
        assert 'analyze' in data['endpoints']
    
    def test_conversions_health_endpoint(self, client):
        """Test conversions health endpoint"""
        response = client.get('/api/v1/conversions/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Conversion Management'
        assert 'services' in data
        assert 'strategy_database' in data['services']
    
    def test_analyze_endpoint_no_service(self, client):
        """Test analyze endpoint when AI service is unavailable"""
        response = client.post(
            '/api/v1/conversions/analyze',
            json={'pine_code': 'strategy("Test")'},
            content_type='application/json'
        )
        
        # Should return error when service is unavailable
        assert response.status_code == 200  # Returns success but with error in data
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'AI analysis service not available' in data['error']
    
    def test_indicators_endpoint(self, client):
        """Test indicators endpoint"""
        response = client.get('/api/v1/conversions/indicators')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'indicators' in data
        assert isinstance(data['indicators'], list)
        assert len(data['indicators']) > 0
    
    def test_convert_working_endpoint_no_data(self, client):
        """Test working converter endpoint with no data"""
        response = client.post('/api/v1/conversions/convert/working')
        
        # Should handle missing data gracefully
        assert response.status_code in [400, 200]  # Either validation error or service error
    
    @patch('routes.conversions.get_strategy_database')
    def test_convert_strategy_endpoint(self, mock_db, client):
        """Test convert strategy by ID endpoint"""
        # Mock database response
        mock_db.return_value.get_strategy.return_value = {
            'id': 'test123',
            'name': 'Test Strategy',
            'pine_code': 'strategy("Test")'
        }
        
        response = client.post('/api/v1/conversions/convert/strategy/test123')
        
        # Since converter is unavailable, should return service error
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'error' in data or 'status' in data


class TestBacktestsBlueprint:
    """Test backtests blueprint functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application with backtests blueprint"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(backtest_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_backtests_info_endpoint(self, client):
        """Test backtests info endpoint"""
        response = client.get('/api/v1/backtests/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'api' in data
        assert data['api'] == 'Backtest Management API'
        assert 'endpoints' in data
        assert 'run' in data['endpoints']
    
    def test_backtests_health_endpoint(self, client):
        """Test backtests health endpoint"""
        response = client.get('/api/v1/backtests/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Backtest Management'
        assert 'services' in data
    
    def test_available_pairs_endpoint(self, client):
        """Test available trading pairs endpoint"""
        response = client.get('/api/v1/backtests/pairs/available')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'pairs' in data
        assert isinstance(data['pairs'], list)
        assert len(data['pairs']) > 0
        # Should have common trading pairs
        pair_symbols = [pair['symbol'] for pair in data['pairs']]
        assert 'BTCUSDT' in pair_symbols
    
    def test_run_backtest_missing_strategy(self, client):
        """Test run backtest with missing strategy"""
        response = client.post(
            '/api/v1/backtests/run',
            json={'strategy_id': 'nonexistent', 'symbol': 'BTCUSDT', 'timeframe': '1h'},
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Strategy not found' in data['error']
    
    def test_run_backtest_invalid_data(self, client):
        """Test run backtest with invalid data"""
        response = client.post('/api/v1/backtests/run')
        
        # Should handle missing JSON data
        assert response.status_code in [400, 200]
    
    @patch('routes.backtests.get_strategy_database')
    def test_run_backtest_with_strategy(self, mock_db, client):
        """Test run backtest with valid strategy"""
        # Mock strategy exists
        mock_db.return_value.get_strategy.return_value = {
            'id': 'test_strategy',
            'name': 'Test Strategy',
            'pine_code': 'strategy("Test")'
        }
        
        response = client.post(
            '/api/v1/backtests/run',
            json={
                'strategy_id': 'test_strategy',
                'symbol': 'BTCUSDT',
                'timeframe': '1h'
            },
            content_type='application/json'
        )
        
        # Should return mock backtest results
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'backtest_id' in data
        assert 'performance_metrics' in data
        assert data['strategy_id'] == 'test_strategy'
    
    def test_backtest_history_endpoint(self, client):
        """Test backtest history endpoint"""
        response = client.get('/api/v1/backtests/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'backtests' in data
        assert isinstance(data['backtests'], list)


class TestMarketDataBlueprint:
    """Test market data blueprint functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application with market data blueprint"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(market_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_market_info_endpoint(self, client):
        """Test market data info endpoint"""
        response = client.get('/api/v1/market/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'api' in data
        assert 'Market Data API' in data['api']
        assert 'endpoints' in data


class TestStrategiesBlueprint:
    """Test strategies blueprint functionality"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application with strategies blueprint"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(strategy_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_strategies_info_endpoint(self, client):
        """Test strategies info endpoint"""
        response = client.get('/api/v1/strategies/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'api' in data
        assert 'endpoints' in data
        assert 'Strategy Management API' in data['api']


class TestBlueprintIntegration:
    """Test blueprint integration and cross-blueprint functionality"""
    
    @pytest.fixture
    def full_app(self):
        """Create app with all blueprints"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['API_VERSION'] = '1.0.0'
        
        # Register all blueprints
        app.register_blueprint(health_bp)
        app.register_blueprint(conversion_bp)
        app.register_blueprint(backtest_bp)
        app.register_blueprint(market_bp)
        app.register_blueprint(strategy_bp)
        
        return app
    
    @pytest.fixture
    def client(self, full_app):
        """Create test client"""
        return full_app.test_client()
    
    def test_all_blueprints_registered(self, client):
        """Test that all blueprint endpoints are accessible"""
        endpoints = [
            '/api/v1/health/',
            '/api/v1/conversions/',
            '/api/v1/backtests/',
            '/api/v1/market/',
            '/api/v1/strategies/'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    def test_health_checks_across_blueprints(self, client):
        """Test health endpoints across different blueprints"""
        health_endpoints = [
            '/api/v1/health/',
            '/api/v1/conversions/health',
            '/api/v1/backtests/health'
        ]
        
        for endpoint in health_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
    
    def test_consistent_response_format(self, client):
        """Test that all blueprints return consistent response formats"""
        endpoints = [
            '/api/v1/health/',
            '/api/v1/conversions/',
            '/api/v1/backtests/'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = json.loads(response.data)
            
            # All responses should have these fields
            assert 'timestamp' in data or 'status' in data
            if 'epic' in data:
                assert 'Epic 7' in data['epic']
    
    def test_blueprint_url_prefixes(self, full_app):
        """Test that all blueprints have correct URL prefixes"""
        # Check that routes are properly prefixed
        routes = [str(rule) for rule in full_app.url_map.iter_rules()]
        
        assert any('/api/v1/health/' in route for route in routes)
        assert any('/api/v1/conversions/' in route for route in routes)
        assert any('/api/v1/backtests/' in route for route in routes)
        assert any('/api/v1/market/' in route for route in routes)
        assert any('/api/v1/strategies/' in route for route in routes)
    
    def test_no_route_conflicts(self, full_app):
        """Test that there are no route conflicts between blueprints"""
        routes = list(full_app.url_map.iter_rules())
        route_patterns = [rule.rule for rule in routes]
        
        # Check for duplicate routes
        assert len(route_patterns) == len(set(route_patterns)), "Duplicate routes detected"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])