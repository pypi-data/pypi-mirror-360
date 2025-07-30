"""
Advanced error handling and recovery system for School of Prompt.
Provides graceful degradation, retry mechanisms, and fallback strategies.
"""

import time
import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import json
import random


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    RANDOM_JITTER = "random_jitter"


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_type: str
    error_message: str
    stack_trace: str
    timestamp: float
    context: Dict[str, Any]
    severity: ErrorSeverity
    retry_count: int = 0
    resolved: bool = False


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    jitter_range: float = 0.1
    retry_on: List[Type[Exception]] = field(default_factory=lambda: [Exception])
    do_not_retry_on: List[Type[Exception]] = field(default_factory=list)


@dataclass
class FallbackStrategy:
    """Fallback strategy configuration."""
    enabled: bool = True
    fallback_func: Optional[Callable] = None
    fallback_value: Any = None
    use_cache: bool = True
    log_fallback: bool = True


class ErrorHandler:
    """Advanced error handler with retry logic and fallback strategies."""
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        error_storage_path: Optional[str] = None
    ):
        self.logger = logger or self._create_default_logger()
        self.error_storage_path = error_storage_path
        self.error_history: List[ErrorRecord] = []
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, bool] = {}
    
    def with_retry(
        self,
        retry_config: Optional[RetryConfig] = None,
        fallback_strategy: Optional[FallbackStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Callable:
        """Decorator for adding retry logic and fallback strategies."""
        
        config = retry_config or RetryConfig()
        fallback = fallback_strategy or FallbackStrategy()
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_retry(
                    func, args, kwargs, config, fallback, context or {}
                )
            return wrapper
        return decorator
    
    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> ErrorRecord:
        """Handle and record an error."""
        
        error_record = ErrorRecord(
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            timestamp=time.time(),
            context=context,
            severity=severity
        )
        
        # Record error
        self.error_history.append(error_record)
        self._update_error_counts(error_record)
        
        # Log error
        self._log_error(error_record)
        
        # Store error if path provided
        if self.error_storage_path:
            self._store_error(error_record)
        
        # Check for circuit breaker
        self._check_circuit_breaker(error_record)
        
        return error_record
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error statistics."""
        total_errors = len(self.error_history)
        
        if total_errors == 0:
            return {"total_errors": 0, "error_rate": 0.0}
        
        # Error counts by type
        error_types = {}
        severity_counts = {}
        recent_errors = 0
        
        current_time = time.time()
        hour_ago = current_time - 3600
        
        for error in self.error_history:
            # Count by type
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
            # Count by severity
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            
            # Count recent errors
            if error.timestamp > hour_ago:
                recent_errors += 1
        
        return {
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_distribution": severity_counts,
            "recent_errors_1h": recent_errors,
            "error_rate_1h": recent_errors / 60 if recent_errors > 0 else 0.0,
            "circuit_breakers_active": list(self.circuit_breakers.keys())
        }
    
    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()
        self.circuit_breakers.clear()
    
    def _execute_with_retry(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        config: RetryConfig,
        fallback: FallbackStrategy,
        context: Dict[str, Any]
    ) -> Any:
        """Execute function with retry logic."""
        
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                # Check circuit breaker
                func_name = func.__name__
                if self.circuit_breakers.get(func_name, False):
                    raise Exception(f"Circuit breaker active for {func_name}")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker if it was active
                if func_name in self.circuit_breakers:
                    del self.circuit_breakers[func_name]
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry this exception
                if not self._should_retry(e, config):
                    break
                
                # Record error
                error_context = {**context, "attempt": attempt + 1, "function": func.__name__}
                self.handle_error(e, error_context, ErrorSeverity.MEDIUM)
                
                # If this is the last attempt, break
                if attempt >= config.max_retries:
                    break
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt, config)
                time.sleep(delay)
        
        # All retries failed, try fallback
        if fallback.enabled:
            return self._execute_fallback(func, args, kwargs, fallback, last_exception, context)
        
        # No fallback, raise the last exception
        if last_exception:
            raise last_exception
        else:
            raise Exception("Unknown error during execution")
    
    def _should_retry(self, exception: Exception, config: RetryConfig) -> bool:
        """Determine if exception should trigger a retry."""
        
        # Check do-not-retry list first
        for exc_type in config.do_not_retry_on:
            if isinstance(exception, exc_type):
                return False
        
        # Check retry list
        for exc_type in config.retry_on:
            if isinstance(exception, exc_type):
                return True
        
        return False
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay before next retry."""
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        
        elif config.strategy == RetryStrategy.RANDOM_JITTER:
            base_delay = config.base_delay * (config.backoff_multiplier ** attempt)
            jitter = random.uniform(-config.jitter_range, config.jitter_range) * base_delay
            delay = base_delay + jitter
        
        else:
            delay = config.base_delay
        
        # Cap at max delay
        return min(delay, config.max_delay)
    
    def _execute_fallback(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        fallback: FallbackStrategy,
        last_exception: Exception,
        context: Dict[str, Any]
    ) -> Any:
        """Execute fallback strategy."""
        
        if fallback.log_fallback:
            self.logger.warning(
                f"Executing fallback for {func.__name__} due to {type(last_exception).__name__}: {last_exception}"
            )
        
        # Try fallback function first
        if fallback.fallback_func:
            try:
                return fallback.fallback_func(*args, **kwargs)
            except Exception as e:
                fallback_context = {**context, "fallback_failed": True}
                self.handle_error(e, fallback_context, ErrorSeverity.HIGH)
        
        # Use fallback value
        if fallback.fallback_value is not None:
            return fallback.fallback_value
        
        # No fallback available, raise original exception
        raise last_exception
    
    def _update_error_counts(self, error_record: ErrorRecord) -> None:
        """Update error count statistics."""
        error_key = error_record.error_type
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _check_circuit_breaker(self, error_record: ErrorRecord) -> None:
        """Check if circuit breaker should be activated."""
        
        # Simple circuit breaker logic - activate after 5 errors of the same type in 5 minutes
        error_type = error_record.error_type
        current_time = time.time()
        recent_threshold = current_time - 300  # 5 minutes
        
        recent_errors = [
            e for e in self.error_history 
            if e.error_type == error_type and e.timestamp > recent_threshold
        ]
        
        if len(recent_errors) >= 5:
            context_func = error_record.context.get("function", "unknown")
            self.circuit_breakers[context_func] = True
            self.logger.error(f"Circuit breaker activated for {context_func} due to {error_type}")
    
    def _log_error(self, error_record: ErrorRecord) -> None:
        """Log error with appropriate level."""
        
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_record.severity, logging.WARNING)
        
        self.logger.log(
            log_level,
            f"{error_record.error_type}: {error_record.error_message} "
            f"(Context: {error_record.context})"
        )
    
    def _store_error(self, error_record: ErrorRecord) -> None:
        """Store error to file for later analysis."""
        try:
            error_data = {
                "error_type": error_record.error_type,
                "error_message": error_record.error_message,
                "timestamp": error_record.timestamp,
                "context": error_record.context,
                "severity": error_record.severity.value,
                "retry_count": error_record.retry_count
            }
            
            with open(self.error_storage_path, 'a') as f:
                f.write(json.dumps(error_data) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to store error record: {e}")
    
    def _create_default_logger(self) -> logging.Logger:
        """Create default logger."""
        logger = logging.getLogger("school_of_prompt.error_handler")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


# Predefined retry configurations
class StandardRetryConfigs:
    """Standard retry configurations for common scenarios."""
    
    @staticmethod
    def api_calls() -> RetryConfig:
        """Retry config for API calls."""
        return RetryConfig(
            max_retries=3,
            base_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            retry_on=[ConnectionError, TimeoutError],
            do_not_retry_on=[ValueError, TypeError]
        )
    
    @staticmethod
    def file_operations() -> RetryConfig:
        """Retry config for file operations."""
        return RetryConfig(
            max_retries=2,
            base_delay=0.5,
            strategy=RetryStrategy.FIXED_DELAY,
            retry_on=[OSError, IOError],
            do_not_retry_on=[FileNotFoundError, PermissionError]
        )
    
    @staticmethod
    def network_operations() -> RetryConfig:
        """Retry config for network operations."""
        return RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.RANDOM_JITTER,
            jitter_range=0.3,
            retry_on=[ConnectionError, TimeoutError],
            do_not_retry_on=[ValueError, TypeError, KeyError]
        )


# Standard fallback strategies
class StandardFallbacks:
    """Standard fallback strategies."""
    
    @staticmethod
    def cache_fallback(cache_key: str) -> FallbackStrategy:
        """Fallback to cached value."""
        def get_cached_value(*args, **kwargs):
            # This would integrate with the cache system
            from .cache import get_global_cache
            cache = get_global_cache()
            return cache.get(cache_key)
        
        return FallbackStrategy(
            enabled=True,
            fallback_func=get_cached_value,
            use_cache=True,
            log_fallback=True
        )
    
    @staticmethod
    def default_value_fallback(default_value: Any) -> FallbackStrategy:
        """Fallback to default value."""
        return FallbackStrategy(
            enabled=True,
            fallback_value=default_value,
            use_cache=False,
            log_fallback=True
        )
    
    @staticmethod
    def graceful_degradation_fallback(degraded_func: Callable) -> FallbackStrategy:
        """Fallback to degraded functionality."""
        return FallbackStrategy(
            enabled=True,
            fallback_func=degraded_func,
            use_cache=False,
            log_fallback=True
        )


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def configure_global_error_handler(
    logger: Optional[logging.Logger] = None,
    error_storage_path: Optional[str] = None
) -> None:
    """Configure the global error handler."""
    global _global_error_handler
    _global_error_handler = ErrorHandler(
        logger=logger,
        error_storage_path=error_storage_path
    )


# Convenience decorators
def with_api_retry(fallback_strategy: Optional[FallbackStrategy] = None):
    """Decorator for API calls with standard retry logic."""
    handler = get_global_error_handler()
    return handler.with_retry(
        StandardRetryConfigs.api_calls(),
        fallback_strategy
    )


def with_network_retry(fallback_strategy: Optional[FallbackStrategy] = None):
    """Decorator for network operations with standard retry logic."""
    handler = get_global_error_handler()
    return handler.with_retry(
        StandardRetryConfigs.network_operations(),
        fallback_strategy
    )


def with_graceful_degradation(fallback_value: Any = None):
    """Decorator for graceful degradation with fallback value."""
    handler = get_global_error_handler()
    fallback = StandardFallbacks.default_value_fallback(fallback_value)
    return handler.with_retry(
        StandardRetryConfigs.api_calls(),
        fallback
    )