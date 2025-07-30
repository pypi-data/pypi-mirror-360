"""
DataGhost Airflow Integration

Provides integration with Apache Airflow for automatic snapshot capture
of PythonOperator tasks and custom operators.
"""
from datetime import datetime
from typing import Any, Callable, Dict, Optional

try:
    from airflow import DAG
    from airflow.models import BaseOperator
    from airflow.operators.python import PythonOperator
    from airflow.utils.decorators import apply_defaults

    HAS_AIRFLOW = True
except ImportError:
    HAS_AIRFLOW = False
    BaseOperator = object  # Fallback for when Airflow is not available

from ..logger import snapshot
from ..storage import DuckDBStorageBackend, StorageBackend


class DataGhostPythonOperator(BaseOperator):
    """
    DataGhost-enabled PythonOperator that automatically captures snapshots.

    This operator wraps the standard PythonOperator functionality while
    automatically applying the @snapshot decorator to capture execution data.
    """

    template_fields = ("python_callable", "op_args", "op_kwargs")

    def __init__(
        self,
        python_callable: Callable,
        op_args: Optional[list] = None,
        op_kwargs: Optional[dict] = None,
        storage_backend: Optional[StorageBackend] = None,
        capture_context: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.python_callable = python_callable
        self.op_args = op_args or []
        self.op_kwargs = op_kwargs or {}
        self.storage_backend = storage_backend or DuckDBStorageBackend()
        self.capture_context = capture_context

        # Wrap the callable with snapshot decorator
        self.wrapped_callable = self._wrap_with_snapshot()

    def _wrap_with_snapshot(self) -> Callable:
        """Wrap the python_callable with DataGhost snapshot decorator"""

        @snapshot(
            task_id=self.task_id,
            storage_backend=self.storage_backend,
            capture_env=True,
            capture_system=True,
        )
        def wrapper(*args, **kwargs):
            # Add Airflow context to metadata if requested
            if self.capture_context and "context" in kwargs:
                context = kwargs["context"]

                # Extract useful Airflow context information
                airflow_metadata = {
                    "dag_id": context.get("dag").dag_id if context.get("dag") else None,
                    "task_id": context.get("task_instance").task_id
                    if context.get("task_instance")
                    else None,
                    "execution_date": str(context.get("execution_date")),
                    "dag_run_id": context.get("dag_run").run_id if context.get("dag_run") else None,
                    "try_number": context.get("task_instance").try_number
                    if context.get("task_instance")
                    else None,
                    "max_tries": context.get("task_instance").max_tries
                    if context.get("task_instance")
                    else None,
                }

                # Store in a way that the snapshot decorator can access
                wrapper._airflow_metadata = airflow_metadata

            return self.python_callable(*args, **kwargs)

        return wrapper

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the wrapped callable"""
        # Prepare arguments
        args = self.op_args.copy() if self.op_args else []
        kwargs = self.op_kwargs.copy() if self.op_kwargs else {}

        # Add context if the callable expects it
        if self.capture_context:
            kwargs["context"] = context

        # Execute the wrapped function
        return self.wrapped_callable(*args, **kwargs)


def create_datahost_dag(
    dag_id: str,
    default_args: Dict[str, Any],
    schedule_interval: Optional[str] = None,
    storage_backend: Optional[StorageBackend] = None,
    **dag_kwargs,
) -> DAG:
    """
    Create a DAG with DataGhost snapshot capture enabled by default.

    Args:
        dag_id: DAG identifier
        default_args: Default arguments for the DAG
        schedule_interval: Schedule interval for the DAG
        storage_backend: Storage backend for snapshots
        **dag_kwargs: Additional arguments for the DAG

    Returns:
        DAG instance with DataGhost integration
    """
    if not HAS_AIRFLOW:
        raise ImportError("Apache Airflow is required for DAG creation")

    # Create the DAG
    dag = DAG(
        dag_id=dag_id, default_args=default_args, schedule_interval=schedule_interval, **dag_kwargs
    )

    # Store the storage backend for use by operators
    dag._dataghost_storage_backend = storage_backend or DuckDBStorageBackend()

    return dag


def snapshot_task(
    task_id: str,
    python_callable: Callable,
    dag: DAG,
    op_args: Optional[list] = None,
    op_kwargs: Optional[dict] = None,
    **operator_kwargs,
) -> DataGhostPythonOperator:
    """
    Create a DataGhost-enabled task within a DAG.

    Args:
        task_id: Task identifier
        python_callable: Function to execute
        dag: DAG to add the task to
        op_args: Arguments for the callable
        op_kwargs: Keyword arguments for the callable
        **operator_kwargs: Additional operator arguments

    Returns:
        DataGhostPythonOperator instance
    """
    storage_backend = getattr(dag, "_dataghost_storage_backend", None)

    return DataGhostPythonOperator(
        task_id=task_id,
        python_callable=python_callable,
        dag=dag,
        op_args=op_args,
        op_kwargs=op_kwargs,
        storage_backend=storage_backend,
        **operator_kwargs,
    )


def patch_python_operator(storage_backend: Optional[StorageBackend] = None):
    """
    Monkey patch PythonOperator to automatically capture snapshots.

    WARNING: This modifies the global PythonOperator class and should be
    used with caution. It's recommended to use DataGhostPythonOperator instead.

    Args:
        storage_backend: Storage backend for snapshots
    """
    if not HAS_AIRFLOW:
        raise ImportError("Apache Airflow is required for patching")

    original_execute = PythonOperator.execute
    default_storage = storage_backend or DuckDBStorageBackend()

    def patched_execute(self, context: Dict[str, Any]) -> Any:
        # Wrap the python_callable with snapshot decorator
        @snapshot(
            task_id=self.task_id,
            storage_backend=default_storage,
            capture_env=True,
            capture_system=True,
        )
        def wrapped_callable(*args, **kwargs):
            return self.python_callable(*args, **kwargs)

        # Temporarily replace the callable
        original_callable = self.python_callable
        self.python_callable = wrapped_callable

        try:
            # Execute with the wrapped callable
            return original_execute(self, context)
        finally:
            # Restore the original callable
            self.python_callable = original_callable

    # Apply the patch
    PythonOperator.execute = patched_execute


class DataGhostAirflowPlugin:
    """
    Airflow plugin for DataGhost integration.

    This plugin can be used to register DataGhost components with Airflow's
    plugin system for better integration.
    """

    name = "DataGhost"
    operators = [DataGhostPythonOperator]
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []


# Example usage functions
def example_airflow_task(name: str, multiplier: int = 2) -> dict:
    """Example function for Airflow task"""
    import random
    import time

    print(f"Processing task: {name}")
    time.sleep(0.1)  # Simulate work

    result = {
        "name": name,
        "result": random.randint(1, 100) * multiplier,
        "timestamp": datetime.now().isoformat(),
    }

    print(f"Task completed: {result}")
    return result


def create_example_dag() -> DAG:
    """Create an example DAG with DataGhost integration"""
    if not HAS_AIRFLOW:
        raise ImportError("Apache Airflow is required for DAG creation")

    default_args = {
        "owner": "dataghost",
        "depends_on_past": False,
        "start_date": datetime(2024, 1, 1),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
    }

    dag = create_datahost_dag(
        dag_id="dataghost_example",
        default_args=default_args,
        description="Example DAG with DataGhost snapshot capture",
        schedule_interval="@daily",
        catchup=False,
        tags=["example", "dataghost"],
    )

    # Task 1: Process data
    task1 = snapshot_task(
        task_id="process_data",
        python_callable=example_airflow_task,
        dag=dag,
        op_args=["data_processing"],
        op_kwargs={"multiplier": 3},
    )

    # Task 2: Validate results
    task2 = snapshot_task(
        task_id="validate_results",
        python_callable=example_airflow_task,
        dag=dag,
        op_args=["validation"],
        op_kwargs={"multiplier": 1},
    )

    # Task 3: Export results
    task3 = snapshot_task(
        task_id="export_results",
        python_callable=example_airflow_task,
        dag=dag,
        op_args=["export"],
        op_kwargs={"multiplier": 2},
    )

    # Set dependencies
    task1 >> task2 >> task3

    return dag


# Global DAG instance for Airflow to discover
if HAS_AIRFLOW:
    try:
        example_dag = create_example_dag()
    except Exception as e:
        print(f"Could not create example DAG: {e}")
        example_dag = None
else:
    example_dag = None
