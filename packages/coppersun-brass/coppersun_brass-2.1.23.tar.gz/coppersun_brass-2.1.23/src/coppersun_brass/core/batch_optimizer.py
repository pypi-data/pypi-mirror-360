"""
Token-based Batch Optimizer for Copper Alloy Brass
Implements intelligent batching based on token count rather than fixed file count
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class FileBatch:
    """Represents a batch of files optimized for token count"""
    batch_id: int
    files: List[Path]
    estimated_tokens: int
    priority_score: float
    
    def add_file(self, file_path: Path, tokens: int):
        """Add a file to the batch"""
        self.files.append(file_path)
        self.estimated_tokens += tokens
        
    def can_fit(self, tokens: int, max_tokens: int) -> bool:
        """Check if file can fit in batch without exceeding limit"""
        return self.estimated_tokens + tokens <= max_tokens


class TokenBatchOptimizer:
    """
    Optimizes file batching based on token count instead of fixed file count.
    Replaces the old 5-file batch system with dynamic token-based batching.
    """
    
    def __init__(self, 
                 max_tokens_per_batch: int = 6000,
                 max_batch_size: int = 20,  # Max files per batch
                 token_reserve: float = 0.1):  # 10% reserve for prompt overhead
        """
        Initialize token-based batch optimizer
        
        Args:
            max_tokens_per_batch: Maximum tokens per batch (default 6000)
            max_batch_size: Maximum number of files per batch
            token_reserve: Reserve percentage for prompt overhead
        """
        self.max_tokens_per_batch = int(max_tokens_per_batch * (1 - token_reserve))
        self.max_batch_size = max_batch_size
        self.token_cache = {}
        
        # Token estimation factors
        self.char_to_token_ratio = 4  # ~4 characters per token
        self.file_type_multipliers = {
            '.py': 1.0,    # Python files are baseline
            '.js': 0.9,    # JS slightly more compact
            '.ts': 1.1,    # TypeScript more verbose
            '.java': 1.2,  # Java more verbose
            '.md': 0.8,    # Markdown more compact
            '.txt': 0.7,   # Plain text most compact
            '.json': 1.3,  # JSON can be verbose
            '.yaml': 1.1,  # YAML moderately verbose
            '.xml': 1.4,   # XML most verbose
        }
        
    def estimate_file_tokens(self, file_path: Path) -> int:
        """
        Estimate token count for a file with caching
        
        Args:
            file_path: Path to file
            
        Returns:
            Estimated token count
        """
        # Check cache first
        cache_key = self._get_cache_key(file_path)
        if cache_key in self.token_cache:
            return self.token_cache[cache_key]
        
        try:
            # Get file size
            file_size = file_path.stat().st_size
            
            # Base token estimate
            base_tokens = file_size // self.char_to_token_ratio
            
            # Apply file type multiplier
            extension = file_path.suffix.lower()
            multiplier = self.file_type_multipliers.get(extension, 1.0)
            
            estimated_tokens = int(base_tokens * multiplier)
            
            # Cache the result
            self.token_cache[cache_key] = estimated_tokens
            
            return estimated_tokens
            
        except Exception as e:
            logger.warning(f"Error estimating tokens for {file_path}: {e}")
            return 1000  # Default fallback
    
    def _get_cache_key(self, file_path: Path) -> str:
        """
        Generate cache key including file size for better invalidation
        
        Args:
            file_path: Path to file
            
        Returns:
            Cache key string
        """
        try:
            stat = file_path.stat()
            # Include file size and modification time in cache key
            key_parts = [
                str(file_path),
                str(stat.st_size),
                str(int(stat.st_mtime))
            ]
            return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
        except Exception:
            # Fallback to just path if stat fails
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def create_optimal_batches(self, 
                             files: List[Path], 
                             priority_func: Optional[callable] = None) -> List[FileBatch]:
        """
        Create optimal batches based on token count
        
        Args:
            files: List of files to batch
            priority_func: Optional function to calculate priority score
            
        Returns:
            List of optimized file batches
        """
        if not files:
            return []
        
        # Calculate tokens and priority for each file
        file_info = []
        for file_path in files:
            tokens = self.estimate_file_tokens(file_path)
            priority = priority_func(file_path) if priority_func else 1.0
            file_info.append({
                'path': file_path,
                'tokens': tokens,
                'priority': priority
            })
        
        # Sort by priority (descending) and tokens (ascending)
        # High priority files first, smaller files preferred within same priority
        file_info.sort(key=lambda x: (-x['priority'], x['tokens']))
        
        # Create batches using bin packing algorithm
        batches = []
        current_batch = None
        batch_id = 0
        
        for info in file_info:
            file_path = info['path']
            tokens = info['tokens']
            
            # Skip files that are too large for any batch
            if tokens > self.max_tokens_per_batch:
                logger.warning(f"File {file_path} exceeds max tokens ({tokens} > {self.max_tokens_per_batch})")
                continue
            
            # Try to fit in current batch
            if current_batch and current_batch.can_fit(tokens, self.max_tokens_per_batch):
                if len(current_batch.files) < self.max_batch_size:
                    current_batch.add_file(file_path, tokens)
                    continue
            
            # Need new batch
            if current_batch:
                batches.append(current_batch)
            
            current_batch = FileBatch(
                batch_id=batch_id,
                files=[file_path],
                estimated_tokens=tokens,
                priority_score=info['priority']
            )
            batch_id += 1
        
        # Add final batch
        if current_batch:
            batches.append(current_batch)
        
        # Apply best-fit optimization
        batches = self._optimize_batches(batches, file_info)
        
        return batches
    
    def _optimize_batches(self, batches: List[FileBatch], file_info: List[Dict]) -> List[FileBatch]:
        """
        Optimize batches using best-fit algorithm to minimize wasted space
        
        Args:
            batches: Initial batches
            file_info: File information with tokens
            
        Returns:
            Optimized batches
        """
        # Create lookup for quick token access
        token_lookup = {info['path']: info['tokens'] for info in file_info}
        
        # Try to rebalance batches
        optimized = []
        remaining_files = []
        
        # Collect all files
        for batch in batches:
            remaining_files.extend(batch.files)
        
        # Recreate batches with better packing
        batch_id = 0
        while remaining_files:
            batch = FileBatch(
                batch_id=batch_id,
                files=[],
                estimated_tokens=0,
                priority_score=0
            )
            
            # Best-fit: try to fill batch optimally
            files_to_remove = []
            
            for file_path in remaining_files:
                tokens = token_lookup[file_path]
                
                if batch.can_fit(tokens, self.max_tokens_per_batch) and len(batch.files) < self.max_batch_size:
                    batch.add_file(file_path, tokens)
                    files_to_remove.append(file_path)
                    
                    # Check if batch is nearly full (>90% capacity)
                    if batch.estimated_tokens > self.max_tokens_per_batch * 0.9:
                        break
            
            # Remove added files
            for file_path in files_to_remove:
                remaining_files.remove(file_path)
            
            if batch.files:
                optimized.append(batch)
                batch_id += 1
            else:
                # No files could fit, might have oversized files
                break
        
        return optimized
    
    def get_batch_statistics(self, batches: List[FileBatch]) -> Dict[str, Any]:
        """
        Get statistics about the batches
        
        Args:
            batches: List of file batches
            
        Returns:
            Dictionary of statistics
        """
        if not batches:
            return {
                'total_batches': 0,
                'total_files': 0,
                'total_tokens': 0,
                'avg_tokens_per_batch': 0,
                'avg_files_per_batch': 0,
                'batch_efficiency': 0
            }
        
        total_files = sum(len(batch.files) for batch in batches)
        total_tokens = sum(batch.estimated_tokens for batch in batches)
        
        # Calculate efficiency (how well we're using token budget)
        max_possible_tokens = len(batches) * self.max_tokens_per_batch
        efficiency = total_tokens / max_possible_tokens if max_possible_tokens > 0 else 0
        
        return {
            'total_batches': len(batches),
            'total_files': total_files,
            'total_tokens': total_tokens,
            'avg_tokens_per_batch': total_tokens / len(batches),
            'avg_files_per_batch': total_files / len(batches),
            'batch_efficiency': efficiency,
            'token_utilization': f"{efficiency * 100:.1f}%",
            'batches': [
                {
                    'id': batch.batch_id,
                    'files': len(batch.files),
                    'tokens': batch.estimated_tokens,
                    'utilization': f"{(batch.estimated_tokens / self.max_tokens_per_batch) * 100:.1f}%"
                }
                for batch in batches
            ]
        }
    
    def clear_cache(self):
        """Clear the token estimation cache"""
        self.token_cache.clear()
        logger.info("Token cache cleared")