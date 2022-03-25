import os

import pytest

from project.add import add_function
from project.commit import commit_function
from project.init import init_function
from project.utils import get_staging_area


@pytest.fixture()
def test_folder(tmp_path):
    test_wit = tmp_path / "test_wit"
    last_folder = test_wit / "folder1" / "folder2"
    last_folder.mkdir(parents=True, exist_ok=True)
    (test_wit / "file1.txt").write_text("")
    (test_wit / "folder1" / "file2.txt").write_text("")
    (last_folder / "file3.txt").write_text("")
    empty_folder = test_wit / "empty"
    empty_folder.mkdir()
    os.chdir(test_wit)
    init_function()
    return test_wit


@pytest.fixture()
def file1(test_folder):
    return test_folder / "file1.txt"


@pytest.fixture()
def folder1(test_folder):
    return test_folder / "folder1"


@pytest.fixture()
def file2(folder1):
    return folder1 / "file2.txt"


@pytest.fixture()
def folder2(folder1):
    return folder1 / "folder2"


@pytest.fixture()
def file3(folder2):
    return folder2 / "file3.txt"


@pytest.fixture()
def empty_folder(test_folder):
    return test_folder / "empty"


def change_add_and_commit_file(file_path, txt):
    file_path.write_text(txt)
    add_function(file_path)
    commit_id = commit_function("")
    return commit_id


def add_new_file_and_commit(folder):
    new = folder / "file_path.txt"
    change_add_and_commit_file(new, "file_path")
    return new


def get_file_path_in_staging_area(file_path, folder):
    staging_area = get_staging_area(folder)
    path_in_staging_area = staging_area / file_path.relative_to(folder)
    return path_in_staging_area
