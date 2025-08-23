"""
Memory Manager for Performance Optimization
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

Advanced memory management and monitoring for trading applications.
Implements memory profiling, garbage collection optimization, and resource tracking.
"""

import gc
import psutil
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass
import sys

logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot at a point in time"""
    timestamp: float
    total_memory_mb: float
    available_memory_mb: float
    process_memory_mb: float
    process_memory_percent: float
    python_objects_count: int
    garbage_collections: Dict[int, int]


class MemoryManager:
    """Advanced memory management and optimization for trading applications"""
    
    def __init__(self, memory_limit_mb: int = 2048, enable_monitoring: bool = True):
        """
        Initialize memory manager
        
        Args:
            memory_limit_mb: Soft memory limit in MB for the process
            enable_monitoring: Enable continuous memory monitoring
        """
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1_000_000
        self.enable_monitoring = enable_monitoring
        
        # Memory tracking
        self.process = psutil.Process()
        self.memory_snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 1000  # Keep last 1000 snapshots
        
        # Alert thresholds
        self.warning_threshold = 0.8  # 80% of limit
        self.critical_threshold = 0.9  # 90% of limit
        
        # Monitoring thread
        self._monitoring_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        
        # Memory optimization settings
        self.gc_thresholds = (700, 10, 10)  # Tuned for trading data
        self.enable_gc_optimization = True
        
        # Initialize monitoring
        if self.enable_monitoring:
            self._start_monitoring()
        
        # Apply memory optimizations
        self._apply_optimizations()
        
        logger.info(f"MemoryManager initialized - Limit: {memory_limit_mb}MB, "
                   f"Monitoring: {enable_monitoring}")
    
    def get_current_memory_usage(self) -> Dict[str, Any]:
        """Get detailed current memory usage information"""
        # System memory info
        memory_info = psutil.virtual_memory()
        
        # Process memory info
        process_memory = self.process.memory_info()
        process_percent = self.process.memory_percent()
        
        # Python garbage collection info
        gc_counts = {i: gc.get_count()[i] for i in range(3)}
        
        return {
            'system_memory': {
                'total_mb': memory_info.total / 1_000_000,
                'available_mb': memory_info.available / 1_000_000,
                'used_mb': memory_info.used / 1_000_000,
                'used_percent': memory_info.percent
            },
            'process_memory': {
                'rss_mb': process_memory.rss / 1_000_000,  # Resident Set Size
                'vms_mb': process_memory.vms / 1_000_000,  # Virtual Memory Size
                'percent': process_percent,
                'limit_mb': self.memory_limit_mb,
                'limit_usage_percent': (process_memory.rss / self.memory_limit_bytes) * 100
            },
            'python_memory': {
                'objects_count': len(gc.get_objects()),
                'gc_counts': gc_counts,
                'gc_stats': gc.get_stats()
            },
            'memory_warnings': self._check_memory_warnings(process_memory.rss)
        }
    
    def create_memory_snapshot(self) -> MemorySnapshot:
        """Create a memory usage snapshot"""
        memory_info = psutil.virtual_memory()
        process_memory = self.process.memory_info()
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            total_memory_mb=memory_info.total / 1_000_000,
            available_memory_mb=memory_info.available / 1_000_000,
            process_memory_mb=process_memory.rss / 1_000_000,
            process_memory_percent=self.process.memory_percent(),
            python_objects_count=len(gc.get_objects()),
            garbage_collections={i: gc.get_count()[i] for i in range(3)}
        )
        
        # Store snapshot
        self.memory_snapshots.append(snapshot)
        
        # Limit snapshot history
        if len(self.memory_snapshots) > self.max_snapshots:
            self.memory_snapshots = self.memory_snapshots[-self.max_snapshots:]
        
        return snapshot
    
    def get_memory_trends(self, minutes: int = 30) -> Dict[str, Any]:
        """Analyze memory usage trends over specified time period"""
        if not self.memory_snapshots:
            return {'error': 'No memory snapshots available'}
        
        # Filter snapshots by time
        cutoff_time = time.time() - (minutes * 60)
        recent_snapshots = [
            s for s in self.memory_snapshots 
            if s.timestamp >= cutoff_time
        ]
        
        if len(recent_snapshots) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Calculate trends
        process_memories = [s.process_memory_mb for s in recent_snapshots]
        object_counts = [s.python_objects_count for s in recent_snapshots]
        
        return {
            'period_minutes': minutes,
            'snapshots_count': len(recent_snapshots),
            'process_memory_trend': {
                'start_mb': process_memories[0],
                'end_mb': process_memories[-1],
                'change_mb': process_memories[-1] - process_memories[0],
                'change_percent': ((process_memories[-1] - process_memories[0]) / process_memories[0]) * 100,
                'peak_mb': max(process_memories),
                'average_mb': sum(process_memories) / len(process_memories)
            },
            'object_count_trend': {
                'start_count': object_counts[0],
                'end_count': object_counts[-1],
                'change_count': object_counts[-1] - object_counts[0],
                'peak_count': max(object_counts),
                'average_count': sum(object_counts) / len(object_counts)
            },
            'memory_stability': self._calculate_memory_stability(process_memories)
        }
    
    def optimize_memory(self, force_gc: bool = True) -> Dict[str, Any]:
        """Run memory optimization routines"""
        start_memory = self.process.memory_info().rss / 1_000_000
        
        optimization_results = {
            'start_memory_mb': start_memory,
            'optimizations_applied': []
        }
        
        if force_gc:
            # Force garbage collection
            objects_before = len(gc.get_objects())
            gc.collect()
            objects_after = len(gc.get_objects())
            
            optimization_results['optimizations_applied'].append({
                'type': 'garbage_collection',
                'objects_freed': objects_before - objects_after
            })
        
        # Clear internal caches if needed
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
            optimization_results['optimizations_applied'].append({
                'type': 'type_cache_clear'
            })
        
        end_memory = self.process.memory_info().rss / 1_000_000
        optimization_results.update({
            'end_memory_mb': end_memory,
            'memory_freed_mb': start_memory - end_memory,
            'memory_reduction_percent': ((start_memory - end_memory) / start_memory) * 100 if start_memory > 0 else 0
        })
        
        logger.info(f"Memory optimization completed - Freed: {start_memory - end_memory:.1f}MB")
        return optimization_results
    
    def check_memory_health(self) -> Dict[str, Any]:
        """Comprehensive memory health check"""
        current_usage = self.get_current_memory_usage()
        process_memory_mb = current_usage['process_memory']['rss_mb']
        memory_percent = (process_memory_mb / self.memory_limit_mb) * 100
        
        # Determine health status
        if memory_percent < 50:
            health_status = 'excellent'
        elif memory_percent < 70:
            health_status = 'good'
        elif memory_percent < 85:
            health_status = 'warning'
        else:
            health_status = 'critical'
        
        # Calculate recent memory growth
        growth_rate = 0
        if len(self.memory_snapshots) >= 10:
            recent_snapshots = self.memory_snapshots[-10:]
            start_memory = recent_snapshots[0].process_memory_mb
            end_memory = recent_snapshots[-1].process_memory_mb
            time_diff = recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp
            
            if time_diff > 0:
                growth_rate = (end_memory - start_memory) / time_diff  # MB per second
        
        health_report = {
            'health_status': health_status,
            'current_memory_mb': process_memory_mb,
            'memory_limit_mb': self.memory_limit_mb,
            'memory_usage_percent': memory_percent,
            'memory_growth_rate_mb_per_minute': growth_rate * 60,
            'recommendations': self._generate_recommendations(health_status, memory_percent, growth_rate),
            'last_check': datetime.now().isoformat()
        }
        
        return health_report
    
    def _start_monitoring(self):
        """Start background memory monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        logger.debug("Memory monitoring started")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                snapshot = self.create_memory_snapshot()
                
                # Check for memory warnings
                warnings = self._check_memory_warnings(snapshot.process_memory_mb * 1_000_000)
                if warnings:
                    for warning in warnings:
                        logger.warning(f"Memory warning: {warning}")
                
                # Sleep for monitoring interval
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(30)  # Sleep longer on error
    
    def _apply_optimizations(self):
        """Apply memory optimizations at initialization"""
        if self.enable_gc_optimization:
            # Set optimized garbage collection thresholds
            gc.set_threshold(*self.gc_thresholds)
            logger.debug(f"Applied GC thresholds: {self.gc_thresholds}")
    
    def _check_memory_warnings(self, memory_bytes: int) -> List[str]:
        """Check for memory usage warnings"""
        warnings = []
        memory_percent = memory_bytes / self.memory_limit_bytes
        
        if memory_percent >= self.critical_threshold:
            warnings.append(f"CRITICAL: Memory usage at {memory_percent:.1%} of limit ({memory_bytes / 1_000_000:.1f}MB)")
        elif memory_percent >= self.warning_threshold:
            warnings.append(f"WARNING: Memory usage at {memory_percent:.1%} of limit ({memory_bytes / 1_000_000:.1f}MB)")
        
        return warnings
    
    def _calculate_memory_stability(self, memory_values: List[float]) -> str:
        """Calculate memory stability score"""
        if len(memory_values) < 5:
            return 'insufficient_data'
        
        # Calculate coefficient of variation (standard deviation / mean)
        mean_memory = sum(memory_values) / len(memory_values)
        variance = sum((x - mean_memory) ** 2 for x in memory_values) / len(memory_values)
        std_dev = variance ** 0.5
        
        if mean_memory > 0:
            cv = std_dev / mean_memory
            
            if cv < 0.05:
                return 'excellent'
            elif cv < 0.1:
                return 'good'
            elif cv < 0.2:
                return 'moderate'
            else:
                return 'unstable'
        
        return 'unknown'
    
    def _generate_recommendations(self, health_status: str, memory_percent: float, 
                                 growth_rate: float) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        if health_status == 'critical':
            recommendations.append("Immediate action required: Memory usage is critical")
            recommendations.append("Run memory optimization: optimize_memory()")
            recommendations.append("Consider restarting the application")
        
        elif health_status == 'warning':
            recommendations.append("Monitor memory usage closely")
            recommendations.append("Consider running garbage collection")
        
        if growth_rate > 1.0:  # Growing more than 1MB per minute
            recommendations.append("Memory growth detected - investigate potential memory leaks")
            recommendations.append("Review cache sizes and TTL settings")
        
        if memory_percent > 80:
            recommendations.append("Consider increasing memory limit")
            recommendations.append("Optimize cache eviction policies")
        
        return recommendations
    
    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        logger.debug("Memory monitoring stopped")
    
    def __del__(self):
        """Cleanup when manager is destroyed"""
        self.stop_monitoring()


def memory_profiler(track_objects: bool = False):
    """
    Decorator to profile memory usage of functions
    
    Args:
        track_objects: Track Python object count changes
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get initial memory state
            process = psutil.Process()
            start_memory = process.memory_info().rss
            start_objects = len(gc.get_objects()) if track_objects else 0
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Get final memory state
                end_memory = process.memory_info().rss
                end_objects = len(gc.get_objects()) if track_objects else 0
                execution_time = time.time() - start_time
                
                # Calculate metrics
                memory_change = (end_memory - start_memory) / 1_000_000  # MB
                object_change = end_objects - start_objects if track_objects else 0
                
                # Log memory profile
                logger.info(f"Memory Profile [{func.__name__}]: "
                           f"Memory: {memory_change:+.1f}MB, "
                           f"Time: {execution_time:.3f}s" +
                           (f", Objects: {object_change:+d}" if track_objects else ""))
                
                return result
                
            except Exception as e:
                # Log memory state even on exception
                end_memory = process.memory_info().rss
                memory_change = (end_memory - start_memory) / 1_000_000
                logger.error(f"Memory Profile [{func.__name__}] FAILED: "
                           f"Memory: {memory_change:+.1f}MB, Error: {e}")
                raise
        
        return wrapper
    return decorator


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(memory_limit_mb: int = 2048) -> MemoryManager:
    """Get or create global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(memory_limit_mb)
    return _memory_manager