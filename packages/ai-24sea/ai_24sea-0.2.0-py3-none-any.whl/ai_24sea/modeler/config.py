# -*- coding: utf-8 -*-
"""The module used to parse the configurations for the various flows"""

from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf


def parse_config(
    config_path: str | Path,
) -> dict:
    """
    Parses configuration files required for the training flow to run.

    Parameters
    ----------
    config_path : str | Path
        Path to the configuration file
    Returns
    -------
    dict
        The parsed configuration as a dictionary.
    """
    config_path = Path(config_path)
    full_conf = OmegaConf.load(config_path)

    resolved_config = OmegaConf.to_container(full_conf, resolve=True)
    return resolved_config  # type: ignore


def validate_config(config: dict, required_keys: list):
    """Validate that all required keys exist in the configuration

    Parameters
    ----------
    config : dict
        The configuration to check for missing keys
    required_keys : list
        The list of required keys which are checked to exist within the
        configuration

    Raises
    ------
    KeyError
        If at least one key is missing an error is raised
    """
    for key in required_keys:
        if config.get(key) is None:
            raise KeyError(
                f"Missing key/value for '{key}' in the configuration file"
            )
