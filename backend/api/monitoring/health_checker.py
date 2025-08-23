"""
Health Checker for Advanced Monitoring & Metrics Collection
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Comprehensive system health monitoring with deep checks for all system components.
Provides detailed health status for databases, APIs, data providers, and services.
"""

import time
import sqlite3
import requests
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result"""
    component: str
    status: HealthStatus
    response_time_ms: float
    message: str
    details: Dict[str, Any]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health check to dictionary"""
        return {
            "component": self.component,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "checked_at": datetime.fromtimestamp(self.timestamp).isoformat()
        }


class HealthChecker:
    """Comprehensive system health monitoring with component-specific checks"""
    
    def __init__(self, check_interval: int = 300):
        """
        Initialize health checker
        
        Args:
            check_interval: Health check interval in seconds (default: 5 minutes)
        """
        self.check_interval = check_interval
        
        # Health check registry
        self.health_checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        
        # Health monitoring thread
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Health thresholds
        self.response_time_thresholds = {
            'database': 100.0,      # ms
            'api_endpoint': 500.0,  # ms
            'external_api': 2000.0, # ms
            'cache': 50.0           # ms
        }
        
        # Register default health checks
        self._register_default_checks()
        
        logger.info(f"HealthChecker initialized - Check interval: {check_interval}s")
    
    def _register_default_checks(self):
        """Register default health checks for trading system components"""
        self.register_health_check("database_main", self._check_main_database)
        self.register_health_check("database_unified", self._check_unified_database)
        self.register_health_check("cache_system", self._check_cache_system)
        self.register_health_check("performance_system", self._check_performance_system)
        self.register_health_check("memory_health", self._check_memory_health)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("binance_api", self._check_binance_api)
        self.register_health_check("system_resources", self._check_system_resources)
    
    def register_health_check(self, component: str, check_function: Callable):
        """Register a new health check function"""
        self.health_checks[component] = check_function
        logger.info(f"Registered health check: {component}")
    
    def unregister_health_check(self, component: str):
        """Unregister a health check"""
        if component in self.health_checks:
            del self.health_checks[component]
            if component in self.last_results:
                del self.last_results[component]
            logger.info(f"Unregistered health check: {component}")
    
    def run_health_check(self, component: str) -> HealthCheck:
        """Run a specific health check"""
        if component not in self.health_checks:
            return HealthCheck(
                component=component,
                status=HealthStatus.UNKNOWN,
                response_time_ms=0.0,
                message=f"Health check not registered: {component}",
                details={},
                timestamp=time.time()
            )
        
        start_time = time.time()
        try:
            result = self.health_checks[component]()
            response_time = (time.time() - start_time) * 1000
            
            # Update result with timing
            result.response_time_ms = response_time
            result.timestamp = time.time()
            
            # Store result
            self.last_results[component] = result
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Health check failed for {component}: {e}")
            
            error_result = HealthCheck(
                component=component,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                message=f"Health check error: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
            
            self.last_results[component] = error_result
            return error_result
    
    def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}
        
        for component in self.health_checks:
            results[component] = self.run_health_check(component)
        
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        results = self.run_all_health_checks()
        
        # Calculate overall status
        statuses = [result.status for result in results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate statistics
        healthy_count = sum(1 for s in statuses if s == HealthStatus.HEALTHY)
        warning_count = sum(1 for s in statuses if s == HealthStatus.WARNING)
        unhealthy_count = sum(1 for s in statuses if s == HealthStatus.UNHEALTHY)
        unknown_count = sum(1 for s in statuses if s == HealthStatus.UNKNOWN)
        
        avg_response_time = sum(r.response_time_ms for r in results.values()) / len(results)
        
        return {
            "overall_status": overall_status.value,
            "timestamp": time.time(),
            "checked_at": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(results),
                "healthy": healthy_count,
                "warning": warning_count,
                "unhealthy": unhealthy_count,
                "unknown": unknown_count,
                "avg_response_time_ms": avg_response_time
            },
            "components": {name: result.to_dict() for name, result in results.items()}
        }
    
    def _check_main_database(self) -> HealthCheck:
        """Check main strategies database health"""
        try:
            db_path = "strategies.db"
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Test strategies table if it exists
            strategy_count = 0
            try:
                cursor.execute("SELECT COUNT(*) FROM strategies")
                strategy_count = cursor.fetchone()[0]
            except sqlite3.Error:
                pass
            
            conn.close()
            
            return HealthCheck(
                component="database_main",
                status=HealthStatus.HEALTHY,
                response_time_ms=0.0,  # Will be filled by caller
                message=f"Database healthy - {table_count} tables, {strategy_count} strategies",
                details={
                    "database_path": db_path,
                    "table_count": table_count,
                    "strategy_count": strategy_count
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="database_main",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_unified_database(self) -> HealthCheck:
        """Check unified database health"""
        try:
            db_path = "../database/pineopt_unified.db"
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Test basic connectivity
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Check for key tables
            expected_tables = ['strategies', 'backtests', 'market_data']
            existing_tables = []
            
            for table in expected_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    existing_tables.append({"name": table, "records": count})
                except sqlite3.Error:
                    existing_tables.append({"name": table, "records": "missing"})
            
            conn.close()
            
            missing_tables = [t for t in existing_tables if t["records"] == "missing"]
            status = HealthStatus.WARNING if missing_tables else HealthStatus.HEALTHY
            
            return HealthCheck(
                component="database_unified",
                status=status,
                response_time_ms=0.0,
                message=f"Unified database - {table_count} tables total",
                details={
                    "database_path": db_path,
                    "total_tables": table_count,
                    "key_tables": existing_tables,
                    "missing_tables": len(missing_tables)
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="database_unified",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Unified database connection failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_cache_system(self) -> HealthCheck:
        """Check cache system health"""
        try:
            # Try to import and test cache system
            from performance import get_cache_manager
            cache_manager = get_cache_manager()
            
            # Test cache operations
            test_key = "health_check_test"
            test_value = {"timestamp": time.time(), "test": True}
            
            # Test set operation
            success = cache_manager.set(test_key, test_value, 'api_responses', 60)
            if not success:
                raise Exception("Cache set operation failed")
            
            # Test get operation
            retrieved_value = cache_manager.get(test_key, 'api_responses')
            if retrieved_value != test_value:
                raise Exception("Cache get operation failed")
            
            # Get cache statistics
            stats = cache_manager.get_stats()
            
            # Clean up test data
            cache_manager.delete(test_key)
            
            return HealthCheck(
                component="cache_system",
                status=HealthStatus.HEALTHY,
                response_time_ms=0.0,
                message=f"Cache system healthy - {stats['total_keys']} keys, "
                       f"{stats['hit_rate_percent']:.1f}% hit rate",
                details={
                    "total_keys": stats['total_keys'],
                    "hit_rate_percent": stats['hit_rate_percent'],
                    "memory_usage_mb": stats['total_size_mb'],
                    "memory_usage_percent": stats['memory_usage_percent']
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="cache_system",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Cache system error: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_performance_system(self) -> HealthCheck:
        """Check performance optimization system health"""
        try:
            from performance import get_memory_manager, get_query_optimizer
            
            # Check memory manager
            memory_manager = get_memory_manager()
            memory_health = memory_manager.check_memory_health()
            
            # Check query optimizer (simplified check)
            query_optimizer = get_query_optimizer()
            query_stats = query_optimizer.get_query_statistics()
            
            status = HealthStatus.HEALTHY
            if memory_health['health_status'] in ['warning', 'critical']:
                status = HealthStatus.WARNING
            
            return HealthCheck(
                component="performance_system",
                status=status,
                response_time_ms=0.0,
                message=f"Performance system - Memory: {memory_health['health_status']}, "
                       f"Queries: {query_stats['total_queries']}",
                details={
                    "memory_health": memory_health['health_status'],
                    "memory_usage_percent": memory_health['memory_usage_percent'],
                    "total_queries": query_stats['total_queries'],
                    "cache_hit_rate": query_stats['cache_hit_rate'],
                    "active_connections": query_stats['active_connections']
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="performance_system",
                status=HealthStatus.WARNING,
                response_time_ms=0.0,
                message=f"Performance system check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_memory_health(self) -> HealthCheck:
        """Check system memory health"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Determine status based on memory usage
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical memory usage"
            elif memory.percent > 80:
                status = HealthStatus.WARNING
                message = "High memory usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Memory usage normal"
            
            return HealthCheck(
                component="memory_health",
                status=status,
                response_time_ms=0.0,
                message=f"{message} - {memory.percent:.1f}% used",
                details={
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / 1_000_000_000,
                    "memory_total_gb": memory.total / 1_000_000_000,
                    "swap_percent": swap.percent,
                    "swap_used_gb": swap.used / 1_000_000_000
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="memory_health",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Memory health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_disk_space(self) -> HealthCheck:
        """Check disk space health"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            # Determine status based on disk usage
            if disk.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = "Critical disk usage"
            elif disk.percent > 85:
                status = HealthStatus.WARNING
                message = "High disk usage"
            else:
                status = HealthStatus.HEALTHY
                message = "Disk usage normal"
            
            return HealthCheck(
                component="disk_space",
                status=status,
                response_time_ms=0.0,
                message=f"{message} - {disk.percent:.1f}% used",
                details={
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / 1_000_000_000,
                    "disk_total_gb": disk.total / 1_000_000_000,
                    "disk_used_gb": disk.used / 1_000_000_000
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="disk_space",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Disk space check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_binance_api(self) -> HealthCheck:
        """Check Binance API connectivity"""
        try:
            # Simple ping to Binance API
            response = requests.get(
                "https://api.binance.com/api/v3/ping",
                timeout=5.0
            )
            
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                message = "Binance API accessible"
            else:
                status = HealthStatus.WARNING
                message = f"Binance API returned status {response.status_code}"
            
            return HealthCheck(
                component="binance_api",
                status=status,
                response_time_ms=0.0,
                message=message,
                details={
                    "status_code": response.status_code,
                    "response_headers": dict(response.headers)
                },
                timestamp=time.time()
            )
            
        except requests.exceptions.Timeout:
            return HealthCheck(
                component="binance_api",
                status=HealthStatus.WARNING,
                response_time_ms=0.0,
                message="Binance API timeout",
                details={"error": "Request timeout"},
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                component="binance_api",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"Binance API error: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def _check_system_resources(self) -> HealthCheck:
        """Check overall system resource health"""
        try:
            import psutil
            import os
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Load average (Unix-like systems)
            load_avg = list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # Process count
            process_count = len(psutil.pids())
            
            # Network interfaces
            network_stats = psutil.net_io_counters()
            
            # Determine overall status
            if cpu_percent > 90:
                status = HealthStatus.WARNING
                message = "High CPU usage"
            elif load_avg[0] > psutil.cpu_count() * 2:
                status = HealthStatus.WARNING
                message = "High system load"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources normal"
            
            return HealthCheck(
                component="system_resources",
                status=status,
                response_time_ms=0.0,
                message=f"{message} - CPU: {cpu_percent:.1f}%",
                details={
                    "cpu_percent": cpu_percent,
                    "load_average": load_avg,
                    "process_count": process_count,
                    "network_bytes_sent": network_stats.bytes_sent,
                    "network_bytes_recv": network_stats.bytes_recv,
                    "cpu_cores": psutil.cpu_count()
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            return HealthCheck(
                component="system_resources",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0.0,
                message=f"System resources check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=time.time()
            )
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=10)
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Background health monitoring loop"""
        while self._monitoring_active:
            try:
                # Run all health checks
                results = self.run_all_health_checks()
                
                # Log any unhealthy components
                for component, result in results.items():
                    if result.status == HealthStatus.UNHEALTHY:
                        logger.error(f"Health check UNHEALTHY: {component} - {result.message}")
                    elif result.status == HealthStatus.WARNING:
                        logger.warning(f"Health check WARNING: {component} - {result.message}")
                
                # Sleep for check interval
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                time.sleep(60)  # Shorter sleep on error
    
    def __del__(self):
        """Cleanup when health checker is destroyed"""
        self.stop_monitoring()


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker(check_interval: int = 300) -> HealthChecker:
    """Get or create global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(check_interval)
        _health_checker.start_monitoring()
    return _health_checker