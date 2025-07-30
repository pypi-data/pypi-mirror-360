# -*- coding: utf-8 -*-
"""
This module defines how to split the data into training and test sets.
Pplit step for the data collection. Here all the generic functionality
for the data splitting into a train and test DataFrame can be found.

The main function to be used for the data splitting is the
``split_flow``. It works in combination with configuration files.
Specifically for the split step, the main configuration of interest is
split config in which parameters such as the test_size can be define.

If a different splitting method is needed, custom code can be passed to the
function though the `train_test_split` argument.
"""
from __future__ import annotations

from typing import Any, Callable, Union

import pandas as pd
from prefect import flow, task
from sklearn.model_selection import train_test_split as sklearn_train_test_split

from .. import constants as C
from ..config import validate_config


@flow
def split_flow(
    df: pd.DataFrame,
    config: dict[str, Any],
    split_func: Union[Callable, None] = None,
) -> tuple[pd.DataFrame, Union[pd.DataFrame, None]]:
    """
    Splits the data into training and test sets.

    .. warning::
        Keep the input and return types as they are. Any inside logic can change
        but make sure to accept a DataFrame and the config, andreturn a tuple of
        a train and test DataFrame.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be split.
    config : dict[str, Any]
        The full configuration dictionary containing also the split
        configuration.
    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame | None]
        A tuple containing the training DataFrame and the test DataFrame.
        If no test set is needed, the second element can be None.
    """
    s_c = config.get("split", {})
    validate_config(s_c, C.SPLIT_CONFIG_KEYS)
    test_size = s_c["test_size"]
    if split_func is None:
        split_func = train_test_split
    train_df, test_df = split_func(df, test_size, s_c)
    return train_df, test_df


@task
def train_test_split(
    df: pd.DataFrame, test_size: float, split_config: dict | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Defines how the data is split into a train and test set."""
    if split_config is None:
        split_config = {}
    random_state = split_config.get("random_state", 42)
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    train_df, test_df = sklearn_train_test_split(
        df, test_size=test_size, random_state=random_state
    )
    return train_df, test_df
