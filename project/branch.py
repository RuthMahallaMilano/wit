from pathlib import Path

from commit import get_head_reference
from errors import WitError
from global_functions import get_repository_path


def branch_function(name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = repository / '.wit' / 'references.txt'
    commit_id = get_head_reference(repository)
    with references_file.open('a') as ref_file:
        ref_file.write(f'\n{name}={commit_id}')
