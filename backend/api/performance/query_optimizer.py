"""
Database Query Optimizer
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

Advanced query optimization for market data and strategy databases.
Implements query caching, index optimization, and connection pooling.
"""

import time
import sqlite3
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from functools import wraps
from contextlib import contextmanager
from datetime import datetime, timedelta
import threading
from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimizer with intelligent caching and connection management"""
    
    def __init__(self, database_path: str, max_connections: int = 10):
        """
        Initialize query optimizer
        
        Args:
            database_path: Path to SQLite database
            max_connections: Maximum number of database connections
        """
        self.database_path = database_path
        self.max_connections = max_connections
        
        # Connection pool management
        self._connection_pool = []
        self._pool_lock = threading.Lock()
        self._active_connections = 0
        
        # Query performance tracking
        self.query_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_execution_time': 0.0,
            'slow_queries': [],  # Store queries that take > 1s
            'query_frequency': {},  # Track most common queries
        }
        
        # Query optimization settings
        self.slow_query_threshold = 1.0  # seconds
        self.cache_enabled = True
        self.explain_analyze_enabled = False
        
        # Initialize database optimizations
        self._initialize_optimizations()
        
        logger.info(f"QueryOptimizer initialized for {database_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool with automatic management"""
        conn = None
        try:
            conn = self._get_pooled_connection()
            yield conn
        finally:
            if conn:
                self._return_connection(conn)
    
    def execute_cached_query(self, query: str, params: Tuple = (), 
                            cache_ttl: int = 300, cache_type: str = 'api_responses') -> List[Dict]:
        """
        Execute query with intelligent caching
        
        Args:
            query: SQL query string
            params: Query parameters
            cache_ttl: Cache time to live in seconds
            cache_type: Type of cache to use
        """
        # Generate cache key
        cache_key = self._generate_query_cache_key(query, params)
        
        # Try to get from cache first
        if self.cache_enabled:
            cache_manager = get_cache_manager()
            cached_result = cache_manager.get(cache_key, cache_type)
            if cached_result is not None:
                self.query_stats['cache_hits'] += 1
                logger.debug(f"Query cache HIT - key: {cache_key[:8]}...")
                return cached_result
        
        # Execute query
        start_time = time.time()
        result = self._execute_query(query, params)
        execution_time = time.time() - start_time
        
        # Update statistics
        self._update_query_stats(query, execution_time, cache_miss=True)
        
        # Cache the result
        if self.cache_enabled and result is not None:
            cache_manager = get_cache_manager()
            cache_manager.set(cache_key, result, cache_type, cache_ttl)
        
        logger.debug(f"Query executed in {execution_time:.3f}s - "
                    f"Cache key: {cache_key[:8]}...")
        
        return result
    
    def optimize_market_data_queries(self) -> None:
        """Apply market data specific optimizations"""
        optimizations = [
            # Create indices for common market data queries
            "CREATE INDEX IF NOT EXISTS idx_symbol_timestamp ON market_data(symbol, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON market_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_symbol_timeframe ON market_data(symbol, timeframe)",
            
            # Create indices for strategy data
            "CREATE INDEX IF NOT EXISTS idx_strategy_created ON strategies(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_strategy_name ON strategies(name)",
            
            # Create indices for backtest results
            "CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy_id)",
            "CREATE INDEX IF NOT EXISTS idx_backtest_created ON backtest_results(created_at)",
        ]
        
        with self.get_connection() as conn:
            for optimization in optimizations:
                try:
                    conn.execute(optimization)
                    logger.debug(f"Applied optimization: {optimization[:50]}...")
                except sqlite3.Error as e:
                    logger.warning(f"Failed to apply optimization: {e}")
            
            conn.commit()
        
        logger.info("Market data query optimizations applied")
    
    def analyze_query_performance(self, query: str, params: Tuple = ()) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN QUERY PLAN
        
        Args:
            query: SQL query to analyze
            params: Query parameters
            
        Returns:
            Dictionary with performance analysis
        """
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get query plan
            cursor.execute(explain_query, params)
            query_plan = cursor.fetchall()
            
            # Execute query and measure time
            start_time = time.time()
            cursor.execute(query, params)
            result = cursor.fetchall()
            execution_time = time.time() - start_time
        
        analysis = {
            'query': query[:100] + ('...' if len(query) > 100 else ''),
            'execution_time_ms': execution_time * 1000,
            'result_count': len(result),
            'query_plan': [
                {
                    'id': row[0],
                    'parent': row[1],
                    'detail': row[3]
                } for row in query_plan
            ],
            'performance_rating': self._rate_query_performance(execution_time, len(result)),
            'optimization_suggestions': self._get_optimization_suggestions(query, query_plan)
        }
        
        return analysis
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries for optimization review"""
        return sorted(
            self.query_stats['slow_queries'],
            key=lambda x: x['execution_time'],
            reverse=True
        )[:limit]
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get comprehensive query performance statistics"""
        total_queries = self.query_stats['total_queries']
        cache_hits = self.query_stats['cache_hits']
        cache_misses = self.query_stats['cache_misses']
        
        return {
            'total_queries': total_queries,
            'cache_hit_rate': (cache_hits / max(total_queries, 1)) * 100,
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'average_execution_time_ms': (
                (self.query_stats['total_execution_time'] / max(total_queries, 1)) * 1000
            ),
            'slow_query_count': len(self.query_stats['slow_queries']),
            'most_frequent_queries': sorted(
                self.query_stats['query_frequency'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'active_connections': self._active_connections,
            'pool_size': len(self._connection_pool)
        }
    
    def clear_query_cache(self) -> int:
        """Clear all cached query results"""
        cache_manager = get_cache_manager()
        return cache_manager.clear('api_responses')
    
    def vacuum_database(self) -> None:
        """Optimize database storage and performance"""
        logger.info("Starting database VACUUM operation...")
        start_time = time.time()
        
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
        
        vacuum_time = time.time() - start_time
        logger.info(f"Database VACUUM completed in {vacuum_time:.2f} seconds")
    
    def _initialize_optimizations(self) -> None:
        """Initialize database-level optimizations"""
        pragma_settings = [
            "PRAGMA journal_mode = WAL",  # Write-Ahead Logging for better concurrency
            "PRAGMA synchronous = NORMAL",  # Balance safety and performance
            "PRAGMA cache_size = 10000",  # 10MB cache
            "PRAGMA temp_store = memory",  # Store temp tables in memory
            "PRAGMA mmap_size = 268435456",  # 256MB memory mapped I/O
        ]
        
        with self.get_connection() as conn:
            for pragma in pragma_settings:
                try:
                    conn.execute(pragma)
                    logger.debug(f"Applied pragma: {pragma}")
                except sqlite3.Error as e:
                    logger.warning(f"Failed to apply pragma {pragma}: {e}")
    
    def _get_pooled_connection(self) -> sqlite3.Connection:
        """Get connection from pool or create new one"""
        with self._pool_lock:
            if self._connection_pool:
                conn = self._connection_pool.pop()
                logger.debug("Reused pooled connection")
                return conn
            
            if self._active_connections < self.max_connections:
                conn = sqlite3.connect(self.database_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row  # Enable column access by name
                self._active_connections += 1
                logger.debug(f"Created new connection ({self._active_connections}/{self.max_connections})")
                return conn
            
            # If pool is full, wait and retry (simple implementation)
            logger.warning("Connection pool exhausted, waiting...")
            time.sleep(0.1)
            return self._get_pooled_connection()
    
    def _return_connection(self, conn: sqlite3.Connection) -> None:
        """Return connection to pool"""
        with self._pool_lock:
            if len(self._connection_pool) < self.max_connections // 2:
                self._connection_pool.append(conn)
                logger.debug("Returned connection to pool")
            else:
                # Close excess connections
                conn.close()
                self._active_connections -= 1
                logger.debug("Closed excess connection")
    
    def _execute_query(self, query: str, params: Tuple) -> List[Dict]:
        """Execute query and return results as list of dictionaries"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Convert rows to dictionaries
            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = []
            
            for row in cursor.fetchall():
                result_dict = {}
                for i, column in enumerate(columns):
                    result_dict[column] = row[i]
                results.append(result_dict)
            
            return results
    
    def _generate_query_cache_key(self, query: str, params: Tuple) -> str:
        """Generate cache key for query and parameters"""
        key_data = f"{query}|{str(params)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_query_stats(self, query: str, execution_time: float, cache_miss: bool = False) -> None:
        """Update query performance statistics"""
        self.query_stats['total_queries'] += 1
        self.query_stats['total_execution_time'] += execution_time
        
        if cache_miss:
            self.query_stats['cache_misses'] += 1
        
        # Track query frequency
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        self.query_stats['query_frequency'][query_hash] = (
            self.query_stats['query_frequency'].get(query_hash, 0) + 1
        )
        
        # Track slow queries
        if execution_time > self.slow_query_threshold:
            slow_query_info = {
                'query': query[:200] + ('...' if len(query) > 200 else ''),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.query_stats['slow_queries'].append(slow_query_info)
            
            # Keep only recent slow queries (max 50)
            if len(self.query_stats['slow_queries']) > 50:
                self.query_stats['slow_queries'] = self.query_stats['slow_queries'][-50:]
    
    def _rate_query_performance(self, execution_time: float, result_count: int) -> str:
        """Rate query performance based on execution time and result count"""
        if execution_time < 0.01:
            return "Excellent"
        elif execution_time < 0.1:
            return "Good"
        elif execution_time < 0.5:
            return "Fair"
        elif execution_time < 1.0:
            return "Slow"
        else:
            return "Very Slow"
    
    def _get_optimization_suggestions(self, query: str, query_plan: List) -> List[str]:
        """Generate optimization suggestions based on query analysis"""
        suggestions = []
        
        query_lower = query.lower()
        
        # Check for missing indices
        if 'scan' in str(query_plan).lower():
            suggestions.append("Consider adding indices for frequently queried columns")
        
        # Check for inefficient patterns
        if 'like' in query_lower and not query_lower.startswith('%'):
            suggestions.append("LIKE patterns starting with % are slow; consider full-text search")
        
        if 'order by' in query_lower and 'limit' not in query_lower:
            suggestions.append("Add LIMIT clause to ORDER BY queries when possible")
        
        if query_lower.count('join') > 3:
            suggestions.append("Complex multi-table joins may benefit from query restructuring")
        
        return suggestions


def optimize_market_queries(func):
    """Decorator to optimize market data queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log slow queries
        if execution_time > 1.0:
            logger.warning(f"Slow query in {func.__name__}: {execution_time:.3f}s")
        
        return result
    
    return wrapper


# Global query optimizer instance
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer(database_path: str = None) -> QueryOptimizer:
    """Get or create global query optimizer instance"""
    global _query_optimizer
    if _query_optimizer is None:
        db_path = database_path or "backend/database/pineopt_unified.db"
        _query_optimizer = QueryOptimizer(db_path)
        _query_optimizer.optimize_market_data_queries()
    return _query_optimizer