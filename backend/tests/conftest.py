"""
Test Configuration for Epic 7 Sprint 2 Testing Suite
Epic 7 Sprint 3 - Comprehensive Testing

Shared test fixtures and configuration for all test modules.
"""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add project paths to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend_path = os.path.join(project_root, 'backend')
api_path = os.path.join(backend_path, 'api')

sys.path.insert(0, project_root)
sys.path.insert(0, backend_path)
sys.path.insert(0, api_path)


@pytest.fixture(scope='session')
def temp_dir():
    """Create temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope='session')
def mock_database():
    """Mock database for testing"""
    mock_db = Mock()
    
    # Mock strategy database responses
    mock_db.get_strategy.return_value = {
        'id': 'test_strategy',
        'name': 'Test Strategy',
        'pine_code': 'strategy("Test Strategy", overlay=true)',
        'created_at': '2025-01-01T00:00:00Z',
        'updated_at': '2025-01-01T00:00:00Z'
    }
    
    mock_db.list_strategies.return_value = [
        {
            'id': 'strategy1',
            'name': 'Strategy 1',
            'created_at': '2025-01-01T00:00:00Z'
        },
        {
            'id': 'strategy2', 
            'name': 'Strategy 2',
            'created_at': '2025-01-01T00:00:00Z'
        }
    ]
    
    mock_db.get_database_stats.return_value = {
        'strategies_count': 10,
        'market_data_count': 1000,
        'market_tickers_count': 50
    }
    
    return mock_db


@pytest.fixture
def mock_ai_analyzer():
    """Mock AI analyzer for testing"""
    mock_analyzer = Mock()
    
    mock_analyzer.analyze_strategy.return_value = {
        'analysis_id': 'test_analysis',
        'strategy_type': 'trend_following',
        'indicators_used': ['SMA', 'EMA', 'RSI'],
        'complexity_score': 0.75,
        'recommendations': [
            'Consider adding stop loss',
            'Optimize entry conditions'
        ]
    }
    
    return mock_analyzer


@pytest.fixture
def mock_converter():
    """Mock converter service for testing"""
    mock_converter = Mock()
    
    mock_converter.convert_pine_to_python.return_value = {
        'conversion_id': 'test_conversion',
        'python_code': '''
def strategy_logic(data):
    # Converted strategy logic
    return signals
''',
        'success': True,
        'warnings': [],
        'errors': []
    }
    
    return mock_converter


@pytest.fixture
def mock_backtest_engine():
    """Mock backtest engine for testing"""
    mock_engine = Mock()
    
    mock_engine.run_backtest.return_value = {
        'backtest_id': 'test_backtest',
        'performance_metrics': {
            'total_return': 15.2,
            'annual_return': 12.8,
            'sharpe_ratio': 1.45,
            'max_drawdown': -8.3,
            'win_rate': 0.62,
            'total_trades': 45,
            'profit_factor': 1.8
        },
        'equity_curve': [100, 105, 103, 108, 115],
        'trades': [
            {
                'entry_time': '2025-01-01T10:00:00Z',
                'exit_time': '2025-01-01T12:00:00Z',
                'side': 'buy',
                'entry_price': 50000,
                'exit_price': 51000,
                'pnl': 1000
            }
        ]
    }
    
    return mock_engine


# Removed automatic mocking - will be handled per test as needed


@pytest.fixture
def sample_pine_code():
    """Sample Pine Script code for testing"""
    return '''
//@version=5
strategy("Test Strategy", overlay=true)

// Input parameters
length = input.int(14, title="Length")

// Calculate indicators
sma = ta.sma(close, length)
rsi = ta.rsi(close, length)

// Entry conditions
long_condition = close > sma and rsi < 30
short_condition = close < sma and rsi > 70

// Execute trades
if long_condition
    strategy.entry("Long", strategy.long)

if short_condition
    strategy.entry("Short", strategy.short)
'''


@pytest.fixture
def sample_strategy_data():
    """Sample strategy data for testing"""
    return {
        'id': 'sample_strategy',
        'name': 'Sample Test Strategy',
        'description': 'A sample strategy for testing purposes',
        'pine_code': '''
//@version=5
strategy("Sample Strategy", overlay=true)
sma = ta.sma(close, 20)
if close > sma
    strategy.entry("Long", strategy.long)
''',
        'parameters': {
            'sma_length': 20,
            'risk_per_trade': 0.02
        },
        'tags': ['test', 'sample', 'sma'],
        'created_at': '2025-01-01T00:00:00Z',
        'updated_at': '2025-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_backtest_request():
    """Sample backtest request data"""
    return {
        'strategy_id': 'test_strategy',
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 10000,
        'commission': 0.001
    }


@pytest.fixture
def sample_conversion_request():
    """Sample conversion request data"""
    return {
        'pine_code': '''
//@version=5
strategy("Test", overlay=true)
sma = ta.sma(close, 14)
if close > sma
    strategy.entry("Long", strategy.long)
''',
        'target_format': 'python',
        'include_comments': True,
        'optimization_level': 'standard'
    }


# Test environment setup
@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Set up test environment"""
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    os.environ['API_VERSION'] = '1.0.0'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Ensure test database is used
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    yield
    
    # Cleanup environment variables
    test_vars = ['FLASK_ENV', 'TESTING', 'API_VERSION', 'LOG_LEVEL', 'DATABASE_URL']
    for var in test_vars:
        os.environ.pop(var, None)


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (slower)"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Mark integration tests
        if "integration" in item.name or "Integration" in str(item.cls):
            item.add_marker(pytest.mark.integration)
        
        # Mark performance tests
        if "performance" in item.name or "Performance" in str(item.cls):
            item.add_marker(pytest.mark.performance)
        
        # Mark security tests
        if "security" in item.name or "Security" in str(item.cls):
            item.add_marker(pytest.mark.security)
        
        # Mark slow tests
        if any(word in item.name.lower() for word in ["load", "concurrent", "stress"]):
            item.add_marker(pytest.mark.slow)


# Test reporting hooks
@pytest.fixture(autouse=True)
def log_test_info(request):
    """Log test information for debugging"""
    test_name = request.node.name
    test_class = request.cls.__name__ if request.cls else "N/A"
    
    print(f"\n🧪 Running test: {test_class}::{test_name}")
    yield
    print(f"✅ Completed test: {test_class}::{test_name}")


# Error handling for tests
@pytest.fixture
def handle_test_errors():
    """Handle and log test errors gracefully"""
    try:
        yield
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        raise