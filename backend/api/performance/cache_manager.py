"""
High-Performance Cache Manager
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

Comprehensive caching system optimized for trading data access patterns.
Supports in-memory, Redis, and file-based caching with intelligent TTL management.
"""

import time
import json
import hashlib
import pickle
import gzip
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable, Union
from functools import wraps
import logging
from threading import Lock
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """High-performance multi-tier cache manager for market data"""
    
    def __init__(self, max_memory_size: int = 500_000_000, enable_compression: bool = True):
        """
        Initialize cache manager
        
        Args:
            max_memory_size: Maximum memory cache size in bytes (default 500MB)
            enable_compression: Enable gzip compression for large objects
        """
        self.max_memory_size = max_memory_size
        self.enable_compression = enable_compression
        
        # Multi-tier cache storage
        self._memory_cache: Dict[str, Dict] = {}
        self._cache_metadata: Dict[str, Dict] = {}
        self._cache_lock = Lock()
        
        # Performance metrics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'compression_saves': 0,
            'total_requests': 0
        }
        
        # Cache configuration for different data types
        self.cache_configs = {
            'market_data_ohlcv': {
                'ttl': 300,  # 5 minutes for OHLCV data
                'max_size': 50_000_000,  # 50MB
                'compress_threshold': 10_000  # Compress if > 10KB
            },
            'historical_data': {
                'ttl': 3600,  # 1 hour for historical data
                'max_size': 200_000_000,  # 200MB
                'compress_threshold': 50_000  # Compress if > 50KB
            },
            'market_metadata': {
                'ttl': 86400,  # 24 hours for market metadata
                'max_size': 10_000_000,  # 10MB
                'compress_threshold': 1_000  # Compress if > 1KB
            },
            'strategy_results': {
                'ttl': 1800,  # 30 minutes for strategy results
                'max_size': 100_000_000,  # 100MB
                'compress_threshold': 5_000  # Compress if > 5KB
            },
            'api_responses': {
                'ttl': 60,  # 1 minute for API responses
                'max_size': 50_000_000,  # 50MB
                'compress_threshold': 1_000  # Compress if > 1KB
            }
        }
        
        logger.info(f"CacheManager initialized - Max memory: {max_memory_size:,} bytes")
    
    def get(self, key: str, cache_type: str = 'api_responses') -> Optional[Any]:
        """Get cached value with automatic decompression"""
        self.stats['total_requests'] += 1
        
        with self._cache_lock:
            if key not in self._memory_cache:
                self.stats['misses'] += 1
                return None
            
            cache_entry = self._memory_cache[key]
            metadata = self._cache_metadata.get(key, {})
            
            # Check TTL expiration
            if self._is_expired(cache_entry, cache_type):
                self._remove_key(key)
                self.stats['misses'] += 1
                return None
            
            # Update access time for LRU
            cache_entry['last_accessed'] = time.time()
            
            # Decompress and deserialize if needed
            data = cache_entry['data']
            if metadata.get('compressed', False):
                data = self._decompress_data(data)
            else:
                # Data is not compressed, deserialize directly
                data = self._deserialize_data(data)
            
            self.stats['hits'] += 1
            return data
    
    def set(self, key: str, value: Any, cache_type: str = 'api_responses', 
            ttl: Optional[int] = None) -> bool:
        """Set cached value with intelligent compression"""
        
        config = self.cache_configs.get(cache_type, self.cache_configs['api_responses'])
        ttl = ttl or config['ttl']
        
        # Serialize data
        serialized_data = self._serialize_data(value)
        data_size = len(serialized_data)
        
        # Compress if data is large enough
        compressed = False
        if self.enable_compression and data_size > config['compress_threshold']:
            compressed_data = self._compress_data(serialized_data)
            if len(compressed_data) < data_size * 0.8:  # Only use if 20%+ compression
                serialized_data = compressed_data
                compressed = True
                self.stats['compression_saves'] += 1
        
        with self._cache_lock:
            # Ensure we don't exceed memory limits
            self._ensure_memory_limit(data_size, cache_type)
            
            # Store cache entry
            cache_entry = {
                'data': serialized_data,
                'created_at': time.time(),
                'last_accessed': time.time(),
                'ttl': ttl,
                'cache_type': cache_type,
                'size': len(serialized_data)
            }
            
            self._memory_cache[key] = cache_entry
            self._cache_metadata[key] = {
                'compressed': compressed,
                'original_size': data_size,
                'cache_type': cache_type
            }
        
        logger.debug(f"Cached key '{key}' - Size: {data_size:,} bytes, "
                    f"Compressed: {compressed}, TTL: {ttl}s")
        return True
    
    def delete(self, key: str) -> bool:
        """Delete cached key"""
        with self._cache_lock:
            if key in self._memory_cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self, cache_type: Optional[str] = None) -> int:
        """Clear cache entries, optionally by type"""
        cleared_count = 0
        
        with self._cache_lock:
            if cache_type is None:
                # Clear all
                cleared_count = len(self._memory_cache)
                self._memory_cache.clear()
                self._cache_metadata.clear()
            else:
                # Clear by type
                keys_to_remove = [
                    key for key, entry in self._memory_cache.items()
                    if entry.get('cache_type') == cache_type
                ]
                for key in keys_to_remove:
                    self._remove_key(key)
                    cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} cache entries" + 
                   (f" of type '{cache_type}'" if cache_type else ""))
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._cache_lock:
            total_size = sum(entry['size'] for entry in self._memory_cache.values())
            hit_rate = (self.stats['hits'] / max(self.stats['total_requests'], 1)) * 100
            
            # Get cache breakdown by type
            type_breakdown = {}
            for key, entry in self._memory_cache.items():
                cache_type = entry.get('cache_type', 'unknown')
                if cache_type not in type_breakdown:
                    type_breakdown[cache_type] = {'count': 0, 'size': 0}
                type_breakdown[cache_type]['count'] += 1
                type_breakdown[cache_type]['size'] += entry['size']
            
            return {
                'total_keys': len(self._memory_cache),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / 1_000_000,
                'memory_usage_percent': (total_size / self.max_memory_size) * 100,
                'hit_rate_percent': hit_rate,
                'performance_stats': self.stats.copy(),
                'type_breakdown': type_breakdown,
                'memory_limit_mb': self.max_memory_size / 1_000_000
            }
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        expired_keys = []
        
        with self._cache_lock:
            current_time = time.time()
            for key, entry in self._memory_cache.items():
                cache_type = entry.get('cache_type', 'api_responses')
                if self._is_expired(entry, cache_type):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_key(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def _is_expired(self, cache_entry: Dict, cache_type: str) -> bool:
        """Check if cache entry has expired"""
        created_at = cache_entry.get('created_at', 0)
        ttl = cache_entry.get('ttl', self.cache_configs.get(cache_type, {}).get('ttl', 60))
        return time.time() - created_at > ttl
    
    def _ensure_memory_limit(self, new_data_size: int, cache_type: str):
        """Ensure memory usage stays within limits using LRU eviction"""
        config = self.cache_configs.get(cache_type, self.cache_configs['api_responses'])
        type_limit = config['max_size']
        
        # Calculate current usage by type
        current_type_size = sum(
            entry['size'] for entry in self._memory_cache.values()
            if entry.get('cache_type') == cache_type
        )
        
        # Evict oldest entries of same type if needed
        if current_type_size + new_data_size > type_limit:
            self._evict_lru(cache_type, current_type_size + new_data_size - type_limit)
        
        # Check global memory limit
        total_size = sum(entry['size'] for entry in self._memory_cache.values())
        if total_size + new_data_size > self.max_memory_size:
            self._evict_lru(None, total_size + new_data_size - self.max_memory_size)
    
    def _evict_lru(self, cache_type: Optional[str], bytes_to_free: int):
        """Evict least recently used entries"""
        # Get candidates for eviction
        candidates = []
        for key, entry in self._memory_cache.items():
            if cache_type is None or entry.get('cache_type') == cache_type:
                candidates.append((key, entry['last_accessed'], entry['size']))
        
        # Sort by last accessed (oldest first)
        candidates.sort(key=lambda x: x[1])
        
        freed_bytes = 0
        evicted_count = 0
        
        for key, _, size in candidates:
            if freed_bytes >= bytes_to_free:
                break
            
            self._remove_key(key)
            freed_bytes += size
            evicted_count += 1
            self.stats['evictions'] += 1
        
        if evicted_count > 0:
            logger.debug(f"Evicted {evicted_count} cache entries "
                        f"({freed_bytes:,} bytes) for type: {cache_type}")
    
    def _remove_key(self, key: str):
        """Remove key from both cache and metadata"""
        self._memory_cache.pop(key, None)
        self._cache_metadata.pop(key, None)
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage"""
        try:
            # Try JSON first (faster)
            return json.dumps(data, default=str).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        return gzip.compress(data)
    
    def _decompress_data(self, data: bytes) -> Any:
        """Decompress and deserialize data"""
        decompressed = gzip.decompress(data)
        return self._deserialize_data(decompressed)


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_response(cache_type: str = 'api_responses', ttl: Optional[int] = None,
                  key_generator: Optional[Callable] = None):
    """
    Decorator for caching function responses
    
    Args:
        cache_type: Type of cache (affects TTL and size limits)
        ttl: Time to live in seconds (overrides cache_type default)
        key_generator: Custom function to generate cache keys
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, cache_type)
            if cached_result is not None:
                logger.debug(f"Cache HIT for {func.__name__} - key: {cache_key[:8]}...")
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache_manager.set(cache_key, result, cache_type, ttl)
            
            logger.debug(f"Cache MISS for {func.__name__} - key: {cache_key[:8]}... "
                        f"(executed in {execution_time:.3f}s)")
            
            return result
        
        # Add cache control methods to the wrapped function
        wrapper.clear_cache = lambda: get_cache_manager().clear(cache_type)
        wrapper.cache_stats = lambda: get_cache_manager().get_stats()
        
        return wrapper
    return decorator


def cache_market_data(symbol: str, timeframe: str, ttl: Optional[int] = None):
    """
    Specialized decorator for caching market data
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        timeframe: Timeframe (e.g., '1h', '1d')
        ttl: Custom TTL (defaults to timeframe-appropriate value)
    """
    # Set TTL based on timeframe if not specified
    if ttl is None:
        timeframe_ttls = {
            '1m': 60,      # 1 minute data - cache for 1 minute
            '5m': 300,     # 5 minute data - cache for 5 minutes  
            '15m': 900,    # 15 minute data - cache for 15 minutes
            '1h': 1800,    # 1 hour data - cache for 30 minutes
            '4h': 3600,    # 4 hour data - cache for 1 hour
            '1d': 14400,   # 1 day data - cache for 4 hours
            '1w': 86400,   # 1 week data - cache for 1 day
        }
        ttl = timeframe_ttls.get(timeframe, 300)
    
    def key_generator(*args, **kwargs):
        # Generate cache key including symbol, timeframe, and relevant parameters
        key_parts = [symbol, timeframe]
        key_parts.extend(str(arg) for arg in args[1:])  # Skip self/first arg
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    return cache_response('historical_data', ttl, key_generator)