import datetime
import os
import random
import re
import shutil
from pathlib import Path
from typing import Optional

from project.errors import WitError
from project.utils import (
    get_activated_branch,
    get_commit_path,
    get_head_reference,
    get_references_path,
    get_repository_path,
    get_staging_area,
)

LENGTH = 20
CHARS = "1234567890abcdef"


def commit_function(message: str, second_parent: Optional[str] = None) -> str:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    new_commit_id = create_commit_id()
    create_commit_folder(new_commit_id, repository)
    create_commit_txt_file(repository, new_commit_id, message, second_parent)
    save_files_in_new_commit(repository, new_commit_id)
    write_references(new_commit_id, repository)
    return new_commit_id


def create_commit_folder(new_commit_id: str, repository: Path) -> None:
    path_of_new_folder = get_commit_path(repository, new_commit_id)
    os.mkdir(path_of_new_folder)


def create_commit_id() -> str:
    commit_id = "".join(random.choices(CHARS, k=LENGTH))
    return commit_id


def create_commit_txt_file(
    repository: Path,
    new_commit_id: str,
    message: str,
    second_parent: Optional[str] = None,
) -> None:
    parent_head = get_head_reference(repository)
    if second_parent:
        parent_head += ", " + second_parent
    new_commit_path = get_commit_path(repository, new_commit_id)
    txt_file = new_commit_path.with_suffix(".txt")
    txt_file.write_text(
        f"parent = {parent_head if parent_head else None}\n"
        f'date = {datetime.datetime.now().strftime("%c")}\n'
        f"message = {message}"
    )


def save_files_in_new_commit(repository: Path, new_commit_id: str) -> None:
    staging_area_path = get_staging_area(repository)
    commit_path = get_commit_path(repository, new_commit_id)
    for item in staging_area_path.iterdir():
        src = staging_area_path / item.name
        dst = commit_path / item.name
        if src.is_file():
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)


def write_references(commit_id: str, repository: Path) -> None:
    references_file = get_references_path(repository)
    parent_head = get_head_reference(repository)
    activated_branch = get_activated_branch(repository)
    if references_file.exists():
        change_head_and_branch_id(
            activated_branch, commit_id, parent_head, references_file
        )
    else:
        change_only_head(activated_branch, commit_id, references_file)


def change_only_head(
    activated_branch: str, commit_id: str, references_file: Path
) -> None:
    new_line = "=".join((activated_branch, commit_id))
    references_file.write_text(f"HEAD={commit_id}\n{new_line}")


def change_head_and_branch_id(
    activated_branch: str, commit_id: str, parent_head: str, references_file: Path
) -> None:
    activated_regex = rf"^{activated_branch}={parent_head}$"
    head_regex = rf"^HEAD={parent_head}$"
    references_data = references_file.read_text()
    activated_match = re.findall(activated_regex, references_data, flags=re.MULTILINE)
    new_references_content = (
        re.sub(
            activated_regex,
            f"{activated_branch}={commit_id}",
            references_data,
            flags=re.MULTILINE,
        )
        if activated_match
        else references_data
    )
    new_references_content = re.sub(
        head_regex, f"HEAD={commit_id}", new_references_content, flags=re.MULTILINE
    )
    references_file.write_text(new_references_content)
