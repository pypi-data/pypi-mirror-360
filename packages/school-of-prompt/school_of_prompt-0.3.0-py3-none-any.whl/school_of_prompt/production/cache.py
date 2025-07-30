"""
Intelligent caching system for School of Prompt.
Reduces API calls and improves performance.
"""

import hashlib
import json
import time
import os
from typing import Any, Dict, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0


class IntelligentCache:
    """Intelligent caching system with expiry and size management."""
    
    def __init__(
        self,
        cache_dir: str = ".cache/school_of_prompt",
        default_expiry: str = "24h",
        max_size_mb: int = 500,
        enabled: bool = True
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_expiry = default_expiry
        self.max_size_mb = max_size_mb
        self.enabled = enabled
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._load_cache_index()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        cache_key = self._hash_key(key)
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if self._is_expired(entry):
                del self._memory_cache[cache_key]
                self._delete_cache_file(cache_key)
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            return entry.value
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                entry = CacheEntry(
                    key=data["key"],
                    value=data["value"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                    access_count=data.get("access_count", 0),
                    last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
                    size_bytes=data.get("size_bytes", 0)
                )
                
                if self._is_expired(entry):
                    cache_file.unlink()
                    return None
                
                # Update access info and move to memory cache
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self._memory_cache[cache_key] = entry
                
                return entry.value
                
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted cache file, delete it
                cache_file.unlink()
                return None
        
        return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expiry: Optional[str] = None
    ) -> None:
        """Set value in cache."""
        if not self.enabled:
            return
        
        cache_key = self._hash_key(key)
        expires_at = self._parse_expiry(expiry or self.default_expiry)
        
        # Calculate size
        try:
            size_bytes = len(json.dumps(value).encode('utf-8'))
        except (TypeError, OverflowError):
            size_bytes = 1024  # Estimate for non-serializable objects
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            access_count=1,
            last_accessed=datetime.now(),
            size_bytes=size_bytes
        )
        
        # Store in memory cache
        self._memory_cache[cache_key] = entry
        
        # Store on disk
        self._save_to_disk(cache_key, entry)
        
        # Cleanup if needed
        self._cleanup_if_needed()
    
    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        cache_key = self._hash_key(key)
        
        # Remove from memory
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        # Remove from disk
        self._delete_cache_file(cache_key)
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate cache entries matching a pattern."""
        keys_to_remove = []
        
        for cache_key, entry in self._memory_cache.items():
            if pattern in entry.key:
                keys_to_remove.append(cache_key)
        
        for cache_key in keys_to_remove:
            self.invalidate(entry.key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._memory_cache.clear()
        
        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._memory_cache)
        total_size = sum(entry.size_bytes for entry in self._memory_cache.values())
        
        # Count disk entries
        disk_files = list(self.cache_dir.glob("*.json"))
        disk_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            "enabled": self.enabled,
            "memory_entries": total_entries,
            "memory_size_mb": total_size / (1024 * 1024),
            "disk_entries": len(disk_files),
            "disk_size_mb": disk_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
            "default_expiry": self.default_expiry,
            "max_size_mb": self.max_size_mb
        }
    
    def _hash_key(self, key: str) -> str:
        """Create hash of cache key."""
        return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]
    
    def _parse_expiry(self, expiry_str: str) -> datetime:
        """Parse expiry string to datetime."""
        now = datetime.now()
        
        if expiry_str.endswith('h'):
            hours = int(expiry_str[:-1])
            return now + timedelta(hours=hours)
        elif expiry_str.endswith('d'):
            days = int(expiry_str[:-1])
            return now + timedelta(days=days)
        elif expiry_str.endswith('m'):
            minutes = int(expiry_str[:-1])
            return now + timedelta(minutes=minutes)
        else:
            # Default to hours
            try:
                hours = int(expiry_str)
                return now + timedelta(hours=hours)
            except ValueError:
                return now + timedelta(hours=24)  # Default 24h
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.expires_at is None:
            return False
        return datetime.now() > entry.expires_at
    
    def _save_to_disk(self, cache_key: str, entry: CacheEntry) -> None:
        """Save cache entry to disk."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                "key": entry.key,
                "value": entry.value,
                "created_at": entry.created_at.isoformat(),
                "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None,
                "size_bytes": entry.size_bytes
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except (TypeError, OverflowError):
            # Skip caching for non-serializable objects
            pass
    
    def _delete_cache_file(self, cache_key: str) -> None:
        """Delete cache file from disk."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            cache_file.unlink()
    
    def _load_cache_index(self) -> None:
        """Load cache index from disk."""
        # For now, we'll load cache on-demand
        # In a more sophisticated implementation, we might maintain an index file
        pass
    
    def _cleanup_if_needed(self) -> None:
        """Cleanup cache if size limits exceeded."""
        total_size = sum(entry.size_bytes for entry in self._memory_cache.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            # Remove least recently used entries
            sorted_entries = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1].last_accessed or x[1].created_at
            )
            
            # Remove 20% of entries
            num_to_remove = max(1, len(sorted_entries) // 5)
            
            for i in range(num_to_remove):
                cache_key, entry = sorted_entries[i]
                del self._memory_cache[cache_key]
                self._delete_cache_file(cache_key)


def cache_result(
    cache: IntelligentCache,
    expiry: Optional[str] = None,
    key_prefix: str = ""
) -> Callable:
    """Decorator for caching function results."""
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{_serialize_args(args, kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expiry)
            
            return result
        
        return wrapper
    return decorator


def _serialize_args(args: tuple, kwargs: dict) -> str:
    """Serialize function arguments for cache key."""
    try:
        # Create a deterministic string representation
        args_str = json.dumps(args, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        combined = f"args:{args_str}:kwargs:{kwargs_str}"
        
        # Hash if too long
        if len(combined) > 200:
            return hashlib.sha256(combined.encode()).hexdigest()[:32]
        
        return combined
    except (TypeError, OverflowError):
        # Fallback for non-serializable objects
        return hashlib.sha256(str((args, kwargs)).encode()).hexdigest()[:32]


# Global cache instance
_global_cache: Optional[IntelligentCache] = None


def get_global_cache() -> IntelligentCache:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = IntelligentCache()
    return _global_cache


def configure_global_cache(
    cache_dir: str = ".cache/school_of_prompt",
    default_expiry: str = "24h",
    max_size_mb: int = 500,
    enabled: bool = True
) -> None:
    """Configure the global cache."""
    global _global_cache
    _global_cache = IntelligentCache(
        cache_dir=cache_dir,
        default_expiry=default_expiry,
        max_size_mb=max_size_mb,
        enabled=enabled
    )