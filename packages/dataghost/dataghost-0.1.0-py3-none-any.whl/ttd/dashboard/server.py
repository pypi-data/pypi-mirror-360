"""
DataGhost Dashboard Server

FastAPI-based web dashboard for visualizing DataGhost snapshots,
tasks, and execution analytics.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..diff import DiffEngine
from ..replay import ReplayEngine
from ..storage import DuckDBStorageBackend, StorageBackend


class DashboardServer:
    """DataGhost Dashboard Server"""

    def __init__(self, storage_backend: Optional[StorageBackend] = None):
        self.storage = storage_backend or DuckDBStorageBackend()
        self.replay_engine = ReplayEngine(self.storage)
        self.diff_engine = DiffEngine(self.storage)
        self.app = FastAPI(title="DataGhost Dashboard", version="0.1.0")

        # Setup templates
        dashboard_dir = Path(__file__).parent
        self.templates = Jinja2Templates(directory=str(dashboard_dir / "templates"))

        # Setup static files - first try React build, then fallback to basic static
        react_build_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
        static_dir = dashboard_dir / "static"

        if react_build_dir.exists():
            # Serve React build assets
            self.app.mount(
                "/assets", StaticFiles(directory=str(react_build_dir / "assets")), name="assets"
            )
        elif static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """Main dashboard page"""
            # Check if React build exists, serve React app if available
            react_build_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
            react_index = react_build_dir / "index.html"

            if react_index.exists():
                with open(react_index, "r") as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                # Fallback to basic template
                return self.templates.TemplateResponse("dashboard.html", {"request": request})

        @self.app.get("/api/overview")
        async def get_overview():
            """Get dashboard overview data"""
            try:
                # Get all snapshots
                all_snapshots = self.storage.list_snapshots()

                # Calculate basic statistics
                total_snapshots = len(all_snapshots)
                successful_runs = sum(1 for s in all_snapshots if s.get("success", False))
                failed_runs = total_snapshots - successful_runs

                # Get task statistics with error handling
                task_health = []
                total_tasks = 0
                try:
                    tasks = self.replay_engine.list_replayable_tasks()
                    total_tasks = len(tasks)

                    # Task health scores
                    for task_id, task_info in tasks.items():
                        if task_info.get("total_runs", 0) > 0:
                            success_rate = (
                                task_info.get("successful_runs", 0) / task_info["total_runs"]
                            ) * 100
                            task_health.append(
                                {
                                    "task_id": task_id,
                                    "total_runs": task_info["total_runs"],
                                    "success_rate": success_rate,
                                    "latest_run": task_info.get("latest_run", ""),
                                }
                            )

                    # Sort by success rate
                    task_health.sort(key=lambda x: x["success_rate"])

                except Exception as e:
                    print(f"Warning: Could not get task statistics: {e}")
                    # Fallback: derive tasks from snapshots
                    task_ids = set(s.get("task_id") for s in all_snapshots if s.get("task_id"))
                    total_tasks = len(task_ids)
                    for task_id in task_ids:
                        task_snapshots = [s for s in all_snapshots if s.get("task_id") == task_id]
                        task_successful = sum(1 for s in task_snapshots if s.get("success", False))
                        success_rate = (
                            (task_successful / len(task_snapshots)) * 100 if task_snapshots else 0
                        )
                        latest_snapshot = max(
                            task_snapshots, key=lambda x: x.get("timestamp", ""), default={}
                        )

                        task_health.append(
                            {
                                "task_id": task_id,
                                "total_runs": len(task_snapshots),
                                "success_rate": success_rate,
                                "latest_run": latest_snapshot.get("timestamp", "").isoformat()
                                if hasattr(latest_snapshot.get("timestamp", ""), "isoformat")
                                else str(latest_snapshot.get("timestamp", "")),
                            }
                        )

                # Serialize recent activity timestamps
                recent_activity = []
                for snapshot in all_snapshots[:10]:
                    activity_item = snapshot.copy()
                    if "timestamp" in activity_item and hasattr(
                        activity_item["timestamp"], "isoformat"
                    ):
                        activity_item["timestamp"] = activity_item["timestamp"].isoformat()
                    recent_activity.append(activity_item)

                return {
                    "statistics": {
                        "total_snapshots": total_snapshots,
                        "total_tasks": total_tasks,
                        "successful_runs": successful_runs,
                        "failed_runs": failed_runs,
                        "success_rate": (successful_runs / total_snapshots * 100)
                        if total_snapshots > 0
                        else 0,
                    },
                    "recent_activity": recent_activity,
                    "task_health": task_health,
                }
            except Exception as e:
                import traceback

                raise HTTPException(
                    status_code=500, detail=f"Overview failed: {str(e)}\n{traceback.format_exc()}"
                )

        @self.app.get("/api/tasks")
        async def get_tasks():
            """Get all tasks with detailed information"""
            try:
                tasks = self.replay_engine.list_replayable_tasks()

                # Add additional task details
                task_details = []
                for task_id, task_info in tasks.items():
                    # Get recent runs for this task
                    task_snapshots = self.storage.list_snapshots(task_id)[:5]

                    # Calculate average execution time
                    if task_snapshots:
                        avg_exec_time = sum(s["execution_time"] for s in task_snapshots) / len(
                            task_snapshots
                        )
                    else:
                        avg_exec_time = 0

                    task_details.append(
                        {
                            "task_id": task_id,
                            "total_runs": task_info["total_runs"],
                            "successful_runs": task_info["successful_runs"],
                            "failed_runs": task_info["failed_runs"],
                            "success_rate": (task_info["successful_runs"] / task_info["total_runs"])
                            * 100,
                            "latest_run": task_info["latest_run"],
                            "avg_execution_time": avg_exec_time,
                            "recent_runs": task_snapshots,
                        }
                    )

                return {"tasks": task_details}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/tasks/{task_id}")
        async def get_task_detail(task_id: str):
            """Get detailed information for a specific task"""
            try:
                # Get all snapshots for this task
                snapshots = self.storage.list_snapshots(task_id)

                if not snapshots:
                    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

                # Calculate statistics
                total_runs = len(snapshots)
                successful_runs = sum(1 for s in snapshots if s["success"])
                failed_runs = total_runs - successful_runs

                # Execution time trends - serialize timestamps
                execution_times = []
                for s in snapshots:
                    timestamp = s["timestamp"]
                    if hasattr(timestamp, "isoformat"):
                        timestamp_str = timestamp.isoformat()
                    else:
                        timestamp_str = str(timestamp)

                    execution_times.append(
                        {
                            "timestamp": timestamp_str,
                            "execution_time": s["execution_time"],
                            "success": s["success"],
                        }
                    )

                # Serialize snapshot timestamps
                serialized_snapshots = []
                for s in snapshots:
                    snapshot_copy = s.copy()
                    if "timestamp" in snapshot_copy and hasattr(
                        snapshot_copy["timestamp"], "isoformat"
                    ):
                        snapshot_copy["timestamp"] = snapshot_copy["timestamp"].isoformat()
                    serialized_snapshots.append(snapshot_copy)

                return {
                    "task_id": task_id,
                    "statistics": {
                        "total_runs": total_runs,
                        "successful_runs": successful_runs,
                        "failed_runs": failed_runs,
                        "success_rate": (successful_runs / total_runs) * 100,
                    },
                    "snapshots": serialized_snapshots,
                    "execution_trends": execution_times,
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/snapshots")
        async def get_snapshots(task_id: Optional[str] = None, limit: int = 50):
            """Get snapshots with optional filtering"""
            try:
                snapshots = self.storage.list_snapshots(task_id)

                # Enhance snapshots with additional metadata
                enhanced_snapshots = []
                for snapshot in snapshots[:limit]:
                    enhanced_snapshot = snapshot.copy()

                    # Serialize timestamp
                    if "timestamp" in enhanced_snapshot and hasattr(
                        enhanced_snapshot["timestamp"], "isoformat"
                    ):
                        enhanced_snapshot["timestamp"] = enhanced_snapshot["timestamp"].isoformat()

                    # Add metadata fields if missing
                    if "metadata" not in enhanced_snapshot:
                        enhanced_snapshot["metadata"] = {}

                    # Estimate record count and size if not available
                    if "record_count" not in enhanced_snapshot["metadata"]:
                        # Try to estimate from data if available
                        if "data" in enhanced_snapshot and hasattr(
                            enhanced_snapshot["data"], "__len__"
                        ):
                            enhanced_snapshot["metadata"]["record_count"] = len(
                                enhanced_snapshot["data"]
                            )
                        else:
                            enhanced_snapshot["metadata"]["record_count"] = 0

                    if "size_bytes" not in enhanced_snapshot["metadata"]:
                        # Estimate size from serialized data
                        try:
                            import json

                            size_estimate = len(
                                json.dumps(enhanced_snapshot.get("data", {}), default=str)
                            )
                            enhanced_snapshot["metadata"]["size_bytes"] = size_estimate
                        except:
                            enhanced_snapshot["metadata"]["size_bytes"] = 0

                    enhanced_snapshots.append(enhanced_snapshot)

                return {"snapshots": enhanced_snapshots}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/snapshots/{snapshot_id}")
        async def get_snapshot_detail(snapshot_id: str):
            """Get detailed information for a specific snapshot"""
            try:
                snapshot = self.storage.read_snapshot(snapshot_id)
                return {"snapshot": snapshot}
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/replay/{task_id}")
        async def replay_task(task_id: str, run_id: Optional[str] = None):
            """Replay a task"""
            try:
                result = self.replay_engine.replay(
                    task_id=task_id, run_id=run_id, validate_output=True
                )
                return {"replay_result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/tasks/{task_id}/export")
        async def export_task_data(task_id: str):
            """Export all data for a specific task"""
            try:
                # Get all snapshots for this task
                snapshots = self.storage.list_snapshots(task_id)

                # Get task details from replay engine
                try:
                    tasks = self.replay_engine.list_replayable_tasks()
                    task_info = tasks.get(task_id, {})
                except Exception as e:
                    # If replay engine fails, create basic task info
                    task_info = {
                        "task_id": task_id,
                        "total_runs": len(snapshots),
                        "successful_runs": len([s for s in snapshots if s.get("success", False)]),
                        "failed_runs": len([s for s in snapshots if not s.get("success", True)]),
                        "error": f"Could not get replay info: {str(e)}",
                    }

                # Serialize timestamps for JSON compatibility
                serialized_snapshots = []
                for snapshot in snapshots:
                    snapshot_copy = snapshot.copy()
                    if "timestamp" in snapshot_copy and hasattr(
                        snapshot_copy["timestamp"], "isoformat"
                    ):
                        snapshot_copy["timestamp"] = snapshot_copy["timestamp"].isoformat()
                    serialized_snapshots.append(snapshot_copy)

                export_data = {
                    "task_id": task_id,
                    "task_info": task_info,
                    "snapshots": serialized_snapshots,
                    "export_timestamp": datetime.now().isoformat(),
                    "total_snapshots": len(snapshots),
                }

                from fastapi.responses import JSONResponse

                return JSONResponse(
                    content=export_data,
                    headers={"Content-Disposition": f"attachment; filename={task_id}_export.json"},
                )
            except Exception as e:
                import traceback

                raise HTTPException(
                    status_code=500, detail=f"Export failed: {str(e)}\n{traceback.format_exc()}"
                )

        @self.app.get("/api/snapshots/{snapshot_id}/export")
        async def export_snapshot_data(snapshot_id: str):
            """Export data for a specific snapshot"""
            try:
                snapshot = self.storage.read_snapshot(snapshot_id)

                # Handle timestamp serialization
                snapshot_copy = snapshot.copy()
                if "timestamp" in snapshot_copy and hasattr(
                    snapshot_copy["timestamp"], "isoformat"
                ):
                    snapshot_copy["timestamp"] = snapshot_copy["timestamp"].isoformat()

                export_data = {
                    "snapshot_id": snapshot_id,
                    "snapshot_data": snapshot_copy,
                    "export_timestamp": datetime.now().isoformat(),
                }

                from fastapi.responses import JSONResponse

                return JSONResponse(
                    content=export_data,
                    headers={
                        "Content-Disposition": f"attachment; filename=snapshot_{snapshot_id[:8]}_export.json"
                    },
                )
            except ValueError as e:
                raise HTTPException(status_code=404, detail=f"Snapshot not found: {str(e)}")
            except Exception as e:
                import traceback

                raise HTTPException(
                    status_code=500, detail=f"Export failed: {str(e)}\n{traceback.format_exc()}"
                )

        @self.app.get("/api/diff/{task_id}")
        async def diff_task_runs(
            task_id: str, run_id1: Optional[str] = None, run_id2: Optional[str] = None
        ):
            """Compare two runs of a task"""
            try:
                result = self.diff_engine.diff_task_runs(
                    task_id=task_id, run_id1=run_id1, run_id2=run_id2
                )
                return {"diff_result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/performance-trends")
        async def get_performance_trends(time_range: str = "24h"):
            """Get performance trends data for charts"""
            try:
                # Calculate time range boundaries
                end_time = datetime.now()
                if time_range == "24h":
                    start_time = end_time - timedelta(hours=24)
                    time_delta = timedelta(hours=1)
                elif time_range == "7d":
                    start_time = end_time - timedelta(days=7)
                    time_delta = timedelta(days=1)
                elif time_range == "30d":
                    start_time = end_time - timedelta(days=30)
                    time_delta = timedelta(days=1)
                else:
                    start_time = end_time - timedelta(hours=24)
                    time_delta = timedelta(hours=1)

                # Get all snapshots from storage
                try:
                    all_snapshots = self.storage.list_snapshots()
                except Exception as e:
                    print(f"Could not get snapshots for trends: {e}")
                    all_snapshots = []

                # Filter snapshots within time range
                relevant_snapshots = []
                for snapshot in all_snapshots:
                    snapshot_time = snapshot.get("timestamp")
                    if snapshot_time:
                        # Handle different timestamp formats
                        if isinstance(snapshot_time, str):
                            try:
                                from dateutil.parser import parse

                                snapshot_time = parse(snapshot_time)
                            except:
                                continue
                        elif hasattr(snapshot_time, "timestamp"):
                            # Already a datetime object
                            pass
                        else:
                            continue

                        if start_time <= snapshot_time <= end_time:
                            relevant_snapshots.append(snapshot)

                # Group snapshots by time buckets
                trends = []
                current_time = start_time

                while current_time <= end_time:
                    bucket_end = current_time + time_delta

                    # Get snapshots in this time bucket
                    bucket_snapshots = []
                    for snapshot in relevant_snapshots:
                        snapshot_time = snapshot.get("timestamp")
                        if isinstance(snapshot_time, str):
                            try:
                                from dateutil.parser import parse

                                snapshot_time = parse(snapshot_time)
                            except:
                                continue

                        if current_time <= snapshot_time < bucket_end:
                            bucket_snapshots.append(snapshot)

                    # Calculate metrics for this bucket
                    total_runs = len(bucket_snapshots)
                    successful_runs = len([s for s in bucket_snapshots if s.get("success", False)])
                    failed_runs = total_runs - successful_runs

                    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

                    # Calculate average duration
                    durations = [
                        s.get("execution_time", 0)
                        for s in bucket_snapshots
                        if s.get("execution_time") is not None
                    ]
                    avg_duration = sum(durations) / len(durations) if durations else 0

                    trends.append(
                        {
                            "timestamp": current_time.isoformat(),
                            "success_rate": round(success_rate, 1),
                            "avg_duration": round(avg_duration, 2),
                            "total_runs": total_runs,
                            "failed_runs": failed_runs,
                        }
                    )

                    current_time = bucket_end

                return {"trends": trends}

            except Exception as e:
                import traceback

                print(f"Performance trends error: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Performance trends failed: {str(e)}")

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def create_dashboard_server(
    storage_backend: Optional[StorageBackend] = None, host: str = "127.0.0.1", port: int = 8080
) -> DashboardServer:
    """Create and configure dashboard server"""
    return DashboardServer(storage_backend)


def run_dashboard(
    storage_backend: Optional[StorageBackend] = None,
    host: str = "127.0.0.1",
    port: int = 8080,
    auto_open: bool = True,
):
    """Run the DataGhost dashboard"""
    import threading
    import time
    import webbrowser

    import uvicorn

    server = create_dashboard_server(storage_backend)

    def open_browser():
        time.sleep(1.5)  # Give server time to start
        if auto_open:
            webbrowser.open(f"http://{host}:{port}")

    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    print(f"🚀 Starting DataGhost Dashboard at http://{host}:{port}")
    print("📊 Dashboard will open automatically in your browser")
    print("🛑 Press Ctrl+C to stop the server")

    try:
        uvicorn.run(server.app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        raise
