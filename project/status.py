from glob import glob
from pathlib import Path
from typing import Iterator, Optional

from project.errors import WitError
from project.utils import (
    get_all_files_in_directory_and_subs,
    get_all_files_in_repository_and_subs,
    get_commit_path,
    get_head_reference,
    get_repository_path,
    get_staging_area,
)


def status_function() -> tuple[Iterator[Path], Iterator[Path], Iterator[Path]]:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    last_commit_id = get_head_reference(repository)
    message_if_no_commit = "No commit was done yet."
    changes_to_be_committed = show_files(get_changes_to_be_committed(repository))
    changes_not_staged_for_commit = show_files(
        get_changes_not_staged_for_commit(repository)
    )
    untracked_files = show_files(get_untracked_files(repository))
    output = (
        f"###Commit id:###\n{last_commit_id if last_commit_id else message_if_no_commit}\n\n"
        f"###Changes to be committed:###\n{changes_to_be_committed}\n\n"
        f"###Changes not staged for commit:###\n{changes_not_staged_for_commit}\n\n"
        f"###Untracked files:###\n{untracked_files}\n"
    )
    print(output)
    return (
        get_changes_to_be_committed(repository),
        get_changes_not_staged_for_commit(repository),
        get_untracked_files(repository),
    )


def show_files(files: Iterator[Path]) -> str:
    txt = ""
    for file in files:
        txt += str(file) + "\n"
    return txt


def get_changes_to_be_committed(repository: Path) -> Optional[Iterator[Path]]:
    staging_area_path = get_staging_area(repository)
    last_commit_id = get_head_reference(repository)
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area_path)
    if not last_commit_id:
        return None
    else:
        commit_path = get_commit_path(repository, last_commit_id)
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


def get_changes_not_staged_for_commit(repository: Path) -> Iterator[Path]:
    staging_area_path = get_staging_area(repository)
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


def get_untracked_files(repository: Path) -> Iterator[Path]:
    staging_area_path = get_staging_area(repository)
    files_in_repository = get_all_files_in_repository_and_subs(repository)
    for file_path in files_in_repository:
        path_in_staging_area = staging_area_path / file_path
        if not glob(str(path_in_staging_area)):
            yield file_path
