"""
DataGhost Replay Module

Provides deterministic task re-execution using historical snapshots.
"""
import importlib
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .storage import DuckDBStorageBackend, StorageBackend


class ReplayEngine:
    """Engine for replaying tasks from snapshots"""

    def __init__(self, storage_backend: Optional[StorageBackend] = None):
        self.storage_backend = storage_backend or DuckDBStorageBackend()

    def replay(
        self,
        task_id: str,
        run_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        validate_output: bool = True,
        sandbox: bool = False,
    ) -> Dict[str, Any]:
        """
        Replay a task using historical snapshot data.

        Args:
            task_id: Task identifier
            run_id: Specific run ID (if not provided, uses latest)
            snapshot_id: Specific snapshot ID (overrides task_id/run_id)
            validate_output: Whether to validate output matches snapshot
            sandbox: Whether to run in subprocess sandbox

        Returns:
            Dictionary containing replay results and comparison
        """
        # Get snapshot data
        if snapshot_id:
            snapshot = self.storage_backend.read_snapshot(snapshot_id)
        else:
            snapshot = self._get_snapshot_by_task_run(task_id, run_id)

        if not snapshot:
            raise ValueError(f"No snapshot found for task_id={task_id}, run_id={run_id}")

        # Extract function information
        func_module = snapshot["metadata"]["module"]
        func_name = snapshot["metadata"]["function_name"]
        inputs = snapshot["inputs"]
        expected_outputs = snapshot["outputs"]

        # Replay the function
        if sandbox:
            result = self._replay_in_sandbox(func_module, func_name, inputs)
        else:
            result = self._replay_in_process(func_module, func_name, inputs)

        # Prepare replay result
        replay_result = {
            "snapshot_id": snapshot["snapshot_id"],
            "task_id": snapshot["task_id"],
            "run_id": snapshot["run_id"],
            "original_timestamp": snapshot["timestamp"],
            "original_success": snapshot["success"],
            "original_error": snapshot["error"],
            "original_outputs": expected_outputs,
            "replay_success": result["success"],
            "replay_error": result["error"],
            "replay_outputs": result["outputs"],
            "replay_execution_time": result["execution_time"],
            "outputs_match": False,
        }

        # Validate output if requested and both executions were successful
        if validate_output and result["success"] and snapshot["success"]:
            replay_result["outputs_match"] = self._compare_outputs(
                expected_outputs, result["outputs"]
            )

        return replay_result

    def _get_snapshot_by_task_run(
        self, task_id: str, run_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Get snapshot by task_id and run_id (or latest if run_id is None)"""
        snapshots = self.storage_backend.list_snapshots(task_id)

        if not snapshots:
            return None

        if run_id:
            for snapshot in snapshots:
                if snapshot["run_id"] == run_id:
                    return self.storage_backend.read_snapshot(snapshot["snapshot_id"])
            return None
        else:
            # Return latest snapshot
            latest = snapshots[0]  # list_snapshots returns sorted by timestamp desc
            return self.storage_backend.read_snapshot(latest["snapshot_id"])

    def _replay_in_process(
        self, func_module: str, func_name: str, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Replay function in current process"""
        import time

        try:
            # Import the module and get the function
            try:
                module = importlib.import_module(func_module)
            except ModuleNotFoundError as e:
                return {
                    "success": False,
                    "error": f"Module '{func_module}' not found: {str(e)}",
                    "outputs": None,
                    "execution_time": 0,
                }

            try:
                func = getattr(module, func_name)
            except AttributeError as e:
                # Try to find similar functions in the module
                available_funcs = [name for name in dir(module) if not name.startswith("_")]
                return {
                    "success": False,
                    "error": f"Function '{func_name}' not found in module '{func_module}'. Available functions: {available_funcs}",
                    "outputs": None,
                    "execution_time": 0,
                }

            # Validate inputs
            if not inputs or not isinstance(inputs, dict):
                return {
                    "success": False,
                    "error": "Invalid inputs format. Expected dictionary with 'args' and 'kwargs'",
                    "outputs": None,
                    "execution_time": 0,
                }

            args = inputs.get("args", [])
            kwargs = inputs.get("kwargs", {})

            # Execute with timing
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            return {
                "success": True,
                "error": None,
                "outputs": result,
                "execution_time": execution_time,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}\nTraceback: {traceback.format_exc()}",
                "outputs": None,
                "execution_time": 0,
            }

    def _replay_in_sandbox(
        self, func_module: str, func_name: str, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Replay function in subprocess sandbox"""
        # Create temporary script for execution
        script_content = f"""
import sys
import time
import cloudpickle
import traceback

# Load inputs
with open('{inputs["temp_file"]}', 'rb') as f:
    inputs = cloudpickle.load(f)

try:
    # Import and execute function
    import {func_module}
    func = getattr({func_module}, '{func_name}')
    
    start_time = time.time()
    result = func(*inputs['args'], **inputs['kwargs'])
    execution_time = time.time() - start_time
    
    # Save result
    output = {{
        'success': True,
        'error': None,
        'outputs': result,
        'execution_time': execution_time
    }}
    
    with open('{inputs["output_file"]}', 'wb') as f:
        cloudpickle.dump(output, f)
        
except Exception as e:
    output = {{
        'success': False,
        'error': str(e),
        'outputs': None,
        'execution_time': 0
    }}
    
    with open('{inputs["output_file"]}', 'wb') as f:
        cloudpickle.dump(output, f)
"""

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as script_file:
            script_path = script_file.name
            script_file.write(script_content)

        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_path = input_file.name
            import cloudpickle

            cloudpickle.dump(inputs, input_file)

        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            output_path = output_file.name

        # Update script with actual file paths
        with open(script_path, "r") as f:
            script_content = f.read()

        script_content = script_content.replace('{inputs["temp_file"]}', input_path)
        script_content = script_content.replace('{inputs["output_file"]}', output_path)

        with open(script_path, "w") as f:
            f.write(script_content)

        try:
            # Run subprocess
            result = subprocess.run(
                [sys.executable, script_path], capture_output=True, text=True, timeout=300
            )

            # Load result
            with open(output_path, "rb") as f:
                import cloudpickle

                output = cloudpickle.load(f)

            return output
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out",
                "outputs": None,
                "execution_time": 0,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Sandbox execution failed: {str(e)}",
                "outputs": None,
                "execution_time": 0,
            }
        finally:
            # Clean up temporary files
            for path in [script_path, input_path, output_path]:
                try:
                    Path(path).unlink()
                except:
                    pass

    def _compare_outputs(self, expected: Any, actual: Any) -> bool:
        """Compare expected and actual outputs"""
        try:
            # Simple equality check first
            if expected == actual:
                return True

            # For complex objects, try deep comparison
            if hasattr(expected, "__dict__") and hasattr(actual, "__dict__"):
                return expected.__dict__ == actual.__dict__

            # For numpy arrays, pandas DataFrames, etc.
            if hasattr(expected, "equals") and callable(expected.equals):
                return expected.equals(actual)

            # For numpy arrays
            if hasattr(expected, "shape") and hasattr(actual, "shape"):
                import numpy as np

                return np.array_equal(expected, actual)

            return False
        except Exception:
            return False

    def list_replayable_tasks(self) -> Dict[str, Any]:
        """List all tasks that can be replayed"""
        snapshots = self.storage_backend.list_snapshots()

        # Group by task_id
        tasks = {}
        for snapshot in snapshots:
            task_id = snapshot["task_id"]
            if task_id not in tasks:
                tasks[task_id] = {
                    "task_id": task_id,
                    "total_runs": 0,
                    "successful_runs": 0,
                    "failed_runs": 0,
                    "latest_run_timestamp": None,
                    "latest_run": None,
                    "runs": [],
                }

            tasks[task_id]["total_runs"] += 1
            if snapshot["success"]:
                tasks[task_id]["successful_runs"] += 1
            else:
                tasks[task_id]["failed_runs"] += 1

            # Track latest run timestamp
            timestamp = snapshot["timestamp"]
            if (
                tasks[task_id]["latest_run_timestamp"] is None
                or timestamp > tasks[task_id]["latest_run_timestamp"]
            ):
                tasks[task_id]["latest_run_timestamp"] = timestamp
                # Convert to string for JSON serialization
                if hasattr(timestamp, "isoformat"):
                    tasks[task_id]["latest_run"] = timestamp.isoformat()
                else:
                    tasks[task_id]["latest_run"] = str(timestamp)

            # Convert timestamp for the run entry
            if hasattr(timestamp, "isoformat"):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = str(timestamp)

            tasks[task_id]["runs"].append(
                {
                    "run_id": snapshot["run_id"],
                    "timestamp": timestamp_str,
                    "success": snapshot["success"],
                    "error": snapshot.get("error"),
                }
            )

        # Remove the internal timestamp objects before returning
        for task in tasks.values():
            del task["latest_run_timestamp"]

        return tasks
