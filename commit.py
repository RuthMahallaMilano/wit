# upload 172
import datetime
import os
from pathlib import Path
import random
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


def commit(message: str) -> None:
    dir_with_wit = get_directory_with_wit(Path.cwd())
    if not dir_with_wit:
        raise WitError("<.wit> file not found")
    images_path = dir_with_wit.joinpath('.wit', 'images')
    path_of_new_folder = create_commit_folder(images_path)
    create_commit_txt_file(dir_with_wit, images_path, path_of_new_folder, message)
    save_files(dir_with_wit, path_of_new_folder)
    commit_id = os.path.basename(path_of_new_folder)
    write_references(commit_id, dir_with_wit)


def create_commit_folder(images_path: Path) -> str:
    length = 20
    chars = '1234567890abcdef'
    folder_name = ''.join(random.choice(chars) for _ in range(length))
    path_of_new_folder = os.path.join(images_path, folder_name)
    os.mkdir(path_of_new_folder)
    return path_of_new_folder


def create_commit_txt_file(dir_with_wit: Path, images_path: Path, path_of_new_folder: str, message: str) -> None:
    parent_head = get_parent_head(dir_with_wit)
    txt_file = images_path.joinpath(Path(path_of_new_folder).name + '.txt')
    txt_file.write_text(
        f'parent = {parent_head if parent_head else None}\n'
        f'date = {datetime.datetime.now().strftime("%c")}\n'
        f'message = {message}'
    )


def get_parent_head(dir_with_wit: Path) -> str:
    wit_folder = dir_with_wit.joinpath('.wit')  # repository + r'\.wit'
    if 'references.txt' in os.listdir(wit_folder):
        ref_path = wit_folder.joinpath('references.txt')
        with ref_path.open() as f_h:
            references_file = f_h.readlines()
        return references_file[0][5:].strip()
    return ''


def save_files(dir_with_wit: Path, path_of_new_folder: str) -> None:
    staging_area_path = os.path.join(dir_with_wit, '.wit', 'staging_area')
    for item in os.listdir(staging_area_path):
        src = os.path.join(staging_area_path, item)
        dst = os.path.join(path_of_new_folder, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)


def write_references(commit_id: str, dir_with_wit: Path) -> None:
    wit_folder = dir_with_wit.joinpath('.wit')
    ref_file = wit_folder.joinpath('references.txt')
    ref_file.write_text(f'HEAD={commit_id}\nMASTER={commit_id}\n')


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


elif sys.argv[1] == 'commit':
    if is_add_or_commit_command_correct(sys.argv):
        commit(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} commit MESSAGE")
