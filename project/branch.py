from pathlib import Path

from project.errors import BranchExistsError, WitError
from project.utils import (
    get_branches_commits,
    get_head_reference,
    get_references_path,
    get_repository_path,
)


def branch_function(name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = get_references_path(repository)
    existing_branches = get_branches_commits(references_file)
    if name in existing_branches:
        raise BranchExistsError(f"Branch {name} already exists.")
    commit_id = get_head_reference(repository)
    # TODO: if no commit was done yet- create references file / raise error
    with references_file.open("a") as ref_file:
        ref_file.write(f"\n{name}={commit_id}")
