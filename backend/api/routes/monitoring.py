"""
Monitoring Routes Blueprint
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Flask blueprint for monitoring endpoints integrated with app.py architecture.
"""

from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

# Create monitoring blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/v1/monitoring')


@monitoring_bp.route('/summary', methods=['GET'])
def monitoring_summary():
    """Get comprehensive monitoring summary"""
    try:
        from monitoring import get_monitoring_dashboard
        dashboard = get_monitoring_dashboard()
        
        summary = dashboard.get_dashboard_summary()
        
        return jsonify({
            "success": True,
            "data": summary
        })
        
    except Exception as e:
        logger.error(f"Error getting monitoring summary: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/health', methods=['GET'])
def monitoring_health():
    """Get detailed health status of all components"""
    try:
        from monitoring import get_health_checker
        health_checker = get_health_checker()
        
        # Run comprehensive health checks
        health_results = health_checker.run_all_health_checks()
        overall_health = health_checker.get_overall_health()
        
        return jsonify({
            "success": True,
            "data": {
                "overall": overall_health,
                "components": [result.to_dict() for result in health_results]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/system', methods=['GET'])
def system_metrics():
    """Get current system performance metrics"""
    try:
        from monitoring import get_system_monitor
        system_monitor = get_system_monitor()
        
        # Get current system metrics
        current_metrics = system_monitor.get_current_metrics()
        
        # Get performance summary
        hours = request.args.get('hours', 1, type=int)
        performance_summary = system_monitor.get_performance_summary(hours=hours)
        
        return jsonify({
            "success": True,
            "data": {
                "current": current_metrics,
                "summary": performance_summary
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/trading', methods=['GET'])
def trading_metrics():
    """Get trading-specific metrics and analytics"""
    try:
        from monitoring import get_trading_metrics_collector
        trading_metrics = get_trading_metrics_collector()
        
        # Get dashboard data
        dashboard_data = trading_metrics.get_trading_dashboard_data()
        
        # Get symbol analytics if requested
        symbol = request.args.get('symbol')
        hours = request.args.get('hours', 24, type=int)
        
        response_data = {"dashboard": dashboard_data}
        
        if symbol:
            symbol_analytics = trading_metrics.get_symbol_analytics(symbol, hours=hours)
            response_data["symbol_analytics"] = symbol_analytics
        
        return jsonify({
            "success": True,
            "data": response_data
        })
        
    except Exception as e:
        logger.error(f"Error getting trading metrics: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/alerts', methods=['GET'])
def alert_status():
    """Get current alert status and recent alerts"""
    try:
        from monitoring import get_alerting_framework
        alerting = get_alerting_framework()
        
        # Get active alerts
        active_alerts = alerting.get_active_alerts()
        
        # Get alert statistics
        hours = request.args.get('hours', 24, type=int)
        alert_stats = alerting.get_alert_statistics(hours=hours)
        
        # Get recent alerts
        recent_alerts = alerting.get_recent_alerts(limit=50)
        
        return jsonify({
            "success": True,
            "data": {
                "active_alerts": [alert.to_dict() for alert in active_alerts],
                "statistics": alert_stats,
                "recent_alerts": [alert.to_dict() for alert in recent_alerts]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting alert status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge a specific alert"""
    try:
        from monitoring import get_alerting_framework
        alerting = get_alerting_framework()
        
        data = request.get_json() or {}
        acknowledged_by = data.get('acknowledged_by', 'api_user')
        
        result = alerting.acknowledge_alert(alert_id, acknowledged_by)
        
        return jsonify({
            "success": result,
            "message": f"Alert {alert_id} acknowledged" if result else "Failed to acknowledge alert"
        })
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/dashboard', methods=['GET'])
def dashboard_data():
    """Get complete dashboard data with trends"""
    try:
        from monitoring import get_monitoring_dashboard
        dashboard = get_monitoring_dashboard()
        
        # Get current dashboard
        current_dashboard = dashboard.get_current_dashboard()
        
        # Get historical trends
        hours = request.args.get('hours', 6, type=int)
        trends = dashboard.get_historical_trends(hours=hours)
        
        # Get performance baseline
        baseline_hours = request.args.get('baseline_hours', 24, type=int)
        baseline = dashboard.get_performance_baseline(hours=baseline_hours)
        
        return jsonify({
            "success": True,
            "data": {
                "current": current_dashboard,
                "trends": trends,
                "baseline": baseline
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/dashboard/export', methods=['GET'])
def export_dashboard():
    """Export dashboard data in JSON format"""
    try:
        from monitoring import get_monitoring_dashboard
        dashboard = get_monitoring_dashboard()
        
        hours = request.args.get('hours', 24, type=int)
        format_type = request.args.get('format', 'json')
        
        export_data = dashboard.export_dashboard_data(format=format_type, hours=hours)
        
        return jsonify({
            "success": True,
            "data": export_data
        })
        
    except Exception as e:
        logger.error(f"Error exporting dashboard: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@monitoring_bp.route('/thresholds', methods=['GET'])
def get_thresholds():
    """Get current monitoring thresholds"""
    try:
        from monitoring import get_system_monitor, get_alerting_framework
        
        system_monitor = get_system_monitor()
        alerting = get_alerting_framework()
        
        return jsonify({
            "success": True,
            "data": {
                "system_thresholds": system_monitor.thresholds,
                "alert_rules": [rule.to_dict() for rule in alerting.alert_rules.values()]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Initialize monitoring components when blueprint is registered
def init_monitoring():
    """Initialize monitoring components"""
    try:
        from monitoring import (
            get_system_monitor, get_trading_metrics_collector,
            get_alerting_framework, get_health_checker, get_monitoring_dashboard
        )
        
        # Initialize all monitoring components
        system_monitor = get_system_monitor(collection_interval=30)
        trading_metrics = get_trading_metrics_collector(collection_interval=60) 
        alerting = get_alerting_framework()
        health_checker = get_health_checker(check_interval=300)
        dashboard = get_monitoring_dashboard(update_interval=60)
        
        logger.info("✅ Monitoring system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize monitoring system: {e}")
        return False


# Register initialization hook
@monitoring_bp.record
def record_monitoring_init(setup_state):
    """Called when blueprint is registered with app"""
    app = setup_state.app
    with app.app_context():
        init_monitoring()