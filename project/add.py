import shutil
from glob import glob
from pathlib import Path
from typing import Iterator

import flask
import pytest
from errors import WitError
from global_functions import get_repository_path


def add_function(path_to_add: str) -> None:
    path = Path(path_to_add).resolve()
    repository = get_repository_path(path)
    if not repository:
        raise WitError("<.wit> file not found")
    destination = get_destination(path, repository)
    save_the_copy(destination, path)


def update_destination(destination: Path, directories_to_copy: Iterator[str]) -> Path:
    for dir_name in directories_to_copy:
        destination = destination / dir_name
        if not glob(str(destination)):
            destination.mkdir()
    return destination


def get_destination(path: Path, repository: Path) -> Path:
    destination = repository / ".wit" / "staging_area"
    file_path = path.relative_to(repository)
    file_parts = file_path.parts
    parents_dirs = (part for part in file_parts if part != file_path.name)
    destination = update_destination(destination, parents_dirs)
    return destination


def save_the_copy(destination: Path, path: Path) -> None:
    if path.is_file():
        shutil.copy2(path, destination)
    else:
        destination_of_folder = destination / path.name
        if destination_of_folder.exists():
            shutil.rmtree(destination_of_folder)
        shutil.copytree(path, destination_of_folder)
