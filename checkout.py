# upload 174
import datetime
from filecmp import dircmp
import os
from pathlib import Path
import random
import shutil
import sys
from typing import Optional, Union, Iterator


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


def get_directory_with_wit(file: Path) -> Optional[Path]:
    parents = file.parents
    for p in parents:
        wit = Path.joinpath(p, '.wit')
        if wit.is_dir():
            return p
    return None


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
    folder_name = create_folder_name()
    path_of_new_folder = os.path.join(images_path, folder_name)
    os.mkdir(path_of_new_folder)
    return path_of_new_folder


def create_folder_name():
    length = 20
    chars = '1234567890abcdef'
    folder_name = ''.join(random.choice(chars) for _ in range(length))
    return folder_name


def create_commit_txt_file(dir_with_wit: Path, images_path: Path, path_of_new_folder: str, message: str) -> None:
    parent_head = get_parent_head(dir_with_wit)
    txt_file = images_path.joinpath(Path(path_of_new_folder).name + '.txt')
    txt_file.write_text(
        f'parent = {parent_head if parent_head else None}\n'
        f'date = {datetime.datetime.now().strftime("%c")}\n'
        f'message = {message}'
    )


def get_parent_head(dir_with_wit: Path) -> str:
    wit_folder = dir_with_wit.joinpath('.wit')
    references_file = wit_folder.joinpath('references.txt')
    if references_file.exists():
        ref_path = wit_folder.joinpath('references.txt')
        with ref_path.open() as f_h:
            references_content = f_h.readlines()
            head_line = references_content[0].split('=')
        return head_line[1].strip()
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


def status() -> None:
    repository = get_directory_with_wit(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    commit_id = get_parent_head(repository)
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    changes_to_be_committed = list(get_changes_to_be_committed(commit_path, staging_area_path))
    changes_not_staged_for_commit = list(get_changes_not_staged_for_commit(repository, staging_area_path))
    untracked_files = list(get_untracked_files(repository, staging_area_path))
    print(
        f"Commit id: {commit_id}\n"
        f"Changes to be committed: {changes_to_be_committed}\n"
        f"Changes not staged for commit: {changes_not_staged_for_commit}\n"
        f"Untracked files: {untracked_files}"
    )


def get_all_files_in_directory_and_subs(directory: Union[Path, str], start_path: Union[Path, str]) -> Iterator[str]:
    for (root, dirs, files) in os.walk(directory, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            rel = os.path.relpath(file_path, start=start_path)
            yield rel


def get_changes_to_be_committed(commit_path: Union[Path, str], staging_area_path: Union[Path, str]) -> Iterator[str]:
    cmp = dircmp(commit_path, staging_area_path)
    yield from get_new_and_changed_files(cmp, staging_area_path)
    for d, d_cmp in cmp.subdirs.items():
        yield from get_new_and_changed_files(d_cmp, os.path.join(staging_area_path, d))


def get_new_and_changed_files(cmp: dircmp[Union[str, bytes]], staging_area_path: Union[Path, str]) -> Iterator[str]:
    yield from get_new_files_added(cmp, staging_area_path)
    yield from get_changed_files(cmp, staging_area_path)


def get_changed_files(cmp: dircmp[Union[str, bytes]], staging_area_path) -> Iterator[str]:
    diff_files = cmp.diff_files
    start_path = os.path.join(get_directory_with_wit(Path.cwd()), '.wit', 'staging_area')
    for diff in diff_files:
        file_path = os.path.join(staging_area_path, diff)
        rel = os.path.relpath(file_path, start=start_path)
        yield rel


def get_new_files_added(cmp: dircmp[Union[str, bytes]], staging_area_path: Union[Path, str]) -> Iterator[str]:
    new_files_added = cmp.right_only
    start_path = staging_area_path
    for f in new_files_added:
        f_path = os.path.join(staging_area_path, f)
        if os.path.isfile(f_path):
            yield f
        else:
            yield from get_all_files_in_directory_and_subs(f_path, start_path)


def get_changes_not_staged_for_commit(
        repository: Union[Path, str], staging_area_path: Union[Path, str]
) -> Iterator[str]:
    cmp = dircmp(repository, staging_area_path)
    yield from get_changed_files(cmp, staging_area_path)
    for common_dir in cmp.common_dirs:
        path_in_repository = os.path.join(repository, common_dir)
        path_in_staging_area = os.path.join(staging_area_path, common_dir)
        yield from get_changes_not_staged_for_commit(path_in_repository, path_in_staging_area)


def get_untracked_files(repository: Union[Path, str], staging_area_path: Union[Path, str]) -> Iterator[str]:
    cmp = dircmp(staging_area_path, repository, ignore=['.wit'])
    yield from get_new_files_added(cmp, repository)
    for common_dir in cmp.common_dirs:
        path_in_repository = os.path.join(repository, common_dir)
        path_in_staging_area = os.path.join(staging_area_path, common_dir)
        yield from get_untracked_files(path_in_repository, path_in_staging_area)


def checkout(commit_id: str) -> None:
    repository = get_directory_with_wit(Path.cwd())
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    last_commit_id = get_parent_head(repository)
    last_commit_path = os.path.join(repository, '.wit', 'images', last_commit_id)
    if not repository:
        raise WitError("<.wit> file not found")
    if (
        list(get_changes_to_be_committed(last_commit_path, staging_area_path))
        or list(get_changes_not_staged_for_commit(repository, staging_area_path))
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit")
    references_file = repository.joinpath('.wit', 'references.txt')
    if commit_id == 'master':
        commit_id = get_master_commit_id(references_file)
    change_files_in_main_folder(commit_path, repository)
    change_head_in_references_file(commit_id, references_file)
    change_staging_area_folder(staging_area_path, commit_path)


def change_head_in_references_file(commit_id: str, references_file: Path) -> None:
    with references_file.open() as file:
        content = file.readlines()
    references_file.write_text(f'HEAD={commit_id}\n{content[1:]}')


def get_master_commit_id(references_file: Path) -> str:
    with references_file.open() as file:
        references_content = file.readlines()
        master_line = references_content[-1].split('=')
        commit_id = master_line[-1].strip()
    return commit_id


def change_files_in_main_folder(commit_path: str, repository: Path) -> None:
    files_committed = get_all_files_in_directory_and_subs(commit_path, commit_path)
    for committed_file in files_committed:
        path_in_commit = os.path.join(commit_path, committed_file)
        with open(path_in_commit, 'r') as committed_file_h:
            content = committed_file_h.read()
        path_in_repository = os.path.join(repository, committed_file)
        with open(path_in_repository, "w") as original_file:
            original_file.write(content)


def change_staging_area_folder(staging_area_path: str, commit_path: str):
    for file_or_dir in Path(staging_area_path).iterdir():
        if file_or_dir.is_file():
            file_or_dir.unlink()
        else:
            shutil.rmtree(file_or_dir)
    for file in Path(commit_path).iterdir():
        rel_path = Path(file).relative_to(commit_path)
        if file.is_file():
            shutil.copy2(file, Path(staging_area_path).joinpath(rel_path))
        else:
            shutil.copytree(file, Path(staging_area_path).joinpath(rel_path))


class WitError(Exception):
    pass


class FilesDoesntMatchError(Exception):
    pass


def is_command_correct(argv: list[str]) -> bool:
    if argv[1] in {'init', 'status'}:
        return len(argv) == 2
    else:
        return len(argv) == 3


if sys.argv[1] == 'init':
    if is_command_correct(sys.argv):
        init()
    else:
        print(fr"Usage: python {sys.argv[0]} init")

elif sys.argv[1] == 'add':
    if is_command_correct(sys.argv):
        add(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} add <file_path>")

elif sys.argv[1] == 'commit':
    if is_command_correct(sys.argv):
        commit(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} commit MESSAGE")

elif sys.argv[1] == 'status':
    if is_command_correct(sys.argv):
        status()
    else:
        print(fr"Usage: python {sys.argv[0]} status")

elif sys.argv[1] == 'checkout':
    if is_command_correct(sys.argv):
        checkout(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} checkout <commit_id>")
