"""
DataGhost Storage Module

Provides pluggable storage backends for snapshot data with DuckDB implementation.
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cloudpickle
import duckdb
import lz4.frame
import pandas as pd


class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def write_snapshot(self, snapshot_data: Dict[str, Any]) -> str:
        """Write snapshot data and return snapshot ID"""
        pass

    @abstractmethod
    def read_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Read snapshot data by ID"""
        pass

    @abstractmethod
    def list_snapshots(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available snapshots, optionally filtered by task_id"""
        pass

    @abstractmethod
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot by ID"""
        pass


class DuckDBStorageBackend(StorageBackend):
    """DuckDB-based storage backend with Parquet files for payloads"""

    def __init__(self, db_path: str = "dataghost.db", data_dir: str = "dataghost_data"):
        self.db_path = Path(db_path)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the DuckDB database with required tables"""
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id VARCHAR PRIMARY KEY,
                    task_id VARCHAR NOT NULL,
                    run_id VARCHAR NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    execution_time DOUBLE NOT NULL,
                    success BOOLEAN NOT NULL,
                    error TEXT,
                    input_hash VARCHAR NOT NULL,
                    inputs_path VARCHAR NOT NULL,
                    outputs_path VARCHAR,
                    metadata_path VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_task_id ON snapshots(task_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON snapshots(timestamp)
            """
            )

            conn.commit()
        finally:
            conn.close()

    def write_snapshot(self, snapshot_data: Dict[str, Any]) -> str:
        """Write snapshot data to DuckDB and separate payload files"""
        snapshot_id = self._generate_snapshot_id(snapshot_data)

        # Create snapshot directory
        snapshot_dir = self.data_dir / snapshot_id
        snapshot_dir.mkdir(exist_ok=True)

        # Save inputs
        inputs_path = snapshot_dir / "inputs.pkl.lz4"
        self._save_compressed_pickle(snapshot_data["inputs"], inputs_path)

        # Save outputs (if successful)
        outputs_path = None
        if snapshot_data["success"] and snapshot_data["outputs"] is not None:
            outputs_path = snapshot_dir / "outputs.pkl.lz4"
            self._save_compressed_pickle(snapshot_data["outputs"], outputs_path)

        # Save metadata
        metadata_path = snapshot_dir / "metadata.pkl.lz4"
        self._save_compressed_pickle(snapshot_data["metadata"], metadata_path)

        # Insert into database
        conn = duckdb.connect(str(self.db_path))
        try:
            conn.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, task_id, run_id, timestamp, execution_time,
                    success, error, input_hash, inputs_path, outputs_path, metadata_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot_id,
                    snapshot_data["task_id"],
                    snapshot_data["run_id"],
                    datetime.fromisoformat(snapshot_data["timestamp"]),
                    snapshot_data["execution_time"],
                    snapshot_data["success"],
                    snapshot_data.get("error"),
                    snapshot_data["input_hash"],
                    str(inputs_path),
                    str(outputs_path) if outputs_path else None,
                    str(metadata_path),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return snapshot_id

    def read_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Read snapshot data by ID"""
        conn = duckdb.connect(str(self.db_path))
        try:
            result = conn.execute(
                """
                SELECT * FROM snapshots WHERE snapshot_id = ?
            """,
                (snapshot_id,),
            ).fetchone()

            if not result:
                raise ValueError(f"Snapshot {snapshot_id} not found")

            # Convert to dict
            columns = [desc[0] for desc in conn.description]
            snapshot_meta = dict(zip(columns, result))

            # Load payload files
            inputs = self._load_compressed_pickle(snapshot_meta["inputs_path"])

            outputs = None
            if snapshot_meta["outputs_path"]:
                outputs = self._load_compressed_pickle(snapshot_meta["outputs_path"])

            metadata = self._load_compressed_pickle(snapshot_meta["metadata_path"])

            return {
                "snapshot_id": snapshot_meta["snapshot_id"],
                "task_id": snapshot_meta["task_id"],
                "run_id": snapshot_meta["run_id"],
                "timestamp": snapshot_meta["timestamp"].isoformat(),
                "execution_time": snapshot_meta["execution_time"],
                "success": snapshot_meta["success"],
                "error": snapshot_meta["error"],
                "input_hash": snapshot_meta["input_hash"],
                "inputs": inputs,
                "outputs": outputs,
                "metadata": metadata,
            }
        finally:
            conn.close()

    def list_snapshots(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available snapshots"""
        conn = duckdb.connect(str(self.db_path))
        try:
            if task_id:
                query = """
                    SELECT snapshot_id, task_id, run_id, timestamp, execution_time, success, error
                    FROM snapshots 
                    WHERE task_id = ? 
                    ORDER BY timestamp DESC
                """
                results = conn.execute(query, (task_id,)).fetchall()
            else:
                query = """
                    SELECT snapshot_id, task_id, run_id, timestamp, execution_time, success, error
                    FROM snapshots 
                    ORDER BY timestamp DESC
                """
                results = conn.execute(query).fetchall()

            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in results]
        finally:
            conn.close()

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot by ID"""
        conn = duckdb.connect(str(self.db_path))
        try:
            # Get snapshot info first
            result = conn.execute(
                """
                SELECT inputs_path, outputs_path, metadata_path 
                FROM snapshots WHERE snapshot_id = ?
            """,
                (snapshot_id,),
            ).fetchone()

            if not result:
                return False

            # Delete files
            snapshot_dir = self.data_dir / snapshot_id
            if snapshot_dir.exists():
                import shutil

                shutil.rmtree(snapshot_dir)

            # Delete from database
            conn.execute("DELETE FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
            conn.commit()

            return True
        finally:
            conn.close()

    def _generate_snapshot_id(self, snapshot_data: Dict[str, Any]) -> str:
        """Generate unique snapshot ID"""
        timestamp = datetime.fromisoformat(snapshot_data["timestamp"])
        return f"{snapshot_data['task_id']}_{snapshot_data['run_id']}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

    def _save_compressed_pickle(self, data: Any, path: Path):
        """Save data as compressed pickle"""
        pickled = cloudpickle.dumps(data)
        compressed = lz4.frame.compress(pickled)
        path.write_bytes(compressed)

    def _load_compressed_pickle(self, path: Union[str, Path]) -> Any:
        """Load data from compressed pickle"""
        compressed = Path(path).read_bytes()
        pickled = lz4.frame.decompress(compressed)
        return cloudpickle.loads(pickled)


class S3StorageBackend(StorageBackend):
    """S3-compatible storage backend (placeholder for future implementation)"""

    def __init__(self, bucket: str, prefix: str = "dataghost/", **kwargs):
        self.bucket = bucket
        self.prefix = prefix
        self.s3_kwargs = kwargs
        raise NotImplementedError("S3 backend not yet implemented")

    def write_snapshot(self, snapshot_data: Dict[str, Any]) -> str:
        raise NotImplementedError("S3 backend not yet implemented")

    def read_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        raise NotImplementedError("S3 backend not yet implemented")

    def list_snapshots(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("S3 backend not yet implemented")

    def delete_snapshot(self, snapshot_id: str) -> bool:
        raise NotImplementedError("S3 backend not yet implemented")
