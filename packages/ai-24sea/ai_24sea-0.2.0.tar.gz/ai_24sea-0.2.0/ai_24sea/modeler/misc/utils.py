# -*- coding: utf-8 -*-
"""Some commonly used utility functions are defined here."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import dotenv
import mlflow


def parse_datetime_to_string(
    dt: str | datetime | None, str_format: str = "%Y.%m.%d"
) -> str | None:
    """Take a datetime in string or datetime object form and converts it to the
    specified format.

    Only valid ISO8601 formatted strings are accepted.

    Parameters
    ----------
    dt : str | datetime | None
        The datetime string or object to convert to specified format
    str_format : str
        The format for the string datetime, by default "%Y.%m.%d"

    Returns
    -------
    str | None
        The formatted datetime string, or None if the input `dt` was None.
        Raises ValueError if a string `dt` is not in valid ISO8601 format.
    """
    if dt is None:
        return dt
    if isinstance(dt, datetime):
        return dt.strftime(str_format)

    return datetime.fromisoformat(dt).strftime(str_format)


def get_full_col_name_from_partial(
    columns: list[str], substring_filter: str
) -> str:
    """
    Retrieve the full column name from a columns list that matches the provided
    partial filter.

    This function ensures that all parts of the substring_filter (split by "_")
    appear in sequence within a column name.

    Parameters:
    -----------
    columns : list[str]
        The list of strings representing column names in a DataFrame.
    substring_filter : str
        Partial column name to match.


    Returns:
    --------
    str
        The full column name that matches the filter.

    Raises:
    -------
    ValueError:
        - If no column matches.
        - If multiple columns match.
    """
    if not isinstance(substring_filter, str):
        raise ValueError("`substring_filter` must be a string.")

    # Split substring_filter into parts (e.g., "mean_yaw" -> ["mean", "yaw"])
    filter_parts = substring_filter.replace(" ", "_").split("_")

    # Ensure case insensitivity
    filter_parts = [part.lower() for part in filter_parts]

    # Find matching columns where all parts appear in order
    matching_cols = [
        col
        for col in columns
        if all(part in col.lower() for part in filter_parts)
    ]

    if not matching_cols:
        raise ValueError(f"No column found matching: '{substring_filter}'")

    if len(matching_cols) > 1:
        raise ValueError(f"Multiple columns found matching: {matching_cols}")

    return matching_cols[0]


def register_mlflow_model(
    run_id: str, start_validity_date: str | datetime | None = None
) -> None:
    """
    Registers a run as an mlflow model which can then be accessed from the api

    Parameters
    ----------
    run_id : str
        The mlflow run_id of the trained model
    """
    client = mlflow.MlflowClient()
    run = client.get_run(run_id)
    tags = run.data.tags
    run_name = tags.get("mlflow.runName")
    if start_validity_date is not None:
        start_validity_date = parse_datetime_to_string(start_validity_date)
    else:
        start_validity_date = tags.get("start_validity_date")
    training_date = tags.get("training_date")
    # This removes the date from the end of the run name.
    registered_model_name = "_".join(run_name.split("_")[:-1])
    if run_name is None:
        raise KeyError(f"Run with id: {run_id} is unnamed")
    version = mlflow.register_model(
        f"runs:/{run_id}/model", registered_model_name
    )
    # This will probably have to be taken from the run's tags in the future.
    # For now it is left to be the current time
    client.set_model_version_tag(
        registered_model_name,
        version.version,
        "training_date",
        training_date,
    )
    client.set_model_version_tag(
        registered_model_name,
        version.version,
        "start_validity_date",
        start_validity_date,
    )


def load_env(env_file_path: str | Path = "./.env"):
    """load the environment variables in the specified path

    Parameters
    ----------
    env_file_path : str | Path, optional
        The path of the file containing the env variables, by default "./.env"

    Raises
    ------
    EnvironmentError
        If the environment variables are not loaded
    """
    _ = dotenv.load_dotenv(env_file_path)
    __ = dotenv.load_dotenv(env_file_path, override=True)
    if _ and __:
        print("Environment Variables Loaded Successfully")
        print(
            "👤  MlFlow User: \033[32;1m"
            f"{os.getenv('MLFLOW_TRACKING_USERNAME')}\033[0m"
        )
        print(
            "🗄️  MlFlow tracking server:   \033[32;1m"
            f"{os.getenv('MLFLOW_TRACKING_URI')}\033[0m"
        )
        print(
            "👤  API User:      \033[32;1m"
            f"{os.getenv('API_24SEA_USERNAME')}\033[0m"
        )
    else:
        raise EnvironmentError("Environment Variables Not Loaded")
