import os

import pytest

from project.add import add_function
from project.errors import WitError
from project.utils import get_staging_area


def test_raise_error(tmp_path):
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
    add_function(test_folder / file_to_add)
    path_in_staging_area = get_staging_area(test_folder) / file_to_add
    assert path_in_staging_area.exists()
