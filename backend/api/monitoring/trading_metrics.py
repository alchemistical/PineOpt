"""
Trading Metrics Collector for Advanced Monitoring & Metrics Collection
Epic 7 Sprint 3 - Task 4: Advanced Monitoring & Metrics Collection

Specialized monitoring for trading operations and historical market data processing.
Tracks OHLCV data requests, cache performance, conversion metrics, and trading patterns.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


@dataclass
class MarketDataMetrics:
    """Market data specific performance metrics"""
    timestamp: float
    ohlcv_requests_count: int
    ohlcv_cache_hits: int
    ohlcv_cache_misses: int
    avg_data_fetch_time_ms: float
    data_providers_used: Dict[str, int]  # Provider -> request count
    timeframes_requested: Dict[str, int]  # Timeframe -> request count
    symbols_requested: Dict[str, int]    # Symbol -> request count
    total_data_points_served: int
    data_compression_ratio: float


@dataclass
class TradingOperationMetrics:
    """Trading operations and strategy metrics"""
    timestamp: float
    strategy_conversions_count: int
    conversion_success_rate: float
    avg_conversion_time_ms: float
    backtests_executed: int
    backtest_success_rate: float
    avg_backtest_time_ms: float
    active_strategies: int
    popular_indicators: Dict[str, int]  # Indicator -> usage count
    error_categories: Dict[str, int]    # Error type -> count


@dataclass
class DataQualityMetrics:
    """Data quality and pipeline health metrics"""
    timestamp: float
    missing_data_points: int
    data_gaps_detected: int
    stale_data_warnings: int
    data_freshness_minutes: float
    provider_response_times: Dict[str, float]  # Provider -> avg response time
    data_validation_errors: int
    anomaly_detections: int


class TradingMetricsCollector:
    """Specialized metrics collection for trading operations and market data"""
    
    def __init__(self, collection_interval: int = 60, history_size: int = 1440):
        """
        Initialize trading metrics collector
        
        Args:
            collection_interval: Metrics collection interval in seconds
            history_size: Number of historical metrics to retain (default: 24h at 1min intervals)
        """
        self.collection_interval = collection_interval
        self.history_size = history_size
        
        # Metrics storage
        self.market_data_history: deque = deque(maxlen=history_size)
        self.trading_ops_history: deque = deque(maxlen=history_size)
        self.data_quality_history: deque = deque(maxlen=history_size)
        
        # Real-time tracking
        self.ohlcv_requests = deque(maxlen=10000)  # Last 10k requests
        self.conversion_requests = deque(maxlen=1000)  # Last 1k conversions
        self.backtest_requests = deque(maxlen=1000)   # Last 1k backtests
        self.data_fetch_times = deque(maxlen=1000)    # Response times
        
        # Provider and symbol tracking
        self.provider_stats = defaultdict(lambda: {'requests': 0, 'errors': 0, 'total_time': 0.0})
        self.symbol_popularity = defaultdict(int)
        self.timeframe_usage = defaultdict(int)
        self.indicator_usage = defaultdict(int)
        
        # Data quality tracking
        self.data_quality_issues = deque(maxlen=1000)
        self.provider_health = defaultdict(lambda: {'up': True, 'last_check': time.time()})
        
        # Monitoring thread
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        logger.info(f"TradingMetricsCollector initialized - Collection interval: {collection_interval}s")
    
    def start_monitoring(self):
        """Start background trading metrics monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.info("Trading metrics monitoring started")
    
    def stop_monitoring(self):
        """Stop background trading metrics monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        logger.info("Trading metrics monitoring stopped")
    
    def record_ohlcv_request(self, symbol: str, timeframe: str, provider: str,
                            response_time_ms: float, cache_hit: bool = False,
                            data_points: int = 0, error: bool = False):
        """Record an OHLCV data request for metrics tracking"""
        current_time = time.time()
        
        # Record request details
        self.ohlcv_requests.append({
            'timestamp': current_time,
            'symbol': symbol,
            'timeframe': timeframe,
            'provider': provider,
            'response_time_ms': response_time_ms,
            'cache_hit': cache_hit,
            'data_points': data_points,
            'error': error
        })
        
        # Update provider stats
        self.provider_stats[provider]['requests'] += 1
        self.provider_stats[provider]['total_time'] += response_time_ms
        if error:
            self.provider_stats[provider]['errors'] += 1
        
        # Update usage statistics
        self.symbol_popularity[symbol] += 1
        self.timeframe_usage[timeframe] += 1
        self.data_fetch_times.append(response_time_ms)
        
        logger.debug(f"Recorded OHLCV request: {symbol}:{timeframe} via {provider} "
                    f"({response_time_ms:.1f}ms, cache_hit={cache_hit})")
    
    def record_strategy_conversion(self, strategy_name: str, success: bool,
                                 conversion_time_ms: float, indicators_used: List[str],
                                 error_type: str = None):
        """Record a Pine Script to Python conversion for metrics tracking"""
        current_time = time.time()
        
        self.conversion_requests.append({
            'timestamp': current_time,
            'strategy_name': strategy_name,
            'success': success,
            'conversion_time_ms': conversion_time_ms,
            'indicators_used': indicators_used,
            'error_type': error_type
        })
        
        # Update indicator usage statistics
        for indicator in indicators_used:
            self.indicator_usage[indicator] += 1
        
        logger.debug(f"Recorded strategy conversion: {strategy_name} "
                    f"(success={success}, {conversion_time_ms:.1f}ms)")
    
    def record_backtest_execution(self, strategy_id: str, symbol: str, timeframe: str,
                                success: bool, execution_time_ms: float,
                                data_points: int = 0, error_type: str = None):
        """Record a backtest execution for metrics tracking"""
        current_time = time.time()
        
        self.backtest_requests.append({
            'timestamp': current_time,
            'strategy_id': strategy_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'success': success,
            'execution_time_ms': execution_time_ms,
            'data_points': data_points,
            'error_type': error_type
        })
        
        logger.debug(f"Recorded backtest: {strategy_id} on {symbol}:{timeframe} "
                    f"(success={success}, {execution_time_ms:.1f}ms)")
    
    def record_data_quality_issue(self, issue_type: str, symbol: str, timeframe: str,
                                provider: str, severity: str = "warning",
                                description: str = ""):
        """Record a data quality issue for monitoring"""
        current_time = time.time()
        
        self.data_quality_issues.append({
            'timestamp': current_time,
            'issue_type': issue_type,
            'symbol': symbol,
            'timeframe': timeframe,
            'provider': provider,
            'severity': severity,
            'description': description
        })
        
        if severity == "critical":
            logger.error(f"Data quality issue: {issue_type} for {symbol}:{timeframe} "
                        f"from {provider} - {description}")
        else:
            logger.warning(f"Data quality issue: {issue_type} for {symbol}:{timeframe} "
                          f"from {provider} - {description}")
    
    def collect_market_data_metrics(self) -> MarketDataMetrics:
        """Collect current market data performance metrics"""
        try:
            current_time = time.time()
            hour_ago = current_time - 3600
            
            # Filter recent requests
            recent_ohlcv = [r for r in self.ohlcv_requests if r['timestamp'] >= hour_ago]
            
            if not recent_ohlcv:
                return MarketDataMetrics(
                    timestamp=current_time,
                    ohlcv_requests_count=0,
                    ohlcv_cache_hits=0,
                    ohlcv_cache_misses=0,
                    avg_data_fetch_time_ms=0.0,
                    data_providers_used={},
                    timeframes_requested={},
                    symbols_requested={},
                    total_data_points_served=0,
                    data_compression_ratio=1.0
                )
            
            # Calculate metrics
            total_requests = len(recent_ohlcv)
            cache_hits = sum(1 for r in recent_ohlcv if r['cache_hit'])
            cache_misses = total_requests - cache_hits
            
            avg_fetch_time = sum(r['response_time_ms'] for r in recent_ohlcv) / total_requests
            
            # Provider usage
            providers = defaultdict(int)
            for r in recent_ohlcv:
                providers[r['provider']] += 1
            
            # Timeframe usage
            timeframes = defaultdict(int)
            for r in recent_ohlcv:
                timeframes[r['timeframe']] += 1
            
            # Symbol usage
            symbols = defaultdict(int)
            for r in recent_ohlcv:
                symbols[r['symbol']] += 1
            
            total_data_points = sum(r['data_points'] for r in recent_ohlcv)
            
            return MarketDataMetrics(
                timestamp=current_time,
                ohlcv_requests_count=total_requests,
                ohlcv_cache_hits=cache_hits,
                ohlcv_cache_misses=cache_misses,
                avg_data_fetch_time_ms=avg_fetch_time,
                data_providers_used=dict(providers),
                timeframes_requested=dict(timeframes),
                symbols_requested=dict(symbols),
                total_data_points_served=total_data_points,
                data_compression_ratio=1.2  # Estimated from cache system
            )
            
        except Exception as e:
            logger.error(f"Error collecting market data metrics: {e}")
            return None
    
    def collect_trading_operations_metrics(self) -> TradingOperationMetrics:
        """Collect trading operations performance metrics"""
        try:
            current_time = time.time()
            hour_ago = current_time - 3600
            
            # Filter recent operations
            recent_conversions = [r for r in self.conversion_requests if r['timestamp'] >= hour_ago]
            recent_backtests = [r for r in self.backtest_requests if r['timestamp'] >= hour_ago]
            
            # Conversion metrics
            conversion_count = len(recent_conversions)
            if conversion_count > 0:
                conversion_success_rate = sum(1 for r in recent_conversions if r['success']) / conversion_count * 100
                avg_conversion_time = sum(r['conversion_time_ms'] for r in recent_conversions) / conversion_count
            else:
                conversion_success_rate = 100.0
                avg_conversion_time = 0.0
            
            # Backtest metrics
            backtest_count = len(recent_backtests)
            if backtest_count > 0:
                backtest_success_rate = sum(1 for r in recent_backtests if r['success']) / backtest_count * 100
                avg_backtest_time = sum(r['execution_time_ms'] for r in recent_backtests) / backtest_count
            else:
                backtest_success_rate = 100.0
                avg_backtest_time = 0.0
            
            # Popular indicators (top 10)
            top_indicators = dict(sorted(self.indicator_usage.items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
            
            # Error categories
            error_categories = defaultdict(int)
            for conversion in recent_conversions:
                if not conversion['success'] and conversion['error_type']:
                    error_categories[conversion['error_type']] += 1
            
            for backtest in recent_backtests:
                if not backtest['success'] and backtest['error_type']:
                    error_categories[backtest['error_type']] += 1
            
            return TradingOperationMetrics(
                timestamp=current_time,
                strategy_conversions_count=conversion_count,
                conversion_success_rate=conversion_success_rate,
                avg_conversion_time_ms=avg_conversion_time,
                backtests_executed=backtest_count,
                backtest_success_rate=backtest_success_rate,
                avg_backtest_time_ms=avg_backtest_time,
                active_strategies=len(set(r['strategy_id'] for r in recent_backtests)),
                popular_indicators=top_indicators,
                error_categories=dict(error_categories)
            )
            
        except Exception as e:
            logger.error(f"Error collecting trading operations metrics: {e}")
            return None
    
    def collect_data_quality_metrics(self) -> DataQualityMetrics:
        """Collect data quality and pipeline health metrics"""
        try:
            current_time = time.time()
            hour_ago = current_time - 3600
            
            # Filter recent quality issues
            recent_issues = [i for i in self.data_quality_issues if i['timestamp'] >= hour_ago]
            
            # Count different types of issues
            missing_data = sum(1 for i in recent_issues if i['issue_type'] == 'missing_data')
            data_gaps = sum(1 for i in recent_issues if i['issue_type'] == 'data_gap')
            stale_data = sum(1 for i in recent_issues if i['issue_type'] == 'stale_data')
            validation_errors = sum(1 for i in recent_issues if i['issue_type'] == 'validation_error')
            anomalies = sum(1 for i in recent_issues if i['issue_type'] == 'anomaly')
            
            # Calculate provider response times
            provider_times = {}
            for provider, stats in self.provider_stats.items():
                if stats['requests'] > 0:
                    provider_times[provider] = stats['total_time'] / stats['requests']
            
            # Estimate data freshness (simplified)
            if self.ohlcv_requests:
                last_request = max(r['timestamp'] for r in self.ohlcv_requests)
                freshness_minutes = (current_time - last_request) / 60
            else:
                freshness_minutes = 0.0
            
            return DataQualityMetrics(
                timestamp=current_time,
                missing_data_points=missing_data,
                data_gaps_detected=data_gaps,
                stale_data_warnings=stale_data,
                data_freshness_minutes=freshness_minutes,
                provider_response_times=provider_times,
                data_validation_errors=validation_errors,
                anomaly_detections=anomalies
            )
            
        except Exception as e:
            logger.error(f"Error collecting data quality metrics: {e}")
            return None
    
    def get_trading_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive trading dashboard data"""
        market_metrics = self.collect_market_data_metrics()
        trading_metrics = self.collect_trading_operations_metrics()
        quality_metrics = self.collect_data_quality_metrics()
        
        if not market_metrics or not trading_metrics or not quality_metrics:
            return {"error": "Failed to collect trading metrics"}
        
        return {
            "market_data": {
                "ohlcv_requests_per_hour": market_metrics.ohlcv_requests_count,
                "cache_hit_rate_percent": (market_metrics.ohlcv_cache_hits / 
                                         max(market_metrics.ohlcv_requests_count, 1)) * 100,
                "avg_data_fetch_time_ms": market_metrics.avg_data_fetch_time_ms,
                "popular_symbols": dict(sorted(market_metrics.symbols_requested.items(), 
                                             key=lambda x: x[1], reverse=True)[:10]),
                "timeframe_usage": market_metrics.timeframes_requested,
                "data_providers": market_metrics.data_providers_used,
                "total_data_points": market_metrics.total_data_points_served
            },
            "trading_operations": {
                "conversions_per_hour": trading_metrics.strategy_conversions_count,
                "conversion_success_rate": trading_metrics.conversion_success_rate,
                "backtests_per_hour": trading_metrics.backtests_executed,
                "backtest_success_rate": trading_metrics.backtest_success_rate,
                "active_strategies": trading_metrics.active_strategies,
                "popular_indicators": trading_metrics.popular_indicators,
                "error_categories": trading_metrics.error_categories
            },
            "data_quality": {
                "missing_data_incidents": quality_metrics.missing_data_points,
                "data_gaps_detected": quality_metrics.data_gaps_detected,
                "stale_data_warnings": quality_metrics.stale_data_warnings,
                "data_freshness_minutes": quality_metrics.data_freshness_minutes,
                "provider_performance": quality_metrics.provider_response_times,
                "validation_errors": quality_metrics.data_validation_errors,
                "anomalies_detected": quality_metrics.anomaly_detections
            },
            "collection_time": datetime.now().isoformat()
        }
    
    def get_symbol_analytics(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get detailed analytics for a specific trading symbol"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter requests for this symbol
        symbol_requests = [r for r in self.ohlcv_requests 
                          if r['symbol'] == symbol and r['timestamp'] >= cutoff_time]
        
        if not symbol_requests:
            return {"error": f"No data found for symbol {symbol}"}
        
        # Calculate symbol-specific metrics
        total_requests = len(symbol_requests)
        cache_hits = sum(1 for r in symbol_requests if r['cache_hit'])
        avg_response_time = sum(r['response_time_ms'] for r in symbol_requests) / total_requests
        
        # Timeframe breakdown
        timeframe_usage = defaultdict(int)
        for r in symbol_requests:
            timeframe_usage[r['timeframe']] += 1
        
        # Provider usage
        provider_usage = defaultdict(int)
        for r in symbol_requests:
            provider_usage[r['provider']] += 1
        
        return {
            "symbol": symbol,
            "period_hours": hours,
            "total_requests": total_requests,
            "cache_hit_rate_percent": (cache_hits / total_requests) * 100,
            "avg_response_time_ms": avg_response_time,
            "timeframe_breakdown": dict(timeframe_usage),
            "provider_breakdown": dict(provider_usage),
            "request_frequency_per_hour": total_requests / hours
        }
    
    def _monitoring_loop(self):
        """Background trading metrics monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect and store metrics
                market_metrics = self.collect_market_data_metrics()
                trading_metrics = self.collect_trading_operations_metrics()
                quality_metrics = self.collect_data_quality_metrics()
                
                if market_metrics:
                    self.market_data_history.append(market_metrics)
                
                if trading_metrics:
                    self.trading_ops_history.append(trading_metrics)
                
                if quality_metrics:
                    self.data_quality_history.append(quality_metrics)
                
                # Sleep for collection interval
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Trading metrics monitoring loop error: {e}")
                time.sleep(self.collection_interval)
    
    def __del__(self):
        """Cleanup when collector is destroyed"""
        self.stop_monitoring()


# Global trading metrics collector instance
_trading_metrics_collector: Optional[TradingMetricsCollector] = None


def get_trading_metrics_collector(collection_interval: int = 60) -> TradingMetricsCollector:
    """Get or create global trading metrics collector instance"""
    global _trading_metrics_collector
    if _trading_metrics_collector is None:
        _trading_metrics_collector = TradingMetricsCollector(collection_interval)
        _trading_metrics_collector.start_monitoring()
    return _trading_metrics_collector