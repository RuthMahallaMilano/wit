# upload 172
import datetime
import filecmp
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
            shutil.copytree(src, dst)  # todo ??


def write_references(commit_id: str, dir_with_wit: Path) -> None:
    wit_folder = dir_with_wit.joinpath('.wit')
    ref_file = wit_folder.joinpath('references.txt')
    old_commit_id = get_parent_head(dir_with_wit)
    print(old_commit_id)
    master_id = get_master_commit_id(ref_file)
    if old_commit_id == master_id:
        ref_file.write_text(f'HEAD={commit_id}\nMASTER={commit_id}\n')
    else:
        ref_file.write_text(f'HEAD={commit_id}\nMASTER={master_id}\n')


###########


def status():
    dir_with_wit = get_directory_with_wit(Path.cwd())
    if not dir_with_wit:
        raise WitError("<.wit> file not found")
    commit_id = get_parent_head(dir_with_wit)
    files_added_or_changed_since_last_commit = get_files_added_or_changed_since_last_commit(commit_id, dir_with_wit)
    files_in_staging_area_that_dont_match_original = get_files_in_staging_area_that_dont_match_original(dir_with_wit)
    files_not_in_staging_area = get_files_not_in_staging_area(dir_with_wit)
    print(
        f"Commit id: {commit_id}\n"
        f"Changes to be committed: {[file for file in files_added_or_changed_since_last_commit if file]}\n"
        f"Changes not staged for commit: {[file for file in files_in_staging_area_that_dont_match_original if file]}\n"
        f"Untracked files: {[file for file in files_not_in_staging_area]}"
    )


def get_files_added_or_changed_since_last_commit(commit_id: str, dir_with_wit: Path) -> list[str]:
    commit_path = os.path.join(dir_with_wit, '.wit', 'images', commit_id)
    staging_area_path = os.path.join(dir_with_wit, '.wit', 'staging_area')
    dir_cmp = filecmp.dircmp(a=commit_path, b=staging_area_path)
    yield dir_cmp.right_only
    yield dir_cmp.diff_files
    # while dir_cmp.subdirs:
    for sub in dir_cmp.subdirs.values():
        dir_cmp = sub
        yield dir_cmp.right_only
        yield dir_cmp.diff_files
    #  return dir_cmp.right_only + dir_cmp.diff_files


def get_files_in_staging_area_that_dont_match_original(dir_with_wit: Path) -> list[str]:
    staging_area_path = os.path.join(dir_with_wit, '.wit', 'staging_area')
    dir_cmp = filecmp.dircmp(a=dir_with_wit, b=staging_area_path)
    yield dir_cmp.diff_files
    # while dir_cmp.subdirs:
    for sub in dir_cmp.subdirs.values():
        yield sub.diff_files


def get_files_not_in_staging_area(dir_with_wit: Path) -> list[str]:
    staging_area_path = os.path.join(dir_with_wit, '.wit', 'staging_area')
    dir_cmp = filecmp.dircmp(a=dir_with_wit, b=staging_area_path)
    yield dir_cmp.left_only
    for sub in dir_cmp.subdirs.values():
        yield sub.left_only


##########
#
#
#
#
# def status():
#     repository = get_directory_with_wit(Path.cwd())
#     if not repository:
#         raise WitError("<.wit> file not found")
#     commit_id = get_parent_head(repository)
#     commit_path = os.path.join(repository, '.wit', 'images', commit_id)
#     staging_area_path = os.path.join(repository, '.wit', 'staging_area')
#     cmp = filecmp.dircmp(staging_area_path, commit_path)
#     files_added_since_last_commit = [f for f in get_files_added_since_last_commit(cmp)]
#     print(files_added_since_last_commit)
#
#
#
#     #
#     # files_in_staging_area_that_dont_match_original = get_files_in_staging_area_that_dont_match_original(repository)
#     # files_not_in_staging_area = get_files_not_in_staging_area(repository)
#     # print(
#     #     f"Commit id: {commit_id}\n"
#     #     f"Changes to be committed: {files_added_or_changed_since_last_commit}\n"
#     #     f"Changes not staged for commit: {[file for file in files_in_staging_area_that_dont_match_original if file]}\n"
#     #     f"Untracked files: {[file for file in files_not_in_staging_area]}"
#
#    # )
#
#
# def get_files_added_since_last_commit(cmp):
#     # cmp = filecmp.dircmp(staging_area_path, commit_path)
#     for name in cmp.left_only:
#         yield name
#     for sub_cmp in cmp.subdirs.values():
#         get_files_added_since_last_commit(sub_cmp)
#
#
#
#     # for file_name in Path(staging_area_path).iterdir():
#     #     if file_name.name not in [f.name for f in Path(commit_path).iterdir()]:
#     #         yield file_name.name
#     #     elif file_name.is_dir():
#     #         path_in_staging_area = os.path.join(staging_area_path, file_name.name)
#     #         path_in_commit = os.path.join(commit_path, file_name.name)
#     #         get_files_changed_since_last_commit(path_in_commit, path_in_staging_area)
#     #
#
#
#
#
#
#
#
#
#
#
# def get_files_changed_since_last_commit(staging_area_path: str, commit_path: str):
#     pass
############


def checkout(commit_id: str):
    dir_with_wit = get_directory_with_wit(Path.cwd())
    if not dir_with_wit:
        raise WitError("<.wit> file not found")
    # if files_added_or_changed_since_last_commit or files_in_staging_area_that_dont_match_original:
    #   return False
    references_file = dir_with_wit.joinpath('.wit', 'references.txt')

    if commit_id == 'master':
        commit_id = get_master_commit_id(references_file)
    change_files_in_main_folder(dir_with_wit, commit_id)
    with references_file.open() as file:
        master = file.readlines()[1]
    references_file.write_text(f'HEAD={commit_id}\n{master}\n')
    change_staging_area_folder(dir_with_wit, commit_id)


def get_master_commit_id(references_file):
    with references_file.open() as file:
        commit_id = file.readlines()[1][7:].strip()
    return commit_id


def change_files_in_main_folder(dir_with_wit: Path, commit_id : str) -> None:
    commit_path = os.path.join(dir_with_wit, '.wit', 'images', commit_id)
    for item in os.listdir(commit_path):
        src = os.path.join(commit_path, item)
        dst = os.path.join(dir_with_wit, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.exists(dst):
                print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")  # todo how to replace if exists
        else:
            shutil.copytree(src, dst)


def change_staging_area_folder(dir_with_wit, commit_id):
    staging_area_path = os.path.join(dir_with_wit, '.wit', 'staging_area')
    commit_path = os.path.join(dir_with_wit, '.wit', 'images', commit_id)
    shutil.rmtree(staging_area_path)
    shutil.copytree(commit_path, staging_area_path)




class WitError(Exception):
    pass


def is_init_status_command_correct(argv: list[str]) -> bool:
    return len(argv) == 2


def is_add_commit_checkout_command_correct(argv: list[str]) -> bool:
    return len(argv) == 3


if sys.argv[1] == 'init':
    if is_init_status_command_correct(sys.argv):
        init()
    else:
        print(fr"Usage: python {sys.argv[0]} init")

elif sys.argv[1] == 'add':
    if is_add_commit_checkout_command_correct(sys.argv):
        add(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} add <file_path>")

elif sys.argv[1] == 'commit':
    if is_add_commit_checkout_command_correct(sys.argv):
        commit(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} commit MESSAGE")

elif sys.argv[1] == 'status':
    if is_init_status_command_correct(sys.argv):
        status()
    else:
        print(fr"Usage: python {sys.argv[0]} status")

elif sys.argv[1] == 'checkout':
    if is_add_commit_checkout_command_correct(sys.argv):
        checkout(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} checkout <commit_id>")

