"""Module for environment file and values."""

import os
import pathlib
import typing

import dotenv


ROOT_DIR: pathlib.Path = pathlib.Path(
    os.path.dirname(os.path.abspath(__file__))
).parents[2]
ENV_PATH: pathlib.Path = ROOT_DIR / pathlib.Path(".env")


def values() -> dict[str, typing.Any]:
    """Returns the keys and values in the environment file."""
    return dotenv.dotenv_values(ENV_PATH)


def get_value(key: str) -> typing.Any | None:
    """Returns the environment value for the given key."""
    return dotenv.dotenv_values(ENV_PATH).get(key)


def get_path() -> pathlib.Path:
    """Returns the environment file path."""
    return ENV_PATH
