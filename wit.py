import datetime
import filecmp
import os
from pathlib import Path
import random
import shutil
import sys
from typing import Any, Generator, Optional, Union


def init() -> None:
    cwd = os.getcwd()
    wit_path = os.path.join(cwd, '.wit')
    os.mkdir(wit_path)
    os.mkdir(os.path.join(wit_path, 'images'))
    os.mkdir(os.path.join(wit_path, 'staging_area'))
    activated_path = os.path.join(wit_path, 'activated.txt')
    Path(activated_path).write_text('master')


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
    folder_name = create_commit_name()
    path_of_new_folder = os.path.join(images_path, folder_name)
    os.mkdir(path_of_new_folder)
    return path_of_new_folder


def create_commit_name():
    length = 20
    chars = '1234567890abcdef'
    folder_name = ''.join(random.choices(chars, k=length))
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


# בעת הרצת פקודת commit, יתעדכן (כרגיל) ה־HEAD כך שיצביע ל־commit החדש שנוצר.
# לפני עדכון ה־HEAD, בדקו אם ה־branch שנמצא במצב “פעיל” מצביע לאותו מקום שבו נמצא ה־HEAD.
# אם כן, עדכנו את references.txt כך שה־branch יצביע למספר ה־commit החדש שנוצר.

def write_references(commit_id: str, dir_with_wit: Path) -> None:
    wit_folder = dir_with_wit.joinpath('.wit')
    ref_file = wit_folder.joinpath('references.txt')
    # new_branch_id = commit_id  # new_master = commit_id
    activated_path = wit_folder.joinpath('activated.txt')
    activated_branch = activated_path.read_text()
    new_content = '='.join((activated_branch, commit_id))
    if ref_file.exists():
        content = ref_file.read_text().split()
        head_line = content[0]
        head_id = head_line.split('=')[1]
        branches_data = content[1:]
        new_content = head_line
        for line in branches_data:
            name_and_id = line.split('=')
            branch_name = name_and_id[0]
            branch_id = name_and_id[1]
            if branch_name == activated_branch:
                if branch_id == head_id:
                    line = '='.join((branch_name, commit_id))
            new_content += line
    ref_file.write_text(f'HEAD={commit_id}\n{new_content}')


def status() -> None:
    repository = get_directory_with_wit(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    commit_id = get_parent_head(repository)
    files_added_since_last_commit = get_files_added_since_last_commit(commit_id, repository)
    files_changed_since_last_commit = get_files_changed_since_last_commit(commit_id, repository)
    files_in_staging_area_that_dont_match_original = get_files_in_staging_area_that_dont_match_original(repository)
    files_not_in_staging_area = get_files_not_in_staging_area(repository)
    print(
        f"Commit id: {commit_id}\n"
        f"Changes to be committed: {(list(files_added_since_last_commit) + list(files_changed_since_last_commit))}\n"
        f"Changes not staged for commit: {list(files_in_staging_area_that_dont_match_original)}\n"
        f"Untracked files: {list(files_not_in_staging_area)}"
    )


def get_files_added_since_last_commit(commit_id: str, repository: Path) -> Generator[Any, Any, None]:
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    all_files_in_stagind_area_and_sub = get_files_of_dir_and_subdirs(staging_area_path)
    all_files_in_commit_and_sub_dirs = get_files_of_dir_and_subdirs(commit_path)
    for file in all_files_in_stagind_area_and_sub:
        if file not in all_files_in_commit_and_sub_dirs:
            yield file


def get_files_changed_since_last_commit(commit_id: str, repository: Path) -> Generator[str, Any, None]:
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    all_files_in_commit_and_sub = get_all_files_in_dir_and_subs(commit_path)
    all_files_in_staging_area_and_sub = get_all_files_in_dir_and_subs(staging_area_path)
    yield from get_names_of_changed_files(
        all_files_in_commit_and_sub, all_files_in_staging_area_and_sub, commit_path, staging_area_path
    )


def get_names_of_changed_files(
        all_files_in_commit_and_sub: Generator[Union[bytes, str], Any, None],
        all_files_in_staging_area_and_sub: Generator[Union[bytes, str], Any, None],
        commit_path: Union[str, Path],
        staging_area_path: Union[str, Path]
) -> Generator[str, Any, None]:
    for s_file in all_files_in_staging_area_and_sub:
        for c_file in all_files_in_commit_and_sub:
            if Path(s_file).relative_to(staging_area_path) == Path(c_file).relative_to(commit_path):
                if not filecmp.cmp(s_file, c_file):
                    yield Path(s_file).name


def get_all_files_in_dir_and_subs(commit_path: str) -> Generator[Union[bytes, str], Any, None]:
    for (root, dirs, files) in os.walk(commit_path, topdown=True):
        for file in files:
            yield os.path.join(root, file)


def get_files_in_staging_area_that_dont_match_original(repository: Path) -> Generator[str, Any, None]:
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    all_files_in_repository_and_sub_dirs = get_all_files_and_dirs_in_repository(repository)
    all_files_in_staging_area_and_sub = get_all_files_in_dir_and_subs(staging_area_path)
    yield from get_names_of_changed_files(
        all_files_in_staging_area_and_sub, all_files_in_repository_and_sub_dirs, staging_area_path, repository
    )


def get_all_files_and_dirs_in_repository(repository: Path) -> Generator[Union[bytes, str], Any, None]:
    for (root, dirs, files) in os.walk(repository, topdown=True):
        if '.wit' not in Path(root).parts:
            for file in files:
                yield os.path.join(root, file)


def get_files_not_in_staging_area(repository: Path) -> Generator[Any, Any, None]:
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    files_names_in_repository_and_sub_dirs = get_files_names_of_repository_and_subs(repository)
    all_files_in_staging_area_and_sub_dirs = get_files_of_dir_and_subdirs(staging_area_path)
    for file in files_names_in_repository_and_sub_dirs:
        if file not in all_files_in_staging_area_and_sub_dirs:
            yield file


def get_files_names_of_repository_and_subs(repository: Path):
    for (root, dirs, files) in os.walk(repository, topdown=True):
        if '.wit' not in Path(root).parts:
            for file in files:
                yield file


def get_files_of_dir_and_subdirs(file_path: str) -> Generator[Any, Any, None]:
    for (root, dirs, files) in os.walk(file_path, topdown=True):
        for file in files:
            yield file


def checkout(commit_id_or_branch: str) -> None:
    repository = get_directory_with_wit(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = repository.joinpath('.wit', 'references.txt')
    last_commit_id = get_parent_head(repository)
    if (
        list(get_files_added_since_last_commit(last_commit_id, repository))
        or list(get_files_changed_since_last_commit(last_commit_id, repository))
        or list(get_files_in_staging_area_that_dont_match_original(repository))
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit")
    commit_id = get_commit_id_of_branch(commit_id_or_branch, references_file)
    print(commit_id)
    change_files_in_main_folder(repository, commit_id)
    change_head_in_references_file(commit_id, references_file)
    change_staging_area_folder(repository, commit_id)
    write_activated(commit_id, commit_id_or_branch, repository)  #


def write_activated(commit_id: str, commit_id_or_branch: str, repository: Path) -> None:
    activated_path = repository.joinpath('.wit', 'activated.txt')
    Path(activated_path).write_text(commit_id_or_branch)


def get_commit_id_of_branch(commit_id_or_branch: str, references_file: Path) -> str:
    with references_file.open() as file:
        references_content = file.readlines()
        branches_data = references_content[1:]
        for branch_line in branches_data:
            name_and_id = branch_line.split('=')
            branch_name = name_and_id[0]
            branch_id = name_and_id[1]
            if branch_name == commit_id_or_branch:
                return branch_id
    return commit_id_or_branch


def change_head_in_references_file(commit_id: str, references_file: Path) -> None:
    with references_file.open() as file:
        branches = file.readlines()[1:]
        branches_txt = ''.join(branches)
    references_file.write_text(f'HEAD={commit_id}\n{branches_txt}')


def get_master_commit_id(references_file: Path) -> str:
    with references_file.open() as file:
        references_content = file.readlines()
        master_line = references_content[1].split('=')
        commit_id = master_line[-1].strip()
    return commit_id


def change_files_in_main_folder(repository: Path, commit_id: str) -> None:
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    # all_files_in_repository_and_sub_dirs = get_all_files_and_dirs_in_repository(repository)
    all_files_in_repository_and_sub_dirs = []
    for (root, dirs, files) in os.walk(repository, topdown=True):
        if '.wit' not in Path(root).parts:
            for file in files:
                all_files_in_repository_and_sub_dirs.append(os.path.join(root, file))
    # all_files_in_commit_and_sub_dirs = get_files_of_dir_and_subdirs(commit_path)  # didn't work with the functions
    all_files_in_commit_and_sub_dirs = []
    for (root, dirs, files) in os.walk(commit_path, topdown=True):
        for file in files:
            all_files_in_commit_and_sub_dirs.append(os.path.join(root, file))
    for c_file in all_files_in_commit_and_sub_dirs:
        for r_file in all_files_in_repository_and_sub_dirs:
            if Path(r_file).relative_to(repository) == Path(c_file).relative_to(commit_path):
                shutil.copy2(c_file, r_file)


def change_staging_area_folder(dir_with_wit: Path, commit_id: str):
    staging_area_path = dir_with_wit.joinpath('.wit', 'staging_area')
    commit_path = dir_with_wit.joinpath('.wit', 'images', commit_id)
    for file_or_dir in staging_area_path.iterdir():
        if file_or_dir.is_file():
            file_or_dir.unlink()
        else:
            shutil.rmtree(file_or_dir)
    for file in commit_path.iterdir():
        rel_path = Path(file).relative_to(commit_path)
        if file.is_file():
            shutil.copy2(file, staging_area_path.joinpath(rel_path))
        else:
            shutil.copytree(file, staging_area_path.joinpath(rel_path))


def branch(name: str) -> None:
    repository = get_directory_with_wit(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = repository.joinpath('.wit', 'references.txt')
    commit_id = get_parent_head(repository)
    with references_file.open('a') as ref_file:
        ref_file.write(f'\n{name}={commit_id}')


class WitError(Exception):
    pass


class FilesDoesntMatchError(Exception):
    pass


def is_command_correct(argv: list[str]) -> bool:
    if argv[1] in ['init', 'status']:
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

elif sys.argv[1] == 'branch':
    if is_command_correct(sys.argv):
        branch(sys.argv[2])
    else:
        print(fr"Usage: python {sys.argv[0]} branch <NAME>")
