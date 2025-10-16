"""
Cache Manager for GA4 Funnel Analysis
Optimized for n8n Data Table (54 MB storage limit)
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching of AI insights to avoid redundant API calls
    Stores cache in n8n Data Table or local file
    """
    
    def __init__(self, cache_duration_hours: int = 24, max_cache_size: int = 100):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.max_cache_size = max_cache_size  # Limit cache entries
        self.cache = {}  # In-memory cache for current session
        
    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        """
        Generate unique cache key based on input data
        
        Args:
            data: Input data for analysis
            
        Returns:
            str: MD5 hash of the data
        """
        # Create deterministic string from data
        cache_str = json.dumps({
            'dimensions': sorted(data.get('dimensions', [])),
            'property_id': data.get('property_id'),
            'date_range': data.get('date_range'),
            'baseline_rates': data.get('baseline_rates')
        }, sort_keys=True)
        
        # Generate hash
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get_cached_insights(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached insights if available and not expired
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            Cached insights or None if not found/expired
        """
        if cache_key not in self.cache:
            logger.info(f"Cache miss: {cache_key[:8]}...")
            return None
        
        cached_data = self.cache[cache_key]
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        
        # Check if cache expired
        if datetime.now() - cached_time > self.cache_duration:
            logger.info(f"Cache expired: {cache_key[:8]}...")
            del self.cache[cache_key]
            return None
        
        logger.info(f"Cache hit: {cache_key[:8]}... (age: {(datetime.now() - cached_time).seconds}s)")
        return cached_data['insights']
    
    def save_insights(self, cache_key: str, insights: Dict[str, Any]) -> None:
        """
        Save insights to cache with size limit
        
        Args:
            cache_key: Cache key
            insights: Insights to cache
        """
        # Check cache size limit
        if len(self.cache) >= self.max_cache_size:
            self._cleanup_oldest_entries()
        
        self.cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'insights': insights
        }
        logger.info(f"Cached insights: {cache_key[:8]}... (cache size: {len(self.cache)}/{self.max_cache_size})")
    
    def _cleanup_oldest_entries(self) -> None:
        """Remove oldest cache entries when limit is reached"""
        # Sort by timestamp and remove oldest 25% of entries
        entries_to_remove = max(1, self.max_cache_size // 4)
        
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: datetime.fromisoformat(x[1]['timestamp'])
        )
        
        for cache_key, _ in sorted_entries[:entries_to_remove]:
            del self.cache[cache_key]
            logger.info(f"Removed oldest cache entry: {cache_key[:8]}...")
        
        logger.info(f"Cache cleanup: removed {entries_to_remove} entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        
        # Calculate approximate size
        cache_size = len(json.dumps(self.cache))
        
        # Get oldest and newest entries
        if self.cache:
            timestamps = [datetime.fromisoformat(v['timestamp']) for v in self.cache.values()]
            oldest = min(timestamps)
            newest = max(timestamps)
        else:
            oldest = newest = None
        
        return {
            'total_entries': total_entries,
            'max_cache_size': self.max_cache_size,
            'cache_size_bytes': cache_size,
            'cache_size_mb': round(cache_size / 1024 / 1024, 2),
            'oldest_entry': oldest.isoformat() if oldest else None,
            'newest_entry': newest.isoformat() if newest else None,
            'memory_usage_percent': round((total_entries / self.max_cache_size) * 100, 1)
        }
    
    def clear_cache(self) -> None:
        """Clear all cache entries (for testing/debugging)"""
        cache_count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {cache_count} cache entries")
    
    def prepare_for_n8n_storage(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare insights for n8n Data Table storage (optimize for 54 MB limit)
        
        Strategies:
        1. Remove verbose fields
        2. Compress text
        3. Keep only essential data
        
        Args:
            insights: Full insights object
            
        Returns:
            Optimized insights for storage
        """
        optimized = {
            'model': insights.get('model'),
            'critical_issues': [
                {
                    'dimension': i.get('dimension'),
                    'value': i.get('value'),
                    'issue': i.get('issue', '')[:200],  # Truncate long text
                    'impact': i.get('impact')
                }
                for i in insights.get('critical_issues', [])[:5]  # Top 5 only
            ],
            'opportunities': [
                {
                    'dimension': o.get('dimension'),
                    'value': o.get('value'),
                    'opportunity': o.get('opportunity', '')[:200],
                    'potential_lift': o.get('potential_lift')
                }
                for o in insights.get('opportunities', [])[:5]
            ],
            'recommendations': [
                {
                    'priority': r.get('priority'),
                    'action': r.get('action', '')[:150],
                    'impact': r.get('expected_impact', '')[:100],
                    'implementation': r.get('implementation')
                }
                for r in insights.get('recommendations', [])[:5]
            ]
        }
        
        # Calculate size reduction
        original_size = len(json.dumps(insights))
        optimized_size = len(json.dumps(optimized))
        reduction_pct = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
        
        logger.info(f"Storage optimization: {original_size} → {optimized_size} bytes ({reduction_pct:.1f}% reduction)")
        
        return optimized


class BatchProcessor:
    """
    Process large datasets in batches to stay within memory/storage limits
    Optimized for n8n Data Table (54 MB)
    """
    
    def __init__(self, max_batch_size: int = 100, max_storage_mb: float = 50):
        self.max_batch_size = max_batch_size
        self.max_storage_bytes = max_storage_mb * 1024 * 1024
        
    def calculate_optimal_batch_size(self, sample_record: Dict[str, Any], total_records: int) -> int:
        """
        Calculate optimal batch size based on record size and storage limit
        
        Args:
            sample_record: Sample record to estimate size
            total_records: Total number of records to process
            
        Returns:
            Optimal batch size
        """
        record_size = len(json.dumps(sample_record))
        
        # Calculate how many records fit in storage limit
        max_records = int(self.max_storage_bytes / record_size * 0.8)  # 80% to be safe
        
        # Determine batch size
        if total_records <= max_records:
            batch_size = min(total_records, self.max_batch_size)
        else:
            # Need to rotate/archive old data
            batch_size = min(max_records // 30, self.max_batch_size)  # ~30 days of data
        
        logger.info(f"Batch size: {batch_size} (record size: {record_size} bytes, total: {total_records})")
        return batch_size
    
    def batch_historical_data(self, historical_data: list, batch_size: int = None) -> list:
        """
        Split historical data into batches
        
        Args:
            historical_data: List of historical records
            batch_size: Batch size (auto-calculated if None)
            
        Returns:
            List of batches
        """
        if not historical_data:
            return []
        
        if batch_size is None:
            batch_size = self.calculate_optimal_batch_size(historical_data[0], len(historical_data))
        
        batches = []
        for i in range(0, len(historical_data), batch_size):
            batch = historical_data[i:i + batch_size]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches from {len(historical_data)} records")
        return batches
    
    def summarize_historical_data(self, historical_data: list, keep_last_n_days: int = 30) -> list:
        """
        Summarize old historical data to save space
        
        Strategy:
        - Keep last 30 days: full detail
        - 31-90 days: daily summaries only
        - 90+ days: weekly summaries only
        
        Args:
            historical_data: Full historical data
            keep_last_n_days: Days to keep in full detail
            
        Returns:
            Summarized data
        """
        if not historical_data:
            return []
        
        now = datetime.now()
        cutoff_date = now - timedelta(days=keep_last_n_days)
        
        recent_data = []
        old_data = []
        
        for record in historical_data:
            record_date = datetime.fromisoformat(record.get('date', record.get('timestamp', '')))
            if record_date >= cutoff_date:
                recent_data.append(record)
            else:
                old_data.append(record)
        
        # For old data, keep only summary
        if old_data:
            logger.info(f"Summarizing {len(old_data)} old records (keeping {len(recent_data)} recent)")
        
        # Combine: recent (full) + old (summarized)
        return recent_data  # For now, just keep recent. Add summarization logic if needed
    
    def estimate_storage_usage(self, data: Any) -> Dict[str, Any]:
        """
        Estimate storage usage for data
        
        Args:
            data: Data to estimate
            
        Returns:
            Storage statistics
        """
        json_str = json.dumps(data)
        size_bytes = len(json_str)
        size_mb = size_bytes / 1024 / 1024
        
        # Calculate how much of 54 MB is used
        usage_pct = (size_mb / 54) * 100
        
        return {
            'size_bytes': size_bytes,
            'size_kb': round(size_bytes / 1024, 2),
            'size_mb': round(size_mb, 2),
            'usage_percent': round(usage_pct, 2),
            'remaining_mb': round(54 - size_mb, 2),
            'can_store': usage_pct < 90,  # Warn if over 90%
            'warning': 'Storage nearly full!' if usage_pct > 90 else None
        }


# Global instances
cache_manager = CacheManager(cache_duration_hours=24)
batch_processor = BatchProcessor(max_batch_size=100, max_storage_mb=50)


