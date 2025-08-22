"""
API Response Caching System for AGK Language Compiler
Caches API responses to improve performance and reduce API costs
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CacheStrategy(Enum):
    """Caching strategies"""
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    NONE = "none"


@dataclass
class CacheEntry:
    """Represents a cached API response"""
    key: str
    response: Any
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[float] = None
    hits: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.timestamp + self.ttl)

    @property
    def age(self) -> float:
        """Get the age of the cache entry in seconds"""
        return time.time() - self.timestamp


@dataclass
class CacheConfig:
    """Configuration for caching behavior"""
    strategy: CacheStrategy = CacheStrategy.MEMORY
    default_ttl: float = 300.0  # 5 minutes
    max_size: int = 1000
    compression: bool = False
    encryption: bool = False
    cache_dir: str = "./cache"
    redis_host: str = "localhost"
    redis_port: int = 6379
    enable_metrics: bool = True


class CacheMetrics:
    """Cache performance metrics"""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.errors = 0
        self.total_requests = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'errors': self.errors,
            'total_requests': self.total_requests,
            'hit_rate': round(self.hit_rate, 4)
        }


class AGKAPICache:
    """API Response Caching System"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = CacheMetrics()
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize the cache based on strategy"""
        if self.config.strategy == CacheStrategy.FILE:
            self._ensure_cache_dir()
        elif self.config.strategy == CacheStrategy.REDIS:
            self._initialize_redis()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        import os
        if not os.path.exists(self.config.cache_dir):
            os.makedirs(self.config.cache_dir)

    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
        except Exception:
            # Fallback to memory cache if Redis is not available
            self.config.strategy = CacheStrategy.MEMORY

    def generate_cache_key(self, service: str, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key for the request"""
        # Create a deterministic key from service, endpoint, and parameters
        key_data = {
            'service': service,
            'endpoint': endpoint,
            'params': params
        }

        # Sort parameters for consistent key generation
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        self.metrics.total_requests += 1

        try:
            if self.config.strategy == CacheStrategy.MEMORY:
                return self._get_memory(key)
            elif self.config.strategy == CacheStrategy.FILE:
                return self._get_file(key)
            elif self.config.strategy == CacheStrategy.REDIS:
                return self._get_redis(key)
        except Exception:
            self.metrics.errors += 1

        self.metrics.misses += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set a value in cache"""
        try:
            ttl = ttl or self.config.default_ttl
            entry = CacheEntry(key=key, response=value, ttl=ttl)

            if self.config.strategy == CacheStrategy.MEMORY:
                return self._set_memory(entry)
            elif self.config.strategy == CacheStrategy.FILE:
                return self._set_file(entry)
            elif self.config.strategy == CacheStrategy.REDIS:
                return self._set_redis(entry)

        except Exception:
            self.metrics.errors += 1

        return False

    def _get_memory(self, key: str) -> Optional[Any]:
        """Get from memory cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry.is_expired:
            del self.cache[key]
            return None

        entry.hits += 1
        self.metrics.hits += 1
        return entry.response

    def _set_memory(self, entry: CacheEntry) -> bool:
        """Set in memory cache"""
        # Check cache size limit
        if len(self.cache) >= self.config.max_size:
            self._evict_lru()

        self.cache[entry.key] = entry
        return True

    def _get_file(self, key: str) -> Optional[Any]:
        """Get from file cache"""
        cache_file = f"{self.config.cache_dir}/{key}.json"

        try:
            if not os.path.exists(cache_file):
                return None

            with open(cache_file, 'r') as f:
                data = json.load(f)

            # Check expiration
            if data.get('ttl') and time.time() > (data['timestamp'] + data['ttl']):
                os.remove(cache_file)
                return None

            # Update hits
            data['hits'] = data.get('hits', 0) + 1
            with open(cache_file, 'w') as f:
                json.dump(data, f)

            self.metrics.hits += 1
            return data['response']

        except Exception:
            return None

    def _set_file(self, entry: CacheEntry) -> bool:
        """Set in file cache"""
        cache_file = f"{self.config.cache_dir}/{entry.key}.json"

        try:
            data = {
                'key': entry.key,
                'response': entry.response,
                'timestamp': entry.timestamp,
                'ttl': entry.ttl,
                'hits': entry.hits
            }

            with open(cache_file, 'w') as f:
                json.dump(data, f)

            return True

        except Exception:
            return False

    def _get_redis(self, key: str) -> Optional[Any]:
        """Get from Redis cache"""
        try:
            data = self.redis_client.get(key)
            if not data:
                return None

            parsed = json.loads(data)

            # Check expiration (Redis handles TTL, but we double-check)
            if parsed.get('ttl') and time.time() > (parsed['timestamp'] + parsed['ttl']):
                self.redis_client.delete(key)
                return None

            # Update hits
            parsed['hits'] = parsed.get('hits', 0) + 1
            self.redis_client.set(key, json.dumps(parsed))

            self.metrics.hits += 1
            return parsed['response']

        except Exception:
            return None

    def _set_redis(self, entry: CacheEntry) -> bool:
        """Set in Redis cache"""
        try:
            data = {
                'key': entry.key,
                'response': entry.response,
                'timestamp': entry.timestamp,
                'ttl': entry.ttl,
                'hits': entry.hits
            }

            self.redis_client.set(entry.key, json.dumps(data), ex=int(entry.ttl or 300))
            return True

        except Exception:
            return False

    def _evict_lru(self):
        """Evict least recently used entries"""
        if not self.cache:
            return

        # Find entry with oldest timestamp
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
        del self.cache[oldest_key]
        self.metrics.evictions += 1

    def clear(self, service: Optional[str] = None):
        """Clear cache entries"""
        if service:
            # Clear entries for specific service
            keys_to_remove = []
            for key in self.cache:
                if key.startswith(f"{service}:"):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self.cache[key]
        else:
            # Clear all entries
            self.cache.clear()

    def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = []
        for key, entry in self.cache.items():
            if entry.is_expired:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'cache_size': len(self.cache),
            'max_size': self.config.max_size,
            'strategy': self.config.strategy.value,
            'default_ttl': self.config.default_ttl,
            'metrics': self.metrics.to_dict()
        }

        # Add cache-specific stats
        if self.config.strategy == CacheStrategy.MEMORY:
            total_hits = sum(entry.hits for entry in self.cache.values())
            oldest_entry = min(self.cache.values(), key=lambda e: e.timestamp) if self.cache else None
            newest_entry = max(self.cache.values(), key=lambda e: e.timestamp) if self.cache else None

            stats.update({
                'total_cache_hits': total_hits,
                'oldest_entry_age': oldest_entry.age if oldest_entry else 0,
                'newest_entry_age': newest_entry.age if newest_entry else 0
            })

        return stats

    def warm_up(self, service: str, endpoints: List[Dict[str, Any]]):
        """Warm up cache with common requests"""
        # This would typically make actual API calls to populate cache
        # For now, we'll just create placeholder entries
        for endpoint in endpoints:
            key = self.generate_cache_key(service, endpoint.get('path', ''), endpoint.get('params', {}))
            # In a real implementation, you would make the API call here
            # self.set(key, placeholder_response, endpoint.get('ttl'))

    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching a pattern"""
        keys_to_remove = []
        for key in self.cache:
            if pattern in key:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.cache[key]


# Global cache instance
api_cache = AGKAPICache()

# Convenience functions for use in generated code
def cache_get(key: str) -> Optional[Any]:
    """Get from cache (for use in generated Python code)"""
    return api_cache.get(key)

def cache_set(key: str, value: Any, ttl: Optional[float] = None) -> bool:
    """Set in cache (for use in generated Python code)"""
    return api_cache.set(key, value, ttl)

def generate_cache_key(service: str, endpoint: str, params: Dict[str, Any]) -> str:
    """Generate cache key (for use in generated Python code)"""
    return api_cache.generate_cache_key(service, endpoint, params)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics (for use in generated Python code)"""
    return api_cache.get_stats()

def clear_cache(service: Optional[str] = None):
    """Clear cache (for use in generated Python code)"""
    api_cache.clear(service)

# Example usage and testing
if __name__ == "__main__":
    # Test the cache system
    print("Testing AGK API Cache...")

    # Test cache operations
    key1 = api_cache.generate_cache_key("openai", "/completions", {"model": "gpt-4"})
    key2 = api_cache.generate_cache_key("anthropic", "/messages", {"model": "claude-3"})

    # Test setting and getting
    api_cache.set(key1, {"response": "Hello from GPT-4"}, ttl=60)
    api_cache.set(key2, {"response": "Hello from Claude"}, ttl=60)

    # Test retrieval
    result1 = api_cache.get(key1)
    result2 = api_cache.get(key2)

    print(f"Cache hit 1: {result1}")
    print(f"Cache hit 2: {result2}")

    # Test statistics
    stats = api_cache.get_stats()
    print(f"Cache stats: {stats}")

    print("API Cache test completed!")