"""
Tests for the DataGhost replay module
"""
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from ttd.replay import ReplayEngine
from ttd.storage import DuckDBStorageBackend


class TestReplayEngine:
    """Test the ReplayEngine class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = DuckDBStorageBackend(self.db_path)
        self.replay_engine = ReplayEngine(self.storage)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_replay_successful_execution(self):
        """Test replaying a successful execution"""
        # Create a snapshot first
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {'multiplier': 2}},
            'outputs': 10,
            'metadata': {
                'function_name': 'test_function',
                'module': 'tests.test_replay'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        # Mock the function for replay
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=10)
            mock_module.test_function = mock_function
            mock_import.return_value = mock_module
            
            # Replay the function
            result = self.replay_engine.replay(
                task_id='test_task',
                run_id='test_run',
                validate_output=True
            )
            
            # Verify replay results
            assert result['replay_success'] is True
            assert result['replay_outputs'] == 10
            assert result['outputs_match'] is True
            
            # Verify function was called with correct arguments
            mock_function.assert_called_once_with(5, multiplier=2)
    
    def test_replay_with_snapshot_id(self):
        """Test replaying using snapshot ID directly"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (3,), 'kwargs': {}},
            'outputs': 9,
            'metadata': {
                'function_name': 'square_function',
                'module': 'tests.test_replay'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=9)
            mock_module.square_function = mock_function
            mock_import.return_value = mock_module
            
            result = self.replay_engine.replay(snapshot_id=snapshot_id)
            
            assert result['replay_success'] is True
            assert result['replay_outputs'] == 9
            mock_function.assert_called_once_with(3)
    
    def test_replay_failed_execution(self):
        """Test replaying a function that fails"""
        snapshot_data = {
            'task_id': 'failing_task',
            'run_id': 'failing_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0.5,
            'success': False,
            'error': 'Division by zero',
            'input_hash': 'def456',
            'inputs': {'args': (10, 0), 'kwargs': {}},
            'outputs': None,
            'metadata': {
                'function_name': 'divide_function',
                'module': 'tests.test_replay'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(side_effect=ZeroDivisionError("Division by zero"))
            mock_module.divide_function = mock_function
            mock_import.return_value = mock_module
            
            result = self.replay_engine.replay(snapshot_id=snapshot_id)
            
            assert result['replay_success'] is False
            assert result['replay_error'] == 'Division by zero'
            assert result['replay_outputs'] is None
    
    def test_replay_with_different_output(self):
        """Test replay when output differs from original"""
        snapshot_data = {
            'task_id': 'random_task',
            'run_id': 'random_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'ghi789',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,
            'metadata': {
                'function_name': 'random_function',
                'module': 'tests.test_replay'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=99)  # Different output
            mock_module.random_function = mock_function
            mock_import.return_value = mock_module
            
            result = self.replay_engine.replay(
                snapshot_id=snapshot_id,
                validate_output=True
            )
            
            assert result['replay_success'] is True
            assert result['replay_outputs'] == 99
            assert result['original_outputs'] == 42
            assert result['outputs_match'] is False
    
    def test_replay_without_validation(self):
        """Test replay without output validation"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': 25,
            'metadata': {
                'function_name': 'test_function',
                'module': 'tests.test_replay'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=30)  # Different output
            mock_module.test_function = mock_function
            mock_import.return_value = mock_module
            
            result = self.replay_engine.replay(
                snapshot_id=snapshot_id,
                validate_output=False
            )
            
            assert result['replay_success'] is True
            assert result['outputs_match'] is False  # Still computed but not validated
    
    def test_replay_nonexistent_snapshot(self):
        """Test replay with non-existent snapshot"""
        with pytest.raises(ValueError, match="No snapshot found"):
            self.replay_engine.replay(
                task_id='nonexistent_task',
                run_id='nonexistent_run'
            )
    
    def test_replay_import_error(self):
        """Test replay when module import fails"""
        snapshot_data = {
            'task_id': 'import_error_task',
            'run_id': 'import_error_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,
            'metadata': {
                'function_name': 'test_function',
                'module': 'nonexistent_module'
            }
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            result = self.replay_engine.replay(snapshot_id=snapshot_id)
            
            assert result['replay_success'] is False
            assert "Module not found" in result['replay_error']
    
    def test_replay_latest_snapshot(self):
        """Test replaying the latest snapshot when run_id is not specified"""
        # Create multiple snapshots for the same task
        for i in range(3):
            snapshot_data = {
                'task_id': 'multi_run_task',
                'run_id': f'run_{i}',
                'timestamp': datetime.now().isoformat(),
                'execution_time': 1.0,
                'success': True,
                'error': None,
                'input_hash': f'hash_{i}',
                'inputs': {'args': (i,), 'kwargs': {}},
                'outputs': i * 2,
                'metadata': {
                    'function_name': 'test_function',
                    'module': 'tests.test_replay'
                }
            }
            self.storage.write_snapshot(snapshot_data)
        
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_function = MagicMock(return_value=4)
            mock_module.test_function = mock_function
            mock_import.return_value = mock_module
            
            # Replay without specifying run_id (should use latest)
            result = self.replay_engine.replay(task_id='multi_run_task')
            
            assert result['replay_success'] is True
            # Should have called with the latest snapshot's inputs (2,)
            mock_function.assert_called_once_with(2)
    
    def test_list_replayable_tasks(self):
        """Test listing replayable tasks"""
        # Create snapshots for different tasks
        tasks_data = [
            ('task_a', 'run_1', True),
            ('task_a', 'run_2', False),
            ('task_b', 'run_1', True),
            ('task_b', 'run_2', True),
            ('task_c', 'run_1', False),
        ]
        
        for task_id, run_id, success in tasks_data:
            snapshot_data = {
                'task_id': task_id,
                'run_id': run_id,
                'timestamp': datetime.now().isoformat(),
                'execution_time': 1.0,
                'success': success,
                'error': None if success else 'Test error',
                'input_hash': f'hash_{task_id}_{run_id}',
                'inputs': {'args': (), 'kwargs': {}},
                'outputs': 42 if success else None,
                'metadata': {
                    'function_name': f'func_{task_id}',
                    'module': 'tests.test_replay'
                }
            }
            self.storage.write_snapshot(snapshot_data)
        
        tasks = self.replay_engine.list_replayable_tasks()
        
        assert len(tasks) == 3
        assert 'task_a' in tasks
        assert 'task_b' in tasks
        assert 'task_c' in tasks
        
        # Check task_a statistics
        task_a = tasks['task_a']
        assert task_a['total_runs'] == 2
        assert task_a['successful_runs'] == 1
        assert task_a['failed_runs'] == 1
        
        # Check task_b statistics
        task_b = tasks['task_b']
        assert task_b['total_runs'] == 2
        assert task_b['successful_runs'] == 2
        assert task_b['failed_runs'] == 0
    
    def test_output_comparison_methods(self):
        """Test different output comparison methods"""
        engine = self.replay_engine
        
        # Test identical values
        assert engine._compare_outputs(42, 42) is True
        assert engine._compare_outputs("hello", "hello") is True
        assert engine._compare_outputs([1, 2, 3], [1, 2, 3]) is True
        
        # Test different values
        assert engine._compare_outputs(42, 43) is False
        assert engine._compare_outputs("hello", "world") is False
        assert engine._compare_outputs([1, 2, 3], [1, 2, 4]) is False
        
        # Test with None
        assert engine._compare_outputs(None, None) is True
        assert engine._compare_outputs(42, None) is False
        assert engine._compare_outputs(None, 42) is False
    
    def test_numpy_array_comparison(self):
        """Test comparison of numpy arrays"""
        import numpy as np
        
        engine = self.replay_engine
        
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([1, 2, 3])
        arr3 = np.array([1, 2, 4])
        
        assert engine._compare_outputs(arr1, arr2) is True
        assert engine._compare_outputs(arr1, arr3) is False
    
    def test_pandas_dataframe_comparison(self):
        """Test comparison of pandas DataFrames"""
        import pandas as pd
        
        engine = self.replay_engine
        
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df3 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 7]})
        
        assert engine._compare_outputs(df1, df2) is True
        assert engine._compare_outputs(df1, df3) is False