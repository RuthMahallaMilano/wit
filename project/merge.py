import re
from glob import glob
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

# regex = re.compile(r"^parent = (?P<commit_id>\w{20})$", flags=re.MULTILINE)
regex = re.compile(r"^parent = (?P<commit_id_1>\w{20})(, (?P<commit_id_2>\w{20}))?$", flags=re.MULTILINE)


def merge_function(branch_name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    wit_dir = repository / '.wit'
    staging_area_path = wit_dir / 'staging_area'
    references_file = wit_dir / 'references.txt'
    head_reference = get_head_reference(repository)
    branch_commit_id = get_commit_id_of_branch(branch_name, references_file)
    if (
        list(get_changes_to_be_committed(repository, staging_area_path))
        or list(get_changes_not_staged_for_commit(repository, staging_area_path))
    ):
        raise FilesDoesntMatchError("There are files added or changed after last commit_function")
    if branch_commit_id == head_reference:
        raise MergeError('Head is already at the branch you are trying to merge.')
    common_commit = get_common_commit(wit_dir, branch_commit_id, head_reference)
    # print(f"common: {common_commit}")
    if not common_commit:
        raise NoCommonCommitError(f"There is no common commit with {branch_name}.")
    common_dir = wit_dir / 'images' / common_commit
    branch_dir = wit_dir / 'images' / branch_commit_id
    common_files = get_all_files_in_directory_and_subs(common_dir)
    branch_files = get_all_files_in_directory_and_subs(branch_dir)
    for file_path in common_files:
        path_in_staging_area = staging_area_path / file_path
        path_in_branch = branch_dir / file_path
        # print(set(set(branch_files)))
        # print(f"path_in_staging_area: {path_in_staging_area}")
        # print(f"file_path not in branch_files: {file_path not in set(branch_files)}")
        # print(f"glob(str(path_in_staging_area)): {glob(str(path_in_staging_area))}")
        if not glob(str(path_in_branch)) or not glob(str(path_in_staging_area)):
            raise NotImplementedError(f"The file {file_path} was deleted. Deleting files not implemented yet.")
        elif file_path.is_file():
            content_in_common = (common_dir / file_path).read_text()
            print(f"content_in_common: {content_in_common}")
            content_in_branch = (branch_dir / file_path).read_text()
            print(f"content_in_branch: {content_in_branch}")
            content_in_staging_area = (staging_area_path / file_path).read_text()
            print(f"content_in_staging: {content_in_staging_area}")
            if content_in_common != content_in_branch:
                if content_in_common != content_in_staging_area:
                    raise NotImplementedError(f"{file_path} was changed in both branches. Not implemented yet.")
                (staging_area_path / file_path).write_text(content_in_branch)
    for file_path in branch_files:
        # path_in_common = common_dir / file_path
        # if not glob(str(path_in_common)):
        if file_path.is_file():
            content_in_branch = (branch_dir / file_path).read_text()
            (staging_area_path / file_path).write_text(content_in_branch)
    activated = get_activated_branch(wit_dir)
    message = f"Commit after merge of {activated if activated else head_reference} and {branch_name}."
    commit_function(message, branch_commit_id)


def get_common_commit(wit_dir: Path, branch_commit_id: str, head_reference: str) -> str:
    branch_parents = set(get_parents_commits(wit_dir, branch_commit_id))
    head_parents = set(get_parents_commits(wit_dir, head_reference))
    common = branch_parents.intersection(head_parents)
    if common:
        return common.pop()
    return ''


def get_parents_commits(wit_dir: Path, commit_id: str) -> Iterator[str]:
    images_path = wit_dir / 'images'
    yield from get_parents_of_commit_id(commit_id, images_path)


def get_parents_of_commit_id(commit_id: str, images_path: Path) -> Iterator[str]:
    while commit_id:
        commit_file = images_path / (commit_id + ".txt")
        commit_txt = commit_file.read_text()
        parent_id_match = regex.match(commit_txt)
        if parent_id_match:  # if parent != None
            parent_id_1 = parent_id_match.group('commit_id_1')
            parent_id_2 = parent_id_match.group('commit_id_2')
            print(f"*******{parent_id_1}*******")
            print(f"*******{parent_id_2}*******")
            yield parent_id_1
            if parent_id_2:
                yield parent_id_2
                yield from get_parents_of_commit_id(parent_id_2, images_path)
        commit_id = parent_id_1 if parent_id_match else None
