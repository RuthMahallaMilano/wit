from collections import namedtuple
from pathlib import Path
from typing import Iterator

from project.commit import commit_function
from project.errors import MergeError, WitError
from project.utils import (
    PARENT_ID_REGEX,
    get_activated_branch,
    get_all_files_in_directory_and_subs,
    get_commit_id_of_branch,
    get_commit_path,
    get_head_reference,
    get_images_path,
    get_references_path,
    get_repository_path,
    get_staging_area_path,
    raise_for_unsaved_work,
)


Paths = namedtuple("Paths", ["branch", "common", "staging_area", "repository"])


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
    common_commit_id = get_common_commit_id(
        repository,
        branch_commit_id,
        head_reference,
    )
    common_commit_path = get_commit_path(repository, common_commit_id)
    branch_path = get_commit_path(repository, branch_commit_id)
    staging_area_path = get_staging_area_path(repository)
    check_common_commit_and_update_staging_area_and_repository(
        branch_path,
        common_commit_path,
        repository,
        staging_area_path,
    )
    check_branch_and_update_staging_area_and_repository(
        branch_path,
        common_commit_path,
        repository,
        staging_area_path,
    )
    commit_merge(branch_commit_id, branch_name, head_reference, repository)


def check_branch_and_update_staging_area_and_repository(
    branch_path: Path,
    common_commit_path: Path,
    repository: Path,
    staging_area_path: Path,
) -> None:
    branch_files = get_all_files_in_directory_and_subs(branch_path)
    for file_path in branch_files:
        paths = Paths(
            branch_path / file_path,
            common_commit_path / file_path,
            staging_area_path / file_path,
            repository / file_path,
        )
        files_in_common_that_match_file = common_commit_path.glob(str(file_path))
        if not set(files_in_common_that_match_file):
            create_new_file_in_staging_area_and_repository(file_path, paths)


def create_new_file_in_staging_area_and_repository(
    file_path: Path, paths: Paths
) -> None:
    if file_path.is_file():
        content_in_branch = paths.branch.read_text()
        file_parent = paths.staging_area.parent
        if not file_parent.exists():
            file_parent.mkdir(parents=True)
        paths.staging_area.write_text(content_in_branch)
        paths.repository.write_text(content_in_branch)
    else:
        paths.staging_area.mkdir(parents=True, exist_ok=True)
        paths.repository.mkdir(parents=True, exist_ok=True)


def check_common_commit_and_update_staging_area_and_repository(
    branch_path: Path,
    common_commit_path: Path,
    repository: Path,
    staging_area_path: Path,
) -> None:
    common_files = get_all_files_in_directory_and_subs(common_commit_path)
    for file_path in common_files:
        if check_if_file_was_deleted(file_path, branch_path, staging_area_path):
            raise NotImplementedError(
                f"The file {file_path} was deleted. Deleting files not implemented yet."
            )
        if file_path.is_file():
            paths = Paths(
                branch_path / file_path,
                common_commit_path / file_path,
                staging_area_path / file_path,
                repository / file_path,
            )
            update_file_in_staging_area_and_repository(file_path, paths)


def check_if_file_was_deleted(
    file_path: Path, branch_path: Path, staging_area_path: Path
) -> bool:
    files_in_branch_that_match_file = branch_path.glob(str(file_path))
    deleted_in_branch = not set(files_in_branch_that_match_file)
    files_in_staging_area_that_match_file = staging_area_path.glob(str(file_path))
    deleted_in_current = not set(files_in_staging_area_that_match_file)
    return deleted_in_branch or deleted_in_current


def update_file_in_staging_area_and_repository(file_path: Path, paths: Paths) -> None:
    content_in_common = paths.common.read_text()
    content_in_branch = paths.branch.read_text()
    content_in_staging_area = paths.staging_area.read_text()
    if content_in_common != content_in_branch:
        if content_in_common != content_in_staging_area:
            raise NotImplementedError(
                f"{file_path} was changed in both branches. Not implemented yet."
            )
        paths.staging_area.write_text(content_in_branch)
        paths.repository.write_text(content_in_branch)


def commit_merge(
    branch_commit_id: str, branch_name: str, head_reference: str, repository: Path
) -> None:
    activated = get_activated_branch(repository)
    current_branch = activated if activated else head_reference
    message = f"Commit after merge of {current_branch} and {branch_name}."
    commit_function(message, branch_commit_id)


def get_common_commit_id(
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
        parent_id_match = PARENT_ID_REGEX.match(commit_txt)
        if parent_id_match:
            parent_id_1 = parent_id_match.group("commit_id_1")
            parent_id_2 = parent_id_match.group("commit_id_2")
            yield parent_id_1
            if parent_id_2:
                yield parent_id_2
                yield from get_parents_of_commit_id(parent_id_2, images_path)
        commit_id = parent_id_1 if parent_id_match else ""
