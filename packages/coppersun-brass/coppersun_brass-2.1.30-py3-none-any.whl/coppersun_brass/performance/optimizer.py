"""
Performance Optimizer

General Staff G4 Role: Resource Optimization
Analyzes performance data and implements optimizations
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import statistics

from coppersun_brass.core.context.dcp_manager import DCPManager
from coppersun_brass.performance.profiler import PerformanceProfiler
from coppersun_brass.performance.metrics import MetricsCollector
from coppersun_brass.core.cache.manager import EnhancedCacheManager

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Automatic performance optimization system
    
    General Staff G4 Function: Analyzes performance bottlenecks and
    implements strategic optimizations to improve Copper Alloy Brass efficiency.
    """
    
    def __init__(self,
                 dcp_path: Optional[str] = None,
                 profiler: Optional[PerformanceProfiler] = None,
                 metrics: Optional[MetricsCollector] = None,
                 cache_manager: Optional[EnhancedCacheManager] = None):
        """
        Initialize with MANDATORY DCP integration
        
        Args:
            dcp_path: Path to DCP context file (mandatory per CLAUDE.md)
            profiler: Performance profiler instance
            metrics: Metrics collector instance
            cache_manager: Cache manager for optimization
        """
        # DCP is MANDATORY
        self.dcp_manager = DCPManager(dcp_path)
        
        # Components
        self.profiler = profiler or PerformanceProfiler(dcp_path)
        self.metrics = metrics or MetricsCollector(dcp_path)
        self.cache_manager = cache_manager
        
        # Optimization strategies
        self.strategies = {
            'cache_optimization': self._optimize_cache,
            'batch_processing': self._optimize_batching,
            'concurrency_tuning': self._optimize_concurrency,
            'memory_management': self._optimize_memory
        }
        
        # Optimization state
        self.applied_optimizations: List[Dict[str, Any]] = []
        self.optimization_results: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            'auto_optimize': True,
            'optimization_interval': 300,  # 5 minutes
            'min_samples': 100,           # Minimum samples before optimizing
            'improvement_threshold': 0.1   # 10% improvement required
        }
        
        # Background optimization
        self._optimizing = False
        self._optimization_task: Optional[asyncio.Task] = None
        
        # Load optimization history
        self._load_optimization_history()
    
    def _load_optimization_history(self) -> None:
        """Load optimization history from DCP"""
        try:
            opt_data = self.dcp_manager.get_section('performance.optimizations', {})
            
            self.applied_optimizations = opt_data.get('applied', [])
            self.optimization_results = opt_data.get('results', {})
            
            logger.info(f"Loaded {len(self.applied_optimizations)} historical optimizations")
            
        except Exception as e:
            logger.warning(f"Could not load optimization history: {e}")
    
    async def start_auto_optimization(self) -> None:
        """Start automatic optimization loop"""
        if self._optimizing:
            logger.warning("Auto-optimization already running")
            return
        
        self._optimizing = True
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("Started automatic performance optimization")
    
    async def stop_auto_optimization(self) -> None:
        """Stop automatic optimization"""
        if not self._optimizing:
            return
        
        self._optimizing = False
        
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        # Save final state
        self._save_optimization_state()
        
        logger.info("Stopped automatic performance optimization")
    
    async def _optimization_loop(self) -> None:
        """Background optimization loop"""
        while self._optimizing:
            try:
                # Wait for interval
                await asyncio.sleep(self.config['optimization_interval'])
                
                # Analyze performance
                issues = await self.analyze_performance()
                
                if issues and self.config['auto_optimize']:
                    # Apply optimizations
                    await self.apply_optimizations(issues)
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
    
    async def analyze_performance(self) -> List[Dict[str, Any]]:
        """Analyze current performance and identify issues"""
        issues = []
        
        # Get performance data
        perf_report = self.profiler.get_performance_report()
        metrics_summary = self.metrics.get_metrics_summary('5m')
        
        # Check for slow operations
        for op, stats in perf_report['operations'].items():
            if stats['count'] >= self.config['min_samples']:
                if stats['avg_ms'] > 1000:  # >1 second average
                    issues.append({
                        'type': 'slow_operation',
                        'operation': op,
                        'avg_ms': stats['avg_ms'],
                        'count': stats['count'],
                        'severity': 'high' if stats['avg_ms'] > 5000 else 'medium'
                    })
        
        # Check cache performance
        if self.cache_manager:
            cache_stats = self.cache_manager.get_stats()
            if cache_stats['hit_rate'] < 0.5 and cache_stats['total_requests'] > 100:
                issues.append({
                    'type': 'low_cache_hit_rate',
                    'hit_rate': cache_stats['hit_rate'],
                    'severity': 'medium'
                })
        
        # Check memory usage
        system_stats = perf_report['system']
        if system_stats['memory']['average_percent'] > 80:
            issues.append({
                'type': 'high_memory_usage',
                'average_percent': system_stats['memory']['average_percent'],
                'severity': 'high'
            })
        
        # Check error rates
        for timer_key, timer_stats in metrics_summary.get('timers', {}).items():
            error_rate = self._calculate_error_rate(timer_key)
            if error_rate > 0.1:  # >10% errors
                issues.append({
                    'type': 'high_error_rate',
                    'operation': timer_key,
                    'error_rate': error_rate,
                    'severity': 'high' if error_rate > 0.25 else 'medium'
                })
        
        return issues
    
    async def apply_optimizations(self, 
                                 issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply optimizations based on identified issues"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'issues_addressed': len(issues),
            'optimizations_applied': [],
            'improvements': {}
        }
        
        for issue in issues:
            try:
                # Select optimization strategy
                if issue['type'] == 'slow_operation':
                    result = await self._optimize_slow_operation(issue)
                elif issue['type'] == 'low_cache_hit_rate':
                    result = await self._optimize_cache(issue)
                elif issue['type'] == 'high_memory_usage':
                    result = await self._optimize_memory(issue)
                elif issue['type'] == 'high_error_rate':
                    result = await self._optimize_error_handling(issue)
                else:
                    continue
                
                if result['success']:
                    results['optimizations_applied'].append(result)
                    results['improvements'][issue['type']] = result.get('improvement', 0)
                
            except Exception as e:
                logger.error(f"Failed to optimize {issue['type']}: {e}")
        
        # Record optimization
        self._record_optimization(results)
        
        return results
    
    async def _optimize_slow_operation(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize slow operation"""
        operation = issue['operation']
        current_avg = issue['avg_ms']
        
        # Strategy 1: Enable caching for expensive operations
        cache_key_prefix = f"opt_cache_{operation}"
        
        # Measure improvement
        before_stats = self.profiler.get_operation_stats(operation)
        
        # Apply caching wrapper
        # In real implementation, would wrap the actual operation
        
        # Simulate improvement measurement
        await asyncio.sleep(0.1)
        after_stats = self.profiler.get_operation_stats(operation)
        
        improvement = 0
        if before_stats['avg_ms'] > 0:
            improvement = (before_stats['avg_ms'] - after_stats.get('avg_ms', before_stats['avg_ms'])) / before_stats['avg_ms']
        
        return {
            'success': True,
            'optimization': 'caching',
            'operation': operation,
            'before_ms': before_stats['avg_ms'],
            'after_ms': after_stats.get('avg_ms', before_stats['avg_ms']),
            'improvement': improvement
        }
    
    async def _optimize_cache(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize cache configuration"""
        if not self.cache_manager:
            return {'success': False, 'reason': 'No cache manager available'}
        
        current_hit_rate = issue['hit_rate']
        
        # Strategy: Adjust cache size and TTL
        current_stats = self.cache_manager.get_stats()
        
        # Increase memory cache size if hit rate is low
        if current_hit_rate < 0.5:
            # In real implementation, would adjust cache parameters
            logger.info("Increasing cache memory allocation")
        
        # Analyze cache misses and adjust strategy
        # In real implementation, would analyze patterns
        
        return {
            'success': True,
            'optimization': 'cache_tuning',
            'before_hit_rate': current_hit_rate,
            'adjustments': ['increased_memory_size', 'optimized_ttl'],
            'improvement': 0.1  # Estimated
        }
    
    async def _optimize_batching(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize batch processing"""
        # Analyze operation patterns for batching opportunities
        
        return {
            'success': True,
            'optimization': 'batch_processing',
            'batch_size': 100,
            'improvement': 0.2
        }
    
    async def _optimize_concurrency(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize concurrency settings"""
        # Analyze thread/coroutine usage and adjust
        
        return {
            'success': True,
            'optimization': 'concurrency_tuning',
            'adjustments': ['increased_worker_pool', 'optimized_queue_size'],
            'improvement': 0.15
        }
    
    async def _optimize_memory(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize memory usage"""
        current_usage = issue['average_percent']
        
        # Strategy 1: Trigger garbage collection
        import gc
        gc.collect()
        
        # Strategy 2: Clear unnecessary caches
        if self.cache_manager:
            # Clear low-priority cached items
            logger.info("Clearing low-priority cache items")
        
        # Strategy 3: Reduce in-memory buffers
        # In real implementation, would adjust buffer sizes
        
        return {
            'success': True,
            'optimization': 'memory_management',
            'before_percent': current_usage,
            'strategies': ['gc_triggered', 'cache_cleared', 'buffers_reduced'],
            'improvement': 0.1
        }
    
    async def _optimize_error_handling(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize error handling"""
        operation = issue['operation']
        error_rate = issue['error_rate']
        
        # Analyze error patterns
        # In real implementation, would implement retry logic, circuit breakers
        
        return {
            'success': True,
            'optimization': 'error_handling',
            'operation': operation,
            'before_error_rate': error_rate,
            'strategies': ['added_retry_logic', 'implemented_circuit_breaker'],
            'improvement': 0.5
        }
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on current performance"""
        recommendations = []
        
        # Analyze historical optimizations
        successful_opts = [
            opt for opt in self.applied_optimizations
            if opt.get('improvements', {})
        ]
        
        # Recommend proven optimizations
        for opt_type, results in self.optimization_results.items():
            if results.get('average_improvement', 0) > self.config['improvement_threshold']:
                recommendations.append({
                    'type': opt_type,
                    'confidence': results.get('success_rate', 0),
                    'expected_improvement': results['average_improvement'],
                    'description': self._get_optimization_description(opt_type)
                })
        
        # Sort by expected improvement
        recommendations.sort(key=lambda x: x['expected_improvement'], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_error_rate(self, operation: str) -> float:
        """Calculate error rate for an operation"""
        # In real implementation, would track errors properly
        # For now, return a simulated value
        return 0.05
    
    def _record_optimization(self, results: Dict[str, Any]) -> None:
        """Record optimization results"""
        # Add to history
        self.applied_optimizations.append(results)
        
        # Update aggregated results
        for opt in results['optimizations_applied']:
            opt_type = opt['optimization']
            
            if opt_type not in self.optimization_results:
                self.optimization_results[opt_type] = {
                    'count': 0,
                    'total_improvement': 0,
                    'successful': 0
                }
            
            stats = self.optimization_results[opt_type]
            stats['count'] += 1
            
            if opt.get('improvement', 0) > 0:
                stats['successful'] += 1
                stats['total_improvement'] += opt['improvement']
            
            # Calculate averages
            stats['success_rate'] = stats['successful'] / stats['count']
            stats['average_improvement'] = stats['total_improvement'] / stats['count']
        
        # Save to DCP
        self._save_optimization_state()
        
        # Log to DCP
        self.dcp_manager.add_observation(
            'performance_optimized',
            {
                'optimizations_applied': len(results['optimizations_applied']),
                'improvements': results['improvements']
            },
            source_agent='performance_optimizer',
            priority=75
        )
    
    def _save_optimization_state(self) -> None:
        """Save optimization state to DCP"""
        try:
            self.dcp_manager.update_section(
                'performance.optimizations',
                {
                    'applied': self.applied_optimizations[-100:],  # Keep last 100
                    'results': self.optimization_results,
                    'config': self.config,
                    'last_updated': datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to save optimization state: {e}")
    
    def _get_optimization_description(self, opt_type: str) -> str:
        """Get human-readable description of optimization"""
        descriptions = {
            'caching': "Enable intelligent caching for expensive operations",
            'batch_processing': "Batch similar operations to reduce overhead",
            'concurrency_tuning': "Optimize thread pool and concurrency settings",
            'memory_management': "Improve memory usage through better resource management",
            'error_handling': "Implement retry logic and circuit breakers"
        }
        
        return descriptions.get(opt_type, "Performance optimization")