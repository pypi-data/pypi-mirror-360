# coppersun_brass/agents/strategist/orchestration_engine.py
"""
DCP Orchestration Engine for Copper Alloy Brass Strategist
Coordinates DCP updates, observation processing, and agent task routing
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class OrchestrationEngine:
    """
    Central orchestration engine that coordinates all DCP operations
    """
    
    def __init__(self, dcp_manager, priority_engine, duplicate_detector, 
                 best_practices_engine=None, gap_detector=None):
        self.dcp_manager = dcp_manager
        self.priority_engine = priority_engine
        self.duplicate_detector = duplicate_detector
        self.best_practices_engine = best_practices_engine
        self.gap_detector = gap_detector
        
        # Orchestration state
        self.last_orchestration_result = None
        self.orchestration_count = 0
        
        logger.debug("Orchestration engine initialized")
    
    async def orchestrate(self, current_dcp: Dict) -> Dict[str, Any]:
        """
        Main orchestration method - coordinates all DCP operations
        
        Args:
            current_dcp: Current DCP state
            
        Returns:
            Orchestration result with metrics and actions taken
        """
        self.orchestration_count += 1
        
        logger.info(f"Starting orchestration cycle #{self.orchestration_count}")
        
        try:
            result = {
                'cycle_id': self.orchestration_count,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'success',
                'actions_taken': [],
                'observations_processed': 0,
                'priorities_updated': 0,
                'duplicates_found': 0,
                'tasks_routed': 0,
                'dcp_updated': False,
                'errors': []
            }
            
            # Phase 1: Load and validate current observations
            observations = current_dcp.get('current_observations', [])
            logger.debug(f"Processing {len(observations)} observations")
            
            if not observations:
                result['status'] = 'no_observations'
                return result
            
            # Phase 2: Detect and handle duplicates
            duplicate_groups = self.duplicate_detector.find_duplicates(observations)
            if duplicate_groups:
                observations = self._handle_duplicates(observations, duplicate_groups, result)
                result['duplicates_found'] = sum(len(dups) for dups in duplicate_groups.values())
                result['actions_taken'].append('duplicate_detection')
            
            # Phase 3: Calculate priorities
            prioritized_observations = self._prioritize_all_observations(observations, result)
            result['observations_processed'] = len(prioritized_observations)
            result['actions_taken'].append('priority_calculation')
            
            # Phase 4: Update strategist metadata
            strategist_metadata = self._generate_strategist_metadata(prioritized_observations, duplicate_groups)
            
            # Phase 5: Route tasks to agents
            task_routing = self._route_tasks(prioritized_observations, result)
            result['tasks_routed'] = sum(len(tasks) for tasks in task_routing.values())
            if result['tasks_routed'] > 0:
                result['actions_taken'].append('task_routing')
            
            # Phase 6: Update DCP with orchestrated data
            if self._should_update_dcp(current_dcp, prioritized_observations, strategist_metadata):
                updated_dcp = self._build_updated_dcp(
                    current_dcp, 
                    prioritized_observations, 
                    strategist_metadata,
                    task_routing
                )
                
                self._save_updated_dcp(updated_dcp, result)
                result['dcp_updated'] = True
                result['actions_taken'].append('dcp_update')
            
            # Phase 7: Generate recommendations
            recommendations = self._generate_recommendations(prioritized_observations, task_routing)
            if recommendations:
                result['recommendations'] = recommendations
                result['actions_taken'].append('recommendation_generation')
            
            self.last_orchestration_result = result
            
            logger.info(f"Orchestration cycle #{self.orchestration_count} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Orchestration cycle #{self.orchestration_count} failed: {e}"
            logger.error(error_msg, exc_info=True)
            
            return {
                'cycle_id': self.orchestration_count,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'error',
                'error': str(e),
                'actions_taken': [],
                'observations_processed': 0
            }
    
    def _handle_duplicates(self, observations: List[Dict], duplicate_groups: Dict[str, List[str]], result: Dict) -> List[Dict]:
        """Handle duplicate observations by merging or removing"""
        duplicate_ids = set()
        for canonical_id, dups in duplicate_groups.items():
            duplicate_ids.update(dups)
        
        # Remove duplicates, keep canonical observations
        filtered_observations = []
        for obs in observations:
            obs_id = obs.get('id', '')
            
            if obs_id not in duplicate_ids:
                # Mark if this is a canonical observation
                if obs_id in duplicate_groups:
                    obs['duplicate_count'] = len(duplicate_groups[obs_id])
                    obs['is_canonical'] = True
                
                filtered_observations.append(obs)
        
        removed_count = len(observations) - len(filtered_observations)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate observations")
        
        return filtered_observations
    
    def _prioritize_all_observations(self, observations: List[Dict], result: Dict) -> List[Dict]:
        """Calculate priorities for all observations"""
        prioritized = []
        priority_updates = 0
        
        for obs in observations:
            try:
                # Calculate new priority
                calculated_priority = self.priority_engine.calculate_priority(obs)
                original_priority = obs.get('priority', 50)
                
                # Update if significantly different
                if abs(calculated_priority - original_priority) >= 5:
                    obs['priority'] = calculated_priority
                    obs['priority_updated_by'] = 'strategist'
                    obs['priority_updated_at'] = datetime.now(timezone.utc).isoformat()
                    priority_updates += 1
                
                # Add priority rationale
                obs['priority_rationale'] = self.priority_engine.get_rationale(obs)
                
                # Mark as processed by strategist
                obs['strategist_processed'] = True
                obs['strategist_processed_at'] = datetime.now(timezone.utc).isoformat()
                
                prioritized.append(obs)
                
            except Exception as e:
                logger.warning(f"Failed to prioritize observation {obs.get('id', 'unknown')}: {e}")
                # Keep original observation
                prioritized.append(obs)
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x.get('priority', 50), reverse=True)
        
        result['priorities_updated'] = priority_updates
        logger.debug(f"Updated priorities for {priority_updates} observations")
        
        return prioritized
    
    def _generate_strategist_metadata(self, observations: List[Dict], duplicate_groups: Dict) -> Dict:
        """Generate metadata about strategist analysis"""
        priority_dist = self.priority_engine.get_priority_distribution(observations)
        duplicate_stats = self.duplicate_detector.get_duplicate_stats(duplicate_groups)
        
        # Analyze observation types
        type_counts = {}
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        # Identify top priorities
        top_priorities = [
            {
                'id': obs.get('id'),
                'type': obs.get('type'),
                'priority': obs.get('priority'),
                'summary': obs.get('summary', '')[:100] + ('...' if len(obs.get('summary', '')) > 100 else '')
            }
            for obs in observations[:5]  # Top 5
        ]
        
        return {
            'orchestration_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_observations': len(observations),
            'priority_distribution': priority_dist,
            'duplicate_statistics': duplicate_stats,
            'type_distribution': type_counts,
            'top_priorities': top_priorities,
            'orchestration_cycle': self.orchestration_count
        }
    
    def _route_tasks(self, observations: List[Dict], result: Dict) -> Dict[str, List[Dict]]:
        """Route high-priority observations to appropriate agents"""
        routing = {
            'claude': [],
            'scout': [],
            'watch': [],
            'human': []
        }
        
        # Only route high-priority items to avoid spam
        high_priority_obs = [obs for obs in observations if obs.get('priority', 0) >= 70]
        
        for obs in high_priority_obs:
            obs_type = obs.get('type', 'unknown')
            priority = obs.get('priority', 50)
            
            # Enhanced routing logic
            if obs_type in ['security', 'critical_bug'] or priority >= 95:
                # Critical issues go to human
                routing['human'].append(self._create_task(obs, 'critical_review'))
            
            elif obs_type in ['todo_item', 'fixme_item'] and priority >= 80:
                # High-priority TODOs go to Claude
                routing['claude'].append(self._create_task(obs, 'implement_fix'))
            
            elif obs_type in ['research_needed', 'implementation_gap'] and priority >= 75:
                # Research tasks go to Scout
                routing['scout'].append(self._create_task(obs, 'research_solution'))
            
            elif obs_type in ['performance', 'optimization'] and priority >= 80:
                # Performance issues go to Claude
                routing['claude'].append(self._create_task(obs, 'optimize_code'))
            
            elif obs_type == 'test_coverage' and priority >= 75:
                # Test coverage issues go to Claude
                routing['claude'].append(self._create_task(obs, 'write_tests'))
        
        # Log routing decisions
        for agent, tasks in routing.items():
            if tasks:
                logger.info(f"Routed {len(tasks)} tasks to {agent}")
        
        return routing
    
    def _create_task(self, observation: Dict, task_type: str) -> Dict:
        """Create a task from an observation"""
        return {
            'observation_id': observation.get('id'),
            'task_type': task_type,
            'priority': observation.get('priority', 50),
            'summary': observation.get('summary'),
            'context': {
                'type': observation.get('type'),
                'location': self._extract_location_from_summary(observation.get('summary', '')),
                'created_at': observation.get('created_at')
            },
            'assigned_at': datetime.now(timezone.utc).isoformat(),
            'assigned_by': 'strategist'
        }
    
    def _extract_location_from_summary(self, summary: str) -> Optional[str]:
        """Extract location information from observation summary"""
        import re
        
        patterns = [
            r'\[Location: ([^\]]+)\]',
            r'Location: ([^\,\|]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, summary)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _should_update_dcp(self, current_dcp: Dict, prioritized_observations: List[Dict], metadata: Dict) -> bool:
        """Determine if DCP should be updated"""
        # Always update if we have new prioritized observations
        if any(obs.get('priority_updated_by') == 'strategist' for obs in prioritized_observations):
            return True
        
        # Update if we processed new observations
        unprocessed_count = len([obs for obs in prioritized_observations if not obs.get('strategist_processed')])
        if unprocessed_count > 0:
            return True
        
        # Update if metadata is significantly different
        current_metadata = current_dcp.get('strategist_metadata', {})
        if current_metadata.get('total_observations', 0) != metadata['total_observations']:
            return True
        
        return False
    
    def _build_updated_dcp(self, current_dcp: Dict, observations: List[Dict], metadata: Dict, task_routing: Dict) -> Dict:
        """Build updated DCP with orchestrated data"""
        updated_dcp = current_dcp.copy()
        
        # Update observations
        updated_dcp['current_observations'] = observations
        
        # Add strategist metadata
        updated_dcp['strategist_metadata'] = metadata
        
        # Add task routing information
        if any(tasks for tasks in task_routing.values()):
            updated_dcp['task_routing'] = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'routing': task_routing
            }
        
        # Update meta information
        meta = updated_dcp.get('meta', {})
        meta['last_orchestration'] = datetime.now(timezone.utc).isoformat()
        meta['orchestration_cycle'] = self.orchestration_count
        updated_dcp['meta'] = meta
        
        return updated_dcp
    
    def _save_updated_dcp(self, updated_dcp: Dict, result: Dict):
        """Save updated DCP with error handling"""
        try:
            self.dcp_manager.write_dcp(updated_dcp)
            logger.debug("DCP updated successfully")
        except Exception as e:
            error_msg = f"Failed to save updated DCP: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            raise
    
    def _generate_recommendations(self, observations: List[Dict], task_routing: Dict) -> List[Dict]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # High-priority issues recommendation
        critical_obs = [obs for obs in observations if obs.get('priority', 0) >= 90]
        if critical_obs:
            recommendations.append({
                'type': 'immediate_attention',
                'priority': 95,
                'summary': f"{len(critical_obs)} critical issues require immediate attention",
                'details': [obs.get('summary', '')[:100] for obs in critical_obs[:3]],
                'recommended_action': 'Review and address critical observations'
            })
        
        # Test coverage recommendation
        test_obs = [obs for obs in observations if obs.get('type') == 'test_coverage']
        if len(test_obs) >= 3:
            recommendations.append({
                'type': 'test_coverage',
                'priority': 70,
                'summary': f"Multiple test coverage gaps detected ({len(test_obs)} issues)",
                'recommended_action': 'Implement comprehensive test suite'
            })
        
        # Security recommendation
        security_obs = [obs for obs in observations if obs.get('type') == 'security']
        if security_obs:
            recommendations.append({
                'type': 'security_review',
                'priority': 85,
                'summary': f"{len(security_obs)} security issues identified",
                'recommended_action': 'Conduct security audit and remediation'
            })
        
        # Use Gap Detector to find gaps
        if self.gap_detector:
            try:
                # Prepare project context from observations
                project_context = {
                    'observations': observations,
                    'type_distribution': self._get_type_distribution(observations),
                    'priority_distribution': self._get_priority_distribution(observations)
                }
                
                # Detect gaps
                gaps = self.gap_detector.detect_gaps(project_context)
                
                # Convert high-priority gaps to recommendations
                for gap in gaps:
                    if gap.confidence > 0.7 and gap.priority >= 70:
                        recommendations.append({
                            'type': 'gap_detection',
                            'priority': gap.priority,
                            'summary': gap.description,
                            'category': gap.category,
                            'risk_level': gap.risk_level,
                            'recommended_action': gap.recommended_actions[0] if gap.recommended_actions else 'Address identified gap',
                            'estimated_effort': gap.effort_estimate
                        })
                        
            except Exception as e:
                logger.warning(f"Gap detection failed: {e}")
        
        # Use Best Practices Engine to find violations
        if self.best_practices_engine:
            try:
                # Get relevant observations for best practices analysis
                code_obs = [obs for obs in observations if obs.get('type') in ['code_analysis', 'file_analysis', 'todo_item']]
                
                if code_obs:
                    # Generate best practices recommendations
                    bp_recommendations = self.best_practices_engine.generate_recommendations(
                        observations=code_obs,
                        limit=5  # Top 5 recommendations
                    )
                    
                    # Convert to orchestration recommendations
                    for bp_rec in bp_recommendations:
                        recommendations.append({
                            'type': 'best_practice',
                            'priority': bp_rec.get('priority', 60),
                            'summary': bp_rec.get('title', 'Best practice recommendation'),
                            'description': bp_rec.get('description', ''),
                            'category': bp_rec.get('category', 'general'),
                            'recommended_action': bp_rec.get('recommendation', ''),
                            'references': bp_rec.get('references', [])
                        })
                        
            except Exception as e:
                logger.warning(f"Best practices analysis failed: {e}")
        
        return recommendations
    
    def _get_type_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of observation types"""
        distribution = {}
        for obs in observations:
            obs_type = obs.get('type', 'unknown')
            distribution[obs_type] = distribution.get(obs_type, 0) + 1
        return distribution
    
    def _get_priority_distribution(self, observations: List[Dict]) -> Dict[str, int]:
        """Get distribution of priorities"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        for obs in observations:
            priority = obs.get('priority', 50)
            if priority >= 80:
                distribution['high'] += 1
            elif priority >= 50:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        return distribution
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestration engine status"""
        return {
            'orchestration_count': self.orchestration_count,
            'last_result': self.last_orchestration_result,
            'components': {
                'dcp_manager': 'connected',
                'priority_engine': 'connected',
                'duplicate_detector': 'connected',
                'best_practices_engine': 'connected' if self.best_practices_engine else 'not_configured',
                'gap_detector': 'connected' if self.gap_detector else 'not_configured'
            }
        }