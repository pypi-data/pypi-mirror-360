"""
Tests for the DataGhost storage module
"""
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from ttd.storage import DuckDBStorageBackend, StorageBackend


class TestDuckDBStorageBackend:
    """Test DuckDB storage backend"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.storage = DuckDBStorageBackend(self.db_path, self.data_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test storage backend initialization"""
        assert os.path.exists(self.db_path)
        assert os.path.exists(self.data_dir)
        
        # Test that database tables are created
        import duckdb
        conn = duckdb.connect(self.db_path)
        try:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='snapshots'").fetchone()
            # DuckDB doesn't have sqlite_master, so test differently
            conn.execute("SELECT COUNT(*) FROM snapshots")
        finally:
            conn.close()
    
    def test_write_and_read_snapshot(self):
        """Test writing and reading snapshots"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run_001',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.5,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (1, 2), 'kwargs': {'param': 'value'}},
            'outputs': {'result': 42},
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        # Write snapshot
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        assert snapshot_id is not None
        
        # Read snapshot
        retrieved_data = self.storage.read_snapshot(snapshot_id)
        
        assert retrieved_data['task_id'] == snapshot_data['task_id']
        assert retrieved_data['run_id'] == snapshot_data['run_id']
        assert retrieved_data['success'] == snapshot_data['success']
        assert retrieved_data['inputs'] == snapshot_data['inputs']
        assert retrieved_data['outputs'] == snapshot_data['outputs']
        assert retrieved_data['metadata'] == snapshot_data['metadata']
    
    def test_write_snapshot_with_failure(self):
        """Test writing snapshot for failed execution"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run_002',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0.5,
            'success': False,
            'error': 'Test error message',
            'input_hash': 'def456',
            'inputs': {'args': (1,), 'kwargs': {}},
            'outputs': None,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        retrieved_data = self.storage.read_snapshot(snapshot_id)
        
        assert retrieved_data['success'] is False
        assert retrieved_data['error'] == 'Test error message'
        assert retrieved_data['outputs'] is None
    
    def test_list_snapshots(self):
        """Test listing snapshots"""
        # Create multiple snapshots
        for i in range(3):
            snapshot_data = {
                'task_id': f'task_{i}',
                'run_id': f'run_{i}',
                'timestamp': datetime.now().isoformat(),
                'execution_time': float(i),
                'success': True,
                'error': None,
                'input_hash': f'hash_{i}',
                'inputs': {'args': (i,), 'kwargs': {}},
                'outputs': i * 2,
                'metadata': {'function_name': f'func_{i}', 'module': 'test_module'}
            }
            self.storage.write_snapshot(snapshot_data)
        
        # List all snapshots
        all_snapshots = self.storage.list_snapshots()
        assert len(all_snapshots) == 3
        
        # List snapshots by task_id
        task_snapshots = self.storage.list_snapshots('task_1')
        assert len(task_snapshots) == 1
        assert task_snapshots[0]['task_id'] == 'task_1'
        
        # List snapshots for non-existent task
        empty_snapshots = self.storage.list_snapshots('non_existent_task')
        assert len(empty_snapshots) == 0
    
    def test_delete_snapshot(self):
        """Test deleting snapshots"""
        snapshot_data = {
            'task_id': 'test_task',
            'run_id': 'test_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'abc123',
            'inputs': {'args': (1,), 'kwargs': {}},
            'outputs': 42,
            'metadata': {'function_name': 'test_func', 'module': 'test_module'}
        }
        
        # Write snapshot
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        # Verify it exists
        snapshots = self.storage.list_snapshots()
        assert len(snapshots) == 1
        
        # Delete snapshot
        deleted = self.storage.delete_snapshot(snapshot_id)
        assert deleted is True
        
        # Verify it's gone
        snapshots = self.storage.list_snapshots()
        assert len(snapshots) == 0
        
        # Try to delete non-existent snapshot
        deleted = self.storage.delete_snapshot('non_existent_id')
        assert deleted is False
    
    def test_read_nonexistent_snapshot(self):
        """Test reading a non-existent snapshot"""
        with pytest.raises(ValueError, match="Snapshot .* not found"):
            self.storage.read_snapshot('non_existent_id')
    
    def test_complex_data_serialization(self):
        """Test serialization of complex data types"""
        import numpy as np
        import pandas as pd
        
        # Create complex data
        complex_data = {
            'numpy_array': np.array([1, 2, 3, 4, 5]),
            'pandas_df': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
            'nested_dict': {
                'level1': {
                    'level2': [1, 2, 3, {'key': 'value'}]
                }
            },
            'custom_object': datetime.now()
        }
        
        snapshot_data = {
            'task_id': 'complex_test',
            'run_id': 'complex_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'complex_hash',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': complex_data,
            'metadata': {'function_name': 'complex_func', 'module': 'test_module'}
        }
        
        # Write and read
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        retrieved_data = self.storage.read_snapshot(snapshot_id)
        
        # Verify complex data is preserved
        assert np.array_equal(retrieved_data['outputs']['numpy_array'], complex_data['numpy_array'])
        pd.testing.assert_frame_equal(retrieved_data['outputs']['pandas_df'], complex_data['pandas_df'])
        assert retrieved_data['outputs']['nested_dict'] == complex_data['nested_dict']
        assert retrieved_data['outputs']['custom_object'] == complex_data['custom_object']
    
    def test_compression(self):
        """Test that data is properly compressed"""
        # Create large data to test compression
        large_data = {
            'large_list': list(range(10000)),
            'repeated_string': 'test' * 1000
        }
        
        snapshot_data = {
            'task_id': 'compression_test',
            'run_id': 'compression_run',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 1.0,
            'success': True,
            'error': None,
            'input_hash': 'compression_hash',
            'inputs': {'args': (), 'kwargs': {}},
            'outputs': large_data,
            'metadata': {'function_name': 'compression_func', 'module': 'test_module'}
        }
        
        snapshot_id = self.storage.write_snapshot(snapshot_data)
        
        # Check that compressed files exist
        snapshot_dir = os.path.join(self.data_dir, snapshot_id)
        assert os.path.exists(snapshot_dir)
        
        # Files should have .lz4 extension
        files = os.listdir(snapshot_dir)
        assert any(f.endswith('.lz4') for f in files)
        
        # Data should be retrievable
        retrieved_data = self.storage.read_snapshot(snapshot_id)
        assert retrieved_data['outputs'] == large_data
    
    def test_concurrent_access(self):
        """Test concurrent access to storage"""
        import threading
        import time
        
        results = []
        errors = []
        
        def write_snapshots(thread_id):
            try:
                for i in range(5):
                    snapshot_data = {
                        'task_id': f'thread_{thread_id}_task_{i}',
                        'run_id': f'thread_{thread_id}_run_{i}',
                        'timestamp': datetime.now().isoformat(),
                        'execution_time': 0.1,
                        'success': True,
                        'error': None,
                        'input_hash': f'hash_{thread_id}_{i}',
                        'inputs': {'args': (i,), 'kwargs': {}},
                        'outputs': i * thread_id,
                        'metadata': {'function_name': f'func_{thread_id}', 'module': 'test_module'}
                    }
                    snapshot_id = self.storage.write_snapshot(snapshot_data)
                    results.append(snapshot_id)
                    time.sleep(0.01)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=write_snapshots, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 15  # 3 threads * 5 snapshots each
        
        # Verify all snapshots are in database
        all_snapshots = self.storage.list_snapshots()
        assert len(all_snapshots) == 15


class TestStorageBackendInterface:
    """Test the StorageBackend abstract interface"""
    
    def test_abstract_interface(self):
        """Test that StorageBackend is properly abstract"""
        with pytest.raises(TypeError):
            StorageBackend()
    
    def test_required_methods(self):
        """Test that all required methods are defined"""
        required_methods = [
            'write_snapshot',
            'read_snapshot',
            'list_snapshots',
            'delete_snapshot'
        ]
        
        for method in required_methods:
            assert hasattr(StorageBackend, method)
            assert callable(getattr(StorageBackend, method))