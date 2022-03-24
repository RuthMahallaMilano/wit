import os

import pytest

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.errors import BranchDoesntExistError, FilesDoNotMatchError, WitError
from project.utils import get_activated_branch, get_head_reference
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        checkout_function("branch")


def test_raise_branch_doesnt_exist_error(test_folder, file1):
    os.chdir(test_folder)
    change_add_and_commit_file(file1, "")
    with pytest.raises(BranchDoesntExistError):
        checkout_function("branch")


def test_raise_files_do_not_match_error_changed(test_folder, file1):
    change_add_and_commit_file(file1, "")
    branch_function("branch")
    checkout_function("branch")
    file1.write_text("FilesDoNotMatchError1")
    with pytest.raises(FilesDoNotMatchError):
        checkout_function("master")


def test_raise_files_do_not_match_error_added(test_folder, file1, file2):
    change_add_and_commit_file(file1, "")
    add_function(file2)
    with pytest.raises(FilesDoNotMatchError):
        checkout_function("master")


def test_checkout_function(test_folder, file1):
    change_add_and_commit_file(file1, "")
    branch_function("branch")
    checkout_function("branch")
    change_add_and_commit_file(file1, "changed")
    checkout_function("master")
    assert get_activated_branch(test_folder) == "master"
    assert file1.read_text() == ""


def test_checkout_id(test_folder, file1, file2):
    change_add_and_commit_file(file1, "")
    test_id = get_head_reference(test_folder)
    change_add_and_commit_file(file2, "")
    checkout_function(test_id)
    activated_branch = get_activated_branch(test_folder)
    assert not activated_branch
