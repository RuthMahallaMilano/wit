from add import get_directory_with_wit
from commit import get_parent_head
from errors import WitError

from filecmp import dircmp
import os
from pathlib import Path
from typing import Union, Iterator


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
