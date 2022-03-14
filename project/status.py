from filecmp import dircmp
import os
from pathlib import Path
from typing import Union, Iterator

from errors import WitError
from global_functions import get_repository_path, get_head_reference, get_all_files_in_directory_and_subs

# If I do "add_function" to a file / folder inside folder 1 (test\folder1\folder2\...) -
# sometimes all other files/ folders inside don't appear in Untracked files.
# and other times they don't appear in Changes to be committed. Very weired...


def status_function():
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    staging_area_path = os.path.join(repository, '.wit', 'staging_area')
    commit_id = get_head_reference(repository)
    message_if_no_commit = "No commit_function was done yet."
    commit_path = os.path.join(repository, '.wit', 'images', commit_id)
    changes_to_be_committed = show_files(get_changes_to_be_committed(commit_path, staging_area_path))
    changes_not_staged_for_commit = show_files(get_changes_not_staged_for_commit(repository, staging_area_path))
    untracked_files = show_files(get_untracked_files(repository, staging_area_path))
    print(
        f"###Commit id:###\n{commit_id if commit_id else message_if_no_commit}\n\n"
        f"###Changes to be committed:###\n{changes_to_be_committed}\n\n"
        f"###Changes not staged for commit_function:###\n{changes_not_staged_for_commit}\n\n"
        f"###Untracked files:###\n{untracked_files}\n"
    )


def show_files(files: Iterator[str]) -> str:
    return '\n'.join(files)


# def get_all_files_in_directory_and_subs(directory: Union[Path, str], start_path: Union[Path, str]) -> Iterator[Path]:
#     for root, dirs, files in os.walk(directory, topdown=True):
#         if not files and not dirs:
#             yield Path(root).relative_to(start_path)
#         for file in files:
#             file_abs_path = Path(root) / file
#             yield file_abs_path.relative_to(start_path)
#         for dir_name in dirs:
#             yield from get_all_files_in_directory_and_subs(directory / dir_name, start_path)


def get_changes_to_be_committed(commit_path: Union[Path, str], staging_area_path: Union[Path, str]) -> Iterator[str]:
    """
    Yield files that the user added to staging area since last commit_function and will be added
    to the next commit_function."""
    # sometimes I get the full path of the file and sometimes only the file name.
    cmp = dircmp(commit_path, staging_area_path)
    yield from get_new_and_changed_files(cmp, staging_area_path)
    for d, d_cmp in cmp.subdirs.items():
        yield from get_new_and_changed_files(d_cmp, os.path.join(staging_area_path, d))


def get_new_and_changed_files(cmp: dircmp[Union[str, bytes]], dir_path: Union[Path, str]) -> Iterator[str]:
    """Yield files that are new in the directory or have different content."""
    yield from get_new_files_added(cmp, dir_path)
    yield from get_changed_files(cmp, dir_path)


def get_changed_files(cmp: dircmp[Union[str, bytes]], dir_path: Union[Path, str]) -> Iterator[str]:
    """Yield files that have different content."""
    diff_files = cmp.diff_files
    start_path = os.path.join(get_repository_path(Path.cwd()), '.wit', 'staging_area')
    for diff in diff_files:
        file_path = os.path.join(dir_path, diff)
        rel = os.path.relpath(file_path, start=start_path)
        yield rel


def get_new_files_added(cmp: dircmp[Union[str, bytes]], dir_path: Union[Path, str], start_path=None) -> Iterator[str]:
    """Yield files that are new in the directory."""
    new_files_added = cmp.right_only
    for f in new_files_added:
        f_path = Path(dir_path) / f
        if os.path.isfile(f_path):
            yield f if not start_path else os.path.relpath(f_path, start=start_path)
        yield from get_all_files_in_directory_and_subs(f_path, start_path=dir_path if not start_path else start_path)


def get_changes_not_staged_for_commit(repository: Union[Path, str], staging_area_path: Union[Path, str]) -> Iterator[str]:
    """Yield files in staging area which their content in repository doesn't match their content in staging area."""
    cmp = dircmp(repository, staging_area_path)
    yield from get_changed_files(cmp, staging_area_path)
    for common_dir in cmp.common_dirs:
        path_in_repository = os.path.join(repository, common_dir)
        path_in_staging_area = os.path.join(staging_area_path, common_dir)
        yield from get_changes_not_staged_for_commit(path_in_repository, path_in_staging_area)


def get_untracked_files(repository: Union[Path, str], staging_area_path: Union[Path, str]) -> Iterator[str]:
    """Yield files that exist only in repository and were never added to staging area."""
    # # this gives all untracked files, but I didn't succeed to get full path correctly:
    # cmp = dircmp(staging_area_path, repository, ignore=['.wit'])
    # yield from get_new_files_added(cmp, repository)
    # for common_dir in cmp.common_dirs:
    #     path_in_repository = os.path.join(repository, common_dir)
    #     path_in_staging_area = os.path.join(staging_area_path, common_dir)
    #     yield from get_untracked_files(path_in_repository, path_in_staging_area)
    cmp = dircmp(staging_area_path, repository, ignore=['.wit'])
    yield from get_new_files_added(cmp, repository)
    for d, d_cmp in cmp.subdirs.items():
        yield from get_new_files_added(d_cmp, os.path.join(repository, d), start_path=repository)
