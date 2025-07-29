"""
Performance Optimizations for Copper Alloy Brass v1.0
Implements various optimization strategies.
"""

import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


class ParallelProcessor:
    """Process multiple items in parallel for better performance."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel processor.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
    async def process_files(self, 
                          files: List[Path], 
                          process_fn: Callable[[Path], Dict[str, Any]],
                          batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Process multiple files in parallel.
        
        Args:
            files: List of files to process
            process_fn: Function to process each file
            batch_size: Number of files to process in each batch
            
        Returns:
            List of results
        """
        results = []
        
        # Process in batches
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            
            # Submit batch to executor
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(self._executor, process_fn, file)
                for file in batch
            ]
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*futures, return_exceptions=True)
            
            # Filter out exceptions
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)
                else:
                    logger.error(f"Error processing file: {result}")
                    
        return results
        
    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)


class BatchProcessor:
    """Process database operations in batches."""
    
    @staticmethod
    def batch_insert(storage, table: str, records: List[Dict[str, Any]], batch_size: int = 100):
        """
        Insert multiple records in batches.
        
        Args:
            storage: Storage instance with connection pool
            table: Table name
            records: List of records to insert
            batch_size: Records per batch
        """
        if not records:
            return
            
        # Get column names from first record
        columns = list(records[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            # Prepare batch data
            batch_data = []
            for record in batch:
                batch_data.append(tuple(record.get(col) for col in columns))
                
            # Execute batch insert
            with storage.transaction() as conn:
                conn.executemany(query, batch_data)
                
            logger.debug(f"Inserted batch of {len(batch)} records into {table}")


def performance_monitor(name: str = None):
    """
    Decorator to monitor function performance.
    
    Args:
        name: Optional name for the operation
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if elapsed > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {op_name} took {elapsed:.2f}s")
                else:
                    logger.debug(f"Operation: {op_name} completed in {elapsed:.2f}s")
                    
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Operation failed: {op_name} after {elapsed:.2f}s - {e}")
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if elapsed > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {op_name} took {elapsed:.2f}s")
                else:
                    logger.debug(f"Operation: {op_name} completed in {elapsed:.2f}s")
                    
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Operation failed: {op_name} after {elapsed:.2f}s - {e}")
                raise
                
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


class QueryOptimizer:
    """Optimize database queries."""
    
    @staticmethod
    def create_indexes(storage):
        """Create database indexes for better query performance."""
        indexes = [
            # Observations table
            "CREATE INDEX IF NOT EXISTS idx_obs_type ON observations(type)",
            "CREATE INDEX IF NOT EXISTS idx_obs_source ON observations(source_agent)",
            "CREATE INDEX IF NOT EXISTS idx_obs_created ON observations(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_obs_processed ON observations(processed)",
            "CREATE INDEX IF NOT EXISTS idx_obs_priority ON observations(priority DESC)",
            
            # File state table
            "CREATE INDEX IF NOT EXISTS idx_file_path ON file_state(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_analyzed ON file_state(last_analyzed)",
            
            # ML usage table
            "CREATE INDEX IF NOT EXISTS idx_ml_model ON ml_usage(model_id)",
            "CREATE INDEX IF NOT EXISTS idx_ml_timestamp ON ml_usage(timestamp)",
            
            # Patterns table
            "CREATE INDEX IF NOT EXISTS idx_pattern_type ON patterns(pattern_type)",
            "CREATE INDEX IF NOT EXISTS idx_pattern_file ON patterns(file_path)"
        ]
        
        with storage.transaction() as conn:
            for index_query in indexes:
                conn.execute(index_query)
                
        logger.info("Created database indexes for optimization")
        
    @staticmethod
    def analyze_tables(storage):
        """Run ANALYZE on tables to update query planner statistics."""
        tables = ['observations', 'file_state', 'ml_usage', 'patterns']
        
        with storage.transaction() as conn:
            for table in tables:
                conn.execute(f"ANALYZE {table}")
                
        logger.info("Updated database statistics for query optimization")


class MemoryOptimizer:
    """Optimize memory usage."""
    
    @staticmethod
    def stream_large_files(file_path: Path, chunk_size: int = 8192):
        """
        Stream large files instead of loading into memory.
        
        Args:
            file_path: Path to file
            chunk_size: Size of each chunk in bytes
            
        Yields:
            File chunks
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
    @staticmethod
    def process_in_chunks(items: List[Any], 
                         process_fn: Callable[[List[Any]], Any],
                         chunk_size: int = 100):
        """
        Process large lists in chunks to reduce memory usage.
        
        Args:
            items: List of items to process
            process_fn: Function to process each chunk
            chunk_size: Items per chunk
            
        Returns:
            Combined results
        """
        results = []
        
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            chunk_result = process_fn(chunk)
            
            if isinstance(chunk_result, list):
                results.extend(chunk_result)
            else:
                results.append(chunk_result)
                
        return results