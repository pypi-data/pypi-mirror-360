"""Module for various filesystem functionality, such as filesystem search."""

import glob
import os

from pathlib import Path


def list_directory(directory: Path, pattern: str = "*") -> list[Path]:
    """List files in a directory."""
    return [Path(path) for path in glob.glob(f"{directory}/{pattern}")]


def walk_directory(root: Path) -> list[Path]:
    """List files by walking from a root directory."""
    walker = os.walk(str(root))

    accumulated: list[Path] = list()

    dirpath: str
    dirnames: list[str]
    filenames: list[str]
    for dirpath, dirnames, filenames in walker:
        # TODO: Terminate early at a given depth

        abs_dirnames: list[Path] = [
            Path(f"{dirpath}/{dirname}") for dirname in dirnames
        ]
        abs_filenames: list[Path] = [
            Path(f"{dirpath}/{filename}") for filename in filenames
        ]

        accumulated.extend(abs_dirnames)
        accumulated.extend(abs_filenames)

    return accumulated


def search_files(pattern: str) -> list[Path]:
    """Searches for files with the given pattern."""
    return [Path(path) for path in glob.glob(pattern)]
