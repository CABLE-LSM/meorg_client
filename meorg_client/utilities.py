"""Utility methods."""

import pkgutil
import json
import yaml
import os
from pathlib import Path
from importlib import resources


# Single argument decoding functions.
PACKAGE_DATA_DECODERS = dict(json=json.loads, yml=yaml.safe_load)


def get_installed_root() -> Path:
    """Get the installed root of the installation.

    Returns
    -------
    Path
        Path to the installed root.
    """
    return Path(resources.files("meorg_client"))


def get_installed_data_root() -> Path:
    """Get the installed data root of the installation.

    Returns
    -------
    Path
        Path to the installed data root.
    """
    return get_installed_root() / "data"


def load_package_data(filename: str) -> dict:
    """Load data out of the installed package data directory.

    Parameters
    ----------
    filename : str
        Filename of the file to load out of the data directory.
    """
    # Work out the encoding of requested file.
    ext = filename.split(".")[-1]

    # Alias yaml and yml.
    ext = ext if ext != "yaml" else "yml"

    # Extract from the installations data directory.
    raw = pkgutil.get_data("meorg_client", os.path.join("data", filename)).decode(
        "utf-8"
    )

    # Decode and return.
    return PACKAGE_DATA_DECODERS[ext](raw)


def get_user_data_filepath(filename):
    """Get the filepath to the user file."""
    return Path.home() / ".meorg" / filename


def load_user_data(filename):
    """Load data from the user's home directory."""
    filepath = get_user_data_filepath(filename)
    raw = open(filepath, "r").read()
    ext = filename.split(".")[-1]
    return PACKAGE_DATA_DECODERS[ext](raw)
