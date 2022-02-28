import os
from pathlib import Path
import shutil
from typing import Optional

from errors import WitError


def add(path_to_add: str) -> None:
    path = Path(os.path.abspath(path_to_add))
    repository = get_repository_path(path)
    if not repository:
        raise WitError("<.wit> file not found")
    destination = repository.joinpath('.wit', 'staging_area')
    directories_to_copy = path.relative_to(repository).parts[:-1]
    for dir_name in directories_to_copy:
        dirs = os.listdir(destination)
        destination = destination.joinpath(dir_name)
        if dir_name not in dirs:
            destination.mkdir()
    save_the_copy(destination, path)


def save_the_copy(destination: Path, file: Path) -> None:
    if file.is_file():
        shutil.copy2(file, destination)
    else:
        destination_of_folder_if_doesnt_exists = destination.joinpath(file.name)
        if destination_of_folder_if_doesnt_exists.exists():
            shutil.rmtree(destination_of_folder_if_doesnt_exists)
        shutil.copytree(file, destination_of_folder_if_doesnt_exists)


def get_repository_path(path: Path) -> Optional[Path]:
    if path.is_dir():
        if '.wit' in os.listdir(path):
            return path
    for parent in path.parents:
        dir_lst = os.listdir(parent)
        if '.wit' in dir_lst:
            return parent
    return None
