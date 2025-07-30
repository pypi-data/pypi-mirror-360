"""
Setup script for DataGhost - Time-Travel Debugger for Data Pipelines
"""
from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dataghost",
    version="0.1.1",
    author="Krish Shah",
    author_email="2003kshah@gmail.com",
    description="Time-Travel Debugger for Data Pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dataghost/dataghost",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cloudpickle>=2.0.0",
        "duckdb>=0.8.0",
        "lz4>=4.0.0",
        "pandas>=1.5.0",
        "psutil>=5.9.0",
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "deepdiff": ["deepdiff>=6.0.0"],
        "airflow": ["apache-airflow>=2.5.0"],
        "s3": ["boto3>=1.26.0", "fsspec>=2023.1.0"],
        "dashboard": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
        ],
        "tunnel": [
            "pyngrok>=5.0.0",
        ],
        "colab": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
            "pyngrok>=5.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "all": [
            "deepdiff>=6.0.0",
            "apache-airflow>=2.5.0",
            "boto3>=1.26.0",
            "fsspec>=2023.1.0",
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
            "pyngrok>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dataghost=cli.main:main",
        ],
    },
    package_data={
        "ttd": ["dashboard/static/**/*", "dashboard/templates/**/*"],
    },
    include_package_data=True,
    zip_safe=False,
)