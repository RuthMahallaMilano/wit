import os

import pytest

from project.branch import branch_function
from project.errors import BranchExistsError, WitError
from project.utils import get_head_reference, get_references_path
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        branch_function("")


def test_branch_function(test_folder, file2):
    os.chdir(test_folder)
    change_add_and_commit_file(file2, "test branch")
    branch_function("TestBranch")
    commit_id = get_head_reference(test_folder)
    references_file = get_references_path(test_folder)
    assert f"TestBranch={commit_id}" in references_file.read_text()


def test_branch_exists_error(test_folder, file2):
    change_add_and_commit_file(file2, "test branch")
    branch_function("TestBranch")
    with pytest.raises(BranchExistsError):
        branch_function("TestBranch")
