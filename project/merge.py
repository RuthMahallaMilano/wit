import os
import re
from glob import glob
from pathlib import Path
from typing import Iterator

from project.checkout import raise_for_unsaved_work
from project.commit import commit_function
from project.errors import MergeError, NoCommonCommitError, WitError
from project.utils import (
    get_activated_branch,
    get_all_files_in_directory_and_subs,
    get_commit_id_of_branch,
    get_commit_path,
    get_head_reference,
    get_images_path,
    get_references_path,
    get_repository_path,
    get_staging_area,
)

regex = re.compile(
    r"^parent = (?P<commit_id_1>\w{20})(, (?P<commit_id_2>\w{20}))?$",
    flags=re.MULTILINE,
)


def merge_function(branch_name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    activated = get_activated_branch(repository)
    if branch_name == activated:
        raise MergeError("Head is already at the branch you are trying to merge.")
    references_file = get_references_path(repository)
    head_reference = get_head_reference(repository)
    branch_commit_id = get_commit_id_of_branch(repository, branch_name, references_file)
    raise_for_unsaved_work(repository)
    common_commit = get_common_commit(repository, branch_commit_id, head_reference)
    common_dir = get_commit_path(repository, common_commit)
    branch_dir = get_commit_path(repository, branch_commit_id)
    branch_files, common_files = get_common_and_branch_files(branch_dir, common_dir)
    check_common_commit_and_update_staging_area_and_repository(
        branch_dir, common_dir, common_files, repository
    )
    check_branch_and_update_staging_area_and_repository(
        branch_dir, branch_files, common_dir, repository
    )
    commit_merge(branch_commit_id, branch_name, head_reference, repository)


def check_branch_and_update_staging_area_and_repository(
    branch_dir: Path,
    branch_files: Iterator[Path],
    common_dir: Path,
    repository: Path,
) -> None:
    staging_area_path = get_staging_area(repository)
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
    repository: Path,
) -> None:
    staging_area_path = get_staging_area(repository)
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
    branch_commit_id: str, branch_name: str, head_reference: str, repository: Path
) -> None:
    activated = get_activated_branch(repository)
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


def get_common_commit(
    repository: Path, branch_commit_id: str, head_reference: str
) -> str:
    branch_parents = set(get_parents_commits(repository, branch_commit_id))
    head_parents = set(get_parents_commits(repository, head_reference))
    if branch_commit_id in head_parents:
        return branch_commit_id
    if head_reference in branch_parents:
        return head_reference
    common = branch_parents.intersection(head_parents)
    if common:
        return common.pop()
    return ""


def get_parents_commits(repository: Path, commit_id: str) -> Iterator[str]:
    images_path = get_images_path(repository)
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
