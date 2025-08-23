"""
Performance Optimization Package
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

High-performance caching and optimization system for PineOpt API,
specifically optimized for historical market data access patterns.
"""

from .cache_manager import CacheManager, cache_response, cache_market_data, get_cache_manager
from .market_data_cache import MarketDataCache, HistoricalDataCache
from .query_optimizer import QueryOptimizer, optimize_market_queries, get_query_optimizer
from .memory_manager import MemoryManager, memory_profiler, get_memory_manager
from .connection_pool import ConnectionPoolManager, get_connection_pool_manager

__all__ = [
    'CacheManager',
    'cache_response', 
    'cache_market_data',
    'get_cache_manager',
    'MarketDataCache',
    'HistoricalDataCache', 
    'QueryOptimizer',
    'optimize_market_queries',
    'get_query_optimizer',
    'MemoryManager',
    'memory_profiler',
    'get_memory_manager',
    'ConnectionPoolManager',
    'get_connection_pool_manager'
]