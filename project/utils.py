import os
import re
from pathlib import Path
from typing import Iterator, Optional

from project.errors import FilesDoNotMatchError


BRANCH_REGEX = re.compile(
    r"^"
    r"(?P<branch_name>\w+)" 
    r"=" 
    r"(?P<branch_id>\w{20})" 
    r"$",
    flags=re.MULTILINE,
)


PARENT_ID_REGEX = re.compile(
    r"^parent = " 
    r"(?P<commit_id_1>\w{20})" 
    r"(, (?P<commit_id_2>\w{20}))" 
    r"?$",
    flags=re.MULTILINE,
)


def get_repository_path(path: Path) -> Optional[Path]:
    if path.is_dir():
        if set(path.glob(".wit")):
            return path
    for directory in path.parents:
        if set(directory.glob(".wit")):
            return directory
    return None


def get_commit_id_of_branch(
    repository: Path,
    branch: str,
    references_file: Path,
) -> str:
    branches_commits_dict = get_commits_by_branches(references_file)
    if branch in branches_commits_dict:
        return branches_commits_dict[branch]
    if branch in list(get_all_commits(repository)):
        return branch
    return ""


def get_all_commits(repository: Path) -> Iterator[str]:
    images_path = get_images_path(repository)
    for file_name in images_path.iterdir():
        if file_name.is_dir():
            yield file_name.name


def get_commits_by_branches(references_file: Path) -> dict[str, str]:
    with references_file.open() as file:
        branches_data = file.read()
    branch_matches = BRANCH_REGEX.findall(branches_data)
    return dict(branch_matches)


def get_head_reference(repository: Path) -> str:
    references_file = get_references_path(repository)
    if references_file.exists():
        return get_commit_id_of_branch(repository, "HEAD", references_file)
    return ""


def get_activated_branch(repository: Path) -> str:
    activated_path = get_activated_path(repository)
    return activated_path.read_text()


def get_all_files_in_directory_and_subs(directory: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(directory, topdown=True):
        if files:
            for file in files:
                yield (Path(root) / file).relative_to(directory)
        else:
            if not dirs:
                yield Path(root).relative_to(directory)


def get_all_files_in_repository_and_subs(repository: Path) -> Iterator[Path]:
    for root, dirs, files in os.walk(repository, topdown=True):
        if files:
            for file in files:
                if ".wit" not in root:
                    yield (Path(root) / file).relative_to(repository)
        else:
            if ".wit" not in root and not dirs:
                yield Path(root).relative_to(repository)


def get_wit_path(repository: Path) -> Path:
    return repository / ".wit"


def get_staging_area_path(repository: Path) -> Path:
    return get_wit_path(repository) / "staging_area"


def get_references_path(repository: Path) -> Path:
    return get_wit_path(repository) / "references.txt"


def get_images_path(repository: Path) -> Path:
    return get_wit_path(repository) / "images"


def get_commit_path(repository: Path, commit_id: str) -> Path:
    return get_images_path(repository) / commit_id


def get_activated_path(repository: Path) -> Path:
    return get_wit_path(repository) / "activated.txt"


def check_if_file_changed(file_path: Path, dir_1: Path, dir_2: Path) -> bool:
    content_in_dir_1 = (dir_1 / file_path).read_text()
    content_in_dir_2 = (dir_2 / file_path).read_text()
    return content_in_dir_1 != content_in_dir_2


def get_changes_to_be_committed(repository: Path) -> Optional[Iterator[Path]]:
    staging_area_path = get_staging_area_path(repository)
    last_commit_id = get_head_reference(repository)
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area_path)
    if not last_commit_id:
        return None
    commit_path = get_commit_path(repository, last_commit_id)
    for file_path in files_in_staging_area:
        files_in_last_commit_that_match_file_path = commit_path.glob(str(file_path))
        if not set(files_in_last_commit_that_match_file_path):
            yield file_path
        elif file_path.is_file():
            if check_if_file_changed(file_path, staging_area_path, commit_path):
                yield file_path


def get_changes_not_staged_for_commit(repository: Path) -> Optional[Iterator[Path]]:
    staging_area_path = get_staging_area_path(repository)
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area_path)
    for file_path in files_in_staging_area:
        if file_path.is_file():
            if check_if_file_changed(file_path, staging_area_path, repository):
                yield file_path


def raise_for_unsaved_work(repository: Path) -> None:
    files_added_since_last_commit = set(get_changes_to_be_committed(repository))
    changed_files_since_last_commit = set(get_changes_not_staged_for_commit(repository))
    if files_added_since_last_commit or changed_files_since_last_commit:
        raise FilesDoNotMatchError("There are files added or changed since last commit")
