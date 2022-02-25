from add import get_repository_path
from errors import WitError

import datetime
import os
from pathlib import Path
import random
import shutil


def commit(message: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    images_path = repository.joinpath('.wit', 'images')
    path_of_new_folder = create_commit_folder(images_path)
    create_commit_txt_file(repository, images_path, path_of_new_folder, message)
    save_files(repository, path_of_new_folder)
    commit_id = os.path.basename(path_of_new_folder)
    write_references(commit_id, repository)


def create_commit_folder(images_path: Path) -> str:
    folder_name = create_folder_name()
    path_of_new_folder = os.path.join(images_path, folder_name)
    os.mkdir(path_of_new_folder)
    return path_of_new_folder


def create_folder_name():
    length = 20
    chars = '1234567890abcdef'
    folder_name = ''.join(random.choices(chars, k=length))
    return folder_name


def create_commit_txt_file(repository: Path, images_path: Path, path_of_new_folder: str, message: str) -> None:
    parent_head = get_parent_head(repository)
    txt_file = images_path.joinpath(Path(path_of_new_folder).name + '.txt')
    txt_file.write_text(
        f'parent = {parent_head if parent_head else None}\n'
        f'date = {datetime.datetime.now().strftime("%c")}\n'
        f'message = {message}'
    )


def get_parent_head(repository: Path) -> str:
    wit_folder = repository.joinpath('.wit')
    references_file = wit_folder.joinpath('references.txt')
    if references_file.exists():
        ref_path = wit_folder.joinpath('references.txt')
        with ref_path.open() as f_h:
            references_content = f_h.readlines()
            head_line = references_content[0].split('=')
        return head_line[1].strip()
    return ''


def save_files(repository: Path, path_of_new_folder: str) -> None:
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    for item in os.listdir(staging_area_path):
        src = os.path.join(staging_area_path, item)
        dst = os.path.join(path_of_new_folder, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)


def write_references(commit_id: str, repository: Path) -> None:
    wit_folder = repository.joinpath('.wit')
    ref_file = wit_folder.joinpath('references.txt')
    activated_path = wit_folder.joinpath('activated.txt')
    activated_branch = activated_path.read_text()
    new_content = '='.join((activated_branch, commit_id))  # ???
    if ref_file.exists():
        with open(ref_file, "r") as references_file:
            data = references_file.readlines()
        current_head_id = data[0].split("=")[1].strip()
        branches_data = data[1:]
        new_content = ""
        for line in branches_data:
            branch_name = line.split("=")[0]
            branch_id = line.split("=")[1].strip()
            if branch_name == activated_branch:
                activated_id = branch_id
                if activated_id == current_head_id:
                    line = "=".join((branch_name, commit_id))
            new_content += line
    ref_file.write_text(f'HEAD={commit_id}\n{new_content}')
