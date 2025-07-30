"""
DataGhost - Main user-facing class for time-travel debugging
"""
from typing import Optional

from .dashboard.server import run_dashboard
from .logger import snapshot
from .storage import DuckDBStorageBackend, StorageBackend


class DataGhost:
    """Main DataGhost class for tracking function executions"""

    def __init__(
        self, storage_backend: Optional[StorageBackend] = None, db_path: str = "dataghost.db"
    ):
        """Initialize DataGhost with optional storage backend"""
        self.storage = storage_backend or DuckDBStorageBackend(db_path)

    def track(self, task_id: str):
        """Decorator to track function execution and create snapshots"""
        return snapshot(task_id=task_id, storage_backend=self.storage)

    def dashboard(self, host: str = "127.0.0.1", port: int = 8080, auto_open: bool = True):
        """Start the DataGhost dashboard"""
        run_dashboard(storage_backend=self.storage, host=host, port=port, auto_open=auto_open)

    def get_snapshots(self, task_id: Optional[str] = None):
        """Get snapshots for a specific task or all tasks"""
        return self.storage.list_snapshots(task_id)

    def get_tasks(self):
        """Get summary of all tracked tasks"""
        snapshots = self.storage.list_snapshots()
        tasks = {}

        for snapshot in snapshots:
            task_id = snapshot.get("task_id", "unknown")
            if task_id not in tasks:
                tasks[task_id] = {
                    "task_id": task_id,
                    "total_runs": 0,
                    "successful_runs": 0,
                    "failed_runs": 0,
                    "latest_run": None,
                }

            tasks[task_id]["total_runs"] += 1
            if snapshot.get("success", False):
                tasks[task_id]["successful_runs"] += 1
            else:
                tasks[task_id]["failed_runs"] += 1

            # Update latest run timestamp
            if snapshot.get("timestamp"):
                if (
                    not tasks[task_id]["latest_run"]
                    or snapshot["timestamp"] > tasks[task_id]["latest_run"]
                ):
                    tasks[task_id]["latest_run"] = snapshot["timestamp"]

        return list(tasks.values())
