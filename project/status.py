from pathlib import Path
from typing import Iterator

from project.errors import WitError
from project.utils import (
    get_all_files_in_repository_and_subs,
    get_changes_not_staged_for_commit,
    get_changes_to_be_committed,
    get_head_reference,
    get_repository_path,
    get_staging_area_path,
)


def status_function() -> tuple[Iterator[Path], Iterator[Path], Iterator[Path]]:
    repository = get_repository_path(Path.cwd())
    if not repository:
        raise WitError("<.wit> file not found")
    last_commit_id = get_head_reference(repository)
    message_if_no_commit = "No commit was done yet."
    changes_to_be_committed = stringify_files(get_changes_to_be_committed(repository))
    changes_not_staged_for_commit = stringify_files(
        get_changes_not_staged_for_commit(repository)
    )
    untracked_files = stringify_files(get_untracked_files(repository))
    output = (
        f"###Commit id:###\n{last_commit_id if last_commit_id else message_if_no_commit}\n\n"
        f"###Changes to be committed:###\n{changes_to_be_committed}\n\n"
        f"###Changes not staged for commit:###\n{changes_not_staged_for_commit}\n\n"
        f"###Untracked files:###\n{untracked_files}\n"
    )
    print(output)
    return (
        get_changes_to_be_committed(repository),
        get_changes_not_staged_for_commit(repository),
        get_untracked_files(repository),
    )


def stringify_files(files: Iterator[Path]) -> str:
    return "\n".join([str(file_name) for file_name in files])


def get_untracked_files(repository: Path) -> Iterator[Path]:
    staging_area_path = get_staging_area_path(repository)
    files_in_repository = get_all_files_in_repository_and_subs(repository)
    for file_path in files_in_repository:
        files_in_staging_area_that_match_file_path = staging_area_path.glob(
            str(file_path)
        )
        if not set(files_in_staging_area_that_match_file_path):
            yield file_path
