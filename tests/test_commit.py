import os

import pytest

from project.add import add_function
from project.commit import commit_function
from project.errors import WitError
from project.utils import get_commit_path, get_head_reference
from tests.conftest import change_add_and_commit_file


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        commit_function("")


def test_commit(test_folder, file1):
    os.chdir(test_folder)
    add_function(file1)
    commit_function("test commit")
    commit_id = get_head_reference(test_folder)
    commit_txt_file = get_commit_path(test_folder, commit_id).with_suffix(".txt")
    assert commit_id
    assert "test commit" in commit_txt_file.read_text()


def test_second_commit(test_folder, file1):
    change_add_and_commit_file(file1, "")
    new_commit_id = change_add_and_commit_file(file1, "1")
    assert get_head_reference(test_folder) == new_commit_id
