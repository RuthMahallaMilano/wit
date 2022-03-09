from glob import glob
from pathlib import Path
import re
from typing import Optional


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
    with references_file.open() as file:
        branches_commits_dict = {}
        for line in file:
            match = branch_regex.match(line)
            branches_commits_dict[match.group('branch_name')] = match.group('branch_id')
        if branch in branches_commits_dict:
            return branches_commits_dict[branch]
        if branch in branches_commits_dict.values():
            return branch
        return ''


def get_head_reference(repository: Path) -> str:
    wit_folder = repository.joinpath('.wit')
    references_file = wit_folder.joinpath('references.txt')
    if references_file.exists():
        return get_commit_id_of_branch('HEAD', references_file)
    return ''
