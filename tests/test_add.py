import os

import pytest

from project.add import add_function
from project.errors import WitError
from tests.conftest import get_file_path_in_staging_area


def test_raise_wit_error(tmp_path):
    os.chdir(tmp_path)
    test_file = tmp_path / "test.txt"
    test_file.write_text("")
    with pytest.raises(WitError):
        add_function(test_file.name)


@pytest.mark.parametrize(
    "file_to_add", ["file1.txt", r"folder1\folder2\file3.txt", r"folder1\folder2"]
)
def test_add_function(test_folder, file_to_add):
    os.chdir(test_folder)
    file_path = test_folder / file_to_add
    add_function(file_path)
    path_in_staging_area = get_file_path_in_staging_area(file_path, test_folder)
    assert path_in_staging_area.exists()


def test_add_dir_already_added(test_folder, file3, folder2):
    add_function(folder2)
    file3.write_text("1")
    add_function(folder2)
    file3_in_staging_area = get_file_path_in_staging_area(file3, test_folder)
    assert file3_in_staging_area.read_text() == "1"
