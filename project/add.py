from errors import WitError

import os
from pathlib import Path
import shutil
from typing import Optional


def add(path_to_add: str) -> None:
    file_to_add = Path(os.path.abspath(path_to_add))
    repository = get_directory_with_wit(file_to_add)
    if not repository:
        raise WitError("<.wit> file not found")
    destination = repository.joinpath('.wit', 'staging_area')
    directories_to_copy = file_to_add.relative_to(repository).parts[:-1]
    for dir_name in directories_to_copy:
        dirs = os.listdir(destination)
        destination = destination.joinpath(dir_name)
        if dir_name not in dirs:
            destination.mkdir()
    save_the_copy(destination, file_to_add)


def save_the_copy(destination: Path, file: Path) -> None:
    if file.is_file():
        shutil.copy2(file, destination)
    else:
        destination_of_folder_if_doesnt_exists = destination.joinpath(file.name)
        if destination_of_folder_if_doesnt_exists.exists():
            shutil.rmtree(destination_of_folder_if_doesnt_exists)
        shutil.copytree(file, destination_of_folder_if_doesnt_exists)


def get_directory_with_wit(file: Path) -> Optional[Path]:
    for parent in file.parents:
        dir_lst = os.listdir(parent)
        if '.wit' in dir_lst:
            return parent
    return None
