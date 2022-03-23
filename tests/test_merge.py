import os

import pytest

from project.branch import branch_function
from project.checkout import checkout_function
from project.errors import WitError, MergeError
from project.merge import merge_function


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

# on master.
# new branch > change file > checkout master > change file > merge new branch
# assert: raise NotImplementedError - f"{file_path} was changed in both branches. Not implemented yet."
def test_raise_changed_file_error(test_folder):
    branch_function("TestChanged")
    checkout_function("TestChanged")
    file1 = test_folder / "file1.txt"
    file1.write_text()
    folder1 = test_folder / "folder1"



# on master.
# new branch > change file > checkout master > change another file > checkout branch > merge master
# assert both files has changed
