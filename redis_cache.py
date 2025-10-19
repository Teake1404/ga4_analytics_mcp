"""
Redis Cache Manager for GA4 Data
Handles caching and retrieval of GA4 data with TTL
"""
import json
import redis
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class RedisCacheManager:
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = self._get_redis_client()
        self.default_ttl = 14400  # 4 hours
    
    def _get_redis_client(self) -> redis.Redis:
        """Get Redis client with connection settings"""
        try:
            # Redis connection settings
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", "6379"))
            password = os.getenv("REDIS_PASSWORD")
            db = int(os.getenv("REDIS_DB", "0"))
            
            # Create Redis client
            client = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Return a mock client for development
            return MockRedisClient()
    
    def _get_cache_key(self, property_id: str, report_type: str, date: str = None) -> str:
        """Generate cache key for GA4 data"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        return f"ga4:{property_id}:{report_type}:{date}"
    
    def get_cached_data(self, property_id: str, report_type: str, date: str = None) -> Optional[Dict[str, Any]]:
        """
        Get cached GA4 data
        Returns None if not found or expired
        """
        try:
            cache_key = self._get_cache_key(property_id, report_type, date)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"Cache hit for {cache_key}")
                return data
            else:
                logger.info(f"Cache miss for {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get cached data: {e}")
            return None
    
    def cache_data(self, property_id: str, report_type: str, data: Dict[str, Any], ttl: int = None, date: str = None) -> bool:
        """
        Cache GA4 data with TTL
        Returns True if successful
        """
        try:
            cache_key = self._get_cache_key(property_id, report_type, date)
            ttl = ttl or self.default_ttl
            
            # Add metadata
            cache_data = {
                "data": data,
                "cached_at": datetime.now().isoformat(),
                "ttl": ttl,
                "property_id": property_id,
                "report_type": report_type
            }
            
            # Store in Redis
            self.redis_client.setex(cache_key, ttl, json.dumps(cache_data))
            logger.info(f"Cached data for {cache_key} with TTL {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache data: {e}")
            return False
    
    def get_funnel_data(self, property_id: str, date: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached funnel data"""
        cached = self.get_cached_data(property_id, "funnel", date)
        return cached.get("data") if cached else None
    
    def cache_funnel_data(self, property_id: str, data: List[Dict[str, Any]], ttl: int = None, date: str = None) -> bool:
        """Cache funnel data"""
        return self.cache_data(property_id, "funnel", data, ttl, date)
    
    def get_traffic_sources(self, property_id: str, date: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached traffic sources data"""
        cached = self.get_cached_data(property_id, "traffic_sources", date)
        return cached.get("data") if cached else None
    
    def cache_traffic_sources(self, property_id: str, data: List[Dict[str, Any]], ttl: int = None, date: str = None) -> bool:
        """Cache traffic sources data"""
        return self.cache_data(property_id, "traffic_sources", data, ttl, date)
    
    def get_overview_metrics(self, property_id: str, date: str = None) -> Optional[Dict[str, Any]]:
        """Get cached overview metrics"""
        cached = self.get_cached_data(property_id, "overview", date)
        return cached.get("data") if cached else None
    
    def cache_overview_metrics(self, property_id: str, data: Dict[str, Any], ttl: int = None, date: str = None) -> bool:
        """Cache overview metrics"""
        return self.cache_data(property_id, "overview", data, ttl, date)
    
    def clear_cache(self, property_id: str, report_type: str = None, date: str = None) -> bool:
        """
        Clear cache for specific property/report type
        If report_type is None, clears all reports for the property
        """
        try:
            if report_type:
                cache_key = self._get_cache_key(property_id, report_type, date)
                self.redis_client.delete(cache_key)
                logger.info(f"Cleared cache for {cache_key}")
            else:
                # Clear all reports for this property
                pattern = f"ga4:{property_id}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache entries for property {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_stats(self, property_id: str) -> Dict[str, Any]:
        """Get cache statistics for a property"""
        try:
            pattern = f"ga4:{property_id}:*"
            keys = self.redis_client.keys(pattern)
            
            stats = {
                "total_keys": len(keys),
                "keys": [],
                "ttl_info": {}
            }
            
            for key in keys:
                ttl = self.redis_client.ttl(key)
                stats["keys"].append(key)
                stats["ttl_info"][key] = ttl
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}


class MockRedisClient:
    """Mock Redis client for development when Redis is not available"""
    
    def __init__(self):
        self.data = {}
        logger.warning("Using MockRedisClient - Redis not available")
    
    def ping(self):
        return True
    
    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    def setex(self, key: str, time: int, value: str):
        self.data[key] = value
    
    def delete(self, *keys):
        for key in keys:
            self.data.pop(key, None)
    
    def keys(self, pattern: str):
        import fnmatch
        return [key for key in self.data.keys() if fnmatch.fnmatch(key, pattern)]
    
    def ttl(self, key: str) -> int:
        return 300  # Mock TTL

