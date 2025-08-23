#!/usr/bin/env python3
"""
Advanced Monitoring System Validation
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Comprehensive validation of the monitoring system with focus on trading data monitoring.
Tests system monitoring, trading metrics, alerting, health checks, and dashboard functionality.
"""

import sys
import time
import logging
import requests
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_imports():
    """Validate all monitoring system imports"""
    try:
        logger.info("🧪 Testing monitoring system imports...")
        
        from monitoring import (
            SystemMonitor, get_system_monitor,
            TradingMetricsCollector, get_trading_metrics_collector,
            AlertingFramework, get_alerting_framework,
            HealthChecker, get_health_checker,
            MonitoringDashboard, get_monitoring_dashboard
        )
        
        logger.info("✅ All monitoring system imports successful")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during imports: {e}")
        return False


def validate_system_monitor():
    """Validate system monitoring functionality"""
    try:
        logger.info("🧪 Testing SystemMonitor...")
        
        from monitoring import get_system_monitor
        system_monitor = get_system_monitor(collection_interval=5)
        
        # Test current metrics collection
        current_metrics = system_monitor.get_current_metrics()
        if "error" in current_metrics:
            raise Exception(f"Failed to collect current metrics: {current_metrics['error']}")
        
        # Validate metrics structure
        required_keys = ['system', 'application']
        for key in required_keys:
            if key not in current_metrics:
                raise Exception(f"Missing key '{key}' in current metrics")
        
        # Test API request recording
        system_monitor.record_api_request(150.5, is_error=False)
        system_monitor.record_api_request(2500.0, is_error=True)
        
        # Test performance summary
        time.sleep(1)  # Allow metrics to be recorded
        summary = system_monitor.get_performance_summary(hours=1)
        if "error" in summary:
            raise Exception(f"Failed to get performance summary: {summary['error']}")
        
        # Test threshold checking
        alerts = system_monitor.check_thresholds()
        
        logger.info(f"✅ SystemMonitor validation successful - {len(alerts)} alerts found")
        return True
        
    except Exception as e:
        logger.error(f"❌ SystemMonitor validation failed: {e}")
        return False


def validate_trading_metrics():
    """Validate trading metrics collector functionality"""
    try:
        logger.info("🧪 Testing TradingMetricsCollector...")
        
        from monitoring import get_trading_metrics_collector
        trading_metrics = get_trading_metrics_collector(collection_interval=5)
        
        # Test OHLCV request recording
        trading_metrics.record_ohlcv_request(
            symbol="BTCUSDT", timeframe="1h", provider="Binance",
            response_time_ms=234.5, cache_hit=False, data_points=1000, error=False
        )
        
        trading_metrics.record_ohlcv_request(
            symbol="ETHUSDT", timeframe="1h", provider="CACHE",
            response_time_ms=15.2, cache_hit=True, data_points=1000, error=False
        )
        
        # Test strategy conversion recording
        trading_metrics.record_strategy_conversion(
            strategy_name="RSI Strategy", success=True, conversion_time_ms=1500.0,
            indicators_used=["RSI", "SMA"], error_type=None
        )
        
        # Test backtest execution recording
        trading_metrics.record_backtest_execution(
            strategy_id="rsi_001", symbol="BTCUSDT", timeframe="1h",
            success=True, execution_time_ms=5000.0, data_points=8760, error_type=None
        )
        
        # Test data quality issue recording
        trading_metrics.record_data_quality_issue(
            issue_type="missing_data", symbol="BTCUSDT", timeframe="1m",
            provider="Binance", severity="warning", 
            description="Missing 5 data points in sequence"
        )
        
        # Test dashboard data collection
        time.sleep(1)  # Allow metrics to be recorded
        dashboard_data = trading_metrics.get_trading_dashboard_data()
        if "error" in dashboard_data:
            raise Exception(f"Failed to get trading dashboard data: {dashboard_data['error']}")
        
        # Test symbol analytics
        symbol_analytics = trading_metrics.get_symbol_analytics("BTCUSDT", hours=1)
        if "error" in symbol_analytics:
            raise Exception(f"Failed to get symbol analytics: {symbol_analytics['error']}")
        
        logger.info("✅ TradingMetricsCollector validation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ TradingMetricsCollector validation failed: {e}")
        return False


def validate_alerting_framework():
    """Validate alerting framework functionality"""
    try:
        logger.info("🧪 Testing AlertingFramework...")
        
        from monitoring import get_alerting_framework
        from monitoring.alerting import AlertRule, AlertSeverity
        
        alerting = get_alerting_framework()
        
        # Test custom alert rule
        custom_rule = AlertRule(
            name="test_high_response_time",
            metric="test_response_time_ms",
            condition="greater_than",
            threshold=1000.0,
            severity=AlertSeverity.WARNING,
            description="Test alert for validation",
            cooldown_seconds=10
        )
        
        alerting.add_alert_rule(custom_rule)
        
        # Test metric evaluation with alert triggering
        test_metrics = {
            "test_response_time_ms": 1500.0,  # Should trigger alert
            "cpu_percent": 45.0,             # Should not trigger
            "memory_percent": 60.0           # Should not trigger
        }
        
        triggered_alerts = alerting.evaluate_metrics(test_metrics)
        
        # Test alert management
        if triggered_alerts:
            alert = triggered_alerts[0]
            alerting.acknowledge_alert(alert.id, "validation_test")
            alerting.suppress_alert(alert.id, duration_minutes=5)
            alerting.resolve_alert(alert.id, "Validation test completed")
        
        # Test alert statistics
        alert_stats = alerting.get_alert_statistics(hours=1)
        if "total_alerts" not in alert_stats:
            raise Exception("Invalid alert statistics format")
        
        # Clean up
        alerting.remove_alert_rule("test_high_response_time")
        
        logger.info(f"✅ AlertingFramework validation successful - {len(triggered_alerts)} alerts triggered")
        return True
        
    except Exception as e:
        logger.error(f"❌ AlertingFramework validation failed: {e}")
        return False


def validate_health_checker():
    """Validate health checker functionality"""
    try:
        logger.info("🧪 Testing HealthChecker...")
        
        from monitoring import get_health_checker
        health_checker = get_health_checker(check_interval=60)
        
        # Test individual health checks
        components_to_test = [
            "memory_health", "disk_space", "system_resources"
        ]
        
        for component in components_to_test:
            health_result = health_checker.run_health_check(component)
            if not health_result:
                raise Exception(f"Health check failed for component: {component}")
            
            health_dict = health_result.to_dict()
            required_fields = ["component", "status", "message", "timestamp"]
            for field in required_fields:
                if field not in health_dict:
                    raise Exception(f"Missing field '{field}' in health result")
        
        # Test overall health assessment
        overall_health = health_checker.get_overall_health()
        if "overall_status" not in overall_health:
            raise Exception("Missing overall_status in health assessment")
        
        # Test all health checks
        all_results = health_checker.run_all_health_checks()
        if not all_results:
            raise Exception("No health check results returned")
        
        logger.info(f"✅ HealthChecker validation successful - {len(all_results)} components checked")
        return True
        
    except Exception as e:
        logger.error(f"❌ HealthChecker validation failed: {e}")
        return False


def validate_monitoring_dashboard():
    """Validate monitoring dashboard functionality"""
    try:
        logger.info("🧪 Testing MonitoringDashboard...")
        
        from monitoring import get_monitoring_dashboard
        dashboard = get_monitoring_dashboard(update_interval=10)
        
        # Test component initialization
        if not dashboard.initialize_components():
            logger.warning("⚠️ Dashboard component initialization had issues (may be expected)")
        
        # Test dashboard data collection
        dashboard_data = dashboard.get_current_dashboard()
        required_sections = ["timestamp", "system_health", "performance_metrics", 
                           "trading_metrics", "alert_summary"]
        
        for section in required_sections:
            if section not in dashboard_data:
                raise Exception(f"Missing section '{section}' in dashboard data")
        
        # Test dashboard summary
        summary = dashboard.get_dashboard_summary()
        if "overall_status" not in summary:
            raise Exception("Missing overall_status in dashboard summary")
        
        # Test performance baseline (may have limited data)
        baseline = dashboard.get_performance_baseline(hours=1)
        # Note: baseline may return error if insufficient data, which is acceptable
        
        # Test export functionality
        export_data = dashboard.export_dashboard_data(format="json", hours=1)
        if not export_data or len(export_data) < 100:  # Should be substantial JSON
            raise Exception("Dashboard export returned insufficient data")
        
        logger.info("✅ MonitoringDashboard validation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ MonitoringDashboard validation failed: {e}")
        return False


def validate_flask_integration():
    """Validate Flask monitoring endpoints (if server is running)"""
    try:
        logger.info("🧪 Testing Flask monitoring endpoints...")
        
        base_url = "http://localhost:5007"
        
        # Test monitoring endpoints
        endpoints_to_test = [
            "/api/v1/monitoring/summary",
            "/api/v1/monitoring/health", 
            "/api/v1/monitoring/system",
            "/api/v1/monitoring/trading",
            "/api/v1/monitoring/alerts"
        ]
        
        successful_endpoints = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        successful_endpoints += 1
                        logger.debug(f"✓ {endpoint} - OK")
                    else:
                        logger.warning(f"⚠️ {endpoint} - Returned error: {data.get('error')}")
                else:
                    logger.warning(f"⚠️ {endpoint} - HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ {endpoint} - Connection error: {e}")
        
        if successful_endpoints == 0:
            logger.warning("⚠️ No Flask endpoints accessible (server may not be running)")
            return False
        else:
            logger.info(f"✅ Flask integration validation - {successful_endpoints}/{len(endpoints_to_test)} endpoints working")
            return True
        
    except Exception as e:
        logger.error(f"❌ Flask integration validation failed: {e}")
        return False


def main():
    """Main validation function"""
    print("=" * 80)
    print("🔍 PineOpt Advanced Monitoring System Validation")
    print("Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection")
    print("=" * 80)
    
    validation_tests = [
        ("Import Validation", validate_imports),
        ("SystemMonitor", validate_system_monitor),
        ("TradingMetricsCollector", validate_trading_metrics), 
        ("AlertingFramework", validate_alerting_framework),
        ("HealthChecker", validate_health_checker),
        ("MonitoringDashboard", validate_monitoring_dashboard),
        ("Flask Integration", validate_flask_integration)
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
    print(f"📊 MONITORING SYSTEM VALIDATION RESULTS")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VALIDATIONS PASSED! Advanced monitoring system is fully functional.")
        print("\n🔍 Key Features Validated:")
        print("  ✅ System resource monitoring with real-time metrics")
        print("  ✅ Trading-specific metrics for OHLCV data and operations")
        print("  ✅ Intelligent alerting with rule-based notifications")
        print("  ✅ Comprehensive health checking for all components")
        print("  ✅ Real-time monitoring dashboard with trends")
        print("  ✅ Flask API integration with monitoring endpoints")
        
        print("\n📈 Monitoring Capabilities:")
        print("  • Real-time system performance tracking")
        print("  • Historical market data access monitoring")
        print("  • Cache efficiency and optimization metrics") 
        print("  • Proactive alerting for performance issues")
        print("  • Component health monitoring and diagnostics")
        print("  • Trading activity and conversion tracking")
        
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} validation(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)