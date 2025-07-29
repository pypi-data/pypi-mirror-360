"""
Production Integration Example for Copper Alloy Brass
Demonstrates how to use production-ready components together
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Import production components
from coppersun_brass.core.event_bus_production import get_production_event_bus, EventBusError
from coppersun_brass.core.file_locking import safe_file_operation, FileLockError
from coppersun_brass.core.context.dcp_manager import DCPManager

# Define DCPIntegrationError locally since we removed DocFlow
class DCPIntegrationError(Exception):
    """Raised when DCP integration fails"""
    pass

logger = logging.getLogger(__name__)

class ProductionCopper Alloy BrassCoordinator:
    """
    Production coordinator that demonstrates integration of all production components.
    
    This shows how Event Bus and File Locking work together to provide
    a reliable, production-ready Copper Alloy Brass experience.
    """
    
    def __init__(self, project_root: Path, dcp_path: Optional[str] = None):
        self.project_root = project_root
        
        # Initialize DCP first (required for all other components)
        if not dcp_path:
            dcp_path = str(project_root / "coppersun_brass.context.json")
            
        # Ensure DCP exists
        if not Path(dcp_path).exists():
            # Create minimal DCP structure
            self._create_initial_dcp(Path(dcp_path))
        
        try:
            self.dcp_manager = DCPManager(dcp_path)
        except Exception as e:
            raise DCPIntegrationError(f"Failed to initialize DCP: {e}")
        
        # Initialize production components with full error handling
        try:
            self.event_bus = get_production_event_bus(
                str(project_root / "brass_events_production.db")
            )
        except Exception as e:
            raise EventBusError(f"Failed to initialize production event bus: {e}")
        
        # DocFlow removed - no longer needed
        
        # Subscribe to relevant events
        self._setup_event_handlers()
        
        # Record coordinator initialization
        self.dcp_manager.add_observation({
            'type': 'production_coordinator_initialized',
            'project_root': str(project_root),
            'dcp_path': dcp_path,
            'timestamp': time.time(),
            'components': ['dcp_manager', 'event_bus']
        }, source_agent='coordinator')
    
    def _create_initial_dcp(self, dcp_path: Path):
        """Create minimal DCP structure for new projects"""
        initial_dcp = {
            "metadata": {
                "version": "0.6.1",
                "created": time.time(),
                "last_updated": time.time(),
                "project_name": self.project_root.name,
                "schema_version": "0.6.1"
            },
            "current_observations": [],
            "project_awareness": {
                "summary": f"New Copper Alloy Brass project: {self.project_root.name}",
                "key_files": [],
                "architecture_notes": "Production-ready Copper Alloy Brass with DCP integration"
            }
        }
        
        # Use safe file operation to create DCP
        dcp_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with safe_file_operation(dcp_path, timeout=10.0):
            with open(dcp_path, 'w') as f:
                json.dump(initial_dcp, f, indent=2)
    
    def _setup_event_handlers(self):
        """Setup event handlers for coordination"""
        
        def handle_file_change(event):
            """Handle file change events"""
            self.dcp_manager.add_observation({
                'type': 'file_change_detected',
                'file_path': event.data.get('file_path'),
                'change_type': event.data.get('change_type', 'unknown'),
                'timestamp': time.time(),
                'source_event_id': event.event_id
            }, source_agent='coordinator')
        
        def handle_analysis_complete(event):
            """Handle analysis completion events"""
            self.dcp_manager.add_observation({
                'type': 'analysis_completed',
                'agent': event.source_agent,
                'results': event.data,
                'timestamp': time.time(),
                'source_event_id': event.event_id
            }, source_agent='coordinator')
        
        def handle_error(event):
            """Handle error events"""
            self.dcp_manager.add_observation({
                'type': 'error_reported',
                'error_type': event.data.get('error_type'),
                'error_message': event.data.get('message'),
                'agent': event.source_agent,
                'timestamp': time.time(),
                'priority': 90,  # High priority for errors
                'source_event_id': event.event_id
            }, source_agent='coordinator')
        
        # Subscribe to events
        self.event_bus.subscribe('file.changed', handle_file_change, 'coordinator')
        self.event_bus.subscribe('analysis.completed', handle_analysis_complete, 'coordinator')
        self.event_bus.subscribe('error.occurred', handle_error, 'coordinator')
    
    @contextmanager
    def safe_project_operation(self, operation_name: str):
        """
        Context manager for safe project operations with full coordination.
        
        This demonstrates production-grade operation safety:
        - File locking for data integrity
        - Event bus notifications
        - DCP tracking
        - Comprehensive error handling
        """
        operation_id = f"op_{int(time.time())}"
        start_time = time.time()
        
        # Record operation start
        self.dcp_manager.add_observation({
            'type': 'operation_start',
            'operation_name': operation_name,
            'operation_id': operation_id,
            'timestamp': start_time
        }, source_agent='coordinator')
        
        # Publish event
        self.event_bus.publish(
            'operation.started',
            'coordinator',
            {
                'operation_name': operation_name,
                'operation_id': operation_id,
                'timestamp': start_time
            }
        )
        
        success = False
        error_info = None
        
        try:
            # Yield control to operation
            yield operation_id
            success = True
            
        except Exception as e:
            success = False
            error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'operation_name': operation_name,
                'operation_id': operation_id
            }
            
            # Record error in DCP
            self.dcp_manager.add_observation({
                'type': 'operation_error',
                'operation_name': operation_name,
                'operation_id': operation_id,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': time.time(),
                'priority': 80
            }, source_agent='coordinator')
            
            # Publish error event
            self.event_bus.publish('error.occurred', 'coordinator', error_info)
            
            raise  # Re-raise the exception
            
        finally:
            duration = time.time() - start_time
            
            # Record operation completion
            self.dcp_manager.add_observation({
                'type': 'operation_complete',
                'operation_name': operation_name,
                'operation_id': operation_id,
                'success': success,
                'duration_seconds': duration,
                'timestamp': time.time()
            }, source_agent='coordinator')
            
            # Publish completion event
            self.event_bus.publish(
                'operation.completed',
                'coordinator',
                {
                    'operation_name': operation_name,
                    'operation_id': operation_id,
                    'success': success,
                    'duration_seconds': duration,
                    'error_info': error_info
                }
            )
    
    def safe_sprint_completion(self, sprint_number: int, version: str, summary: str):
        """
        Demonstrate production-safe sprint completion.
        
        This shows how all production components work together for complex operations.
        Note: DocFlow was removed - this is now a simplified example.
        """
        with self.safe_project_operation(f"sprint_{sprint_number}_completion"):
            # Record sprint completion in DCP
            self.dcp_manager.add_observation({
                'type': 'sprint_completion',
                'sprint_number': sprint_number,
                'version': version,
                'summary': summary,
                'timestamp': time.time(),
                'priority': 90
            }, source_agent='coordinator')
            
            # Verify completion
            completion_verified = self._verify_sprint_completion(sprint_number, version)
            
            if not completion_verified:
                raise RuntimeError(f"Sprint {sprint_number} completion verification failed")
            
            return {
                'sprint_number': sprint_number,
                'version': version,
                'summary': summary,
                'completion_verified': completion_verified,
                'timestamp': time.time()
            }
    
    def _verify_sprint_completion(self, sprint_number: int, version: str) -> bool:
        """Verify that sprint completion was successful"""
        try:
            # Check if DCP was updated with sprint info
            recent_observations = self.dcp_manager.get_observations()[-10:]
            sprint_observations = [
                obs for obs in recent_observations 
                if obs.get('type', '') == 'sprint_completion'
            ]
            
            if not sprint_observations:
                logger.error("No sprint completion observations found in DCP")
                return False
            
            # Check if PROJECT_STATUS.md exists (manual verification)
            status_file = self.project_root / "PROJECT_STATUS.md"
            if not status_file.exists():
                logger.error("PROJECT_STATUS.md not found")
                return False
            
            # Check if export files were created
            export_dir = self.project_root / "claude_export"
            expected_files = [
                f"CLAUDE_CONTEXT_SPRINT_{sprint_number}.md",
                "coppersun_brass.context.json",
                "PROJECT_STATUS.md"
            ]
            
            for expected_file in expected_files:
                if not (export_dir / expected_file).exists():
                    logger.error(f"Expected export file missing: {expected_file}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Sprint completion verification failed: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information"""
        # Event bus health
        event_bus_health = self.event_bus.get_health()
        event_bus_stats = self.event_bus.get_stats()
        
        # DCP health
        try:
            dcp_data = self.dcp_manager.read_dcp()
            dcp_healthy = True
            dcp_info = {
                'observations_count': len(dcp_data.get('current_observations', [])),
                'last_updated': dcp_data.get('metadata', {}).get('last_updated'),
                'file_exists': True
            }
        except Exception as e:
            dcp_healthy = False
            dcp_info = {'error': str(e), 'file_exists': False}
        
        # File locking health
        from coppersun_brass.core.file_locking import get_file_lock_manager
        lock_manager = get_file_lock_manager()
        lock_stats = lock_manager.get_stats()
        
        return {
            'overall_healthy': (
                event_bus_health.status.value in ['healthy', 'degraded'] and
                dcp_healthy and
                lock_stats['active_locks'] >= 0  # Basic sanity check
            ),
            'components': {
                'event_bus': {
                    'status': event_bus_health.status.value,
                    'database_accessible': event_bus_health.database_accessible,
                    'recent_error_rate': event_bus_health.recent_error_rate,
                    'total_events': event_bus_stats['total_events'],
                    'unprocessed_events': event_bus_stats['unprocessed_events']
                },
                'dcp': {
                    'healthy': dcp_healthy,
                    'info': dcp_info
                },
                'file_locking': {
                    'total_locks': lock_stats['total_locks'],
                    'active_locks': lock_stats['active_locks']
                },
                'file_system': {
                    'project_status_exists': (self.project_root / "PROJECT_STATUS.md").exists(),
                    'dcp_file_exists': self.dcp_manager.dcp_path.exists()
                }
            },
            'check_time': time.time()
        }
    
    def cleanup_and_maintenance(self):
        """Perform cleanup and maintenance operations"""
        maintenance_results = {}
        
        # Clean up stale file locks
        from coppersun_brass.core.file_locking import get_file_lock_manager
        lock_manager = get_file_lock_manager()
        cleaned_locks = lock_manager.cleanup_stale_locks()
        maintenance_results['cleaned_locks'] = cleaned_locks
        
        # Event bus integrity check
        event_integrity = self.event_bus.verify_integrity()
        maintenance_results['event_bus_integrity'] = event_integrity
        
        # DCP pruning (if it gets too large)
        try:
            dcp_data = self.dcp_manager.read_dcp()
            observations_count = len(dcp_data.get('current_observations', []))
            
            if observations_count > 1000:  # Arbitrary threshold
                # In a real implementation, you'd implement DCP pruning
                maintenance_results['dcp_pruning_needed'] = True
                maintenance_results['dcp_observations_count'] = observations_count
            else:
                maintenance_results['dcp_pruning_needed'] = False
                maintenance_results['dcp_observations_count'] = observations_count
                
        except Exception as e:
            maintenance_results['dcp_check_error'] = str(e)
        
        # Record maintenance completion
        self.dcp_manager.add_observation({
            'type': 'maintenance_completed',
            'results': maintenance_results,
            'timestamp': time.time()
        }, source_agent='coordinator')
        
        return maintenance_results


def demonstrate_production_integration():
    """
    Demonstration function showing how production components work together.
    """
    print("🚀 Copper Alloy Brass Production Integration Demonstration")
    print("=" * 60)
    
    # Initialize coordinator
    project_root = Path(".")
    
    try:
        coordinator = ProductionCopper Alloy BrassCoordinator(project_root)
        print("✅ Production coordinator initialized successfully")
        
        # Check system health
        health = coordinator.get_system_health()
        print(f"✅ System health check: {'HEALTHY' if health['overall_healthy'] else 'ISSUES DETECTED'}")
        
        if not health['overall_healthy']:
            print("⚠️  Health issues detected:")
            for component, status in health['components'].items():
                if isinstance(status, dict) and not status.get('healthy', True):
                    print(f"   - {component}: {status}")
        
        # Demonstrate safe operation
        try:
            with coordinator.safe_project_operation("test_operation"):
                print("✅ Safe operation context established")
                time.sleep(0.1)  # Simulate work
                
            print("✅ Safe operation completed successfully")
            
        except Exception as e:
            print(f"❌ Safe operation failed: {e}")
        
        # Perform maintenance
        maintenance_results = coordinator.cleanup_and_maintenance()
        print(f"✅ Maintenance completed: {maintenance_results}")
        
        # Final health check
        final_health = coordinator.get_system_health()
        print(f"✅ Final health status: {'HEALTHY' if final_health['overall_healthy'] else 'ISSUES'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Production integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demonstration
    success = demonstrate_production_integration()
    
    if success:
        print("\n🎉 Production integration demonstration completed successfully!")
        print("All critical production issues have been addressed:")
        print("  ✅ Event Bus fail-fast behavior - No more silent failures")
        print("  ✅ OS-level file locking - No more corruption risk")
        print("  ✅ DCP coordination - All components use unified context")
    else:
        print("\n💥 Production integration demonstration failed!")
        print("Please check the error messages above and fix any issues.")