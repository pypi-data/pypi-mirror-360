"""
Production features for School of Prompt.
Caching, batch processing, and error handling for enterprise use.
"""

from .batch import (
    BatchProcessor,
    BatchProgress,
    BatchResult,
    ProgressTracker,
    batch_api_calls,
    batch_with_circuit_breaker,
    create_batch_processor,
)
from .cache import (
    IntelligentCache,
    cache_result,
    configure_global_cache,
    get_global_cache,
)
from .error_handling import (
    ErrorHandler,
    ErrorRecord,
    ErrorSeverity,
    FallbackStrategy,
    RetryConfig,
    RetryStrategy,
    StandardFallbacks,
    StandardRetryConfigs,
    configure_global_error_handler,
    get_global_error_handler,
    with_api_retry,
    with_graceful_degradation,
    with_network_retry,
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
    "with_graceful_degradation",
]
