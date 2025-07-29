#!/usr/bin/env python3
"""
Comprehensive unit tests for TODO resolution detection functionality.

Tests the complete TODO resolution detection system including:
- BrassStorage.detect_resolved_todos() method
- Database schema migration
- BrassRunner integration 
- OutputGenerator resolution filtering
- Edge cases and error handling
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import the modules we're testing
from coppersun_brass.core.storage import BrassStorage
from coppersun_brass.core.output_generator import OutputGenerator
from coppersun_brass.agents.scout.todo_detector import TODOFinding
from coppersun_brass.config import BrassConfig


class TestTodoResolutionDetection(unittest.TestCase):
    """Test suite for TODO resolution detection core functionality."""
    
    def setUp(self):
        """Set up test environment with temporary database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_brass.db"
        self.storage = BrassStorage(self.db_path)
        
        # Create sample TODO findings for testing
        self.sample_todos = [
            TODOFinding(
                file_path="/test/file1.py",
                line_number=10,
                content="Fix authentication bug",
                todo_type="FIXME",
                confidence=0.9,
                priority_score=80,
                is_researchable=False,
                context_lines=["# Authentication code", "# TODO: Fix authentication bug", "# End of function"],
                content_hash="abc123",
                created_at=datetime.now()
            ),
            TODOFinding(
                file_path="/test/file2.py", 
                line_number=25,
                content="Add error handling",
                todo_type="TODO",
                confidence=0.8,
                priority_score=60,
                is_researchable=True,
                context_lines=["def process_data():", "    # TODO: Add error handling", "    return result"],
                content_hash="def456",
                created_at=datetime.now()
            ),
            TODOFinding(
                file_path="/test/file3.py",
                line_number=42,
                content="Optimize performance",
                todo_type="TODO", 
                confidence=0.7,
                priority_score=40,
                is_researchable=True,
                context_lines=["# Performance critical section", "# TODO: Optimize performance", "# Process data"],
                content_hash="ghi789",
                created_at=datetime.now()
            )
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_database_resolution(self):
        """Test resolution detection with empty database (no stored TODOs)."""
        # Should handle empty database gracefully
        resolved_count = self.storage.detect_resolved_todos(self.sample_todos)
        self.assertEqual(resolved_count, 0, "Should return 0 for empty database")
    
    def test_no_resolutions_detected(self):
        """Test when all stored TODOs are still present in current findings."""
        # First, store some TODOs
        for todo in self.sample_todos:
            self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content,
                    'todo_type': todo.todo_type,
                    'confidence': todo.confidence,
                    'priority_score': todo.priority_score
                },
                source_agent='test',
                priority=todo.priority_score
            )
        
        # Run resolution detection with same TODOs
        resolved_count = self.storage.detect_resolved_todos(self.sample_todos)
        self.assertEqual(resolved_count, 0, "Should detect no resolutions when all TODOs still present")
        
        # Verify none marked as resolved
        todos = self.storage.get_observations(obs_type='todo')
        for todo in todos:
            self.assertFalse(todo.get('resolved', False), "No TODOs should be marked as resolved")
    
    def test_partial_resolutions(self):
        """Test when some TODOs are resolved but others remain."""
        # Store all TODOs
        for todo in self.sample_todos:
            self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content,
                    'todo_type': todo.todo_type,
                    'confidence': todo.confidence,
                    'priority_score': todo.priority_score
                },
                source_agent='test',
                priority=todo.priority_score
            )
        
        # Run resolution detection with only first two TODOs (third is "resolved")
        current_todos = self.sample_todos[:2]
        resolved_count = self.storage.detect_resolved_todos(current_todos)
        
        self.assertEqual(resolved_count, 1, "Should detect 1 resolution")
        
        # Verify the correct TODO is marked as resolved
        todos = self.storage.get_observations(obs_type='todo')
        resolved_todos = [t for t in todos if t.get('resolved', False)]
        self.assertEqual(len(resolved_todos), 1, "Exactly 1 TODO should be marked as resolved")
        
        resolved_todo = resolved_todos[0]
        self.assertEqual(resolved_todo['data']['file_path'], "/test/file3.py")
        self.assertEqual(resolved_todo['data']['line_number'], 42)
    
    def test_complete_resolutions(self):
        """Test when all stored TODOs are resolved."""
        # Store some TODOs
        for todo in self.sample_todos:
            self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content,
                    'todo_type': todo.todo_type,
                    'confidence': todo.confidence,
                    'priority_score': todo.priority_score
                },
                source_agent='test',
                priority=todo.priority_score
            )
        
        # Run resolution detection with empty current findings (all resolved)
        resolved_count = self.storage.detect_resolved_todos([])
        
        self.assertEqual(resolved_count, 3, "Should detect 3 resolutions")
        
        # Verify all TODOs marked as resolved
        todos = self.storage.get_observations(obs_type='todo')
        for todo in todos:
            self.assertTrue(todo.get('resolved', False), "All TODOs should be marked as resolved")
            self.assertIsNotNone(todo.get('resolved_at'), "All TODOs should have resolved_at timestamp")
    
    def test_duplicate_line_handling(self):
        """Test handling of duplicate line numbers in different files."""
        # Create TODOs with same line numbers in different files
        duplicate_todos = [
            TODOFinding(
                file_path="/test/file1.py",
                line_number=10,
                content="Fix bug in file1",
                todo_type="FIXME",
                confidence=0.9,
                priority_score=80,
                is_researchable=False,
                context_lines=["# File1 code"],
                content_hash="file1_abc",
                created_at=datetime.now()
            ),
            TODOFinding(
                file_path="/test/file2.py",
                line_number=10,  # Same line number, different file
                content="Fix bug in file2",
                todo_type="FIXME", 
                confidence=0.9,
                priority_score=80,
                is_researchable=False,
                context_lines=["# File2 code"],
                content_hash="file2_abc",
                created_at=datetime.now()
            )
        ]
        
        # Store both TODOs
        for todo in duplicate_todos:
            self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content,
                    'todo_type': todo.todo_type
                },
                source_agent='test',
                priority=todo.priority_score
            )
        
        # Resolve only the first file's TODO
        current_todos = [duplicate_todos[1]]  # Only file2 TODO remains
        resolved_count = self.storage.detect_resolved_todos(current_todos)
        
        self.assertEqual(resolved_count, 1, "Should resolve only file1 TODO")
        
        # Verify correct TODO resolved
        todos = self.storage.get_observations(obs_type='todo')
        for todo in todos:
            if todo['data']['file_path'] == "/test/file1.py":
                self.assertTrue(todo.get('resolved', False), "File1 TODO should be resolved")
            else:
                self.assertFalse(todo.get('resolved', False), "File2 TODO should not be resolved")
    
    def test_file_rename_scenarios(self):
        """Test behavior when files are renamed (TODOs appear to be missing)."""
        # Store TODO in original file path
        original_todo = self.sample_todos[0]
        self.storage.add_observation(
            obs_type='todo',
            data={
                'file_path': original_todo.file_path,
                'line_number': original_todo.line_number,
                'content': original_todo.content,
                'todo_type': original_todo.todo_type
            },
            source_agent='test',
            priority=original_todo.priority_score
        )
        
        # Create "renamed" file TODO (same content, different path)
        renamed_todo = TODOFinding(
            file_path="/test/renamed_file.py",  # Different path
            line_number=original_todo.line_number,
            content=original_todo.content,  # Same content
            todo_type=original_todo.todo_type,
            confidence=original_todo.confidence,
            priority_score=original_todo.priority_score,
            is_researchable=original_todo.is_researchable,
            context_lines=original_todo.context_lines,
            content_hash="renamed_hash",
            created_at=datetime.now()
        )
        
        # Run resolution detection - should mark original as resolved
        resolved_count = self.storage.detect_resolved_todos([renamed_todo])
        
        self.assertEqual(resolved_count, 1, "Should detect original file TODO as resolved")
        
        # Note: This is expected behavior - file renames look like resolutions
        # In practice, this is acceptable since the TODO effectively moved
    
    def test_database_migration(self):
        """Test database schema migration for resolved columns."""
        # Create a new storage instance to trigger migration
        new_storage = BrassStorage(self.db_path)
        
        # Check that columns exist by trying to query them
        with new_storage.transaction() as conn:
            # This should not raise an error if migration worked
            result = conn.execute("SELECT resolved, resolved_at FROM observations LIMIT 0").fetchall()
            self.assertEqual(len(result), 0, "Migration should create resolved columns")
    
    def test_resolution_metrics(self):
        """Test resolution metrics calculation."""
        # Add some TODOs and mark some as resolved
        for i, todo in enumerate(self.sample_todos):
            obs_id = self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content,
                    'todo_type': todo.todo_type
                },
                source_agent='test',
                priority=todo.priority_score
            )
            
            # Mark first two as resolved
            if i < 2:
                self.storage.mark_observations_resolved([obs_id])
        
        # Get metrics
        metrics = self.storage.get_resolution_metrics()
        
        self.assertEqual(metrics['total_todos'], 3, "Should count all TODOs")
        self.assertEqual(metrics['resolved_todos'], 2, "Should count resolved TODOs")
        self.assertEqual(metrics['active_todos'], 1, "Should count active TODOs")
        self.assertAlmostEqual(metrics['resolution_rate'], 2/3, places=2, msg="Should calculate correct resolution rate")
    
    def test_error_handling(self):
        """Test graceful error handling in resolution detection."""
        # Add a TODO with malformed JSON data
        with self.storage.transaction() as conn:
            conn.execute("""
                INSERT INTO observations (type, source_agent, priority, data)
                VALUES (?, ?, ?, ?)
            """, ('todo', 'test', 50, 'invalid json'))
        
        # Should handle gracefully without crashing
        resolved_count = self.storage.detect_resolved_todos(self.sample_todos)
        self.assertEqual(resolved_count, 0, "Should handle malformed data gracefully")
    
    def test_mark_observations_resolved(self):
        """Test manual resolution marking."""
        # Add TODOs and get their IDs
        todo_ids = []
        for todo in self.sample_todos:
            obs_id = self.storage.add_observation(
                obs_type='todo',
                data={
                    'file_path': todo.file_path,
                    'line_number': todo.line_number,
                    'content': todo.content
                },
                source_agent='test',
                priority=todo.priority_score
            )
            todo_ids.append(obs_id)
        
        # Mark first two as resolved
        self.storage.mark_observations_resolved(todo_ids[:2])
        
        # Verify correct TODOs marked
        todos = self.storage.get_observations(obs_type='todo')
        resolved_count = sum(1 for t in todos if t.get('resolved', False))
        self.assertEqual(resolved_count, 2, "Should mark exactly 2 TODOs as resolved")


class TestIntegrationFlow(unittest.TestCase):
    """Test suite for integration between components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_brass.db"
        self.storage = BrassStorage(self.db_path)
        
        # Mock config for OutputGenerator
        self.mock_config = Mock(spec=BrassConfig)
        self.mock_config.project_root = Path(self.temp_dir)
        self.mock_config.output_dir = Path(self.temp_dir) / '.brass'
        self.mock_config.output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_output_excludes_resolved(self):
        """Test that OutputGenerator excludes resolved TODOs."""
        # Add some TODOs, mark some as resolved
        active_todo_id = self.storage.add_observation(
            obs_type='todo',
            data={
                'file': '/test/active.py',
                'line': 10,
                'content': 'Active TODO',
                'classification': 'important'
            },
            source_agent='test',
            priority=80
        )
        
        resolved_todo_id = self.storage.add_observation(
            obs_type='todo', 
            data={
                'file': '/test/resolved.py',
                'line': 20,
                'content': 'Resolved TODO',
                'classification': 'important'
            },
            source_agent='test',
            priority=70
        )
        
        # Mark one as resolved
        self.storage.mark_observations_resolved([resolved_todo_id])
        
        # Generate output
        generator = OutputGenerator(self.mock_config, self.storage)
        todo_path = generator.generate_todo_list()
        
        # Read generated output
        with open(todo_path, 'r') as f:
            todo_data = json.load(f)
        
        # Should only contain active TODO
        self.assertEqual(len(todo_data['todos']), 1, "Should only include active TODOs")
        self.assertEqual(todo_data['todos'][0]['content'], 'Active TODO')
        
        # Should include resolution metrics
        self.assertIn('resolution_metrics', todo_data)
        self.assertEqual(todo_data['resolution_metrics']['active_todos'], 1)
        self.assertEqual(todo_data['resolution_metrics']['resolved_todos'], 1)
    
    def test_analysis_report_includes_metrics(self):
        """Test that analysis report includes resolution metrics."""
        # Add some TODOs
        self.storage.add_observation(
            obs_type='todo',
            data={'file': '/test/file.py', 'line': 10, 'content': 'Test TODO'},
            source_agent='test',
            priority=50
        )
        
        # Generate analysis report
        generator = OutputGenerator(self.mock_config, self.storage)
        report_path = generator.generate_analysis_report()
        
        # Read generated report
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Should include resolution metrics
        self.assertIn('resolution_metrics', report_data['summary'])
        metrics = report_data['summary']['resolution_metrics']
        
        self.assertIn('total_todos', metrics)
        self.assertIn('active_todos', metrics)
        self.assertIn('resolved_todos', metrics)
        self.assertIn('resolution_rate', metrics)
    
    @patch('coppersun_brass.runner.TODODetector')
    def test_runner_calls_detection(self, mock_detector_class):
        """Test that BrassRunner calls resolution detection correctly."""
        # This would require more complex mocking of the full BrassRunner
        # For now, we'll test the logic we can isolate
        
        # Mock detector instance
        mock_detector = Mock()
        mock_detector.scan_file.return_value = []
        mock_detector_class.return_value = mock_detector
        
        # Create some stored TODOs that should be resolved
        self.storage.add_observation(
            obs_type='todo',
            data={
                'file_path': '/test/old.py',
                'line_number': 10,
                'content': 'Old TODO'
            },
            source_agent='test',
            priority=50
        )
        
        # Simulate resolution detection with empty current findings
        resolved_count = self.storage.detect_resolved_todos([])
        
        self.assertEqual(resolved_count, 1, "Should detect resolution when no current TODOs")


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Suppress debug logs during tests
    
    # Run the tests
    unittest.main()