"""
DCP Snapshot Manager for Copper Alloy Brass Historical Analysis
Handles capture, storage, retrieval, and management of DCP snapshots.
"""

import asyncio
import json
import sqlite3
import hashlib
import gzip
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SnapshotMetadata:
    """Metadata for DCP snapshots"""
    id: str
    project_id: str
    cycle_id: Optional[int]
    created_at: datetime
    size_bytes: int
    compressed_size_bytes: int
    observation_count: int
    recommendation_count: int
    content_hash: str
    version: str
    tags: List[str]


@dataclass
class SnapshotQuery:
    """Query parameters for snapshot retrieval"""
    project_id: Optional[str] = None
    limit: Optional[int] = None
    timeframe_days: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    min_cycle_id: Optional[int] = None
    max_cycle_id: Optional[int] = None


class DCPSnapshotManager:
    """
    Manages DCP snapshot capture, storage, and retrieval for historical analysis.
    Provides efficient storage with compression and metadata indexing.
    """
    
    def __init__(self, db_path: str = "brass_snapshots.db", 
                 storage_path: str = "snapshots/"):
        self.db_path = db_path
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._init_database()
        
        # Configuration
        self.config = {
            'compression_enabled': True,
            'max_snapshots_per_project': 1000,
            'default_retention_days': 90,
            'auto_cleanup_enabled': True,
            'content_hash_algorithm': 'sha256'
        }
    
    def _init_database(self):
        """Initialize snapshot database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dcp_snapshots (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        cycle_id INTEGER,
                        created_at TIMESTAMP NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        compressed_size_bytes INTEGER NOT NULL,
                        observation_count INTEGER NOT NULL,
                        recommendation_count INTEGER NOT NULL,
                        content_hash TEXT NOT NULL,
                        version TEXT NOT NULL,
                        tags TEXT,  -- JSON array
                        file_path TEXT NOT NULL,
                        metadata TEXT  -- JSON metadata
                    )
                """)
                
                # Create indexes for performance
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_snapshots_project_time 
                    ON dcp_snapshots(project_id, created_at DESC)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_snapshots_cycle 
                    ON dcp_snapshots(project_id, cycle_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_snapshots_hash 
                    ON dcp_snapshots(content_hash)
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize snapshot database: {e}")
            raise
    
    async def capture_snapshot(self, dcp_data: Dict, project_id: str, 
                             cycle_id: Optional[int] = None,
                             tags: Optional[List[str]] = None) -> str:
        """
        Capture a DCP snapshot with metadata.
        
        Args:
            dcp_data: Complete DCP data structure
            project_id: Project identifier
            cycle_id: Optional cycle identifier
            tags: Optional tags for categorization
            
        Returns:
            Snapshot ID
        """
        try:
            snapshot_id = str(uuid.uuid4())
            created_at = datetime.utcnow()
            
            # Serialize DCP data
            dcp_json = json.dumps(dcp_data, indent=2, default=str)
            size_bytes = len(dcp_json.encode('utf-8'))
            
            # Calculate content hash
            content_hash = hashlib.sha256(dcp_json.encode('utf-8')).hexdigest()
            
            # Check for duplicate content
            existing_snapshot = await self._find_by_hash(content_hash, project_id)
            if existing_snapshot:
                self.logger.info(f"Duplicate content detected, returning existing snapshot: {existing_snapshot}")
                return existing_snapshot
            
            # Extract metadata
            observations = dcp_data.get('current_observations', [])
            recommendations = dcp_data.get('strategic_recommendations', [])
            version = dcp_data.get('meta', {}).get('version', 'unknown')
            
            metadata = SnapshotMetadata(
                id=snapshot_id,
                project_id=project_id,
                cycle_id=cycle_id,
                created_at=created_at,
                size_bytes=size_bytes,
                compressed_size_bytes=0,  # Will be updated after compression
                observation_count=len(observations),
                recommendation_count=len(recommendations),
                content_hash=content_hash,
                version=version,
                tags=tags or []
            )
            
            # Store snapshot data
            file_path = await self._store_snapshot_data(snapshot_id, dcp_json)
            
            # Update compressed size in metadata
            if self.config['compression_enabled']:
                metadata.compressed_size_bytes = file_path.stat().st_size
            else:
                metadata.compressed_size_bytes = size_bytes
            
            # Save to database
            await self._save_snapshot_metadata(metadata, str(file_path))
            
            self.logger.info(f"Snapshot captured: {snapshot_id} ({size_bytes} bytes)")
            
            # Auto-cleanup if enabled
            if self.config['auto_cleanup_enabled']:
                await self._auto_cleanup_old_snapshots(project_id)
            
            return snapshot_id
            
        except Exception as e:
            self.logger.error(f"Failed to capture snapshot: {e}")
            raise
    
    async def get_snapshot(self, snapshot_id: str) -> Optional[Dict]:
        """
        Retrieve a specific snapshot by ID.
        
        Args:
            snapshot_id: Snapshot identifier
            
        Returns:
            Snapshot data with metadata, or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM dcp_snapshots WHERE id = ?
                """, (snapshot_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Load snapshot data
                file_path = Path(row['file_path'])
                snapshot_data = await self._load_snapshot_data(file_path)
                
                return {
                    'id': row['id'],
                    'project_id': row['project_id'],
                    'cycle_id': row['cycle_id'],
                    'created_at': row['created_at'],
                    'size_bytes': row['size_bytes'],
                    'observation_count': row['observation_count'],
                    'recommendation_count': row['recommendation_count'],
                    'content_hash': row['content_hash'],
                    'version': row['version'],
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'snapshot_data': snapshot_data
                }
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve snapshot {snapshot_id}: {e}")
            return None
    
    async def get_snapshots(self, project_id: Optional[str] = None,
                          limit: Optional[int] = None,
                          timeframe_days: Optional[int] = None,
                          query: Optional[SnapshotQuery] = None) -> List[Dict]:
        """
        Retrieve snapshots with flexible filtering.
        
        Args:
            project_id: Filter by project ID
            limit: Maximum number of snapshots to return
            timeframe_days: Only return snapshots from last N days
            query: Advanced query parameters
            
        Returns:
            List of snapshot metadata (without full data)
        """
        try:
            # Build query from parameters
            if query is None:
                query = SnapshotQuery(
                    project_id=project_id,
                    limit=limit,
                    timeframe_days=timeframe_days
                )
            
            # Build SQL query
            sql_parts = ["SELECT * FROM dcp_snapshots WHERE 1=1"]
            params = []
            
            if query.project_id:
                sql_parts.append("AND project_id = ?")
                params.append(query.project_id)
            
            if query.timeframe_days:
                cutoff_date = datetime.utcnow() - timedelta(days=query.timeframe_days)
                sql_parts.append("AND created_at >= ?")
                params.append(cutoff_date.isoformat())
            
            if query.start_date:
                sql_parts.append("AND created_at >= ?")
                params.append(query.start_date.isoformat())
            
            if query.end_date:
                sql_parts.append("AND created_at <= ?")
                params.append(query.end_date.isoformat())
            
            if query.min_cycle_id is not None:
                sql_parts.append("AND cycle_id >= ?")
                params.append(query.min_cycle_id)
            
            if query.max_cycle_id is not None:
                sql_parts.append("AND cycle_id <= ?")
                params.append(query.max_cycle_id)
            
            # Add ordering and limit
            sql_parts.append("ORDER BY created_at DESC")
            
            if query.limit:
                sql_parts.append("LIMIT ?")
                params.append(query.limit)
            
            sql = " ".join(sql_parts)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                
                snapshots = []
                for row in cursor.fetchall():
                    snapshots.append({
                        'id': row['id'],
                        'project_id': row['project_id'],
                        'cycle_id': row['cycle_id'],
                        'created_at': row['created_at'],
                        'size_bytes': row['size_bytes'],
                        'compressed_size_bytes': row['compressed_size_bytes'],
                        'observation_count': row['observation_count'],
                        'recommendation_count': row['recommendation_count'],
                        'content_hash': row['content_hash'],
                        'version': row['version'],
                        'tags': json.loads(row['tags']) if row['tags'] else []
                    })
                
                # Filter by tags if specified
                if query.tags:
                    snapshots = [
                        s for s in snapshots 
                        if any(tag in s['tags'] for tag in query.tags)
                    ]
                
                self.logger.info(f"Retrieved {len(snapshots)} snapshots")
                return snapshots
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve snapshots: {e}")
            return []
    
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """
        Delete a specific snapshot.
        
        Args:
            snapshot_id: Snapshot to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get file path first
                cursor = conn.execute("""
                    SELECT file_path FROM dcp_snapshots WHERE id = ?
                """, (snapshot_id,))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                file_path = Path(row[0])
                
                # Delete from database
                conn.execute("DELETE FROM dcp_snapshots WHERE id = ?", (snapshot_id,))
                conn.commit()
                
                # Delete file
                if file_path.exists():
                    file_path.unlink()
                
                self.logger.info(f"Deleted snapshot: {snapshot_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False
    
    async def cleanup_old_snapshots(self, project_id: Optional[str] = None,
                                  retention_days: Optional[int] = None) -> int:
        """
        Clean up old snapshots based on retention policy.
        
        Args:
            project_id: Only clean up specific project (None for all)
            retention_days: Retention period in days
            
        Returns:
            Number of snapshots deleted
        """
        try:
            retention_days = retention_days or self.config['default_retention_days']
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Find old snapshots
            sql = "SELECT id, file_path FROM dcp_snapshots WHERE created_at < ?"
            params = [cutoff_date.isoformat()]
            
            if project_id:
                sql += " AND project_id = ?"
                params.append(project_id)
            
            deleted_count = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, params)
                old_snapshots = cursor.fetchall()
                
                for snapshot_id, file_path in old_snapshots:
                    # Delete file
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception as e:
                        self.logger.warning(f"Failed to delete file {file_path}: {e}")
                    
                    # Delete from database
                    conn.execute("DELETE FROM dcp_snapshots WHERE id = ?", (snapshot_id,))
                    deleted_count += 1
                
                conn.commit()
            
            self.logger.info(f"Cleaned up {deleted_count} old snapshots")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old snapshots: {e}")
            return 0
    
    async def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for a project's snapshots.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Statistics dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic counts
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_snapshots,
                        MIN(created_at) as oldest_snapshot,
                        MAX(created_at) as newest_snapshot,
                        AVG(size_bytes) as avg_size_bytes,
                        SUM(size_bytes) as total_size_bytes,
                        AVG(observation_count) as avg_observations,
                        AVG(recommendation_count) as avg_recommendations
                    FROM dcp_snapshots 
                    WHERE project_id = ?
                """, (project_id,))
                
                row = cursor.fetchone()
                
                # Recent activity (last 7 days)
                cursor = conn.execute("""
                    SELECT COUNT(*) as recent_snapshots
                    FROM dcp_snapshots 
                    WHERE project_id = ? AND created_at >= ?
                """, (project_id, (datetime.utcnow() - timedelta(days=7)).isoformat()))
                
                recent_row = cursor.fetchone()
                
                return {
                    'total_snapshots': row[0],
                    'oldest_snapshot': row[1],
                    'newest_snapshot': row[2],
                    'avg_size_bytes': row[3] or 0,
                    'total_size_bytes': row[4] or 0,
                    'avg_observations': row[5] or 0,
                    'avg_recommendations': row[6] or 0,
                    'recent_snapshots_7d': recent_row[0],
                    'storage_efficiency': self._calculate_storage_efficiency(project_id)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get project statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _store_snapshot_data(self, snapshot_id: str, dcp_json: str) -> Path:
        """Store snapshot data to file with optional compression"""
        file_path = self.storage_path / f"{snapshot_id}.json"
        
        if self.config['compression_enabled']:
            file_path = file_path.with_suffix('.json.gz')
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                f.write(dcp_json)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(dcp_json)
        
        return file_path
    
    async def _load_snapshot_data(self, file_path: Path) -> Dict:
        """Load snapshot data from file with optional decompression"""
        if file_path.suffix == '.gz':
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    async def _save_snapshot_metadata(self, metadata: SnapshotMetadata, file_path: str):
        """Save snapshot metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO dcp_snapshots (
                    id, project_id, cycle_id, created_at, size_bytes,
                    compressed_size_bytes, observation_count, recommendation_count,
                    content_hash, version, tags, file_path, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.id,
                metadata.project_id,
                metadata.cycle_id,
                metadata.created_at.isoformat(),
                metadata.size_bytes,
                metadata.compressed_size_bytes,
                metadata.observation_count,
                metadata.recommendation_count,
                metadata.content_hash,
                metadata.version,
                json.dumps(metadata.tags),
                file_path,
                json.dumps(asdict(metadata), default=str)
            ))
            conn.commit()
    
    async def _find_by_hash(self, content_hash: str, project_id: str) -> Optional[str]:
        """Find existing snapshot with same content hash"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id FROM dcp_snapshots 
                WHERE content_hash = ? AND project_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (content_hash, project_id))
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    async def _auto_cleanup_old_snapshots(self, project_id: str):
        """Automatically clean up if too many snapshots exist"""
        max_snapshots = self.config['max_snapshots_per_project']
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM dcp_snapshots WHERE project_id = ?
            """, (project_id,))
            
            count = cursor.fetchone()[0]
            
            if count > max_snapshots:
                # Delete oldest snapshots
                cursor = conn.execute("""
                    SELECT id, file_path FROM dcp_snapshots 
                    WHERE project_id = ?
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (project_id, count - max_snapshots))
                
                for snapshot_id, file_path in cursor.fetchall():
                    await self.delete_snapshot(snapshot_id)
    
    def _calculate_storage_efficiency(self, project_id: str) -> float:
        """Calculate storage efficiency (compression ratio)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        SUM(size_bytes) as total_size,
                        SUM(compressed_size_bytes) as total_compressed
                    FROM dcp_snapshots 
                    WHERE project_id = ?
                """, (project_id,))
                
                row = cursor.fetchone()
                total_size, total_compressed = row
                
                if total_size and total_compressed:
                    return (1.0 - (total_compressed / total_size)) * 100.0
                
                return 0.0
                
        except Exception:
            return 0.0


# Export main class
__all__ = ['DCPSnapshotManager', 'SnapshotMetadata', 'SnapshotQuery']
