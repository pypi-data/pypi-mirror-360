# ai-24sea

A Python package for building, training, and managing AI/ML models for 24sea windfarm data. This repository provides a modular framework for data ingestion, preprocessing, splitting, training, and experiment tracking using MLflow.

## Features

- **Configurable ML Pipelines:** Easily define preprocessing, splitting, and training steps via configuration files.
- **Data Ingestion:** Fetch and aggregate windfarm data using the 24sea API.
- **Preprocessing:** Modular, reusable preprocessing functions for feature engineering and cleaning.
- **Train/Test Split:** Flexible splitting with support for custom strategies.
- **Model Training:** Standardized training flow with MLflow experiment tracking and signature enforcement.
- **Testing:** Comprehensive unit tests using `pytest` and `hypothesis`.

## Project Structure
```sh
├── LICENSE
├── README.md
├── VERSION
├── ai_24sea
│   ├── __init__.py
│   ├── modeler
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── misc
│   │   │   ├── __init__.py
│   │   │   ├── preprocessors.py
│   │   │   └── utils.py
│   │   └── tasks
│   │       ├── __init__.py
│   │       ├── ingest.py
│   │       ├── optimize.py
│   │       ├── split.py
│   │       ├── train.py
│   │       └── transform.py
│   └── version.py
├── bitbucket-pipelines.yml
├── bumpversion.py
├── notebooks
│   ├── tests.ipynb
│   └── tests.py
├── pyproject.toml
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── misc
│   │   ├── test_preprocessors.py
│   │   └── test_utils.py
│   ├── tasks
│   │   ├── test_ingest.py
│   │   ├── test_optimize.py
│   │   ├── test_split.py
│   │   ├── test_train.py
│   │   ├── test_transform.py
│   │   └── test_validate.py
│   ├── test_config.py
│   └── test_version.py
└── uv.lock
```

## Installation

This project uses `uv` for package management

To install:

```sh
uv sync
```

To install for development:

```sh
uv sync --all-groups
```
