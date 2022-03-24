import os

import pytest

from project.branch import branch_function
from project.checkout import checkout_function
from project.errors import MergeError, WitError
from project.merge import merge_function
from project.utils import get_staging_area
from tests.conftest import change_add_and_commit_file


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
    staging_area_path = get_staging_area(test_folder)
    file1_in_staging_area = staging_area_path / "file1.txt"
    new_in_staging_area = staging_area_path / "folder1" / "new.txt"
    assert file1.read_text() == "merge"
    assert file1_in_staging_area.read_text() == "merge"
    assert new.read_text() == "new"
    assert new_in_staging_area.read_text() == "new"


def test_merge_function2(test_folder, file1, file3):
    change_add_and_commit_file(file1, "")
    branch_function("branch1")
    checkout_function("branch1")
    change_add_and_commit_file(file3, "1")
    checkout_function("master")
    merge_function("branch1")
    staging_area_path = get_staging_area(test_folder)
    file1_in_staging_area = staging_area_path / "file1.txt"
    file3_in_staging_area = staging_area_path / "folder2" / "file3.txt"
    assert file1.read_text() == ""
    assert file1_in_staging_area.read_text() == ""
    assert file3.read_text() == "1"
    assert file3_in_staging_area.read_text() == "1"


def add_new_file_and_commit(folder):
    new = folder / "new.txt"
    change_add_and_commit_file(new, "new")
    return new
