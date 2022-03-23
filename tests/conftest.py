import os

import pytest

from project.add import add_function
from project.commit import commit_function
from project.init import init_function


@pytest.fixture(scope="session")
def test_folder(tmp_path_factory):
    test_folder = tmp_path_factory.mktemp("test_wit")
    last_folder = test_folder / "folder1" / "folder2"
    last_folder.mkdir(parents=True, exist_ok=True)
    (test_folder / "file1.txt").write_text("")
    (test_folder / "folder1" / "file2.txt").write_text("")
    (last_folder / "file3.txt").write_text("")
    os.chdir(test_folder)
    init_function()
    return test_folder


def change_add_and_commit_file(file_path, txt):
    file_path.write_text(txt)
    add_function(file_path)
    commit_function("")
