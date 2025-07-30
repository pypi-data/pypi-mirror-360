"""
DataGhost - Time-Travel Debugger for Data Pipelines
"""
from ttd.logger import snapshot, get_storage_backend, set_storage_backend
from ttd.storage import DuckDBStorageBackend, StorageBackend
from ttd.replay import ReplayEngine
from ttd.diff import DiffEngine

# Dashboard imports (optional)
try:
    from ttd.dashboard.server import create_dashboard_server, run_dashboard
    _has_dashboard = True
except ImportError:
    _has_dashboard = False

__version__ = "0.1.0"
__all__ = [
    "snapshot", "DuckDBStorageBackend", "StorageBackend", "ReplayEngine", "DiffEngine",
    "get_storage_backend", "set_storage_backend"
]

if _has_dashboard:
    __all__.extend(["create_dashboard_server", "run_dashboard"])