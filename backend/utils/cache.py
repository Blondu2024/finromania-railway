"""Simple in-memory cache for backend API responses"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """Thread-safe in-memory cache"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if datetime.now(timezone.utc) > item['expires_at']:
            # Expired - remove it
            del self._cache[key]
            return None
        
        return item['data']
    
    def set(self, key: str, data: Any, ttl_seconds: int = 30):
        """Set value in cache with TTL"""
        self._cache[key] = {
            'data': data,
            'created_at': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        }
    
    def delete(self, key: str):
        """Delete specific key"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
    
    def clear_prefix(self, prefix: str):
        """Clear all keys starting with prefix"""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._cache[key]
    
    def get_stats(self):
        """Get cache statistics"""
        now = datetime.now(timezone.utc)
        total = len(self._cache)
        valid = sum(1 for item in self._cache.values() if now <= item['expires_at'])
        
        return {
            'total_keys': total,
            'valid_keys': valid,
            'expired_keys': total - valid
        }


# Global cache instance
_cache = SimpleCache()

def get_cache() -> SimpleCache:
    """Get global cache instance"""
    return _cache
