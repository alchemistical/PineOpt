"""
Monitoring Dashboard for Advanced Monitoring & Metrics Collection
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Centralized dashboard for all monitoring data with real-time metrics aggregation.
Provides unified interface for system health, performance, and trading metrics.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Aggregated dashboard metrics"""
    timestamp: float
    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    trading_metrics: Dict[str, Any]
    alert_summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard metrics to dictionary"""
        return {
            "timestamp": self.timestamp,
            "collected_at": datetime.fromtimestamp(self.timestamp).isoformat(),
            "system_health": self.system_health,
            "performance_metrics": self.performance_metrics,
            "trading_metrics": self.trading_metrics,
            "alert_summary": self.alert_summary
        }


class MonitoringDashboard:
    """Centralized monitoring dashboard with real-time data aggregation"""
    
    def __init__(self, update_interval: int = 30):
        """
        Initialize monitoring dashboard
        
        Args:
            update_interval: Dashboard update interval in seconds
        """
        self.update_interval = update_interval
        
        # Component references
        self.system_monitor = None
        self.trading_metrics = None
        self.alerting_framework = None
        self.health_checker = None
        
        # Dashboard state
        self.current_metrics: Optional[DashboardMetrics] = None
        self.metrics_history: List[DashboardMetrics] = []
        self.max_history_size = 1440  # 24 hours at 1-minute intervals
        
        # Update thread
        self._update_thread: Optional[threading.Thread] = None
        self._update_active = False
        
        # Dashboard configuration
        self.config = {
            'auto_refresh': True,
            'show_historical_trends': True,
            'alert_threshold_days': 7,
            'performance_baseline_hours': 24
        }
        
        logger.info(f"MonitoringDashboard initialized - Update interval: {update_interval}s")
    
    def initialize_components(self):
        """Initialize monitoring components"""
        try:
            # Import and initialize components
            from .system_monitor import get_system_monitor
            from .trading_metrics import get_trading_metrics_collector
            from .alerting import get_alerting_framework
            from .health_checker import get_health_checker
            
            self.system_monitor = get_system_monitor()
            self.trading_metrics = get_trading_metrics_collector()
            self.alerting_framework = get_alerting_framework()
            self.health_checker = get_health_checker()
            
            logger.info("Dashboard components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dashboard components: {e}")
            return False
    
    def collect_dashboard_metrics(self) -> DashboardMetrics:
        """Collect comprehensive dashboard metrics from all components"""
        current_time = time.time()
        
        # Initialize empty metrics
        dashboard_metrics = DashboardMetrics(
            timestamp=current_time,
            system_health={},
            performance_metrics={},
            trading_metrics={},
            alert_summary={}
        )
        
        try:
            # Collect system health
            if self.health_checker:
                health_data = self.health_checker.get_overall_health()
                dashboard_metrics.system_health = {
                    "overall_status": health_data.get("overall_status", "unknown"),
                    "healthy_components": health_data.get("summary", {}).get("healthy", 0),
                    "total_components": health_data.get("summary", {}).get("total_checks", 0),
                    "avg_response_time_ms": health_data.get("summary", {}).get("avg_response_time_ms", 0),
                    "components": health_data.get("components", {}),
                    "last_check": health_data.get("checked_at")
                }
            
            # Collect performance metrics
            if self.system_monitor:
                perf_data = self.system_monitor.get_current_metrics()
                if "error" not in perf_data:
                    dashboard_metrics.performance_metrics = {
                        "system": perf_data.get("system", {}),
                        "application": perf_data.get("application", {}),
                        "collection_time": perf_data.get("collection_time")
                    }
                    
                    # Add performance system data if available
                    try:
                        from performance import get_cache_manager, get_memory_manager
                        cache_manager = get_cache_manager()
                        memory_manager = get_memory_manager()
                        
                        cache_stats = cache_manager.get_stats()
                        memory_health = memory_manager.check_memory_health()
                        
                        dashboard_metrics.performance_metrics.update({
                            "cache": {
                                "hit_rate_percent": cache_stats.get("hit_rate_percent", 0),
                                "total_keys": cache_stats.get("total_keys", 0),
                                "memory_usage_mb": cache_stats.get("total_size_mb", 0)
                            },
                            "memory": {
                                "health_status": memory_health.get("health_status", "unknown"),
                                "usage_percent": memory_health.get("memory_usage_percent", 0),
                                "growth_rate_mb_per_min": memory_health.get("memory_growth_rate_mb_per_minute", 0)
                            }
                        })
                    except Exception as e:
                        logger.warning(f"Could not collect performance system data: {e}")
            
            # Collect trading metrics
            if self.trading_metrics:
                trading_data = self.trading_metrics.get_trading_dashboard_data()
                if "error" not in trading_data:
                    dashboard_metrics.trading_metrics = trading_data
            
            # Collect alert summary
            if self.alerting_framework:
                alert_stats = self.alerting_framework.get_alert_statistics(hours=24)
                active_alerts = self.alerting_framework.get_active_alerts()
                
                dashboard_metrics.alert_summary = {
                    "total_alerts_24h": alert_stats.get("total_alerts", 0),
                    "active_alerts": len(active_alerts),
                    "critical_alerts": len([a for a in active_alerts if a.severity.value == "critical"]),
                    "warning_alerts": len([a for a in active_alerts if a.severity.value == "warning"]),
                    "alert_frequency_per_hour": alert_stats.get("alert_frequency_per_hour", 0),
                    "avg_resolution_time_minutes": alert_stats.get("avg_resolution_time_minutes", 0),
                    "alerts_by_metric": alert_stats.get("alerts_by_metric", {})
                }
            
            return dashboard_metrics
            
        except Exception as e:
            logger.error(f"Error collecting dashboard metrics: {e}")
            return dashboard_metrics
    
    def get_current_dashboard(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        if not self.current_metrics:
            self.current_metrics = self.collect_dashboard_metrics()
        
        return self.current_metrics.to_dict()
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get high-level dashboard summary"""
        current = self.get_current_dashboard()
        
        # Overall system status
        system_status = current.get("system_health", {}).get("overall_status", "unknown")
        
        # Key performance indicators
        performance = current.get("performance_metrics", {})
        system_perf = performance.get("system", {})
        app_perf = performance.get("application", {})
        
        # Trading metrics summary
        trading = current.get("trading_metrics", {})
        market_data = trading.get("market_data", {})
        
        # Alert status
        alerts = current.get("alert_summary", {})
        
        return {
            "timestamp": current.get("timestamp"),
            "overall_status": system_status,
            "key_indicators": {
                "cpu_usage_percent": system_perf.get("cpu_percent", 0),
                "memory_usage_percent": system_perf.get("memory_percent", 0),
                "api_response_time_ms": app_perf.get("avg_response_time_ms", 0),
                "error_rate_percent": app_perf.get("error_rate_percent", 0),
                "cache_hit_rate_percent": market_data.get("cache_hit_rate_percent", 0),
                "active_alerts": alerts.get("active_alerts", 0)
            },
            "health_summary": {
                "healthy_components": current.get("system_health", {}).get("healthy_components", 0),
                "total_components": current.get("system_health", {}).get("total_components", 0),
                "health_percentage": (
                    (current.get("system_health", {}).get("healthy_components", 0) / 
                     max(current.get("system_health", {}).get("total_components", 1), 1)) * 100
                )
            },
            "trading_activity": {
                "ohlcv_requests_per_hour": market_data.get("ohlcv_requests_per_hour", 0),
                "conversions_per_hour": trading.get("trading_operations", {}).get("conversions_per_hour", 0),
                "backtests_per_hour": trading.get("trading_operations", {}).get("backtests_per_hour", 0)
            }
        }
    
    def get_historical_trends(self, hours: int = 6) -> Dict[str, Any]:
        """Get historical trends for dashboard charts"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter historical metrics
        historical_data = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not historical_data:
            return {"error": "No historical data available"}
        
        # Extract time series data
        timestamps = [m.timestamp for m in historical_data]
        
        # System metrics trends
        cpu_usage = []
        memory_usage = []
        response_times = []
        error_rates = []
        
        # Trading metrics trends
        ohlcv_requests = []
        cache_hit_rates = []
        active_alerts = []
        
        for metrics in historical_data:
            # System trends
            system = metrics.performance_metrics.get("system", {})
            app = metrics.performance_metrics.get("application", {})
            
            cpu_usage.append(system.get("cpu_percent", 0))
            memory_usage.append(system.get("memory_percent", 0))
            response_times.append(app.get("avg_response_time_ms", 0))
            error_rates.append(app.get("error_rate_percent", 0))
            
            # Trading trends
            trading = metrics.trading_metrics
            market_data = trading.get("market_data", {})
            alerts = metrics.alert_summary
            
            ohlcv_requests.append(market_data.get("ohlcv_requests_per_hour", 0))
            cache_hit_rates.append(market_data.get("cache_hit_rate_percent", 0))
            active_alerts.append(alerts.get("active_alerts", 0))
        
        return {
            "period_hours": hours,
            "data_points": len(historical_data),
            "timestamps": timestamps,
            "trends": {
                "system_performance": {
                    "cpu_usage_percent": cpu_usage,
                    "memory_usage_percent": memory_usage,
                    "api_response_time_ms": response_times,
                    "error_rate_percent": error_rates
                },
                "trading_activity": {
                    "ohlcv_requests_per_hour": ohlcv_requests,
                    "cache_hit_rate_percent": cache_hit_rates
                },
                "monitoring": {
                    "active_alerts": active_alerts
                }
            }
        }
    
    def get_performance_baseline(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance baseline for comparison"""
        cutoff_time = time.time() - (hours * 3600)
        
        baseline_data = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not baseline_data:
            return {"error": "Insufficient data for baseline"}
        
        # Calculate baseline statistics
        cpu_values = []
        memory_values = []
        response_values = []
        
        for metrics in baseline_data:
            system = metrics.performance_metrics.get("system", {})
            app = metrics.performance_metrics.get("application", {})
            
            if system.get("cpu_percent"):
                cpu_values.append(system["cpu_percent"])
            if system.get("memory_percent"):
                memory_values.append(system["memory_percent"])
            if app.get("avg_response_time_ms"):
                response_values.append(app["avg_response_time_ms"])
        
        def calculate_stats(values):
            if not values:
                return {"avg": 0, "min": 0, "max": 0, "p95": 0}
            
            values.sort()
            return {
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "p95": values[int(len(values) * 0.95)] if values else 0
            }
        
        return {
            "period_hours": hours,
            "baseline_metrics": {
                "cpu_usage_percent": calculate_stats(cpu_values),
                "memory_usage_percent": calculate_stats(memory_values),
                "response_time_ms": calculate_stats(response_values)
            },
            "data_points": len(baseline_data)
        }
    
    def start_auto_refresh(self):
        """Start automatic dashboard refresh"""
        if self._update_thread and self._update_thread.is_alive():
            return
        
        self._update_active = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        logger.info("Dashboard auto-refresh started")
    
    def stop_auto_refresh(self):
        """Stop automatic dashboard refresh"""
        self._update_active = False
        if self._update_thread:
            self._update_thread.join(timeout=10)
        logger.info("Dashboard auto-refresh stopped")
    
    def _update_loop(self):
        """Background dashboard update loop"""
        while self._update_active:
            try:
                # Collect fresh metrics
                new_metrics = self.collect_dashboard_metrics()
                
                # Update current metrics
                self.current_metrics = new_metrics
                
                # Add to history
                self.metrics_history.append(new_metrics)
                
                # Limit history size
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # Sleep for update interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Dashboard update loop error: {e}")
                time.sleep(self.update_interval)
    
    def export_dashboard_data(self, format: str = "json", hours: int = 24) -> str:
        """Export dashboard data in specified format"""
        if format.lower() == "json":
            import json
            
            export_data = {
                "export_timestamp": time.time(),
                "export_date": datetime.now().isoformat(),
                "period_hours": hours,
                "current_dashboard": self.get_current_dashboard(),
                "historical_trends": self.get_historical_trends(hours),
                "performance_baseline": self.get_performance_baseline(hours)
            }
            
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def __del__(self):
        """Cleanup when dashboard is destroyed"""
        self.stop_auto_refresh()


# Global monitoring dashboard instance
_monitoring_dashboard: Optional[MonitoringDashboard] = None


def get_monitoring_dashboard(update_interval: int = 30) -> MonitoringDashboard:
    """Get or create global monitoring dashboard instance"""
    global _monitoring_dashboard
    if _monitoring_dashboard is None:
        _monitoring_dashboard = MonitoringDashboard(update_interval)
        if _monitoring_dashboard.initialize_components():
            _monitoring_dashboard.start_auto_refresh()
    return _monitoring_dashboard