"""Optimized analyzer for large codebases with memory-efficient processing."""
import os
import gc
import time
import multiprocessing
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import logging
import psutil

logger = logging.getLogger(__name__)

@dataclass
class FileChunk:
    """A chunk of files for processing."""
    chunk_id: int
    files: List[Path]
    total_size: int

class LargeCodebaseAnalyzer:
    """
    Optimized analyzer for large codebases.
    
    Features:
    - Memory-efficient file processing
    - Parallel analysis with process pool
    - Automatic chunking based on memory
    - Progress tracking
    - Graceful degradation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Memory management
        self.max_memory_mb = self.config.get('max_memory_mb', 1024)  # 1GB default
        self.chunk_size_mb = self.config.get('chunk_size_mb', 50)   # 50MB chunks
        self.max_file_size_mb = self.config.get('max_file_size_mb', 10)  # Skip large files
        
        # Performance
        self.num_workers = self.config.get('num_workers', max(1, multiprocessing.cpu_count() - 1))
        self.batch_size = self.config.get('batch_size', 100)
        
        # File filters
        self.skip_patterns = {
            '.git', '__pycache__', 'node_modules', '.next', 'dist', 'build',
            'venv', 'env', '.tox', 'coverage', 'htmlcov', '.pytest_cache',
            'target', '.idea', '.vscode', 'vendor', 'bower_components'
        }
        
        self.binary_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll', '.exe',
            '.jpg', '.jpeg', '.png', '.gif', '.ico', '.pdf', '.zip',
            '.tar', '.gz', '.bz2', '.7z', '.rar', '.mp3', '.mp4',
            '.avi', '.mov', '.wmv', '.flv', '.swf', '.woff', '.woff2',
            '.ttf', '.eot', '.otf', '.db', '.sqlite', '.sqlite3'
        }
        
        # Source file extensions to analyze
        self.source_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c',
            '.h', '.hpp', '.cs', '.go', '.rs', '.php', '.rb', '.swift',
            '.kt', '.scala', '.r', '.m', '.mm', '.vue', '.svelte'
        }
    
    def analyze_project(self, project_path: Path, 
                       progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Analyze large project with memory efficiency.
        
        Args:
            project_path: Path to project
            progress_callback: Optional callback(current, total, message)
        """
        start_time = time.time()
        
        # Phase 1: Scan and filter files
        logger.info("Phase 1: Scanning project structure...")
        eligible_files = list(self._scan_files(project_path))
        total_files = len(eligible_files)
        
        if progress_callback:
            progress_callback(0, total_files, f"Found {total_files} files to analyze")
        
        if total_files == 0:
            return {
                'total_files': 0,
                'findings': [],
                'metadata': {
                    'duration_seconds': time.time() - start_time,
                    'memory_peak_mb': self._get_peak_memory()
                }
            }
        
        # Phase 2: Create memory-efficient chunks
        logger.info("Phase 2: Creating processing chunks...")
        chunks = self._create_chunks(eligible_files)
        logger.info(f"Created {len(chunks)} chunks for processing")
        
        # Phase 3: Process chunks in parallel
        logger.info(f"Phase 3: Processing {len(chunks)} chunks with {self.num_workers} workers...")
        results = self._process_chunks(chunks, progress_callback, total_files)
        
        # Phase 4: Aggregate results
        logger.info("Phase 4: Aggregating results...")
        final_results = self._aggregate_results(results)
        
        # Add metadata
        final_results['metadata'] = {
            'total_files': total_files,
            'chunks_processed': len(chunks),
            'duration_seconds': time.time() - start_time,
            'memory_peak_mb': self._get_peak_memory(),
            'workers_used': self.num_workers
        }
        
        return final_results
    
    def _scan_files(self, project_path: Path) -> Iterator[Path]:
        """Scan and filter eligible files."""
        for root, dirs, files in os.walk(project_path, topdown=True):
            root_path = Path(root)
            
            # Filter directories (modifies dirs in-place to skip)
            dirs[:] = [d for d in dirs if d not in self.skip_patterns]
            
            for file_name in files:
                file_path = root_path / file_name
                
                # Skip by extension
                if file_path.suffix in self.binary_extensions:
                    continue
                
                # Only analyze source files
                if file_path.suffix not in self.source_extensions:
                    continue
                
                # Skip large files
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > self.max_file_size_mb:
                        logger.debug(f"Skipping large file: {file_path} ({size_mb:.1f}MB)")
                        continue
                except:
                    continue
                
                yield file_path
    
    def _create_chunks(self, files: List[Path]) -> List[FileChunk]:
        """Create memory-efficient chunks."""
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
            except:
                continue
            
            # Check if adding this file would exceed chunk size
            if current_size + file_size > self.chunk_size_mb * 1024 * 1024 and current_chunk:
                chunks.append(FileChunk(
                    chunk_id=chunk_id,
                    files=current_chunk,
                    total_size=current_size
                ))
                chunk_id += 1
                current_chunk = []
                current_size = 0
            
            current_chunk.append(file_path)
            current_size += file_size
        
        # Add remaining files
        if current_chunk:
            chunks.append(FileChunk(
                chunk_id=chunk_id,
                files=current_chunk,
                total_size=current_size
            ))
        
        return chunks
    
    def _process_chunks(self, chunks: List[FileChunk], 
                       progress_callback: Optional[Callable],
                       total_files: int) -> List[Dict]:
        """Process chunks in parallel."""
        results = []
        completed_files = 0
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(self._process_single_chunk, chunk): chunk
                for chunk in chunks
            }
            
            # Process completed chunks
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    result = future.result(timeout=300)  # 5 minute timeout per chunk
                    results.append(result)
                    
                    completed_files += len(chunk.files)
                    if progress_callback:
                        progress_callback(
                            completed_files, total_files, 
                            f"Processed chunk {chunk.chunk_id + 1}/{len(chunks)}"
                        )
                    
                except Exception as e:
                    logger.error(f"Chunk {chunk.chunk_id} failed: {e}")
                    # Create empty result for failed chunk
                    results.append({
                        'chunk_id': chunk.chunk_id,
                        'files_processed': 0,
                        'findings': [],
                        'errors': [{'error': str(e), 'chunk_id': chunk.chunk_id}]
                    })
        
        return results
    
    def _process_single_chunk(self, chunk: FileChunk) -> Dict[str, Any]:
        """Process a single chunk (runs in separate process)."""
        # Import heavy dependencies only in worker process
        from ...agents.scout.todo_detector import TODODetector
        from ...agents.scout.analyzers.pattern_analyzer import PatternAnalyzer
        
        chunk_results = {
            'chunk_id': chunk.chunk_id,
            'files_processed': 0,
            'findings': [],
            'errors': [],
            'patterns': {}
        }
        
        # Create analyzer instances
        todo_detector = TODODetector()
        pattern_analyzer = PatternAnalyzer()
        
        for file_path in chunk.files:
            try:
                # Read file content
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Analyze TODOs
                todos = todo_detector.scan_content(content, str(file_path))
                chunk_results['findings'].extend(todos)
                
                # Analyze patterns
                patterns = pattern_analyzer.analyze_file(file_path, content)
                for pattern_type, pattern_list in patterns.items():
                    if pattern_type not in chunk_results['patterns']:
                        chunk_results['patterns'][pattern_type] = []
                    chunk_results['patterns'][pattern_type].extend(pattern_list)
                
                chunk_results['files_processed'] += 1
                
            except Exception as e:
                chunk_results['errors'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
            
            # Periodic garbage collection
            if chunk_results['files_processed'] % 50 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
        
        return chunk_results
    
    def _aggregate_results(self, chunk_results: List[Dict]) -> Dict[str, Any]:
        """Aggregate results from all chunks."""
        aggregated = {
            'total_findings': 0,
            'findings_by_type': {},
            'patterns': {},
            'errors': [],
            'chunks_processed': len(chunk_results),
            'files_processed': 0
        }
        
        for result in chunk_results:
            aggregated['files_processed'] += result['files_processed']
            aggregated['total_findings'] += len(result['findings'])
            aggregated['errors'].extend(result['errors'])
            
            # Aggregate findings by type
            for finding in result['findings']:
                finding_type = finding.get('type', 'unknown')
                if finding_type not in aggregated['findings_by_type']:
                    aggregated['findings_by_type'][finding_type] = 0
                aggregated['findings_by_type'][finding_type] += 1
            
            # Aggregate patterns
            for pattern_type, patterns in result.get('patterns', {}).items():
                if pattern_type not in aggregated['patterns']:
                    aggregated['patterns'][pattern_type] = []
                aggregated['patterns'][pattern_type].extend(patterns)
        
        # Summarize patterns
        aggregated['pattern_summary'] = {
            pattern_type: len(patterns)
            for pattern_type, patterns in aggregated['patterns'].items()
        }
        
        return aggregated
    
    def _get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0
    
    def analyze_file_async(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file (for incremental updates)."""
        from ...agents.scout.todo_detector import TODODetector
        from ...agents.scout.analyzers.pattern_analyzer import PatternAnalyzer
        
        todo_detector = TODODetector()
        pattern_analyzer = PatternAnalyzer()
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                'file': str(file_path),
                'todos': todo_detector.scan_content(content, str(file_path)),
                'patterns': pattern_analyzer.analyze_file(file_path, content),
                'size_bytes': file_path.stat().st_size,
                'analyzed_at': time.time()
            }
            
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'analyzed_at': time.time()
            }

# Export classes
__all__ = ['LargeCodebaseAnalyzer', 'FileChunk']