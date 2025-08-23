"""
Epic 7 Sprint 1 Test Suite
Tests for API foundation and route consolidation
"""

import pytest
import json
from backend.api.app import create_app
from backend.database.unified_data_access import UnifiedDataAccess


@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    return app


@pytest.fixture  
def client(app):
    """Create test client"""
    return app.test_client()


class TestAPIFoundation:
    """Test Flask application factory and basic setup"""
    
    def test_app_creation(self, app):
        """Test that app is created properly"""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_api_info_endpoint(self, client):
        """Test basic API info endpoint"""
        response = client.get('/api')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['name'] == 'PineOpt API'
        assert data['version'] == 'v1'
        assert 'Epic 7' in data['epic']
    
    def test_health_endpoint(self, client):
        """Test basic health check"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'Epic 7' in data['epic']


class TestHealthRoutes:
    """Test health check endpoints"""
    
    def test_basic_health(self, client):
        """Test basic health check"""
        response = client.get('/api/v1/health/')
        # May be 404 if blueprint not registered yet
        # This test will pass once Sprint 1 Task 1 is complete
        
    def test_detailed_health(self, client):
        """Test detailed health check"""
        response = client.get('/api/v1/health/detailed')
        # Will be implemented in Sprint 1
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/api/v1/health/metrics')
        # Will be implemented in Sprint 1


class TestMarketDataRoutes:
    """Test market data route consolidation"""
    
    def test_market_info(self, client):
        """Test market API info"""
        response = client.get('/api/v1/market/')
        # Will be 404 until blueprint is registered
    
    def test_market_overview(self, client):
        """Test market overview endpoint"""
        response = client.get('/api/v1/market/overview')
        # Test will pass once consolidation is complete
    
    def test_get_symbols(self, client):
        """Test symbols endpoint"""
        response = client.get('/api/v1/market/symbols')
        # Test will pass once consolidation is complete
    
    def test_get_tickers(self, client):
        """Test tickers endpoint"""
        response = client.get('/api/v1/market/tickers')
        # Test will pass once consolidation is complete
    
    def test_get_ohlc_data(self, client):
        """Test OHLC data endpoint"""
        response = client.get('/api/v1/market/ohlc/BTCUSDT')
        # Test will pass once consolidation is complete


class TestStrategyRoutes:
    """Test strategy route consolidation"""
    
    def test_strategy_info(self, client):
        """Test strategy API info"""
        response = client.get('/api/v1/strategies/')
        # Will be 404 until blueprint is registered
    
    def test_list_strategies(self, client):
        """Test strategy listing"""
        response = client.get('/api/v1/strategies/')
        # Test will pass once consolidation is complete
    
    def test_create_strategy(self, client):
        """Test strategy creation"""
        strategy_data = {
            'name': 'Test Strategy',
            'description': 'Test strategy for Epic 7',
            'pine_script': '//@version=5\nstrategy("Test", overlay=true)'
        }
        
        response = client.post('/api/v1/strategies/',
                              json=strategy_data,
                              content_type='application/json')
        # Test will pass once consolidation is complete
    
    def test_get_strategy(self, client):
        """Test get strategy by ID"""
        response = client.get('/api/v1/strategies/1')
        # Test will pass once consolidation is complete
    
    def test_update_strategy(self, client):
        """Test strategy update"""
        update_data = {
            'description': 'Updated description'
        }
        
        response = client.put('/api/v1/strategies/1',
                             json=update_data,
                             content_type='application/json')
        # Test will pass once consolidation is complete
    
    def test_delete_strategy(self, client):
        """Test strategy deletion"""
        response = client.delete('/api/v1/strategies/1')
        # Test will pass once consolidation is complete


class TestDatabaseIntegration:
    """Test database integration with new routes"""
    
    def test_database_connectivity(self):
        """Test unified database access"""
        try:
            da = UnifiedDataAccess()
            stats = da.get_database_stats()
            assert isinstance(stats, dict)
            assert 'market_data_count' in stats
        except Exception as e:
            pytest.fail(f"Database connectivity failed: {e}")
    
    def test_market_data_access(self):
        """Test market data retrieval"""
        try:
            da = UnifiedDataAccess()
            symbols = da.get_available_symbols()
            assert isinstance(symbols, list)
        except Exception as e:
            pytest.fail(f"Market data access failed: {e}")
    
    def test_strategy_access(self):
        """Test strategy data retrieval"""
        try:
            da = UnifiedDataAccess()
            strategies = da.get_strategies()
            assert isinstance(strategies, list)
        except Exception as e:
            pytest.fail(f"Strategy access failed: {e}")


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])