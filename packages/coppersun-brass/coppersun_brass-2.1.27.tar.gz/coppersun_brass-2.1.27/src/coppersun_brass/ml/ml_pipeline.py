"""
ML Pipeline - Efficient two-tier filtering with cost optimization

Implements:
- Quick heuristic filtering (80% of cases)
- Batch ML processing for uncertain cases
- Cost tracking and optimization
- Graceful degradation
"""
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .quick_filter import QuickHeuristicFilter, QuickResult
from .efficient_classifier import EfficientMLClassifier
from .semantic_analyzer import SemanticAnalyzer
from ..core.storage import BrassStorage
from ..integrations.claude_api import ClaudeAnalyzer
from ..integrations.content_safety import DualPurposeContentSafety

logger = logging.getLogger(__name__)


class MLPipeline:
    """Efficient ML pipeline with two-tier filtering.
    
    Process:
    1. Quick heuristics catch 80% (instant)
    2. ML classification for uncertain cases
    3. Batch processing for efficiency
    4. Cost tracking for optimization
    """
    
    def __init__(self, model_dir: Path, storage: BrassStorage):
        """Initialize ML pipeline.
        
        Args:
            model_dir: Directory for ML models
            storage: Storage backend for tracking
        """
        self.storage = storage
        self.model_dir = model_dir
        
        # Initialize components
        self.quick_filter = QuickHeuristicFilter()
        self.ml_classifier = EfficientMLClassifier(model_dir)
        
        # Initialize semantic analyzer (always available with pure Python ML)
        try:
            self.semantic_analyzer = SemanticAnalyzer(model_dir)
            logger.info("Semantic analyzer initialized with pure Python ML")
        except Exception as e:
            self.semantic_analyzer = None
            logger.error(f"Failed to initialize semantic analyzer: {e}")
        
        # 🩸 BLOOD OATH: Pure Python ML only - no legacy pre-trained adapters
        self.pretrained_adapter = None
        logger.debug("Using pure Python ML instead of legacy pre-trained adapters")
        
        # Initialize Claude analyzer
        self.claude_analyzer = ClaudeAnalyzer()
        if self.claude_analyzer.api_key:
            logger.info("Claude API initialized for validation")
        
        # Initialize content safety for Phase 3 enhancement
        self.content_safety = DualPurposeContentSafety()
        logger.info("Dual-purpose content safety system initialized")
        
        # Threading for ML (keep it off main async loop)
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml_worker")
        
        # Batching configuration
        self.batch_size = 32
        self.batch_timeout = 1.0  # seconds
        self.pending_batch = []
        self.batch_lock = asyncio.Lock()
        self.batch_task = None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'quick_filtered': 0,
            'ml_processed': 0,
            'cache_hits': 0,
            'total_time_ms': 0
        }
    
    async def process_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process observations through two-tier filtering.
        
        Args:
            observations: List of observations to classify
            
        Returns:
            Classified observations with added 'classification' field
        """
        if not observations:
            return []
        
        start_time = time.time()
        results = []
        needs_ml = []
        
        # Phase 1: Quick filtering
        for obs in observations:
            self.stats['total_processed'] += 1
            
            # Quick classification
            quick_result = self.quick_filter.classify(obs)
            
            if quick_result.confidence >= 0.9:
                # Very confident - skip ML
                obs['classification'] = quick_result.label
                obs['confidence'] = quick_result.confidence
                obs['ml_used'] = False
                obs['classification_reason'] = quick_result.reason
                results.append(obs)
                self.stats['quick_filtered'] += 1
                
                logger.debug(
                    f"Quick classified {obs.get('data', {}).get('file', 'unknown')} "
                    f"as {quick_result.label} ({quick_result.confidence:.2f})"
                )
            else:
                # Uncertain - needs ML
                obs['quick_result'] = quick_result
                needs_ml.append(obs)
        
        # Phase 2: ML classification for uncertain cases
        if needs_ml:
            ml_results = await self._process_ml_batch(needs_ml)
            results.extend(ml_results)
        
        # Track timing
        elapsed_ms = (time.time() - start_time) * 1000
        self.stats['total_time_ms'] += elapsed_ms
        
        # Log statistics
        if len(observations) > 0:
            ml_percentage = (len(needs_ml) / len(observations)) * 100
            logger.info(
                f"Processed {len(observations)} observations: "
                f"{len(observations) - len(needs_ml)} quick filtered, "
                f"{len(needs_ml)} needed ML ({ml_percentage:.1f}%). "
                f"Time: {elapsed_ms:.1f}ms"
            )
        
        # Track ML usage for cost analysis
        if needs_ml:
            self._track_ml_usage(len(needs_ml), elapsed_ms)
        
        return results
    
    async def _process_ml_batch(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process observations through ML in batches.
        
        Args:
            observations: Observations needing ML classification
            
        Returns:
            Classified observations
        """
        # Add to pending batch
        async with self.batch_lock:
            self.pending_batch.extend(observations)
            
            # Process if batch is full
            if len(self.pending_batch) >= self.batch_size:
                return await self._run_ml_batch(self.pending_batch)
            
            # Otherwise, schedule batch processing
            if not self.batch_task or self.batch_task.done():
                self.batch_task = asyncio.create_task(self._batch_timeout())
        
        # For now, return observations with timeout processing
        # In production, would wait for batch completion
        return await self._wait_for_batch_results(observations)
    
    async def _batch_timeout(self):
        """Process batch after timeout."""
        await asyncio.sleep(self.batch_timeout)
        
        async with self.batch_lock:
            if self.pending_batch:
                await self._run_ml_batch(self.pending_batch)
    
    async def _run_ml_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run ML classification on a batch.
        
        Args:
            batch: Observations to classify
            
        Returns:
            Classified observations
        """
        # 🩸 BLOOD OATH: Use pure Python ML only - no legacy pre-trained models
        if not batch:
            return []
        
        try:
            # Extract file paths and content
            items = []
            for obs in batch:
                data = obs.get('data', {})
                file_path = data.get('file', 'unknown')
                content = data.get('content', '')
                
                # For file changes without content, try to get from description
                if not content and 'description' in data:
                    content = data['description']
                    
                items.append((file_path, content))
            
            # Run ML classification in thread pool
            loop = asyncio.get_event_loop()
            
            # Try semantic analysis first if available
            if self.semantic_analyzer:
                ml_results = []
                for file_path, content in items:
                    try:
                        # Use semantic analyzer for intelligent classification
                        semantic_result = await loop.run_in_executor(
                            self.executor,
                            self.semantic_analyzer.analyze,
                            content,
                            {'file_path': file_path}
                        )
                        ml_results.append((semantic_result.category, semantic_result.confidence))
                    except Exception as e:
                        logger.debug(f"Semantic analysis failed, using fallback: {e}")
                        # Fallback to pattern-based classifier
                        result = self.ml_classifier.classify_code(content, file_path)
                        ml_results.append((result['category'], result['confidence']))
            else:
                # Use pattern-based classifier
                ml_results = await loop.run_in_executor(
                    self.executor,
                    self.ml_classifier.classify_batch,
                    items
                )
            
            # Update observations with ML results
            validated_results = []
            
            for obs, (label, confidence) in zip(batch, ml_results):
                logger.debug(f"ML result for {obs.get('type')}: {label} ({confidence})")
                obs['classification'] = label
                obs['confidence'] = confidence
                obs['ml_used'] = True
                
                # Combine with quick result reason if available
                quick_result = obs.pop('quick_result', None)
                if quick_result:
                    obs['classification_reason'] = f"ML confirmed: {quick_result.reason}"
                else:
                    obs['classification_reason'] = "ML classification"
                
                # Claude validation for critical findings
                if label == 'critical' and self.claude_analyzer.api_key:
                    validated_results.append((obs, (label, confidence)))
                else:
                    self.stats['ml_processed'] += 1
                
                logger.debug(
                    f"ML classified {obs.get('data', {}).get('file', 'unknown')} "
                    f"as {label} ({confidence:.2f})"
                )
            
            # Batch validate critical findings with Claude
            if validated_results:
                await self._validate_with_claude(validated_results)
            
            # Clear batch
            self.pending_batch = []
            
            return batch
            
        except Exception as e:
            logger.error(f"ML batch processing failed: {e}")
            
            # Fallback: use quick filter results
            for obs in batch:
                quick_result = obs.pop('quick_result', None)
                if quick_result:
                    obs['classification'] = quick_result.label
                    obs['confidence'] = quick_result.confidence
                else:
                    obs['classification'] = 'important'
                    obs['confidence'] = 0.5
                    
                obs['ml_used'] = False
                obs['classification_reason'] = f"ML failed, fallback: {e}"
            
            return batch
    
    async def _wait_for_batch_results(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Wait for batch processing to complete.
        
        Simplified for initial implementation - in production would properly
        track and wait for specific observations.
        """
        # For now, process immediately
        return await self._run_ml_batch(observations)
    
    def _track_ml_usage(self, batch_size: int, processing_time_ms: float):
        """Track ML usage for cost analysis.
        
        Args:
            batch_size: Number of items in batch
            processing_time_ms: Processing time in milliseconds
        """
        try:
            # Get cache statistics from classifier
            ml_stats = self.ml_classifier.get_stats()
            
            self.storage.track_ml_usage(
                batch_size=batch_size,
                model_version="codebert-small-quantized-v1",
                processing_time_ms=int(processing_time_ms),
                cache_hits=ml_stats.get('cache_hits', 0),
                cache_misses=batch_size  # Simplified
            )
            
        except Exception as e:
            logger.error(f"Failed to track ML usage: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.stats.copy()
        
        # Calculate rates
        if stats['total_processed'] > 0:
            stats['quick_filter_rate'] = stats['quick_filtered'] / stats['total_processed']
            stats['ml_rate'] = stats['ml_processed'] / stats['total_processed']
            stats['avg_time_ms'] = stats['total_time_ms'] / stats['total_processed']
        else:
            stats['quick_filter_rate'] = 0.0
            stats['ml_rate'] = 0.0
            stats['avg_time_ms'] = 0.0
        
        # Add component stats
        stats['quick_filter'] = self.quick_filter.get_stats()
        stats['ml_classifier'] = self.ml_classifier.get_stats()
        
        # 🩸 BLOOD OATH: Pure Python ML only - no legacy pre-trained status
        
        # Get ML usage from storage
        try:
            ml_usage = self.storage.get_ml_stats(since=datetime.utcnow().replace(hour=0, minute=0))
            stats['ml_usage_today'] = ml_usage
        except Exception as e:
            logger.error(f"Failed to get ML usage stats: {e}")
            stats['ml_usage_today'] = {}
        
        return stats
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        if not file_path:
            return 'unknown'
        
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, 'unknown')
    
    async def _validate_with_claude(self, validated_results: List[Tuple[Dict, Tuple[str, float]]]):
        """Validate critical findings with Claude API.
        
        Args:
            validated_results: List of (observation, ml_result) tuples
        """
        logger.info(f"Validating {len(validated_results)} critical findings with Claude")
        
        for obs, ml_result in validated_results:
            try:
                # Get code content
                data = obs.get('data', {})
                content = data.get('content', data.get('snippet', ''))
                
                if not content:
                    continue
                
                # Validate with Claude
                validation = await self.claude_analyzer.validate_classification(
                    content, 
                    ml_result
                )
                
                if validation.get('validated'):
                    # Update classification based on Claude
                    obs['classification'] = validation['classification']
                    obs['confidence'] = validation['confidence']
                    obs['classification_reason'] = f"Claude validated: {validation['reason']}"
                    obs['claude_validated'] = True
                
                self.stats['ml_processed'] += 1
                
            except Exception as e:
                logger.error(f"Claude validation failed: {e}")
                self.stats['ml_processed'] += 1
    
    async def shutdown(self):
        """Clean shutdown of ML pipeline."""
        # Process any pending batches
        async with self.batch_lock:
            if self.pending_batch:
                await self._run_ml_batch(self.pending_batch)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Save ML classifier cache
        if self.ml_classifier.enabled:
            self.ml_classifier._save_cache()
        
        logger.info("ML pipeline shutdown complete")
    
    # PHASE 3 CLAUDE ENHANCEMENT: Smart filtering and orchestration
    
    async def select_for_claude_enhancement(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Phase 3: Select top 30% of observations for Claude enhancement (vs 10% baseline).
        
        Uses content safety pre-filtering and enhanced scoring algorithm.
        
        Args:
            observations: All processed observations
            
        Returns:
            Top ~30% most valuable observations safe for Claude enhancement
        """
        if not observations:
            return []
            
        logger.info(f"Selecting observations for Claude enhancement from {len(observations)} candidates")
        
        # Step 1: Enhanced scoring algorithm (more inclusive than baseline 10%)
        scored_observations = []
        for obs in observations:
            score = self._calculate_enhancement_value_expanded(obs)
            if score >= 60:  # Lower threshold vs 85+ for top 10%
                scored_observations.append((obs, score))
        
        # Sort by enhancement value
        scored_observations.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 30% candidates
        target_count = max(1, int(len(observations) * 0.30))
        candidates = [obs for obs, score in scored_observations[:target_count]]
        
        logger.info(f"Enhanced scoring selected {len(candidates)} candidates for content safety review")
        
        # Step 2: Content safety pre-filtering
        safe_candidates = []
        safety_blocked = 0
        
        for obs in candidates:
            # Get code content for safety analysis
            content = self._extract_content_for_safety(obs)
            if not content:
                continue
                
            # Comprehensive safety analysis
            safety_result = self.content_safety.analyze_content_comprehensive(
                content=content,
                file_path=obs.get('data', {}).get('file_path', ''),
                line_number=obs.get('data', {}).get('line_number', 0)
            )
            
            if safety_result.safe_for_api:
                # Safe for Claude API
                obs['claude_enhancement_eligible'] = True
                obs['content_safety_score'] = safety_result.risk_score
                obs['safety_processing_time_ms'] = safety_result.processing_time_ms
                safe_candidates.append(obs)
            else:
                # Blocked by safety filters
                safety_blocked += 1
                obs['claude_enhancement_eligible'] = False
                obs['safety_block_reason'] = f"Risk: {safety_result.risk_score}, Findings: {len(safety_result.customer_findings)}"
                
                # Still valuable for customer-facing security analysis
                obs['customer_security_findings'] = [
                    {
                        'type': f.type,
                        'description': f.description,
                        'remediation': f.remediation,
                        'severity': f.severity
                    }
                    for f in safety_result.customer_findings
                ]
        
        logger.info(f"Content safety approved {len(safe_candidates)} observations, blocked {safety_blocked}")
        
        return safe_candidates
    
    def _calculate_enhancement_value_expanded(self, obs: Dict[str, Any]) -> int:
        """Enhanced scoring algorithm for 30% coverage (vs 10% baseline).
        
        More inclusive criteria to identify valuable enhancement opportunities.
        
        Args:
            obs: Observation to score
            
        Returns:
            Enhancement value score (0-100, 60+ = top 30%)
        """
        score = 0
        obs_type = obs.get('type', '')
        data = obs.get('data', {})
        
        # Base scoring (more inclusive than baseline)
        if obs_type == 'security_issue':
            score += 40  # Increased from 30
        elif obs_type == 'todo':
            score += 35  # Increased from 25
        elif obs_type == 'code_entity':
            score += 30  # Increased from 20
        elif obs_type == 'code_issue':
            score += 25  # NEW: Include code quality issues
        else:
            score += 15  # Give everything a base chance
        
        # Priority and severity bonuses
        priority = data.get('priority_score', 0)
        if priority >= 70:
            score += 20
        elif priority >= 50:
            score += 10
        
        severity = data.get('severity', '').lower()
        if severity == 'high':
            score += 15
        elif severity == 'medium':
            score += 8
        
        # File importance analysis (expanded criteria)
        file_path = data.get('file_path', '').lower()
        
        # Critical file patterns
        critical_patterns = ['auth', 'security', 'payment', 'api', 'admin', 'user', 'login', 'config']
        if any(pattern in file_path for pattern in critical_patterns):
            score += 15
        
        # Important file patterns
        important_patterns = ['model', 'controller', 'service', 'util', 'core', 'main', 'index']
        if any(pattern in file_path for pattern in important_patterns):
            score += 8
        
        # Complexity indicators
        complexity = data.get('complexity_score', 0)
        if complexity > 8:
            score += 10
        elif complexity > 5:
            score += 5
        
        # Research potential (valuable for enhancement)
        if data.get('is_researchable', False):
            score += 12
        
        # Code quality indicators
        if 'injection' in str(data).lower() or 'xss' in str(data).lower():
            score += 20  # Security vulnerabilities
        
        if 'memory leak' in str(data).lower() or 'race condition' in str(data).lower():
            score += 15  # Performance issues
        
        return min(score, 100)
    
    def _extract_content_for_safety(self, obs: Dict[str, Any]) -> str:
        """Extract content from observation for safety analysis."""
        data = obs.get('data', {})
        
        # Try multiple content fields
        content_fields = ['content', 'snippet', 'description', 'pattern_text']
        for field in content_fields:
            content = data.get(field, '')
            if content and len(content.strip()) > 10:
                return content
        
        # Fallback to observation type info
        return f"{obs.get('type', 'unknown')}: {data.get('summary', '')}"
    
    async def enhance_observations_with_claude(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Phase 3: Enhance selected observations using optimized Claude API integration.
        
        Args:
            observations: Pre-filtered observations safe for Claude enhancement
            
        Returns:
            Observations with Claude enhancement data added
        """
        if not observations or not self.claude_analyzer.api_key:
            logger.warning("Claude enhancement skipped - no API key or observations")
            return observations
        
        enhanced_count = 0
        
        for obs in observations:
            try:
                obs_type = obs.get('type', '')
                data = obs.get('data', {})
                
                # Route to appropriate enhancement method based on type
                enhancement_result = {}
                
                if obs_type == 'todo':
                    enhancement_result = await self.claude_analyzer.enhance_todo_with_claude(data)
                elif obs_type == 'security_issue':
                    enhancement_result = await self.claude_analyzer.enhance_security_issue_with_claude(data)
                elif obs_type == 'code_entity':
                    enhancement_result = await self.claude_analyzer.enhance_code_entity_with_claude(data)
                elif obs_type == 'code_issue':
                    enhancement_result = await self.claude_analyzer.enhance_code_issue_with_claude(data)
                
                # Add enhancement data if successful
                if enhancement_result:
                    obs['claude_enhancement'] = enhancement_result
                    obs['claude_enhanced'] = True
                    enhanced_count += 1
                    
                    logger.debug(f"Enhanced {obs_type} with Claude: {list(enhancement_result.keys())}")
                else:
                    obs['claude_enhanced'] = False
                    obs['claude_enhancement'] = {}
                    
            except Exception as e:
                logger.error(f"Claude enhancement failed for {obs.get('type')}: {e}")
                obs['claude_enhanced'] = False
                obs['claude_enhancement_error'] = str(e)
        
        logger.info(f"Claude enhanced {enhanced_count}/{len(observations)} observations")
        
        return observations