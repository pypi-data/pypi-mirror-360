"""
Batch processing system for School of Prompt.
Handles large datasets efficiently with progress tracking and error recovery.
"""

import time
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional, Iterator, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue
import traceback


@dataclass
class BatchProgress:
    """Progress tracking for batch operations."""
    total_items: int
    completed_items: int
    failed_items: int
    current_batch: int
    total_batches: int
    start_time: float
    current_time: float
    estimated_completion: Optional[float] = None
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds."""
        return self.current_time - self.start_time
    
    @property
    def items_per_second(self) -> float:
        """Calculate processing rate."""
        if self.elapsed_time == 0:
            return 0
        return self.completed_items / self.elapsed_time
    
    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimate time to completion."""
        if self.items_per_second == 0:
            return None
        remaining_items = self.total_items - self.completed_items
        return remaining_items / self.items_per_second


@dataclass
class BatchResult:
    """Result of batch processing."""
    successful_results: List[Any]
    failed_items: List[Tuple[Any, Exception]]
    progress: BatchProgress
    total_time: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = len(self.successful_results) + len(self.failed_items)
        if total == 0:
            return 1.0
        return len(self.successful_results) / total


class BatchProcessor:
    """Efficient batch processor with error handling and progress tracking."""
    
    def __init__(
        self,
        chunk_size: int = 100,
        max_workers: int = 4,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout_per_item: float = 30.0,
        progress_callback: Optional[Callable[[BatchProgress], None]] = None
    ):
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout_per_item = timeout_per_item
        self.progress_callback = progress_callback
    
    def process_batch(
        self,
        items: List[Any],
        processor_func: Callable[[Any], Any],
        parallel: bool = True
    ) -> BatchResult:
        """Process a batch of items with error handling and progress tracking."""
        
        start_time = time.time()
        total_items = len(items)
        successful_results = []
        failed_items = []
        
        # Split into chunks
        chunks = self._create_chunks(items)
        total_batches = len(chunks)
        
        progress = BatchProgress(
            total_items=total_items,
            completed_items=0,
            failed_items=0,
            current_batch=0,
            total_batches=total_batches,
            start_time=start_time,
            current_time=start_time
        )
        
        if self.progress_callback:
            self.progress_callback(progress)
        
        # Process chunks
        for batch_idx, chunk in enumerate(chunks):
            progress.current_batch = batch_idx + 1
            progress.current_time = time.time()
            
            if parallel and self.max_workers > 1:
                chunk_results, chunk_failures = self._process_chunk_parallel(chunk, processor_func)
            else:
                chunk_results, chunk_failures = self._process_chunk_sequential(chunk, processor_func)
            
            successful_results.extend(chunk_results)
            failed_items.extend(chunk_failures)
            
            progress.completed_items = len(successful_results)
            progress.failed_items = len(failed_items)
            progress.current_time = time.time()
            
            if self.progress_callback:
                self.progress_callback(progress)
        
        total_time = time.time() - start_time
        
        return BatchResult(
            successful_results=successful_results,
            failed_items=failed_items,
            progress=progress,
            total_time=total_time
        )
    
    def process_streaming(
        self,
        items_iterator: Iterator[Any],
        processor_func: Callable[[Any], Any],
        parallel: bool = True
    ) -> Iterator[Tuple[Any, Optional[Exception]]]:
        """Process items in streaming fashion for very large datasets."""
        
        if parallel and self.max_workers > 1:
            yield from self._process_streaming_parallel(items_iterator, processor_func)
        else:
            yield from self._process_streaming_sequential(items_iterator, processor_func)
    
    def _create_chunks(self, items: List[Any]) -> List[List[Any]]:
        """Split items into chunks for batch processing."""
        chunks = []
        for i in range(0, len(items), self.chunk_size):
            chunks.append(items[i:i + self.chunk_size])
        return chunks
    
    def _process_chunk_sequential(
        self, 
        chunk: List[Any], 
        processor_func: Callable[[Any], Any]
    ) -> Tuple[List[Any], List[Tuple[Any, Exception]]]:
        """Process chunk sequentially."""
        results = []
        failures = []
        
        for item in chunk:
            try:
                result = self._process_item_with_retry(item, processor_func)
                results.append(result)
            except Exception as e:
                failures.append((item, e))
        
        return results, failures
    
    def _process_chunk_parallel(
        self, 
        chunk: List[Any], 
        processor_func: Callable[[Any], Any]
    ) -> Tuple[List[Any], List[Tuple[Any, Exception]]]:
        """Process chunk in parallel using thread pool."""
        results = []
        failures = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self._process_item_with_retry, item, processor_func): item
                for item in chunk
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_item, timeout=self.timeout_per_item * len(chunk)):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    failures.append((item, e))
        
        return results, failures
    
    def _process_streaming_sequential(
        self,
        items_iterator: Iterator[Any],
        processor_func: Callable[[Any], Any]
    ) -> Iterator[Tuple[Any, Optional[Exception]]]:
        """Process items sequentially in streaming fashion."""
        for item in items_iterator:
            try:
                result = self._process_item_with_retry(item, processor_func)
                yield (result, None)
            except Exception as e:
                yield (item, e)
    
    def _process_streaming_parallel(
        self,
        items_iterator: Iterator[Any],
        processor_func: Callable[[Any], Any]
    ) -> Iterator[Tuple[Any, Optional[Exception]]]:
        """Process items in parallel streaming fashion."""
        # Use a queue to buffer items and results
        item_queue = queue.Queue(maxsize=self.chunk_size * 2)
        result_queue = queue.Queue()
        
        def producer():
            """Producer thread to feed items."""
            try:
                for item in items_iterator:
                    item_queue.put(item)
                # Signal end of items
                for _ in range(self.max_workers):
                    item_queue.put(None)
            except Exception as e:
                result_queue.put((None, e))
        
        def consumer():
            """Consumer threads to process items."""
            while True:
                try:
                    item = item_queue.get(timeout=1.0)
                    if item is None:  # End signal
                        break
                    
                    try:
                        result = self._process_item_with_retry(item, processor_func)
                        result_queue.put((result, None))
                    except Exception as e:
                        result_queue.put((item, e))
                    
                    item_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    result_queue.put((None, e))
                    break
        
        # Start producer thread
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()
        
        # Start consumer threads
        consumer_threads = []
        for _ in range(self.max_workers):
            thread = threading.Thread(target=consumer)
            thread.start()
            consumer_threads.append(thread)
        
        # Yield results as they come
        active_consumers = self.max_workers
        while active_consumers > 0:
            try:
                result, error = result_queue.get(timeout=1.0)
                if result is None and error is None:
                    active_consumers -= 1
                    continue
                yield (result, error)
                result_queue.task_done()
            except queue.Empty:
                continue
        
        # Wait for all threads to complete
        producer_thread.join()
        for thread in consumer_threads:
            thread.join()
    
    def _process_item_with_retry(
        self, 
        item: Any, 
        processor_func: Callable[[Any], Any]
    ) -> Any:
        """Process single item with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return processor_func(item)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise last_exception
        
        # This should never be reached, but just in case
        raise last_exception or Exception("Unknown error during processing")


class ProgressTracker:
    """Progress tracker with console output and callbacks."""
    
    def __init__(
        self,
        show_console: bool = True,
        update_interval: float = 1.0,
        callbacks: Optional[List[Callable[[BatchProgress], None]]] = None
    ):
        self.show_console = show_console
        self.update_interval = update_interval
        self.callbacks = callbacks or []
        self.last_update = 0.0
    
    def update(self, progress: BatchProgress) -> None:
        """Update progress display."""
        current_time = time.time()
        
        # Rate limit updates
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        # Console output
        if self.show_console:
            self._print_progress(progress)
        
        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(progress)
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    def _print_progress(self, progress: BatchProgress) -> None:
        """Print progress to console."""
        eta_str = ""
        if progress.eta_seconds:
            eta_str = f" (ETA: {progress.eta_seconds:.0f}s)"
        
        print(
            f"\rBatch {progress.current_batch}/{progress.total_batches} | "
            f"{progress.completion_percentage:.1f}% | "
            f"{progress.completed_items}/{progress.total_items} items | "
            f"{progress.items_per_second:.1f} items/s"
            f"{eta_str}",
            end="",
            flush=True
        )
        
        # New line when complete
        if progress.completed_items + progress.failed_items >= progress.total_items:
            print()  # New line


def create_batch_processor(
    chunk_size: int = 100,
    max_workers: int = 4,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout_per_item: float = 30.0,
    show_progress: bool = True
) -> Tuple[BatchProcessor, Optional[ProgressTracker]]:
    """Create a batch processor with optional progress tracking."""
    
    progress_tracker = None
    progress_callback = None
    
    if show_progress:
        progress_tracker = ProgressTracker()
        progress_callback = progress_tracker.update
    
    processor = BatchProcessor(
        chunk_size=chunk_size,
        max_workers=max_workers,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout_per_item=timeout_per_item,
        progress_callback=progress_callback
    )
    
    return processor, progress_tracker


# Utility functions for common batch operations
def batch_api_calls(
    items: List[Any],
    api_func: Callable[[Any], Any],
    chunk_size: int = 50,
    max_workers: int = 3,
    delay_between_chunks: float = 0.1
) -> BatchResult:
    """Batch API calls with rate limiting."""
    
    def rate_limited_processor(item):
        result = api_func(item)
        time.sleep(delay_between_chunks / chunk_size)  # Distribute delay
        return result
    
    processor, _ = create_batch_processor(
        chunk_size=chunk_size,
        max_workers=max_workers,
        show_progress=True
    )
    
    return processor.process_batch(items, rate_limited_processor, parallel=True)


def batch_with_circuit_breaker(
    items: List[Any],
    processor_func: Callable[[Any], Any],
    failure_threshold: float = 0.5,
    chunk_size: int = 100
) -> BatchResult:
    """Batch processing with circuit breaker pattern."""
    
    failures_in_window = 0
    window_size = min(50, len(items) // 10)  # 10% of items or 50, whichever is smaller
    window_start = 0
    
    def circuit_breaker_processor(item):
        nonlocal failures_in_window, window_start
        
        # Check if we're in a new window
        current_index = items.index(item) if item in items else 0
        if current_index >= window_start + window_size:
            failures_in_window = 0
            window_start = current_index
        
        # Check failure rate
        if failures_in_window / window_size > failure_threshold:
            raise Exception(f"Circuit breaker triggered: failure rate {failures_in_window/window_size:.2%} > {failure_threshold:.2%}")
        
        try:
            return processor_func(item)
        except Exception as e:
            failures_in_window += 1
            raise e
    
    processor, _ = create_batch_processor(chunk_size=chunk_size, show_progress=True)
    return processor.process_batch(items, circuit_breaker_processor, parallel=False)