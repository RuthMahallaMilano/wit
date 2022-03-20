from pathlib import Path

from commit import get_head_reference
from errors import BranchExistsError, WitError
from global_functions import get_branches_commits, get_repository_path


def branch_function(name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = repository / ".wit" / "references.txt"
    existing_branches = get_branches_commits(references_file)
    if name in existing_branches:
        raise BranchExistsError(f"Branch {name} already exists.")
    commit_id = get_head_reference(repository)
    with references_file.open("a") as ref_file:
        ref_file.write(f"\n{name}={commit_id}")
