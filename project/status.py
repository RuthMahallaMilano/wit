from glob import glob
from pathlib import Path
from typing import Iterator

from errors import WitError
from utils import (
    get_all_files_in_directory_and_subs,
    get_head_reference,
    get_repository_path,
)


def status_function() -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    staging_area_path = repository / ".wit" / "staging_area"
    last_commit_id = get_head_reference(repository)
    message_if_no_commit = "No commit was done yet."
    changes_to_be_committed = show_files(
        get_changes_to_be_committed(repository, staging_area_path)
    )
    changes_not_staged_for_commit = show_files(
        get_changes_not_staged_for_commit(repository, staging_area_path)
    )
    untracked_files = show_files(get_untracked_files(repository, staging_area_path))
    print(
        f"###Commit id:###\n{last_commit_id if last_commit_id else message_if_no_commit}\n\n"
        f"###Changes to be committed:###\n{changes_to_be_committed}\n\n"
        f"###Changes not staged for commit:###\n{changes_not_staged_for_commit}\n\n"
        f"###Untracked files:###\n{untracked_files}\n"
    )


def show_files(files: Iterator[Path]) -> str:
    txt = ""
    for file in files:
        txt += str(file) + "\n"
    return txt


def get_changes_to_be_committed(
    repository: Path, staging_area_path: Path
) -> Iterator[Path]:
    last_commit_id = get_head_reference(repository)
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area_path)
    if not last_commit_id:
        for file_path in files_in_staging_area:
            yield file_path
    else:
        commit_path = repository / ".wit" / "images" / last_commit_id
        for file_path in files_in_staging_area:
            path_in_last_commit = commit_path / file_path
            if not glob(str(path_in_last_commit)):
                yield file_path
            elif file_path.is_file():
                if check_if_file_changed(file_path, staging_area_path, commit_path):
                    yield file_path


def check_if_file_changed(file_path: Path, dir_1: Path, dir_2: Path) -> bool:
    content_in_dir_1 = (dir_1 / file_path).read_text()
    content_in_dir_2 = (dir_2 / file_path).read_text()
    return content_in_dir_1 != content_in_dir_2


def get_changes_not_staged_for_commit(
    repository: Path, staging_area_path: Path
) -> Iterator[Path]:
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area_path)
    for file_path in files_in_staging_area:
        path_in_repository = repository / file_path
        if not glob(str(path_in_repository)):
            raise NotImplementedError(
                f"The file {file_path} was deleted. Deleting files not implemented yet."
            )
        if file_path.is_file():
            if check_if_file_changed(file_path, staging_area_path, repository):
                yield file_path


def get_untracked_files(repository: Path, staging_area_path: Path) -> Iterator[Path]:
    files_in_repository = get_all_files_in_directory_and_subs(repository, repo=True)
    for file_path in files_in_repository:
        path_in_staging_area = staging_area_path / file_path
        if not glob(str(path_in_staging_area)):
            yield file_path
