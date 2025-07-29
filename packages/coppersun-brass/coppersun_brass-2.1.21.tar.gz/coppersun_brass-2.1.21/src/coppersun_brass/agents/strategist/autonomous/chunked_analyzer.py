"""
ChunkedAnalyzer - Memory-efficient analysis for large projects

Implements chunked analysis with memory management for projects with 1000+ files
while maintaining analysis quality through intelligent sampling and aggregation.
"""

import asyncio
import gc
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Iterator, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AnalysisChunk:
    """Represents a chunk of files for analysis"""
    files: List[Path]
    estimated_size: int
    chunk_id: int
    
    def __len__(self) -> int:
        return len(self.files)


@dataclass
class PartialAnalysis:
    """Represents partial analysis results with confidence scoring"""
    data: Dict[str, Any]
    confidence: float
    files_analyzed: int
    total_files: int
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.data,
            'analysis_metadata': {
                'confidence': self.confidence,
                'files_analyzed': self.files_analyzed,
                'total_files': self.total_files,
                'message': self.message
            }
        }


class ChunkedAnalyzer:
    """
    Memory-efficient chunked analysis for large projects
    
    Implements intelligent sampling, graceful degradation, and efficient
    memory management for projects exceeding memory limits.
    """
    
    def __init__(self, max_memory_mb: int = 400):
        """
        Initialize chunked analyzer with memory constraints
        
        Args:
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_memory_mb = max_memory_mb
        self.max_chunk_size_mb = max_memory_mb // 4  # 25% of total memory per chunk
        self.chunk_timeout = 2.0  # 2 seconds per chunk
        
        # File size estimation (bytes per file type)
        self.file_size_estimates = {
            '.py': 3000,
            '.js': 2500,
            '.ts': 3500,
            '.jsx': 3000,
            '.tsx': 4000,
            '.java': 4000,
            '.cpp': 3500,
            '.c': 2500,
            '.go': 2800,
            '.rs': 3200,
            '.php': 2800,
            '.rb': 2200,
            'default': 2000
        }
        
        # Analysis priorities for sampling
        self.file_priorities = {
            '.py': 10,
            '.js': 9,
            '.ts': 9,
            '.jsx': 8,
            '.tsx': 8,
            '.java': 7,
            '.cpp': 6,
            '.c': 6,
            '.go': 7,
            '.rs': 7,
            '.php': 6,
            '.rb': 6,
            '.vue': 8,
            '.svelte': 7,
            'default': 3
        }
    
    async def analyze_large_project(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze large project with chunked processing and memory management
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Aggregated analysis results with confidence scoring
        """
        if not project_path.exists() or not project_path.is_dir():
            raise ValueError(f"Invalid project path: {project_path}")
        
        try:
            logger.info(f"Starting chunked analysis for large project: {project_path}")
            
            # Collect and prioritize files
            files = await self._collect_analyzable_files(project_path)
            total_files = len(files)
            
            if total_files == 0:
                return self._get_empty_analysis()
            
            # Create chunks based on memory constraints
            chunks = await self._create_analysis_chunks(files)
            logger.info(f"Created {len(chunks)} chunks for {total_files} files")
            
            # Analyze chunks with timeout and memory management
            chunk_results = []
            files_analyzed = 0
            
            for chunk in chunks:
                try:
                    chunk_result = await self._analyze_chunk_with_timeout(project_path, chunk)
                    chunk_results.append(chunk_result)
                    files_analyzed += chunk_result.files_analyzed
                    
                    # Force garbage collection after each chunk
                    gc.collect()
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Chunk {chunk.chunk_id} timed out after {self.chunk_timeout}s")
                    chunk_results.append(PartialAnalysis(
                        data=self._get_minimal_chunk_data(),
                        confidence=0.3,
                        files_analyzed=0,
                        total_files=len(chunk),
                        message=f"Chunk {chunk.chunk_id} timed out"
                    ))
                except Exception as e:
                    logger.error(f"Chunk {chunk.chunk_id} failed: {e}")
                    chunk_results.append(PartialAnalysis(
                        data=self._get_minimal_chunk_data(),
                        confidence=0.2,
                        files_analyzed=0,
                        total_files=len(chunk),
                        message=f"Chunk {chunk.chunk_id} failed: {str(e)}"
                    ))
            
            # Aggregate results from all chunks
            aggregated_result = await self._aggregate_chunk_results(
                chunk_results, files_analyzed, total_files
            )
            
            logger.info(f"Chunked analysis complete: {files_analyzed}/{total_files} files analyzed "
                       f"(confidence: {aggregated_result['analysis_metadata']['confidence']:.2f})")
            
            return aggregated_result
            
        except Exception as e:
            logger.error(f"Chunked analysis failed: {e}")
            raise RuntimeError(f"Large project analysis failed: {e}")
    
    async def analyze_file_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze file structure with chunked processing"""
        try:
            files = await self._collect_analyzable_files(project_path)
            
            if len(files) <= 100:
                # Use regular analysis for smaller projects
                return await self._analyze_structure_regular(project_path, files)
            
            # Use chunked analysis for large projects
            chunks = await self._create_file_chunks_by_type(files)
            structure_data = {
                'total_files': len(files),
                'file_types': defaultdict(int),
                'directory_structure': {},
                'depth_analysis': {},
                'organization_patterns': {}
            }
            
            for chunk in chunks:
                chunk_structure = await self._analyze_structure_chunk(project_path, chunk)
                await self._merge_structure_data(structure_data, chunk_structure)
            
            # Calculate final metrics
            structure_data['structure_quality_score'] = await self._calculate_structure_quality_chunked(
                structure_data
            )
            
            return structure_data
            
        except Exception as e:
            logger.error(f"Chunked file structure analysis failed: {e}")
            return self._get_minimal_structure_data(project_path)
    
    async def analyze_code_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze code patterns with intelligent sampling"""
        try:
            files = await self._collect_code_files(project_path)
            
            if len(files) <= 50:
                # Analyze all files for smaller projects
                return await self._analyze_patterns_complete(project_path, files)
            
            # Use intelligent sampling for large projects
            sampled_files = await self._sample_files_intelligently(files, max_files=50)
            
            patterns = await self._analyze_patterns_sampled(project_path, sampled_files)
            
            # Add sampling metadata
            patterns['sampling_metadata'] = {
                'total_files': len(files),
                'sampled_files': len(sampled_files),
                'sampling_ratio': len(sampled_files) / len(files),
                'confidence': min(1.0, len(sampled_files) / 30)  # Full confidence at 30+ files
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Chunked pattern analysis failed: {e}")
            return {'patterns': [], 'architecture_style': 'unknown', 'confidence': 0.0}
    
    async def _collect_analyzable_files(self, project_path: Path) -> List[Path]:
        """Collect all files suitable for analysis"""
        files = []
        
        # File extensions to analyze
        analyzable_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
            '.java', '.cpp', '.c', '.h', '.hpp', '.go', '.rs',
            '.php', '.rb', '.cs', '.swift', '.kt', '.scala',
            '.json', '.yaml', '.yml', '.toml', '.xml'
        }
        
        # Ignore patterns
        ignore_patterns = {
            '__pycache__', '.git', 'node_modules', '.npm', 'venv', '.venv',
            'target', 'build', 'dist', '.idea', '.vscode', 'coverage'
        }
        
        try:
            for file_path in project_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip ignored directories
                if any(ignore_pattern in str(file_path) for ignore_pattern in ignore_patterns):
                    continue
                
                # Only include analyzable file types
                if file_path.suffix.lower() in analyzable_extensions:
                    # Skip very large files (>1MB)
                    try:
                        if file_path.stat().st_size < 1024 * 1024:
                            files.append(file_path)
                    except OSError:
                        continue  # Skip files we can't read
            
            return files
            
        except Exception as e:
            logger.error(f"Error collecting analyzable files: {e}")
            return []
    
    async def _create_analysis_chunks(self, files: List[Path]) -> List[AnalysisChunk]:
        """Create analysis chunks based on memory constraints"""
        chunks = []
        current_chunk_files = []
        current_chunk_size = 0
        chunk_id = 0
        
        # Sort files by priority and size
        prioritized_files = await self._prioritize_files(files)
        
        for file_path in prioritized_files:
            # Estimate file size for memory calculation
            estimated_size = self._estimate_file_size(file_path)
            
            # Check if adding this file would exceed chunk size limit
            if (current_chunk_size + estimated_size > self.max_chunk_size_mb * 1024 * 1024 and 
                current_chunk_files):
                
                # Create chunk with current files
                chunks.append(AnalysisChunk(
                    files=current_chunk_files.copy(),
                    estimated_size=current_chunk_size,
                    chunk_id=chunk_id
                ))
                
                # Start new chunk
                current_chunk_files = [file_path]
                current_chunk_size = estimated_size
                chunk_id += 1
            else:
                current_chunk_files.append(file_path)
                current_chunk_size += estimated_size
        
        # Add remaining files as final chunk
        if current_chunk_files:
            chunks.append(AnalysisChunk(
                files=current_chunk_files,
                estimated_size=current_chunk_size,
                chunk_id=chunk_id
            ))
        
        return chunks
    
    async def _prioritize_files(self, files: List[Path]) -> List[Path]:
        """Prioritize files for analysis based on importance"""
        def get_priority(file_path: Path) -> int:
            extension = file_path.suffix.lower()
            base_priority = self.file_priorities.get(extension, self.file_priorities['default'])
            
            # Boost priority for certain file names
            name_lower = file_path.name.lower()
            if any(important in name_lower for important in ['main', 'index', 'app', 'config']):
                base_priority += 3
            
            # Boost priority for root-level files
            try:
                depth = len(file_path.parts)
                if depth <= 3:  # Root or near-root files
                    base_priority += 2
            except Exception:
                pass
            
            return base_priority
        
        return sorted(files, key=get_priority, reverse=True)
    
    def _estimate_file_size(self, file_path: Path) -> int:
        """Estimate file size for memory calculation"""
        try:
            # Try to get actual file size first
            actual_size = file_path.stat().st_size
            if actual_size > 0:
                return actual_size
        except OSError:
            pass
        
        # Fall back to estimated size based on extension
        extension = file_path.suffix.lower()
        return self.file_size_estimates.get(extension, self.file_size_estimates['default'])
    
    async def _analyze_chunk_with_timeout(self, project_path: Path, chunk: AnalysisChunk) -> PartialAnalysis:
        """Analyze a chunk with timeout and graceful degradation"""
        try:
            result = await asyncio.wait_for(
                self._analyze_chunk(project_path, chunk),
                timeout=self.chunk_timeout
            )
            return result
        except asyncio.TimeoutError:
            # Return partial results on timeout
            return PartialAnalysis(
                data=self._get_minimal_chunk_data(),
                confidence=0.4,
                files_analyzed=0,
                total_files=len(chunk),
                message=f"Chunk analysis timed out after {self.chunk_timeout}s"
            )
    
    async def _analyze_chunk(self, project_path: Path, chunk: AnalysisChunk) -> PartialAnalysis:
        """Analyze a single chunk of files"""
        chunk_data = {
            'file_types': defaultdict(int),
            'patterns': [],
            'complexity_indicators': [],
            'structure_info': {}
        }
        
        files_analyzed = 0
        
        try:
            for file_path in chunk.files:
                try:
                    # Check file accessibility and size
                    try:
                        stat_info = file_path.stat()
                        if stat_info.st_size > 100000:  # Skip files > 100KB
                            continue
                    except (OSError, PermissionError):
                        continue
                    
                    # Basic file analysis
                    extension = file_path.suffix.lower()
                    chunk_data['file_types'][extension] += 1
                    
                    # Analyze file content for patterns (sample only)
                    if files_analyzed < 10:  # Limit content analysis to first 10 files
                        await self._analyze_file_content(file_path, chunk_data)
                    
                    files_analyzed += 1
                    
                except Exception as e:
                    logger.debug(f"Error analyzing file {file_path}: {e}")
                    continue
            
            # Calculate confidence based on files analyzed
            confidence = min(1.0, files_analyzed / len(chunk.files))
            
            return PartialAnalysis(
                data=chunk_data,
                confidence=confidence,
                files_analyzed=files_analyzed,
                total_files=len(chunk.files)
            )
            
        except Exception as e:
            logger.error(f"Chunk analysis failed: {e}")
            return PartialAnalysis(
                data=self._get_minimal_chunk_data(),
                confidence=0.3,
                files_analyzed=files_analyzed,
                total_files=len(chunk.files),
                message=f"Chunk analysis error: {str(e)}"
            )
        finally:
            # Ensure cleanup
            gc.collect()
    
    async def _analyze_file_content(self, file_path: Path, chunk_data: Dict[str, Any]) -> None:
        """Analyze file content for patterns (simplified)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Read only first 5KB
            
            # Look for common patterns
            if 'class ' in content or 'function ' in content or 'def ' in content:
                chunk_data['patterns'].append('object_oriented')
            
            if 'import ' in content or 'require(' in content:
                chunk_data['patterns'].append('modular')
            
            if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                chunk_data['patterns'].append('testing')
            
            # Check for complexity indicators
            if len(content.split('\n')) > 500:
                chunk_data['complexity_indicators'].append(f'large_file:{file_path.name}')
                
        except Exception as e:
            logger.debug(f"Error analyzing content for {file_path}: {e}")
    
    async def _aggregate_chunk_results(self, chunk_results: List[PartialAnalysis], 
                                     files_analyzed: int, total_files: int) -> Dict[str, Any]:
        """Aggregate results from all chunks"""
        aggregated = {
            'total_files': total_files,
            'file_types': defaultdict(int),
            'patterns': [],
            'complexity_indicators': [],
            'structure_info': {},
            'chunks_processed': len(chunk_results)
        }
        
        # Aggregate file types
        for result in chunk_results:
            for file_type, count in result.data.get('file_types', {}).items():
                aggregated['file_types'][file_type] += count
        
        # Aggregate patterns (with deduplication)
        all_patterns = []
        for result in chunk_results:
            all_patterns.extend(result.data.get('patterns', []))
        aggregated['patterns'] = list(set(all_patterns))  # Remove duplicates
        
        # Aggregate complexity indicators
        for result in chunk_results:
            aggregated['complexity_indicators'].extend(
                result.data.get('complexity_indicators', [])
            )
        
        # Calculate overall confidence
        if chunk_results:
            confidence_scores = [r.confidence for r in chunk_results if r.confidence > 0]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.3
        else:
            overall_confidence = 0.0
        
        # Calculate coverage
        coverage = files_analyzed / total_files if total_files > 0 else 0
        
        # Add analysis metadata
        aggregated['analysis_metadata'] = {
            'confidence': overall_confidence,
            'coverage': coverage,
            'files_analyzed': files_analyzed,
            'total_files': total_files,
            'analysis_method': 'chunked',
            'chunks_processed': len(chunk_results)
        }
        
        return aggregated
    
    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'total_files': 0,
            'file_types': {},
            'patterns': [],
            'complexity_indicators': [],
            'analysis_metadata': {
                'confidence': 0.0,
                'coverage': 0.0,
                'files_analyzed': 0,
                'total_files': 0,
                'analysis_method': 'chunked'
            }
        }
    
    def _get_minimal_chunk_data(self) -> Dict[str, Any]:
        """Return minimal chunk data structure"""
        return {
            'file_types': {},
            'patterns': [],
            'complexity_indicators': [],
            'structure_info': {}
        }
    
    async def _create_file_chunks_by_type(self, files: List[Path]) -> List[List[Path]]:
        """Create chunks grouped by file type for structure analysis"""
        chunks_by_type = defaultdict(list)
        
        # Group files by extension
        for file_path in files:
            extension = file_path.suffix.lower()
            chunks_by_type[extension].append(file_path)
        
        # Create chunks with mixed file types
        chunks = []
        chunk_size = 100  # Files per chunk for structure analysis
        
        all_files = []
        for files_of_type in chunks_by_type.values():
            all_files.extend(files_of_type)
        
        for i in range(0, len(all_files), chunk_size):
            chunks.append(all_files[i:i + chunk_size])
        
        return chunks
    
    async def _analyze_structure_regular(self, project_path: Path, files: List[Path]) -> Dict[str, Any]:
        """Regular structure analysis for smaller projects"""
        from .file_structure_analyzer import FileStructureAnalyzer
        
        analyzer = FileStructureAnalyzer()
        return await analyzer.analyze(project_path)
    
    async def _analyze_structure_chunk(self, project_path: Path, chunk: List[Path]) -> Dict[str, Any]:
        """Analyze structure for a chunk of files"""
        structure_data = {
            'file_count': len(chunk),
            'file_types': defaultdict(int),
            'directories': set(),
            'depth_info': {}
        }
        
        for file_path in chunk:
            try:
                # File type analysis
                extension = file_path.suffix.lower()
                structure_data['file_types'][extension] += 1
                
                # Directory analysis
                relative_path = file_path.relative_to(project_path)
                for parent in relative_path.parents:
                    if parent != Path('.'):
                        structure_data['directories'].add(str(parent))
                
                # Depth analysis
                depth = len(relative_path.parts) - 1  # Subtract 1 for the file itself
                if depth not in structure_data['depth_info']:
                    structure_data['depth_info'][depth] = 0
                structure_data['depth_info'][depth] += 1
                
            except Exception as e:
                logger.debug(f"Error analyzing structure for {file_path}: {e}")
                continue
        
        return structure_data
    
    async def _merge_structure_data(self, main_data: Dict[str, Any], chunk_data: Dict[str, Any]) -> None:
        """Merge chunk structure data into main structure data"""
        # Merge file types
        for file_type, count in chunk_data.get('file_types', {}).items():
            main_data['file_types'][file_type] += count
        
        # Merge directories
        if 'directory_structure' not in main_data:
            main_data['directory_structure'] = set()
        main_data['directory_structure'].update(chunk_data.get('directories', set()))
        
        # Merge depth info
        if 'depth_analysis' not in main_data:
            main_data['depth_analysis'] = {}
        for depth, count in chunk_data.get('depth_info', {}).items():
            if depth not in main_data['depth_analysis']:
                main_data['depth_analysis'][depth] = 0
            main_data['depth_analysis'][depth] += count
    
    async def _calculate_structure_quality_chunked(self, structure_data: Dict[str, Any]) -> float:
        """Calculate structure quality score for chunked analysis"""
        quality_score = 70  # Base score for chunked analysis
        
        # Adjust based on file type distribution
        total_files = structure_data['total_files']
        if total_files > 0:
            file_types = structure_data['file_types']
            
            # Check for good file type balance
            code_files = sum(count for ext, count in file_types.items() 
                           if ext in ['.py', '.js', '.ts', '.java', '.cpp'])
            code_ratio = code_files / total_files
            
            if 0.5 <= code_ratio <= 0.8:  # Good code file ratio
                quality_score += 15
            elif code_ratio < 0.3:  # Too few code files
                quality_score -= 10
        
        # Adjust based on depth distribution
        depth_analysis = structure_data.get('depth_analysis', {})
        if depth_analysis:
            avg_depth = sum(depth * count for depth, count in depth_analysis.items()) / total_files
            if 2 <= avg_depth <= 4:  # Good depth range
                quality_score += 10
            elif avg_depth > 6:  # Too deep
                quality_score -= 15
        
        return max(0, min(100, quality_score))
    
    def _get_minimal_structure_data(self, project_path: Path) -> Dict[str, Any]:
        """Return minimal structure data when analysis fails"""
        try:
            # Count files manually as fallback
            file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
            dir_count = sum(1 for _ in project_path.rglob('*') if _.is_dir())
            
            return {
                'total_files': file_count,
                'total_directories': dir_count,
                'file_types': {'unknown': file_count},
                'structure_quality_score': 30,  # Low score due to minimal analysis
                'analysis_metadata': {
                    'confidence': 0.2,
                    'analysis_method': 'minimal_fallback'
                }
            }
        except Exception:
            return {
                'total_files': 0,
                'total_directories': 0,
                'file_types': {},
                'structure_quality_score': 0,
                'analysis_metadata': {
                    'confidence': 0.0,
                    'analysis_method': 'failed'
                }
            }
    
    async def _collect_code_files(self, project_path: Path) -> List[Path]:
        """Collect only code files for pattern analysis"""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.java', '.cpp', '.c', '.go', '.rs'}
        
        files = await self._collect_analyzable_files(project_path)
        return [f for f in files if f.suffix.lower() in code_extensions]
    
    async def _sample_files_intelligently(self, files: List[Path], max_files: int) -> List[Path]:
        """Intelligently sample files for pattern analysis"""
        if len(files) <= max_files:
            return files
        
        # Prioritize files and take top samples
        prioritized = await self._prioritize_files(files)
        
        # Take samples from different parts of the priority list
        step = len(prioritized) // max_files
        sampled = []
        
        for i in range(0, len(prioritized), max(1, step)):
            if len(sampled) >= max_files:
                break
            sampled.append(prioritized[i])
        
        # Ensure we have exactly max_files (or fewer if not enough files)
        return sampled[:max_files]
    
    async def _analyze_patterns_complete(self, project_path: Path, files: List[Path]) -> Dict[str, Any]:
        """Complete pattern analysis for smaller projects"""
        from .file_structure_analyzer import FileStructureAnalyzer
        
        analyzer = FileStructureAnalyzer()
        return await analyzer.analyze_patterns(project_path)
    
    async def _analyze_patterns_sampled(self, project_path: Path, sampled_files: List[Path]) -> Dict[str, Any]:
        """Pattern analysis using sampled files"""
        patterns = {
            'naming_conventions': {},
            'architectural_patterns': [],
            'import_patterns': {},
            'code_organization': {}
        }
        
        # Analyze naming conventions
        naming_patterns = defaultdict(int)
        for file_path in sampled_files:
            pattern = self._detect_naming_pattern(file_path.stem)
            naming_patterns[pattern] += 1
        
        if naming_patterns:
            dominant_pattern = max(naming_patterns.keys(), key=naming_patterns.get)
            consistency = naming_patterns[dominant_pattern] / len(sampled_files) * 100
            
            patterns['naming_conventions'] = {
                'dominant_pattern': dominant_pattern,
                'consistency_score': consistency,
                'pattern_distribution': dict(naming_patterns)
            }
        
        # Analyze architectural patterns (simplified)
        directories = {f.parent.name.lower() for f in sampled_files}
        
        if any(arch in directories for arch in ['models', 'views', 'controllers']):
            patterns['architectural_patterns'].append('mvc')
        
        if any(comp in directories for comp in ['components', 'widgets']):
            patterns['architectural_patterns'].append('component_based')
        
        if len(directories) > 5:
            patterns['architectural_patterns'].append('modular')
        
        return {
            'patterns': patterns,
            'architecture_style': patterns['architectural_patterns'][0] if patterns['architectural_patterns'] else 'unknown',
            'confidence': min(1.0, len(sampled_files) / 30)
        }
    
    def _detect_naming_pattern(self, name: str) -> str:
        """Detect naming pattern of a file name"""
        if '_' in name and name.islower():
            return 'snake_case'
        elif '-' in name and name.islower():
            return 'kebab-case'
        elif name[0].isupper() and any(c.isupper() for c in name[1:]):
            return 'PascalCase'
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            return 'camelCase'
        else:
            return 'mixed'