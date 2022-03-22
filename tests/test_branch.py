import os

import pytest

from project.branch import branch_function
from project.errors import WitError, BranchExistsError
from project.utils import get_references_path, get_head_reference


def test_raise_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        branch_function("")


def test_branch_function(test_folder):  # fail
    os.chdir(test_folder)
    branch_function("TestBranch")
    commit_id = get_head_reference(test_folder)
    references_file = get_references_path(test_folder)
    assert f"TestBranch={commit_id}" in references_file


def test_branch_exists_error(test_folder):  # fail
    with pytest.raises(BranchExistsError):
        branch_function("TestBranch")


# TODO: test if no commit was done yet.
#  test second branch.
