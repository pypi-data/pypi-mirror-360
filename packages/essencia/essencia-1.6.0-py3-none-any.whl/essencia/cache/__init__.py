"""
Cache package - Intelligent caching system for performance optimization
"""

try:
    from .intelligent_cache import (
        IntelligentCache,
        get_cache,
        cached,
        async_cached,
        MedicalDataCache,
        FinancialDataCache,
        UserSessionCache,
        CacheWarmer
    )
    
    from .async_cache import (
        AsyncCacheManager,
        async_cache,
        async_cache_result,
        invalidate_model_cache
    )
    
    from .cache_integration import (
        CacheIntegrationService,
        get_cache_integration,
        medical_cached,
        financial_cached,
        user_cached
    )
    
    __all__ = [
        # Intelligent cache
        'IntelligentCache',
        'get_cache',
        'cached',
        'async_cached',
        'MedicalDataCache',
        'FinancialDataCache',
        'UserSessionCache',
        'CacheWarmer',
        # Async cache
        'AsyncCacheManager',
        'async_cache',
        'async_cache_result',
        'invalidate_model_cache',
        # Cache integration
        'CacheIntegrationService',
        'get_cache_integration',
        'medical_cached',
        'financial_cached',
        'user_cached'
    ]
except ImportError as e:
    # Fallback for missing dependencies
    print(f"Cache import warning: {e}")
    __all__ = []