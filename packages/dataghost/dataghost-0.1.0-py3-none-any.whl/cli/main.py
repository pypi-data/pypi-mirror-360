"""
DataGhost CLI Main Module

Command-line interface for DataGhost time-travel debugging functionality.
"""
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table

from ttd.diff import DiffEngine
from ttd.replay import ReplayEngine
from ttd.storage import DuckDBStorageBackend

app = typer.Typer(
    name="dataghost",
    help="DataGhost - Time-Travel Debugger for Data Pipelines",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def snapshot(
    list_all: bool = typer.Option(False, "--list", "-l", help="List all snapshots"),
    task_id: Optional[str] = typer.Option(None, "--task-id", "-t", help="Filter by task ID"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
):
    """List and manage snapshots"""
    if list_all or task_id:
        storage = DuckDBStorageBackend(db_path)
        snapshots = storage.list_snapshots(task_id)

        if not snapshots:
            console.print("[yellow]No snapshots found[/yellow]")
            return

        if format == "json":
            print(json.dumps(snapshots, indent=2, default=str))
        else:
            table = Table(title="DataGhost Snapshots")
            table.add_column("Task ID")
            table.add_column("Run ID")
            table.add_column("Timestamp")
            table.add_column("Duration")
            table.add_column("Success")
            table.add_column("Error")

            for snap in snapshots:
                error_text = (
                    snap.get("error", "")[:50] + "..."
                    if snap.get("error") and len(snap.get("error", "")) > 50
                    else snap.get("error", "")
                )
                table.add_row(
                    snap["task_id"],
                    snap["run_id"],
                    str(snap["timestamp"]),
                    f"{snap['execution_time']:.3f}s",
                    "✓" if snap["success"] else "✗",
                    error_text or "",
                )

            console.print(table)
    else:
        console.print("[yellow]Use --list to see all snapshots or --task-id to filter[/yellow]")


@app.command()
def replay(
    task_id: str = typer.Argument(..., help="Task ID to replay"),
    run_id: Optional[str] = typer.Option(None, "--run-id", "-r", help="Specific run ID"),
    snapshot_id: Optional[str] = typer.Option(
        None, "--snapshot-id", "-s", help="Specific snapshot ID"
    ),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate output matches"),
    sandbox: bool = typer.Option(False, "--sandbox", help="Run in subprocess sandbox"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
):
    """Replay a task from snapshot"""
    try:
        storage = DuckDBStorageBackend(db_path)
        replay_engine = ReplayEngine(storage)

        console.print(f"[blue]Replaying task: {task_id}[/blue]")
        if run_id:
            console.print(f"[blue]Run ID: {run_id}[/blue]")
        if snapshot_id:
            console.print(f"[blue]Snapshot ID: {snapshot_id}[/blue]")

        result = replay_engine.replay(
            task_id=task_id,
            run_id=run_id,
            snapshot_id=snapshot_id,
            validate_output=validate,
            sandbox=sandbox,
        )

        if format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            # Create summary table
            table = Table(title="Replay Results")
            table.add_column("Property")
            table.add_column("Value")

            table.add_row("Task ID", result["task_id"])
            table.add_row("Run ID", result["run_id"])
            table.add_row("Original Success", "✓" if result["original_success"] else "✗")
            table.add_row("Replay Success", "✓" if result["replay_success"] else "✗")
            table.add_row("Outputs Match", "✓" if result.get("outputs_match", False) else "✗")
            table.add_row("Execution Time", f"{result['replay_execution_time']:.3f}s")

            console.print(table)

            # Show errors if any
            if result["replay_error"]:
                console.print(
                    Panel(result["replay_error"], title="Replay Error", border_style="red")
                )
    except Exception as e:
        console.print(f"[red]Error during replay: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def diff(
    task_id: str = typer.Argument(..., help="Task ID to compare"),
    run_id1: Optional[str] = typer.Option(None, "--run-id1", help="First run ID"),
    run_id2: Optional[str] = typer.Option(None, "--run-id2", help="Second run ID"),
    snapshot_id1: Optional[str] = typer.Option(None, "--snapshot-id1", help="First snapshot ID"),
    snapshot_id2: Optional[str] = typer.Option(None, "--snapshot-id2", help="Second snapshot ID"),
    outputs_only: bool = typer.Option(False, "--outputs-only", help="Compare outputs only"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, json)"),
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
):
    """Compare two snapshots"""
    try:
        storage = DuckDBStorageBackend(db_path)
        diff_engine = DiffEngine(storage)

        if snapshot_id1 and snapshot_id2:
            # Direct snapshot comparison
            if outputs_only:
                result = diff_engine.diff_outputs_only(snapshot_id1, snapshot_id2)
            else:
                result = diff_engine.diff_snapshots(snapshot_id1, snapshot_id2)
        else:
            # Task run comparison
            result = diff_engine.diff_task_runs(
                task_id=task_id,
                run_id1=run_id1,
                run_id2=run_id2,
                include_outputs=True,
                include_inputs=not outputs_only,
                include_metadata=not outputs_only,
            )

        if format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            # Generate text report
            if outputs_only:
                console.print("[blue]Outputs Comparison[/blue]")
                console.print(JSON(json.dumps(result, indent=2, default=str)))
            else:
                report = diff_engine.generate_diff_report(result, format="text")
                console.print(report)
    except Exception as e:
        console.print(f"[red]Error during diff: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def tasks(
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
):
    """List all replayable tasks"""
    try:
        storage = DuckDBStorageBackend(db_path)
        replay_engine = ReplayEngine(storage)

        tasks = replay_engine.list_replayable_tasks()

        if not tasks:
            console.print("[yellow]No replayable tasks found[/yellow]")
            return

        if format == "json":
            print(json.dumps(tasks, indent=2, default=str))
        else:
            table = Table(title="Replayable Tasks")
            table.add_column("Task ID")
            table.add_column("Total Runs")
            table.add_column("Successful")
            table.add_column("Failed")
            table.add_column("Latest Run")

            for task_id, task_info in tasks.items():
                table.add_row(
                    task_id,
                    str(task_info["total_runs"]),
                    str(task_info["successful_runs"]),
                    str(task_info["failed_runs"]),
                    str(task_info["latest_run"]),
                )

            console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing tasks: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def init(
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
    data_dir: str = typer.Option("dataghost_data", "--data-dir", help="Data directory"),
):
    """Initialize DataGhost storage"""
    try:
        storage = DuckDBStorageBackend(db_path, data_dir)
        console.print(f"[green]Initialized DataGhost storage:[/green]")
        console.print(f"  Database: {db_path}")
        console.print(f"  Data directory: {data_dir}")
    except Exception as e:
        console.print(f"[red]Error initializing storage: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def clean(
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
    data_dir: str = typer.Option("dataghost_data", "--data-dir", help="Data directory"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt"),
):
    """Clean up DataGhost storage"""
    if not confirm:
        confirm = typer.confirm("This will delete all snapshots and data. Are you sure?")

    if confirm:
        try:
            # Remove database and data directory
            db_file = Path(db_path)
            data_path = Path(data_dir)

            if db_file.exists():
                db_file.unlink()

            if data_path.exists():
                import shutil

                shutil.rmtree(data_path)

            console.print("[green]DataGhost storage cleaned[/green]")
        except Exception as e:
            console.print(f"[red]Error cleaning storage: {str(e)}[/red]")
            sys.exit(1)
    else:
        console.print("[yellow]Operation cancelled[/yellow]")


@app.command()
def dashboard(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run dashboard on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind dashboard to"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Don't auto-open browser"),
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
):
    """Launch the DataGhost web dashboard"""
    try:
        from ttd.dashboard.server import run_dashboard

        storage = DuckDBStorageBackend(db_path)
        console.print(f"[blue]Starting DataGhost Dashboard...[/blue]")
        console.print(f"[blue]Database: {db_path}[/blue]")

        run_dashboard(storage_backend=storage, host=host, port=port, auto_open=not no_browser)
    except ImportError:
        console.print("[red]Dashboard dependencies not installed.[/red]")
        console.print("[yellow]Install with: pip install dataghost[dashboard][/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting dashboard: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def overview(
    db_path: str = typer.Option("dataghost.db", "--db", help="Database path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
):
    """Show comprehensive dashboard overview in terminal"""
    try:
        storage = DuckDBStorageBackend(db_path)
        replay_engine = ReplayEngine(storage)

        # Get all data
        all_snapshots = storage.list_snapshots()
        tasks = replay_engine.list_replayable_tasks()

        if format == "json":
            # Return comprehensive JSON data
            overview_data = {
                "statistics": {
                    "total_snapshots": len(all_snapshots),
                    "total_tasks": len(tasks),
                    "successful_runs": sum(1 for s in all_snapshots if s["success"]),
                    "failed_runs": sum(1 for s in all_snapshots if not s["success"]),
                    "success_rate": (
                        sum(1 for s in all_snapshots if s["success"]) / len(all_snapshots) * 100
                    )
                    if all_snapshots
                    else 0,
                },
                "tasks": tasks,
                "recent_snapshots": all_snapshots[:10],
            }
            print(json.dumps(overview_data, indent=2, default=str))
            return

        # Table format
        console.print("[bold blue]📊 DataGhost Overview[/bold blue]\n")

        # Statistics table
        stats_table = Table(title="Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="magenta")

        total_snapshots = len(all_snapshots)
        successful_runs = sum(1 for s in all_snapshots if s["success"])
        failed_runs = total_snapshots - successful_runs
        success_rate = (successful_runs / total_snapshots * 100) if total_snapshots > 0 else 0

        stats_table.add_row("Total Snapshots", str(total_snapshots))
        stats_table.add_row("Total Tasks", str(len(tasks)))
        stats_table.add_row("Successful Runs", str(successful_runs))
        stats_table.add_row("Failed Runs", str(failed_runs))
        stats_table.add_row("Success Rate", f"{success_rate:.1f}%")

        console.print(stats_table)
        console.print()

        # Task health table
        if tasks:
            health_table = Table(title="Task Health")
            health_table.add_column("Task ID")
            health_table.add_column("Total Runs")
            health_table.add_column("Success Rate")
            health_table.add_column("Latest Run")
            health_table.add_column("Health Status")

            for task_id, task_info in tasks.items():
                success_rate = (task_info["successful_runs"] / task_info["total_runs"]) * 100
                health_status = (
                    "🟢 Healthy"
                    if success_rate >= 90
                    else "🟡 Warning"
                    if success_rate >= 70
                    else "🔴 Critical"
                )

                health_table.add_row(
                    task_id,
                    str(task_info["total_runs"]),
                    f"{success_rate:.1f}%",
                    str(task_info["latest_run"]),
                    health_status,
                )

            console.print(health_table)
            console.print()

        # Recent activity table
        if all_snapshots:
            recent_table = Table(title="Recent Activity (Last 10)")
            recent_table.add_column("Task ID")
            recent_table.add_column("Timestamp")
            recent_table.add_column("Duration")
            recent_table.add_column("Status")

            for snapshot in all_snapshots[:10]:
                status = "✓ Success" if snapshot["success"] else "✗ Failed"
                recent_table.add_row(
                    snapshot["task_id"],
                    str(snapshot["timestamp"]),
                    f"{snapshot['execution_time']:.3f}s",
                    status,
                )

            console.print(recent_table)

        # Dashboard hint
        console.print(f"\n[dim]💡 For interactive dashboard: dataghost dashboard[/dim]")

    except Exception as e:
        console.print(f"[red]Error generating overview: {str(e)}[/red]")
        sys.exit(1)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
