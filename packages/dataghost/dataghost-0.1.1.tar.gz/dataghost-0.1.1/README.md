# DataGhost 👻

> **Time-Travel Debugger for Data Pipelines**

Debug your data pipelines like you debug your code. DataGhost captures complete execution snapshots, enables precise replay of historical runs, and provides rich comparison tools - all with zero configuration.

[![PyPI version](https://badge.fury.io/py/dataghost.svg)](https://badge.fury.io/py/dataghost)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Downloads](https://pepy.tech/badge/dataghost)](https://pepy.tech/project/dataghost)

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install dataghost

# With dashboard support
pip install dataghost[dashboard]

# For Google Colab/Jupyter
pip install dataghost[colab]
```

### 30-Second Demo

```python
from ttd import snapshot

@snapshot(task_id="my_pipeline")
def process_data(data: list, multiplier: int = 2) -> dict:
    processed = [x * multiplier for x in data]
    return {
        "processed_data": processed,
        "count": len(processed),
        "average": sum(processed) / len(processed)
    }

# Run your function normally - snapshots are captured automatically
result = process_data([1, 2, 3, 4, 5], multiplier=3)
```

### View Your Data

```bash
# See all your pipeline runs
dataghost overview

# Launch interactive dashboard
dataghost dashboard

# For Google Colab (creates public URL)
dataghost dashboard --tunnel
```

---

## ✨ Key Features

### 🎯 **Zero-Config Snapshots**
Just add `@snapshot` decorator - no setup required. Captures inputs, outputs, metadata, and execution context automatically.

### 🔄 **Time-Travel Debugging**
Replay any historical execution with identical conditions. Perfect for debugging failures and testing changes.

### 📊 **Rich Comparisons**
Compare runs side-by-side with structured diffing. See exactly what changed between executions.

### 🌐 **Cloud-Ready**
Works seamlessly in Google Colab, Jupyter notebooks, and remote environments with automatic tunnel support.

### 📱 **Beautiful Dashboard**
Interactive web interface with real-time monitoring, performance analytics, and one-click operations.

### 🏗️ **Framework Integration**
First-class support for Apache Airflow, with more integrations coming soon.

---

## 🎮 Interactive Demo

Try DataGhost in your browser:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dataghost/dataghost/blob/main/examples/colab_demo.ipynb)

---

## 📖 Complete Guide

### 1. Basic Usage

#### Capture Snapshots

```python
from ttd import snapshot

@snapshot(task_id="data_processing")
def transform_data(raw_data: list, config: dict) -> dict:
    # Your data processing logic
    filtered = [x for x in raw_data if x > config['threshold']]
    return {
        "filtered_count": len(filtered),
        "data": filtered,
        "metadata": {"threshold": config['threshold']}
    }

# Every call is automatically captured
result = transform_data([1, 5, 10, 2, 8], {"threshold": 4})
```

#### Advanced Snapshot Options

```python
@snapshot(
    task_id="advanced_task",
    capture_env=True,        # Capture environment variables
    capture_system=True,     # Capture system info
    storage_backend=None     # Use custom storage
)
def advanced_processing(data):
    return process_complex_data(data)
```

### 2. Command Line Interface

#### Overview & Monitoring

```bash
# Comprehensive dashboard overview
dataghost overview

# List all captured snapshots
dataghost snapshot --list

# List snapshots for specific task
dataghost snapshot --task-id my_task

# Show all replayable tasks
dataghost tasks
```

#### Debugging & Replay

```bash
# Replay latest run of a task
dataghost replay my_task

# Replay specific run
dataghost replay my_task --run-id 20241201_143022

# Replay with validation
dataghost replay my_task --validate
```

#### Comparison & Analysis

```bash
# Compare latest two runs
dataghost diff my_task

# Compare specific runs
dataghost diff my_task --run-id1 run1 --run-id2 run2

# Output comparison as JSON
dataghost diff my_task --format json
```

### 3. Interactive Dashboard

#### Local Development

```bash
# Start dashboard (opens browser automatically)
dataghost dashboard

# Custom port and host
dataghost dashboard --port 3000 --host 0.0.0.0

# Run without opening browser
dataghost dashboard --no-browser
```

#### Cloud Environments

```bash
# Auto-detects Colab/Jupyter and creates public tunnel
dataghost dashboard --tunnel

# Use specific tunnel service
dataghost dashboard --tunnel --tunnel-service localtunnel
```

#### Dashboard Features

- **📊 Real-time Overview**: Live statistics and health metrics
- **🎯 Task Health Monitoring**: Success rates and performance trends  
- **⚡ Recent Activity**: Latest pipeline executions with filtering
- **📋 Interactive Task Management**: Browse, replay, and compare runs
- **🔄 One-click Operations**: Replay tasks directly from the UI
- **📊 Visual Diffs**: Side-by-side run comparisons
- **🔍 Detailed Snapshots**: Drill down into execution details
- **📈 Performance Analytics**: Execution time trends and statistics
- **📱 Mobile Responsive**: Works on all devices

### 4. Programmatic API

#### Replay Engine

```python
from ttd import ReplayEngine

engine = ReplayEngine()

# Replay latest run
result = engine.replay(task_id="my_task")

# Replay specific run
result = engine.replay(task_id="my_task", run_id="20241201_143022")

# Replay with custom validation
result = engine.replay(task_id="my_task", validate_output=True)

print(f"Replay successful: {result['success']}")
print(f"Original output: {result['original_output']}")
print(f"Replayed output: {result['replayed_output']}")
```

#### Diff Engine

```python
from ttd import DiffEngine

diff_engine = DiffEngine()

# Compare latest two runs
diff = diff_engine.diff_task_runs("my_task")

# Compare specific runs
diff = diff_engine.diff_task_runs("my_task", run_id1="run1", run_id2="run2")

# Generate human-readable report
report = diff_engine.generate_diff_report(diff, format="text")
print(report)
```

#### Custom Storage

```python
from ttd.storage import DuckDBStorageBackend

# Custom database location
storage = DuckDBStorageBackend(
    db_path="my_pipeline_snapshots.db",
    data_dir="./snapshot_data"
)

# Use with snapshots
@snapshot(task_id="custom_storage", storage_backend=storage)
def my_task(data):
    return process_data(data)
```

---

## 🌐 Google Colab & Jupyter

### Quick Setup

```python
# Install in Colab
!pip install dataghost[colab]

# Your DataGhost code
from ttd import snapshot

@snapshot(task_id="colab_analysis")
def analyze_data(dataset):
    # Your analysis logic
    return {"mean": sum(dataset) / len(dataset)}

# Run analysis
result = analyze_data([1, 2, 3, 4, 5])
```

### Launch Dashboard

```python
# Auto-detects environment and creates public tunnel
!dataghost dashboard --tunnel
```

**What happens:**
1. 🔍 Detects Google Colab environment
2. 🌐 Creates secure ngrok tunnel  
3. 📱 Generates public URL (e.g., `https://abc123.ngrok.io`)
4. 🔗 Share URL with teammates for collaborative debugging

### Advanced Colab Usage

```python
# Programmatic setup
from ttd.dashboard.colab_utils import setup_colab_dashboard

public_url, success = setup_colab_dashboard(port=8080)

if success:
    print(f"🚀 Dashboard: {public_url}")
    print("💡 Share this URL with your team!")
```

---

## 🏗️ Framework Integrations

### Apache Airflow

```python
from ttd.integrations.airflow import DataGhostPythonOperator, create_datahost_dag
from datetime import datetime

# Create DataGhost-enabled DAG
dag = create_datahost_dag(
    dag_id='my_etl_pipeline',
    default_args={'owner': 'data-team'},
    schedule_interval='@daily'
)

# Use DataGhost operators
extract_task = DataGhostPythonOperator(
    task_id='extract_data',
    python_callable=extract_data_function,
    dag=dag
)

transform_task = DataGhostPythonOperator(
    task_id='transform_data', 
    python_callable=transform_data_function,
    dag=dag
)

# Set dependencies
extract_task >> transform_task
```

### Coming Soon
- 🔥 **Prefect Integration**
- 🚀 **Dagster Integration** 
- 📓 **Native Jupyter Support**
- 🔧 **VS Code Extension**

---

## 🎯 Use Cases

### 🔍 Debug Pipeline Failures

```python
# When a pipeline fails, replay the exact conditions
from ttd import ReplayEngine

engine = ReplayEngine()
result = engine.replay(task_id="failed_task", run_id="failure_run_id")

if not result['success']:
    print(f"Error: {result['error']}")
    print(f"Inputs: {result['inputs']}")
    print(f"Stack trace: {result['stack_trace']}")
```

### 📈 Monitor Performance Changes

```bash
# Compare performance between deployments
dataghost diff my_etl_task --run-id1 yesterday --run-id2 today

# See execution time changes, output differences, etc.
```

### 🧪 Test Changes Safely

```python
# Test new logic against historical data
historical_inputs = get_historical_inputs("my_task", "specific_run")
new_result = new_function(historical_inputs)

# Compare with historical output
diff_engine = DiffEngine()
diff = diff_engine.compare_outputs(historical_output, new_result)
```

### 📊 Data Quality Monitoring

```python
@snapshot(task_id="data_quality_check")
def check_data_quality(df):
    return {
        "row_count": len(df),
        "null_count": df.isnull().sum().sum(),
        "duplicate_count": df.duplicated().sum(),
        "completeness": 1 - (df.isnull().sum().sum() / df.size)
    }

# Track quality metrics over time
quality_result = check_data_quality(daily_data)
```

---

## 🔧 Configuration

### Environment Variables

```bash
export DATAGHOST_DB_PATH="./my_snapshots.db"
export DATAGHOST_DATA_DIR="./my_data"
export DATAGHOST_CAPTURE_ENV="true"
export DATAGHOST_CAPTURE_SYSTEM="true"
```

### Global Settings

```python
from ttd import set_storage_backend
from ttd.storage import DuckDBStorageBackend

# Set global storage backend
set_storage_backend(DuckDBStorageBackend("global.db"))
```

---

## 🗄️ Storage Backends

### DuckDB (Default)

```python
from ttd.storage import DuckDBStorageBackend

# Default configuration
storage = DuckDBStorageBackend()

# Custom configuration
storage = DuckDBStorageBackend(
    db_path="custom_snapshots.db",
    data_dir="./custom_data"
)
```

### S3 (Coming Soon)

```python
from ttd.storage import S3StorageBackend

storage = S3StorageBackend(
    bucket="my-dataghost-bucket",
    prefix="snapshots/",
    region="us-west-2"
)
```

---

## 🚀 Advanced Features

### Custom Snapshot Metadata

```python
@snapshot(task_id="custom_meta")
def process_with_metadata(data):
    # Add custom metadata to snapshots
    snapshot_metadata = {
        "data_source": "production_db",
        "processing_mode": "batch",
        "quality_score": calculate_quality(data)
    }
    
    return {
        "result": process_data(data),
        "_metadata": snapshot_metadata
    }
```

### Conditional Snapshots

```python
@snapshot(task_id="conditional", condition=lambda inputs: inputs[0] > 100)
def process_large_datasets(data):
    # Only capture snapshots for large datasets
    return expensive_processing(data)
```

### Performance Optimization

```python
@snapshot(
    task_id="optimized",
    compress_data=True,        # Compress large outputs
    sample_large_data=True,    # Sample large inputs
    max_snapshot_size="10MB"   # Limit snapshot size
)
def memory_efficient_task(large_data):
    return process_efficiently(large_data)
```

---

## 🛠️ Development & Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/dataghost/dataghost.git
cd dataghost

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
isort .
flake8
```

### Running Examples

```bash
# Basic example
python examples/basic_example.py

# Airflow DAG example
python examples/airflow_dag.py

# Google Colab example
python examples/colab_example.py
```

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 🗺️ Roadmap

### ✅ **v0.1.0 - Core Engine** (Current)
- [x] Snapshot decorator with metadata capture
- [x] DuckDB storage backend
- [x] CLI with rich commands
- [x] Replay engine
- [x] Diff engine  
- [x] Interactive web dashboard
- [x] Google Colab support

### 🚧 **v0.2.0 - Enhanced Features** (In Progress)
- [ ] S3 storage backend
- [ ] Advanced diff algorithms
- [ ] Performance optimizations
- [ ] Extended Airflow integration
- [ ] Prefect integration

### 📋 **v0.3.0 - Ecosystem Integration**
- [ ] Dagster integration
- [ ] Native Jupyter support
- [ ] VS Code extension
- [ ] Slack/Teams notifications

### 🎨 **v0.4.0 - Advanced UI**
- [ ] Advanced dashboard features
- [ ] Custom dashboard themes
- [ ] Real-time collaboration
- [ ] Mobile app

---

## 📊 Performance

DataGhost is designed for minimal overhead:

- **Snapshot capture**: < 1ms overhead per function call
- **Storage**: Efficient compression and deduplication
- **Memory usage**: < 50MB for typical workloads
- **Dashboard**: Sub-second response times

---

## 🤝 Support & Community

### Getting Help

- 📚 **Documentation**: [GitHub Wiki](https://github.com/dataghost/dataghost/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/dataghost/dataghost/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/dataghost/dataghost/issues)
- 📧 **Email**: [2003kshah@gmail.com](mailto:2003kshah@gmail.com)

### Community

- ⭐ **Star us on GitHub**: [dataghost/dataghost](https://github.com/dataghost/dataghost)
- 🐦 **Follow updates**: [@dataghost](https://twitter.com/dataghost) (coming soon)
- 📺 **YouTube tutorials**: [DataGhost Channel](https://youtube.com/dataghost) (coming soon)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by [Krish Shah](https://github.com/2003kshah)
- Inspired by time-travel debugging concepts from software engineering
- Thanks to the Apache Airflow community for pipeline orchestration patterns
- Special thanks to the Python data engineering community

---

<div align="center">

**Happy Time-Travel Debugging! 👻✨**

[Get Started](#-quick-start) • [Documentation](https://github.com/dataghost/dataghost/wiki) • [Examples](./examples/) • [Contributing](#-development--contributing)

</div>