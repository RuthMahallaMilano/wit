import os
from glob import glob
from pathlib import Path
import re
from typing import Optional, Iterator, Union

branch_regex = re.compile(r"^(?P<branch_name>\w+)=(?P<branch_id>\w{20})$")


def get_repository_path(path: Path) -> Optional[Path]:
    if path.is_dir():
        if glob(str(path / '.wit')):
            return path
    for directory in path.parents:
        if glob(str(directory / '.wit')):
            return directory
    return None


def get_commit_id_of_branch(branch: str, references_file: Path) -> str:
    branches_commits_dict = get_branches_commits(references_file)
    if branch in branches_commits_dict:
        return branches_commits_dict[branch]
    if branch in branches_commits_dict.values():
        return branch
    return ''


def get_branches_commits(references_file: Path) -> dict[str, str]:
    with references_file.open() as file:
        branches_commits_dict = {}
        for line in file:
            match = branch_regex.match(line)
            branches_commits_dict[match.group('branch_name')] = match.group('branch_id')
        return branches_commits_dict


def get_head_reference(repository: Path) -> str:
    wit_folder = repository.joinpath('.wit')
    references_file = wit_folder.joinpath('references.txt')
    if references_file.exists():
        return get_commit_id_of_branch('HEAD', references_file)
    return ''


def get_activated_branch(wit_folder: Path) -> str:
    activated_path = wit_folder / 'activated.txt'
    return activated_path.read_text()


def get_all_files_in_directory_and_subs(
        directory: Union[Path, str],
        start_path: Optional[Union[Path, str]] = None,
) -> Iterator[Path]:
    if not start_path:
        start_path = directory
    for root, dirs, files in os.walk(directory, topdown=True):
        if not files and not dirs:
            yield Path(root).relative_to(start_path)
        for file in files:
            file_abs_path = Path(root) / file
            yield file_abs_path.relative_to(start_path)
        for dir_name in dirs:
            yield from get_all_files_in_directory_and_subs(directory / dir_name, start_path)
