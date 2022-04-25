from pathlib import Path

from project.errors import BranchExistsError, BranchNotCreatedError, WitError
from project.utils import (
    get_commits_by_branches,
    get_head_reference,
    get_references_path,
    get_repository_path,
)


def branch_function(name: str) -> None:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    references_file = get_references_path(repository)
    if not references_file.exists():
        raise BranchNotCreatedError(
            "No commit was done yet. Can't create a new branch."
        )
    existing_branches = get_commits_by_branches(references_file)
    if name in existing_branches:
        raise BranchExistsError(f"Branch {name} already exists.")
    commit_id = get_head_reference(repository)
    with references_file.open("a") as ref_file:
        ref_file.write(f"\n{name}={commit_id}")
