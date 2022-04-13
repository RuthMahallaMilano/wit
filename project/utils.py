import os
import re
from glob import glob
from pathlib import Path
from typing import Iterator, Optional

branch_regex = re.compile(
BRANCH_REGEX = re.compile(
    r"^"
    r"(?P<branch_name>\w+)"
    r"="
    r"(?P<branch_id>[0-9a-fA-F]{20})"
    r"$",
    flags=re.MULTILINE,
)
)


def get_repository_path(path: Path) -> Optional[Path]:
    if path.is_dir():
        if glob(str(path / ".wit")):
            return path
    for directory in path.parents:
        if glob(str(directory / ".wit")):
            return directory
    return None


def get_commit_id_of_branch(
    repository: Path, branch: str, references_file: Path
) -> str:
    branches_commits_dict = get_branches_commits(references_file)
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


def get_branches_commits(references_file: Path) -> dict[str, str]:
    with references_file.open() as file:
        branches_data = file.read()
    branches_commits = {}
    branch_matches = branch_regex.findall(branches_data)
    for branch_name, commit_id in branch_matches:
        branches_commits[branch_name] = commit_id
    return branches_commits


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


def get_wit_dir(repository: Path) -> Path:
    return repository / ".wit"


def get_staging_area(repository: Path) -> Path:
    return get_wit_dir(repository) / "staging_area"


def get_references_path(repository: Path) -> Path:
    return get_wit_dir(repository) / "references.txt"


def get_images_path(repository: Path) -> Path:
    return get_wit_dir(repository) / "images"


def get_commit_path(repository: Path, commit_id: str):
    return get_images_path(repository) / commit_id


def get_activated_path(repository: Path) -> Path:
    return get_wit_dir(repository) / "activated.txt"
