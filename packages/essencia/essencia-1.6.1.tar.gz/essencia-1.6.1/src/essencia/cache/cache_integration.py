"""
Cache Integration - Service decorators and integration utilities
Seamlessly integrates caching into existing services
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta

from essencia.cache import (
    get_cache, 
    MedicalDataCache, 
    FinancialDataCache, 
    UserSessionCache,
    CacheWarmer
)

logger = logging.getLogger(__name__)


class CacheIntegrationService:
    """
    Service for integrating caching into existing application services.
    
    Provides decorators, cache warming, and invalidation strategies for
    seamless performance optimization.
    """
    
    def __init__(self):
        self.cache = get_cache()
        self.medical_cache = MedicalDataCache()
        self.financial_cache = FinancialDataCache()
        self.user_cache = UserSessionCache()
        self.warmer = CacheWarmer()
    
    # Service Integration Decorators
    
    def cache_medical_data(self, ttl_seconds: int = 1800):
        """
        Decorator for caching medical service methods.
        
        Args:
            ttl_seconds: Time to live for cached data (default 30 minutes)
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and parameters
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.cache.get("medical_methods", cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.cache.set("medical_methods", cache_key, result, ttl_seconds)
                logger.debug(f"Cached result for {func.__name__}")
                return result
            return wrapper
        return decorator
    
    def cache_financial_data(self, ttl_seconds: int = 900):
        """
        Decorator for caching financial service methods.
        
        Args:
            ttl_seconds: Time to live for cached data (default 15 minutes)
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                cached_result = self.cache.get("financial_methods", cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                result = await func(*args, **kwargs)
                self.cache.set("financial_methods", cache_key, result, ttl_seconds)
                logger.debug(f"Cached result for {func.__name__}")
                return result
            return wrapper
        return decorator
    
    def cache_user_data(self, ttl_seconds: int = 3600):
        """
        Decorator for caching user service methods.
        
        Args:
            ttl_seconds: Time to live for cached data (default 1 hour)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                cached_result = self.cache.get("user_methods", cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                result = func(*args, **kwargs)
                self.cache.set("user_methods", cache_key, result, ttl_seconds)
                logger.debug(f"Cached result for {func.__name__}")
                return result
            return wrapper
        return decorator
    
    # Cache Warming Strategies
    
    async def warm_application_cache(self, 
                                   warm_patients: bool = True,
                                   warm_financial: bool = True,
                                   warm_users: bool = True,
                                   medical_service = None,
                                   financial_service = None) -> Dict[str, Any]:
        """
        Warm application cache with frequently accessed data.
        
        Args:
            warm_patients: Whether to warm patient-related cache
            warm_financial: Whether to warm financial cache
            warm_users: Whether to warm user cache
            medical_service: Optional medical service instance
            financial_service: Optional financial service instance
            
        Returns:
            Warming statistics and results
        """
        warming_stats = {
            'start_time': datetime.now(),
            'patients_warmed': 0,
            'financial_items_warmed': 0,
            'users_warmed': 0,
            'errors': []
        }
        
        try:
            if warm_patients and medical_service:
                # Get active patients from last 30 days
                active_patients = await self._get_active_patients(medical_service, days_back=30)
                if active_patients:
                    await self.warmer.warm_active_patients(active_patients, medical_service)
                    warming_stats['patients_warmed'] = len(active_patients)
                    logger.info(f"Warmed cache for {len(active_patients)} active patients")
            
            if warm_financial and financial_service:
                # Warm financial summaries
                await self.warmer.warm_financial_data(financial_service)
                warming_stats['financial_items_warmed'] = 3  # Current month, previous month, pending
                logger.info("Warmed financial cache")
            
            if warm_users:
                # Warm active user sessions
                active_users = await self._get_active_users()
                for user_key in active_users:
                    try:
                        # Pre-load user permissions and preferences
                        await self._warm_user_data(user_key)
                        warming_stats['users_warmed'] += 1
                    except Exception as e:
                        warming_stats['errors'].append(f"User {user_key}: {str(e)}")
                
                logger.info(f"Warmed cache for {warming_stats['users_warmed']} users")
            
        except Exception as e:
            logger.error(f"Cache warming error: {e}", exc_info=True)
            warming_stats['errors'].append(str(e))
        
        warming_stats['end_time'] = datetime.now()
        warming_stats['duration_seconds'] = (
            warming_stats['end_time'] - warming_stats['start_time']
        ).total_seconds()
        
        return warming_stats
    
    # Cache Invalidation Strategies
    
    def invalidate_patient_cache(self, patient_key: str) -> int:
        """
        Invalidate all cached data for a specific patient.
        
        Args:
            patient_key: Patient identifier
            
        Returns:
            Number of cache entries invalidated
        """
        total_invalidated = 0
        
        # Invalidate medical data cache
        total_invalidated += self.medical_cache.invalidate_patient_data(patient_key)
        
        # Invalidate method cache entries for this patient
        total_invalidated += self.cache.delete_pattern("medical_methods", f"*{patient_key}*")
        
        logger.info(f"Invalidated {total_invalidated} cache entries for patient {patient_key}")
        return total_invalidated
    
    def invalidate_financial_cache(self, 
                                 date_range: Optional[tuple] = None,
                                 patient_key: Optional[str] = None) -> int:
        """
        Invalidate financial cache for date range or specific patient.
        
        Args:
            date_range: Tuple of (start_date, end_date) to invalidate
            patient_key: Specific patient to invalidate
            
        Returns:
            Number of cache entries invalidated
        """
        total_invalidated = 0
        
        if date_range:
            total_invalidated += self.financial_cache.invalidate_financial_data(date_range)
        
        if patient_key:
            total_invalidated += self.cache.delete_pattern("financial_methods", f"*{patient_key}*")
        
        # Invalidate general financial method cache
        total_invalidated += self.cache.delete_pattern("financial_methods", "*revenue*")
        total_invalidated += self.cache.delete_pattern("financial_methods", "*expense*")
        
        logger.info(f"Invalidated {total_invalidated} financial cache entries")
        return total_invalidated
    
    def invalidate_user_cache(self, user_key: str) -> int:
        """
        Invalidate all cached data for a specific user.
        
        Args:
            user_key: User identifier
            
        Returns:
            Number of cache entries invalidated
        """
        total_invalidated = 0
        
        # Invalidate user session cache
        total_invalidated += self.user_cache.invalidate_user_session(user_key)
        
        # Invalidate method cache entries for this user
        total_invalidated += self.cache.delete_pattern("user_methods", f"*{user_key}*")
        
        logger.info(f"Invalidated {total_invalidated} cache entries for user {user_key}")
        return total_invalidated
    
    # Cache Monitoring and Statistics
    
    def get_cache_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive cache performance report.
        
        Returns:
            Detailed cache statistics and performance metrics
        """
        cache_stats = self.cache.get_stats()
        
        # Get namespace-specific statistics
        namespaces = ["medical", "financial", "sessions", "medical_methods", "financial_methods", "user_methods"]
        namespace_stats = {}
        
        for namespace in namespaces:
            # This is a simplified approach - in a real implementation,
            # you might want to track namespace-specific metrics
            namespace_stats[namespace] = {
                'estimated_entries': 'N/A',  # Would require namespace-aware cache implementation
                'last_access': 'N/A'
            }
        
        report = {
            'overall_stats': cache_stats,
            'namespace_breakdown': namespace_stats,
            'recommendations': self._generate_cache_recommendations(cache_stats),
            'report_time': datetime.now().isoformat()
        }
        
        return report
    
    def _generate_cache_recommendations(self, stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        hit_rate = stats.get('hit_rate_percent', 0)
        
        if hit_rate < 50:
            recommendations.append({
                'priority': 'high',
                'title': 'Low Cache Hit Rate',
                'description': f'Hit rate is only {hit_rate:.1f}%. Consider increasing TTL or reviewing cache strategy.',
                'action': 'Analyze access patterns and adjust TTL settings'
            })
        elif hit_rate < 70:
            recommendations.append({
                'priority': 'medium',
                'title': 'Moderate Cache Hit Rate',
                'description': f'Hit rate is {hit_rate:.1f}%. There is room for improvement.',
                'action': 'Implement pre-loading for frequently accessed data'
            })
        
        total_requests = stats.get('total_requests', 0)
        if total_requests < 100:
            recommendations.append({
                'priority': 'low',
                'title': 'Low Cache Usage',
                'description': f'Only {total_requests} cache requests. Cache may be underutilized.',
                'action': 'Expand cache usage to more operations'
            })
        
        if stats.get('backend') == 'memory':
            recommendations.append({
                'priority': 'medium',
                'title': 'Memory-Only Cache',
                'description': 'Using local memory cache only. Redis would provide better performance.',
                'action': 'Consider configuring Redis for distributed caching'
            })
        
        return recommendations
    
    # Helper Methods
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and parameters"""
        import hashlib
        
        # Create key components
        key_parts = [func_name]
        
        # Add positional args (skip 'self' if present)
        start_idx = 1 if args and hasattr(args[0], func_name) else 0
        key_parts.extend(str(arg) for arg in args[start_idx:])
        
        # Add keyword args
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        # Create hash of the key
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_active_patients(self, medical_service, days_back: int = 30) -> List[str]:
        """Get list of active patient keys"""
        try:
            # This would need to be implemented based on the medical service methods
            # For now, return a placeholder
            if hasattr(medical_service, 'get_active_patients'):
                return await medical_service.get_active_patients(days_back)
            return []  # Placeholder - implement based on actual service methods
            
        except Exception as e:
            logger.error(f"Error getting active patients: {e}")
            return []
    
    async def _get_active_users(self) -> List[str]:
        """Get list of active user keys"""
        try:
            # This would query recent login sessions or active users
            # For now, return a placeholder
            return []  # Placeholder - implement based on user activity
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def _warm_user_data(self, user_key: str):
        """Warm cache for specific user"""
        try:
            # Load and cache user permissions
            # This would integrate with your user service
            pass  # Placeholder - implement based on user service
            
        except Exception as e:
            logger.error(f"Error warming user data for {user_key}: {e}")
            raise


# Global cache integration instance
_cache_integration_instance = None

def get_cache_integration() -> CacheIntegrationService:
    """Get global cache integration instance"""
    global _cache_integration_instance
    if _cache_integration_instance is None:
        _cache_integration_instance = CacheIntegrationService()
    return _cache_integration_instance


# Convenient decorators for direct use
def medical_cached(ttl_seconds: int = 1800):
    """Convenient decorator for medical data caching"""
    return get_cache_integration().cache_medical_data(ttl_seconds)

def financial_cached(ttl_seconds: int = 900):
    """Convenient decorator for financial data caching"""
    return get_cache_integration().cache_financial_data(ttl_seconds)

def user_cached(ttl_seconds: int = 3600):
    """Convenient decorator for user data caching"""
    return get_cache_integration().cache_user_data(ttl_seconds)