# -*- coding: utf-8 -*-
"""Train step for the model training and logging into an MlFlow run. Here all
the generic functionality can be found.

The main function to be used for the data collection into a DataFrame is the
``train_flow``. It works in combination with configuration files.
Specifically for the train step, the main configurations of interest are
general and train in which parameters such as the pehyperparameters of the ML
model can be specified.

The train_flow expects the following functions to be custom defiend by the user
and passed as arguments, to make the flow compatible for the training of any
type of model:
- get_output_name_func
- get_target_name_func
- train_func
- log_model_func

These can be used along with custom configuration to train any type of model.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Union

import mlflow
import pandas as pd
import yaml
from mlflow.models.signature import ModelSignature
from mlflow.types import DataType
from mlflow.types.schema import ColSpec, Schema
from prefect import flow, task
from sklearn.pipeline import Pipeline

from .. import constants as C
from ..misc.utils import parse_datetime_to_string


@flow
def train_flow(  # pylint: disable=R0913, R0917, R0914
    train_df: pd.DataFrame,
    test_df: Union[pd.DataFrame, None],
    pipeline: Pipeline,
    # Functions to be passed by the user. NO DEFAULTS HERE
    train_func: Callable,
    get_output_name_func: Callable,
    get_target_name_func: Callable,
    log_model_func: Callable,
    # -----------------------------------------------------
    config: dict,
) -> str:
    """
    Train flow. This is the main function to be used for training the model and
    logging it into an MlFlow run.

    It takes the training and test data, a preprocessing pipeline, and a
    configuration dictionary as input. It performs the following steps:
    1. Creates a model signature based on the input columns and output column
       name.
    2. Sets up the MLflow experiment and run name based on the configuration.
    3. Fits the preprocessing pipeline to the training data.
    4. Transforms the training and test data using the fitted pipeline.
    5. Balances the inputs and outputs by dropping NaN values.
    6. Starts an MLflow run and logs the model, pipeline, signature, and
       configuration.

    Parameters
    ----------
    train_df : pd.DataFrame
        The DataFrame containing the training data.
    test_df : pd.DataFrame | None
        The DataFrame containing the test data. If None, no test data is used.
        for validation.
    pipeline: Pipeline
        The preprocessing pipeline including all preprocessing steps
    config : dict
        A dictionary containing configuration parameters for training. It should
        have the following structure:
        {
            "general": {
                "site": str,
                "training_turbines": list,
                "dt_start_training": str,
                "dt_stop_training": str,
                ...
            },
            "train": {
                ...
            },
            ...
            }
    Returns
    -------
    str
        The run_id of the MLflow run.
    """
    # Getting usefull things from the config
    g_c = config["general"]
    t_c = config["train"]
    site = g_c[C.SITE_KEY]
    locations = g_c[C.LOCATIONS_TRAINING_KEY]
    start_validity_date = t_c.get(C.DT_START_VALIDITY_KEY)
    root_folder = t_c.get("root", Path.cwd())
    initial_col_list = train_df.columns.tolist()

    ## define manually these functions.
    output_col_name: str | list[str] = get_output_name_func(
        initial_col_list, config
    )
    target_col_name: str | list[str] = get_target_name_func(
        initial_col_list, config
    )
    signature = create_signature(initial_col_list, output_col_name)
    signature_input_columns = [
        col.name
        for col in signature.inputs.inputs
        if len(col.name.split("_")) > 1
    ]
    train_input = train_df[signature_input_columns]
    train_output = (
        train_df[[target_col_name]]
        if isinstance(target_col_name, str)
        else train_df[target_col_name]
    )
    if test_df is not None:
        test_input = test_df[signature_input_columns]
        test_output = (
            test_df[[target_col_name]]
            if isinstance(target_col_name, str)
            else test_df[target_col_name]
        )
    else:
        test_input = None
        test_output = None

    # this step is only usefull is there is a scaler in the pipeline or
    # something else that needs to be fit. Important the the pipeline is only
    # fit with the training data.
    pipeline.fit(train_input, train_output)
    processed_train_input = pipeline.transform(train_input)
    processed_train_input, train_output = balance_inputs_outputs(
        processed_train_input, train_output
    )
    if test_input is not None:
        processed_test_input = pipeline.transform(test_input)
        processed_test_input, test_output = balance_inputs_outputs(
            processed_test_input, test_output
        )
    else:
        processed_test_input = None
    experiment_name, run_name, tags = setup_mlflow_info(
        site, locations, output_col_name, start_validity_date
    )
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    input_example = create_input_example(signature_input_columns)
    with mlflow.start_run(
        tags=tags, run_name=run_name, experiment_id=experiment.experiment_id
    ) as run:

        model = train_func(
            processed_train_input,
            train_output,
            processed_test_input,
            test_output,
            target_col_name,
            output_col_name,
            config,
        )
        log_model_func(
            model,
            pipeline,
            signature,
            root_folder=root_folder,
            input_example=input_example,
            config=config,
        )
        log_full_config(config, root_folder)
        run_id = run.info.run_id
    return run_id  # type: ignore


@task
def create_signature(
    input_columns: list[str], output_name: str | list[str]
) -> ModelSignature:
    """
    .. warning::
        DO NOT CHANGE THIS FUNCTION UNLESS ABSOLUTELY NECESSARY. IT IS USED TO
        ENFORCE A STANDARD WAY OF CREATING THE MODEL SIGNATURES FOR THE MODELS.

    Create a model signature for the given input output columns. Will also add a
    timestamp input and output column to the schema.

    The signature is used to create the model schema in the AI API, meaning that
    if the created signature is missing required columns, predictions will not,
    be possible, while if it has redundant columns, more than the required
    inputs will be requested which will make the predictions more time  and
    resource demanding.

    Parameters
    ----------
    input_columns : list[str]
        The columns of the input dataframe before any preprocessing. So any
        models that are added in a preprocessing step should not be included.
        These types of columns must be calculated during inference within the
        .predict function of the model
    output_name : str
        The output column name.

    Returns
    -------
    ModelSignature
        The model signature to be used to validate the input and output data
    """
    if isinstance(output_name, str):
        output_name = [output_name]
    # Create input schema
    input_cols = [
        ColSpec(DataType.double, col)
        for col in input_columns
        if col
        not in ["timestamp", "location"]
        + [out.replace("_pred", "") for out in output_name]
    ]
    input_cols.append(ColSpec(DataType.string, "timestamp"))

    input_schema = Schema(input_cols)  # type: ignore
    # Ensure that output names end with "_pred"
    output_name = [
        out + "_pred" if not out.endswith("_pred") else out
        for out in output_name
    ]
    # Create output schema
    output_cols = [ColSpec(DataType.double, col) for col in output_name]
    output_cols.append(ColSpec(DataType.string, "timestamp"))
    output_schema = Schema(output_cols)  # type: ignore
    # Create and return signature
    return ModelSignature(inputs=input_schema, outputs=output_schema)


@task
def create_input_example(input_columns: list[str]) -> pd.DataFrame:
    """
    Create an input example for the model based on the input columns.

    Assumes that all inputs are floating point values and assignes them the
    value of 1.0. Can be changed to something more realistic, like randomly
    assigning numbers toe ach input.

    Parameters
    ----------
    signature : list[str]
        the input columns exactly as they are in the signature.
    Returns
    -------
    pd.DataFrame
        The input example DataFrame
    """
    input_example = []
    single_input = {k: 1.0 for k in input_columns if len(k.split("_")) > 1}
    single_input["timestamp"] = "2022-11-01T00:00:00Z"  # type: ignore
    input_example.append(single_input)
    return pd.DataFrame(input_example)


@task
def setup_mlflow_info(
    site: str,
    locations: str | list[str],
    output_name: str | list[str],
    start_validity_date: str | datetime | None = None,
) -> tuple[str, str, dict]:
    """
    .. warning::
        DO NOT CHANGE THIS FUNCTION. IT IS USED TO ENFORCE A STANDARD WAY OF
        NAMING THE RUNS, EXPERIMENTS AND BASIC TAGS

    Parameters
    ----------
    site : str
        Full windfarm name
    locations : str
        Full Turbine name
    output_name : str | list[str]
        Name of the output parameter. This is the name of the signature output
        column, which is usually the target column name + "_pred".
    start_validity_date: str | datetime
        Start of validity of the model

    Returns
    -------
    tuple[str, str, dict]
        The experiment name, run name and tags in a standardised way.
    """
    if isinstance(output_name, list):
        output_name = output_name[0]  # Not sure how to handle this better
    experiment_name = site.lower()
    output_name = output_name.split("_pred", 1)[0]
    run_name = "_".join(
        [
            output_name,
            datetime.now().strftime("%Y-%m-%d-%H:%M"),
        ]
    )
    start_validity_date = parse_datetime_to_string(start_validity_date)

    tags = {
        "site": site,
        "locations": str(locations),
        "training_date": datetime.now().strftime("%Y.%m.%d"),
        "start_validity_date": start_validity_date,
    }
    return experiment_name, run_name, tags


@task
def balance_inputs_outputs(
    input_df: pd.DataFrame, target_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Drop nan values in both input and output and ensure they are in balance in
    terms of length.

    Parameters
    ----------
    input_df : pd.DataFrame
        The dataframe of the input data
    target_df : pd.DataFrame
        The dataframe of the output data
    """
    combined_df = pd.concat([input_df, target_df], axis=1)
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
    cleaned_combined_df = combined_df.dropna()
    input_cleaned = cleaned_combined_df[input_df.columns]
    output_cleaned = cleaned_combined_df[target_df.columns]
    return input_cleaned, output_cleaned


@task
def log_full_config(config: dict, root_folder=None):
    """
    Logs all used conf files to MLflow as artifacts. This doesn't log the yaml
    files from the config folder. Instead it temporarily saves the each key of
    the config dictionary and logs it as an artifact, then deletes it.

    Parameters
    ----------
    config : dict
        The conf dictionary with all training configurations.
    """
    if root_folder is None:
        root_folder = Path.cwd()
    root_folder = Path(root_folder)
    config_path = Path.cwd() / "config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)
    mlflow.log_artifact(str(config_path), artifact_path="config")
    os.unlink(config_path)
