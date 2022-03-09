import datetime
import os
from pathlib import Path
import random
import re
import shutil

from errors import WitError
from global_functions import get_repository_path, get_head_reference


def commit_function(message: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    images_path = repository / '.wit' / 'images'
    path_of_new_folder = create_commit_folder(images_path)
    create_commit_txt_file(repository, images_path, path_of_new_folder, message)
    save_files(repository, path_of_new_folder)
    commit_id = os.path.basename(path_of_new_folder)
    write_references(commit_id, repository)


def create_commit_folder(images_path: Path) -> Path:
    folder_name = create_folder_name()
    path_of_new_folder = images_path / folder_name
    os.mkdir(path_of_new_folder)
    return path_of_new_folder


def create_folder_name() -> str:
    length = 20
    chars = '1234567890abcdef'
    folder_name = ''.join(random.choices(chars, k=length))
    return folder_name


def create_commit_txt_file(repository: Path, images_path: Path, path_of_new_folder: Path, message: str) -> None:
    parent_head = get_head_reference(repository)
    txt_file = images_path / (path_of_new_folder.name + '.txt')
    txt_file.write_text(
        f'parent = {parent_head if parent_head else None}\n'
        f'date = {datetime.datetime.now().strftime("%c")}\n'
        f'message = {message}'
    )


def save_files(repository: Path, path_of_new_folder: Path) -> None:
    staging_area_path = repository / '.wit' / 'staging_area'
    for item in os.listdir(staging_area_path):
        src = staging_area_path / item
        dst = path_of_new_folder / item
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)


def write_references(commit_id: str, repository: Path) -> None:
    wit_folder = repository / '.wit'
    references_file = wit_folder / 'references.txt'
    parent_head = get_head_reference(repository)
    activated_path = wit_folder / 'activated.txt'
    activated_branch = activated_path.read_text()
    if references_file.exists():
        change_head_and_branch_id(activated_branch, commit_id, parent_head, references_file)
    else:
        references_file.write_text(f'HEAD={commit_id}\n{"=".join((activated_branch, commit_id))}')


def change_head_and_branch_id(activated_branch: str, commit_id: str, parent_head: str, references_file: Path) -> None:
    regex = re.compile(fr"^{activated_branch}={parent_head}$", flags=re.MULTILINE)
    head_regex = re.compile(fr"^HEAD={parent_head}$", flags=re.MULTILINE)
    data = references_file.read_text()
    match = regex.findall(data)
    if match:
        new = regex.sub(f"{activated_branch}={commit_id}", data)
        new = head_regex.sub(f"HEAD={commit_id}", new)
        references_file.write_text(new)
