from pathlib import Path

from add import get_repository_path
from commit import get_parent_head
from errors import WitError


def branch(name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = repository.joinpath('.wit', 'references.txt')
    commit_id = get_parent_head(repository)
    with references_file.open('a') as ref_file:
        ref_file.write(f'\n{name}={commit_id}')
