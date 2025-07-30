"""
Production features for School of Prompt.
Caching, batch processing, and error handling for enterprise use.
"""

from .cache import (
    IntelligentCache,
    get_global_cache,
    configure_global_cache,
    cache_result
)

from .batch import (
    BatchProcessor,
    BatchResult,
    BatchProgress,
    ProgressTracker,
    create_batch_processor,
    batch_api_calls,
    batch_with_circuit_breaker
)

from .error_handling import (
    ErrorHandler,
    ErrorRecord,
    ErrorSeverity,
    RetryConfig,
    RetryStrategy,
    FallbackStrategy,
    StandardRetryConfigs,
    StandardFallbacks,
    get_global_error_handler,
    configure_global_error_handler,
    with_api_retry,
    with_network_retry,
    with_graceful_degradation
)

__all__ = [
    # Cache
    "IntelligentCache",
    "get_global_cache", 
    "configure_global_cache",
    "cache_result",
    
    # Batch processing
    "BatchProcessor",
    "BatchResult",
    "BatchProgress", 
    "ProgressTracker",
    "create_batch_processor",
    "batch_api_calls",
    "batch_with_circuit_breaker",
    
    # Error handling
    "ErrorHandler",
    "ErrorRecord",
    "ErrorSeverity",
    "RetryConfig",
    "RetryStrategy", 
    "FallbackStrategy",
    "StandardRetryConfigs",
    "StandardFallbacks",
    "get_global_error_handler",
    "configure_global_error_handler",
    "with_api_retry",
    "with_network_retry",
    "with_graceful_degradation"
]