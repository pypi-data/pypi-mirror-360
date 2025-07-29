"""AWS API response caching for terraback."""
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading
import gzip

class ScanCache:
    """Thread-safe cache for AWS API responses."""
    
    def __init__(self, cache_dir: Path = Path("generated/.terraback/cache"), ttl: timedelta = timedelta(hours=1)):
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_size_bytes": 0
        }
        self._memory_cache = {}  # In-memory cache for frequently accessed data
        self._memory_cache_max_size = 100  # Max items in memory
        
    def _generate_key(self, service: str, operation: str, params: Dict[str, Any]) -> str:
        """Generate cache key from service, operation and parameters."""
        # Sort params for consistent hashing
        params_str = json.dumps(params, sort_keys=True, default=str)
        content = f"{service}:{operation}:{params_str}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Use subdirectories to avoid too many files in one directory
        return self.cache_dir / key[:2] / key[2:4] / f"{key}.json.gz"
    
    def get(self, service: str, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available and not expired."""
        key = self._generate_key(service, operation, params)
        
        # Check memory cache first
        with self._lock:
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if self._is_valid(entry):
                    self._stats["hits"] += 1
                    return entry["data"]
                else:
                    del self._memory_cache[key]
        
        # Check disk cache
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            with self._lock:
                self._stats["misses"] += 1
            return None
            
        try:
            with gzip.open(cache_path, 'rt', encoding='utf-8') as f:
                entry = json.load(f)
            
            if self._is_valid(entry):
                with self._lock:
                    self._stats["hits"] += 1
                    # Add to memory cache
                    self._add_to_memory_cache(key, entry)
                return entry["data"]
            else:
                # Expired, remove from disk
                cache_path.unlink()
                with self._lock:
                    self._stats["misses"] += 1
                return None
                
        except (json.JSONDecodeError, OSError):
            with self._lock:
                self._stats["misses"] += 1
            return None
    
    def set(self, service: str, operation: str, params: Dict[str, Any], data: Dict[str, Any]):
        """Store response in cache."""
        key = self._generate_key(service, operation, params)
        entry = {
            "timestamp": time.time(),
            "service": service,
            "operation": operation,
            "params": params,
            "data": data
        }
        
        # Save to disk
        cache_path = self._get_cache_path(key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with gzip.open(cache_path, 'wt', encoding='utf-8') as f:
                json.dump(entry, f, default=str)
            
            # Update stats
            with self._lock:
                self._stats["total_size_bytes"] += cache_path.stat().st_size
                # Add to memory cache
                self._add_to_memory_cache(key, entry)
                
        except OSError:
            pass  # Silently fail on cache write errors
    
    def _add_to_memory_cache(self, key: str, entry: Dict[str, Any]):
        """Add entry to memory cache with LRU eviction."""
        if len(self._memory_cache) >= self._memory_cache_max_size:
            # Remove oldest entry (simple FIFO for now)
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
        self._memory_cache[key] = entry
    
    def _is_valid(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        timestamp = entry.get("timestamp", 0)
        age = time.time() - timestamp
        return age < self.ttl.total_seconds()
    
    def clear(self):
        """Clear all cached data."""
        with self._lock:
            self._memory_cache.clear()
            self._stats = {"hits": 0, "misses": 0, "total_size_bytes": 0}
        
        # Remove all cache files
        for cache_file in self.cache_dir.rglob("*.json.gz"):
            try:
                cache_file.unlink()
            except OSError:
                pass
        
        # Clean up empty directories
        for subdir in self.cache_dir.rglob("*"):
            if subdir.is_dir() and not any(subdir.iterdir()):
                try:
                    subdir.rmdir()
                except OSError:
                    pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate actual disk usage
            total_size = sum(f.stat().st_size for f in self.cache_dir.rglob("*.json.gz"))
            
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": f"{hit_rate:.1f}%",
                "total_size_kb": total_size // 1024,
                "memory_cache_size": len(self._memory_cache),
                "ttl_minutes": self.ttl.total_seconds() / 60
            }
    
    def invalidate_pattern(self, service: Optional[str] = None, operation: Optional[str] = None):
        """Invalidate cache entries matching pattern."""
        invalidated = 0
        
        # Clear memory cache entries matching pattern
        with self._lock:
            keys_to_remove = []
            for key, entry in self._memory_cache.items():
                if (service is None or entry.get("service") == service) and \
                   (operation is None or entry.get("operation") == operation):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._memory_cache[key]
                invalidated += 1
        
        # Clear disk cache entries matching pattern
        for cache_file in self.cache_dir.rglob("*.json.gz"):
            try:
                with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if (service is None or entry.get("service") == service) and \
                   (operation is None or entry.get("operation") == operation):
                    cache_file.unlink()
                    invalidated += 1
                    
            except (json.JSONDecodeError, OSError):
                continue
        
        return invalidated


# Global cache instance
_cache_instance = None

def get_scan_cache(cache_dir: Optional[Path] = None, ttl: Optional[timedelta] = None) -> ScanCache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ScanCache(
            cache_dir=cache_dir or Path("generated/.terraback/cache"),
            ttl=ttl or timedelta(hours=1)
        )
    return _cache_instance


class CachedBotoSession:
    """Wrapper around boto3 session that caches API responses."""
    
    def __init__(self, session, cache: ScanCache):
        self._session = session
        self._cache = cache
        self._clients = {}
    
    def client(self, service_name: str, **kwargs):
        """Get a cached client for the service."""
        key = f"{service_name}:{kwargs.get('region_name', self._session.region_name)}"
        if key not in self._clients:
            client = self._session.client(service_name, **kwargs)
            self._clients[key] = CachedBotoClient(client, service_name, self._cache)
        return self._clients[key]


class CachedBotoClient:
    """Wrapper around boto3 client that caches responses."""
    
    def __init__(self, client, service_name: str, cache: ScanCache):
        self._client = client
        self._service_name = service_name
        self._cache = cache
        
        # Operations that should always be cached
        self._cacheable_operations = {
            'describe_instances', 'describe_vpcs', 'describe_subnets',
            'describe_security_groups', 'describe_volumes', 'describe_snapshots',
            'list_roles', 'list_policies', 'list_buckets', 'list_functions',
            'describe_load_balancers', 'describe_target_groups', 'describe_listeners',
            'describe_db_instances', 'describe_clusters', 'describe_services',
            'list_queues', 'list_topics', 'list_secrets', 'describe_parameters'
        }
    
    def __getattr__(self, name):
        """Intercept client method calls for caching."""
        attr = getattr(self._client, name)
        
        if callable(attr) and name in self._cacheable_operations:
            def cached_method(**kwargs):
                # Try to get from cache
                cached_response = self._cache.get(self._service_name, name, kwargs)
                if cached_response is not None:
                    return cached_response
                
                # Call actual API
                response = attr(**kwargs)
                
                # Cache the response
                self._cache.set(self._service_name, name, kwargs, response)
                
                return response
            
            return cached_method
        
        return attr


def get_cached_boto_session(profile: Optional[str] = None, region: str = "us-east-1", 
                           cache: Optional[ScanCache] = None) -> CachedBotoSession:
    """Get a cached boto session."""
    import boto3
    
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)
    
    if cache is None:
        cache = get_scan_cache()
    
    return CachedBotoSession(session, cache)