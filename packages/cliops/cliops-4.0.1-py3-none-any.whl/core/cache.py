import json
import hashlib
from pathlib import Path
from typing import Any, Optional
from .config import Config

class Cache:
    def __init__(self):
        self.cache_dir = Config.get_app_data_dir() / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache = {}

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        # Check memory cache first
        if key in self._memory_cache:
            return self._memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self._memory_cache[key] = data
                    return data
            except (json.JSONDecodeError, IOError):
                cache_file.unlink(missing_ok=True)
        
        return None

    def set(self, key: str, value: Any):
        """Set cached value"""
        self._memory_cache[key] = value
        
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except (IOError, TypeError):
            pass  # Fail silently for caching

    def clear(self):
        """Clear all cache"""
        self._memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)