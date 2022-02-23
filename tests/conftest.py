import os
from pathlib import Path
import pytest


@pytest.fixture()
def test_folder():
    folder_name = 'test_wit'
    os.mkdir(folder_name)
    file1_path = Path(folder_name).joinpath('file1.txt')
    file1_path.write_text("")
    folder1_path = os.path.join(folder_name, 'folder1')
    os.mkdir(folder1_path)
    file2_path = Path(folder1_path).joinpath('file2.txt')
    file2_path.write_text("")
    folder2_path = os.path.join(folder1_path, 'folder2')
    os.mkdir(folder2_path)
    file3_path = Path(folder2_path).joinpath('file3.txt')
    file3_path.write_text("")
    return folder_name  # yield?
    # os.unlink(folder_name)
