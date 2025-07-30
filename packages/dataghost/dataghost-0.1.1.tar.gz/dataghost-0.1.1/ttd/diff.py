"""
DataGhost Diff Module

Provides structured comparison of snapshot outputs and execution metadata.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

try:
    from deepdiff import DeepDiff

    HAS_DEEPDIFF = True
except ImportError:
    HAS_DEEPDIFF = False

from .storage import DuckDBStorageBackend, StorageBackend


class DiffEngine:
    """Engine for comparing snapshots and generating structured diffs"""

    def __init__(self, storage_backend: Optional[StorageBackend] = None):
        self.storage_backend = storage_backend or DuckDBStorageBackend()

    def diff_snapshots(
        self,
        snapshot_id1: str,
        snapshot_id2: str,
        include_metadata: bool = True,
        include_inputs: bool = True,
        include_outputs: bool = True,
        deep_diff: bool = True,
    ) -> Dict[str, Any]:
        """
        Compare two snapshots and generate structured diff.

        Args:
            snapshot_id1: First snapshot ID
            snapshot_id2: Second snapshot ID
            include_metadata: Whether to include metadata diff
            include_inputs: Whether to include inputs diff
            include_outputs: Whether to include outputs diff
            deep_diff: Whether to use deep diff for complex objects

        Returns:
            Dictionary containing structured diff results
        """
        # Load snapshots
        snapshot1 = self.storage_backend.read_snapshot(snapshot_id1)
        snapshot2 = self.storage_backend.read_snapshot(snapshot_id2)

        diff_result = {
            "snapshot1": {
                "id": snapshot1["snapshot_id"],
                "task_id": snapshot1["task_id"],
                "run_id": snapshot1["run_id"],
                "timestamp": snapshot1["timestamp"],
                "success": snapshot1["success"],
            },
            "snapshot2": {
                "id": snapshot2["snapshot_id"],
                "task_id": snapshot2["task_id"],
                "run_id": snapshot2["run_id"],
                "timestamp": snapshot2["timestamp"],
                "success": snapshot2["success"],
            },
            "execution_diff": self._diff_execution_metadata(snapshot1, snapshot2),
            "diffs": {},
        }

        # Compare inputs
        if include_inputs:
            diff_result["diffs"]["inputs"] = self._diff_values(
                snapshot1["inputs"], snapshot2["inputs"], deep_diff
            )

        # Compare outputs
        if include_outputs:
            diff_result["diffs"]["outputs"] = self._diff_values(
                snapshot1["outputs"], snapshot2["outputs"], deep_diff
            )

        # Compare metadata
        if include_metadata:
            diff_result["diffs"]["metadata"] = self._diff_values(
                snapshot1["metadata"], snapshot2["metadata"], deep_diff
            )

        # Add summary
        diff_result["summary"] = self._generate_diff_summary(diff_result)

        return diff_result

    def diff_task_runs(
        self, task_id: str, run_id1: Optional[str] = None, run_id2: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Compare two runs of the same task.

        Args:
            task_id: Task identifier
            run_id1: First run ID (if None, uses latest)
            run_id2: Second run ID (if None, uses second latest)
            **kwargs: Additional arguments for diff_snapshots

        Returns:
            Dictionary containing structured diff results
        """
        # Get snapshots for the task
        snapshots = self.storage_backend.list_snapshots(task_id)

        if len(snapshots) < 2:
            raise ValueError(f"Task {task_id} has fewer than 2 snapshots")

        # Find the appropriate snapshots
        if run_id1 is None:
            snapshot1_id = snapshots[0]["snapshot_id"]  # Latest
        else:
            snapshot1_id = self._find_snapshot_id_by_run(snapshots, run_id1)

        if run_id2 is None:
            snapshot2_id = snapshots[1]["snapshot_id"]  # Second latest
        else:
            snapshot2_id = self._find_snapshot_id_by_run(snapshots, run_id2)

        return self.diff_snapshots(snapshot1_id, snapshot2_id, **kwargs)

    def diff_outputs_only(
        self, snapshot_id1: str, snapshot_id2: str, deep_diff: bool = True
    ) -> Dict[str, Any]:
        """Quick diff of outputs only"""
        snapshot1 = self.storage_backend.read_snapshot(snapshot_id1)
        snapshot2 = self.storage_backend.read_snapshot(snapshot_id2)

        return {
            "snapshot1_id": snapshot_id1,
            "snapshot2_id": snapshot_id2,
            "outputs_diff": self._diff_values(
                snapshot1["outputs"], snapshot2["outputs"], deep_diff
            ),
        }

    def _diff_execution_metadata(
        self, snapshot1: Dict[str, Any], snapshot2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare execution-level metadata"""
        return {
            "execution_time_diff": snapshot2["execution_time"] - snapshot1["execution_time"],
            "success_change": {"from": snapshot1["success"], "to": snapshot2["success"]},
            "error_change": {"from": snapshot1.get("error"), "to": snapshot2.get("error")},
            "time_difference": self._calculate_time_difference(
                snapshot1["timestamp"], snapshot2["timestamp"]
            ),
        }

    def _diff_values(self, value1: Any, value2: Any, deep_diff: bool = True) -> Dict[str, Any]:
        """Compare two values and return structured diff"""
        if value1 == value2:
            return {"type": "identical", "equal": True, "summary": "Values are identical"}

        # Basic type comparison
        type1, type2 = type(value1).__name__, type(value2).__name__

        if type1 != type2:
            return {
                "type": "type_change",
                "equal": False,
                "type1": type1,
                "type2": type2,
                "value1": self._serialize_for_diff(value1),
                "value2": self._serialize_for_diff(value2),
                "summary": f"Type changed from {type1} to {type2}",
            }

        # Use DeepDiff if available and requested
        if deep_diff and HAS_DEEPDIFF:
            return self._deep_diff_values(value1, value2)
        else:
            return self._simple_diff_values(value1, value2)

    def _deep_diff_values(self, value1: Any, value2: Any) -> Dict[str, Any]:
        """Use DeepDiff for comprehensive comparison"""
        diff = DeepDiff(value1, value2, ignore_order=True)

        if not diff:
            return {"type": "identical", "equal": True, "summary": "Values are identical"}

        # Convert DeepDiff result to our format
        result = {
            "type": "deep_diff",
            "equal": False,
            "deepdiff": diff,
            "summary": self._summarize_deep_diff(diff),
        }

        return result

    def _simple_diff_values(self, value1: Any, value2: Any) -> Dict[str, Any]:
        """Simple value comparison without DeepDiff"""
        serialized1 = self._serialize_for_diff(value1)
        serialized2 = self._serialize_for_diff(value2)

        return {
            "type": "value_change",
            "equal": False,
            "value1": serialized1,
            "value2": serialized2,
            "summary": f"Value changed from {serialized1} to {serialized2}",
        }

    def _serialize_for_diff(self, value: Any) -> Any:
        """Serialize complex objects for diff display"""
        try:
            # Try JSON serialization first
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            # Fall back to string representation
            return str(value)

    def _summarize_deep_diff(self, diff: Dict[str, Any]) -> str:
        """Create human-readable summary of DeepDiff results"""
        changes = []

        if "values_changed" in diff:
            changes.append(f"{len(diff['values_changed'])} values changed")

        if "dictionary_item_added" in diff:
            changes.append(f"{len(diff['dictionary_item_added'])} items added")

        if "dictionary_item_removed" in diff:
            changes.append(f"{len(diff['dictionary_item_removed'])} items removed")

        if "iterable_item_added" in diff:
            changes.append(f"{len(diff['iterable_item_added'])} items added to lists")

        if "iterable_item_removed" in diff:
            changes.append(f"{len(diff['iterable_item_removed'])} items removed from lists")

        if "type_changes" in diff:
            changes.append(f"{len(diff['type_changes'])} type changes")

        return "; ".join(changes) if changes else "No significant changes detected"

    def _calculate_time_difference(self, timestamp1: str, timestamp2: str) -> Dict[str, Any]:
        """Calculate time difference between two timestamps"""
        dt1 = datetime.fromisoformat(timestamp1)
        dt2 = datetime.fromisoformat(timestamp2)
        diff = dt2 - dt1

        return {
            "seconds": diff.total_seconds(),
            "human_readable": str(diff),
            "direction": "forward" if diff.total_seconds() > 0 else "backward",
        }

    def _find_snapshot_id_by_run(self, snapshots: List[Dict[str, Any]], run_id: str) -> str:
        """Find snapshot ID by run ID"""
        for snapshot in snapshots:
            if snapshot["run_id"] == run_id:
                return snapshot["snapshot_id"]
        raise ValueError(f"Run ID {run_id} not found")

    def _generate_diff_summary(self, diff_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of diff results"""
        summary = {
            "total_differences": 0,
            "sections_with_changes": [],
            "execution_changed": False,
            "success_changed": False,
        }

        # Check execution changes
        exec_diff = diff_result["execution_diff"]
        if (
            exec_diff["success_change"]["from"] != exec_diff["success_change"]["to"]
            or exec_diff["error_change"]["from"] != exec_diff["error_change"]["to"]
        ):
            summary["execution_changed"] = True
            summary["success_changed"] = (
                exec_diff["success_change"]["from"] != exec_diff["success_change"]["to"]
            )

        # Check section changes
        for section, diff_data in diff_result["diffs"].items():
            if not diff_data.get("equal", True):
                summary["sections_with_changes"].append(section)
                summary["total_differences"] += 1

        return summary

    def generate_diff_report(self, diff_result: Dict[str, Any], format: str = "text") -> str:
        """Generate formatted diff report"""
        if format == "json":
            return json.dumps(diff_result, indent=2, default=str)

        # Text format
        report = []
        report.append("=== DataGhost Snapshot Diff Report ===")
        report.append("")

        # Basic info
        report.append(f"Snapshot 1: {diff_result['snapshot1']['id']}")
        report.append(f"  Task: {diff_result['snapshot1']['task_id']}")
        report.append(f"  Run: {diff_result['snapshot1']['run_id']}")
        report.append(f"  Time: {diff_result['snapshot1']['timestamp']}")
        report.append(f"  Success: {diff_result['snapshot1']['success']}")
        report.append("")

        report.append(f"Snapshot 2: {diff_result['snapshot2']['id']}")
        report.append(f"  Task: {diff_result['snapshot2']['task_id']}")
        report.append(f"  Run: {diff_result['snapshot2']['run_id']}")
        report.append(f"  Time: {diff_result['snapshot2']['timestamp']}")
        report.append(f"  Success: {diff_result['snapshot2']['success']}")
        report.append("")

        # Summary
        summary = diff_result["summary"]
        report.append("=== Summary ===")
        report.append(f"Total differences: {summary['total_differences']}")
        report.append(f"Sections with changes: {', '.join(summary['sections_with_changes'])}")
        report.append(f"Execution changed: {summary['execution_changed']}")
        report.append(f"Success status changed: {summary['success_changed']}")
        report.append("")

        # Detailed diffs
        for section, diff_data in diff_result["diffs"].items():
            if not diff_data.get("equal", True):
                report.append(f"=== {section.title()} Changes ===")
                report.append(f"Summary: {diff_data.get('summary', 'No summary available')}")
                report.append("")

        return "\n".join(report)
