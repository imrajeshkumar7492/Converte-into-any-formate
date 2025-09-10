import hashlib
import json
import os
import time
from typing import Any, Optional, Dict
from pathlib import Path
import tempfile

class FileCache:
    """Simple file-based cache for conversion results"""
    
    def __init__(self, cache_dir: str = None, max_size_mb: int = 1000, ttl_seconds: int = 3600):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "converter_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass
    
    def _generate_key(self, source_format: str, target_format: str, file_hash: str, **options) -> str:
        """Generate cache key from conversion parameters"""
        key_data = {
            'source_format': source_format,
            'target_format': target_format,
            'file_hash': file_hash,
            'options': sorted(options.items()) if options else []
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_file_hash(self, file_content: bytes) -> str:
        """Generate hash for file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        return self.cache_dir / f"{key}.cache"
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > self.ttl_seconds
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, metadata in self.metadata.items():
            if self._is_expired(metadata.get('timestamp', 0)):
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
    
    def _remove_entry(self, key: str):
        """Remove cache entry"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
        
        if key in self.metadata:
            del self.metadata[key]
    
    def _cleanup_size(self):
        """Remove oldest entries if cache is too large"""
        current_size = sum(
            self.cache_dir.glob("*.cache"),
            key=lambda p: p.stat().st_size if p.exists() else 0
        )
        
        if current_size > self.max_size_mb * 1024 * 1024:
            # Sort by timestamp and remove oldest
            sorted_entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1].get('timestamp', 0)
            )
            
            for key, _ in sorted_entries:
                self._remove_entry(key)
                current_size = sum(
                    self.cache_dir.glob("*.cache"),
                    key=lambda p: p.stat().st_size if p.exists() else 0
                )
                if current_size <= self.max_size_mb * 1024 * 1024:
                    break
    
    def get(self, source_format: str, target_format: str, file_content: bytes, **options) -> Optional[bytes]:
        """Get cached conversion result"""
        self._cleanup_expired()
        
        file_hash = self._get_file_hash(file_content)
        key = self._generate_key(source_format, target_format, file_hash, **options)
        
        if key not in self.metadata:
            return None
        
        metadata = self.metadata[key]
        if self._is_expired(metadata.get('timestamp', 0)):
            self._remove_entry(key)
            return None
        
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            self._remove_entry(key)
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return f.read()
        except IOError:
            self._remove_entry(key)
            return None
    
    def set(self, source_format: str, target_format: str, file_content: bytes, 
            converted_content: bytes, **options) -> bool:
        """Cache conversion result"""
        try:
            file_hash = self._get_file_hash(file_content)
            key = self._generate_key(source_format, target_format, file_hash, **options)
            
            cache_path = self._get_cache_path(key)
            
            # Write converted content to cache
            with open(cache_path, 'wb') as f:
                f.write(converted_content)
            
            # Update metadata
            self.metadata[key] = {
                'timestamp': time.time(),
                'source_format': source_format,
                'target_format': target_format,
                'file_hash': file_hash,
                'size': len(converted_content),
                'options': options
            }
            
            self._save_metadata()
            self._cleanup_size()
            
            return True
        except IOError:
            return False
    
    def clear(self):
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        self.metadata = {}
        self._save_metadata()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._cleanup_expired()
        
        total_size = sum(
            p.stat().st_size for p in self.cache_dir.glob("*.cache") if p.exists()
        )
        
        return {
            'entries': len(self.metadata),
            'total_size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.max_size_mb,
            'ttl_seconds': self.ttl_seconds
        }

# Global cache instance
cache = FileCache()