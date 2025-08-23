"""
System Monitor for Advanced Monitoring & Metrics Collection
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Comprehensive system resource monitoring with real-time metrics collection.
Tracks CPU, memory, disk I/O, network usage, and application performance.
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    load_average: List[float]
    uptime_seconds: float


@dataclass
class ApplicationMetrics:
    """Application-specific performance metrics"""
    timestamp: float
    api_requests_per_minute: int
    avg_response_time_ms: float
    error_rate_percent: float
    active_connections: int
    cache_hit_rate_percent: float
    database_connections: int
    memory_usage_mb: float
    cpu_usage_percent: float


class SystemMonitor:
    """Advanced system monitoring with real-time metrics collection"""
    
    def __init__(self, collection_interval: int = 30, history_size: int = 2880):
        """
        Initialize system monitor
        
        Args:
            collection_interval: Metrics collection interval in seconds
            history_size: Number of historical metrics to retain (default: 24h at 30s intervals)
        """
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # Metrics storage
        self.system_metrics_history: deque = deque(maxlen=history_size)
        self.app_metrics_history: deque = deque(maxlen=history_size)
        
        # System monitoring state
        self.start_time = time.time()
        self.last_network_stats = psutil.net_io_counters()
        self.process = psutil.Process()
        
        # Application metrics tracking
        self.api_request_counts = deque(maxlen=60)  # Last 60 minutes
        self.response_times = deque(maxlen=1000)    # Last 1000 requests
        self.error_counts = deque(maxlen=60)        # Last 60 minutes
        
        # Monitoring thread
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'response_time_warning': 1000.0,  # ms
            'response_time_critical': 5000.0,  # ms
            'error_rate_warning': 5.0,        # %
            'error_rate_critical': 10.0       # %
        }
        
        logger.info(f"SystemMonitor initialized - Collection interval: {collection_interval}s")
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring thread"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics  
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / 1_000_000
            network_recv_mb = network.bytes_recv / 1_000_000
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Load average (Unix-like systems)
            load_avg = list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # System uptime
            uptime = time.time() - self.start_time
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / 1_000_000,
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / 1_000_000_000,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                load_average=load_avg,
                uptime_seconds=uptime
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific performance metrics"""
        try:
            current_time = time.time()
            
            # API request rate (requests per minute)
            recent_requests = sum(1 for t in self.api_request_counts if current_time - t < 60)
            
            # Average response time
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
            else:
                avg_response_time = 0.0
            
            # Error rate
            recent_errors = sum(1 for t in self.error_counts if current_time - t < 60)
            error_rate = (recent_errors / max(recent_requests, 1)) * 100 if recent_requests > 0 else 0.0
            
            # Process metrics
            process_memory = self.process.memory_info().rss / 1_000_000
            process_cpu = self.process.cpu_percent()
            
            metrics = ApplicationMetrics(
                timestamp=current_time,
                api_requests_per_minute=recent_requests,
                avg_response_time_ms=avg_response_time,
                error_rate_percent=error_rate,
                active_connections=0,  # Will be populated by performance system
                cache_hit_rate_percent=0.0,  # Will be populated by performance system
                database_connections=0,  # Will be populated by performance system
                memory_usage_mb=process_memory,
                cpu_usage_percent=process_cpu
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    def record_api_request(self, response_time_ms: float, is_error: bool = False):
        """Record an API request for metrics tracking"""
        current_time = time.time()
        
        self.api_request_counts.append(current_time)
        self.response_times.append(response_time_ms)
        
        if is_error:
            self.error_counts.append(current_time)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current comprehensive system metrics"""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        
        if not system_metrics or not app_metrics:
            return {"error": "Failed to collect metrics"}
        
        return {
            "system": {
                "timestamp": system_metrics.timestamp,
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_available_mb": system_metrics.memory_available_mb,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "disk_free_gb": system_metrics.disk_free_gb,
                "network_sent_mb": system_metrics.network_sent_mb,
                "network_recv_mb": system_metrics.network_recv_mb,
                "process_count": system_metrics.process_count,
                "load_average": system_metrics.load_average,
                "uptime_seconds": system_metrics.uptime_seconds
            },
            "application": {
                "timestamp": app_metrics.timestamp,
                "api_requests_per_minute": app_metrics.api_requests_per_minute,
                "avg_response_time_ms": app_metrics.avg_response_time_ms,
                "error_rate_percent": app_metrics.error_rate_percent,
                "active_connections": app_metrics.active_connections,
                "cache_hit_rate_percent": app_metrics.cache_hit_rate_percent,
                "database_connections": app_metrics.database_connections,
                "memory_usage_mb": app_metrics.memory_usage_mb,
                "cpu_usage_percent": app_metrics.cpu_usage_percent
            },
            "collection_time": datetime.now().isoformat()
        }
    
    def get_metrics_history(self, hours: int = 1) -> Dict[str, Any]:
        """Get historical metrics for specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter historical data
        system_history = [
            {
                "timestamp": m.timestamp,
                "cpu_percent": m.cpu_percent,
                "memory_percent": m.memory_percent,
                "disk_usage_percent": m.disk_usage_percent,
                "network_sent_mb": m.network_sent_mb,
                "network_recv_mb": m.network_recv_mb
            }
            for m in self.system_metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        app_history = [
            {
                "timestamp": m.timestamp,
                "api_requests_per_minute": m.api_requests_per_minute,
                "avg_response_time_ms": m.avg_response_time_ms,
                "error_rate_percent": m.error_rate_percent,
                "memory_usage_mb": m.memory_usage_mb
            }
            for m in self.app_metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        return {
            "period_hours": hours,
            "system_metrics": system_history,
            "application_metrics": app_history,
            "total_data_points": len(system_history)
        }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Calculate system performance summary
        recent_system = [m for m in self.system_metrics_history if m.timestamp >= cutoff_time]
        recent_app = [m for m in self.app_metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_system or not recent_app:
            return {"error": "Insufficient historical data"}
        
        # System statistics
        cpu_values = [m.cpu_percent for m in recent_system]
        memory_values = [m.memory_percent for m in recent_system]
        
        # Application statistics
        response_times = [m.avg_response_time_ms for m in recent_app]
        error_rates = [m.error_rate_percent for m in recent_app]
        
        return {
            "period_hours": hours,
            "system_performance": {
                "avg_cpu_percent": sum(cpu_values) / len(cpu_values),
                "max_cpu_percent": max(cpu_values),
                "avg_memory_percent": sum(memory_values) / len(memory_values),
                "max_memory_percent": max(memory_values),
                "data_points": len(recent_system)
            },
            "application_performance": {
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "max_response_time_ms": max(response_times),
                "avg_error_rate_percent": sum(error_rates) / len(error_rates),
                "max_error_rate_percent": max(error_rates),
                "total_requests": sum(m.api_requests_per_minute for m in recent_app),
                "data_points": len(recent_app)
            }
        }
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """Check current metrics against performance thresholds"""
        alerts = []
        current_metrics = self.get_current_metrics()
        
        if "error" in current_metrics:
            return alerts
        
        system = current_metrics["system"]
        app = current_metrics["application"]
        
        # CPU threshold checks
        if system["cpu_percent"] >= self.thresholds["cpu_critical"]:
            alerts.append({
                "severity": "critical",
                "metric": "cpu_usage",
                "value": system["cpu_percent"],
                "threshold": self.thresholds["cpu_critical"],
                "message": f"Critical CPU usage: {system['cpu_percent']:.1f}%"
            })
        elif system["cpu_percent"] >= self.thresholds["cpu_warning"]:
            alerts.append({
                "severity": "warning",
                "metric": "cpu_usage",
                "value": system["cpu_percent"],
                "threshold": self.thresholds["cpu_warning"],
                "message": f"High CPU usage: {system['cpu_percent']:.1f}%"
            })
        
        # Memory threshold checks
        if system["memory_percent"] >= self.thresholds["memory_critical"]:
            alerts.append({
                "severity": "critical",
                "metric": "memory_usage",
                "value": system["memory_percent"],
                "threshold": self.thresholds["memory_critical"],
                "message": f"Critical memory usage: {system['memory_percent']:.1f}%"
            })
        elif system["memory_percent"] >= self.thresholds["memory_warning"]:
            alerts.append({
                "severity": "warning",
                "metric": "memory_usage",
                "value": system["memory_percent"],
                "threshold": self.thresholds["memory_warning"],
                "message": f"High memory usage: {system['memory_percent']:.1f}%"
            })
        
        # Response time threshold checks
        if app["avg_response_time_ms"] >= self.thresholds["response_time_critical"]:
            alerts.append({
                "severity": "critical",
                "metric": "response_time",
                "value": app["avg_response_time_ms"],
                "threshold": self.thresholds["response_time_critical"],
                "message": f"Critical response time: {app['avg_response_time_ms']:.1f}ms"
            })
        elif app["avg_response_time_ms"] >= self.thresholds["response_time_warning"]:
            alerts.append({
                "severity": "warning",
                "metric": "response_time",
                "value": app["avg_response_time_ms"],
                "threshold": self.thresholds["response_time_warning"],
                "message": f"High response time: {app['avg_response_time_ms']:.1f}ms"
            })
        
        # Error rate threshold checks
        if app["error_rate_percent"] >= self.thresholds["error_rate_critical"]:
            alerts.append({
                "severity": "critical",
                "metric": "error_rate",
                "value": app["error_rate_percent"],
                "threshold": self.thresholds["error_rate_critical"],
                "message": f"Critical error rate: {app['error_rate_percent']:.1f}%"
            })
        elif app["error_rate_percent"] >= self.thresholds["error_rate_warning"]:
            alerts.append({
                "severity": "warning",
                "metric": "error_rate",
                "value": app["error_rate_percent"],
                "threshold": self.thresholds["error_rate_warning"],
                "message": f"High error rate: {app['error_rate_percent']:.1f}%"
            })
        
        return alerts
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect and store metrics
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_application_metrics()
                
                if system_metrics:
                    self.system_metrics_history.append(system_metrics)
                
                if app_metrics:
                    self.app_metrics_history.append(app_metrics)
                
                # Check thresholds and log alerts
                alerts = self.check_thresholds()
                for alert in alerts:
                    if alert["severity"] == "critical":
                        logger.error(f"System Alert: {alert['message']}")
                    else:
                        logger.warning(f"System Alert: {alert['message']}")
                
                # Sleep for collection interval
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.collection_interval)
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        if format.lower() == "json":
            current_metrics = self.get_current_metrics()
            return json.dumps(current_metrics, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def __del__(self):
        """Cleanup when monitor is destroyed"""
        self.stop_monitoring()


# Global system monitor instance
_system_monitor: Optional[SystemMonitor] = None


def get_system_monitor(collection_interval: int = 30) -> SystemMonitor:
    """Get or create global system monitor instance"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor(collection_interval)
        _system_monitor.start_monitoring()
    return _system_monitor