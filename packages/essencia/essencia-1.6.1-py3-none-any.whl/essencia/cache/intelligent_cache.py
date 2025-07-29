"""
Intelligent Cache Layer - Redis-based caching system with TTL and invalidation
Provides performance optimization for frequently accessed data
"""

import logging
import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class IntelligentCache:
    """
    Intelligent caching system with Redis backend and fallback to in-memory.
    
    Features:
    - Automatic TTL management
    - Smart invalidation patterns
    - Fallback to memory cache when Redis unavailable
    - Performance monitoring
    - Cache warming strategies
    """
    
    def __init__(self, redis_config: Optional[Dict] = None):
        self.redis_client = None
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0
        }
        
        # Initialize Redis connection
        if REDIS_AVAILABLE and redis_config is not None:
            try:
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    password=redis_config.get('password'),
                    decode_responses=False  # Keep binary for pickle
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not available, using memory cache")
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace"""
        return f"essencia:{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        return pickle.dumps({
            'data': value,
            'timestamp': datetime.now().isoformat(),
            'type': type(value).__name__
        })
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            cached_data = pickle.loads(data)
            return cached_data['data']
        except Exception as e:
            logger.error(f"Cache deserialization error: {e}")
            return None
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_key(namespace, key)
        
        try:
            if self.redis_client:
                # Try Redis first
                data = self.redis_client.get(cache_key)
                if data:
                    self.cache_stats['hits'] += 1
                    return self._deserialize_value(data)
            else:
                # Use memory cache
                if cache_key in self.memory_cache:
                    cached_item = self.memory_cache[cache_key]
                    # Check TTL
                    if cached_item['expires'] > datetime.now():
                        self.cache_stats['hits'] += 1
                        return cached_item['value']
                    else:
                        # Expired, remove from cache
                        del self.memory_cache[cache_key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, namespace: str, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache with TTL"""
        cache_key = self._generate_key(namespace, key)
        
        try:
            if self.redis_client:
                # Use Redis with TTL
                serialized_value = self._serialize_value(value)
                result = self.redis_client.setex(cache_key, ttl_seconds, serialized_value)
                if result:
                    self.cache_stats['sets'] += 1
                    return True
            else:
                # Use memory cache with TTL
                self.memory_cache[cache_key] = {
                    'value': value,
                    'expires': datetime.now() + timedelta(seconds=ttl_seconds)
                }
                self.cache_stats['sets'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            
        return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """Delete specific key from cache"""
        cache_key = self._generate_key(namespace, key)
        
        try:
            if self.redis_client:
                result = self.redis_client.delete(cache_key)
                if result > 0:
                    self.cache_stats['invalidations'] += 1
                    return True
            else:
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    self.cache_stats['invalidations'] += 1
                    return True
                    
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            
        return False
    
    def delete_pattern(self, namespace: str, pattern: str) -> int:
        """Delete all keys matching pattern"""
        cache_pattern = self._generate_key(namespace, pattern)
        deleted_count = 0
        
        try:
            if self.redis_client:
                keys = self.redis_client.keys(cache_pattern)
                if keys:
                    deleted_count = self.redis_client.delete(*keys)
                    self.cache_stats['invalidations'] += deleted_count
            else:
                # Memory cache pattern matching
                keys_to_delete = []
                for key in self.memory_cache.keys():
                    if key.startswith(self._generate_key(namespace, '')) and pattern in key:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    deleted_count += 1
                
                self.cache_stats['invalidations'] += deleted_count
                
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            
        return deleted_count
    
    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in namespace"""
        return self.delete_pattern(namespace, '*')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            **self.cache_stats,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests,
            'backend': 'redis' if self.redis_client else 'memory',
            'memory_cache_size': len(self.memory_cache)
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats['redis_memory_usage'] = info.get('used_memory_human', 'N/A')
                stats['redis_connected_clients'] = info.get('connected_clients', 0)
            except:
                pass
                
        return stats


# Global cache instance
_cache_instance = None

def get_cache(redis_config: Optional[Dict] = None) -> IntelligentCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = IntelligentCache(redis_config)
    return _cache_instance


# Cache decorators for easy use
def cached(namespace: str, ttl_seconds: int = 3600, key_generator: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        namespace: Cache namespace
        ttl_seconds: Time to live in seconds
        key_generator: Function to generate cache key from args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
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
            result = cache.get(namespace, cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(namespace, cache_key, result, ttl_seconds)
            return result
        return wrapper
    return decorator


def async_cached(namespace: str, ttl_seconds: int = 3600, key_generator: Optional[Callable] = None):
    """
    Decorator to cache async function results
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            
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
            result = cache.get(namespace, cache_key)
            if result is not None:
                return result
            
            # Execute async function and cache result
            result = await func(*args, **kwargs)
            cache.set(namespace, cache_key, result, ttl_seconds)
            return result
        return wrapper
    return decorator


# Specific cache strategies for different data types
class MedicalDataCache:
    """Specialized cache for medical data"""
    
    def __init__(self):
        self.cache = get_cache()
        self.namespace = "medical"
    
    def get_patient_summary(self, patient_key: str) -> Optional[Dict]:
        """Get cached patient summary"""
        return self.cache.get(self.namespace, f"patient_summary:{patient_key}")
    
    def set_patient_summary(self, patient_key: str, summary: Dict) -> bool:
        """Cache patient summary for 30 minutes"""
        return self.cache.set(self.namespace, f"patient_summary:{patient_key}", summary, 1800)
    
    def invalidate_patient_data(self, patient_key: str) -> int:
        """Invalidate all cached data for a patient"""
        return self.cache.delete_pattern(self.namespace, f"*{patient_key}*")
    
    def get_visit_history(self, patient_key: str, doctor_key: str = None) -> Optional[List]:
        """Get cached visit history"""
        key = f"visit_history:{patient_key}:{doctor_key or 'all'}"
        return self.cache.get(self.namespace, key)
    
    def set_visit_history(self, patient_key: str, history: List, doctor_key: str = None) -> bool:
        """Cache visit history for 15 minutes"""
        key = f"visit_history:{patient_key}:{doctor_key or 'all'}"
        return self.cache.set(self.namespace, key, history, 900)


class FinancialDataCache:
    """Specialized cache for financial data"""
    
    def __init__(self):
        self.cache = get_cache()
        self.namespace = "financial"
    
    def get_pending_revenues(self, limit: int = 50) -> Optional[List]:
        """Get cached pending revenues"""
        return self.cache.get(self.namespace, f"pending_revenues:{limit}")
    
    def set_pending_revenues(self, revenues: List, limit: int = 50) -> bool:
        """Cache pending revenues for 10 minutes"""
        return self.cache.set(self.namespace, f"pending_revenues:{limit}", revenues, 600)
    
    def get_monthly_summary(self, year: int, month: int) -> Optional[Dict]:
        """Get cached monthly financial summary"""
        return self.cache.get(self.namespace, f"monthly_summary:{year}:{month}")
    
    def set_monthly_summary(self, year: int, month: int, summary: Dict) -> bool:
        """Cache monthly summary for 1 hour"""
        return self.cache.set(self.namespace, f"monthly_summary:{year}:{month}", summary, 3600)
    
    def invalidate_financial_data(self, date_range: Optional[tuple] = None) -> int:
        """Invalidate financial data for date range or all"""
        if date_range:
            start_date, end_date = date_range
            # Invalidate specific months
            deleted = 0
            current_date = start_date.replace(day=1)
            while current_date <= end_date.replace(day=1):
                key = f"monthly_summary:{current_date.year}:{current_date.month}"
                self.cache.delete(self.namespace, key)
                deleted += 1
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            # Also invalidate pending revenues
            self.cache.delete_pattern(self.namespace, "pending_revenues:*")
            return deleted
        else:
            return self.cache.clear_namespace(self.namespace)


class UserSessionCache:
    """Specialized cache for user session data"""
    
    def __init__(self):
        self.cache = get_cache()
        self.namespace = "sessions"
    
    def get_user_permissions(self, user_key: str) -> Optional[Dict]:
        """Get cached user permissions"""
        return self.cache.get(self.namespace, f"permissions:{user_key}")
    
    def set_user_permissions(self, user_key: str, permissions: Dict) -> bool:
        """Cache user permissions for 1 hour"""
        return self.cache.set(self.namespace, f"permissions:{user_key}", permissions, 3600)
    
    def get_user_preferences(self, user_key: str) -> Optional[Dict]:
        """Get cached user preferences"""
        return self.cache.get(self.namespace, f"preferences:{user_key}")
    
    def set_user_preferences(self, user_key: str, preferences: Dict) -> bool:
        """Cache user preferences for 8 hours"""
        return self.cache.set(self.namespace, f"preferences:{user_key}", preferences, 28800)
    
    def invalidate_user_session(self, user_key: str) -> int:
        """Invalidate all cached session data for user"""
        return self.cache.delete_pattern(self.namespace, f"*{user_key}*")


# Cache warming utilities
class CacheWarmer:
    """Utilities for warming up cache with frequently accessed data"""
    
    def __init__(self):
        self.medical_cache = MedicalDataCache()
        self.financial_cache = FinancialDataCache()
        self.user_cache = UserSessionCache()
    
    async def warm_active_patients(self, patient_keys: List[str], medical_service=None):
        """Pre-load data for active patients"""
        if not medical_service:
            logger.warning("No medical service provided for cache warming")
            return
        
        for patient_key in patient_keys:
            try:
                # Load and cache patient summary
                if hasattr(medical_service, 'get_comprehensive_medical_summary_optimized'):
                    summary = await medical_service.get_comprehensive_medical_summary_optimized(
                        patient_key, include_timeline=True, days_back=30
                    )
                    self.medical_cache.set_patient_summary(patient_key, summary)
                
                # Load and cache recent visit history
                if hasattr(medical_service, 'get_patient_visit_history_optimized'):
                    history = await medical_service.get_patient_visit_history_optimized(
                        patient_key, limit=20
                    )
                    self.medical_cache.set_visit_history(patient_key, history)
                
                logger.info(f"Warmed cache for patient {patient_key}")
                
            except Exception as e:
                logger.error(f"Cache warming failed for patient {patient_key}: {e}")
    
    async def warm_financial_data(self, financial_service=None):
        """Pre-load financial summaries for current and previous months"""
        if not financial_service:
            logger.warning("No financial service provided for cache warming")
            return
        
        try:
            # Load pending revenues
            if hasattr(financial_service, 'get_pending_revenues_optimized'):
                pending_revenues = await financial_service.get_pending_revenues_optimized(limit=100)
                self.financial_cache.set_pending_revenues(pending_revenues, 100)
            
            # Load current month summary
            now = datetime.now()
            if hasattr(financial_service, 'get_monthly_financial_summary_optimized'):
                current_summary = await financial_service.get_monthly_financial_summary_optimized(
                    now.year, now.month
                )
                self.financial_cache.set_monthly_summary(now.year, now.month, current_summary)
            
            logger.info("Warmed financial cache")
            
        except Exception as e:
            logger.error(f"Financial cache warming failed: {e}")
    
    def get_warming_stats(self) -> Dict[str, Any]:
        """Get cache warming statistics"""
        return self.medical_cache.cache.get_stats()