# -*- coding: utf-8 -*-
"""Commonly used pre-processing functions are defined here. They are
automatically imported in ai_24sea.modeler.tasks.transform, where they can be
used to create the preprocessing pipeline of the training data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import get_full_col_name_from_partial


def drop_cols(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Drop specified columns from DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to process
    columns : list[str]
        Column names to drop. Can be partial names (e.g. mean_windpeed instead
        of mean_WF_A01_windspeed)

    Returns
    -------
    pd.DataFrame
        Processed DataFrame
    """
    if not columns:
        return df
    cols_to_drop = [
        get_full_col_name_from_partial(df.columns.tolist(), col)
        for col in columns
    ]
    return df.drop(columns=cols_to_drop)


def include_thrust_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add the sin and cos (yaw) thrust columns calculated by dividing the
    power by windspeed.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to add the thrust columns

    Returns
    -------
    pd.DataFrame
        Processed DataFrame including the thrust columns
    """
    df_columns = df.columns.tolist()
    ws_col = get_full_col_name_from_partial(df_columns, "mean_windspeed")
    power_col = get_full_col_name_from_partial(df_columns, "mean_power")
    yaw_col_name = get_full_col_name_from_partial(df_columns, "mean_yaw")
    mean_thrust = np.divide(df[power_col], df[ws_col])
    df["mean_thrust_cos"] = np.multiply(
        mean_thrust, np.cos(df[yaw_col_name] / 180 * np.pi)
    )
    df["mean_thrust_sin"] = np.multiply(
        mean_thrust, np.sin(df[yaw_col_name] / 180 * np.pi)
    )
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna(subset=["mean_thrust_cos", "mean_thrust_sin"])
    return df


def add_turbulance(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add a 'mean_ti' column for turbulence intensity, calculated as the
    ratio of standard deviation to mean windspeed.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be updated with the new 'mean_ti' column.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame
    """
    std_ws_col = get_full_col_name_from_partial(
        df.columns.tolist(), "std_windspeed"
    )
    mean_ws_col = get_full_col_name_from_partial(
        df.columns.tolist(), "mean_windspeed"
    )
    df["mean_ti"] = 100 * df[std_ws_col] / df[mean_ws_col]

    return df


def add_relative_wind_dir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'relative_winddir' column by calculating the difference
    between 'mean_winddirection' and 'mean_yaw'.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be updated with the new 'relative_winddir' column.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame
    """
    wind_dir_col = get_full_col_name_from_partial(
        df.columns.tolist(), "mean_winddirection"
    )
    yaw_col = get_full_col_name_from_partial(df.columns.tolist(), "mean_yaw")
    df["relative_winddir"] = df.apply(
        lambda row: _get_heading_error(
            row[wind_dir_col],
            row[yaw_col],  # pylint: disable=R0801
        ),
        axis=1,
    )
    return df


def _get_heading_error(init, final):
    """
    Calculate the heading error between two yaw angles.

    Parameters
    ----------
    init : float
        The initial yaw angle in degrees.
    final : float
        The final yaw angle in degrees.

    Returns
    -------
    float
        The heading error between the initial and final yaw angles.

    Raises
    ------
    ValueError
        If either yaw angle is outside the range 0-360 degrees.
    """
    if init > 360 or init < 0 or final > 360 or final < 0:
        raise ValueError("Yaw angle must be between 0 and 360 degrees")
    diff = final - init
    abs_diff = abs(diff)

    if abs_diff == 180:  # pylint: disable=R0801
        return abs_diff
    if abs_diff < 180:
        return diff
    if final > init:
        return abs_diff - 360
    return 360 - abs_diff


def remove_col_outliers(
    df: pd.DataFrame,
    col_w_outliers_to_remove: str,
    quantile_to_remove: float = 0.95,
) -> pd.DataFrame:
    """
    Remove outliers in a column based on a specified quantile threshold.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be updated by removing outliers.
    col_w_outliers_to_remove : str
        The column name in which to remove outliers.
    quantile_to_remove : float, optional
        Quantile threshold above which values are considered outliers.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame
    """
    col_name = get_full_col_name_from_partial(
        df.columns.tolist(), col_w_outliers_to_remove
    )
    stat_limit = df[col_name].quantile(quantile_to_remove)
    df = df[df[col_name] < stat_limit]
    return df
