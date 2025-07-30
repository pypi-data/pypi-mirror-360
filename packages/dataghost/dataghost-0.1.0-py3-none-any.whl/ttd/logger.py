"""
DataGhost Logger Module

Provides the main snapshot decorator for capturing task metadata,
inputs, outputs, and execution context.
"""
import hashlib
import inspect
import os
import platform
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

import cloudpickle
import psutil

from .storage import DuckDBStorageBackend, StorageBackend


class SnapshotManager:
    """Manages snapshot configuration and storage backend"""

    def __init__(self, storage_backend: Optional[StorageBackend] = None):
        self.storage_backend = storage_backend or DuckDBStorageBackend()

    def set_storage_backend(self, backend: StorageBackend):
        """Set the storage backend"""
        self.storage_backend = backend


# Global snapshot manager instance
_snapshot_manager = SnapshotManager()


def snapshot(
    task_id: Optional[str] = None,
    capture_env: bool = True,
    capture_system: bool = True,
    storage_backend: Optional[StorageBackend] = None,
):
    """
    Decorator to capture function execution snapshots.

    Args:
        task_id: Optional task identifier. If None, uses function name
        capture_env: Whether to capture environment variables
        capture_system: Whether to capture system information
        storage_backend: Optional storage backend override
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided storage backend or global one
            backend = storage_backend or _snapshot_manager.storage_backend

            # Generate task_id if not provided
            actual_task_id = task_id or func.__name__

            # Capture input arguments
            inputs = {"args": args, "kwargs": kwargs}

            # Get function source code for hashing
            try:
                source = inspect.getsource(func)
            except OSError:
                # Function might be defined in REPL or dynamically
                source = f"{func.__module__}.{func.__name__}"

            # Create input hash
            input_hash = _create_input_hash(source, args, kwargs)

            # Capture metadata
            metadata = _capture_metadata(func, capture_env, capture_system)

            # Execute function and capture timing
            start_time = time.time()
            start_timestamp = datetime.utcnow()

            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time

                # Create snapshot data
                snapshot_data = {
                    "task_id": actual_task_id,
                    "run_id": _generate_run_id(),
                    "timestamp": start_timestamp.isoformat(),
                    "execution_time": execution_time,
                    "success": success,
                    "error": error,
                    "input_hash": input_hash,
                    "inputs": inputs,
                    "outputs": result,
                    "metadata": metadata,
                }

                # Store snapshot
                backend.write_snapshot(snapshot_data)

            return result

        return wrapper

    return decorator


def _create_input_hash(source: str, args: Tuple, kwargs: Dict) -> str:
    """Create SHA256 hash of function source and inputs"""
    hash_content = {"source": source, "args": args, "kwargs": kwargs}
    serialized = cloudpickle.dumps(hash_content)
    return hashlib.sha256(serialized).hexdigest()


def _generate_run_id() -> str:
    """Generate unique run ID based on timestamp and process ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    return f"{timestamp}_{os.getpid()}"


def _capture_metadata(func: Callable, capture_env: bool, capture_system: bool) -> Dict[str, Any]:
    """Capture execution metadata"""
    metadata = {
        "function_name": func.__name__,
        "module": func.__module__,
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    if capture_system:
        metadata.update(
            {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
            }
        )

    if capture_env:
        # Capture relevant environment variables (avoid sensitive ones)
        safe_env_vars = [
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "TERM",
            "LANG",
            "LC_ALL",
            "PYTHONPATH",
            "VIRTUAL_ENV",
            "CONDA_ENV",
            "AIRFLOW_HOME",
        ]
        env_vars = {var: os.environ.get(var) for var in safe_env_vars if var in os.environ}
        metadata["environment"] = env_vars

    # Try to capture Git information
    try:
        import subprocess

        git_sha = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
        metadata["git_sha"] = git_sha
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return metadata


def set_storage_backend(backend: StorageBackend):
    """Set global storage backend"""
    _snapshot_manager.set_storage_backend(backend)


def get_storage_backend() -> StorageBackend:
    """Get current storage backend"""
    return _snapshot_manager.storage_backend
