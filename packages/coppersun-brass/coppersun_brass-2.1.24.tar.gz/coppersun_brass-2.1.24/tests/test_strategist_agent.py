# tests/test_strategist_agent.py
"""
Comprehensive test suite for Copper Alloy Brass Strategist Agent
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from coppersun_brass.agents.strategist.strategist_agent import StrategistAgent
from coppersun_brass.agents.strategist.priority_engine import PriorityEngine
from coppersun_brass.agents.strategist.duplicate_detector import DuplicateDetector
from coppersun_brass.agents.strategist.orchestration_engine import OrchestrationEngine
from coppersun_brass.agents.strategist.config import StrategistConfig

class TestPriorityEngine:
    """Test suite for PriorityEngine"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = PriorityEngine()
    
    def test_calculate_priority_security(self):
        """Test priority calculation for security observations"""
        observation = {
            'id': 'test-1',
            'type': 'security',
            'summary': 'Critical SQL injection vulnerability found',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        priority = self.engine.calculate_priority(observation)
        
        # Security issues should get high base score (95) plus urgency multiplier
        assert priority >= 95
        assert priority <= 100
    
    def test_calculate_priority_with_time_decay(self):
        """Test priority calculation with time decay"""
        # Old observation (1 week ago)
        old_time = datetime.now(timezone.utc) - timedelta(hours=168)
        old_observation = {
            'id': 'test-old',
            'type': 'bug',
            'summary': 'Some bug',
            'created_at': old_time.isoformat()
        }
        
        # New observation (1 hour ago)
        new_time = datetime.now(timezone.utc) - timedelta(hours=1)
        new_observation = {
            'id': 'test-new',
            'type': 'bug',
            'summary': 'Some bug',
            'created_at': new_time.isoformat()
        }
        
        old_priority = self.engine.calculate_priority(old_observation)
        new_priority = self.engine.calculate_priority(new_observation)
        
        # New observation should have higher priority due to less time decay
        assert new_priority > old_priority
    
    def test_urgency_multipliers(self):
        """Test urgency keyword multipliers"""
        base_obs = {
            'id': 'test-base',
            'type': 'bug',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Test different urgency keywords
        test_cases = [
            ('Normal bug found in the authentication system', 70),  # Base score for bug
            ('Critical bug found in the authentication system', 91),  # Base score * critical multiplier (1.3)
            ('Urgent bug blocking deployment in production environment', 84)  # Base score * urgent multiplier (1.2)
        ]
        
        for summary, expected_min_priority in test_cases:
            obs = {**base_obs, 'summary': summary}
            priority = self.engine.calculate_priority(obs)
            assert priority >= expected_min_priority
    
    def test_get_rationale(self):
        """Test priority rationale generation"""
        observation = {
            'id': 'test-rationale',
            'type': 'security',
            'summary': 'Critical security issue in core module',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        priority = self.engine.calculate_priority(observation)
        rationale = self.engine.get_rationale(observation)
        
        assert 'security' in rationale.lower()
        assert 'critical' in rationale.lower() or 'urgency' in rationale.lower()
        assert str(priority) in rationale or 'Final:' in rationale
    
    def test_priority_distribution(self):
        """Test priority distribution analysis"""
        observations = [
            {'id': '1', 'type': 'security', 'priority': 95},
            {'id': '2', 'type': 'bug', 'priority': 75},
            {'id': '3', 'type': 'todo_item', 'priority': 50},
            {'id': '4', 'type': 'documentation', 'priority': 30}
        ]
        
        distribution = self.engine.get_priority_distribution(observations)
        
        assert distribution['critical'] == 1  # priority >= 90
        assert distribution['high'] == 1      # priority 70-89
        assert distribution['medium'] == 1    # priority 40-69
        assert distribution['low'] == 1       # priority 0-39


class TestDuplicateDetector:
    """Test suite for DuplicateDetector"""
    
    def setup_method(self):
        """Setup for each test"""
        self.detector = DuplicateDetector()
    
    def test_exact_duplicate_detection(self):
        """Test detection of exact duplicates"""
        observations = [
            {
                'id': 'obs-1',
                'type': 'bug',
                'summary': 'Missing error handling in file upload',
                'created_at': '2025-01-01T10:00:00Z'
            },
            {
                'id': 'obs-2',
                'type': 'bug',
                'summary': 'Missing error handling in file upload',
                'created_at': '2025-01-01T10:05:00Z'
            },
            {
                'id': 'obs-3',
                'type': 'security',
                'summary': 'SQL injection vulnerability',
                'created_at': '2025-01-01T10:10:00Z'
            }
        ]
        
        duplicates = self.detector.find_duplicates(observations)
        
        # Should find obs-1 and obs-2 as duplicates
        assert len(duplicates) == 1
        canonical_id = list(duplicates.keys())[0]
        assert canonical_id in ['obs-1', 'obs-2']
        assert len(duplicates[canonical_id]) == 1
    
    def test_similar_content_detection(self):
        """Test detection of similar but not identical content"""
        # Create detector with lower threshold for semantic similarity
        detector = DuplicateDetector({'content_threshold': 0.7})
        
        observations = [
            {
                'id': 'obs-1',
                'type': 'test_coverage',
                'summary': 'Missing test framework setup (pytest/unittest)',
                'created_at': '2025-01-01T10:00:00Z'
            },
            {
                'id': 'obs-2',
                'type': 'test_coverage',
                'summary': 'Test framework implementation missing (pytest/unittest)',
                'created_at': '2025-01-01T10:05:00Z'
            }
        ]
        
        duplicates = detector.find_duplicates(observations)
        
        # Should detect similar content about test framework
        assert len(duplicates) == 1
    
    def test_temporal_grouping(self):
        """Test temporal proximity in duplicate detection"""
        base_time = datetime.now(timezone.utc)
        
        # Create detector with higher threshold to ensure temporal proximity matters
        detector = DuplicateDetector({'content_threshold': 0.9})
        
        observations = [
            {
                'id': 'obs-1',
                'type': 'bug',
                'summary': 'Database connection error',
                'created_at': base_time.isoformat()
            },
            {
                'id': 'obs-2',
                'type': 'bug',
                'summary': 'Database connection error',
                'created_at': (base_time + timedelta(minutes=10)).isoformat()
            },
            {
                'id': 'obs-3',
                'type': 'bug',
                'summary': 'Database connection error',
                'created_at': (base_time + timedelta(hours=25)).isoformat()  # Outside time window
            }
        ]
        
        duplicates = detector.find_duplicates(observations)
        
        # obs-1 and obs-2 should be grouped (within time window)
        # obs-3 should not be grouped (outside time window)
        assert len(duplicates) == 1
        canonical_id = list(duplicates.keys())[0]
        assert len(duplicates[canonical_id]) == 1
    
    def test_location_similarity(self):
        """Test location-based duplicate detection"""
        # Create detector with lower threshold for location-based similarity
        detector = DuplicateDetector({'content_threshold': 0.8})
        
        observations = [
            {
                'id': 'obs-1',
                'type': 'bug',
                'summary': 'Error in file processing [Location: utils.py:42]',
                'created_at': '2025-01-01T10:00:00Z'
            },
            {
                'id': 'obs-2',
                'type': 'bug',
                'summary': 'Bug found in file handling [Location: utils.py:45]',
                'created_at': '2025-01-01T10:05:00Z'
            }
        ]
        
        duplicates = detector.find_duplicates(observations)
        
        # Should detect as similar due to same file location
        assert len(duplicates) == 1
    
    def test_no_duplicates(self):
        """Test when no duplicates exist"""
        observations = [
            {
                'id': 'obs-1',
                'type': 'security',
                'summary': 'SQL injection vulnerability',
                'created_at': '2025-01-01T10:00:00Z'
            },
            {
                'id': 'obs-2',
                'type': 'performance',
                'summary': 'Slow database queries',
                'created_at': '2025-01-01T10:05:00Z'
            },
            {
                'id': 'obs-3',
                'type': 'documentation',
                'summary': 'Missing API documentation',
                'created_at': '2025-01-01T10:10:00Z'
            }
        ]
        
        duplicates = self.detector.find_duplicates(observations)
        
        assert len(duplicates) == 0


class TestOrchestrationEngine:
    """Test suite for OrchestrationEngine"""
    
    def setup_method(self):
        """Setup for each test"""
        self.mock_dcp_manager = Mock()
        self.priority_engine = PriorityEngine()
        self.duplicate_detector = DuplicateDetector()
        
        self.engine = OrchestrationEngine(
            self.mock_dcp_manager,
            self.priority_engine,
            self.duplicate_detector
        )
    
    @pytest.mark.asyncio
    async def test_orchestrate_success(self):
        """Test successful orchestration cycle"""
        # Mock DCP data
        mock_dcp = {
            'current_observations': [
                {
                    'id': 'obs-1',
                    'type': 'security',
                    'summary': 'Critical security issue',
                    'priority': 90,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        
        # Mock successful DCP write
        self.mock_dcp_manager.write_dcp = Mock()
        
        result = await self.engine.orchestrate(mock_dcp)
        
        assert result['status'] == 'success'
        assert result['observations_processed'] == 1
        assert 'priority_calculation' in result['actions_taken']
        assert result['dcp_updated'] == True
    
    @pytest.mark.asyncio
    async def test_orchestrate_no_observations(self):
        """Test orchestration with no observations"""
        mock_dcp = {'current_observations': []}
        
        result = await self.engine.orchestrate(mock_dcp)
        
        assert result['status'] == 'no_observations'
        assert result['observations_processed'] == 0
    
    @pytest.mark.asyncio
    async def test_orchestrate_with_duplicates(self):
        """Test orchestration with duplicate detection"""
        mock_dcp = {
            'current_observations': [
                {
                    'id': 'obs-1',
                    'type': 'bug',
                    'summary': 'Database error',
                    'priority': 70,
                    'created_at': '2025-01-01T10:00:00Z'
                },
                {
                    'id': 'obs-2',
                    'type': 'bug',
                    'summary': 'Database error',
                    'priority': 70,
                    'created_at': '2025-01-01T10:05:00Z'
                }
            ]
        }
        
        self.mock_dcp_manager.write_dcp = Mock()
        
        result = await self.engine.orchestrate(mock_dcp)
        
        assert result['status'] == 'success'
        assert result['duplicates_found'] > 0
        assert 'duplicate_detection' in result['actions_taken']
    
    def test_task_routing(self):
        """Test task routing logic"""
        observations = [
            {
                'id': 'obs-1',
                'type': 'security',
                'summary': 'Critical security issue',
                'priority': 95
            },
            {
                'id': 'obs-2',
                'type': 'todo_item',
                'summary': 'Implement new feature',
                'priority': 85
            },
            {
                'id': 'obs-3',
                'type': 'test_coverage',
                'summary': 'Missing tests',
                'priority': 75
            }
        ]
        
        routing = self.engine._route_tasks(observations, {})
        
        # Security issue should go to human
        assert len(routing['human']) > 0
        
        # High-priority TODO should go to Claude
        assert len(routing['claude']) > 0
        
        # Test coverage should go to Claude
        claude_tasks = routing['claude']
        test_tasks = [task for task in claude_tasks if 'test' in task.get('summary', '').lower()]
        assert len(test_tasks) > 0


class TestStrategistAgent:
    """Integration tests for StrategistAgent"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        
        # Create mock DCP file
        dcp_content = {
            'meta': {
                'project_id': 'test-project',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'version': 'dcp-0.6'
            },
            'project_awareness': {
                'description': 'Test project for Strategist Agent',
                'last_updated': datetime.now(timezone.utc).isoformat()
            },
            'current_observations': [
                {
                    'id': 'test-obs-1',
                    'type': 'security',
                    'summary': 'Test security issue',
                    'priority': 85,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            ],
            'strategic_recommendations': []
        }
        
        dcp_file = self.project_path / 'coppersun_brass.context.json'
        with open(dcp_file, 'w') as f:
            json.dump(dcp_content, f)
    
    def test_strategist_initialization(self):
        """Test strategist agent initialization"""
        strategist = StrategistAgent(str(self.project_path))
        
        assert strategist.agent_id == 'strategist'
        assert strategist.project_path == self.project_path
        assert strategist.priority_engine is not None
        assert strategist.duplicate_detector is not None
        assert strategist.orchestration_engine is not None
    
    def test_prioritize_observations(self):
        """Test observation prioritization"""
        strategist = StrategistAgent(str(self.project_path))
        
        observations = [
            {
                'id': 'obs-1',
                'type': 'security',
                'summary': 'Critical security vulnerability',
                'priority': 50,  # Will be updated
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'obs-2',
                'type': 'documentation',
                'summary': 'Missing documentation',
                'priority': 40,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        prioritized = strategist.prioritize_observations(observations)
        
        # Security observation should be prioritized higher
        assert prioritized[0]['type'] == 'security'
        assert prioritized[0]['calculated_priority'] > prioritized[1]['calculated_priority']
        
        # Check that rationale was added
        assert 'priority_rationale' in prioritized[0]
    
    def test_get_orchestration_status(self):
        """Test orchestration status reporting"""
        strategist = StrategistAgent(str(self.project_path))
        
        status = strategist.get_orchestration_status()
        
        assert status['agent_id'] == 'strategist'
        assert 'metrics' in status
        assert 'components' in status
        assert 'dcp_status' in status
    
    @pytest.mark.asyncio
    async def test_full_orchestration_cycle(self):
        """Test complete orchestration cycle"""
        strategist = StrategistAgent(str(self.project_path))
        
        # Run orchestration
        result = await strategist.orchestrate_dcp_updates(force=True)
        
        assert result['status'] in ['success', 'no_observations']
        assert 'observations_processed' in result
        assert 'actions_taken' in result


class TestStrategistConfig:
    """Test suite for StrategistConfig"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
    
    def test_default_config(self):
        """Test default configuration loading"""
        config = StrategistConfig(str(self.project_path))
        
        assert config.get('priority.time_decay_hours') == 168
        assert config.get('duplicates.content_threshold') == 0.85
        assert config.get('orchestration.auto_orchestrate') == True
    
    def test_config_override(self):
        """Test configuration override"""
        override = {
            'priority': {
                'time_decay_hours': 72
            },
            'duplicates': {
                'content_threshold': 0.9
            }
        }
        
        config = StrategistConfig(str(self.project_path), override)
        
        assert config.get('priority.time_decay_hours') == 72
        assert config.get('duplicates.content_threshold') == 0.9
        # Other defaults should remain
        assert config.get('orchestration.auto_orchestrate') == True
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = StrategistConfig(str(self.project_path))
        
        validation = config.validate_config()
        
        assert validation['valid'] == True
        assert isinstance(validation['issues'], list)
        assert isinstance(validation['warnings'], list)
    
    def test_config_persistence(self):
        """Test configuration save and load"""
        config = StrategistConfig(str(self.project_path))
        
        # Modify configuration
        config.set('priority.time_decay_hours', 96)
        config.save_config()
        
        # Load new instance
        config2 = StrategistConfig(str(self.project_path))
        
        assert config2.get('priority.time_decay_hours') == 96


# Performance and stress tests
class TestStrategistPerformance:
    """Performance tests for Strategist Agent"""
    
    def setup_method(self):
        """Setup for performance tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
    
    def test_large_observation_set_performance(self):
        """Test performance with large number of observations"""
        import time
        
        # Create 1000 observations
        observations = []
        for i in range(1000):
            observations.append({
                'id': f'obs-{i}',
                'type': 'bug' if i % 2 == 0 else 'todo_item',
                'summary': f'Test observation {i}',
                'priority': 50 + (i % 50),
                'created_at': datetime.now(timezone.utc).isoformat()
            })
        
        strategist = StrategistAgent(str(self.project_path))
        
        # Test prioritization performance
        start_time = time.time()
        prioritized = strategist.prioritize_observations(observations)
        prioritization_time = time.time() - start_time
        
        # Should process 1000 observations in under 2 seconds
        assert prioritization_time < 2.0
        assert len(prioritized) == 1000
        
        # Test duplicate detection performance
        start_time = time.time()
        duplicates = strategist.detect_duplicates(observations)
        duplicate_time = time.time() - start_time
        
        # Should detect duplicates in under 5 seconds
        assert duplicate_time < 5.0
    
    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large observation set
        observations = []
        for i in range(5000):
            observations.append({
                'id': f'obs-{i}',
                'type': 'test_coverage',
                'summary': f'Long summary for observation {i} with lots of text to increase memory usage and test how the system handles larger datasets',
                'priority': 50,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
        
        strategist = StrategistAgent(str(self.project_path))
        strategist.prioritize_observations(observations)
        strategist.detect_duplicates(observations)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        assert memory_increase < 100 * 1024 * 1024


if __name__ == '__main__':
    pytest.main([__file__, '-v'])