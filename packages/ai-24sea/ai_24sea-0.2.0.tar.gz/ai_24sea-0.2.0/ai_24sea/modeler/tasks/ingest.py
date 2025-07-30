# -*- coding: utf-8 -*-
"""Ingest step for the data collection. Here all the generic functionality
for the data ingestion can be found.

The main function to be used for the data collection into a DataFrame is the
``ingest_flow``. It works in combination with configuration files.
Specifically for the ingest step, the main configurations of interest are
general and ingest in which parameters such as the period to gather data, and
he specific metrics to retrieve can be specified.

If a different aggregation method is needed, custom code can be passed to the
function though the `aggr_func` argument.
"""
from __future__ import annotations

from asyncio import run as R
from datetime import datetime
from typing import Callable, Union

import pandas as pd
from api_24sea.core import AsyncAPI
from prefect import flow, task
from prefect.cache_policies import INPUTS, TASK_SOURCE

from .. import constants as C
from ..config import validate_config

api = AsyncAPI()


@flow
def ingest_flow(
    config: dict,
    dt_start: Union[datetime, str, None] = None,
    dt_stop: Union[datetime, str, None] = None,
    turbines: Union[list[str], str, None] = None,
    aggr_func: Union[Callable, None] = None,
) -> pd.DataFrame:
    """
    Function to load data based on a provided configuration file

    Parameters
    ----------
    config : dict
        The loaded configuration file as a dictionary. The structure of the file
        is important to follow the structure of the template in order for this
        function work
    dt_start : datetime | str | None = None, by default None
        Start time to gather data. If it isn't provided it is looked for in
        config["general"].
    dt_stop : datetime | str | None = None, by default None
        Stop time to gather data. If it isn't provided it is looked for in
        config["general"].
    turbines : list[str] | str | None, by default None
        The turbines to gather data from. If it isn't provided it is looked for
        in config["general"].
    Returns
    -------
    pd.DataFrame
        The training dataframe

    Raises
    ------
    ValueError
        If more than one turbine is provided raises a value error because only
        one should be used for location specific models
    """
    i_c = config["ingest"]
    g_c = config["general"]

    # If no start and stop date are passed in the args it looks for them in the
    # general config
    g_c[C.DT_START_TRAINING_KEY] = (
        dt_start if dt_start is not None else g_c.get(C.DT_START_TRAINING_KEY)
    )
    g_c[C.DT_STOP_TRAINING_KEY] = (
        dt_stop if dt_stop is not None else g_c.get(C.DT_STOP_TRAINING_KEY)
    )
    g_c[C.LOCATIONS_TRAINING_KEY] = (
        turbines if turbines is not None else g_c.get(C.LOCATIONS_TRAINING_KEY)
    )
    validate_config(g_c, C.REQUIRED_GENERAL_CONFIG_KEYS)
    validate_config(i_c, C.REQUIRED_INGEST_CONFIG_KEYS)

    site = g_c[C.SITE_KEY]

    dfs = load_data_api(
        site,
        g_c[C.LOCATIONS_TRAINING_KEY],
        g_c[C.DT_START_TRAINING_KEY],
        g_c[C.DT_STOP_TRAINING_KEY],
        i_c["parameters"],
    )
    if g_c[C.MODEL_TYPE_KEY] == "location_specific":
        if len(dfs) > 1:
            raise ValueError(
                """You are trying to train a location specific model with more
                than one turbine"""
            )
        df = dfs[0]  # location specific case
    elif g_c[C.MODEL_TYPE_KEY] == "fleetwide":
        df = combine_training_data_into_single_df(
            dfs, i_c.get("add_location_column", False)
        )
    else:
        if aggr_func is None:
            raise NotImplementedError(
                f"{g_c[C.MODEL_TYPE_KEY]} has not been implemented. Please pass"
                " custom aggregation function to utilize"
            )
        df = aggr_func(dfs, config)

    return df


@task(
    result_serializer="pickle",
    persist_result=True,
    cache_policy=INPUTS + TASK_SOURCE,
)
def load_data_api(
    site: str,
    training_turbines: list[str] | str,
    start_timestamp: str | datetime,
    end_timestamp: str | datetime,
    parameters: list[str],
) -> list[pd.DataFrame]:
    """
    Function to load data from the api

    Parameters
    ----------
    site : str
        The windfarm name
    training_turbines : list[str] | str
        Full names of the training turbines
    dt_start : str | datetime
        Starting date to load data
    dt_stop : str | datetime
        Ending date to load data
    parameters : list[str]
        A list of all parameters to load

    Returns
    -------
    list[pd.DataFrame]
        A list of each turbines dataframe
    """

    if isinstance(training_turbines, str):
        training_turbines = [training_turbines]
    data = R(
        api.get_data(
            [site],
            training_turbines,
            parameters,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
    )
    dfs = list(data.datasignals.as_dict()[site.lower()].values())
    if not dfs:
        raise ValueError(
            "Empty list of dataframes loaded from the 24SEA API."
            " Please verify the selected parameters and period."
        )

    return dfs


@task
def combine_training_data_into_single_df(
    df_list: list[pd.DataFrame], add_location_column: bool = False
) -> pd.DataFrame:
    """
    Combine data from all turbines in a list of DataFrames into a single
    DataFrame.

    Parameters
    ----------
    df_list : list[pd.DataFrame]
        A list of dataframes containing the data from each turbine
    add_location_column : bool
        Whether to add a location column which contains the location ids of the
        original dataframes, by default False

    Returns
    -------
    pd.DataFrame
        Combined DataFrame with data from all turbines and loc_id and site_id
        removed from the column names.
    """
    for df in df_list:
        split_col_name = df.columns[0].split("_")
        site_id = split_col_name[1]
        loc_id = split_col_name[2]
        df.columns = df.columns.str.replace(f"{site_id}_{loc_id}_", "")
        if add_location_column:
            df.loc[:, "location"] = loc_id
    full_df = pd.concat(
        [df for df in df_list], axis=0  # pylint: disable=R1721
    ).reset_index(drop=True)
    return full_df.dropna(axis=1, how="all")
