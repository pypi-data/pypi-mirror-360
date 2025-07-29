"""
Connection Pooling for Copper Alloy Brass v1.0
Manages database connections efficiently to improve performance.
"""

import sqlite3
import threading
import queue
import time
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ConnectionPool:
    """SQLite connection pool for better performance."""
    
    def __init__(self, 
                 db_path: Path,
                 min_connections: int = 2,
                 max_connections: int = 10,
                 timeout: float = 30.0):
        """
        Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            min_connections: Minimum connections to maintain
            max_connections: Maximum connections allowed
            timeout: Connection timeout in seconds
        """
        self.db_path = str(db_path)
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.timeout = timeout
        
        self._pool = queue.Queue(maxsize=max_connections)
        self._active_connections = 0
        self._lock = threading.Lock()
        self._stats = {
            'connections_created': 0,
            'connections_reused': 0,
            'connections_closed': 0,
            'wait_time_total': 0.0,
            'requests': 0
        }
        
        # Pre-create minimum connections
        self._initialize_pool()
        
    def _initialize_pool(self):
        """Pre-create minimum connections."""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            self._pool.put(conn)
            
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False  # Allow multi-threaded access
        )
        
        # Enable optimizations
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        conn.execute("PRAGMA cache_size=10000")  # Larger cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        
        # Enable row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        with self._lock:
            self._active_connections += 1
            self._stats['connections_created'] += 1
            
        logger.debug(f"Created new connection (total: {self._active_connections})")
        return conn
        
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        start_time = time.time()
        conn = None
        
        try:
            # Try to get from pool
            try:
                conn = self._pool.get_nowait()
                self._stats['connections_reused'] += 1
                logger.debug("Reused connection from pool")
            except queue.Empty:
                # Create new if under limit
                with self._lock:
                    if self._active_connections < self.max_connections:
                        conn = self._create_connection()
                    else:
                        # Wait for available connection
                        logger.debug("Waiting for available connection...")
                        conn = self._pool.get(timeout=self.timeout)
                        self._stats['connections_reused'] += 1
                        
            # Track statistics
            wait_time = time.time() - start_time
            self._stats['wait_time_total'] += wait_time
            self._stats['requests'] += 1
            
            # Ensure connection is alive
            try:
                conn.execute("SELECT 1")
            except sqlite3.Error:
                # Connection is dead, create new one
                logger.warning("Dead connection detected, creating new one")
                conn.close()
                conn = self._create_connection()
                
            yield conn
            
        finally:
            # Return to pool
            if conn:
                try:
                    self._pool.put_nowait(conn)
                except queue.Full:
                    # Pool is full, close connection
                    conn.close()
                    with self._lock:
                        self._active_connections -= 1
                        self._stats['connections_closed'] += 1
                    logger.debug("Closed excess connection")
                    
    def close_all(self):
        """Close all connections in the pool."""
        closed = 0
        
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
                closed += 1
            except queue.Empty:
                break
                
        with self._lock:
            self._active_connections = 0
            self._stats['connections_closed'] += closed
            
        logger.info(f"Closed {closed} connections")
        
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        avg_wait = (self._stats['wait_time_total'] / self._stats['requests'] 
                   if self._stats['requests'] > 0 else 0)
                   
        return {
            'pool_size': self._pool.qsize(),
            'active_connections': self._active_connections,
            'connections_created': self._stats['connections_created'],
            'connections_reused': self._stats['connections_reused'],
            'connections_closed': self._stats['connections_closed'],
            'total_requests': self._stats['requests'],
            'average_wait_time': avg_wait,
            'reuse_rate': (self._stats['connections_reused'] / self._stats['requests']
                          if self._stats['requests'] > 0 else 0)
        }


class PooledStorage:
    """Storage implementation using connection pooling."""
    
    def __init__(self, db_path: Path):
        self.pool = ConnectionPool(db_path)
        
    @contextmanager
    def transaction(self):
        """Execute operations in a transaction with pooled connection."""
        with self.pool.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
                
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query using pooled connection."""
        with self.pool.get_connection() as conn:
            return conn.execute(query, params).fetchall()
            
    def execute_write(self, query: str, params: tuple = ()):
        """Execute a write operation using pooled connection."""
        with self.transaction() as conn:
            return conn.execute(query, params)
            
    def close(self):
        """Close all pooled connections."""
        self.pool.close_all()
        
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self.pool.get_stats()