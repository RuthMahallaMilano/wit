import os
import shutil

import pytest

from project.add import add_function
from project.branch import branch_function
from project.commit import commit_function
from project.errors import WitError, BranchExistsError
from project.init import init_function
from project.utils import get_references_path, get_head_reference, get_wit_dir


def test_raise_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        branch_function("")


def test_branch_function(test_folder):  # fail
    os.chdir(test_folder)
    file2 = test_folder / "folder1" / "file2.txt"
    file2.write_text("test branch")
    add_function(file2)
    commit_function("test branch")
    branch_function("TestBranch")
    commit_id = get_head_reference(test_folder)
    references_file = get_references_path(test_folder)
    assert f"TestBranch={commit_id}" in references_file.read_text()


def test_branch_exists_error(test_folder):  # fail
    with pytest.raises(BranchExistsError):
        branch_function("TestBranch")


# TODO: test if no commit was done yet.
#  test second branch.
