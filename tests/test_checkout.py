import os

import pytest

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.commit import commit_function
from project.errors import WitError, BranchDoesntExistError, FilesDoNotMatchError
from project.utils import get_activated_branch, get_commit_id_of_branch, get_references_path, get_activated_path, \
    get_head_reference


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        checkout_function("branch")


def test_raise_branch_doesnt_exist_error(test_folder):
    os.chdir(test_folder)
    commit_function("")
    with pytest.raises(BranchDoesntExistError):
        checkout_function("branch")


def test_raise_files_do_not_match_error_changed(test_folder):
    branch_function("branch")
    checkout_function("branch")
    file1 = test_folder / "file1.txt"
    file1.write_text("FilesDoNotMatchError1")
    with pytest.raises(FilesDoNotMatchError):
        checkout_function("master")


def test_raise_files_do_not_match_error_added(test_folder):
    file1 = test_folder / "file1.txt"
    add_function(file1)
    with pytest.raises(FilesDoNotMatchError):
        checkout_function("master")


def test_checkout_function(test_folder):
    commit_function("")
    checkout_function("master")
    file1 = test_folder / "file1.txt"
    assert get_activated_branch(test_folder) == "master"
    assert file1.read_text() != "FilesDoNotMatchError1"


def test_checkout_id(test_folder):
    add_and_commit_file1(test_folder)
    test_id = get_head_reference(test_folder)
    add_and_commit_file2(test_folder)
    checkout_function(test_id)
    activated_branch = get_activated_branch(test_folder)
    assert not activated_branch
    checkout_function("master")


def add_and_commit_file2(test_folder):
    file2 = test_folder / "folder1" / "file2.txt"
    add_function(file2)
    commit_function(file2)


def add_and_commit_file1(test_folder):
    file1 = test_folder / "file1.txt"
    add_function(file1)
    commit_function("")
