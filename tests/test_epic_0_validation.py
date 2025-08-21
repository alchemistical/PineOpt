#!/usr/bin/env python3
"""
EPIC 0 Validation Tests
Tests all Epic 0 success criteria for Foundation & Database Layer
"""

import pytest
import os
import sys
import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import db_manager, CryptoOHLCData, Strategy
from database.data_access import crypto_data, strategy_data, activity_data
from database.init_database import DatabaseInitializer
from sqlalchemy import text

# Global API base URL (will be set dynamically)
API_BASE_URL = 'http://localhost:5005'

class TestEpic0Validation:
    """Epic 0 validation test suite."""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment."""
        print("\n🧪 Setting up Epic 0 validation tests...")
        
        # Clean up any existing test database
        if os.path.exists("database/test_pineopt.db"):
            os.remove("database/test_pineopt.db")
        
        # Initialize fresh test database
        cls.db_init = DatabaseInitializer("database/test_pineopt.db")
        success = cls.db_init.initialize()
        cls.db_init.close()  # Close the connection
        
        if not success:
            raise Exception("Failed to initialize test database")
        
        # Create new database manager with test database
        global db_manager
        db_manager = db_manager.__class__(db_url="sqlite:///database/test_pineopt.db")
        
        print("   ✅ Test database initialized")
    
    def test_database_schema_is_valid(self):
        """✅ Database creates successfully with all tables."""
        session = db_manager.get_session()
        try:
            # Test that all critical tables exist
            critical_tables = [
                'crypto_ohlc_data', 'strategies', 'strategy_parameters',
                'backtest_configs', 'backtest_results', 'optimization_campaigns'
            ]
            
            for table in critical_tables:
                result = session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                assert result.fetchone() is not None, f"Table {table} does not exist"
            
            print("   ✅ All critical tables exist")
            
        finally:
            session.close()
    
    def test_can_insert_sample_ohlc_data(self):
        """✅ Can insert/query sample OHLC data."""
        # Prepare sample data
        sample_data = [
            {
                'timestamp_utc': int(datetime.now().timestamp() * 1000000),
                'datetime_str': datetime.now().isoformat() + 'Z',
                'open_price': 45000.0,
                'high_price': 45100.0,
                'low_price': 44900.0,
                'close_price': 45050.0,
                'volume': 100.0
            }
        ]
        
        # Insert data
        records_inserted = crypto_data.store_ohlc_data(
            symbol="TESTCOIN",
            exchange="TEST_EXCHANGE", 
            timeframe="1h",
            ohlc_data=sample_data,
            source_type="test"
        )
        
        assert records_inserted > 0, "No records were inserted"
        
        # Query data back
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol="TESTCOIN",
            exchange="TEST_EXCHANGE",
            timeframe="1h"
        )
        
        assert not df.empty, "Could not retrieve inserted data"
        assert len(df) >= 1, "Retrieved data count mismatch"
        
        print(f"   ✅ Successfully inserted and retrieved {records_inserted} OHLC records")
    
    def test_can_create_strategy_record(self):
        """✅ Can create and query strategy records."""
        strategy_id = strategy_data.create_strategy(
            name="Test Strategy",
            description="A test strategy for Epic 0 validation",
            pine_script_content="// Test Pine Script\nstrategy('Test', overlay=true)",
            category="Test"
        )
        
        assert strategy_id > 0, "Strategy creation failed"
        
        # Retrieve strategy
        strategy = strategy_data.get_strategy_with_parameters(strategy_id)
        assert strategy is not None, "Could not retrieve created strategy"
        assert strategy['name'] == "Test Strategy", "Strategy data mismatch"
        
        # Add parameter
        param_id = strategy_data.add_strategy_parameter(
            strategy_id=strategy_id,
            param_name="test_param",
            param_type="int",
            constraints={"min": 1, "max": 100},
            default_value=50
        )
        
        assert param_id > 0, "Parameter creation failed"
        
        print(f"   ✅ Created strategy {strategy_id} with parameter {param_id}")
    
    def test_api_returns_strategies_list(self):
        """✅ API endpoints return database data correctly."""
        # Find the API server
        api_base_url = 'http://localhost:5005'
        for port in [5005, 5006, 5007]:
            try:
                response = requests.get(f'http://localhost:{port}/api/db/health', timeout=2)
                if response.status_code == 200:
                    api_base_url = f'http://localhost:{port}'
                    break
            except:
                continue
        
        try:
            # Test database health endpoint
            response = requests.get(f'{api_base_url}/api/db/health', timeout=5)
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data['success'] is True, "Health check returned failure"
            assert health_data['status'] == 'healthy', "Database not healthy"
            
            # Test strategies endpoint
            response = requests.get(f'{api_base_url}/api/db/strategies', timeout=5)
            assert response.status_code == 200, f"Strategies endpoint failed: {response.status_code}"
            
            strategies_data = response.json()
            assert strategies_data['success'] is True, "Strategies API returned failure"
            assert 'strategies' in strategies_data, "Strategies data missing"
            
            print(f"   ✅ API returned {strategies_data['count']} strategies")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API server not available for testing: {e}")
    
    def test_api_handles_database_errors(self):
        """✅ API handles database errors gracefully."""
        # Find the API server
        api_base_url = 'http://localhost:5005'
        for port in [5005, 5006, 5007]:
            try:
                response = requests.get(f'http://localhost:{port}/api/db/health', timeout=2)
                if response.status_code == 200:
                    api_base_url = f'http://localhost:{port}'
                    break
            except:
                continue
                
        try:
            # Test invalid strategy ID
            response = requests.get(f'{api_base_url}/api/db/strategies/99999', timeout=5)
            assert response.status_code == 404, "API should return 404 for invalid strategy"
            
            error_data = response.json()
            assert error_data['success'] is False, "Error response should indicate failure"
            
            print("   ✅ API handles invalid requests correctly")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API server not available for testing: {e}")
    
    def test_database_query_performance_acceptable(self):
        """✅ Database query performance is acceptable."""
        # Insert more test data for performance testing
        large_dataset = []
        base_timestamp = int(datetime.now().timestamp() * 1000000)
        
        for i in range(1000):  # 1000 records
            large_dataset.append({
                'timestamp_utc': base_timestamp + (i * 3600000000),  # 1 hour intervals
                'datetime_str': datetime.fromtimestamp((base_timestamp + i * 3600000000) / 1000000).isoformat() + 'Z',
                'open_price': 45000.0 + i,
                'high_price': 45100.0 + i,
                'low_price': 44900.0 + i,
                'close_price': 45050.0 + i,
                'volume': 100.0 + i
            })
        
        # Time the insert operation
        start_time = time.time()
        records_inserted = crypto_data.store_ohlc_data(
            symbol="PERFTEST",
            exchange="TEST_EXCHANGE",
            timeframe="1h",
            ohlc_data=large_dataset,
            source_type="performance_test"
        )
        insert_time = time.time() - start_time
        
        assert insert_time < 10.0, f"Insert took too long: {insert_time:.2f}s"
        
        # Time the query operation
        start_time = time.time()
        df = crypto_data.get_ohlc_data_as_dataframe(
            symbol="PERFTEST",
            exchange="TEST_EXCHANGE",
            timeframe="1h"
        )
        query_time = time.time() - start_time
        
        assert query_time < 2.0, f"Query took too long: {query_time:.2f}s"
        assert len(df) >= 1000, "Performance test data not retrieved correctly"
        
        print(f"   ✅ Performance test: {records_inserted} records inserted in {insert_time:.2f}s, queried in {query_time:.2f}s")
    
    def test_frontend_integration_ready(self):
        """✅ Frontend integration endpoints are ready."""
        # Find the API server
        api_base_url = 'http://localhost:5005'
        for port in [5005, 5006, 5007]:
            try:
                response = requests.get(f'http://localhost:{port}/api/db/health', timeout=2)
                if response.status_code == 200:
                    api_base_url = f'http://localhost:{port}'
                    break
            except:
                continue
                
        try:
            # Test crypto sources endpoint
            response = requests.get(f'{api_base_url}/api/db/crypto/sources', timeout=5)
            assert response.status_code == 200, "Crypto sources endpoint failed"
            
            sources_data = response.json()
            assert sources_data['success'] is True, "Crypto sources API failed"
            
            # Test system stats endpoint
            response = requests.get(f'{api_base_url}/api/db/stats', timeout=5)
            assert response.status_code == 200, "System stats endpoint failed"
            
            stats_data = response.json()
            assert stats_data['success'] is True, "System stats API failed"
            assert 'stats' in stats_data, "Stats data missing"
            
            print("   ✅ Frontend integration endpoints ready")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API server not available for testing: {e}")
    
    def test_data_integrity_constraints(self):
        """✅ Data integrity checks prevent corrupt/duplicate data."""
        session = db_manager.get_session()
        try:
            # Test unique constraint on OHLC data
            duplicate_data = [{
                'timestamp_utc': 1640995200000000,  # Fixed timestamp
                'datetime_str': '2022-01-01T00:00:00Z',
                'open_price': 45000.0,
                'high_price': 45100.0,
                'low_price': 44900.0,
                'close_price': 45050.0,
                'volume': 100.0
            }]
            
            # First insert should succeed
            records1 = crypto_data.store_ohlc_data(
                symbol="UNIQUETEST",
                exchange="TEST_EXCHANGE",
                timeframe="1h",
                ohlc_data=duplicate_data,
                source_type="integrity_test"
            )
            
            # Second insert of same data should be handled gracefully
            records2 = crypto_data.store_ohlc_data(
                symbol="UNIQUETEST",
                exchange="TEST_EXCHANGE",
                timeframe="1h",
                ohlc_data=duplicate_data,
                source_type="integrity_test"
            )
            
            assert records1 > 0, "First insert should succeed"
            assert records2 == 0, "Duplicate insert should be prevented"
            
            print("   ✅ Data integrity constraints working correctly")
            
        finally:
            session.close()
    
    def test_system_stats_tracking(self):
        """✅ System statistics are tracked correctly."""
        # Update a system stat
        activity_data.update_system_stat('test_epic_0', '100', 'test')
        
        # Retrieve stats
        stats = activity_data.get_system_stats()
        assert 'test_epic_0' in stats, "System stat not found"
        assert stats['test_epic_0'] == '100', "System stat value incorrect"
        
        print("   ✅ System statistics tracking working")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests."""
        print("\n🧹 Cleaning up Epic 0 validation tests...")
        
        # Remove test database
        if os.path.exists("database/test_pineopt.db"):
            os.remove("database/test_pineopt.db")
            
        print("   ✅ Test cleanup completed")

def main():
    """Run Epic 0 validation tests."""
    print("🎯 EPIC 0: Foundation & Database Layer - Validation Tests")
    print("=" * 70)
    
    # Check if API server is running (try multiple ports)
    api_available = False
    api_port = None
    
    for port in [5005, 5006, 5007]:
        try:
            response = requests.get(f'http://localhost:{port}/api/db/health', timeout=2)
            if response.status_code == 200:
                api_available = True
                api_port = port
                break
        except:
            continue
    
    if not api_available:
        print("⚠️ API server not detected on localhost:5005-5007")
        print("   Some tests will be skipped. To run full tests, start the server:")
        print("   python3 api/server.py")
        print()
    else:
        print(f"✅ API server detected on localhost:{api_port}")
        # Update test URLs to use the detected port
        global API_BASE_URL
        API_BASE_URL = f'http://localhost:{api_port}'
    
    # Run tests
    pytest.main([
        __file__, 
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '-x',  # Stop on first failure
    ])

if __name__ == "__main__":
    main()