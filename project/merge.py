import os
import re
from glob import glob
from pathlib import Path
from typing import Iterator

from commit import commit_function
from errors import FilesDoesntMatchError, MergeError, NoCommonCommitError, WitError
from global_functions import (
    get_activated_branch,
    get_all_files_in_directory_and_subs,
    get_commit_id_of_branch,
    get_head_reference,
    get_repository_path,
)
from status import get_changes_not_staged_for_commit, get_changes_to_be_committed

regex = re.compile(
    r"^parent = (?P<commit_id_1>\w{20})(, (?P<commit_id_2>\w{20}))?$",
    flags=re.MULTILINE,
)


def merge_function(branch_name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    wit_dir = repository / ".wit"
    staging_area_path = wit_dir / "staging_area"
    references_file = wit_dir / "references.txt"
    head_reference = get_head_reference(repository)
    branch_commit_id = get_commit_id_of_branch(branch_name, references_file)
    if list(get_changes_to_be_committed(repository, staging_area_path)) or list(
        get_changes_not_staged_for_commit(repository, staging_area_path)
    ):
        raise FilesDoesntMatchError(
            "There are files added or changed after last commit_function"
        )
    if branch_commit_id == head_reference:
        raise MergeError("Head is already at the branch you are trying to merge.")
    common_commit = get_common_commit(wit_dir, branch_commit_id, head_reference)
    if not common_commit:
        raise NoCommonCommitError(f"There is no common commit with {branch_name}.")
    common_dir = wit_dir / "images" / common_commit
    branch_dir = wit_dir / "images" / branch_commit_id
    branch_files, common_files = get_common_and_branch_files(branch_dir, common_dir)
    check_common_commit_and_update_staging_area_and_repository(
        branch_dir, common_dir, common_files, staging_area_path, repository
    )
    check_branch_and_update_staging_area_and_repository(
        branch_dir, branch_files, common_dir, staging_area_path, repository
    )
    commit_merge(branch_commit_id, branch_name, head_reference, wit_dir)


def check_branch_and_update_staging_area_and_repository(
    branch_dir: Path,
    branch_files: Iterator[Path],
    common_dir: Path,
    staging_area_path: Path,
    repository: Path,
) -> None:
    for file_path in branch_files:
        (
            path_in_branch,
            path_in_common,
            path_in_staging_area,
            path_in_repository,
        ) = get_file_path_in_all_dirs(
            file_path, branch_dir, common_dir, staging_area_path, repository
        )
        if not glob(str(path_in_common)):
            create_new_file_in_staging_area_and_repository(
                file_path, path_in_branch, path_in_staging_area, path_in_repository
            )


def check_common_commit_and_update_staging_area_and_repository(
    branch_dir: Path,
    common_dir: Path,
    common_files: Iterator[Path],
    staging_area_path: Path,
    repository: Path,
) -> None:
    for file_path in common_files:
        (
            path_in_branch,
            path_in_common,
            path_in_staging_area,
            path_in_repository,
        ) = get_file_path_in_all_dirs(
            file_path, branch_dir, common_dir, staging_area_path, repository
        )
        if not glob(str(path_in_branch)) or not glob(str(path_in_staging_area)):
            raise NotImplementedError(
                f"The file {file_path} was deleted. Deleting files not implemented yet."
            )
        elif file_path.is_file():
            update_file_in_staging_area_and_repository(
                file_path,
                path_in_branch,
                path_in_common,
                path_in_staging_area,
                path_in_repository,
            )


def get_common_and_branch_files(
    branch_dir: Path, common_dir: Path
) -> tuple[Iterator[Path], Iterator[Path]]:
    common_files = get_all_files_in_directory_and_subs(common_dir)
    branch_files = get_all_files_in_directory_and_subs(branch_dir)
    return branch_files, common_files


def update_file_in_staging_area_and_repository(
    file_path: Path,
    path_in_branch: Path,
    path_in_common: Path,
    path_in_staging_area: Path,
    path_in_repository: Path,
) -> None:
    content_in_common = path_in_common.read_text()
    content_in_branch = path_in_branch.read_text()
    content_in_staging_area = path_in_staging_area.read_text()
    if content_in_common != content_in_branch:
        if content_in_common != content_in_staging_area:
            raise NotImplementedError(
                f"{file_path} was changed in both branches. Not implemented yet."
            )
        path_in_staging_area.write_text(content_in_branch)
        path_in_repository.write_text(content_in_branch)


def get_file_path_in_all_dirs(
    file_path: Path,
    branch_dir: Path,
    common_dir: Path,
    staging_area_path: Path,
    repository: Path,
) -> tuple[Path, ...]:
    path_in_common = common_dir / file_path
    path_in_staging_area = staging_area_path / file_path
    path_in_branch = branch_dir / file_path
    path_in_repository = repository / file_path
    return path_in_branch, path_in_common, path_in_staging_area, path_in_repository


def commit_merge(
    branch_commit_id: str, branch_name: str, head_reference: str, wit_dir: Path
) -> None:
    activated = get_activated_branch(wit_dir)
    message = f"Commit after merge of {activated if activated else head_reference} and {branch_name}."
    commit_function(message, branch_commit_id)


def create_new_file_in_staging_area_and_repository(
    file_path: Path,
    path_in_branch: Path,
    path_in_staging_area: Path,
    path_in_repository: Path,
) -> None:
    if file_path.is_file():
        content_in_branch = path_in_branch.read_text()
        path_in_staging_area.write_text(content_in_branch)
        path_in_repository.write_text(content_in_branch)
    else:
        os.mkdir(path_in_staging_area)
        os.mkdir(path_in_repository)


def get_common_commit(wit_dir: Path, branch_commit_id: str, head_reference: str) -> str:
    branch_parents = set(get_parents_commits(wit_dir, branch_commit_id))
    head_parents = set(get_parents_commits(wit_dir, head_reference))
    if branch_commit_id in head_parents:
        return branch_commit_id
    if head_reference in branch_parents:
        return head_reference
    common = branch_parents.intersection(head_parents)
    if common:
        return common.pop()
    return ""


def get_parents_commits(wit_dir: Path, commit_id: str) -> Iterator[str]:
    images_path = wit_dir / "images"
    yield from get_parents_of_commit_id(commit_id, images_path)


def get_parents_of_commit_id(commit_id: str, images_path: Path) -> Iterator[str]:
    while commit_id:
        commit_file = images_path / (commit_id + ".txt")
        commit_txt = commit_file.read_text()
        parent_id_match = regex.match(commit_txt)
        if parent_id_match:
            parent_id_1 = parent_id_match.group("commit_id_1")
            parent_id_2 = parent_id_match.group("commit_id_2")
            yield parent_id_1
            if parent_id_2:
                yield parent_id_2
                yield from get_parents_of_commit_id(parent_id_2, images_path)
        commit_id = parent_id_1 if parent_id_match else ""
