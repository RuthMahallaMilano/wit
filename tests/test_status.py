import os

import pytest

from project.add import add_function
from project.errors import WitError
from project.status import status_function
from project.utils import (
    get_all_files_in_directory_and_subs,
    get_all_files_in_repository_and_subs,
    get_staging_area,
)
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        status_function()


def test_status(test_folder, file1, file3):
    os.chdir(test_folder)
    change_add_and_commit_file(file1, "")
    add_function(file3)
    file1.write_text("1")
    (
        changes_to_be_committed,
        changes_not_staged_for_commit,
        untracked_files,
    ) = status_function()
    assert set(changes_to_be_committed) == {file3.relative_to(test_folder)}
    assert set(changes_not_staged_for_commit) == {file1.relative_to(test_folder)}
    staging_area = get_staging_area(test_folder)
    all_files = get_all_files_in_repository_and_subs(test_folder)
    files_in_staging_area = get_all_files_in_directory_and_subs(staging_area)
    assert set(untracked_files).union(set(files_in_staging_area)) == set(all_files)
