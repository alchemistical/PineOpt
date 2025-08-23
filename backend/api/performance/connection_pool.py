"""
Connection Pool Manager for Performance Optimization
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

Advanced connection pooling for database and external API connections.
Optimized for trading applications with high-frequency data access patterns.
"""

import time
import threading
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from contextlib import contextmanager
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from queue import Queue, Empty, Full
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


@dataclass
class ConnectionStats:
    """Connection pool statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    connection_errors: int = 0
    average_response_time: float = 0.0
    peak_concurrent_connections: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PoolConnection:
    """Connection wrapper with metadata"""
    connection: Any
    created_at: float
    last_used: float
    use_count: int
    connection_id: str
    is_healthy: bool = True


class DatabaseConnectionPool:
    """High-performance database connection pool for SQLite"""
    
    def __init__(self, database_path: str, max_connections: int = 20, 
                 max_idle_time: int = 300, health_check_interval: int = 60):
        """
        Initialize database connection pool
        
        Args:
            database_path: Path to SQLite database
            max_connections: Maximum number of connections in pool
            max_idle_time: Maximum idle time before connection is closed (seconds)
            health_check_interval: Health check interval (seconds)
        """
        self.database_path = database_path
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        
        # Connection management
        self._available_connections: Queue[PoolConnection] = Queue(maxsize=max_connections)
        self._all_connections: Dict[str, PoolConnection] = {}
        self._connection_lock = threading.RLock()
        self._connection_counter = 0
        
        # Statistics tracking
        self.stats = ConnectionStats()
        
        # Health monitoring
        self._health_check_thread: Optional[threading.Thread] = None
        self._health_check_active = False
        
        # Connection optimization settings
        self.connection_pragmas = [
            "PRAGMA journal_mode = WAL",
            "PRAGMA synchronous = NORMAL", 
            "PRAGMA cache_size = 10000",
            "PRAGMA temp_store = memory",
            "PRAGMA mmap_size = 268435456"
        ]
        
        # Start health monitoring
        self._start_health_monitoring()
        
        logger.info(f"DatabaseConnectionPool initialized - Path: {database_path}, "
                   f"Max connections: {max_connections}")
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """
        Get database connection from pool with automatic return
        
        Args:
            timeout: Maximum time to wait for connection (seconds)
        """
        conn_wrapper = None
        start_time = time.time()
        
        try:
            conn_wrapper = self._acquire_connection(timeout)
            yield conn_wrapper.connection
            
        except Exception as e:
            # Mark connection as unhealthy if error occurs
            if conn_wrapper:
                conn_wrapper.is_healthy = False
            logger.error(f"Database connection error: {e}")
            raise
            
        finally:
            if conn_wrapper:
                self._release_connection(conn_wrapper)
                
                # Update statistics
                response_time = time.time() - start_time
                self._update_stats(response_time)
    
    def execute_query(self, query: str, params: tuple = (), timeout: float = 30.0) -> List[Dict[str, Any]]:
        """
        Execute query using pooled connection
        
        Args:
            query: SQL query string
            params: Query parameters
            timeout: Connection timeout
        """
        with self.get_connection(timeout) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Convert results to list of dictionaries
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            
            return []
    
    def execute_many(self, query: str, param_list: List[tuple], timeout: float = 30.0) -> int:
        """
        Execute query with multiple parameter sets
        
        Args:
            query: SQL query string
            param_list: List of parameter tuples
            timeout: Connection timeout
        
        Returns:
            Number of affected rows
        """
        with self.get_connection(timeout) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, param_list)
            conn.commit()
            return cursor.rowcount
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection pool statistics"""
        with self._connection_lock:
            idle_count = self._available_connections.qsize()
            active_count = len(self._all_connections) - idle_count
            
            # Update current stats
            self.stats.total_connections = len(self._all_connections)
            self.stats.active_connections = active_count
            self.stats.idle_connections = idle_count
            self.stats.peak_concurrent_connections = max(
                self.stats.peak_concurrent_connections, 
                active_count
            )
            
            return {
                'total_connections': self.stats.total_connections,
                'active_connections': self.stats.active_connections,
                'idle_connections': self.stats.idle_connections,
                'failed_connections': self.stats.failed_connections,
                'max_connections': self.max_connections,
                'utilization_percent': (active_count / self.max_connections) * 100,
                'total_requests': self.stats.total_requests,
                'connection_errors': self.stats.connection_errors,
                'average_response_time_ms': self.stats.average_response_time * 1000,
                'peak_concurrent_connections': self.stats.peak_concurrent_connections,
                'pool_health': self._assess_pool_health(),
                'uptime_seconds': (datetime.now() - self.stats.created_at).total_seconds()
            }
    
    def cleanup_idle_connections(self) -> int:
        """Clean up idle connections that exceed max idle time"""
        cleaned_count = 0
        current_time = time.time()
        
        with self._connection_lock:
            # Get all idle connections to check
            temp_connections = []
            
            while not self._available_connections.empty():
                try:
                    conn_wrapper = self._available_connections.get_nowait()
                    
                    # Check if connection is too old
                    if current_time - conn_wrapper.last_used > self.max_idle_time:
                        # Close the connection
                        try:
                            conn_wrapper.connection.close()
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"Error closing idle connection: {e}")
                        
                        # Remove from tracking
                        self._all_connections.pop(conn_wrapper.connection_id, None)
                    else:
                        # Keep the connection
                        temp_connections.append(conn_wrapper)
                        
                except Empty:
                    break
            
            # Put back the connections we're keeping
            for conn_wrapper in temp_connections:
                try:
                    self._available_connections.put_nowait(conn_wrapper)
                except Full:
                    # This shouldn't happen, but close connection if it does
                    try:
                        conn_wrapper.connection.close()
                    except Exception:
                        pass
        
        if cleaned_count > 0:
            logger.debug(f"Cleaned up {cleaned_count} idle database connections")
        
        return cleaned_count
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        with self._connection_lock:
            # Stop health monitoring
            self._health_check_active = False
            if self._health_check_thread:
                self._health_check_thread.join(timeout=5)
            
            # Close all connections
            closed_count = 0
            for conn_wrapper in self._all_connections.values():
                try:
                    conn_wrapper.connection.close()
                    closed_count += 1
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
            
            # Clear all tracking structures
            self._all_connections.clear()
            
            # Clear the queue
            while not self._available_connections.empty():
                try:
                    self._available_connections.get_nowait()
                except Empty:
                    break
        
        logger.info(f"Closed {closed_count} database connections")
    
    def _acquire_connection(self, timeout: float) -> PoolConnection:
        """Acquire connection from pool or create new one"""
        start_time = time.time()
        
        # Try to get existing connection first
        while time.time() - start_time < timeout:
            try:
                conn_wrapper = self._available_connections.get_nowait()
                
                # Check if connection is still healthy
                if self._test_connection_health(conn_wrapper):
                    conn_wrapper.last_used = time.time()
                    conn_wrapper.use_count += 1
                    return conn_wrapper
                else:
                    # Connection is unhealthy, remove it
                    with self._connection_lock:
                        self._all_connections.pop(conn_wrapper.connection_id, None)
                    
                    try:
                        conn_wrapper.connection.close()
                    except Exception:
                        pass
                    
            except Empty:
                # No connections available, try to create new one
                break
            
            time.sleep(0.01)  # Small delay before retry
        
        # Create new connection if under limit
        with self._connection_lock:
            if len(self._all_connections) < self.max_connections:
                return self._create_new_connection()
        
        # Wait for connection to become available
        try:
            conn_wrapper = self._available_connections.get(timeout=timeout)
            conn_wrapper.last_used = time.time()
            conn_wrapper.use_count += 1
            return conn_wrapper
        except Empty:
            self.stats.connection_errors += 1
            raise TimeoutError(f"Timeout waiting for database connection after {timeout}s")
    
    def _create_new_connection(self) -> PoolConnection:
        """Create new database connection"""
        try:
            # Create SQLite connection
            conn = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            
            # Set row factory for dict-like access
            conn.row_factory = sqlite3.Row
            
            # Apply optimization pragmas
            for pragma in self.connection_pragmas:
                try:
                    conn.execute(pragma)
                except sqlite3.Error as e:
                    logger.warning(f"Failed to apply pragma '{pragma}': {e}")
            
            # Create connection wrapper
            self._connection_counter += 1
            connection_id = f"db_conn_{self._connection_counter}"
            
            conn_wrapper = PoolConnection(
                connection=conn,
                created_at=time.time(),
                last_used=time.time(),
                use_count=1,
                connection_id=connection_id,
                is_healthy=True
            )
            
            # Track the connection
            self._all_connections[connection_id] = conn_wrapper
            
            logger.debug(f"Created new database connection: {connection_id}")
            return conn_wrapper
            
        except Exception as e:
            self.stats.failed_connections += 1
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def _release_connection(self, conn_wrapper: PoolConnection):
        """Release connection back to pool"""
        if conn_wrapper.is_healthy:
            try:
                self._available_connections.put_nowait(conn_wrapper)
            except Full:
                # Pool is full, close the connection
                try:
                    conn_wrapper.connection.close()
                except Exception:
                    pass
                
                with self._connection_lock:
                    self._all_connections.pop(conn_wrapper.connection_id, None)
        else:
            # Connection is unhealthy, close it
            try:
                conn_wrapper.connection.close()
            except Exception:
                pass
            
            with self._connection_lock:
                self._all_connections.pop(conn_wrapper.connection_id, None)
    
    def _test_connection_health(self, conn_wrapper: PoolConnection) -> bool:
        """Test if connection is still healthy"""
        try:
            # Simple query to test connection
            cursor = conn_wrapper.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception:
            return False
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        self._health_check_active = True
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop, 
            daemon=True
        )
        self._health_check_thread.start()
        logger.debug("Database connection health monitoring started")
    
    def _health_check_loop(self):
        """Background health check loop"""
        while self._health_check_active:
            try:
                # Clean up idle connections
                self.cleanup_idle_connections()
                
                # Sleep for health check interval
                for _ in range(self.health_check_interval):
                    if not self._health_check_active:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Database health check error: {e}")
                time.sleep(30)
    
    def _update_stats(self, response_time: float):
        """Update connection statistics"""
        self.stats.total_requests += 1
        
        # Update running average response time
        if self.stats.total_requests == 1:
            self.stats.average_response_time = response_time
        else:
            self.stats.average_response_time = (
                (self.stats.average_response_time * (self.stats.total_requests - 1) + response_time) / 
                self.stats.total_requests
            )
    
    def _assess_pool_health(self) -> str:
        """Assess overall pool health"""
        error_rate = (self.stats.connection_errors / max(self.stats.total_requests, 1)) * 100
        utilization = (self.stats.active_connections / self.max_connections) * 100
        
        if error_rate > 10:
            return 'critical'
        elif error_rate > 5 or utilization > 90:
            return 'warning'
        elif utilization > 70:
            return 'moderate'
        else:
            return 'healthy'
    
    def __del__(self):
        """Cleanup when pool is destroyed"""
        self.close_all_connections()


class HTTPConnectionPool:
    """High-performance HTTP connection pool for external API calls"""
    
    def __init__(self, max_connections: int = 50, max_retries: int = 3, 
                 backoff_factor: float = 0.3, timeout: tuple = (10, 30)):
        """
        Initialize HTTP connection pool
        
        Args:
            max_connections: Maximum connections per host
            max_retries: Maximum retry attempts
            backoff_factor: Retry backoff factor
            timeout: Connection and read timeout (connect_timeout, read_timeout)
        """
        self.max_connections = max_connections
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        
        # Create requests session with optimized settings
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=max_connections,
            pool_block=False
        )
        
        # Mount adapters for both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'PineOpt-Trading-Bot/1.0',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        # Statistics tracking
        self.stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'total_response_time': 0.0,
            'retry_attempts': 0
        }
        
        logger.info(f"HTTPConnectionPool initialized - Max connections: {max_connections}")
    
    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, 
            timeout: Optional[tuple] = None) -> requests.Response:
        """Execute GET request using connection pool"""
        return self._make_request('GET', url, params=params, headers=headers, timeout=timeout)
    
    def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None,
             headers: Optional[Dict] = None, timeout: Optional[tuple] = None) -> requests.Response:
        """Execute POST request using connection pool"""
        return self._make_request('POST', url, data=data, json=json, headers=headers, timeout=timeout)
    
    def put(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None,
            headers: Optional[Dict] = None, timeout: Optional[tuple] = None) -> requests.Response:
        """Execute PUT request using connection pool"""
        return self._make_request('PUT', url, data=data, json=json, headers=headers, timeout=timeout)
    
    def delete(self, url: str, headers: Optional[Dict] = None, 
               timeout: Optional[tuple] = None) -> requests.Response:
        """Execute DELETE request using connection pool"""
        return self._make_request('DELETE', url, headers=headers, timeout=timeout)
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with statistics tracking"""
        start_time = time.time()
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            
            # Update statistics
            response_time = time.time() - start_time
            self._update_http_stats(response_time, success=True)
            
            return response
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self._update_http_stats(response_time, success=False)
            
            logger.error(f"HTTP request failed [{method} {url}]: {e}")
            raise
    
    def get_http_stats(self) -> Dict[str, Any]:
        """Get HTTP connection pool statistics"""
        total_requests = self.stats['requests_made']
        avg_response_time = (
            self.stats['total_response_time'] / max(total_requests, 1)
        )
        
        return {
            'total_requests': total_requests,
            'failed_requests': self.stats['requests_failed'],
            'success_rate_percent': (
                ((total_requests - self.stats['requests_failed']) / max(total_requests, 1)) * 100
            ),
            'average_response_time_ms': avg_response_time * 1000,
            'retry_attempts': self.stats['retry_attempts'],
            'max_connections': self.max_connections,
            'session_health': 'active' if self.session else 'closed'
        }
    
    def _update_http_stats(self, response_time: float, success: bool):
        """Update HTTP statistics"""
        self.stats['requests_made'] += 1
        self.stats['total_response_time'] += response_time
        
        if not success:
            self.stats['requests_failed'] += 1
    
    def close(self):
        """Close HTTP session and cleanup connections"""
        if self.session:
            self.session.close()
            logger.debug("HTTP connection pool closed")


class ConnectionPoolManager:
    """Centralized connection pool manager for all connection types"""
    
    def __init__(self, db_path: str = None, max_db_connections: int = 20,
                 max_http_connections: int = 50):
        """
        Initialize connection pool manager
        
        Args:
            db_path: Database file path
            max_db_connections: Maximum database connections
            max_http_connections: Maximum HTTP connections
        """
        self.db_path = db_path
        
        # Initialize connection pools
        self._db_pool: Optional[DatabaseConnectionPool] = None
        self._http_pool: Optional[HTTPConnectionPool] = None
        
        # Pool configuration
        self.max_db_connections = max_db_connections
        self.max_http_connections = max_http_connections
        
        logger.info("ConnectionPoolManager initialized")
    
    def get_db_pool(self) -> DatabaseConnectionPool:
        """Get or create database connection pool"""
        if self._db_pool is None:
            if not self.db_path:
                raise ValueError("Database path not configured")
            
            self._db_pool = DatabaseConnectionPool(
                database_path=self.db_path,
                max_connections=self.max_db_connections
            )
        
        return self._db_pool
    
    def get_http_pool(self) -> HTTPConnectionPool:
        """Get or create HTTP connection pool"""
        if self._http_pool is None:
            self._http_pool = HTTPConnectionPool(
                max_connections=self.max_http_connections
            )
        
        return self._http_pool
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics from all connection pools"""
        stats = {
            'database_pool': None,
            'http_pool': None,
            'manager_status': 'active'
        }
        
        if self._db_pool:
            stats['database_pool'] = self._db_pool.get_pool_stats()
        
        if self._http_pool:
            stats['http_pool'] = self._http_pool.get_http_stats()
        
        return stats
    
    def cleanup_all_pools(self):
        """Cleanup all connection pools"""
        if self._db_pool:
            self._db_pool.cleanup_idle_connections()
            logger.debug("Database pool cleanup completed")
        
        if self._http_pool:
            # HTTP pool cleanup is handled automatically by requests
            pass
        
        logger.info("All connection pools cleaned up")
    
    def close_all_pools(self):
        """Close all connection pools"""
        if self._db_pool:
            self._db_pool.close_all_connections()
            self._db_pool = None
        
        if self._http_pool:
            self._http_pool.close()
            self._http_pool = None
        
        logger.info("All connection pools closed")
    
    def __del__(self):
        """Cleanup when manager is destroyed"""
        self.close_all_pools()


# Global connection pool manager instance
_connection_pool_manager: Optional[ConnectionPoolManager] = None


def get_connection_pool_manager(db_path: str = None) -> ConnectionPoolManager:
    """Get or create global connection pool manager instance"""
    global _connection_pool_manager
    if _connection_pool_manager is None:
        _connection_pool_manager = ConnectionPoolManager(db_path)
    return _connection_pool_manager