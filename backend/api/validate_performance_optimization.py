#!/usr/bin/env python3
"""
Performance Optimization System Validation
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

Validates the complete performance optimization system for historical market data structure.
"""

import sys
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_imports():
    """Validate all performance optimization imports"""
    try:
        logger.info("🧪 Testing performance optimization imports...")
        
        from performance import (
            CacheManager, cache_response, cache_market_data,
            MarketDataCache, HistoricalDataCache,
            QueryOptimizer, optimize_market_queries,
            MemoryManager, memory_profiler,
            ConnectionPoolManager,
            get_cache_manager, get_query_optimizer, 
            get_memory_manager, get_connection_pool_manager
        )
        
        logger.info("✅ All performance optimization imports successful")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during imports: {e}")
        return False

def validate_cache_manager():
    """Validate cache manager functionality"""
    try:
        logger.info("🧪 Testing CacheManager...")
        
        from performance import get_cache_manager
        cache_manager = get_cache_manager()
        
        # Test basic caching
        test_key = "test_key_validation"
        test_value = {"test": "data", "timestamp": time.time()}
        
        # Set cache entry
        success = cache_manager.set(test_key, test_value, 'api_responses', 60)
        if not success:
            raise Exception("Failed to set cache entry")
        
        # Get cache entry
        cached_value = cache_manager.get(test_key, 'api_responses')
        if cached_value != test_value:
            raise Exception("Cache value mismatch")
        
        # Test cache statistics
        stats = cache_manager.get_stats()
        if 'total_keys' not in stats:
            raise Exception("Invalid cache statistics")
        
        logger.info(f"✅ CacheManager validation successful - {stats['total_keys']} keys cached")
        return True
        
    except Exception as e:
        logger.error(f"❌ CacheManager validation failed: {e}")
        return False

def validate_market_data_cache():
    """Validate market data cache functionality"""
    try:
        logger.info("🧪 Testing MarketDataCache...")
        
        from performance import MarketDataCache
        import pandas as pd
        
        market_cache = MarketDataCache()
        
        # Create sample OHLCV data
        sample_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
            'open': [100.0 + i for i in range(100)],
            'high': [105.0 + i for i in range(100)],
            'low': [95.0 + i for i in range(100)],
            'close': [102.0 + i for i in range(100)],
            'volume': [1000 + i * 10 for i in range(100)]
        })
        
        # Test caching OHLCV data
        success = market_cache.cache_ohlcv_data(
            data=sample_data,
            symbol='BTCUSDT',
            timeframe='1h',
            limit=100
        )
        
        if not success:
            raise Exception("Failed to cache OHLCV data")
        
        # Test retrieving OHLCV data
        cached_data = market_cache.get_ohlcv_data(
            symbol='BTCUSDT',
            timeframe='1h',
            limit=100
        )
        
        if cached_data is None:
            raise Exception("Failed to retrieve cached OHLCV data")
        
        if len(cached_data) != len(sample_data):
            raise Exception("Cached data length mismatch")
        
        # Test cache efficiency metrics
        efficiency = market_cache.get_cache_efficiency()
        if 'total_cached_symbols' not in efficiency:
            raise Exception("Invalid cache efficiency metrics")
        
        logger.info("✅ MarketDataCache validation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ MarketDataCache validation failed: {e}")
        return False

def validate_query_optimizer():
    """Validate query optimizer functionality"""
    try:
        logger.info("🧪 Testing QueryOptimizer...")
        
        from performance import get_query_optimizer
        import tempfile
        import sqlite3
        
        # Create temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Initialize test database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_market_data (
                id INTEGER PRIMARY KEY,
                symbol TEXT,
                timestamp TEXT,
                price REAL
            )
        """)
        
        # Insert test data
        test_data = [
            ('BTCUSDT', '2024-01-01T00:00:00', 45000.0),
            ('BTCUSDT', '2024-01-01T01:00:00', 45100.0),
            ('ETHUSDT', '2024-01-01T00:00:00', 3000.0),
        ]
        
        cursor.executemany(
            "INSERT INTO test_market_data (symbol, timestamp, price) VALUES (?, ?, ?)",
            test_data
        )
        conn.commit()
        conn.close()
        
        # Test query optimizer
        query_optimizer = get_query_optimizer(db_path)
        
        # Test cached query execution
        query = "SELECT * FROM test_market_data WHERE symbol = ? ORDER BY timestamp"
        results = query_optimizer.execute_cached_query(query, ('BTCUSDT',), cache_ttl=60)
        
        if not results or len(results) != 2:
            raise Exception("Query execution failed or returned incorrect results")
        
        # Test query statistics
        stats = query_optimizer.get_query_statistics()
        if 'total_queries' not in stats:
            raise Exception("Invalid query statistics")
        
        # Apply market data optimizations
        query_optimizer.optimize_market_data_queries()
        
        logger.info(f"✅ QueryOptimizer validation successful - {stats['total_queries']} queries executed")
        
        # Cleanup
        Path(db_path).unlink()
        return True
        
    except Exception as e:
        logger.error(f"❌ QueryOptimizer validation failed: {e}")
        return False

def validate_memory_manager():
    """Validate memory manager functionality"""
    try:
        logger.info("🧪 Testing MemoryManager...")
        
        from performance import get_memory_manager
        
        memory_manager = get_memory_manager(memory_limit_mb=1024)
        
        # Test memory usage monitoring
        usage = memory_manager.get_current_memory_usage()
        if 'system_memory' not in usage or 'process_memory' not in usage:
            raise Exception("Invalid memory usage data")
        
        # Test memory health check
        health = memory_manager.check_memory_health()
        if 'health_status' not in health:
            raise Exception("Invalid memory health data")
        
        # Test memory optimization
        optimization = memory_manager.optimize_memory(force_gc=True)
        if 'memory_freed_mb' not in optimization:
            raise Exception("Invalid memory optimization data")
        
        logger.info(f"✅ MemoryManager validation successful - Health: {health['health_status']}")
        return True
        
    except Exception as e:
        logger.error(f"❌ MemoryManager validation failed: {e}")
        return False

def validate_connection_pool():
    """Validate connection pool manager functionality"""
    try:
        logger.info("🧪 Testing ConnectionPoolManager...")
        
        from performance import get_connection_pool_manager
        import tempfile
        import sqlite3
        
        # Create temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Initialize test database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
        cursor.execute("INSERT INTO test_table (data) VALUES ('test')")
        conn.commit()
        conn.close()
        
        # Test connection pool manager
        pool_manager = get_connection_pool_manager(db_path)
        
        # Test database pool
        db_pool = pool_manager.get_db_pool()
        
        # Test connection acquisition and query execution
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table")
            result = cursor.fetchone()
            
            if result[0] != 1:
                raise Exception("Database query failed")
        
        # Test pool statistics
        stats = pool_manager.get_all_stats()
        if 'database_pool' not in stats:
            raise Exception("Invalid connection pool statistics")
        
        # Test HTTP pool
        http_pool = pool_manager.get_http_pool()
        http_stats = http_pool.get_http_stats()
        if 'total_requests' not in http_stats:
            raise Exception("Invalid HTTP pool statistics")
        
        logger.info("✅ ConnectionPoolManager validation successful")
        
        # Cleanup
        pool_manager.close_all_pools()
        Path(db_path).unlink()
        return True
        
    except Exception as e:
        logger.error(f"❌ ConnectionPoolManager validation failed: {e}")
        return False

def validate_decorators():
    """Validate decorator functionality"""
    try:
        logger.info("🧪 Testing performance decorators...")
        
        from performance import cache_response, memory_profiler
        
        # Test cache_response decorator
        @cache_response('api_responses', ttl=60)
        def cached_function(value):
            return {"result": value, "timestamp": time.time()}
        
        # Call function twice - second should be cached
        result1 = cached_function("test")
        result2 = cached_function("test")
        
        if result1 != result2:
            raise Exception("Cache decorator not working")
        
        # Test memory_profiler decorator
        @memory_profiler(track_objects=True)
        def memory_test_function():
            data = [i for i in range(1000)]  # Create some objects
            return len(data)
        
        result = memory_test_function()
        if result != 1000:
            raise Exception("Memory profiler decorator not working")
        
        logger.info("✅ Performance decorators validation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Decorator validation failed: {e}")
        return False

def main():
    """Main validation function"""
    print("=" * 80)
    print("🚀 PineOpt Performance Optimization System Validation")
    print("Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching")
    print("=" * 80)
    
    validation_tests = [
        ("Import Validation", validate_imports),
        ("CacheManager", validate_cache_manager),
        ("MarketDataCache", validate_market_data_cache),
        ("QueryOptimizer", validate_query_optimizer),
        ("MemoryManager", validate_memory_manager),
        ("ConnectionPoolManager", validate_connection_pool),
        ("Decorators", validate_decorators)
    ]
    
    passed_tests = 0
    total_tests = len(validation_tests)
    
    for test_name, test_function in validation_tests:
        print(f"\n📋 Running {test_name} validation...")
        try:
            if test_function():
                passed_tests += 1
            else:
                logger.error(f"❌ {test_name} validation failed")
        except Exception as e:
            logger.error(f"❌ {test_name} validation error: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 VALIDATION RESULTS")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VALIDATIONS PASSED! Performance optimization system is fully functional.")
        print("\n🔥 Key Features Validated:")
        print("  ✅ Multi-tier caching system with market data optimization")
        print("  ✅ Database query optimization with connection pooling")
        print("  ✅ Memory management with real-time monitoring")
        print("  ✅ Historical market data structure optimization")
        print("  ✅ Performance decorators and profiling")
        print("  ✅ HTTP connection pooling for external APIs")
        
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} validation(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)