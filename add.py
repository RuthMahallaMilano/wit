# upload 171

import os
from pathlib import Path
import shutil
import sys
from typing import Union


def init() -> None:
    cwd = os.getcwd()
    wit_path = os.path.join(cwd, '.wit')
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, 'images'))
    os.mkdir(os.path.join(wit_path, 'staging_area'))


def add(path_to_add: str) -> None:
    file = Path(os.path.abspath(path_to_add))
    directory_with_wit = get_directory_with_wit(file)
    if not directory_with_wit:
        raise WitError("<.wit> file not found")
    destination = directory_with_wit.joinpath('.wit', 'staging_area')
    directories_to_copy = file.relative_to(directory_with_wit).parts[:-1]
    for dir_name in directories_to_copy:
        dirs = os.listdir(destination)
        destination = destination.joinpath(dir_name)
        if dir_name not in dirs:
            destination.mkdir()
    save_the_copy(destination, file)


def save_the_copy(destination: Path, file: Path) -> None:
    if file.is_file():
        shutil.copy2(file, destination)
    else:
        destination_of_folder_if_doesnt_exists = destination.joinpath(file.name)
        if destination_of_folder_if_doesnt_exists.exists():
            shutil.rmtree(destination_of_folder_if_doesnt_exists)
        shutil.copytree(file, destination_of_folder_if_doesnt_exists)


def get_directory_with_wit(file: Path) -> Union[Path, bool]:
    for parent in file.parents:
        dir_lst = os.listdir(parent)
        if '.wit' in dir_lst:  # and os.path.isdir(os.path.abspath('.wit')): > never True. also with iterdir. why?
            return parent
    return False


class WitError(Exception):
    pass


def is_init_status_command_correct(argv: list[str]) -> bool:
    return len(argv) == 2


def is_add_or_commit_command_correct(argv: list[str]) -> bool:
    return len(argv) == 3


if sys.argv[1] == 'init':
    if is_init_status_command_correct(sys.argv):
        init()
    else:
        print(fr"Usage: python {sys.argv[0]} init")


elif sys.argv[1] == 'add':
    if is_add_or_commit_command_correct(sys.argv):
        add(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} add <file_path>")
