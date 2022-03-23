import os

import pytest

from project.branch import branch_function
from project.checkout import checkout_function
from project.utils import get_staging_area
from project.errors import WitError, MergeError
from project.merge import merge_function
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    test_file = tmp_path / "test.txt"
    test_file.write_text("")
    with pytest.raises(WitError):
        merge_function("")


def test_raise_merge_error(test_folder):
    os.chdir(test_folder)
    with pytest.raises(MergeError):
        merge_function("master")


def test_raise_changed_file_error(test_folder):
    branch_function("TestChanged")
    checkout_function("TestChanged")
    file1 = test_folder / "file1.txt"
    change_add_and_commit_file(file1, "changed")
    # folder1 = test_folder / "folder1"
    checkout_function("master")
    change_add_and_commit_file(file1, "changed again")
    with pytest.raises(NotImplementedError):
        merge_function("TestChanged")


def test_merge_function(test_folder):
    file1 = test_folder / "file1.txt"
    change_add_and_commit_file(file1, "")  # zero
    branch_function("TestMerge")
    checkout_function("TestMerge")
    folder1 = test_folder / "folder1"
    new = folder1 / 'new.txt'
    change_add_and_commit_file(new, "new")
    checkout_function("master")
    file1 = test_folder / "file1.txt"
    change_add_and_commit_file(file1, "merge")
    checkout_function("TestMerge")
    merge_function("master")
    staging_area_path = get_staging_area(test_folder)
    file1_in_staging_area = staging_area_path / "file1.txt"
    new_in_staging_area = staging_area_path / "folder1" / 'new.txt'
    assert file1.read_text() == "merge"
    assert file1_in_staging_area.read_text() == "merge"
    assert new.read_text() == "new"
    assert new_in_staging_area.read_text() == "new"
