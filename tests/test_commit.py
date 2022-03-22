import os

import pytest

from project.commit import commit_function
from project.errors import WitError
from project.utils import get_head_reference, get_commit_path, get_commit_id_of_branch, get_references_path


def test_raise_error(tmp_path):
    os.chdir(tmp_path)
    with pytest.raises(WitError):
        commit_function("")


def test_commit(test_folder):
    os.chdir(test_folder)
    commit_function("test commit")
    commit_id = get_head_reference(test_folder)
    commit_txt_file = get_commit_path(test_folder, commit_id).with_suffix(".txt")
    assert commit_id
    assert "test commit" in commit_txt_file.read_text()


def test_second_commit(test_folder):
    commit_function("test second commit")
    references_path = get_references_path(test_folder)
    assert get_head_reference(test_folder) == get_commit_id_of_branch("master", references_path)
