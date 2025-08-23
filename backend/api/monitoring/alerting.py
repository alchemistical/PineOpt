"""
Alerting Framework for Advanced Monitoring & Metrics Collection
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Intelligent alerting system for proactive issue detection and notification.
Supports multiple alert channels, rule-based alerting, and escalation policies.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import threading
import json
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Individual alert with metadata and tracking"""
    id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    metric: str
    current_value: float
    threshold_value: float
    created_at: float
    updated_at: float
    resolved_at: Optional[float] = None
    acknowledged_at: Optional[float] = None
    escalation_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for serialization"""
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "metric": self.metric,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "acknowledged_at": self.acknowledged_at,
            "escalation_level": self.escalation_level,
            "metadata": self.metadata
        }


@dataclass
class AlertRule:
    """Alert rule definition with conditions and actions"""
    name: str
    metric: str
    condition: str  # "greater_than", "less_than", "equals", "not_equals"
    threshold: float
    severity: AlertSeverity
    description: str
    cooldown_seconds: int = 300  # 5 minutes
    evaluation_window_seconds: int = 60  # 1 minute
    min_data_points: int = 1
    enabled: bool = True
    last_triggered: Optional[float] = None
    
    def should_trigger(self, current_value: float, current_time: float) -> bool:
        """Check if rule should trigger based on current conditions"""
        if not self.enabled:
            return False
        
        # Check cooldown period
        if (self.last_triggered and 
            current_time - self.last_triggered < self.cooldown_seconds):
            return False
        
        # Evaluate condition
        if self.condition == "greater_than":
            return current_value > self.threshold
        elif self.condition == "less_than":
            return current_value < self.threshold
        elif self.condition == "equals":
            return abs(current_value - self.threshold) < 0.001
        elif self.condition == "not_equals":
            return abs(current_value - self.threshold) >= 0.001
        else:
            logger.error(f"Unknown condition: {self.condition}")
            return False


class AlertingFramework:
    """Advanced alerting framework with intelligent notification and escalation"""
    
    def __init__(self, alert_history_size: int = 10000):
        """
        Initialize alerting framework
        
        Args:
            alert_history_size: Number of historical alerts to retain
        """
        self.alert_history_size = alert_history_size
        
        # Alert management
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=alert_history_size)
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Notification channels
        self.notification_channels: Dict[str, Callable] = {}
        
        # Statistics
        self.alert_stats = {
            'total_alerts': 0,
            'alerts_by_severity': {severity.value: 0 for severity in AlertSeverity},
            'alerts_by_metric': {},
            'avg_resolution_time': 0.0,
            'false_positive_rate': 0.0
        }
        
        # Monitoring thread
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Default alert rules for trading systems
        self._setup_default_rules()
        
        logger.info("AlertingFramework initialized with default trading rules")
    
    def _setup_default_rules(self):
        """Setup default alert rules for trading system monitoring"""
        default_rules = [
            # System resource alerts
            AlertRule(
                name="high_cpu_usage",
                metric="cpu_percent",
                condition="greater_than",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                description="CPU usage is high and may impact performance"
            ),
            AlertRule(
                name="critical_cpu_usage",
                metric="cpu_percent",
                condition="greater_than",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                description="CPU usage is critically high"
            ),
            AlertRule(
                name="high_memory_usage",
                metric="memory_percent",
                condition="greater_than",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                description="Memory usage is high and may cause issues"
            ),
            AlertRule(
                name="critical_memory_usage",
                metric="memory_percent",
                condition="greater_than",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                description="Memory usage is critically high"
            ),
            
            # Application performance alerts
            AlertRule(
                name="high_response_time",
                metric="avg_response_time_ms",
                condition="greater_than",
                threshold=2000.0,
                severity=AlertSeverity.WARNING,
                description="API response times are elevated"
            ),
            AlertRule(
                name="critical_response_time",
                metric="avg_response_time_ms",
                condition="greater_than",
                threshold=5000.0,
                severity=AlertSeverity.CRITICAL,
                description="API response times are critically high"
            ),
            AlertRule(
                name="high_error_rate",
                metric="error_rate_percent",
                condition="greater_than",
                threshold=5.0,
                severity=AlertSeverity.WARNING,
                description="API error rate is elevated"
            ),
            AlertRule(
                name="critical_error_rate",
                metric="error_rate_percent",
                condition="greater_than",
                threshold=15.0,
                severity=AlertSeverity.CRITICAL,
                description="API error rate is critically high"
            ),
            
            # Trading-specific alerts
            AlertRule(
                name="low_cache_hit_rate",
                metric="cache_hit_rate_percent",
                condition="less_than",
                threshold=50.0,
                severity=AlertSeverity.WARNING,
                description="Market data cache efficiency is low"
            ),
            AlertRule(
                name="data_fetch_slow",
                metric="avg_data_fetch_time_ms",
                condition="greater_than",
                threshold=3000.0,
                severity=AlertSeverity.WARNING,
                description="Market data fetching is slow"
            ),
            AlertRule(
                name="conversion_failures",
                metric="conversion_success_rate",
                condition="less_than",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                description="Strategy conversion success rate is low"
            ),
            AlertRule(
                name="backtest_failures",
                metric="backtest_success_rate",
                condition="less_than",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                description="Backtest execution success rate is low"
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.severity.value})")
    
    def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Removed alert rule: {rule_name}")
    
    def update_alert_rule(self, rule_name: str, **kwargs):
        """Update an existing alert rule"""
        if rule_name in self.alert_rules:
            rule = self.alert_rules[rule_name]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            logger.info(f"Updated alert rule: {rule_name}")
    
    def evaluate_metrics(self, metrics: Dict[str, float]):
        """Evaluate current metrics against all alert rules"""
        current_time = time.time()
        triggered_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if rule.metric in metrics:
                current_value = metrics[rule.metric]
                
                if rule.should_trigger(current_value, current_time):
                    alert = self._create_alert(rule, current_value, current_time)
                    triggered_alerts.append(alert)
                    rule.last_triggered = current_time
        
        return triggered_alerts
    
    def _create_alert(self, rule: AlertRule, current_value: float, current_time: float) -> Alert:
        """Create a new alert from a triggered rule"""
        alert_id = f"{rule.name}_{int(current_time)}"
        
        # Check if similar alert is already active
        existing_alert = self._find_similar_active_alert(rule.name, rule.metric)
        if existing_alert:
            # Update existing alert instead of creating new one
            existing_alert.current_value = current_value
            existing_alert.updated_at = current_time
            existing_alert.escalation_level += 1
            return existing_alert
        
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=f"{rule.name.replace('_', ' ').title()}",
            message=f"{rule.description}. Current value: {current_value:.2f}, Threshold: {rule.threshold:.2f}",
            metric=rule.metric,
            current_value=current_value,
            threshold_value=rule.threshold,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Update statistics
        self.alert_stats['total_alerts'] += 1
        self.alert_stats['alerts_by_severity'][rule.severity.value] += 1
        if rule.metric not in self.alert_stats['alerts_by_metric']:
            self.alert_stats['alerts_by_metric'][rule.metric] = 0
        self.alert_stats['alerts_by_metric'][rule.metric] += 1
        
        # Send notifications
        self._send_notifications(alert)
        
        logger.warning(f"Alert triggered: {alert.title} - {alert.message}")
        
        return alert
    
    def _find_similar_active_alert(self, rule_name: str, metric: str) -> Optional[Alert]:
        """Find similar active alert to avoid duplicates"""
        for alert in self.active_alerts.values():
            if (alert.rule_name == rule_name and 
                alert.metric == metric and 
                alert.status == AlertStatus.ACTIVE):
                return alert
        return None
    
    def resolve_alert(self, alert_id: str, reason: str = ""):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()
            alert.updated_at = time.time()
            
            if reason:
                alert.metadata['resolution_reason'] = reason
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert.title} - {reason}")
    
    def acknowledge_alert(self, alert_id: str, acknowledger: str = "system"):
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = time.time()
            alert.updated_at = time.time()
            alert.metadata['acknowledged_by'] = acknowledger
            
            logger.info(f"Alert acknowledged: {alert.title} by {acknowledger}")
    
    def suppress_alert(self, alert_id: str, duration_minutes: int = 60):
        """Suppress an alert for a specified duration"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            alert.updated_at = time.time()
            alert.metadata['suppressed_until'] = time.time() + (duration_minutes * 60)
            
            logger.info(f"Alert suppressed: {alert.title} for {duration_minutes} minutes")
    
    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    def get_alert_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics for specified time period"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter recent alerts
        recent_alerts = [a for a in self.alert_history if a.created_at >= cutoff_time]
        
        if not recent_alerts:
            return {
                "period_hours": hours,
                "total_alerts": 0,
                "alerts_by_severity": {},
                "alerts_by_metric": {},
                "avg_resolution_time_minutes": 0.0,
                "current_active_alerts": len(self.active_alerts)
            }
        
        # Calculate statistics
        alerts_by_severity = {}
        alerts_by_metric = {}
        resolution_times = []
        
        for alert in recent_alerts:
            # Severity breakdown
            severity = alert.severity.value
            alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
            
            # Metric breakdown
            alerts_by_metric[alert.metric] = alerts_by_metric.get(alert.metric, 0) + 1
            
            # Resolution time calculation
            if alert.resolved_at:
                resolution_time = alert.resolved_at - alert.created_at
                resolution_times.append(resolution_time)
        
        avg_resolution_time = (sum(resolution_times) / len(resolution_times) / 60) if resolution_times else 0.0
        
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "alerts_by_severity": alerts_by_severity,
            "alerts_by_metric": alerts_by_metric,
            "avg_resolution_time_minutes": avg_resolution_time,
            "current_active_alerts": len(self.active_alerts),
            "alert_frequency_per_hour": len(recent_alerts) / hours
        }
    
    def add_notification_channel(self, channel_name: str, handler: Callable[[Alert], None]):
        """Add a notification channel for alerts"""
        self.notification_channels[channel_name] = handler
        logger.info(f"Added notification channel: {channel_name}")
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        for channel_name, handler in self.notification_channels.items():
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel_name}: {e}")
    
    def start_monitoring(self):
        """Start background alert monitoring and cleanup"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop background alert monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop for alert management"""
        while self._monitoring_active:
            try:
                current_time = time.time()
                
                # Auto-resolve old alerts (24 hours)
                old_threshold = current_time - (24 * 3600)
                alerts_to_resolve = []
                
                for alert_id, alert in self.active_alerts.items():
                    if alert.created_at < old_threshold:
                        alerts_to_resolve.append(alert_id)
                
                for alert_id in alerts_to_resolve:
                    self.resolve_alert(alert_id, "Auto-resolved due to age")
                
                # Un-suppress alerts
                alerts_to_unsuppress = []
                for alert_id, alert in self.active_alerts.items():
                    if (alert.status == AlertStatus.SUPPRESSED and 
                        'suppressed_until' in alert.metadata and
                        current_time > alert.metadata['suppressed_until']):
                        alerts_to_unsuppress.append(alert_id)
                
                for alert_id in alerts_to_unsuppress:
                    alert = self.active_alerts[alert_id]
                    alert.status = AlertStatus.ACTIVE
                    alert.updated_at = current_time
                    del alert.metadata['suppressed_until']
                    logger.info(f"Alert un-suppressed: {alert.title}")
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Alert monitoring loop error: {e}")
                time.sleep(60)
    
    def export_alerts(self, format: str = "json", hours: int = 24) -> str:
        """Export alerts in specified format"""
        if format.lower() == "json":
            cutoff_time = time.time() - (hours * 3600)
            recent_alerts = [a.to_dict() for a in self.alert_history if a.created_at >= cutoff_time]
            return json.dumps(recent_alerts, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def __del__(self):
        """Cleanup when framework is destroyed"""
        self.stop_monitoring()


# Default notification handlers
def log_notification_handler(alert: Alert):
    """Simple log-based notification handler"""
    if alert.severity == AlertSeverity.CRITICAL or alert.severity == AlertSeverity.EMERGENCY:
        logger.error(f"ALERT [{alert.severity.value.upper()}]: {alert.title} - {alert.message}")
    else:
        logger.warning(f"ALERT [{alert.severity.value.upper()}]: {alert.title} - {alert.message}")


# Global alerting framework instance
_alerting_framework: Optional[AlertingFramework] = None


def get_alerting_framework() -> AlertingFramework:
    """Get or create global alerting framework instance"""
    global _alerting_framework
    if _alerting_framework is None:
        _alerting_framework = AlertingFramework()
        _alerting_framework.add_notification_channel("log", log_notification_handler)
        _alerting_framework.start_monitoring()
    return _alerting_framework