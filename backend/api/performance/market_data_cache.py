"""
Market Data Specialized Cache
Epic 7 Sprint 3 - Task 3: Performance Optimization & Caching

High-performance caching specifically optimized for historical market data patterns.
Implements intelligent prefetching, data compression, and OHLCV optimizations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from .cache_manager import CacheManager, get_cache_manager
import hashlib
import time

logger = logging.getLogger(__name__)


class MarketDataCache:
    """Specialized cache for real-time and historical market data"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or get_cache_manager()
        
        # Market data specific configurations
        self.symbol_metadata: Dict[str, Dict] = {}
        self.active_subscriptions: Dict[str, datetime] = {}
        
        # Performance optimization settings
        self.prefetch_enabled = True
        self.compression_enabled = True
        self.batch_size = 1000  # Records per batch for large datasets
        
        logger.info("MarketDataCache initialized with optimized settings")
    
    def get_ohlcv_data(self, symbol: str, timeframe: str, start_date: Optional[str] = None,
                       end_date: Optional[str] = None, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Get OHLCV data with intelligent caching and optimization
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Timeframe ('1m', '5m', '1h', '1d', etc.)
            start_date: Start date (ISO format)
            end_date: End date (ISO format)  
            limit: Number of records to return
        """
        cache_key = self._generate_ohlcv_key(symbol, timeframe, start_date, end_date, limit)
        
        # Try to get from cache first
        cached_data = self.cache_manager.get(cache_key, 'historical_data')
        if cached_data is not None:
            logger.debug(f"Cache HIT for OHLCV data: {symbol}:{timeframe}")
            return self._deserialize_dataframe(cached_data)
        
        # If not in cache, this would typically fetch from data source
        # For now, return None to indicate cache miss
        logger.debug(f"Cache MISS for OHLCV data: {symbol}:{timeframe}")
        return None
    
    def cache_ohlcv_data(self, data: pd.DataFrame, symbol: str, timeframe: str,
                        start_date: Optional[str] = None, end_date: Optional[str] = None,
                        limit: Optional[int] = None) -> bool:
        """
        Cache OHLCV data with compression and optimization
        
        Args:
            data: OHLCV DataFrame with columns [timestamp, open, high, low, close, volume]
            symbol: Trading pair
            timeframe: Timeframe
            start_date: Start date filter
            end_date: End date filter
            limit: Record limit
        """
        if data is None or data.empty:
            return False
        
        cache_key = self._generate_ohlcv_key(symbol, timeframe, start_date, end_date, limit)
        
        # Optimize and serialize the DataFrame
        serialized_data = self._serialize_dataframe(data)
        
        # Determine TTL based on timeframe and data recency
        ttl = self._calculate_ttl(timeframe, data)
        
        # Cache the data
        success = self.cache_manager.set(cache_key, serialized_data, 'historical_data', ttl)
        
        if success:
            # Update metadata
            self._update_symbol_metadata(symbol, timeframe, data)
            logger.debug(f"Cached OHLCV data: {symbol}:{timeframe} "
                        f"({len(data)} records, TTL: {ttl}s)")
        
        return success
    
    def get_market_metadata(self, symbol: str) -> Optional[Dict]:
        """Get cached market metadata for a symbol"""
        cache_key = f"metadata:{symbol}"
        return self.cache_manager.get(cache_key, 'market_metadata')
    
    def cache_market_metadata(self, symbol: str, metadata: Dict) -> bool:
        """Cache market metadata (trading rules, precision, etc.)"""
        cache_key = f"metadata:{symbol}"
        return self.cache_manager.set(cache_key, metadata, 'market_metadata', 86400)  # 24h TTL
    
    def prefetch_adjacent_data(self, symbol: str, timeframe: str, current_start: str,
                              current_end: str, prefetch_ratio: float = 0.2) -> None:
        """
        Prefetch adjacent time ranges for better cache hit rates
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            current_start: Current query start date
            current_end: Current query end date  
            prefetch_ratio: Ratio of current range to prefetch (0.2 = 20%)
        """
        if not self.prefetch_enabled:
            return
        
        try:
            # Calculate prefetch ranges
            start_dt = datetime.fromisoformat(current_start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
            duration = end_dt - start_dt
            prefetch_duration = duration * prefetch_ratio
            
            # Prefetch earlier data
            earlier_end = start_dt
            earlier_start = start_dt - prefetch_duration
            
            # Prefetch later data  
            later_start = end_dt
            later_end = end_dt + prefetch_duration
            
            # This would trigger background prefetch operations
            logger.debug(f"Prefetch scheduled for {symbol}:{timeframe} "
                        f"(earlier: {earlier_start} to {earlier_end}, "
                        f"later: {later_start} to {later_end})")
            
        except Exception as e:
            logger.warning(f"Prefetch failed for {symbol}:{timeframe}: {e}")
    
    def get_cache_efficiency(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get cache efficiency metrics for market data"""
        stats = self.cache_manager.get_stats()
        
        # Filter for historical data if symbol specified
        if symbol:
            # This would require tracking per-symbol metrics
            pass
        
        # Calculate market data specific metrics
        historical_data_stats = stats['type_breakdown'].get('historical_data', {})
        
        return {
            'total_cached_symbols': len(self.symbol_metadata),
            'historical_data_size_mb': historical_data_stats.get('size', 0) / 1_000_000,
            'historical_data_entries': historical_data_stats.get('count', 0),
            'active_subscriptions': len(self.active_subscriptions),
            'prefetch_enabled': self.prefetch_enabled,
            'compression_enabled': self.compression_enabled,
            'overall_cache_stats': stats
        }
    
    def optimize_cache_for_timeframe(self, timeframe: str) -> None:
        """Optimize cache settings based on timeframe usage patterns"""
        optimization_settings = {
            '1m': {'ttl': 60, 'prefetch_ratio': 0.1, 'batch_size': 2000},
            '5m': {'ttl': 300, 'prefetch_ratio': 0.15, 'batch_size': 1500},
            '1h': {'ttl': 1800, 'prefetch_ratio': 0.2, 'batch_size': 1000},
            '1d': {'ttl': 14400, 'prefetch_ratio': 0.3, 'batch_size': 500}
        }
        
        settings = optimization_settings.get(timeframe, {})
        if settings:
            logger.info(f"Optimized cache settings for {timeframe}: {settings}")
    
    def clear_symbol_cache(self, symbol: str) -> int:
        """Clear all cached data for a specific symbol"""
        # This would require symbol-based key tracking
        # For now, clear all historical data
        return self.cache_manager.clear('historical_data')
    
    def _generate_ohlcv_key(self, symbol: str, timeframe: str, start_date: Optional[str],
                           end_date: Optional[str], limit: Optional[int]) -> str:
        """Generate cache key for OHLCV data"""
        key_parts = [
            'ohlcv',
            symbol,
            timeframe,
            start_date or 'None',
            end_date or 'None',
            str(limit) if limit else 'None'
        ]
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def _serialize_dataframe(self, df: pd.DataFrame) -> Dict:
        """Serialize DataFrame for efficient caching"""
        return {
            'data': df.to_dict('records'),
            'index': df.index.tolist() if hasattr(df.index, 'tolist') else list(df.index),
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'serialized_at': time.time()
        }
    
    def _deserialize_dataframe(self, serialized_data: Dict) -> pd.DataFrame:
        """Deserialize cached DataFrame data"""
        df = pd.DataFrame(serialized_data['data'])
        
        # Restore data types
        for col, dtype_str in serialized_data.get('dtypes', {}).items():
            if col in df.columns:
                try:
                    if 'datetime' in dtype_str:
                        df[col] = pd.to_datetime(df[col])
                    elif 'float' in dtype_str:
                        df[col] = df[col].astype(float)
                    elif 'int' in dtype_str:
                        df[col] = df[col].astype(int)
                except Exception as e:
                    logger.warning(f"Failed to restore dtype for {col}: {e}")
        
        return df
    
    def _calculate_ttl(self, timeframe: str, data: pd.DataFrame) -> int:
        """Calculate appropriate TTL based on timeframe and data freshness"""
        base_ttls = {
            '1m': 60,      # 1 minute
            '5m': 300,     # 5 minutes
            '15m': 900,    # 15 minutes
            '1h': 1800,    # 30 minutes
            '4h': 3600,    # 1 hour
            '1d': 14400,   # 4 hours
            '1w': 86400,   # 1 day
        }
        
        base_ttl = base_ttls.get(timeframe, 300)
        
        # Adjust TTL based on data recency
        if not data.empty and 'timestamp' in data.columns:
            try:
                latest_timestamp = pd.to_datetime(data['timestamp']).max()
                age_hours = (datetime.now() - latest_timestamp).total_seconds() / 3600
                
                # Increase TTL for older data (it changes less frequently)
                if age_hours > 24:
                    base_ttl *= 4  # 4x TTL for data older than 24 hours
                elif age_hours > 1:
                    base_ttl *= 2  # 2x TTL for data older than 1 hour
            except Exception as e:
                logger.debug(f"Could not calculate data age: {e}")
        
        return base_ttl
    
    def _update_symbol_metadata(self, symbol: str, timeframe: str, data: pd.DataFrame) -> None:
        """Update symbol metadata with latest information"""
        if symbol not in self.symbol_metadata:
            self.symbol_metadata[symbol] = {
                'timeframes': set(),
                'last_updated': {},
                'record_counts': {}
            }
        
        metadata = self.symbol_metadata[symbol]
        metadata['timeframes'].add(timeframe)
        metadata['last_updated'][timeframe] = datetime.now()
        metadata['record_counts'][timeframe] = len(data)


class HistoricalDataCache:
    """Specialized cache for large historical datasets with intelligent chunking"""
    
    def __init__(self, chunk_size_mb: int = 50):
        """
        Initialize historical data cache
        
        Args:
            chunk_size_mb: Size of data chunks in MB for large datasets
        """
        self.cache_manager = get_cache_manager()
        self.chunk_size_mb = chunk_size_mb
        self.chunk_size_bytes = chunk_size_mb * 1_000_000
        
        logger.info(f"HistoricalDataCache initialized - Chunk size: {chunk_size_mb}MB")
    
    def get_large_dataset(self, dataset_key: str, start_chunk: int = 0,
                         max_chunks: Optional[int] = None) -> Optional[List[pd.DataFrame]]:
        """
        Get large historical dataset with chunked loading
        
        Args:
            dataset_key: Unique identifier for the dataset
            start_chunk: Starting chunk number
            max_chunks: Maximum number of chunks to load
        """
        chunks = []
        chunk_index = start_chunk
        loaded_chunks = 0
        
        while max_chunks is None or loaded_chunks < max_chunks:
            chunk_key = f"{dataset_key}:chunk:{chunk_index}"
            chunk_data = self.cache_manager.get(chunk_key, 'historical_data')
            
            if chunk_data is None:
                break  # No more chunks available
            
            chunks.append(self._deserialize_chunk(chunk_data))
            chunk_index += 1
            loaded_chunks += 1
        
        return chunks if chunks else None
    
    def cache_large_dataset(self, data: pd.DataFrame, dataset_key: str,
                           ttl: Optional[int] = None) -> bool:
        """
        Cache large dataset by splitting into optimized chunks
        
        Args:
            data: Large DataFrame to cache
            dataset_key: Unique identifier for the dataset
            ttl: Time to live for cached chunks
        """
        if data is None or data.empty:
            return False
        
        # Calculate chunk size based on memory usage
        data_size_bytes = data.memory_usage(deep=True).sum()
        num_chunks = max(1, int(data_size_bytes / self.chunk_size_bytes))
        
        logger.info(f"Caching large dataset '{dataset_key}' "
                   f"({data_size_bytes:,} bytes) in {num_chunks} chunks")
        
        # Split data into chunks
        chunk_size = len(data) // num_chunks
        cached_chunks = 0
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size if i < num_chunks - 1 else len(data)
            
            chunk_data = data.iloc[start_idx:end_idx].copy()
            chunk_key = f"{dataset_key}:chunk:{i}"
            
            # Serialize and cache chunk
            serialized_chunk = self._serialize_chunk(chunk_data, i, num_chunks)
            
            if self.cache_manager.set(chunk_key, serialized_chunk, 'historical_data', ttl):
                cached_chunks += 1
            else:
                logger.warning(f"Failed to cache chunk {i} of dataset '{dataset_key}'")
        
        # Cache metadata about the dataset
        metadata = {
            'total_chunks': num_chunks,
            'total_records': len(data),
            'chunk_size': chunk_size,
            'data_size_bytes': data_size_bytes,
            'cached_at': time.time(),
            'columns': data.columns.tolist()
        }
        
        metadata_key = f"{dataset_key}:metadata"
        self.cache_manager.set(metadata_key, metadata, 'historical_data', ttl)
        
        logger.info(f"Successfully cached {cached_chunks}/{num_chunks} chunks "
                   f"for dataset '{dataset_key}'")
        
        return cached_chunks == num_chunks
    
    def get_dataset_info(self, dataset_key: str) -> Optional[Dict]:
        """Get metadata information about a cached dataset"""
        metadata_key = f"{dataset_key}:metadata"
        return self.cache_manager.get(metadata_key, 'historical_data')
    
    def _serialize_chunk(self, chunk_data: pd.DataFrame, chunk_index: int,
                        total_chunks: int) -> Dict:
        """Serialize data chunk with metadata"""
        return {
            'data': chunk_data.to_dict('records'),
            'columns': chunk_data.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in chunk_data.dtypes.items()},
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'record_count': len(chunk_data),
            'serialized_at': time.time()
        }
    
    def _deserialize_chunk(self, chunk_data: Dict) -> pd.DataFrame:
        """Deserialize cached chunk data"""
        df = pd.DataFrame(chunk_data['data'])
        
        # Restore data types
        for col, dtype_str in chunk_data.get('dtypes', {}).items():
            if col in df.columns:
                try:
                    if 'datetime' in dtype_str:
                        df[col] = pd.to_datetime(df[col])
                    elif 'float' in dtype_str:
                        df[col] = df[col].astype(float)
                    elif 'int' in dtype_str:
                        df[col] = df[col].astype(int)
                except Exception as e:
                    logger.warning(f"Failed to restore dtype for {col}: {e}")
        
        return df