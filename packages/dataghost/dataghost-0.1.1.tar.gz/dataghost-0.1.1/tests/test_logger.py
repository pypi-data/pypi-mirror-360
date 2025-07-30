"""
Tests for the DataGhost logger module
"""
import os
import tempfile
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from ttd.logger import snapshot, _create_input_hash, _generate_run_id, _capture_metadata
from ttd.storage import DuckDBStorageBackend


class TestSnapshot:
    """Test the snapshot decorator"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage_backend = DuckDBStorageBackend(self.db_path)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_basic_snapshot(self):
        """Test basic snapshot functionality"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function(x: int, y: int = 5) -> int:
            return x + y
        
        result = test_function(3, y=7)
        assert result == 10
        
        # Check that snapshot was created
        snapshots = self.storage_backend.list_snapshots()
        assert len(snapshots) == 1
        
        snapshot_data = self.storage_backend.read_snapshot(snapshots[0]['snapshot_id'])
        assert snapshot_data['inputs']['args'] == (3,)
        assert snapshot_data['inputs']['kwargs'] == {'y': 7}
        assert snapshot_data['outputs'] == 10
        assert snapshot_data['success'] is True
    
    def test_snapshot_with_custom_task_id(self):
        """Test snapshot with custom task ID"""
        @snapshot(task_id="custom_task", storage_backend=self.storage_backend)
        def test_function(x: int) -> int:
            return x * 2
        
        result = test_function(5)
        assert result == 10
        
        snapshots = self.storage_backend.list_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0]['task_id'] == "custom_task"
    
    def test_snapshot_with_exception(self):
        """Test snapshot behavior when function raises exception"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function(x: int) -> int:
            if x < 0:
                raise ValueError("Negative value not allowed")
            return x * 2
        
        # Test successful execution
        result = test_function(5)
        assert result == 10
        
        # Test exception handling
        with pytest.raises(ValueError, match="Negative value not allowed"):
            test_function(-1)
        
        # Check snapshots
        snapshots = self.storage_backend.list_snapshots()
        assert len(snapshots) == 2
        
        # Check successful snapshot
        success_snapshot = next(s for s in snapshots if s['success'])
        success_data = self.storage_backend.read_snapshot(success_snapshot['snapshot_id'])
        assert success_data['outputs'] == 10
        assert success_data['success'] is True
        
        # Check failed snapshot
        failed_snapshot = next(s for s in snapshots if not s['success'])
        failed_data = self.storage_backend.read_snapshot(failed_snapshot['snapshot_id'])
        assert failed_data['outputs'] is None
        assert failed_data['success'] is False
        assert "Negative value not allowed" in failed_data['error']
    
    def test_snapshot_metadata_capture(self):
        """Test that metadata is properly captured"""
        @snapshot(storage_backend=self.storage_backend, capture_env=True, capture_system=True)
        def test_function(x: int) -> int:
            return x
        
        result = test_function(42)
        assert result == 42
        
        snapshots = self.storage_backend.list_snapshots()
        snapshot_data = self.storage_backend.read_snapshot(snapshots[0]['snapshot_id'])
        
        metadata = snapshot_data['metadata']
        assert 'function_name' in metadata
        assert 'module' in metadata
        assert 'python_version' in metadata
        assert 'hostname' in metadata
        assert 'timestamp' in metadata
        assert 'os' in metadata
        assert 'environment' in metadata
        assert metadata['function_name'] == 'test_function'
    
    def test_snapshot_execution_time(self):
        """Test that execution time is captured"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function(sleep_time: float) -> str:
            time.sleep(sleep_time)
            return "done"
        
        result = test_function(0.1)
        assert result == "done"
        
        snapshots = self.storage_backend.list_snapshots()
        snapshot_data = self.storage_backend.read_snapshot(snapshots[0]['snapshot_id'])
        
        assert snapshot_data['execution_time'] >= 0.1
        assert snapshot_data['execution_time'] < 1.0  # Should be quick


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_input_hash(self):
        """Test input hash creation"""
        source = "def test(): pass"
        args = (1, 2, 3)
        kwargs = {"a": 1, "b": 2}
        
        hash1 = _create_input_hash(source, args, kwargs)
        hash2 = _create_input_hash(source, args, kwargs)
        
        # Same inputs should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
        
        # Different inputs should produce different hashes
        hash3 = _create_input_hash(source, (1, 2, 4), kwargs)
        assert hash1 != hash3
    
    def test_generate_run_id(self):
        """Test run ID generation"""
        run_id1 = _generate_run_id()
        time.sleep(0.01)  # Small delay to ensure different timestamp
        run_id2 = _generate_run_id()
        
        assert run_id1 != run_id2
        assert "_" in run_id1
        assert str(os.getpid()) in run_id1
    
    def test_capture_metadata(self):
        """Test metadata capture"""
        def dummy_function():
            pass
        
        metadata = _capture_metadata(dummy_function, capture_env=True, capture_system=True)
        
        # Check required fields
        assert 'function_name' in metadata
        assert 'module' in metadata
        assert 'python_version' in metadata
        assert 'hostname' in metadata
        assert 'timestamp' in metadata
        assert 'os' in metadata
        assert 'environment' in metadata
        
        assert metadata['function_name'] == 'dummy_function'
        
        # Test with capture flags disabled
        metadata_minimal = _capture_metadata(dummy_function, capture_env=False, capture_system=False)
        assert 'environment' not in metadata_minimal
        assert 'os' not in metadata_minimal
        assert 'function_name' in metadata_minimal  # Always captured


class TestComplexScenarios:
    """Test complex scenarios and edge cases"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage_backend = DuckDBStorageBackend(self.db_path)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complex_data_types(self):
        """Test snapshot with complex data types"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function(data: dict) -> dict:
            return {
                'input_keys': list(data.keys()),
                'processed': [v * 2 for v in data.values() if isinstance(v, int)],
                'nested': {'result': sum(data.values())}
            }
        
        input_data = {
            'a': 1,
            'b': 2,
            'c': 3,
            'nested': {'x': 10}
        }
        
        result = test_function(input_data)
        
        snapshots = self.storage_backend.list_snapshots()
        snapshot_data = self.storage_backend.read_snapshot(snapshots[0]['snapshot_id'])
        
        assert snapshot_data['inputs']['args'] == (input_data,)
        assert snapshot_data['outputs'] == result
        assert snapshot_data['success'] is True
    
    def test_multiple_snapshots_same_function(self):
        """Test multiple snapshots of the same function"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function(x: int) -> int:
            return x * 2
        
        # Run function multiple times
        results = []
        for i in range(3):
            result = test_function(i)
            results.append(result)
        
        assert results == [0, 2, 4]
        
        # Check snapshots
        snapshots = self.storage_backend.list_snapshots()
        assert len(snapshots) == 3
        
        # All should have same task_id but different run_ids
        task_ids = [s['task_id'] for s in snapshots]
        run_ids = [s['run_id'] for s in snapshots]
        
        assert len(set(task_ids)) == 1  # All same task_id
        assert len(set(run_ids)) == 3   # All different run_ids
    
    def test_snapshot_with_no_args(self):
        """Test snapshot with function that takes no arguments"""
        @snapshot(storage_backend=self.storage_backend)
        def test_function() -> str:
            return "no args"
        
        result = test_function()
        assert result == "no args"
        
        snapshots = self.storage_backend.list_snapshots()
        snapshot_data = self.storage_backend.read_snapshot(snapshots[0]['snapshot_id'])
        
        assert snapshot_data['inputs']['args'] == ()
        assert snapshot_data['inputs']['kwargs'] == {}
        assert snapshot_data['outputs'] == "no args"
    
    def test_snapshot_preserves_function_attributes(self):
        """Test that snapshot decorator preserves function attributes"""
        def original_function(x: int) -> int:
            """Original function docstring"""
            return x * 2
        
        original_function.custom_attr = "test"
        
        decorated = snapshot(storage_backend=self.storage_backend)(original_function)
        
        assert decorated.__name__ == original_function.__name__
        assert decorated.__doc__ == original_function.__doc__
        assert hasattr(decorated, 'custom_attr')
        assert decorated.custom_attr == "test"