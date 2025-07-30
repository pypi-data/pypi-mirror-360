"""
Tests for the DataGhost diff module
"""
import os
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

from ttd.diff import DiffEngine
from ttd.storage import DuckDBStorageBackend


class TestDiffEngine:
    """Test the DiffEngine class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = DuckDBStorageBackend(self.db_path)
        self.diff_engine = DiffEngine(self.storage)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_identical_snapshots_diff(self):
        """Test diff of identical snapshots"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {'param': 'value'}},
            'outputs': {'result': 42, 'status': 'success'},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        # Create two identical snapshots
        snapshot_id1 = self.storage.write_snapshot(snapshot_data)
        
        snapshot_data['run_id'] = 'run_2'
        snapshot_data['timestamp'] = datetime.now().isoformat()
        snapshot_id2 = self.storage.write_snapshot(snapshot_data)
        
        # Diff the snapshots
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        # Check that inputs and outputs are identical
        assert diff_result['diffs']['inputs']['equal'] is True
        assert diff_result['diffs']['outputs']['equal'] is True
        assert diff_result['summary']['total_differences'] == 0
    
    def test_different_outputs_diff(self):
        """Test diff of snapshots with different outputs"""
        base_time = datetime.now()
        
        snapshot1_data = {
            'task_id': 'test_task',
            'run_id': 'run_1',
            'timestamp': base_time.isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42, 'status': 'success'},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'test_task',
            'run_id': 'run_2',
            'timestamp': (base_time + timedelta(minutes=5)).isoformat(),
            'execution_time': 1.5,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 84, 'status': 'success'},  # Different result
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        # Check that outputs are different
        assert diff_result['diffs']['outputs']['equal'] is False
        assert diff_result['summary']['total_differences'] > 0
        assert 'outputs' in diff_result['summary']['sections_with_changes']
        
        # Check execution time difference
        assert diff_result['execution_diff']['execution_time_diff'] == 0.5
    
    def test_different_inputs_diff(self):
        """Test diff of snapshots with different inputs"""
        snapshot1_data = {
            'task_id': 'test_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {'param': 'value1'}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'test_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'def456',
            'inputs': {'args': (10,), 'kwargs': {'param': 'value2'}},  # Different inputs
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        # Check that inputs are different
        assert diff_result['diffs']['inputs']['equal'] is False
        assert 'inputs' in diff_result['summary']['sections_with_changes']
    
    def test_success_status_change_diff(self):
        """Test diff when success status changes"""
        snapshot1_data = {
            'task_id': 'test_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'test_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0.5,
            'success': False,  # Changed to failure
            'error': 'Something went wrong',
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': None,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        # Check execution changes
        assert diff_result['execution_diff']['success_change']['from'] is True
        assert diff_result['execution_diff']['success_change']['to'] is False
        assert diff_result['execution_diff']['error_change']['from'] is None
        assert diff_result['execution_diff']['error_change']['to'] == 'Something went wrong'
        assert diff_result['summary']['success_changed'] is True
    
    def test_diff_task_runs(self):
        """Test diff_task_runs method"""
        # Create multiple snapshots for the same task
        for i in range(3):
            snapshot_data = {
                'task_id': 'multi_run_task',
                'run_id': f'run_{i}',
                'timestamp': datetime.now().isoformat(),
                'execution_time': 1.0 + i * 0.1,
                'success': True,
                'error': None,
                'input_hash': f'hash_{i}',
                'inputs': {'args': (i,), 'kwargs': {}},
                'outputs': {'result': i * 2},
                'metadata': {'function_name': 'test_func', 'module': 'test_module'}
            }
            self.storage.write_snapshot(snapshot_data)
        
        # Diff latest two runs
        diff_result = self.diff_engine.diff_task_runs('multi_run_task')
        
        assert diff_result['snapshot1']['run_id'] == 'run_2'  # Latest
        assert diff_result['snapshot2']['run_id'] == 'run_1'  # Second latest
        
        # Diff specific runs
        diff_result = self.diff_engine.diff_task_runs(
            'multi_run_task',
            run_id1='run_0',
            run_id2='run_2'
        )
        
        assert diff_result['snapshot1']['run_id'] == 'run_0'
        assert diff_result['snapshot2']['run_id'] == 'run_2'
    
    def test_diff_outputs_only(self):
        """Test diff_outputs_only method"""
        snapshot1_data = {
            'task_id': 'test_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42, 'data': [1, 2, 3]},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'test_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 84, 'data': [1, 2, 3, 4]},  # Different outputs
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_outputs_only(snapshot_id1, snapshot_id2)
        
        assert 'outputs_diff' in diff_result
        assert diff_result['outputs_diff']['equal'] is False
        assert diff_result['snapshot1_id'] == snapshot_id1
        assert diff_result['snapshot2_id'] == snapshot_id2
    
    def test_type_change_diff(self):
        """Test diff when output types change"""
        snapshot1_data = {
            'task_id': 'type_change_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,  # Integer
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'type_change_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': "42",  # String
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        outputs_diff = diff_result['diffs']['outputs']
        assert outputs_diff['type'] == 'type_change'
        assert outputs_diff['type1'] == 'int'
        assert outputs_diff['type2'] == 'str'
        assert outputs_diff['equal'] is False
    
    @pytest.mark.skipif(True, reason="DeepDiff is optional dependency")
    def test_deep_diff_with_deepdiff(self):
        """Test deep diff functionality with DeepDiff library"""
        # This test would only run if DeepDiff is available
        snapshot1_data = {
            'task_id': 'deep_diff_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': {
                'nested': {'a': 1, 'b': 2, 'c': [1, 2, 3]},
                'simple': 42
            },
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'deep_diff_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': {
                'nested': {'a': 1, 'b': 3, 'c': [1, 2, 3, 4]},  # Changes in nested data
                'simple': 42
            },
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        with patch('ttd.diff.HAS_DEEPDIFF', True):
            with patch('ttd.diff.DeepDiff') as mock_deepdiff:
                mock_deepdiff.return_value = {
                    'values_changed': {"root['nested']['b']": {'old_value': 2, 'new_value': 3}},
                    'iterable_item_added': {"root['nested']['c'][3]": 4}
                }
                
                diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
                
                outputs_diff = diff_result['diffs']['outputs']
                assert outputs_diff['type'] == 'deep_diff'
                assert outputs_diff['equal'] is False
                assert 'deepdiff' in outputs_diff
    
    def test_generate_diff_report_text(self):
        """Test generating text diff report"""
        snapshot1_data = {
            'task_id': 'report_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'report_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.5,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 84},  # Different output
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        report = self.diff_engine.generate_diff_report(diff_result, format='text')
        
        assert 'DataGhost Snapshot Diff Report' in report
        assert 'Snapshot 1:' in report
        assert 'Snapshot 2:' in report
        assert 'Summary' in report
        assert 'report_task' in report
    
    def test_generate_diff_report_json(self):
        """Test generating JSON diff report"""
        snapshot1_data = {
            'task_id': 'json_report_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'json_report_task',
            'run_id': 'run_2',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (5,), 'kwargs': {}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        report = self.diff_engine.generate_diff_report(diff_result, format='json')
        
        # Should be valid JSON
        parsed_report = json.loads(report)
        assert 'snapshot1' in parsed_report
        assert 'snapshot2' in parsed_report
        assert 'diffs' in parsed_report
        assert 'summary' in parsed_report
    
    def test_diff_with_insufficient_snapshots(self):
        """Test diff_task_runs with insufficient snapshots"""
        # Create only one snapshot
        snapshot_data = {
            'task_id': 'single_snapshot_task',
            'run_id': 'run_1',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        self.storage.write_snapshot(snapshot_data)
        
        with pytest.raises(ValueError, match="has fewer than 2 snapshots"):
            self.diff_engine.diff_task_runs('single_snapshot_task')
    
    def test_time_difference_calculation(self):
        """Test time difference calculation in diff"""
        base_time = datetime.now()
        
        snapshot1_data = {
            'task_id': 'time_diff_task',
            'run_id': 'run_1',
            'timestamp': base_time.isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot2_data = {
            'task_id': 'time_diff_task',
            'run_id': 'run_2',
            'timestamp': (base_time + timedelta(hours=2)).isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': 42,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id1 = self.storage.write_snapshot(snapshot1_data)
        snapshot_id2 = self.storage.write_snapshot(snapshot2_data)
        
        diff_result = self.diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        
        time_diff = diff_result['execution_diff']['time_difference']
        assert time_diff['seconds'] == 7200.0  # 2 hours in seconds
        assert time_diff['direction'] == 'forward'