import shutil
from pathlib import Path
from typing import Union

from errors import BranchDoesntExistError, FilesDoesntMatchError, WitError
from utils import (
    get_all_files_in_directory_and_subs,
    get_commit_id_of_branch,
    get_repository_path,
)
from status import get_changes_not_staged_for_commit, get_changes_to_be_committed


def checkout_function(commit_id_or_branch: str) -> None:
    repository = get_repository_path(Path.cwd())
    staging_area_path = repository / ".wit" / "staging_area"
    if not repository:
        raise WitError("<.wit> file not found")
    if list(get_changes_to_be_committed(repository, staging_area_path)) or list(
        get_changes_not_staged_for_commit(repository, staging_area_path)
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit_function")
    references_file = repository / ".wit" / "references.txt"
    commit_id = get_commit_id_of_branch(commit_id_or_branch, references_file)
    if not commit_id:
        raise BranchDoesntExistError("Branch doesn't exist.")
    if commit_id != commit_id_or_branch:
        write_activated(commit_id_or_branch, repository)
    else:
        write_activated("", repository)
    commit_path = repository / ".wit" / "images" / commit_id
    update_files_in_main_folder(commit_path, repository)
    update_head_in_references_file(commit_id, references_file)
    update_staging_area_folder(staging_area_path, commit_path)


def write_activated(commit_id_or_branch: str, repository: Path) -> None:
    activated_path = repository / ".wit" / "activated.txt"
    activated_path.write_text(commit_id_or_branch)


def update_head_in_references_file(commit_id: str, references_file: Path) -> None:
    with references_file.open() as file:
        branches = file.readlines()[1:]
        branches_txt = "".join(branches)
    references_file.write_text(f"HEAD={commit_id}\n{branches_txt}")


def update_files_in_main_folder(
    commit_path: Union[str, Path], repository: Path
) -> None:
    files_committed = get_all_files_in_directory_and_subs(commit_path)
    for committed_file in files_committed:
        path_in_commit = commit_path / committed_file
        if path_in_commit.is_file():
            with open(path_in_commit, "r") as committed_file_h:
                content = committed_file_h.read()
            path_in_repository = repository / committed_file
            with open(path_in_repository, "w") as original_file:
                original_file.write(content)


def update_staging_area_folder(
    staging_area_path: Union[str, Path], commit_path: Union[str, Path]
):
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
