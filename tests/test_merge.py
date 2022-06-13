import os

import pytest

from project.add import add_function
from project.branch import branch_function
from project.checkout import checkout_function
from project.commit import commit_function
from project.errors import MergeError, WitError
from project.merge import merge_function
from tests.conftest import (
    add_new_file_and_commit,
    change_add_and_commit_file,
    get_file_path_in_staging_area,
)


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        merge_function("")


def test_raise_merge_error(test_folder):
    os.chdir(test_folder)
    with pytest.raises(MergeError):
        merge_function("master")


def test_raise_changed_file_error(test_folder, file1):
    change_add_and_commit_file(file1, "")
    branch_function("TestChanged")
    checkout_function("TestChanged")
    change_add_and_commit_file(file1, "changed")
    checkout_function("master")
    change_add_and_commit_file(file1, "changed again")
    with pytest.raises(NotImplementedError):
        merge_function("TestChanged")


def test_merge_function(test_folder, file1, folder1):
    change_add_and_commit_file(file1, "")
    branch_function("TestMerge")
    checkout_function("TestMerge")
    new = add_new_file_and_commit(folder1)
    checkout_function("master")
    change_add_and_commit_file(file1, "merge")
    checkout_function("TestMerge")
    merge_function("master")
    file1_in_staging_area = get_file_path_in_staging_area(file1, test_folder)
    new_in_staging_area = get_file_path_in_staging_area(new, test_folder)
    assert file1.read_text() == "merge"
    assert file1_in_staging_area.read_text() == "merge"
    assert new.read_text() == "file_path"
    assert new_in_staging_area.read_text() == "file_path"


def test_merge_function2(test_folder, file1, file3):
    change_add_and_commit_file(file1, "")
    branch_function("branch1")
    checkout_function("branch1")
    change_add_and_commit_file(file3, "1")
    checkout_function("master")
    merge_function("branch1")
    file1_in_staging_area = get_file_path_in_staging_area(file1, test_folder)
    file3_in_staging_area = get_file_path_in_staging_area(file3, test_folder)
    assert file1.read_text() == ""
    assert file1_in_staging_area.read_text() == ""
    assert file3.read_text() == "1"
    assert file3_in_staging_area.read_text() == "1"


def test_raise_deleted_file_error(test_folder, file1, file2):
    change_add_and_commit_file(file1, "")
    branch_function("TestMerge")
    checkout_function("TestMerge")
    file2.unlink()
    checkout_function("master")
    with pytest.raises(NotImplementedError):
        merge_function("TestMerge")


def test_create_file_and_merge(test_folder, file1):
    change_add_and_commit_file(file1, "")
    branch_function("TestMerge")
    checkout_function("TestMerge")
    new = add_new_file_and_commit(test_folder)
    checkout_function("master")
    merge_function("TestMerge")
    new_in_staging_area = get_file_path_in_staging_area(new, test_folder)
    assert new_in_staging_area.read_text() == "file_path"


def test_merge_master(test_folder, file1, file2):
    change_add_and_commit_file(file1, "")
    branch_function("TestMerge")
    checkout_function("TestMerge")
    change_add_and_commit_file(file2, "1")
    merge_function("master")


def test_create_folder_and_merge(test_folder, file1):
    change_add_and_commit_file(file1, "")
    branch_function("TestMerge")
    checkout_function("TestMerge")
    new = test_folder / "file_path"
    new.mkdir()
    add_function(new)
    commit_function("")
    checkout_function("master")
    merge_function("TestMerge")
    new_in_staging_area = get_file_path_in_staging_area(new, test_folder)
    assert new_in_staging_area.exists()
    assert new.exists()
