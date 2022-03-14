import re
from pathlib import Path
from typing import Iterator

from commit import commit_function
from errors import WitError, MergeError, NoCommonCommitError, FilesDoesntMatchError
from global_functions import (
    get_commit_id_of_branch,
    get_head_reference,
    get_repository_path,
    get_activated_branch,
    get_all_files_in_directory_and_subs,
)
from status import get_changes_to_be_committed, get_changes_not_staged_for_commit

regex = re.compile(r"^parent = (?P<commit_id>\w{20})$", flags=re.MULTILINE)


def merge_function(branch_name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    branch_commit_id, head_reference, last_commit_path, staging_area_path, wit_dir = get_paths_and_commit_ids(
        branch_name, repository
    )
    if (
        list(get_changes_to_be_committed(last_commit_path, staging_area_path))
        or list(get_changes_not_staged_for_commit(repository, staging_area_path))
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit_function")
    if branch_commit_id == head_reference:
        raise MergeError('Head is already at the branch you are trying to merge.')
    common_commit = get_common_commit(wit_dir, branch_commit_id, head_reference)
    if not common_commit:
        raise NoCommonCommitError(f"There is no common commit with {branch_name}.")
    branch_dir, branch_files, common_dir, common_files, staging_area_files = get_dirs_and_files(
        branch_commit_id, common_commit, staging_area_path, wit_dir,
    )
    for file_path in common_files:
        if file_path not in branch_files or file_path not in staging_area_files:
            raise NotImplementedError(f"The file {file_path} was deleted. Deleting files not implemented yet.")
        content_in_branch, content_in_common, content_in_staging_area = get_file_content_in_dirs(
            branch_dir, common_dir, file_path, staging_area_path
        )
        if content_in_common != content_in_branch:
            if content_in_common != content_in_staging_area:
                raise NotImplementedError(
                    f"The file {file_path} was changed both in {branch_name} and in current branch."
                )
            (staging_area_path / file_path).write_text(content_in_branch)
    for file_path in branch_files:
        if file_path not in common_files:
            content_in_branch = (branch_dir / file_path).read_text()
            (staging_area_path / file_path).write_text(content_in_branch)
    commit_merge(branch_commit_id, branch_name, head_reference, wit_dir)


def commit_merge(branch_commit_id: str, branch_name: str, head_reference: str, wit_dir: Path):
    activated = get_activated_branch(wit_dir)
    message = f"Commit after merge of {activated if activated else head_reference} and {branch_name}."
    commit_function(message, branch_commit_id)


def get_file_content_in_dirs(
        branch_dir: Path, common_dir: Path, file_path: Path, staging_area_path: Path
) -> tuple[str, ...]:
    content_in_common = (common_dir / file_path).read_text()
    content_in_branch = (branch_dir / file_path).read_text()
    content_in_staging_area = (staging_area_path / file_path).read_text()
    return content_in_branch, content_in_common, content_in_staging_area


def get_dirs_and_files(
        branch_commit_id: str, common_commit: str, staging_area_path: Path, wit_dir: Path
) -> tuple[Path, Iterator[Path], Path, Iterator[Path], Iterator[Path]]:
    common_dir = wit_dir / 'images' / common_commit
    common_files = get_all_files_in_directory_and_subs(common_dir)
    branch_dir = wit_dir / 'images' / branch_commit_id
    branch_files = get_all_files_in_directory_and_subs(branch_dir)
    staging_area_files = get_all_files_in_directory_and_subs(staging_area_path)
    return branch_dir, branch_files, common_dir, common_files, staging_area_files


def get_paths_and_commit_ids(branch_name: str, repository: Path) -> tuple[str, str, Path, Path, Path]:
    wit_dir = repository / '.wit'
    staging_area_path = wit_dir / 'staging_area'
    head_reference = get_head_reference(repository)
    last_commit_path = repository / '.wit' / 'images' / head_reference
    references_file = wit_dir / 'references.txt'
    branch_commit_id = get_commit_id_of_branch(branch_name, references_file)
    return branch_commit_id, head_reference, last_commit_path, staging_area_path, wit_dir


def get_common_commit(wit_dir: Path, branch_commit_id: str, head_reference: str) -> str:
    branch_parents = set(get_parents_commits(wit_dir, branch_commit_id))
    head_parents = set(get_parents_commits(wit_dir, head_reference))
    common = branch_parents.intersection(head_parents)
    if common:
        return common.pop()
    return ''


def get_parents_commits(wit_dir: Path, commit_id: str) -> Iterator[str]:
    images_path = wit_dir / 'images'
    while commit_id:
        commit_file = images_path / (commit_id + ".txt")
        commit_txt = commit_file.read_text()
        parent_id_match = regex.match(commit_txt)
        if parent_id_match:  # if parent != None
            parent_id = parent_id_match.group('commit_id')
            yield parent_id
        commit_id = parent_id if parent_id_match else None
