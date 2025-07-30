# -*- coding: utf-8 -*-
"""Transform step for the data preprocessing. Here all the generic functionality
for the creation of a preprocessing pipeline can be found.

The main function to be used for the transformation of the dataframe is
``transform_flow``. It works in combination with configuaration files.
Specifically for the transform step, the main configuration of interest is the
tranform section in which the specific processors to use, along with their
arguments can be specified. Some commonly used preprocessors are already defined
in ai_24sea.modeler.misc.preprocessors.

If a custom preprocessor is needed it can be passed as an argument to the flow
and added to the configuration in the same way.
"""

from __future__ import annotations

import sys
from functools import partial
from typing import Callable

from prefect import flow, task
from sklearn.pipeline import FunctionTransformer, Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .. import constants as C
from ..config import validate_config
from ..misc.preprocessors import *  # noqa: F401, F403 # pylint: disable=unused-wildcard-import, wildcard-import

scaler_name_dict = {
    "standardscaler": StandardScaler,
    "minmaxscaler": MinMaxScaler,
}


@flow
def transform_flow(
    config: dict, extra_preprocessors_list: list[Callable]
) -> Pipeline:
    """
    Create an Sk-Learn Pipeline with all preprocessing steps defined in the
    configuration.

    Can also include a scaler at the beginning or end of the pipeline.

    .. warning::
        It is assumed that the preprocessing steps are always the same both for
        training and inference. This is a good practice in general and not
        following this can be very dangerous. In case there is a goodcreason to
        have different preprocessing steps for inference and training,
        make 2 pipelines and log as an artifact the one used for inference. This
        is NOT recommended but can be done.

    Parameters
    ----------
    config : dict
        The full training configuration

    Returns
    -------
    Pipeline
        A pipeline including all preprocessing steps
    """
    t_c = config["transform"]
    validate_config(t_c, C.REQUIRED_TRANSFORM_CONFIG_KEYS)
    return build_preprocessing_pipeline(t_c, extra_preprocessors_list)


# pylint: disable=R0914, R0912
@task
def build_preprocessing_pipeline(
    transform_config: dict, preprocessors: list[Callable]
) -> Pipeline:
    """Create a preprocessing pipeline based on the tranform configuration and
    functions defined in misc.preprocessors.

    Parameters
    ----------
    transform_config : dict
        A dictionary containing the tranform configuration, with the
        preprocessing steps, and optionally a scaler specification.

    Returns
    -------
    Pipeline
        The preprocessing pipeline

    Raises
    ------
    NotImplementedError
        If a scaler order other than "first" or "last" is specified in the
        config
    NotImplementedError
        If a scaler type other than "standardscaler" or "minmaxscaler" is
        specified
    """
    steps = []

    scaler_config = transform_config.get("scaler", {})

    # Create a lookup map for preprocessors passed as arguments
    # Ensure preprocessors is not None before iterating
    passed_preprocessors_map: dict[str, Callable] = {}
    if preprocessors:
        for func_obj in preprocessors:
            if callable(func_obj) and hasattr(func_obj, "__name__"):
                passed_preprocessors_map[func_obj.__name__] = func_obj
            else:
                # Optionally, raise an error or warning for invalid items
                print(
                    f"Warning: Item {func_obj} in preprocessors list is not a "
                    "named callable and will be ignored."
                )

    current_module = sys.modules[__name__]
    for step in transform_config["steps"]:
        for func_name, args in step.items():
            func = None
            # 1. Try to get from passed_preprocessors_map
            if func_name in passed_preprocessors_map:
                func = passed_preprocessors_map[func_name]
            # 2. Else, try to get from the current module
            elif hasattr(current_module, func_name):
                func_candidate = getattr(current_module, func_name)
                if callable(func_candidate):
                    func = func_candidate

            if func is None:
                raise NameError(
                    f"Preprocessor function '{func_name}' not found. "
                    f"Searched in functions passed via 'preprocessors' argument"
                    f" and in module '{current_module.__name__}'."
                )
            wrapped = partial(func, **args) if isinstance(args, dict) else func
            tx = FunctionTransformer(wrapped, validate=False)
            steps.append((func_name, tx))

    if scaler_config:
        scaler_name = scaler_config["type"].lower()
        scaler_order = scaler_config["order"].lower()
        if scaler_name not in scaler_name_dict:
            raise NotImplementedError(
                f"Scaler type {scaler_config['type']} not recognized. "
                f"Available options: {list(scaler_name_dict.keys())}"
            )
        scaler = scaler_name_dict[
            scaler_name
        ]()  # () needed to instantiate the scaler
        if scaler_order == "first":
            # If the scaler is to be applied first, we add it at the beginning
            steps.insert(0, ("scaler", scaler))
        elif scaler_order == "last":
            # If the scaler is to be applied last, we add it at the end
            steps.append(("scaler", scaler))
        else:
            raise NotImplementedError(
                f"Scaler order {scaler_order} not recognized. "
                "Available options: 'first', 'last'"
            )
    pipeline = Pipeline(steps)
    pipeline.set_output(transform="pandas")
    return pipeline


# pylint: enable=R0914, R0912
